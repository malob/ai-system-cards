import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { auditPageHtml } from '../src/lib/article-dom.js';
import { listCardIds } from '../src/lib/card-inventory.js';

const SITE_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const cardIds = listCardIds();
const failures = [];
let ids = 0;
let internalLinks = 0;

if (!cardIds.length) throw new Error('No site-discoverable cards found for built-page link audit');

for (const cardId of cardIds) {
  const htmlPath = join(SITE_ROOT, 'dist', ...cardId.split('/'), 'index.html');
  const { model, findings } = auditPageHtml(readFileSync(htmlPath, 'utf8'));
  ids += model.ids.length;
  internalLinks += model.internalLinks.length;
  if (findings.length) failures.push({ cardId, htmlPath, findings });
}

if (failures.length) {
  console.error(`Built-page link audit failed:\n${JSON.stringify(failures, null, 2)}`);
  process.exitCode = 1;
} else {
  console.log(
    `built-page link audit: ${cardIds.length} cards, ${ids} ids, `
      + `${internalLinks} fragment links, 0 findings`,
  );
}
