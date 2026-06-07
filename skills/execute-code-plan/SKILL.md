---
name: execute-code-plan
description: >-
  Use this skill to execute or carry out an already-approved code plan, running
  its tasks to completion through the subagent pipeline. Use when the user says
  "execute the plan", "run the plan", "implement this plan", "build out the
  plan", "carry out the code plan", "run the pipeline on this plan", or hands
  over an approved plan and says to build it. Do not use for creating or
  designing the plan (use create-code-plan, or the implementation-planner
  agent), for a single isolated task with no plan (dispatch the task-implementer
  agent directly), or when no approved plan exists yet.
---

## Purpose

Drive an approved code plan to completion by orchestrating the agent pipeline from the main conversation. This skill conducts; it does not implement. It dispatches `task-implementer` per plan task in dependency order, gates each checkpoint with `completion-verifier`, routes failures to `root-cause-investigator`, and runs `code-reviewer` and `security-reviewer` on the finished change. It stays thin because the agents own the methodology and already speak compatible output contracts; the skill's whole job is sequencing, gating, and honest failure handling. Do not begin until an approved plan exists, and do not let the orchestrator drift into doing the work itself.

## This must run in the main conversation

Subagents cannot spawn subagents. The orchestration that dispatches `task-implementer` and `completion-verifier` can only run where the Agent tool reaches them: the main thread. This skill therefore cannot be wrapped as an agent, and the main loop must not hand the orchestration to one. If you cannot spawn the pipeline agents, you are inside a subagent and must hand back to the main conversation.

## Workflow

Copy this checklist and track progress:

```text
Execute Plan:
- [ ] 1. Load, validate, and (if large or complex) adversarially review the plan
- [ ] 2. Establish a green baseline
- [ ] 3. Execute tasks in dependency order (parallel where marked)
- [ ] 4. Gate every checkpoint with completion-verifier
- [ ] 5. Final review pass (code + security)
- [ ] 6. Report; the user owns commit and merge
```

### 1. Load and validate the plan

Read the approved plan (from `create-code-plan` or the `implementation-planner` agent). Extract the task table: each task's description, files, verify command, dependencies, and any parallel marker. If no approved plan exists, stop and route to `create-code-plan`; executing an unwritten plan is improvising, not orchestrating. If the plan is stale against the current code (files moved, interfaces changed), surface that before starting rather than dispatching tasks against a map that no longer matches the territory. When the plan was written from a spec that is still available, reconcile the plan against it too; a plan that drifted from the spec gets faithfully executed into the wrong thing, and execution is the most expensive place to discover that divergence.

**Pre-flight review for large or complex plans.** Before establishing the baseline, dispatch a `plan-reviewer` for any plan that is large or complex: more than roughly six tasks, spanning multiple subsystems, touching production data or infrastructure, carrying a High-impact risk, or introducing a new architectural pattern or data model. Pass it the plan and the source spec or request. It returns severity-ranked findings and a verdict (approve, revise-then-approve, rework, or reject) against the goal, and never edits the plan. Treat a blocker finding or a rework/reject verdict as a stop: surface it and route the fix back through `create-code-plan` or to the user before any task runs, because a flaw caught in the plan is one cheap edit while the same flaw caught mid-execution is unwound work across every task built on it. Skip the pre-flight for small, single-subsystem plans; their create-code-plan step 6 self-review already covers them, and a fresh reviewer on a three-task plan is latency for no gain.

### 2. Establish a green baseline

Run the build and test suite once before touching anything, and record the result. A green baseline is what lets you attribute any later failure to the work. If the baseline is red, stop and route the existing failure to `fix` first, because you cannot tell your breakage from the pre-existing one on a red suite.

### 3. Execute tasks in dependency order

Walk the task graph. For each task, dispatch a `task-implementer` subagent with the full task text (description, files, verify command) plus the plan context it needs.

- **Parallelize only what the plan marks independent.** Spawn independent tasks in one message so they run concurrently. Tasks that share a contract wait for the task that defines it.
- **Isolate parallel tasks that touch the same files** with `isolation: worktree`, or they corrupt each other's edits.
- Collect each report. A `task-implementer` returns `Complete` with quoted evidence, or `Blocked` with what is missing. A `Blocked` report halts that branch; do not invent the missing piece in the main thread.

