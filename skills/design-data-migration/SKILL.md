---
name: design-data-migration
description: >-
  Use this skill when writing or running a database migration: adding, altering,
  or dropping a column or index on a live table, backfilling or transforming data
  at scale, making a schema change zero-downtime, or authoring migration files in
  Prisma, Drizzle, Kysely, Django, Alembic, Rails, or golang-migrate. Use when the
  user says "write the migration", "add a column without downtime", "this
  migration locks the table", "create the index concurrently", "backfill this
  column", or "the migration tool wraps it in a transaction". Do not use for
  planning the staged rollout and deprecation sequence (use create-migration-plan,
  which decides the stages this skill then writes), designing the target tables,
  keys, and indexes (use design-data-schema), or writing ordinary application
  queries (use code-with-best-practices with the SQL reference).
---

## Purpose

Write each migration so it changes the schema or data without locking live traffic or breaking deployed code. This skill owns the execution craft: the lock-safe form of each operation, the batched backfill, and the ORM-specific authoring that the migration tool gets wrong by default. The rollout sequence (which stages exist, in what order, with what deprecation window) is decided by create-migration-plan; this skill writes the migration for a given stage. The deliverable is the migration file or files plus the execution approach (locking strategy, online-change tool if needed, verification against production-sized data).

## The five non-negotiables

1. **Every change is a migration.** Never alter a production database by hand; the migration file is the audit trail and the only thing that reproduces across environments.
2. **Forward-only in production.** A "rollback" is a new forward migration that undoes the change, written and tested as part of the work, not a reverted migration file. Deployed migrations are immutable; editing one that has run anywhere creates drift that surfaces months later as unexplainable differences.
3. **Schema and data are separate migrations.** Mixing DDL and DML produces long transactions, long locks, and a middle state that cannot be rolled back. Add the column in one migration; backfill it in the next.
4. **Test against production-sized data.** A migration that is instant on 100 dev rows can lock the table for hours on 10M production rows. The row count is the variable that matters, and dev never has it.
5. **Lock for the shortest possible time.** A migration that takes a long lock does not just slow itself; it queues every query behind it. Prefer the operation form that takes no lock or a brief one, and bound the wait with `lock_timeout` so a blocked migration fails instead of freezing the application.

## Lock-safety by operation

The same logical change has a safe and an unsafe form. Default to the safe one; the unsafe one rewrites or blocks the table.

