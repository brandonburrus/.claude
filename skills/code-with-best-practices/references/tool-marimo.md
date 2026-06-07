Apply these practices whenever planning, writing, or reviewing marimo notebooks. marimo is a reactive notebook stored as a pure `.py` file; this file covers its model, constraints, and idioms. Grounded in the marimo docs (~0.23.x); confirm exact CLI flags with `marimo <command> --help` on your installed version.

## Contents

- The Reactive Model
- Working Within the Constraints
- Structuring Cells
- Interactivity and State
- Expensive Notebooks
- Packages and Reproducibility
- Running, Exporting, Deploying
- Testing
- SQL and DataFrames
- Migrating from Jupyter

## The Reactive Model

| Practice | Detail |
|---|---|
| Let dependencies drive execution, not cell order | marimo statically reads each cell's referenced and defined globals to build a DAG, then re-runs every cell that references a changed cell's outputs, with zero runtime tracing overhead. This eliminates the out-of-order-execution bugs that make roughly a third of public Jupyter notebooks non-reproducible. |
| Treat deleting a cell as deleting its state | marimo removes a deleted cell's globals from memory and re-runs or invalidates dependents, so there are no orphaned references to ghosts. |

## Working Within the Constraints

| Practice | Detail |
|---|---|
| Define every global in exactly one cell | A name defined in two cells raises a multiple-definitions error (marimo could not order them); split or merge cells so each name has one definition site. |
| Reassign rather than mutate across cells | marimo does not track in-place mutation (`list.append`, `obj.attr = ...`); mutate in the same cell as the definition, or build a new value (`extended = lst + [2]`). |
| Never create cross-cell cycles | If cell A defines `a` and reads `b`, another cannot define `b` and read `a` (cycle error); restructure into a topological order. Deliberate runtime cycles use `mo.state` only. |
| Use explicit imports, never `import *` | Wildcard imports defeat the static analysis of definitions and raise an import-star error. |
| Prefix throwaway names with `_` | `_tmp` is cell-local, so the same name can be reused across cells without collision or polluting the global namespace. |
| Quote cell-reference type annotations | A non-string annotation is treated as a cell reference and pulled into the dataflow graph; write it as a string. |

## Structuring Cells

| Practice | Detail |
|---|---|
| Encapsulate throwaway logic in a function | `def _(): ...; _()` keeps intermediates out of the global namespace and lets them be garbage-collected. |
| Write idempotent cells | Same inputs, same output and behavior; this enables caching and avoids order-dependent bugs. |
| Split long notebooks into modules | Move stable logic into helper `.py` files and import them; marimo autoreloads module edits. |
| Use descriptive global names | Globals are the dataflow edges, so clear names mean fewer collisions and clearer dependencies. |

## Interactivity and State

| Practice | Detail |
|---|---|
| Assign each UI element to a global, read `.value` in another cell | Interacting re-runs cells that reference the variable but not the defining cell, so reading `.value` in the cell that creates the widget never updates. Put the widget in one cell, consume `.value` downstream. |
| Compose runtime-unknown widget sets with `mo.ui.array`/`mo.ui.dictionary` | Use them when you cannot bind each element to its own global; `.value` aggregates the children. |
| Gate expensive updates with `mo.ui.form` | It defers value updates until submission, so dependents do not re-run on every keystroke. |
| Avoid `mo.state` and `on_change` in nearly all cases | UI elements already carry state via `.value` and reactivity handles updates; `mo.state` introduces hard-to-find bugs. Reserve it for derived history, tied/synchronized elements, or deliberate cycles. |

## Expensive Notebooks

| Practice | Detail |
|---|---|
| Switch the runtime to lazy when autorun is too eager | Configure "on cell change: lazy" (mark cells stale instead of running them) and disable autorun on startup; these are runtime settings, not code. |
| Gate heavy cells with `mo.stop` and a run button | `run = mo.ui.run_button(); mo.stop(not run.value)` short-circuits everything below the cell until clicked. |
| Cache pure expensive functions | `@mo.cache` (in-memory, keys include closed-over globals), `@mo.persistent_cache` (disk, pickle-serializable, survives restart), `@mo.lru_cache(maxsize=...)`. Side effects are not cached. |
| Disable cells while iterating | A disabled cell and its dependents are blocked from running; re-enabling runs it if an ancestor changed in the meantime. |

## Packages and Reproducibility

| Practice | Detail |
|---|---|
| Edit reproducible notebooks in sandbox mode | `uvx marimo edit --sandbox notebook.py` runs in an isolated venv and records dependencies as PEP 723 inline metadata in the file header, so the notebook is shareable without a separate requirements file. Requires `uv`. |
| Keep the inline script-metadata header with the file | marimo writes `# /// script ... ///` deps via `uv add --script`; removing an import does not remove the dep, so prune with `uv remove --script notebook.py <pkg>` when needed. |

## Running, Exporting, Deploying

| Practice | Detail |
|---|---|
| Use the right run mode | `marimo edit` (reactive editor), `marimo run notebook.py` (read-only app, code hidden), `python notebook.py` (top-to-bottom script, good for side effects), `marimo check` (static lint). |
| Export for the audience | `marimo export html` (static snapshot), `html-wasm` (self-contained interactive, no server), `ipynb`, `script`, `md`. Include the `layouts/` folder when sharing a grid or slides app. |
| Treat `marimo run` as not a sandbox | App mode hides code but can still execute the notebook's code through the UI; pair with `--sandbox` and the default token auth for untrusted exposure. |

## Testing

| Practice | Detail |
|---|---|
| Test notebooks with pytest directly | Cells are functions, so `pytest test_notebook.py` works and a test cell can take another cell's def as a parameter. marimo only collects cells that are exclusively test code; because pytest collects statically, a fixture defined in one cell cannot be used by tests in another, so put fixtures in the setup cell or a `conftest.py`. |

## SQL and DataFrames

| Practice | Detail |
|---|---|
| Use `mo.sql` / SQL cells over DuckDB | Reference Python dataframes by name in the query; f-string interpolation of `{ui.value}` puts the SQL cell into the reactive DAG. The output type is configurable (the native DuckDB relation is fastest). |
| Return a dataframe as the last expression for the interactive viewer | `mo.ui.table(df, selection="multi")` exposes the selection via `.value`; `mo.ui.dataframe(df)` is a no-code transform GUI that shows the generated code. |

## Migrating from Jupyter

| Practice | Detail |
|---|---|
| Convert, then fix the three constraint violations | `marimo convert nb.ipynb -o nb.py`, then resolve redefinitions (one cell per global), cross-cell mutations (combine or reassign), and cycles. Set the runtime to lazy at first if the auto-rerun feels aggressive. |
