// Load system cards from the repo's cards/ directory: metadata, stitched
// markdown (with site-specific preprocessing), and per-card asset URLs.
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import YAML from 'yaml';
import { CARDS_ROOT, listCardDirectories } from './card-inventory.js';
import {
  assertSafeAuthoredMarkdown,
  GENERATED_FNREF_ATTRIBUTE,
  GENERATED_FNREF_VALUE,
} from './markdown.js';

export function listCards() {
  const cards = listCardDirectories().map(({ vendor, slug, metaPath }) => ({
    vendor,
    slug,
    meta: YAML.parse(readFileSync(metaPath, 'utf8')),
  }));
  cards.sort((a, b) => String(b.meta.release_date).localeCompare(String(a.meta.release_date)));
  return cards;
}

// Sections dir is env-overridable so v2 pipeline output can be previewed
// without touching the shipped content (e.g. SECTIONS_DIR=sections).
const SECTIONS_DIR = process.env.SECTIONS_DIR || 'sections';
const SOURCE_FIGURE_SKIP_COMMENT = /^<!--\s*figure\s+p\d{3,}-[1-9]\d*\.png\s+skipped\s*:\s*\S[\s\S]*?\s*-->$/i;

// Raw stitched markdown, exactly as transcribed (page markers and all).
export function stitchedMarkdown(vendor, slug) {
  const dir = join(CARDS_ROOT, vendor, slug, SECTIONS_DIR);
  return readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => readFileSync(join(dir, f), 'utf8').trim())
    .join('\n\n');
}

// GFM does not parse footnote references inside a raw-HTML table. Bridge those
// references to real HTML links and place parseable shim references immediately
// after the table so the definitions survive Markdown rendering.
//
// The site mode preserves the shipped HTML behavior: only a table-only
// footnote's first ref owns the backlink target, and one shim keeps its
// definition alive. Portable exports need a little more: every table occurrence
// gets a hidden shim, so repeated refs receive distinct backlinks and the
// renderer numbers later prose footnotes as if it had parsed the table refs at
// their document positions.
function linkRawTableFootnotes(md, { portable = false } = {}) {
  const lines = md.split('\n');
  const isTableLine = (line) => /<t[dh][ >]/.test(line);
  const proseRefs = new Set();
  const tableRefs = [];
  const refsByLine = new Map();
  const refCounts = new Map();
  const displayNumbers = new Map();

  for (let i = 0; i < lines.length; i += 1) {
    const tableLine = isTableLine(lines[i]);
    for (const match of lines[i].matchAll(/\[\^(\d+)\](?!:)/g)) {
      const id = match[1];
      if (!displayNumbers.has(id)) displayNumbers.set(id, displayNumbers.size + 1);
      const refIndex = (refCounts.get(id) ?? 0) + 1;
      refCounts.set(id, refIndex);
      if (tableLine) {
        const ref = { id, line: i, refIndex };
        tableRefs.push(ref);
        if (!refsByLine.has(i)) refsByLine.set(i, []);
        refsByLine.get(i).push(ref);
      } else {
        proseRefs.add(id);
      }
    }
  }

  const tableEnd = (start) => {
    let at = start;
    while (at < lines.length - 1 && !lines[at].includes('</table>')) at += 1;
    return at;
  };
  const shims = new Map(); // closing-table line -> ids to parse after it
  const firstTableRef = new Map();
  for (const ref of tableRefs) {
    if (!firstTableRef.has(ref.id)) firstTableRef.set(ref.id, ref);
    if (!portable && (proseRefs.has(ref.id) || firstTableRef.get(ref.id) !== ref)) continue;
    const at = tableEnd(ref.line);
    if (!shims.has(at)) shims.set(at, []);
    shims.get(at).push(ref.id);
  }

  const claimedIds = new Set();
  return lines
    .map((sourceLine, i) => {
      let line = sourceLine;
      if (isTableLine(line)) {
        const refs = refsByLine.get(i) ?? [];
        let cursor = 0;
        // Consume an enclosing literal <sup> pair so the replacement does not
        // nest one superscript inside another.
        line = line.replace(
          /(?:<sup>)?\[\^(\d+)\](?:<\/sup>)?/g,
          (_, id) => {
            const ref = refs[cursor++];
            if (portable) {
              const suffix = ref.refIndex === 1 ? '' : `-${ref.refIndex}`;
              const label = displayNumbers.get(id);
              return (
                `<sup class="fn-html"><a id="user-content-fnref-${id}${suffix}" ` +
                `href="#user-content-fn-${id}">${label}</a></sup>`
              );
            }
            const first = firstTableRef.get(id)?.line === i && !proseRefs.has(id)
              && !claimedIds.has(id);
            if (first) claimedIds.add(id);
            const anchorId = first ? ` id="user-content-fnref-${id}"` : '';
            return (
              `<sup class="fn-html"><a${anchorId} ` +
              `href="#user-content-fn-${id}">${id}</a></sup>`
            );
          },
        );
      }
      const ids = shims.get(i);
      if (!ids) return line;
      const orderedIds = portable ? ids : [...ids].sort((a, b) => a - b);
      const refs = orderedIds.map((id) => `[^${id}]`).join('');
      const generated = portable
        ? ' hidden'
        : ` ${GENERATED_FNREF_ATTRIBUTE}="${GENERATED_FNREF_VALUE}"`;
      return `${line}\n\n<span class="fnref-shim"${generated}>${refs}</span>\n`;
    })
    .join('\n');
}

