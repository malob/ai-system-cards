// Fail-closed bridge from the independent source/canonical L2 report to the
// browser-normalized article DOM. This module does not resolve PDF destinations
// or create slugs; it only verifies artifact freshness and projection fidelity.
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

import { CARDS_ROOT } from './card-inventory.js';
import { auditArticleHtml } from './article-dom.js';

export const L2_ARTIFACT_NAME = 'l2-links.json';
export const L2_ARTIFACT_SCHEMA = 1;

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

// pathlib.Path.read_text() performs universal-newline translation. Mirror it
// so artifacts generated on another platform bind to the same canonical text.
function canonicalSectionText(path) {
  return readFileSync(path, 'utf8').replace(/\r\n?/g, '\n');
}

function lengthPrefix(length) {
  const bytes = Buffer.alloc(8);
  bytes.writeBigUInt64BE(BigInt(length));
  return bytes;
}

export function liveL2Digests(vendor, slug, cardsRoot = CARDS_ROOT) {
  const cardDir = join(cardsRoot, vendor, slug);
  const sectionsDir = join(cardDir, 'sections');
  const names = readdirSync(sectionsDir).filter((name) => name.endsWith('.md')).sort();
  const sectionSha256 = {};
  const digest = createHash('sha256');

  for (const name of names) {
    const nameBytes = Buffer.from(name, 'utf8');
    const bodyBytes = Buffer.from(canonicalSectionText(join(sectionsDir, name)), 'utf8');
    sectionSha256[name] = sha256(bodyBytes);
    digest.update(lengthPrefix(nameBytes.length));
    digest.update(nameBytes);
    digest.update(lengthPrefix(bodyBytes.length));
    digest.update(bodyBytes);
  }

  return {
    sourceSha256: sha256(readFileSync(join(cardDir, 'source.pdf'))),
    canonicalSectionsSha256: digest.digest('hex'),
    sectionSha256,
  };
}

function artifactError(cardId, message) {
  return new Error(`Stale or invalid L2 artifact for ${cardId}: ${message}`);
}

function requireEqual(cardId, field, actual, expected) {
  if (actual !== expected) {
    throw artifactError(cardId, `${field} is ${JSON.stringify(actual)}, expected ${JSON.stringify(expected)}`);
  }
}

/** Load and validate the source/canonical artifact against current card bytes. */
export function loadL2Artifact(vendor, slug, cardsRoot = CARDS_ROOT) {
  const cardId = `${vendor}/${slug}`;
  const path = join(cardsRoot, vendor, slug, L2_ARTIFACT_NAME);
  let artifact;
  try {
    artifact = JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw artifactError(cardId, `${L2_ARTIFACT_NAME} cannot be read: ${error.message}`);
  }

  requireEqual(cardId, 'schema_version', artifact.schema_version, L2_ARTIFACT_SCHEMA);
  requireEqual(cardId, 'card_id', artifact.card_id, cardId);
  if (!Array.isArray(artifact.flags) || artifact.flags.length) {
    throw artifactError(cardId, `flags must be an empty array, got ${JSON.stringify(artifact.flags)}`);
  }
  if (!Array.isArray(artifact.canonical_links) || !Array.isArray(artifact.expected_links)) {
    throw artifactError(cardId, 'canonical_links and expected_links must be arrays');
  }

  const live = liveL2Digests(vendor, slug, cardsRoot);
  requireEqual(cardId, 'source_sha256', artifact.source_sha256, live.sourceSha256);
  requireEqual(
    cardId,
    'canonical_sections_sha256',
    artifact.canonical_sections_sha256,
    live.canonicalSectionsSha256,
  );
  requireEqual(
    cardId,
    'section_sha256',
    JSON.stringify(artifact.section_sha256),
    JSON.stringify(live.sectionSha256),
  );

  for (const [index, link] of artifact.canonical_links.entries()) {
    requireEqual(cardId, `canonical_links[${index}].authoredLinkIndex`, link.authoredLinkIndex, index);
    if (typeof link.text !== 'string' || typeof link.href !== 'string' || !link.href.startsWith('#')) {
      throw artifactError(cardId, `canonical_links[${index}] needs string text and fragment href`);
    }
  }
  const expectedIndexes = [];
  for (const [index, expected] of artifact.expected_links.entries()) {
    const authoredIndex = expected.authoredLinkIndex;
    if (!Number.isInteger(authoredIndex) || !artifact.canonical_links[authoredIndex]) {
      throw artifactError(cardId, `expected_links[${index}] has invalid authoredLinkIndex`);
    }
    expectedIndexes.push(authoredIndex);
    const canonical = artifact.canonical_links[authoredIndex];
    requireEqual(cardId, `expected_links[${index}].actual_href`, expected.actual_href, canonical.href);
    requireEqual(cardId, `expected_links[${index}].expected_href`, expected.expected_href, `#${expected.targetId}`);
    requireEqual(cardId, `expected_links[${index}] source/canonical target`, expected.actual_href, expected.expected_href);
  }
  const exactCover = [...new Set(expectedIndexes)].sort((a, b) => a - b);
  if (artifact.expected_links.length !== artifact.canonical_links.length
      || exactCover.length !== artifact.canonical_links.length
      || exactCover.some((value, index) => value !== index)) {
    throw artifactError(
      cardId,
      `expected_links authoredLinkIndex must exactly cover 0..${artifact.canonical_links.length - 1}`,
    );
  }

  return { artifact, path, live };
}

