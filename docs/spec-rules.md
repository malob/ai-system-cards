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

## R2 — A broken named destination needs an independently recoverable identity (decided 2026-08-15)

When the source PDF's own named destination does not resolve, the output must
never emit an empty `href="#"`. If the anchor printed in the source uniquely
identifies exactly one accepted source heading — for example the literal
section number `6.5.4.3` — the web edition may recover that link mechanically,
and L2 must verify the recovered identity. Otherwise render the anchor as plain
text. In both cases L1 reports the publisher's broken destination as the minor
`source-defect-unresolvable-dest` class; a recovery is not permission to hide
the source defect.

This supersedes the proposed all-plain-text wording: it keeps the defensible
plain-text outcome for prose anchors such as Fable's broken
`h.6c8a0mx55isl` link while making the already-mechanical, unambiguous
`6.5.4.3` recovery an explicit rule rather than an accidental exception.
Whether to add a visible *sic*-style annotation remains a separate D17
presentation question.
