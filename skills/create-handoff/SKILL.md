---
name: create-handoff
description: >-
  Use this skill when compacting the current working session into a handoff
  document so a fresh session or another agent can continue without
  re-deriving context. Use when the user says "write a handoff", "hand this
  off", "compact this for a fresh session", "context is running low", or
  "summarize where we are to continue later". Captures the goal, verified
  versus half-done state, decisions and their reasons, the exact next step,
  blockers, and load-bearing paths and commands. Do not use for extracting
  durable cross-session learnings into
  memory (use learn-from-context).
---

## Purpose

Compact the working session into a single handoff document a fresh session (a new agent, a teammate, or you tomorrow) reads to continue the work without re-deriving the context that lived only in this conversation. The deliverable is a continuation brief, not a transcript: capture the goal, what is done and verified versus half-done, the decisions and their reasons, the exact next step, open blockers, and the load-bearing paths, commands, and identifiers. Cut everything the next session can reconstruct on its own from the repo, the diff, or the linked artifacts; keep only what it cannot.

## Workflow

```text
Handoff checklist:
- [ ] 1. Gather ground truth (git state + linked artifacts) before writing
- [ ] 2. Decide what the next session genuinely cannot reconstruct
- [ ] 3. Fill the template; reference artifacts by path, never re-paste them
- [ ] 4. Write the single exact next step, runnable as-is
- [ ] 5. Redact secrets, then save and report the path
```

### 1. Gather ground truth

Run these before writing a word; memory of the session drifts, the repo does not.

```bash
git rev-parse --abbrev-ref HEAD     # branch the work lives on
git status --short                  # what is dirty, staged vs unstaged
git diff --stat                     # shape of the uncommitted change
git log --oneline -10               # commits this session produced
```

The changed-file list, the branch, and the recent commits anchor the handoff in verifiable state, so the next session trusts the doc over its own guesses. Note which listed work is committed versus only on disk; an uncommitted change that the reader does not know about gets clobbered.

### 2. Decide what cannot be reconstructed

This is the whole discipline. For every candidate line, apply the test: would the next session recover this on its own from the repo, the diff, the test output, or a linked artifact? If yes, cut it. What survives the cut:

| Keep (unreconstructable) | Cut (reconstructable or noise) |
|---|---|
| Why a decision was made, the rejected alternative | What the code now says (the diff shows it) |
| A failed approach and why it failed | A narrated log of every step taken |
| The exact next action and where to start | Generic restatement of the task |
| A non-obvious gotcha, constraint, or dependency | Anything already in a PRD, plan, ADR, or issue |
| Verified-versus-assumed status of each piece | Praise, filler, "we successfully..." |
| Load-bearing paths, commands, env, identifiers | File contents that the path alone resolves |

A handoff that re-pastes a plan or a diff buries its one job (the reasoning and the next step) under content the reader already has. Reference those artifacts by path or URL instead.

### 3. Fill the template

Use the block below verbatim as the structure. Omit a section only if it is genuinely empty (say "None", do not delete the heading: a missing "Blockers" reads as "unknown", an explicit "None" reads as "checked"). Keep each entry to the shortest form that survives a cold read by someone who was not here.

```markdown
# Handoff: <short title of the work>

**Date:** <YYYY-MM-DD>  **Branch:** <branch>  **Status:** <in-progress | blocked | ready-for-review>

## Goal
<1-3 sentences: what this work is trying to achieve and why. The destination, not the journey.>

## State
**Done and verified:** <what works, and how it was verified (test name, command, observed output)>
**Half-done:** <what is started but incomplete, and exactly where it stops>
**Uncommitted:** <changes on disk but not committed, so they are not lost>

## Key decisions
- <decision> -- because <reason>. Rejected <alternative> because <reason>.

## Next step
<The single exact next action, runnable or startable as written. Name the file, the function, the command.>

## Open threads / blockers
- <blocker or open question, with what was tried and what would unblock it>

## Tried and failed
- <approach that did not work, and why, so it is not retried>

## Load-bearing references
- <path/to/file> -- <why it matters>
- <command to run the suite / reproduce> -- <what it proves>
- Plan / PRD / issue: <path or URL> (referenced, not duplicated)

## Suggested skills
- <skill the next session should invoke to continue, e.g. follow-tdd, fix>
```

