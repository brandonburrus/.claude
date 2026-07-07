---
name: spec
description: >-
  This skill should be used when writing a product spec (PRD), a tech spec (system design,
  design doc), or an ADR (architecture decision record). It applies when the user says "PRD",
  "product spec", "define this feature", "tech spec", "system design", "spec this out", "ADR",
  "record this decision", or "why did we choose X", or when a significant decision settles
  mid-conversation. It should not be used for implementation planning (use create-code-plan),
  ticket slicing (use decompose), persuasive RFCs (use write-proposal), documenting an existing
  system as-is, or project conventions (AGENTS.md).
---

## Purpose

Interrogate the user until the product intent (PRD), the design (tech spec), or the decision (ADR) is explicit and free of gaps, then produce the document. One skill, three document types, one shared discipline: mine what already exists, ask one question at a time with a guess attached, and never draft before the gate passes. This file carries everything the modes share; each mode's reference file carries its role, interrogation phases, template, and completion criteria.

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

## Shared Interrogation Spine

Every mode runs this interview discipline; the reference adds the mode's phases and rules on top.

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
