---
name: code-planning
description: IMPORTANT - Use when planning out code implementations. This includes new features, bug fixes, refactors, or any kind of code change.
---

Produce a structured implementation plan before writing any code. The plan is the deliverable — do not begin implementation until the user approves it.

## Workflow

1. Analyze the request. Identify ambiguities and ask clarifying questions before drafting.
2. Gather context — read relevant files, search the codebase, check existing patterns.
3. Draft the plan using the template below.
4. Include every applicable section. Omit a section only when it genuinely does not apply to the change.
5. Ground every claim in actual code — cite files, functions, types. Do not speculate.
6. Present the plan and ALWAYS wait for explicit user approval before proceeding.

## Template

```markdown
# Code Plan: <Short Title>

## File Summary
| Action   | File | Notes |
| -------- | ---- | ----- |
| New      | ...  | ...   |
| Modified | ...  | ...   |
| Deleted  | ...  | ...   |

## Tasks
| #   | Task        | Files     | Subagent       |
| --- | ----------- | --------- | -------------- |
| 1   | ...         | ...       | ...            |

### Security Considerations
- Auth/authz changes, input sanitization, secret handling
- New attack surfaces introduced by the change

### Infrastructure Changes
- Resources created, modified, or destroyed (cloud, DB, networking, IAM)
- Environment-specific considerations (dev/staging/prod differences)
- Config and secrets changes

### Migration and Rollback
- Data migration steps if applicable
- How to roll back safely if the change fails in production

### Dependencies
- New packages, services, or tools required
- Prerequisites that must be completed before this work can start
- Blockers from other teams or PRs

### Testing Strategy
- What to test (unit, integration, e2e) and why
- Key scenarios and edge cases to cover
- How to run and verify tests

### Integration Points
- External systems, APIs, services touched (direction + mechanism)
- Auth model, rate limits, retry behavior

### Side Effects
- File writes, network calls, process spawning, state mutations
- Anything that changes system state beyond the immediate return value

### Error Handling
- How failures are caught, propagated, or surfaced to the user
- Logging strategy (what level, when, what context)

## Data Schemas
- Structures created or modified (field names, types, relationships)
- Include Zod schemas, DB table shapes, API request/response types as applicable

### Data Flow
- How data enters the system, transforms between layers, and where it persists
- Include direction (inbound/outbound) and transport (HTTP, event, file, queue)

### Validations
- Guards, constraints, assertions to add or modify
- Where each check occurs (boundary, service, DB) and failure behavior

### Business Logic
- Core rules, decisions, branching behavior affected by the change
- Algorithms, state machines, or workflows being introduced or modified

```

## Section guidance

**File Summary** — every file created, modified, or deleted. This is the contract — the implementation should match this list.
**Tasks table** — one row per discrete unit of work. Include the specific files touched and who does it (subagent type or "direct" for trivial changes).
**Infrastructure Changes** — include the full resource identifiers (ARN, path, config key). Note which environments are affected and in what order changes should be applied.
**Security Considerations** — omit only when the change touches no auth, no user input, no secrets, and no network boundaries.
**Migration and Rollback** — omit only for purely additive changes with no data migration and no breaking changes.
**Dependencies** — include version constraints. Flag any dependency that must merge or publish before this work can start.
**Integration Points** — include the HTTP method, path, auth mechanism, and expected response shape for any API touched.
**Error Handling** — distinguish between errors surfaced to users and errors logged internally. Specify log levels.
**Data Schemas** — derive from actual DDL, Zod schemas, or interface definitions in the codebase. Do not invent field names.
**Data Flow** — trace the full path from input to persistence. If the change introduces a new path, diagram it. If it modifies an existing path, describe the before and after.
**Validations** — specify the exact check, where it runs, and what happens on failure (error code, message, exit behavior).
**Business Logic** — if the logic involves state transitions, document the states and transitions. If it involves conditional branching, enumerate the conditions and outcomes.

## Guardrails

- Do not pad the plan with generic advice. Every statement should be specific to this change.
- Do not include implementation code in the plan. Describe what will be built, not how to type it.
- If a section would be empty, omit it entirely rather than writing "N/A" or "None".
- If you lack information to fill a section, say so explicitly and ask the user.
- Plans for changes touching production data or infrastructure must include a rollback section.
