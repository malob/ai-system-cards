# Architecture hardening roadmap

Settled 2026-08-15 after an adversarial two-model review of the shipped pipeline.
The immutable review record is under
[`architecture-review-exchange/`](architecture-review-exchange/); D51 records the
decision. Implementation and validation status live in [`state.md`](state.md). D55
records phase 3's locally validated authority repair; it has not yet been pushed or
deployed.

## Bottom line

Do not rebuild the whole converter. The three-card pipeline is more reproducible and
less document-specialized than its table code initially suggests. Its leading risk is
instead **verification authority**: several checks derive their expectation from the
same input or interpretation that drives generation. When that shared premise is
wrong, generator and verifier can agree on the same wrong result.

The program is therefore:

1. close known release and projection defects;
2. make important expectations independent of generator decisions;
3. preserve low-level source observations separately from semantic annotations;
4. use focused experiments to decide whether tables need a typed internal grid; and
5. reconsider a whole-document semantic IR only if narrower seams fail under measured
   cross-producer or cross-projection pressure.

## What the review established

### Strong current foundations

- All three accepted documents regenerate byte-identically under the measured current
  inputs; a cold PyMuPDF observation-cache rebuild also reproduces.
- There are no executable card-slug branches. Per-card visual grammar is represented
  as data, and one pipeline serves all three current Anthropic documents.
- PyMuPDF is a strong primary observer for this born-digital family, especially for
  exact text and geometry. It remains a versioned, fallible observer—not source truth.
- Markdown is adequate as the accepted prose artifact on current evidence.
- Exact acceptances, fail-closed majors, byte-diff regression, page/DOM sweeps, owner
  inspection, and full-site builds are safeguards to preserve.

### Demonstrated defect at review time

The published portable-Markdown projection mishandles table-only footnotes. The HTML
path repairs references embedded in raw table HTML; the portable export path does not.
The review counted 24 affected footnotes across the corpus. This is a localized
projection defect, not evidence that canonical sections or the main HTML have lost
source content.

No source-content defect was demonstrated in canonical `sections/*.md` or the main
HTML rendering. Nineteen table-zone T1 residuals of at least three tokens—largest 51
and 45 tokens—were hidden by current severity demotion and still require PDF
adjudication. They are neither cleared nor declared defects.

### Demonstrated blind spots

The following were true at review time; [`state.md`](state.md) records which phases
have since closed them.

| Area | Failure of authority | Consequence |
| --- | --- | --- |
| Release inventory | The site discovers card directories automatically; CI names three cards literally. | A new publishable card can bypass its full gate and seam audit. |
| Internal links (L2) | PDF internal destinations are not mechanically compared through generated targets to final anchors. | Repointing every internal link produced no new blocking finding. |
| Page coverage | One `toc_pages` interpretation controls generation, expected coverage, and invariant exclusions. | A mistaken exclusion can remove both content and the evidence expected to detect its absence. |
| Figures (F1) | Generation and verification both trust `figures-map.json`. | Deleting a map entry can remove both the figure and its expectation. |
| Semantic zoning | `oracle.py` mixes low-level observations with body/footnote/table interpretation. | Re-zoning body text as footnote text produced a correlated false green. |
| Tables | Output Markdown determines table scope, which weakens T1 over each table page and its neighbors. | About a quarter of each document receives reduced scrutiny; table topology has no independent source model. |
| Severity | Token count stands in for semantic importance. Mutation results report detection, not whether release blocks. | Changed numbers, negations, and many two-token deletions can remain nonblocking. |
| Structure (ST2) | List/structure blocking recall is weak against known sweeps and mutations. | Token-preserving structural errors can pass. |
| Replay | Docling candidates and extractor/model provenance are untracked or unpinned, and caches lack sufficient invalidation. | Warm replay does not prove that cold extraction reproduces the candidate. |
| Projections | Browser/export reconstruction is not comprehensively verified. | A canonical artifact can be correct while a published projection is wrong. |

These are measured weaknesses, not a claim that every possible failure is present in
the published corpus.

D55 closes the immediate page, figure, semantic-zoning, table-severity, critical-token,
and projection loops named above, but only within its written scopes. Source-bound P2
and F3 replace shared omission authority; RF1 plus output-side footnote closure catch
the demonstrated F18 shape; table attribution no longer lowers T1 severity; and V1
rejects browser-hidden authored raw HTML before rendering. This does **not** close
ST2, table topology, extractor/cache replay, the broader observation/annotation split,
computed-CSS/viewport visibility, every non-HTML projection, clean bootstrap, or a
different PDF producer. Those remain assigned to phases 4–9 rather than being implied
by a green phase-3 gate.

## Settled architecture

