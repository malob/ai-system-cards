// The single repository inventory for cards the site can publish. Keep this
// dependency-free so CI can use the exact same discovery logic before installing
// the site package.
import { existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export const CARDS_ROOT = join(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  '..',
  'cards',
);

export function listCardDirectories(cardsRoot = CARDS_ROOT) {
  const cards = [];
  for (const vendor of readdirSync(cardsRoot)) {
    const vendorDir = join(cardsRoot, vendor);
    for (const slug of readdirSync(vendorDir)) {
      const metaPath = join(vendorDir, slug, 'meta.yaml');
      if (!existsSync(metaPath)) continue;
      cards.push({ vendor, slug, metaPath });
    }
  }
  return cards;
}

export function listCardIds(cardsRoot = CARDS_ROOT) {
  return listCardDirectories(cardsRoot)
    .map(({ vendor, slug }) => `${vendor}/${slug}`)
    .sort();
}
