# Verification contract

The spine of v2 (charter principle 1): every way the output can be wrong is mapped
to the mechanism that catches it. Invariant IDs are stable and referenced from
experiments, code, and the decision log. The archived PDF is the content authority;
PyMuPDF/docling observations, generator annotations, canonical Markdown, and rendered
DOM are distinct claims with distinct scopes. Where an observer is the weak link,
that boundary is stated rather than promoted to source truth.

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
7. **A weaker acceptance file cannot override a stronger authority.** Generic exact
   `accepted.json` entries are forbidden for L2, P2, F3, RF1, and V1. P2/F3/RF1
   exceptions, where meaningful, live only in exact source-hash/tool/schema-bound
   inventory or disposition files; L2 and V1 permit no generic exception.

## Invariants

### T — Text (gates)

- **T1 — Bidirectional token-stream equality.** The markdown text projection equals
  the source text layer: no omissions (source→output) and no additions
  (output→source — v1 only ever checked the first direction; additions are a
  real failure mode even though the one cataloged instance, CA-01, was later
  retracted). Projection-known fields that are legitimately not source text
  (figure alt text, slugs/ids) are excluded by construct, not an arbitrary text
  allowlist. Every difference of at least three tokens is major. A one- or two-token
  difference is also major when its local ordered semantic atoms change a number,
  date, unit/currency, negation, or quantified comparator. Full text SHA-256 and token
  counts bind each opcode; readable samples may be truncated but acceptance identity
  cannot be.
- **T2 — Order.** T1 is sequence-sensitive (alignment diff, not set membership):
  reading order is compared with the oracle's. A paired same-text insertion/deletion
  within ±2 pages becomes a minor displacement only when the complete digest and token
  count agree. Table attribution is retained as diagnostic `zone: table` metadata but
  no longer lowers severity: a table page cannot make arbitrary source/output loss
  harmless. TB2 plus the inspection sweeps remain independent table-local backstops.

### L — Links (gates)

- **L1 — Source-link coverage.** The current gate counts source `/URI`
  occurrences by target across the whole document and requires at least that many
  matching markdown targets. For `/GoTo`, it requires each normalized source anchor
  text to occur among the markdown link texts. This is source→output coverage, not
  per-page/bidirectional link equality: it does not reject output-only links, bind a
  URI occurrence to its source anchor/page, or by itself verify a GoTo link's output
  target. A source-unresolvable named destination is always the L1 minor
  `source-defect-unresolvable-dest`, whether L2 can recover a unique printed heading
  identity or the output correctly leaves it plain (R2). (FL-01: v1 silently dropped
  all 111 internal links.)
- **L2 — Destination identity and projection.** The full-graph gate independently
  reopens and hashes `source.pdf`, reads `/GoTo` annotations, accepts source heading
  identities from the PDF outline plus printed heading geometry, and pairs source and
  canonical link occurrences without consulting their destinations. Every paired
  occurrence must name the exact accepted heading—not merely an existing anchor—and
  missing/unexplained links, unresolved or ambiguous destinations, dead targets, and
  wrong existing targets are majors. Partial/page-filtered runs omit L2 because they
  do not contain the complete graph. A tracked zero-flag artifact binds the source
  SHA-256, aggregate and per-file canonical Markdown hashes, canonical authored links,
  and source-derived expected targets. CI regenerates it byte-for-byte. The site then
  recomputes those hashes and independently parses serialized HTML with HTML5
  tree-building; every authored body/relocated-footnote link and expectation must
  survive, and every rendered id/fragment target must be present, nonempty, valid, and
  unique (also covers PM-06). Artifact drift or incomplete expectation coverage fails
  closed (D53).

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
  bbox/reading-order placement, or alt text. It remains a useful legacy projection
  check but is no longer the source authority.
- **F2 — Captions (inspection-owned today).** Caption text and styling are covered
  by T1/S1; association with the right figure is checked in the page sweeps.
