// Sync card assets (figures + source PDF) from ../cards into public/ so the
// static build can serve them. Run via the predev/prebuild hooks.
import { cpSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { basename, join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { CARDS_ROOT, listCardIds } from '../src/lib/card-inventory.js';

const here = dirname(fileURLToPath(import.meta.url));
const publicRoot = join(here, '..', 'public', 'cards');
const resolvedPublicRoot = resolve(publicRoot);

function resetGeneratedCardsRoot() {
  const expectedParent = resolve(here, '..', 'public');
  if (dirname(resolvedPublicRoot) !== expectedParent || basename(resolvedPublicRoot) !== 'cards') {
    throw new Error(`Refusing to reset unsafe asset root: ${resolvedPublicRoot}`);
  }
  rmSync(resolvedPublicRoot, { recursive: true, force: true });
  mkdirSync(resolvedPublicRoot, { recursive: true });
}

// public/cards is wholly generated output. Reset it once so both stale files
// within a card and removed card/vendor trees self-heal before deployment.
resetGeneratedCardsRoot();

for (const cardId of listCardIds()) {
  const [vendor, slug] = cardId.split('/');
  const cardDir = join(CARDS_ROOT, vendor, slug);
  const dest = join(publicRoot, vendor, slug);
  mkdirSync(dest, { recursive: true });
  if (existsSync(join(cardDir, 'assets', 'figures'))) {
    cpSync(join(cardDir, 'assets', 'figures'), join(dest, 'figures'), { recursive: true });
  }
  if (existsSync(join(cardDir, 'source.pdf'))) {
    cpSync(join(cardDir, 'source.pdf'), join(dest, 'source.pdf'));
  }
  console.log(`synced ${cardId}`);
}
