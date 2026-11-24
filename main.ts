// news-image-20261124 entry program (Node 22, standard library only).
//
// The picture itself is drawn by draw.py (Python + Pillow, no network, no
// external assets). Its output is a 1024x1024 PNG, carried in this
// repository as entry.b64 — the same bytes, base64-encoded in long lines —
// so the repository stays plain text end to end. All this program does is
// deliver the picture to the grader: it decodes entry.b64 and writes the
// PNG to <output>/entry.png, where <output> is /output in the grading
// container, or $MAKEFUN_OUTPUT_DIR when run locally:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// Base64 decoding is exact, so two runs always write identical bytes.

import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = new URL('./entry.b64', import.meta.url);
const target = join(outputDir, 'entry.png');

const encoded = readFileSync(source, 'utf8').replace(/\s+/g, '');
const picture = Buffer.from(encoded, 'base64');

// The gate accepts only a whole image, so prove the decoded bytes are the
// complete PNG (magic header plus the IEND trailer) before writing.
const pngMagic =
  picture.length > 20 &&
  picture[0] === 0x89 && picture[1] === 0x50 &&
  picture[2] === 0x4e && picture[3] === 0x47;
const pngTrailer = picture.subarray(picture.length - 8).includes('IEND');
if (!pngMagic || !pngTrailer) {
  throw new Error('entry.b64 does not decode to a complete PNG');
}

// The grader hands us a writable /output, but create the directory anyway
// so a local run works without a separate mkdir step.
mkdirSync(outputDir, { recursive: true });
writeFileSync(target, picture);

// Prove the delivered file is the whole picture before exiting.
const delivered = statSync(target).size;
if (delivered !== picture.length) {
  throw new Error(`entry.png write incomplete: ${delivered} of ${picture.length} bytes`);
}
console.log(`entry.png delivered: ${delivered} bytes`);
