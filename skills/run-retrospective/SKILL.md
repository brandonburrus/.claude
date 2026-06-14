---
name: run-retrospective
description: >-
  Use this skill to run a retrospective on a work period (a sprint, a project, a
  release cycle, a quarter) and turn it into a few concrete, owned, dated actions
  grounded in evidence. Use when the user says "run a retro", "retrospective",
  "sprint retro", "project retro", "post-sprint review", "what went well and what
  didn't", "let's reflect on the last cycle", or "start/stop/continue". Do not use
  for the root-cause analysis of a single incident or outage (use
  write-post-mortem), for extracting durable agent-behavior learnings into memory
  (use learn-from-context), or for reporting status or outcomes up to leadership
  (use translate-for-leadership).
---

## Purpose

Produce a retrospective that ends in action, not catharsis. The deliverable is 2-3 specific, owned, dated changes the team will make next cycle, each traceable to evidence from the cycle just finished. A retro that produces a list of feelings and no owned actions is theater; a retro that blames a person instead of a system fixes nothing and costs trust.

The rule the skill defends: **ground every observation in evidence, and end every theme in an action with an owner and a date.** Memory is recency-biased and flattering; the cycle's actual record is not.

## Workflow

- [ ] 1. Set the window and gather the evidence
- [ ] 2. Surface observations in a frame, grouped by theme
- [ ] 3. Root-cause the 2-3 themes that cost the most
- [ ] 4. Commit to 2-3 owned, dated, verifiable actions

### 1. Set the window and gather evidence

Fix the period under review, then pull the record rather than relying on recall: commit and PR history, merged-vs-planned scope, incidents and their timing, cycle time and review latency, and any product metrics that moved. Evidence first is what keeps the retro from becoming "the last bad thing everyone remembers." Note where the plan and the outcome diverged; the divergences are the richest material.

### 2. Surface observations in a frame

Organize what the evidence and the team raise into a frame: **What went well / What hurt / What was confusing**, or **Start / Stop / Continue**. Group related observations into themes rather than listing every one; ten symptoms of one cause are one theme. Keep it blameless: describe what happened and its effect, not who to fault.

### 3. Root-cause the themes that cost the most

Do not try to fix everything. Take the two or three themes that cost the most time, quality, or morale and trace each to a process or system cause by asking why until you stop landing on a person. "The release slipped" because "QA was late" because "QA started after code-freeze" because "there is no shared definition of ready" is a fixable system cause; "QA was slow" is a blame dead-end.

### 4. Commit to owned, dated actions

Turn each root cause into one action that is **specific** (a concrete change, not "communicate better"), **owned** (a named person), **dated** (a due date or the next checkpoint), and **verifiable** (you can tell next retro whether it happened). Cap at three. More than three actions means none of them happen; a retro that changes three things beats one that resolves twenty.

## Anti-patterns

| Trap | Why it fails | Instead |
|---|---|---|
| Actions with no owner or date | "We should test more" is a wish; nothing changes | Name a person and a date for every action |
| More than ~3 actions | Diffuse focus means none land | Pick the highest-cost few; carry the rest to a backlog |
| Blaming people | Kills the candor the retro depends on | Trace to the process or system that let it happen |
| Vibes over evidence | Recency and politics distort recall | Pull commits, PRs, incidents, and metrics first |
| Re-listing last retro's actions | Signals they were never owned | Check prior actions' status at the top of each retro |

## Gotchas

- **A retro is not an incident post-mortem.** `write-post-mortem` dissects one failure in depth; this reviews a whole period's pattern and is forward-looking. If one incident dominated the cycle, reference its post-mortem here rather than redoing it.
- **Carry forward last cycle's actions.** Open every retro by checking whether the previous actions actually happened; un-owned actions that silently lapse are how retros lose their teeth.
- **Blameless is a precondition, not a nicety.** The moment a retro assigns fault, people stop surfacing the real problems, and the evidence dries up.

## Example

Window: the last two-week sprint. Evidence: 14 PRs, 3 reopened after merge, one Friday hotfix, review latency averaging 1.5 days, two stories carried over.

- **Theme (What hurt):** three post-merge reopens and a hotfix, all in the payments module. Root cause traced: no integration test covers the payments path, so regressions are caught only in production.
- **Action:** "Add an integration test suite for the payments happy path and top two failure modes. Owner: Priya. Due: end of next sprint." (specific, owned, dated, verifiable)
- **Theme (What was confusing):** two stories carried over because "done" was ambiguous. Root cause: no shared definition of ready. **Action:** "Draft a one-paragraph definition-of-ready and apply it at next planning. Owner: Sam. Due: next planning." Cap reached at two; the slow-review observation goes to the backlog.
