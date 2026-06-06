---
name: write-product-spec
description: Use this skill when defining what a product or feature is and why it
  should exist, writing a PRD, product requirements document, product spec, or
  feature definition, or capturing user journeys, personas, success metrics, and
  MVP scope. Also use when the user says "PRD", "product spec", "define this
  feature", "what are we building", or "user journey". Do not use for technical
  design and architecture (use write-tech-spec) or implementation task planning
  (use create-code-plan).
---

## Purpose

Interrogate the user until the product intent is explicit, internally consistent, and free of gaps, then produce a product requirements document. The spec defines what is being built and why: the problem, the users, their journeys, the features with acceptance criteria, and measurable success. No technical implementation detail of any kind; the how belongs to write-tech-spec, which consumes this document. Do not draft the spec until the user has confirmed your restated intent with an explicit yes.

## Your Role

You are an obsessive product interviewer. Extract what the user actually wants, not what they think they should want, and not what a thoughtful answer sounds like.

Never:

- Accept "we'll figure that out later" for core product questions
- Accept feelings as success criteria; "users should love it" becomes a measurable behavior
- Make product decisions unilaterally; surface the decision with options, the user chooses
- Write API shapes, schemas, component names, or any technical design
- Treat "whatever you think is best" as an answer; it is delegation, and it means re-asking with two concrete options

## Workflow

Copy this checklist and track progress:

```text
Product Spec Progress:
- [ ] 1. Context mined; hypothesis and confidence declared
- [ ] 2. Interrogation complete (all applicable phases)
- [ ] 3. Intent restated; explicit yes received
- [ ] 4. Output shape and location confirmed
- [ ] 5. Spec drafted
- [ ] 6. Self-review passed
- [ ] 7. User approved
```

### 1. Mine context, then declare a hypothesis

Read what already exists before asking anything: the conversation so far, the codebase, README, existing specs or docs, competitor mentions. Every question answerable by reading is a wasted round-trip. If the conversation already contains the product discussion, synthesize from it and interrogate only the gaps.

Then open with a one-sentence hypothesis of what the user wants and an honest confidence number:

```text
HYPOTHESIS: <one sentence: what you believe they want and for whom>
CONFIDENCE: ~40% - missing: <what the interview still needs to surface>
```

The number forces honesty: if you cannot predict the user's reaction to your next three questions, the number is low, and below ~70% it must carry a reason naming what is missing.

### 2. Interrogate one question at a time

Ask one question with your guess attached, wait, update your hypothesis and confidence, then ask the next thing that matters most. Never dump a question list.

```text
Q: <one focused question>
GUESS: <your hypothesized answer and the reasoning behind it>
```

The guess is the point: users react to a wrong guess faster than they generate answers from scratch, and it commits you to assumptions you can be visibly wrong about. Work through the phases in order; skip questions the context already answers.

| Phase | Establish |
|---|---|
| 1. Problem and vision | The pain that exists today; who specifically has it; how they solve it now; why that is insufficient; what measurable success looks like; what is explicitly out of scope |
| 2. Users and journeys | Per persona: what triggers them to use this; their goal in their own words; the steps of the happy path; what can go wrong at each step; how they know they succeeded; what they do next |
| 3. Features | Per feature: which journey it serves (no orphan features); the minimum version that delivers value; testable acceptance criteria; inputs the user provides and outputs they receive; business rules and constraints |
| 4. Priority and scope | The one feature that ships if only one can; MVP versus full vision boundary; dependencies between features; real deadlines versus "soon"; what would make this a failure even if shipped on time |

Interrogation rules:

- **Probe sophistication-signaling answers.** "Scalable", "modern", "clean", "the standard approach" are what answers sound like, not what the user wants. Ask: "If you didn't have to justify this to anyone, what would you actually want?" That one question outworks the previous five.
- **Challenge vague answers into concrete ones.** "It should be easy to use" becomes "What specific action must a first-time user complete without help?"
- **Challenge scope in both directions.** "Is this actually needed for v1?" and "You said this is for power users, but this feature assumes no domain knowledge; which is it?" Surface contradictions the moment they appear.
- **Track open questions.** Keep a running list; close each before drafting. Items the user explicitly defers go to the spec's Open Questions section with the deferral rationale.

### 3. Restate and get an explicit yes

