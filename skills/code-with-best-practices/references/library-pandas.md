Apply these practices whenever planning, writing, or reviewing pandas data code. They sit on top of the general Python practices; this file covers pandas-specific idioms, the Copy-on-Write model, correctness traps, and performance. Write to the pandas 3.0 contract (Copy-on-Write, and a PyArrow-backed default string dtype), which is forward-compatible from 2.2.

## Contents

- Copy-on-Write
- Indexing Correctness
- Vectorization
- dtypes and Memory
- Method Chaining
- Merge, Join, Concat
- groupby
- Missing Data
- Datetime and Time Series
- Reading and Writing
- Scaling and Switching Tools
- Removed APIs and Anti-Patterns

## Copy-on-Write

Copy-on-Write (CoW) is the default and only mode in pandas 3.0 and opt-in via `pd.options.mode.copy_on_write` in 2.2. Any object derived from another behaves as a copy, so mutating it never touches the parent; copies happen lazily, only on the first write.

| Practice | Detail |
|---|---|
| Migrate on 2.2 with warn mode before upgrading | `pd.options.mode.copy_on_write = "warn"` surfaces the patterns that change behavior so you can fix them before the 3.0 default lands. |
| Never chained-assign; use `.loc` | `df["foo"][cond] = x` writes to an intermediate copy and raises `ChainedAssignmentError` under CoW. Write `df.loc[cond, "foo"] = x`, which updates one object in one step. |
| Avoid `inplace=True` | On a derived Series (`df["foo"].replace(1, 5, inplace=True)`) it updates nothing under CoW, and inplace rarely saves memory. Reassign: `df["foo"] = df["foo"].replace(1, 5)`, or operate on the whole frame. |
| Treat `.to_numpy()` / `.values` as read-only | For single-dtype frames CoW returns a read-only view; call `df.to_numpy().copy()` when you need to mutate the array. |
| Drop defensive `.copy()` calls | Copies added only to silence `SettingWithCopyWarning` are wasted work under CoW, and the warning is gone. |
| Reassign instead of holding stale references | A lingering `df2 = df.reset_index()` forces a defensive copy on the next write; `df = df.reset_index(drop=True)` invalidates the old reference and keeps the write cheap. This recovers inplace-like performance. |

## Indexing Correctness

| Practice | Detail |
|---|---|
| `.loc` for labels, `.iloc` for positions, never chained `[]` for assignment | Chained `[]` writes to a copy: `df.loc[mask, "B"] = 100`, not `df[mask]["B"] = 100`. |
| Know that slice semantics differ | `.loc["a":"f"]` includes both ends (label slice); `.iloc[1:5]` excludes the stop (positional). Mixing them up is a common off-by-one. |
| Use `.at`/`.iat` for a single scalar | Faster than `.loc`/`.iloc` for one cell. |
| Parenthesize boolean masks; use `&`/`\|`/`~` | `df[(df.A > 2) & (df.B < 3)]`; Python `and`/`or` do not vectorize, and the operators bind wrong without parentheses. |
| Do not create columns by attribute | `df.new = [...]` sets an attribute, not a column; use `df["new"] = [...]`. |

## Vectorization

The documented speed order, fastest to slowest: vectorized ops, then `eval`/`query` on large frames, then Numba/Cython, then `apply(axis=1)`, then `iterrows`/`itertuples`.

| Practice | Detail |
|---|---|
| Vectorize first; loop last | `apply(axis=1)`/`iterrows` build a Python object per row; the docs show `df["a"]*2` at ~3.4x over the `apply` equivalent and far more on real row logic. |
| Use the `.str` and `.dt` accessors | `s.str.contains(...)`, `s.dt.year` dispatch to vectorized kernels; never `s.apply(lambda x: x.year)`. |
| Replace row conditionals with `np.where`/`np.select`/`.map` | Branch-free vectorized assignment; `df["k"].map(lookup)` for table lookups, a `merge` for table-driven enrichment instead of per-row lookups. |
| If you must `apply` over rows, pass `raw=True` | Passes a NumPy array instead of constructing a Series per row; still slower than true vectorization. |

## dtypes and Memory

| Practice | Detail |
|---|---|
| Set dtypes at read time | `read_csv(path, dtype={"sku": str, "amt": "float32"}, parse_dates=["ts"])`; `dtype=str` on identifier columns keeps leading zeros and stops IDs becoming floats. |
| Use nullable dtypes for columns that can be missing | NumPy `int64` cannot hold NA, so a missing integer silently upcasts to float; `Int64`/`boolean`/`string` keep the logical type with `pd.NA`. |
| Use `category` for low-cardinality text | Large memory win (docs cite ~13x on repetitive strings): `df["region"] = df["region"].astype("category")`. |
| Consider the PyArrow backend | `read_parquet(path, dtype_backend="pyarrow")` or `.convert_dtypes(dtype_backend="pyarrow")` gives compact, NA-aware, fast types with zero-copy interop to polars and duckdb. |
| Measure with `memory_usage(deep=True)` | `deep=True` counts object-string payloads the shallow estimate misses; downcast numerics with `pd.to_numeric(s, downcast=...)` when range allows. |