- **F3 — Source raster identity and final projection.** A fresh, PDF-hash- and
  observer-bound source inventory observes every raw raster occurrence directly and
  checks `figures-map.json` plus every local PNG's filename, dimensions, decoded pixel
  identity, alpha/soft-mask status, and file hash. Every occurrence is required by
  default; duplicate draws and allowed skips require exact reviewed observations in
  `source-inventory.json`. The tracked `source-projection.json` carries required
  figure identity/order and accepted-skip reason digests into the production renderer.
  The HTML5-normalized article must contain each required visible figure exactly once,
  under the correct source-page context and in exact interleaved event order; copied
  build assets must have the exact source-bound bytes, with no missing or extra files.
  Missing/stale/malformed inventory, map, asset, artifact, sentinel, or DOM evidence is
  major. Alt text, caption association, vector artwork, and visual layout remain
  outside F3.

### FN — Footnotes (gates)

- **FN1 — References and bodies.** The gate compares document-wide reference
  counts, requires each markdown reference to have a definition in its section,
  rejects each definition with no reference in that same independently publishable
  section, and compares body text per footnote number. The section-local dangling-
  definition major is an output-side structural check that does not consult semantic
  source zones; it closes the demonstrated F18 correlated false green. Ordinary body-
  text mismatches remain advisory minors until oracle boundaries harden, but changed
  numbers, dates, units/currencies, negations, or quantified comparators are major.
  Declared source-orphan references are reported as minors by the legacy lane.

### RF — Raw-PDF footnotes (gates)

- **RF1 — Occurrence-bound raw reference/definition authority.** A separate observer
  reopens `source.pdf` without importing `oracle.py` or generator `zone`/`fn`
  annotations. It observes numeric superscript reference glyphs and smaller,
  left-margin numeric definition markers in a contiguous bottom-of-page small-type
  region, then binds source and canonical occurrences one-to-one by section, number,
  page proximity, order, and concrete source bbox. Definitions and normalized body
  text are bidirectional requirements; duplicate, missing, ambiguous, stale, or
  mismatched evidence is major. Exact exclusions require a disposition bound to the
  PDF SHA-256, observer schema, PyMuPDF version, and source occurrence. Scope is
  intentionally narrow: numeric superscripts with numeric definitions beginning on
  the same or adjacent page are covered; symbol/letter markers and endnotes are not.

### P — Provenance (gates)

- **P1 — Page-map coverage.** Every expected non-cover/non-TOC page must be
  represented by either a section start or a serialized page marker, and duplicate
  serialized markers are majors. The current gate does not reject unexpected
  markers, compare marker order, or treat a marker that repeats an implicit section
  start as a duplicate. Page-local checks provide the practical attribution backstop.
- **P2 — Source-page disposition and final-DOM event identity.** A fresh PDF
  observation requires every page by default. Cover/TOC/blank exclusions exist only
  in a checked-in `source-inventory.json` bound to the source SHA-256, PyMuPDF version,
  observer schema, exact page observation, and written reason. Generator `toc_pages`
  is merely a claim checked against that authority. The hash-bound source-projection
  artifact then requires every content page marker exactly once, in source order and
  in the exact interleaved page/figure event stream of the HTML5-normalized built
  article. Unexpected, excluded, duplicated, reordered, malformed, or missing markers
  and stale/malformed authority are majors. P2 complements rather than deletes P1;
  P1 remains useful on partial/historical projections where the full source-to-DOM
  graph is unavailable.

### SC — Schema and projection (pre-build design target)

- **SC1 — Model validity.** The planned canonical JSON tree/schema did not ship;
  transient block dictionaries feed the markdown serializer directly.
