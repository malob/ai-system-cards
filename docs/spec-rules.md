# Living spec rules

The accumulated issue-type decisions (D2): the owner decides each type once,
it's recorded here, and the judge model applies matching cases automatically —
escalating only types with no rule. Append new rules; supersede, don't rewrite.
Universal rules (any card) live here; card-specific signal mappings live in
that card's `style-manifest.yaml`.

## R1 — PDF auto-links render as plain text/code (decided 2026-06-09, owner)

Google Docs auto-attaches link annotations to URL-shaped strings (signature:
`http://` scheme and the anchor text is the URL itself). These are data, not
navigation — e.g. the §9.2 HLE blocklist tables (source pp. 318–319). Render
as plain text/code exactly as styled; record the annotation as provenance.
Verifier: L1 classifies these as the minor `auto-link` class, never missing
links. (Decided on the Fable 5 card, 2026-06-10 conversation; applies to any
Google-Docs-exported PDF.)

## R2 — Unresolvable internal destinations stay plain text (PROPOSED, default in effect)

When the source PDF's own named destination doesn't resolve (e.g. the
`h.6c8a0mx55isl` links on p.100 — a Google Docs export defect), the output
cannot link to nowhere: render the anchor as plain text. Verifier: L1 class
`source-defect-unresolvable-dest` (minor, reported). Open question for the
owner, non-blocking: whether the canonical web edition should *annotate* such
source defects (a discreet sic-style note) — D17 presentation territory.
