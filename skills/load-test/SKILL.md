---
name: load-test
description: >-
  This skill should be used to empirically answer whether a system holds at target traffic by
  scripting and running load tests and reading the results against SLO targets. It applies when
  the user says "load test", "stress test", "soak test", "will it handle launch traffic", "how
  does it behave under load", "test at scale", "find the breaking point", or mentions k6,
  artillery, locust, gatling, or vegeta. It should not be used for estimating capacity by math
  with no measurement (use estimate-at-scale), for fixing an already-observed slow path (use
  optimize-performance), or for designing the SLOs themselves (use spec).
---

## Purpose

Answer "will this hold at target traffic?" with a measurement instead of a guess: script the load the system will actually face, run it against a production-like target, and read the percentiles against the SLO. estimate-at-scale predicts capacity by arithmetic and optimize-performance fixes slowness someone already observed; this skill sits between them and produces the evidence both consume. The deliverable is a verdict per target plus a saved, re-runnable scenario.

Two standing rules, in force for the entire engagement:

- **Never load test production.** A load test is a self-inflicted denial of service; run it against a production-like environment, and treat a request to point it at production as a mistake to push back on, not an instruction to follow.
- **Never test infrastructure the user does not own or have explicit authorization to test.** Third-party APIs, shared SaaS tenants, and anything behind someone else's rate limiter are off limits; from the target's side, unauthorized load testing is indistinguishable from an attack.

## Workflow

Copy this checklist and track progress:

```text
Load Test Progress:
- [ ] 1. Targets pinned (SLOs, RPS, peak factor, journeys)
- [ ] 2. Tool chosen (project's existing tool, else k6)
- [ ] 3. Scenario scripted (ramp profile, think time, data variety)
- [ ] 4. Target environment confirmed production-like and authorized
- [ ] 5. Results read (p95/p99, error rate, saturation, knee) against targets
- [ ] 6. Outcome routed and baseline saved
```

### 1. Derive the scenario from real targets

A load test without a target number produces a graph nobody can pass or fail. Pull the targets from what already exists: SLOs and latency budgets in the spec or the observability design, traffic projections, current production metrics. Where none exist, interrogate for them, offering a recommended default for each so the user confirms rather than composes:

- Steady-state RPS and the peak multiplier (2-5x average is typical for diurnal traffic; launches and campaigns spike harder)
- Latency target as a percentile ("p95 under 300ms"), never an average
- Acceptable error rate under load
- Payload shapes and sizes that match real requests
- The user journeys that matter, in realistic proportion (browse-heavy with occasional checkout, not uniform)

Script journeys, not lone endpoints. A lone-endpoint test exercises one handler in isolation; real traffic exercises sessions, the cache hierarchy, and the write path together, and the interactions between them are where systems actually fall over.

### 2. Pick the tool pragmatically

Honor what the project already uses: an existing artillery config, locustfile, gatling simulation, or vegeta script means extend it, for the same reason any project convention wins over preference. With no incumbent, default to k6: scriptable JS scenarios, first-class ramp stages, and built-in percentile thresholds that make the run pass or fail itself.

### 3. Script realistic load

| Element | Why it must be there |
|---|---|
| Warm-up stage at low rate | Cold caches, empty connection pools, and JIT make the first minutes unrepresentative; measuring them pollutes the percentiles |
| Gradual ramp | A step to full load hides where degradation starts; a ramp exposes the knee |
| Sustain at target | Stable p95/p99 need minutes of steady load, not a drive-by |
| Spike to peak | Tests surge behavior and recovery, which a smooth ramp never exercises |
| Think time between steps | Real users pause; zero think time turns N virtual users into a connection-recycling storm no real N users produce |
| Data variety | Parameterize IDs, search terms, and payloads from a data file; a loop of identical requests measures the cache, not the system |
| Thresholds encoding the SLO | The script should fail on its own numbers, so a regression run in CI needs no human to read the graph |

### 4. Run against a production-like target

Production-like means: same instance sizes and limits, production-like data volume (query planners choose different plans on empty tables), and the same topology, including the load balancer and TLS. Run the generator from a separate machine on a fat enough pipe, and watch server-side metrics (CPU, memory, queue depth, pool usage) during the run; the generator's view alone cannot distinguish a slow server from a saturated client.

