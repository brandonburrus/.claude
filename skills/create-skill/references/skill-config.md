# Skill Configuration Reference

Harness features available to skills beyond `name` and `description`: frontmatter fields, string substitutions, dynamic context injection, and the content lifecycle. Read this when deciding Phase 2 invocation and execution controls, or when a skill needs arguments, tool permissions, or isolated execution.

## Contents

- Frontmatter fields
- Invocation control
- String substitutions
- Dynamic context injection
- Running in a subagent
- Skill content lifecycle
- Listing budget and description caps

## Frontmatter fields

All fields are optional; only `description` is needed for automatic routing. This library additionally requires `name` matching the directory.

| Field | Effect |
|---|---|
| `name` | Display name in skill listings. Defaults to the directory name. The command name (`/skill-name`) always comes from the directory name, not this field |
| `description` | Routing text Claude uses to decide when to load the skill. If omitted, the first paragraph of the body is used |
| `when_to_use` | Extra trigger context appended to the description in the listing. This library folds triggers into `description` instead; the two share one truncation cap |
| `argument-hint` | Autocomplete hint for expected arguments, such as `[issue-number]` |
| `arguments` | Named positional arguments for `$name` substitution. Space-separated string or YAML list; names map to positions in order |
| `disable-model-invocation` | `true` removes the skill from Claude's context entirely; only the user can invoke it via `/name`. Default `false` |
| `user-invocable` | `false` hides the skill from the `/` menu; only Claude can invoke it. Default `true` |
| `allowed-tools` | Tools Claude may use without permission prompts while the skill is active. Grants, does not restrict: unlisted tools remain available under normal permission rules |
| `disallowed-tools` | Tools removed from the pool while the skill is active. Clears on the user's next message |
| `model` | Model override while the skill is active, for the rest of the current turn |
| `effort` | Effort override (`low`, `medium`, `high`, `xhigh`, `max`) while the skill is active |
| `context` | `fork` runs the skill in an isolated subagent context (see Running in a subagent) |
| `agent` | Subagent type when `context: fork` is set: `Explore`, `Plan`, `general-purpose`, or a custom agent. Defaults to `general-purpose` |
| `hooks` | Hooks scoped to the skill's lifecycle |
| `paths` | Glob patterns; the skill auto-loads only when working with matching files |
| `shell` | `bash` (default) or `powershell` for dynamic context injection commands |

## Invocation control

| Frontmatter | User can invoke | Claude can invoke | Context cost when idle |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context |
| `disable-model-invocation: true` | Yes | No | None; not listed to Claude |
| `user-invocable: false` | No | Yes | Description always in context |

Decision rules:

- Side-effect workflows where timing matters (deploy, commit, publish, send message): `disable-model-invocation: true`. Claude should not decide on its own that the code looks ready to deploy.
- Background knowledge that is not a meaningful user action (legacy system context, internal conventions): `user-invocable: false`. It keeps the `/` menu clean without hiding the knowledge from routing.
- Everything else: leave both unset. Most skills in this library are default-invocable.

## String substitutions

Substitution happens once, when the skill content is rendered at invocation. Agents reading the raw SKILL.md file (rather than invoking the skill) see the literal placeholder text.

| Variable | Expands to |
|---|---|
| `$ARGUMENTS` | Everything typed after the skill name. If absent from the body, arguments are appended as `ARGUMENTS: <value>` |
| `$ARGUMENTS[N]` or `$N` | Argument at 0-based position N; shell-style quoting groups multi-word values |
| `$name` | Named argument declared in the `arguments` frontmatter list |
| `${CLAUDE_SKILL_DIR}` | Absolute path of the directory containing this SKILL.md, regardless of working directory |
| `${CLAUDE_SESSION_ID}` | Current session ID, for logging or session-scoped files |
| `${CLAUDE_EFFORT}` | Active effort level |

`${CLAUDE_SKILL_DIR}` is how a skill references its own `scripts/` and `references/` files without an absolute path in the file on disk: write `uv run ${CLAUDE_SKILL_DIR}/scripts/x.py` and the rendered content carries the real path wherever the library is installed. Escape a literal dollar before a digit or argument name with a backslash: `\$1.00`.

## Dynamic context injection

`` !`command` `` runs a shell command while the skill content is being rendered and replaces the placeholder with its output, so the instructions arrive with live data already inlined:

```markdown
## Current changes

!`git diff HEAD`
```

Rules:

- The `!` must start a line or follow whitespace; `` KEY=!`cmd` `` stays literal
- For multi-line commands, open a fenced block with ` ```! `
- Output is inserted as plain text and not re-scanned, so injected output cannot trigger further injection
- This is preprocessing: Claude never sees or runs the command itself, only the result
- Use it when the skill always needs the same live context (a diff, a status, a listing); use normal tool calls when the data needed depends on the task

## Running in a subagent

`context: fork` runs the skill body as the prompt of an isolated subagent with no access to the conversation history. Only useful for skills that contain an explicit task: a body of guidelines forked into a subagent produces nothing, because the subagent receives conventions but no actionable prompt.

The `agent` field picks the execution environment. `Explore` and `Plan` skip CLAUDE.md and git status at startup, so a forked skill on those agents sees only the skill content and the agent's own system prompt.

## Skill content lifecycle

When a skill is invoked, the rendered body enters the conversation once and stays for the rest of the session; the file is not re-read on later turns. Two authoring consequences:

- Write standing instructions, not one-time steps, for guidance that should hold throughout a task ("always tag debug logs" rather than "now tag your logs")
- Put the critical rules early in the body. On auto-compaction, each invoked skill is re-attached keeping only its first 5,000 tokens, and all re-attached skills share a 25,000-token budget filled most-recent-first, so the tail of a long skill and the entirety of long-ago skills can drop

Live editing: changes to a SKILL.md under a watched skills directory take effect within the current session, no restart needed.

## Listing budget and description caps

Skill descriptions sit in context so Claude knows what is available; bodies load only on invocation. The listing has real limits:

- Combined `description` plus `when_to_use` text is truncated at 1,536 characters per skill. Put the key use case first so truncation cuts the tail, not the trigger
- The whole listing gets a budget of about 1 percent of the context window; when it overflows, the least-used skills lose their descriptions first. `/doctor` reports overflow
- This library's 300-600 character description target stays well inside both limits; the cap matters when auditing third-party skills or diagnosing why a skill stopped triggering
