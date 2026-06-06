---
name: edit-word-doc
description: >-
  Use this skill when creating, editing, or reading Microsoft Word documents
  (.docx), including text, headings, styles, tables, images, and headers or
  footers. Use when the user says "create a Word doc", "update this docx",
  "read the Word document", "fill in this template", or references a .docx
  file. Do not use for Markdown or plain-text writing (write directly), for
  PDFs (use edit-pdf), or for legacy .doc files without converting them to
  .docx first.
---

## Purpose

Create, edit, and read Word documents with python-docx through small per-task Python scripts run with uv. The central trap in this format is that what looks like contiguous text is not: Word fragments paragraph text across runs unpredictably, so naive find-and-replace either misses matches or destroys formatting. Every edit follows the inspect, edit a copy, verify loop.

## Workflow

1. **Inspect first**: `uv run ${CLAUDE_SKILL_DIR}/scripts/inspect-document.py <file>`. The output shows the outline, styles in use, tables, headers/footers, and warns about tracked changes (which python-docx cannot edit). Reading a .docx as raw text loses the structure the edit needs to respect.
2. **Edit a copy, not the original**; replace it only after verification.
3. **Write a per-task script** with PEP 723 inline deps:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["python-docx>=1.1"]
# ///
from docx import Document
from docx.shared import Inches, Pt

doc = Document("input.docx")
doc.add_heading("Q3 Summary", level=2)
p = doc.add_paragraph("Revenue grew ")
p.add_run("18%").bold = True
doc.save("output.docx")
```

4. **Verify by re-opening**: load the output, assert the new text is present, the paragraph count and style usage look right, and untouched content survived. For replacements, assert the old string is gone everywhere it should be and nowhere it should not.

## The run-fragmentation rule

`paragraph.text` reads cleanly, but the text lives in runs, and Word splits runs at arbitrary points (spell-check passes, formatting history, revision saves). The two safe edit patterns:

- **Replace within runs when the target is short and likely intact**: iterate `paragraph.runs`, replace in `run.text`. Preserves formatting. Misses matches that straddle run boundaries.
- **Rebuild the paragraph when the match straddles runs**: check `target in paragraph.text`, then rewrite at the paragraph level by clearing runs and re-adding the assembled text. Loses per-run formatting inside that paragraph, so capture what formatting matters first (bold spans, links) and reapply.

Never set `paragraph.text = ...` across a whole document as a replace strategy; it silently flattens every formatted span in every touched paragraph. Search headers, footers, and table cells too; text the user wants replaced is frequently in all three.

## Common operations

| Operation | How |
|---|---|
| New document | `Document()` for default template; `Document("template.docx")` to inherit its styles, headers, and branding |
| Headings | `doc.add_heading(text, level=N)`; maps to Heading N styles |
| Styled paragraph | `doc.add_paragraph(text, style="Quote")`; the style must already exist in the document or python-docx raises KeyError |
| Inline formatting | Build the paragraph from runs: `p.add_run("bold").bold = True`; formatting is per-run, not per-paragraph |
| Tables | `doc.add_table(rows, cols, style="Table Grid")`; cells via `table.cell(r, c).text`; cells contain paragraphs, so rich content goes through `cell.paragraphs[0].add_run(...)` |
| Images | `doc.add_picture("chart.png", width=Inches(5.5))`; always set width or it imports at native DPI size |
| Page break | `doc.add_page_break()`; section break via new `doc.add_section()` |
| Headers/footers | Per section: `section.header.paragraphs[0].text = ...`; check `header.is_linked_to_previous` |
| Lists | Paragraph styles "List Bullet" / "List Number"; nesting via "List Bullet 2" etc. |
| Fill a template | Open the template, replace placeholder tokens (run-fragmentation rule applies), save as new file |

## Gotchas

- **Styles must exist before use.** A style name not defined in the document raises KeyError; the inspector lists what is available. The reliable way to get corporate styling is to start from the user's template file, not to rebuild styles in code.
- **python-docx has no concept of pages.** Page count, page numbers, and "what is on page 3" are layout-time facts that only a renderer knows. Do not promise page-accurate edits; if a rendered check matters and LibreOffice is installed, convert to PDF (`soffice --headless --convert-to pdf`) and inspect that.
- **Tracked changes are invisible to python-docx and survive edits untouched.** A document with pending revisions reads as partial text and saves with the revision markup intact. The inspector warns; have the user accept/reject revisions first, or state that revisions were left as-is.
- **`doc.paragraphs` does not include table, header, or footer text.** Whole-document operations must walk `doc.tables` (recursively: cells can nest tables) and each section's header and footer explicitly.
- **Empty paragraphs are content.** Word documents are full of empty spacing paragraphs; deleting them "to clean up" changes the visual layout users expect. Leave structure alone unless asked.
- **Hyperlinks are not runs.** python-docx exposes them poorly; text inside hyperlinks does not appear in `paragraph.runs` (it does appear in `paragraph.text` in recent versions). Replacing link text means editing the XML or recreating the hyperlink; flag it rather than silently skipping.
