# Verification contract

The spine of v2 (charter principle 1): every way the output can be wrong is mapped
to the mechanism that catches it. Invariant IDs are stable and referenced from
experiments, code, and the decision log. The oracle for all mechanical checks is
the structure-aware extraction (brief §4.1); where the extractor is the weak link,
that's noted, and the bake-off (experiment 02) is what firms it up.

This file is both a defect-catcher catalog and an implementation ledger. The
invariant descriptions state the intended ownership boundary; **Calibration status**
at the end says which boundaries are executable today. The pre-build canonical-JSON,
N-version, and automated vision design was not implemented as written: the built
pipeline mechanically assembles transient typed blocks and serializes `sections/*.md`
directly, with independent agent sweeps for the non-mechanical layer (D50).

## Operating rules

1. **Gates block; advisors direct.** A gate failure stops the unit from advancing
   — the loop repairs and re-checks. An advisor flag routes attention to the
   inspection/orchestrator/owner loop; advisor silence proves nothing (D8).
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
   a pass-through. S2 reads the manifest's chip colors/labels; broader signal
   closure is census- and inspection-owned because N1 did not ship. Nothing about
   a specific vendor's idioms is hardcoded in the invariants.

## Invariants

### T — Text (gates)

- **T1 — Bidirectional token-stream equality.** The markdown text projection equals
  the source text layer: no omissions (source→output) and no additions
  (output→source — v1 only ever checked the first direction; additions are a
  real failure mode even though the one cataloged instance, CA-01, was later
  retracted). Projection-known fields that are legitimately not source text
  (figure alt text, slugs/ids) are excluded by construct, not an arbitrary text
  allowlist.
- **T2 — Order.** T1 is sequence-sensitive (alignment diff, not set membership):
  reading order is compared with the oracle's. A paired same-text insertion/deletion
  within ±2 pages becomes a minor displacement; where extraction order is unreliable,
  all T1 differences on the table spill set (each table-attributed page plus adjacent
  pages) are also minors. TB2 plus the inspection sweeps own those residuals.

### L — Links (gates)

- **L1 — Source-link coverage.** The current gate counts source `/URI`
  occurrences by target across the whole document and requires at least that many
  matching markdown targets. For `/GoTo`, it requires each normalized source anchor
  text to occur among the markdown link texts. This is source→output coverage, not
  per-page/bidirectional link equality: it does not reject output-only links, bind a
  URI occurrence to its source anchor/page, or verify a GoTo link's output target.
  (FL-01: v1 silently dropped all 111 internal links.)
- **L2 — Destination resolution.** Every internal link resolves to an existing
  anchor in the output; every anchor id is unique (also covers PM-06). The current
  generator resolves destinations mechanically, but exact output-anchor/destination
  resolution is covered by the site/link audit rather than a separately emitted
  `L2` verifier flag.

### S — Styling (gates, extractor-dependent)

- **S1 — Source bold-run coverage.** Qualifying bold body-text runs from the PDF
  must appear as markdown bold, a heading, or a turn label. The current check is
  source→output only and skips the entire table spill set (table-attributed pages
  plus adjacent pages); italic and output-only emphasis are not mechanically gated.
  (FL-04.)
- **S2 — Chip-pill coverage.** Every pill whose fill is one of the manifest's chip
  colors must have a matching `:chip[...]` label. Other non-body-color text and
  visual signals remain manifest/sweep concerns rather than emitted S2 checks
  (FL-02, FL-07).
- **S3 — Chip vocabulary.** Every markdown chip label must occur in the per-card
  `style-manifest.yaml` chip registry. The label→color mapping is configuration;
  S3 checks membership, not rendered color equality. (Categorization quality —
  *which* label — is inspection-owned.)

### ST — Token-preserving structure (gates)

- **ST1 — List-item presence.** Layout-derived source list-marker counts must be
  represented by markdown list items.
- **ST2 — Block-start integrity.** A markdown block may not begin in the middle of
  a source line; this catches wrapped items or paragraphs split without token loss.
- **ST3 — Heading integrity.** Each layout-derived heading line group must serialize
  as one complete markdown heading.

### TB — Tables

