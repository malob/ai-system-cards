import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test from 'node:test';

import {
  extractListStructure,
  LIST_STRUCTURE_SCHEMA_VERSION,
  LIST_TOKEN_DIGEST_METHOD,
} from './list-structure.js';

function digest(tokens) {
  return createHash('sha256').update(JSON.stringify(tokens)).digest('hex');
}

function context(overrides = {}) {
  return {
    nearestPageMarkerId: null,
    nearestSectionId: null,
    blockquoteOccurrences: [],
    tableAncestry: [],
    ...overrides,
  };
}

function list(occurrence, overrides = {}) {
  return {
    kind: 'list',
    occurrence,
    tagName: 'ul',
    markerType: 'bullet',
    start: null,
    reversed: false,
    parentListOccurrence: null,
    parentItemOccurrence: null,
    parentItemTokenOffset: null,
    depth: 0,
    siblingIndex: occurrence,
    descendantPageMarkers: [],
    pageSpan: { startId: null, endId: null },
    ...context(),
    ...overrides,
  };
}

function item(occurrence, listOccurrence, ownText, ownTokens, overrides = {}) {
  return {
    kind: 'item',
    occurrence,
    listOccurrence,
    parentItemOccurrence: null,
    depth: 0,
    siblingIndex: 0,
    explicitValue: null,
    ownText,
    ownTokens,
    ownTokenCount: ownTokens.length,
    ownTokenSha256: digest(ownTokens),
    ownPageMarkers: [],
    childListOccurrences: [],
    listChildPath: [],
    ...context(),
    ...overrides,
  };
}

function observation(events) {
  return {
    schemaVersion: LIST_STRUCTURE_SCHEMA_VERSION,
    tokenDigestMethod: LIST_TOKEN_DIGEST_METHOD,
    events,
  };
}

// Deliberately test-only. Phase 4 needs source constraints mapped onto DOM
// events, not a production API that blesses a checked-in snapshot of today's
// DOM as authority.
function auditListStructure(articleHtml, expected) {
  if (
    expected?.schemaVersion !== LIST_STRUCTURE_SCHEMA_VERSION
    || expected?.tokenDigestMethod !== LIST_TOKEN_DIGEST_METHOD
    || !Array.isArray(expected?.events)
  ) {
    throw new TypeError('Expected list structure has an unsupported or incomplete schema');
  }
  const actual = extractListStructure(articleHtml);
  const findings = [];
  const eventCount = Math.max(expected.events.length, actual.events.length);
  for (let eventIndex = 0; eventIndex < eventCount; eventIndex += 1) {
    const wanted = expected.events[eventIndex];
    const observed = actual.events[eventIndex];
    const differingFields = wanted === undefined || observed === undefined
      ? ['event']
      : [...new Set([...Object.keys(wanted), ...Object.keys(observed)])]
        .sort()
        .filter((key) => JSON.stringify(wanted[key]) !== JSON.stringify(observed[key]));
    if (differingFields.length) findings.push({
      kind: wanted === undefined
        ? 'unexpected-list-structure-event'
        : observed === undefined
          ? 'missing-list-structure-event'
          : 'list-structure-event-mismatch',
      differingFields,
    });
  }
  return {
    actual,
    findings,
    stats: {
      expectedEvents: expected.events.length,
      actualEvents: actual.events.length,
      expectedItems: expected.events.filter(({ kind }) => kind === 'item').length,
      actualItems: actual.events.filter(({ kind }) => kind === 'item').length,
    },
  };
}

const NESTED_HTML = `
  <ol type="a">
    <li><p>Long first paragraph.</p><p>Tail.</p>
      <ul><li>Nested one</li><li>Nested two</li></ul>
    </li>
    <li value="4">Second</li>
  </ol>`;

