## Streamlit reference

Streamlit turns a Python script into an interactive web app. Core API and execution model digested from the official docs (docs.streamlit.io). The defining trait: the whole script re-runs top to bottom on every interaction, widgets return their current value, and caching keeps expensive work from repeating.

### Contents

- [Setup](#setup)
- [Execution model](#execution-model)
- [Display and data](#display-and-data)
- [Charts](#charts)
- [Widgets](#widgets)
- [Layout](#layout)
- [Caching](#caching)
- [Minimal app](#minimal-app)

### Setup

`pip install streamlit`, or `uvx --with pandas streamlit run app.py` without installing. Run with `streamlit run app.py` (opens `http://localhost:8501`).

### Execution model

On load and on every widget interaction, Streamlit re-runs the entire script top to bottom. There is no callback wiring: a widget call like `st.slider(...)` returns the current value, you use it further down, and the rerun recomputes everything below it. This is why caching matters, since without it every slider nudge reloads your data.

### Display and data

- `st.title` / `st.header` / `st.subheader` / `st.markdown`, and `st.write`, the catch-all that renders text, dataframes, charts, and most objects.
- `st.dataframe(df)` is interactive (sort, resize, search); `st.table(df)` is static.
- `st.metric("Revenue", "$1.2M", "+4%")` for a KPI tile.

### Charts

Built-in (pass a dataframe; Streamlit picks sensible defaults):

- `st.line_chart(df)`, `st.bar_chart(df)`, `st.area_chart(df)`, `st.scatter_chart(df)`, `st.map(df_with_lat_lon)`

Library charts (full control; pass a figure or spec):

- `st.plotly_chart(fig)`, `st.altair_chart(chart)`, `st.vega_lite_chart(spec)`, `st.pyplot(fig)`, `st.pydeck_chart(deck)`

Use the built-ins for speed and the happy path; reach for a library chart when you need encodings, tooltips, or styling the built-ins do not expose.

### Widgets

Each returns its current value on every run:

- `st.slider`, `st.selectbox`, `st.multiselect`, `st.radio`, `st.checkbox`, `st.text_input`, `st.number_input`, `st.date_input`, `st.file_uploader`, `st.button`

```python
plan = st.selectbox("Plan", ["Free", "Pro", "Team"])
n = st.slider("Rows", 10, 1000, 100)
```

### Layout

- `st.sidebar` holds filters: `st.sidebar.selectbox(...)` or `with st.sidebar:`.
- `st.columns(3)` returns side-by-side containers; `st.tabs(["A", "B"])`, `st.expander("Details")`, and `st.container()` group content.

### Caching

- `@st.cache_data` on functions that load or transform data (it returns a copy each call; use for dataframes, API results, computations).
- `@st.cache_resource` for singletons that must not be copied (a database connection, a model).

Without caching, the top-to-bottom rerun reloads everything on every interaction.

### Minimal app

```python
import streamlit as st
import pandas as pd

st.title("Signups by plan")


@st.cache_data
def load():
    return pd.read_csv("signups.csv", parse_dates=["week"])


df = load()
plans = st.multiselect("Plans", df["plan"].unique(), default=list(df["plan"].unique()))
weekly = (
    df[df["plan"].isin(plans)]
    .groupby([pd.Grouper(key="week", freq="W"), "plan"])
    .size()
    .unstack("plan")
)
st.line_chart(weekly)
```

Run: `streamlit run app.py`.
