---
name: plan-go-to-market
description: Use this skill to plan a go-to-market launch for a software product or feature, choosing the GTM motion (product-led, sales-led, community-led), the beachhead segment and ideal-customer profile, the positioning, the channels, the launch sequence, and success metrics. Use when the user says "plan the launch", "go-to-market", "GTM plan", "how do we launch this", "launch strategy", or "PLG vs sales-led". Do not use for sizing the market or validating demand (use research-market), for the technical release and rollback (use prepare-for-deploy), or for a sales document (use write-proposal).
---

## Purpose

Produce a concrete go-to-market plan for launching a software product or feature: the motion that gets it to buyers, the beachhead segment and ideal-customer profile to aim at first, the positioning and messaging, the channels, the launch sequence, and the success metrics that say it worked. Interview for the inputs before planning; a GTM plan written from assumptions targets the market you wish you had, not the one you can reach. The deliverable is a single GTM plan artifact, not a launch executed.

This skill plans the market launch. It does not size the market or validate demand: if the target segment, market size, or whether anyone wants this is still open, run `research-market` first and feed its findings in here. It also does not plan the technical release; rollout, rollback, and release readiness belong to `prepare-for-deploy`. A GTM plan assumes a buildable product aimed at a validated market and decides how it reaches customers.

## Workflow

Copy this checklist and track progress:

```text
GTM plan:
- [ ] 1. Interview for inputs (refuse to plan without them)
- [ ] 2. Choose the GTM motion
- [ ] 3. Pick the beachhead segment and ICP
- [ ] 4. Set positioning and messaging
- [ ] 5. Choose and sequence channels
- [ ] 6. Sequence the launch
- [ ] 7. Define what success looks like
- [ ] 8. Assemble the plan artifact
```

### 1. Interview for inputs

Do not draft any of the plan until these are answered; each missing answer is a section you would otherwise fabricate. Ask in one batch:

- What is the product or feature, and what job does it do for the user?
- Who is the buyer, and is the buyer the same as the user? (decides motion and message)
- Price point and contract value, and the expected sales-cycle length.
- Validated target segment and demand evidence (from `research-market` if it ran).
- Team, budget, and the launch deadline or window.
- The top one or two competitors and the do-nothing alternative customers use today.
- What outcome would make this launch a success in 90 days?

If `research-market` already produced a segment and demand read, mine it instead of re-asking; only fill the gaps. If the buyer, price, and segment are still unknown after asking, stop and say so: the motion choice in step 2 is unrecoverable without them.

### 2. Choose the GTM motion

The motion is the load-bearing decision; it determines the channels, the message, the team, and the metrics. Choose the primary motion from price, buyer, and sales cycle, then name at most one secondary motion to layer later. Most launches run one primary motion well; a launch spread across three motions executes none.

| Motion | Fits when | Buyer reaches product via | Primary metric |
|---|---|---|---|
| Product-led (PLG) | Low price, self-serve, fast time-to-value, individual or team buyer | Free trial or freemium, in-product onboarding | Activation rate, free-to-paid conversion |
| Sales-led | High contract value, committee buyer, long cycle, complex product | Outbound, demos, account-based outreach | Pipeline, win rate, deal size |
| Community-led | Developer or practitioner buyer, network effects, low CAC tolerance | Forums, events, advocates, content | Active members, advocate-sourced signups |

Decision rule: contract value under roughly a self-serve threshold and a product a user can adopt alone points to product-led; a buying committee and a five-figure-plus deal points to sales-led; a peer-credibility buyer who distrusts ads points to community-led. State the rule you applied and why the rejected motions lose, so the choice survives a later challenge.

### 3. Pick the beachhead segment and ICP

Narrow to the smallest winnable, referenceable segment, then profile the ideal customer inside it. A vague mass-market target makes every later step ungroundable. Score candidate segments and pick the highest combined score:

- Burning pain: the problem is acute, getting worse, and current workarounds are fragile or expensive.
- Willingness to pay: budget exists for this problem and the ROI beats the price.
- Winnable: small enough to plausibly dominate, with a differentiation or distribution edge over incumbents.
- Referenceable: customers talk to each other and to adjacent segments, so winning one seeds the next.

Then write the ICP for that segment so messaging and channels have a target: firmographics (size, industry, role), the job-to-be-done, the top pain points, the buying process and who signs, and explicit disqualifiers (who looks like a fit but is not). The disqualifiers matter as much as the fit: an ICP that excludes no one focuses no one.

### 4. Set positioning and messaging

Positioning states what the product is, who it is for, and why it beats the alternative the ICP uses today. Anchor the alternative on the real status quo, including doing nothing, not only a named competitor. Build the message in this order so it stays grounded in the ICP's pain, not the product's feature list:

1. The ICP's burning pain, in their words.
2. The promise: the after-state the product delivers.
3. Two or three differentiators that make the promise credible against the alternative.
4. Proof: a metric, a customer quote, or a demo moment for each differentiator.

For the top competitor, prepare the objection counters the launch will face ("why not competitor X?", "they are cheaper", "they are more established") with a response framed on the ICP's outcome, not a feature war. Keep it to the one or two competitors the ICP actually weighs; a battlecard against every rival is noise.

### 5. Choose and sequence channels

Channels follow from the motion and the ICP, never the reverse: pick the channels that reach this ICP through this motion, and run two or three well rather than seven poorly. Use the motion-to-channel fit below as the starting set, then cut to where the ICP actually pays attention.

| Motion | Lead channels | Why these |
|---|---|---|
| Product-led | Content/SEO, in-product virality, community, light paid | Low CAC channels that scale with self-serve signup |
| Sales-led | Outbound, account-based marketing, partnerships, events | Reach concentrated high-value accounts directly |
| Community-led | Forums, events, advocate programs, developer content | Earn peer credibility the ICP trusts over ads |

