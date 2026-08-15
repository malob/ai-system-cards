# Experiment 11 — risk-report-2026-08 inspection sweep, round 1 (2026-08-14)

**Question:** after the automated gate converged at 0 majors on the third card
(anthropic/risk-report-2026-08 — the first non-system-card document), what
does the layer-2 agent inspection find that the gates can't see — and does
the sweep design hold for a document with new constructs (unlabeled prompt
boxes, in-bubble lists, links inside tables, page-filling footnotes)?

**Method:** the two-check round-G design (experiment 09), re-rulebooked for
this card (`rulebook.md` here): 8 triple-pane comparators over all 180
content pages (PDF render vs md slice vs served HTML, zoom crops for dense
constructs) + 3 markdown-smell linters over the 9 section files. Inputs:
`pipeline/.cache/rr-sweep1/` (slices, served.html, findings-*.jsonl).
Findings are re-runnable from the rulebook + this README alone.

**Context going in:** gate at 0 majors; typed residuals FN1 1 (declared
orphan-ref source defect, p.126) + T1 31 (docling cell tokenization, seam
displacements, repeated-header dedup). Seam audit: 0 flags. Mutation recall:
loss classes 100%, structural splits 50–62% (calibrated band). The D45 fix
classes (footnote region walk, orphan refs, table link injection, in-box
list items) all landed with both system cards byte-identical.

**Result:** 11 agents, 189 units (180 pages + 9 files), ~145 clean. **66
major findings (heavily overlapping between comparators and linters — ~40
distinct) in 9 mechanical classes**, 25 minors, 3 source-faithful reports.
The gates could see none of them (tables are outside T1's token stream;
anchors and styling are below its resolution) — exactly the layer-2 charter.

Distinct major classes and their class-level fixes (commits `cd5a21c`,
`ef9f5fe`; every fix regen-verified with BOTH system cards byte-identical):

| class | pages | root cause → fix |
| --- | --- | --- |
| goto links to wrong heading | 12, 26–27, 60, 82, 114, 146, 183 | dest coords sloppy on multi-heading pages (Claim 6/7 swapped) → extended text resolution (Claim map, Appendix pattern, unique-title map, pooled split halves) behind the `link_text_resolution: extended` manifest knob (D46) |
| table repair cascade/garble | 182–185 | `_extend_truncated_cells` anchored on a mid-sentence twin in another cell and leaked across rows → span-OWNERSHIP guard (chains + reading order + column regions) |
| label cell split/scramble | 78, 80 | rotation repair split label+link into an extra cell → `_merge_overflow_cells` (header-width authority, fragment-or-scramble proof, y-band-anchored multiset rebuild) |
| bold cell leads dropped | 14, 113, 125–128, 155–156, 182–184 | fnref digits / mid-line x0 changes / HTML entities defeated cell↔span matching → digit variants, `_column_regions`, entity remap; underline border guard |
| all-th data rows | 115, 131, 183 | docling tags continuation-chunk lead rows as headers (and the p.115 header as td) → dark-band geometry demotion + row-0 white-text promotion |
| in-cell lists flattened | 113, 155 | `_bullet_breaks` knew only •, this family uses ● → both |
| full-width bold Claim leads merged | 35, 52, 62 | lead exactly fills its line, hiding the short-line signal → claim-grammar-gated split (opus's welfare run-in keeps flowing) |
| in-box list structure | 85 | typed 'N.' enumerations and nested rubric bullets flattened → ordered items + bullet nesting in bubbles |
| lettered-list forms | 9, 42, 136–138 | parentless lettered items rendered as a code block (orphan-indent run normalization); emphasis-splitting marker spacing; bold ordered markers |

Also fixed: subscript flattening §2.6 (new `<sub>` mark), 'Opus- and
Sonnet-class' hyphen-join over-fire (shared A1 with suspended-compound
exception), p.115→116 mid-sentence seam (flows when the previous side ends
unpunctuated), nested `<sup>` renderer shim, p.86 'Output format' label
(accepted as bold-lead parity).

