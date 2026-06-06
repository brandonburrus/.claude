# AGENTS.md

This repository is Brandon's personal Claude Code configuration directory (`~/.claude`): settings, a personal skills library, and reference material for improving that library.

## Project Structure

- `skills/` - Personal skills library. Each skill is a kebab-case directory containing `SKILL.md`, with optional `references/` and `scripts/` subdirectories.
- `_refs/` - Cloned open-source skill/agent/hook projects used as reference material for improving the skills library. See `_refs/CATALOG.md` for a full inventory of every ref's skills, agents, and hooks. Never edit files inside `_refs/`; they are read-only references.
- `settings.json` - Claude Code harness configuration (permissions, hooks, env).
- `CLAUDE.md` - Global behavioral instructions loaded into every session.

## Critical Constraints

- All skill files: no emojis, no em dashes, no H1 headings in the body.
- No "When to Use" or "When NOT to Use" sections in any skill body; the description is the only routing surface. Boundary detail too big for the description becomes a Gotcha; behavioral exceptions attach to the relevant rule.
- No absolute filesystem paths inside skill files; all locations are relative to the skill directory so the library stays portable.
- Skill directory name and the `name` frontmatter field must match exactly (kebab-case), and skill names are verb-led: the name states the action the skill performs (`create-diagram`, `write-adr`, `follow-tdd`), never a topic or noun.
- Skill scripts are Python only, run via `uv run ${CLAUDE_SKILL_DIR}/scripts/<name>.py`, with dependencies declared inline using PEP 723 metadata (no venvs, no requirements files). `${CLAUDE_SKILL_DIR}` is substituted by the harness at invocation, keeping skill files free of absolute paths while commands work from any working directory.
- Reference files within a skill stay one level deep from SKILL.md and get a table of contents when over 100 lines.
- SKILL.md target length is 80-250 lines, hard limit 500; overflow goes to `references/`.
- The `create-skill` skill (`skills/create-skill/SKILL.md`) is the authority on skill conventions; follow it when creating or restructuring any skill.

## Conventions

- Skill descriptions state triggers only, never workflow summaries (a summarized workflow becomes a shortcut that prevents the body from being read).
- New or substantially changed skills get verified per create-skill Phase 5: parallel baseline vs with-skill subagent runs on realistic prompts.
- Git commits follow conventional commit style (`feat(skills): ...`, `chore: ...`); commit only when asked.

## Key Decisions

- 2026-06-06: Skill scripts standardized on Python via `uv run` with PEP 723 inline dependencies.
- 2026-06-06: Adopted lightweight subagent verification (baseline vs with-skill) as the default for new skills, with full pressure-scenario methodology reserved for discipline-enforcing skills (`skills/create-skill/references/testing-skills.md`).
- 2026-06-06: `write-tech-spec` uses relentless interrogation (one question at a time with a recommended answer), outputs a single spec document with an offered split for systems of 3+ components, and only states decisions with a one-line rationale; full alternatives capture belongs to `write-adr` (spec Decisions rows flag "ADR candidate").
- 2026-06-06: `diagrams-as-code` renamed to `create-diagram` and broadened to all diagram types, routing architecture/infra to the Python diagrams library and flowcharts/sequence/state/ER to Mermaid, with destination overriding type (Markdown destinations get fenced Mermaid blocks). Render verification is mandatory; the Mermaid chain is render if tooling exists, one npm install attempt, then deliver validated source with explicit disclosure.
- 2026-06-06: `write-adr` mines the conversation first and interrogates only gaps, enforces a significance gate (conventions and cheap-to-reverse choices go to AGENTS.md, not the ADR log), requires concrete revisit-when conditions, and treats accepted ADRs as immutable (supersede, never edit). The rsg weighted evaluation-criteria table is optional, kept only for decisions actually scored on multiple criteria, to protect the two-minute readability rule.
- 2026-06-06: Removed "When to Use"/"When NOT to Use" sections from all skills and banned absolute filesystem paths in skill files; the description is the single routing surface and skills must stay portable. Unique boundary content was preserved as Gotchas (obsidian) or rule exceptions (test-driven-development Iron Law).
- 2026-06-06: Always-on rule sets do not belong in the skills library; they go in `CLAUDE.md`, which is unconditionally in context. The `code-style` and `git` skills were extracted into `CLAUDE.md` (Code Style, Git Conventions sections) and deleted; a skill marked "ALWAYS use" is a routing bet that CLAUDE.md does not have to make.
- 2026-06-06: `create-skill` gained `references/skill-config.md`, a digest of the official skills docs covering the full frontmatter surface (invocation control, allowed-tools, context fork, arguments), string substitutions, dynamic context injection, and the content lifecycle (compaction keeps only the first 5,000 tokens of an invoked skill, so critical rules are front-loaded). Script invocation convention changed to `uv run ${CLAUDE_SKILL_DIR}/scripts/<name>.py`.
- 2026-06-06: All skill names must be verb-led (the name doubles as the imperative `/command`). Renames applied: `test-driven-development` to `follow-tdd`, `ui-ux` to `design-ui`, `code-planning` to `create-code-plan`, `obsidian` to `format-for-obsidian`, `writing-blog` to `write-blog-post`, `writing-educative` to `teach-through-writing`, `writing-persuasive` to `write-proposal`. Earlier decision entries reference the pre-rename names.
- 2026-06-06: Debugging skill named `fix` (verb-led, user choice) because Claude Code's bundled `/debug` skill (session debug logs) collides with the obvious name. It is a discipline skill: Iron Law of no fix without a reproduced root cause, feedback-loop-first methodology (synthesized from superpowers systematic-debugging, mattpocock diagnose, 9arm debug-mantra, addyosmani debugging-and-error-recovery), three-failed-fixes architecture escalation, and a hand-off to test-driven-development's Prove-It pattern for the regression test. Pressure-verified: baseline chose rerun-and-merge on a flaky payment test; with-skill refused, citing the rationalization table.