For a product-led or community-led motion, decide whether a growth loop can carry acquisition: a built-in mechanism where using the product creates the next user (a shared artifact, a collaboration invite, a referral incentive). A working loop compounds and lowers CAC; only design one when the product's core action naturally produces a share or an invite, otherwise it is a feature nobody triggers.

### 6. Sequence the launch

Phase the launch so momentum builds instead of peaking on day one and dying. Lay it on a timeline against the deadline from step 1, with a go/no-go gate before the public moment:

- Pre-launch: finalize messaging and assets, prime channels, line up design partners or beta users and early proof, set the baseline for every success metric.
- Launch: the public moment and announcement across the chosen channels, concentrated to be visible.
- Post-launch: sustain with content, partnerships, and community; run the feedback-and-optimize cadence; report against the metrics.

Name a go/no-go gate before launch with explicit criteria (proof in hand, assets ready, baseline captured); a launch with no gate ships on the calendar regardless of readiness.

### 7. Define what success looks like

Set targets before launch and capture the pre-launch baseline, or post-launch numbers prove nothing. Choose a small metric set tied to the motion, spanning the funnel, with one headline metric that defines success:

- Awareness: reach, impressions, qualified traffic.
- Acquisition and activation: signups, trials, demos, activation rate (the PLG headline).
- Conversion and revenue: free-to-paid, pipeline, win rate, new MRR, CAC.
- The 90-day success outcome from step 1, stated as a number to hit.

Tie each metric to the motion: a PLG plan whose headline metric is pipeline is measuring the wrong motion. Define the headline metric and its target explicitly; a plan that tracks ten metrics equally has no definition of success.

### 8. Assemble the plan artifact

Write the plan as one Markdown document with these sections, each carrying the decision and its reasoning, not just the choice:

```text
1. Summary: product, motion, beachhead, headline success metric
2. Motion: chosen motion, why, rejected alternatives
3. Beachhead and ICP: segment scoring, ICP profile, disqualifiers
4. Positioning and messaging: positioning statement, message, competitor counters
5. Channels: chosen channels, sequence, growth loop if any
6. Launch sequence: pre-launch / launch / post-launch timeline with go/no-go gate
7. Success metrics: funnel metrics, headline target, 90-day outcome, baseline
8. Risks: top launch risks and mitigations
```

State assumptions inline wherever an input was estimated rather than known, so a wrong one is visible and correctable instead of buried in the plan.

## Gotchas

- **The motion is upstream of everything; deciding channels first inverts the plan.** Channels, message, team, and metrics all derive from the motion. A team that picks channels before the motion ends up running paid ads for a community-led product or hiring sales reps for a self-serve one.
- **A beachhead that excludes no one focuses no one.** "Mid-market and enterprise across several verticals" is not a beachhead. The point of the beachhead is to dominate one small referenceable segment, then expand; the disqualifiers in the ICP are what make it small enough to win.
- **Success metrics without a pre-launch baseline are unfalsifiable.** "10,000 signups" means nothing if you never recorded the trajectory before launch. Capture the baseline in pre-launch or the launch cannot be shown to have caused anything.
- **A growth loop is not a referral feature you bolt on.** It only compounds when the product's core action naturally produces a share or invite. Adding a referral incentive to a product nobody shares yields a button nobody clicks; design the loop only where the usage already wants to spread.
- **Defer market sizing and demand validation.** If the plan starts arguing whether anyone wants the product or how big the market is, the wrong skill is loaded. That is `research-market`; this skill assumes a validated market and plans how to reach it.

## Example

Launching a PDF-to-structured-data API for developers, priced at usage-based metering starting near zero, buyer is the individual developer.

- **Motion**: Product-led. Self-serve, low entry price, fast time-to-value, the developer adopts alone with no committee. Sales-led rejected (no committee, contract value too low to fund reps); community-led named as the secondary motion because developers trust peer proof over ads.
- **Beachhead and ICP**: Solo and small-team developers building document-ingestion features who today stitch together brittle open-source OCR. Burning pain (fragile pipelines), clear ROI (hours saved per integration), winnable (incumbents target enterprise), referenceable (developers post what works). ICP: backend or full-stack engineer at a seed-to-Series-B startup shipping a document feature. Disqualifier: enterprises needing on-prem and procurement.
- **Positioning and message**: "Structured data from any PDF in one API call, for developers who would rather ship than babysit an OCR pipeline." Differentiators: one call vs a multi-tool pipeline, accuracy on messy real-world PDFs, transparent usage pricing. Proof: a 10-line quickstart, an accuracy benchmark, a usage-cost example. Competitor counter to a cheaper raw-OCR tool: total cost of ownership once you add the parsing and cleanup it omits.
- **Channels**: Developer content and SEO on the exact pain ("parse messy PDFs to JSON"), a generous free tier as the in-product entry, and presence where these developers already are (a relevant community and changelog). Growth loop: shared, runnable example outputs that link back to the playground, so one developer's demo recruits the next.
- **Launch sequence**: Pre-launch (quickstart and benchmark published, 20 design-partner developers on the free tier, baseline signup trajectory recorded). Go/no-go gate: benchmark live, free tier stable, three public testimonials. Launch (Show HN plus changelog plus docs-site banner, same day). Post-launch (weekly use-case posts, partner-integration writeups, fortnightly metric review).
- **Success metrics**: Headline is free-to-paid conversion at 90 days, target 5 percent. Funnel: qualified docs traffic, free-tier signups, activation (first successful API call), conversion, new MRR. 90-day outcome: 500 activated free accounts and 25 paying, against a recorded near-zero baseline.
