---
name: orchestrate-delivery
description: >-
  Use this skill to take a substantial product idea all the way to production in
  users' hands, sequencing the right skill at each stage and stopping at the
  evidence gates between them. Use when the user says "take this idea to
  production", "build this product end to end", "what's the path from idea to
  launch", "ship this new product/feature start to finish", "guide me through the
  whole build", "where do we even start with this", or describes a greenfield
  product or a large feature with no plan yet. Do not use for executing an
  already-approved code plan (use execute-code-plan), for a single well-scoped
  change where one stage skill suffices (invoke that skill directly), or for the
  build pipeline alone with the idea already specified and designed (start at the
  plan stage).
---

## Purpose

Drive a substantial effort across the whole arc from raw idea to a measured production launch, invoking the right library skill at each stage and refusing to advance past a stage until its gate is met. The deliverable is forward progress through the arc with the gates honored, not any single artifact. This skill is a router and a runbook; it never reimplements a stage's methodology, it hands off to the skill that owns it. Its entire value is sequencing and the gates: the failures it exists to prevent are building an unvalidated idea, coding an unwritten spec, and shipping unverified work.

The arc loops; it is not a one-way pipeline. A post-launch measurement feeds the next cycle's problem statement, and a gate failure sends you back, not forward.

## The arc

- [ ] 0. Triage: does this warrant the full arc, or skip to a stage?
- [ ] 1. Understand and validate the idea
- [ ] 2. Specify what to build and why
- [ ] 3. Design how to build it
- [ ] 4. Plan and build it
- [ ] 5. Review and verify it
- [ ] 6. Ship it
- [ ] 7. Measure it, then loop

### 0. Triage

Size the work first. A bug fix or a small, well-understood change does not need this skill; route it straight to the stage that fits (`fix`, a single `design-*` skill, or `create-code-plan`). Reserve the full arc for greenfield products and large features where skipping validation, spec, or verification is a real risk. State which stage you are entering and why.

### 1. Understand and validate

Skill(s): `clarify-ambiguity` if the idea is vague, then `validate-idea`. **Gate:** a Go verdict (or an explicit, recorded decision to proceed at risk). Do not write a spec for an idea no one has shown demand for; an unvalidated idea is the most expensive thing to carry forward.

### 2. Specify

Skill(s): `research-market` if the market or competition is unknown, then `write-product-spec`. **Gate:** a user-approved PRD with measurable success metrics and a named activation moment. The spec is the contract the rest of the arc is checked against.

### 3. Design

Skill(s): `write-tech-spec`, plus the relevant `design-*` skills (`design-api`, `design-data-schema`, `design-ui`, `design-cli`, `design-mcp`, `design-llm-agent`, `design-observability`, ...). Validate with `design-contract-validator` (can it be built without guessing) and, for large designs, `tech-spec-reviewer`. **Gate:** the design is complete and implementable; interfaces, states, and error semantics are pinned down.

### 4. Plan and build

Skill(s): `create-code-plan`, then `plan-reviewer` for large or risky plans, then `execute-code-plan` (which runs the implement/verify agent pipeline; parallelize independent tasks, worktree-isolate ones that would collide). **Gate:** every task implemented and verified by `completion-verifier`; the work is wired in, not just present and green.

### 5. Review and verify

Skill(s): `review-pull-request`, `harden-security` or the `security-reviewer` agent for anything touching untrusted input or auth, and `manual-tester` (`validate-web` / `validate-api`) to confirm real user-visible behavior. **Gate:** review is clean and behavior is confirmed by actually running it; a green automated suite is necessary but never sufficient.

### 6. Ship

Skill(s): `prepare-for-deploy` (plus `design-cicd` if no pipeline exists). **Gate:** a rollback plan exists and the release is staged. Never auto-deploy to production; releases get a rollback plan and a human go.

### 7. Measure and loop

Skill(s): `analyze-product-metrics` against the spec's success metrics; `respond-to-incident` and `write-post-mortem` if something breaks. **Gate (to close the cycle):** the launch is measured against the metrics the spec committed to. Feed the finding back: a confirmed bottleneck or a missed metric becomes the next cycle's stage 1 or 2 input.

## Gotchas

- **Router, not doer.** Do not inline a stage's work; invoke the skill that owns it. Reimplementing `write-product-spec` or `create-code-plan` here duplicates methodology and guarantees drift. This skill's job is to know what comes next and what gate guards it.
- **The gates are the point.** Advancing past a failed gate is the exact failure mode this skill prevents. A skipped validation surfaces as a built-but-unwanted product; a skipped spec as a rebuild; a skipped verify as a production incident. When a gate fails, go back, do not push forward.
- **It loops.** Treating the arc as one-way and "finishing" at ship misses the half of the goal that is "in users' hands and working." Stage 7 is not optional, and its output re-enters at stage 1 or 2.
- **Stages collapse for smaller work.** Not every effort needs all eight steps; the triage in step 0 is where you decide how much arc applies. The skill scales down by skipping stages, never by skipping gates on the stages it does run.
