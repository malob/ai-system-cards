// Independent checks over the HTML that is inserted into <article>. This
// deliberately consumes serialized HTML instead of the Markdown/HAST producer
// tree: parse5 applies the same HTML5 tree-building rules a browser uses (for
// example, foster-parenting invalid content around tables).
import { parse, parseFragment } from 'parse5';

function attribute(node, name) {
  return node.attrs?.find((candidate) => candidate.name === name)?.value;
}

function hasAttribute(node, name) {
  return node.attrs?.some((candidate) => candidate.name === name) ?? false;
}

function hasClass(node, name) {
  return (attribute(node, 'class') ?? '').split(/\s+/).includes(name);
}

function textOf(node) {
  if (node.nodeName === '#text') return node.value;
  return (node.childNodes ?? []).map(textOf).join('');
}

function normalizedText(node) {
  return textOf(node).replace(/\s+/g, ' ').trim();
}

function fragmentTarget(href) {
  if (!href.startsWith('#')) return null;
  const fragment = href.slice(1);
  if (!fragment) return '';
  try {
    return decodeURIComponent(fragment);
  } catch {
    return undefined;
  }
}

/**
 * Parse rendered article HTML into the small, JSON-safe observation model used
 * by both the projection audit and future source-to-DOM L2 expectations.
 * `internalLinks[].index` is the zero-based order of `<a href="#…">` elements
 * in the browser-normalized article tree.
 */
function inspectTree(root) {
  const elements = [];
  const headings = [];
  const internalLinks = [];
  const authoredInternalLinks = [];

  const walk = (node, ancestors = []) => {
    if (node.tagName) {
      const id = attribute(node, 'id');
      const element = {
        tagName: node.tagName,
        id: id ?? null,
        text: normalizedText(node),
        offset: node.sourceCodeLocation?.startOffset ?? null,
      };
      elements.push(element);

      if (/^h[1-6]$/.test(node.tagName)) headings.push(element);

      if (node.tagName === 'a') {
        const href = attribute(node, 'href');
        if (href?.startsWith('#')) {
          let rendererGenerated = null;
          if (hasClass(node, 'hanchor')) {
            rendererGenerated = 'heading-self-link';
          } else if (hasAttribute(node, 'data-footnote-ref')) {
            rendererGenerated = 'footnote-reference';
          } else if (hasAttribute(node, 'data-footnote-backref')) {
            rendererGenerated = 'footnote-backlink';
          } else if (ancestors.some((parent) => parent.tagName === 'sup' && hasClass(parent, 'fn-html'))) {
            rendererGenerated = 'raw-table-footnote-reference';
          }
          const link = {
            index: internalLinks.length,
            authoredLinkIndex: rendererGenerated ? null : authoredInternalLinks.length,
            href,
            targetId: fragmentTarget(href),
            text: element.text,
            className: attribute(node, 'class') ?? '',
            rendererGenerated,
            relocatedFootnote: ancestors.some(
              (parent) => parent.tagName === 'section'
                && (hasAttribute(parent, 'data-footnotes') || hasClass(parent, 'footnotes')),
            ),
            offset: element.offset,
          };
          internalLinks.push(link);
          if (!rendererGenerated) authoredInternalLinks.push(link);
        }
      }
    }
    const nextAncestors = node.tagName ? [...ancestors, node] : ancestors;
    for (const child of node.childNodes ?? []) walk(child, nextAncestors);
  };
  walk(root);

  const ids = new Map();
  for (const element of elements) {
    if (!element.id) continue;
    const occurrences = ids.get(element.id) ?? [];
    occurrences.push(element);
    ids.set(element.id, occurrences);
  }

  return {
    elements,
    headings,
    internalLinks,
    authoredInternalLinks,
    ids: [...ids].map(([id, occurrences]) => ({ id, occurrences })),
  };
}

export function inspectArticleHtml(html) {
  return inspectTree(parseFragment(html, { sourceCodeLocationInfo: true }));
}

export function inspectPageHtml(html) {
  return inspectTree(parse(html, { sourceCodeLocationInfo: true }));
}