- **TB1 — Presence and shape (design target; inspection-owned today).** The intended
  boundary is per-page table count plus row/column/span structure. No `TB1` flag is
  emitted today: docling supplies generation candidates, T1 covers cell text, TB2
  covers a class of cell-order damage, and the sweeps/owner inspect table shape,
  merged cells, and assignment.
- **TB2 — Cell order integrity (gate for single-page tables; advisor for
  seam-merged, 2026-08-14, owner-requested).** Every md table cell's text
  (squashed: tags/refs/quotes/whitespace/hyphens dropped) must appear as a
  CONTIGUOUS run of its page's span streams (reading order, x0 columns, and
  all-pairs column-edge intervals; ±1-page one-cut split for seam cells). A
  scrambled/flipped cell — invisible to T1's table-zone demotion — cannot.
  Calibrated 2026-08-14: 0 false flags on all three cards' certified tables;
  known recall limit: a scramble whose flipped form coincides with adjacent
  REPEATED rows ('MonitorBench Hard (n=60 sample) + …' neighborhoods)
  streams as contiguous and escapes — the layer-2 sweeps remain the catcher
  for that shape.

### F — Figures (gates)

- **F1 — Figure-count coverage.** Per-page extracted-figure counts are compared
  with markdown image counts plus declared `figure ... skipped` comments; a pure
  ±1-page count shift is a minor. The gate does not compare image identity,
  bbox/reading-order placement, or alt text; those remain inspection-owned.
- **F2 — Captions (inspection-owned today).** Caption text and styling are covered
  by T1/S1; association with the right figure is checked in the page sweeps.

### FN — Footnotes (gates)

- **FN1 — References and bodies.** The gate compares document-wide reference
  counts, requires each markdown reference to have a definition in its section,
  and compares body text per footnote number. Body-text mismatches are advisory
  minors until oracle boundaries harden; superscript positions are not compared.
  Declared source-orphan references are reported as minors.

### P — Provenance (gates)

- **P1 — Page-map coverage.** Every expected non-cover/non-TOC page must be
  represented by either a section start or a serialized page marker, and duplicate
  serialized markers are majors. The current gate does not reject unexpected
  markers, compare marker order, or treat a marker that repeats an implicit section
  start as a duplicate. Page-local checks provide the practical attribution backstop.

### SC — Schema and projection (pre-build design target)

- **SC1 — Model validity.** The planned canonical JSON tree/schema did not ship;
  transient block dictionaries feed the markdown serializer directly.
- **SC2 — Projection health.** The clean Astro/Pagefind production build exercises
  HTML, `card.md`, and `llms.txt`; structural link/DOM inspection remains in the
  sweep layer rather than a named `SC2` Python invariant.

### N — Semantic judgment (pre-build design target; replaced in practice)

- **N1 — N-version agreement.** The planned mechanism for judgment calls — transcript-turn boundaries
  (FL-03; experiment 02 found a strong mechanical prior: narrator commentary is
  gray `#444444` vs body-black turn text, so N1 arbitrates residual ambiguity
  rather than working unaided), chip categorization, heading-vs-bold,
  blockquote-vs-example, reading-order repair — N independent proposals are
  tree-diffed. Agreement =
  accept; disagreement → arbiter with page image; arbiter uncertainty → H1.
  Every generator would also emit a structured uncertainty log. This machinery was
  not used in the built converter; the rulebook-driven agent sweeps and owner
  adjudication now own these calls.

### V — Visual (pre-build advisor target; not shipped)

- **V1 — Page-level visual diff.** The planned automated advisor would compare each
  rendered page region against the PDF page image and enumerate discrepancies. It
  did not ship as a standing tool; independent page/markdown/DOM sweeps and the
  owner scroll are the implemented visual layer.

### H — Human (the bounded remainder)

- **H1 — Escalation worklist.** Novel issue-types and uncertain or high-severity
  sweep findings route to the orchestrator/owner. Resolutions become living-spec or
  pipeline rules; no judge-model/arbiter service is present in the shipped loop.
- **H2 — Acceptance review.** Flag-directed review plus the mandatory owner scroll.
  Exact accepted majors are recorded by full finding fingerprint; recurring blind
  spots determine the sweep/control sample rather than being inferred from a single
  aggregate recall percentage.

## Normalization allowlist (v0 — grows by appending, each entry with rationale)

