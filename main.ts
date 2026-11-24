// The World Today — 24 November 2026 · make.fun news-image-20261124
//
// How this entry works: the front page itself is drawn by draw.py and
// stored in this folder as entry.b64 (base64 text, wrapped so the
// repository stays plain text). This program is the delivery step —
// it unfolds that text back into the exact PNG bytes, sanity-checks
// them, and drops the picture where the grader expects it:
//
//   MAKEFUN_OUTPUT_DIR=<dir> node main.ts      (local runs)
//   node main.ts                               (grader: /output)
//
// Node 22, standard library only, no network. Running it twice
// always produces byte-identical output.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));

// --- unfold the picture -------------------------------------------------

const encoded = readFileSync(join(here, 'entry.b64'), 'utf8');
const png = Buffer.from(encoded.replace(/\s+/g, ''), 'base64');

if (png.length === 0) {
  throw new Error('entry.b64 decoded to nothing');
}

// --- sanity-check the bytes before handing them over --------------------

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
for (let i = 0; i < PNG_SIGNATURE.length; i += 1) {
  if (png[i] !== PNG_SIGNATURE[i]) {
    throw new Error(`not a PNG: signature byte ${i} is wrong`);
  }
}

// A well-formed PNG ends with the twelve-byte IEND chunk:
// length 0, the letters IEND, then its CRC.
const tail = png.subarray(png.length - 12);
const iendOk =
  tail.readUInt32BE(0) === 0 && tail.toString('ascii', 4, 8) === 'IEND';
if (!iendOk) {
  throw new Error('truncated PNG: IEND trailer missing');
}

// --- deliver --------------------------------------------------------------

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const target = join(outDir, 'entry.png');
writeFileSync(target, png);
console.log(`entry.png written to ${target} (${png.length} bytes)`);
