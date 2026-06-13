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
- [ ] 2. Size the market (TAM, SAM, SOM)
- [ ] 3. Map the competitive landscape and the market structure
- [ ] 4. Read the demand signals
- [ ] 5. Find the wedge
- [ ] 6. Synthesize a go / refine / no-go read
```

### 1. Frame the idea and the target segment

State the product, the job it does, and a named ideal-customer hypothesis. A market assessment with no target segment evaluates "everyone", which is no one, and every later step (sizing, competitors, demand) becomes ungroundable. Narrow to a beachhead segment to assess; the whole TAM comes later.

### 2. Size the market: TAM, SAM, SOM

Size three nested figures with stated assumptions, and compute TAM two independent ways so they can check each other:

- **TAM (top-down):** start from a published industry figure and narrow to the relevant slice.
- **TAM (bottom-up):** number of target customers times realistic annual spend, built from the ground up.
- **Reconcile the two.** They will not match; the gap is the point. A disagreement of more than roughly an order of magnitude means a load-bearing assumption is wrong (customer count, price, or the slice you carved), so hunt it down before trusting either number. A single method is easy to fool yourself with; two that disagree expose the bad assumption.
- **SAM:** the serviceable slice of TAM you can actually reach given product, channel, geography, and pricing tier.
- **SOM:** what is realistically obtainable in 1-3 years given competition, traction, and go-to-market capacity.

Lead with the bottom-up build; top-down alone ("1% of a $50B market") is the vanity trap that justifies anything. Carry confidence; a sized market on guessed inputs is a guess with a dollar sign. Use the `estimate-at-scale` altitude for the arithmetic.

### 3. Map the competitive landscape and the market structure

List direct competitors, indirect or adjacent ones, and, most importantly, what the customer does today instead: a spreadsheet, a manual process, or nothing. The status-quo alternative is the competitor most analyses miss and the one hardest to displace. But a list only tells you who is in the room; it does not tell you whether the room is worth entering. Do two things on top of the list.

**Battlecard each serious player.** For each direct competitor and the do-nothing alternative, capture a few lines, not a dossier:

- **Positioning:** who they serve well and the one-sentence promise they make.
- **Pricing and model:** the number and the shape (per-seat, usage, freemium, flat).
- **Strengths:** what genuinely makes them hard to beat (brand, integrations, lock-in, distribution).
- **Weaknesses and the gap they leave:** the segment or job they under-serve.
- **Where you win / where you lose vs them:** the honest two-sided read. If you cannot name where you lose, you have not researched them, you have pitched against them.

**Read the industry structure, not just the players.** A competitor is something you can out-execute; a structural force constrains every player including you, so no amount of execution escapes it. Assess only the two or three of Porter's forces that bite hardest in this market, each as low / medium / high with the reason and the trend:

- **Rivalry:** many similar players, slow growth, and weak differentiation mean margins get competed away no matter how good you are.
- **Buyer or supplier power:** a few concentrated buyers (or one critical supplier or platform you depend on) sets your price and can squeeze you at will.
- **Substitutes:** a cheaper or good-enough adjacent solution caps what anyone can charge.
- **Entry barriers:** low barriers mean a win invites a flood of fast followers; high barriers (network effects, IP, switching costs) protect a winner but also mean entrenched incumbents are hard to dislodge.

The distinction is the deliverable: a beatable competitor is an opportunity, a hostile structure is a reason the whole market may not be winnable for anyone. Name which forces are load-bearing and skip the ones that are not; this is a founder's read, not a five-force term paper.

### 4. Read the demand signals

Find evidence the problem is felt and people pay to solve it: search and keyword demand, communities voicing the pain, competitor traction and funding, recurring themes in reviews, and existing spend (the strongest signal). Separate "interesting" from "people pay for this"; surveys of enthusiasm are not demand, revealed spend and search are.

### 5. Find the wedge

Name the underserved segment, unmet job, or differentiation angle the incumbents leave open. Product-market fit starts as a beachhead, not the whole market, so the question is not "is there a market" but "is there a door in". If you cannot name a wedge, say so plainly; a market with no entry is a market you do not have.

### 6. Synthesize a go / refine / no-go read

Close with a clear read: go, refine (promising for segment X but not Y), or no-go, with the single biggest reason and the riskiest assumption the whole thing rests on. A brief that only concludes yes has done marketing, not research; the honest no-go is the most valuable output the skill produces.

## Output shape

An opportunity brief: target segment and job; market size with assumptions and confidence; competitive map (battlecards for the serious players including the do-nothing alternative, plus the load-bearing structural forces); demand evidence with sources; the wedge; and the read, with the riskiest assumption and what would change it.

## Gotchas

- **Vanity TAM is self-deception with a number.** "1% of a huge market" assumes the 1% and the market both; size bottoms-up and cross-check, and state what you assumed.
- **The real competitor is usually inertia.** A spreadsheet and the habit of doing nothing beat most analyses' competitor lists; switching cost from the status quo is the hardest thing to overcome.
- **A competitor list is not a structural read.** Naming who is in the market tells you nothing about whether it is winnable. You can out-execute a competitor; you cannot out-execute concentrated buyer power, a commoditized rivalry, or a substitute that caps the price. Separate the player you can beat from the force that constrains everyone.
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

Competitors: Toggl, Harvest (horizontal, team-shaped; strong brand and
integrations, weak on solo-designer workflows; we win on per-client fit,
lose on ecosystem maturity). Do-nothing alternative: a notes app and a
calculator, which most solo freelancers actually use, and the real
competitor to beat. Structure: rivalry HIGH (many cheap trackers,
commoditized), substitute threat HIGH (the free notes-app habit), entry
barriers LOW. The structural read, not the competitor count, is what
makes this hard.

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
