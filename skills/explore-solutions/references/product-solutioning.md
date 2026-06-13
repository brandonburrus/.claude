Read this when the decision is which product approach best solves a user problem: what to build, what shape it takes, and how the user reaches value. This specializes the core method (diverge, score against weighted axes, name the rejected alternatives, converge) for the product space. The shared method lives in SKILL.md; this file adds only the axes, generators, and pitfalls particular to product decisions.

This is about the user-value shape of the solution, not the implementation mechanism (that is technical-solutioning.md) and not picking a named vendor or library (that is research-solutioning and evaluate-software-options). Frame the fork around the user and the outcome, not the stack.

## Reframe the decision around the user

Before diverging, restate the fork as a user problem and an outcome, not a feature request. "Should we build a dashboard" is a solution in disguise; the decision is "how do users understand the state of their account today, and which approach moves that the most for the least." A fork stated as a feature has already foreclosed the alternatives. Name the job the user is hiring this for, the moment of need, and what they do today instead. If you cannot state the user problem without naming a feature, the decision is not yet framed.

## Divergence generators for product approaches

The core method demands genuinely distinct options. In the product space, force distance along these axes rather than producing three variants of one feature:

- **Feature shape**: full workflow tool versus a single sharp action versus a notification that surfaces the right moment. The same job can be served by very different surface areas.
- **UX direction**: guided/opinionated flow versus flexible/configurable surface versus invisible/automatic (the system acts so the user never touches it).
- **Build versus buy versus partner, from the user-value angle**: build owns the experience and the differentiation; buy or embed a third party gets users value sooner but commoditizes that part of the product; partner or integrate borrows another product's reach. Decide on whether this is where the product should be differentiated, not only on engineering cost.
- **Manual or concierge first**: deliver the outcome by hand or with internal tooling before building user-facing software, to learn whether the value lands at all.
- **Defer or do nothing**: name what the user does without this and whether that is actually painful now. The boring option in the product space is usually "users keep doing the workaround, and that is fine for another quarter."

The deferral option is mandatory here, not optional. Product roadmaps overbuild far more often than they underbuild; the alternative an inflated proposal omits is the one where you ship nothing and the problem turns out not to bind.

## Criteria that decide product approaches

Weight these to the situation; they are the axes the product space adds on top of the generic ones in SKILL.md:

- **User value and problem fit**: how much of the real job each approach actually completes, end to end, not how many features it has. An approach that solves 90 percent of the job for everyone usually beats one that solves 100 percent for a few.
- **Adoption and time to value**: how quickly a user gets the outcome, how much they must learn, change, or migrate to get it. An approach with a steep adoption cliff loses to a weaker one users actually reach.
- **Differentiation**: whether this approach is where the product should be distinct, or table stakes better bought, embedded, or copied. Building undifferentiated surface area is cost without moat.
- **Reversibility**: how cheaply you can withdraw or change the approach after users depend on it. User-facing commitments are stickier than code; a published workflow, an API others built on, or a pricing promise is expensive to walk back. Favor approaches that keep options open until the demand is proven.
- **Reach and segment fit**: whether the approach serves the segment that matters now, or optimizes for a segment you are not winning yet.
- **Coherence with the product**: whether it fits the mental model users already have, or adds a second model they must hold. A locally optimal feature that fragments the product loses.

Notably absent and deliberately so: raw implementation cost and operability dominate the technical decision, not this one. They enter here only as time to value and as a tie-breaker, never as the lead axis. If engineering effort is driving the product choice, you are answering the technical question, not the product one.

## Converge with a deferral line

Recommend one approach and, distinct to product decisions, state explicitly what you are deferring and why: the slice you ship now, the slice you are deliberately not building yet, and the signal that would tell you to build it. A product recommendation that does not name what it defers has not actually scoped; it has just ordered the whole backlog. The strongest rejected alternative still gets named per the core method, and if its best piece is graftable (a UX idea, a segment it served better), say so.

## Pitfalls specific to product decisions

- **The feature is the decision in disguise.** Arriving with "build feature X" and generating three flavors of X is fake divergence dressed as product thinking. Go back up to the user problem and regenerate from there.
- **Solving for the loud user, not the common job.** The most vocal request is not the most valuable approach. Weight by the job most users share, not by who asked loudest.
- **Counting features instead of completed jobs.** A richer feature set is not more user value; an approach that completes the job with less surface usually wins on adoption and coherence both.
- **Ignoring adoption cost.** The best approach on paper that requires users to change their workflow, migrate data, or learn a new model often loses to a weaker approach they reach without friction. Time to value is a first-class axis, not a footnote.
- **Building what should be bought.** Spending the team's differentiation budget on undifferentiated surface area is a product mistake, not just an engineering one. If users would not care who built it, that is a buy-or-embed candidate.
- **Skipping the cheap probe before the expensive build.** When the binding uncertainty is whether users want this at all, a concierge or manual delivery answers it for a fraction of the build. Reaching straight for the full build when demand is unproven is the product analogue of skipping the spike.
- **No deferral line.** Converging on an approach without naming what you are not building yet turns a decision aid into a license to build everything. State the deferred slice and its trigger.
