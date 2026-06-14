Apply these practices whenever planning, writing, or reviewing Jupyter notebooks. The root cause of most notebook pain is hidden, mutable kernel state, and every practice here exists to contain it. Generic clean-code rules live in CLAUDE.md; this reference is the notebook-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win. For new exploratory work where reproducibility matters from day one, prefer marimo (see tool-marimo), which removes hidden state by construction.

## Contents

- [Hidden state and restart-run-all](#hidden-state-and-restart-run-all)
- [Version control](#version-control)
- [Reproducible execution](#reproducible-execution)
- [Structure and scope](#structure-and-scope)
- [Testing](#testing)
- [Magics and environment](#magics-and-environment)
- [Security and secrets](#security-and-secrets)
- [When to graduate](#when-to-graduate)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Hidden state and restart-run-all

| Practice | Detail |
|---|---|
| Trust only what "Restart Kernel and Run All" reproduces | Cells run in any order, and kernel state diverges from the visible sequence: a variable can survive only because the cell that defined it was edited or deleted after running. Make restart-and-run-all a habit before trusting any result, not a final ritual. A large GitHub study found roughly a quarter to a third of public notebooks fail to re-execute top-to-bottom. |
| Run cells top-to-bottom in order while working | Out-of-order execution is the single core hazard. The bracket number `[n]` is the only on-screen clue to true run order; non-monotonic numbers signal a notebook whose state no longer matches its layout. |
| Never let distant cells depend on hidden intermediate state | A cell that silently relies on a variable set 40 cells earlier (or in a since-deleted cell) breaks on a clean run. Keep dependencies local and explicit. |
| Split out anything too valuable to lose on restart | If a kernel restart would cost you a long computation, that result belongs in a script that serializes its output to disk, not in live kernel state. |

## Version control

| Practice | Detail |
|---|---|
| Never commit output blobs | Notebooks are JSON, so raw git diffs are unreadable execution-count and metadata churn, embedded image/data outputs bloat history and cause merge conflicts, and printed cells can leak data or secrets into permanent history. |
| Strip outputs at the git boundary with nbstripout | `pip install nbstripout; nbstripout --install --attributes .gitattributes` registers a clean filter that strips outputs and counts on stage while your working copy stays interactive. This is both a diff-hygiene and a secret-leakage control. |
| Pair to a reviewable `.py` with Jupytext | `jupytext --set-formats ipynb,py:percent nb.ipynb` then `jupytext --sync`; commit the line-diffable `py:percent` script as source of truth and gitignore or output-strip the `.ipynb`. Edits to either side sync back. |
| Use nbdime when you must diff `.ipynb` directly | `nbdiff`/`nbmerge` and the git drivers (`nbdime config-git --enable`) understand notebook structure and render content-level diffs and merges instead of JSON noise. |

## Reproducible execution

| Practice | Detail |
|---|---|
| Treat only batch-run output as official | Interactively produced output is never authoritative. `jupyter nbconvert --to notebook --execute --inplace nb.ipynb` runs a fresh kernel top-to-bottom and fails on any cell error, which is the headless equivalent of restart-and-run-all and the right CI gate. |
| Parametrize with papermill, do not hand-edit cells | Tag one cell `parameters`; `papermill in.ipynb out.ipynb -p alpha 0.6` injects an `injected-parameters` cell immediately after it. Keep the parameters cell to bare literal assignments, since overrides are injected as literals and downstream derived values are not recomputed for you. |
| Pin the environment and lock it | Track deps in `requirements.txt`/`environment.yml` and lock with uv, pip-tools, or conda-lock; run only inside that environment. Record exact versions in the notebook itself via `%load_ext watermark` then `%watermark --iversions`. |
| Set every RNG seed early, in the parameters cell | Seed each library explicitly (`random.seed`, `np.random.default_rng(0)`, framework-specific seeds, `PYTHONHASHSEED`). Stochastic steps do not reproduce otherwise, and a single unseeded library defeats the rest. |
| Clear all outputs before committing | Output is a byproduct of one run, not source. Clear it (manually, nbstripout, or `nbconvert --clear-output`) so the committed artifact carries no stale or environment-specific results. |

## Structure and scope

| Practice | Detail |
|---|---|
| One small, idempotent step per cell | One paragraph, function, or task per cell, kept short; re-running a cell should be safe and produce the same state. Giant cells and forward references are where hidden-state bugs hide; consolidate one-liner sprawl. |
| Top-load parameters and imports | Put imports and key variable declarations at the top, never buried mid-notebook, so a reader sees the inputs and a clean run resolves dependencies in order. |
| Tell a narrative in markdown | Headers, a table of contents, and prose explaining the why; your primary audience is future-you. Document dead ends as you go, not at the end. |
| Move reusable logic into imported modules | Do not grow application logic inside cells; notebooks do not scale to modularization, debugging, or diffing. Factor stable logic into tested `.py` modules and import them, keeping the notebook as the thin exploration and reporting layer. |
| Reload imported modules live | `%load_ext autoreload` then `%autoreload 2` picks up edits to imported modules without a kernel restart, the companion to extracting logic out of cells. |
| Name notebooks on creation | Avoid `Untitled*.ipynb` and purpose drift; split a notebook when it accretes unrelated work, and chain long analyses as ordered task notebooks with serialized intermediate results. |

## Testing

| Practice | Detail |
|---|---|
| Put notebooks under automated test in CI | Eyeballing outputs is not testing. Scatter `assert` mini-tests through cells, and run a notebook-aware runner in CI on a fresh kernel. |
| Regression-test stored outputs with nbval | `pytest --nbval nb.ipynb` re-executes and compares to stored output; `--nbval-lax` only fails on exceptions; mark cells `# NBVAL_IGNORE_OUTPUT`/`# NBVAL_SKIP` and add sanitizers for nondeterministic output (timestamps, addresses). |
| Lint and type-check with nbQA | `nbqa ruff nb.ipynb`, `nbqa black nb.ipynb`, `nbqa mypy nb.ipynb` run standard tools on notebooks while handling magics; wire them into pre-commit so notebook code meets the same bar as `.py`. |

## Magics and environment

| Practice | Detail |
|---|---|
| Expose one pinned environment as a named kernel | `python -m ipykernel install --user --name proj --display-name "Python (proj)"`; select it deliberately, and pass the same kernel to papermill (`-k`) and nbval (`--nbval-kernel-name`). A mismatched kernel is a silent reproducibility break. |
| Profile before optimizing | `%time`/`%timeit` (timing), `%prun` (cProfile), `%lprun` (line profiler), `%memit`/`%mprun` (memory). Find the hot path, then optimize only it. |
| Free large objects from long-lived kernel state | A long-running kernel keeps big DataFrames and arrays resident, and that residency is itself hidden state. `del big; import gc; gc.collect()`, serialize expensive results to disk and reload, or move heavy compute to a script. |
| Keep logic in plain Python, magics at the top | Magic-dependent code will not run as a plain script and confuses linters, which is exactly why nbQA exists. |

## Security and secrets

| Practice | Detail |
|---|---|
| Do not run untrusted notebooks | A downloaded notebook can carry arbitrary code in cells and arbitrary HTML/JS in saved outputs. Jupyter's trust model withholds rendering of HTML/JS output until a notebook's signature is trusted (output you generate in your own session is trusted); review cells first and run unknown notebooks in an isolated environment. |
| Never hardcode secrets | Load credentials from environment variables or a secrets manager. Because printed outputs can capture secrets or raw data, output-stripping at commit (nbstripout) is a second line of defense against leaking them into history. |

## When to graduate

| Practice | Detail |
|---|---|
| Move logic out when these signals appear | Copy-pasting cells to reuse code (wrap in a function, then a module), reuse across notebooks (a library), needing real unit tests or CLI execution (a module plus papermill), heavy or long-running compute (a job or script), or a stabilized analysis that repeats on new data (a parametrized papermill pipeline). |
| Consider marimo for new reproducibility-critical work | Reactive pure-Python notebooks remove out-of-order execution and the JSON-diff problem by construction; keep the Jupyter plus Jupytext plus nbstripout plus papermill stack for existing notebook estates. |

## Gotchas

- A variable can exist in the kernel only because its defining cell was edited or deleted after running; nothing on screen reveals this until a clean restart-and-run-all fails.
- Non-monotonic `[n]` execution counts are the visible symptom of out-of-order state; treat them as a warning, not cosmetic.
- papermill injects overrides as literals after the `parameters` cell and does not recompute values you derived from those parameters elsewhere, so keep the parameters cell to bare assignments.
- "It ran for me" proves nothing: interactive output reflects accumulated state, not a fresh run. Only `nbconvert --execute` output is trustworthy.
- A kernel whose name does not match the pinned project environment runs against the wrong packages silently; verify the selected kernel.
- `ruff`/`black`/`mypy` cannot read `.ipynb` directly; run them through nbQA, not on the raw file.

## Sources

- [Jupyter Notebook docs: security and the trust model](https://jupyter-notebook.readthedocs.io/en/stable/) and [Project Jupyter](https://docs.jupyter.org/) - official, authoritative on the signature/trust model and notebook behavior.
- [Rule et al., "Ten Simple Rules for Reproducible Research in Jupyter Notebooks," PLOS Comp Bio (2019)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007007) - peer-reviewed reproducibility guidance; restart-run-all, modularization, parametrization, seeds, environment pinning.
- [Jupytext documentation](https://jupytext.readthedocs.io/en/latest/) and [nbstripout](https://github.com/kynan/nbstripout) - the canonical text-pairing and output-stripping tools for clean diffs and secret hygiene.
- [papermill documentation](https://papermill.readthedocs.io/en/latest/usage-parameterize.html) - official; the `parameters` tag, `injected-parameters` behavior, and CLI/API execution.
- [nbval](https://nbval.readthedocs.io/en/latest/), [nbQA](https://nbqa.readthedocs.io/en/latest/), and [nbdime](https://nbdime.readthedocs.io/en/latest/) - established notebook test, lint, and diff/merge tooling for CI.
- [nbdev: Notebook Best Practices (fast.ai)](https://nbdev.fast.ai/tutorials/best_practices.html) - widely adopted notebook-driven-development project; small cells, importable modules, and testing in notebooks.
