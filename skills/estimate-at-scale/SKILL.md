---
name: estimate-at-scale
description: >-
  Use this skill to produce an order-of-magnitude estimate from rough scale
  parameters: monthly cost, storage, capacity, or throughput, given inputs like
  volume, request rate, data size, retention, and growth. It interrogates for
  the parameters first, then shows the assumptions and arithmetic behind the
  number. Use when the user says "estimate the cost", "how much would this cost
  at scale", "ballpark this", "napkin math", "rough numbers for", "what's the
  monthly cost if", "how much storage for X users", "size this", "how many servers or connections do
  I need", "size the thread or connection pool", "what QPS can this handle", or
  "capacity planning". Do not use
  for computing over a real dataset you already have (use analyze-data), for
  designing the system being estimated (use write-tech-spec), or for diagnosing
  why something is slow (use optimize-performance or fix).
---

## Purpose

Turn rough scale parameters into a defensible order-of-magnitude estimate, with the assumptions and the arithmetic exposed so every line can be challenged. The deliverable is not a precise figure; it is a number you can defend and a sense of what moves it. A number without stated assumptions is worse than no number, because it gets trusted at a precision the method never had. Two disciplines carry the whole skill: interrogate for the inputs before computing, and show the math instead of reporting a total.

## Interrogate first

Do not compute on guessed inputs. Pull the scale parameters from the user before doing any arithmetic, offering a recommended default for each so they confirm rather than compose (the same interrogation pattern clarify-ambiguity and the spec skills use). Batch independent questions; ask sequentially when one answer changes the next. If the user gives a range, carry the range through.

What to elicit depends on what is being estimated:

| Estimating | Pull these parameters |
|---|---|
| Cost | The resource and provider; volume and its unit; throughput; data size per unit and retention; growth horizon; the unit prices (look them up live or ask); the easily-forgotten line items below |
| Storage / capacity | Record or event count; bytes per record; index and overhead multiplier (2-4x for an indexed DB); retention window; replication factor; growth rate |
| Throughput | Events per unit time; peak-to-average ratio (a peak factor of 3-10x is common); work done per event |

If the user cannot give a parameter, carry it as an explicit assumption and widen the final range; never silently invent it.

## Workflow

### 1. Pin the unit economics

Establish the per-unit numbers the estimate multiplies: price per GB-month, price per million requests, bytes per record, requests per user per day. State each with its source: a known stable constant, a current provider price, or an explicit assumption the user can override. Look prices up live or ask for them; a cloud price recalled from memory is probably stale and is the fastest way to be confidently wrong.

### 2. Compute in steps, with units visible

Lay the arithmetic out line by line, carrying units that cancel (`GB/month x $/GB-month = $/month`). Keep one or two significant figures; the inputs do not justify more. Convert everything to a common time basis, usually monthly, so the terms add up.

### 3. Find the dominant term and sanity-check

Name the one or two terms that drive the number; that is where accuracy matters and where the user should push back, and the rest can stay sloppy. Then cross-check the result against a known anchor (a familiar bill, a published price per GB, a unit-economics figure). An estimate that lands far from a known anchor has a units bug; find it before reporting.

### 4. Report the number with its assumptions and sensitivity

Lead with the headline figure, rounded. Then the assumptions table, then the step-by-step breakdown, then a low / expected / high band and the one or two assumptions the answer is most sensitive to. If the user will re-run this with different inputs, offer to save it as a small reusable model (a table or a short script).

## Patterns beyond the arithmetic

A flat multiply (volume x unit price) is the easy half, and the half a strong estimator already does by reflex. Capacity, scaling, peak, and availability questions need techniques a quick mental pass skips; reach for these whenever the question is "how many" or "how big", not just "how much". Formulas and detail are in `references/estimation-patterns.md`.

