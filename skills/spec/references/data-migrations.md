# Data migrations: schema and data changes on live tables

Read this for the execution craft of changing a schema or transforming data on a table that is taking live traffic: the lock-safe form of each operation, the batched backfill, the ORM-specific authoring the migration tool gets wrong by default, and the online change tools for tables too large for in-place DDL.

## Schema and data are separate migrations

Mixing DDL and DML produces long transactions, long locks, and a middle state that cannot be rolled back. Add the column in one migration; backfill it in the next. This is the expand and migrate split from the universal method, made concrete.

## Lock-safety by operation

The same logical change has a safe and an unsafe form. Default to the safe one; the unsafe one rewrites or blocks the table behind a lock, queuing every query behind it.

| Operation | Unsafe (locks/rewrites) | Safe form |
|---|---|---|
| Add column, nullable | (already safe) | `ADD COLUMN x TEXT` takes a brief metadata lock only |
| Add column with default | Full rewrite on older engines | Postgres 11+ / MySQL 8: instant metadata-only default; older engines: add nullable, backfill, then set default |
| Add NOT NULL | `ADD COLUMN x NOT NULL` rewrites and locks | Add nullable, backfill, add `CHECK (x IS NOT NULL) NOT VALID` then `VALIDATE CONSTRAINT` (validate takes a weak lock), then set NOT NULL |
| Add index | `CREATE INDEX` blocks writes for the whole build | `CREATE INDEX CONCURRENTLY` (Postgres) / `ALGORITHM=INPLACE, LOCK=NONE` (MySQL); cannot run inside a transaction |
| Drop column | Dropping while deployed code references it errors live | Remove all code references and deploy first, then drop in a later migration |
| Rename column | In-place rename breaks code mid-deploy | Expand-contract: add new, dual-write, backfill, switch reads, drop old |
| Change column type | Often a full rewrite under lock | Add a new column of the target type, backfill, switch reads, drop old |

## Backfill as its own batched migration

A backfill is a data migration, separate from the DDL, run in bounded batches so it never holds one long transaction or lock. Track progress and make it resumable; the update that is instant on dev locks the table at production size. In an ORM the shape is identical: select a batch by primary key, update it, commit, repeat until empty (Django `bulk_update` in a loop, a raw batched UPDATE elsewhere). See the worked example in SKILL.md for the canonical batched-loop SQL.

## ORM authoring: where the tool's default is wrong

Most ORMs wrap each migration in a transaction by default, which is exactly what a concurrent index or a long backfill must not run inside. Override per tool:

| Tool | The footgun and the fix |
|---|---|
| Prisma | Cannot express `CONCURRENTLY`; create with `migrate dev --create-only` and write the raw SQL by hand. Apply with `migrate deploy` in prod, never `migrate dev` / `reset` |
| Drizzle | `generate` then `migrate`; `push` is dev-only (no migration file). Hand-write raw SQL for concurrent indexes |
| Kysely | Type migrations as `Kysely<any>`, never your live DB interface: migrations are frozen in time and must not depend on current schema types |
| Django | `RunPython` for data, separate from schema ops; set `atomic = False` on the Migration for `AddIndexConcurrently`; use `SeparateDatabaseAndState` to drop a field from the model without the DB `DROP COLUMN` yet |
| Alembic | `op.create_index(..., postgresql_concurrently=True)` requires the migration run outside a transaction (autocommit block); Alembic wraps by default |
| Rails | `disable_ddl_transaction!` in the migration for `add_index algorithm: :concurrently`; the strong_migrations gem flags the unsafe forms |
| golang-migrate | Author explicit `.up.sql` / `.down.sql` pairs; the down file is the tested reversal, not an afterthought |

## When the native DDL still locks: online schema change tools

For a large table where even the safe DDL form takes an unacceptable lock (common on big MySQL tables, and some Postgres rewrites), use an online schema change tool that builds a shadow copy and swaps it: `gh-ost` or `pt-online-schema-change` (Percona) for MySQL, `pg_repack` for Postgres bloat and some rewrites. They trade a slower, copy-based migration for no long lock. Reach for them only when the in-place safe form is proven too slow against production-sized data, not by default.

## Pitfalls

- **`CONCURRENTLY` cannot run inside a transaction, and your migration tool opens one by default.** The single most common failure: the tool wraps the migration, Postgres rejects the concurrent index, and the migration dies half-applied. Disable the per-migration transaction (the switch above) for any concurrent operation.
- **A failed `CREATE INDEX CONCURRENTLY` leaves an INVALID index behind.** It is not cleaned up and not used by the planner; the next attempt must `DROP INDEX` it first (`IF NOT EXISTS` will not save you, because the invalid one exists). Check `pg_index.indisvalid` after a failure.
- **A migration waiting on a lock blocks everything behind it.** An `ALTER` that cannot get its lock sits in the lock queue, and every query needing that table queues behind it, so a quick change becomes a site-wide stall. Set a low `lock_timeout` and retry so the migration yields instead of freezing the application.
- **NOT NULL on an existing column is a two-step, not a flag flip.** Adding it directly scans and locks the whole table. Add a `NOT VALID` check constraint (instant, no scan), then `VALIDATE CONSTRAINT` (scans under a weak lock that allows writes).
- **The down migration is real code and gets tested.** An untested down that has never run is a rollback that does not exist; run it against the changed copy and confirm the schema and data return to a working state.
