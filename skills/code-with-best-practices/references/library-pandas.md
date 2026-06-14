Apply these practices whenever planning, writing, or reviewing pandas data code. Targets pandas 2.x and 3.0 (3.0 shipped Jan 2026; version-specific items are flagged). Generic clean-code and Python rules live in CLAUDE.md and language-python; this reference is the pandas-specific, version-current, and easy-to-get-wrong material: the Copy-on-Write model, correctness traps, and performance. On conflict, the project's own conventions win.

## Contents

- [Copy-on-Write](#copy-on-write)
- [Indexing correctness](#indexing-correctness)
- [Vectorization](#vectorization)
- [dtypes and memory](#dtypes-and-memory)
- [Method chaining](#method-chaining)
- [Merge, join, concat](#merge-join-concat)
- [groupby](#groupby)
- [Missing data](#missing-data)
- [Datetime and time series](#datetime-and-time-series)
- [Reading and writing](#reading-and-writing)
- [Scaling and switching tools](#scaling-and-switching-tools)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Copy-on-Write

Copy-on-Write (CoW) is the default and only mode in pandas 3.0, opt-in via `pd.options.mode.copy_on_write` in 2.x. Any object derived from another behaves as a copy, so mutating it never touches the parent; copies happen lazily, only on first write. `SettingWithCopyWarning` is gone.

| Practice | Detail |
|---|---|
| Migrate on 2.3 with warn mode before the 3.0 upgrade | `pd.options.mode.copy_on_write = "warn"` surfaces the patterns that change behavior so you can fix them first. The option is deprecated and inert in 3.0. |
| Never chained-assign; use `.loc` | `df["foo"][cond] = x` writes to an intermediate copy and raises `ChainedAssignmentError`. Write `df.loc[cond, "foo"] = x`, one object in one step. |
| Avoid `inplace=True` on derived objects | `df["foo"].replace(1, 5, inplace=True)` updates nothing under CoW. Reassign (`df["foo"] = df["foo"].replace(1, 5)`) or operate on the whole frame. Note 3.0 makes `inplace` methods return self, not `None`. |
| Treat `.to_numpy()` / `.values` as read-only | When data is shared, CoW returns a read-only array; call `df.to_numpy().copy()` to mutate. (New string dtype `.values` returns an ExtensionArray, not NumPy; prefer `.to_numpy()`.) |
| Drop defensive `.copy()` calls | Copies added only to silence `SettingWithCopyWarning` are wasted work under CoW. |
| Reassign instead of holding stale references | A lingering `df2 = df.reset_index()` forces a defensive copy on the next write; `df = df.reset_index(drop=True)` invalidates the old reference and recovers inplace-like performance. |
| Constructors copy NumPy input by default | `pd.Series(arr)` copies `arr`; pass `copy=False` to share when you control the source array. |

## Indexing correctness

| Practice | Detail |
|---|---|
| `.loc` for labels, `.iloc` for positions, never chained `[]` for assignment | `df.loc[mask, "B"] = 100`, not `df[mask]["B"] = 100`. |
| Know that slice semantics differ | `.loc["a":"f"]` includes both ends (label slice); `.iloc[1:5]` excludes the stop (positional). A common off-by-one. |
| Use `.at`/`.iat` for a single scalar | Faster than `.loc`/`.iloc` for one cell. |
| Parenthesize boolean masks; use `&`/`\|`/`~` | `df[(df.A > 2) & (df.B < 3)]`; Python `and`/`or` do not vectorize, and the operators bind wrong without parentheses. |
| Do not create columns by attribute | `df.new = [...]` sets an attribute, not a column; use `df["new"] = [...]`. |

## Vectorization

Documented speed order, fastest to slowest: vectorized ops, then Numba/Cython, then `eval`/`query` on large frames, then `apply(axis=1)`, then `iterrows`/`itertuples`. Cython examples reach ~80-100x over pure-Python `apply`.

| Practice | Detail |
|---|---|
| Vectorize first; loop last | `apply(axis=1)`/`iterrows` build a Python object per row. Row loops are the last resort, not the first reach. |
| Use the `.str` and `.dt` accessors | `s.str.contains(...)`, `s.dt.year` dispatch to vectorized kernels; never `s.apply(lambda x: x.year)`. |
| Replace row conditionals with `np.where`/`np.select`/`.map` | Branch-free vectorized assignment; `df["k"].map(lookup)` for table lookups, a `merge` for table-driven enrichment instead of per-row lookups. |
| If you must `apply` over rows, pass `raw=True` | Passes a NumPy array instead of constructing a Series per row; still slower than true vectorization. |

## dtypes and memory

| Practice | Detail |
|---|---|
| Set dtypes at read time | `read_csv(path, dtype={"sku": str, "amt": "float32"}, parse_dates=["ts"])`; `dtype=str` on identifier columns keeps leading zeros and stops IDs becoming floats. |
| Use nullable dtypes for columns that can be missing | NumPy `int64` cannot hold NA, so a missing integer silently upcasts to float; `Int64`/`boolean` keep the logical type with `pd.NA`. |
| Use `category` for low-cardinality text | Large memory win on repetitive strings: `df["region"] = df["region"].astype("category")`. Worth it for string-heavy columns since strings are already on the slow path. |
| Consider the PyArrow backend | `read_parquet(path, dtype_backend="pyarrow")` or `.convert_dtypes(dtype_backend="pyarrow")` gives compact, NA-aware, fast types with zero-copy interop to polars and duckdb. `dtype_backend` also takes `"numpy_nullable"`. |
| Measure with `memory_usage(deep=True)` | `deep=True` counts object-string payloads the shallow estimate misses; downcast numerics with `pd.to_numeric(s, downcast=...)` when range allows. |

## Method chaining

| Practice | Detail |
|---|---|
| Build transforms as one chain, not reassigned intermediates | No temp variables to drift, no inplace mutation, top-to-bottom readability, cheap under CoW. `.assign(col=...)` to add columns, `.loc[lambda d: ...]` to filter mid-chain, `.pipe(fn)` for a multi-line step. |
| Reference current-frame columns without binding a name | Pass a callable: `.assign(c=lambda d: d.a + d.b)`, or in 3.0 the new `pd.col`: `.assign(c=pd.col("a") + pd.col("b"))`. Either sees the frame as it is at that step, avoiding chained assignment. |
| Reserve `.pipe` for genuinely multi-line logic | Fragmenting one-liners into many pipes adds overhead without readability. |
| Split the chain to debug | Insert a temporary `.pipe(lambda d: (print(d.shape), d)[1])` or break the chain while diagnosing, then recombine. |

## Merge, join, concat

| Practice | Detail |
|---|---|
| Always pass `validate=` | `merge(left, right, on="key", validate="one_to_many")` catches unexpected many-to-many duplication that silently multiplies rows (a Cartesian blow-up, possible OOM). |
| Audit coverage with `indicator=True` | The `_merge` column (`left_only`/`right_only`/`both`) reveals unmatched keys and silent data loss. |
| Align key dtypes before merging | `int` vs `str`, or NumPy `int64` vs nullable `Int64`, keys do not match and produce empty or wrong joins; cast both sides first. |
| Be explicit with `how=` and `suffixes=` | Default `how="left"`; set meaningful suffixes instead of the default `_x`/`_y`. |
| `concat` to stack, once | `pd.concat` makes a full copy; collect frames into a list and concat once, never `result = pd.concat([result, chunk])` per iteration. |
| `merge_asof` for nearest-key time joins | Sort both sides first; supports `by=`, `tolerance=`, `allow_exact_matches=`. |

## groupby

| Practice | Detail |
|---|---|
| Pass `observed=True` on categoricals | `observed=False` materializes every category combination, exploding output and memory; set it explicitly. |
| Be intentional about `dropna=` | The default drops NA group keys; `dropna=False` keeps a missing-key group and avoids silent row loss. |
| Use named aggregation | `.agg(avg_w=("weight", "mean"))` gives clean columns instead of an opaque MultiIndex from `.agg(["min","mean"])`. |
| Pick the right verb | `aggregate` reduces to one row per group; `transform` preserves shape (group z-score: `(s - g.transform("mean")) / g.transform("std")`); `apply` is the slow flexible fallback. Avoid `groupby.apply` when a built-in or `transform` exists. |
| Select columns before aggregating | `df.groupby("A")["C"].std()` computes only `C`; add `sort=False` when group order does not matter. |

## Missing data

| Practice | Detail |
|---|---|
| Detect with `isna()`/`notna()`, never `==` | `np.nan != np.nan`, `pd.NaT != pd.NaT`, and `pd.NA == pd.NA` returns `<NA>`, not a bool. |
| Know the sentinel per dtype | NumPy numeric uses `np.nan` (forces float or object); datetime/timedelta uses `NaT`; nullable and Arrow dtypes use `pd.NA`. The 3.0 default `str` dtype uses `NaN`, not `pd.NA`. |
| Never put `pd.NA` in an `if` | `bool(pd.NA)` raises; `pd.NA` uses three-valued logic (`True \| pd.NA` is True, `False \| pd.NA` is `<NA>`). |
| Check the NA rate after `errors="coerce"` | Coercion silently turns unparsable values into NaN/NaT; validate with `s.isna().mean()` or log dropped counts. |
| Aggregations skip NA by default | `sum` of all-NA is 0.0; pass `skipna=False` to propagate. |

## Datetime and time series

| Practice | Detail |
|---|---|
| Parse with an explicit `format=` | Inference is slow and mis-parses ambiguous dates; `format="mixed"` for heterogeneous strings, `errors="coerce"` yields `NaT`. 3.0 parses to `datetime64[us]` by default, not `[ns]`. |
| Distinguish localize vs convert | `tz_localize` attaches a zone to naive timestamps; `tz_convert` changes the zone on aware ones; mixing naive and aware raises. Reading as UTC (`utc=True`) sidesteps DST ambiguity. 3.0 uses `zoneinfo`, not `pytz`. |
| Use `.dt` for vectorized fields | `s.dt.year`, `s.dt.day_name()`, `s.dt.is_month_end` instead of `apply`. |
| `resample` for frequency change, `rolling` for sliding windows | `ts.resample("5min").mean()`; be explicit about `closed=`/`label=` on `ME`/`QE`/`W` to avoid look-ahead. |
| Use the current offset aliases | `ME`/`QE`/`YE`/`D`/`B`, not the removed `M`/`Q`/`Y`/`BM`. |

## Reading and writing

| Practice | Detail |
|---|---|
| Prefer Parquet over CSV | Typed, columnar, compressed, with column push-down: `read_parquet(path, columns=["a","b"])` reads only those columns; CSV must read all then subset. |
| Read only the columns you need | `usecols=` (CSV) / `columns=` (Parquet); large memory cuts. `usecols` ignores order, so reselect with `[[...]]` afterward. |
| Control NA and types at read | `dtype=`, `parse_dates=`, `na_values=`; the `low_memory` chunk-inference flag is removed in 3.0. |
| Chunk large CSVs | `read_csv(path, chunksize=N)` for sequential aggregations; a complex groupby is the signal to switch tools. |

## Scaling and switching tools

| Practice | Detail |
|---|---|
| Use `eval`/`query` on large multi-term expressions | `df.query("a < b and b < c")`, `pd.eval(...)` fuse ops via numexpr. The docs put the break-even near ~100k-200k rows; below ~10k rows plain Python is faster. Reference locals with `@threshold` in `query`/`eval` (not in top-level `pd.eval`). |
| Switch tools when pandas is the wrong fit | Larger-than-memory or heavy out-of-core joins route to polars or duckdb (SQL-shaped); Dask for distributed. Hand off zero-copy through Arrow. |
| Profile before optimizing | `%prun` to find the bottleneck, vectorize the hot path, consider Numba/Cython only if still slow. |

## Gotchas

- Stop using APIs removed in 3.0: `df.append` -> `pd.concat`; `df.applymap` -> `df.map`; `M`/`Q`/`Y` -> `ME`/`QE`/`YE`; `Index.sort()` -> `Index.sort_values()`.
- The 3.0 default `str` dtype holds only strings or NA; `df["s"] = 2.5` raises `TypeError`, and `dtype == object` checks on strings break (use `pd.api.types.is_string_dtype`). Pass `dtype="object"` only for genuinely mixed cells.
- `astype(str)` on a string column now preserves NA instead of producing the literal `"nan"`.
- Do not mutate while iterating; the vectorized replacement is almost always `np.where`/`np.select`/`merge`/`map`.
- Arithmetic and `.loc` assignment align on index and columns (mismatches inject NaN); use `.to_numpy()` or `.iloc` for positional behavior.
- A missing integer in a NumPy `int64` column silently upcasts the whole column to float; reach for `Int64`.

## Sources

- [pandas user guide: Copy-on-Write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html) and [Migration guides](https://pandas.pydata.org/docs/user_guide/migration.html) - official; the authoritative CoW contract and 2.x-to-3.0 migration steps.
- [What's new in 3.0.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) and [string dtype migration](https://pandas.pydata.org/docs/user_guide/migration-3-strings.html) - official release notes; default `str` dtype, `pd.col`, removed APIs, datetime/tz changes.
- [Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html) - official; vectorization vs apply vs eval/query vs Cython/Numba ordering, speedups, and the eval row threshold.
- [PyArrow functionality](https://pandas.pydata.org/docs/user_guide/pyarrow.html) and [scaling to large datasets](https://pandas.pydata.org/docs/user_guide/scale.html) - official; `dtype_backend`, Arrow-backed types, chunking and when to switch tools.
- [Modern Pandas (Tom Augspurger)](https://tomaugspurger.net/posts/method-chaining/) - core pandas maintainer; method chaining, indexing, and avoiding row-wise apply.
- [Effective Pandas (Matt Harrison)](https://store.metasnake.com/effective-pandas-book) - widely cited practitioner book; chaining as default, inplace as anti-pattern, categorical for memory.