**Deferred as typed minors (owner list):** p.13 two cell paragraphs merged
(text intact); p.153 shallow-indent italic RSP quotes render flush; p.36
'sed' black-vs-green inside one code span (renderer styles code uniformly);
footnote URL wrap-spaces in visible link text (hrefs correct); p.42
taxonomy sub-list rides in a blockquote (content correct).

**Post-fix state:** gates 0 majors (FN1 1 declared source-defect + T1 26
typed); seam audit 0; mutation recall at the calibrated band. Round 2
(fresh `rr-sweep2/` inputs): 4 agents — 3 fix-verification comparators over
the 37 affected pages + 1 rotating 15-page regression sample.

## Round 2 (same day) — fix verification + rotating sample

52 units, 4 agents (`pipeline/.cache/rr-sweep2/findings-*.jsonl`): the
15-page rotating regression sample came back **fully clean — zero
regressions** from the ~30-commit fix batch. Of the 37 re-inspected fix
pages, 30 verified immediately; 7 residuals surfaced and were fixed the
same evening (commit `e352168`): p.9 lettered siblings nesting (indent
inheritance), p.52 wrapped Claim 4.1 lead (grammar now tests the
paragraph's first line), p.113 cross-seam third bullet (`_bullet_breaks`
re-runs post-merge), and the §6.6 label-bold cluster pp.182–184
(`_bold_label_cells` whole-cell pass + duplicate-word leak strip + false
`<u>` removal). One agent flag (p.80 scrambled label) was stale — its
snapshot predated the y-band fix; the corrected row was verified directly.
Each residual fix was re-verified by direct crop/DOM inspection rather
than a third agent round.

**Convergence state:** gates 0 majors (FN1 1 declared source-defect +
T1 26 typed residuals); seam audit 0; both system cards byte-identical;
10/10 rendered-page assertions pass on the production build. Remaining
items are the five deferred typed minors (owner list above) and the owner
scroll pass (onboarding step 8).

## Owner scroll pass — findings log

1. **p.42 taxonomy sub-list** (owner, 2026-08-14 ~21:50): rendered as a
   blockquoted bullet list with literal/bold letter markers vs the PDF's
   plain nested lettered list. Two roots, both class-fixed (commit
   `8d96f1a`): a stale quote context from a cross-page item continuation
   (non-quote items now close the context — a marker-grid discriminator was
   tried and REVERTED, it de-quoted the genuinely-quoted UK-AISI lists:
   quoted lists sit on-grid in this family, only the bullet-glyph signal
   discriminates), and the renderer's `<ol type="a">` transform aborting on
   a source-faithful bold letter marker. This retires the p.42 entry from
   the deferred-minors list.

2. **Cross-page bubble splits** (owner, 2026-08-14 ~22:00): the §2.24
   prompt box (one box in the PDF, pp.84-86) rendered as three bubbles cut
   at the page seams, the p.86 fragment promoted to an 'OUTPUT FORMAT'
   label. Class-fixed (commit `076161f`): geometry continuation rule in
   stitch() (same fill, box to the bottom margin, resuming at the top) +
   per-segment page facts and inline seam markers in the serializer. Also
   healed §2.20's review box (pp.73-74). **Carries one system-card canon
   change pending owner approval: fable 06a p.101→102 pilot-quote box (the
   identical construct) now one bubble.**

3. **Table 3.10.A cell paragraphs** (owner, 2026-08-14 ~22:30): sub-
   paragraphs INSIDE bulleted cells rendered as one dense blob per bullet.
   Root: `_cell_blank_lines` could never align bulleted cells (glyphs in
   their own x0 cluster or glued into spans; intro + hanging-indent bullets
   spanning two x0 tiers; docling's quote folds, low-9 comma, and absorbed
   fnref digits each breaking the char match mid-cell). Fixed as five
   tolerance classes + pairwise edge-interval fallback families (canon
   single-column path untouched; commits `c3d046c`, this one). Restored the
   full 9-paragraph structure of the frontier-developer cell, the §4.8
   twins, AND the p.13 two-paragraph cell — retiring that deferred minor.
