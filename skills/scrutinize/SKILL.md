---
name: scrutinize
description: >-
  Use this skill to scrutinize a plan, PR, diff, design doc, or proposed
  decision from an outsider's perspective: first whether it should exist at all
  or a simpler path reaches the same goal, then tracing the real end-to-end path
  to verify it does what it claims. Use when the user says "scrutinize this",
  "sanity-check this", "poke holes in this", "second opinion", or "is this the
  right approach". Do not use for line-level code review of a PR (use review-pull-request), for
  verifying a finished task meets its spec with fresh evidence (use the
  completion-verifier agent), for whole-system architecture evaluation (use
  audit-architecture), or for sharpening a vague request before any work exists
  (use clarify-ambiguity).
---

## Purpose

Stand outside a change and ask whether it should exist at all, then verify it actually does what it claims, end to end. This is intent-level scrutiny, not line-level review: the most valuable thing it produces is "there is a simpler way to reach the same goal", surfaced before any nitpick. A confident artifact is not a correct one, and a long session quietly turns its own assumptions into facts; scrutinize materializes the outsider who never had that context.

## Operating stance

- **Outsider.** Forget who wrote it and why they were sure. Read the artifact cold, as someone encountering the goal for the first time.
- **End to end, not diff-local.** The diff is the entry point, not the scope. Follow the real call graph, including the unchanged code on either side; bugs hide at the seams.
- **Adversarial.** Assume the author is overconfident. Bias toward disproving the change, not approving it. The goal is to find what is wrong, or to state plainly that you could not after a real attempt.
- **Concise, actionable, evidenced.** Every finding states what to change, why it matters, and the evidence that led you there. No restating the diff back, no filler.

## Workflow

Run these in order. Do not skip to the line-level pass.

### 1. Intent: what is this actually trying to do?

State the goal in one sentence, in your own words. If you cannot, the artifact is underspecified; say so and stop, because scrutinizing an unstated goal invents one.

Then the mandatory simpler-alternative pass. Before reading a single line for correctness, ask whether a smaller path reaches the same goal:

- Doing nothing: is the problem real and load-bearing, or speculative?
- Reusing something that already exists instead of adding new surface.
- A smaller change that solves 90% of the goal with 10% of the risk.
- Solving it at a different layer (config vs code, framework vs app, build vs runtime).

If a better alternative exists, name it explicitly with rationale, and lead with it. This is the highest-value output the skill produces; a slow code review that skips it has missed the point.

### 2. Trace: walk the actual path

For each behavior the change claims, trace it end to end through the real code, not just the diffed lines: entry point, call sites, branches taken, state mutated, exit and side effects. Include the surrounding unchanged code.

For a plan or design doc, trace the proposed flow against the existing system: where does it touch reality, and what does it assume that is not true? Note every place the trace surprises you (an unexpected branch, dead code reached, state you did not know existed). Surprises are signal, not noise.

### 3. Verify: does it do what it claims?

For each claim, answer explicitly:

- **Does the traced path actually produce that behavior?** Walk it: "Claims X. Path A to B to C. At C, [observation]. Therefore holds / does not hold."
- **What inputs or states break it?** Edge cases, concurrent callers, error and retry paths, partial failures, empty / null / huge / unicode inputs, ordering assumptions.
- **What does it silently change?** Performance, error semantics, observability, the contract other callers depend on, on-disk or on-wire format.
- **Do the tests exercise the traced path, or pass while skipping it?** Mocks that hide the bug, assertions on intermediate state, happy-path only.

### 4. Enumerate: mechanically walk every path

Steps 1 through 3 are attitude-driven: they question intent and motive, then chase down the specific inputs that would break a *claimed* behavior. This pass is method-driven and runs independent of any claim. Drop the adversary's voice and become a pure path tracer: do not judge whether the code is good or right, only list what it leaves unhandled.

Walk every branch and boundary in scope mechanically, not by intuition, and derive the edge classes from the artifact itself rather than a fixed list:

- **Control flow**: every conditional (the missing `else` / default), every loop bound (off-by-one, empty collection, single element), every early return, every `catch` and the error it does not catch.
- **Boundary values**: empty, null / undefined, zero, negative, one, the maximum, just over the maximum, overflow, the unicode or whitespace input.
- **State and ordering**: the uninitialized state, the partial-write state, the concurrent caller, the retry that runs twice, the out-of-order arrival.
- **Exit and failure**: every path that can throw, time out, or return early, and what is left half-done when it does.

For each path, decide one thing only: is it handled, explicitly, in scope? Report the unhandled ones with `file:line` and the trigger condition; discard the handled ones silently. No editorializing, no restating handled paths to show you looked. This pass is exhaustive where step 3 is targeted, and it catches the opposite defect: step 1's simpler-alternative question finds the wrong thing built, this pass finds the un-handled case in the right thing. Run both; neither subsumes the other.

### 5. Report

One tight section per finding, ordered by severity (blocker, then major, then nit):

- **Finding**: one specific sentence; cite `file:line` when applicable.
- **Why it matters**: the consequence, not the principle.
- **Evidence**: the trace step or input that exposes it.
- **Suggested change**: concrete and minimal.

Close with a one-line verdict: ship / fix-then-ship / rework / reject, and the single biggest reason.

## Rules

- **No rubber-stamps.** "LGTM" is not an output. If you genuinely find nothing, state what you traced and checked so the user can judge whether you covered the surface they cared about.
- **Cite or it did not happen.** Every claim about the code references a path, file, or line. No vague "this might break under load".
- **Keep claim and verification separate.** "The PR says X" and "I traced X and confirmed it" are different statements; never let the author's claim stand in for your verification.
- **The simpler-alternative pass is mandatory.** Spend one real breath on it even for small changes. Skip only when the user explicitly says "do not question scope".
- **Lead with structure, defer nits.** If step 1 or 2 surfaces a real problem, lead with it and drop or defer the style nits. A list of nits under a load-bearing flaw buries the thing that matters.
- **No flattery, no hedging.** "Great PR, but" adds nothing. State the finding.

## Gotchas

- **The simpler-alternative pass is the value.** Jumping straight to line-level correctness turns scrutinize into a slower review-pull-request. The question "should this exist" is the one no other skill asks.
- **Diff-local reading misses the seam bugs.** The unchanged code on either side of the change is in scope, because that is where the new behavior actually lands.
- **Attitude and enumeration catch different defects.** The adversarial passes find the wrong thing built; the path-enumeration pass finds the un-handled case in an otherwise sound change. A confident reviewer running on intuition skips the boring branch that holds the bug, which is exactly why step 4 is mechanical rather than adversarial.
- **Confidence is not correctness.** The artifact reads as right because its author was sure and you have absorbed their context. The adversarial stance exists to counter exactly that pull.
- **Social pressure manufactures rubber-stamps.** A polished artifact from a trusted author invites "looks good". Trace it anyway; the stamp is not a finding.