function projectionText(text) {
  return text
    .normalize('NFC')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201c\u201d]/g, '"')
    .replace(/\s+/g, ' ')
    .trim();
}

function projectionFinding(kind, lane, expected, actual, detail = {}) {
  return {
    kind,
    lane,
    authoredLinkIndex: expected?.authoredLinkIndex ?? actual?.authoredLinkIndex ?? null,
    expectedText: expected?.text ?? null,
    actualText: actual?.text ?? null,
    expectedHref: expected?.href ?? null,
    actualHref: actual?.href ?? null,
    ...detail,
  };
}

/**
 * Prove that every canonical authored fragment link reaches the article DOM
 * without being dropped, inserted, reordered, or repointed. Footnote-definition
 * links are compared in a separate lane because GFM deliberately relocates
 * their definitions to the final footnotes section.
 */
export function auditL2Projection(html, artifact) {
  const { model, findings: graphFindings } = auditArticleHtml(html);
  const findings = [...graphFindings];
  const matchedByAuthoredIndex = new Map();
  const lanes = [
    {
      name: 'body',
      expected: artifact.canonical_links.filter((link) => !link.relocatedFootnote),
      actual: model.authoredInternalLinks.filter((link) => !link.relocatedFootnote),
    },
    {
      name: 'relocated-footnote',
      expected: artifact.canonical_links.filter((link) => link.relocatedFootnote),
      actual: model.authoredInternalLinks.filter((link) => link.relocatedFootnote),
    },
  ];

  for (const lane of lanes) {
    const length = Math.max(lane.expected.length, lane.actual.length);
    for (let index = 0; index < length; index += 1) {
      const expected = lane.expected[index];
      const actual = lane.actual[index];
      if (!expected) {
        findings.push(projectionFinding('unexpected-authored-link', lane.name, null, actual));
        continue;
      }
      if (!actual) {
        findings.push(projectionFinding('missing-authored-link', lane.name, expected, null));
        continue;
      }
      matchedByAuthoredIndex.set(expected.authoredLinkIndex, actual);
      if (projectionText(actual.text) !== projectionText(expected.text)) {
        findings.push(projectionFinding('authored-link-text-mismatch', lane.name, expected, actual));
      }
      if (actual.href !== expected.href) {
        findings.push(projectionFinding('authored-link-href-mismatch', lane.name, expected, actual));
      }
    }
  }

  for (const expected of artifact.expected_links) {
    const actual = matchedByAuthoredIndex.get(expected.authoredLinkIndex);
    if (!actual) {
      findings.push({
        kind: 'source-expected-link-missing',
        key: expected.key,
        authoredLinkIndex: expected.authoredLinkIndex,
        expectedTargetId: expected.targetId,
      });
    } else if (actual.targetId !== expected.targetId) {
      findings.push({
        kind: 'source-expected-target-mismatch',
        key: expected.key,
        authoredLinkIndex: expected.authoredLinkIndex,
        text: actual.text,
        href: actual.href,
        expectedTargetId: expected.targetId,
        actualTargetId: actual.targetId,
      });
    }
  }

  return { model, findings, matchedByAuthoredIndex };
}
