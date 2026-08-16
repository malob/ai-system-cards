#!/usr/bin/env node
// Render one card through the production Markdown pipeline and report only the
// browser-normalized list observation. Expectations deliberately live outside
// this process so the renderer cannot become its own authority.
import { join } from 'node:path';

import { CARDS_ROOT } from '../src/lib/card-inventory.js';
import { listCards, siteMarkdown } from '../src/lib/cards.js';
import { extractListStructure } from '../src/lib/list-structure.js';
import { renderCard } from '../src/lib/markdown.js';

function cardId(value) {
  if (typeof value !== 'string' || !/^[a-z0-9][a-z0-9-]*\/[a-z0-9][a-z0-9-]*$/.test(value)) {
    throw new TypeError('usage: node site/scripts/list-structure-report.mjs vendor/slug');
  }
  return value;
}

const id = cardId(process.argv[2]);
const [vendor, slug] = id.split('/');
const card = listCards().find((candidate) => (
  candidate.vendor === vendor && candidate.slug === slug
));
if (!card) throw new TypeError(`unknown card: ${id}`);

const assetBase = `/ai-system-cards/cards/${id}`;
const figuresDir = join(CARDS_ROOT, vendor, slug, 'assets', 'figures');
const { html } = await renderCard(siteMarkdown(vendor, slug, assetBase), {
  figuresDir,
  chips: card.meta.chips ?? {},
});

process.stdout.write(`${JSON.stringify(extractListStructure(html))}\n`);
