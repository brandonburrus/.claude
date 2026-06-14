Apply these practices whenever planning, writing, or reviewing SQL queries or migrations. Targets standard SQL with PostgreSQL-leaning notes (engine differences flagged). Generic clean-code rules live in CLAUDE.md; this reference is the SQL-specific, easy-to-get-wrong material. Table, key, and index DESIGN is out of scope here (use design-data-schema); this covers writing queries and migrations against an existing schema. On conflict, the project's own conventions win.

## Contents

- [Safety and parameterization](#safety-and-parameterization)
- [Query structure](#query-structure)
- [NULL and three-valued logic](#null-and-three-valued-logic)
- [Joins and filtering](#joins-and-filtering)
- [Performance and sargability](#performance-and-sargability)
- [Set-based thinking](#set-based-thinking)
- [Transactions](#transactions)
- [Migrations](#migrations)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Safety and parameterization

| Practice | Detail |
|---|---|
| Always bind parameters, never interpolate input | Concatenating any external value into SQL text is the root cause of injection. Bound parameters (`$1`, `?`, `:name`) send code and data on separate channels so input can never be parsed as SQL. This is non-negotiable even for values you "know" are safe. |
| Parameterize values, not identifiers | Placeholders bind values only. Table and column names cannot be parameters, so an allowlist-validate dynamic identifier and quote it with the engine's identifier quoting, never raw interpolation. |
| Expand `IN` lists to one placeholder each | `IN ($1, $2, $3)`, not a comma-joined string spliced into one placeholder. Splicing reopens injection and defeats plan caching. For large sets pass an array parameter (`= ANY($1)` in Postgres) instead. |
| Set a per-statement timeout for app queries | An unbounded statement can hold locks and pin a connection indefinitely. `statement_timeout` (or the driver equivalent) caps the blast radius of a runaway query. |
| Grant least privilege to the app role | The application connection rarely needs `DROP`/`ALTER`/superuser. A constrained role limits what a successful injection or bug can reach. |

## Query structure

| Practice | Detail |
|---|---|
| List columns explicitly, never `SELECT *` | `*` fetches unneeded data, breaks silently when columns are added or reordered, defeats covering indexes, and hides the query's real dependencies. Reserve `*` for ad-hoc exploration. |
| Alias every computed column | `SUM(amount) AS total_amount`. Unnamed expressions get engine-specific default names that vary across databases and break downstream code. |
| Use CTEs (`WITH`) to name steps, not nesting | CTEs read top to bottom and name intermediate results, far clearer than deeply nested subqueries. Note Postgres before 12 materialized every CTE (an optimization fence); 12+ inlines non-recursive single-use CTEs, with `MATERIALIZED` / `NOT MATERIALIZED` to force it. |
| Keep keywords and identifiers cased consistently | Conventionally uppercase keywords, lowercase snake_case identifiers. Unquoted identifiers fold case (Postgres to lower, others differ), so never rely on case to distinguish names. |
| `UNION ALL` unless you need dedup | `UNION` sorts and removes duplicates; when duplicates are impossible or harmless, `UNION ALL` skips that cost. |
| Comment the why, not the what | `-- exclude internal test orders` adds context; `-- filter id > 10` restates the code. |

## NULL and three-valued logic

| Practice | Detail |
|---|---|
| Treat conditions as TRUE / FALSE / UNKNOWN | Any comparison to `NULL` yields UNKNOWN, and `WHERE`/`ON`/`HAVING` keep only TRUE rows. `= NULL` matches nothing; use `IS NULL` / `IS NOT NULL`. `x <> 5` silently drops rows where `x` is NULL. |
| Never use `NOT IN` with a nullable subquery | If the subquery returns even one NULL, `NOT IN` evaluates to UNKNOWN for every row and the result is empty, a classic silent wrong-answer bug. Use `NOT EXISTS` (correlated), which handles NULL correctly. |
| Use `IS DISTINCT FROM` for null-safe inequality | `a IS DISTINCT FROM b` treats two NULLs as equal and a NULL vs value as different, the comparison most people actually mean. MySQL spells it `<=>` (null-safe equals). |
| Know `COUNT` and aggregates skip NULL | `COUNT(col)` ignores NULLs while `COUNT(*)` counts rows; `AVG`/`SUM` ignore NULLs, which changes the denominator. Use `COALESCE` deliberately, not reflexively. |

## Joins and filtering

| Practice | Detail |
|---|---|
| Explicit `JOIN ... ON`, never comma joins | `FROM a JOIN b ON a.id = b.a_id` separates join logic from filters. Comma joins with conditions in `WHERE` hide intent and make accidental cross joins easy. |
| Qualify every column with its table alias | Unqualified columns break silently when a joined table later gains a same-named column, producing wrong results with no error. |
| Confirm join-key cardinality before writing it | A join on a non-unique key silently multiplies rows and inflates aggregates (fan-out). Know whether the relationship is 1:1, 1:N, or N:M first. |
| Put outer-join conditions in `ON`, not `WHERE` | A predicate on the right table of a `LEFT JOIN` placed in `WHERE` filters out the unmatched (NULL-extended) rows and silently turns it into an inner join. Keep such conditions in `ON`. |
| `WHERE` before `HAVING` | `WHERE` removes rows before aggregation (cheaper); `HAVING` is only for conditions on aggregates like `COUNT(*) > 1`. |

## Performance and sargability

| Practice | Detail |
|---|---|
| Keep predicates sargable: no functions on indexed columns | `WHERE lower(email) = $1` or `WHERE date(created_at) = $1` cannot use a plain index and forces a scan. Rewrite as a range (`created_at >= $1 AND created_at < $2`), store the normalized form, or add a matching expression/function-based index. |
| Avoid leading-wildcard `LIKE` | `LIKE '%term'` cannot use a B-tree index and scans the table. Prefer trailing wildcards, a trigram index, or full-text search. |
| `EXISTS` over `IN` for subquery existence checks | `EXISTS` short-circuits on first match; `IN` may materialize the whole inner result. (Keep `IN` for small literal lists.) |
| Verify the plan with `EXPLAIN (ANALYZE, BUFFERS)` | Reasoning about performance is guessing; the planner decides. `ANALYZE` runs the query and shows actual vs estimated rows: a large gap means stale statistics. Watch for unexpected `Seq Scan` on big tables and nested-loop row explosions. |
| `LIMIT` is nondeterministic without `ORDER BY` | Without an explicit total order the engine may return any rows in any order, and the set can change between runs. Always pair `LIMIT` with a deterministic `ORDER BY` (include a tiebreaker like the primary key). |
| Paginate by keyset, not large `OFFSET` | `OFFSET 100000` still scans and discards 100k rows. Seek with `WHERE (sort_col, id) > ($1, $2) ORDER BY sort_col, id LIMIT n` for stable, constant-cost pages. |

## Set-based thinking

| Practice | Detail |
|---|---|
| One set-based statement, not row-by-row loops | Looping in application code and querying per row multiplies round trips (the N+1 problem). One join, one batched `= ANY(array)`, or one multi-row write replaces N statements. |
| Use window functions instead of correlated subqueries | `ROW_NUMBER()`, `SUM(...) OVER (PARTITION BY ...)`, `LAG`/`LEAD`, running totals, and per-group ranks compute in a single scan; a correlated subquery re-runs once per outer row. Window functions are also far more readable. |
| Filter window results with `QUALIFY` where supported | `QUALIFY ROW_NUMBER() OVER (...) = 1` reads cleaner than wrapping in a CTE then filtering. Supported by Snowflake/BigQuery/DuckDB; on Postgres/MySQL use a subquery or CTE around the window. |
| Set-update and upsert in one statement | `UPDATE ... FROM`, `INSERT ... ON CONFLICT` (Postgres) / `ON DUPLICATE KEY UPDATE` (MySQL) / `MERGE` apply many changes atomically instead of read-modify-write loops. |
| Eager-load ORM associations | Lazy associations trigger a hidden query per record while iterating; eager loading (join or batch fetch) collapses them into one. |

## Transactions

| Practice | Detail |
|---|---|
| Wrap all-or-nothing changes in one transaction | Without a transaction a mid-sequence failure leaves data half-updated. A transaction guarantees atomic application. |
| Keep transactions short; no slow work inside | Open transactions hold locks; long ones block writers and breed deadlocks and timeouts. Do network calls and heavy computation outside the transaction boundary. |
| Choose the isolation level deliberately | Postgres defaults to READ COMMITTED, which permits non-repeatable and phantom reads; a read-modify-write of a balance can lose updates. Use REPEATABLE READ / SERIALIZABLE, or explicit `SELECT ... FOR UPDATE` row locks, where an invariant depends on it. Note Postgres maps READ UNCOMMITTED to READ COMMITTED. |
| Be ready to retry on serialization failure | SERIALIZABLE (and Postgres REPEATABLE READ) can abort with a serialization error (SQLSTATE 40001) instead of corrupting data. Application code must catch it and retry the whole transaction. |
| Lock rows in a consistent order everywhere | Two transactions locking the same rows in opposite order deadlock. A single canonical ordering eliminates that class of failure. |

## Migrations

| Practice | Detail |
|---|---|
| Make migrations reversible or flag why not | A bad deploy needs a clean rollback path; an irreversible step (a destructive drop) must be called out so it is reviewed and backed up first. |
| Make each migration idempotent or guarded | Migrations get retried after partial failure; `IF NOT EXISTS` / `IF EXISTS` guards let a re-run succeed instead of erroring on a half-applied schema. |
| Expand, then contract, across deploys | Add the new column/table, deploy code that writes both, backfill, switch reads, then drop the old shape in a later migration. Doing it all at once breaks instances still running the old code mid-deploy. |
| Add columns nullable or with a constant default first | A volatile default or a `NOT NULL` add can rewrite a whole large table under lock. Modern Postgres adds a constant default cheaply, but add nullable, backfill, then add the `NOT NULL` constraint to be safe across engines. |
| Backfill in bounded batches, not one statement | A single mass `UPDATE` locks rows and bloats the WAL / undo log. Loop over keyed batches with short transactions so other traffic proceeds. |
| Build indexes without long write locks | A plain `CREATE INDEX` locks writes for the build. Use `CREATE INDEX CONCURRENTLY` (Postgres; cannot run inside a transaction block and can leave an `INVALID` index to clean up on failure) or the engine's online-DDL equivalent on busy tables. |
| Avoid long-locking DDL on big tables | Some `ALTER`s rewrite or take an `ACCESS EXCLUSIVE` lock for the duration. Prefer metadata-only changes, set a short `lock_timeout` so a blocked migration fails fast instead of stalling all traffic behind it, and test against production-scale data volume first. |

## Gotchas

- A predicate on the null-able side of a `LEFT JOIN` in `WHERE` silently downgrades it to an inner join; keep it in `ON`.
- `NOT IN (subquery)` returns zero rows the moment the subquery yields a single NULL; use `NOT EXISTS`.
- `<>` / `!=` and `NOT IN` exclude NULL rows because the comparison is UNKNOWN, not FALSE.
- `LIMIT` without a fully deterministic `ORDER BY` can return different rows on identical reruns.
- Wrapping an indexed column in a function (`lower()`, `date()`, casts) silently disables the index.
- `COUNT(col)` skips NULLs but `COUNT(*)` does not; mixing them changes results.
- `CREATE INDEX CONCURRENTLY` cannot run inside a transaction, so it does not fit a tool that wraps each migration in `BEGIN`/`COMMIT`.
- `EXPLAIN` alone shows estimates; only `EXPLAIN ANALYZE` runs the query and reveals estimate-vs-actual row gaps that signal stale statistics.

## Sources

- [PostgreSQL: Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html), [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html) - official engine docs; authoritative on isolation semantics, concurrent index builds, and plan reading.
- [Use The Index, Luke!](https://use-the-index-luke.com/) (Markus Winand): [functions in WHERE](https://use-the-index-luke.com/sql/where-clause/functions), [LIKE filters](https://use-the-index-luke.com/sql/where-clause/searching-for-ranges) - the standard developer reference on sargability and indexable predicates across engines.
- [Modern SQL](https://modern-sql.com/) (Markus Winand): [three-valued logic](https://modern-sql.com/concept/three-valued-logic), [NULL](https://modern-sql.com/concept/null), [OVER(PARTITION BY)](https://modern-sql.com/caniuse/over_partition_by) - cross-engine standard-SQL reference for NULL semantics and window functions.
- [SQL Style Guide](https://www.sqlstyle.guide/) (Simon Holywell) - widely adopted style guide; casing, aliasing, identifier, and readability conventions.
- [MySQL Reference: Comparison Operators](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html) and [Subquery Optimization](https://dev.mysql.com/doc/refman/8.0/en/subquery-optimization.html) - second major engine; null-safe `<=>`, `NOT IN`/`EXISTS`, and join-condition behavior.
- [PostgreSQL bug thread: NULL in subselects forces NOT IN to false](https://www.postgresql.org/message-id/20070205192044.D67106%40megazone.bigpanda.com) - core-developer discussion documenting the `NOT IN` + NULL trap by spec.