| Layer | Settled role |
| --- | --- |
| Source | The archived PDF is the sole content authority. |
| Observation | Keep PyMuPDF as the primary born-digital observer. Record source hash, tool/schema version, and raw spans, links, geometry, drawings, and image facts. |
| Interpretation | Store derived roles—body, heading, footnote, table, figure, exclusions—separately enough that they can be mutated and checked without changing raw observations. |
| Table candidate | Treat pinned Docling output as a proposal. Retain a replayable legacy artifact immediately; test a normalized candidate with cells, spans, geometry, and provenance. |
| Accepted prose | Keep tracked Markdown canonical for prose. |
| Published projections | Treat HTML, `card.md`, per-section Markdown, `llms.txt`, anchors, search, and social output as separate claims that need projection-specific checks. L2 plus D55's P2/F3/V1 lane now bind links, source pages/figures, copied source bytes, event order, and authored raw-HTML visibility through the production HTML renderer; it is not yet an all-projection or computed-layout proof. |
| Verification | Build expectations independently where correctness is load-bearing. Detector disagreement widens scrutiny; it never grants immunity from a general invariant. |

The review explicitly rejected these as present work:

- no whole-document semantic-IR migration;
- no `DoclingDocument` canonical schema—the inspected version cannot losslessly carry
  the required inline bold, link, and footnote ranges inside table cells;
- no Pandoc dependency without a real downstream consumer, and never as extraction
  authority;
- no producer-plugin architecture before a genuinely different PDF producer is
  measured; and
- no general rule DSL. Stable rule identity and evidence are required, not a new
  language.

## Ordered implementation program

Each phase earns the next. A later refactor must not be used to delay a smaller
correctness repair.

| Phase | Work | Exit evidence |
| ---: | --- | --- |
| 0 | Derive the deployment gate inventory from the same validated repository inventory the site can publish. | A synthetic fourth card changes CI coverage automatically; every discoverable card has exactly one full gate and seam result. |
| 1 | Repair portable table-footnote semantics. | Full-card and section exports preserve one/many references, stable later numbering, definitions, and backlinks under the supported Markdown interpretation. |
| 2 | Implement L2 from PDF `/GoTo` destinations through source/canonical hash binding, accepted source heading identity, generated targets, and an independently parsed final DOM. | Known wrong destinations and declared source defects replay correctly before L2 becomes blocking; stale expectation artifacts fail closed. |
| 3 | Close immediate authority loops: F18 mutation harness, dangling definitions, source-page disposition, independent figure inventory, table-zone T1 ≥3, critical-token severity, separate detection/blocking metrics, and production-normalization contract. | Every new blocker is source-adjudicated; true defects are fixed and residuals are exact or narrowly evidenced. |
| 4 | Harden ST2 with the 16 sweep findings, missed mutations, and nearest-negative controls. | Useful blocking recall without noisy control failures. |
| 5 | Pin/version table extraction, track candidate provenance, correct cache keys, and add fast replay plus cold scheduled/release extraction lanes. | Warm replay is deterministic; cold drift is either reproducible or explicit. |
| 6 | Split observations from annotations at a serialized schema/view boundary without changing output. | Byte-identical generation and identical verifier findings. |
| 7 | Run independent verifier and generator table experiments across ruled, filled, short-rule, and whitespace tables. | Measured decision on whether a persistent typed grid improves repairs/provenance and whether independent topology reaches useful recall. |
| 8 | Replace page-wide table immunity with source-bbox attribution and exact or narrow residual acceptances. | Table membership enables table checks but never disables general checks. |
| 9 | Test clean bootstrap, every export/DOM projection, and a different producer. | Evidence either justifies a broader representation/producer boundary or rejects it. |

Phases 0–1 are deployed at `685cba6`; phase 2 is deployed at `ff9b6e3` (D53/D54).
It intentionally changes one Fable p.99 canonical line from a dead empty-fragment
link to plain text under R2; Opus and Risk Report sections remain byte-identical.
Hosted fast-gate, Pages, and three-card mutation runs all passed for phase 2.

Phase 3 implementation and its fast release graph are complete and validated
**locally** (D55), not yet pushed or deployed; exact final-tree replay of all mutation
floors remains pending on the hosted post-push jobs. It
changes no canonical `sections/*.md`; a clean `site/dist`, including Pagefind, is
byte-identical to pre-change HEAD. The source/final-DOM lane verifies 676 page markers,
263 rendered figures, and 267 exact source raster assets. Twenty-two newly blocking,
PDF-reviewed table-order residuals are exact accepted T1 findings (25 accepted majors
total across the corpus), not broad table immunity. Strict schema-v2 mutation floors
cover 584 trials and separately preserve detection, intended-major severity, and
major-blocking behavior. Phase 4 (ST2) is next. Phase 5 still owns complete
extractor/cache provenance, and phase 9 still owns all-projection/bootstrap,
computed-browser-visibility, and different-producer evidence.

