---
name: create-code-plan
description: Use this skill when planning any non-trivial code implementation, including
  new features, bug fixes, refactors, or architectural changes. Use when the user says
  "plan this", "let's plan before coding", "what's the approach", "how should we
  approach X", or describes a multi-step code change without explicitly asking for
  a plan. Do not use for trivial single-line changes or tasks already fully specified
  with no design decisions remaining.
---

## Purpose

Produce a structured implementation plan before writing any code. The plan is the deliverable: do not begin implementation until the user approves it. A plan exists to surface design decisions, hidden dependencies, and risks while they are still cheap to change.

## Workflow

Copy this checklist and track progress through it:

```text
Plan Progress:
- [ ] 1. Scope check
- [ ] 2. Gather context from the codebase
- [ ] 3. Clarify what the codebase cannot answer
- [ ] 4. Resolve design decisions
- [ ] 5. Draft the plan
- [ ] 6. Self-review
- [ ] 7. Present and wait for approval
```

### 1. Scope check

If the request spans multiple independent subsystems (for example "build chat, billing, and analytics"), do not write one mega-plan. Propose a decomposition into separate plans, one per subsystem, and plan the first one. Each plan should produce working, testable software on its own.

### 2. Gather context from the codebase

Read relevant files, search for existing patterns, map what the change touches. Do this before asking the user anything: every question answerable from the codebase is a wasted round-trip and signals the plan is not grounded. Follow existing patterns in the codebase rather than inventing new ones.

### 3. Clarify what the codebase cannot answer

Ask only the questions that remain. For each question, provide your recommended answer so the user can confirm rather than compose. When questions are independent, batch them in one message; when an answer would change what you ask next, ask one at a time in dependency order.

### 4. Resolve design decisions

For each consequential decision (data model shape, sync vs async, library choice, where logic lives), present 2-3 viable approaches with trade-offs, lead with your recommendation, and get the user's pick before drafting. Jumping straight to one approach hides the decision from the user and bakes it into every downstream section. Record the chosen approach and rationale in the plan's Approach section.

Skip this step only when the change has no decisions where a reasonable engineer would choose differently.

### 5. Draft the plan

Use the template below. Include every applicable section; omit a section only when it genuinely does not apply. Ground every claim in actual code: cite files, functions, types. Do not speculate.

### 6. Self-review

Run this checklist against the draft before presenting it. Fix issues inline.

1. **Spec reconciliation**: re-read the original request or spec and confirm three things: every requirement maps to a task (add tasks for gaps), no part of the plan contradicts what the spec stated (stack, constraint, success criterion), and no requirement is too vague or unmeasurable to plan against. A contradiction is a silent divergence the user never approved; a vague requirement gets kicked back to the user or clarify-ambiguity, not planned around with a guess.
2. **Placeholder scan**: search the plan for the patterns in No Placeholders below. Replace each with concrete detail or a question for the user.
3. **Naming consistency**: types, function names, and file paths used in later tasks must match what earlier tasks define. `createTask` in Task 2 but `addTask` in Task 5 is a plan defect.
4. **Dependency ordering**: can each task execute in the listed order? If Task 3 needs output from Task 5, reorder.
5. **File summary completeness**: the File Summary must account for every file mentioned in any task. Missing entries mean the implementation will diverge from the plan.
6. **Scope discipline**: does every task trace to the request, or did the plan add abstraction, configurability, or future-proofing nobody asked for? Cut it, or surface it as an explicit option for the user; unrequested flexibility is scope creep in plan form (see Guardrails).

### 7. Present and wait for approval

Present the plan and ALWAYS wait for explicit user approval before implementing. For large plans or work spanning multiple sessions, offer to save the plan to a markdown file so it survives session boundaries and compaction.

## Template

```markdown
# Code Plan: <Short Title>

## Approach
- Chosen approach in 2-3 sentences
- Key decisions made and why (one bullet per decision, including rejected alternative)

## File Summary
| Action   | File | Notes |
| -------- | ---- | ----- |
| New      | ...  | ...   |
| Modified | ...  | ...   |
| Deleted  | ...  | ...   |

## Tasks
| #   | Task | Files | Depends on | Verify | Subagent |
| --- | ---- | ----- | ---------- | ------ | -------- |
| 1   | ...  | ...   | None       | ...    | ...      |

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
- Per feature, the three cases to cover: golden path, error cases, and edge cases (boundaries, empty/null, concurrency)
- How to run and verify tests
- For a web or API surface, the post-implementation live-validation step (validate-web or validate-api against the running app); green tests do not prove the running system works

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

## Risks
| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| ...  | High/Med/Low | ... |

## Open Questions
- Anything still needing a user decision (empty list means none remain)
```

## Task Granularity

Each task should be completable by a single subagent in one focused pass. Size guide:

| Size | Files | Example |
|------|-------|---------|
| S | 1-2 | Add the Zod schema for TaskInput in `src/tasks/schemas.ts` |
| M | 3-5 | One vertical feature slice: endpoint + validation + tests |
| L | 5-8 | Borderline; split unless the files are tightly coupled |
| XL | 8+ | Too large; always break it down |

Split a task when any of these holds:

- Its title contains "and" joining two deliverables (it is two tasks)
- It touches two or more independent subsystems
- Its acceptance cannot be stated in 3 or fewer verifiable conditions

Ordering rules:

