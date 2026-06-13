import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { statSync } from 'node:fs';

// sharp is a global install (npm i -g sharp). Node ignores NODE_PATH for ESM
// imports, so resolve sharp by basing a require at the global node_modules root;
// `anchor.js` need not exist, it only seeds the resolution base directory.
const sharp = createRequire(execSync('npm root -g').toString().trim() + '/anchor.js')('sharp');

const file = process.argv[2];
if (!file) {
  console.error('Usage: node inspect.mjs <image>');
  process.exit(2);
}

let meta, bytes;
try {
  bytes = statSync(file).size;
  meta = await sharp(file).metadata();
} catch (err) {
  console.error(`Error reading ${file}: ${err.message}`);
  process.exit(1);
}

// pages > 1 marks animated/multi-page input (GIF/WebP/TIFF); orientation is the
// EXIF tag that rotate()/autoOrient() act on; exif/icc presence flags whether a
// strip will actually drop anything.
console.log(JSON.stringify({
  format: meta.format,
  width: meta.width,
  height: meta.height,
  space: meta.space,
  channels: meta.channels,
  depth: meta.depth,
  hasAlpha: meta.hasAlpha,
  density: meta.density,
  pages: meta.pages,
  orientation: meta.orientation,
  hasExif: Boolean(meta.exif),
  hasIcc: Boolean(meta.icc),
  fileBytes: bytes,
}, null, 2));