- **SC2 — Projection health.** The clean Astro/Pagefind production build exercises
  HTML, `card.md`, and `llms.txt`. L2 mechanically checks internal-link fidelity in
  serialized article HTML and the complete rendered-page fragment graph. P2/F3 verify
  source-bound page/figure identity, order, and copied source bytes in the same built
  HTML. V1 rejects browser-hidden authored raw HTML before renderer transforms. Other
  portable-export semantics remain in export tests and the sweep layer rather than a
  named `SC2` Python invariant; search/social output, computed browser layout, and
  every projection mutation remain phase 9 work.

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

### V — Browser visibility (gate at the authored-HTML boundary)

- **V1 — Authored semantic content may not use browser-hidden raw HTML.** Before
  renderer transforms can make provenance ambiguous, the production Markdown parser
  examines authored HTML with HTML5 fragment parsing. It rejects `hidden`, `inert`,
  `aria-hidden=true`, closed popovers/details/dialogs, hidden input/control containers,
  browser-hidden control elements, and the site's hidden semantic classes unless an
  exact renderer-generated footnote shim is in the trusted transform lane. Active or
  reserved markup, event handlers, inline style, JavaScript URLs, article-boundary
  crossing, and forged source-projection sentinels are rejected separately. The
  mutation worker converts the structured `browser-hidden-authored-content` finding
  into a blocking V1 result while continuing the DOM audit over the same supplied
  bytes. Generic acceptance is forbidden. This is not computed CSS or visual layout:
  responsive stylesheets, clipping, occlusion, stacking, and viewport-specific
  visibility remain phase 9 plus the independent sweeps/owner scroll.

The old pre-build plan also called its unshipped automated page-image diff “V1.” D55
supersedes that unused design label with the executable visibility contract above.
No standing pixel-diff judge shipped; page/Markdown/DOM sweeps and the owner scroll
remain the visual-comparison layer.

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
fidelity, not render patching), non-breaking hyphens, dashes, and unicode beyond NFC.
NBSP participates only as ordinary A2 Unicode whitespace; it is not a hidden
calibration fold. Historical defect replay may opt into its old quote/hyphen folds,
but the production gate may not. Mojibake (CA-02) must fail T1.

## Exclusion list (v0)

- Running headers/footers and bare page numbers (derived per-card; derivation
  checked for cross-page consistency).
- PDF cover/TOC/blank pages (the site generates its own TOC) — exact observations and
  reasons in the source-hash/tool/schema-bound `source-inventory.json`. Per-card
  metadata is only a checked claim and cannot authorize an exclusion by itself.
- Raster-internal chart text remains pixels in the retained image and therefore has
  no PDF text-layer spans to compare. Text-layer overlays are not excluded merely
  because they overlap an image bbox; vector-chart furniture remains an oracle/
  inspection boundary.

## Traceability: catalog → invariants

| defect          | caught by         | defect    | caught by      |
|-----------------|-------------------|-----------|----------------|
| PM-01…05        | P2 final-DOM event stream; P1 partial backstop + sweeps | FL-04 | S1 |
| PM-06           | L2/P2 final-DOM audits | FL-05 | T1 (no-normalize rule) |
| PM-07           | V1 + build + sweeps | FL-06 | build + sweeps |
| FL-01           | L1 + L2 canonical/final-DOM gates | CA-01  | retracted (exp 04); T1 stays bidirectional |
| FL-02           | S2, S3            | CA-02     | T1             |
| FL-03           | sweeps + H1        | RN-01/02  | build + sweeps |
| PR-01…03        | process: D4/D25/D47 (gated class-fix loop) |  |                |

## Calibration status

Current as of 2026-08-15 (D49/D50/D53/D55). Historical v0 calibration evidence remains in
[experiment 04](experiments/04-verifier-calibration/README.md); current mutation
artifacts and per-class counts are in
[experiment 05](experiments/05-mutation-testing/README.md).

