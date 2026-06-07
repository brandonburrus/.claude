---
name: design-observability
description: >-
  Use this skill when designing how a service is monitored before an incident:
  choosing what metrics, logs, and traces to emit, defining SLIs/SLOs and error
  budgets, designing alerts and on-call paging, building service-health
  dashboards, or instrumenting code for visibility. Use when the user says "set up
  monitoring", "add observability", "what should we track", "define SLOs", "design
  the alerts", "we have no visibility into X", "we got paged for the wrong thing",
  or "alert fatigue". Do not use for running an active outage (use
  respond-to-incident), release-day readiness and the rollback plan (use
  prepare-for-deploy), making something measured faster (use optimize-performance),
  or writing the post-incident RCA (use write-post-mortem).
---

## Purpose

Design the instrumentation, signals, and alerts that let you answer one question fast when a service misbehaves: is it broken, where, and why. The deliverable is the observability design, what to emit, what to alert on, and what each dashboard answers, built before the incident, because the time to discover you have no visibility into a failure is never during the failure. Observability is the ability to ask new questions of a running system without shipping new code; the design goal is that ability, not the volume of data collected.

## Workflow

### 1. Start from the questions, not the data

List the questions an on-call engineer will actually ask at 3am ("are users seeing errors", "is it us or a dependency", "which release introduced this", "is the queue backing up") and design backward to the minimum signals that answer them. Collecting everything and hoping the answer is in there produces high bills and low insight; an unasked metric is cost without value.

### 2. Choose the signal for each question

Three signal types, each with a job. Most services need all three, scoped tightly:

| Signal | Answers | Design discipline |
|---|---|---|
| Metrics | "Is it broken, and how badly" (rates, ratios, percentiles over time) | Cheap and aggregatable; keep label cardinality low (see gotchas) |
| Logs | "What exactly happened in this one case" | Structured (key-value, not prose), with a correlation id; never log secrets or PII |
| Traces | "Where in the request path did the time or the error go" | Propagate one trace id across service boundaries; sample to control cost |

### 3. Instrument at the boundaries with a standard signal set

Cover request-driven work with the RED method and resources with USE, which together are the four golden signals:

- **RED** (per endpoint, queue consumer, and outbound dependency call): Rate, Errors, Duration (as a latency distribution, p50/p95/p99, never just the mean).
- **USE** (per resource: CPU, memory, connection pool, disk, queue): Utilization, Saturation, Errors.
- Instrument every boundary where work enters or leaves the service (request handlers, external API calls, DB queries, queue publish/consume), because that is where failures and latency originate, and propagate a correlation/trace id through all of them so logs and traces from one request join up.

### 4. Design alerts on symptoms, not causes

Every alert answers "is a human needed now". Alert on user-visible symptoms (error rate, latency SLO burn, the queue not draining), not on internal causes (CPU at 90 percent), because high CPU with healthy latency needs no one and a cause-alert that fires without user impact is exactly how alert fatigue starts.

- **Page** only on what should wake someone: a symptom that is hurting users now or imminently. Everything else is a ticket or a dashboard, not a page.
- **Every paging alert has a runbook**: what it means, how to confirm, first mitigations. An alert with no documented action is an interrupt with no payload.
- **Tune for the cost of a miss vs a false page.** A noisy alert that is routinely ignored is worse than no alert, because it trains the team to ignore the next real one.

### 5. Define SLIs, SLOs, and error budgets

An SLI is a good-event ratio (requests served under 300ms / total; successful requests / total). An SLO is the target for that ratio over a window (99.9 percent over 30 days). The error budget is the allowed failure (0.1 percent); it converts reliability into a quantity you can spend and makes "is this reliable enough" a measurement instead of an argument. Alert on the budget burn rate (a fast multi-window burn pages; a slow burn tickets), not on every individual error, so the page correlates with real budget risk rather than noise.

### 6. Design the dashboards around drill-down

One top-level service-health dashboard shows the four golden signals at a glance: is the service healthy right now. From there, drill-down dashboards per dependency and resource answer "is it us or something downstream". Design the top dashboard to be readable in five seconds during an incident; a dashboard with forty panels and no hierarchy is unreadable exactly when it is needed.

### 7. Verify the observability actually works

Prove it before trusting it: inject a synthetic failure (return errors from one dependency, add latency) in a safe environment and confirm the metric moves, the alert fires, the trace shows where, and the runbook leads to the cause. An alert that has never fired in a test is an untested code path on the most important day.

## Example: an SLO with a multi-window burn-rate alert

```yaml
# A 99.9%-success SLO over 30 days, alerted by error-budget burn rate.
# Fast burn (2% of the budget in 1h) pages; slow burn (10% in 6h) tickets.
slo:
  sli: sum(rate(http_requests_total{status!~"5.."}[5m]))
       / sum(rate(http_requests_total[5m]))
  objective: 0.999
  window: 30d

alerts:
  - name: ErrorBudgetFastBurn          # symptom-based, page-worthy
    expr: |
      (1 - (sum(rate(http_requests_total{status!~"5.."}[1h]))
            / sum(rate(http_requests_total[1h])))) > (14.4 * 0.001)
    for: 5m
    severity: page
    runbook: https://runbooks/internal/error-budget-fast-burn
  - name: ErrorBudgetSlowBurn          # erodes budget over time, ticket
    expr: |
      (1 - (sum(rate(http_requests_total{status!~"5.."}[6h]))
            / sum(rate(http_requests_total[6h])))) > (6 * 0.001)
    for: 30m
    severity: ticket
```

The page fires on a fast burn that threatens the budget within hours; the slow burn opens a ticket. Both derive from the same SLI, so the alert and the reliability target never disagree.

## Gotchas

- **Label cardinality explodes metric stores.** A metric labeled by `user_id`, request id, or full URL path creates a separate time series per value and can take the metrics backend down. Labels are for bounded, low-cardinality dimensions (endpoint, status class, region); high-cardinality identifiers belong in logs and traces, not metric labels.
- **Cause-based alerts are the source of alert fatigue.** Paging on CPU, memory, or a restart count fires constantly without user impact, and a team that silences pages stops seeing the real one. Alert on the symptom (latency, errors, budget burn); investigate the cause after the page, using the dashboards.
- **Data without an SLO is noise.** Metrics and dashboards with no target answer "what is the number" but not "is that bad". The SLO is what turns a latency graph into a decision; without it, every graph needs a human to interpret in real time.
- **Logs and traces leak secrets and PII by default.** A logged request body, auth header, or full error object routinely captures tokens and personal data into a store with looser access than the database. Redact at the logging boundary, and treat a secret that reached the log as published.
- **A missing correlation id makes traces and logs un-joinable.** Without one id propagated across boundaries, you have three disconnected signals and cannot follow a single failing request through the system. Establish and propagate it first; it is the spine the rest hangs on.
- **Monitoring only the happy path hides the failures that matter.** Instrumenting successful requests and not error rates, timeouts, retries, or saturation means the dashboards stay green through the incident. Emit and alert on the failure signals explicitly, because those are the ones an outage moves.
- **100 percent trace sampling is expensive and rarely needed.** Tracing every request costs storage and throughput; sample (head or tail), keeping all error traces and a fraction of successes, so cost scales with insight rather than traffic.
