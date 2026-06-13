import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { readdirSync, mkdirSync } from 'node:fs';
import { join, extname, parse } from 'node:path';

// sharp is a global install (npm i -g sharp). Node ignores NODE_PATH for ESM
// imports, so resolve sharp by basing a require at the global node_modules root;
// `anchor.js` need not exist, it only seeds the resolution base directory.
const sharp = createRequire(execSync('npm root -g').toString().trim() + '/anchor.js')('sharp');

const args = process.argv.slice(2);
const positional = [];
const opts = { format: null, quality: null, width: null, height: null };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--format') opts.format = args[++i];
  else if (a === '--quality') opts.quality = Number(args[++i]);
  else if (a === '--width') opts.width = Number(args[++i]);
  else if (a === '--height') opts.height = Number(args[++i]);
  else positional.push(a);
}

const [inputDir, outputDir] = positional;
if (!inputDir || !outputDir) {
  console.error('Usage: node batch.mjs <input-dir> <output-dir> [--format webp] [--quality 80] [--width N] [--height N]');
  console.error('  Converts/resizes every image in input-dir into output-dir, keeping base names.');
  console.error('  Omit --format to keep each source format; --width/--height never enlarge.');
  process.exit(2);
}

const SUPPORTED = new Set(['.jpg', '.jpeg', '.png', '.webp', '.avif', '.tiff', '.tif', '.gif']);
// sharp's format methods spell it 'jpeg'; the '.jpg' alias is input-only.
const normalizeFormat = (f) => (f === 'jpg' ? 'jpeg' : f);

let files;
try {
  files = readdirSync(inputDir).filter((f) => SUPPORTED.has(extname(f).toLowerCase()));
} catch (err) {
  console.error(`Cannot read input dir ${inputDir}: ${err.message}`);
  process.exit(1);
}
if (files.length === 0) {
  console.error(`No images found in ${inputDir} (looked for: ${[...SUPPORTED].join(', ')})`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });

let ok = 0;
for (const f of files) {
  try {
    let pipeline = sharp(join(inputDir, f));
    if (opts.width || opts.height) {
      pipeline = pipeline.resize({ width: opts.width || null, height: opts.height || null, withoutEnlargement: true });
    }
    const outExt = (opts.format || extname(f).slice(1)).toLowerCase();
    const formatOpts = opts.quality ? { quality: opts.quality } : {};
    pipeline = pipeline.toFormat(normalizeFormat(outExt), formatOpts);
    await pipeline.toFile(join(outputDir, `${parse(f).name}.${outExt}`));
    ok++;
  } catch (err) {
    console.error(`  skip ${f}: ${err.message}`);
  }
}
console.log(`Processed ${ok}/${files.length} image(s) into ${outputDir}`);
