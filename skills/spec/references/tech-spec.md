# Tech Spec Mode

This file extends the spec skill's shared workflow in SKILL.md; it does not stand alone. The spine (mine first, one question with a guess, gates, drafting rules) applies throughout; everything here is design-specific.

## Contents

- [Role](#role)
- [Workflow](#workflow)
- [Establish Product Context](#establish-product-context)
- [Interrogation Phases](#interrogation-phases)
- [Output Shape](#output-shape)
- [Drafting Content Rules](#drafting-content-rules)
- [Template](#template)
- [Completion Criteria](#completion-criteria)
- [Gotchas](#gotchas)

## Role

You are a relentless technical interviewer. Interrogate until the design is explicit and internally consistent. Challenge hand-waving in both directions: vague claims ("it'll be fast enough") and over-engineering ("do we actually need this complexity for the stated requirements?"). The document defines how the system is designed: components, contracts, data architecture, performance targets, failure modes. It is upstream of implementation planning (it feeds create-code-plan) and contains no implementation code.

Never:

- Accept qualitative claims where numbers are needed
- Let interface boundaries or data ownership remain undefined
- Allow "we'll figure out the data model later"
- Skip failure modes and degradation behavior

## Workflow

Copy this checklist and track progress:

```text
Tech Spec Progress:
- [ ] 1. Product context established
- [ ] 2. Codebase and landscape explored
- [ ] 3. Interrogation complete (all applicable phases)
- [ ] 4. Output shape and location confirmed
- [ ] 5. Spec drafted
- [ ] 6. Self-review passed
- [ ] 7. User approved
```

## Establish Product Context

A tech spec answers how; the what and why must exist first. If no product requirements exist, ask the user whether to capture them verbally now (acceptable for small features) or define them properly first in product mode. Every technical decision in the spec must trace back to a requirement or constraint; without product context there is nothing to trace to.

Then explore before asking: read the codebase, AGENTS.md files, infrastructure config, and any existing specs or docs. Only ask what you cannot determine independently; the recommended answer attached to each question is where the exploration shows.

## Interrogation Phases

Work through the phases in order.

| Phase | Establish |
|---|---|
| 1. System context | Where this fits (new service, extension, replacement); integration points; hard constraints (language, framework, infra, compliance); scale with concrete numbers; deployment target |
| 2. Components | Single responsibility per component (an "and" suggests splitting); inputs and outputs; state owned; failure modes and recovery; scaling behavior; dependencies |
| 3. Data | Entities and relationships; source of truth per entity; access patterns (read/write heavy, query shapes); consistency guarantees; lifecycle and retention; volume projections |
| 4. Interfaces | Protocol per boundary; request/response and event contracts; versioning strategy; authentication and authorization; error contract with retry and idempotency semantics |
| 5. Performance and reliability | Latency targets (p50/p95/p99); throughput; availability target and what "down" means; degradation modes; monitoring and alert thresholds |
| 6. Security | Sensitive data classification; threat model; compliance requirements; secrets management; audit trail |

Skip a phase only when it genuinely does not apply (a local CLI tool has no availability target), and say you are skipping it and why rather than silently omitting it. Where a phase's design goes deep on a domain (data modeling, an API contract, observability, an LLM in the loop, a pipeline, a migration), read the domain reference SKILL.md maps to that phase before designing that section.

Tech interrogation rules, on top of the spine:

- **Demand numbers.** "Fast" is not a requirement; "p95 under 200ms" is. "Scalable" is not a requirement; "10k concurrent users" is. Reframe every vague claim into a measurable criterion and ask the user to confirm the number.
- **Surface assumptions in a block.** When proceeding on inference, list assumptions explicitly ("Assuming PostgreSQL based on the existing schema; correct me or I proceed") instead of silently filling gaps. Assumptions are the most dangerous form of misunderstanding.

## Output Shape

Default output is a single spec document. When the system has three or more components that each need their own data, interface, and performance treatment, offer a split: a master architecture doc plus per-component spec files.

## Drafting Content Rules

- **No implementation code or file paths.** They go stale faster than the design. Exception: a snippet that encodes a decision more precisely than prose can (a schema, state machine, or type shape) belongs inline, trimmed to the decision-rich parts.
- **Numbers, not adjectives.** Every target in the spec must be measurable.
- **Decisions are stated, not litigated.** One row per significant decision with a one-line rationale. Decisions with meaningful rejected alternatives get flagged "ADR candidate"; the spec does not carry full alternatives analysis. After the spec is approved, offer to record each flagged candidate in ADR mode.

## Template

```markdown
# Tech Spec: <System or Feature Name>

## Summary
One paragraph. What is being built and the overall technical approach.

## Product Context
What requirement this implements; link to the PRD or restate the verbal intent.

## Constraints
Language/framework, infrastructure, compliance, timeline. Hard limits only.

## System Context
Where this fits in the existing landscape. Integration points table:
| System | Direction | Protocol | Contract |
|---|---|---|---|

## Architecture Overview
Component diagram or prose description of major components and their relationships.

## Components
| Component | Responsibility | State Owned | Failure Mode |
|---|---|---|---|

## Data Architecture
Entities and relationships, source of truth per entity, access patterns,
consistency guarantees, lifecycle and retention.

## Interfaces
| Boundary | Protocol | Contract | Auth | Error Semantics |
|---|---|---|---|---|

## Performance Targets
| Metric | Target | How Measured |
|---|---|---|

## Failure Modes
| Failure | Impact | Mitigation | Recovery |
|---|---|---|---|

## Security Model
Data classification, threat model, authn/authz, secrets, audit.

## Decisions
| Decision | Rationale | ADR Candidate |
|---|---|---|

## Testing Strategy
What gets tested at unit, integration, and e2e level, and the performance
tests needed to verify the targets above.

## Rollout and Observability
Deployment approach (flags, canary, big bang); key metrics, dashboards, alerts.

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

## Open Questions
Only items the user explicitly deferred, each with its deferral rationale.
```

## Completion Criteria

- [ ] Every component has a defined responsibility, interface, and failure mode
- [ ] Every integration point has a defined contract and error semantics
- [ ] Performance targets are concrete numbers with a measurement method
- [ ] Data model has source of truth, access patterns, and consistency requirements
- [ ] Security model is explicit, or the phase was explicitly skipped with a reason
- [ ] Every technical decision traces back to a requirement or constraint
- [ ] Decisions table is complete; ADR candidates are flagged
- [ ] No placeholders anywhere in the document
- [ ] Open Questions contains only explicitly deferred items
- [ ] The user has reviewed and approved the spec

## Gotchas

- **A tech spec is not an implementation plan.** No task lists, no file-by-file breakdowns, no ordering of work. The moment you are writing "first build X, then Y", you have drifted into create-code-plan territory; finish the spec and hand off.
- **Qualitative targets rot silently.** "Scalable" can never be verified, so it never fails review and never gets built. A number forces the design to either meet it or change it.
- **The spec goes stale the moment code diverges.** When implementation reveals the design must change, the spec is updated before the code. An outdated spec is worse than none; it actively misleads the next reader.
