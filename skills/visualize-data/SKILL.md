---
name: visualize-data
description: >-
  Use this skill when building a data visualization as the deliverable with
  marimo, Streamlit, or D3: an interactive reactive notebook, a shareable data
  app or dashboard, or a bespoke custom web chart. Use when the user says
  "visualize this", "build a dashboard", "make an interactive chart", "data
  app", "build a marimo or streamlit notebook for this", "custom D3
  visualization", or wants a visualization someone will interact with rather
  than a one-off image. Do not use for a quick static chart answering an
  analysis question (use analyze-data), for architecture, flow, or sequence
  diagrams (use create-diagram), or for general UI building with no data
  visualization at its center (use design-ui).
---

## Purpose

Build a data visualization with the tool that fits the medium: a reactive Python notebook (marimo), a shareable interactive data app (Streamlit), or a bespoke custom web chart (D3). The first decision is the tool, driven by who will use the result and where it lives; the second is the encoding, driven by what the data has to say. A visualization is an argument about data, not decoration: it exists to make one comparison, relationship, distribution, trend, flow, or hierarchy legible. Ground every build in the chosen tool's reference rather than its API from memory; these APIs are exact and easy to misremember.

## Choose the tool first

| The result is | Tool | Why |
|---|---|---|
| An interactive Python notebook for exploration, reproducible, handed off as a `.py` file | marimo | reactive dataflow, no hidden state, runs as a script or an app |
| A shareable interactive data app or dashboard, served over a URL to non-technical users | Streamlit | one Python file becomes a web app, widgets and layout built in |
| A bespoke, custom, publication-quality web chart: novel encoding, custom layout, network or geographic, fine-grained SVG control or interaction | D3 | full control over every element, beyond what charting libraries allow |

Name the choice and why before building. The wrong tool is the most expensive mistake here: a D3 build for what `st.line_chart` does in one line wastes days, and a Streamlit app for a one-off exploration nobody revisits is overhead that rots.

Boundaries: a quick static chart to answer a data question is `analyze-data` (matplotlib), not this skill. marimo is shared with `analyze-data`, so route by intent, an analysis that produces an answer is `analyze-data`, a visualization or exploration UI that is itself the deliverable is this skill. Architecture and flow diagrams are `create-diagram`.

## Match the encoding to the question

| The data has to show | Encoding |
|---|---|
| Comparison across categories | bar (horizontal when labels are long or many) |
| Trend over time | line; area only when the cumulative total is the point |
| Distribution of one variable | histogram or box plot, not a bar of means |
| Relationship between two variables | scatter; add a trend line only if the relationship is real |
| Part to whole | stacked bar or treemap; avoid pie beyond about five slices |
| Flow or relationships between entities | sankey or chord (D3) |
| Hierarchy | tree or treemap |
| Geographic | choropleth or point map |

One question per view; a chart trying to show three things shows none. Label axes with units, and do not start a bar axis anywhere but zero.

## Workflow

1. **Know the data and the question.** Profile the data (shape, types, ranges) and state the one thing the visualization must make legible. If the data needs cleaning, that is `analyze-data` first; visualize the clean result.
2. **Choose the tool and the encoding** from the tables above, and name why.
3. **Build it grounded in the reference.** Read the matching file before writing: [references/marimo.md](references/marimo.md), [references/streamlit.md](references/streamlit.md), or [references/d3.md](references/d3.md).
4. **Render it with the real data and look at it.** Run it live (`marimo edit` or `run`, `streamlit run`, or open the D3 page) and confirm it renders with the actual dataset, not placeholder data. For a web result (D3, or Streamlit in a browser), `validate-web` can drive the browser to confirm it renders without console errors. A visualization you have not seen rendered is unverified.
5. **Hand off.** State where it lives and the exact command to run it.

## Gotchas

- **The tool follows the medium, not familiarity.** Reaching for D3 because it is powerful, or Streamlit because it is quick, instead of matching the result's destination, is the usual misroute. A notebook for exploration, an app for sharing, D3 for bespoke.
- **Real data or it is not validated.** A visualization that looks right on toy data routinely breaks on the real shape: nulls, long tails, many categories, unicode labels, a date axis that is actually strings. Build against the actual dataset.
- **Interactivity is a cost, not a default.** Every widget, tooltip, and zoom is code to maintain and another way to mislead. Add interaction only where it answers a follow-up question the static view raised.
- **A chart inherits the analysis's caveats.** Excluded rows, a log axis, a truncated range: put the essential caveat in the title or a caption, because the visualization travels past the conversation that qualified it.

## Example

"Show how signups trend by week across our three plans, as something the team can poke at."

The result is a shared interactive view for the team, so Streamlit, not D3. The encoding is a trend over time split by category, so a multi-series line chart with a plan selector. Read `references/streamlit.md`, build `signups_app.py` (`st.line_chart` of the weekly-resampled dataframe, `st.multiselect` for plans, `@st.cache_data` on the load), run `streamlit run signups_app.py` against the real export, confirm it renders, and hand the team the one-line command.
