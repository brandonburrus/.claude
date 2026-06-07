# hooks/

Hook scripts executed by the Claude Code harness on session events. Each script is wired in via the `hooks` block in `../settings.json`; the script file is re-read per invocation, but the settings wiring only loads at session start, so wiring changes need a fresh session to take effect.

## Conventions

- Language by weight: bash + `jq` for short pattern checks (the PreToolUse Bash guards), Python stdlib + system `python3` when logic outgrows jq (the AGENTS.md injector). Neither uses `uv run`: hooks fire on every matching tool call and must not pay dependency-resolution latency.
- Wire bash hooks via `bash ~/.claude/hooks/<name>.sh` and Python via `python3 ~/.claude/hooks/<name>.py`: the explicit interpreter means the scripts never need an executable bit (`chmod` is denied by this repo's permissions anyway).
- Convenience hooks fail open (exit 0 on any internal error); security hooks fail closed. State the choice in the script docstring.
- Hooks parse stdin as JSON, never regex the raw stream. Event stdin shapes and output schemas are documented in `../skills/create-claude-hook/references/hook-events.md`.
- Per-session state goes under `~/.cache/claude-agents-md/` style cache dirs, never inside this repo.

## Scripts

- `inject-agents-md.py` - Auto-injects AGENTS.md files (Claude Code natively loads only CLAUDE.md). Root AGENTS.md at SessionStart via stdout; nested ones lazily on PostToolUse (Read|Edit|Write|NotebookEdit) via additionalContext, walking the touched file's ancestry up to cwd. Dedup is per session per file via path+mtime state keyed by session_id plus transcript basename (isolates subagents from the main loop); compaction clears the state so files re-inject. Files over 10KB inject as a pointer. Test battery pattern: pipe hand-built event JSON through the script and assert stdout/exit codes.
- `block-interactive-cmds.sh` - PreToolUse(Bash) guard. Denies `cp`/`mv`/`rm` at a statement boundary without an `-f` flag, because macOS aliases them to the `-i` interactive variants and the agent then hangs on an unanswerable prompt. Bypasses (`command rm`, absolute path, backslash) are allowed through. Fails open: non-matching or unparseable input exits 0.
- `block-gh-watch.sh` - PreToolUse(Bash) guard. Denies `gh run watch` / `gh run list --watch`, which poll every ~3s and can exhaust the 5000/hr GitHub API quota; the denial reason points the agent at a single `gh run view`. Fails open.