- **Slice vertically, not horizontally.** "User can register (schema + endpoint + UI)" beats "all schemas, then all endpoints, then all UI" because each slice delivers working, testable functionality and surfaces integration problems immediately instead of at the end.
- **Order by dependency, foundations first.** Every task's "Depends on" must reference earlier tasks only.
- **Put high-risk or unknown-heavy tasks early.** If an approach is going to fail, fail before the cheap tasks are built on top of it.
- **Mark parallelizable tasks.** Independent slices can run as concurrent subagents; tasks sharing a contract need the contract defined in an earlier task first; migrations and shared-state changes stay sequential.
- **Each task's Verify cell is an exact command or observable check** ("`npm test -- --grep tasks` passes", "POST /tasks returns 201 with id"), not "verify it works".
- For plans over ~6 tasks, group tasks into phases with a checkpoint after each: tests pass, build clean, flow works end to end.

## No Placeholders

Every section and task must contain concrete, actionable content. These are plan failures; never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" without naming what to test
- "Similar to Task N" (repeat the relevant details; the implementer may read tasks out of order)
- Vague scope like "update the UI accordingly" or "wire up the backend"
- References to types, functions, or APIs neither defined in any task nor existing in the codebase

A placeholder is a signal you lack information. Ask the user instead of writing it.

## Section Guidance

**Approach**: one bullet per consequential decision, naming the rejected alternative. This is where step 4's outcomes are recorded so they survive into review.
**File Summary**: every file created, modified, or deleted. This is the contract; the implementation should match this list.
**Tasks table**: one row per discrete unit of work, exact file paths, who executes it (subagent type or "direct" for trivial changes).
**Infrastructure Changes**: include the full resource identifiers (ARN, path, config key). Note which environments are affected and in what order changes apply.
**Security Considerations**: omit only when the change touches no auth, no user input, no secrets, and no network boundaries.
**Migration and Rollback**: omit only for purely additive changes with no data migration and no breaking changes.
**Dependencies**: include version constraints. Flag any dependency that must merge or publish before this work can start.
**Integration Points**: include the HTTP method, path, auth mechanism, and expected response shape for any API touched.
**Error Handling**: distinguish errors surfaced to users from errors logged internally. Specify log levels.
**Data Schemas**: derive from actual DDL, Zod schemas, or interface definitions in the codebase. Do not invent field names.
**Data Flow**: trace the full path from input to persistence. New path: diagram it. Modified path: describe before and after.
**Validations**: specify the exact check, where it runs, and what happens on failure (error code, message, exit behavior).
**Business Logic**: state transitions get the states and transitions documented; conditional branching gets the conditions and outcomes enumerated.
**Risks**: only real risks specific to this change, with a mitigation that names an action, not "be careful".
**Open Questions**: questions blocking implementation belong here only if the user deferred them; otherwise resolve them in step 3.

## Replanning Mid-Flight

Requirements move while a build is in progress: a constraint surfaces, an assumption proves false, a stakeholder changes the target. A plan that cannot absorb that change gets abandoned wholesale or silently drifts from what the code now needs to do. Neither is acceptable; replan deliberately instead.

When a change lands mid-build, run a change-impact assessment before touching the plan. Identify what the change disturbs:

- **Plan items**: which tasks, File Summary entries, and Approach decisions no longer hold.
- **Assumptions**: which recorded decisions or Open Questions the change invalidates.
- **Completed work**: which finished tasks the change contradicts, and whether their output must be reverted, reworked, or kept.

Then classify the scope and act accordingly:

| Scope | Trigger | Action |
| ----- | ------- | ------ |
| Minor | One task's details shift; Approach and dependencies hold | Adjust the affected task in place, note the change in its row, continue. |
| Moderate | A slice of related tasks is affected; the rest of the plan stands | Replan only the affected slice (re-run steps 4-6 for those tasks), preserve unaffected tasks and their order. |
| Major | The Approach, data model, or task ordering no longer holds | Stop. Escalate to the user with the impact assessment and replan from step 1; do not patch a plan whose foundation moved. |

Record the assessment and the chosen scope in the plan so the divergence is visible and approved, never silent. When the scope is unclear between two levels, treat it as the higher one; under-scoping a replan reintroduces the silent-drift failure this guards against.

## Guardrails

- Every task must trace directly to the user's request. Tasks adding unrequested flexibility, configurability, or future-proofing are scope creep in plan form; cut them, or surface them as explicit options for the user to accept.
- Do not pad the plan with generic advice. Every statement should be specific to this change.
- Do not include implementation code in the plan. Describe what will be built, not how to type it.
- If a section would be empty, omit it entirely rather than writing "N/A" or "None".
- If you lack information to fill a section, say so explicitly and ask the user.
- Plans for changes touching production data or infrastructure must include a rollback section.

## Gotchas

- **Do not ask the user what the codebase can answer.** Field names, existing patterns, current behavior, and call sites are all discoverable. Asking wastes a round-trip and erodes trust in the plan's grounding.
- **Presenting one approach hides the decision.** When a reasonable engineer could choose differently, the user gets alternatives and trade-offs, not a fait accompli.
- **Horizontal slicing defers all integration risk to the end.** All-schemas-then-all-endpoints-then-all-UI plans look organized and fail late. Slice vertically.
- **Do not pad with generic advice.** "Ensure proper error handling" is padding; "wrap the S3 call in a retry loop and surface 5xx as 503 to the caller" is a plan.
- **If a section would be empty, omit it.** An absent section means it does not apply; "N/A" is noise.
- **If you lack information, say so and ask.** Do not invent field names, assume file paths, or speculate about interfaces.
- **A plan that lives only in conversation dies at compaction.** For multi-session work, save it to a file.
