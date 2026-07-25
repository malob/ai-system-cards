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
  const pagemark = (n) =>
    `<a class="pagemark" id="p-${n}" href="${assetBase}/source.pdf#page=${n}" ` +
    `title="Page ${n} of the source PDF" aria-label="Page ${n} of the source PDF" ` +
    `data-page="p.${n}" target="_blank" rel="noopener"></a>`;
  // the page template supplies the title/date, so drop the document's own
  // leading H1 and a standalone date line right after it
  md = md.replace(/^(<!--[\s\S]*?-->\s*)*# .*\n+(?:\*?[A-Z][a-z]+ \d{1,2}, \d{4}\*?\n+)?/, '$1');
  // a marker between table rows would be FOSTER-PARENTED out of the table
  // by the HTML parser (an <a> between </tr> and <tr> is invalid), landing
  // every such anchor at the table top — nine of them overlapped into a
  // smear beside the fable appendix interview table (pp.307–316). Anchor it
  // inside the following row's first cell instead: same margin X (its
  // containing block is .doc, so .table-wrap's overflow can't clip it),
  // and its static Y is the row it belongs to.
  md = md.replace(
    /<\/tr><!--\s*p\.(\d+)\s*--><tr>(<t[dh][^>]*>)/g,
    (_, n, cell) => `</tr><tr>${cell}${pagemark(n)}`,
  );
  md = md.replace(/<!--\s*p\.(\d+)\s*-->/g, (_, n) => pagemark(n));
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

// Top-level section groups: consecutive section files form one group until a
// file that OPENS with a level-2 heading starts the next (the pipeline splits
// big sections into 06a/06b… for its own reasons; only the first part carries
// the '## N Title' heading, so deeper-opening files are continuations).
export function sectionGroups(vendor, slug) {
  const dir = join(CARDS_ROOT, vendor, slug, SECTIONS_DIR);
  const groups = [];
  for (const f of readdirSync(dir).filter((n) => n.endsWith('.md')).sort()) {
    const text = readFileSync(join(dir, f), 'utf8').trim();
    const head = text.match(/^#{2,6} .*$/m)?.[0] ?? '';
    const range = text.match(/<!-- source: source\.pdf pages (\d+)-(\d+) -->/);
    if (head.startsWith('## ') || !groups.length) {
      const title = (head || f).replace(/^#+ /, '').trim();
      groups.push({
        title,
        slug: title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''),
        parts: [text],
        pages: range ? [Number(range[1]), Number(range[2])] : null,
      });
    } else {
      const g = groups[groups.length - 1];
      g.parts.push(text);
      if (range && g.pages) g.pages[1] = Number(range[2]);
    }
  }
  return groups.map(({ parts, ...g }) => ({ ...g, md: parts.join('\n\n') }));
}

function portableBody(md, absoluteAssetBase) {
  return md
    .replace(/<!--\s*source: [^>]*-->\n?/g, '')
    .replace(/\]\(assets\/figures\//g, `](${absoluteAssetBase}/figures/`)
    // the document's own leading H1 + date line, when a card carries one —
    // the export header below supplies both
    .replace(/^(\s*(<!--[^>]*-->\s*)*)# .*\n+(?:\*?[A-Z][a-z]+ \d{1,2}, \d{4}\*?\n+)?/, '$1')
    .trim();
}

// Self-describing header so a fetched .md identifies itself (owner-requested:
// exports previously opened on a bare page marker).
function exportHeader(meta, links, note) {
  return [
    `# ${meta.title}`,
    '',
    `**${meta.vendor}** · ${meta.release_date} · ${links.join(' · ')}`,
    '',
    `> ${note} Mechanically converted from the source PDF; page markers are`,
    '> preserved as `<!-- p.N -->` comments. There may be occasional',
    '> transcription artifacts.',
    '',
  ];
}

// Self-contained markdown for machine consumption (card.md): provenance
// header, per-section contents (each entry a fetchable .md — agents can pull
// just the section they need), absolute asset URLs, page markers preserved.
export function portableMarkdown(vendor, slug, absoluteAssetBase, urls = {}) {
  const { meta } = listCards().find((c) => c.vendor === vendor && c.slug === slug);
  const cardUrl = urls.cardUrl ?? '';
  const links = [
    `[Original PDF](${absoluteAssetBase}/source.pdf)`,
    ...(urls.htmlUrl ? [`[Web version](${urls.htmlUrl})`] : []),
  ];
  const toc = sectionGroups(vendor, slug).map(
    (g) =>
      `- [${g.title}](${cardUrl}${g.slug}.md)` +
      (g.pages ? ` — pp. ${g.pages[0]}–${g.pages[1]}` : ''),
  );
  return [
    ...exportHeader(meta, links, 'Complete system card.'),
    '## Contents (each section is a standalone markdown file)',
    '',
    ...toc,
    '',
    '---',
    '',
    portableBody(stitchedMarkdown(vendor, slug), absoluteAssetBase),
    '',
  ].join('\n');
}

// One top-level section as a standalone, self-identifying markdown file.
export function portableSectionMarkdown(vendor, slug, group, absoluteAssetBase, urls = {}) {
  const { meta } = listCards().find((c) => c.vendor === vendor && c.slug === slug);
  const links = [
    ...(urls.cardUrl ? [`[Full card (markdown)](${urls.cardUrl}card.md)`] : []),
    `[Original PDF](${absoluteAssetBase}/source.pdf)`,
    ...(urls.htmlUrl ? [`[Web version](${urls.htmlUrl})`] : []),
  ];
  const note =
    `Section “${group.title}”` +
    (group.pages ? ` (pp. ${group.pages[0]}–${group.pages[1]} of the PDF).` : '.');
  return [
    ...exportHeader(meta, links, note),
    portableBody(group.md, absoluteAssetBase),
    '',
  ].join('\n');
}
