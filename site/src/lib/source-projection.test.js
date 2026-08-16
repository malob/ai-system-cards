import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { siteMarkdownFromText } from './cards.js';
import { liveL2Digests } from './l2-artifact.js';
import { renderCard } from './markdown.js';
import {
  auditBuiltSourceProjectionAssets,
  auditSourceProjectionPageHtml,
  auditSourceProjectionSections,
  loadSourceProjectionAuthority,
} from './source-projection.js';

const CARD_ID = 'example/fixture';
const ASSET_BASE = `/ai-system-cards/cards/${CARD_ID}`;
const SOURCE_BYTES = Buffer.from('synthetic source identity');
const COVER_REASON = 'reviewed cover';
const DUPLICATE_REASON = 'reviewed duplicate';
const SKIP_REASON = 'reviewed non-visual raster';

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function pageObservation(page, rasterCount) {
  return {
    drawing_count: 0,
    internal_links: 0,
    page,
    raster_count: rasterCount,
    text_chars: 1,
    uri_links: 0,
    word_count: 1,
  };
}

function projectionAsset(cardDir, filename, disposition, duplicateOf = null, reason = null) {
  const match = /^p(\d+)-(\d+)\.png$/.exec(filename);
  const pdfPage = Number(match[1]);
  const drawIndex = Number(match[2]);
  const bytes = Buffer.alloc(24);
  bytes.write(`synthetic:${drawIndex}`);
  bytes.writeUInt32BE(100, 16);
  bytes.writeUInt32BE(50, 20);
  writeFileSync(join(cardDir, 'assets', 'figures', filename), bytes);
  return {
    disposition,
    duplicate_of: duplicateOf,
    file_sha256: sha256(bytes),
    filename,
    has_alpha: false,
    height: 50,
    logical_path: `figures/${filename}`,
    reason_sha256: reason === null ? null : sha256(reason),
    source: {
      asset_sample_md5: '2'.repeat(32),
      bbox: [0, 0, 100, 50],
      draw_index: drawIndex,
      has_soft_mask: false,
      pdf_page: pdfPage,
      raw_sample_md5: '1'.repeat(32),
      xref: drawIndex,
    },
    width: 100,
  };
}

function writeProjectionFixture(root, { zeroFigures = false } = {}) {
  const cardDir = join(root, 'example', 'fixture');
  mkdirSync(join(cardDir, 'extracted'), { recursive: true });
  mkdirSync(join(cardDir, 'sections'), { recursive: true });
  writeFileSync(join(cardDir, 'meta.yaml'), `source_pages: ${zeroFigures ? 1 : 3}\n`);
  writeFileSync(join(cardDir, 'source.pdf'), SOURCE_BYTES);
  writeFileSync(join(cardDir, 'sections', '00.md'), 'Synthetic section\n');
  const inventoryBytes = Buffer.from('{}\n');
  const figureMapBytes = Buffer.from('{}\n');
  writeFileSync(join(cardDir, 'source-inventory.json'), inventoryBytes);
  writeFileSync(join(cardDir, 'extracted', 'figures-map.json'), figureMapBytes);

  let pages;
  let assets;
  if (zeroFigures) {
    pages = [{
      disposition: 'content',
      pdf_page: 1,
      reason_sha256: null,
      source_observation: pageObservation(1, 0),
    }];
    assets = [];
  } else {
    mkdirSync(join(cardDir, 'assets', 'figures'), { recursive: true });
    pages = [{
      disposition: 'cover',
      pdf_page: 1,
      reason_sha256: sha256(COVER_REASON),
      source_observation: pageObservation(1, 1),
    }, {
      disposition: 'content',
      pdf_page: 2,
      reason_sha256: null,
      source_observation: pageObservation(2, 1),
    }, {
      disposition: 'content',
      pdf_page: 3,
      reason_sha256: null,
      source_observation: pageObservation(3, 4),
    }];
    assets = [
      projectionAsset(cardDir, 'p001-1.png', 'excluded-cover', null, COVER_REASON),
      projectionAsset(cardDir, 'p002-1.png', 'required-output'),
      projectionAsset(cardDir, 'p003-1.png', 'required-output'),
      projectionAsset(cardDir, 'p003-2.png', 'required-output'),
      projectionAsset(cardDir, 'p003-3.png', 'duplicate-draw', 'p003-2.png', DUPLICATE_REASON),
      projectionAsset(cardDir, 'p003-4.png', 'accepted-skip', null, SKIP_REASON),
    ];
  }

  const events = [];
  for (const page of pages) {
    if (page.disposition !== 'content') continue;
    events.push({ anchor: `p-${page.pdf_page}`, kind: 'page', pdf_page: page.pdf_page });
    for (const asset of assets.filter(({ source }) => source.pdf_page === page.pdf_page)) {
      if (asset.disposition === 'required-output') {
        events.push({
          asset_sha256: asset.file_sha256,
          draw_index: asset.source.draw_index,
          filename: asset.filename,
          kind: 'figure',
          logical_src: asset.logical_path,
          pdf_page: page.pdf_page,
        });
      } else if (asset.disposition === 'accepted-skip') {
        events.push({
          draw_index: asset.source.draw_index,
          filename: asset.filename,
          kind: 'accepted-skip',
          pdf_page: page.pdf_page,
          reason_sha256: asset.reason_sha256,
        });
      }
    }
  }
  const canonicalSectionsSha256 = liveL2Digests('example', 'fixture', root)
    .canonicalSectionsSha256;
  const artifact = {
    assets,
    card_id: CARD_ID,
    events,
    inputs: {
      canonical_sections: {
        digest_method: 'l2.sections_sha256.v1',
        sha256: canonicalSectionsSha256,
      },
      figures_map: { file: 'extracted/figures-map.json', sha256: sha256(figureMapBytes) },
      inventory: { file: 'source-inventory.json', sha256: sha256(inventoryBytes) },
    },
    observer_schema_version: 2,
    pages,
    pymupdf_version: '1.28.2',
    schema_version: 1,
    source: { file: 'source.pdf', page_count: pages.length, sha256: sha256(SOURCE_BYTES) },
    source_flags: [],
  };
  writeFileSync(join(cardDir, 'source-projection.json'), JSON.stringify(artifact));
  return { artifact, cardDir };
}

