---
name: generate-test-cases
description: >-
  This skill should be used when enumerating or planning what test cases to write for a
  function, module, feature, or spec, covering golden path, error, and edge cases as a
  reviewed case matrix before any test code exists. It applies when the user says "what
  should we test", "list the edge cases", "enumerate test cases", "plan the test
  coverage", or "what cases am I missing", or wants an exhaustive coverage plan up front.
  It should not be used to write or run the actual test files (use test-writer), to drive
  test-first implementation (use follow-tdd), or to audit an existing suite against
  requirements (use test-coverage-requirement-auditor).
---

## Purpose

Turn a target (a function, module, feature, or spec) into an exhaustive, reviewed plan of test cases covering golden path, error, and edge cases, by dispatching the `test-case-planner` agent to enumerate them in an isolated context and then reviewing what it returns. The deliverable is a reviewed case matrix, not test code: implementation is a deliberate handoff to `follow-tdd` or the `test-writer` agent. Two standing rules hold for the whole run:

- **Run this from the main conversation.** It dispatches a subagent, and subagents cannot dispatch subagents; wrapped inside another agent it has nothing to call.
- **Do not dispatch on a vague target.** The agent cannot ask you anything, so a thin brief yields a generic, shallow list. Scope the target first (step 1); a repaired brief is cheaper than a discarded plan.

## Workflow

```text
Generate test cases:
- [ ] 1. Resolve and scope the target
- [ ] 2. Build the self-contained brief
- [ ] 3. Dispatch test-case-planner
- [ ] 4. Review and tighten the returned plan
- [ ] 5. Hand off for implementation
```

### 1. Resolve and scope the target

Identify the exact unit(s) under test (file paths, the function or module, or the spec text) and gather the behaviors and any acceptance criteria they must satisfy. If the target is ambiguous or its intended behavior is unclear, ask the user now, because the agent cannot recover from a vague brief and will pad the gap with generic cases.

### 2. Build the self-contained brief

Fill this brief; it is everything the agent gets, so it must stand alone.

```text
Target: <file paths / function / module / spec text>
Known behaviors and acceptance criteria: <the behaviors that must hold>
Language / stack: <so the agent reads the code in the right idiom>
Output: a Test-Case Plan only. Enumerate golden path, error, and edge cases
per behavior; walk your edge-case taxonomy. Return no test code and no files.
```

### 3. Dispatch test-case-planner

Dispatch the `test-case-planner` agent (Agent tool, `subagent_type: test-case-planner`) with the brief. The exhaustive sweep runs in the agent's own context so it never floods this conversation; you get back only the finished plan.

### 4. Review and tighten the returned plan

The plan is a draft, not gospel. Enforce the floor and cut the noise (see the review gate below): at least golden + error + edge per behavior, an error and an edge case per branch, every case able to fail and naming what it proves. Drop restatements of the implementation and duplicates. If an area came back thin, re-dispatch the agent scoped to just that area rather than inventing cases yourself, and repeat until coverage is adequate.

### 5. Hand off for implementation

Present the reviewed plan. This skill stops here; offer the two implementation paths and let the user pick:

- `follow-tdd` to implement one failing test at a time (best when the code is being written now).
- the `test-writer` agent to write the files for code that already exists.

## Review gate: a real case vs noise

Judge every returned case against these; a case that fails one is noise that dilutes the plan.

- **It can fail.** If no realistic defect would make this case fail, it proves nothing. Delete it.
- **It names what it proves.** A case without a distinct "proves" column is a duplicate or a filler.
- **It asserts an outcome, not an internal.** "Returns 429 after the 11th call" is a case; "calls the counter" is a restatement of the code.
- **It is one concept.** Two independent conditions in one case blur which one broke; split them.
- **The floor holds per branch.** Branchy logic and each named failure mode get their own error and edge case, not one shared "error" row.

## Gotchas

- **This skill deliberately stops at the plan.** Writing runnable tests is owned by `test-writer` (existing code) and `follow-tdd` (code being written); producing them here would duplicate that and bias the tests toward the implementation. Enumerate, review, hand off.
- **A thin brief cannot be fixed downstream.** The agent has no channel back to the user; every gap in the brief becomes a generic case or a wrong assumption. Spend the time in step 1.
- **Not a substitute for follow-tdd's inline enumeration.** When you are already mid-cycle writing one behavior's test, follow-tdd's step 1 is enough. Reach for this skill when you want an exhaustive standalone coverage contract up front, or the target is large enough that the sweep would otherwise flood the main context.

## Examples

Target: a `RateLimiter.allow(userId)` that permits 10 requests per rolling 60s window.

Brief handed to the agent:

```text
Target: src/rate-limiter.ts, RateLimiter.allow(userId)
Known behaviors: allows up to 10 calls per user per rolling 60s window; the
11th within the window is denied; the window slides, not resets on the minute.
Language / stack: TypeScript, vitest.
Output: a Test-Case Plan only. Golden/error/edge per behavior; no test code.
```

A slice of the returned plan the review gate would keep:

```markdown
### Allows within the limit
| ID | Category | Input / Preconditions | Expected result | Proves |
|---|---|---|---|---|
| 1 | golden | fresh user, 10 calls in 5s | all 10 allowed | limit is honored |
| 2 | edge | 10 calls, then 1 more at t=59.9s | 11th denied | boundary is the count, not the clock |
| 3 | edge | 11th call at t=60.1s (first aged out) | allowed | window slides, not resets |
| 4 | error | userId is null | rejected, not counted against another user | bad key never shares a bucket |
```
