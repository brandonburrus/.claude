# MCP protocol reference

Digest of the official Model Context Protocol documentation and specification, revision 2025-11-25 (modelcontextprotocol.io). Field names and enum values are exact; do not invent fields beyond these.

## Contents

- Primitives
- Tool definitions
- Resources
- Prompts
- Client primitives (sampling, roots, elicitation)
- Transports
- Authorization
- SDK shapes
- Client configuration

## Primitives

| Primitive | Control | Discovery / invocation | Capability declaration |
|---|---|---|---|
| Tools | Model-controlled | `tools/list`, `tools/call` | `tools: {listChanged}` |
| Resources | Application-controlled | `resources/list`, `resources/read`, templates via `resources/templates/list` | `resources: {subscribe, listChanged}` |
| Prompts | User-controlled | `prompts/list`, `prompts/get` with arguments | `prompts: {listChanged}` |

## Tool definitions

- `name`: unique, 1-128 chars, case-sensitive; allowed `A-Z a-z 0-9 _ - .` (no spaces or commas)
- `title` (optional display name), `description` (required, written for the model)
- `inputSchema`: JSON Schema object, never null; defaults to draft 2020-12. No-parameter tools use `{"type": "object", "additionalProperties": false}`
- `outputSchema` (optional): shape of structured output
- `annotations` (hints, untrusted unless the server is trusted): `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` (all boolean)
- Result content types: `text`, `image` (base64 + mimeType), `audio`, `resource_link` (uri/name/description/mimeType), embedded `resource`, and `structuredContent` (JSON object; include a text serialization alongside for compatibility)
- Errors: tool-execution failures return `{"content": [...], "isError": true}` with actionable feedback so the model can self-correct; JSON-RPC protocol errors (-32602 invalid params, -32603 internal) are for malformed requests

## Resources

- `uri` (RFC 3986; `file://`, `https://`, custom schemes), `name`, optional `title`, `description`, `mimeType`, `size`
- Content is `text` or base64 `blob` with `mimeType`
- Optional annotations on content: `audience` (`["user"]`, `["assistant"]`, or both), `priority` (0.0-1.0), `lastModified` (ISO 8601)
- Templates use RFC 6570 URI templates (`wiki://{space}/{page}`); arguments integrate with the completion API
- Subscriptions: client sends `resources/subscribe`; server emits `notifications/resources/updated` and `notifications/resources/list_changed`

## Prompts

- `name`, optional `title`, `description`, `arguments` (each: `name`, `description`, `required` boolean)
- `prompts/get` returns messages whose content types mirror tool results (text, image, audio, embedded resource)

## Client primitives

**Sampling** (`sampling/createMessage`): the server requests an LLM completion through the client. Params: `messages`, optional `modelPreferences` (`hints` by name, `intelligencePriority`/`speedPriority`/`costPriority` 0-1), `systemPrompt`, `maxTokens`, optional `tools` + `toolChoice` (`auto|required|none`). Response carries `role`, `content`, `model`, `stopReason` (`endTurn|toolUse|stopSequence`); on `toolUse` the server executes and re-samples with results. User approval sits in the loop by design.

**Roots** (`roots/list`): client returns permitted directories as `{uri: "file://...", name}`; servers use this instead of guessing filesystem scope; `notifications/roots/list_changed` on change.

**Elicitation** (`elicitation/create`): mid-tool user input. Form mode: flat JSON Schema, primitives and enums only; response `{action: "accept"|"decline"|"cancel", content}`. URL mode: server provides `url`, `elicitationId`, `message` for out-of-band flows (OAuth, payment); completion signaled via `notifications/elicitation/complete`; sensitive data never transits the client. Servers MUST NOT request passwords or API keys via form mode.

## Transports

| Transport | Use | Auth | Notes |
|---|---|---|---|
| stdio | Local, same machine | Environment variables | Newline-delimited JSON-RPC over stdin/stdout |
| Streamable HTTP | Remote, multi-client | OAuth 2.1 / bearer headers | POST for requests, SSE for server streaming |
| HTTP+SSE (old) | Deprecated | n/a | Do not build new servers on it |

Protocol is stateful from `initialize` (capability negotiation) to termination; one client connection per server, the host fans out.

## Authorization (HTTP transports)

- Discovery: RFC 9728 protected-resource metadata via `WWW-Authenticate` on 401 or `/.well-known/oauth-protected-resource`
- Client registration: pre-registered, Client ID Metadata Documents (HTTPS URL as client_id, recommended), or RFC 7591 dynamic registration
- PKCE with `S256` is mandatory; refuse servers that do not advertise it
- `resource` parameter (RFC 8707) binds tokens to the server audience; servers validate audience and reject tokens issued for anything else
- Bearer tokens in the `Authorization` header only, never query strings
- Scopes: least privilege initially; progressive elevation via 403 `insufficient_scope` challenges

## Security obligations

- **Token passthrough forbidden**: never forward client tokens downstream; obtain own credentials (URL elicitation for user-delegated access)
- **Confused deputy**: proxy servers require per-client consent before forwarding to third-party authorization
- **SSRF**: when fetching client-supplied metadata URLs, block private ranges and require HTTPS
- **Sessions**: non-deterministic IDs, bound to user identity, expiring; sessions are not authentication
- **Consent**: clients gate tool invocation and sampling on user approval; local stdio servers execute arbitrary commands at install, so the install command is the consent surface

## SDK shapes

Python (`mcp` package, FastMCP high-level API): decorators generate definitions from type hints and docstrings.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wiki")

@mcp.tool()
def search_pages(query: str, space: str = "ENG") -> str:
    """Search wiki pages by keyword within a space."""
    ...

mcp.run(transport="stdio")
```

TypeScript (`@modelcontextprotocol/sdk`, `McpServer` + zod):

```typescript
const server = new McpServer({ name: "wiki", version: "1.0.0" });
server.tool(
  "search_pages",
  "Search wiki pages by keyword within a space.",
  { query: z.string(), space: z.string().default("ENG") },
  async (args) => ({ content: [{ type: "text", text: ... }] })
);
await server.connect(new StdioServerTransport());
```

Official SDKs also exist for C#, Go, Java (tier 1) and Rust, Swift, Ruby, PHP, Kotlin.

## Client configuration

```json
{
  "mcpServers": {
    "wiki": {
      "command": "uv",
      "args": ["--directory", "/path/to/server", "run", "server.py"],
      "env": { "WIKI_TOKEN": "..." }
    },
    "remote": { "url": "https://api.example.com/mcp" }
  }
}
```

Command entries launch stdio servers; url entries connect Streamable HTTP servers. The authoritative type schema lives at github.com/modelcontextprotocol/specification (schema/2025-11-25/schema.ts).
