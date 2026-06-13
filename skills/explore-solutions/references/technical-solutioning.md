Read this when the decision is which technical approach or mechanism to use: the architecture, the pattern, the shape of the system, not which named tool fills a slot. This specializes the core method (diverge, score against weighted axes, name the rejected alternatives, converge) for the technical space. The shared method lives in SKILL.md; this file adds only the axes, generators, and pitfalls particular to architecture and mechanism choices.

This decides the approach: sync versus async, monolith versus service, which pattern, where the work runs. Once the approach is chosen and the open question becomes which specific library, framework, database, or managed service implements it, that is research-solutioning, not this file. Do not turn a mechanism decision into a vendor bake-off here; pick the shape first, then hand the named-tool comparison to research-solutioning.

## Frame the decision around the mechanism and its blast radius

Before diverging, state what the approach must do, the load and failure conditions it runs under, and what it touches when it breaks. A technical fork is decided as much by the failure and scale envelope as by the happy path: "process the upload" is not framed until you know the volume, the latency budget, what is downstream, and what happens when it fails halfway. Name the part of the system that pays the price if this choice is wrong, because that blast radius is the axis that usually dominates.

## Divergence generators for technical approaches

The core method demands genuinely distinct options. In the technical space, force distance along the structural axes rather than producing three tunings of one design:

- **Coupling posture**: synchronous in-request versus asynchronous queue or event versus scheduled batch. These differ in latency, failure handling, and observability, not just in timing.
- **Boundary**: keep it in the existing process or monolith versus extract a service versus push it to the edge or the client. Each moves a different cost (deployment, network, consistency) onto a different part of the system.
- **Consistency model**: strong/transactional versus eventual versus read-repair. The choice constrains everything downstream and is expensive to reverse once data accumulates under it.
- **State and computation placement**: compute on write versus on read, cache versus recompute, materialize versus derive. The same result has very different operability depending on where the work lives.
- **Layer of intervention**: solve it in application code versus configuration versus infrastructure versus the data model. The lowest layer that solves it is usually the cheapest to own.
- **Do nothing or defer the hard part**: the boring option here is often the existing approach scaled one notch (a bigger instance, an index, a cache) rather than a new architecture. Put it on the board; new architecture is overchosen relative to tuning what exists.

## Criteria that decide technical approaches

Weight these to the situation; they are the axes the technical space adds on top of the generic ones in SKILL.md:

- **Complexity and cognitive load**: how much the approach adds to what the team must hold in their heads to operate and change the system. The simplest approach that meets the envelope wins; accidental complexity is a recurring cost, not a one-time one.
- **Operability**: how it is deployed, observed, debugged, and recovered when it fails at 3am. An approach that works but cannot be seen into or rolled back is a liability. Favor approaches whose failure modes are visible and whose recovery is a known procedure.
- **Performance and scale headroom**: behavior at the real load and at the next order of magnitude, including tail latency and the failure behavior under overload, not just the median on the happy path.
- **Blast radius**: how much breaks when this fails, and whether the failure is contained or cascades. A choice that fails into a degraded-but-up state beats one that fails into a total outage, even at equal happy-path quality.
- **Migration and reversibility cost**: what it takes to get from the current state to this, and to back out if it is wrong. A data-model or consistency choice with an expensive migration and no exit is a near-irreversible door; weight it accordingly and prefer the reversible approach when the call is close.
- **Fit with existing patterns**: whether the approach matches how the system already works or introduces a second way of doing the same thing. A novel mechanism in an otherwise consistent system carries an ongoing tax even when it is locally better.

Notably the lead axes here are operability, blast radius, and reversibility, not user-facing value (that drives the product decision). If the choice is being made on user adoption or differentiation, you are answering the product question, not the technical one.

## Converge with the reversibility and migration call stated

Recommend one approach and, distinct to technical decisions, make the reversibility and migration cost explicit in the recommendation: how you get there from here, whether the door swings both ways, and what the rollback is if it does not. State the load or failure assumption the choice rests on, because the technical call most often flips when the scale or failure envelope turns out different from what was framed. If the deciding question is empirical (does it actually hold at this load, does the latency budget survive contact with production), recommend a time-boxed spike to measure rather than deliberating further on paper. If the approach is chosen and the remaining open question is which concrete tool implements it, hand that to research-solutioning rather than answering it here.

## Pitfalls specific to technical decisions

- **Resume-driven architecture.** Choosing the interesting approach over the boring one that fits the envelope. The novel mechanism must earn its complexity against the requirement, not against curiosity.
- **Scaling for load you do not have.** Building the distributed, sharded, eventually consistent design for traffic that a single indexed table would serve for years. Size the approach to the real envelope plus one notch, not to an imagined one.
- **Ignoring operability until it pages someone.** An approach scored only on happy-path performance hides its real cost, which is the debugging and recovery story. Weight observability and rollback as first-class axes, because that is where the choice is actually lived with.
- **Treating an irreversible door as reversible.** Consistency models and data-model choices accumulate state under them and become expensive to change. Mark these and weight reversibility heavily; the close call should break toward the approach you can back out of.
- **Underweighting blast radius.** Two approaches with equal happy-path quality are not equal if one fails contained and the other cascades. Score what breaks when it breaks, not only what happens when it works.
- **Turning the mechanism choice into a vendor bake-off.** Comparing named tools before the approach is settled mixes two decisions. Pick the shape here; defer the specific-tool comparison to research-solutioning.
- **Deliberating an empirical tie on paper.** When two approaches are close and the question is whether one actually performs or holds up, more analysis is procrastination. Spike and measure.
