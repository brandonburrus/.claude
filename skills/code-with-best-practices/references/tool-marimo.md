Apply these practices whenever planning, writing, or reviewing marimo notebooks. Targets marimo 0.x (current series; confirm exact CLI flags with `marimo <command> --help` on your installed version). Generic clean-code and naming rules live in CLAUDE.md; this reference is the marimo-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [The reactive model](#the-reactive-model)
- [Working within the constraints](#working-within-the-constraints)
- [Structuring cells](#structuring-cells)
- [Interactivity and state](#interactivity-and-state)
- [Expensive notebooks](#expensive-notebooks)
- [Packages and reproducibility](#packages-and-reproducibility)
- [Running, exporting, deploying](#running-exporting-deploying)
- [Testing](#testing)
- [SQL and dataframes](#sql-and-dataframes)
- [Migrating from Jupyter](#migrating-from-jupyter)
- [Gotchas](#gotchas)
- [Sources](#sources)

## The reactive model

| Practice | Detail |
|---|---|
| Let dependencies drive execution, not cell order | marimo statically reads each cell's referenced and defined globals to build a DAG (edge from a defining cell to every cell that references its definitions), then re-runs dependents on change. It reads the code, not a trace, so there is zero runtime overhead. This eliminates the out-of-order-execution bugs behind the well-cited finding that the vast majority of public Jupyter notebooks are non-reproducible. |
| Treat deleting a cell as deleting its state | Deleting a cell removes its global variables from program memory and re-runs or invalidates dependents, so there are no orphaned references to ghost values. |
| Run a cell, get its dependents | Running a cell automatically runs every other cell that references a global it defines; never manually re-run downstream cells to "refresh" state. |

## Working within the constraints

| Practice | Detail |
|---|---|
| Define every global in exactly one cell | A name defined in two cells raises a multiple-definitions error (marimo cannot order them deterministically); split or merge cells so each name has one definition site. |
| Reassign rather than mutate across cells | marimo does not track in-place mutation (`list.append(...)`, `obj.attr = ...`), so it will not re-run dependents. Mutate in the same cell as the definition, or build a new value (`extended = lst + [2]`). |
| Never create cross-cell cycles | If cell A defines `a` and reads `b`, another cannot define `b` and read `a` (cycle error); the DAG must stay acyclic. Deliberate runtime cycles use `mo.state` only. |
| Use explicit imports, never `import *` | A wildcard import defeats the static analysis of which names a cell defines and raises an import-star error. |
| Prefix throwaway names with `_` | `_tmp` and `_i` are cell-local, so the same name can be reused across cells without a redefinition error or polluting the global namespace. |
| Quote forward-referenced type annotations | A bare (non-string) annotation naming another cell's symbol is treated as a reference and pulled into the dataflow graph; write it as a string to keep it out. |

## Structuring cells

| Practice | Detail |
|---|---|
| Encapsulate throwaway logic in a function | `def _(): ...; _()` keeps intermediates out of the global namespace, sidesteps the one-definition rule, and lets them be garbage-collected. |
| Write idempotent cells | Same inputs, same output and behavior; this is what makes caching safe and avoids order-dependent bugs. |
| Keep globals few and descriptively named | Globals are the dataflow edges, so a small, clearly-named set means fewer collisions and a readable dependency graph. |
| Split long notebooks into modules | Move stable logic into helper `.py` files and import them; enable the module autoreloader so edits to those files refresh in the notebook. |

## Interactivity and state

| Practice | Detail |
|---|---|
| Assign a UI element to a global, read `.value` in another cell | Interacting re-runs cells that reference the variable, not the cell that defines the widget, so reading `.value` in the creating cell never updates. Create the widget in one cell, consume `.value` downstream. |
| Compose runtime-unknown widget sets with `mo.ui.array` / `mo.ui.dictionary` | Use these when you cannot bind each element to its own global; the container's `.value` aggregates the children's values reactively. |
| Gate expensive updates with `mo.ui.form` | Wrapping inputs in a form defers value propagation until submit, so dependents do not re-run on every keystroke. |
| Avoid `mo.state` and `on_change` in nearly all cases | UI elements already hold state via `.value` and reactivity handles updates; `mo.state` and `on_change` reintroduce hidden state and hard-to-find bugs. Reserve `mo.state` for derived history, tied/synchronized elements, or deliberate cycles. |

## Expensive notebooks

| Practice | Detail |
|---|---|
| Switch the runtime to lazy when autorun is too eager | In runtime settings, set on-cell-change to lazy (mark dependents stale instead of running them) and disable autorun on startup; these are settings, not code changes. |
| Gate heavy cells with `mo.stop` and a run button | `run = mo.ui.run_button(); mo.stop(not run.value)` short-circuits the cell and everything downstream until clicked. |
| Cache pure expensive work | `@mo.cache` (in-memory; the key includes closed-over globals), `@mo.persistent_cache` (disk, survives restart, reads back when the cell is not stale), and `@mo.lru_cache(maxsize=...)`. Caching assumes idempotent functions; side effects are not replayed. |
| Disable cells while iterating | A disabled cell and its descendants are blocked from running; re-enabling runs it if an ancestor changed in the meantime. |

## Packages and reproducibility

| Practice | Detail |
|---|---|
| Edit reproducible notebooks in sandbox mode | `uvx marimo edit --sandbox notebook.py` runs in an isolated temporary venv and records dependencies as PEP 723 inline script metadata in the file header, so the notebook is shareable and reproducible down to its packages without a separate requirements file. Requires `uv`. |
| Keep the inline script-metadata header with the file | marimo writes the `# /// script ... ///` block via `uv add --script`; removing an import does not remove the recorded dep, so prune with `uv remove --script notebook.py <pkg>` when needed. |

## Running, exporting, deploying

| Practice | Detail |
|---|---|
| Use the right run mode | `marimo edit` (reactive editor), `marimo run notebook.py` (read-only app, code hidden), `python notebook.py` (top-to-bottom script, good for side effects and CI), `marimo check` (static lint). |
| Import notebook symbols like a module | Because the file is pure Python, functions and classes defined in a notebook can be imported into other programs, which is not practical with Jupyter's JSON. |
| Export for the audience | `marimo export html` (static snapshot), `html-wasm` (self-contained interactive, no server), plus `ipynb`, `script`, `md`. Include the `layouts/` folder when sharing a grid or slides app. |
| Treat `marimo run` as not a sandbox | App mode hides code but still executes it through the UI; for untrusted exposure pair with `--sandbox` and keep the default token auth. |

## Testing

| Practice | Detail |
|---|---|
| Test notebooks with pytest directly | Cells are functions, so `pytest test_notebook.py` works and a test cell can take another cell's def as a parameter. pytest collects statically, so a fixture defined in one cell is not visible to tests in another; put shared fixtures in the setup cell or a `conftest.py`. |

## SQL and dataframes

| Practice | Detail |
|---|---|
| Use SQL cells (`mo.sql`) over DuckDB | Reference Python dataframes by name inside the query; f-string interpolation of `{ui.value}` puts the SQL cell into the reactive DAG. The output type is configurable (the native DuckDB relation is fastest). |
| Return a dataframe as the cell's last expression for the rich viewer | `mo.ui.table(df, selection="multi")` exposes the selection via `.value`; `mo.ui.dataframe(df)` is a no-code transform GUI that shows the generated code. |

## Migrating from Jupyter

| Practice | Detail |
|---|---|
| Convert, then fix the three constraint violations | `marimo convert nb.ipynb -o nb.py` (also converts `# %%`-marked scripts), then resolve redefinitions (one cell per global), cross-cell mutations (combine or reassign), and cycles. Set the runtime to lazy at first if the auto-rerun feels aggressive. |
| Expect outputs to live outside the file | The `.py` file stores code only, not plots or results, which is what makes git diffs clean; enable HTML/ipynb auto-snapshots if you need a visual record alongside it. |

## Gotchas

- A variable defined in two cells is an error, not a last-write-wins overwrite as in Jupyter; the fix is one definition site or an `_`-prefixed local.
- `list.append(...)` and `obj.attr = ...` do not trigger reactivity because mutation is untracked; downstream cells silently keep stale values.
- Reading a UI element's `.value` in the same cell that creates it never reflects interaction; the value updates only in downstream cells.
- `@mo.cache` and friends assume idempotent, side-effect-free functions; cached side effects are not replayed on a hit.
- `marimo run` hides code but is not a security sandbox; the app can still execute notebook code through its UI.
- The notebook file holds no outputs, so a clean `git diff` does not mean a cell still produces the same plot; re-run to confirm.

## Sources

- [marimo best practices guide](https://docs.marimo.io/guides/best_practices/) and [reactivity guide](https://docs.marimo.io/guides/reactivity/) - official docs; the canonical statements on globals, mutations, `on_change`, idempotency, and the DAG runtime.
- [marimo FAQ](https://docs.marimo.io/faq/) - official; caching APIs, expensive-notebook strategies, importing notebooks, script vs app execution, testing.
- [Coming from Jupyter](https://docs.marimo.io/guides/coming_from/jupyter/) - official migration guide; `marimo convert`, constraint fixes, pure-`.py` format vs JSON.
- [marimo GitHub README and repo docs](https://github.com/marimo-team/marimo) - source of truth for the project; reproducibility, git-friendliness, run/export/deploy modes.
- [Python notebooks as dataflow graphs](https://marimo.io/blog/dataflow) - marimo team blog; the DAG model and reproducibility rationale.
- [marimo: A Reactive, Reproducible Notebook](https://realpython.com/marimo-notebook/) - Real Python; well-regarded independent walkthrough corroborating the reactive model and constraints.
