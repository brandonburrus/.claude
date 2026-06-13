---
name: clarify-ambiguity
description: Use this skill when a request, idea, or direction is ambiguous, underspecified,
  or vague and needs clarification before any work starts, especially when the ask is
  missing who it is for, why now, what success looks like, or the binding constraint.
  Also use when the user says "grill me", "interview me", "clarify this", "stress-test
  my thinking", "refine this idea", "ideate", "poke holes in this", or "am I missing
  something". Do not use for writing the resulting PRD (use write-product-spec), system
  design (use write-tech-spec), rewriting text to read more clearly, or single-fact
  ambiguities that one direct question resolves.
---

## Purpose

Converge on what the user actually wants, not what they think they should want, before any plan, spec, or code exists. That is the cheapest moment to find the gap; after work starts, switching costs are real and the user rationalizes the wrong thing into "good enough". The deliverable is a confirmed statement of intent (or a sharpened idea one-pager), explicitly confirmed by the user. Do not produce any downstream artifact, plan, or code until that confirmation lands. This skill needs a live user; in non-interactive contexts (CI, loops, background runs) flag the ambiguity as a blocker instead of guessing.

## Route by the Shape of the Ambiguity

| Shape | Signal | Mode |
|---|---|---|
| Underspecified request | An ask missing at least one of: who, why now, success, binding constraint ("build me a dashboard", "make it faster") | Interview |
| Vague idea | Something they might build or do, shape still unknown ("I've been thinking about...", "refine this idea", "ideate") | Refine |
| Existing plan or direction | A decision already drafted, wants holes poked ("grill me", "stress-test this plan", "am I missing something") | Grill |

When the shape itself is unclear, ask which they want; the modes diverge enough that guessing wrong wastes the session.

## Shared Mechanics (all modes)

- **Explore before asking.** Read the conversation, codebase, and docs first; every question answerable by reading is a wasted round-trip and signals the clarification is not grounded.
- **Open with a hypothesis and an honest confidence number.** One sentence of your best read plus 0-100%. Below ~70%, name what is missing on the same line; the user cannot help close a gap they cannot see.

```text
HYPOTHESIS: <one sentence: what you believe they actually want>
CONFIDENCE: ~35% - missing: <what must still surface>
```

- **One question at a time, your guess attached.** Users react to a wrong guess faster than they generate answers from scratch, and the guess commits you to assumptions you can be visibly wrong about. Never batch; the third question usually depends on the first answer, and batches get skim-read. When the AskUserQuestion tool is available, use it with your guess as the recommended option.
- **Probe sophistication-signaling answers.** "Scalable", "modern", "clean", "the standard approach" are what answers sound like, not what the user wants. Ask: "If you didn't have to justify this to anyone, what would you actually want?" That one probe outworks the previous five questions.
- **Surface contradictions immediately**, not at the end: "You said X earlier, but this implies Y; which is it?"
- **The floor rule.** Several rounds without confidence visibly rising means you are asking the wrong questions, and that is information about the ask. Stop and say: "I've asked N questions and still can't predict your answers; something foundational is missing. Want to step back?"
- **Gate on an explicit yes.** "Sounds good", "sure, let's go", and silence are not yes; follow with "anything you'd refine?". "Whatever you think is best" is delegation, not decision; re-ask as a choice between two concrete options.

## Elicitation Methods (pick one to match the ambiguity)

Different ambiguities yield to different techniques; a single monolithic interview blunts on the ones that need a sharper instrument. Read the situation, pick the method that fits, then return to the one-question-at-a-time mechanics above. These compose: a stuck Socratic line often hands off to inversion or first-principles.

| Method | Pick this when |
|---|---|
| Socratic questioning | The user holds the answer but has not examined it; questions surface it faster than you guessing |
| First-principles decomposition | The ask is tangled in inherited assumptions ("we always do X"); strip to fundamentals and rebuild |
| Inversion | Success is fuzzy but failure is vivid; ask what would guarantee the wrong outcome, then avoid it |
| Red-team / devil's advocate | The user is over-committed to one answer; argue the opposing case to test whether it holds |
| Pre-mortem | A plan feels settled and risks are unspoken; imagine it has already failed and trace the causes |
| Constraint removal | A stated constraint may be artificial; ask "what if X weren't a limit?" to find the real boundary |
| Analogy / expert-lens | The user lacks vocabulary for the domain; map to a domain they know, or ask what an expert would find obvious |
| Stakeholder round-table | Competing interests are unnamed; voice each affected party in turn to reveal whose needs are being overlooked |

## Mode: Interview

For underspecified requests. Stop condition: you can predict the user's reaction to the next three questions you would ask. That is a checkable test, not a vibe.

When the stop condition holds, restate the intent in the user's own words, line by line:

```text
Here's what I now think you want:
- Outcome:      <one line>
- User:         <one line, who benefits>
- Why now:      <one line, what changed>
- Success:      <one line, how we know it worked>
- Constraint:   <one line, the binding limit>
- Out of scope: <one line, what we are explicitly not doing>
Yes / no / refine?
```

