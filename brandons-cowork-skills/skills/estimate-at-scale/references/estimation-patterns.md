# Estimation patterns beyond the arithmetic

Read when an estimate involves capacity (servers, threads, connections, concurrency), scaling, peak load, or availability, not just a flat cost or storage multiply. These are the techniques a quick mental estimate usually skips; they are where an estimate goes from "plausible" to "defensible."

## Contents

- [Little's Law and concurrency sizing](#littles-law-and-concurrency-sizing)
- [The bottleneck resource](#the-bottleneck-resource)
- [Sub-linear scaling (Universal Scalability Law)](#sub-linear-scaling-universal-scalability-law)
- [Peak, headroom, and the queueing wall](#peak-headroom-and-the-queueing-wall)
- [Growth over the horizon](#growth-over-the-horizon)
- [Two independent derivations](#two-independent-derivations)
- [Availability math](#availability-math)
- [Why the cloud is not infinitely scalable](#why-the-cloud-is-not-infinitely-scalable)

## Little's Law and concurrency sizing

The single most useful capacity identity. The average number of in-flight items in a stable system is the arrival rate times the average time each spends in the system:

```
concurrency (in-flight) = throughput (arrivals/sec) × latency (sec)
```

This is how a request rate plus a latency becomes a *count* of the things you must provision: concurrent requests, threads, connections, pool slots. Example: 2,000 req/s at 50 ms each means `2000 × 0.05 = 100` requests in flight at any instant, so roughly 100 worker slots are needed just to keep up at average load (before peak and headroom).

**Connection pool sizing:**

```
pool_size = peak_concurrent_requests × avg_hold_time / avg_request_time
```

In practice, measure p99 concurrency under peak load and add 20-30% headroom; cap below the downstream's own connection limit. Too few and requests queue (latency climbs, pool exhaustion looks like a database outage); too many and each connection costs memory on both ends and the database degrades.

**Thread pool sizing:**

- CPU-bound: `threads = number_of_cores`
- I/O-bound (most web work): `threads = cores × (1 + wait_time / service_time)`. Example: 8 cores, requests 80% waiting on I/O, `8 × (1 + 80/20) = 40` threads.

Always size from measured throughput, not a guess; find the pool size where added threads stop increasing throughput (the plateau) rather than going higher.

## The bottleneck resource

Capacity is not one number. A service's real ceiling is whichever resource saturates first as load rises: CPU, memory, disk IOPS, connection pool, thread pool, or network. Estimate each dimension and report the smallest ceiling; that resource *is* the capacity. A healthy average across resources hides the single one about to run out.

A capacity-model row per dimension makes the bottleneck visible:

| Dimension | Current | Limit | Action at limit |
|---|---|---|---|
| Requests/sec | 500 | 2,000 | Scale horizontally |
| CPU | 40% avg / 70% peak | 80% sustained | Add instances |
| DB connections | 30 active | 45 of 50 | Add read replicas |
| Disk I/O | 200 IOPS | 3,000 provisioned | Upgrade storage tier |

Typical first bottleneck by service type: API services hit the thread or connection pool; data-heavy services hit DB connections or query throughput; compute-heavy hit CPU; file processing hits disk I/O; real-time hits network or connection count.

## Sub-linear scaling (Universal Scalability Law)

Adding N machines almost never yields N times the throughput. The Universal Scalability Law models why:

```
C(N) = N / (1 + σ(N-1) + κN(N-1))
```

- **σ (contention):** the fraction of work that must serialize (a shared lock, a single writer). Pure contention gives Amdahl's Law, diminishing returns toward a ceiling.
- **κ (coherence):** the cost of keeping shared state consistent across nodes (cache invalidation, consensus). Once κ > 0, throughput eventually goes *retrograde*, adding machines makes it slower.

Estimation consequence: never extrapolate a small-scale throughput linearly to a large N. There is a ceiling, and past it more machines cost money and buy nothing. And some tiers do not scale horizontally at all, a single relational primary or any stateful service, so "add servers" does not apply to them.

## Peak, headroom, and the queueing wall

Two corrections a mean-based estimate misses:

- **Size for peak, not average.** Diurnal traffic peaks at roughly 2-5x its daily average; launches, virality, and batch jobs spike higher. Provision for the peak you must survive, derived as `average × peak_factor`.
- **Leave utilization headroom.** Never size to 100%. As utilization ρ approaches 1, queue wait grows like `ρ / (1 - ρ)`, so latency climbs gently to ~70% and then explodes: 80% utilization already roughly doubles queue time versus 50%, and 90% roughly quadruples it. Target ~70% sustained utilization so a normal fluctuation does not cross the wall. This is why soak tests run at 70-80% of measured capacity, not 100%.

When you size from *measured* numbers, beware coordinated omission: closed-loop load tools that wait for a response before sending the next request undercount latency at saturation, making a degrading system look stable. Size from open-loop (fixed-rate) measurements.

## Growth over the horizon

You provision ahead of demand, so estimate at the *end* of the provisioning window, not today. Apply the growth factor before sizing. Doubling-time shortcut: a quantity growing at g% per period doubles in about `70 / g` periods (20%/month doubles in ~3.5 months). A cost or capacity number with no growth applied is already obsolete the day you compute it.

## Two independent derivations

Derive the headline two ways and reconcile:

- **Top-down:** from population and behavior (DAU × actions/day / 86,400 → QPS).
- **Bottom-up:** from per-unit resource limits (per-instance throughput × instance count).

When the two agree to an order of magnitude, confidence is high. When they diverge, the gap localizes a bad assumption far more sharply than a single anchor check does.

## Availability math

Convert nines to a downtime budget, and remember how components compose:

| Availability | Downtime/year | Downtime/month |
|---|---|---|
| 99% (two nines) | 3.65 days | 7.3 hours |
| 99.9% (three nines) | 8.77 hours | 43.8 minutes |
| 99.99% (four nines) | 52.6 minutes | 4.4 minutes |
| 99.999% (five nines) | 5.26 minutes | 26 seconds |

- **Serial dependencies multiply:** a request crossing three independent services each at 99.9% sees `0.999^3 ≈ 99.7%`, worse than any one. Each added hard dependency lowers the ceiling.
- **Redundancy improves it:** two parallel replicas each at 99% give `1 - 0.01^2 = 99.99%` for the pair, if they truly fail independently (rarely fully true).

## Why the cloud is not infinitely scalable

Estimates that assume elastic infinity are wrong in expensive ways:

- Auto-scaling has 1-5 minute provisioning lag plus cold starts, so it cannot absorb an instant spike; capacity planning anticipates load, auto-scaling only reacts to it.
- Accounts have hard limits (instance counts, API rate limits) that cap "just add more."
- Relational primaries and stateful tiers do not scale horizontally; adding app servers there increases load on the same bottleneck.
- Infinite scale means infinite cost; the dollar figure is itself a capacity limit.
