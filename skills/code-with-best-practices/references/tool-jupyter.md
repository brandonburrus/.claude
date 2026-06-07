Apply these practices whenever planning, writing, or reviewing Jupyter notebooks. The root cause of most notebook pain is hidden, mutable kernel state; every practice here exists to contain it. For new exploratory work where reproducibility matters from day one, prefer marimo (see tool-marimo), which removes hidden state by construction.

## Contents

- Hidden State and Restart-Run-All
- Version Control
- Reproducible Execution
- Hygiene and Structure
- Scope Discipline
- Testing
- Magics and Tooling
- Security and Secrets
- Environment and Kernels
- Performance and Memory
- When to Graduate

## Hidden State and Restart-Run-All

| Practice | Detail |
|---|---|
| Trust only what "Restart Kernel and Run All" reproduces | Cells run in any order, and kernel state can diverge from the visible sequence (a variable may exist only from a since-deleted cell). Make restart-and-run-all a habit, not a final ritual; roughly a third of public notebooks fail to reproduce top-to-bottom. The CI/headless equivalent is `jupyter nbconvert --to notebook --execute --inplace nb.ipynb`. |
| Split out anything too valuable to lose on restart | If you would be upset that the kernel restarted, that long-running computation belongs in a script that serializes its output, not in live kernel state. |

## Version Control

| Practice | Detail |
|---|---|
| Never commit output blobs | Notebooks are JSON, so git diffs are unreadable metadata, embedded outputs bloat history and cause merge conflicts, and printed cells can leak data or secrets. |
| Strip outputs at the git boundary with nbstripout | `pip install nbstripout; nbstripout --install --attributes .gitattributes` registers a clean filter that strips outputs on stage while leaving your working copy interactive. |
| Pair to a reviewable `.py` with Jupytext | `jupytext --set-formats ipynb,py:percent nb.ipynb` then `jupytext --sync`; review and commit the `py:percent` script (line-diffable real Python) and gitignore or strip the `.ipynb`. |
| Use nbdime when you must diff `.ipynb` directly | `nbdiff`/`nbmerge` and the git drivers understand notebook structure and present meaningful diffs. |

## Reproducible Execution

| Practice | Detail |
|---|---|
| Treat only batch-run output as official | Never trust interactively-produced output. `jupyter nbconvert --execute` runs a fresh kernel top-to-bottom and fails on any error. |
| Parameterize and automate with papermill | `papermill in.ipynb out.ipynb -p alpha 0.6` injects an `injected-parameters` cell after the cell tagged `parameters`; keep the parameters cell to bare assignments, because overrides are injected as literals and downstream values are not recomputed. |
| Pin the environment | Track dependencies in `requirements.txt`/`environment.yml` and lock them (uv, pip-tools, conda-lock); run only inside that environment. Record versions in the notebook with `%load_ext watermark` then `%watermark --iversions`. |
| Set every RNG seed early | Seed each library in the parameters cell (`random.seed`, `np.random.default_rng(0)`, framework seeds, `PYTHONHASHSEED`); stochastic steps do not reproduce otherwise. |

## Hygiene and Structure

| Practice | Detail |
|---|---|
| One step per cell, defined before use | One paragraph, function, or task per cell; keep cells under ~100 lines and consolidate one-liner sprawl. Forward references and giant cells are where hidden-state bugs hide. |
| Tell a narrative in markdown | Headers, a table of contents, and prose explaining the why (your main audience is future-you); document dead ends as you go, not at the end. |
| Top-load parameters | Put key variable declarations at the top, not buried mid-notebook. |
| Name notebooks on creation | Avoid `Untitled*.ipynb` and purpose drift; split a notebook when it accretes unrelated work. |

## Scope Discipline

| Practice | Detail |
|---|---|
| Notebooks explore and report; modules run in production | Notebooks do not scale to modularization, testing, debugging, or diffing. Factor reusable logic into importable, tested `.py` modules and import them, keeping the notebook as the exploration layer. |
| Reload imported modules live | `%load_ext autoreload` then `%autoreload 2` picks up module edits without a kernel restart, the companion to extracting logic into modules. |
| Break monoliths into pipelines | Split a long analysis into smaller task notebooks with a defined order and serialized intermediate results; generalize a stabilized notebook into a parameterized papermill pipeline. |

## Testing

| Practice | Detail |
|---|---|
| Put notebooks under automated test in CI | Eyeballing outputs is not testing. Scatter `assert` mini-tests through cells, and run notebook-aware tools in CI. |
| Regression-test stored outputs with nbval | `pytest --nbval nb.ipynb` re-executes and compares to stored output; `--nbval-lax` only fails on errors; mark cells `# NBVAL_IGNORE_OUTPUT`/`# NBVAL_SKIP` and sanitize nondeterministic output. |
| Lint and type-check with nbQA | `nbqa ruff nb.ipynb`, `nbqa black nb.ipynb`, `nbqa mypy nb.ipynb` run standard tools on notebooks (handling magics); wire them into pre-commit. |

## Magics and Tooling

| Practice | Detail |
|---|---|
| Use profiling magics before optimizing | `%time`/`%timeit` (timing), `%prun` (cProfile), `%lprun` (line profiler), `%memit`/`%mprun` (memory). Profile, then optimize the hot path. |
| Keep logic in plain Python, magics at the top | Magic-dependent code will not run as a plain script and confuses linters, which is why nbQA exists. |

## Security and Secrets

| Practice | Detail |
|---|---|
| Do not run untrusted notebooks | A downloaded notebook can carry arbitrary code in cells and arbitrary HTML/JS in saved outputs; review cells first and run in an isolated environment (Jupyter's trust model blocks auto-rendering until you trust it). |
| Never hardcode secrets; stripping outputs is also a security control | Load credentials from environment variables or a secrets manager; because outputs can capture printed secrets or raw data, nbstripout prevents leakage into version history. |

## Environment and Kernels

| Practice | Detail |
|---|---|
| One pinned environment per project, exposed as a named kernel | `python -m ipykernel install --user --name proj --display-name "Python (proj)"`; select it deliberately, and pass the same kernel to papermill (`-k`) and nbval (`--nbval-kernel-name`). A mismatched kernel is a silent reproducibility break. |

## Performance and Memory

| Practice | Detail |
|---|---|
| Free large objects from long-lived kernel state | A long-running kernel accumulates large DataFrames and arrays that stay resident and are themselves hidden state; `del big; import gc; gc.collect()`, serialize expensive results to disk and reload, or move heavy compute to a script. |

## When to Graduate

| Practice | Detail |
|---|---|
| Move logic out when these signals appear | Copy-pasting cells to reuse code (wrap in a function, then a module), reuse across notebooks (a library), needing real unit tests or CLI execution (a module plus papermill), heavy or long-running compute (a job or script), or a stabilized analysis that repeats on new data (a parameterized pipeline). |
| Consider marimo for new reproducibility-critical work | Reactive pure-Python notebooks remove out-of-order execution and the JSON-diff problem by construction; keep the Jupyter plus Jupytext plus nbstripout plus papermill stack for existing notebook estates. |
