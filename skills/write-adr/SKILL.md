---
name: write-adr
description: Use this skill when recording an architecture decision record, capturing
  why a significant technical choice was made, what alternatives were considered,
  and when to revisit it. Use when the user says "ADR", "record this decision",
  "document why we chose X", or asks "why did we choose X" about a past decision,
  when a tech spec flags an ADR candidate, or when a significant technology, pattern,
  or infrastructure choice gets settled mid-conversation. Do not use for full system
  design (use write-tech-spec), implementation planning (use code-planning), or
  project conventions (use AGENTS.md).
---

## Purpose

Capture why a significant technical decision was made, with enough clarity that someone encountering it in two years, with none of today's context, can understand the rationale and judge whether it still applies. ADRs are institutional memory: they prevent future teams from re-litigating settled decisions or blindly continuing decisions whose conditions no longer hold. The deliverable is one numbered, immutable record plus an updated index. Do not write the record until the decision, its alternatives, and its revisit conditions are explicit.

## Your Role

You are a decision archaeologist and devil's advocate. Most ADRs record a decision already made in the current conversation: mine the transcript and codebase first, then interrogate only the gaps, one question at a time with your recommended answer. Before drafting, argue against the chosen option and for the rejected ones; a rationale that survives that pressure is worth recording, and one that does not means the decision needs more discussion, not documentation.

Never accept "it was obvious" as rationale (obvious to whom, given what context?), "it's better" without the criterion it is better on, or a record with zero documented alternatives.

## Workflow

Copy this checklist and track progress:

```text
ADR Progress:
- [ ] 1. Decision mined from conversation and codebase
- [ ] 2. Significance gate passed
- [ ] 3. ADR log located, number assigned
- [ ] 4. Gaps interrogated
- [ ] 5. Rationale stress-tested
- [ ] 6. Record drafted
- [ ] 7. User approved, file written, index updated
```

### 1. Mine before asking

Extract from the conversation: the decision in one sentence, what triggered it, the alternatives discussed, the stated reasons, and the trade-offs acknowledged. Read the codebase and existing ADRs for context the conversation lacks. Only interrogate what remains unknown.

### 2. Apply the significance gate

| Record an ADR | Do not record |
|---|---|
| Technology choice (framework, database, broker, cloud service, protocol) | Variable naming, formatting, lint rules |
| Structural decision affecting multiple modules, teams, or systems | Implementation details invisible outside one module |
| Meaningful trade-off where reasonable engineers would differ | Clear winner with no viable alternative |
| Accepted constraint that limits future options | Easily reversible choices with negligible switching cost |
| Superseding or revisiting a prior ADR | Project conventions (AGENTS.md owns those) |

When the gate fails, say so and offer the AGENTS.md line instead. Recording trivial decisions buries the significant ones.

### 3. Locate the log and assign a number

Look for an existing ADR directory (`docs/adr/`, `docs/decisions/`, `spec/adr/`) and follow its conventions. If none exists, propose `docs/adr/` with an index `README.md`, and get explicit confirmation before creating anything. Number sequentially with four digits (`0007-queue-over-stream-for-delivery.md`); scan existing files for the next number, lowercase kebab-case title.

### 4. Interrogate the gaps

One question at a time, recommended answer attached. Cover whatever mining did not:

- **The decision**: one clear sentence; scope (what systems and teams it affects); the trigger (why now, what changed)
- **The context**: constraints in force (timeline, team skills, compliance, existing systems); assumptions that must hold for the decision to stay valid
- **The alternatives**: minimum two, including "do nothing" when applicable; for each, what it wins, what it loses, and the specific reason it was rejected
- **The rationale**: the criteria the options were compared on; what is being given up, honestly
- **Revisit conditions**: concrete, observable triggers for reconsideration ("write volume exceeds 10k/sec", "vendor price exceeds $X/month"), never "revisit if needed"

### 5. Stress-test the rationale

Argue the strongest case for the best rejected alternative and the strongest case against the chosen one. Put the result to the user. If the rationale holds, record it, including the counterargument it survived. If it does not, the user is deciding, not documenting; pause the ADR.

### 6. Draft the record

Use the template. An ADR should be readable in two minutes: if Context exceeds ten lines, cut. Be specific ("use Prisma ORM", not "use an ORM"), use present tense ("we use X"), and state negative consequences honestly; an ADR with no downsides documented is advertising, not a record. When backfilling a past decision, mark the original decision date and note it is recorded retroactively.

### 7. Approve, write, index

Present the draft, get explicit approval, write the file, and append a row to the index `README.md` (number, linked title, status, date). If this ADR supersedes another, update the old record's status line to `Superseded by ADR-XXXX`; that status change is the only edit an accepted ADR ever receives.

## Template

```markdown
# ADR-XXXX: <Decision Title>

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-YYYY
**Date**: YYYY-MM-DD
**Deciders**: <who made this call>

## Context

What situation forces a decision. Constraints, requirements, and the trigger,
written for a reader with no prior context. Max ten lines.

## Decision

One or two sentences. "We will use X for Y because Z."

## Alternatives Considered

### <Alternative name>
- **Pros**: where it wins
- **Cons**: where it loses
- **Why rejected**: the specific reason, not "it's worse"

### <Chosen option name>
- **Pros**: where it wins
- **Cons**: honest weaknesses of the choice we made anyway

## Evaluation Criteria

Optional; include only when options were scored on multiple weighted criteria.
| Criterion | Weight | Alt A | Alt B | Chosen |
|---|---|---|---|---|

## Consequences

- **Easier**: what this decision enables
- **Harder**: what it costs or constrains
- **Follow-ups**: decisions this one forces next

## Revisit When

Concrete, observable conditions that should reopen this decision.

## Related

Links to the tech spec, product requirement, or ADRs this supersedes or depends on.
```

## Lifecycle

```text
Proposed -> Accepted -> (Deprecated | Superseded by ADR-XXXX)
```

Accepted ADRs are immutable. When a decision changes, write a new ADR that references and supersedes the old one; never edit or delete the old record, because the historical context is the point. A superseded ADR that quietly disappears takes its lessons with it.

## Answering "why did we choose X"

When the user asks about a past decision, scan the index, read the matching record, and present its Context and Decision sections. No matching record means the answer is reconstruction, not memory: say so, answer from code and git history as best you can, and offer to backfill an ADR marked retroactive.

## Gotchas

- **An ADR is a record, not a proposal.** When the document's job is to convince stakeholders to adopt the choice, that is a persuasive document; apply the writing-persuasive skill for the prose and keep this skill's structure. Once the decision lands, the ADR is written as settled fact in present tense.
- **AGENTS.md and ADRs divide the territory.** Conventions and lightweight project decisions live in AGENTS.md where agents read them every session; expensive-to-reverse architecture decisions get ADRs, and the nearest AGENTS.md links to the ADR log so agents discover it.
- **"It was obvious" means one of two things.** Either the alternatives were non-trivial (document them) or the decision is not significant enough for an ADR (fail the gate and skip). Truly obvious decisions never need records.
- **Zero documented downsides is a defect.** Every real decision trades something away. A record without honest cons will read as naive the first time the cost shows up, and the reader will distrust the rest of it.
- **Vague revisit conditions never fire.** "Revisit if it becomes a problem" triggers nothing because no one is watching for "a problem". A number or an event ("p95 over 500ms", "team exceeds 10 engineers") can actually be noticed.
- **The interrogation is for gaps only.** When the conversation already contains the decision, alternatives, and rationale, asking the user to repeat them is process worship; draft from the transcript and confirm.
