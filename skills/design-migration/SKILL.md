---
name: design-migration
description: >-
  This skill should be used when designing or writing a migration of any kind: a schema or data
  change on a live table, a major version bump of a library, framework, or language runtime, a move
  to a new platform, provider, region, cluster, or datastore engine, or an evolution of a public
  API or interface that consumers depend on. It applies when the user says "write the migration",
  "add a column without downtime", "this migration locks the table", "upgrade to the next major
  version of X safely", "migrate to a new database, provider, or region", "version this API without
  breaking consumers", or "deprecate this endpoint safely". It should not be used for the staged
  rollout and deprecation PLAN of what stages run in what order (use create-migration-plan, which
  decides the stages this skill then writes), for designing the target tables, keys, and indexes
  (use design-schema), or for writing ordinary application queries (use code-with-best-practices
  with the SQL reference).
---

## Purpose

Design and write a migration of any type so that it moves the system to its new state without breaking what is deployed, without a window where traffic is lost, and with a way back at every step. This skill owns the execution craft that is common to all migrations plus the type-specific form of each operation. The rollout sequence (which stages exist, in what order, with what deprecation window) is decided by create-migration-plan; this skill writes the migration for a given stage. The deliverable is the migration artifact (the migration file, the upgrade diff and codemod, the cutover runbook, or the versioned contract) plus the execution approach that makes it safe.

## The universal safe-migration method

Every migration, regardless of type, follows the same discipline. The mechanics differ by type; the shape does not.

1. **Parallel-change, never big-bang.** Add the new thing alongside the old, move to it, verify, then remove the old. This is expand-and-contract, and it is the spine of every safe migration: the column rename, the library upgrade, the provider move, the API version are all the same three beats (expand, migrate, contract). A migration that flips old to new in one step has removed the only state from which you can recover.
2. **Backward compatible through the transition window.** While the migration is in flight, the old and the new must both work, because deployed code, in-flight requests, cached clients, and un-upgraded consumers still use the old. The window closes only when nothing uses the old path, proven by evidence, not assumed.
3. **Reversible with a rollback at every step.** Each step has a defined way back that you wrote and tested as part of the step, not a hope. "Rollback" is usually a new forward step that undoes the change (production databases and shipped releases are forward-only), and the irreversible step is its own final beat with its rollback being the prerequisite evidence (backups verified, zero usage confirmed).
4. **Incremental rollout, not all at once.** Move a slice first and watch it: a canary, a traffic percentage, a single tenant or region. A change that is correct on the slice may still fail at full scale or full traffic, and the slice is what bounds the blast radius when it does.
5. **Idempotent and re-runnable steps.** Every step survives being interrupted and re-run: it checks whether its work is already done and resumes rather than double-applying. Migrations get killed mid-run (a lock timeout, a deploy, a network blip), and a step that corrupts on the second run is a step that cannot be operated.
6. **Shadow-and-verify (or dual-write) before cutover.** Before reads or traffic switch to the new path, run both and prove they agree: dual-write to old and new and compare, or shadow the new path against live input and diff the results. The middle state silently diverges otherwise, and the consistency check is the gate that catches it before users do.

Treat these six as standing constraints on the artifact you produce, not a checklist to mention. If a step cannot satisfy one, that is a finding to surface, not a corner to cut quietly.

## Route to the type-specific reference

Read the reference for the migration's type; each carries the concrete sequence, tools, and pitfalls for that type.

| Migration type | Read | Covers |
|---|---|---|
| Schema or data change on a live table | references/data-migrations.md | Add/alter/drop column or index, backfill at scale, lock avoidance, `CREATE INDEX CONCURRENTLY`, ORM migration files (Prisma, Drizzle, Kysely, Django, Alembic, Rails, golang-migrate), the transaction-wrapping gotcha |
| Major version bump of a library, framework, or runtime | references/dependency-upgrades.md | Reading changelogs and breaking changes, codemods, compatibility shims, incremental adoption, lockfile and test-gate discipline |
| Move between platforms, providers, regions, clusters, or datastore engines | references/infrastructure-migrations.md | Running old and new in parallel, traffic cutover (DNS or load-balancer weight), data sync, verification, decommissioning the old |
| Evolving a public API or consumer-facing interface | references/api-contract-migrations.md | Additive vs breaking changes, versioning, deprecation windows and signals, consumer migration, removing the old contract last |

If the task spans types (a provider move that is also a datastore-engine change, an API version that needs a schema change behind it), read each relevant reference and sequence the work so each piece independently satisfies the six.

## Worked example: a column add-backfill-drop, the universal shape in one type

This database example illustrates expand-and-contract concretely; the same three beats generalize to every type above. Replacing the `email` column's storage with a normalized form:

**Expand.** Add the new column, nullable, in its own migration. Nullable add takes a brief metadata lock only, so it is safe on a live table; a `NOT NULL` add would rewrite the whole table under lock.

```sql
-- Migration 1 (expand): add the new column alongside the old. No backfill here;
-- DDL and DML stay in separate migrations so neither holds a long lock.
ALTER TABLE users ADD COLUMN normalized_email TEXT;
```

**Migrate.** Backfill in bounded, independently committing batches so no single transaction holds a lock, and make it resumable (`WHERE normalized_email IS NULL`) so an interrupted run picks up where it stopped. Dual-write the new column from application code during this window so rows written mid-backfill are correct. Run the consistency check (old and new agree) before switching reads.

```sql
-- Migration 2 (migrate): backfill in batches. Each batch commits on its own; SKIP
-- LOCKED steps around rows live writes hold; the IS NULL filter makes it re-runnable.
DO $$
DECLARE
  batch_size INT := 10000;  -- keep each batch well under lock_timeout
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

**Contract.** Only after reads have switched to the new column and no deployed code references the old one, drop the old column in a final migration. Dropping before code stops using it is an instant incident; this beat comes last and is the irreversible one.

```sql
-- Migration 3 (contract): drop the old column. Runs only after every reference to
-- `email` is gone from deployed code and reads use normalized_email.
ALTER TABLE users DROP COLUMN email;
```

The lock-safety of each operation, the ORM-specific authoring, and the online schema change tools for tables too large for in-place DDL are in references/data-migrations.md.

## Gotchas

- **Big-bang is the default temptation, and it is always wrong here.** A single PR that swaps the library, a one-shot rename, a hard provider cutover all feel simpler because they skip the transition window. They skip the recovery state with it. Every type has a parallel-change form; use it.
- **The transition window needs a consistency check, not optimism.** Whenever old and new run in parallel (dual-write, shadow traffic, both API versions live), writes or behavior can diverge silently. The migration includes the query, diff, or job that proves they agree before the old path retires.
- **A "rollback" that was never run is not a rollback.** Production databases and shipped releases are forward-only; the way back is a forward step you wrote and tested against the changed state. An untested down migration or an unrehearsed traffic-shift-back is a plan that does not exist.
- **Removal requires evidence of zero usage, not absence of complaints.** The contract beat (drop the column, delete the old cluster, remove the API version) runs only on metrics, logs, or dependency scans showing nothing uses the old path over a representative window. Silence is not evidence.
- **Scale and traffic are the variables dev does not have.** A migration instant on 100 dev rows locks for hours on 10M; an upgrade green in CI breaks under production load; a cutover fine at 1% melts at 100%. Test against production-sized data and roll out incrementally for exactly this reason.