### 4. Gate every checkpoint with completion-verifier

After each task, or each phase checkpoint the plan defines, dispatch `completion-verifier` with the task's requirements and the implementer's report. It returns `Verified` or `Rejected` with per-requirement evidence it gathered itself.

- **Never advance past a `Rejected`.** A rejection means a requirement is unmet or the green is decorative; feed the verifier's findings to a fresh `task-implementer` and re-run. Bound this to two attempts, then stop and surface to the user. A verify-implement loop that will not converge is a sign the task or the plan is wrong, not something to grind on.
- When a task fails for an unclear reason rather than a named unmet requirement, dispatch `root-cause-investigator` to diagnose before re-implementing, so the retry targets the cause instead of guessing.

### 5. Final review pass

When every task is `Complete` and `Verified`, dispatch `code-reviewer` on the cumulative diff, and `security-reviewer` too when the change touched any sensitive surface (auth, input handling, secrets, external integrations). Route each confirmed finding back through a `task-implementer` the same way, then re-verify.

### 6. Report

Summarize for the user: tasks completed with their evidence, what each checkpoint verified, the review findings and their resolution, and the final suite state. Surface any task left `Blocked` and why. Do not commit or merge unless the plan or the user explicitly says to; the user owns git.

## Orchestration rules

- **Conduct, do not perform.** The agents do the work; the main thread sequences and gates. If you are editing files or writing tests in the main conversation, you have stopped orchestrating and lost the clean per-task context the pipeline exists to provide.
- **One task, one fresh implementer.** Each `task-implementer` gets isolated context by design; do not try to carry one agent across tasks.
- **A green checkpoint is the only gate forward**, meaning the verifier's verdict, never the implementer's own word.
- **Stop and surface to the user** on: no plan, a red baseline, a blocker the pipeline cannot resolve, a non-converging verify loop, or any scope decision the plan did not settle. The orchestrator escalates honestly; it does not paper over.

## Gotchas

- **This skill cannot be an agent.** The whole pipeline rests on spawning subagents, which only the main thread can do; wrapping the orchestrator as an agent breaks it silently at the first dispatch.
- **A red baseline poisons attribution.** Without step 2, the first test failure is unattributable and you burn a diagnosis cycle discovering it predated your work.
- **Parallel tasks on shared files corrupt silently.** Two implementers editing one file without worktree isolation overwrite each other; the plan's parallel marker is a claim of independence you verify, not assume.
- **The retry loop has a floor.** Re-dispatching forever on a `Rejected` is the orchestrator refusing to admit the task or plan is wrong. Two rounds, then escalate.
- **Review findings do not reopen the plan.** A `code-reviewer` finding becomes a new task routed through the pipeline, not a license to re-architect mid-execution; if a finding reveals the plan itself was wrong, stop and say so instead of improvising a rewrite.

## Example

A four-task plan (T1 schema, T2 endpoint depends on T1, T3 client depends on T1, T4 docs independent):

```text
1. Load plan; baseline `npm test` green (42 passing).
2. Dispatch T1 (schema) and T4 (docs) in parallel; both independent.
   T1 -> Complete (RED/GREEN quoted). T4 -> Complete.
3. Verify T1 and T4 -> both Verified.
4. T1 done, so dispatch T2 (endpoint) and T3 (client) in parallel,
   isolation: worktree (both import the new schema file).
   T2 -> Complete. T3 -> Blocked: "client SDK version in plan does not exist".
5. T3 blocked: stop that branch, surface the report to the user; do not guess a version.
6. Verify T2 -> Verified. Dispatch code-reviewer + security-reviewer on the T1+T2+T4 diff.
   One finding (missing authz check on the endpoint) -> new task -> implement -> re-verify.
7. Report: T1/T2/T4 complete and verified, review clean after the fix, T3 blocked pending
   the SDK question. Suite green (51 passing). No commit; the user owns git.
```