// Markdown prepared for the HTML pipeline: page markers become PDF deep-link
// anchors, leftover comments are stripped, image paths point at synced public
// assets, and footnote refs inside raw-HTML table cells become real links
// (remark-gfm cannot parse [^N] inside raw HTML).
export function siteMarkdownFromText(rawMarkdown, assetBase, options = {}) {
  if (typeof rawMarkdown !== 'string') throw new TypeError('rawMarkdown must be a string');
  if (typeof assetBase !== 'string' || !assetBase) throw new TypeError('assetBase must be a string');
  if (options.allowUnsafeAuthoredHtmlForAudit !== true) assertSafeAuthoredMarkdown(rawMarkdown);
  let md = rawMarkdown;
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
  // Preserve exact, standalone source-figure skip evidence for the HAST
  // renderer. All other authored comments disappear from the web projection.
  // A lookalike inside a fenced/code block remains code in the Markdown AST
  // and therefore cannot become a skip sentinel.
  md = md.replace(
    /<!--[\s\S]*?-->/g,
    (comment) => (SOURCE_FIGURE_SKIP_COMMENT.test(comment) ? comment : ''),
  );
  md = md.replace(/\]\(assets\/figures\//g, `](${assetBase}/figures/`);
  return linkRawTableFootnotes(md, options);
}

export function siteMarkdown(vendor, slug, assetBase) {
  return siteMarkdownFromText(stitchedMarkdown(vendor, slug), assetBase);
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

export function portableBody(md, absoluteAssetBase) {
  const body = md
    .replace(/<!--\s*source: [^>]*-->\n?/g, '')
    .replace(/\]\(assets\/figures\//g, `](${absoluteAssetBase}/figures/`)
    // the document's own leading H1 + date line, when a card carries one —
    // the export header below supplies both
    .replace(/^(\s*(<!--[^>]*-->\s*)*)# .*\n+(?:\*?[A-Z][a-z]+ \d{1,2}, \d{4}\*?\n+)?/, '$1')
    .trim();
  return linkRawTableFootnotes(body, { portable: true });
}

// word-wrap for raw-md readability (blockquote soft-wraps don't affect
// rendering; ragged template wrapping did affect reading the file raw)
function wrapQuote(text, width = 78) {
  const out = [];
  let line = '>';
  for (const w of text.split(/\s+/)) {
    if (line.length + w.length + 1 > width && line !== '>') {
      out.push(line);
      line = '>';
    }
    line += ` ${w}`;
  }
  if (line !== '>') out.push(line);
  return out;
}

// Self-describing header so a fetched .md identifies itself (owner-requested:
// exports previously opened on a bare page marker).
function exportHeader(meta, links, note) {
  return [
    `# ${meta.title}`,
    '',
    `**${meta.vendor}** · ${meta.release_date} · ${links.join(' · ')}`,
    '',
    ...wrapQuote(
      `${note} Mechanically converted from the archived PDF (the exact` +
      ' revision transcribed — vendors sometimes revise in place); page' +
      ' markers are preserved as `<!-- p.N -->` comments. There may be' +
      ' occasional transcription artifacts.',
    ),
    '',
  ];
}

// Self-contained markdown for machine consumption (card.md): provenance
// header, per-section contents (each entry a fetchable .md — agents can pull
// just the section they need), absolute asset URLs, page markers preserved.
export function portableMarkdown(vendor, slug, absoluteAssetBase, urls = {}) {
  const { meta } = listCards().find((c) => c.vendor === vendor && c.slug === slug);
  const cardUrl = urls.cardUrl ?? '';
  // Original = the vendor's authoritative URL (matches the HTML masthead);
  // Archived = the exact bytes this conversion is faithful to (vendors
  // revise PDFs in place — fable's June 11 revision, D37)
  const links = [
    ...(meta.source_url ? [`[Original PDF](${meta.source_url})`] : []),
    `[Archived PDF](${absoluteAssetBase}/source.pdf)`,
    ...(urls.htmlUrl ? [`[Web version](${urls.htmlUrl})`] : []),
  ];
  const toc = sectionGroups(vendor, slug).map(
    (g) =>
      `- [${g.title}](${cardUrl}${g.slug}.md)` +
      (g.pages ? ` — pp. ${g.pages[0]}–${g.pages[1]}` : ''),
  );
  return [
    ...exportHeader(meta, links, `Complete ${(meta.doc_type ?? 'system card').toLowerCase()}.`),
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
    ...(meta.source_url ? [`[Original PDF](${meta.source_url})`] : []),
    `[Archived PDF](${absoluteAssetBase}/source.pdf)`,
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
