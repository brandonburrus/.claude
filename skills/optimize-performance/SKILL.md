---
name: optimize-performance
description: >-
  Use this skill when making code, pages, queries, or services faster, when
  performance budgets or SLAs exist, when Core Web Vitals need improvement, or
  when the user says "make this faster", "this is slow", "optimize this",
  "reduce the bundle size", "speed up this query", or "improve load time". Do
  not use for diagnosing a performance regression where something got slow
  after a change (use fix to find the root cause first), or for refactoring
  for readability without a speed goal (use refactor-code).
---

## Purpose

Make things measurably faster through a measure, identify, fix, verify, guard loop. The Iron Rule: **no optimization without a measurement showing the bottleneck.** Unmeasured optimization is guessing; it routinely speeds up code that was never the problem, adds permanent complexity, and leaves the actual bottleneck untouched. "This optimization is obvious" is the precise feeling that precedes optimizing the wrong thing.

## Workflow

Copy this checklist and track progress:

```text
Perf Progress:
- [ ] 1. Baseline measured (numbers recorded)
- [ ] 2. Bottleneck identified from data
- [ ] 3. Fix applied to that bottleneck
- [ ] 4. Re-measured under same conditions
- [ ] 5. Regression guard in place
```

### 1. Route the symptom, then measure a baseline

Triage the observed symptom to its first suspects and the right tool before recording numbers; pointing the wrong instrument (synthetic where you needed RUM, wall-clock where you needed a profiler) wastes the baseline and the comparison built on it.

| Symptom | First suspects | Where/how to measure |
|---|---|---|
| Slow first page load | Bundle size, render-blocking resources, slow TTFB (then: server, not frontend) | DevTools Network waterfall (TTFB vs transfer); bundle analyzer |
| Slow LCP | Oversized or late-discovered hero image, render-blocking CSS/JS, slow server | Lighthouse synthetic + CrUX/RUM for field LCP; trace the LCP element |
| Poor INP / janky interaction | Long main-thread tasks (>50ms), oversized DOM updates, layout thrashing | Field-first (CrUX/RUM), then DevTools Performance trace while interacting, throttled CPU |
| High CLS | Images without dimensions, late-loading embeds, font swaps | DevTools Performance layout-shift attribution; field CLS in RUM |
| One endpoint slow | N+1 queries, missing index, unbounded fetch | Query log with timing, `EXPLAIN ANALYZE`; APM trace of the path |
| Everything slow | Connection pool exhaustion, memory pressure, GC, an external dependency | APM dashboards, pool and GC metrics, p95 latency |
| Intermittent slowness | Lock contention, GC pauses, cold caches, a flaky upstream | p95/p99 over time, GC and lock traces, upstream latency |
| Job or script slow | The hot function is rarely the one that looks ugly | A profiler (`python -m cProfile`, `node --cpu-prof`, `go pprof`), not wall-clock guesses |

General rules once routed:

- Synthetic (Lighthouse, DevTools trace) finds and reproduces issues; RUM (web-vitals library, CrUX) proves users felt the fix. Use both where they apply.
- Measure on representative conditions: production-like data volume, throttled network and CPU for web, release builds not dev builds.

### 2. Identify the bottleneck from the data

The profile decides, not intuition: optimize the top of the profile, treat the routing table's first suspects as a starting hypothesis, and discard it the moment real measurement data contradicts it.

### 3. Fix the measured bottleneck

The recurring offenders, most of the wins live here:

