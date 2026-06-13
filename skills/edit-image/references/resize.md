# Resize, crop, rotate

Sizing and geometry: resize/thumbnail, crop (extract), rotate, flip, extend, trim.
Covers both the `sharp-cli` quick path and the `sharp` library path.

## sharp-cli

```bash
# Resize. One dimension keeps aspect ratio (omit the other).
npx -y sharp-cli -i in.png -o ./out resize 800            # width 800, height auto
npx -y sharp-cli -i in.png -o ./out resize 800 600        # fit within 800x600

# Crop: extract <top> <left> <width> <height>  (NOTE the CLI order: top, left first).
npx -y sharp-cli -i in.png -o ./out extract 10 20 200 150

# Rotate / flip / flop.
npx -y sharp-cli -i in.png -o ./out rotate 90
npx -y sharp-cli -i in.png -o ./out flip                  # vertical (top-bottom)
npx -y sharp-cli -i in.png -o ./out flop                  # horizontal (left-right)

# Chain operations in one pass with `--` between commands.
npx -y sharp-cli -i in.png -o ./out -f webp rotate 90 -- resize 400
```

- `extract` CLI arg order is `<top> <left> <width> <height>` and differs from the library
  object `{ left, top, width, height }`. This is the most common crop mistake.
- Other commands: `extend <top> <bottom> <left> <right>`, `trim [threshold]`.

## sharp library

```js
import sharp from 'sharp';

// resize(width, height, options). fit controls how the image adapts:
//   cover (default) crop to fill; contain letterbox; fill stretch;
//   inside fit within; outside cover at minimum.
await sharp('in.png').resize(800, 600, { fit: 'cover', position: 'center' }).toFile('out.png');
await sharp('in.png').resize(800, 600, { fit: 'contain', background: '#ffffff' }).toFile('out.png');

// Thumbnail that never upscales a smaller source.
await sharp('in.png').resize({ width: 200, withoutEnlargement: true }).toFile('thumb.png');

// Crop a region. extract takes { left, top, width, height } (library order).
await sharp('in.png').extract({ left: 20, top: 10, width: 200, height: 150 }).toFile('out.png');

// Rotate by angle (fills new corners with background), or autoOrient by EXIF tag.
await sharp('in.jpg').rotate(90).toFile('out.jpg');
await sharp('in.jpg').rotate(45, { background: '#00000000' }).toFile('out.png');
await sharp('in.jpg').autoOrient().toFile('out.jpg');     // honor camera EXIF orientation

await sharp('in.png').flip().toFile('out.png');           // vertical mirror
await sharp('in.png').flop().toFile('out.png');           // horizontal mirror

// Add a border / pad, or auto-trim a uniform border.
await sharp('in.png').extend({ top: 10, bottom: 10, left: 10, right: 10, background: '#fff' }).toFile('out.png');
await sharp('in.png').trim({ threshold: 10 }).toFile('out.png');
```

## fit modes

| fit | Behavior |
|---|---|
| `cover` (default) | Preserve aspect, crop to fill both dimensions |
| `contain` | Preserve aspect, letterbox with `background` to fit both dimensions |
| `fill` | Ignore aspect, stretch to exact dimensions |
| `inside` | Preserve aspect, as large as possible within both dimensions |
| `outside` | Preserve aspect, as small as possible covering both dimensions |

`position` (for cover/contain): `top`, `right`, `bottom`, `left`, `center`, or corner
combinations like `right top`; gravity names (`north`, `southeast`, ...) also work.
