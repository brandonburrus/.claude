---
name: create-migration-plan
description: >-
  Use this skill when planning a migration or deprecation: schema changes on
  live data, API version transitions, library or framework upgrades,
  replacing a system or service, renaming a column or endpoint safely, or
  sunsetting anything with consumers. Use when the user says "plan the
  migration", "upgrade to the next major version", "move from X to Y",
  "deprecate this", "zero-downtime change", or "how do we get rid of this
  safely". The deliverable is a staged plan, not executed changes. Do not use
  for designing a schema from scratch (use design-data-schema), for executing
  the planned work (use create-code-plan), or for release mechanics (use
  prepare-for-deploy).
---

## Purpose

Produce a migration plan that is a sequence of safe states, not a before-and-after diff: every stage leaves the system deployed, working, and abandonable, and the irreversible steps come last. The plan exists because migrations fail in the gap between states, not at the endpoints; a plan that only describes the destination has not planned the migration. Deliverable: a staged plan with per-stage verification and rollback, ready to hand to decompose-into-tasks for tickets or create-code-plan for execution detail.

## Workflow

### 1. Scope: what moves, who depends on it, what replaces it

- Quantify the consumers with evidence (call sites, traffic metrics, dependent packages), not assumptions. Hyrum's Law sets the bar: with enough users, every observable behavior is depended on, including bugs and timing quirks, so "nobody uses that" requires data.
- Confirm the replacement exists and covers the depended-upon behavior before any deprecation is announced. Deprecating without a working alternative strands consumers in permanent limbo.
- Weigh migration cost against the standing cost of not migrating; if keeping the old thing for two more years is cheaper than moving every consumer, that is a finding, not a failure.

### 2. Pick the strategy

| Strategy | Use for | Shape | Rollback story |
|---|---|---|---|
| Expand-contract | Schema and contract changes on live systems | Add new alongside old, dual-write, switch reads, retire old | New forward step; old path still present until contract |
| Strangler | Replacing a system or service | Route traffic incrementally (canary share first) to the new system | Shift traffic back; old system still running |
| Adapter | Swapping an implementation behind a stable interface | Old interface delegates to new internals | Restore old delegation |
| Feature-flag cutover | Per-consumer or per-tenant moves | Flag switches each consumer independently | Flip the flag |

Never rename or replace in place on anything live; a direct rename is an expand-contract plan compressed into one step with the safety removed.

### 3. Stage the plan

Each stage must be independently deployable, verifiable, and either reversible or explicitly marked irreversible. Ordering laws that do not bend:

- Code stops referencing a thing in one stage; the thing is removed in a later stage. Dropping a column or endpoint while any deployed code still touches it is an instant incident.
- Destructive steps (drops, deletes, irreversible transforms) are their own final stage, never bundled with anything else.
- Schema changes and data backfills are separate stages: mixing DDL and DML produces long transactions, long locks, and unrollbackable middles.
- Backfills run in batches with progress tracking, because the update that is instant on dev data locks the table for hours at production size. Test stages against production-sized data for the same reason.

### 4. Plan the deprecation window (when consumers are external to the change)

- Default to advisory (migrate on your own timeline); go compulsory (hard deadline) only when security, unsustainable maintenance, or a blocking dependency justifies forcing it.
- The announcement names the replacement, the date or "no hard deadline", the reason, and a concrete migration guide.
- The Churn Rule: the owner of the deprecated thing migrates the consumers or ships tooling (codemods, scripts, compat shims) that makes migration near-free. Announcing and waiting is not a plan; it produces zombie deprecations that confuse everyone for years.

### 5. Rollback and abort, per stage

- Production databases are forward-only: "rollback" means a new forward migration that undoes the change, written and tested as part of the stage, not reverting the migration file.
- Define abort criteria per stage (lock contention observed, error budget burned, consistency check fails) and what abort means there: stop and hold is usually safe precisely because every stage is a working state.
- For the irreversible stage, the rollback plan is the prerequisite evidence: backups verified, zero-usage confirmed, sign-off recorded.

### 6. Verify sunset before removal

Removal requires evidence of zero active usage (metrics, logs, dependency scans over a representative window), not absence of complaints. Remove code, tests, docs, config, and the deprecation notices themselves together; a notice for a removed thing is noise that erodes trust in the remaining notices.

## Gotchas

- **Schema-change traps are version-specific.** NOT NULL without a default rewrites the table under lock on older engines; index builds block writes unless created concurrently; concurrent index creation cannot run inside a transaction, which most migration tools wrap by default. The plan names these hazards per step instead of assuming the tool handles them.
- **Deployed migrations are immutable.** Editing a migration file that has run anywhere creates environment drift that surfaces as unexplainable differences months later; fixes are new migrations.
- **Dual-write windows need a consistency check.** Expand-contract's middle stage silently corrupts if writes diverge; the plan includes the comparison query or job that proves old and new agree before reads switch.
- **The library-upgrade variant still stages.** Major-version bumps follow the same shape: compat layer or codemod first (expand), incremental adoption with both patterns allowed (migrate), removal of the old pattern and shims (contract). A big-bang upgrade PR is the rename-in-place mistake at repo scale.
- **Plans decay; pin the trigger.** A migration plan written today against today's traffic and schema needs its assumptions rechecked if execution starts months later; date the plan and list the assumptions that must still hold.