- **Size capacity with Little's Law.** Concurrent in-flight work = throughput x latency. This is how a request rate plus a latency becomes a count of servers, threads, connections, or pool slots (2,000 req/s x 50 ms = 100 in flight). Estimating capacity without it is guessing.
- **Capacity is the bottleneck resource, not an average.** A service's ceiling is whichever of CPU, memory, IOPS, connections, threads, or network saturates first. Estimate each dimension and report the smallest; a healthy average hides the one resource about to run out.
- **Size for peak, then leave headroom.** Provision for peak (roughly 2-5x average for diurnal traffic, more for spikes), and never to 100% utilization: queue wait grows like rho/(1-rho), so latency stays flat to about 70% and then explodes. Target ~70% sustained.
- **Estimate at the horizon, not today.** Apply the growth factor over the provisioning window before sizing, since you provision ahead of demand; a number with no growth applied is obsolete on day one. Doubling time is about 70 / (percent growth per period).
- **Adding machines is sub-linear.** N servers rarely give Nx throughput; contention and coordination cause diminishing then retrograde returns (the Universal Scalability Law). Never extrapolate linearly to a large N, and never assume a relational primary or a stateful tier scales horizontally at all.
- **Derive the headline two independent ways.** Estimate top-down (from volume or DAU) and bottom-up (from per-resource limits) and reconcile; divergence localizes a bad assumption better than a single anchor check does.

## Handy stable constants

These do not drift, so they are safe to use from memory. Prices do drift and are not listed here on purpose; pin them live in step 1.

| Class | Values |
|---|---|
| Time | 1 day = 86,400 s; 1 month ~ 2.6M s; 1 year ~ 31.5M s |
| Throughput | 1/s ~ 86k/day ~ 2.6M/month; 100/s ~ 260M/month |
| Powers | 2^10 ~ 10^3; 2^20 ~ 10^6 (1 Mi); 2^30 ~ 10^9 (1 Gi) |
| Sizes | UUID 16 B; typical DB row 0.1-1 KB; 1 KB JSON event; 1 KB x 1M = 1 GB |
| Latency ladder | memory ref ~100 ns; SSD random read ~16 us; same-DC round trip ~0.5 ms; disk seek ~10 ms; cross-continent round trip ~150 ms |
| Availability | 99.9% ~ 8.8h down/yr; 99.99% ~ 53m/yr; serial deps multiply (0.999^3 ~ 99.7%); peak QPS ~ 2-5x average |
| Little's Law | in-flight = throughput x latency (1k req/s x 20 ms = 20 concurrent) |

## Gotchas

- **False precision is a tell that the method was abandoned.** "$4,213.87 per month" claims an accuracy rough inputs cannot support. Round to one or two significant figures; the honest output is "about $4K per month".
- **The interrogation is the skill.** Skipping it to produce a fast number manufactures false confidence, and a guessed input reported as a fact is the worst outcome. Confirm the parameters or carry them as stated assumptions.
- **Memorized cloud prices are stale.** Pin every price from current provider pricing or from the user. A number built on a remembered price is wrong in a way that looks authoritative.
- **Units bugs are the dominant failure mode.** GB versus GiB, per-second versus per-month, bits versus bytes, replication counted once versus per-replica. The anchor cross-check in step 3 exists specifically to catch them.
- **Cloud estimates miss the hidden line items.** Counting only compute and storage while forgetting egress, request charges, cross-AZ traffic, NAT, load balancers, and managed-service premiums underestimates badly. Prompt for them explicitly.
- **Spend effort on the dominant term only.** If egress is 80% of the bill, polishing the storage term to three figures is wasted; get the big term right and leave the small ones rough.

## Example

A worked cost estimate, parameters already confirmed with the user:

```text
Inputs (confirmed): 500 req/s average, each writing one 1 KB event,
retained 90 days, on object storage. Peak factor and compute excluded
by the user's scope (storage + request + egress only).

Unit economics (pinned live, not from memory):
- object storage: $0.023 / GB-month   (confirm against current pricing)
- PUT requests:   $0.005 / 1,000       (confirm)
- egress:         $0.09 / GB           (confirm), assume 10% of writes re-read

Volume:    500/s x 2.6M s/month        = 1.3B events/month
Storage:   1.3B x 1 KB = 1.3 TB/month written; 90-day retention ~ 3 months
           steady-state stored ~ 1.3 TB x 3 = ~4 TB
Storage $: 4,000 GB x $0.023            = ~$92 / month   (dominant? no)
Request $: 1.3B PUTs / 1,000 x $0.005   = ~$6,500 / month  <- DOMINANT TERM
Egress $:  10% x 1.3 TB = 130 GB x $0.09 = ~$12 / month

Headline: ~$6.6K / month, driven almost entirely by PUT request charges.
Sensitivity: batching events 10-to-1 cuts requests 10x and drops the
bill to ~$0.7K. The per-request charge, not storage, is the lever.
Range: ~$5K-8K depending on the real re-read rate and request pricing.
```

The storage term, the obvious thing to compute, turned out to be 1% of the bill; the request charge was the whole answer. That is the dominant-term check earning its place.
