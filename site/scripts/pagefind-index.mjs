// Build the Pagefind index with one record PER SECTION (heading → next heading)
// instead of letting the CLI crawl whole pages. A card is a single huge HTML
// page, so the CLI yields exactly one result whose sub-results are listed in
// document order of any-word matches — multi-word queries surface whichever
// early sections contain the commonest word ("of"), never the section that
// actually contains the phrase. Per-section records restore real ranking:
// word-AND and scoring apply within each section, and each result deep-links
// to its heading anchor.
import { readFile, readdir, access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import * as pagefind from 'pagefind';

const DIST = fileURLToPath(new URL('../dist/', import.meta.url));
// record urls are SITE-RELATIVE (no astro base): pagefind.js detects the base
// from where the bundle is served and prepends it at runtime, like the CLI flow

const decode = (s) =>
  s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
const text = (html) => decode(html.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();

// card pages live at dist/<vendor>/<slug>/index.html (home/404/og/assets don't match)
async function cardPages() {
  const pages = [];
  for (const vendor of await readdir(DIST, { withFileTypes: true })) {
    if (!vendor.isDirectory()) continue;
    const vdir = join(DIST, vendor.name);
    for (const slug of await readdir(vdir, { withFileTypes: true })) {
      if (!slug.isDirectory()) continue;
      const file = join(vdir, slug.name, 'index.html');
      try {
        await access(file);
        pages.push({ file, url: `/${vendor.name}/${slug.name}/` });
      } catch {
        /* not a page dir (asset folders etc.) */
      }
    }
  }
  return pages;
}

const { index } = await pagefind.createIndex();
let records = 0;
for (const { file, url } of await cardPages()) {
  const html = await readFile(file, 'utf8');
  const article = html.match(/<article class="article"[^>]*>([\s\S]*?)<\/article>/)?.[1];
  if (!article) continue;
  const pageTitle = text(html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)?.[1] ?? url);
  for (const part of article.split(/(?=<h[2-6][^>]*\bid=")/)) {
    const h = part.match(/^<h([2-6])[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)<\/h\1>/);
    const title = h ? text(h[3]) : pageTitle;
    const body = text(h ? part.slice(h[0].length) : part);
    if (!title && !body) continue;
    await index.addCustomRecord({
      url: h ? `${url}#${h[2]}` : url,
      // heading words are part of the searchable text, not only display meta
      content: body ? `${title}. ${body}` : title,
      language: 'en',
      meta: { title: title || pageTitle },
    });
    records += 1;
  }
}
const out = join(DIST, 'pagefind');
await index.writeFiles({ outputPath: out });
await pagefind.close();
console.log(`pagefind: ${records} section records → ${out}`);
