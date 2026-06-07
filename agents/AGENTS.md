# AGENTS.md

Personal Claude Code subagent definitions. Each `<name>.md` file's frontmatter configures identity, tools, and model; its body is the agent's entire system prompt. The `create-claude-agent` skill (and its `references/agent-config.md` docs digest) is the authority on the frontmatter surface.

## How these agents are built

- **Thin agent + skill.** When a library skill already owns the methodology, the agent preloads it via the `skills` frontmatter field and the body carries only identity, tool limits, autonomous overrides, and the output contract. Methodology stays in one place; duplicating it into the agent body creates drift.
- **Autonomous overrides are the load-bearing section.** Library skills assume an interactive session; subagents cannot ask the user, post externally, or wait for approval. Each agent body explicitly rewrites the skill's "ask the user" steps as decide-and-disclose and its outward actions as return-only.
- **Reviewers and auditors get read-only tool allowlists** (`Read, Grep, Glob, Bash`) plus a body rule restricting Bash to inspection; an agent that can edit can "fix" what it was asked to judge.
- **Verification is spawn-by-path**: new agents do not appear in the session registry until reload, so they are tested by general-purpose subagents adopting the definition file, run against sandboxes with planted ground truth, twinned with no-definition baselines.

## Agents

- `implementation-planner` - wraps `create-code-plan`; pinned to opus because planning is architecture-grade judgment and the plan quality bounds everything built from it.
- `code-reviewer` - wraps `review-pull-request`; adds an anti-noise discipline (80 percent confidence bar, pre-report gate, zero-findings-valid) because manufactured findings are the primary failure mode of automated review. Never posts to GitHub, never `gh pr checkout` (uses `git fetch pull/<n>/head` + `git show` so the spawning session's tree is untouched).
- `security-reviewer` - preloads `harden-security` as the rulebook, not the workflow (that skill is build-time; the audit methodology lives in the agent body). Exploitability-ranked severity with a PoC bar for Critical/High.
- `task-implementer` - wraps `follow-tdd` + `code-with-best-practices`; executes one plan task test-first and returns an evidence-based report (quoted RED/GREEN/verify output). A task that cannot be implemented honestly as written returns Blocked, never an invented premise; the skill's user-confirmed TDD exceptions become Blocked reports since a subagent cannot ask. Does not commit unless told.
- `completion-verifier` - read-only adversarial done-checker; re-runs everything itself (a handed report is claims to audit, not facts) and exists specifically to catch the green-suite-but-unmet-requirement case via a reward-hacking sweep. Shares the task-implementer's report shape so the two compose.
- `root-cause-investigator` - wraps `fix` but runs only through step 4 (loop, reproduce, localize, falsify); stops at the confirmed root cause and hands the fix to the main loop so the failing-test-first workflow is preserved. The one agent allowed to mutate the tree (instrument, bisect) but contractually required to restore it before returning.

## The pipeline

The seven agents compose into plan -> implement -> verify: `implementation-planner` produces the plan, `task-implementer` executes each task (parallelizable where the plan marks tasks independent; add `isolation: worktree` if they would collide), `completion-verifier` gates each checkpoint, `code-reviewer` + `security-reviewer` do the final pass, and `root-cause-investigator` is the off-ramp when something breaks. `execute-code-plan` (deferred) is the thin orchestration skill that will drive this; the agents already speak compatible output contracts so it stays thin.

## Gotchas

- `harden-security` explicitly excludes auditing ("use the bundled /security-review"); the security-reviewer agent is the library's own audit surface and reframes the skill as its checklist. Do not "fix" the agent by pointing it at a nonexistent audit skill.
- Spawn tests showed strong opus baselines reach near detection parity on planted bugs; these agents earn their place through format consistency, scope discipline, and hard guardrails (no posting, no tree mutation), not raw detection. Judge future agents the same way.
- Verifier-type agents need a genuine-work control in their spawn test, not just a planted-defect case. A verifier that rejects everything passes the defect case for the wrong reason; `completion-verifier` was tested against both a doctored copy (must Reject) and a real completion (must Verify) to prove it discriminates rather than always-rejects.
- Interrogation/interview skills cannot become agents. `AskUserQuestion` is one of the tools the official docs list as unavailable to subagents (alongside `Agent`, `EnterPlanMode`, `ScheduleWakeup`) "even when listed in the `tools` field", and the docs route "frequent back-and-forth or iterative refinement" to the main conversation. Skills built on a live one-question-at-a-time interview with a user yes-gate (`write-product-spec`, `write-tech-spec`, `clarify-ambiguity`) stay skills; wrapping them as agents silently drops the interview, which is their entire value. The decide-and-disclose pattern only substitutes for clarification the agent can resolve from material it was handed, never for eliciting intent that lives only in the user's head.
