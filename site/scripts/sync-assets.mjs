// Sync card assets (figures + source PDF) from ../cards into public/ so the
// static build can serve them. Run via the predev/prebuild hooks.
import { cpSync, mkdirSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const cardsRoot = join(here, '..', '..', 'cards');
const publicRoot = join(here, '..', 'public', 'cards');

for (const vendor of readdirSync(cardsRoot)) {
  const vendorDir = join(cardsRoot, vendor);
  for (const slug of readdirSync(vendorDir)) {
    const cardDir = join(vendorDir, slug);
    if (!existsSync(join(cardDir, 'meta.yaml'))) continue;
    const dest = join(publicRoot, vendor, slug);
    mkdirSync(dest, { recursive: true });
    if (existsSync(join(cardDir, 'assets', 'figures'))) {
      cpSync(join(cardDir, 'assets', 'figures'), join(dest, 'figures'), { recursive: true });
    }
    if (existsSync(join(cardDir, 'source.pdf'))) {
      cpSync(join(cardDir, 'source.pdf'), join(dest, 'source.pdf'));
    }
    console.log(`synced ${vendor}/${slug}`);
  }
}
