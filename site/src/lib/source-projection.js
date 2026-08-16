// Source-bound projection checks over the HTML5-normalized, built page DOM.
//
// The Python verifier remains the authority that binds source-inventory.json
// and figures-map.json to raw PDF observations. This site-side lane strictly
// validates its checked-in source-projection.json artifact and asks the narrower
// deployment question: did every required page and visual raster actually
// survive into the built HTML, exactly once and in source order?
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

import { parse } from 'parse5';
import YAML from 'yaml';

import { CARDS_ROOT } from './card-inventory.js';
import { siteMarkdownFromText } from './cards.js';
import { liveL2Digests } from './l2-artifact.js';
import { AuthoredHtmlPolicyError, renderCard } from './markdown.js';

const PAGE_OBSERVATION_KEYS = new Set([
  'page',
  'word_count',
  'text_chars',
  'internal_links',
  'uri_links',
  'drawing_count',
  'raster_count',
]);
const PROJECTION_KEYS = new Set([
  'assets',
  'card_id',
  'events',
  'inputs',
  'observer_schema_version',
  'pages',
  'pymupdf_version',
  'schema_version',
  'source',
  'source_flags',
]);
const PROJECTION_SOURCE_KEYS = new Set(['file', 'page_count', 'sha256']);
const PROJECTION_INPUT_KEYS = new Set(['canonical_sections', 'figures_map', 'inventory']);
const FILE_INPUT_KEYS = new Set(['file', 'sha256']);
const SECTION_INPUT_KEYS = new Set(['digest_method', 'sha256']);
const PROJECTION_PAGE_KEYS = new Set([
  'disposition',
  'pdf_page',
  'reason_sha256',
  'source_observation',
]);
const PROJECTION_ASSET_KEYS = new Set([
  'disposition',
  'duplicate_of',
  'file_sha256',
  'filename',
  'has_alpha',
  'height',
  'logical_path',
  'reason_sha256',
  'source',
  'width',
]);
const PROJECTION_ASSET_SOURCE_KEYS = new Set([
  'asset_sample_md5',
  'bbox',
  'draw_index',
  'has_soft_mask',
  'pdf_page',
  'raw_sample_md5',
  'xref',
]);
const PAGE_EVENT_KEYS = new Set(['anchor', 'kind', 'pdf_page']);
const FIGURE_EVENT_KEYS = new Set([
  'asset_sha256',
  'draw_index',
  'filename',
  'kind',
  'logical_src',
  'pdf_page',
]);
const SKIP_EVENT_KEYS = new Set([
  'draw_index',
  'filename',
  'kind',
  'pdf_page',
  'reason_sha256',
]);
const ACTIVE_ARTICLE_TAGS = new Set([
  'audio',
  'base',
  'canvas',
  'embed',
  'iframe',
  'listing',
  'link',
  'meta',
  'noembed',
  'noframes',
  'noscript',
  'object',
  'picture',
  'plaintext',
  'script',
  'source',
  'style',
  'template',
  'textarea',
  'title',
  'track',
  'video',
  'xmp',
]);
const BROWSER_HIDDEN_CONTAINER_TAGS = new Set([
  'datalist',
  'option',
  'optgroup',
  'select',
]);
const FIGURE_NAME = /^p(?<page>\d{3,})-(?<ordinal>[1-9]\d*)\.png$/;
const SHA256 = /^[0-9a-f]{64}$/;

function fail(message) {
  throw new TypeError(`Source projection authority: ${message}`);
}

function plainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function exactKeys(value, expected, label) {
  if (!plainObject(value)) fail(`${label} must be an object`);
  const actual = Object.keys(value);
  if (actual.length !== expected.size || actual.some((key) => !expected.has(key))) {
    fail(`${label} keys must be exactly ${[...expected].sort().join(', ')}`);
  }
}

function naturalNumber(value, label, { allowZero = true } = {}) {
  if (!Number.isInteger(value) || value < (allowZero ? 0 : 1)) {
    fail(`${label} must be ${allowZero ? 'a non-negative' : 'a positive'} integer`);
  }
}

