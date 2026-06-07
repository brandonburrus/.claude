---
name: edit-powerpoint-slides
description: >-
  Use this skill when creating, editing, or reading PowerPoint presentations
  (.pptx), including slides, layouts, placeholders, text, images, tables,
  charts, speaker notes, and click-to-reveal builds and animations. Use when
  the user says "make a slide deck", "create a presentation", "update these
  slides", "add a slide", "reveal the bullets one at a time", or references
  a .pptx file. Do not use for diagrams as standalone artifacts (use
  create-diagram), for visual design direction of non-slide UIs (use
  design-ui), or for legacy .ppt files without converting to .pptx first.
---

## Purpose

Create, edit, and read PowerPoint decks with python-pptx through small per-task Python scripts run with uv. Decks are template-driven: slides get their look from the master's layouts, so the difference between a deck that matches the user's brand and an obviously generated one is whether the edit works through the existing layouts and placeholders or draws ad-hoc text boxes. Every edit follows the inspect, edit a copy, verify loop.

## Workflow

1. **Inspect first**: `uv run ${CLAUDE_SKILL_DIR}/scripts/inspect-presentation.py <file>`. The output lists slide size, the master's layouts with their placeholder idx values, and every slide's shapes and notes. Placeholder idx values are how edits target the right box; never guess them.
2. **Edit a copy, not the original**; replace it only after verification.
3. **Write a per-task script** with PEP 723 inline deps:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx>=1.0"]
# ///
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("deck.pptx")          # existing deck = its layouts and branding
layout = prs.slide_layouts[1]            # index from the inspector, not guessed
slide = prs.slides.add_slide(layout)
slide.placeholders[0].text = "Q3 Results"
body = slide.placeholders[1].text_frame
body.text = "Revenue up 18%"
body.add_paragraph().text = "Churn down 0.4pt"
prs.save("deck-updated.pptx")
```

4. **Verify by re-opening**: slide count, the new slide's text via its placeholders, and untouched slides intact. python-pptx cannot render, so describe what was verified structurally. For a visual check, render to PDF with LibreOffice: `soffice --headless --convert-to pdf <file>` (on macOS soffice is not on PATH; it lives at `/Applications/LibreOffice.app/Contents/MacOS/soffice`). Pass a fresh `-env:UserInstallation=file:///tmp/<new-dir>` each run, because a reused profile silently returns a stale render, and close the .pptx first or the convert is blocked.

## Working with the template

- **To extend an existing deck, open it and use its layouts.** `Presentation("their-deck.pptx")` carries the master, fonts, and colors; `Presentation()` gives the bare default template. To create a branded deck from scratch, ask for a template file before inventing styling.
- **Choose layouts by what the inspector shows**, not the conventional indexes; decks reorder them freely. Title-only, title+content, section header, and blank are the usual working set.
- **Fill placeholders rather than adding text boxes.** Placeholder text inherits the deck's typography and position; an `add_textbox` carries none of it. Use text boxes only for content the layout genuinely has no placeholder for.
- **Slide titles**: `slide.shapes.title` when the layout has one; other placeholders via `slide.placeholders[idx]` using the inspector's idx values (they are not sequential).

## Common operations

| Operation | How |
|---|---|
| Sizes and positions | Everything is EMU; always use `Inches(...)` / `Pt(...)` helpers, never raw ints |
| Bullets | Paragraphs in a body placeholder: `tf.add_paragraph()` + `para.level = 1` for nesting; first paragraph is `tf.text` |
| Run formatting | `run.font.size = Pt(18)`, `.bold`, `.color.rgb = RGBColor(0x1F, 0x4E, 0x79)`; per-run, like Word |
| Images | `slide.shapes.add_picture("chart.png", Inches(1), Inches(1.5), width=Inches(8))`; set width or height, the other scales |
| Tables | `shapes.add_table(rows, cols, left, top, width, height)`; cell text via `table.cell(r, c).text` |
| Charts | `shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, CategoryChartData(...))`; editing an existing chart's data uses `chart.replace_data(...)` |
| Speaker notes | `slide.notes_slide.notes_text_frame.text = ...`; accessing `notes_slide` creates it if absent |
| Reorder slides | No public API; requires manipulating `prs.slides._sldIdLst` XML element order |

## Builds and animations

python-pptx has no animation API; click-to-reveal builds are raw `<p:timing>` XML appended to the slide element. Each click is an entrance effect (presetID 1, presetClass "entr") whose `<p:set>` flips the target's visibility to visible.

- **Build text by paragraph with `build="p"` in `<p:bldP>`.** Valid `ST_TLParaBuildType` values are `allAtOnce`, `p`, `cust`, `whole`; the plausible-looking `byParagraph` is invalid, and PowerPoint silently reveals the whole shape at once instead.
- **A table animates only as one object.** There is no row-level target, so to reveal rows one at a time, build each row as its own one-row table stacked seamlessly and animate each; splitting the table means re-creating banding with explicit cell fills.
- **Verify builds structurally, not by rendering.** A PDF render shows the fully-built slide, so confirm builds by counting `clickEffect` nodes and checking `bldP` build values in the XML, then have the user confirm the click sequence in PowerPoint.

## Gotchas

- **There is no delete-slide API.** python-pptx cannot remove a slide through its public interface; deletion means dropping the slide's entry from the `_sldIdLst` XML and its relationship. When asked to delete slides, either do the XML manipulation deliberately and verify the deck still opens, or rebuild a new deck copying the slides to keep; say which you did.
- **Overfull text does not shrink.** PowerPoint's autofit is computed by the renderer, not stored in the file, so python-pptx happily writes text that overflows its box invisibly. Budget content to the box: roughly 5-7 bullets per content placeholder, titles on one line; when in doubt, less text per slide.
- **Copying a slide between decks is not supported.** Cross-deck copy drags layout, master, and relationship dependencies; the practical route is recreating the slide's content on the target deck's closest layout.
- **`slide.shapes.title` can be None** on layouts without a title placeholder; check before assigning or the edit dies mid-script.
- **Text extraction misses grouped shapes and SmartArt.** Reading a deck means walking `shape.shape_type == MSO_SHAPE_TYPE.GROUP` recursively, and SmartArt text is not exposed by python-pptx at all; the inspector shows shape types so silence about a SmartArt-heavy slide is detectable rather than assumed empty.
- **16:9 vs 4:3 changes every position, and the default master is 4:3.** Read `prs.slide_width` before computing any placement; hardcoded positions for one aspect ratio land off-slide in the other. If you set a 16:9 size on the default template, inherited title and body placeholders keep their 4:3 (left-half-width) geometry, so centered text lands left of center even with `algn=ctr`. Fix by setting the placeholder's left, top, width, and height to span the slide, and set all four together: assigning just one (e.g. `.left`) materializes the transform and zeroes the rest.
- **A named font that is not installed renders with wrong metrics** (loose spacing, wrong widths) in both LibreOffice and PowerPoint, even though the .pptx names the right font. Install the font (on macOS, drop the .ttf into `~/Library/Fonts`) before rendering, or embed it in the file so it travels.
