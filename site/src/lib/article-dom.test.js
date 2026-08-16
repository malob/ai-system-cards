import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { auditArticleHtml, auditPageHtml } from './article-dom.js';
import { CARDS_ROOT } from './card-inventory.js';
import { listCards, siteMarkdown } from './cards.js';
import {
  L2_ARTIFACT_NAME,
  auditL2Projection,
  liveL2Digests,
  loadL2Artifact,
} from './l2-artifact.js';
import { renderCard } from './markdown.js';

test('every discovered card has a closed, unique final-DOM fragment graph', async (t) => {
  const totals = {
    cards: 0,
    headings: 0,
    ids: 0,
    internalLinks: 0,
    authoredInternalLinks: 0,
    sourceExpectedLinks: 0,
  };

  for (const { vendor, slug, meta } of listCards()) {
    const assetBase = `/cards/${vendor}/${slug}`;
    const figuresDir = join(CARDS_ROOT, vendor, slug, 'assets', 'figures');
    const { html } = await renderCard(siteMarkdown(vendor, slug, assetBase), {
      figuresDir,
      chips: meta.chips ?? {},
    });
    const { artifact } = loadL2Artifact(vendor, slug);
    const { model, findings } = auditL2Projection(html, artifact);
    assert.deepEqual(findings, [], `${vendor}/${slug}: ${JSON.stringify(findings, null, 2)}`);

    totals.cards += 1;
    totals.headings += model.headings.length;
    totals.ids += model.ids.length;
    totals.internalLinks += model.internalLinks.length;
    totals.authoredInternalLinks += model.authoredInternalLinks.length;
    totals.sourceExpectedLinks += artifact.expected_links.length;
  }

  assert.ok(totals.cards > 0, 'site inventory must not be empty');
  assert.ok(totals.headings > 0, 'corpus must exercise heading IDs');
  assert.ok(totals.internalLinks > 0, 'corpus must exercise internal links');
  t.diagnostic(`audited ${JSON.stringify(totals)}`);
});

test('an existing but wrong destination needs an independent expectation to fail', () => {
  const html = [
    '<h2 id="accepted">Accepted heading</h2>',
    '<h2 id="wrong-but-real">Wrong heading</h2>',
    '<p><a href="#wrong-but-real">Go to the accepted heading</a></p>',
  ].join('');

  assert.deepEqual(
    auditArticleHtml(html).findings,
    [],
    'existence-only DOM integrity cannot identify the semantically correct heading',
  );

  const { findings } = auditArticleHtml(html, {
    expectedTargets: [{
      key: 'synthetic/wrong-existing',
      authoredLinkIndex: 0,
      targetId: 'accepted',
    }],
  });
  assert.deepEqual(findings, [{
    kind: 'unexpected-target',
    key: 'synthetic/wrong-existing',
    linkIndex: 0,
    authoredLinkIndex: 0,
    text: 'Go to the accepted heading',
    href: '#wrong-but-real',
    expectedTargetId: 'accepted',
    actualTargetId: 'wrong-but-real',
  }]);
});

test('authored-link order filters renderer navigation and preserves raw HTML and relocated links', async () => {
  const markdown = [
    '## Accepted',
    '',
    '## Wrong but real',
    '',
    '[Body link](#accepted)',
    '',
    '<table><tbody><tr><td><a href="#accepted"><strong>Raw link</strong></a>',
    '<sup class="fn-html"><a href="#accepted">2</a></sup></td></tr></tbody></table>',
    '',
    'Footnote reference[^1].',
    '',
    '[^1]: [Relocated link](#accepted)',
    '',
    'A [later body link](#accepted) remains in the body.',
  ].join('\n');
  const canonicalLinks = [
    { authoredLinkIndex: 0, text: 'Body link', href: '#accepted', relocatedFootnote: false },
    { authoredLinkIndex: 1, text: 'Raw link', href: '#accepted', relocatedFootnote: false },
    { authoredLinkIndex: 2, text: 'Relocated link', href: '#accepted', relocatedFootnote: true },
    { authoredLinkIndex: 3, text: 'later body link', href: '#accepted', relocatedFootnote: false },
  ];
  const artifact = {
    canonical_links: canonicalLinks,
    expected_links: [{
      key: 'synthetic/body',
      authoredLinkIndex: 0,
      targetId: 'accepted',
    }],
  };

  const { html } = await renderCard(markdown);
  const result = auditL2Projection(html, artifact);
  assert.deepEqual(result.findings, []);
  assert.deepEqual(
    result.model.authoredInternalLinks.map(({ authoredLinkIndex, text, href, relocatedFootnote }) => ({
      authoredLinkIndex,
      text,
      href,
      relocatedFootnote,
    })),
    [
      { authoredLinkIndex: 0, text: 'Body link', href: '#accepted', relocatedFootnote: false },
      { authoredLinkIndex: 1, text: 'Raw link', href: '#accepted', relocatedFootnote: false },
      { authoredLinkIndex: 2, text: 'later body link', href: '#accepted', relocatedFootnote: false },
      { authoredLinkIndex: 3, text: 'Relocated link', href: '#accepted', relocatedFootnote: true },
    ],
  );
  assert.deepEqual(
    new Set(result.model.internalLinks.map(({ rendererGenerated }) => rendererGenerated).filter(Boolean)),
    new Set([
      'heading-self-link',
      'footnote-reference',
      'footnote-backlink',
      'raw-table-footnote-reference',
    ]),
  );

  const { html: wrongHtml } = await renderCard(markdown.replace('[Body link](#accepted)', '[Body link](#wrong-but-real)'));
  assert.deepEqual(auditArticleHtml(wrongHtml).findings, [], 'wrong existing target is still closed');
  assert.deepEqual(
    auditL2Projection(wrongHtml, artifact).findings.map(({ kind }) => kind),
    ['authored-link-href-mismatch', 'source-expected-target-mismatch'],
  );
});

