Read this when the decision is which product approach is worth pursuing for a user problem: what to build, what shape it takes, how the user reaches value, and whether the approach is even validated enough to commit to. This specializes the core method (diverge, score against weighted axes, name the rejected alternatives, converge) for product discovery, and adds the discovery loop that precedes a commitment: surface the opportunity, generate candidate solutions, find the riskiest assumption, and design the cheapest experiment to test it before building.

This is about the user-value shape of the solution and whether it holds up, not the implementation mechanism (that is technical-solutioning.md) and not picking a named vendor or library (that is research-solutioning and evaluate-software-options). Frame the fork around the user and the outcome, not the stack. When the approach is settled and the open question is which named tool implements it, hand that to research-solutioning.

## Reframe the decision as an opportunity, not a feature

Before diverging, restate the fork as a desired outcome and the user opportunity beneath it, not a feature request. Borrowing the opportunity-solution-tree framing: a measurable desired outcome sits at the top (for example "more users reach their first successful result"); under it are opportunities, the user needs and pains framed from the user's view ("I cannot tell whether my account is healthy"); candidate solutions hang off each opportunity; and experiments validate them. "Should we build a dashboard" is a solution in disguise that has already foreclosed the alternatives. Name the job the user is hiring this for, the moment of need, and what they do today instead. If you cannot state the opportunity without naming a feature, the decision is not yet framed.

## Divergence generators for product approaches

The core method demands genuinely distinct options. Generate at least three candidate solutions per opportunity before committing to any; the first idea is a trap. Force distance along these axes rather than producing three variants of one feature:

- **Feature shape**: full workflow tool versus a single sharp action versus a notification that surfaces the right moment. The same job can be served by very different surface areas.
- **UX direction**: guided/opinionated flow versus flexible/configurable surface versus invisible/automatic (the system acts so the user never touches it).
- **Build versus buy versus partner, from the user-value angle**: build owns the experience and the differentiation; buy or embed a third party gets users value sooner but commoditizes that part; partner or integrate borrows another product's reach. Decide on whether this is where the product should be differentiated, not only on engineering cost.
- **Manual or concierge first**: deliver the outcome by hand or with internal tooling before building user-facing software, to learn whether the value lands at all.
- **Defer or do nothing**: name what the user does without this and whether that is actually painful now. The boring option in the product space is usually "users keep doing the workaround, and that is fine for another quarter."

The deferral option is mandatory here, not optional. Product roadmaps overbuild far more often than they underbuild; the alternative an inflated proposal omits is the one where you ship nothing and the problem turns out not to bind.

## Criteria that decide product approaches

Weight these to the situation; they are the axes the product space adds on top of the generic ones in SKILL.md:

- **User value and problem fit**: how much of the real job each approach actually completes, end to end, not how many features it has. An approach that solves 90 percent of the job for everyone usually beats one that solves 100 percent for a few.
- **Adoption and time to value**: how quickly a user gets the outcome, how much they must learn, change, or migrate to get it. An approach with a steep adoption cliff loses to a weaker one users actually reach.
- **Differentiation**: whether this is where the product should be distinct, or table stakes better bought, embedded, or copied. Building undifferentiated surface area is cost without moat.
- **Reversibility**: how cheaply you can withdraw or change the approach after users depend on it. User-facing commitments are stickier than code; a published workflow, an API others built on, or a pricing promise is expensive to walk back. Favor approaches that keep options open until the demand is proven.
- **Reach and segment fit**: whether the approach serves the segment that matters now, or optimizes for one you are not winning yet.
- **Coherence with the product**: whether it fits the mental model users already have, or adds a second model they must hold. A locally optimal feature that fragments the product loses.

Notably absent and deliberately so: raw implementation cost and operability dominate the technical decision, not this one. They enter here only as time to value and as a tie-breaker, never as the lead axis. If engineering effort is driving the product choice, you are answering the technical question, not the product one.

## Find the riskiest assumption before committing

A product approach that scores well on paper still rests on assumptions that, if wrong, sink it. Before converging, surface the assumptions each leading approach depends on and sort them by risk across the four product risks:

- **Value**: will users actually want this and keep using it? Usually the riskiest for a new approach.
- **Usability**: can users figure it out and reach the outcome without undue friction?
- **Viability**: can the business sustain, monetize, support, and comply with it?
- **Feasibility**: can it be built with what the team and technology can do now?

The riskiest assumption is the one with the highest uncertainty and the highest cost if it turns out false; that is the one to test first, not the one easiest to test. An approach whose value assumption is unproven is a bet, not a decision.

## Design the cheapest experiment for the riskiest assumption

Once the riskiest assumption is named, design the smallest experiment that would move your confidence in it, and run it before the expensive build. State the experiment as a falsifiable hypothesis ("at least X percent of segment Y will do Z"), the method, the metric, and the success threshold. Favor cheap probes that capture real behavior over opinion: a concierge or manual delivery, a landing page or waitlist, a fake-door click test, a pre-order or other skin-in-the-game commitment. Measure what users do, not what they say they would do, and collect your own signal rather than leaning on someone else's market data. The experiment's job is evidence, not a shippable product; pick the one that retires the most risk per hour spent.

## Converge with a deferral line and the test that gates it

Recommend one approach and, distinct to product decisions, state explicitly what you are deferring and why: the slice you ship now, the slice you are deliberately not building yet, the signal that would tell you to build it, and the experiment result that gates committing at all when the riskiest assumption is still open. A product recommendation that does not name what it defers has not actually scoped; it has just ordered the whole backlog. The strongest rejected alternative still gets named per the core method, and if its best piece is graftable (a UX idea, a segment it served better), say so.

## Pitfalls specific to product decisions

- **The feature is the decision in disguise.** Arriving with "build feature X" and generating three flavors of X is fake divergence dressed as product thinking. Go back up to the opportunity and regenerate from there.
- **Committing before testing the value assumption.** Scoring approaches on paper and shipping the winner without a cheap probe, when whether users want it at all is the open question, is the product analogue of skipping the spike. Run the experiment first.
- **Testing the easy assumption, not the risky one.** Validating feasibility (which you are fairly sure of) while leaving value (which you are not) untested burns effort and retires no real risk. Sort by uncertainty times cost-if-wrong.
- **Solving for the loud user, not the common job.** The most vocal request is not the most valuable approach. Weight by the job most users share, not by who asked loudest.
- **Counting features instead of completed jobs.** A richer feature set is not more user value; an approach that completes the job with less surface usually wins on adoption and coherence both.
- **Ignoring adoption cost.** The best approach on paper that requires users to change their workflow, migrate data, or learn a new model often loses to a weaker approach they reach without friction. Time to value is a first-class axis, not a footnote.
- **Building what should be bought.** Spending the team's differentiation budget on undifferentiated surface area is a product mistake, not just an engineering one. If users would not care who built it, that is a buy-or-embed candidate.
- **No deferral line.** Converging on an approach without naming what you are not building yet turns a decision aid into a license to build everything. State the deferred slice and its trigger.
