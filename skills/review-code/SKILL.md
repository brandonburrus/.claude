---
name: review-code
description: >-
  This skill should be used when reviewing code the user just wrote or changed, before committing
  or opening a PR, by fanning out parallel adversarial reviewers across distinct lenses (security,
  performance, best practices, maintainability, and an optional acceptance check against a work
  item). It applies when the user says "review the code I just wrote", "review my changes", "review
  what we just built", "review this before I commit", "multi-angle review", "adversarially review
  this", or asks for a thorough review of the current change. It is the multi-lens adversarial
  fan-out over the current change; for a quick single-pass review of the current diff use the
  bundled /code-review instead, and inside the execute-code-plan pipeline the code-reviewer and
  security-reviewer agents fill this role. It should not be used for reviewing someone else's
  pull request or an external branch (use review-pull-request), or for fixing the issues it finds
  (it reports only; hand fixes to fix or refactor).
---

## Purpose

Review the code just written by fanning out parallel, read-only, adversarial reviewer subagents across distinct lenses, verifying their findings to cut false positives, and synthesizing one severity-ranked report. The deliverable is the report; this skill reviews and never edits. Four standing rules govern it, because they are the ones an agent drops under time pressure:

- **Reviewers are read-only.** Each reviewer reports findings and changes nothing. A reviewer that "helpfully" fixes a bug muddies the diff under review and skips the verification gate.
- **Spawn the lenses in parallel, in one message.** Serial dispatch is slow and tempts you to drop lenses; concurrent reviewers are the whole point of the fan-out.
- **Scope every reviewer to the just-written change, not the whole codebase.** A reviewer drowning in unchanged code reviews the wrong thing. Hand each the diff and the changed-file list.
- **Adversarial verification is mandatory, not optional polish.** Single-pass review ships plausible-but-wrong findings; the refute pass is what makes this adversarial rather than just multi-angle.

## Workflow

```text
Review code:
- [ ] 1. Resolve the review target (the just-written change)
- [ ] 2. Select the applicable lenses, then fan them out in parallel
- [ ] 3. Adversarially verify the findings
- [ ] 4. Synthesize the severity-ranked report
```

### 1. Resolve the review target

Auto-detect the smallest set that captures the just-written change, preferring the richest available:

```bash
# Prefer the whole feature branch when there is a base to diff against:
base=$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null)
git diff "$base"...HEAD          # branch vs base, plus:
git diff HEAD                    # any uncommitted + staged work on top
# No base / not a feature branch: review the working tree.
git diff HEAD                    # uncommitted + staged vs last commit
# Nothing uncommitted and no base: review the last commit.
git show HEAD
```

Capture the changed-file list and the unified diff; both are handed to every reviewer. If the target is empty, stop and report that there is nothing to review rather than reviewing the whole repository.

### 2. Select the applicable lenses, then fan them out in parallel

Select the lenses by what the diff actually contains; do not run every lens on every change. Classify the change first (documentation, config, tests, refactor, feature, or mixed), then run only the lenses whose **Run when** the diff matches. A docs-only or formatting change has no attack surface and no hot path, so security and performance do not run; a mixed change runs each lens against the parts it applies to. Choosing lenses is the difference between a sharp review and reviewers padding the report with irrelevance.

Spawn the selected reviewers as read-only subagents in a single message so they run concurrently. Give each the same payload (the diff and the changed-file list), its lens, and the skill to load; instruct each to review only through its lens and to change nothing. A purpose-built review agent may stand in for a lens where one exists (for example the `security-reviewer` agent for security). The fan-out earns its overhead on a substantial change; for a diff small enough to read in full, applying the selected lenses directly is fine, but the selection, adversarial verification, dedup, and ranking still apply either way.

| Lens | Loads | Run when | Hunts for |
|---|---|---|---|
| Security | `harden` | The change touches untrusted input, auth/authz, secrets, config, or network, file, or DB access. Skip pure docs, comments, or formatting | Injection, auth/authz gaps, secrets in code, unsafe handling of untrusted input, missing validation at trust boundaries, unsafe deserialization, SSRF/path traversal |
| Performance | `optimize-performance` | The change adds or alters runtime logic, loops, queries, or I/O. Skip docs, config-only, or trivial wiring | N+1 queries, hot-path allocations, blocking I/O on the request path, accidental quadratic loops, missing indexes, unbounded fetches, needless serialization |
| Best practices | `code-with-best-practices` | The change is code in a supported stack. Skip pure documentation | Language and stack idioms, error handling, concurrency correctness, API misuse, missing or weak tests for the new behavior |
| Maintainability | `refactor` | Any non-trivial code change. Skip docs-only or one-line changes | Structure and coupling, naming, duplication, function and module size, leaky abstractions, anything that raises the long-term cost of change |
| Acceptance (optional) | the work item's criteria | A work item is identifiable (see below) | Whether the change satisfies each acceptance criterion, and which criteria are unmet, partially met, or untested |