Out of scope is non-negotiable; half of all misalignment is silent disagreement about what is not being done. The confirmed restate is the deliverable, and it feeds whatever comes next: write-product-spec for a product definition, write-tech-spec for system design, create-code-plan for implementation, or just doing the now-clear task.

## Mode: Refine

For vague ideas: diverge first, then converge. Quality over quantity throughout; 5-8 considered variations beat 20 shallow ones.

1. **Restate the idea as a "How might we..." problem statement.** This forces clarity on what is actually being solved before any solutions appear.
2. **Ask 3-5 sharpening questions** (one at a time, guess attached): who specifically, what success looks like, the real constraints, what has been tried, why now. Do not proceed without who-it-is-for and what-success-looks-like.
3. **Generate 5-8 variations** through deliberate lenses, each with a reason it exists:

| Lens | Question |
|---|---|
| Inversion | What if we did the opposite? |
| Constraint removal | What if time, budget, or tech were not factors? |
| Audience shift | What if this were for a different user? |
| Simplification | What is the version that is 10x simpler? |
| 10x | What does this look like at massive scale? |
| Combination | What if we merged this with an adjacent idea? |
| Expert lens | What would a domain expert find obvious here? |

4. **Converge.** Cluster what resonated into 2-3 genuinely distinct directions and stress-test each: user value (painkiller or vitamin?), feasibility (what is the hardest part?), differentiation (would anyone switch?). Be honest, not supportive; a clarification partner that yes-machines weak ideas is worthless.
5. **Surface hidden assumptions** for the leading direction: what you are betting is true but have not validated, what could kill it, what you are choosing to ignore and why that is acceptable. Skipping this step is where most ideation fails.
6. **Deliver a one-pager** on explicit yes: problem statement, recommended direction, assumptions to validate (each with how to test it), MVP scope, a Not-Doing list with reasons (the most valuable section; focus is saying no to good ideas), and open questions. Offer to save it; only save on confirmation.

## Mode: Grill

For an existing plan or direction the user wants stress-tested. The user has decided; your job is to find what the decision missed, not to re-litigate it from scratch.

- Map the plan's decision tree first, then walk it branch by branch in dependency order; resolving "how is data stored" before "how is it synced" prevents revisiting answers.
- For every question, attach your recommended answer; a grill without recommendations is an interrogation the user does all the work for.
- Hunt specifically for: contradictions between stated goals and chosen means, unstated assumptions load-bearing to the plan, the cheapest thing that would prove the plan wrong, and the branch the user has not thought about (their fluency drops there; follow it).
- Resolve each branch explicitly before moving on; "we'll see" leaves the branch open and it will be relitigated mid-build.
- Deliverable: the resolved decision list plus any branches the user explicitly deferred, each with its deferral reason. Significant settled decisions worth a permanent record hand off to write-adr.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The ask is clear enough" | If you cannot write the desired outcome in one sentence right now, it is not clear. State the hypothesis first, then decide. |
| "Questions waste the user's time" | Four targeted questions cost minutes; building the wrong thing costs the user days, and they bear that cost. |
| "I'll figure it out as I build" | Discovery during implementation is rework at 10x the price of asking now. |
| "They said 'whatever you think', so I decide" | Delegation means they do not know either. Re-ask as a choice between two concrete options. |
| "I'll offer several options to pick from" | Options help users choosing between known trade-offs. This user does not know what they want yet; asking narrows, listing widens. |
| "Attaching my guess leads the witness" | Leading is the point; reacting beats generating. The real risk is sycophancy, mitigated by being visibly willing to be wrong. |
| "We've talked enough, I get it" | Test it: predict their reaction to the next three questions. Cannot? Not done. |

## Red Flags

- Three or more questions in one message: batching, not interviewing
- A question without your guess or recommendation attached: surveying, not committing
- A buzzword answer ("scalable", "modern") accepted without the actually-want probe
- Any plan, spec, or code produced before the explicit yes
- Saving an artifact before the user confirmed it (the file implies a yes they did not give)
- A restate without an out-of-scope or Not-Doing line
- Confidence below ~70% stated without a reason attached

## Gotchas

- **Proportionality is part of the skill.** A single missing fact gets a single direct question, not a protocol; running the full interview on "which config file did you mean?" is process worship. The modes exist for genuinely open asks.
- **The polite user is the failure mode.** Someone agreeing with every guess to be agreeable is not converging, they are disengaging. Occasionally guess in a direction you expect pushback on; a user who never corrects you has stopped reading.
- **Domain interrogations outrank this skill.** write-product-spec and write-tech-spec carry their own interrogation protocols tuned to their documents. When the conversation is clearly headed at one of those artifacts, hand off instead of running a generic clarification first and a specific one second; the user answers everything twice otherwise.
- **Divergence is a tool, not a deliverable.** The variations in Refine mode exist to locate the real want by contrast; presenting eight ideas and asking "which one?" without clustering and stress-testing just moves the ambiguity from the idea to the menu.
