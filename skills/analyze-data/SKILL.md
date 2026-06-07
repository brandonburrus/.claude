---
name: analyze-data
description: >-
  Use this skill when analyzing, aggregating, summarizing, or plotting tabular
  data from CSV, TSV, Excel, JSON, Parquet, or SQLite sources. Use when the
  user says "analyze this data", "what's the total/average/trend", "group by",
  "how many rows", "plot this", "make a chart from this data", or hands over a
  data file with a question. Do not use for editing spreadsheet files as
  documents (use edit-excel-sheet), designing database schemas (use
  design-data-schema), or architecture diagrams (use create-diagram).
---

## Purpose

Answer questions about data with numbers that are actually true, through small per-task Python scripts run with uv. Wrong analysis looks identical to right analysis in the output; the difference is made earlier, by profiling the data before trusting it, cleaning with disclosure instead of silently, and reconciling aggregates against the raw data before reporting them. An answer without its caveats is a different, less honest answer.

## Workflow

1. **Profile before analyzing**: `uv run ${CLAUDE_SKILL_DIR}/scripts/profile-data.py <file>`. The output shows shape, nulls, uniques, ranges, duplicate rows, and warnings for the classic traps (leading-zero IDs, currency strings, case variants, Excel serial dates). Plan the analysis against what the data actually is, not what its column names imply.
2. **Clean with disclosure.** Every cleaning decision changes the answer, so each one is recorded and reported: rows dropped (and how many), duplicates kept or removed (and why), values normalized, nulls excluded or treated as zero. Silent cleaning is how two analysts get two different totals from one file.
3. **Write a per-task analysis script** with PEP 723 inline deps and run it with uv:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.2"]
# ///
import pandas as pd

df = pd.read_csv("sales.csv", dtype={"sku": str, "zip": str})  # IDs stay strings
df["revenue"] = (
    df["revenue"].str.replace(r"[$,]", "", regex=True).astype(float)
)
df["region"] = df["region"].str.strip().str.title()
by_region = df.groupby("region", dropna=False)["revenue"].sum()
print(by_region)
print("reconcile:", by_region.sum(), "==", df["revenue"].sum())
```

4. **Sanity-check before reporting.** Group sums reconcile to the grand total, row counts in plus rows excluded equals rows out, percentages sum to ~100, and a spot check of one group computed by hand from the raw rows matches. An aggregate that fails reconciliation is a bug, not an answer.
5. **Report numbers with their methodology.** The answer, then in brief: rows used vs excluded and why, cleaning applied, and any caveat that changes interpretation (tiny n, missing periods, one group dominating a mean). Keep it to a few lines; the point is reproducibility, not ceremony.

## Tool routing

| Situation | Tool |
|---|---|
| Default tabular work, up to a few million rows | pandas |
| File bigger than memory, or the question is SQL-shaped aggregation over big files | duckdb (`duckdb.sql("SELECT ... FROM 'file.parquet'")` reads csv/parquet directly, larger-than-memory included) |
| SQLite databases | duckdb or sqlite3; never parse the file manually |
| Charts | matplotlib, saved to a file the user can open; one chart per question, labeled axes and units |
| Xlsx as a data source | `pd.read_excel`; the file is a container here, editing it routes to edit-excel-sheet |

## The trap table

These silently corrupt analyses; the profiler warns about most of them:

| Trap | Consequence | Defense |
|---|---|---|
| Numeric-looking IDs (zip, SKU, account) | Leading zeros destroyed, IDs turned into floats | `dtype=str` for identifier columns at read time |
| Currency and thousands strings ("$1,234.56") | Column reads as text; sum is concatenation or NaN | Strip symbols, then cast; never `errors="coerce"` blindly (it converts bad rows to NaN silently) |
| Duplicated rows | Inflated totals | Count them, ask or decide visibly whether they are real repeats |
| Case/whitespace category variants ("West", "west ") | One region becomes three groups | Normalize before grouping; report the collapse |
| Ambiguous dates (03/04/2025) | Month and day swapped for half the rows | Check value ranges to infer the format; pass an explicit format, never let inference guess per-row |
| NaN in group keys | pandas drops those rows from groupby by default | `dropna=False` and report the null group |
| Excel serial dates (45123) | Dates read as integers | `pd.to_datetime(col, unit="D", origin="1899-12-30")` |
| Mean vs median on skewed data | One whale makes the average a lie | Check the distribution; report median or both when skew is real |
| Tiny groups in rates ("100% of 2 rows") | Impressive percentages with no support | Report n alongside every rate; flag groups below a sane floor |

## Honesty rules

- **Never silently drop data.** `errors="coerce"`, `dropna()`, and failed joins all delete rows; count what each step removed and say it.
- **The dedup decision belongs to the user when it changes the answer materially.** "Removing 312 duplicate rows changes the total by 4.1%; they look like an export artifact because X. I removed them" is a report; removing them wordlessly is not.
- **Correlation language stays correlational.** "X is associated with Y in this data" unless the data actually supports more.
- **Do not extrapolate beyond the data's window** without flagging it; a 3-month trend line projected to a year is fiction with axes.
- **When the data cannot answer the question, say so.** Missing columns, missing periods, or granularity mismatches mean the honest answer is "not answerable from this file, here is what would be needed".

## Gotchas

- **The profiler reads text formats as all-strings deliberately.** It shows the raw data so formatting problems are visible; the analysis script then casts deliberately. Letting `read_csv` infer everything is how zip codes become floats in the first place.
- **Joins are where rows silently die.** After any merge, compare row counts to expectations and check unmatched keys from both sides; an inner join quietly discarding 20% of the data invalidates everything downstream.
- **Plots inherit the cleaning, so caveat the plot too.** A chart travels further than the chat message that qualified it; put the essential caveat (excluded rows, log scale, truncated axis) in the title or caption.
- **Aggregating before validating wastes the work.** A profile takes seconds; redoing the analysis after discovering mid-report that revenue was a string costs the whole pass.
