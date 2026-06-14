Apply these practices whenever planning, writing, or reviewing NumPy numerical code. Targets current NumPy (2.x). Generic clean-code and naming rules live in CLAUDE.md; this reference is the NumPy-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Vectorization and broadcasting](#vectorization-and-broadcasting)
- [Views, copies, and memory](#views-copies-and-memory)
- [dtypes and numeric correctness](#dtypes-and-numeric-correctness)
- [Random numbers](#random-numbers)
- [Selection, reduction, and conditionals](#selection-reduction-and-conditionals)
- [Building arrays](#building-arrays)
- [Performance](#performance)
- [NumPy 2.0 migration](#numpy-20-migration)
- [Testing numerical code](#testing-numerical-code)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Vectorization and broadcasting

| Practice | Detail |
|---|---|
| Replace Python loops with array operations | ufuncs and array ops run the loop in C; the docs measure roughly 30x for a column sum (`arr.sum(axis=0)`) over nested Python loops. A Python `for` loop over a NumPy array is the signal you skipped vectorizing. |
| Know the broadcasting rule exactly | NumPy compares shapes from the trailing dimension leftward; two dimensions are compatible when equal or one is 1, and missing leading dimensions are treated as 1. `(4,3) + (4,)` raises; add a length-4 column vector with `a + b[:, None]`. |
| Insert axes explicitly with `np.newaxis`/`None` | `a[:, None] + b[None, :]` makes the outer combination unambiguous instead of relying on implicit alignment that may pair the wrong axis. `np.expand_dims` does the same by axis number. |
| Watch for oversized broadcast temporaries | Broadcasting an `N x M x K` cross-product can exceed RAM and swap; the docs explicitly note broadcasting can use unnecessarily large memory. For very large fan-outs, loop over blocks, which is both more memory-efficient and clearer than one giant intermediate. |
| Avoid `np.matrix` | It is no longer recommended even for linear algebra and may be removed; use a regular `ndarray` with `@` for matrix products. `np.matrix` overloads `*` as matmul, silently breaking code that expects elementwise. |

## Views, copies, and memory

| Practice | Detail |
|---|---|
| Basic slicing returns a view, advanced indexing returns a copy | `x[2:7]` shares memory with `x` so mutations propagate; `x[[1,3,5]]` and `x[x>5]` are independent copies. This is the top source of "why did/didn't my array change" bugs; confirm with `y.base is None` (None means copy, otherwise `.base` is the parent). |
| Treat in-place ops on a slice as mutating the parent | `y = x[1:3]; y += 100` also changes `x[1:3]`. Take `x[1:3].copy()` when you need independence. |
| Copy a small slice out of a large array you will discard | A view holds a reference to the entire parent buffer, so a tiny slice keeps a huge array alive and blocks its garbage collection: `small = large[:100].copy()`. |
| Know which operations view vs copy | `reshape`/`ravel`/`.T` view when possible; `flatten` always copies; `.T` swaps strides so the result is often non-contiguous. Call `np.ascontiguousarray(a)` before hot kernels that need C-contiguous data. |
| Fancy-index assignment does not accumulate duplicates | `x[[1,1,1]] += 1` reads a temporary, adds once, writes back once, so it increments by 1, not 3. Use `np.add.at(x, idx, 1)` for true unbuffered accumulation. |

## dtypes and numeric correctness

| Practice | Detail |
|---|---|
| Fixed-width integers overflow silently | NumPy ints wrap with no warning (`np.int8(300)` is 44). Check ranges with `np.iinfo`, widen the accumulator on reductions (`arr.sum(dtype=np.int64)`), and cast up before large products. |
| Never compare floats with `==` | Floating point is inexact (`0.3 - 0.2 - 0.1` is not 0). Use `np.isclose` / `np.allclose` with tolerance `atol + rtol*|b|`. |
| Handle NaN and inf explicitly | `np.nan != np.nan`, and a single NaN poisons a reduction. Detect with `np.isnan`/`np.isfinite`, mask with `x[~np.isnan(x)]`, or use the nan-aware reductions `np.nansum`/`np.nanmean`/`np.nanmax`. `arr == np.nan` is always False. |
| Combine masks with `&`, `\|`, `~`, never `and`/`or` | Python boolean keywords evaluate the array's truth value and raise "ambiguous truth value"; use parenthesized bitwise operators: `(a > 2) & (a < 5)`. |
| Avoid object dtype | `object` arrays store Python objects and lose all vectorization; they usually arise by accident from ragged or mixed data. Keep homogeneous numeric dtypes. |
| float64 is the safe default | Drop to float32 only when memory-bound and the precision loss is acceptable; inspect precision with `np.finfo`. Long reductions in float32 accumulate error. |

## Random numbers

| Practice | Detail |
|---|---|
| Use the Generator API, not the legacy global functions | `rng = np.random.default_rng(seed)` then `rng.standard_normal(n)` / `rng.integers(0, 10, n)` / `rng.random(n)`. The legacy `np.random.seed` / `np.random.rand` use the older MT19937 algorithm and shared global state; all future improvements target `Generator`, and the global state makes code non-modular and order-dependent. |
| Seed for reproducibility, but know it is not cryptographic | A fixed seed makes runs deterministic; for security use the `secrets` module, not NumPy PRNGs. For a fresh high-quality seed, `secrets.randbits(128)`. |
| Derive independent parallel streams with `SeedSequence` | `[np.random.default_rng(s) for s in np.random.SeedSequence(entropy).spawn(n)]`; naively adjacent integer seeds can produce correlated streams. `default_rng` uses `PCG64`; use `PCG64DXSM` for massive parallelism. |

## Selection, reduction, and conditionals

| Practice | Detail |
|---|---|
| Reduce along an axis, not with loops | `arr.sum(axis=0)`, `arr.mean(axis=1, keepdims=True)`; `axis=0` collapses rows (down columns), `axis=1` collapses columns (across rows). `keepdims=True` preserves rank for later broadcasting. |
| `np.where` for two-way, `np.select` for multi-way | `np.where(cond, a, b)`; `np.select([c1, c2], [v1, v2], default)` reads cleaner than nested `where`. Both vectorize an if/elif chain. |
| Filter with boolean masks | `arr[arr.sum(-1) <= 2]` selects rows by predicate; boolean indexing returns a copy. |
| Use `np.einsum` for explicit contractions | One subscript string expresses matmul (`'ij,jk->ik'`), diagonal, and batched matmul; pass `optimize='greedy'` for multi-operand. For a plain matrix product, `@` / `np.matmul` is clearer and dispatches to BLAS. |

## Building arrays

| Practice | Detail |
|---|---|
| Preallocate and fill; never grow in a loop | `np.append` / `np.concatenate` inside a loop reallocate and copy the whole array each iteration (O(n^2) overall). Preallocate `out = np.empty(n)` and assign by index, or collect into a Python list and `np.array(list)` once. |
| Join known chunks in one call | `np.concatenate(list, axis=0)` joins along an existing axis; `np.stack(list, axis=0)` adds a new axis; `np.vstack`/`np.hstack` for the 2-D cases. |

## Performance

| Practice | Detail |
|---|---|
| Eliminate temporaries with `out=` and in-place ops | `G = A * B; np.add(G, C, out=G)` (or `G += C`) avoids the intermediate that `A*B + C` allocates each pass in a tight loop. |
| Mind memory layout for hot loops | NumPy is C-order (row-major) by default; iterate and reduce along the last axis for cache locality, and pass `order='F'` only when feeding column-major consumers (some BLAS/LAPACK paths). A `.T` flips the effective order, so a transposed array's "rows" are strided. |
| Compute only selected positions with `where=` | `np.add(a, b, where=cond, out=buf)` skips masked elements; pre-fill `out` because `where=False` positions are left untouched (garbage if `out` came from `np.empty`). |
| Escalate past vectorized NumPy deliberately | Start with vectorization; reach for Numba `@njit` when a real loop is unavoidable and the design is still moving; Cython for a long-lived shippable kernel. If data exceeds RAM, chunked loops can beat vectorization, which would swap. |

## NumPy 2.0 migration

| Practice | Detail |
|---|---|
| Use canonical dtype names | Removed aliases: `np.float_`->`np.float64`, `np.int_`->`np.intp`, `np.unicode_`->`np.str_`, `np.string_`->`np.bytes_`, `np.complex_`->`np.complex128`. The Ruff `NPY201` rule auto-fixes most 2.0 breakages. |
| Use canonical constants and functions | `np.Inf`/`np.NaN`->`np.inf`/`np.nan`; `np.alltrue`->`np.all`, `np.product`->`np.prod`, `np.row_stack`->`np.vstack`, `np.in1d`->`np.isin`, `np.trapz`->`np.trapezoid`. |
| Account for NEP 50 scalar promotion | `np.float32(3) + 3.0` stays float32 in 2.0 (was float64 in 1.x); cast explicitly when you need the wider type. Debug with `np._set_promotion_state("weak_and_warn")`. |
| Know the new `copy=` semantics | In 2.0 `np.array(x, copy=False)` means never copy and raises if a copy is required; use `np.asarray(x)` for "view if possible, else copy". |

## Testing numerical code

| Practice | Detail |
|---|---|
| Compare floats with `assert_allclose` | `np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-12)`; the docs recommend it over `assert_almost_equal`. Set `atol` explicitly near zero, since the default `atol=0` fails the relative check there. |
| Use `assert_array_equal` for exact integer or bool checks | Tolerance is meaningless for integers. |
| Seed every stochastic test with the Generator API | Construct `rng = np.random.default_rng(SEED)` inside the test, never the global `np.random`, so failures reproduce. |

## Gotchas

- Basic slicing is a view, fancy/boolean indexing is a copy; mutating the wrong one silently does nothing (or silently corrupts the parent). Check with `.base`.
- `x[[1,1,1]] += 1` increments by 1, not 3; use `np.add.at` for duplicate-index accumulation.
- `arr == np.nan` is always False, and one NaN poisons a whole reduction; use `np.isnan` and the `nan*` reductions.
- `(a > 2) and (a < 5)` raises "ambiguous truth value"; use `&`/`|`/`~` with parentheses.
- Fixed-width ints wrap silently (`np.int8(300)` is 44); widen the accumulator dtype on reductions.
- `np.append`/`np.concatenate` in a loop is O(n^2); preallocate or collect-then-convert once.
- NEP 50 keeps `np.float32(3) + 3.0` as float32 in 2.x; cast up if you need float64.
- `np.matrix` overloads `*` as matmul and is on the way out; use `ndarray` with `@`.

## Sources

- [NumPy user guide: broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html), [copies and views](https://numpy.org/doc/stable/user/basics.copies.html), [absolute basics](https://numpy.org/doc/stable/user/absolute_beginners.html) - official docs; the authoritative rules for broadcasting, view/copy semantics, axes, and dtypes.
- [NumPy random sampling guide](https://numpy.org/doc/stable/reference/random/index.html) and [Generator reference](https://numpy.org/doc/stable/reference/random/generator.html) - official; the modern `default_rng`/`Generator` API, PCG64, and `SeedSequence.spawn`.
- [NumPy 2.0 migration guide](https://numpy.org/doc/stable/numpy_2_0_migration_guide.html) - official; removed aliases/constants/functions, NEP 50 promotion, `copy=` semantics, and the Ruff `NPY201` rule.
- [numpy.matrix reference](https://numpy.org/doc/stable/reference/generated/numpy.matrix.html) - official; the explicit note that `np.matrix` is no longer recommended and may be removed.
- [Best Practices for Using NumPy's Random Number Generators](https://blog.scientific-python.org/numpy/numpy-rng/) - Scientific Python project blog; why isolated generators beat the global `np.random.seed` and how to spawn independent streams.
- [np.testing assert functions](https://numpy.org/doc/stable/reference/routines.testing.html) - official; `assert_allclose` vs `assert_array_equal` for comparing numerical results in tests.
