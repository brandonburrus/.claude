---
name: create-claude-hook
description: >-
  Use this skill when creating, editing, debugging, or improving a Claude Code
  hook, meaning the scripts and settings entries that run automatically on
  harness events such as PreToolUse, PostToolUse, SessionStart, Stop, or
  UserPromptSubmit. Use when the user says "create a hook", "block X
  automatically", "run the formatter after every edit", "inject context at
  session start", "guard against Y before it happens", or "the hook isn't
  firing". Do not use for skills (use create-skill), agents (use
  create-claude-agent), or settings changes with no hook script involved (use
  the bundled update-config).
---

## Purpose

Author a Claude Code hook: pick the right event, write a script that parses the event's stdin JSON and answers through exit codes or structured JSON, wire it into settings, and prove it fires. Hooks are the harness's enforcement layer; unlike instructions, a hook cannot be talked out of its rule, which is exactly why the rule must be precise. The full event list, stdin shapes, and output schema live in [references/hook-events.md](references/hook-events.md); read it before writing, because the field names are exact and commonly hallucinated.

## Workflow

### 1. Pick the event from the intent

| Intent | Event and mechanism |
|---|---|
| Block or rewrite a tool call before it runs | `PreToolUse` + JSON `permissionDecision` (deny/allow/ask) or `updatedInput` |
| React to a completed change (format, lint, check) | `PostToolUse` (matcher on Edit\|Write) |
| Inject context every session | `SessionStart`, stdout becomes context |
| Inject or gate on each user prompt | `UserPromptSubmit` (stdout = context, exit 2 = block) |
| Keep Claude working until a condition holds | `Stop` + `decision: block` with the reason |
| Set up environment per directory | `SessionStart`/`CwdChanged` writing to `$CLAUDE_ENV_FILE` |
| React to subagent lifecycle | `SubagentStart`/`SubagentStop` (matcher = agent type) |
| Audit or veto config changes | `ConfigChange` (can block) |
| Re-inject rules after compaction | `SessionStart` with `compact` matcher, or `PostCompact` |

Blockable events: `PreToolUse`, `UserPromptSubmit`, `Stop`, `ConfigChange`, `PermissionRequest`, `WorktreeCreate`. Everything else observes.

### 2. Choose the hook type

`command` (default): a script receiving JSON on stdin. `prompt`: a single-turn model judgment returning ok/reason, for rules that need reading comprehension rather than pattern matching. `agent`: multi-turn verification with tools, expensive, for checks that must inspect files. Prefer `command` whenever the rule is mechanically checkable; it is faster, free, and deterministic.

### 3. Write the script

Language: bash + `jq` for short pattern checks; Python (system `python3`, stdlib only) when logic outgrows jq. Blocking hooks sit on the critical path, so keep them fast and dependency-free; `uv run` resolution is fine for non-blocking async hooks but adds startup latency a PreToolUse hook should not pay.

Script rules:

- **Parse stdin as JSON** (`jq -r '.tool_input.command'`, `json.load(sys.stdin)`); never regex the raw stream, the input is attacker-influenceable text inside a JSON envelope
- **Answer precisely.** Exit 0 with JSON on stdout for structured decisions; exit 2 with the reason on stderr to block crudely; any other exit is a non-blocking error. For PreToolUse denials prefer the JSON form, because the reason string is what Claude reads to self-correct: make it state the rule, why, and the compliant alternative
- **Decide fail-open vs fail-closed deliberately.** Convenience hooks (formatters, notifications) fail open: exit 0 on any internal error so a broken hook never wedges the session. Security hooks (secret guards, destructive-command blocks) fail closed: an unparseable input is a deny, because attackers send unparseable inputs on purpose
- **Match narrowly.** The settings `matcher` (exact, regex, `mcp__server__tool`) plus early returns in the script; a hook that fires on every Bash call pays its latency on every Bash call
- Anchor patterns against bypass: a command check matching `rm ` misses `command rm`, `/bin/rm`, and `foo && rm`; match on word boundaries after separators (`^|[;&|]`)

Example, a deny hook in the canonical shape:

```bash
#!/bin/bash
# Block edits to .env files; secrets do not get machine-edited in this repo.
file=$(jq -r '.tool_input.file_path // empty')
case "$file" in
  *.env|*.env.*) jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Edits to .env files are blocked; change .env.example and let the user copy values manually."
    }
  }'; exit 0;;
esac
exit 0
```

### 4. Wire it into settings

Hook scripts live in `~/.claude/hooks/` (personal) or `.claude/hooks/` (project); the settings entry goes in the matching settings.json under `hooks.<Event>` with a `matcher` and a `command` (use `${CLAUDE_PROJECT_DIR}` for project-relative paths). Set `timeout` below the 600s default for anything blocking; mark long observers `async: true`. Wiring mechanics beyond this are the bundled update-config skill's territory.

### 5. Test before trusting

A hook is config plus code, and both fail silently. Test in two layers:

1. **Script alone**: pipe a hand-built stdin JSON through it and assert the output for the deny case, the allow case, and garbage input (`echo '{"tool_input":{"file_path":".env"}}' | ./hook.sh`). The garbage case is where fail-open/fail-closed actually gets verified
2. **Live**: trigger the event in a session and confirm via the `/hooks` browser and the transcript that it fired and did what the test predicted; `claude --debug-file` shows matches, exit codes, and output when it does not

## Gotchas

- **Settings hooks load at session start.** Editing a hook's settings entry mid-session may not take effect until reload; the script file itself is re-read per invocation, so iterate on the script, not the wiring.
- **Exit 2 ignores your JSON.** Structured output is parsed only on exit 0; a script that emits a careful permissionDecision and then exits 2 gets the crude path. Pick one mechanism per code path.
- **stdout is context on some events.** SessionStart and UserPromptSubmit stdout lands in Claude's context, so debug prints become prompt injection against yourself; log to stderr or a file.
- **Multiple matching hooks merge restrictively.** deny beats ask beats allow across all hooks on the same event; a permissive hook cannot override a strict one, and identical commands are deduplicated.
- **A PreToolUse deny outranks bypassPermissions.** Hooks tighten policy and nothing loosens it; this makes deny hooks the right home for never-rules that must survive any session mode.
- **Hooks run with your full user permissions.** A hook is arbitrary code executing on harness events; review what you wire in, quote variables, and never embed secrets in the script (env vars exist).
