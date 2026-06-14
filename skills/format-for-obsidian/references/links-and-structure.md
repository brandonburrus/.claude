Obsidian note structure and linking syntax. Load when writing properties, internal links, embeds, callouts, or tags. The SKILL.md Essentials cover the common cases; this file is the complete catalog.

## Contents

- [Properties (frontmatter)](#properties-frontmatter)
- [Internal links (wikilinks)](#internal-links-wikilinks)
- [Embeds](#embeds)
- [Callouts](#callouts)
- [Tags](#tags)

## Properties (frontmatter)

Properties are stored in a YAML block delimited by `---` at the very top of the file.

```yaml
---
title: My Note
tags:
  - journal
  - project/alpha
aliases:
  - My Old Title
cssclasses:
  - wide-page
date: 2024-03-15
---
```

**Supported property types:**

| Type | Format | Example |
| --- | --- | --- |
| Text | Single line string | `title: A New Hope` |
| List | YAML list | `tags:\n  - one\n  - two` |
| Number | Integer or decimal | `year: 1977` |
| Checkbox | `true` or `false` | `draft: true` |
| Date | `YYYY-MM-DD` | `date: 2024-03-15` |
| Date & time | `YYYY-MM-DDTHH:MM:SS` | `time: 2024-03-15T10:30:00` |

**Default Obsidian properties:**

- `tags`: list of tag strings (no `#` prefix needed here)
- `aliases`: alternative names for the note
- `cssclasses`: list of CSS class names for per-note styling

**Obsidian Publish properties:** `publish`, `permalink`, `description`, `image`, `cover`

**Rules:**
- Internal links in property values must be quoted: `link: "[[Note Name]]"`
- Internal links in list properties must also be quoted: `- "[[Note Name]]"`
- Markdown formatting is not rendered inside properties
- Avoid deprecated forms: `tag`, `alias`, `cssclass`; use their plural equivalents

## Internal links (wikilinks)

```md
[[Note Name]]
[[Note Name|Display Text]]
[[Note Name#Heading]]
[[Note Name#Heading|Display Text]]
[[#Heading in this note]]
[[Note Name#^block-id]]
[[Note Name#^block-id|Display Text]]
```

**Searching across the vault:**

```md
[[##search term]]   link to any heading matching "search term"
[[^^search term]]   link to any block matching "search term"
```

**Markdown link format (interoperable alternative):**

```md
[Display Text](Note%20Name.md)
[Section](Note%20Name.md#Heading)
```

Blank spaces in Markdown-format links must be URL-encoded as `%20`. Prefer Wikilink format unless interoperability with non-Obsidian tools is required.

**Block identifiers**: append to the end of a paragraph with a blank space and `^`:

```md
This is the paragraph you want to reference. ^my-block-id
```

For structured blocks (lists, callouts, tables), the identifier goes on its own line with blank lines around it:

```md
- item one
- item two

^my-list-id
```

Block identifiers may only contain Latin letters, numbers, and hyphens.

## Embeds

Prefix any internal link with `!` to embed its content inline.

```md
![[Note Name]]
![[Note Name#Heading]]
![[Note Name#^block-id]]
```

**Images:**

```md
![[image.jpg]]
![[image.jpg|640x480]]   explicit width and height
![[image.jpg|100]]       width only, preserves aspect ratio
```

**External image with size control:**

```md
![alt text|100x145](https://example.com/image.jpg)
![alt text|100](https://example.com/image.jpg)
```

**PDFs:**

```md
![[Document.pdf]]
![[Document.pdf#page=3]]         open to page 3
![[Document.pdf#height=400]]     set viewer height in pixels
```

**Audio:** `![[recording.ogg]]`

**YouTube and Twitter/X**: use the standard external image syntax with the full URL:

```md
![](https://www.youtube.com/watch?v=VIDEO_ID)
![](https://twitter.com/user/status/TWEET_ID)
```

**Web pages via iframe:**

```html
<iframe src="https://example.com"></iframe>
```

Note: some sites block iframe embedding. Search for the site name + "embed iframe" if the default URL does not work.

## Callouts

```md
> [!type] Optional custom title
> Callout body content.
> Supports **Markdown**, [[wikilinks]], and ![[embeds]].
```

**Foldable callouts:**

```md
> [!tip]+ Expanded by default
> Body text here.

> [!warning]- Collapsed by default
> Body text here.
```

**Nested callouts:**

```md
> [!question] Can callouts be nested?
> > [!todo] Yes, they can.
> > > [!example] Multiple levels work too.
```

**Supported types and their aliases:**

| Type | Aliases |
| --- | --- |
| `note` | None |
| `abstract` | `summary`, `tldr` |
| `info` | None |
| `todo` | None |
| `tip` | `hint`, `important` |
| `success` | `check`, `done` |
| `question` | `help`, `faq` |
| `warning` | `caution`, `attention` |
| `failure` | `fail`, `missing` |
| `danger` | `error` |
| `bug` | None |
| `example` | None |
| `quote` | `cite` |

Type identifiers are case-insensitive. Any unsupported type defaults to the `note` style.

## Tags

**Inline tags**: use a `#` prefix directly in note body text:

```md
This note is about #productivity and #writing/fiction.
```

**Nested tags**: use `/` to create a hierarchy:

```md
#inbox/to-read
#project/alpha/design
```

**Valid characters:** letters, numbers, `_`, `-`, `/`, Unicode characters and emoji. Tags must contain at least one non-numeric character. No spaces allowed; use `#camelCase`, `#PascalCase`, `#snake_case`, or `#kebab-case`.

Tags are case-insensitive. When searching `tag:inbox`, Obsidian matches `#inbox` and all nested variants like `#inbox/to-read`.

In frontmatter, list tags without the `#` prefix:

```yaml
tags:
  - productivity
  - writing/fiction
```
