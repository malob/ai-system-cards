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

// Raw stitched markdown, exactly as transcribed (page markers and all).
export function stitchedMarkdown(vendor, slug) {
  const dir = join(CARDS_ROOT, vendor, slug, 'sections');
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
      `title="Page ${n} of the source PDF" target="_blank" rel="noopener">p. ${n}</a>`,
  );
  md = md.replace(/<!--[\s\S]*?-->/g, '');
  md = md.replace(/\]\(assets\/figures\//g, `](${assetBase}/figures/`);
  md = md
    .split('\n')
    .map((line) =>
      /<t[dh][ >]/.test(line)
        ? line.replace(
            /\[\^(\d+)\]/g,
            '<sup class="fn-html"><a href="#user-content-fn-$1" id="user-content-fnref-$1">$1</a></sup>',
          )
        : line,
    )
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
