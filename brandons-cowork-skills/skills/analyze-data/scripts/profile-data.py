# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.2", "openpyxl>=3.1", "pyarrow>=16"]
# ///
"""Profile a tabular data file so analysis can be planned safely.

Reports shape, dtypes, null and unique counts, ranges, duplicate rows, and a
sample, plus warnings for the traps that silently corrupt analyses: numeric-
looking identifier columns, currency or thousands-separator strings, mixed
types, and categorical columns with case or whitespace variants.
"""

import sys
from pathlib import Path

import pandas as pd


def load(path: Path) -> dict[str, pd.DataFrame]:
    suffix = path.suffix.lower()
    if suffix in (".csv", ".tsv", ".txt"):
        # sep=None + engine='python' sniffs the delimiter; encoding fallbacks cover BOM and latin-1 exports
        for enc in ("utf-8-sig", "latin-1"):
            try:
                return {"": pd.read_csv(path, sep=None, engine="python", encoding=enc, dtype=str, keep_default_na=False, na_values=[""])}
            except UnicodeDecodeError:
                continue
        raise SystemExit(f"Error: could not decode {path} as utf-8 or latin-1")
    if suffix in (".xlsx", ".xlsm"):
        sheets = pd.read_excel(path, sheet_name=None, dtype=str)
        return {name: df for name, df in sheets.items()}
    if suffix == ".parquet":
        return {"": pd.read_parquet(path)}
    if suffix in (".json", ".jsonl", ".ndjson"):
        return {"": pd.read_json(path, lines=suffix != ".json")}
    raise SystemExit(f"Error: unsupported format {suffix}; supported: csv/tsv, xlsx, parquet, json/jsonl")


def profile_frame(df: pd.DataFrame, label: str) -> None:
    if label:
        print(f"\n===== Sheet: {label!r}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    dupes = df.duplicated().sum()
    if dupes:
        print(f"WARNING: {dupes} fully duplicated row(s). Decide deliberately whether they are real repeats or an export artifact before aggregating.")

    print(f"\n{'column':<24} {'nulls':>7} {'unique':>7}  notes")
    for col in df.columns:
        s = df[col]
        nulls = s.isna().sum()
        nunique = s.nunique(dropna=True)
        notes = []
        sample = s.dropna().astype(str)
        if not sample.empty:
            head = sample.head(200)
            if head.str.fullmatch(r"0\d+").any():
                notes.append("leading zeros: keep as string, numeric cast destroys them")
            if head.str.contains(r"^[\$€£]|,\d{3}", regex=True).mean() > 0.5:
                notes.append("currency/thousands formatting: strip before numeric use")
            if head.str.fullmatch(r"-?[\d,.]+[%]?").all() and s.dtype == object:
                notes.append("numeric-looking strings")
            # compare uniques within the same sample, or high-cardinality columns false-positive
            stripped = head.str.strip().str.lower()
            if head.nunique() > stripped.nunique():
                notes.append("case/whitespace variants collapse distinct values: normalize before grouping")
            if head.str.fullmatch(r"\d{4,5}(\.0)?").all() and ("date" in col.lower() or "day" in col.lower()):
                notes.append("possible Excel serial dates")
        mn = mx = ""
        try:
            mn, mx = str(s.min())[:19], str(s.max())[:19]
        except TypeError:
            notes.append("mixed types: min/max undefined")
        print(f"{col[:24]:<24} {nulls:>7} {nunique:>7}  {'; '.join(notes)}")
        if mn or mx:
            print(f"{'':<24} {'':>7} {'':>7}  range: {mn} .. {mx}")

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: uv run {sys.argv[0]} <file.csv|.tsv|.xlsx|.parquet|.json|.jsonl>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 1
    frames = load(path)
    print(f"File: {path} ({path.stat().st_size:,} bytes)")
    for label, df in frames.items():
        profile_frame(df, label)
    print("\nNOTE: text formats were read with all columns as strings so the profile shows the raw data; cast types deliberately in the analysis script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
