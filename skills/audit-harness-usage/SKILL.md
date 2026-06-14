---
name: audit-harness-usage
description: >-
  Use this skill to mine your own Claude Code session history for signals that
  improve the harness: which skills never fire in real use, which fire most, and
  where repeated manual corrections point to a missing hook or skill. Use when the
  user says "which skills never fire", "audit harness usage", "analyze my
  transcripts", "what should I turn into a hook", "find repeated corrections",
  "is my harness actually working", or "what skills are unused". Do not use for
  testing whether a skill changes behavior via baseline runs (use
  audit-skill-efficacy), for auditing AGENTS.md coverage in a codebase (use
  audit-agent-context), or for capturing a single learning from the current
  session (use learn-from-context).
---

## Purpose

Close the feedback loop on the harness itself. The transcripts and history under the Claude config directory are a record of what actually happened across sessions; mined, they reveal which skills never trigger (cut or re-route candidates), which carry the load, and where the same correction recurs (a hook, a skill, or a CLAUDE.md rule waiting to be written). The deliverable is a prioritized list of harness changes, each backed by usage evidence, routed to the right meta-skill.

The rule the skill defends: **decide harness changes from the usage record, not from imagination.** A skill you assume is useful but that has never fired is the same dead weight as one that fails a baseline test, and a correction you make once is noise while one you make every week is a hook.

## Workflow

- [ ] 1. Run the firing analysis over the history
- [ ] 2. Interpret the three signals
- [ ] 3. Route each finding to the meta-skill that fixes it

### 1. Run the firing analysis

Run the bundled script over the config directory:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/analyze-skill-firing.py
```

It lists every skill in the library with its real firing count across `projects/**/*.jsonl` and `history.jsonl`, the never-fired skills, and the heaviest-used ones. Pass `--claude-dir <path>` if the config lives elsewhere. The script reports counts only; interpretation is yours.

### 2. Interpret the three signals

- **Never-fired skills:** a skill present in the library with zero firings is a candidate. But zero firings has two causes, distinguish them: the skill is genuinely unused (cut candidate), or it is useful but its description never matches how the user actually phrases the task (re-route candidate, fix the description's triggers). A recently added skill with no firings yet is neither; note its age.
- **Firing distribution:** the heaviest-used skills are where polish pays off most. A skill firing far more than expected may be over-triggering on tasks it should not own (a boundary problem in its description).
- **Repeated corrections:** scan the recent transcripts (the script points to the busiest ones) for the same manual correction recurring across sessions, the user redirecting the same default behavior. One correction is noise; the same one three times is a pattern to encode.

### 3. Route each finding

| Finding | Route to |
|---|---|
| Skill never fires, genuinely unused | Cut it (confirm with audit-skill-efficacy if unsure of its value) |
| Skill never fires, but should | Fix its description triggers (create-skill, Phase 4) |
| Repeated correction of a deterministic behavior ("always/never/before/after X") | A hook (create-claude-hook) |
| Repeated correction that needs judgment, reusable across projects | A skill (create-skill) or a CLAUDE.md rule |
| One-off correction, this project only | learn-from-context or the project's AGENTS.md, not the global harness |

Report the findings ranked by evidence strength (how many sessions support each), with the routed fix named per finding. Apply only with the user's go.

## Gotchas

- **Zero firings is ambiguous, not a verdict.** Always separate "unused" from "mis-described" before recommending a cut; the second is fixed by a better description, and cutting it loses a useful skill.
- **The script counts; it does not judge.** Firing frequency measures triggering, not value. A high-firing skill could still be low-efficacy (cross-check with audit-skill-efficacy), and a low-firing one could be a rarely-needed but critical specialist.
- **Correction-mining is manual and judgment-heavy.** The script reliably surfaces firing counts; recurring corrections require reading transcripts, because the same intent is phrased a dozen ways and no regex catches them all. Do not claim a correction pattern the transcripts do not actually show.
- **Bundled and plugin skills are not in the library directory.** Firings of skills that have no folder under `skills/` are bundled or plugin skills; the script flags them separately so they are not mistaken for orphans to cut.

## Example

The script reports 73 skills, 11 never fired. Of those, `format-for-obsidian` has 40 firings (heavy use), and `translate-for-leadership` has zero across six months. Reading recent transcripts shows the user three times manually asked for a commit message rewrite after the agent wrote a verbose one. Findings: `translate-for-leadership` is a re-route candidate (the user does summarize for leadership, but phrases it as "rewrite this for my manager", which the description may not catch, fix triggers via create-skill); the commit-message correction recurs deterministically (route to a create-claude-hook PostToolUse nudge or a CLAUDE.md rule). Ranked by evidence: the commit pattern (3 sessions) first.
