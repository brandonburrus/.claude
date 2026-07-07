---
name: interrogate
description: >-
  This skill should be used when a request, idea, topic, or direction is unclear, underspecified,
  or likely bigger than it first sounds, and must be understood from every angle before any work
  starts. It flips the script: the agent relentlessly questions the user until everything
  discovered is explicitly in scope, out of scope, or deferred, ending in a user-confirmed scope
  contract. It applies when the user says "interrogate me", "grill me", "interview me", "question
  me until you get it", "clarify this", "refine this idea", "stress-test my thinking", "poke holes
  in my idea", "define the scope", or "am I missing something". It should not be used for writing
  the resulting PRD or tech spec (use spec), or for single-fact ambiguities that one direct
  question resolves.
---

## Purpose

Flip the script: the agent asks, the user answers. Interrogate an unclear request, idea, or topic until it is understood from every angle and everything discovered is explicitly in scope, out of scope, or deferred. The deliverable is a scope contract the user has confirmed with an explicit yes. Produce no plan, spec, code, or any other artifact before that confirmation; premature solutioning is the exact failure this skill exists to prevent. The interrogation ends in exactly two ways: the angle checklist completes and the user signs off, or the user aborts. There is no third exit, and the agent never takes the exit on the user's behalf.

This protocol needs a live user. In non-interactive contexts (CI, background runs, subagent work) flag the ambiguity as a blocker instead of guessing.

## The Angle Checklist