| Operation | Unsafe (locks/rewrites) | Safe form |
|---|---|---|
| Add column, nullable | (already safe) | `ADD COLUMN x TEXT` takes a brief lock only |
| Add column with default | Full rewrite on older engines | Postgres 11+ / MySQL 8: instant metadata-only default; older engines: add nullable, backfill, then set default |
| Add NOT NULL | `ADD COLUMN x NOT NULL` rewrites and locks | Add nullable, backfill, add a `CHECK (x IS NOT NULL) NOT VALID` then `VALIDATE CONSTRAINT` (validate takes a weak lock), or set NOT NULL after the validated check |
| Add index | `CREATE INDEX` blocks writes for the whole build | `CREATE INDEX CONCURRENTLY` (Postgres) / `ALGORITHM=INPLACE, LOCK=NONE` (MySQL); cannot run inside a transaction |
| Drop column | Dropping while deployed code references it errors live | Remove all code references and deploy first, then drop in a later migration |
| Rename column | In-place rename breaks code mid-deploy | Expand-contract: add new, dual-write, backfill, switch reads, drop old (the sequence is create-migration-plan's; each step is a migration here) |
| Change column type | Often a full rewrite under lock | Add a new column of the target type, backfill, switch, drop old |

## Backfill as its own batched migration

A backfill is a data migration, separate from the DDL, run in bounded batches so it never holds one long transaction or lock. Track progress and make it resumable; the update that is instant on dev locks the table at production size.

```sql
-- Backfill normalized_email in batches; each batch commits independently so no
-- single long transaction holds a lock, and SKIP LOCKED avoids fighting live writes.
DO $$
DECLARE
  batch_size INT := 10000;  -- tune to keep each batch well under any lock_timeout
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
    RAISE NOTICE 'backfilled % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

In an ORM, the same shape: select a batch by primary key, update it, commit, repeat until empty (Django `bulk_update` in a loop, a raw batched UPDATE elsewhere).

## ORM authoring: where the tool's default is wrong

Most ORMs wrap each migration in a transaction by default, which is exactly what a concurrent index or a long backfill must not run inside. Override per tool:

| Tool | The footgun and the fix |
|---|---|
| Prisma | Cannot express `CONCURRENTLY`; create the migration with `migrate dev --create-only` and write the raw SQL by hand. Apply with `migrate deploy` in prod, never `migrate dev`/`reset` |
| Drizzle | `generate` then `migrate`; `push` is dev-only (no migration file). Hand-write raw SQL for concurrent indexes |
| Kysely | Type migrations as `Kysely<any>`, never your live DB interface: migrations are frozen in time and must not depend on current schema types |
| Django | `RunPython` for data, separate from schema ops; set `atomic = False` on the Migration for `AddIndexConcurrently`; use `SeparateDatabaseAndState` to drop a field from the model without the DB `DROP COLUMN` yet |
| Alembic | `op.create_index(..., postgresql_concurrently=True)` requires the migration run outside a transaction (autocommit block); Alembic wraps by default |
| Rails | `disable_ddl_transaction!` in the migration for `add_index algorithm: :concurrently`; the strong_migrations gem flags the unsafe forms |
| golang-migrate | Author explicit `.up.sql` / `.down.sql` pairs; the down file is the tested reversal, not an afterthought |

## When the native DDL still locks: online schema change tools

For a large table where even the safe DDL form takes an unacceptable lock (common on big MySQL tables, and some Postgres rewrites), use an online schema change tool that builds a shadow copy and swaps it: `gh-ost` or `pt-online-schema-change` (Percona) for MySQL, `pg_repack` for Postgres bloat and some rewrites. They trade a slower, copy-based migration for no long lock. Reach for them only when the in-place safe form is proven too slow against production-sized data, not by default.

## Verify before shipping

- Run the migration against a copy of production-sized data and measure how long it holds a lock (`pg_stat_activity` / `SHOW PROCESSLIST` during the run, or `lock_timeout` set low so an unsafe lock fails the test instead of hanging it).
- For an expand-contract dual-write window, run the consistency check (a query or job comparing old and new) and confirm they agree before switching reads; the middle state silently corrupts if writes diverge.
- Confirm the reversal works: run the down migration (or the forward-undo) against the changed copy and verify the schema and data return to a working state.

## Gotchas

- **`CONCURRENTLY` cannot run inside a transaction, and your migration tool opens one by default.** This is the single most common failure: the tool wraps the migration, Postgres rejects the concurrent index, and the migration dies half-applied. Disable the per-migration transaction (the ORM-specific switch above) for any concurrent operation.
- **A failed `CREATE INDEX CONCURRENTLY` leaves an INVALID index behind.** It is not cleaned up automatically and it is not used by the planner; the next attempt must `DROP INDEX` it first (or `CREATE ... IF NOT EXISTS` will not save you, because the invalid one exists). Check `pg_index.indisvalid` after a failure.
- **A migration waiting on a lock blocks everything behind it.** An `ALTER` that cannot get its lock sits in the lock queue, and every query needing that table queues behind the `ALTER`, so a "quick" change becomes a site-wide stall. Set a low `lock_timeout` and retry, so the migration yields instead of freezing the application.
- **NOT NULL on an existing column is a two-step, not a flag flip.** Adding the constraint directly scans and locks the whole table. Add a `NOT VALID` check constraint (instant, no scan), then `VALIDATE CONSTRAINT` (scans under a weak lock that allows writes).
- **Dropping a column before the code stops using it is an instant incident.** Order is law: remove every reference and deploy, then drop in a later migration. The reverse order breaks production the moment the migration lands.
- **The down migration is real code and gets tested.** An untested `down` that has never run is a rollback plan that does not exist; production databases are forward-only, so the reversal is a forward migration you wrote and ran against the changed state, not a hope.