### 4. Make the next step executable

The "Next step" line is the highest-value content; a vague one ("continue the refactor") forces the reader to re-derive what you already knew. Name the file and symbol, paste the exact command, or state the precise decision awaiting input. The reader should be able to act on it without opening the rest of the doc.

### 5. Redact, save, and report

Strip secrets before saving: API keys, tokens, passwords, connection strings, and personal data. A handoff is a file that gets shared, pasted, and committed by accident.

Save to a stable, discoverable location and tell the user the path. Default to the repository if the team shares handoffs (for example `docs/handoffs/<date>-<slug>.md`); use the OS temp directory for a private, throwaway handoff to your own next session. Confirm the location with the user when it is ambiguous. Writing a handoff captures state only: do not change code, commit, or push as part of producing it.

## Gotchas

- **A handoff is not a status report.** A report says what happened; a handoff sets up what happens next. If a line does not help the reader take the next action, it is report padding. The bias is omission: a tight handoff that loses a reconstructable detail costs nothing, a bloated one buries the next step.
- **Uncommitted work is the silent data-loss trap.** The reader resets, switches branches, or runs a clean checkout and your on-disk-only changes vanish. State explicitly what is uncommitted so it survives.
- **"Verified" and "assumed" are different claims; never blur them.** Marking assumed work as done sends the next session building on a foundation that was never checked. Tie each "done" to its evidence (test, command, observed output) or label it assumed.
- **Reasons are the payload, decisions are the wrapper.** "Chose Postgres" is reconstructable from the config; "chose Postgres over SQLite because the access pattern needs concurrent writers" is not. Without the reason, the next session re-litigates settled choices or silently reverses them.

## Example

```markdown
# Handoff: rate-limit the public search endpoint

**Date:** 2026-06-13  **Branch:** feat/search-rate-limit  **Status:** in-progress

## Goal
Stop the unauthenticated /api/search endpoint from being hammered. Target: 30 req/min per IP, 429 with Retry-After when exceeded.

## State
**Done and verified:** Token-bucket limiter in src/middleware/rateLimit.ts. Unit tests green: `npm test rateLimit` -> "12 passing". Confirmed 429 + Retry-After header by hand against the dev server.
**Half-done:** Limiter is written but NOT yet wired into the route. src/routes/search.ts still serves unthrottled.
**Uncommitted:** rateLimit.ts and its test are committed; the half-finished wiring edit in search.ts is on disk only.

## Key decisions
- In-memory token bucket, not Redis -- because single-instance deploy today. Rejected Redis because it adds an infra dependency we do not need yet; revisit when we scale horizontally.
- Keyed by IP from X-Forwarded-For -- because we sit behind one trusted proxy. Note: trusting that header is wrong the moment a second proxy hop appears.

## Next step
In src/routes/search.ts, wrap the GET handler with `rateLimit({ max: 30, windowMs: 60000 })` imported from ../middleware/rateLimit. Then add an integration test in test/search.int.ts asserting the 31st request in a window returns 429.

## Open threads / blockers
- None blocking. Open question: should authenticated callers bypass the limit? Not yet decided; current code limits everyone.

## Tried and failed
- express-rate-limit package -- its store interface fought our test harness's fake timers; the hand-rolled bucket tests cleanly with injected `now()`.

## Load-bearing references
- src/middleware/rateLimit.ts -- the limiter; takes an injectable clock for testing
- `npm test rateLimit` -- proves the bucket logic
- Plan: docs/plans/search-hardening.md (referenced, not duplicated)

## Suggested skills
- follow-tdd -- write the integration test before wiring the route
```
