---
name: spec
description: >-
  This skill should be used for system and software design: writing a product spec (PRD), a tech
  spec (system design, design doc), or an ADR (architecture decision record), and for domain
  design consults: API contracts, database schemas, observability (SLOs, alerts, dashboards),
  LLM agent architecture, CLI command surfaces, MCP servers, CI/CD pipelines, and migration or
  deprecation plans. It applies when the user says "PRD", "tech spec", "spec this out", "ADR",
  "record this decision", "why did we choose X", "design the API", "add an endpoint", "design
  the schema", "model this data", "define SLOs", "design the alerts", "build an agent", "add an
  LLM feature", "build a CLI", "build an MCP server", "set up CI", "plan the migration", or
  "deprecate this". It should not be used for implementation planning (use create-code-plan),
  ticket slicing (use decompose), persuasive RFCs (use write-proposal), or UI and visual design
  (use design).
---

## Purpose

One surface for system design. Three document modes interrogate the user until the product intent (PRD), the design (tech spec), or the decision (ADR) is explicit, then produce the document, never drafting before the gate passes. Eight design domains carry the standards for the surfaces a system is made of, consulted standalone or from inside a tech spec. This file carries the routing and everything the document modes share; each reference file carries its mode's or domain's substance.

## Route to the Document Type

Identify the document type, then read exactly one reference file before asking the first question (in lookup mode, before answering).

| Mode | Signals | Read |
|---|---|---|
| Product spec (PRD) | What and why: users, personas, journeys, features, success metrics, MVP scope | references/product-spec.md |
| Tech spec | How: architecture, components, data, interfaces, performance targets, failure modes; a design RFC that specifies | references/tech-spec.md |
| ADR | One settled, significant decision: record why, the alternatives, when to revisit | references/adr.md |
| ADR lookup | "Why did we choose X" about a past decision | references/adr.md (its answering mode; no interview) |

Routing rules:

- An ambiguous "spec this out" or "write a spec" gets one routed question with a guess attached: is this defining what and why (product) or how it is built (tech)?
- An end-to-end request ("from idea to design") sequences product then tech. Confirm the sequence with the user, then read each reference at its turn.
- Handoffs between modes are internal. A PRD approved with design work requested: continue into tech mode. A tech spec approved with flagged ADR candidates: offer to record each in ADR mode. A tech spec requested with no product context: offer to capture requirements verbally (acceptable for small features) or run product mode first.
- Guard against mode drift. A PRD growing endpoint shapes or schemas has drifted: capture the requirement those details serve and defer the design to tech mode. A tech spec litigating one decision's alternatives at length: flag it as an ADR candidate and move on.

## Route to the Design Domain

Domain design work outside a full spec document is a consult: read the domain reference and apply it directly, delivering the domain's artifact (a contract document, DDL or key design, alert rules, a server or pipeline design, a staged migration plan). A consult skips the document workflow and its gates, follows the reference's own workflow, and still surfaces decisions as options rather than deciding unilaterally. During a tech spec, the same references deepen the matching interrogation phase: read the domain reference before designing that section of the spec.

| Domain | Read | Consult triggers / tech-spec phase |
|---|---|---|
| API contract (REST, GraphQL, typed interfaces) | references/api.md | "design the API", "add an endpoint"; phase 4 interfaces |
| Data schema (SQL, DynamoDB) | references/schema.md | "model this data", "add a table"; phase 3 data |
| Observability (signals, SLOs, alerts, dashboards) | references/observability.md | "define SLOs", "design the alerts", "alert fatigue"; phase 5 and the rollout section |
| LLM and agent systems | references/llm-agents.md | "build an agent", "add an LLM feature"; any phase with an LLM in the loop |
| CLI tools | references/cli.md | "build a CLI", "turn this script into a real tool" |
| MCP servers | references/mcp.md plus references/mcp-protocol.md | "build an MCP server", "tool or resource?"; read both, the digest carries the exact protocol fields |
| CI/CD pipelines | references/cicd.md | "set up CI", "gate merges on tests", "CI is too slow"; the rollout section |
| Migrations and deprecation | references/migration.md, which routes among references/data-migrations.md, references/dependency-upgrades.md, references/infrastructure-migrations.md, and references/api-contract-migrations.md | "plan the migration", "add a column without downtime", "deprecate this" |

