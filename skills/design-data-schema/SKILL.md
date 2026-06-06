---
name: design-data-schema
description: Use this skill when designing or reviewing a database schema, including
  SQL tables, columns, constraints, indexes, and migrations, or DynamoDB and
  similar NoSQL key design, access patterns, and single-table modeling. Use when
  the user says "design the schema", "model this data", "what should the tables
  look like", "add a table", or "single-table design". Do not use for API contract
  design (use design-api) or for writing application-level queries and ORM code
  against an existing schema.
---

## Purpose

Design the schema before data accumulates in it, because schemas are the hardest layer to change after the fact. The deliverable is the schema definition (DDL or a key-design document) plus the recorded trade-offs. The two store families demand opposite design orders, and applying the wrong one is the dominant failure mode: SQL models entities and relationships first and serves arbitrary queries; DynamoDB models access patterns first and serves exactly the queries it was designed for.

## Workflow

1. **Establish the store.** Use what the project already runs unless the user is choosing. Relational is the default when query patterns are evolving or unknown; DynamoDB-style stores earn their constraints when the access patterns are enumerable up front and the scale demands them.
2. **Gather the right inputs for the store.** SQL: entities, relationships (1:1, 1:N, M:N), and the known query patterns. DynamoDB: the complete access-pattern list first (each with query shape, expected QPS, item size, consistency need); refuse to design keys before this list exists.
3. **Design in the per-store order below**, applying the hard rules.
4. **Document the contextual choices made** and the trade-offs (especially any denormalization and its refresh strategy).
5. **Plan evolution**: migrations are additive and backward compatible; expand-contract for anything breaking (add the new shape, migrate readers, then remove the old) so schema and code never have to deploy atomically.

## SQL

Design order: entities and relationships -> normalize to 3NF -> primary key strategy -> column types and NOT NULL -> foreign keys with explicit referential actions -> indexes for known query patterns -> CHECK constraints -> audit columns -> migration plan.

Hard rules:

- `snake_case` for every identifier; plural table names (`orders`), singular column names (`user_id`, `email`)
- Every table has an explicit primary key; `BIGINT`/`BIGSERIAL` surrogate keys by default (an `INT` key on a growing table is a time bomb at 2B rows)
- `TIMESTAMP WITH TIME ZONE` for all temporal columns; bare `TIMESTAMP` silently strips timezone and corrupts cross-region data
- `NUMERIC(p, s)` for money and precise values, never `FLOAT`/`DOUBLE`
- `TEXT` over `VARCHAR(n)` unless the length cap is a genuine business rule
- NOT NULL is the default stance; each nullable column needs a justification
- Every foreign key column gets an index, and every foreign key declares its `ON DELETE` behavior explicitly; cascade only within an aggregate (owned children), never across aggregate roots
- `created_at` on every table, `updated_at` on mutable tables
- Derived or denormalized data requires a documented refresh strategy or it will silently go stale

Contextual choices:

| Decision | Default recommendation |
|---|---|
| Primary key form | BIGSERIAL internal; UUID for distributed or publicly exposed IDs |
| Enums | Lookup table when values change; CHECK constraint for small stable sets |
| Soft delete | `deleted_at` column; audit table when compliance demands history |
| Multi-tenant | Shared schema + row-level security; schema-per-tenant for regulatory isolation |
| Denormalization | Only with profiling evidence, preferably as a materialized view |
| Partitioning | Range for time-series, list for tenant isolation |

## DynamoDB

Design order: enumerate all access patterns -> single-table vs multi-table -> partition key -> sort key -> map remaining patterns to GSIs -> item structure and size budgets -> TTL, versioning, condition expressions -> capacity mode -> streams consumers -> IAM and encryption.

Hard rules:

- Access patterns first, always; designing from entity relationships produces a relational schema trapped in a key-value store
- Partition keys need high cardinality and even distribution; status flags, booleans, and dates make hot partitions
- No `Scan` in any production read path; every operational read is a `Query` or `GetItem`, and a "necessary" Scan means the key design is wrong
- Sort keys use consistent type prefixes (`USER#`, `ORDER#`) for entity discrimination and range queries
- Items stay bounded: 400 KB is the hard limit, budget 350 KB; unbounded lists become separate items, large payloads go to S3 with a pointer
- GSI keys need high cardinality too, and each GSI adds write amplification; do not mint one per hypothetical future query
- Stream consumers are idempotent (delivery is at-least-once); transactions cost double capacity and are single-region; TTL deletion timing is approximate, never load-bearing for locks or state transitions
- Encryption at rest always; KMS customer-managed keys for regulated data

Contextual choices:

| Decision | Default recommendation |
|---|---|
| Table strategy | Single-table unless retention, security, or workload profiles genuinely differ |
| Capacity mode | On-demand for variable or unknown traffic; provisioned for stable, cost-governed loads |
| GSI projection | KEYS_ONLY or INCLUDE; ALL only with justification |
| Consistency | Eventually consistent reads unless the logic requires read-your-writes |
| ID format | ULID when time-ordering helps; composite `TYPE#id` for single-table patterns |

## Anti-patterns (reject on sight)

| Anti-pattern | Why |
|---|---|
| EAV tables (entity-attribute-value) | Defeats types, constraints, and indexes simultaneously |
| Polymorphic FKs (`subject_type` + `subject_id`) | The database cannot enforce them; orphans accumulate silently |
| "We enforce referential integrity in the app" | Every app bug becomes a data corruption; the constraint is the backstop |
| `FLOAT` for money | Accumulating rounding errors in the one domain that audits them |
| God tables (50+ columns) | Multiple entities wearing one schema; decompose |
| Stringly-typed status columns | Free text where a constraint belongs; typos become states |
| Relational modeling in DynamoDB (normalized items + FK lookups) | Recreates joins client-side at N round trips each |
| Low-cardinality partition or GSI keys | Hot partitions throttle exactly when traffic peaks |
| Scan-based application queries | Cost and latency scale with table size, not result size |
| Schema design before access patterns (DynamoDB) | The store cannot serve queries it was not keyed for; this is unfixable later without a migration |

## Gotchas

- **The design orders are opposites and not interchangeable.** Entity-first DynamoDB design is the single most common NoSQL failure; access-pattern-first SQL design produces premature denormalization. Confirm which store before applying either order.
- **Migrations are schema design too.** A perfect target schema reachable only through a destructive migration is not deployable; expand-contract keeps every intermediate state working with both old and new code.
- **Denormalization is a measurement decision, not a taste decision.** Without profiling evidence that the normalized query is too slow, denormalizing trades correctness risk for imagined performance.
- **DynamoDB makes added queries expensive, not impossible.** A new access pattern after launch means a new GSI (write amplification, backfill) or a migration; the access-pattern list deserves real effort, including the patterns ops and analytics will need.
- **Nullable columns are tiny unions.** Each NULL means "this column has two meanings"; many of them per table usually signal an entity trying to escape.
