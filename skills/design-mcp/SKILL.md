---
name: design-mcp
description: >-
  Use this skill when designing or reviewing an MCP (Model Context Protocol)
  server, including deciding what becomes a tool versus a resource versus a
  prompt, tool naming and schemas, transport and authorization choices, and
  server security. Use when the user says "build an MCP server", "expose X to
  Claude over MCP", "design the MCP integration", or "should this be a tool or
  a resource". Do not use for consuming MCP servers in harness config (use the
  bundled update-config), for designing the agent that uses the server (use
  design-llm-agent), or for plain HTTP APIs consumed by code (use design-api).
---

## Purpose

Design an MCP server's contract before any implementation: which capabilities it exposes, as which primitives, over which transport, with what authorization, and against which security obligations. The deliverable is the server design (primitive inventory, tool schemas, transport and auth decision, security review) ready to hand to implementation. Exact protocol field names and semantics live in [references/mcp-protocol.md](references/mcp-protocol.md); read it before designing, because the primitive semantics and auth requirements are precise and hallucination-prone.

## Workflow

### 1. Inventory the capabilities and the consumer

What should the model be able to DO, what context should it be able to READ, and what workflows should the USER be able to trigger? Those three questions map directly onto the three primitives, and most design errors are capability-to-primitive misroutes. Also pin who connects: one local user (stdio, simple) or many remote users (HTTP, OAuth, sessions; a different project).

### 2. Route each capability to its primitive

| Primitive | Controlled by | Use for | Misroute smell |
|---|---|---|---|
| Tool | The model decides to invoke | Actions and computations: search, create, transform, call an API | Read-only context modeled as a getter tool the model must guess to call |
| Resource | The application attaches as context | Passive data the client chooses to include: file contents, schemas, records; parameterized via URI templates | Data shoved into tool results that should be addressable and subscribable |
| Prompt | The user explicitly selects | Reusable workflow templates with arguments (slash-command shaped) | Workflow instructions buried in a tool description |

Everything-is-a-tool is the default failure mode; it makes the model responsible for context-fetching decisions the application should own and bloats the tool list (which dilutes selection accuracy, the same fewer-sharper-tools law from design-llm-agent).

### 3. Design the tool surface

- **One tool per logical operation**, named for what it does in the domain (`search_wiki_pages`, not `do_query`); name rules per the reference (1-128 chars, letters, digits, `_`, `-`, `.`)
- **Descriptions are written for the model as the audience**: when to use it, what it returns, what it must not be used for; the description is the routing surface exactly as skill descriptions are
- **Schemas make invalid calls unrepresentable**: typed `inputSchema` with enums and constraints over free strings; `outputSchema` plus `structuredContent` when callers act on the result programmatically (with text serialization alongside for compatibility)
- **Annotations are honest hints**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` set truthfully; clients use them for consent UX, and a destructive tool marked read-only is a lie the user pays for. Treat annotations from other servers as untrusted; they are hints, not enforcement
- **Errors teach the model**: tool-execution failures return `isError: true` with actionable content (what was wrong, what valid input looks like), because the model retries from your error text; protocol errors are reserved for malformed requests

### 4. Design resources and prompts

Resources get stable URIs (custom scheme is fine), `mimeType`, and RFC 6570 templates for parameterized access; add subscriptions only when the data genuinely changes under the client. Prompts carry named, described arguments and exist for the workflows users repeat; a server with zero prompts is common and fine.

### 5. Decide what the server borrows from the client

- **Sampling**: the server requests LLM completions through the client instead of embedding its own key; right for servers whose tools need language work, with user approval in the loop
- **Roots**: ask the client for permitted directories instead of guessing filesystem scope
- **Elicitation**: structured user input mid-tool (form mode, flat schemas, primitives only) or out-of-band URL mode for OAuth and payment flows. Never collect passwords or API keys through form elicitation; that is what URL mode exists for

### 6. Pick transport and authorization

| Situation | Choice |
|---|---|
| Local, single user, same machine | stdio; credentials from environment variables, no OAuth machinery |
| Remote or multi-client | Streamable HTTP; OAuth 2.1 with PKCE (S256), resource-bound tokens (RFC 8707), bearer tokens in headers never query strings |
| Old SSE transport | Deprecated; do not design new servers on it |

Stateless tools beat session state where possible; when sessions exist, IDs are non-deterministic, bound to user identity, and expiring.

### 7. Security review before handoff

- **Token passthrough is forbidden**: the server never forwards client-supplied tokens to downstream APIs; it obtains its own credentials (URL elicitation for user-delegated access) and validates that inbound tokens were issued for this server
- **Confused deputy**: proxy-style servers need per-client consent before forwarding to third-party auth
- **Untrusted inputs everywhere**: tool arguments are model-generated from possibly-hostile context; validate them like any boundary input (harden-security applies in full)
- **Least privilege**: minimal scopes up front, progressive elevation on challenge; destructive operations gated by annotation honesty plus server-side checks, not annotation alone

### 8. Hand off to implementation

Name the SDK (Python `mcp` with FastMCP decorators, or TypeScript `@modelcontextprotocol/sdk` with `McpServer` and zod schemas; shapes in the reference), show the client config the server will need (`.mcp.json` command entry for stdio, url entry for HTTP), and route the build through create-code-plan. Plan the eval loop too: a server is verified by connecting a real client and watching the model actually choose the right tools, which is a design-llm-agent eval in miniature.

## Gotchas

- **The model only sees names, descriptions, and schemas.** Every behavior you hope for must be legible in those three surfaces; a tool that "should be obvious" from its implementation is invisible at selection time.
- **Tool count is a quality dial, not a feature count.** Ten sharp tools outperform thirty thin wrappers around the same API; when coverage pressure grows the list, collapse variants into one tool with an enum parameter.
- **Resources depend on client support.** Not every client surfaces resources or prompts; when the capability must work everywhere, a tool is the lowest common denominator, and that tradeoff is a documented design decision, not an accident.
- **stdio servers inherit the user's full environment.** A local server runs with the user's permissions and their env vars; the consent moment is install time, so the install command and required env must be explicit and minimal.
- **Spec revisions matter.** The protocol versions by date and negotiates at initialize; pin the SDK version in the design and note the spec revision it targets, because primitive semantics have shifted between revisions.
