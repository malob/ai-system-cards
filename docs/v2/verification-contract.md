# Verification contract

The spine of v2 (charter principle 1): every way the output can be wrong is mapped
to the mechanism that catches it. Invariant IDs are stable and referenced from
experiments, code, and the decision log. The oracle for all mechanical checks is
the structure-aware extraction (brief §4.1); where the extractor is the weak link,
that's noted, and the bake-off (experiment 02) is what firms it up.

## Operating rules

1. **Gates block; advisors direct.** A gate failure stops the unit from advancing
   — the loop repairs and re-checks. An advisor flag routes attention (arbiter,
   judge, or human); advisor silence proves nothing (D8).
2. **A human-found defect with no failing invariant is a process bug.** The fix
   isn't complete until an invariant (or living-spec rule) would catch the next
   instance (charter P1).
3. **Fidelity, not correctness.** When source and output disagree, the PDF wins.
   When the PDF itself is wrong (typo, bad cross-reference), we reproduce it
   faithfully — the contract verifies fidelity. (Annotating sic-style corrections
   is a renderer/policy question, out of scope here.)
4. **Every exclusion is declared.** Any source content not subject to T-series
   equality (headers/footers, TOC pages, figure-internal text) is enumerated in a
   versioned exclusion list with a rationale, and the *derivation* of repeating
   exclusions (e.g. running footers) is itself checked for consistency.
5. **Every normalization is allowlisted.** Text comparisons run under an explicit,
   versioned allowlist (§ Normalization). Anything not listed is a difference.
6. **Closure: no unexplained signals (D16).** Every recurring distinctive visual
   signal in the source (fill color, text color, box geometry, font shift) must
   be explained by an entry in the card's **style manifest** — the per-card data
   file mapping signals to semantic roles, seeded by the signal census
   (experiment 03) and confirmed by the owner. An unmapped signal is a flag, not
   a pass-through. S2 and N1 read their vocabularies from the manifest; nothing
   about a specific vendor's idioms is hardcoded in the invariants.

## Invariants

### T — Text (gates)

- **T1 — Bidirectional token-stream equality.** The model's text projection equals
  the source text layer: no omissions (source→output) and no additions
  (output→source; CA-01 — v1 only ever checked the first direction). Typed fields
  that are legitimately not source text (figure alt text, slugs/ids) are excluded
  *by type*, not by pattern.
- **T2 — Order.** T1 is sequence-sensitive (alignment diff, not set membership):
  reading order must match the oracle's. Where the extractor's reading order is
  unreliable on a page, the page is flagged to N1 rather than silently trusted.

### L — Links (gates)

- **L1 — Link-set equality per page.** Every `/URI` *and* `/GoTo` annotation in
  the source has a corresponding link node matched on anchor text + target
  (URI string, or resolved internal destination), and vice versa. (FL-01: v1
  silently dropped all 111 internal links.)
- **L2 — Destination resolution.** Every internal link resolves to an existing
  anchor in the output; every anchor id is unique (also covers PM-06).

### S — Styling (gates, extractor-dependent)

- **S1 — Bold/italic run equality.** Style runs from span flags match the model's
  emphasis marks, modulo *typed* conversions (a bold run consumed by a heading,
  chip, or turn label is accounted for, never silently dropped). (FL-04.)
- **S2 — Colored-signal coverage.** Every chip-pill background fill (pill-sized
  filled rect behind a text span — experiment 02: the *fill* color carries the
  registry color; chip text color is just contrast) and every non-body-color text
  span maps to a typed node that explains it (chip, link, heading style,
  transcript commentary, highlight); none flattened to plain text (FL-02, FL-07).
