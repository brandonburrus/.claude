---
name: review-pull-request
description: >-
  Use this skill when reviewing someone else's pull request or proposed
  code changes. Use when the user says "review PR #42", "review this pull request",
  "take a look at this PR", "what do you think of these changes", or asks for a
  second opinion on a branch, diff, or commit range. Also use for reviewing a local
  branch against a base when no PR exists. Do not use for opening a PR (use
  open-pull-request), reviewing your own in-progress work mid-task, or rewriting
  code for clarity (use refactor-code).
---

## Purpose

Review a pull request end-to-end and deliver an honest, severity-labeled report in chat. The report is the deliverable: never post anything to GitHub unless the user explicitly asks, and then only after showing the exact command and body. The approval standard is code health, not perfection: approve when the change definitely improves the codebase and follows its conventions, even if it is not how you would have written it.

## Workflow

Copy this checklist and track progress:

```text
Review Progress:
- [ ] 1. Fetch the change, its spec, and its standards
- [ ] 2. Intent pass (simpler-alternative check)
- [ ] 3. Read the tests first
- [ ] 4. Trace end-to-end on both axes
- [ ] 5. Categorize findings by severity
- [ ] 6. Report with verdict
```

### 1. Fetch the change, its spec, and its standards

- `gh pr view <n> --json title,body,url,state,baseRefName,headRefName` for intent, `gh pr diff <n>` for the diff, `gh pr checks <n>` for CI state
- No PR or no GitHub remote: ask for the base ref, then review `git diff <base>...<head>` with the same methodology
- To trace beyond the diff you need the code at the PR head: if the working tree is clean, `gh pr checkout <n>` (note the original branch and switch back when done); if dirty, `git fetch origin pull/<n>/head:review-pr-<n>` and read files via `git show review-pr-<n>:<path>`
- **Spec sources**, in order: linked issues referenced from the PR body or commits, the PR description itself, plan or spec docs in the repo. No spec found means the spec axis reports "no spec available", not silence
- **Standards sources**: CLAUDE.md, AGENTS.md, CONTRIBUTING.md, ADRs, style docs. Note linter and formatter configs but never re-check what tooling already enforces; flagging what ESLint catches wastes the author's attention

### 2. Intent pass

Before any line-level reading:

- State the PR's goal in one sentence, in your own words. If you cannot, the PR is underspecified; say so and ask rather than reviewing blind
- Run one mandatory simpler-alternative check: is the problem real, does something in the codebase already solve it, would a smaller change get 90% of the value with 10% of the risk, does it belong at a different layer (config vs code, framework vs app)? A better alternative, named with rationale, is the most valuable possible finding; surface it before everything else
- Size check: a PR too large to actually read (roughly 1000+ changed lines without a mechanical cause like a rename or generated code) gets a request to split, not a skim. A skimmed review is a rubber stamp with extra steps

### 3. Read the tests first

Tests reveal intent and coverage before the implementation biases you:

- Do tests exist for the changed behavior? Do they test behavior rather than implementation details?
- Would they catch a regression, or do they pass while skipping the real path (mocks hiding the bug, happy path only, asserts on intermediate state)?
- A bug fix without a regression test is an Important finding by default

### 4. Trace end-to-end on both axes

The diff is the entry point, not the scope. Follow the call graph through the unchanged code on both sides of each hunk; bugs hide at the seams. Note every surprise in the trace (unexpected branch, dead code reached, unknown state); surprises are signal.

Review on two independent axes, because each can mask the other:

- **Spec axis**: requirements asked for but missing or partial; behavior present that was not asked for (scope creep); requirements that look implemented but the traced path produces something else. Quote the spec line for each finding
- **Standards axis**: violations of the repo's documented conventions, citing the doc and rule. Distinguish hard violations from judgment calls

Within the trace, check these dimensions:

| Dimension | Look for |
|---|---|
| Correctness | Edge cases (null, empty, boundary), error paths, race conditions, off-by-one, state inconsistencies |
| Readability | Names needing explanation, control flow requiring a mental stack, clever tricks, dead code artifacts |
| Architecture | New patterns where existing ones fit, boundary violations, wrong-direction dependencies, abstraction without a third use case |
| Security | Unvalidated input at boundaries, secrets in code or logs, missing auth checks, unparameterized queries, untrusted external data |
| Performance | N+1 queries, unbounded loops or fetches, missing pagination, sync work that should be async |

Keep claim and verification separate: "the PR says X" and "I traced X and confirmed it" are different statements, and the report must say which one you are making.

### 5. Categorize findings by severity

Label every finding so the author knows what is required versus optional; unlabeled feedback reads as all-mandatory and wastes author time:

| Label | Meaning | Author action |
|---|---|---|
| Critical | Security vulnerability, data loss, broken functionality | Blocks merge |
| Important | Missing test, wrong abstraction, unhandled error path, spec gap | Fix before merge |
| Suggestion | Worth considering, not required | Author's call |
| Nit | Style or preference | Author may ignore |

Each finding carries four parts: what (one sentence, with `file:line`), why it matters (the consequence, not the principle), evidence (the trace step or input that exposes it), and a concrete suggested fix. Quantify when possible: "this N+1 adds ~50ms per list item" beats "could be slow".

### 6. Report with verdict

```markdown
## Review: <PR title> (#<n>)

**Verdict:** Approve | Approve with fixes | Request changes
**Reason:** <the single biggest reason, one sentence>

### Strengths
- <specific, at least one; accurate praise makes the rest credible>

### Critical / Important / Suggestions / Nits
- <findings per step 5, omit empty levels>

### Spec coverage
- <missing / partial / scope creep, or "no spec available">

### What I traced
- <paths walked and checks performed, so the user can judge coverage>
```

If you genuinely find nothing, the "What I traced" section is the review; a bare LGTM is not an output.

## Posting to GitHub

Only on explicit user request. Show the exact `gh pr review` command and full body first, wait for an explicit yes, then run it. Default to `--comment`; use `--approve` or `--request-changes` only when the user explicitly chooses that verdict. A posted review is published to the author and team immediately and cannot be unsent.

## Guardrails

- Never post, approve, or request changes on GitHub without an explicit user request and a shown payload.
- Never give feedback on code you did not read; if you skipped files, list them in the report.
- Comment on the code, never the author. "This function mutates shared state" not "you mutated shared state".
- Do not block on personal preference. Style guides and documented conventions are the authority on style; engineering facts override opinions.
- Do not accept "I'll clean it up later" for Important findings; ask for the fix or a filed, self-assigned follow-up before approval.
- Do not pad with nits when a structural problem exists; lead with the structural problem and drop or defer the nits.

## Gotchas

- **Diff-local review misses the real bugs.** The changed lines are usually fine; the breakage lives where they meet unchanged code. Trace through the seams or you are reviewing formatting.
- **Tests passing is necessary, not sufficient.** Tests catch regressions in covered behavior; they say nothing about architecture, security, readability, or whether the tests themselves test anything.
- **Agent-written code needs more scrutiny, not less.** It is confident and plausible even when wrong, and it was never manually run by anyone before reaching you.
- **The five-axis sweep is for finding, not padding.** An axis with no findings gets silence in the report, not a manufactured observation per dimension.
- **`gh pr checkout` mutates your working tree.** Check the tree is clean first, record the current branch, and switch back when the review ends; a review that strands the user on the PR branch is a defect.
