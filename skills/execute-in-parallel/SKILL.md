---
name: execute-in-parallel
description: >-
  Use this skill to structure work across multiple concurrent subagents for speed
  or quality: fanning out genuinely independent tasks, generating several
  competing solutions and judging them, or adversarially verifying findings with
  independent skeptics. Use when the user says "run these in parallel",
  "parallelize this", "fan out agents", "do these at the same time", "generate a
  few versions and pick the best", "competitive generation", "judge multiple
  approaches", "use worktrees for parallel work", or "speed this up with
  concurrency". Do not use for executing an already-approved code plan's
  implement/verify pipeline (use execute-code-plan), for the line-by-line
  mechanics of authoring a Workflow orchestration script (that is the Workflow
  tool's own surface), or for reasoning through solution options as a one-time
  analytical decision without spawning agents (use explore-solutions).
---

## Purpose

Decide whether work should run concurrently, and if so structure it so the concurrency actually pays off instead of corrupting state or wasting wall-clock. The deliverable is a correct dispatch: the right tasks in parallel, isolated where they would collide, with verification built in. Two distinct wins are on the table, parallelism buys **speed** (independent work at once) and competitive generation buys **quality** (several attempts, judged, beats one attempt iterated); pick for the win you need.

The rule the skill defends: **parallelize only genuinely independent work, and isolate anything that writes.** The failure mode is false independence, two agents that share hidden state and quietly corrupt each other's results or the same files.

## When to parallelize

| Situation | Run it |
|---|---|
| 2+ tasks with no shared state and no ordering between them | Parallel fan-out |
| Tasks where each depends on the previous one's output | Serial (or a pipeline; see below) |
| One task, wide solution space, low confidence in the approach | Competitive generation (parallel attempts, then judge) |
| A finding or claim whose correctness is load-bearing | Adversarial verification (parallel skeptics) |
| Discovery of unknown size (bugs, edge cases, sources) | Loop-until-dry rounds of parallel finders |

If tasks have dependencies but each item flows through the same stages, prefer a **pipeline** (each item moves to its next stage as soon as it is ready) over a **barrier** (wait for all of stage N before any of stage N+1). A barrier is only correct when stage N+1 genuinely needs every stage-N result at once (dedup across the full set, an early-exit on zero results, cross-item comparison). Barriers waste the fast items' time; default to the pipeline.

## The patterns

- **Independent fan-out.** Dispatch the tasks concurrently and collect results. If two tasks could write the same files, give each its own git worktree so they cannot collide; worktree setup has real cost, so use it only when writes would actually conflict, not for read-only work.
- **Competitive generation.** For a decision with a wide solution space, spawn several agents from genuinely different angles (e.g. simplest-thing-first, risk-first, user-first), score them with independent judges, then synthesize from the winner while grafting the best ideas from the runners-up. This beats one-attempt-iterated precisely because the attempts explore the space instead of refining one guess.
- **Adversarial verification.** For a load-bearing finding, spawn an odd number of independent skeptics each prompted to *refute* it, defaulting to "refuted" when uncertain; keep the finding only if a majority fail to refute. When a finding can fail in more than one way, give each verifier a distinct lens (correctness, security, does-it-reproduce) rather than running identical refuters.
- **Loop-until-dry.** For unknown-size discovery, run rounds of parallel finders until N consecutive rounds surface nothing new; dedup each round against everything seen, not just the kept results, or rejected items reappear forever.

## Mechanism

For a handful of independent dispatches, plain concurrent subagent calls (multiple in one message) suffice. For deterministic orchestration, loops, conditionals, fan-out over many items, judged stages, the Workflow tool is the right harness, but it is opt-in: only reach for it when the user has explicitly asked for multi-agent orchestration, and otherwise describe what it would do and let them choose. A dispatched subagent cannot itself fan out to sub-subagents; to widen coverage, dispatch more agents from the main loop and synthesize, rather than asking one agent to spawn others.

## Gotchas

- **False independence corrupts silently.** Two "independent" tasks that touch the same file, the same database, or the same global state are not independent. Verify the no-shared-state claim before parallelizing; when writes overlap, worktree-isolate or serialize.
- **Barriers waste wall-clock.** Synchronizing every stage when only one stage needs the full set means the fast items idle waiting for the slowest. Use a pipeline unless a stage genuinely needs all prior results together.
- **Worktrees are not free.** Each one costs setup time and disk. Use isolation for parallel writers; for read-only fan-out (review, research, search) it is pure overhead.
- **Silent caps read as full coverage.** If you bound the work (top-N, no retries, sampling), say so in the result. An unstated cap makes partial coverage look complete.
- **Competitive generation needs genuinely distinct attempts.** N agents given the same prompt produce N near-identical answers and waste the budget. Vary the angle, the constraint, or the starting assumption per attempt, or the judging has nothing to choose between.

## Example

Task: "review this PR for bugs across correctness, security, and performance, and don't report noise."

- **Structure:** a pipeline over the three review dimensions. Stage 1: three reviewers run concurrently, one per dimension (independent, read-only, no worktrees needed). Stage 2: each finding flows immediately into adversarial verification, three skeptics per finding prompted to refute, kept only if a majority cannot. Dimension "bugs" findings verify while "performance" is still reviewing, no barrier.
- **Why not a barrier:** the dimensions do not need each other's results, so synchronizing them would only make the fast reviewer wait. The one place a barrier would be correct is if you wanted to dedup overlapping findings across all three dimensions before the expensive verification step, then collect-all-then-verify is justified.
- **Result:** confirmed findings only, produced in roughly the time of the slowest single dimension rather than the sum of all three.