A consult that grows into whole-system design (several components, cross-cutting constraints, competing architectures) upgrades to tech-spec mode: say so and switch. A significant decision settled during a consult gets the ADR offer.

## Shared Interrogation Spine

Every document mode runs this interview discipline (consults follow their domain reference's workflow instead); the mode's reference adds its phases and rules on top.

- **Mine before asking.** Read what already exists first: the conversation so far, the codebase, AGENTS.md files, READMEs, existing specs and ADRs. Every question answerable by reading is a wasted round-trip and signals the work is not grounded. When the conversation already contains the discussion, synthesize from it and interrogate only the gaps.
- **One question at a time, guess attached.** Ask one focused question, wait, process, then ask the next thing that matters most. Never dump a question list.

  ```text
  Q: <one focused question>
  GUESS: <your hypothesized answer and the reasoning behind it>
  ```

  The guess is the point: users react to a wrong guess faster than they generate answers from scratch, and it commits you to assumptions you can be visibly wrong about.
- **Skip questions the context already answers.** The mode's phases are coverage, not a script.
- **Surface decisions with options; the user decides.** "Option A gives X but costs Y; option B gives Z but costs W. Which matters more?" Never make the call unilaterally, and never treat "whatever you think is best" as an answer; it is delegation, and it means re-asking as a choice between two concrete options.
- **Track open questions.** Keep a running list; close each before drafting. Items the user explicitly defers go to the document's Open Questions section with the deferral rationale.

## Gates

- **Restate, then draft only on an explicit yes.** When you can predict the user's answers to the next three questions you would ask, stop interviewing and restate the intent in the user's own words: product mode carries a restate shape; in tech and ADR modes restate the design summary or the decision and its survived counterargument in prose. "Sounds good", "sure, let's go", and silence are not yes; follow up with "anything you'd refine?". Do not draft until the yes lands.
- **Present and get explicit approval** before the document is treated as final.

## Drafting Rules

- Confirm the output location before writing; suggest `docs/specs/` when the project has no convention. ADR mode has its own log discovery in its reference.
- Use the mode's template. Omit sections that genuinely do not apply; never write "N/A".
- No placeholders. "TBD", "figure out later", and "appropriate error handling" are failures; a placeholder means the interrogation missed something, so go back and ask.
- Self-review against the mode's Completion Criteria before presenting, and verify internal consistency: names used in one section match every other section.
- Commit the document to version control.
- PRDs and tech specs are living documents: when a decision changes, update the document first, then the work. ADRs are the opposite: an accepted record is immutable and changes only by being superseded.

## Gotchas

- **Mining beats interviewing when the context is rich.** If the user has been discussing the topic for an hour, opening with phase-1 question 1 is interrogation theater. Synthesize, present your understanding at high confidence, and interrogate only what is genuinely unresolved.
- **The polite yes is the dangerous yes.** A user agreeing with your guess to be agreeable produces a confidently wrong document. Be visibly willing to be wrong, and occasionally guess in a direction you expect pushback on; a user who never corrects you is not converged, they are disengaged.
- **One question at a time is a pacing rule, not a padding rule.** Asking every phase question to a user with a small, well-understood need is process worship. The phases are coverage checklists, not scripts.
- **Consults deliver artifacts, not documents.** "Add an endpoint" wants a contract, not a PRD; do not drag a domain consult through the document gates. The reverse also holds: when a consult starts sprouting components and cross-cutting constraints, it is a tech spec now, so upgrade.
