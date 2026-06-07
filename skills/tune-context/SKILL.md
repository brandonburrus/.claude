---
name: tune-context
description: >-
  Use this skill when auditing or tightening the always-on agent context,
  including CLAUDE.md, AGENTS.md files, rules files, skill descriptions, and
  memory indexes. Use when the user says "trim my CLAUDE.md", "my context is
  bloated", "the agent keeps ignoring conventions", "audit my agent setup",
  or "clean up the AGENTS.md", and periodically as always-on files accumulate.
  Do not use for capturing new learnings (use learn-from-context), for
  writing a project's first AGENTS.md (use onboard-codebase), for auditing a
  project's AGENTS.md coverage and conformance against the standard (use
  audit-agent-context), or for managing conversation-level context in a single
  session (compaction handles that).
---

## Purpose

Audit the standing context an agent carries into every session and tighten it: cut what does not change behavior, move what is conditional out of the always-on tier, and fix what has drifted from reality. Context is the biggest lever on agent quality in both directions; too little starves the agent into hallucinating conventions, and too much dilutes attention until the rules that matter stop firing. The budget is attention, not window size, and every always-on line spends it in every future session.

## The context tiers

| Tier | Lives in | Cost model |
|---|---|---|
| Always-on | CLAUDE.md, AGENTS.md, rules files, skill descriptions, memory index | Paid every session, forever; the expensive tier |
| Conditional | Skill bodies, references/, agent definitions | Paid only when triggered; cheap until used |
| Per-task | Files read, specs loaded | Paid per task by choice |
| Per-iteration | Errors, test output | Transient |

The single most valuable move in any tuning pass is demoting content one tier: an always-on procedure becomes a skill, a skill body's rarely-needed table becomes a reference file, a CLAUDE.md project section becomes that project's AGENTS.md entry.

## Audit workflow

1. **Inventory the always-on tier**: CLAUDE.md, the AGENTS.md hierarchy in play, rules files, the skill descriptions listing (combined description budget is finite and shared), and the memory index. Measure each; know what the standing context actually costs before judging it.
2. **Sweep each file against the cut list**:
   - **Default-behavior duplicates**: rules the agent already follows without being told (the baseline test from skill verification applies here: if removing the line changes nothing, the line is dead weight)
   - **Narratives that should be rules**: three sentences of story compressible to one directive with a why
   - **Stale references**: files, flags, commands, and tools that no longer exist; every one erodes trust in the rest of the file ("if this is wrong, what else is?")
   - **Contradictions**: rules that disagree with each other or with observed project reality; agents resolve contradictions arbitrarily, which reads as "ignoring instructions"
   - **Wrong-tier content**: procedures, large tables, and rarely-relevant detail that belongs in a skill or reference; project-specific content in the global file; global content trapped in one project
   - **Automation wishes written as prose**: "always run X after Y" instructions that should be hooks, because hooks fire deterministically and prose decays
3. **Check the routing surfaces**: skill descriptions that overlap (two skills claiming the same trigger), boundaries that no longer name the right neighbor, and descriptions that drifted from what the body now does.
4. **Propose the edit set** with per-item rationale: cut, compress, move (and to where), or fix. The user approves before anything changes; standing instructions are their voice, not the agent's.
5. **Apply and verify**: behavior the cut content governed should be spot-checked (the same prompt that used to exercise the rule), because a tuning pass that silently broke a load-bearing rule is worse than bloat.

## Sizing heuristics

- A CLAUDE.md past a few hundred lines is carrying content that belongs in lower tiers; the global file holds identity, hard rules, and routing, not procedures.
- An AGENTS.md decision log that has become a session diary gets compressed: keep the decisions and constraints, drop the play-by-play (the git history already records what happened when).
- Every rule earns its line with a behavior change; "would the agent get this wrong without this line?" is the inclusion test, identical to the skill-content test.
- One example beats three explanations, in rules files as in skills; but examples are the first thing to demote when space is tight, because the rule plus why usually survives without it.

## Gotchas

- **Bloat arrives one good line at a time.** Every addition was locally justified; the failure is global, when the file's hundredth rule dilutes the firing of the first. This is why tuning is periodic maintenance, not a one-time fix.
- **Symptoms of context problems point both directions.** An agent inventing APIs is starved (missing the convention); an agent ignoring stated conventions is usually flooded (the rule is present but drowned) or contradicted. Diagnose before adding or cutting, because the intuitive fix (add more rules) worsens the flooded case.
- **Compression must preserve the why.** A rule stripped to its bare imperative invites the loopholes the original reasoning closed; compress the story, keep the reason clause.
- **The memory index and skill descriptions are context too.** Tuning CLAUDE.md while sixty stale description lines and a bloated MEMORY.md ride along misses half the budget.
- **Deletion needs the same approval bar as addition.** A rule that looks dead may encode a correction the user made three times; check entries against their history (learn-from-context evidence, AGENTS.md dates) before proposing the cut, and when in doubt, ask rather than delete.
