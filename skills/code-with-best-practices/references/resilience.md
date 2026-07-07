Apply these practices whenever writing code that calls another service, database, queue, or third-party API, or when adding retries, timeouts, circuit breakers, fallbacks, or queue consumers. The patterns are language-agnostic; snippets are TypeScript, port as needed. Generic error-handling and data-loss rules live in CLAUDE.md; this reference is the fault-tolerance material that is easy to get wrong. On conflict, the project's own conventions win.

## Contents

- [Timeouts](#timeouts)
- [Retries, backoff, and jitter](#retries-backoff-and-jitter)
- [Idempotency for retried writes](#idempotency-for-retried-writes)
- [Circuit breakers](#circuit-breakers)
- [Graceful degradation and fallbacks](#graceful-degradation-and-fallbacks)
- [Queues: poison messages and dead letters](#queues-poison-messages-and-dead-letters)
- [Bulkheads and connection pools](#bulkheads-and-connection-pools)
- [Health checks](#health-checks)
- [Testing resilience](#testing-resilience)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Timeouts

| Practice | Detail |
|---|---|
| Every outbound call gets an explicit timeout | Many clients default to no timeout or an absurd one (`fetch` has none; classic Python `requests` has none). A missing timeout turns one slow dependency into thread, socket, and memory exhaustion in every caller upstream of it. |
| Derive budgets from the caller's deadline, not round numbers | Work backward from the SLO: a 500ms endpoint budget with two sequential downstream calls means each gets a slice with headroom for retries, not 30s each. A timeout longer than what the caller will wait is a timeout in name only. |
| Separate connect from overall timeout | Connect should fail fast (1-2s catches a dead host); the overall timeout bounds total time including body transfer. One combined number forces choosing between slow failure detection and cutting off slow-but-succeeding transfers. |
| Propagate the remaining deadline downstream | Pass the budget through (`AbortSignal`, Go `context.Context`, gRPC deadlines) so a downstream service stops computing a response nobody upstream is still waiting for. |
| On timeout, cancel the work, not just the wait | A `Promise.race` timer abandons the losing promise but the request keeps running and holding a socket. Use `AbortSignal.timeout(ms)` or the client's native cancellation so the resources are actually released. |

## Retries, backoff, and jitter

| Practice | Detail |
|---|---|
| Retry only transient failures | Timeouts, connection resets, 429, 502/503/504. Never retry other 4xx: the same request will fail the same way, and retrying a 401 can lock an account. |
| Exponential backoff with full jitter | Delay = random between 0 and `min(cap, base * 2^attempt)`. Without jitter, every client that failed together retries together, and the synchronized wave re-kills the recovering service. |
| Cap attempts and total time | 2-3 attempts is the normal ceiling, bounded by the caller's deadline. A retry loop that outlives the deadline burns resources computing answers nobody receives. |
| Retry at one layer only | Client retries times sidecar retries times queue redelivery multiply: three layers of three attempts is 27 requests from one call. Pick the layer closest to the failure knowledge and disable the rest; retry amplification is how a degraded service becomes a dead one. |
| Honor `Retry-After` and back off on 429 | The server is telling you its recovery time; a fixed backoff that ignores it keeps hitting the rate limiter and extends the penalty. |

```typescript
async function withRetry<T>(fn: () => Promise<T>, attempts = 3, baseMs = 200, capMs = 5_000): Promise<T> {
  for (let attempt = 0; ; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt >= attempts - 1 || !isTransient(err)) throw err;
      // Full jitter: 0..min(cap, base * 2^attempt), so failed-together clients do not retry together
      const delay = Math.random() * Math.min(capMs, baseMs * 2 ** attempt);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}
```

## Idempotency for retried writes

| Practice | Detail |
|---|---|
| A timeout is not a failure | The first attempt may have succeeded with the response lost in transit. Retrying a non-idempotent write on timeout is how customers get charged twice; any write that can be retried must be safe to receive twice. |
| Use idempotency keys for writes behind retries | The client generates a key per logical operation (not per attempt) and sends it on every retry; the server stores key-to-result and replays the stored result on a duplicate. Stripe's `Idempotency-Key` header is the reference design. |
| Enforce the key at a uniqueness boundary | The dedupe check must be atomic: a unique constraint on the key column or an atomic set-if-absent, not a read-then-write, or two concurrent retries both pass the check. |
| Prefer naturally idempotent designs | PUT with full state, upsert on a unique constraint, "set status to X" instead of "increment counter". A design that needs no dedupe machinery beats one that dedupes correctly. |

## Circuit breakers

| Practice | Detail |
|---|---|
| Know what a breaker is for | After a failure-rate threshold, the breaker opens and calls fail immediately without touching the dependency; after a cooldown it half-opens to probe. The point is to stop burning caller resources on a dependency that fails slowly, and to give it room to recover. |
| Know when it is overkill | Low-traffic paths (the failure sample is too small to trip meaningfully), dependencies that already fail fast, and anything a timeout plus a retry cap fully handles. A breaker adds tuning burden and a new failure mode (false open); start with timeouts and retry caps, add a breaker when evidence shows slow-failure pileups or retry storms. |
| Use a library, not a hand-rolled one | opossum (Node), resilience4j (JVM), pybreaker (Python). Half-open probing, rolling windows, and concurrent-request accounting are subtle enough that hand-rolled breakers are a recurring bug source. |
| An open breaker needs a defined fallback | The breaker converts slow failures into fast ones; what the caller returns on that fast failure (stale cache, default, 503) is a product decision that must be made, not defaulted into a stack trace. |
| Scope breakers per dependency | One breaker shared across dependencies opens for all of them when one fails, converting a partial outage into a full one. |

## Graceful degradation and fallbacks

| Practice | Detail |
|---|---|
| Decide per feature what down looks like | Stale cached value, static default, hidden widget, queued-for-later write, or an honest error. "Throw a 500" is also a decision; make it deliberately, not by omission. |
| Fallbacks must be strictly cheaper than the primary | A fallback that calls another service can cascade the overload sideways. The safe fallbacks are local: cache, constant, skip. |
| Serve stale over serving nothing | For read paths, keep the last good response and serve it when the source fails (stale-while-revalidate / stale-if-error semantics); most data is far less perishable than the error page implies. |
| Make degradation observable | Emit a metric and a log when serving a fallback. Silent degradation means the outage is discovered from the revenue graph instead of the dashboard. |

## Queues: poison messages and dead letters

| Practice | Detail |
|---|---|
| Bound redelivery per message | A poison message (one that always fails processing) with unbounded redelivery loops forever, and in FIFO or single-consumer setups blocks everything behind it. Set a max receive count. |
| Route exhausted messages to a dead-letter queue | After max receives, the broker moves the message to a DLQ instead of dropping it. Alert on DLQ depth (any depth is a defect signal) and build the replay path before it is needed; a DLQ nobody drains is a slow-motion data loss. |
| Ack after processing, never before | Ack-then-process converts every consumer crash into silent message loss. Process-then-ack means redelivery on crash, which is why the next rule exists. |
| Consumers must be idempotent | At-least-once delivery makes duplicates normal operation, not an edge case: redelivery after a crash, after a slow ack, after a network blip. Dedupe by message ID or design the handler so double-processing converges to the same state. |

## Bulkheads and connection pools

| Practice | Detail |
|---|---|
| Partition pools per dependency | One shared pool means one slow dependency's calls accumulate until they hold every connection or thread, starving calls to healthy dependencies. Separate pools (bulkheads) contain the damage to the failing dependency's compartment. |
| Size pools with Little's Law, not folklore | Concurrent connections needed = throughput x latency: 200 req/s at 50ms is 10 in flight, so a pool of 15-20 covers it with headroom. Oversized pools hide leaks and can exceed the database's connection ceiling across replicas. |
| Bound the queue in front of the pool | An unbounded wait queue converts overload into unbounded latency and eventual OOM. A bounded queue that rejects fast (503 with `Retry-After`) hands the caller something its retry and fallback logic can act on. |
| Set acquisition timeouts on the pool itself | Waiting forever for a connection is the same pathology as a missing call timeout, one layer down. |

## Health checks

| Practice | Detail |
|---|---|
| Liveness answers "should this process be restarted?" | Check only in-process health (the event loop responds, no deadlock). Never check dependencies: if liveness pings the database, a database outage makes the orchestrator kill and restart every healthy pod in a loop, adding a restart storm to the outage. |
| Readiness answers "should traffic route here?" | Check the dependencies genuinely required to serve (database, required cache). Failing readiness removes the pod from rotation without killing it, which is exactly the right response to a dependency outage. |
| Keep checks cheap and non-cascading | A health endpoint that fans out to downstream health endpoints amplifies load exactly when the system is weakest. Check your own dependencies directly, shallowly, with a short timeout. |

## Testing resilience

The golden rule: a resilience pattern that has never seen the failure it guards is decoration, not protection. Every pattern above is verified by injecting the failure and asserting the designed response, never by assuming the library works.

| Pattern | Inject | Assert |
|---|---|---|
| Timeout | Dependency stub that never responds (fake timers) | Call fails at the budget, resources released |
| Retry | Stub failing twice then succeeding; stub failing with a 400 | Success after backoff; no retry on the 400, correct attempt count |
| Idempotency | Deliver the same request or message twice | Exactly one effect (one row, one charge) |
| Circuit breaker | Failure rate past threshold, then recovery | Opens (calls fail fast, dependency untouched), half-opens, closes |
| Fallback | Dependency down | Degraded response served, degradation metric emitted |
| DLQ | A message whose handler always throws | Lands in the DLQ after max receives, queue keeps flowing |

Unit level, fake timers plus a mocked failing dependency cover most of this. Integration level, inject real latency and partitions with a fault proxy (toxiproxy or equivalent) between the service and its dependency.

## Gotchas

- A successful-looking timeout may hide a completed write; the retry then duplicates it. Idempotency is not optional wherever retries touch writes.
- Retry layers multiply silently: the HTTP client, the service mesh, and the queue each "only retrying three times" is 27 attempts.
- Backoff without jitter synchronizes clients into retry waves that re-kill the recovering service; full jitter is the fix, not a refinement.
- A liveness probe that checks the database converts a database outage into a cluster-wide restart storm.
- A circuit breaker on a low-traffic path trips on statistical noise (3 failures out of 5 requests) and then false-opens a healthy dependency.
- The fallback path is code that runs only on the worst day; if it was never executed in a test, that day is also its first run.

## Sources

- [AWS Builders' Library: Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - the canonical treatment of retry amplification and full jitter, backed by AWS-scale evidence.
- [Google SRE book: Handling Overload / Addressing Cascading Failures](https://sre.google/sre-book/handling-overload/) - load shedding, per-dependency isolation, and why graceful degradation beats queuing.
- [Release It! (Nygard)](https://pragprog.com/titles/mnee2/release-it-second-edition/) - origin of the circuit breaker and bulkhead patterns as stability patterns.
- [Stripe: Designing robust and predictable APIs with idempotency](https://stripe.com/blog/idempotency) - the reference design for idempotency keys on retried writes.
- [Kubernetes docs: Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) - authoritative on the liveness vs readiness split.