## Experiments and kill criteria

### X1 — observation/annotation split

Dual-serialize current information without changing values.

**Kill:** if the schema-only split changes behavior or forces a premature
producer-specific interface, keep the fused code temporarily, retain the correlated-
authority mutation, and first measure which annotation assumptions actually vary.

### X2 — table residual adjudication

Map T1 operations to source table bboxes; inspect all 19 known ≥3-token residuals and
all critical one-token residuals. Compare page-wide demotion, bbox attribution, and
exact/narrow acceptance.

**Phase-3 result.** The page-wide severity demotion was rejected and removed. Every
ordinary difference of at least three tokens now remains major; critical one- and
two-token changes remain major as well. PDF adjudication produced 22 exact new T1
acceptances—17 Fable, 4 Opus, 1 Risk Report—including Fable p.316's one-token critical
`None` residual. Full text digests/token counts prevent display truncation from
colliding, rationale is explicit, and clean pinned replay is stable. This completes
the immediate severity/adjudication question without pretending that a page-level
`zone: table` tag is bbox attribution. Phase 8 still owns that narrower provenance
and the removal of remaining whole-page table spill assumptions from other checks.

**Kill exact acceptance:** if legitimate fingerprints churn under clean replay or a
harmless version change, identify a narrow structural residual class. Do not raise a
threshold merely to preserve a green dashboard.

### X3 — independent table topology and generator representation

Build verifier-side topology from low-level spans/drawings and a separate normalized
Docling candidate. Mutate output, candidate, and verifier interpretation independently
against human-adjudicated ruled and unruled cases.

**Adopt a persistent project grid only if** it materially simplifies generator
repair/provenance or both sides independently demonstrate a need for the same explicit
cell model. If verifier topology works without shared generator structure and a grid
does not improve repair, keep HTML canonical for tables and refactor locally.

### X4 — different-producer probe

Test low-level observations separately from body-size, list, footnote-region,
heading-role, and table-signal assumptions.

**Kill global rule scope:** move failed assumptions into an explicit producer-family
grammar; do not widen a global heuristic to absorb the new PDF.

### X5 — cold bootstrap and projection tests

Generate from stubs without reading prior accepted structure, then mutate list,
heading, figure, footnote, link, and table reconstruction in each published projection.
For HTML, include computed stylesheet behavior, responsive breakpoints, clipping,
occlusion, and representative browser viewports; D55's authored-raw-HTML V1 policy is
an important input gate, not a substitute for that browser evidence.

**Reopen a whole-document IR only for** systematic non-table projection loss,
inability to bootstrap without prior Markdown, repeated encoding of the same semantics
across incompatible stages, or provenance/ambiguity that cannot be gated at a
narrower boundary. If none appears, reject the IR rather than deferring it forever.

## Evidence standard and self-improvement loop

Every claimed defect or new rule must:

1. identify a mechanism;
2. demonstrate its consequence in the accepted or rendered projection;
3. check for redundant semantic channels;
4. distinguish a verifier blind spot from a present defect; and
5. adversarially attempt to refute the headline.

A rule compounds only when it carries a smallest source-backed positive fixture, the
nearest counterexample where it must not fire, a mutation proving the release gate
responds, visible corpus fire counts, and full-corpus replay. Start rules at the
narrowest demonstrated scope; promote them to a producer family or universal rule
only after cross-document evidence. Agents propose abstractions; fixtures and replay
decide whether they survive.

Stronger checks should begin in shadow/reporting mode. Adjudicate every newly
blocking result against the PDF, fix genuine defects, exact-accept only evidenced
source/extraction residuals, regression-sweep controls, then land the check, repair,
acceptance, regenerated output, and certification evidence together. A truthful red
gate must not be tuned away merely to keep the release branch green.

Generic acceptance is not an escape hatch for source-bound or final-projection
authority. L2, P2, F3, RF1, and V1 are denied in `accepted.json`; where an exception is
meaningful it must live in the exact, source-bound authority that owns it, and L2/V1
permit no generic exception. This keeps a weaker fingerprint file from silently
overriding the boundary phase 3 was built to establish.

## Source record

The load-bearing settled messages are
[`A0004`](architecture-review-exchange/maintainer/A0004-settled-diagnosis-and-program.md),
[`A0005`](architecture-review-exchange/maintainer/A0005-final-response-to-verified-additions.md),
[`A0006`](architecture-review-exchange/maintainer/A0006-accepted-final-facts-and-close.md),
[`B0005`](architecture-review-exchange/reviewer/B0005-final-verified-additions.md),
and
[`B0006`](architecture-review-exchange/reviewer/B0006-accepted-corrections-and-close.md).
Those immutable messages hold claim provenance and measurement qualifications; this
document is the operating synthesis.
