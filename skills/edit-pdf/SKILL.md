---
name: edit-pdf
description: >-
  Use this skill when creating, editing, or reading PDF files, including
  extracting text and tables, merging or splitting documents, rotating pages,
  filling form fields, adding watermarks or page numbers, and generating new
  PDFs such as reports or invoices. Use when the user says "read this PDF",
  "fill out this form", "merge these PDFs", "make a PDF of", or references a
  .pdf file. Do not use for Word documents (use edit-word-doc), for rendering
  Markdown to PDF when a site generator or pandoc pipeline already exists, or
  for OCR of scanned documents (flag it; OCR is out of scope).
---

## Purpose

Create, read, and manipulate PDFs through small per-task Python scripts run with uv, choosing the right tool per job: pdfplumber to extract text and tables, pypdf to manipulate documents (merge, split, rotate, encrypt, fill forms, overlay), reportlab to generate new content. The format's defining constraint drives everything: a PDF is a layout of positioned glyphs, not a structured document, so "edit the text in place" is not an operation that exists; what exists is extraction, page manipulation, overlay, and regeneration.

## Workflow

1. **Inspect first**: `uv run ${CLAUDE_SKILL_DIR}/scripts/inspect-pdf.py <file>`. The output shows pages, encryption, form fields with names and types, the outline, and per-page text presence, including a warning for scanned pages with no text layer.
2. **Edit a copy, not the original**; replace it only after verification.
3. **Pick the tool for the job** (table below) and write a per-task PEP 723 script.
4. **Verify by re-opening**: page counts after merge/split, field values after filling, extracted text after generation. For visual operations (watermarks, overlays), render a check: pdfplumber's `page.to_image()` can save a PNG to look at.

## Tool routing

| Job | Tool |
|---|---|
| Extract text, tables, layout info | pdfplumber |
| Merge, split, reorder, rotate pages | pypdf |
| Read or fill form fields | pypdf |
| Encrypt, decrypt, metadata | pypdf |
| Watermark, stamp, page numbers on existing pages | reportlab (make the overlay) + pypdf (`page.merge_page`) |
| Create a new PDF (report, invoice, letter) | reportlab |
| Modify existing body text in place | No tool; see the no-text-editing rule |

## The no-text-editing rule

PDFs do not support find-and-replace on body text in any reliable way; the text is positioned glyph runs, frequently with subset fonts that do not contain the characters a replacement would need. When the user asks to "change the text in this PDF", the honest options, in order of preference:

1. **Source round-trip**: if the PDF was generated from a source you can edit (a .docx, Markdown, HTML), edit the source and regenerate.
2. **Overlay**: cover the old content with a white rectangle and draw new text on top via a reportlab overlay merged onto the page. Works for small, position-known changes (dates, names, amounts); fragile for flowing text.
3. **Regenerate**: extract the full text, rebuild the document with reportlab, accepting layout differences.

State which path was taken; never imply an in-place edit happened.

## Common operations

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pypdf>=5"]
# ///
from pypdf import PdfReader, PdfWriter

# merge
writer = PdfWriter()
for src in ["a.pdf", "b.pdf"]:
    writer.append(src)
with open("merged.pdf", "wb") as f:
    writer.write(f)
```

| Operation | How |
|---|---|
| Split / extract pages | `writer.append(reader, pages=(0, 3))` zero-indexed, end exclusive |
| Rotate | `writer.pages[i].rotate(90)` clockwise |
| Fill form | `writer.append(reader)` then `writer.update_page_form_field_values(writer.pages[i], {"name": "value"}, auto_regenerate=False)`; set `writer.set_need_appearances_writer(True)` so values render in viewers |
| Checkboxes | The value is the export state from the inspector's `states` list (often `/Yes`), not `True` |
| Flatten form | After filling, `writer.flatten_annotations()` (pypdf 5+) makes values permanent and uneditable |
| Tables out | `pdfplumber.open(p).pages[i].extract_table()`; tune with `table_settings` when borders are sparse |
| Text out | `page.extract_text()`; layout mode `extract_text(layout=True)` preserves columns better |
| Page numbers / watermark | reportlab canvas per page size, then `existing_page.merge_page(overlay_page)` |
| New document | reportlab platypus: `SimpleDocTemplate` + flowables (`Paragraph`, `Table`, `Spacer`, `Image`) for multi-page flow; raw `canvas` for precise one-page layouts |
| Encrypt | `writer.encrypt(user_password)`; decrypt by constructing `PdfReader(path, password=...)` |

## Gotchas

- **Scanned PDFs read as empty, not as errors.** A scanned page is one big image; `extract_text()` returns nothing and no exception. The inspector flags likely scans. Report "scanned, needs OCR" rather than "the page is blank", because the user can see the text in their viewer and a blank report reads as a malfunction.
- **Extraction order is visual-ish, not logical.** Multi-column layouts, headers, and footnotes interleave in extracted text; tables extracted as text lose their grid. Extract tables with pdfplumber's table API, not by parsing text lines.
- **Filled form values can be invisible in viewers.** Without appearance regeneration (`set_need_appearances_writer(True)`) some viewers show empty fields even though the values are stored. Verify by re-reading field values AND, when it matters, rendering the page to an image.
- **Some PDFs have no form fields at all**, just lines and boxes drawn to look like a form. The inspector says which case you have; a fieldless form is filled by overlaying text at measured coordinates, which needs the page rendered to an image to find them.
- **Coordinates origin differs by library.** pdfplumber's y grows downward from the top; reportlab's y grows upward from the bottom-left. Overlay placement that mixes measurements from one into the other lands mirrored; convert with `page_height - y`.
- **Merging preserves bookmarks but not form-field name collisions.** Two merged forms with identical field names become linked fields holding one value; rename fields before merging when both must stay independently fillable.
- **reportlab default page size is A4, not US Letter.** Set `pagesize=letter` (or match the user's locale) explicitly; the 6mm difference clips content printed on the other size.
