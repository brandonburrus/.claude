# /// script
# requires-python = ">=3.12"
# dependencies = ["pypdf>=5", "pdfplumber>=0.11"]
# ///
"""Dump the structure of a PDF so work on it can be planned safely.

Reports pages, encryption, metadata, form fields (with names and types, needed
for filling), outline/bookmarks, and per-page text/table presence. Critically,
it detects pages with no extractable text (scanned images), which silently
defeat text extraction.
"""

import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: uv run {sys.argv[0]} <file.pdf>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 1

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        if not reader.decrypt(""):
            print("Error: PDF is password-protected; a password is required to read it.")
            return 1
        print("NOTE: PDF was encrypted with an empty owner password; opened.")

    print(f"PDF: {path}")
    print(f"Pages: {len(reader.pages)}")
    meta = reader.metadata or {}
    shown = {k: str(v)[:60] for k, v in meta.items() if v}
    if shown:
        print(f"Metadata: {shown}")

    fields = reader.get_fields()
    if fields:
        print(f"\nForm fields ({len(fields)}):")
        for name, f in list(fields.items())[:40]:
            ftype = f.get("/FT", "?")
            value = f.get("/V", "")
            states = f.get("/_States_", "")
            extra = f" states={states}" if states else ""
            print(f"  {name!r}: type={ftype} value={value!r}{extra}")
        if len(fields) > 40:
            print(f"  ... and {len(fields) - 40} more")
    else:
        print("\nNo fillable form fields (filling requires overlay, not field values).")

    if reader.outline:
        def walk(items, depth=0):
            for item in items:
                if isinstance(item, list):
                    walk(item, depth + 1)
                else:
                    print(f"  {'  ' * depth}{item.title}")
        print("\nOutline:")
        walk(reader.outline)

    print("\nPer-page text:")
    scanned = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            tables = len(page.find_tables())
            images = len(page.images)
            status = f"  page {i}: {len(text)} chars, {tables} table(s), {images} image(s)"
            if len(text.strip()) < 20 and images:
                status += "  <- likely scanned (image, no text layer)"
                scanned.append(i)
            print(status)
    if scanned:
        print(f"\nWARNING: pages {scanned} appear to be scanned images with no text layer. Text extraction returns nothing for them; OCR is required and is outside this skill's scope. Say so rather than reporting the page as empty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
