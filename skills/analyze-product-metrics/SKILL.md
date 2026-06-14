---
name: analyze-product-metrics
description: >-
  Use this skill after a feature or product ships, to turn usage and product
  data into a ship / iterate / roll-back decision with statistical honesty. Use
  when the user says "did the launch work", "analyze the metrics", "read the A/B
  test", "is this experiment significant", "should we ship the variant",
  "funnel analysis", "retention / cohort analysis", "why did activation drop",
  "what's our north-star metric", "the feature is live, now what", or "are these
  numbers real". Do not use for generic tabular data crunching with no product
  decision attached (use analyze-data), for pre-launch market sizing from desk
  research (use research-market), for pre-build demand validation before anything
  exists (use validate-idea), or for building a dashboard or custom visualization
  as the deliverable (use visualize-data).
---

## Purpose

Close the post-launch loop: decide whether what shipped actually worked for users, and what to do next. The deliverable is a decision (ship wider / iterate / roll back / keep measuring) backed by evidence that survives scrutiny. This is the after-launch counterpart to `validate-idea` (which tests demand before you build); together they answer "are we building the right thing" before and after. The arithmetic itself belongs to `analyze-data`; this skill owns the product judgment around it: which metric the decision rides on, whether the measurement can be trusted, and what the result licenses you to do.

The rule the skill defends: **a number is not a result until you know what decision it changes and whether it is real.** A metric with no attached decision is a vanity metric; a result read without checking the measurement is a guess with a decimal point.

## Workflow

- [ ] 1. Frame the decision and pick the one metric it rides on (plus guardrails)
- [ ] 2. Validate the measurement before trusting any number
- [ ] 3. Read it out with the method that fits the question
- [ ] 4. Decide against the guardrails, and name the evidence

### 1. Frame the decision and pick the metric

State the decision first: what will you do differently depending on the result? If nothing, stop; there is no analysis to do. Then choose **one primary metric** that the decision rides on, tied to the activation or value moment the product spec named (the point where a user crosses from trying to getting value), not a convenient surface metric like page views. Name **guardrail metrics** that must not degrade for a win to count (revenue, latency, error rate, engagement breadth). For an experiment, pre-commit the decision rule (the lift that ships, the result that kills it) before looking at data, so a marginal result cannot be rationalized after the fact.

### 2. Validate the measurement

Before trusting any number, rule out the ways it lies. Garbage measurement means stop here; reporting a clean-looking result off broken instrumentation is worse than no result.

- **Power / sample size:** is the sample large enough to detect the effect you care about? An underpowered "no difference" is "we couldn't tell," not "they're equal." See `references/methods.md` for the sizing formula.
- **Duration:** did it run at least one to two full business cycles (usually a week or more), so day-of-week and novelty effects wash out?
- **Sample ratio mismatch (SRM):** in an A/B test, does the actual split match the intended split? A skewed split signals a broken assignment and invalidates the test.
- **Instrumentation sanity:** do totals reconcile with a known source? Did tracking change mid-window? A step that suddenly reads 0 or 100% is usually a logging bug, not behavior.

### 3. Read it out with the right method

Pick the method by the question, not habit:

| Question | Method | What the signal looks like |
|---|---|---|
| Where do users fall out on the way to value? | Funnel | The step with the steepest drop is the activation bottleneck |
| Does the value persist, or do they leave? | Cohort / retention | A retention curve that flattens (not decays to zero) means real, durable value |
| Did this change cause an improvement? | A/B test | Statistically significant AND practically meaningful lift, with guardrails intact |
| What might be going on? | Trend / segment cut | Hypotheses only; observational cuts cannot establish cause |

For A/B results, report the lift, the p-value or confidence interval, and the guardrail check together; a significant primary metric with a degraded guardrail is not a win. `references/methods.md` has the funnel, cohort, and significance mechanics.

### 4. Decide against the guardrails

Return one decision, with the evidence that forces it:

| Decision | Trigger |
|---|---|
| Ship wider | Significant, practically meaningful, guardrails intact |
| Iterate | Real signal but below the bar, or a guardrail concern worth fixing before rollout |
| Roll back | Significant negative effect, or a guardrail breach |
| Keep measuring | Underpowered or too short; a trend but not yet conclusive (extend, do not peek-and-ship) |

A "keep measuring" is a legitimate answer and far better than shipping on noise. Feed the result back into the next product cycle: a confirmed activation bottleneck is the next spec's problem statement.

## Anti-patterns

| Trap | Why it misleads | Instead |
|---|---|---|
| Statistical = practical | A 0.1% lift can be significant at huge N and still not worth the complexity | Require both significance and a lift that matters to the business |
| Peeking and stopping early | Checking repeatedly and stopping at the first significant blip inflates false positives | Fix the duration up front, or use a sequential-testing correction |
| Vanity metrics | Cumulative totals only ever go up; they cannot fail and so decide nothing | Use rates and per-cohort metrics that can move both ways |
| Aggregate hides the truth | A trend can reverse within every segment (Simpson's paradox) | Cut by the segments that matter before concluding |
| Causation from a trend | "Metric rose after launch" ignores seasonality and concurrent changes | Reserve causal claims for controlled experiments |

## Gotchas

- **The agent analyzes; it does not invent the data.** If no real data is provided, say what is needed (the events, the split, the window) and stop. Do not fabricate plausible numbers.
- **A flat A/B result is information, not failure.** "No detectable difference" correctly kills a change that added complexity for nothing; report it as a clean negative, not a disappointment to explain away.
- **Retention that decays to zero is not retention.** Durable value shows as a curve that flattens at a non-zero floor; a curve still heading to zero at the window's end means you have not yet seen anyone retain.
- **This closes the loop `validate-idea` opened.** A post-launch finding (activation drops at step 3) is the input to the next cycle's spec, not a dead-end report.

## Example

A team ships a redesigned onboarding and asks "did it work?"

1. **Decision + metric:** decision is keep-the-redesign or revert. Primary metric: activation rate (share of new signups who reach first value within 24h), tied to the spec's activation moment. Guardrails: 7-day retention, support-ticket rate.
2. **Validate:** A/B at 50/50, 9,000 users/arm over 10 days (covers two weekends), SRM check passes, activation events reconcile with the warehouse. Powered to detect a 2-point absolute lift.
3. **Read out (A/B):** activation 41% control vs 45% variant, +4 points, p = 0.003, 95% CI [+1.4, +6.6]. Guardrails: retention flat, tickets flat.
4. **Decide:** **Ship wider.** Significant and practically meaningful, no guardrail degradation. Next cycle: the funnel shows the remaining drop is at email verification, which becomes the next spec's problem statement.