The interrogation is complete only when every angle below is resolved or explicitly deferred with a reason. An angle is resolved when new questions in it stop yielding new information (you can predict the user's answers) and everything it surfaced is sorted into the ledger.

| Angle | Resolved when you know |
|---|---|
| Intent | The outcome wanted, why now, and the problem beneath the stated ask |
| Premise | Whether the ask itself is right: alternative framings weighed, what would make it unnecessary |
| Actors | Who it is for, who else it touches, who can veto or break it |
| Surface | What goes in, what comes out, what it connects to |
| Success | What done looks like, how it will be checked, what outcome the user would regret |
| Constraints | The hard limits (time, money, tech, policy) and which one binds first |
| Edge cases | The extremes, empty states, unusual inputs, and timing issues that still count |
| Failure modes | What happens on breakage or misuse, and the worst credible outcome |
| Adjacencies | What borders the ask unmentioned: follow-on work, integrations, second-order effects |

Premise and Adjacencies never resolve silently; each requires at least one explicit exchange with the user, because both live outside the initial framing and are exactly where interrogations default to staying inside it. When the subject is a topic rather than a task, adapt: Surface becomes the topic's boundary with neighboring topics, Edge cases become counterexamples and gray areas.

## The Scope Ledger

Sort every fact an answer surfaces, immediately, into one of four bins: in scope, out of scope (with the reason and what would bring it back), deferred (with the reason and what decides it later), or open. The ledger is the working state of the interrogation; an unsorted fact is a scope decision being made silently. When an angle closes, say so in one line so the user can see progress:

```text
Closed: failure modes. Open: constraints, premise, adjacencies.
```

## Workflow

### 1. Ground

Read the conversation, codebase, and docs before asking anything. Every question answerable by reading is a wasted round that teaches the user the interrogation is not serious. Seed the ledger with what the reading established and note which angles it already touches.

### 2. Open with a hypothesis

State your best read and an honest confidence number before the first question; users correct a visible wrong guess faster than they answer an open prompt, and the named gap tells them where to aim.

```text
HYPOTHESIS: <one sentence: what you believe they actually want>
CONFIDENCE: ~35%, missing: <what must still surface>
```

### 3. Interrogate

One question per message, never more, always with your best guess or recommended answer attached. Never batch: the next question should depend on the last answer, and batched questions get skim-read. When the AskUserQuestion tool is available, use it with your guess as the recommended option.

- Aim every question at an open angle; before asking, know which angle the answer feeds. A question with no target angle is filler.
- Refuse vague answers into the ledger. "Scalable", "clean", "modern", "just make it work" are placeholders, not answers: probe with "if you didn't have to justify this to anyone, what would you actually want?" or demand a concrete example. Restate any answer you are not certain of and get it confirmed; "roughly means" is unverified.
- Surface contradictions the moment they appear ("you said X earlier, but this implies Y; which is it?"), never at the end.
- Follow dropped fluency. The angle the user answers haltingly or generically is the one that most needs the next question.
- When several rounds move nothing in the ledger, the questions are wrong and that is itself a finding: say so and step back to Premise.
- When the user shows impatience, state what remains and ask whether to continue or abort. Never silently thin the checklist to wrap up; the exit is theirs to take, not yours to take for them.

### 4. Contract and sign-off

Only when every angle is resolved or explicitly deferred, present the scope contract:

```text
SCOPE CONTRACT
Intent:     <the real goal, in the user's words>
Premise:    <survived as asked | reframed to X, because Y>
In scope:
- <item>: <why>
Out of scope:
- <item>: <why excluded, what would bring it back>
Deferred:
- <item>: <reason, what decides it later>
Open risks: <what could still invalidate this>
Yes / no / refine?
```

Gate on an explicit yes. "Sounds good", "sure", and silence are not yes; follow with "anything you'd refine?". "Whatever you think is best" is delegation, not decision: re-ask as a choice between two concrete options. An out-of-scope section that is empty or one line means the interrogation never left the initial framing; go back to Adjacencies and Premise before presenting again.

On yes, the contract feeds whatever comes next: spec for product definition or system design, create-code-plan for implementation, or simply doing the now-defined work. On abort, deliver the ledger as-is, labeled unconfirmed, with the open angles listed.

## Elicitation Methods

Different ambiguities yield to different techniques; pick per question, then return to the one-question mechanics. A stuck line of questioning hands off to another method, never to the exit.

| Method | Pick this when |
|---|---|
| Socratic questioning | The user holds the answer but has not examined it |
| First-principles decomposition | The ask is tangled in inherited assumptions ("we always do X") |
| Inversion | Success is fuzzy but failure is vivid; ask what would guarantee the wrong outcome |
| Red-team | The user is over-committed to one answer; argue the opposing case |
| Pre-mortem | A direction feels settled and risks are unspoken; imagine it failed, trace the causes |
| Constraint removal | A stated limit may be artificial; ask "what if X weren't a limit?" |
| Analogy / expert lens | The user lacks the domain vocabulary; map to a domain they know |
| Stakeholder round-table | Competing interests are unnamed; voice each affected party in turn |
| Decision-tree walk | The subject is an existing plan; map its branches, walk them in dependency order, resolve each explicitly |
| Variation contrast | The want is fuzzy; offer 2-3 deliberately different versions (simpler, inverted, 10x) and let the reaction locate it |

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The ask is clear enough" | If the outcome cannot be written in one sentence right now, it is not clear. |
| "I've covered the angles that matter" | The checklist defines covered. A silently skipped angle is a scope decision the user never made. |
| "Questions waste the user's time" | Targeted questions cost minutes; building the wrong thing costs days, and the user pays. |
| "The user seems impatient, wrap it up" | Impatience means offer the abort explicitly. Taking it for them silently is the one forbidden exit. |
| "I'll figure the rest out as I build" | Discovery during implementation is this same interrogation at 10x the price. |
| "Their answer roughly means X" | Roughly means unverified. Restate it and get confirmation before it enters the ledger. |
| "Attaching my guess leads the witness" | Leading is the point; reacting beats generating. The risk is sycophancy, mitigated by being visibly willing to be wrong. |
| "Several questions at once is faster" | Batches get skim-read and the answers cannot shape each other. One at a time is the pace. |

## Red Flags

- More than one question in a single message
- A question with no guess or recommendation attached
- A question whose answer was already in the conversation, code, or docs
- A buzzword sorted into the ledger without the actually-want probe
- Premise or Adjacencies marked resolved with zero exchanges on them
- Any plan, spec, or code produced before the confirmed contract
- A contract presented while an angle is open and undeferred
- An out-of-scope section that is empty or one line
- Saving any artifact before the user confirmed it

## Gotchas

- **Proportionality gates invocation, not depth.** A single missing fact gets one direct question without this protocol. But once the interrogation starts, it runs the full checklist; a half interrogation produces a contract that lies about being complete.
- **The polite user is the failure mode.** Someone agreeing with every guess is disengaging, not converging. Occasionally guess in a direction you expect pushback on; a user who never corrects you has stopped reading.
- **Domain interrogations outrank this skill.** The spec skill's product and tech modes carry their own interrogation protocols tuned to their documents. When the conversation is clearly headed at one of those artifacts, hand off instead of making the user answer everything twice.
- **Relentless describes the agent's persistence, not the user's captivity.** The agent never quits first, but the user can abort at any time and gets the unconfirmed ledger when they do.

## Example

User: "I want to add caching to my API, it's getting slow."

```text
HYPOTHESIS: You want response caching on the read-heavy endpoints to cut p95 latency.
CONFIDENCE: ~30%, missing: whether the slowness is even the read path, freshness
tolerance, what "slow" is costing you.

Q1 (Intent): What made this urgent this week: a complaint, a metric, a bill?
    My guess: a specific customer complained about one screen.
```

User: "The dashboard takes like 8 seconds, a customer brought it up."

```text
Ledger: in: dashboard latency. Open: premise (8s smells like a query problem,
not a cache problem).

Q2 (Premise): An 8-second page is usually one bad query, not a missing cache,
    and caching it would hide the problem behind staleness. Can we look at the
    dashboard's queries before committing to caching as the framing?
    My guess: two or three N+1 queries we could fix outright.
```

The interrogation continues through the remaining angles. The final contract reads "Premise: reframed to fixing the dashboard queries, because the latency is query-bound" with caching deferred until read traffic justifies it, and cache invalidation, other endpoints, and a CDN layer explicitly out of scope.