### 5. Read the results correctly

- **p95/p99, never averages.** The average is dragged down by cache hits and hides the tail users complain about.
- **Error rate under load, and what the errors are.** A fast 503 is not throughput; rising errors with flat latency means load shedding, which may be the designed behavior or the failure, so check which.
- **Saturation signals server-side.** CPU, connection pool exhaustion, queue depth, memory growth; the resource that saturates first is the real capacity limit and the first target for scaling.
- **The knee of the curve.** Plot latency against arrival rate from the ramp: the point where latency departs from flat is the effective capacity. Throughput plateauing while latency climbs means the system is past it.
- **Verdict against each SLO target**, stated as pass or fail with the measured number next to the target.

### 6. Route the outcome

- **Fails latency with a hot path**: hand the offending journey and the server-side evidence to optimize-performance; its measure-fix-verify loop takes over from a measured baseline.
- **Capacity shortfall (knee below target traffic)**: feed the measured per-instance throughput back into estimate-at-scale's arithmetic and the spec's scaling design; a measured number always replaces an assumed one.
- **Passing run**: save the scenario, results, and environment description as a baseline artifact that prepare-for-deploy can reference and future runs can regress against.
- **Then soak**: run at 70-80% of the knee for hours to catch what short runs cannot: memory creep, fd and connection leaks, disk filling with logs, degrading GC behavior.

## Test shapes

| Shape | Profile | Question it answers |
|---|---|---|
| Smoke | 1-2 VUs, a minute | Does the script and the system work at all? |
| Load | Ramp to target, sustain | Does it meet the SLO at expected traffic? |
| Stress | Ramp past target until failure | Where is the knee, and what breaks first? |
| Spike | Sudden jump to peak, drop back | Does it survive the surge and recover after? |
| Soak | 70-80% of knee, hours | Does it leak or degrade over time? |

## Gotchas

- **Load-generator saturation masquerades as server latency.** A generator out of CPU, sockets, or bandwidth reports rising response times that are its own queuing. Watch generator-side resource usage, and prove headroom by adding a second generator: if reported latency drops, the first generator was the bottleneck.
- **Coordinated omission understates the tail.** A closed-loop generator that waits for each response before sending the next slows its own request rate exactly when the server degrades, silently dropping the worst samples. Prefer open-model arrival rates (k6 `constant-arrival-rate` / `ramping-arrival-rate`) when measuring latency under load.
- **Testing through a CDN or WAF measures the CDN, not the system.** Cache hits at the edge flatter the numbers, and the WAF may throttle or block the generator mid-run. Point the test at origin for capacity questions; test through the edge only when edge behavior is itself the question.
- **Localhost results mean nothing for production.** No real network, no TLS handshakes, no load balancer, dev-mode builds, and toy data volume. Localhost is for debugging the script (the smoke shape), never for the verdict.

## Example

A two-step journey in k6 with the realism elements from step 3:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// Data variety: without it, every iteration hits the same cache line
const products = new SharedArray('products', () =>
  JSON.parse(open('./products.json')));

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // warm-up: fill caches and pools
    { duration: '5m', target: 400 },  // ramp: watch for the knee on the way up
    { duration: '10m', target: 400 }, // sustain: percentiles come from here
    { duration: '1m', target: 800 },  // spike: 2x peak factor
    { duration: '2m', target: 0 },    // recovery
  ],
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<800'], // the SLO, encoded
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const product = products[Math.floor(Math.random() * products.length)];

  const res = http.get(`${__ENV.TARGET}/api/products/${product.id}`);
  check(res, { 'product loaded': (r) => r.status === 200 });
  sleep(1 + Math.random() * 2); // think time: users read before acting

  const cart = http.post(
    `${__ENV.TARGET}/api/cart`,
    JSON.stringify({ productId: product.id, qty: 1 }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  check(cart, { 'added to cart': (r) => r.status === 201 });
  sleep(2 + Math.random() * 3);
}
```

Run with `TARGET` pointing at the staging or perf environment, never production.