const NESTED_EXPECTATION = observation([
  list(0, { tagName: 'ol', markerType: 'a', siblingIndex: 0 }),
  item(
    0,
    0,
    'Long first paragraph. Tail.',
    ['Long', 'first', 'paragraph', '.', 'Tail', '.'],
    { childListOccurrences: [1] },
  ),
  list(1, {
    parentListOccurrence: 0,
    parentItemOccurrence: 0,
    parentItemTokenOffset: 6,
    depth: 1,
    siblingIndex: 0,
  }),
  item(1, 1, 'Nested one', ['Nested', 'one'], {
    parentItemOccurrence: 0,
    depth: 1,
  }),
  item(2, 1, 'Nested two', ['Nested', 'two'], {
    parentItemOccurrence: 0,
    depth: 1,
    siblingIndex: 1,
  }),
  item(3, 0, 'Second', ['Second'], { siblingIndex: 1, explicitValue: 4 }),
]);

test('extracts multi-paragraph item text and nested-list membership without duplicating child text', () => {
  const { excludedSubtrees, ...bodyObservation } = extractListStructure(NESTED_HTML);
  assert.deepEqual(excludedSubtrees, []);
  assert.deepEqual(bodyObservation, NESTED_EXPECTATION);
});

test('same visible tokens fail when a short tail becomes a separate list item', () => {
  const splitTail = `
    <ol type="a">
      <li><p>Long first paragraph.</p></li><li><p>Tail.</p>
        <ul><li>Nested one</li><li>Nested two</li></ul>
      </li>
      <li value="4">Second</li>
    </ol>`;
  const audit = auditListStructure(splitTail, NESTED_EXPECTATION);
  assert.ok(audit.findings.length > 0);
  assert.equal(audit.stats.expectedItems, 4);
  assert.equal(audit.stats.actualItems, 5);
});

test('same visible tokens fail when a nested list is flattened', () => {
  const flat = `
    <ol type="a"><li><p>Long first paragraph.</p><p>Tail.</p></li></ol>
    <ul><li>Nested one</li><li>Nested two</li></ul>
    <ol type="a"><li value="4">Second</li></ol>`;
  const audit = auditListStructure(flat, NESTED_EXPECTATION);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields.includes('parentListOccurrence')
      || differingFields.includes('parentItemOccurrence')
      || differingFields.includes('depth')
  )));
});

test('distinguishes decimal, lettered, and bullet list types', () => {
  const html = '<ol><li>Decimal</li></ol><ol type="a"><li>Letter</li></ol><ul><li>Bullet</li></ul>';
  const actual = extractListStructure(html);
  assert.deepEqual(
    actual.events.filter(({ kind }) => kind === 'list').map(({ tagName, markerType }) => ({
      tagName,
      markerType,
    })),
    [
      { tagName: 'ol', markerType: '1' },
      { tagName: 'ol', markerType: 'a' },
      { tagName: 'ul', markerType: 'bullet' },
    ],
  );
  const wrongType = html.replace('<ol type="a">', '<ul>');
  const audit = auditListStructure(wrongType, actual);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields.includes('tagName') && differingFields.includes('markerType')
  )));
});

test('records blockquote, table, row, and cell occurrences in the browser-normalized DOM', () => {
  const html = `
    <blockquote><ul><li>Quoted</li></ul></blockquote>
    <table><tbody><tr><th><ol><li>Cell</li></ol></th></tr></tbody></table>`;
  const actual = extractListStructure(html);
  const listEvents = actual.events.filter(({ kind }) => kind === 'list');
  assert.deepEqual(
    listEvents.map(({ blockquoteOccurrences, tableAncestry }) => ({
      blockquoteOccurrences,
      tableAncestry,
    })),
    [
      { blockquoteOccurrences: [0], tableAncestry: [] },
      {
        blockquoteOccurrences: [],
        tableAncestry: [{
          tableOccurrence: 0,
          rowOccurrence: 0,
          cellOccurrence: 0,
          cellTagName: 'th',
        }],
      },
    ],
  );
  const moved = '<ul><li>Quoted</li></ul><ol><li>Cell</li></ol>';
  const audit = auditListStructure(moved, actual);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields?.includes('blockquoteOccurrences') || differingFields?.includes('tableAncestry')
  )));
});