function nonEmptyString(value, label) {
  if (typeof value !== 'string' || !value.trim()) fail(`${label} must be a non-empty string`);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function validatePageObservation(observation, page, label) {
  exactKeys(observation, PAGE_OBSERVATION_KEYS, label);
  for (const key of PAGE_OBSERVATION_KEYS) naturalNumber(observation[key], `${label}.${key}`);
  if (observation.page !== page) fail(`${label}.page must equal its exclusion page`);
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (plainObject(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function digestOrNull(value, label, { required = false } = {}) {
  if (value === null && !required) return;
  if (typeof value !== 'string' || !SHA256.test(value)) fail(`${label} must be a lowercase SHA-256 digest`);
}

function loadProjectionArtifact(cardId, cardDir, cardsRoot) {
  const artifactPath = join(cardDir, 'source-projection.json');
  let artifact;
  try {
    artifact = JSON.parse(readFileSync(artifactPath, 'utf8'));
  } catch (error) {
    fail(`${cardId}/source-projection.json cannot be read: ${error.message}`);
  }
  exactKeys(artifact, PROJECTION_KEYS, `${cardId}/source-projection.json`);
  if (artifact.schema_version !== 1) fail(`${cardId} has an unsupported projection schema_version`);
  if (artifact.card_id !== cardId) fail(`${cardId} projection card_id disagrees`);
  if (artifact.observer_schema_version !== 2) fail(`${cardId} projection observer schema disagrees`);
  nonEmptyString(artifact.pymupdf_version, `${cardId}.pymupdf_version`);
  if (!Array.isArray(artifact.source_flags) || artifact.source_flags.length) {
    fail(`${cardId}.source_flags must be an empty array`);
  }

  exactKeys(artifact.source, PROJECTION_SOURCE_KEYS, `${cardId}.source`);
  if (artifact.source.file !== 'source.pdf') fail(`${cardId}.source.file must be source.pdf`);
  naturalNumber(artifact.source.page_count, `${cardId}.source.page_count`, { allowZero: false });
  digestOrNull(artifact.source.sha256, `${cardId}.source.sha256`, { required: true });
  const liveSourceSha256 = sha256(readFileSync(join(cardDir, 'source.pdf')));
  if (artifact.source.sha256 !== liveSourceSha256) fail(`${cardId}.source.sha256 is stale`);
  const meta = YAML.parse(readFileSync(join(cardDir, 'meta.yaml'), 'utf8'));
  if (meta?.source_pages !== artifact.source.page_count) fail(`${cardId}.source.page_count disagrees with meta.yaml`);

  exactKeys(artifact.inputs, PROJECTION_INPUT_KEYS, `${cardId}.inputs`);
  const fileInputs = [
    ['inventory', 'source-inventory.json'],
    ['figures_map', 'extracted/figures-map.json'],
  ];
  for (const [key, expectedFile] of fileInputs) {
    const input = artifact.inputs[key];
    exactKeys(input, FILE_INPUT_KEYS, `${cardId}.inputs.${key}`);
    if (input.file !== expectedFile) fail(`${cardId}.inputs.${key}.file is not canonical`);
    digestOrNull(input.sha256, `${cardId}.inputs.${key}.sha256`, { required: true });
    if (input.sha256 !== sha256(readFileSync(join(cardDir, ...expectedFile.split('/'))))) {
      fail(`${cardId}.inputs.${key}.sha256 is stale`);
    }
  }
  const canonicalSections = artifact.inputs.canonical_sections;
  exactKeys(canonicalSections, SECTION_INPUT_KEYS, `${cardId}.inputs.canonical_sections`);
  if (canonicalSections.digest_method !== 'l2.sections_sha256.v1') {
    fail(`${cardId}.inputs.canonical_sections.digest_method is unknown`);
  }
  digestOrNull(
    canonicalSections.sha256,
    `${cardId}.inputs.canonical_sections.sha256`,
    { required: true },
  );
  const liveSections = liveL2Digests(...cardId.split('/'), cardsRoot).canonicalSectionsSha256;
  if (canonicalSections.sha256 !== liveSections) fail(`${cardId} canonical section digest is stale`);

  if (!Array.isArray(artifact.pages) || artifact.pages.length !== artifact.source.page_count) {
    fail(`${cardId}.pages must cover every source page exactly once`);
  }
  const pages = artifact.pages.map((page, index) => {
    const label = `${cardId}.pages[${index}]`;
    exactKeys(page, PROJECTION_PAGE_KEYS, label);
    if (page.pdf_page !== index + 1) fail(`${label}.pdf_page is not complete source order`);
    if (!['content', 'cover', 'toc', 'blank'].includes(page.disposition)) {
      fail(`${label}.disposition is unknown`);
    }
    digestOrNull(page.reason_sha256, `${label}.reason_sha256`, {
      required: page.disposition !== 'content',
    });
    if (page.disposition === 'content' && page.reason_sha256 !== null) {
      fail(`${label}.reason_sha256 must be null for content`);
    }
    validatePageObservation(page.source_observation, page.pdf_page, `${label}.source_observation`);
    return page;
  });
  const pageByNumber = new Map(pages.map((page) => [page.pdf_page, page]));

  if (!Array.isArray(artifact.assets)) fail(`${cardId}.assets must be an array`);
  const assets = [];
  const assetByName = new Map();
  let priorPage = 0;
  let priorDraw = 0;
  for (const [index, asset] of artifact.assets.entries()) {
    const label = `${cardId}.assets[${index}]`;
    exactKeys(asset, PROJECTION_ASSET_KEYS, label);
    exactKeys(asset.source, PROJECTION_ASSET_SOURCE_KEYS, `${label}.source`);
    naturalNumber(asset.source.pdf_page, `${label}.source.pdf_page`, { allowZero: false });
    naturalNumber(asset.source.draw_index, `${label}.source.draw_index`, { allowZero: false });
    naturalNumber(asset.source.xref, `${label}.source.xref`);
    const page = pageByNumber.get(asset.source.pdf_page);
    if (!page) fail(`${label} names an unknown source page`);
    if (
      asset.source.pdf_page < priorPage
      || (asset.source.pdf_page === priorPage && asset.source.draw_index !== priorDraw + 1)
      || (asset.source.pdf_page > priorPage && asset.source.draw_index !== 1)
    ) {
      fail(`${label}.source is not complete page/draw order`);
    }
    priorPage = asset.source.pdf_page;
    priorDraw = asset.source.draw_index;
    const expectedName = `p${String(priorPage).padStart(3, '0')}-${priorDraw}.png`;
    if (asset.filename !== expectedName || asset.logical_path !== `figures/${expectedName}`) {
      fail(`${label} filename/logical_path is not canonical`);
    }
    if (assetByName.has(asset.filename)) fail(`${label}.filename is duplicated`);
    digestOrNull(asset.file_sha256, `${label}.file_sha256`, { required: true });
    naturalNumber(asset.width, `${label}.width`, { allowZero: false });
    naturalNumber(asset.height, `${label}.height`, { allowZero: false });
    if (typeof asset.has_alpha !== 'boolean') fail(`${label}.has_alpha must be boolean`);
    if (typeof asset.source.has_soft_mask !== 'boolean') fail(`${label}.source.has_soft_mask must be boolean`);
    if (asset.has_alpha !== asset.source.has_soft_mask) fail(`${label} alpha identity disagrees`);
    for (const key of ['raw_sample_md5', 'asset_sample_md5']) {
      if (typeof asset.source[key] !== 'string' || !/^[0-9a-f]{32}$/.test(asset.source[key])) {
        fail(`${label}.source.${key} must be lowercase MD5`);
      }
    }
    if (
      !Array.isArray(asset.source.bbox)
      || asset.source.bbox.length !== 4
      || asset.source.bbox.some((value) => typeof value !== 'number' || !Number.isFinite(value))
    ) fail(`${label}.source.bbox must contain four finite numbers`);

    const expectedExcludedDisposition = page.disposition === 'content'
      ? null
      : `excluded-${page.disposition}`;
    const contentDispositions = ['required-output', 'accepted-skip', 'duplicate-draw'];
    if (
      (expectedExcludedDisposition && asset.disposition !== expectedExcludedDisposition)
      || (!expectedExcludedDisposition && !contentDispositions.includes(asset.disposition))
    ) fail(`${label}.disposition disagrees with its page`);
    const reasonRequired = asset.disposition !== 'required-output';
    digestOrNull(asset.reason_sha256, `${label}.reason_sha256`, { required: reasonRequired });
    if (!reasonRequired && asset.reason_sha256 !== null) fail(`${label}.reason_sha256 must be null`);
    if (expectedExcludedDisposition && asset.reason_sha256 !== page.reason_sha256) {
      fail(`${label}.reason_sha256 disagrees with its page exclusion`);
    }
    if (asset.disposition === 'duplicate-draw') {
      const target = assetByName.get(asset.duplicate_of);
      if (!target || target.source.pdf_page !== asset.source.pdf_page) {
        fail(`${label}.duplicate_of must name a prior same-page asset`);
      }
    } else if (asset.duplicate_of !== null) {
      fail(`${label}.duplicate_of must be null`);
    }
    assetByName.set(asset.filename, asset);
    assets.push(asset);
  }
  for (const page of pages) {
    const pageAssets = assets.filter(({ source }) => source.pdf_page === page.pdf_page);
    if (pageAssets.length !== page.source_observation.raster_count) {
      fail(`${cardId}.assets do not cover every raster on page ${page.pdf_page}`);
    }
  }

  const expectedArtifactEvents = [];
  const assetsByPage = new Map();
  for (const asset of assets) {
    const pageAssets = assetsByPage.get(asset.source.pdf_page) ?? [];
    pageAssets.push(asset);
    assetsByPage.set(asset.source.pdf_page, pageAssets);
  }
  for (const page of pages) {
    if (page.disposition !== 'content') continue;
    expectedArtifactEvents.push({ anchor: `p-${page.pdf_page}`, kind: 'page', pdf_page: page.pdf_page });
    for (const asset of assetsByPage.get(page.pdf_page) ?? []) {
      if (asset.disposition === 'required-output') {
        expectedArtifactEvents.push({
          asset_sha256: asset.file_sha256,
          draw_index: asset.source.draw_index,
          filename: asset.filename,
          kind: 'figure',
          logical_src: asset.logical_path,
          pdf_page: page.pdf_page,
        });
      } else if (asset.disposition === 'accepted-skip') {
        expectedArtifactEvents.push({
          draw_index: asset.source.draw_index,
          filename: asset.filename,
          kind: 'accepted-skip',
          pdf_page: page.pdf_page,
          reason_sha256: asset.reason_sha256,
        });
      }
    }
  }
  if (!Array.isArray(artifact.events) || stableJson(artifact.events) !== stableJson(expectedArtifactEvents)) {
    fail(`${cardId}.events is not the exact source projection stream`);
  }
  for (const [index, event] of artifact.events.entries()) {
    const keys = event.kind === 'page'
      ? PAGE_EVENT_KEYS
      : event.kind === 'figure'
        ? FIGURE_EVENT_KEYS
        : event.kind === 'accepted-skip'
          ? SKIP_EVENT_KEYS
          : null;
    if (!keys) fail(`${cardId}.events[${index}].kind is unknown`);
    exactKeys(event, keys, `${cardId}.events[${index}]`);
  }

  return { artifact, pages, assets };
}

export function loadSourceProjectionAuthority(vendor, slug, cardsRoot = CARDS_ROOT) {
  const cardId = `${vendor}/${slug}`;
  const cardDir = join(cardsRoot, vendor, slug);
  const { artifact, pages, assets } = loadProjectionArtifact(cardId, cardDir, cardsRoot);
  const requiredPages = pages
    .filter(({ disposition }) => disposition === 'content')
    .map(({ pdf_page: page }) => page);
  const excludedPages = new Map(
    pages
      .filter(({ disposition }) => disposition !== 'content')
      .map((page) => [page.pdf_page, { kind: page.disposition, reasonSha256: page.reason_sha256 }]),
  );
  const sourceFigures = assets.map((asset, sourceIndex) => ({
    filename: asset.filename,
    page: asset.source.pdf_page,
    ordinal: asset.source.draw_index,
    sourceIndex,
    width: asset.width,
    height: asset.height,
  }));
  const requiredFigures = sourceFigures.filter(
    ({ filename }) => assetByDisposition(assets, filename) === 'required-output',
  );
  const requiredFigureSkips = sourceFigures.filter(
    ({ filename }) => assetByDisposition(assets, filename) === 'accepted-skip',
  );
  const excludedFigures = new Map(
    assets
      .filter(({ disposition }) => ['accepted-skip', 'duplicate-draw'].includes(disposition))
      .map((asset) => [asset.filename, {
        kind: asset.disposition === 'accepted-skip' ? 'allow-skip' : 'duplicate-draw',
        reasonSha256: asset.reason_sha256,
      }]),
  );
  const expectedEvents = artifact.events.map((event) => {
    if (event.kind === 'page') return { kind: 'page', page: event.pdf_page };
    if (event.kind === 'figure') return { kind: 'figure', filename: event.filename };
    return { kind: 'accepted-skip', page: event.pdf_page, filename: event.filename };
  });
  const figureAssetSha256 = new Map(assets.map((asset) => [asset.filename, asset.file_sha256]));
  const figuresDir = join(cardDir, 'assets', 'figures');
  if (!existsSync(figuresDir) && sourceFigures.length) {
    fail('assets/figures is missing for a non-empty figures-map.json');
  }
  const entries = existsSync(figuresDir)
    ? readdirSync(figuresDir, { withFileTypes: true })
    : [];
  const actualNames = entries.filter((entry) => entry.isFile()).map(({ name }) => name).sort();
  const nonFiles = entries.filter((entry) => !entry.isFile()).map(({ name }) => name).sort();
  if (nonFiles.length) fail(`assets/figures contains non-files: ${nonFiles.join(', ')}`);
  const expectedNames = sourceFigures.map(({ filename }) => filename).sort();
  if (
    actualNames.length !== expectedNames.length
    || actualNames.some((name, index) => name !== expectedNames[index])
  ) {
    fail('assets/figures filename set disagrees with source-projection.json');
  }
  for (const name of expectedNames) {
    if (sha256(readFileSync(join(figuresDir, name))) !== figureAssetSha256.get(name)) {
      fail(`assets/figures/${name} disagrees with source-projection.json`);
    }
  }
  return {
    schemaVersion: artifact.schema_version,
    cardId,
    sourcePages: artifact.source.page_count,
    sourceSha256: artifact.source.sha256,
    requiredPages,
    excludedPages,
    sourceFigures,
    requiredFigures,
    requiredFigureSkips,
    excludedFigures,
    expectedEvents,
    figureAssetSha256,
  };
}

function assetByDisposition(assets, filename) {
  return assets.find((asset) => asset.filename === filename)?.disposition;
}

/** Verify the published source PDF and copied figure assets, including bytes. */
export function auditBuiltSourceProjectionAssets(authority, { sourcePdfPath, figuresDir }) {
  const findings = [];
  try {
    const actual = sha256(readFileSync(sourcePdfPath));
    if (actual !== authority.sourceSha256) {
      findings.push({
        kind: 'built-source-pdf-sha256',
        expected: authority.sourceSha256,
        actual,
      });
    }
  } catch (error) {
    findings.push({ kind: 'built-source-pdf-unreadable', message: error.message });
  }

  let entries = [];
  if (!existsSync(figuresDir) && authority.sourceFigures.length === 0) {
    return {
      findings,
      stats: { expectedFigureAssets: 0, builtFigureAssets: 0 },
    };
  }
  try {
    entries = readdirSync(figuresDir, { withFileTypes: true });
  } catch (error) {
    findings.push({ kind: 'built-figure-directory-unreadable', message: error.message });
    return {
      findings,
      stats: { expectedFigureAssets: authority.sourceFigures.length, builtFigureAssets: 0 },
    };
  }
  const actualNames = entries.map(({ name }) => name).sort();
  const expectedNames = authority.sourceFigures.map(({ filename }) => filename).sort();
  const expectedSet = new Set(expectedNames);
  const actualSet = new Set(actualNames);
  for (const name of expectedNames) {
    if (!actualSet.has(name)) findings.push({ kind: 'missing-built-figure-asset', filename: name });
  }
  for (const name of actualNames) {
    if (!expectedSet.has(name)) findings.push({ kind: 'extra-built-figure-asset', filename: name });
  }
  const expectedHashes = authority.figureAssetSha256;
  if (!(expectedHashes instanceof Map)) fail('loaded figure asset digests are required');
  for (const entry of entries) {
    if (!expectedSet.has(entry.name)) continue;
    if (!entry.isFile()) {
      findings.push({ kind: 'built-figure-asset-not-file', filename: entry.name });
      continue;
    }
    const actual = sha256(readFileSync(join(figuresDir, entry.name)));
    const expected = expectedHashes.get(entry.name);
    if (actual !== expected) {
      findings.push({
        kind: 'built-figure-asset-sha256',
        filename: entry.name,
        expected,
        actual,
      });
    }
  }
  return {
    findings,
    stats: { expectedFigureAssets: expectedNames.length, builtFigureAssets: actualNames.length },
  };
}

function attrsOf(node) {
  return Object.fromEntries((node.attrs ?? []).map(({ name, value }) => [name, value]));
}

const HTML_NAMESPACE = 'http://www.w3.org/1999/xhtml';

function isHtmlElement(node) {
  return node?.namespaceURI === HTML_NAMESPACE;
}

function classTokens(node) {
  return (attrsOf(node).class ?? '').split(/\s+/).filter(Boolean);
}

function hasClass(node, name) {
  return classTokens(node).includes(name);
}

function exactAttributeNames(node, names) {
  const actual = (node.attrs ?? []).map(({ name }) => name).sort();
  return actual.length === names.length && actual.every((name, index) => name === names[index]);
}

function elementChildren(node) {
  return (node.childNodes ?? []).filter((child) => child.tagName);
}

function textOf(node) {
  if (node.nodeName === '#text') return node.value;
  return (node.childNodes ?? []).map(textOf).join('');
}

function hasDirectVisibleText(node) {
  return (node.childNodes ?? []).some(
    (child) => child.nodeName === '#text' && child.value.trim() !== '',
  );
}

function inlineStyleDeclarations(styleAttribute) {
  const style = styleAttribute
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .toLowerCase();
  const cascaded = new Map();
  for (const declaration of style.split(';')) {
    const colon = declaration.indexOf(':');
    if (colon < 0) continue;
    const property = declaration.slice(0, colon).trim();
    const rawValue = declaration.slice(colon + 1).trim();
    const important = /!\s*important\s*$/i.test(rawValue);
    const value = rawValue.replace(/!\s*important\s*$/i, '').trim();
    const prior = cascaded.get(property);
    // Inline declarations share origin and specificity: an important value
    // beats every non-important value; among equal importance, the last wins.
    if (!prior || important || !prior.important) cascaded.set(property, { important, value });
  }
  return new Map([...cascaded].map(([property, { value }]) => [property, value]));
}

function isHidden(node, ancestors) {
  return [...ancestors, node].some((candidate) => {
    const attrs = attrsOf(candidate);
    const declarations = inlineStyleDeclarations(attrs.style ?? '');
    return Object.hasOwn(attrs, 'hidden')
      || Object.hasOwn(attrs, 'inert')
      || Object.hasOwn(attrs, 'popover')
      || attrs['aria-hidden']?.toLowerCase() === 'true'
      || ['fnref-shim', 'sidenote'].some((className) => hasClass(candidate, className))
      || declarations.get('display') === 'none'
      || ['hidden', 'collapse'].includes(declarations.get('visibility'))
      || declarations.get('content-visibility') === 'hidden'
      || BROWSER_HIDDEN_CONTAINER_TAGS.has(candidate.tagName)
      || (candidate.tagName === 'details' && !Object.hasOwn(attrs, 'open'))
      || (candidate.tagName === 'dialog' && !Object.hasOwn(attrs, 'open'));
  });
}

function activeJavascriptUrl(value) {
  // The URL parser strips ASCII tabs/newlines even when they appear inside a
  // scheme, and trims leading C0 controls/spaces. Mirror that normalization so
  // entity-decoded `java&#10;script:` cannot evade this static gate.
  const browserNormalized = value.replace(/[\u0009\u000a\u000d]/g, '');
  return /^[\u0000-\u0020]*javascript:/i.test(browserNormalized);
}

function canonicalPagemark(node, page, assetBase, ancestors) {
  const attrs = attrsOf(node);
  const expectedNames = [
    'aria-label',
    'class',
    'data-page',
    'href',
    'id',
    'rel',
    'target',
    'title',
  ].sort();
  return isHtmlElement(node)
    && node.tagName === 'a'
    && !isHidden(node, ancestors)
    && exactAttributeNames(node, expectedNames)
    && attrs.class === 'pagemark'
    && attrs.id === `p-${page}`
    && attrs.href === `${assetBase}/source.pdf#page=${page}`
    && attrs.title === `Page ${page} of the source PDF`
    && attrs['aria-label'] === `Page ${page} of the source PDF`
    && attrs['data-page'] === `p.${page}`
    && attrs.target === '_blank'
    && attrs.rel === 'noopener'
    && textOf(node).trim() === '';
}

function markerCandidate(node) {
  if (!node.tagName) return false;
  const attrs = attrsOf(node);
  return classTokens(node).some((token) => token.toLowerCase() === 'pagemark')
    || /^p-\d+$/i.test(attrs.id ?? '')
    || /^p\.\d+$/i.test(attrs['data-page'] ?? '')
    || /\/source\.pdf#page=\d+$/i.test(attrs.href ?? '');
}

function markerClaim(node) {
  const attrs = attrsOf(node);
  const claims = [
    /^p-(\d+)$/i.exec(attrs.id ?? '')?.[1],
    /^p\.(\d+)$/i.exec(attrs['data-page'] ?? '')?.[1],
    /\/source\.pdf#page=(\d+)$/i.exec(attrs.href ?? '')?.[1],
  ].filter((claim) => claim !== undefined).map(Number);
  const unique = [...new Set(claims)];
  return unique.length === 1 ? unique[0] : null;
}

function imageCandidate(node) {
  // There are no decorative images inside a card article. Every final article
  // image must therefore be one exact source-raster projection; this also
  // rejects unrelated/data/srcset-only insertions instead of ignoring them.
  return node.tagName === 'img';
}

function imageName(src) {
  const match = /\/figures\/(p\d{3,}-[1-9]\d*\.png)$/i.exec(src);
  return match?.[1] ?? null;
}

function canonicalFigureImage(node, name, assetBase, ancestors, sourceFigure) {
  if (!name || !FIGURE_NAME.test(name) || isHidden(node, ancestors)) return false;
  const attrs = attrsOf(node);
  const src = `${assetBase}/figures/${name}`;
  if (
    !exactAttributeNames(node, ['alt', 'decoding', 'height', 'loading', 'src', 'width'])
    || attrs.src !== src
    || attrs.alt !== ''
    || attrs.loading !== 'lazy'
    || attrs.decoding !== 'async'
    || !/^\d+$/.test(attrs.width ?? '')
    || !/^\d+$/.test(attrs.height ?? '')
    || Number(attrs.width) < 1
    || Number(attrs.height) < 1
    || (sourceFigure?.width !== undefined && Number(attrs.width) !== sourceFigure.width)
    || (sourceFigure?.height !== undefined && Number(attrs.height) !== sourceFigure.height)
  ) return false;
  const link = ancestors.at(-1);
  const card = ancestors.at(-2);
  const figure = ancestors.at(-3);
  if (
    !isHtmlElement(node)
    || !isHtmlElement(link)
    || !isHtmlElement(card)
    || !isHtmlElement(figure)
    || link?.tagName !== 'a'
    || card?.tagName !== 'div'
    || figure?.tagName !== 'figure'
  ) return false;
  const linkAttrs = attrsOf(link);
  return exactAttributeNames(link, ['class', 'href'])
    && linkAttrs.class === 'figure-zoom'
    && linkAttrs.href === src
    && elementChildren(link).length === 1
    && elementChildren(link)[0] === node
    && !hasDirectVisibleText(link)
    && attrsOf(card).class === 'figure-card'
    && exactAttributeNames(card, ['class'])
    && elementChildren(card).every((child) => child.tagName === 'a' && hasClass(child, 'figure-zoom'))
    && !hasDirectVisibleText(card)
    && exactAttributeNames(figure, [])
    && elementChildren(figure)[0] === card
    && elementChildren(figure).slice(1).every((child) => child.tagName === 'figcaption')
    && !hasDirectVisibleText(figure);
}

function figureLinkCandidate(node, assetBase) {
  if (node.tagName !== 'a') return false;
  const attrs = attrsOf(node);
  return classTokens(node).some((token) => token.toLowerCase() === 'figure-zoom')
    || (attrs.href ?? '').toLowerCase().includes(`${assetBase}/figures/`.toLowerCase());
}

function skipCandidate(node) {
  if (!node.tagName) return false;
  const attrs = attrsOf(node);
  return classTokens(node).some((token) => token.toLowerCase() === 'source-figure-skip')
    || Object.hasOwn(attrs, 'data-figure')
    || Object.hasOwn(attrs, 'data-reason-sha256');
}

function canonicalSkip(node, sourceFigure, exclusion) {
  const attrs = attrsOf(node);
  return isHtmlElement(node)
    && node.tagName === 'span'
    && exactAttributeNames(
      node,
      ['class', 'data-figure', 'data-page', 'data-reason-sha256', 'hidden'],
    )
    && attrs.class === 'source-figure-skip'
    && attrs['data-figure'] === sourceFigure.filename
    && attrs['data-page'] === `p.${sourceFigure.page}`
    && attrs['data-reason-sha256'] === exclusion.reasonSha256
    && textOf(node).trim() === '';
}

function findArticle(document) {
  const articles = [];
  const walk = (node, ancestors = []) => {
    if (isHtmlElement(node) && node.tagName === 'article' && hasClass(node, 'article')) {
      articles.push({ node, ancestors });
    }
    const nextAncestors = node.tagName ? [...ancestors, node] : ancestors;
    for (const child of node.childNodes ?? []) walk(child, nextAncestors);
  };
  walk(document);
  return articles;
}

/** Audit page markers and rendered source figures in a complete built page. */
export function auditSourceProjectionPageHtml(html, authority, { assetBase } = {}) {
  if (
    !plainObject(authority)
    || !Number.isInteger(authority.sourcePages)
    || !Array.isArray(authority.requiredPages)
    || !(authority.excludedPages instanceof Map)
    || !Array.isArray(authority.sourceFigures)
    || !Array.isArray(authority.requiredFigures)
    || !Array.isArray(authority.requiredFigureSkips)
    || !(authority.excludedFigures instanceof Map)
    || !Array.isArray(authority.expectedEvents)
  ) {
    fail('a validated authority object is required');
  }
  if (typeof assetBase !== 'string' || !/^\/[^?#]*[^/?#]$/.test(assetBase)) {
    fail('assetBase must be an absolute, slash-free canonical path');
  }

  const findings = [];
  const articles = findArticle(parse(html, { sourceCodeLocationInfo: true }));
  if (articles.length !== 1) {
    findings.push({ kind: 'article-root-count', expected: 1, actual: articles.length });
    return { findings, stats: { requiredPages: authority.requiredPages.length, requiredFigures: authority.requiredFigures.length } };
  }

  const requiredPageSet = new Set(authority.requiredPages);
  const requiredFigureByName = new Map(
    authority.requiredFigures.map((figure) => [figure.filename, figure]),
  );
  const requiredSkipByName = new Map(
    authority.requiredFigureSkips.map((figure) => [figure.filename, figure]),
  );
  const sourceFigureByName = new Map(
    authority.sourceFigures.map((figure) => [figure.filename, figure]),
  );
  const pagemarks = [];
  const figures = [];
  const figureLinks = [];
  const skips = [];
  const events = [];
  let precedingPage = null;

  const walk = (node, ancestors = []) => {
    if (node.tagName) {
      const attrs = attrsOf(node);
      const activeTag = ACTIVE_ARTICLE_TAGS.has(node.tagName);
      const activeAttribute = Object.keys(attrs).some((name) => /^on/i.test(name) || name === 'style');
      const alternateImage = Object.hasOwn(attrs, 'background')
        || Object.hasOwn(attrs, 'poster')
        || (node.tagName === 'input' && attrs.type?.trim().toLowerCase() === 'image');
      const activeUrl = Object.entries(attrs).some(([name, value]) => (
        ['action', 'formaction', 'href', 'src', 'xlink:href'].includes(name)
        && activeJavascriptUrl(value)
      ));
      if (!isHtmlElement(node) || activeTag || activeAttribute || alternateImage || activeUrl) {
        findings.push({
          kind: 'active-or-non-html-article-content',
          tagName: node.tagName,
          namespace: node.namespaceURI ?? null,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
      }
    }
    // Accepted-skip evidence necessarily carries data-page, but is not a page
    // marker. All other marker-shaped elements remain candidates and must pass
    // the exact canonical anchor contract.
    if (!skipCandidate(node) && markerCandidate(node)) {
      const page = markerClaim(node);
      const canonical = page !== null && canonicalPagemark(node, page, assetBase, ancestors);
      if (!canonical) {
        findings.push({
          kind: 'noncanonical-pagemark',
          claimedPage: page,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
      } else {
        precedingPage = page;
        pagemarks.push({ page, offset: node.sourceCodeLocation?.startOffset ?? null });
        events.push({ kind: 'page', page });
      }
    }

    if (figureLinkCandidate(node, assetBase)) figureLinks.push(node);
    if (skipCandidate(node)) {
      const attrs = attrsOf(node);
      const name = attrs['data-figure'] ?? null;
      const sourceFigure = requiredSkipByName.get(name);
      const exclusion = authority.excludedFigures.get(name);
      if (
        !sourceFigure
        || !exclusion
        || exclusion.kind !== 'allow-skip'
        || !canonicalSkip(node, sourceFigure, exclusion)
      ) {
        findings.push({
          kind: 'noncanonical-figure-skip',
          filename: name,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
      } else {
        skips.push({
          filename: name,
          page: sourceFigure.page,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
        events.push({ kind: 'accepted-skip', page: sourceFigure.page, filename: name });
      }
    }
    if (imageCandidate(node)) {
      const src = attrsOf(node).src ?? '';
      const name = imageName(src);
      const canonical = canonicalFigureImage(
        node,
        name,
        assetBase,
        ancestors,
        sourceFigureByName.get(name),
      );
      if (!canonical) {
        findings.push({
          kind: 'noncanonical-rendered-figure',
          filename: name,
          src,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
      } else {
        figures.push({
          filename: name,
          precedingPage,
          offset: node.sourceCodeLocation?.startOffset ?? null,
        });
        events.push({ kind: 'figure', filename: name });
      }
    }

    const nextAncestors = node.tagName ? [...ancestors, node] : ancestors;
    for (const child of node.childNodes ?? []) walk(child, nextAncestors);
  };
  walk(articles[0].node, articles[0].ancestors);

  for (const link of figureLinks) {
    const attrs = attrsOf(link);
    const children = elementChildren(link);
    if (
      !isHtmlElement(link)
      || attrs.class !== 'figure-zoom'
      || !exactAttributeNames(link, ['class', 'href'])
      || children.length !== 1
      || children[0].tagName !== 'img'
      || attrs.href !== attrsOf(children[0]).src
    ) {
      findings.push({
        kind: 'noncanonical-figure-link',
        href: attrs.href ?? null,
        offset: link.sourceCodeLocation?.startOffset ?? null,
      });
    }
  }

  const pagesByNumber = new Map();
  for (const marker of pagemarks) {
    const occurrences = pagesByNumber.get(marker.page) ?? [];
    occurrences.push(marker);
    pagesByNumber.set(marker.page, occurrences);
    if (marker.page < 1 || marker.page > authority.sourcePages) {
      findings.push({ kind: 'out-of-range-page-marker', page: marker.page });
    } else if (authority.excludedPages.has(marker.page)) {
      findings.push({
        kind: 'excluded-page-marker',
        page: marker.page,
        exclusionKind: authority.excludedPages.get(marker.page).kind,
      });
    }
  }
  for (const page of authority.requiredPages) {
    const count = pagesByNumber.get(page)?.length ?? 0;
    if (count === 0) findings.push({ kind: 'missing-page-marker', page });
    if (count > 1) findings.push({ kind: 'duplicate-page-marker', page, count });
  }
  const projectedPageOrder = pagemarks
    .map(({ page }) => page)
    .filter((page) => requiredPageSet.has(page));
  if (
    projectedPageOrder.length === authority.requiredPages.length
    && projectedPageOrder.some((page, index) => page !== authority.requiredPages[index])
  ) {
    findings.push({
      kind: 'page-marker-order',
      expected: authority.requiredPages,
      actual: projectedPageOrder,
    });
  }

  const figuresByName = new Map();
  for (const figure of figures) {
    const occurrences = figuresByName.get(figure.filename) ?? [];
    occurrences.push(figure);
    figuresByName.set(figure.filename, occurrences);
    const expected = requiredFigureByName.get(figure.filename);
    if (!expected) {
      const exclusion = authority.excludedFigures.get(figure.filename);
      const sourceFigure = sourceFigureByName.get(figure.filename);
      findings.push({
        kind: 'extra-rendered-figure',
        filename: figure.filename,
        reason: exclusion?.kind ?? (sourceFigure && authority.excludedPages.has(sourceFigure.page)
          ? 'excluded-page'
          : 'not-in-source-inventory'),
      });
    } else if (figure.precedingPage !== expected.page) {
      findings.push({
        kind: 'figure-page-context-mismatch',
        filename: figure.filename,
        expectedPage: expected.page,
        precedingPage: figure.precedingPage,
      });
    }
  }
  for (const { filename } of authority.requiredFigures) {
    const count = figuresByName.get(filename)?.length ?? 0;
    if (count === 0) findings.push({ kind: 'missing-rendered-figure', filename });
    if (count > 1) findings.push({ kind: 'duplicate-rendered-figure', filename, count });
  }
  const skipsByName = new Map();
  for (const skip of skips) {
    const occurrences = skipsByName.get(skip.filename) ?? [];
    occurrences.push(skip);
    skipsByName.set(skip.filename, occurrences);
  }
  for (const { filename } of authority.requiredFigureSkips) {
    const count = skipsByName.get(filename)?.length ?? 0;
    if (count === 0) findings.push({ kind: 'missing-figure-skip-sentinel', filename });
    if (count > 1) findings.push({ kind: 'duplicate-figure-skip-sentinel', filename, count });
  }
  const projectedFigureOrder = figures
    .map(({ filename }) => filename)
    .filter((name) => requiredFigureByName.has(name));
  const requiredFigureOrder = authority.requiredFigures.map(({ filename }) => filename);
  if (
    projectedFigureOrder.length === requiredFigureOrder.length
    && projectedFigureOrder.some((name, index) => name !== requiredFigureOrder[index])
  ) {
    findings.push({
      kind: 'rendered-figure-order',
      expected: requiredFigureOrder,
      actual: projectedFigureOrder,
    });
  }

  const expectedEvents = authority.expectedEvents;
  const expectedEventJson = JSON.stringify(expectedEvents);
  const actualEventJson = JSON.stringify(events);
  if (actualEventJson !== expectedEventJson) {
    const mismatch = expectedEvents.findIndex(
      (event, index) => JSON.stringify(event) !== JSON.stringify(events[index]),
    );
    findings.push({
      kind: 'source-projection-event-stream',
      firstMismatch: mismatch < 0 ? Math.min(expectedEvents.length, events.length) : mismatch,
      expectedEvent: expectedEvents[mismatch] ?? null,
      actualEvent: events[mismatch] ?? null,
      expectedCount: expectedEvents.length,
      actualCount: events.length,
      expectedSha256: sha256(Buffer.from(expectedEventJson)),
      actualSha256: sha256(Buffer.from(actualEventJson)),
    });
  }

  return {
    findings,
    stats: {
      requiredPages: authority.requiredPages.length,
      renderedPagemarks: pagemarks.length,
      requiredFigures: authority.requiredFigures.length,
      renderedFigures: figures.length,
      acceptedFigureSkips: skips.length,
    },
  };
}

/**
 * Render and audit exact in-memory section texts without reading sections/.
 * Names are sorted and each body is edge-trimmed exactly like stitchedMarkdown;
 * all content bytes otherwise come only from the supplied array.
 */
export async function auditSourceProjectionSections({
  vendor,
  slug,
  sections,
  cardsRoot = CARDS_ROOT,
  authority = null,
  assetBase = `/ai-system-cards/cards/${vendor}/${slug}`,
}) {
  if (!Array.isArray(sections)) fail('sections must be an array of {name, text}');
  const names = new Set();
  for (const [index, section] of sections.entries()) {
    if (
      !plainObject(section)
      || typeof section.name !== 'string'
      || !section.name.endsWith('.md')
      || typeof section.text !== 'string'
    ) fail(`sections[${index}] must contain a Markdown name and string text`);
    if (names.has(section.name)) fail(`sections[${index}].name is duplicated`);
    names.add(section.name);
  }
  const stitched = [...sections]
    // Match readdirSync(...).sort() in stitchedMarkdown exactly. localeCompare
    // is both locale-sensitive and observably different for case/punctuation.
    .sort((left, right) => (left.name < right.name ? -1 : left.name > right.name ? 1 : 0))
    .map(({ text }) => text.trim())
    .join('\n\n');
  const cardId = `${vendor}/${slug}`;
  const cardDir = join(cardsRoot, vendor, slug);
  const projectionAuthority = authority
    ?? loadSourceProjectionAuthority(vendor, slug, cardsRoot);
  if (projectionAuthority.cardId !== cardId) fail('supplied authority belongs to another card');
  const meta = YAML.parse(readFileSync(join(cardDir, 'meta.yaml'), 'utf8'));
  let markdown;
  let visibilityFinding = null;
  try {
    markdown = siteMarkdownFromText(stitched, assetBase);
  } catch (error) {
    if (!(error instanceof AuthoredHtmlPolicyError)) throw error;
    visibilityFinding = error.finding;
    // Mutation analysis still renders the rejected bytes in a non-executing
    // static pipeline. That preserves independent P2/F3 evidence when a hidden
    // subtree also contains a required marker or raster, while production site
    // rendering remains fail-closed at siteMarkdownFromText above.
    markdown = siteMarkdownFromText(stitched, assetBase, {
      allowUnsafeAuthoredHtmlForAudit: true,
    });
  }
  const { html } = await renderCard(markdown, {
    figuresDir: join(cardDir, 'assets', 'figures'),
    chips: meta.chips ?? {},
    allowHiddenAuthoredHtmlForAudit: visibilityFinding !== null,
  });
  const audit = auditSourceProjectionPageHtml(
    `<article class="article">${html}</article>`,
    projectionAuthority,
    { assetBase },
  );
  return {
    ...audit,
    findings: visibilityFinding ? [visibilityFinding, ...audit.findings] : audit.findings,
    html,
  };
}