function expectationLink(model, expectation) {
  const hasIndex = Number.isInteger(expectation.linkIndex);
  const hasAuthoredIndex = Number.isInteger(expectation.authoredLinkIndex);
  const hasText = typeof expectation.linkText === 'string';
  if (Number(hasIndex) + Number(hasAuthoredIndex) + Number(hasText) !== 1) {
    throw new TypeError(
      'Each expected target needs exactly one of linkIndex, authoredLinkIndex, or linkText',
    );
  }
  if (hasIndex) return model.internalLinks[expectation.linkIndex];
  if (hasAuthoredIndex) return model.authoredInternalLinks[expectation.authoredLinkIndex];

  const wanted = expectation.linkText.replace(/\s+/g, ' ').trim();
  const matches = model.internalLinks.filter((link) => link.text === wanted);
  const occurrence = expectation.occurrence ?? 0;
  if (!Number.isInteger(occurrence) || occurrence < 0) {
    throw new TypeError('Expected target occurrence must be a non-negative integer');
  }
  return matches[occurrence];
}

/**
 * Audit final article-DOM link integrity.
 *
 * `expectedTargets` is the seam for the independent source/accepted-heading
 * lane. Each entry names the expected target ID and locates the rendered link
 * by `authoredLinkIndex` after renderer-generated navigation is filtered.
 * `linkIndex`, or `linkText` plus an optional duplicate-text `occurrence`, are
 * retained for focused diagnostics. Existence-only checks cannot detect a link
 * repointed to another real heading; an expectation produces
 * `unexpected-target` for that case.
 */
function auditModel(model, { expectedTargets = [], requireHeadingIds = true } = {}) {
  const findings = [];
  const ids = new Map(model.ids.map(({ id, occurrences }) => [id, occurrences]));

  if (requireHeadingIds) {
    for (const heading of model.headings) {
      if (!heading.id) {
        findings.push({
          kind: 'heading-without-id',
          tagName: heading.tagName,
          text: heading.text,
          offset: heading.offset,
        });
      }
    }
  }

  for (const [id, occurrences] of ids) {
    if (occurrences.length <= 1) continue;
    findings.push({
      kind: 'duplicate-id',
      id,
      count: occurrences.length,
      headingCount: occurrences.filter(({ tagName }) => /^h[1-6]$/.test(tagName)).length,
      tags: occurrences.map(({ tagName }) => tagName),
    });
  }

  for (const link of model.internalLinks) {
    if (link.targetId === '') {
      findings.push({
        kind: 'empty-target',
        linkIndex: link.index,
        href: link.href,
        text: link.text,
        offset: link.offset,
      });
      continue;
    }
    if (link.targetId === undefined) {
      findings.push({
        kind: 'malformed-target',
        linkIndex: link.index,
        href: link.href,
        text: link.text,
        offset: link.offset,
      });
      continue;
    }
    const targets = ids.get(link.targetId) ?? [];
    if (!targets.length) {
      findings.push({
        kind: 'missing-target',
        linkIndex: link.index,
        href: link.href,
        targetId: link.targetId,
        text: link.text,
        offset: link.offset,
      });
    } else if (targets.length > 1) {
      findings.push({
        kind: 'ambiguous-target',
        linkIndex: link.index,
        href: link.href,
        targetId: link.targetId,
        count: targets.length,
        text: link.text,
        offset: link.offset,
      });
    }
  }

  for (const expectation of expectedTargets) {
    if (typeof expectation.targetId !== 'string' || !expectation.targetId) {
      throw new TypeError('Each expected target needs a non-empty targetId');
    }
    const link = expectationLink(model, expectation);
    let locator;
    if (Number.isInteger(expectation.linkIndex)) {
      locator = { linkIndex: expectation.linkIndex };
    } else if (Number.isInteger(expectation.authoredLinkIndex)) {
      locator = { authoredLinkIndex: expectation.authoredLinkIndex };
    } else {
      locator = { linkText: expectation.linkText, occurrence: expectation.occurrence ?? 0 };
    }
    if (!link) {
      findings.push({
        kind: 'expected-link-missing',
        key: expectation.key ?? null,
        ...locator,
        expectedTargetId: expectation.targetId,
      });
    } else if (link.targetId !== expectation.targetId) {
      findings.push({
        kind: 'unexpected-target',
        key: expectation.key ?? null,
        linkIndex: link.index,
        authoredLinkIndex: link.authoredLinkIndex,
        text: link.text,
        href: link.href,
        expectedTargetId: expectation.targetId,
        actualTargetId: link.targetId ?? null,
      });
    }
  }

  return { model, findings };
}

export function auditArticleHtml(html, { expectedTargets = [] } = {}) {
  return auditModel(inspectArticleHtml(html), { expectedTargets, requireHeadingIds: true });
}

/** Audit global ID uniqueness and every fragment href in a complete built page. */
export function auditPageHtml(html) {
  return auditModel(inspectPageHtml(html), { requireHeadingIds: false });
}