- **Executable mechanical checks:** T1/T2, L1 (document-wide source URI
  occurrence coverage + GoTo anchor-text/source-defect coverage), L2 (exact
  source→canonical destination identity plus hash-bound final-DOM projection), S1,
  S2/S3, ST1/ST2/ST3, TB2, P1/P2, F1/F3, FN1/RF1, and V1.
  `calibrate.py WORKTREE` exits 1 on any unsuppressed major. That unfiltered current
  form also rejects malformed, duplicate, non-major, fingerprint-mismatched, or stale
  owner acceptances with exit 2. Partial/historical runs validate configuration but
  do not require out-of-scope acceptances to appear. `--report-only` relaxes majors
  only. Generic acceptance rejects L2/P2/F3/RF1/V1 entries before matching.
- **Current full-gate baselines:** Fable suppresses 20 exact accepted T1 majors—3
  historical owner-adjudicated visual-order findings plus 17 maintainer/source-
  adjudicated table-order findings under the owner's broad authorization—and reports
  `L1 34` / `T1 28` minors; Opus suppresses 4 maintainer/source-adjudicated exact T1
  majors and reports `T1 9`; the Risk Report suppresses 1 such exact T1 major and
  reports `FN1 1` /
  `T1 21` / `TB2 1`. All have 0 unsuppressed majors and seam 0. The 22 new
  acceptances are PDF-reviewed table-order projection residuals exposed by removing
  blanket demotion; the three older Fable findings retain their prior visual-order
  adjudication. L2 remains clean at 108 Fable and 54 Opus authored destinations, plus
  121 Risk Report logical destinations over 123 authored occurrences. P2/F3 require
  309 pages/151 figures for Fable, 187/98 for Opus, and 180/14 for Risk: the built DOM
  totals 676 page markers and 263 rendered figures, while the copied asset set contains
  267 exact source rasters. RF1 is clean at raw ref/definition counts 76/76, 36/36,
  and 93/92 respectively; Risk's difference is the one exact p.126 source-artifact
  disposition.
- **Mutation floors (8/class, seed 5):** strict schema-v2 artifacts record four
  separate signals. Fable's 25 classes / 200 trials yield 191 detected, 184
  intended-major, and 185 major-blocked. Opus and Risk have 24 classes / 192 trials
  each (`flatten-chip` inapplicable): Opus 176/168/171 and Risk 173/166/171. Across
  584 trials the totals are 540 detected, 518 intended-major, and 527 major-blocked;
  all 527 also exit nonzero. Detection, intended-major, and major-blocking counts are
  independently non-decreasing floors; gate-blocked is diagnostic because an
  acceptance-configuration error also stops release. The complete schema binds card,
  seed, trials/class, class set, invariant, aggregates, and per-trial evidence, with no
  legacy fallback or baseline-overwriting output. V1/P2/F3/L2 and every critical
  T1/FN1 class are 8/8 wherever eligible.
- **Advisory/inspection boundaries:** ordinary one- and two-token T1 differences and
  noncritical FN1 body differences can remain minors; seam-merged TB2 findings can be
  advisory. T1 table attribution no longer changes severity, but S1 and ST still skip
  the table spill set. L1 still does not bind individual `/URI` occurrences to source
  anchors/pages; L2 owns internal `/GoTo` occurrence/target identity. S1 does not check
  italics; F1 remains count-only; P1 remains partial coverage. RF1 does not cover
  symbol/letter footnotes or endnotes. F3 does not prove caption/alt/layout fidelity.
  V1 does not compute stylesheet/viewport visibility. TB1/F2, broader visual
  semantics, every-projection bootstrap, and computed layout remain sweep/owner or
  later-phase work; those backstops are mandatory, not optional polish.
- **Pre-build mechanisms not shipped:** canonical JSON + SC1, N-version N1, and an
  automated page-image judge. The mechanical compiler, production build, independent
  source-first L2/P2/F3/RF1/V1 lanes, rulebook sweeps, regression controls, and owner
  scroll are the built substitutes.
