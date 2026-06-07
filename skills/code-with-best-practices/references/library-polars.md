Apply these practices whenever planning, writing, or reviewing Polars code. They sit on top of the general Python practices; this file covers Polars-specific idioms. Polars evolves fast: pin the version in production and re-verify the streaming engine and categorical behavior on each upgrade.

## Contents

- Lazy vs Eager
- Query Optimization
- Expressions and Contexts
- Mental Model
- Coming from pandas
- Performance: Streaming and Sinks
- Data Types
- Joins, Group-by, Conditionals
- Interop
- Anti-Patterns

## Lazy vs Eager

| Practice | Detail |
|---|---|
| Default to the lazy API | `pl.scan_csv(...).filter(...).group_by(...).agg(...).collect()` defers execution so the optimizer rewrites the whole plan (predicate and projection pushdown, lower memory). The docs say to prefer lazy unless you want intermediate results or are doing exploratory work. |
| Use eager only for interactive work | `pl.read_csv` / `DataFrame` give immediate feedback; eager still optimizes each single query but loses cross-step optimization. |
| Inspect the plan with `.explain()` | Confirms pushdown reached the scan; `.show_graph()` gives a visual plan. |
| Convert in-memory data to lazy with `.lazy()` | To get optimization on a `DataFrame` you already hold. |

## Query Optimization

| Practice | Detail |
|---|---|
| Let the optimizer push work down; do not hand-optimize | On a lazy plan Polars applies predicate pushdown (filter at the scan), projection pushdown (read only needed columns), slice pushdown, common-subplan elimination, expression simplification, join reordering, and group-by strategy selection automatically. Pre-filtering eagerly or reordering joins by hand defeats this. |

## Expressions and Contexts

| Practice | Detail |
|---|---|
| Express transforms as `pl.col(...)` expressions, not Python operations | An expression is a lazy representation of a transformation; independent expressions within a context are parallelized automatically. |
| Pick the right context | `select` (produce or transform columns), `with_columns` (add columns, length-preserving), `filter` (keep rows, multiple conditions ANDed), `group_by().agg()` (one row per group). |
| Batch independent column work into one `with_columns`/`select` | Expressions in one context run in parallel; sequential `.pipe()` chains serialize them. |
| Use expression expansion over per-column copies | `pl.col(pl.Float64).mean().name.prefix("avg_")` applies to every matching column. |
| Use `.over()` for group-wise results that keep row shape | Replaces pandas `groupby().transform()`: `pl.col("speed").rank().over("type")`; `mapping_strategy` controls the row layout. |

## Mental Model

| Practice | Detail |
|---|---|
| Stop thinking in a row index | Polars has no index; address columns by name (`df.select("a")`) and rows by position. Results are more predictable. |
| Treat `null` and `NaN` as distinct | `null` is missing data (Arrow validity bitmap, all types, no silent int->float promotion); `NaN` is only a floating-point value. Use `is_null`/`fill_null`/`drop_nulls` for missingness. |
| Let Polars parallelize | The Rust core is multithreaded across the whole API; do not add your own threading or Dask layer for single-machine work. |

## Coming from pandas

| Practice | Detail |
|---|---|
| Never use `.apply`/`map_elements` for what an expression can do | Per-element Python calls add huge overhead and run under the GIL; the docs strongly discourage Python UDFs. Order of preference: native expressions, then plugins, then `map_batches` (one Python call over the whole Series, e.g. a NumPy ufunc), then `map_elements` as a last resort. |
| Avoid Python lambdas inside `group_by().agg()` | They trigger the GIL during the parallel aggregation, killing the speedup; stay in the expression API. |
| Replace `np.where`/`.mask` with `when/then/otherwise` | `pl.when(c).then(a).otherwise(b)`, chainable for multi-branch logic. |
| If your code looks like pandas it will run slow | Mutating in place, expecting an index, row loops, and `read_*` for big pipelines all fight the engine. |

## Performance: Streaming and Sinks

| Practice | Detail |
|---|---|
| Run larger-than-memory work with `collect(engine="streaming")` | Processes data out-of-core in batches and is also faster as data grows; unsupported operations fall back to in-memory. Validate streaming output against the in-memory engine for critical pipelines, as the engine is still maturing. |
| Do not use the deprecated `collect(streaming=True)` boolean | It invokes the removed old streaming engine and raises a deprecation/type error; use `engine="streaming"`. |
| Stream large outputs with `sink_*`, not `collect()` then `write_*` | `lf.sink_parquet("out.parquet")` writes in batches without holding all data in RAM; `sink_csv`/`sink_ipc`/`sink_ndjson` too. |
| Do not call `.collect()` mid-pipeline | Each collect materializes results and forces a re-plan of the next segment, losing pushdown; keep one lazy chain to a single terminal `collect()`/`sink_*`. |
| Prefer `scan_*` over `read_*().lazy()` for files | Scanning lets the optimizer push projections and predicates into the reader and start before the file is fully read. |

## Data Types

| Practice | Detail |
|---|---|
| Set explicit schemas for production | Inference reads the first non-null values and can guess wrong; inspect `df.schema`, override with `schema_overrides={"age": pl.UInt8}`. |
| Cast with intent and a deliberate `strict` | `strict=True` (default) raises on a failed conversion with the offending values; `strict=False` turns failures into `null`; floats truncate when cast to int. |
| Prefer `Enum` over `Categorical` for known categories | `Enum` is fixed, ordered, immutable, and needs no re-encoding; `Categorical` is for dynamic categories (lexical comparison, runtime-inferred encoding). |
| Use nested dtypes natively | `List`, `Array`, and `Struct` are first-class and operate inside the engine; combine columns with `pl.struct([...])` to pass several into one batch operation. |

## Joins, Group-by, Conditionals

| Practice | Detail |
|---|---|
| Choose `how` precisely; use semi/anti to filter by membership | `semi` keeps left rows with a match (a filter, no right columns); `anti` keeps left rows with none; `full` with `coalesce=True` merges the key columns. |
| `join_where` for non-equi, `join_asof` for nearest-key | `join_asof(quotes, on="ts", by="stock", tolerance="1m")`; pass `by=` to avoid cross-group matches. |
| Filter and conditionalize inside `agg` | `(pl.col("party") == x).sum()`, `.filter(...).mean()`, and `sort_by(...).first()` happen in one pass instead of pre/post steps. |

## Interop

| Practice | Detail |
|---|---|
| Convert at boundaries, prefer zero-copy | `df.to_numpy(allow_copy=False)` fails loudly instead of silently copying; `df.to_pandas(use_pyarrow_extension_array=True)` is zero-copy and preserves nulls; install `pyarrow` to unlock more zero-copy paths. |

## Anti-Patterns

| Practice | Detail |
|---|---|
| Avoid the common Polars mistakes | repeated mid-pipeline `.collect()`; `map_elements`/`apply`/loops/lambdas in `agg`; mixing eager and lazy ad hoc; bringing `np.where`/`.mask`/index/in-place habits from pandas; `collect(streaming=True)`; conflating `null` and `NaN`; sequential `.pipe()` instead of one parallel `with_columns`; relying on type inference for production schemas. |