function withFixture(callback, options) {
  const root = mkdtempSync(join(tmpdir(), 'source-projection-card-'));
  try {
    const fixture = writeProjectionFixture(root, options);
    return callback({ root, ...fixture });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

async function withAsyncFixture(callback, options) {
  const root = mkdtempSync(join(tmpdir(), 'source-projection-card-'));
  try {
    const fixture = writeProjectionFixture(root, options);
    return await callback({ root, ...fixture });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function authority() {
  return withFixture(({ root }) => loadSourceProjectionAuthority('example', 'fixture', root));
}

function updateArtifact(cardDir, mutate) {
  const path = join(cardDir, 'source-projection.json');
  const artifact = JSON.parse(readFileSync(path, 'utf8'));
  mutate(artifact);
  writeFileSync(path, JSON.stringify(artifact));
}

function pagemark(page, extra = '') {
  return [
    `<a class="pagemark" id="p-${page}"`,
    ` href="${ASSET_BASE}/source.pdf#page=${page}"`,
    ` title="Page ${page} of the source PDF"`,
    ` aria-label="Page ${page} of the source PDF"`,
    ` data-page="p.${page}" target="_blank" rel="noopener"${extra}></a>`,
  ].join('');
}

function figure(name, extra = '') {
  const src = `${ASSET_BASE}/figures/${name}`;
  return [
    `<figure${extra}><div class="figure-card">`,
    `<a href="${src}" class="figure-zoom">`,
    `<img src="${src}" alt="" loading="lazy" decoding="async" width="100" height="50">`,
    '</a></div></figure>',
  ].join('');
}

function skipSentinel(name, reason = SKIP_REASON) {
  const page = Number(/^p(\d+)-/.exec(name)[1]);
  return (
    `<span hidden class="source-figure-skip" data-figure="${name}" data-page="p.${page}" `
    + `data-reason-sha256="${sha256(reason)}"></span>`
  );
}

function page(body) {
  return `<!doctype html><html><body><article class="article">${body}</article></body></html>`;
}

function cleanHtml() {
  return page([
    pagemark(2),
    figure('p002-1.png'),
    pagemark(3),
    figure('p003-1.png'),
    figure('p003-2.png'),
    skipSentinel('p003-4.png'),
  ].join(''));
}

test('strict projection artifact supplies every required DOM event in source order', () => {
  const result = authority();
  assert.deepEqual(result.requiredPages, [2, 3]);
  assert.deepEqual(
    result.requiredFigures.map(({ filename }) => filename),
    ['p002-1.png', 'p003-1.png', 'p003-2.png'],
  );
  assert.deepEqual(auditSourceProjectionPageHtml(cleanHtml(), result, { assetBase: ASSET_BASE }), {
    findings: [],
    stats: {
      requiredPages: 2,
      renderedPagemarks: 2,
      requiredFigures: 3,
      renderedFigures: 3,
      acceptedFigureSkips: 1,
    },
  });
});

test('projection artifact loader fails closed on stale and malformed facts', async (t) => {
  await t.test('stale source digest', () => withFixture(({ root, cardDir }) => {
    updateArtifact(cardDir, (artifact) => { artifact.source.sha256 = '0'.repeat(64); });
    assert.throws(() => loadSourceProjectionAuthority('example', 'fixture', root), /source\.sha256 is stale/);
  }));
  await t.test('JSON-valid malformed page disposition', () => withFixture(({ root, cardDir }) => {
    updateArtifact(cardDir, (artifact) => { artifact.pages[0].disposition = []; });
    assert.throws(() => loadSourceProjectionAuthority('example', 'fixture', root), /disposition is unknown/);
  }));
  await t.test('asset occurrence gap', () => withFixture(({ root, cardDir }) => {
    updateArtifact(cardDir, (artifact) => { artifact.assets[2].source.draw_index = 9; });
    assert.throws(() => loadSourceProjectionAuthority('example', 'fixture', root), /page\/draw order/);
  }));
  await t.test('duplicate target must be prior and on-page', () => withFixture(({ root, cardDir }) => {
    updateArtifact(cardDir, (artifact) => { artifact.assets[4].duplicate_of = 'p003-4.png'; });
    assert.throws(() => loadSourceProjectionAuthority('example', 'fixture', root), /prior same-page/);
  }));
  await t.test('hashed inventory input drift', () => withFixture(({ root, cardDir }) => {
    writeFileSync(join(cardDir, 'source-inventory.json'), '{"changed":true}\n');
    assert.throws(() => loadSourceProjectionAuthority('example', 'fixture', root), /inventory\.sha256 is stale/);
  }));
});

test('only canonical final DOM nodes satisfy page and figure expectations', () => {
  const fakeMarker = pagemark(2);
  const fakeFigureSrc = `${ASSET_BASE}/figures/p002-1.png`;
  const html = page([
    `<!-- ${fakeMarker} -->`,
    `<div title='${fakeMarker.replaceAll("'", '&#39;')}'></div>`,
    `<a title='${fakeMarker.replaceAll("'", '&#39;')}'>link title</a>`,
    '<p>:pagemark[Page 2]{#p-2}</p>',
    `<p>&lt;a class="pagemark" id="p-2" href="${ASSET_BASE}/source.pdf#page=2"&gt;</p>`,
    `<p>< a class="pagemark" id="p-2">space-angle text</p>`,
    `<A CLASS="PAGEMARK" ID="P-2" HREF="${ASSET_BASE}/SOURCE.PDF#PAGE=2"></A>`,
    `<img src="${fakeFigureSrc}" loading="lazy" decoding="async" width="100" height="50">`,
    `<div data-image='<img src="${fakeFigureSrc}">'></div>`,
    `<p>&lt;img src="${fakeFigureSrc}"&gt;</p>`,
    `<IMG SRC="${ASSET_BASE}/FIGURES/P002-1.PNG">`,
    pagemark(3),
    figure('p003-1.png'),
    figure('p003-2.png'),
    skipSentinel('p003-4.png'),
  ].join(''));

  const result = auditSourceProjectionPageHtml(html, authority(), { assetBase: ASSET_BASE });
  assert.equal(result.stats.renderedPagemarks, 1);
  assert.equal(result.stats.renderedFigures, 2);
  assert.ok(result.findings.some(({ kind, page: n }) => kind === 'missing-page-marker' && n === 2));
  assert.ok(result.findings.some(
    ({ kind, filename }) => kind === 'missing-rendered-figure' && filename === 'p002-1.png',
  ));
  assert.ok(result.findings.some(({ kind }) => kind === 'noncanonical-pagemark'));
  assert.ok(result.findings.some(({ kind }) => kind === 'noncanonical-rendered-figure'));
});

test('SVG namespace, hidden ancestors, responsive overrides, and path variants never satisfy', () => {
  const svgMarker = `<svg>${pagemark(2)}</svg>`;
  const svgHtml = cleanHtml().replace(pagemark(2), svgMarker);
  const svgKinds = auditSourceProjectionPageHtml(svgHtml, authority(), { assetBase: ASSET_BASE })
    .findings.map(({ kind }) => kind);
  assert.ok(svgKinds.includes('noncanonical-pagemark'));
  assert.ok(svgKinds.includes('missing-page-marker'));

  const hiddenHtml = cleanHtml().replace(
    `${pagemark(2)}${figure('p002-1.png')}`,
    `<div style="DISPLAY : none !important">${pagemark(2)}${figure('p002-1.png')}</div>`,
  );
  const hiddenKinds = auditSourceProjectionPageHtml(hiddenHtml, authority(), { assetBase: ASSET_BASE })
    .findings.map(({ kind }) => kind);
  assert.ok(hiddenKinds.includes('noncanonical-pagemark'));
  assert.ok(hiddenKinds.includes('noncanonical-rendered-figure'));

  for (const [opening, closing] of [
    ['<main hidden>', '</main>'],
    ['<main style="display:none!important">', '</main>'],
    ['<main style="display:none!important;display:block">', '</main>'],
    ['<main style="visibility:hidden!important;visibility:visible">', '</main>'],
    ['<main style="content-visibility:hidden!important;content-visibility:visible">', '</main>'],
    ['<dialog>', '</dialog>'],
  ]) {
    const wrapped = cleanHtml().replace(
      '<article class="article">',
      `${opening}<article class="article">`,
    ).replace('</article></body>', `</article>${closing}</body>`);
    const wrapperKinds = auditSourceProjectionPageHtml(
      wrapped,
      authority(),
      { assetBase: ASSET_BASE },
    ).findings.map(({ kind }) => kind);
    assert.ok(wrapperKinds.includes('noncanonical-pagemark'));
    assert.ok(wrapperKinds.includes('noncanonical-rendered-figure'));
  }

  const src = `${ASSET_BASE}/figures/p002-1.png`;
  for (const mutation of [
    (html) => html.replace(`src="${src}"`, `src="${src}?v=1"`),
    (html) => html.replace(`src="${src}"`, `src="${ASSET_BASE}/figures/./p002-1.png"`),
    (html) => html.replace(`src="${src}"`, `src="${src}" srcset="${src} 1x"`),
    (html) => html.replace('alt=""', 'alt="not the source raster"'),
    (html) => html.replace('width="100"', 'width="1"'),
    (html) => html.replace('height="50"', 'height="999"'),
    (html) => html.replace(`<img src="${src}"`, `<picture><img src="${src}"`).replace('</a>', '</picture></a>'),
  ]) {
    const findings = auditSourceProjectionPageHtml(mutation(cleanHtml()), authority(), { assetBase: ASSET_BASE }).findings;
    assert.ok(findings.some(({ kind }) => kind === 'noncanonical-rendered-figure'));
    assert.ok(findings.some(({ kind }) => kind === 'missing-rendered-figure'));
  }
});

test('CSS-hidden, UA-hidden, and marker-shaped impostors never satisfy', () => {
  for (const wrapper of [
    '<div class="fnref-shim">BODY</div>',
    '<span class="sidenote">BODY</span>',
    '<div popover>BODY</div>',
    '<datalist>BODY</datalist>',
  ]) {
    const hidden = cleanHtml().replace(
      `${pagemark(2)}${figure('p002-1.png')}`,
      wrapper.replace('BODY', `${pagemark(2)}${figure('p002-1.png')}`),
    );
    const kinds = auditSourceProjectionPageHtml(hidden, authority(), { assetBase: ASSET_BASE })
      .findings.map(({ kind }) => kind);
    assert.ok(kinds.includes('noncanonical-pagemark'));
    assert.ok(kinds.includes('noncanonical-rendered-figure'));
  }

  const impostor = cleanHtml().replace(
    pagemark(2),
    '<span class="pagemark" id="p-2" data-page="p.2"></span>',
  );
  const impostorKinds = auditSourceProjectionPageHtml(
    impostor,
    authority(),
    { assetBase: ASSET_BASE },
  ).findings.map(({ kind }) => kind);
  assert.ok(impostorKinds.includes('noncanonical-pagemark'));
  assert.ok(impostorKinds.includes('missing-page-marker'));
});

test('active and alternate visual article content fails closed', () => {
  for (const active of [
    '<script>document.querySelector(".pagemark").remove()</script>',
    '<style>.pagemark{display:none}</style>',
    '<template shadowrootmode="open"><p>shadow</p></template>',
    '<video poster="/wrong.png"></video>',
    '<input type="image" src="/wrong.png">',
    '<noscript><img src="/wrong.png"></noscript>',
    '<table background="/wrong.png"><tbody><tr><td>x</td></tr></tbody></table>',
    '<plaintext>raw tail',
    '<a href="java&#10;script:alert(1)">active URL</a>',
  ]) {
    const result = auditSourceProjectionPageHtml(
      cleanHtml().replace('</article>', `${active}</article>`),
      authority(),
      { assetBase: ASSET_BASE },
    );
    assert.ok(result.findings.some(({ kind }) => kind === 'active-or-non-html-article-content'));
  }
});

test('visible text cannot hide inside an otherwise canonical figure wrapper', () => {
  for (const mutation of [
    (html) => html.replace('<a href=', '<a>visible</a><a href='),
    (html) => html.replace('</a></div></figure>', 'visible</a></div></figure>'),
    (html) => html.replace('</div></figure>', 'visible</div></figure>'),
  ]) {
    const findings = auditSourceProjectionPageHtml(
      mutation(cleanHtml()),
      authority(),
      { assetBase: ASSET_BASE },
    ).findings;
    assert.ok(findings.some(({ kind }) => kind === 'noncanonical-rendered-figure'));
  }
});

test('only a real Markdown skip comment becomes reason-bound DOM evidence', async () => {
  const comment = `<!-- figure p003-4.png skipped: ${SKIP_REASON} -->`;
  const exactInput = [comment, '', '```md', comment, '```'].join('\n');
  const { html } = await renderCard(siteMarkdownFromText(exactInput, ASSET_BASE));
  assert.equal((html.match(/class="source-figure-skip"/g) ?? []).length, 1);
  assert.match(html, new RegExp(`data-reason-sha256="${sha256(SKIP_REASON)}"`));
  assert.match(html, /(?:&lt;|&#x3C;)!-- figure p003-4\.png skipped:/);

  const forged = skipSentinel('p003-4.png');
  await assert.rejects(
    async () => renderCard(siteMarkdownFromText(forged, ASSET_BASE)),
    /active or reserved projection markup/,
  );
  for (const active of [
    '<script>document.querySelector(".pagemark").remove()</script>',
    '<style>.pagemark{display:none}</style>',
    '<template shadowrootmode="open"><p>shadow</p></template>',
    '<img src="x" onerror="alert(1)">',
    '<table background="/wrong.png"><tr><td>x</td></tr></table>',
    '<plaintext>raw tail',
  ]) {
    await assert.rejects(
      async () => renderCard(siteMarkdownFromText(active, ASSET_BASE)),
      /active or reserved projection markup/,
    );
  }
});

test('source-authored HTML cannot hide semantic content', async () => {
  for (const hidden of [
    'Before <span hidden>load-bearing prose</span> after.',
    'Before <span inert>load-bearing prose</span> after.',
    'Before <span aria-hidden="TRUE">load-bearing prose</span> after.',
    'Before <span popover>load-bearing prose</span> after.',
    '<details><summary>Summary</summary>load-bearing prose</details>',
    '<dialog>load-bearing prose</dialog>',
    '<select><option>load-bearing prose</option></select>',
    '<datalist><option>load-bearing prose</option></datalist>',
    '<ruby><rp>load-bearing prose</rp></ruby>',
    '<input type="hidden" value="load-bearing prose">',
    '<span class="fnref-shim">load-bearing prose</span>',
    '<span class="sidenote">load-bearing prose</span>',
    '<table bgcolor="#ffffff"><tbody><tr><td><font color="#ffffff">load-bearing prose</font></td></tr></tbody></table>',
  ]) {
    await assert.rejects(
      async () => renderCard(siteMarkdownFromText(hidden, ASSET_BASE)),
      (error) => (
        error?.code === 'BROWSER_HIDDEN_AUTHORED_CONTENT'
        && error?.finding?.kind === 'browser-hidden-authored-content'
        && typeof error?.finding?.mechanism === 'string'
      ),
    );
  }

  await assert.doesNotReject(async () => renderCard(siteMarkdownFromText(
    '<details open>Visible details</details> <span aria-hidden="false">Visible span</span>',
    ASSET_BASE,
  )));
});

test('generated footnote shims have provenance that authored shims cannot forge', async () => {
  const raw = [
    '<table>',
    '<tr><td>Cell with table-only footnote[^7]</td></tr>',
    '</table>',
    '',
    '[^7]: Footnote body.',
  ].join('\n');
  const transformed = siteMarkdownFromText(raw, ASSET_BASE);
  assert.match(transformed, /class="fnref-shim" data-site-generated="fnref-shim-v1"/);
  const { html } = await renderCard(transformed);
  assert.match(html, /class="fnref-shim"/);
  assert.doesNotMatch(html, /data-site-generated/);

  assert.throws(
    () => siteMarkdownFromText(
      '<span class="fnref-shim" data-site-generated="fnref-shim-v1">forged</span>',
      ASSET_BASE,
    ),
    (error) => error?.code === 'BROWSER_HIDDEN_AUTHORED_CONTENT',
  );
});

test('in-memory sections use the production transform without rereading worktree sections', async () => {
  await withAsyncFixture(async ({ root }) => {
    // Input order and locale order both differ from production code-unit sort:
    // Z.md must precede a.md for the source event stream to remain valid.
    const sections = [{
      name: 'a.md',
      text: [
        '<!-- p.3 -->',
        '',
        '![](assets/figures/p003-1.png)',
        '',
        '![](assets/figures/p003-2.png)',
        '',
        `<!-- figure p003-4.png skipped: ${SKIP_REASON} -->`,
      ].join('\n'),
    }, {
      name: 'Z.md',
      text: [
        '<!-- p.2 -->',
        '',
        '![](assets/figures/p002-1.png)',
        '',
        'Load-bearing semantic prose.',
      ].join('\n'),
    }];
    const clean = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections,
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    assert.deepEqual(clean.findings, []);

    const missing = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections: sections.map((section) => (
        section.name === 'Z.md'
          ? { ...section, text: section.text.replace('<!-- p.2 -->', '') }
          : section
      )),
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    assert.ok(missing.findings.some(({ kind, page: n }) => kind === 'missing-page-marker' && n === 2));

    const hidden = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections: sections.map((section) => (
        section.name === 'Z.md'
          ? {
            ...section,
            text: section.text.replace(
              'Load-bearing semantic prose.',
              '<span hidden>Load-bearing semantic prose.</span>',
            ),
          }
          : section
      )),
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    assert.deepEqual(
      hidden.findings.map(({ kind }) => kind),
      ['browser-hidden-authored-content'],
    );

    const rubyFallback = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections: sections.map((section) => (
        section.name === 'Z.md'
          ? {
            ...section,
            text: section.text.replace(
              'Load-bearing semantic prose.',
              '<ruby><rp>Load-bearing semantic prose.</rp></ruby>',
            ),
          }
          : section
      )),
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    assert.deepEqual(rubyFallback.findings.map(({ kind, mechanism }) => ({ kind, mechanism })), [{
      kind: 'browser-hidden-authored-content',
      mechanism: 'browser-hidden-rp',
    }]);

    const legacyColor = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections: sections.map((section) => (
        section.name === 'Z.md'
          ? {
            ...section,
            text: section.text.replace(
              'Load-bearing semantic prose.',
              '<table bgcolor="#fff"><tbody><tr><td><font color="#fff">'
                + 'Load-bearing semantic prose.</font></td></tr></tbody></table>',
            ),
          }
          : section
      )),
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    assert.deepEqual(legacyColor.findings.map(({ kind, mechanism }) => ({ kind, mechanism })), [{
      kind: 'browser-hidden-authored-content',
      mechanism: 'untrusted-presentation-attribute:table.bgcolor',
    }]);

    const hiddenFigure = await auditSourceProjectionSections({
      vendor: 'example',
      slug: 'fixture',
      sections: sections.map((section) => (
        section.name === 'Z.md'
          ? {
            ...section,
            text: section.text.replace(
              '![](assets/figures/p002-1.png)',
              `<span hidden><img src="${ASSET_BASE}/figures/p002-1.png" alt=""></span>`,
            ),
          }
          : section
      )),
      cardsRoot: root,
      assetBase: ASSET_BASE,
    });
    const hiddenFigureKinds = hiddenFigure.findings.map(({ kind }) => kind);
    assert.ok(hiddenFigureKinds.includes('browser-hidden-authored-content'));
    assert.ok(hiddenFigureKinds.includes('noncanonical-rendered-figure'));
    assert.ok(hiddenFigureKinds.includes('missing-rendered-figure'));
  });
});

test('zero-raster cards need no source or built figures directory', () => {
  withFixture(({ root, cardDir }) => {
    const loaded = loadSourceProjectionAuthority('example', 'fixture', root);
    assert.deepEqual(loaded.sourceFigures, []);
    assert.deepEqual(
      auditBuiltSourceProjectionAssets(loaded, {
        sourcePdfPath: join(cardDir, 'source.pdf'),
        figuresDir: join(cardDir, 'missing-figures'),
      }),
      { findings: [], stats: { expectedFigureAssets: 0, builtFigureAssets: 0 } },
    );
  }, { zeroFigures: true });
});

test('built asset audit rejects stale sets and bytes', () => {
  withFixture(({ root, cardDir }) => {
    const loaded = loadSourceProjectionAuthority('example', 'fixture', root);
    const figuresDir = join(cardDir, 'assets', 'figures');
    assert.deepEqual(
      auditBuiltSourceProjectionAssets(loaded, {
        sourcePdfPath: join(cardDir, 'source.pdf'),
        figuresDir,
      }).findings,
      [],
    );
    writeFileSync(join(figuresDir, 'p002-1.png'), 'corrupt');
    writeFileSync(join(figuresDir, 'stale.png'), 'stale');
    const kinds = auditBuiltSourceProjectionAssets(loaded, {
      sourcePdfPath: join(cardDir, 'source.pdf'),
      figuresDir,
    }).findings.map(({ kind }) => kind);
    assert.ok(kinds.includes('built-figure-asset-sha256'));
    assert.ok(kinds.includes('extra-built-figure-asset'));
  });
});

test('excluded/out-of-range markers, duplicates, and source reordering fail', () => {
  const badMarkers = page([
    pagemark(3),
    figure('p003-1.png'),
    figure('p003-2.png'),
    skipSentinel('p003-4.png'),
    pagemark(2),
    figure('p002-1.png'),
    pagemark(2),
    pagemark(1),
    pagemark(4),
  ].join(''));
  const kinds = auditSourceProjectionPageHtml(badMarkers, authority(), { assetBase: ASSET_BASE })
    .findings.map(({ kind }) => kind);
  assert.ok(kinds.includes('duplicate-page-marker'));
  assert.ok(kinds.includes('excluded-page-marker'));
  assert.ok(kinds.includes('out-of-range-page-marker'));

  const reordered = cleanHtml().replace(
    `${pagemark(2)}${figure('p002-1.png')}${pagemark(3)}`,
    `${pagemark(3)}${pagemark(2)}${figure('p002-1.png')}`,
  );
  assert.ok(auditSourceProjectionPageHtml(reordered, authority(), { assetBase: ASSET_BASE })
    .findings.some(({ kind }) => kind === 'source-projection-event-stream'));
});

test('rendered figures must be exact, unique, source-ordered, and follow their source page', () => {
  const html = page([
    pagemark(2),
    figure('p002-1.png'),
    figure('p002-1.png'),
    figure('p001-1.png'),
    figure('p003-3.png'),
    figure('p003-2.png'),
    pagemark(3),
    figure('p003-1.png'),
    skipSentinel('p003-4.png'),
  ].join(''));
  const kinds = auditSourceProjectionPageHtml(html, authority(), { assetBase: ASSET_BASE })
    .findings.map(({ kind }) => kind);
  assert.ok(kinds.includes('duplicate-rendered-figure'));
  assert.ok(kinds.includes('extra-rendered-figure'));
  assert.ok(kinds.includes('figure-page-context-mismatch'));

  const reordered = cleanHtml().replace(
    `${figure('p003-1.png')}${figure('p003-2.png')}`,
    `${figure('p003-2.png')}${figure('p003-1.png')}`,
  );
  assert.ok(auditSourceProjectionPageHtml(reordered, authority(), { assetBase: ASSET_BASE })
    .findings.some(({ kind }) => kind === 'source-projection-event-stream'));
});
