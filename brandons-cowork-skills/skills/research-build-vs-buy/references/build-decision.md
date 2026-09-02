# Build-decision depth

Read this when framing and deciding build vs buy vs partner vs defer from the user-value angle. It carries the opportunity framing, the criteria that decide the direction, the four product risks, and the experiment discipline that gates a lean-to-build call.

## Reframe the decision as an opportunity, not a feature

Restate the fork as a desired outcome and the user opportunity beneath it. Borrowing the opportunity-solution-tree framing: a measurable desired outcome sits at the top (for example "more users reach their first successful result"); under it are opportunities, the user needs and pains framed from the user's view ("I cannot tell whether my account is healthy"); candidate directions (build, buy, partner) hang off each opportunity; and experiments validate them. Name the job the user is hiring this for, the moment of need, and what they do today instead. If you cannot state the opportunity without naming a feature or a named product, the decision is not yet framed.

## Criteria that decide the direction

Weight these to the situation; they lead the build-vs-buy call and outrank raw engineering cost:

- **User value and problem fit**: how much of the real job each direction actually completes, end to end. An approach that solves 90 percent of the job for everyone usually beats one that solves 100 percent for a few.
- **Adoption and time to value**: how quickly a user gets the outcome, how much they must learn, change, or migrate. Buy and embed usually win here; a build with a steep adoption cliff loses to a weaker option users actually reach.
- **Differentiation**: whether this is where the product should be distinct (build), or table stakes better bought, embedded, or partnered for. Building undifferentiated surface area is cost without a moat.
- **Reversibility**: how cheaply you can withdraw or change the direction after users depend on it. A published workflow, an API others built on, or a vendor lock-in is expensive to walk back. Favor directions that keep options open until demand is proven.

Raw implementation cost and operability enter here only as time to value and as a tie-breaker, never as the lead axis. If engineering effort is driving the choice, you are answering a technical question, not the build-vs-buy one.

## Find the riskiest assumption before committing to build

A build direction that scores well on paper still rests on assumptions that, if wrong, sink it. Before committing, sort the assumptions by risk across the four product risks:

- **Value**: will users actually want this and keep using it? Usually the riskiest for a new build.
- **Usability**: can users figure it out and reach the outcome without undue friction?
- **Viability**: can the business sustain, monetize, support, and comply with it?
- **Feasibility**: can it be built with what the team and technology can do now?

The riskiest assumption is the one with the highest uncertainty and the highest cost if false; that is the one to test first, not the one easiest to test. A build whose value assumption is unproven is a bet, not a decision.

## Design the cheapest experiment for the riskiest assumption

Once the riskiest assumption is named, design the smallest experiment that would move your confidence, and run it before the expensive build. State it as a falsifiable hypothesis ("at least X percent of segment Y will do Z"), with the method, the metric, and the success threshold. Favor cheap probes that capture real behavior over opinion: a concierge or manual delivery, a landing page or waitlist, a fake-door click test, a pre-order or other skin-in-the-game commitment. Measure what users do, not what they say. The experiment's job is evidence, not a shippable product; pick the one that retires the most risk per hour spent.

## Converge with a deferral line

Recommend one direction and state explicitly what you are deferring: the slice you ship now, the slice you are deliberately not building yet, the signal that would tell you to build it, and the experiment result that gates committing when the riskiest assumption is still open. A recommendation that does not name what it defers has not scoped; it has ordered the whole backlog. Name the strongest rejected direction per the core method, and if its best piece is graftable (a UX idea, a segment it served better), say so.
