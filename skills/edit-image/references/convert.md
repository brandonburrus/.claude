# Convert and compress

Format conversion, per-format quality/compression, and metadata handling. Covers both
the `sharp-cli` quick path and the `sharp` library path.

## sharp-cli

```bash
# Convert: -o is an output DIRECTORY; the file is written as <basename>.<ext>.
npx -y sharp-cli -i photo.png -o ./out -f jpeg            # -> ./out/photo.jpg
npx -y sharp-cli -i photo.png -o ./out -f webp -q 80      # quality 1..100 (lossy formats)
npx -y sharp-cli -i logo.png  -o ./out -f avif -q 50
```

- `-f, --format`: one of `avif gif heif jpeg jpg png raw tiff webp`. Omit to infer from
  the output extension. The `jpeg` format is written with a `.jpg` extension.
- `-q, --quality`: 1..100, default 80. Applies to lossy formats (jpeg, webp, avif); it is
  ignored for png (png is lossless, see compression below).
- `-m, --metadata`: keep input metadata on the output (EXIF/ICC). It is an OUTPUT flag,
  so it needs `-i` and `-o`; it cannot print metadata. To READ image info, use the
  inspect script (see SKILL.md), not the CLI.

## sharp library (for per-format tuning the CLI does not expose)

By default sharp STRIPS all metadata (including EXIF orientation) on output. Call
`.keepMetadata()` to retain it, or `.keepExif()` / `.keepIccProfile()` for a subset.

```js
import sharp from 'sharp';

// PNG: lossless. compressionLevel 0..9 (default 6) trades speed for size; quality is
// only meaningful with palette: true (quantised PNG, much smaller for flat graphics).
await sharp('in.png').png({ compressionLevel: 9, palette: true }).toFile('out.png');

// JPEG: mozjpeg gives the best size/quality; progressive helps large photos.
await sharp('in.png').jpeg({ quality: 82, mozjpeg: true, progressive: true }).toFile('out.jpg');

// WebP: effort 0..6 (default 4, higher = smaller/slower); lossless for graphics.
await sharp('in.png').webp({ quality: 80, effort: 6 }).toFile('out.webp');
await sharp('in.png').webp({ lossless: true }).toFile('out.webp');

// AVIF: smallest files; quality default 50, effort 0..9 (default 4).
await sharp('in.png').avif({ quality: 50, effort: 4 }).toFile('out.avif');

// Strip metadata to shrink (default), or keep it explicitly:
await sharp('in.jpg').jpeg({ quality: 80 }).toFile('stripped.jpg');     // metadata gone
await sharp('in.jpg').keepMetadata().jpeg().toFile('kept.jpg');         // EXIF/ICC kept
```

## Choosing a format

| Goal | Format | Why |
|---|---|---|
| Photographs, broad compatibility | jpeg (mozjpeg) | Best size/quality for photos, universal support |
| Transparency, sharp edges, text/UI | png | Lossless, alpha channel |
| Smaller web delivery, transparency | webp | ~30% smaller than jpeg/png, supports alpha + animation |
| Smallest web delivery | avif | Best compression; slower to encode, narrower support |
| Animation | gif or webp | Multi-page output (inspect reports `pages > 1`) |