## Method Chaining

| Practice | Detail |
|---|---|
| Build transforms as one chain, not reassigned intermediates | No temp variables to drift, no inplace mutation, top-to-bottom readability, cheap under CoW. Use `.assign(col=lambda d: ...)` to add columns, `.loc[lambda d: ...]` to filter mid-chain, `.pipe(fn)` for a multi-line step. |
| Pass callables in `.assign`/`.loc` | A lambda sees the current frame, so each step can reference columns created earlier in the chain without binding a name or risking chained assignment. |
| Reserve `.pipe` for genuinely multi-line logic | Fragmenting one-liners into many pipes adds cognitive overhead without readability. |
| Split the chain to debug | Insert a temporary `.pipe(lambda d: (print(d.shape), d)[1])` or break the chain while diagnosing, then recombine. |

## Merge, Join, Concat

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

## Missing Data

| Practice | Detail |
|---|---|
| Detect with `isna()`/`notna()`, never `==` | `np.nan != np.nan`, `pd.NaT != pd.NaT`, and `pd.NA == pd.NA` returns `<NA>`, not a bool. |
| Know the sentinel per dtype | NumPy numeric uses `np.nan` (forces float or object); datetime/timedelta uses `NaT`; nullable and Arrow dtypes use `pd.NA` (preserves dtype). |
| Never put `pd.NA` in an `if` | `bool(pd.NA)` raises; `pd.NA` uses three-valued logic (`True \| pd.NA` is True, `False \| pd.NA` is `<NA>`). |
| Check the NA rate after `errors="coerce"` | Coercion silently turns unparsable values into NaN/NaT; validate with `s.isna().mean()` or log dropped counts. |
| Aggregations skip NA by default | `sum` of all-NA is 0.0; pass `skipna=False` to propagate. |

## Datetime and Time Series

| Practice | Detail |
|---|---|
| Parse with an explicit `format=` | Inference is slow and mis-parses ambiguous dates; `format="mixed"` for heterogeneous strings, `errors="coerce"` yields `NaT`. |
| Distinguish localize vs convert | `tz_localize` attaches a zone to naive timestamps; `tz_convert` changes the zone on aware ones; mixing naive and aware raises. Reading as UTC (`utc=True`) sidesteps DST ambiguity. |
| Use `.dt` for vectorized fields | `s.dt.year`, `s.dt.day_name()`, `s.dt.is_month_end` instead of `apply`. |
| `resample` for frequency change, `rolling` for sliding windows | `ts.resample("5min").mean()`; be explicit about `closed=`/`label=` on `ME`/`QE`/`W` to avoid look-ahead. |
| Use the current offset aliases | `ME`/`QE`/`YE`/`D`/`B`, not the removed `M`/`Q`/`Y`. |

## Reading and Writing

| Practice | Detail |
|---|---|
| Prefer Parquet over CSV | Typed, columnar, compressed, with column push-down: `read_parquet(path, columns=["a","b"])` reads only those columns; CSV must read all then subset. |
| Read only the columns you need | `usecols=` (CSV) / `columns=` (Parquet); documented ~90% memory cuts. `usecols` ignores order, so reselect with `[[...]]` afterward. |
| Control NA and types at read | `dtype=`, `parse_dates=`, `na_values=`; beware the default `low_memory=True` producing mixed int/str across chunks. |
| Chunk large CSVs | `read_csv(path, chunksize=N)` for sequential aggregations; a complex groupby is the signal to switch tools. |

## Scaling and Switching Tools

| Practice | Detail |
|---|---|
| Use `eval`/`query` on large multi-term expressions | `df.query("a < b and b < c")`, `pd.eval(...)` fuse ops via numexpr above ~100-200k rows; below that plain Python is faster. Reference locals with `@threshold`. |
| Switch tools when pandas is the wrong fit | Larger-than-memory or heavy out-of-core joins route to polars or duckdb (SQL-shaped); Dask for distributed. Hand off zero-copy through Arrow. |
| Profile before optimizing | `%prun` to find the bottleneck, vectorize the hot path, consider Numba/Cython only if still slow. |

## Removed APIs and Anti-Patterns

| Practice | Detail |
|---|---|
| Stop using APIs removed in 3.0 | `df.append`->`pd.concat`; `df.applymap`->`df.map`; offset aliases `M`/`Q`/`Y`->`ME`/`QE`/`YE`; `Index.sort()`->`Index.sort_values()`. |
| Account for the default string dtype change (3.0) | Default string columns are PyArrow-backed `str`, not `object`; `dtype == object` checks on strings break (use `pd.api.types.is_string_dtype`). Pass `dtype="object"` only when you genuinely need mixed-type cells. |
| Do not mutate while iterating | Build a new column and assign once; the vectorized replacement is almost always `np.where`/`np.select`/`merge`/`map`. |
| Remember index alignment | Arithmetic and `.loc` assignment align on index and columns (mismatches inject NaN); use `.to_numpy()` or `.iloc` for positional behavior. |
