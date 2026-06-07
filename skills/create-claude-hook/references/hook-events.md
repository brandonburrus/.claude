# Hook events and I/O reference

Digest of the official Claude Code hooks documentation (code.claude.com/docs/en/hooks). Field names and enum values are exact; do not invent fields beyond these.

## Contents

- Event catalog
- Settings shape
- Stdin JSON
- Exit codes
- JSON output schema
- Matchers
- Execution model

## Event catalog

| Event | Fires | Matcher values | Blocks? |
|---|---|---|---|
| SessionStart | session begins/resumes | startup, resume, clear, compact | no |
| UserPromptSubmit | user submits prompt | none | yes |
| UserPromptExpansion | command/skill expands | command name | yes |
| PreToolUse | before a tool call | tool name | yes |
| PermissionRequest | permission dialog shows | tool name | yes |
| PermissionDenied | auto-mode denies a call | tool name | no |
| PostToolUse | after tool succeeds | tool name | no |
| PostToolUseFailure | after tool fails | tool name | no |
| PostToolBatch | after a parallel batch | none | no |
| Notification | notification sent | permission_prompt, idle_prompt, auth_success, elicitation_* | no |
| SubagentStart / SubagentStop | subagent spawned / finished | agent type name | no |
| TaskCreated / TaskCompleted | task list changes | none | no |
| Stop | Claude finishes responding | none | yes |
| StopFailure | turn ends on API error | rate_limit, overloaded, billing_error, server_error, ... | no |
| InstructionsLoaded | CLAUDE.md/rules loaded | session_start, include, compact, ... | no |
| ConfigChange | config file changes mid-session | user_settings, project_settings, local_settings, policy_settings, skills | yes |
| CwdChanged | working directory changes | none | no |
| FileChanged | watched file changes | literal filenames split on \| | no |
| WorktreeCreate / WorktreeRemove | worktree lifecycle | none | create: yes |
| PreCompact / PostCompact | around compaction | manual, auto | no |
| SessionEnd | session terminates | clear, logout, other, ... | no |

## Settings shape

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "if": "Bash(git *)",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.sh",
            "timeout": 10,
            "async": false,
            "statusMessage": "Checking..."
          }
        ]
      }
    ]
  }
}
```

- `type`: `command` (script, stdin JSON), `http` (POST the JSON to `url`), `mcp_tool` (`server`+`tool`+`input`), `prompt` (single-turn model judgment, returns ok/reason), `agent` (multi-turn with tools, experimental)
- `args` array switches command to exec form (no shell interpretation); without it the command string runs in a shell
- `if` accepts permission-rule syntax (`Bash(git *)`, `Edit(*.ts)`) on tool events only; fails open when unparseable
- Timeout defaults: command/http/mcp_tool 600s (UserPromptSubmit 30s), prompt 30s, agent 60s
- `async: true` runs in background; `asyncRewake: true` wakes Claude when an async hook exits 2
- Locations: `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, plugin hooks.json, and skill/agent frontmatter (`Stop` in agent frontmatter becomes `SubagentStop`)
- `disableAllHooks: true` disables everything

## Stdin JSON

Common fields: `session_id`, `cwd`, `hook_event_name`, plus per-event:

| Event | Key fields |
|---|---|
| PreToolUse / PostToolUse / PermissionRequest | `tool_name`, `tool_input` (the tool's arguments object, e.g. `.tool_input.command` for Bash, `.tool_input.file_path` for Edit) |
| PostToolUseFailure | `tool_name`, `tool_input`, error details |
| UserPromptSubmit | `prompt` |
| UserPromptExpansion | `command`, `expanded_text` |
| SessionStart | `source` |
| Stop | `stop_hook_active` (true if a Stop hook already blocked once this turn; guard against infinite loops with it) |
| SubagentStart/Stop | `agent_type` |
| ConfigChange | `source`, `file_path` |
| CwdChanged | `new_cwd` |
| FileChanged | `file_path`, `watchPaths` |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success; stdout parsed for the JSON output schema. On SessionStart/UserPromptSubmit, plain stdout is added to context. PreToolUse exit 0 does NOT auto-approve; normal permission flow continues unless the JSON says otherwise |
| 2 | Blocking error; stderr is fed to Claude as the reason; stdout JSON is IGNORED. On non-blockable events, stderr is shown to the user and execution continues |
| other | Non-blocking error; action proceeds; first stderr line shown in transcript |

## JSON output schema (exit 0)

```json
{
  "decision": "block",
  "reason": "why",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "what Claude reads to self-correct",
    "additionalContext": "text injected for Claude",
    "updatedInput": {"command": "rewritten args (PreToolUse only)"},
    "retry": true
  },
  "systemMessage": "user-facing transcript warning",
  "suppressOutput": false
}
```

Per event: PreToolUse uses `permissionDecision`/`updatedInput`; Stop and PostToolUse use top-level `decision: "block"` + `reason`; UserPromptSubmit uses `additionalContext`; PermissionRequest uses `hookSpecificOutput.decision.behavior` and `updatedPermissions`; PermissionDenied uses `retry`. `defer` exists for non-interactive mode only. Prompt/agent hook types return `{"ok": true|false, "reason": "..."}` instead.

## Matchers

- Exact tool name (`Bash`), alternation (`Edit|Write`), regex when non-alphanumeric chars present (`mcp__.*__write`, `^Notebook.*`)
- MCP tools: `mcp__<server>__<tool>`
- Empty or omitted matcher matches all
- FileChanged matchers are literal filenames separated by `|`, not regex

## Execution model

- All matching hooks run in parallel to completion; identical commands deduplicate
- Permission decisions merge restrictively: deny > ask > allow; additionalContext from every hook is kept
- A PreToolUse deny blocks even in bypassPermissions mode; hooks tighten, never loosen
- `${CLAUDE_PROJECT_DIR}` resolves to the project root in commands; `CLAUDE_ENV_FILE` (SessionStart/CwdChanged/FileChanged/Setup) accepts `export VAR=value` lines that preface every later Bash command
- Debugging: `/hooks` browser lists configured hooks per event; transcript shows per-hook one-liners; `claude --debug-file <path>` logs matches, exit codes, and output