- **S3 — Chip vocabulary.** Every chip label ∈ the per-card registry
  (`meta.yaml` chips) and each label has exactly one color document-wide.
  (Categorization quality — *which* label — is N1's problem.)

### TB — Tables

- **TB1 — Presence and shape (gate).** Table count per page matches; row/col
  counts and span structure match the oracle where the extractor provides reliable
  structure. Cell *text* is already covered by T1; cell *assignment* is what TB1
  adds. If the bake-off shows extractor table structure is weak (merged cells!),
  TB1 degrades to advisor + N-version for affected tables — declared per table,
  never silently.

### F — Figures (gates)

- **F1 — Placement.** Every extracted figure image appears exactly once, anchored
  at its bbox position in reading order (PM-05's root). Alt text present
  (quality → V1/N1).
- **F2 — Captions.** Caption text and styling are covered by T1/S1; F2 adds the
  *association* — each caption attached to the right figure node.

### FN — Footnotes (gates)

- **FN1 — Anchors and bodies.** Footnote-reference count, anchor positions
  (superscript spans in the oracle), and body text all present and matched; no
  orphaned refs or bodies.

### P — Provenance (gates)

- **P1 — Page map.** Page provenance covers 1..N exactly once each (no gaps, no
  duplicates; declared exclusions like TOC pages are listed, not hardcoded),
  and each node's page assignment is consistent with the oracle's span offsets.
  (Replaces the entire v1 page-marker class PM-01…07, which the typed model
  eliminates by construction — P1 checks the construction.)

### SC — Schema and projection (gates)

- **SC1 — Model validity.** The typed document tree validates against the schema
  (makes FL-06/PM-07 impossible).
- **SC2 — Projection health.** All serializers (HTML, card.md, llms.txt) run
  clean; HTML passes structural lint (unique ids, no empty paragraphs, no
  unparsed directive text).

### N — Semantic judgment (no exact oracle; D7 machinery)

- **N1 — N-version agreement.** For judgment calls — transcript-turn boundaries
  (FL-03; experiment 02 found a strong mechanical prior: narrator commentary is
  gray `#444444` vs body-black turn text, so N1 arbitrates residual ambiguity
  rather than working unaided), chip categorization, heading-vs-bold,
  blockquote-vs-example, reading-order repair — N independent proposals are
  tree-diffed. Agreement =
  accept; disagreement → arbiter with page image; arbiter uncertainty → H1.
  Every generator also emits a structured uncertainty log; logged uncertainties
  route to the judge regardless of agreement.

### V — Visual (advisor; promotion path per D8)

- **V1 — Page-level visual diff.** A fresh vision model compares each rendered
  page region against the PDF page image and enumerates discrepancies with
  severity. Advisor until mutation-tested recall (D6) and cross-card track record
  justify gate status.

### H — Human (the bounded remainder)

- **H1 — Escalation worklist.** Novel issue-types (per D2's judge), arbiter
  deadlocks, and high-severity V1 flags. Each resolution becomes a living-spec
  rule.
- **H2 — Acceptance review.** Flag-directed review plus a random page sample
  sized by measured verifier recall. This is the owner's *entire* required
  surface.

## Normalization allowlist (v0 — grows by appending, each entry with rationale)

| id | transform                                   | rationale                                  |
|----|---------------------------------------------|--------------------------------------------|
| A1 | join end-of-line/page hyphenation           | layout artifact, not content               |
| A2 | collapse runs of whitespace                 | layout artifact                            |
| A3 | expand ligatures (ﬁ→fi, ﬂ→fl, …)            | font artifact in text layer                |
| A4 | drop soft hyphens / zero-width chars        | invisible artifacts                        |

Explicitly **not** normalized: quote style (curly stays curly — FL-05 is solved by
fidelity, not render patching), dashes, unicode beyond NFC. Mojibake (CA-02) must
fail T1.

## Exclusion list (v0)

- Running headers/footers and bare page numbers (derived per-card; derivation
  checked for cross-page consistency).
- PDF TOC pages (the site generates its own TOC) — declared per card in metadata.
- Figure-internal text (charts stay images) — bounded by figure bboxes; any text
  *outside* declared figure bboxes is in scope for T1.

## Traceability: catalog → invariants

| defect          | caught by         | defect    | caught by      |
|-----------------|-------------------|-----------|----------------|
| PM-01…05        | P1 (by construction + check) | FL-04     | S1             |
| PM-06           | L2, P1            | FL-05     | T1 (no-normalize rule) |
| PM-07           | SC1               | FL-06     | SC1            |
| FL-01           | L1, L2            | CA-01     | T1 (output→source direction) |
| FL-02           | S2, S3            | CA-02     | T1             |
| FL-03           | N1, V1            | RN-01/02  | SC2, V1        |
| PR-01…03        | process: D2/D4/D7 (in-loop, staged, spec) |  |                |

## Calibration status

Every invariant carries a status; this section is updated as experiments land.
Target: each gate **mutation-tested** with per-class recall (D6) and, where
applicable, **calibrated** against the v1 corpus (experiment 01 refs).

As of 2026-06-09 (experiment 02 part 1, PyMuPDF probe on 11 pages):

- **Signal-feasible:** L1/L2 (URI+GoTo exact on probe pages: 23/23, 26/26, 1/1),
  S1 (bold/italic flags incl. caption leads), S2 (chip fills — signal amended),
  FN1 (superscript flag), F1 (image counts exact), P1 (page-anchored by
  construction).
- **TB1 signal-feasible via docling** (2026-06-10, experiment 02 part 2): merged
  cells structurally exact, zero false-positive tables on probe pages. Extraction
  stack settled as D14 (PyMuPDF oracle + docling tables + LLM semantics).
- **T2:** block order corroborated by docling; prose segmentation stays anchored
  to the PyMuPDF span stream (docling's paragraph merging is too mushy to gate on).
- **No invariant is yet implemented, calibrated, or mutation-tested.**
