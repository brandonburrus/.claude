---
name: edit-excel-sheet
description: >-
  Use this skill when creating, editing, or reading Excel spreadsheets (.xlsx,
  .xlsm) including cell values, formulas, formatting, multiple sheets, tables,
  and charts. Use when the user says "create a spreadsheet", "update this
  Excel file", "read the xlsx", "add a column to the sheet", or references a
  .xlsx/.xlsm file. Do not use for plain .csv files (edit them as text), for
  legacy .xls files without converting first, or for analyzing tabular data
  where the spreadsheet is only the container (load it and analyze directly).
---

## Purpose

Create, edit, and read Excel workbooks with openpyxl through small per-task Python scripts run with uv. The non-negotiable core is the inspect, edit a copy, verify loop: Excel files carry state that does not survive a careless load+save cycle (formulas, macros, charts), so every edit starts by knowing what is in the file and ends by proving the edit landed without collateral damage.

## Workflow

1. **Inspect before touching anything**: `uv run ${CLAUDE_SKILL_DIR}/scripts/inspect-workbook.py <file>`. The output lists sheets, dimensions, headers, formula counts, merged ranges, and features openpyxl can damage (charts, images, macros). Plan the edit against this, not against assumptions about the file.
2. **Edit a copy, not the original.** Write output to a new file (or copy first and edit the copy). Replace the original only after verification passes; openpyxl failures corrupt silently, not loudly.
3. **Write a per-task script** with PEP 723 inline deps and run it with `uv run`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl>=3.1"]
# ///
from openpyxl import load_workbook

wb = load_workbook("input.xlsx")  # data_only=False: formulas preserved
ws = wb["Q3 Forecast"]
ws["D2"] = "=B2*C2"
ws.cell(row=1, column=4, value="Total")
wb.save("output.xlsx")
```

4. **Verify by re-opening.** Load the output file and assert the change landed: the new value reads back, the formula string is present, sheet count is unchanged, and a spot-check of cells you did not touch still holds the old values. An edit without a read-back is unverified.
5. **Report limits honestly.** If the workbook had charts, pivot tables, or conditional formatting, state what survived and what may not have; do not claim full fidelity.

## The formula rules

These cause silent data destruction and are the most important content in this skill:

- **`data_only=True` then `save()` destroys every formula in the workbook.** `data_only=True` replaces formulas with their last cached values on load; saving writes that stripped version back. Read values with `data_only=True` only in a read-only pass; never save a workbook loaded that way.
- **openpyxl never calculates.** Writing `=B2*C2` stores the formula string; the cell's cached value stays stale (or empty) until Excel or LibreOffice opens and recalculates the file. After editing formulas, read-back verification checks the formula string, not the computed value, and the report to the user states that values will appear on next open in Excel.
- **`.xlsm` requires `load_workbook(path, keep_vba=True)`** and saving with the `.xlsm` extension, or the macros are stripped without warning.

## Common operations

| Operation | How |
|---|---|
| New workbook | `Workbook()`; first sheet is `wb.active`; more via `wb.create_sheet("Name")` |
| Address cells | `ws["B2"]` or `ws.cell(row=2, column=2)`; 1-indexed |
| Bulk read | `ws.iter_rows(min_row=2, values_only=True)`; use `read_only=True` for big files |
| Bulk write | `ws.append([...])` per row; `write_only=True` workbook for very large output |
| Number formats | `cell.number_format = "#,##0.00"` or `"yyyy-mm-dd"`; dates are Python datetimes plus a format |
| Styling | `cell.font = Font(bold=True)`, `cell.fill = PatternFill("solid", fgColor="DDEBF7")`; styles are objects assigned whole, not mutated in place |
| Column width | `ws.column_dimensions["A"].width = 18`; openpyxl does not auto-fit, compute from content length when it matters |
| Header row | Bold + `ws.freeze_panes = "A2"` |
| Excel table | `Table(displayName="Sales", ref="A1:D20")` + `ws.add_table(...)`; gives filters and structured refs |
| Merged cells | `ws.merge_cells("A1:C1")`; only the top-left cell holds the value, the rest read None |
| New chart | `BarChart()`/`LineChart()` + `Reference(...)` + `ws.add_chart(chart, "F2")` |

## Gotchas

- **Inserting rows does not move anything attached to positions.** `insert_rows()` shifts cell values but not merged ranges, charts, images, or formula references pointing at the old rows. After structural edits, re-check merged ranges and any formulas referencing shifted regions; for formula-heavy sheets prefer appending or writing to a new area over inserting into the middle.
- **Charts and images may not survive load+save.** openpyxl rebuilds the file on save and its chart/image support is partial; the inspector warns when they are present. When fidelity matters, confine edits to writing cell values and accept-or-flag the risk explicitly.
- **`max_row`/`max_column` lie on dirty files.** Formatting-only cells (a styled but empty column) extend the reported dimensions. Trust actual values, not the bounding box, when iterating.
- **Cell styles do not deep-copy across cells or workbooks.** Assign new style objects (`Font(...)`, not `other_cell.font`); copying a styled range needs `copy(cell._style)` per cell or re-applying named styles.
- **CSV is not Excel.** Round-tripping an .xlsx through CSV destroys formulas, types, formatting, and extra sheets; only do it when the user explicitly wants plain data.
- **Reading values requires the file to have been calculated.** A workbook generated programmatically and never opened in Excel has no cached values, so `data_only=True` reads None for every formula cell. If you need computed values from such a file and LibreOffice is installed, `soffice --headless --convert-to xlsx` recalculates; otherwise report the limitation.
