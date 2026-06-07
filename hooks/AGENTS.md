# hooks/

Hook scripts executed by the Claude Code harness on session events. Each script is wired in via the `hooks` block in `../settings.json`; the script file is re-read per invocation, but the settings wiring only loads at session start, so wiring changes need a fresh session to take effect.

## Conventions

- Python stdlib only, system `python3`, no `uv run`: hooks on the PostToolUse path run on every matching tool call and must not pay dependency-resolution latency.
- Convenience hooks fail open (exit 0 on any internal error); security hooks fail closed. State the choice in the script docstring.
- Hooks parse stdin as JSON, never regex the raw stream. Event stdin shapes and output schemas are documented in `../skills/create-claude-hook/references/hook-events.md`.
- Per-session state goes under `~/.cache/claude-agents-md/` style cache dirs, never inside this repo.

## Scripts

- `inject-agents-md.py` - Auto-injects AGENTS.md files (Claude Code natively loads only CLAUDE.md). Root AGENTS.md at SessionStart via stdout; nested ones lazily on PostToolUse (Read|Edit|Write|NotebookEdit) via additionalContext, walking the touched file's ancestry up to cwd. Dedup is per session per file via path+mtime state keyed by session_id plus transcript basename (isolates subagents from the main loop); compaction clears the state so files re-inject. Files over 10KB inject as a pointer. Test battery pattern: pipe hand-built event JSON through the script and assert stdout/exit codes.
