Apply these practices whenever planning, writing, or reviewing SQL queries or migrations.

## Query Structure

| Practice | Detail |
|---|---|
| Select specific columns, never `SELECT *` | `*` fetches unneeded data, breaks silently when columns are added or reordered, and hides which columns the query actually depends on. Reserve `*` for ad-hoc exploration. |
| Always alias computed columns | `SUM(amount) AS total_amount`. Unnamed expressions receive engine-specific default names that vary across databases and break downstream code. |
| Use CTEs (`WITH`) for complex queries | CTEs name intermediate results and read top to bottom, which is far easier to follow than deeply nested subqueries. Reserve subqueries for simple single-use expressions. |
| Do not sort inside subqueries | Ordering in a subquery is expensive and meaningless because the outer query controls final ordering. The optimizer may discard it, so it only adds cost. |
| Prefer `UNION ALL` over `UNION` when duplicates are fine | `UNION` sorts and deduplicates the combined set. If duplicates are harmless, `UNION ALL` skips that overhead. |
| Comment the why, not the what | `-- exclude internal test orders` adds context. `-- filter where id > 10` restates the code and is noise. |

## Parameterization and Safety

| Practice | Detail |
|---|---|
| Always use bound parameters, never string interpolation | Concatenating user input into SQL is the root cause of injection vulnerabilities. Parameterized queries separate code from data so input can never be executed as SQL. |
| Parameterize values, not identifiers | Placeholders bind values only. Table and column names cannot be parameterized, so validate them against an allowlist rather than interpolating raw input. |
| Pass `IN` lists as individual parameters | Build one placeholder per element rather than splicing a comma-joined string, otherwise the values bypass parameterization and reopen injection. |
| Set a statement timeout for application queries | An unbounded query can hold locks and exhaust connections indefinitely. A timeout caps the blast radius of a slow or runaway statement. |

## Joins and Filtering

| Practice | Detail |
|---|---|
| Use explicit `JOIN ... ON`, never comma joins | `FROM a JOIN b ON a.id = b.a_id` separates join logic from filter logic. Comma joins with conditions in `WHERE` obscure intent and make accidental cross joins easy. |
| Prefix every column reference with its table alias | Unqualified columns break silently when a joined table later adds a same-named column, producing wrong results with no error. |
| Confirm the join key relationship before writing the join | A join on a non-unique key silently multiplies rows and inflates aggregates. Knowing the cardinality prevents fan-out bugs that are hard to spot. |
| Avoid functions on columns in `WHERE` | `WHERE YEAR(created_at) = 2024` is non-sargable and forces a full scan. Rewrite as a range (`>= '2024-01-01' AND < '2025-01-01'`) so an index can be used. |
| Avoid leading wildcards in `LIKE` | `LIKE '%son'` cannot use a standard index and scans the whole table. Prefer trailing wildcards or full-text search. |
| Prefer `EXISTS` over `IN` for existence checks on subqueries | `EXISTS` short-circuits on the first match, while `IN` may materialize the entire inner result. Keep `IN` for small literal lists. |
| Filter with `WHERE` before `HAVING` | `WHERE` removes rows before aggregation, so it is cheaper. Use `HAVING` only for conditions on aggregated values like `COUNT(*) > 1`. |

## Avoiding N+1 Queries

| Practice | Detail |
|---|---|
| Fetch related rows in a single set-based query | Looping over results and querying per row multiplies round trips and crushes throughput. One join or one batched `IN` query replaces N queries. |
| Use eager loading instead of lazy per-record access | When iterating ORM results, lazy associations trigger a hidden query per record. Eager loading (a join or batch fetch) collapses them into one. |
| Batch writes rather than inserting row by row | A single multi-row `INSERT` or bulk operation avoids per-row round-trip latency and reduces transaction and lock overhead. |

## Transactions

| Practice | Detail |
|---|---|
| Wrap multi-statement changes that must succeed together in a transaction | Without a transaction, a failure midway leaves data partially updated and inconsistent. A transaction guarantees all-or-nothing application. |
| Keep transactions short and do no slow work inside them | Open transactions hold locks; long ones block other writers and cause deadlocks and timeouts. Do network calls and heavy computation outside the transaction boundary. |
| Acquire locks in a consistent order across the codebase | Two transactions locking the same rows in opposite orders deadlock. A single canonical ordering eliminates that class of failure. |
| Choose an isolation level deliberately for correctness-critical logic | The default may allow phantom reads or lost updates that corrupt invariants like balances. Raise isolation or use explicit row locks where consistency matters. |

## Migration Safety

| Practice | Detail |
|---|---|
| Make migrations reversible or document why they are not | A bad deploy needs a clean rollback path. An irreversible migration (like a destructive drop) must be flagged so it is reviewed and backed up first. |
| Split schema changes from backfills and column drops | Add a column, deploy code that writes it, backfill, then later remove the old column in a separate migration. Doing it all at once breaks running instances during deploy. |
| Add columns as nullable or with a safe default first | On large tables, adding a `NOT NULL` column without a default can rewrite the whole table and lock it. Add nullable, backfill, then enforce the constraint. |
| Backfill large tables in batches, not one statement | A single mass `UPDATE` locks the table and bloats the transaction log. Batched updates keep locks short and let other traffic proceed. |
| Build indexes concurrently on busy tables when supported | A normal `CREATE INDEX` locks writes for the duration. A concurrent build avoids blocking production traffic on a large table. |
| Make migrations idempotent or guarded | Migrations can be retried after partial failure. Guards like `IF NOT EXISTS` prevent a re-run from erroring and leaving the schema half-applied. |
| Test the migration against production-like data volume | A migration that is instant on an empty dev table can lock a million-row production table for minutes. Validating on realistic volume surfaces the cost beforehand. |