Run the **acceptance** lens only when a work item is identifiable: passed in by the user, or detected from the branch name or a commit message (for example `PROJ-123`, `#456`). Fetch its criteria through an available MCP or CLI (a Jira/Linear MCP tool, or `gh issue view`); if none is reachable, ask the user to paste the criteria. If no work item exists, skip this lens silently; never fabricate criteria.

Each reviewer returns findings in this shape, one per finding:

```text
[severity: critical|high|medium|low] path/to/file.ext:LINE
issue:      one line, what is wrong
why:        the concrete impact (the exploit, the slow path, the maintenance cost)
suggestion: the direction of the fix, not a full patch
confidence: high|low   (low flags it for the verify pass)
```

### 3. Adversarially verify the findings

For every finding marked `critical`/`high` or `confidence: low`, spawn a skeptic subagent whose job is to refute it: is the issue real, reachable on this code path, and actually a problem in this context, or an artifact of the reviewer not seeing the whole picture? Drop findings the skeptic refutes; keep the ones that survive. Low-severity, high-confidence nits skip this pass. Verify in parallel, one skeptic per finding or batched by file, and default a finding to refuted when the skeptic is uncertain, so the report errs toward signal.

### 4. Synthesize the severity-ranked report

Dedupe across lenses first: when two lenses flag the same location, merge into one finding and note both lenses, rather than double-reporting. Then rank by severity and emit the report.

```text
## Code review: <target, e.g. "feature/auth vs main, 7 files">

Verdict: <block | fix-before-merge | minor-nits | clean>   (N critical, N high, N medium, N low)

### Critical
- path/file:LINE [security, maintainability] - <issue>. <why>. Fix: <direction>.
### High
- ...
### Medium / Low
- ...

### Acceptance        (only if the lens ran)
- <criterion> -> met | partial | unmet | untested

### Not flagged
- <what the reviewers checked and found clean, so the report's silence is informative>
```

End with the report. This skill does not fix; offer to hand the confirmed findings to `fix` or `refactor` if the user wants them addressed.

## Gotchas

- **A reviewer that edits has broken the review.** Read-only is a hard rule: the diff under review must not change mid-review, and a fixed bug never reaches the verification gate. Instruct every reviewer to report only.
- **Skipping the verify pass turns the report into noise.** Multiple adversarial reviewers generate plausible-but-wrong findings at a higher rate than one; without the refute pass, the user wades through false positives and stops trusting the report. The verification is the feature.
- **The acceptance lens invents criteria when it cannot find them.** A reviewer told to check acceptance with no work item will hallucinate plausible criteria and grade against them. Gate the lens on a real, fetched work item; skip it otherwise.
- **Whole-repo review drowns the real change.** Reviewers given the whole tree spend their attention on unchanged code and miss the actual diff. Resolve the target first and scope every reviewer to it.

- **Every lens on every change is the wrong default.** Running the security lens on a README edit or the performance lens on a config bump produces noise and burns a reviewer on a change it cannot find anything in. Select lenses by what the diff contains: a documentation-only change runs no security or performance lens, and a config-only change runs no performance lens.
- **Two lenses flagging one line is one finding.** Security and maintainability both catching the same unsafe parse is not two problems. Dedupe by location before ranking, or the severity counts lie.

## Examples

Invocation: "review the auth changes I just made before I open the PR."

1. **Target.** On `feature/auth-PROJ-412`; base is `origin/main`. Resolve to the branch diff (`git diff $(git merge-base HEAD origin/main)...HEAD`) plus uncommitted work: 7 files, 240 lines.
2. **Fan out (one message, 5 parallel reviewers).** Security (loads `harden`), performance (`optimize-performance`), best practices (`code-with-best-practices`), maintainability (`refactor`), and acceptance, which detects `PROJ-412` from the branch name and pulls the criteria via the Jira MCP. Each gets the 7-file diff, reviews read-only, returns findings.
3. **Verify.** Security flags "JWT not verified before decode" (critical) and "timing-unsafe token compare" (high); two skeptics confirm the first against the code path and refute the second (the compare is on a non-secret request id). Performance's "N+1 on session lookup" survives; maintainability's "extract a helper" (low, high-confidence) skips verification.
4. **Synthesize.** Dedupe (security and best-practices both flagged the unverified JWT, merged), rank, emit: verdict `fix-before-merge`, 1 critical, 1 high, 3 medium, 2 low, plus acceptance showing one criterion `untested`. Offer to hand the confirmed set to `fix`.
