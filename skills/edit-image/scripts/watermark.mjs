import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

// sharp is a global install (npm i -g sharp). Node ignores NODE_PATH for ESM
// imports, so resolve sharp by basing a require at the global node_modules root;
// `anchor.js` need not exist, it only seeds the resolution base directory.
const sharp = createRequire(execSync('npm root -g').toString().trim() + '/anchor.js')('sharp');

const args = process.argv.slice(2);
const positional = [];
const opts = { gravity: 'southeast', opacity: 1, scale: null };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--gravity') opts.gravity = args[++i];
  else if (a === '--opacity') opts.opacity = Number(args[++i]);
  else if (a === '--scale') opts.scale = Number(args[++i]);
  else positional.push(a);
}

const [base, overlay, output] = positional;
if (!base || !overlay || !output) {
  console.error('Usage: node watermark.mjs <base> <overlay> <output> [--gravity southeast] [--opacity 0.5] [--scale 0.2]');
  console.error('  --gravity  north|south|east|west|center|northeast|northwest|southeast|southwest (default southeast)');
  console.error('  --opacity  0..1, overlay transparency (default 1, fully opaque)');
  console.error('  --scale    overlay width as a fraction of the base width, e.g. 0.2 for 20% (default: no resize)');
  process.exit(2);
}
if (!(opts.opacity >= 0 && opts.opacity <= 1)) {
  console.error(`--opacity must be between 0 and 1, got ${opts.opacity}`);
  process.exit(2);
}

try {
  const baseMeta = await sharp(base).metadata();
  let overlayPipeline = sharp(overlay);

  if (opts.scale) {
    const targetWidth = Math.max(1, Math.round(baseMeta.width * opts.scale));
    overlayPipeline = overlayPipeline.resize({ width: targetWidth });
  }

  // Apply opacity by multiplying the overlay's alpha with a uniform alpha tile:
  // dest-in keeps the overlay's colour but scales its alpha by the tile's alpha.
  if (opts.opacity < 1) {
    overlayPipeline = overlayPipeline.ensureAlpha().composite([{
      input: Buffer.from([255, 255, 255, Math.round(opts.opacity * 255)]),
      raw: { width: 1, height: 1, channels: 4 },
      tile: true,
      blend: 'dest-in',
    }]);
  }

  const overlayBuf = await overlayPipeline.png().toBuffer();
  await sharp(base)
    .composite([{ input: overlayBuf, gravity: opts.gravity }])
    .toFile(output);

  console.log(`Wrote ${output} (overlay ${opts.gravity}, opacity ${opts.opacity}${opts.scale ? `, scale ${opts.scale}` : ''})`);
} catch (err) {
  console.error(`Watermark failed: ${err.message}`);
  process.exit(1);
}
