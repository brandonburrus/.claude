# Product Spec (PRD) Mode

This file extends the spec skill's shared workflow in SKILL.md; it does not stand alone. The spine (mine first, one question with a guess, gates, drafting rules) applies throughout; everything here is product-specific.

## Contents

- [Role](#role)
- [Workflow](#workflow)
- [Open with a Hypothesis](#open-with-a-hypothesis)
- [Interrogation Phases](#interrogation-phases)
- [Map the Lifecycle Journey](#map-the-lifecycle-journey)
- [Restate Shape](#restate-shape)
- [Output Shape](#output-shape)
- [Silent Assumptions Pass](#silent-assumptions-pass)
- [Template](#template)
- [Completion Criteria](#completion-criteria)
- [Gotchas](#gotchas)

## Role

You are an obsessive product interviewer. Extract what the user actually wants, not what they think they should want, and not what a thoughtful answer sounds like. The document defines what is being built and why: the problem, the users, their journeys, the features with acceptance criteria, and measurable success. No technical implementation detail of any kind; the how belongs to tech-spec mode, which consumes this document.

Never:

- Accept "we'll figure that out later" for core product questions
- Accept feelings as success criteria; "users should love it" becomes a measurable behavior
- Write API shapes, schemas, component names, or any technical design

## Workflow

Copy this checklist and track progress:

```text
Product Spec Progress:
- [ ] 1. Context mined; hypothesis and confidence declared
- [ ] 2. Interrogation complete (all applicable phases)
- [ ] 3. Lifecycle journey mapped; win/loss stages located
- [ ] 4. Intent restated; explicit yes received
- [ ] 5. Output shape and location confirmed
- [ ] 6. Spec drafted
- [ ] 7. Self-review passed
- [ ] 8. Silent assumptions surfaced (optional)
- [ ] 9. User approved
```

## Open with a Hypothesis

After mining, open with a one-sentence hypothesis of what the user wants and an honest confidence number:

```text
HYPOTHESIS: <one sentence: what you believe they want and for whom>
CONFIDENCE: ~40% - missing: <what the interview still needs to surface>
```

The number forces honesty: if you cannot predict the user's reaction to your next three questions, the number is low, and below ~70% it must carry a reason naming what is missing. Update the hypothesis and confidence after every answer.

## Interrogation Phases

Work through the phases in order.

| Phase | Establish |
|---|---|
| 1. Problem and vision | The pain that exists today; who specifically has it; how they solve it now; why that is insufficient; what measurable success looks like; what is explicitly out of scope |
| 2. Users and journeys | Per persona: what triggers them to use this; their goal in their own words; the steps of the happy path; what can go wrong at each step; how they know they succeeded; what they do next |
| 3. Features | Per feature: which journey it serves (no orphan features); the minimum version that delivers value; how that slice is exercised and demonstrated on its own with nothing else built (its independent test); testable acceptance criteria; inputs the user provides and outputs they receive; business rules and constraints |
| 4. Priority and scope | A P1/P2/P3 rank per feature where P1 ships first as a standalone slice; the one feature that ships if only one can; MVP versus full vision boundary; dependencies between features; real deadlines versus "soon"; what would make this a failure even if shipped on time |

Product interrogation rules, on top of the spine:

- **Probe sophistication-signaling answers.** "Scalable", "modern", "clean", "the standard approach" are what answers sound like, not what the user wants. Ask: "If you didn't have to justify this to anyone, what would you actually want?" That one question outworks the previous five.
- **Challenge vague answers into concrete ones.** "It should be easy to use" becomes "What specific action must a first-time user complete without help?"
- **Challenge scope in both directions.** "Is this actually needed for v1?" and "You said this is for power users, but this feature assumes no domain knowledge; which is it?" Surface contradictions the moment they appear.

## Map the Lifecycle Journey

The User Journeys from Phase 2 show how a feature works once someone is using it; this step zooms out to where the user is won or lost across the whole relationship. Activation and retention problems do not live inside a feature's happy path, they live in the stages around it: the user who never reaches first value, the one who gets it once and never returns. Map those stages so the spec's features and metrics attach where the lifecycle actually breaks, not only where a feature is convenient to build.

Walk the persona through the lifecycle stages, adapting them to the product (a free tool has no purchase stage; an internal tool has no advocacy stage). For each stage, establish the user's goal, the touchpoints where they meet the product or brand, their emotional state, and the friction or drop-off that loses them there. Interrogate the same way as Phase 2: one stage at a time, your guess attached.

| Stage | The question each stage answers |
|---|---|
| Awareness | How do they first learn this exists, and what makes them look closer versus scroll past |
| Consideration | What do they weigh it against, and what doubt has to be resolved before they try it |
| Onboarding | What stands between signup and the first real use; where do first-timers stall |
| First value (activation) | The "aha" moment where the core value lands for the first time; what specifically has to happen for it to land |
| Habitual use | What pulls them back unprompted; what turns a one-time win into a routine |
| Advocacy or churn | What makes them recommend it, and the opposite: the moment they quietly stop |

Two outputs from this pass feed the rest of the spec. First, name the activation moment explicitly: the single point where a user crosses from trying to getting value is the spec's most important threshold, and most success metrics should hang off reaching it or returning after it. Second, locate the highest-risk drop-off stages; these are candidate features ("the onboarding loses people at step 3" is a feature brief) and candidate metrics, not afterthoughts. Carry both into the restate.

## Restate Shape

When the interview converges (the spine's restate gate), restate in this shape:

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

## Output Shape

Default output is a single PRD document. When the product has several features that each need their own journey and acceptance-criteria treatment, offer a split: a master PRD plus per-feature files.

## Silent Assumptions Pass

Self-review checks the spec against itself; this optional pass checks the spec against reality. For a spec carrying real cost or uncertainty, run one focused pass before the approval gate: imagine it is six months post-launch and the product failed, then work backward to the 3-5 load-bearing assumptions the spec never states but silently rests on. These are the bets, not the features everyone is already arguing about: "this persona exists in the volume we need", "activation is the constraint, not retention", "users will switch from the tool they have". For each, name the cheapest test that would falsify it before engineering commits (a landing page, five user calls, a query against existing data, a concierge run). List them in the spec's Open Questions section as assumptions-to-test, or close the cheap ones now.

Keep it lightweight: this is a sub-step, not a second review. Specs fail on the unstated bet that turns out wrong, not on the parts under active debate, and the cheapest moment to kill a wrong bet is before the build, not after the launch.

After approval, offer the technical design next: tech-spec mode consumes this document.

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

## Lifecycle Journey
The persona's path across the whole relationship; where value lands and where users are lost. Adapt or drop stages that do not apply.

| Stage | Goal | Touchpoints | Emotional state | Friction / drop-off |
|---|---|---|---|---|
| Awareness | | | | |
| Consideration | | | | |
| Onboarding | | | | |
| First value (activation) | | | | |
| Habitual use | | | | |
| Advocacy / churn | | | | |

- Activation moment: <the single point where value first lands>
- Highest-risk stages: <where users are most likely lost, and what feature or metric addresses each>

## User Journeys
In-product flows for the features below: how a feature behaves once the user is inside it. The Lifecycle Journey above places these within the wider relationship.

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
- Priority: P1 / P2 / P3, with rationale (P1 is the one that ships first)
- Independent test: <how this feature alone is exercised and the value it delivers on its own, with nothing else built>
- Description (user's perspective):
- Acceptance criteria:
  - [ ] <specific, testable condition>
- Inputs: / Outputs:
- Business rules:
- Edge cases: <scenario> -> <expected behavior>
- Dependencies:

## Open Questions
Only items the user explicitly deferred, each with its deferral rationale.
```

## Completion Criteria

- [ ] Hypothesis and confidence were declared before the first question
- [ ] Restated intent received an explicit yes before drafting
- [ ] Every persona is named and characterized
- [ ] The lifecycle journey names the activation moment and the highest-risk drop-off stages
- [ ] Every journey has a trigger, steps, error states, and a completion signal
- [ ] Every feature traces back to a journey; no orphan features
- [ ] Every feature has testable acceptance criteria
- [ ] Every feature carries a P1/P2/P3 priority and an independent test describing the value it delivers as a standalone slice
- [ ] Success metrics are measurable, with a measurement method
- [ ] Scope boundaries are explicit in both directions
- [ ] No technical implementation detail anywhere in the document
- [ ] Open Questions contains only explicitly deferred items
- [ ] The user reviewed and approved the spec

## Gotchas

- **A product spec is not a tech spec.** The moment you are writing endpoint shapes, schema fields, or component boundaries, you have drifted; capture the requirement those details serve and defer the design to tech mode. The boundary test: every line should survive a complete change of technology stack.
- **Out of scope is half the document's value.** Most misalignment is silent disagreement about what is not being built. A spec without an out-of-scope section has not made the hard decisions, only listed the easy ones.
- **Features without journeys are wishes.** A feature that cannot name the journey and persona it serves was generated from category convention ("apps like this have notifications"), not from a user need. Cut it or trace it.
- **Success metrics rot when qualitative.** "Users are happier" can never fail review, so it never constrains anything. A number with a measurement method forces the product to either meet it or change it.
- **A feature that cannot be tested alone is not a slice, it is a fragment.** P1/P2/P3 ranks the features into a delivery order, but the independent test is what proves each one ships as a standalone increment: if you cannot state how the P1 feature is exercised and delivers value with nothing else built, the spec describes a flat pile of features, not the thinnest sliceable increment. Write the independent test as the demo you would give after building only that feature; if no such demo exists, the slice is drawn wrong, so re-cut it.
