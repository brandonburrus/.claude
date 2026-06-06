---
name: design-api
description: Use this skill when designing or reviewing an API contract, including
  REST endpoints, GraphQL schemas, resource naming, pagination, error formats,
  versioning, auth scopes, or typed interfaces between modules. Use when the user
  says "design the API", "add an endpoint", "what should this endpoint look like",
  "model this in GraphQL", or is about to expose any new public interface surface.
  Do not use for database schema design (use design-data-schema) or for
  implementing an endpoint whose contract already exists.
---

## Purpose

Design the contract before any implementation exists. The deliverable is the contract artifact (OpenAPI spec, GraphQL SDL, or typed interface definitions) plus the decisions that shaped it; implementation follows the contract, never the reverse. Good interfaces make the right thing easy and the wrong thing hard, and every shortcut taken at design time becomes a permanent commitment once a consumer depends on it.

## Principles (any style)

- **Hyrum's Law.** With enough users, every observable behavior gets depended on: undocumented quirks, error text, ordering, timing. Be intentional about what you expose; do not leak implementation details; plan deprecation at design time.
- **Prefer addition over modification.** New fields are optional and additive. Changing a field's type or removing it breaks consumers; design so evolution never requires it.
- **Validate at boundaries, trust inside.** User input, third-party responses, and config get validated where they enter; internal functions sharing type contracts do not re-validate. Third-party API responses are untrusted data regardless of the vendor.
- **One error strategy, used everywhere.** If some endpoints throw, others return null, and others return an error object, the consumer cannot write correct code. Pick the shape once.
- **One version.** Extend rather than fork; parallel API versions multiply maintenance and create diamond dependencies. GraphQL evolves in place by design; REST should aim for the same via compatible evolution.

## Workflow

1. **Clarify what the codebase cannot answer**: who the consumers are, the access patterns and rough volumes, the auth model, and which operations must be idempotent. Mine the codebase for existing conventions first; ask only the remainder, with a recommended answer per question.
2. **Pick the style if not already fixed**: REST is the default for resource-oriented CRUD and public APIs; GraphQL earns its complexity when diverse clients compose varied views of a shared graph. The project's existing API style wins over preference; do not introduce a second style without flagging it as a decision.
3. **Design in the per-style order below**, applying the hard rules.
4. **Write the contract artifact** (OpenAPI or SDL) and walk the user through the consequential choices made.
5. **Sweep the anti-pattern list** against the result before presenting.

## REST

Design order: resources and relationships (nouns) -> methods with correct semantics -> request/response schemas -> error responses -> pagination, filtering, sorting -> auth scheme and per-endpoint scopes -> caching and idempotency -> OpenAPI document.

Hard rules:

- Plural nouns for resources (`/users`, `/orders`), kebab-case path segments, never verbs in URLs
- Field casing follows the project's dominant convention (`camelCase` in JS-centric stacks, `snake_case` otherwise); never mix within one API
- ISO 8601 UTC for all timestamps (`2025-05-31T10:00:00Z`)
- Structured errors with a machine-readable code (`DUPLICATE_EMAIL`) alongside the HTTP status; never raw strings or stack traces. RFC 7807 Problem JSON is the default shape
- Collection responses wrap a `data` array in a top-level object, never a bare array (bare arrays cannot grow pagination metadata later)
- Correct method semantics: GET never mutates, PUT is idempotent full replacement, PATCH is partial update, 201 carries a `Location` header
- Every collection endpoint paginates from day one; retrofitting pagination is a breaking change
- HTTPS only; secrets never in URLs or query strings; validate server-side regardless of client validation

Status code mapping: 400 malformed, 401 unauthenticated, 403 unauthorized, 404 missing, 409 conflict, 422 semantically invalid, 500 internal (with details logged, not returned).

Contextual choices, one row per decision the user should see:

| Decision | Default recommendation |
|---|---|
| Pagination | Cursor-based at scale; offset acceptable for small internal APIs |
| Partial updates | JSON Merge Patch unless operation-level control is needed |
| Versioning | Evolve compatibly without versioning; media-type versioning if unavoidable |
| Auth | OAuth2 + JWT for user-facing; API keys for service-to-service |
| IDs | UUID for public surfaces; numeric internal IDs never exposed raw |

## GraphQL

Design order: model the domain as a graph of types -> naming and nullability -> query fields with pagination contracts -> mutations with typed inputs and payloads -> auth policy per type and field -> demand controls -> deprecation plan -> SDL document.

Hard rules:

- `PascalCase` types, `camelCase` fields and arguments, `SCREAMING_SNAKE_CASE` enum values
- Mutations take a single required `input` argument and return a structured payload type, never a bare scalar or Boolean
- Purpose-built mutations (`archiveOrder`, `updateOrderStatus`), never generic `updateEntity(id, json)`
- Any list that can grow beyond ~20 items uses Relay-style cursor connections; cursors are opaque, never raw offsets
- Typed union payloads for domain errors; the top-level `errors` array is for protocol and execution failures only
- DataLoader (request-scoped batching) is the default N+1 mitigation; a resolver issuing queries in a loop is a defect
- Authorization lives in the business logic layer, expressed uniformly (schema directives delegate to it); never copy-pasted into resolvers
- `@deprecated(reason)` precedes any field removal; introspection is disabled or restricted in production for non-public APIs
- Demand controls are part of the design: depth limits, complexity limits, rate limits

## Anti-patterns (reject on sight)

| Anti-pattern | Why |
|---|---|
| Verbs in REST URLs (`/createUser`) | RPC leaking into a resource model; model actions as resources or sub-resources |
| GET that mutates state | Breaks caching, retries, and prefetching; safety semantics are load-bearing |
| Endpoints returning different shapes by condition | The consumer needs a union type the contract never declared |
| Bare-array collection responses | Cannot add pagination or metadata without breaking every consumer |
| Mutations returning Boolean | Discards the data clients need to update caches, forcing refetches |
| Untyped JSON blobs in inputs | Skips validation, typing, and documentation in one move |
| Unbounded query depth with no limits | One nested query can take down the service |
| Validation scattered through internal code | Signals nobody knows where the boundary is; consolidate at the edge |
| Breaking field changes without deprecation | Hyrum's Law guarantees someone depended on it |

## Gotchas

- **Pagination is a day-one decision.** "We don't need it yet" is true right up until the first consumer has 100 items, at which point adding it breaks the response shape for every existing consumer.
- **Error shape consistency outranks error shape quality.** A mediocre format used everywhere beats a great format used on new endpoints only; consumers code against the worst case.
- **Hyrum's Law applies to your error messages.** Consumers parse error text you never promised; give them machine-readable codes so they have something stable to depend on.
- **The contract artifact is the deliverable, not a formality.** An API designed in prose and implemented from memory drifts on the first endpoint; the OpenAPI or SDL document is what review, codegen, and tests hang off.
- **Existing convention beats this skill's defaults.** A codebase with offset pagination and snake_case everywhere gets more of the same; consistency within an API surface outranks any rule here except the security ones.
