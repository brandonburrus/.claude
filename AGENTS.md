# AGENTS.md

This repository is Brandon's personal Claude Code configuration directory (`~/.claude`): settings, a personal skills library, and reference material for improving that library.

## Project Structure

- `skills/` - Personal skills library. Each skill is a kebab-case directory containing `SKILL.md`, with optional `references/` and `scripts/` subdirectories.
- `_refs/` - Cloned open-source skill/agent/hook projects used as reference material for improving the skills library. See `_refs/CATALOG.md` for a full inventory of every ref's skills, agents, and hooks. Never edit files inside `_refs/`; they are read-only references.
- `settings.json` - Claude Code harness configuration (permissions, hooks, env).
- `CLAUDE.md` - Global behavioral instructions loaded into every session.

## Critical Constraints

- All skill files: no emojis, no em dashes, no H1 headings in the body.
- Skill directory name and the `name` frontmatter field must match exactly (kebab-case).
- Skill scripts are Python only, run via `uv run`, with dependencies declared inline using PEP 723 metadata (no venvs, no requirements files).
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
- 2026-06-06: `write-adr` mines the conversation first and interrogates only gaps, enforces a significance gate (conventions and cheap-to-reverse choices go to AGENTS.md, not the ADR log), requires concrete revisit-when conditions, and treats accepted ADRs as immutable (supersede, never edit). The rsg weighted evaluation-criteria table is optional, kept only for decisions actually scored on multiple criteria, to protect the two-minute readability rule.
