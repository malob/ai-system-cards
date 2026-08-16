import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { auditPageHtml } from '../src/lib/article-dom.js';
import { listCardIds } from '../src/lib/card-inventory.js';
import {
  auditBuiltSourceProjectionAssets,
  auditSourceProjectionPageHtml,
  loadSourceProjectionAuthority,
} from '../src/lib/source-projection.js';

const SITE_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// This is intentionally an independent deployment expectation. If Astro's
// configured base moves, the final-DOM authority audit must be updated with it
// instead of silently accepting whatever URL the renderer happened to emit.
const SITE_BASE = '/ai-system-cards';
const cardIds = listCardIds();
const failures = [];
let ids = 0;
let internalLinks = 0;
let pageMarkers = 0;
let renderedFigures = 0;
let builtFigureAssets = 0;

function twoLevelIds(root, requiredChild) {
  if (!existsSync(root)) return [];
  const ids = [];
  for (const vendor of readdirSync(root, { withFileTypes: true })) {
    if (!vendor.isDirectory()) continue;
    for (const slug of readdirSync(join(root, vendor.name), { withFileTypes: true })) {
      if (!slug.isDirectory()) continue;
      if (requiredChild && !existsSync(join(root, vendor.name, slug.name, requiredChild))) continue;
      ids.push(`${vendor.name}/${slug.name}`);
    }
  }
  return ids.sort();
}

const builtRouteIds = twoLevelIds(join(SITE_ROOT, 'dist'), 'index.html');
const builtAssetIds = twoLevelIds(join(SITE_ROOT, 'dist', 'cards'));
for (const [kind, actual] of [['built-route-set', builtRouteIds], ['built-asset-set', builtAssetIds]]) {
  if (JSON.stringify(actual) !== JSON.stringify(cardIds)) {
    failures.push({ kind, expected: cardIds, actual });
  }
}

if (!cardIds.length) throw new Error('No site-discoverable cards found for built-page link audit');

for (const cardId of cardIds) {
  const htmlPath = join(SITE_ROOT, 'dist', ...cardId.split('/'), 'index.html');
  const html = readFileSync(htmlPath, 'utf8');
  const { model, findings: linkFindings } = auditPageHtml(html);
  const [vendor, slug] = cardId.split('/');
  const authority = loadSourceProjectionAuthority(vendor, slug);
  const projection = auditSourceProjectionPageHtml(html, authority, {
    assetBase: `${SITE_BASE}/cards/${cardId}`,
  });
  const builtAssets = auditBuiltSourceProjectionAssets(authority, {
    sourcePdfPath: join(SITE_ROOT, 'dist', 'cards', vendor, slug, 'source.pdf'),
    figuresDir: join(SITE_ROOT, 'dist', 'cards', vendor, slug, 'figures'),
  });
  ids += model.ids.length;
  internalLinks += model.internalLinks.length;
  pageMarkers += projection.stats.renderedPagemarks ?? 0;
  renderedFigures += projection.stats.renderedFigures ?? 0;
  builtFigureAssets += builtAssets.stats.builtFigureAssets ?? 0;
  if (linkFindings.length || projection.findings.length || builtAssets.findings.length) {
    failures.push({
      cardId,
      htmlPath,
      linkFindings,
      sourceProjectionFindings: projection.findings,
      builtAssetFindings: builtAssets.findings,
    });
  }
}

if (failures.length) {
  console.error(`Built-page link audit failed:\n${JSON.stringify(failures, null, 2)}`);
  process.exitCode = 1;
} else {
  console.log(
    `built-page DOM audit: ${cardIds.length} cards, ${ids} ids, `
      + `${internalLinks} fragment links, ${pageMarkers} source page markers, `
      + `${renderedFigures} rendered source figures, ${builtFigureAssets} exact figure assets, `
      + '0 findings',
  );
}
