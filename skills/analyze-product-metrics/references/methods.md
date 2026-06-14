# Product-metric methods

Read when validating a measurement (workflow step 2) or reading out a result (step 3). The arithmetic can be handed to `analyze-data`; this file is the product-specific method and the traps.

## Contents

- [Sample size and power](#sample-size-and-power)
- [A/B significance](#ab-significance)
- [Funnel analysis](#funnel-analysis)
- [Cohort and retention](#cohort-and-retention)
- [Measurement-validity checks](#measurement-validity-checks)

## Sample size and power

Before a test, estimate the sample needed to detect the smallest effect worth acting on (the minimum detectable effect, MDE). For a comparison of two proportions at 95% confidence and 80% power:

```
n per arm ~= (Z_alpha/2 + Z_beta)^2 * 2 * p * (1 - p) / MDE^2
```

with `Z_alpha/2 = 1.96`, `Z_beta = 0.84`, `p` the baseline rate, and `MDE` the absolute lift you want to catch. The smaller the effect you care about, the quadratically larger the sample. After the test, an inconclusive result on an underpowered sample means "could not tell," never "no difference."

## A/B significance

Report three things together, never the first alone:

- **Lift:** relative `(variant - control) / control`, and absolute `variant - control`. Absolute is what guardrails and decisions usually hang on.
- **Significance:** a two-proportion z-test (or chi-squared) p-value, or better, the 95% confidence interval on the difference. A CI that excludes 0 is significant; its width tells you how precise the estimate is.
- **Guardrails:** the metrics that must not move the wrong way. A significant primary win with a degraded guardrail is not a win.

Two failure modes that manufacture false wins: **peeking** (checking repeatedly and stopping at the first significant reading inflates the false-positive rate far above 5%; fix the horizon up front or apply a sequential correction), and **multiple comparisons** (testing many metrics or segments and celebrating whichever crossed 0.05; correct for the number of comparisons or pre-register the primary).

## Funnel analysis

Define the ordered steps from entry to the value moment. For each step compute the conversion to the next and the absolute users lost. The single steepest drop is the activation bottleneck and the highest-leverage place to act. Watch for: steps that are actually optional (inflate apparent drop), and users who skip steps (linear funnels misrepresent non-linear products). A funnel answers "where," not "why"; pair the worst step with `validate-idea`-style observation or session review to learn the why.

## Cohort and retention

Group users by the period they joined (the cohort), then track a metric across the periods since join. Two readings:

- **Retention curve shape:** plot the share of each cohort still active at week 1, 2, 3, and so on. A curve that **flattens at a non-zero floor** means a segment found durable value (the floor is your real retained base). A curve still **decaying toward zero** at the window's end means no one has retained yet, regardless of a healthy week-1 number.
- **Cohort comparison:** newer cohorts retaining better than older ones is evidence a change improved the product; worse means a regression or a shift in who is signing up.

A retention heatmap (cohorts as rows, periods-since-join as columns) makes both readings visible at once.

## Measurement-validity checks

Run these before trusting any number:

- **SRM (sample ratio mismatch):** does the observed assignment split match the intended split (a chi-squared test against the expected ratio)? A mismatch means broken randomization; the test is invalid until fixed.
- **Reconciliation:** do totals match an independent source (the warehouse, billing)? A metric that does not reconcile is an instrumentation bug.
- **Tracking change mid-window:** was an event renamed, added, or fixed during the period? That creates a step change that looks like behavior.
- **Novelty and primacy:** early behavior after a visible change is unrepresentative; either run long enough to wash it out, or analyze only post-stabilization data.
- **Simpson's paradox:** a direction in the aggregate can reverse within every segment. If a result drives a real decision, confirm it holds in the segments that matter.
