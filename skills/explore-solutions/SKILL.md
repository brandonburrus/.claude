---
name: explore-solutions
description: >-
  Use this skill when a decision has more than one viable direction and you need
  to choose: generate several genuinely distinct approaches, weigh them against
  explicit criteria, and converge on a recommendation with the rejected
  alternatives named. Use when the user says "what are the options", "explore
  solutions", "which approach should we take", "help me decide between", or "buy
  vs build". Do not use for picking among approaches inside a code
  implementation plan (use create-code-plan), for documenting an
  already-chosen design (use write-tech-spec), for building a throwaway
  prototype to feel out one direction (use vibe-code), or for clarifying a vague
  problem before any solutions exist (use clarify-ambiguity).
---

## Purpose

When a decision has more than one viable direction, generate several genuinely distinct approaches, evaluate them against criteria that come from the problem, and converge on one with the rejected alternatives named. The deliverable is a decision and its reasoning, not code. The discipline is forcing real divergence before converging: the default failure is anchoring on the first idea and dressing minor variants up as alternatives to justify it.

## When this is the right altitude

This skill is for the decision itself, standing alone, before there is a plan or a spec. It covers non-code decisions too: tooling, architecture strategy, process, build versus buy. The adjacent skills handle neighboring altitudes, and reaching for the wrong one wastes the work:

- create-code-plan already weighs 2-3 approaches inside its design step, for a specific code implementation it is about to plan. If the deliverable is an implementation plan, use that; explore-solutions is for when the deliverable is just the decision.
- write-tech-spec records a design already chosen, in depth. Explore first to pick; then spec the winner. Do not re-run the exploration inside the spec.
- vibe-code answers a design question by building a throwaway prototype of one direction. Explore-solutions reasons across directions on paper first, and may recommend a spike as the tie-breaker.

## Workflow

### 1. Frame the decision

State the problem, the goal, and the hard constraints in a few lines. Name what actually makes this a fork: why the one obvious answer does not simply win. If after framing there is only one viable approach, say so and stop. Manufacturing alternatives to look thorough wastes the reader's time and yours.

### 2. Diverge

Generate at least three genuinely different approaches. Force real distance: they must differ in mechanism, layer, or trade-off posture, not be one idea with a parameter changed. Generators that produce real divergence:

- Do nothing, or defer: is the problem load-bearing right now?
- Reuse or buy what exists versus build new.
- A different layer: config, application code, infrastructure, or build time.
- A different posture on a core axis: sync versus async, strong versus eventual consistency, simple-now versus flexible-later.

Include the cheap, boring option explicitly. It is often the right one, and omitting it inflates every comparison against it.

### 3. Define the axes

Before scoring anything, name the three to six criteria that actually decide this case: for example time to ship, operational cost, blast radius and reversibility, fit with existing patterns, scaling headroom, team familiarity. Defining axes before scoring is what keeps the evaluation honest; axes invented afterward are just the winner's features written as criteria. Weight them to the situation: a throwaway prototype and a payments system rank reversibility very differently.

### 4. Evaluate

Score each approach against the axes honestly, including the real costs of the one you suspect will win. Lay it out as a table so the trade-offs are visible at a glance. Mark where an approach is disqualified by a hard constraint, which is different from merely scoring lower.

| Approach | Axis A | Axis B | Axis C | Notes |
|---|---|---|---|---|
| Do the simple thing | ... | ... | ... | ... |
| Build it properly | ... | ... | ... | ... |
| Buy / reuse | ... | ... | ... | ... |

### 5. Converge

Recommend one approach with the single biggest reason it wins. Name the strongest rejected alternative and why it lost; if the runner-up has a piece worth grafting in, say so. State the condition that would change the decision, so the reader knows what assumption it rests on. If two approaches are genuinely close and the tie-breaker is empirical (does it perform, does the API actually work that way), recommend a time-boxed spike with vibe-code rather than deliberating further on paper.

## Anti-patterns

- **Fake divergence.** Three variants of one idea is one option, not three. The test: if swapping any two approaches would not change the trade-off conversation, you have not actually diverged.
- **Anchoring.** Generating options to justify the one already chosen. Defining the axes before scoring, in step 3, is the guard against it.
- **Criteria reverse-engineered from the winner.** The axes come from the problem and its constraints, never from the features of the preferred answer.
- **Analysis paralysis.** This is a decision aid, not a research project. Three to five options, three to six axes, then converge. A close call is a signal to spike, not to keep deliberating.

## Gotchas

- **The boring option is a real option.** Leaving "do the simple thing" off the board makes every alternative look better than it is. Put it on the table even when you expect it to lose.
- **Weighting is situational, not universal.** The same approach wins or loses on reversibility depending entirely on the stakes; carry the weights from step 3, do not assume a house favorite.
- **A genuine tie means spike, not deliberate.** When two approaches are close and the deciding question is empirical, more paper analysis is procrastination; a time-boxed prototype settles it.
- **This precedes the plan and the spec.** Once the decision is made, hand the winner to create-code-plan or write-tech-spec. Re-opening the exploration there reruns work that is already done.