test('literal duplicated markers remain visible tokens and change the item digest', () => {
  const expected = extractListStructure('<ol><li>Alpha</li></ol>');
  const audit = auditListStructure('<ol><li>1. Alpha</li></ol>', expected);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields.includes('ownTokens') && differingFields.includes('ownTokenSha256')
  )));
  assert.deepEqual(audit.actual.events[1].ownTokens, ['1', '.', 'Alpha']);
});

test('hidden items and hidden nested lists do not enter visible topology or item text', () => {
  const html = `
    <ul><li>Visible <span hidden>ghost</span>
      <ol aria-hidden="true"><li>hidden child</li></ol>
    </li><li style="display: none">hidden item</li></ul>
    <details><ul><li>closed detail</li></ul></details>`;
  const actual = extractListStructure(html);
  assert.equal(actual.events.filter(({ kind }) => kind === 'list').length, 1);
  assert.equal(actual.events.filter(({ kind }) => kind === 'item').length, 1);
  assert.equal(actual.events[1].ownText, 'Visible');
});

test('excludes and classifies only the exact renderer-owned footnotes subtree', () => {
  const html = `
    <h2 id="body-section">Body</h2><a class="pagemark" id="p-7"></a>
    <ul><li>Body item</li></ul>
    <section data-footnotes="" class="footnotes"><h2 id="footnote-label">Footnotes</h2>
      <ol><li id="user-content-fn-1">Footnote item</li></ol>
    </section>`;
  const expected = observation([
    list(0, {
      siblingIndex: 0,
      pageSpan: { startId: 'p-7', endId: 'p-7' },
      nearestPageMarkerId: 'p-7',
      nearestSectionId: 'body-section',
    }),
    item(0, 0, 'Body item', ['Body', 'item'], {
      nearestPageMarkerId: 'p-7',
      nearestSectionId: 'body-section',
    }),
  ]);
  const auditWithFootnotes = auditListStructure(html, expected);
  assert.deepEqual(auditWithFootnotes.findings, []);
  const actual = auditWithFootnotes.actual;
  assert.equal(actual.events.filter(({ kind }) => kind === 'list').length, 1);
  assert.equal(actual.events[1].ownText, 'Body item');
  assert.deepEqual(actual.excludedSubtrees, [{
    kind: 'renderer-footnotes',
    occurrence: 0,
    listCount: 1,
    itemCount: 1,
    nearestPageMarkerId: 'p-7',
    nearestSectionId: 'body-section',
  }]);

  const impostor = html.replace(
    '<section data-footnotes="" class="footnotes">',
    '<section data-footnotes="" class="footnotes" id="authored-impostor">',
  );
  const audit = auditListStructure(impostor, expected);
  assert.ok(audit.findings.some(({ kind }) => kind === 'unexpected-list-structure-event'));
  assert.equal(audit.actual.events.filter(({ kind }) => kind === 'list').length, 2);
});

test('page and section identity defeat hidden-list substitution elsewhere', () => {
  const expectedHtml = `
    <h2 id="required-section">Required</h2><a class="pagemark" id="p-3"></a>
    <ul><li>Same item</li></ul>
    <h2 id="other-section">Other</h2><a class="pagemark" id="p-4"></a>`;
  const substitutedHtml = `
    <h2 id="required-section">Required</h2><a class="pagemark" id="p-3"></a>
    <ul hidden><li>Same item</li></ul>
    <h2 id="other-section">Other</h2><a class="pagemark" id="p-4"></a>
    <ul><li>Same item</li></ul>`;
  const expected = extractListStructure(expectedHtml);
  assert.deepEqual(
    expected.events.map(({ nearestPageMarkerId, nearestSectionId }) => ({
      nearestPageMarkerId,
      nearestSectionId,
    })),
    [
      { nearestPageMarkerId: 'p-3', nearestSectionId: 'required-section' },
      { nearestPageMarkerId: 'p-3', nearestSectionId: 'required-section' },
    ],
  );
  const audit = auditListStructure(substitutedHtml, expected);
  assert.equal(audit.stats.actualEvents, audit.stats.expectedEvents);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields?.includes('nearestPageMarkerId')
      && differingFields.includes('nearestSectionId')
  )));
});

