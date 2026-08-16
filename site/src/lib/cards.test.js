import assert from 'node:assert/strict';
import test from 'node:test';

import {
  listCards,
  portableBody,
  portableMarkdown,
  portableSectionMarkdown,
  sectionGroups,
} from './cards.js';
import { renderCard } from './markdown.js';

const ASSET_BASE = 'https://example.test/cards/anthropic/fixture';

test('portable table footnotes render definitions, repeated backlinks, and stable later numbering', async () => {
  const source = [
    '<table><tbody>',
    '<tr><td>First<sup>[^7]</sup> and repeated<sup>[^7]</sup></td></tr>',
    '</tbody></table>',
    '',
    'Later prose[^8].',
    '',
    '[^7]: Table-only note.',
    '',
    '[^8]: Later prose note.',
  ].join('\n');

  const portable = portableBody(source, ASSET_BASE);
  assert.doesNotMatch(portable, /<sup>\[\^7\]<\/sup>/);
  assert.match(portable, /<span class="fnref-shim" hidden>\[\^7\]\[\^7\]<\/span>/);

  const { html } = await renderCard(portable);
  const table = html.match(/<table>[\s\S]*?<\/table>/)?.[0] ?? '';
  assert.equal((table.match(/href="#user-content-fn-7"/g) ?? []).length, 2);
  assert.match(table, /id="user-content-fnref-7"[^>]*>1<\/a>/);
  assert.match(table, /id="user-content-fnref-7-2"[^>]*>1<\/a>/);
  assert.match(html, /id="user-content-fnref-8"[^>]*>2<\/a>/);

  const definition = html.match(/<li id="user-content-fn-7">[\s\S]*?<\/li>/)?.[0] ?? '';
  assert.match(definition, /Table-only note\./);
  assert.match(definition, /href="#user-content-fnref-7"/);
  assert.match(definition, /href="#user-content-fnref-7-2"/);
  assert.equal((html.match(/id="user-content-fnref-7"/g) ?? []).length, 1);
  assert.equal((html.match(/id="user-content-fnref-7-2"/g) ?? []).length, 1);
});

test('full-card and standalone-section exports both preserve real table-only footnotes', async () => {
  const vendor = 'anthropic';
  const slug = 'claude-fable-5';
  const assetBase = 'https://example.test/cards/anthropic/claude-fable-5';
  const group = sectionGroups(vendor, slug).find((candidate) =>
    candidate.md.includes('<sup>[^3]</sup>'),
  );
  assert.ok(group, 'fixture section containing table-only footnote 3');

  const full = portableMarkdown(vendor, slug, assetBase);
  const section = portableSectionMarkdown(vendor, slug, group, assetBase);
  for (const [name, markdown] of [['full card', full], ['standalone section', section]]) {
    assert.doesNotMatch(markdown, /<sup>\[\^3\]<\/sup>/, name);
    const { html } = await renderCard(markdown);
    assert.match(html, /<a id="user-content-fnref-3" href="#user-content-fn-3">3<\/a>/, name);
    assert.match(
      html,
      /<li id="user-content-fn-3">[\s\S]*?We re-run this evaluation upon finding a bug/,
      name,
    );
    assert.match(html, /href="#user-content-fnref-3"[^>]*data-footnote-backref/, name);
  }
});

test('every discovered card and section export repairs raw table footnote syntax', () => {
  let repaired = 0;
  for (const { vendor, slug } of listCards()) {
    const assetBase = `https://example.test/cards/${vendor}/${slug}`;
    const full = portableMarkdown(vendor, slug, assetBase);
    repaired += (full.match(/<sup class="fn-html">/g) ?? []).length;
    assert.doesNotMatch(full, /<t[dh][^>]*>[\s\S]*?<sup>\[\^\d+\]<\/sup>/);
    for (const group of sectionGroups(vendor, slug)) {
      const section = portableSectionMarkdown(vendor, slug, group, assetBase);
      assert.doesNotMatch(section, /<t[dh][^>]*>[\s\S]*?<sup>\[\^\d+\]<\/sup>/);
    }
  }
  assert.ok(repaired > 0, 'corpus exercises portable table-footnote repair');
});
