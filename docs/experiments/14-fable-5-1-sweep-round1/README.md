# Experiment 14 — claude-fable-5-1 inspection sweep, round 1 (2026-09-01)

**Question:** after the automated gate converged at 0 unsuppressed majors on the
fourth card (anthropic/claude-fable-5-1 — Claude Fable 5.1 & Claude Mythos 5.1,
212pp, same Google-Docs export family as the three certified documents), what
does the layer-2 agent inspection find that the gates cannot see — and does the
sweep design hold for the card's new constructs (2×2 merged header corners, a
seven-page rowspan table cut at every page seam, a three-page code box, a
publisher's stray-size glyph inside a caption)?

**Method:** the two-check round-G design (experiment 09), re-rulebooked for this
card (`rulebook.md` here): 8 triple-pane comparators over all 206 content pages
(PDF render vs md slice vs served HTML, zoom crops for dense constructs) + 3
markdown-smell linters over the 11 section files. Inputs:
`pipeline/.cache/f51-sweep1/` (slices, served.html, findings-*.jsonl). Findings
are re-runnable from the rulebook + this README alone.

**Context going in:** gate at 0 unsuppressed majors (5 exact accepted seam /
stream-order residuals, D62), typed T1 4; L2 66/66; P2/F3 206 pages / 103
figures; RF1 30/30; seam audit 0; fast-release gate green with four cards; strict
mutation baseline 178 / 170 / 170 over 24 classes / 192 trials. The D62 onboarding
fix batch (three table-repair classes, list re-tier after stitch, four projection
classes) had landed with all three certified cards byte-identical.

**Result:** 11 agents, 217 units (206 pages + 11 files), 190 clean, 27 flagged.
10 major findings (5 distinct, all confirmed against zoom crops), 55 minors — of
which 38 are `source-faithful` reports that grow the rulebook (`rulebook-round2.md`
records them), 6 uncertain, and the rest confirmed cosmetic. The gates could see
none of the majors (table structure, caption extent, emphasis delimiters, and
page-seam grouping are below T1's token resolution) — the layer-2 charter.

Distinct major classes and their class-level fixes (commit `2340278`; every fix
regen-verified with ALL THREE certified cards byte-identical; D63):

| class | pages | root cause → fix |
| --- | --- | --- |
| merged header corner emitted as empty cells | 88, 167 (+ the §4 tables' 'Model' over their sub-header rows) | docling emits empty grid cells for one drawn 2×2 cell → `tables._merge_cells_by_fill`: one fill rect under the non-empty cell that also covers the empty cell proves colspan/rowspan; the oracle gains an additive `fills` key; per-card knob `merge_cells_by_fill` (certified corners await owner adjudication, D46 precedent) |
| two-row label without rowspan | 167 | `_promote_split_rowspan` needs a sibling rowspan-2 as proof; none in Table 8.1.A → same fill-geometry rule (rowspan from the label's fill) |
| caption split after its first line | 199 | a publisher's 11pt 't' inside a 9pt caption raised the line's MAX size → continuation judged by the line's DOMINANT (char-weighted) size |
| literal `**` in a bold lead | 106 | `**…behavior—**most`: CommonMark cannot close on punctuation before a word char → such a run is emitted as raw `<b>` (link-edge pieces exempt) |
| page-seam rows of a rowspan table stranded | 207–209 | Google Docs does not repeat a spanned label after a page break; the fragment's empty-lead rows stayed unlabeled, and on p.209 the repeated header row was promoted to a rowspan that stripped the continuation's lead → `_merge_tables` extends the host's last GROUP START by the non-flowing empty-lead rows; `_promote_split_rowspan` skips all-header rows |
| three-page code box as two fences | 210–212 | the stitch adjacency test used the block's first page → tests the last merged page |

Also fixed: p.100 `admin / admin123` (Inconsolata joins the mono font set).
Tried and reverted: `link_text_resolution: extended` for 'Appendix 9.1' (p.142) —
L2's source-first geometry binds the PDF destination to the parent '9 Appendix'
heading that shares p.206's top with 9.1, and rejected the text target; the
knob is for wrong destinations, not coarse ones.

**Regression net:** the first version of the seam rule also claimed the
mid-sentence continuation rows of fable-5's nine-page welfare table and the risk
report's p.115→116 row; the first bold fallback re-emitted every
`[**Claim N**](#…)**:` piece in fable/opus/risk. Both were caught by byte-identity
within one regeneration and tightened (flow test; link-edge exemption).

**Deferred as typed minors (owner list):** p.159 `<p>`-wrapped seam-merged cells
(TB2 class); p.207 a wrapped internal link as two adjacent anchors with one
correct target; p.55 link span excluding the trailing comma the PDF's link rect
covers; p.59 'Fable 5.1/ Mythos' wrap space (the PDF's text layer carries it);
the renderer's typographer curling the straight quotes of the p.95–96 shell
command (site-wide); the 'Transcript' chrome on the label-less §6.1.3 boxes (site
styling, as for the risk report).

**Post-fix state:** gates 0 unsuppressed majors (5 exact) + T1 4 typed; L2 66/66;
seam audit 0; L2 and source-projection artifacts regenerated; all three certified
cards byte-identical. Round 2 (fresh `f51-sweep2/` inputs, `rulebook-round2.md`):
fix-verification comparators over the ~35 affected pages + a rotating clean
sample; mutation replays for all four cards follow.

## Round 2 (same day) — fix verification + rotating sample

Inputs `pipeline/.cache/f51-sweep2/` (fresh slices and served snapshot after
commit `2340278`); rulebook `rulebook-round2.md`. Three agents, 49 units
(`findings-fixver1.jsonl` 18 table-header pages, `findings-fixver2.jsonl` 16
other fixed pages, `findings-sample2.jsonl` 15 pages clean in round 1): **48
clean, zero regressions.** Every fix was confirmed against zoom crops and the
served DOM — the 'Model' rowspan on the §4 tables, the 2×2 corners on pp.85–87
and 167, the two-row 'Humanity's Last Exam' label, the p.100 code span, the
p.106 bold lead, the whole p.199 caption, all 17 Table 9.1.A groups with rowspans
equal to their question counts, and the single 75-line blocklist fence.

One residual major: p.88 Table 5.2.2.3.A's corner was still split. Root cause:
`_split_glued_cells` indexes one span per squash text, so the prefix of the wrapped
header resolved to the neighbouring column's identical first line — to the right,
so the side-by-side guard passed — and the corner's empty cell swallowed the
second line before `_merge_cells_by_fill` ran. Fixed with a reading-order guard
(the prefix piece must be the left one; D64, commit after `2340278`), regenerated
with the certified cards byte-identical, and verified directly in the regenerated
section (`<th colspan="2" rowspan="2">Model</th>` over `Attempts | Scenarios`),
the same way the round-1 residuals were closed in experiment 11.

**Convergence state:** gates 0 unsuppressed majors (5 exact) + T1 3 typed; L2
66/66; seam audit 0; all three certified cards byte-identical; the fast-release
gate green with four cards; the fourth card's strict mutation baseline regenerated
on the final canon (24 classes / 192 trials). Remaining items are the deferred
typed minors (owner list above) and the owner scroll pass (onboarding step 9).
