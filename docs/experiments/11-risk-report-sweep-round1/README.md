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

4. **In-cell italics** (owner, 2026-08-14 ~22:40): Table 3.10.A's italic
   runs rendered regular — restyle's segmentation (where D42's italic
   support lives) can't reach these cells. `_cell_blank_lines`' tolerant
   alignment now emits `<i>` runs too. Side effect kept as a canon
   improvement: fable p.313 '(interview only)' (Lora-Italic in the PDF)
   gains its italics after rendering regular since June.

5. **Seam marker hoisted to table top** (owner asked for a full in-browser
   look at Table 3.10.A, 2026-08-14 ~22:50): the p.114 gutter label sat at
   the table's top. HTML foster-parenting: the between-fragments marker
   was left between `</tr>` and `</tbody>` after the seam row merged, and
   the parser hoists it out of the table. Marker now rides inside the
   merged cell at its seam (only in the foster-parenting case — canon
   placements before surviving rows untouched). In-browser verified:
   p-114 anchors 624px into the table at the true seam.

6. **Dead footnote backlinks** (owner, 2026-08-14 ~23:05): the ↩ on
   table-only footnotes (10, 11) did nothing — their GFM ref anchor lives
   in the display:none .fnref-shim, an unscrollable target. The visible
   in-table ref now carries the anchor id (shim ids stripped post-render).
   Renderer-level, so it also heals the certified cards' table-only
   footnotes. Click-verified in-browser.

## Deferred-minor re-adjudication (2026-08-15, owner-directed)

The owner asked what the agents had caught that remained unfixed. Auditing
the findings files against the current output gave an uncomfortable answer:
**three of the owner's five scroll findings had been flagged by the round-1
agents and downgraded by the orchestrator** (p.42's blockquote as
"cosmetic", the in-cell italics and cell-paragraph flattening as "typed
minors"). Worse, the round-2 verification prompts described the *fix*
("verify the `<br>●` breaks") rather than the PDF, so the sweep could only
confirm the partial repair — the charter's independence principle (§4)
violated at the orchestration layer, and the rulebook's do-not-flag list
seeded with self-adjudicated entries rather than owner decisions.

Of the nine minors still open, four classes were re-adjudicated as real and
fixed (`e8f8f61`): hyphen-lead wrap-join corruption in visible text
(p.184, fn50/fn53 URLs), space-before-punctuation after in-cell links (6),
docling quote folds in cells (p.13), and p.153's indented RSP quotations
rendering flush — the same error shape as p.42, an indent that is the only
signal marking a quotation. T1 residual fell 25 → 22 as a side effect.
One deferral survives: p.36's part-black/part-green code span.

Process changes proposed to the owner and pending decision: (1) sweep-flagged
majors may not be downgraded by the orchestrator — only mechanically
disproven with an archived crop, or owner-adjudicated; (2) verification
prompts describe the PDF, never the fix, and the do-not-flag list holds
owner decisions only; (3) a mechanical cross-page-construct check from
oracle box geometry; (4) a rendered-DOM assertion station (anchor
y-monotonicity, backref targets having layout boxes) between build and
scroll.

7. **Page-marker labels one line high** (owner, 2026-08-15 ~11:15): where a
   page break fell at a rendered line end, the gutter label sat beside the
   previous line — 34/180 markers here, 22/187 on opus. Root: `.pagemark`
   is `position: absolute`, so the anchor is out of flow and never wraps
   with the following word; its static position stays on the previous line.
   A markup fix (bind the marker to the following word) was tried and
   reverted — 126 lines of canon churn, zero rendering change, for exactly
   that reason. Fixed in the renderer (`site/.../index.astro`): a
   reflow-dependent layout pass re-aligns inline markers to the first
   following text's line box, clamped so labels never cross a figure or
   table. Risk report 34 → 5 stranded (all standalone-before-table, benign);
   opus 0.

## Round 3 (2026-08-15) — ship gate

Run because 23 commits (+575 lines across 11 pipeline/renderer files) had
landed since the last full inspection: the output nobody had swept was the
output about to ship. 11 agents, 185 units, fresh inputs in
`pipeline/.cache/rr-sweep3/`, under `rulebook-round3.md` — which fixes the
round-2 process failure by describing the PDF rather than the fixes, and by
holding only OWNER decisions in the do-not-flag list.

**4 majors, all fixed** (commit `aab9e96`):

| class | pages | root cause → fix |
| --- | --- | --- |
| header band read as a body row | 10, 11, 12 | header-text promotion recognised only `#ffffff`; this card's headers are CREAM `#faf9f5` → colours read from the manifest's `table-header-text` role, and header cells matched by per-COLUMN containment (a header cell spans several spans; reading order interleaves multi-column header rows) |
| seam marker outside the box | 74 | the LEGACY mid-sentence turn merge never learned the inline-marker trick the geometry merge uses → ~90 words of p.74 deep-linked to p.73 |
| footnote sup inside a bold run | 125, 126, 128 | whole-cell bold wrapped the superscript, which the PDF sets at regular weight → trailing sup lifted out of the bold |
| link destinations resolved to the wrong heading | doc-wide, **both certified cards** | PDF dests are BOTTOM-UP, span geometry top-down → every geometric comparison failed and multi-heading destination pages fell back to their FIRST heading. Converted at the oracle; `anchor_for` now takes the first heading at-or-below the dest (measured: dests sit 0–40pt above their heading, modes 15/17pt, 99% within 40pt; PDF-verified at +1pt for a TOC dest and +15pt for a body dest) |

Also fixed: dest-pooling restricted to short fragments (a full anchor phrase
was inheriting a coarser target from another link sharing its destination,
p.121), and the last-row border rule extended to `th` (stray segment under
the first column, p.80).

**Minors** were either owner-decided (smart quotes — the typographer stays
on, 2026-07-25; p.22 tints; p.36 code span), source-faithful on inspection
(p.153's fully-italic quotation, p.181's bold-lead absence, p.42's bold
`c.`), or cosmetic-latent (th/td mix in row labels, invisible under current
CSS). Two disagreements between inspectors were resolved against the PDF.

**Open, owner's call:** in-cell bulleted lists render as literal `●` glyphs
separated by `<br><br>` rather than `<ul>/<li>`, so a bullet's follow-on
paragraphs lose their indent and no longer read as belonging to it
(p.113 Table 3.10.A, p.155). One inspector called it major, one called it
the document-wide convention, one flagged only the inconsistency with the
`<p>`-based cell on p.156. It is how the pipeline has always rendered
in-cell bullets — including on both shipped cards — so changing it is a
D17 presentation decision, not a bug fix.

**Convergence state:** gates 0 majors (FN1 1 declared source defect, T1 22,
TB2 1 seam advisor); fable `L1 31`/`T1 44`, opus `T1 13`; seam audit 0;
mutation at baseline; 7/8 rendered-page assertions pass (the 8th targeted
the wrong card and passed once retargeted).
