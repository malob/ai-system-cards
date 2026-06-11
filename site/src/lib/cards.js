// Load system cards from the repo's cards/ directory: metadata, stitched
// markdown (with site-specific preprocessing), and per-card asset URLs.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';

const CARDS_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', 'cards');

export function listCards() {
  const cards = [];
  for (const vendor of readdirSync(CARDS_ROOT)) {
    const vendorDir = join(CARDS_ROOT, vendor);
    for (const slug of readdirSync(vendorDir)) {
      const metaPath = join(vendorDir, slug, 'meta.yaml');
      if (!existsSync(metaPath)) continue;
      cards.push({ vendor, slug, meta: YAML.parse(readFileSync(metaPath, 'utf8')) });
    }
  }
  cards.sort((a, b) => String(b.meta.release_date).localeCompare(String(a.meta.release_date)));
  return cards;
}

// Sections dir is env-overridable so v2 pipeline output can be previewed
// without touching the shipped content (e.g. SECTIONS_DIR=sections).
const SECTIONS_DIR = process.env.SECTIONS_DIR || 'sections';

// Raw stitched markdown, exactly as transcribed (page markers and all).
export function stitchedMarkdown(vendor, slug) {
  const dir = join(CARDS_ROOT, vendor, slug, SECTIONS_DIR);
  return readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => readFileSync(join(dir, f), 'utf8').trim())
    .join('\n\n');
}

// Markdown prepared for the HTML pipeline: page markers become PDF deep-link
// anchors, leftover comments are stripped, image paths point at synced public
// assets, and footnote refs inside raw-HTML table cells become real links
// (remark-gfm cannot parse [^N] inside raw HTML).
export function siteMarkdown(vendor, slug, assetBase) {
  let md = stitchedMarkdown(vendor, slug);
  // the page template supplies the title/date, so drop the document's own
  // leading H1 and a standalone date line right after it
  md = md.replace(/^(<!--[\s\S]*?-->\s*)*# .*\n+(?:\*?[A-Z][a-z]+ \d{1,2}, \d{4}\*?\n+)?/, '$1');
  md = md.replace(
    /<!--\s*p\.(\d+)\s*-->/g,
    (_, n) =>
      `<a class="pagemark" id="p-${n}" href="${assetBase}/source.pdf#page=${n}" ` +
      `title="Page ${n} of the source PDF" target="_blank" rel="noopener">p.${n}</a>`,
  );
  md = md.replace(/<!--[\s\S]*?-->/g, '');
  md = md.replace(/\]\(assets\/figures\//g, `](${assetBase}/figures/`);
  // A footnote whose only refs sit inside raw-HTML table cells is invisible
  // to remark-gfm: its def is dropped (body lost, dead fn-html links) and
  // every later footnote renumbers away from the PDF. A hidden shim ref
  // right after the table keeps the def alive, and because the shim sits at
  // the table's document position, the whole list numbers 1:1 with the PDF.
  const lines = md.split('\n');
  const isTableLine = (l) => /<t[dh][ >]/.test(l);
  const proseRefs = new Set();
  const tableRefs = new Map(); // id -> line index of first in-table ref
  lines.forEach((line, i) => {
    for (const m of line.matchAll(/\[\^(\d+)\](?!:)/g)) {
      if (isTableLine(line)) {
        if (!tableRefs.has(m[1])) tableRefs.set(m[1], i);
      } else {
        proseRefs.add(m[1]);
      }
    }
  });
  const shims = new Map(); // line index -> ids needing a shim there
  for (const [id, i] of tableRefs) {
    if (proseRefs.has(id)) continue;
    if (!shims.has(i)) shims.set(i, []);
    shims.get(i).push(id);
  }
  md = lines
    .map((line, i) => {
      if (isTableLine(line))
        line = line.replace(
          /\[\^(\d+)\]/g,
          '<sup class="fn-html"><a href="#user-content-fn-$1">$1</a></sup>',
        );
      const ids = shims.get(i);
      if (!ids) return line;
      const refs = ids.sort((a, b) => a - b).map((n) => `[^${n}]`).join('');
      return `${line}\n\n<span class="fnref-shim">${refs}</span>\n`;
    })
    .join('\n');
  return md;
}

// Self-contained markdown for machine consumption (card.md): absolute asset
// URLs, page markers preserved as comments.
export function portableMarkdown(vendor, slug, absoluteAssetBase) {
  return stitchedMarkdown(vendor, slug)
    .replace(/<!--\s*source: [^>]*-->\n?/g, '')
    .replace(/\]\(assets\/figures\//g, `](${absoluteAssetBase}/figures/`);
}