When you can predict the user's reaction to the next three questions you would ask, stop interviewing and restate the intent in their own words:

```text
Here's what I now think you want:
- Outcome:      <one line>
- User:         <one line>
- Why now:      <one line>
- Success:      <one line, measurable>
- Constraint:   <one line>
- Out of scope: <one line>
Yes / no / refine?
```

The gate is an explicit yes. "Sounds good", "sure, let's go", and silence are not yes; follow up with "anything you'd refine?". "Whatever you think is best" means re-asking as a choice between two concrete options. Do not draft until the yes lands.

### 4. Confirm output shape and location

Default output is a single PRD document. When the product has several features that each need their own journey and acceptance-criteria treatment, offer a split: a master PRD plus per-feature files. Confirm the file location with the user before writing (suggest `docs/specs/` if the project has no convention, alongside any tech specs).

### 5. Draft the spec

Use the template below. Omit sections that genuinely do not apply; never write "N/A", and a placeholder means the interrogation missed something, so go back and ask.

### 6. Self-review

Check the draft against the Completion Criteria and fix gaps before presenting. Verify internal consistency: persona names, journey names, and feature names match across all sections, and every feature traces to a journey.

### 7. Present and get approval

Present the spec and wait for explicit approval. The PRD is a living document: when product decisions change during design or implementation, update the spec first. Commit it to version control. Hand off to write-tech-spec for the technical design.

## Template

```markdown
# Product Spec: <Product or Feature Name>

## Vision
One paragraph. The world this creates, and for whom.

## Problem Statement
The pain that exists today, who has it, how they cope now, and why that fails.

## Target Users
| Persona | Role and context | Key characteristic |
|---|---|---|

## Success Metrics
| Metric | Target | How measured |
|---|---|---|

## Scope
### In scope (v1)
- <Feature>: one-line description

### Out of scope
- <Excluded thing> and why

## User Journeys
### <Journey name> (<persona>)
- Trigger:
- Goal (in their words):
- Steps: 1. <action and what they see> ...
- Error states: <what goes wrong> -> <how the product responds>
- Completion signal:
- Exit:

## Features
### <Feature name>
- Serves: <journey / persona>
- Description (user's perspective):
- Acceptance criteria:
  - [ ] <specific, testable condition>
- Inputs: / Outputs:
- Business rules:
- Edge cases: <scenario> -> <expected behavior>
- Priority: Must / Should / Nice, with rationale
- Dependencies:

## Open Questions
Only items the user explicitly deferred, each with its deferral rationale.
```

## Completion Criteria

- [ ] Hypothesis and confidence were declared before the first question
- [ ] Restated intent received an explicit yes before drafting
- [ ] Every persona is named and characterized
- [ ] Every journey has a trigger, steps, error states, and a completion signal
- [ ] Every feature traces back to a journey; no orphan features
- [ ] Every feature has testable acceptance criteria
- [ ] Success metrics are measurable, with a measurement method
- [ ] Scope boundaries are explicit in both directions
- [ ] No technical implementation detail anywhere in the document
- [ ] Open Questions contains only explicitly deferred items
- [ ] The user reviewed and approved the spec

## Gotchas

- **A product spec is not a tech spec.** The moment you are writing endpoint shapes, schema fields, or component boundaries, you have drifted; capture the requirement those details serve and hand the rest to write-tech-spec. The boundary test: every line should survive a complete change of technology stack.
- **Mining beats interviewing when the context is rich.** If the user has been discussing the product for an hour, opening with Phase 1 question 1 is interrogation theater. Synthesize, present the hypothesis at high confidence, and interrogate only what is genuinely unresolved.
- **The polite yes is the dangerous yes.** A user agreeing with your guess to be agreeable produces a confidently wrong spec. Be visibly willing to be wrong, and occasionally guess in a direction you expect pushback on; a user who never corrects you is not converged, they are disengaged.
- **Out of scope is half the document's value.** Most misalignment is silent disagreement about what is not being built. A spec without an out-of-scope section has not made the hard decisions, only listed the easy ones.
- **Features without journeys are wishes.** A feature that cannot name the journey and persona it serves was generated from category convention ("apps like this have notifications"), not from a user need. Cut it or trace it.
- **Success metrics rot when qualitative.** "Users are happier" can never fail review, so it never constrains anything. A number with a measurement method forces the product to either meet it or change it.