test('same-depth blockquote and table-cell substitutions retain occurrence identity', () => {
  const expectedHtml = `
    <blockquote><ul><li>Quote item</li></ul></blockquote><blockquote></blockquote>
    <table><tr><td><ol><li>Cell item</li></ol></td><td></td></tr></table>`;
  const substitutedHtml = `
    <blockquote></blockquote><blockquote><ul><li>Quote item</li></ul></blockquote>
    <table><tr><td></td><td><ol><li>Cell item</li></ol></td></tr></table>`;
  const expected = extractListStructure(expectedHtml);
  const actualLists = extractListStructure(substitutedHtml).events.filter(({ kind }) => kind === 'list');
  assert.deepEqual(actualLists[0].blockquoteOccurrences, [1]);
  assert.equal(actualLists[1].tableAncestry[0].rowOccurrence, 0);
  assert.equal(actualLists[1].tableAncestry[0].cellOccurrence, 1);
  const audit = auditListStructure(substitutedHtml, expected);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields?.includes('blockquoteOccurrences')
  )));
  assert.ok(audit.findings.some(({ differingFields }) => differingFields?.includes('tableAncestry')));
});

test('malformed wrapper ancestry cannot masquerade as a direct list item', () => {
  const expected = extractListStructure('<ul><li>Item</li></ul>');
  const audit = auditListStructure('<ul><div><li>Item</li></div></ul>', expected);
  assert.equal(audit.stats.actualEvents, audit.stats.expectedEvents);
  assert.deepEqual(audit.actual.events[1].listChildPath, ['div']);
  assert.ok(audit.findings.some(({ differingFields }) => differingFields?.includes('listChildPath')));
});

test('child-list token offset preserves Lead/list/Tail interleaving', () => {
  const expectedHtml = `
    <ul><li><p>Lead</p><ol><li>Child</li></ol><p>Tail</p></li></ul>`;
  const movedHtml = `
    <ul><li><p>Lead</p><p>Tail</p><ol><li>Child</li></ol></li></ul>`;
  const expected = extractListStructure(expectedHtml);
  assert.equal(expected.events[2].parentItemTokenOffset, 1);
  const audit = auditListStructure(movedHtml, expected);
  assert.equal(audit.actual.events[1].ownText, expected.events[1].ownText);
  assert.deepEqual(audit.actual.events[1].ownTokens, expected.events[1].ownTokens);
  assert.equal(audit.actual.events[2].parentItemTokenOffset, 2);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields?.includes('parentItemTokenOffset')
  )));
});

test('item marker ownership catches moving p44 from the first item to between items', () => {
  const expectedHtml = `
    <a class="pagemark" id="p-43"></a>
    <ul><li>Lead <a class="pagemark" id="p-44"></a> tail</li><li>Second</li></ul>`;
  const movedHtml = `
    <a class="pagemark" id="p-43"></a>
    <ul><li>Lead tail</li><a class="pagemark" id="p-44"></a><li>Second</li></ul>`;
  const expected = extractListStructure(expectedHtml);
  assert.deepEqual(expected.events[0].descendantPageMarkers, [{ id: 'p-44' }]);
  assert.deepEqual(expected.events[0].pageSpan, { startId: 'p-43', endId: 'p-44' });
  assert.deepEqual(expected.events[1].ownPageMarkers, [{ id: 'p-44', tokenOffset: 1 }]);

  const audit = auditListStructure(movedHtml, expected);
  assert.deepEqual(audit.actual.events[0].descendantPageMarkers, [{ id: 'p-44' }]);
  assert.deepEqual(audit.actual.events[0].pageSpan, { startId: 'p-43', endId: 'p-44' });
  assert.deepEqual(audit.actual.events[1].ownPageMarkers, []);
  assert.equal(audit.actual.events[1].ownText, expected.events[1].ownText);
  assert.ok(audit.findings.some(({ differingFields }) => (
    differingFields?.includes('ownPageMarkers')
  )));
});

test('rejects expectations that are not an explicit supported observation', () => {
  assert.throws(
    () => auditListStructure('<ul><li>x</li></ul>', { events: [] }),
    /unsupported or incomplete schema/,
  );
});
