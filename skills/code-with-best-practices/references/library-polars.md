Apply these practices whenever planning, writing, or reviewing Polars code. Targets current Polars (1.x, the new streaming engine). They sit on top of the general Python practices in CLAUDE.md; this reference is the Polars-specific, version-current, and easy-to-get-wrong material. Polars moves fast, so pin the version in production and re-verify streaming and categorical behavior on each upgrade. On conflict, the project's own conventions win.

## Contents

- [Lazy vs eager](#lazy-vs-eager)
- [Query optimization](#query-optimization)
- [Expressions and contexts](#expressions-and-contexts)
- [Mental model vs pandas](#mental-model-vs-pandas)
- [Avoiding Python UDFs](#avoiding-python-udfs)
- [Streaming and sinks](#streaming-and-sinks)
- [Data types and nulls](#data-types-and-nulls)
- [Joins, group-by, conditionals](#joins-group-by-conditionals)
- [Interop](#interop)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Lazy vs eager

| Practice | Detail |
|---|---|
| Default to the lazy API | `pl.scan_csv(...).filter(...).group_by(...).agg(...).collect()` defers execution so the optimizer rewrites the whole plan (predicate and projection pushdown, lower memory). Prefer lazy unless you genuinely need intermediate results or are doing quick exploratory work. |
| Use eager only for interactive work | `pl.read_csv` / `DataFrame` give immediate feedback; eager still optimizes each single query but loses cross-step optimization. |
| Prefer `scan_*` over `read_*().lazy()` for files | Scanning lets the optimizer push projections and predicates into the reader and start before the file is fully read; `read_*().lazy()` already materialized everything. |
| Convert in-memory data to lazy with `.lazy()` | The way to get optimization on a `DataFrame` you already hold. |
| Inspect the plan with `.explain()` | Shows the optimized plan; confirm pushdown reached the scan (`PARQUET SCAN ... PROJECT n/m COLUMNS, SELECTION`). `.show_graph()` gives a visual plan. |

## Query optimization

| Practice | Detail |
|---|---|
| Let the optimizer push work down; do not hand-optimize | On a lazy plan Polars applies predicate pushdown (filter at the scan, sometimes all the way into the file reader), projection pushdown (read only the columns the query touches), slice pushdown, common-subplan elimination, expression simplification, and join/group-by strategy selection automatically. Pre-filtering eagerly or hand-reordering defeats this. |
| Verify pushdown rather than assume it | A Python UDF, an opaque op, or an eager `.collect()` mid-chain can block pushdown. Read `.explain()` to confirm projection/selection actually reached the scan node. |

## Expressions and contexts

| Practice | Detail |
|---|---|
| Express transforms as `pl.col(...)` expressions, not Python operations | An expression is a lazy, composable description of a transformation; independent expressions within a context run in parallel automatically. |
| Pick the right context | `select` (produce or transform columns, can change row count via aggregation), `with_columns` (add or replace columns, length-preserving), `filter` (keep rows; multiple conditions are ANDed), `group_by().agg()` (one row per group). |
| Batch independent column work into one `with_columns`/`select` | Expressions in one context run in parallel; splitting them across sequential `.pipe()`/chained calls serializes them for no reason. |
| Use expression expansion over per-column copies | `pl.col(pl.Float64).mean().name.prefix("avg_")` applies to every matching column; selectors (`cs.numeric()`, `cs.starts_with(...)`) target groups of columns. |
| Use `.over()` for group-wise results that keep row shape | Replaces pandas `groupby().transform()`: `pl.col("speed").rank().over("type")`. The default `mapping_strategy="group_to_rows"` maps each result back to its row; `"join"` imploded into a repeated list (memory heavy); `"explode"` changes row count. Groups are cached and shared across window expressions in one context. |

## Mental model vs pandas

| Practice | Detail |
|---|---|
| Stop thinking in a row index | Polars has no index: address columns by name and rows by integer position. There is no `.loc`/`.iloc`/`reset_index`; use `select` and `filter` instead. |
| Operations return new frames | No in-place mutation. Replace `.assign(...)` with `with_columns(...)` and stop expecting methods to mutate. |
| Let Polars parallelize | The Rust core is multithreaded across the whole API; do not bolt on your own threads or a Dask layer for single-machine work. |
| If your code looks like pandas it will run slow | Row loops, an assumed index, `.apply`, in-place edits, and `read_*` for big pipelines all fight the engine. Think declaratively in expressions. |

## Avoiding Python UDFs

| Practice | Detail |
|---|---|
| Never use `map_elements`/`apply` for what an expression can do | Per-element Python calls run under the GIL, force the frame to materialize in memory, cannot be parallelized, and cannot be optimized. The docs strongly discourage them. |
| Know the fallback order | Native expressions first, then a Polars plugin, then `map_batches` (one Python call over a whole Series, e.g. a NumPy ufunc), then `map_elements` only as a last resort. |
| Replace `np.where`/`.mask` with `when/then/otherwise` | `pl.when(c).then(a).otherwise(b)`, chainable for multi-branch logic, stays vectorized. |
| Avoid Python lambdas inside `group_by().agg()` | They serialize the otherwise-parallel aggregation behind the GIL; stay in the expression API. |

## Streaming and sinks

| Practice | Detail |
|---|---|
| Run larger-than-memory work with `collect(engine="streaming")` | Processes data in batches out-of-core and is often faster than the in-memory engine as data grows. Unsupported ops fall back to in-memory; inspect with `.show_graph(plan_stage="physical", engine="streaming")`. |
| Do not use the deprecated `collect(streaming=True)` boolean | It targets the removed old engine; use `engine="streaming"`. |
| Stream large outputs with `sink_*`, not `collect()` then `write_*` | `lf.sink_parquet("out.parquet")` writes in batches without holding the result in RAM; `sink_csv`/`sink_ipc`/`sink_ndjson` too. |
| Do not call `.collect()` mid-pipeline | Each collect materializes and forces a re-plan of the next segment, losing pushdown; keep one lazy chain to a single terminal `collect()`/`sink_*`. |
| Validate streaming output for critical pipelines | The engine is still maturing; spot-check against the in-memory result. |

## Data types and nulls

| Practice | Detail |
|---|---|
| Treat `null` and `NaN` as distinct | `null` is missing data (Arrow validity bitmap, every dtype, no silent int->float promotion like pandas); `NaN` is only a floating-point value. Use `is_null`/`fill_null`/`drop_nulls` for missingness, `is_nan`/`fill_nan` for the float. |
| Set explicit schemas for production | Inference reads a sample and can guess wrong; inspect `df.schema` and override with `schema_overrides={"age": pl.UInt8}`. |
| Cast with a deliberate `strict` | `strict=True` (default) raises on a failed conversion with the offending values; `strict=False` turns failures into `null`; float-to-int truncates. |
| Prefer `Enum` over `Categorical` for known categories | `Enum` is a fixed, ordered, immutable set needing no re-encoding; `Categorical` is for dynamic, runtime-inferred categories. |
| Use nested dtypes natively | `List`, `Array`, and `Struct` are first-class; `pl.struct([...])` packs several columns to pass into one operation. |

## Joins, group-by, conditionals

| Practice | Detail |
|---|---|
| Choose `how` precisely; use semi/anti to filter by membership | `semi` keeps left rows that have a match (a membership filter, no right columns); `anti` keeps left rows with none; `full` keeps both sides; pass `coalesce=True` to merge the key columns into one. |
| Guard cardinality with `validate=` | `validate="m:1"` (also `1:1`/`1:m`/`m:m`) raises if the join is not the expected shape, catching accidental row fan-out early. Not supported by the streaming engine. |
| `join_where` for non-equi, `join_asof` for nearest-key | `join_asof(trades, quotes, on="time", by="stock", strategy="backward", tolerance="1m")`; pass `by=` to avoid cross-group matches; asof inputs must be sorted on the key. |
| Filter and conditionalize inside `agg` | `(pl.col("party") == x).sum()`, `.filter(...).mean()`, and `sort_by(...).first()` run in one pass rather than as pre/post steps. |

## Interop

| Practice | Detail |
|---|---|
| Convert at boundaries, prefer zero-copy | `df.to_numpy(allow_copy=False)` fails loudly instead of silently copying; `df.to_pandas(use_pyarrow_extension_array=True)` preserves nulls and avoids copies; install `pyarrow` to unlock more zero-copy paths. |

## Gotchas

- `null` (missing) and `NaN` (a float value) are different; `fill_null` will not touch a `NaN` and vice versa.
- `collect(streaming=True)` is deprecated; the current switch is `collect(engine="streaming")`.
- A mid-pipeline `.collect()` silently kills pushdown for everything downstream; keep one terminal collect.
- A `map_elements`/lambda anywhere in the plan can block parallelism and pushdown and force materialization; check `.explain()`.
- `over()` with `mapping_strategy="join"` repeats an imploded list on every row and can blow up memory; default `group_to_rows` is usually what you want.
- Asof and other order-dependent joins assume sorted keys; unsorted input gives wrong results, not an error, unless you let it check sortedness.
- Type inference on `scan_*`/`read_*` samples only the first values; set `schema_overrides` for production rather than trusting the guess.

## Sources

- [Polars user guide: Lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/) and [Streaming](https://docs.pola.rs/user-guide/concepts/streaming/) - official guide; lazy-vs-eager, `collect(engine="streaming")`, sinks.
- [Polars user guide: Expressions and contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/) and [Window functions](https://docs.pola.rs/user-guide/expressions/window-functions/) - official; contexts, `.over()`, mapping strategies.
- [Polars user guide: Coming from pandas](https://docs.pola.rs/user-guide/migration/pandas/) - official; no index, columnar, parallel, expressions over `apply`, null vs NaN.
- [Polars user guide: Joins](https://docs.pola.rs/user-guide/transformations/joins/) and the [join API reference](https://docs.pola.rs/py-polars/html/reference/dataframe/api/polars.DataFrame.join.html) - official; join strategies, `validate`, `coalesce`, asof/non-equi.
- [polars.Expr.map_elements](https://docs.pola.rs/py-polars/html/reference/expressions/api/polars.Expr.map_elements.html) and [LazyFrame.explain](https://docs.pola.rs/py-polars/html/reference/lazyframe/api/polars.LazyFrame.explain.html) - official API docs; UDF fallback order and plan inspection.
- [Modern Polars](https://kevinheavey.github.io/modern-polars/) (Kevin Heavey) - widely cited side-by-side pandas/Polars guide; idiomatic expression patterns.
