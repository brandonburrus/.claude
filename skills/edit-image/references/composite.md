# Composite and effects

Overlaying images (watermarks, logos) and pixel effects (grayscale, tint, blur, sharpen,
flatten). Compositing with control over opacity/scale is the main reason to drop from
`sharp-cli` to the `sharp` library; the `watermark.mjs` script wraps the common case.

## Watermark / overlay (use the bundled script first)

```bash
# Composite an overlay onto a base image at a gravity, with optional opacity and scale.
node ${CLAUDE_SKILL_DIR}/scripts/watermark.mjs base.jpg logo.png out.jpg \
  --gravity southeast --opacity 0.5 --scale 0.2
```

- `--gravity`: `north south east west center` or corners `northeast northwest southeast southwest`.
- `--opacity`: 0..1, applied by scaling the overlay's alpha channel.
- `--scale`: overlay width as a fraction of the base width (e.g. `0.2` = 20%).

## sharp library

```js
import sharp from 'sharp';

// composite([{ input, ... }]) draws each input OVER the pipeline image.
// Position with gravity, or absolute top/left; blend sets the Porter-Duff/PDF mode.
await sharp('base.jpg')
  .composite([{ input: 'logo.png', gravity: 'southeast' }])
  .toFile('out.jpg');

await sharp('base.jpg')
  .composite([{ input: 'logo.png', top: 20, left: 20, blend: 'over' }])
  .toFile('out.jpg');

// Semi-transparent overlay: multiply the overlay alpha with a uniform alpha tile.
// dest-in keeps the overlay's colour and scales its alpha by the tile's alpha.
const faded = await sharp('logo.png').ensureAlpha().composite([{
  input: Buffer.from([255, 255, 255, 128]),   // alpha 128/255 ~= 50%
  raw: { width: 1, height: 1, channels: 4 },
  tile: true,
  blend: 'dest-in',
}]).png().toBuffer();
await sharp('base.jpg').composite([{ input: faded, gravity: 'center' }]).toFile('out.jpg');
```

## Effects

```js
import sharp from 'sharp';

await sharp('in.jpg').grayscale().toFile('out.jpg');             // (greyscale also works)
await sharp('in.jpg').tint('#ff0000').toFile('out.jpg');         // colourise
await sharp('in.jpg').blur(5).toFile('out.jpg');                 // sigma 0.3..1000
await sharp('in.jpg').sharpen({ sigma: 2 }).toFile('out.jpg');
await sharp('in.jpg').negate().toFile('out.jpg');
await sharp('in.jpg').normalise().toFile('out.jpg');             // stretch contrast

// Flatten transparency onto a solid background (required when converting RGBA -> JPEG,
// which has no alpha channel; otherwise the transparent areas turn black).
await sharp('in.png').flatten({ background: '#ffffff' }).jpeg().toFile('out.jpg');
```

`sharp-cli` exposes simple forms of these too (`greyscale`, `tint <rgb>`, `blur [sigma]`,
`sharpen [sigma]`, `flatten [background]`), but multi-step pipelines and opacity belong in
a Node script.
