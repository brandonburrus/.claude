## marimo reference

What marimo is, the notebook file format, the reactive model, UI widgets, and charting. The format and the slider example were verified live against marimo 0.23.9. marimo is a reactive Python notebook stored as a plain `.py` file: Git-friendly, runnable as a script, and free of the hidden-state bugs that make Jupyter outputs silently wrong.

### Contents

- [Setup and CLI](#setup-and-cli)
- [Notebook format](#notebook-format)
- [Reactive dataflow](#reactive-dataflow)
- [UI widgets](#ui-widgets)
- [Markdown and layout](#markdown-and-layout)
- [Charts](#charts)
- [SQL](#sql)
- [Export](#export)

### Setup and CLI

| Goal | Command |
|---|---|
| Install | `pip install marimo` (or `marimo[recommended]`) |
| Edit (browser editor) | `uvx --with pandas marimo edit notebook.py` |
| Run as a read-only app | `uvx marimo run notebook.py` |
| Run headless as a script | `python notebook.py` |
| Convert from Jupyter | `uvx marimo convert old.ipynb > notebook.py` |
| Export to static HTML | `uvx marimo export html notebook.py -o out.html` |

Add `--with <pkg>` to `uvx` for each library the notebook imports, or run inside a project venv that already has them.

### Notebook format

A notebook is a `.py` file: an `app`, one decorated function per cell, and a run guard. (Verified valid against marimo 0.23.9.)

```python
import marimo

app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    return mo, pd


@app.cell
def _(mo):
    n = mo.ui.slider(1, 100, value=10, label="rows")
    n
    return (n,)


@app.cell
def _(n, pd):
    df = pd.DataFrame({"x": range(n.value)})
    df
    return


if __name__ == "__main__":
    app.run()
```

The last expression in a cell is its displayed output (`n` and `df` above). In the editor, marimo regenerates each cell's `def _(...)` arguments and `return` tuple from static analysis on save; when authoring by hand, the arguments are the globals the cell reads and the return tuple is the globals it defines.

### Reactive dataflow

- A cell's arguments are the globals it reads; its return tuple is the globals it defines. marimo builds a DAG from these, and running a cell automatically re-runs every cell downstream. No manual re-run, no stale output.
- Every global must be defined by exactly one cell; defining the same name in two cells is an error marimo flags.
- marimo does not track in-place mutation: `lst.append(x)` or `obj.attr = x` will not trigger downstream re-runs. Reassign (`df = df.assign(...)`) instead of mutating.

### UI widgets

`mo.ui` widgets are reactive: reading `widget.value` in another cell makes that cell re-run when the widget changes.

```python
slider = mo.ui.slider(1, 100, value=10, label="n")
dropdown = mo.ui.dropdown(["a", "b", "c"], value="a")
text = mo.ui.text(placeholder="search")
table = mo.ui.table(df)            # selectable, sortable; table.value is the selection
explorer = mo.ui.dataframe(df)     # page, filter, sort millions of rows
```

Display a widget by making it the cell's last expression; read `slider.value`, `table.value`, etc. downstream. Group several with `mo.ui.array([...])` or a dict, and arrange outputs with `mo.hstack` / `mo.vstack`.

### Markdown and layout

`mo.md("...")` renders Markdown and interpolates Python with f-strings: `mo.md(f"Total: **{total:,}**")`. Interpolate a widget into markdown to place it inline. `mo.hstack`, `mo.vstack`, `mo.ui.tabs`, and `mo.accordion` arrange outputs.

### Charts

A cell displays whatever it returns, so make the chart the last expression:

- matplotlib: return the `Axes` or figure (`ax = df.plot(...)` then `ax`, or `plt.gca()`).
- Altair: `mo.ui.altair_chart(chart)` renders it and makes the selection reactive, so a brush in the chart drives `chart.value` (the selected rows) downstream.
- Plotly: `mo.ui.plotly(fig)` similarly, with selection.

Reactive charts are marimo's strength: a selection in one chart drives another cell with no callback wiring.

### SQL

`mo.sql(f"SELECT ... FROM df WHERE x > {threshold}")` runs SQL (DuckDB) over dataframes and databases and returns a dataframe usable downstream; the editor also offers dedicated SQL cells.

### Export

`marimo export html notebook.py -o out.html` produces a static, shareable snapshot. `marimo export script notebook.py` flattens to a plain `.py` script (and loses reactivity). To share a live app instead of a snapshot, use `marimo run`.
