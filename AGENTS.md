# AGENTS.md

This repository is Brandon's personal Claude Code configuration directory (`~/.claude`): settings, a personal skills library, and reference material for improving that library.

## Project Structure

- `skills/` - Personal skills library. Each skill is a kebab-case directory containing `SKILL.md`, with optional `references/` and `scripts/` subdirectories.
- `_refs/` - Cloned open-source skill/agent/hook projects used as reference material for improving the skills library. See `_refs/CATALOG.md` for a full inventory of every ref's skills, agents, and hooks. Never edit files inside `_refs/`; they are read-only references.
- `agents/` - Personal subagent definitions (see `agents/AGENTS.md`).
- `hooks/` - Hook scripts wired into `settings.json` (see `hooks/AGENTS.md`).
- `settings.json` - Claude Code harness configuration (permissions, hooks, env).
- `CLAUDE.md` - Global behavioral instructions loaded into every session.

## Critical Constraints

- All skill files: no H1 headings in the body (the frontmatter `name` serves as the title). The no-emoji and no-em-dash rules are global; see `CLAUDE.md`.
- No "When to Use" or "When NOT to Use" sections in any skill body; the description is the only routing surface. Boundary detail too big for the description becomes a Gotcha; behavioral exceptions attach to the relevant rule.
- No absolute filesystem paths inside skill files; all locations are relative to the skill directory so the library stays portable.
- Skill directory name and the `name` frontmatter field must match exactly (kebab-case), and skill names are verb-led: the name states the action the skill performs (`create-diagram`, `write-adr`, `follow-tdd`), never a topic or noun.
- Skill scripts are Python only, run via `uv run ${CLAUDE_SKILL_DIR}/scripts/<name>.py`, with dependencies declared inline using PEP 723 metadata (no venvs, no requirements files). `${CLAUDE_SKILL_DIR}` is substituted by the harness at invocation, keeping skill files free of absolute paths while commands work from any working directory.
- Reference files within a skill stay one level deep from SKILL.md and get a table of contents when over 100 lines.
- SKILL.md target length is 80-250 lines, hard limit 500; overflow goes to `references/`.
- The `create-skill` skill (`skills/create-skill/SKILL.md`) is the authority on skill conventions; follow it when creating or restructuring any skill.
- `_refs/anthropic-skills` is license-restricted: no extraction, copying, or derivative works (see its LICENSE.txt). Every other ref is open for mining, but check the LICENSE before mining any newly added ref.
- `skills/humanize/references/ai-patterns.md` contains deliberate em dashes inside the pattern-14 "Before" specimen; they are the artifact being taught. Never remove them in convention sweeps.

## Conventions

- Skill descriptions state triggers only, never workflow summaries (a summarized workflow becomes a shortcut that prevents the body from being read).
- New or substantially changed skills get verified per create-skill Phase 5: parallel baseline vs with-skill subagent runs on realistic prompts.
- Always-on rule sets go in `CLAUDE.md`, never the skills library; a skill marked "ALWAYS use" is a routing bet CLAUDE.md does not have to make.
- Skills that teach exact harness or protocol formats (agent frontmatter, hook events, MCP) ground them in a fresh official-docs digest captured under `references/`; these formats are hallucination-prone.
- Agents in `agents/` are thin role wrappers: they preload library skills via the `skills` frontmatter field, and the body carries only identity, tool limits, autonomous overrides (subagents cannot ask the user or act outward), and the output contract.
- Git commits follow conventional commit style (`feat(skills): ...`, `chore: ...`); commit only when asked.

## Key Decisions

- 2026-06-06: The debugging skill is named `fix`. Why: Claude Code's bundled `/debug` skill (session debug logs) collides with the obvious name.
- 2026-06-06: `design-ui` is build-only; auditing existing UI without changing it is out of scope. Why: user choice.
- 2026-06-06: `open-pull-request` is frictionless: no approval gate before `gh pr create`, pending work auto-committed. Why: user chose one-command PR creation.
- 2026-06-06: `triage-issues` was verified by judged trigger checks only. Why: no live tracker was available; shake it down on first real use.
- 2026-06-06: `execute-code-plan` is deferred until the agents phase. Why: user wants the skills library finished first.
- 2026-06-06: `hooks/inject-agents-md.py` auto-injects AGENTS.md files (root at SessionStart, nested lazily on file touch). Why: Claude Code natively loads only CLAUDE.md.
- 2026-06-06: Decision records are gated one-liners; work narrative lives in git history. Why: the log had grown to 25KB of changelog, past the hook's 10KB inline injection cap.
- 2026-06-06: Threat modeling lives inside `harden-security` as a proactive front-section, not a separate `model-threats` skill. Why: same attacker-mindset domain across design and build; avoids a near-duplicate security skill.
