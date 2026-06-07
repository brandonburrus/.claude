---
name: create-claude-agent
description: >-
  Use this skill when creating, editing, or improving a Claude Code subagent
  or agent persona, meaning the Markdown agent definitions in ~/.claude/agents
  or .claude/agents. Use when the user says "create an agent", "make a
  subagent for X", "add a reviewer agent", "the agent isn't triggering", or
  wants a reusable role with its own system prompt, tools, and model. Do not
  use for skills (use create-skill), for hooks (use create-claude-hook), or
  for one-off subagent dispatch that needs no saved definition (just use the
  Agent tool).
---

## Purpose

Author a Claude Code subagent definition: a Markdown file whose frontmatter configures identity, tools, and model, and whose body becomes the agent's entire system prompt. Do not start writing until the role is unambiguous, and do not declare it done until it has been spawn-tested; an agent verified only by reading it is unverified. The exact frontmatter surface lives in [references/agent-config.md](references/agent-config.md); read it before writing, because several fields are commonly hallucinated.

## Phase 1: Establish the role

A subagent is a single role with a single output format. Confirm before writing:

1. What task does it perform, start to finish, and what does it return? (Its final message is its entire output; the parent sees nothing else)
2. Should this be an agent at all? The layer test: a **skill** is a workflow the current agent follows; an **agent** is a role with its own context window, tool surface, and perspective; a **command/explicit invocation** is the entry point that composes them. Reach for an agent when the work benefits from context isolation (verbose output the parent does not need), a restricted tool surface, or an independent perspective (review, audit). A second role appearing during the interview means a second agent, not a bigger one.
3. When should the parent delegate to it automatically? (This becomes the description)

## Phase 2: Design decisions

- **Tools**: omitting `tools` inherits everything, which is correct for general workers and wrong for judges. Reviewers and auditors get read-only allowlists (`Read, Grep, Glob, Bash`); an agent that cannot edit cannot "fix" what it was asked to evaluate. `disallowedTools` subtracts from inheritance when the list is shorter to express.
- **Model**: default is `inherit`. Pin `haiku` for high-volume mechanical work, `sonnet` for focused single-domain roles, `opus` only when the role genuinely needs it; a pinned model is a cost and capability decision, so record why.
- **Skills**: list library skills in the `skills` field to preload their full content at startup (the agent does not browse the registry reliably mid-task; preloading is the guarantee).
- **Memory**: add `memory: user` (or `project`) only for agents that genuinely learn across sessions (a reviewer accumulating codebase-specific findings); it adds curation overhead.
- **Autonomy**: subagents cannot ask the user questions or spawn other subagents (no AskUserQuestion, no Agent tool). Write the body for autonomous execution: decide-and-disclose instead of ask, return structured results instead of conversation.

## Phase 3: Write the definition

Location: `~/.claude/agents/<name>.md` for personal agents, `.claude/agents/<name>.md` for project agents. Template:

```markdown
---
name: docs-link-checker
description: Use this agent to verify documentation links and cross-references
  after editing docs. Use proactively after any change to *.md files that adds
  or modifies links.
tools: Read, Grep, Glob, Bash
model: haiku
---

You are a documentation link checker. Your job is to find broken links,
anchors, and cross-references in Markdown documentation and report them
precisely. You never edit files.

## Process

1. ...

## Output format

Return a Markdown report with exactly these sections: ...

## Rules

- Report file:line for every finding; a finding without a location is noise.
- ...
```

Body rules:

- The body is the agent's ENTIRE system prompt; it does not receive the Claude Code system prompt, so include the operating rules it needs (it does still get CLAUDE.md and the environment basics, so do not duplicate the global rules)
- Open with role and scope in two sentences, then process, then an explicit output format, then rules with reasons
- Specify the output format concretely; the final message is the deliverable, and an unspecified format produces a different shape every run
- No emojis, no em dashes (library conventions apply to agent files too)

**The description field** drives automatic delegation exactly like a skill description: triggers and boundaries, never a workflow summary. Include "use proactively" plus the concrete condition when the agent should fire without being named. Write it last, after the body settles the true scope.

**The name field** is the agent's identity: lowercase-and-hyphens, and unique within its scope, because two files declaring the same name silently discard one of them with no warning.

## Phase 4: Verify by spawning

Reading an agent file tests nothing; spawn it.

1. Run a realistic task through the agent (Agent tool with its type, or `@agent-<name>`) and check: did it stay in role, respect its tool limits, and return the specified output format?
2. Run the same task without the agent as a baseline; if the baseline output is equivalent, the agent's body is dead weight, sharpen or delete it.
3. Trigger check: judge 3-4 realistic prompts against the description alone; would the parent delegate? Misses are description edits.
4. New agents may not appear in the registry until the session reloads; spawn-by-path testing or a fresh session confirms registration.

## Gotchas

- **Most "agent not working" reports are description problems.** The parent never delegates because the description names the output, not the trigger. Fix the description before touching the body.
- **An agent is not a skill wearing a trench coat.** If the content is a procedure the main agent should follow inline, it is a skill; turning it into an agent buys context isolation at the cost of conversation access, user questions, and shared state. Choose for the isolation, not the novelty.
- **Tool inheritance includes MCP tools.** An agent with `tools` omitted inherits every connected MCP server's tools too; judges and reviewers should allowlist precisely for this reason.
- **The final message is the only output.** Anything the agent "did" but did not state in its last message is invisible to the parent; the body must demand a complete final report.
- **Stop hooks in agent frontmatter become SubagentStop at runtime**, and plugin-installed agents silently ignore `hooks`, `mcpServers`, and `permissionMode`; details in the reference.
