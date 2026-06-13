---
name: plan-pricing
description: Use this skill when designing a pricing and packaging model for a software product, including picking a pricing model (flat, per-seat, usage-based, tiered, freemium, value-based), choosing the metric to charge on, estimating willingness to pay, and laying out tiers. Use when the user says "how should I price this", "what should I charge", "design the pricing", "set up our tiers", "freemium or paid", "per-seat vs usage-based", or "what's our pricing model". Do not use for sizing or segmenting the market (use research-market) or for cost and capacity math at scale (use estimate-at-scale).
---

## Purpose

Interview the user for the inputs a pricing decision requires, then produce a concrete pricing-and-packaging recommendation artifact for a software product: a chosen model, the metric charged on, a willingness-to-pay estimate, competitive and value framing, and a tier table. Do not lecture on pricing theory and do not emit a recommendation until the four load-bearing inputs are gathered (value delivered, the customer's alternative, the buyer, the competitive set); a recommendation built on assumed inputs anchors the user on a wrong number that is expensive to walk back. The deliverable is the artifact in the final section, not prose about pricing.

## Workflow

```text
Pricing plan checklist:
- [ ] 1. Interviewed for the six inputs; gaps stated as assumptions, not invented
- [ ] 2. Quantified value delivered and the customer's next-best alternative cost
- [ ] 3. Picked a model from the table with the reason it beats the runner-up
- [ ] 4. Chose ONE value metric that scales with the value the buyer perceives
- [ ] 5. Estimated WTP from value and competitor anchors, not from cost-plus
- [ ] 6. Designed 2-4 tiers with feature gating on value, an anchor tier, annual discount
- [ ] 7. Wrote the artifact with assumptions-to-test and risks
```

### 1. Interview for the inputs

Ask for all of these in one message; skip only what the user already gave. Do not proceed to a recommendation with any of the first four missing, because each one independently moves the price and you cannot back-solve them from a number.

- **Value delivered**: the concrete outcome the product produces (hours saved, revenue gained, cost or headcount avoided, risk reduced). Push for a number, not an adjective.
- **The customer's alternative**: what they do today instead (a competitor, a manual process, a spreadsheet, nothing) and what that costs them. This is the true price ceiling reference, not your costs.
- **Who buys and who uses**: an individual self-serve buyer, a team lead, or a procurement-driven enterprise. The buyer determines the model and the sales motion more than the product does.
- **Competitive set**: the two or three alternatives a buyer compares against, with their published prices if known.
- **Variable cost to serve one customer**: the floor below which you lose money per unit. Used only as a floor; never price up from it.
- **Business goal**: land-grab market share, maximize revenue per customer, or fund the business from customer #1. This breaks ties between otherwise-valid models.

When an input is genuinely unavailable, state the assumption you are proceeding on explicitly in the artifact's assumptions list so a wrong one is visible and correctable, rather than silently picking one.

### 2. Quantify value and the alternative

Express the value delivered in the same unit the customer measures their alternative in, so the two are comparable. The defensible price lives between the variable cost floor and a fraction (commonly 10-30%) of the quantified annual value the customer captures; charging a slice of value created is what makes a price feel fair rather than extractive. If value cannot be quantified at all, the buyer will anchor entirely on competitors, so weight step 4 toward competitive framing instead.

### 3. Pick the pricing model

Choose one primary model. Recommend it by naming why it beats the closest runner-up for this buyer and value metric, not by listing every model's merits.

| Model | Charge on | Fits when | Watch out for |
|---|---|---|---|
| Flat-rate | One price, all-you-can-use | Single segment, predictable usage, self-serve simplicity wins | Leaves money on the table from heavy users; no expansion path |
| Per-seat | Active users / seats | Collaboration value grows with team size | Buyers ration seats and share logins; breaks if value is not per-person |
| Usage-based | Consumption (API calls, compute, events, GB) | Cost-to-serve tracks usage; value is consumption-shaped | Revenue unpredictability and customer bill anxiety suppress adoption |
| Tiered | Bundles at fixed prices | Distinct segments want distinct feature sets | Too many tiers cause choice paralysis; gate on value, not arbitrary caps |
| Freemium | Free base, paid upgrade | Viral or network effects, low marginal cost, large top of funnel | Conversion is typically 1-5%; the free tier must leave a real reason to pay |
| Value-based | Negotiated to value captured | High-impact enterprise, dedicated sales, quantifiable ROI | Needs a sales team and ROI proof; does not work self-serve |

Always charge something rather than ship free-by-default outside a deliberate freemium funnel: the gap between $0 and any price is a behavioral cliff (the zero-price effect), and a free default forfeits the signal of what customers actually value. Hybrids are common and expected (freemium plus usage, per-seat plus a platform fee); pick the dominant axis first, then layer.

### 4. Choose the value metric

Select exactly one primary metric you charge on. The right metric rises as the customer gets more value and is something they can predict and control. A metric the buyer cannot forecast (raw compute-seconds) or that punishes engagement (charging per login) caps growth because customers optimize against their own success. Test the candidate metric against three questions: does it grow with realized value, can the buyer estimate their bill before committing, and does it align your incentive with theirs.

### 5. Estimate willingness to pay

Anchor WTP on the quantified value (step 2) and the competitive set (step 1), never on cost-plus; cost-plus pricing in software systematically underprices because marginal cost is near zero while value is not. If survey data exists, apply the Van Westendorp four-question frame to find the acceptable band.

| Question to the buyer | Signal |
|---|---|
| At what price is it so cheap you doubt its quality? | Lower bound of credibility |
| At what price is it a bargain? | Bottom of the acceptable range |
| At what price does it start feeling expensive? | Top of the acceptable range |
| At what price is it too expensive to consider? | Upper bound |

Without survey data, triangulate: set the floor at variable cost, the ceiling at 10-30% of annual value delivered, and sanity-check the result against where competitors sit. Start nearer the low end of the defensible band when the goal is adoption; price is the easiest thing to raise later and the hardest relationship to rebuild after a cut.

### 6. Design the packaging

- **Tiers**: 2-4, no more. Each tier targets one segment from the interview and reads as an obvious choice for that segment.
- **Feature gating**: gate on features and limits that track the value metric, not on arbitrary throttles. A buyer should upgrade because they outgrew the value, not because a counter they do not care about hit a wall.
- **Anchor tier**: design the middle tier to be the obvious pick, and price the top tier high enough to make the middle feel reasonable by contrast.
- **Annual discount**: offer annual billing at roughly 15-20% off monthly to trade a discount for cash and lower churn.
- **Trial or free entry**: include a path to experience value before paying (time-limited trial or a freemium tier), because self-serve buyers compare in parallel tabs and a no-try option loses by default.

### 7. Output the recommendation artifact

Produce exactly this structure. Flag every assumption that must be validated before launch with how to test it; a pricing plan whose assumptions are not testable cannot be corrected before it costs revenue.

```markdown
## Pricing Recommendation: <product>

**Model:** <model> because <why it beats the runner-up for this buyer>
**Value metric:** <the one unit charged on>
**WTP band:** <low>-<high> per <metric per period>, anchored on <value/competitor basis>

| Tier | Price | Target segment | Gated on (value metric) | Positioning |
|---|---|---|---|---|
| <tier> | <price> | <segment> | <what unlocks> | <why this tier> |

**Annual:** <monthly vs annual>
**Entry:** <trial / freemium / none and why>

**Assumptions to validate:**
- <assumption> -> <experiment: landing-page price test, founder-led sales call, cohort conversion>

**Risks:**
- <risk> -> <mitigation>
```

## Gotchas

- **Cost-plus underprices software by default.** Marginal cost is near zero, so a margin on cost ignores the value gap that is the whole basis for the price. Use cost only as the floor, never the anchor.
- **The wrong value metric caps growth invisibly.** If the metric punishes the customer for succeeding (per-login, per-stored-record they cannot prune), they suppress usage and you have built a ceiling into the contract. Pick the metric that rises with realized value.
- **Free-by-default forfeits the strongest pricing signal.** Outside a deliberate freemium funnel, charging nothing means you never learn what the product is worth and cross the zero-price behavioral cliff in the wrong direction. Charge something from the first customer.
- **More tiers feel generous and convert worse.** Each added tier multiplies the buyer's decision cost; four is a hard ceiling and three is usually better. Cut tiers before adding them.
- **Pricing is reversible up, painful down.** Starting low and raising as the product improves is healthy and expected; cutting a price signals trouble and erodes trust. When uncertain, start at the low end of the defensible band.

## Example

Worked end to end for a real-shaped product: a B2B meeting-notes-to-CRM tool that auto-logs sales calls into Salesforce.

- **Value delivered**: saves each rep ~5 hours/week of manual CRM entry; at a loaded $80/hr that is ~$1,600/month of recovered selling time per rep.
- **Alternative**: reps do it by hand (the recovered time above) or use a generic transcription tool (~$30/seat/month) that does not write to the CRM.
- **Buyer/user**: a VP of Sales buys for the team; reps use it. Team adoption, not individual self-serve.
- **Competitive set**: generic transcribers at ~$30/seat; an enterprise revenue-intelligence suite at ~$100+/seat.
- **Model**: per-seat. It beats usage-based because the value (selling time recovered) is inherently per-rep, and beats flat-rate because the VP expects cost to scale with team size and a flat price would leave large-team revenue uncaptured.
- **Value metric**: active rep seats. Rises with team value, the VP can forecast it from headcount, and it does not punish usage.
- **WTP**: floor near the ~$30 generic tier; ceiling at ~15% of the ~$1,600/seat monthly value, about $240. Land below the enterprise suite to win on focus. Band $40-$80/seat/month.

```markdown
## Pricing Recommendation: AutoLog CRM Notes

**Model:** Per-seat because the value (selling time recovered) is per-rep and the VP expects cost to scale with headcount.
**Value metric:** Active rep seats
**WTP band:** $40-$80 per seat/month, anchored on ~15% of $1,600/seat value recovered, priced under the $100+ enterprise suite

| Tier | Price | Target segment | Gated on (seats + features) | Positioning |
|---|---|---|---|---|
| Starter | $40/seat/mo | Small teams (<10 reps) | CRM auto-logging, 1 CRM integration | Entry, undercuts manual cost |
| Team | $65/seat/mo | Growing sales orgs | + analytics, multiple integrations, admin | Anchor: the obvious pick |
| Scale | $90/seat/mo | Large orgs | + SSO, custom fields, priority support | Makes Team feel reasonable |

**Annual:** 18% off monthly (Team becomes ~$53/seat/mo billed annually)
**Entry:** 14-day team trial; no permanent free tier (B2B buyer evaluates in a trial window, not a freemium funnel)

**Assumptions to validate:**
- VPs value 5 recovered rep-hours/week at ~$1,600/mo -> founder-led sales calls quoting the ROI math
- $65 anchor converts better than $80 -> A/B landing-page price test on the Team tier

**Risks:**
- Enterprise suite drops price to compete -> defend on focus and faster setup, not on undercutting further
- Reps share logins to ration seats -> enforce per-active-user metering, not honor-system seats
```
