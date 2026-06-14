---
name: format-for-obsidian
description: Use this skill when writing or formatting Markdown files for an Obsidian
  vault. Use when the user mentions Obsidian, vault, wikilinks, or Obsidian-flavored
  Markdown, or when a .obsidian directory is detected. Do not use for GitHub READMEs,
  static site generators, or any Markdown renderer that is not Obsidian.
---

## Purpose

Produce Markdown that renders correctly in Obsidian, using its syntax extensions beyond CommonMark and GFM. Obsidian's base is CommonMark + GFM + LaTeX; everything Obsidian-specific is cataloged in the references below.

When a `.obsidian` directory is detected in the working directory or any ancestor, ask first: "I noticed a `.obsidian` directory, would you like me to use Obsidian-flavored Markdown syntax?" The directory proves Obsidian is present, not that every file is vault content.

## Essentials

The high-frequency syntax; load a reference below for the full catalog.

- **Internal link:** `[[Note]]`, aliased `[[Note|Display Text]]`, to a heading `[[Note#Heading]]`. Prefer wikilinks over `[text](Note%20Name.md)` unless the file must stay portable to non-Obsidian tools.
- **Embed:** prefix any link with `!`: `![[Note]]`, `![[image.png|400]]` (width), `![[Document.pdf#page=3]]`.
- **Frontmatter:** a YAML `---` block at the very top. Quote internal links in values (`link: "[[Note]]"`); use the plural keys `tags` / `aliases` / `cssclasses` (the singular forms are deprecated).
- **Callout:** `> [!note] Optional title` then `>` body lines; make it foldable with `+` (open) or `-` (collapsed) after the type.
- **Tag:** `#tag`, nested `#parent/child`; in frontmatter list tags without the `#`.
- **Highlight** `==text==`; **comment** `%%hidden in reading view%%`; **strikethrough** `~~text~~`.

## Reference routing

Load only the file the task needs:

| The task involves | Load |
|---|---|
| Property types and rules, wikilink search and block IDs, image/PDF/audio/iframe embeds, the full callout type-and-alias table, tag rules | [links-and-structure.md](references/links-and-structure.md) |
| Highlights, comments, footnotes, custom task statuses, escaping, tables with embedded links, Mermaid diagrams, LaTeX math, HTML and its limits | [rich-content.md](references/rich-content.md) |

## Gotchas

- **A detected `.obsidian` directory is a signal, not a mandate.** Ask the user before applying Obsidian-flavored syntax to files in such a project; the directory proves Obsidian is present, not that every Markdown file is vault content.
- **Static site generators need confirmation first.** Wikilinks and callouts break in Hugo, Jekyll, MkDocs, and Docusaurus unless an Obsidian-compatible renderer plugin is installed; confirm before using them in SSG content, and prefer plain CommonMark when the file must stay portable across tools.
