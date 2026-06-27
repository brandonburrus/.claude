Read this when the open question is which technical approach or mechanism to use: the architecture, the pattern, the shape of the system, not which named tool fills a slot. This adds the divergence generators, weighted axes, and pitfalls particular to architecture and mechanism choices, on top of the approach method in SKILL.md. Once the shape is fixed and the open question becomes which concrete library, framework, database, or service implements it, switch to the tool-selection workflow in SKILL.md; do not turn a mechanism decision into a vendor bake-off here.

## Frame around the mechanism and its blast radius

Before diverging, state what the approach must do, the load and failure conditions it runs under, and what it touches when it breaks. A technical fork is decided as much by the failure and scale envelope as by the happy path: "process the upload" is not framed until you know the volume, the latency budget, what is downstream, and what happens when it fails halfway. Name the part of the system that pays the price if this choice is wrong; that blast radius is the axis that usually dominates.

## Divergence generators for technical approaches

Force distance along the structural axes rather than producing three tunings of one design:

- **Coupling posture**: synchronous in-request versus asynchronous queue or event versus scheduled batch. These differ in latency, failure handling, and observability.
- **Boundary**: keep it in the existing process or monolith versus extract a service versus push it to the edge or the client. Each moves a different cost (deployment, network, consistency) onto a different part of the system.
- **Consistency model**: strong/transactional versus eventual versus read-repair. The choice constrains everything downstream and is expensive to reverse once data accumulates under it.
- **State and computation placement**: compute on write versus on read, cache versus recompute, materialize versus derive.
- **Layer of intervention**: application code versus configuration versus infrastructure versus the data model. The lowest layer that solves it is usually cheapest to own.
- **Do nothing or defer the hard part**: the boring option is often the existing approach scaled one notch (a bigger instance, an index, a cache), not a new architecture. New architecture is overchosen relative to tuning what exists.

## Criteria that decide technical approaches

Weight these to the situation; they are the axes the technical space adds on top of the generic ones in SKILL.md:

- **Complexity and cognitive load**: how much the approach adds to what the team must hold in their heads to operate and change the system. The simplest approach that meets the envelope wins.
- **Operability**: how it is deployed, observed, debugged, and recovered when it fails at 3am. Favor approaches whose failure modes are visible and whose recovery is a known procedure.
- **Performance and scale headroom**: behavior at the real load and at the next order of magnitude, including tail latency and behavior under overload, not just the median on the happy path.
- **Blast radius**: how much breaks when this fails, and whether the failure is contained or cascades. A choice that fails into degraded-but-up beats one that fails into a total outage at equal happy-path quality.
- **Migration and reversibility cost**: what it takes to get here from the current state, and to back out if it is wrong. A data-model or consistency choice with an expensive migration and no exit is a near-irreversible door; prefer the reversible approach when the call is close.
- **Fit with existing patterns**: whether it matches how the system already works or introduces a second way of doing the same thing. A novel mechanism in a consistent system carries an ongoing tax.

The lead axes here are operability, blast radius, and reversibility, not user-facing value. When you converge, make the reversibility and migration call explicit: how you get there from here, whether the door swings both ways, and what the rollback is. State the load or failure assumption the choice rests on, because the technical call most often flips when the scale or failure envelope turns out different from framed.

## Pitfalls specific to technical decisions

- **Resume-driven architecture.** Choosing the interesting approach over the boring one that fits the envelope. The novel mechanism must earn its complexity against the requirement, not against curiosity.
- **Scaling for load you do not have.** Building the distributed, sharded, eventually consistent design for traffic a single indexed table would serve for years. Size to the real envelope plus one notch.
- **Ignoring operability until it pages someone.** An approach scored only on happy-path performance hides its real cost, the debugging and recovery story. Weight observability and rollback as first-class axes.
- **Treating an irreversible door as reversible.** Consistency and data-model choices accumulate state and become expensive to change. Mark these and weight reversibility heavily; the close call breaks toward the approach you can back out of.
- **Underweighting blast radius.** Two approaches with equal happy-path quality are not equal if one fails contained and the other cascades. Score what breaks when it breaks.
- **Turning the mechanism choice into a vendor bake-off.** Comparing named tools before the approach is settled mixes two decisions. Pick the shape here, then run the tool-selection workflow in SKILL.md.
- **Deliberating an empirical tie on paper.** When two approaches are close and the question is whether one actually performs or holds up, spike and measure rather than analyze further.
