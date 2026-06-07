# Subagent configuration reference

Digest of the official Claude Code subagent documentation (code.claude.com/docs/en/sub-agents). Field names and enum values are exact; do not invent fields beyond these.

## Contents

- Locations and precedence
- Frontmatter fields
- Tool restriction semantics
- Invocation modes
- Context isolation
- Built-in agents

## Locations and precedence

Highest to lowest: managed settings agents, `--agents` CLI JSON (session-only), project `.claude/agents/`, user `~/.claude/agents/`, plugin `agents/`. Both project and user directories are scanned recursively; subdirectories do not affect identity. Only the `name` frontmatter field determines identity (the filename does not have to match), and duplicate names within one scope keep one file and silently discard the other.

## Frontmatter fields

| Field | Required | Semantics |
|---|---|---|
| `name` | yes | Lowercase letters and hyphens; the agent's identity and the `agent_type` reported to hooks |
| `description` | yes | Drives automatic delegation; "use proactively" encourages unprompted use |
| `tools` | no | Allowlist; omitted = inherit ALL parent tools including MCP tools. `Agent(worker, researcher)` syntax restricts spawnable subagents |
| `disallowedTools` | no | Denylist applied before `tools`; a tool in both lists is removed |
| `model` | no | `sonnet`, `opus`, `haiku`, a full model ID, or `inherit` (default). Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env var, per-invocation parameter, frontmatter, parent model |
| `permissionMode` | no | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. Parent `bypassPermissions`/`acceptEdits`/auto override it. Ignored for plugin agents |
| `maxTurns` | no | Cap on agentic turns |
| `skills` | no | Skill names whose FULL content is injected at startup; cannot preload skills marked `disable-model-invocation: true`. Unlisted skills remain invocable via the Skill tool |
| `mcpServers` | no | Server name references or inline server definitions; inline servers connect at start, disconnect at finish. Ignored for plugin agents |
| `hooks` | no | Lifecycle hooks scoped to this agent (PreToolUse, PostToolUse, Stop). `Stop` converts to `SubagentStop` when run as a subagent. Ignored for plugin agents |
| `memory` | no | `user` (~/.claude/agent-memory/<name>/), `project` (.claude/agent-memory/<name>/), or `local`. First 200 lines or 25KB of MEMORY.md injected; Read/Write/Edit auto-enabled |
| `background` | no | `true` = always run as background task; permissions that would prompt are auto-denied in background |
| `isolation` | no | `worktree` = run in a temp git worktree branched from the default branch; auto-cleaned if unchanged |
| `effort` | no | `low`, `medium`, `high`, `xhigh`, `max`; overrides session effort |
| `color` | no | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | no | Auto-submitted first user turn when the agent runs as the MAIN session agent (`--agent` flag) |

The Markdown body after the frontmatter is the agent's system prompt.

## Tool restriction semantics

- Omitted `tools` inherits everything available to the parent, MCP included.
- These tools are never available to subagents regardless of listing: `Agent` (subagents cannot spawn subagents), `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`.
- To block specific spawnable agents use `permissions.deny` with `Agent(subagent-name)`; the `Agent(...)` tools syntax is allowlist-only.

## Invocation modes

- **Automatic delegation**: the parent matches task against `description`.
- **@-mention**: `@agent-<name>` guarantees that agent handles one task.
- **Session-wide**: `claude --agent <name>` or `agent` in settings.json makes it the main agent; its system prompt REPLACES the default Claude Code system prompt in that mode, and `initialPrompt` applies.
- **CLI-defined**: `--agents '<json>'` accepts the same fields with `prompt` carrying the body.

## Context isolation

A fresh (non-fork) subagent starts with: its own body as system prompt plus environment basics, the delegation message, the full CLAUDE.md hierarchy, a git status snapshot from parent session start, and any preloaded skills. It does NOT get the parent's conversation history or the full Claude Code system prompt. Built-in Explore and Plan skip CLAUDE.md and git status; custom agents cannot opt out of them.

Only the final message returns to the parent; intermediate tool calls stay isolated. Each invocation is a fresh instance; transcripts persist under the session directory and survive parent compaction.

Forked subagents (`CLAUDE_CODE_FORK_SUBAGENT=1`, default-on in recent versions) instead inherit the parent's entire conversation, tools, and model, run in background by default, and reuse the parent's prompt cache.

## Built-in agents

| Agent | Model | Notes |
|---|---|---|
| `Explore` | Haiku | Read-only search; skips CLAUDE.md and git status; thoroughness specified in prompt |
| `Plan` | inherits | Read-only research for plan mode; skips CLAUDE.md and git status |
| `general-purpose` | inherits | All tools |
| `claude-code-guide` | Haiku | Claude Code questions |

Custom agent names must not collide with these.
