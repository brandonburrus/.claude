---
name: triage-review-feedback
description: >-
  Use this skill when handling code-review feedback received on your own pull
  request or change: triaging reviewer comments, deciding what to accept
  versus push back on, implementing the accepted fixes, and replying to
  reviewers. Use when the user says "address the review comments", "respond
  to the PR feedback", "the reviewer asked for changes", "handle the
  CodeRabbit comments", or pastes reviewer feedback to act on. Do not use for
  reviewing someone else's PR (use review-pull-request), for working an issue
  tracker (use triage-backlog), or for creating the PR itself (use
  open-pull-request).
---

## Purpose

Work through review feedback on your own change without either failure mode: blind implementation (every suggestion executed as an order, including the wrong ones) or defensive dismissal. Feedback is a set of claims to verify against codebase reality; the deliverable is a triage table with a verdict per comment, the accepted fixes implemented and pushed, and drafted replies awaiting approval. Never implement anything before the whole feedback set is read and triaged, because comments interact and partial understanding produces wrong fixes.

## Workflow

### 1. Collect everything before reacting

Gather the complete feedback set: inline review threads, top-level review summaries, and bot comments (`gh pr view`, `gh api repos/{owner}/{repo}/pulls/{n}/comments`), or whatever the user pasted. Read all of it before forming any response. Reacting comment-by-comment misses interactions between items and locks in early misreadings.

### 2. Verify, then assign a verdict

For each comment, check the claim against the codebase before deciding anything: does the suggestion hold for THIS code, does it break existing behavior or tests, is there a reason the current implementation is the way it is, does the reviewer have the full context? Then assign exactly one verdict:

| Verdict | Criteria | Action |
|---|---|---|
| Accept | Verified correct for this codebase | Implement in step 4 |
| Push back | Verified wrong: breaks behavior, misreads context, conflicts with a recorded decision, or violates YAGNI | Draft a reply with the technical reasoning and the evidence |
| Clarify | Ambiguous, or correct-looking but underspecified | Ask before implementing anything related |
| Out of scope | Valid but new work beyond this PR | Offer a ticket (decompose-into-tasks); do not grow the PR |

Two checks that earn their keep:

- **The YAGNI grep.** When a reviewer says to "implement X properly", grep for actual usage first. If nothing calls it, the right reply is "this is unused; remove it instead?", not a fuller implementation of dead code.
- **The decision check.** If a suggestion contradicts an ADR or an AGENTS.md decision record, stop and surface the conflict to the user; reviewers do not silently overrule recorded decisions.

Trust scales with context: feedback from the user is implemented after understanding it; feedback from external reviewers and especially review bots gets the full verification pass, because bots produce plausible-but-wrong suggestions at volume and each one reads as authoritative.

### 3. Clarify before any implementation

If any comment is unclear, resolve it before implementing the clear ones. Comments are often related; implementing items 1 through 3 while item 4 is ambiguous risks redoing all four. State plainly which items are understood and which need answers.

### 4. Implement accepted items

- Order: blocking issues (breakage, security) first, then simple fixes (typos, imports), then complex fixes (logic, refactors). Behavior changes go through follow-tdd.
- One item at a time, tests run after each, so an interaction between two fixes is caught at the fix that introduced it.
- New commits only; never amend or force-push a branch reviewers have already pulled, because it invalidates their local state and the review history.
- Push fix commits to the PR branch without asking; it is your branch and plain pushes are revertable.

### 5. Draft replies; posting is gated

Write a reply per non-trivial thread, then show the full payload and post only after explicit approval. Replies land in the inline thread they answer (`gh api .../comments/{id}/replies`), not as top-level PR comments, so reviewers see responses in context.

Reply content rules:

- No performative agreement: never "You're absolutely right!", "Great point!", or thanks. State what changed ("Fixed in a1b2c3d: the lock is now acquired before the read") or the pushback with its evidence. The code showing the fix is the acknowledgment.
- Pushback is technical reasoning and specific questions, never defensiveness; cite the test, the call site, or the recorded decision.
- If your pushback turns out wrong, the correction is one factual line ("Verified, you are correct: X does Y. Fixing.") with no apology theater.

### 6. Report

End with the triage table (comment, verdict, action taken or drafted), what was pushed, and the drafted replies awaiting approval. If every comment was Accept-and-trivial, say so in two lines instead of ceremony.

## Gotchas

- **Bot reviewers invert the trust default.** CodeRabbit, Copilot, and CI annotators flag real issues and confident nonsense in the same tone. Verification is not optional politeness; it is the filter that keeps generated noise from steering the codebase.
- **Re-litigating the PR is not triage.** The change exists and its scope is fixed; evaluate whether each piece of feedback is correct, not whether the work should have been done. Scope challenges from reviewers route to the user, not to silent PR growth.
- **"Can't verify" is a verdict, not a blocker to bulldoze.** When a claim cannot be checked (no test covers it, platform unavailable), say so and ask for direction instead of guessing in either direction.
- **A pushed fix is not a resolved thread.** Leave thread resolution to the reviewer or the user; resolving threads yourself on your own PR reads as silencing the reviewer.