test('artifact loading fails closed when either source or canonical sections drift', () => {
  const cardsRoot = mkdtempSync(join(tmpdir(), 'l2-artifact-'));
  const vendor = 'example';
  const slug = 'fixture';
  const cardDir = join(cardsRoot, vendor, slug);
  const sectionsDir = join(cardDir, 'sections');
  mkdirSync(sectionsDir, { recursive: true });
  try {
    writeFileSync(join(cardDir, 'source.pdf'), 'source-v1');
    writeFileSync(join(sectionsDir, '01.md'), '## Heading\n\n[Link](#heading)\n');
    const digests = liveL2Digests(vendor, slug, cardsRoot);
    const artifact = {
      schema_version: 1,
      card_id: `${vendor}/${slug}`,
      source_sha256: digests.sourceSha256,
      canonical_sections_sha256: digests.canonicalSectionsSha256,
      section_sha256: digests.sectionSha256,
      flags: [],
      canonical_links: [{ authoredLinkIndex: 0, text: 'Link', href: '#heading' }],
      expected_links: [{
        authoredLinkIndex: 0,
        targetId: 'heading',
        actual_href: '#heading',
        expected_href: '#heading',
      }],
    };
    writeFileSync(join(cardDir, L2_ARTIFACT_NAME), JSON.stringify(artifact));
    assert.equal(loadL2Artifact(vendor, slug, cardsRoot).artifact.card_id, `${vendor}/${slug}`);

    writeFileSync(
      join(cardDir, L2_ARTIFACT_NAME),
      JSON.stringify({ ...artifact, expected_links: [] }),
    );
    assert.throws(() => loadL2Artifact(vendor, slug, cardsRoot), /must exactly cover/);
    writeFileSync(join(cardDir, L2_ARTIFACT_NAME), JSON.stringify(artifact));

    writeFileSync(join(cardDir, 'source.pdf'), 'source-v2');
    assert.throws(() => loadL2Artifact(vendor, slug, cardsRoot), /source_sha256/);

    writeFileSync(join(cardDir, 'source.pdf'), 'source-v1');
    writeFileSync(join(sectionsDir, '01.md'), '## Changed\n\n[Link](#changed)\n');
    assert.throws(() => loadL2Artifact(vendor, slug, cardsRoot), /canonical_sections_sha256/);
  } finally {
    rmSync(cardsRoot, { recursive: true, force: true });
  }
});

test('missing, empty, and malformed fragment destinations are rejected', () => {
  const { findings } = auditArticleHtml([
    '<h2 id="present">Present</h2>',
    '<a href="#missing">Missing</a>',
    '<a href="#">Empty</a>',
    '<a href="#bad%zz">Malformed</a>',
  ].join(''));

  assert.deepEqual(findings.map(({ kind }) => kind), [
    'missing-target',
    'empty-target',
    'malformed-target',
  ]);
});

test('duplicate heading IDs fail both uniqueness and exact target resolution', () => {
  const { findings } = auditArticleHtml([
    '<h2 id="duplicate">First</h2>',
    '<h3 id="duplicate">Second</h3>',
    '<a href="#duplicate">Ambiguous</a>',
  ].join(''));

  assert.deepEqual(findings.map(({ kind }) => kind), ['duplicate-id', 'ambiguous-target']);
  assert.deepEqual(findings[0], {
    kind: 'duplicate-id',
    id: 'duplicate',
    count: 2,
    headingCount: 2,
    tags: ['h2', 'h3'],
  });
  assert.equal(findings[1].count, 2);
});

test('a rendered heading without an ID fails closed', () => {
  const { findings } = auditArticleHtml('<h2>Unaddressable</h2>');
  assert.deepEqual(findings.map(({ kind }) => kind), ['heading-without-id']);
});

test('full-page audit catches an article heading colliding with a template ID', () => {
  const { findings } = auditPageHtml([
    '<!doctype html><html><body>',
    '<div id="progress"></div>',
    '<article><h2 id="progress">Progress</h2><a href="#progress">Progress link</a></article>',
    '</body></html>',
  ].join(''));
  assert.deepEqual(findings.map(({ kind }) => kind), ['duplicate-id', 'ambiguous-target']);
});
