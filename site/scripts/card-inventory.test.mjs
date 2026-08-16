import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), 'card-matrix.mjs');

function addCard(root, id) {
  const cardDir = join(root, ...id.split('/'));
  mkdirSync(cardDir, { recursive: true });
  writeFileSync(join(cardDir, 'meta.yaml'), 'title: Test card\n');
}

function emittedCards(root) {
  return JSON.parse(execFileSync(process.execPath, [SCRIPT], {
    encoding: 'utf8',
    env: { ...process.env, CARD_INVENTORY_ROOT: root },
  }));
}

test('CI matrix exactly follows the site card inventory', () => {
  const root = mkdtempSync(join(tmpdir(), 'card-inventory-'));
  try {
    const original = [
      'anthropic/claude-fable-5',
      'anthropic/claude-opus-5',
      'anthropic/risk-report-2026-08',
    ];
    for (const id of original) addCard(root, id);

    assert.deepEqual(emittedCards(root), original);

    addCard(root, 'example/synthetic-fourth-card');
    mkdirSync(join(root, 'example', 'not-a-card'), { recursive: true });

    const discovered = emittedCards(root);
    assert.deepEqual(discovered, [...original, 'example/synthetic-fourth-card'].sort());
    assert.ok(!discovered.includes('example/not-a-card'));
    assert.ok(!discovered.includes('example/nonexistent-card'));
    for (const id of discovered) {
      assert.ok(existsSync(join(root, ...id.split('/'), 'meta.yaml')));
    }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CI matrix refuses an empty publishable inventory', () => {
  const root = mkdtempSync(join(tmpdir(), 'card-inventory-empty-'));
  try {
    const result = spawnSync(process.execPath, [SCRIPT], {
      encoding: 'utf8',
      env: { ...process.env, CARD_INVENTORY_ROOT: root },
    });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /No site-discoverable cards found/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
