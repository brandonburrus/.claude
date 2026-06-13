---
name: edit-image
description: Use this skill when manipulating or converting raster images with sharp,
  including "convert this png to jpg", "resize this image", "make a thumbnail", "compress
  this photo", "crop/rotate/flip this image", "strip EXIF metadata", "add a watermark",
  "overlay my logo", "batch convert these images", or "what are this image's dimensions".
  Covers jpeg, png, webp, avif, gif, tiff. Do not use for creating diagrams (use
  create-diagram), charts or plots from data (use visualize-data or analyze-data), editing
  PDFs (use edit-pdf), or vector/SVG authoring.
---

## Purpose

Manipulate and convert raster images using [sharp](https://sharp.pixelplumbing.com). Two
tiers: reach for the quick path (`sharp-cli` via `npx`) for single conversions and simple
transforms, and the script path (global `sharp` + a Node script) for multi-step
pipelines, compositing, batch work, and reading image info. Always confirm the result by
inspecting the output dimensions/format, not by assuming the command worked.

## Routing

- Single convert, resize, crop, rotate, or one simple effect on one file -> **sharp-cli**
  (no install, runs from the npx cache).
- Multi-step pipeline, watermark/overlay, opacity, many files, or reading metadata ->
  **Node script** against the global sharp install (the bundled scripts cover the common
  cases; write an ad-hoc `.mjs` for anything else).

## Quick path: sharp-cli

`sharp-cli` needs no install; `npx -y` runs it from cache. General form:

```bash
npx -y sharp-cli -i <input> -o <output-dir> [-f <format>] [-q <1-100>] <command> [args] -- <command2> [args]
```

```bash
npx -y sharp-cli -i photo.png -o ./out -f jpeg            # convert png -> ./out/photo.jpg
npx -y sharp-cli -i photo.jpg -o ./out resize 800         # width 800, height auto
npx -y sharp-cli -i photo.jpg -o ./out -f webp -q 80 rotate 90 -- resize 400   # chained
```

`-o` is an output **directory**, not a filename: sharp-cli writes `<basename>.<ext>` into
it (and `jpeg` lands as `.jpg`). Chain operations in one pass by separating them with `--`.

For the full command surface and per-task detail, read the reference for the task at hand:

- Converting formats, quality/compression, metadata -> read `references/convert.md`
- Resizing, thumbnails, cropping, rotating, flipping -> read `references/resize.md`
- Watermarks, overlays, grayscale/tint/blur effects -> read `references/composite.md`

## Script path: global sharp + Node

For anything sharp-cli cannot express in one pass, install sharp once and run a Node
script that uses its chaining API.

1. Install once (idempotent; skip if `npm ls -g sharp` already resolves):

   ```bash
   npm i -g sharp
   ```

2. Run a bundled script (or your own `.mjs`) with plain `node`:

   ```bash
   node ${CLAUDE_SKILL_DIR}/scripts/inspect.mjs <image>                 # print format/size/metadata as JSON
   node ${CLAUDE_SKILL_DIR}/scripts/watermark.mjs <base> <overlay> <out> [--gravity southeast] [--opacity 0.5] [--scale 0.2]
   node ${CLAUDE_SKILL_DIR}/scripts/batch.mjs <input-dir> <output-dir> [--format webp] [--quality 80] [--width N] [--height N]
   ```

   - `inspect.mjs` is how you READ image info; sharp-cli cannot print metadata.
   - `watermark.mjs` composites an overlay at a gravity, with optional opacity and scale.
   - `batch.mjs` converts/resizes every image in a directory, keeping base names.

### Writing an ad-hoc script

A global install is **not** on Node's ESM resolution path, and Node ignores `NODE_PATH`
for `import`. Resolve sharp by basing a `require` at the global `node_modules` root, so the
script runs from any directory with no env setup:

```js
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const sharp = createRequire(execSync('npm root -g').toString().trim() + '/anchor.js')('sharp');

await sharp('in.png')
  .resize({ width: 1200, withoutEnlargement: true })
  .jpeg({ quality: 82, mozjpeg: true })
  .toFile('out.jpg');
```

The bundled scripts use exactly this header; copy one as a starting template.

## Gotchas

- **`-o` is a directory, not a filename.** sharp-cli writes `<basename>.<ext>` into it.
  To rename, move the output afterward, or write a Node script that calls `.toFile(path)`.
- **`NODE_PATH` does nothing for ESM.** Use the `createRequire`-from-global-root header
  above; do not prefix `node` with `NODE_PATH`.
- **sharp-cli cannot read metadata.** Its `--metadata` is an output flag (it keeps EXIF on
  the result). Use `inspect.mjs` to read dimensions/format/EXIF.
- **Metadata is stripped by default.** sharp drops EXIF (including orientation) and ICC on
  output unless you call `.keepMetadata()`. Good for shrinking, surprising if you needed it.
- **`extract` arg order differs.** sharp-cli is `extract <top> <left> <w> <h>`; the library
  object is `{ left, top, width, height }`.
- **RGBA -> JPEG turns transparency black.** JPEG has no alpha; `.flatten({ background })`
  onto a solid colour before encoding.
- **`quality` is for lossy formats.** It is ignored by png; use `compressionLevel`/`palette`
  for png size instead.

## Examples

Convert a folder of PNG screenshots to optimized WebP thumbnails (max 400px wide):

```bash
npm i -g sharp
node ${CLAUDE_SKILL_DIR}/scripts/batch.mjs ./screenshots ./thumbs --format webp --quality 80 --width 400
node ${CLAUDE_SKILL_DIR}/scripts/inspect.mjs ./thumbs/first.webp   # confirm format + dimensions
```
