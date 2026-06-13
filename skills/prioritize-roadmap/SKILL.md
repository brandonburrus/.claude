---
name: prioritize-roadmap
description: >-
  Use this skill to decide what to build next and in what order from a set of
  candidate features, bets, epics, or backlog items. Use when the user says
  "prioritize the roadmap", "what should we build next", "rank these features",
  "what's the priority", "RICE these", "value vs effort", "sequence the
  backlog", "what do we cut", or "what's most important to ship this quarter".
  The deliverable is a ranked and sequenced list with the reasoning and the
  explicit cut pile. Do not use for defining what one feature is (use
  write-product-spec), for breaking a chosen item into tasks (use
  decompose-into-tasks), for triaging individual incoming issues (use
  triage-backlog), or for choosing among technical approaches to one problem (use
  explore-solutions).
---

## Purpose

Turn a set of candidate features, bets, or backlog items into a ranked and sequenced roadmap, with the scoring visible and the cut pile explicit. The deliverable is an ordering and its reasoning, not a spec or a task breakdown. The discipline is refusing to rank by gut or by whoever asked loudest: score against criteria tied to the goal, sequence by dependency and risk, and make the "no" pile as deliberate as the "yes" pile. A roadmap that says yes to everything has prioritized nothing.

## Workflow

Copy this checklist and track progress:

```text
Prioritize:
- [ ] 1. Frame the goal as a measurable objective
- [ ] 2. Gather the candidates
- [ ] 3. Pick one scoring lens
- [ ] 4. Score honestly, with confidence
- [ ] 5. Sequence, do not just rank
- [ ] 6. Make the cut explicit
- [ ] 7. Name what would change the order
```

### 1. Frame the goal as a measurable objective

Priorities are meaningless without the objective they serve, and a vague objective is no better than none: ranking against "grow the business" is unfalsifiable, so any score survives and the cut pile is indefensible. Make the goal checkable before scoring anything.

- **Name the metric the work must move.** Establish a single success metric for the cycle, ideally a north-star metric: one customer-centric measure of the value users get, a leading indicator of the business outcome, not a raw revenue or activity count. Add 2 to 4 input metrics that drive it (the levers a feature can actually pull, like activation rate or repeat usage). Candidates then compete on how much they move these, not on how they feel.
- **Express the goal as an objective with key results.** State the qualitative objective and the 2 to 3 key results that say what "moved it" means in numbers (a target on the north-star or its inputs). Each candidate then has to ladder to a key result; an item that maps to no key result is either a missing objective or a cut.

Pull the metric and objective from the user; they live in their head, not the backlog. Without them, every score is arbitrary and the exercise just launders a gut call. If the user cannot name a metric, that gap is the finding to surface, not a reason to invent one.

### 2. Gather the candidates

List the items in contention, each with enough detail to score: the value it claims, who it is for, the rough effort, and its dependencies. An item too vague to score is not ready to prioritize; send it back to discovery or `write-product-spec` rather than guessing a score for it.

### 3. Pick one scoring lens

Choose the lens that fits the situation, name why, and do not blend two. Blending (averaging a RICE score with a gut 2x2) hides the actual decision behind false math.

| Lens | Best when | Shape |
|---|---|---|
| Value vs Effort (2x2) | small set, fast triage | plot, take the high-value low-effort quadrant first |
| RICE | feature backlog with measurable reach | Reach x Impact x Confidence / Effort |
| Weighted scoring | several criteria matter unequally | sum of (criterion score x weight): value, strategic fit, risk, effort |
| WSJF / cost of delay | timing and urgency dominate | (value + time-criticality + risk-reduction) / effort |
| Kano | sorting a release into must-haves vs delighters | basic, performance, delighter buckets |

### 4. Score honestly, with confidence

Score each candidate against the lens and state confidence alongside. Effort and reach are rough by nature (use the `estimate-at-scale` altitude); a RICE score to two decimals on guessed inputs is theater. A high-impact, low-confidence item earns a discovery spike, not a high rank on faith; sandbagging confidence to high everywhere to avoid that spike is the move to catch in yourself.

### 5. Sequence, do not just rank

A sorted list is not a roadmap. Re-order the ranked list by:

- **Dependencies**: foundations first; a high-scoring item blocked by a low-scoring one waits.
- **Risk**: de-risk the scary bet early, before other work is built on top of an assumption that might not hold.
- **Value cadence**: ship something users feel soon, rather than a long invisible foundation.

Group the result into now / next / later (or this-cycle / next-cycle / backlog).

### 6. Make the cut explicit

The "not now" pile is the hardest and most valuable output. State what is deprioritized and the single reason each lost: low value against the goal, blocked, low confidence, or simply outranked by limited capacity. A roadmap without a visible cut list is a wishlist that hides the trade-off it was supposed to make.

### 7. Name what would change the order

Priorities rest on assumptions: the goal, the value estimates, the confidence. Name the one or two that, if wrong, would reshuffle the list, so the user knows what to watch and when to re-prioritize.

## Output shape

A table plus the cut list and the assumptions:

| Item | Score (lens) | Confidence | Bucket | One-line rationale |
|---|---|---|---|---|

Then: **Cut for now:** item, reason, one line each. Then: **Re-prioritize if:** the assumption that would flip it.

## Gotchas

- **No goal means no priority, and a vague goal is no goal.** Scoring without the objective it serves is noise with a number attached, and "grow the business" survives any ranking. The criterion is a success metric and its key results; an item that ladders to none of them is a cut, not a contender.
- **The loudest voice is not the criterion.** The stakeholder who asks most often, or the HiPPO (highest-paid person's opinion), is one input weighted like any other against the goal, not an override.
- **Ranking is not sequencing.** A list sorted purely by score ignores dependencies and risk; foundations and scary bets come first regardless of their raw number.
- **False precision is theater.** Two-decimal RICE on guessed reach and effort projects a rigor the inputs do not have. Round, and carry the confidence instead.
- **The cut pile is the deliverable, not the leftover.** If everything made the roadmap, no prioritization happened. The discipline is in what you said no to and why.