| Anti-pattern | Fix |
|---|---|
| N+1 queries | One query with a join or include; batch lookups (DataLoader pattern) |
| Unbounded fetching | Pagination and limits at the query, not after it |
| Missing index | Index the filtered/joined column; confirm with the query plan |
| Repeated identical work | Cache with an explicit TTL and invalidation story; HTTP caching for static assets |
| Oversized bundle | Route-level code splitting, lazy-load heavy rarely-used features; check what tree-shaking actually shipped |
| Unoptimized hero image | Modern format, responsive sizes, explicit dimensions, fetchpriority high; lazy-load only below the fold |
| Re-render storms (React) | Stable references, memo on expensive subtrees only, derive instead of syncing state |
| Sync work blocking the loop | Move CPU-heavy work off the main thread or hot path; stream instead of buffering |
| Algorithmic complexity | The O(n squared) hiding behind nested loops or per-item scans; fix the algorithm before micro-tuning the code |

One fix at a time; combined fixes make the re-measurement unattributable.

When the bottleneck is a slow TTFB (over ~800ms), it is not atomic: split it in the Network waterfall and fix the dominant segment, because "the server is slow" is usually only one of four segments.

| TTFB segment | Targeted fix |
|---|---|
| DNS resolution | `dns-prefetch` or `preconnect` for known origins |
| TCP + TLS handshake | HTTP/2 or HTTP/3, connection keep-alive and reuse, edge deployment |
| Server processing | Profile the backend, fix slow queries, add caching |

### 4. Verify with the same yardstick

Re-measure under the same conditions as the baseline and report both numbers ("LCP 4.1s to 2.2s", "p95 480ms to 140ms"). An optimization without before/after numbers is a claim. Tests still pass: an optimization that changed behavior is a bug with good latency, and behavior includes error handling and result ordering.

### 5. Guard against regression

Wins erode silently. Pin them: a bundle-size budget in CI, a Lighthouse CI threshold, a query-count assertion in a test (N+1 detection), an alert on the p95. Pick the cheapest guard that would have caught the original problem. Typical budget shape: initial JS under 200KB gzipped, API p95 under 200ms, LCP under 2.5s; adjust to the project's reality and write them down.

## Core Web Vitals targets

| Metric | Good | Poor |
|---|---|---|
| LCP (Largest Contentful Paint) | <= 2.5s | > 4.0s |
| INP (Interaction to Next Paint) | <= 200ms | > 500ms |
| CLS (Cumulative Layout Shift) | <= 0.1 | > 0.25 |

For the per-layer checklists (images, JS, fonts, network, rendering, DB, API, infra), measurement commands, and the anti-pattern table, read `references/performance.md`.

## Rationalizations

| Excuse | Reality |
|---|---|
| "This optimization is obvious" | If you did not measure, you do not know. The obvious-looking code is frequently not the hot path |
| "It's fast on my machine" | Your machine has a warm cache, fast CPU, and local network. Profile representative hardware, data, and network |
| "Users won't notice 100ms" | Conversion research says they do; latency compounds across the request chain |
| "The framework handles performance" | Frameworks cannot fix your N+1 queries, your bundle, or your algorithm |
| "We'll optimize later" | Architecture-level performance debt (chatty APIs, missing pagination) compounds; fix structural anti-patterns now, defer micro-tuning |

## Red flags

- Any change justified by "should be faster" with no profile or numbers
- `memo`/`useMemo`/caching sprinkled everywhere; blanket memoization costs memory and hides the real problem exactly like blanket optimism
- Optimizing a dev build, unthrottled, on empty data
- Measuring once, after the fix only
- A "performance PR" that also refactors and renames; the measurement can no longer attribute the win

## Gotchas

- **Regressions route to fix first.** "It got slow after Tuesday's deploy" is a root-cause hunt (what changed?), not an optimization pass; optimizing around an unidentified regression buries it. Once fix identifies the cause, this skill's loop applies to the repair.
- **The bottleneck moves.** After fixing the top of the profile, re-profile before fixing what was second; the distribution changes and yesterday's number two may now be noise.
- **Caches are a correctness liability bought for speed.** Every cache added needs an invalidation answer and a stampede answer (what happens when it expires under load), or the perf fix becomes next month's data bug.
- **p95 beats average.** Averages hide the slow tail users actually complain about; measure and report percentiles for anything server-side.
