---
name: research-market
description: >-
  Use this skill to research a market and assess product-market opportunity: who
  the customers are, how big and reachable the market is, the competitive
  landscape, real demand signals, and where a wedge to fit might be. Use when
  the user says "market research", "is there a market for this", "product-market
  fit", "PMF", "market size", "TAM", "competitive landscape", "who are the
  competitors", "is this worth building", or "validate the market". The
  deliverable is an evidence-grounded opportunity brief with a go, refine, or
  no-go read. Do not use for defining the product once the market is validated
  (use write-product-spec), for synthesizing feedback from existing users (use
  synthesize-feedback), for comparing technical tools or vendors to adopt (use
  research-solutioning), or for general fact-finding (use deep-research).
---

## Purpose

Assess the market opportunity for a product or feature idea: who would buy it, how big and reachable that market is, what the competition and the do-nothing alternative look like, what real demand exists, and whether there is a credible wedge toward product-market fit. The deliverable is an evidence-grounded opportunity brief, not a pitch. The discipline is refusing to confuse the market you wish existed with the one the evidence shows: size with stated assumptions, count the status-quo alternative as a real competitor, separate enthusiasm from spend, and end with an honest read that can be a no-go.

For depth on any leg (pulling competitor pricing, funding, reviews, search demand across many sources), hand the multi-source fact-finding to the `deep-research` harness. This skill owns the market framing the research feeds.

## Workflow

Copy this checklist and track progress:

```text
Market research:
- [ ] 1. Frame the idea and the target segment
- [ ] 2. Size the market bottoms-up
- [ ] 3. Map competitors and the do-nothing alternative
- [ ] 4. Read the demand signals
- [ ] 5. Find the wedge
- [ ] 6. Synthesize a go / refine / no-go read
```

### 1. Frame the idea and the target segment

State the product, the job it does, and a named ideal-customer hypothesis. A market assessment with no target segment evaluates "everyone", which is no one, and every later step (sizing, competitors, demand) becomes ungroundable. Narrow to a beachhead segment to assess; the whole TAM comes later.

### 2. Size the market bottoms-up

Estimate TAM, SAM, and SOM with stated assumptions, and lead with a bottoms-up build (number of target customers times realistic annual spend), then cross-check against a top-down figure. Top-down alone ("1% of a $50B market") is the vanity trap that justifies anything. Carry confidence; a sized market on guessed inputs is a guess with a dollar sign. Use the `estimate-at-scale` altitude for the arithmetic.

### 3. Map competitors and the do-nothing alternative

List direct competitors, indirect or adjacent ones, and, most importantly, what the customer does today instead: a spreadsheet, a manual process, or nothing. The status-quo alternative is the competitor most analyses miss and the one hardest to displace. For each, capture positioning, pricing, who they serve well, and the gap they leave.

### 4. Read the demand signals

Find evidence the problem is felt and people pay to solve it: search and keyword demand, communities voicing the pain, competitor traction and funding, recurring themes in reviews, and existing spend (the strongest signal). Separate "interesting" from "people pay for this"; surveys of enthusiasm are not demand, revealed spend and search are.

### 5. Find the wedge

Name the underserved segment, unmet job, or differentiation angle the incumbents leave open. Product-market fit starts as a beachhead, not the whole market, so the question is not "is there a market" but "is there a door in". If you cannot name a wedge, say so plainly; a market with no entry is a market you do not have.

### 6. Synthesize a go / refine / no-go read

Close with a clear read: go, refine (promising for segment X but not Y), or no-go, with the single biggest reason and the riskiest assumption the whole thing rests on. A brief that only concludes yes has done marketing, not research; the honest no-go is the most valuable output the skill produces.

## Output shape

An opportunity brief: target segment and job; market size with assumptions and confidence; competitive map (including the do-nothing alternative); demand evidence with sources; the wedge; and the read, with the riskiest assumption and what would change it.

## Gotchas

- **Vanity TAM is self-deception with a number.** "1% of a huge market" assumes the 1% and the market both; size bottoms-up and cross-check, and state what you assumed.
- **The real competitor is usually inertia.** A spreadsheet and the habit of doing nothing beat most analyses' competitor lists; switching cost from the status quo is the hardest thing to overcome.
- **Interest is not demand.** "Cool idea" and survey thumbs-up are cheap; demand is revealed by what people already pay for and search for. Weight spend over sentiment.
- **Pitch mode finds what it wants.** Research run to justify a decision already made surfaces only confirming signal. Hunt the disconfirming evidence and be willing to write the no-go.
- **Whole-TAM thinking has no door.** A market read that cannot name a wedge segment has found a market without an entry. Beachhead first.
- **Memory is not a source.** The market shifts faster than training data; ground claims in current sources via `deep-research`, not a recalled impression of who the players are.

## Example

Idea: a time-tracking tool for freelance designers.

```text
Segment: solo freelance designers who bill hourly (not agencies).

Sizing (bottoms-up): target designers x % who bill hourly x ~$120/yr
willingness-to-pay = SAM in the low tens of millions; cross-checked
against Toggl/Harvest revenue for order of magnitude. The top-down
"1% of the productivity market" framing is deliberately discarded.

Competitors: Toggl, Harvest (horizontal, team-shaped). Do-nothing
alternative: a notes app and a calculator, which most solo freelancers
actually use, and the real competitor to beat.

Demand: steady search for "freelance time tracker"; recurring threads
complaining the big tools feel built for teams. Search and complaints,
not survey enthusiasm.

Wedge: designer-specific (per-client projects, invoice-ready exports)
for the solo segment the horizontal tools under-serve.

Read: REFINE. Strong as a solo-designer wedge, weak as a general tracker
against entrenched incumbents. Riskiest assumption: "feels built for
teams" is painful enough to switch from a free notes-app habit. Validate
willingness-to-pay before building.
```
