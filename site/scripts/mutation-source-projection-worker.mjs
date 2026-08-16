#!/usr/bin/env node
// Persistent JSONL bridge for Python mutation runs. Authority, renderer
// modules, and PNG metadata are loaded once; every request still supplies the
// complete exact section corpus to render.
import { createInterface } from 'node:readline';

import {
  auditSourceProjectionSections,
  loadSourceProjectionAuthority,
} from '../src/lib/source-projection.js';

function abort(message) {
  process.stderr.write(`mutation source projection: ${message}\n`);
  process.exit(2);
}

const cardAt = process.argv.indexOf('--card');
const cardId = cardAt >= 0 ? process.argv[cardAt + 1] : null;
if (typeof cardId !== 'string' || !/^[a-z0-9][a-z0-9-]*\/[a-z0-9][a-z0-9-]*$/.test(cardId)) {
  abort('--card must name one canonical vendor/slug');
}
const [vendor, slug] = cardId.split('/');
let authority;
try {
  authority = loadSourceProjectionAuthority(vendor, slug);
} catch (error) {
  abort(error?.stack ?? String(error));
}

const lines = createInterface({ input: process.stdin, crlfDelay: Infinity });
for await (const line of lines) {
  let request;
  try {
    request = JSON.parse(line);
    if (
      request === null
      || typeof request !== 'object'
      || Array.isArray(request)
      || !Number.isSafeInteger(request.id)
      || request.id < 1
    ) throw new TypeError('request.id must be a positive integer');
    const audit = await auditSourceProjectionSections({
      vendor,
      slug,
      sections: request.sections,
      authority,
    });
    // HTML is intentionally not returned over JSONL: findings and stats are
    // the authority result, while retaining a multi-megabyte rendered string
    // per mutation would only add transport and GC cost.
    const { findings, stats } = audit;
    process.stdout.write(`${JSON.stringify({ id: request.id, findings, stats })}\n`);
  } catch (error) {
    const id = Number.isSafeInteger(request?.id) ? request.id : null;
    const message = error?.message ?? String(error);
    if (error?.code === 'BROWSER_HIDDEN_AUTHORED_CONTENT' && error?.finding) {
      process.stdout.write(`${JSON.stringify({
        id,
        findings: [error.finding],
        stats: {
          requiredPages: authority.requiredPages.length,
          requiredFigures: authority.requiredFigures.length,
        },
      })}\n`);
    } else if ([
      'Authored HTML cannot cross the article boundary',
      'Authored HTML contains active or reserved projection markup',
    ].includes(message)) {
      // A policy rejection is successful detection, not an infrastructure
      // outage. Emit it in the same findings channel so Python can normalize
      // it into blocking P2/F3 evidence. Browser-hidden authored content has
      // its own structured V1 finding and is returned by the audit normally.
      process.stdout.write(`${JSON.stringify({
        id,
        findings: [{ kind: 'render-rejected', reason: message }],
        stats: {
          requiredPages: authority.requiredPages.length,
          requiredFigures: authority.requiredFigures.length,
        },
      })}\n`);
    } else {
      process.stdout.write(`${JSON.stringify({ id, error: error?.stack ?? String(error) })}\n`);
    }
  }
}
