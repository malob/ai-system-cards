#!/usr/bin/env node
import { listCardIds } from '../src/lib/card-inventory.js';

const cards = listCardIds(process.env.CARD_INVENTORY_ROOT);
if (cards.length === 0) {
  throw new Error('No site-discoverable cards found; refusing to create an empty gate matrix');
}

process.stdout.write(`${JSON.stringify(cards)}\n`);