| id | transform                                   | rationale                                  |
|----|---------------------------------------------|--------------------------------------------|
| A1 | join end-of-line/page hyphenation           | layout artifact, not content               |
| A2 | collapse runs of whitespace                 | layout artifact                            |
| A3 | expand ligatures (ﬁ→fi, ﬂ→fl, …)            | font artifact in text layer                |
| A4 | drop soft hyphens / zero-width chars        | invisible artifacts                        |
| A5 | drop list bullet glyphs from token streams  | list structure is checked separately by ST |

Explicitly **not** normalized: quote style (curly stays curly — FL-05 is solved by
fidelity, not render patching), dashes, unicode beyond NFC. Mojibake (CA-02) must
fail T1.

## Exclusion list (v0)

- Running headers/footers and bare page numbers (derived per-card; derivation
  checked for cross-page consistency).
- PDF TOC pages (the site generates its own TOC) — declared per card in metadata.
- Raster-internal chart text remains pixels in the retained image and therefore has
  no PDF text-layer spans to compare. Text-layer overlays are not excluded merely
  because they overlap an image bbox; vector-chart furniture remains an oracle/
  inspection boundary.

## Traceability: catalog → invariants

| defect          | caught by         | defect    | caught by      |
|-----------------|-------------------|-----------|----------------|
| PM-01…05        | P1 (limited scope) + sweeps | FL-04     | S1             |
| PM-06           | site/link audit; P1 marker subset | FL-05 | T1 (no-normalize rule) |
| PM-07           | build + sweeps    | FL-06     | build + sweeps |
| FL-01           | L1 + site/link audit | CA-01  | retracted (exp 04); T1 stays bidirectional |
| FL-02           | S2, S3            | CA-02     | T1             |
| FL-03           | sweeps + H1        | RN-01/02  | build + sweeps |
| PR-01…03        | process: D4/D25/D47 (gated class-fix loop) |  |                |

## Calibration status

Current as of 2026-08-15 (D49/D50). Historical v0 calibration evidence remains in
[experiment 04](experiments/04-verifier-calibration/README.md); current mutation
artifacts and per-class counts are in
[experiment 05](experiments/05-mutation-testing/README.md).

- **Executable mechanical checks:** T1/T2, L1 (document-wide source URI
  occurrence coverage + GoTo anchor-text coverage), S1, S2/S3, ST1/ST2/ST3, TB2,
  P1, F1, and FN1.
  `calibrate.py WORKTREE` exits 1 on any unsuppressed major. That unfiltered current
  form also rejects malformed, duplicate, non-major, fingerprint-mismatched, or stale
  owner acceptances with exit 2. Partial/historical runs validate configuration but
  do not require out-of-scope acceptances to appear. `--report-only` relaxes majors
  only.
- **Current full-gate baselines:** Fable suppresses 3 exact owner-accepted T1
  majors and reports `L1 31` / `T1 44` minors; Opus reports `T1 13`; the Risk
  Report reports `FN1 1` / `T1 22` / `TB2 1`. All have 0 unsuppressed majors and
  seam 0. The full operational record lives in `CLAUDE.md` and `state.md`.
- **Mutation floors (8/class, seed 5):** Fable 86/96 across 12 eligible classes;
  Opus 72/88 and Risk Report 74/88 across 11 each (`flatten-chip` not applicable).
  Exact class set, invariant, sample count, and non-decreasing caught count are CI
  enforced. Details are retained as evidence but excluded from the floor because
  source edits can move a deterministic sample without changing recall.
- **Advisory/inspection boundaries:** T1 differences on the table spill set, FN1
  body differences, and seam-merged TB2 findings can be minors. S1 and ST skip that
  same whole-page spill set. L1 does not check output-only links or GoTo destinations;
  S1 does not check italics; F1 is count-only; P1 is presence/duplicate-marker
  coverage rather than a complete provenance proof. TB1/F2 and exact output-anchor/
  visual semantics remain inspection-owned; the sweep and owner scroll layers are
  mandatory backstops, not optional polish.
- **Pre-build mechanisms not shipped:** canonical JSON + SC1, N-version N1, and an
  automated V1 judge. The mechanical compiler, production build, independent
  rulebook sweeps, regression controls, and owner scroll are the built substitutes.
