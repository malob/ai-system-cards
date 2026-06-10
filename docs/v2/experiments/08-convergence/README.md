# Experiment 08 — convergence loop, rounds D–E (re-sweep → fix → verify)

**Question.** Does the autonomous loop (regen → re-slice → re-sweep → triage →
fix → repeat) converge: do vision-sweep major counts fall toward zero, and do
fixes hold under re-verification?

## Round D — full re-sweep (4 agents, fresh `vsweep2` slices)

Same protocol as experiment 07, against the regenerated output after the
round-C fixes. **Result: 25 majors / 88 findings** (sweep #1 baseline: 69
majors / 134) — a 64% major reduction, with sweep #1's biggest classes
(blockquote-lost, transcript-structure, caption split) at zero.

Round-D majors by class (findings in `pipeline/.cache/vsweep2/findings-0*.jsonl`,
agent ranges 2–81 / 82–161 / 162–241 / 242–319):

- **Table cell placement ×13** (pp. 51, 72, 77, 80, 82×2, 89, 91×2, 253×2,
  269, 297): docling row rotation, glued/missplit cells, fragment rows,
  truncated wrapped cells.
- **Table styling ×8** (pp. 72, 82, 86, 89, 95, 98, 252 + the p.73/79 pair from
  round C): legend-promised best-score bolds missing.
- **Footnote ×1** (p.133): fn15's cross-page continuation grafted onto fn16.
- **Structure ×2**: p.65 lettered sub-list collapsed; p.177 wrapped heading
  split.
- **Adjudicated source-faithful ×1**: p.43 literal `—` — present in the
  PDF itself (model's raw output); not a defect.

## Fix wave (all 24 actionable majors closed at the class level)

Table geometry (`pipeline/generate/tables.py`), one principled core: a row's
**y-band** is anchored by its uniquely-matchable cells, then every repair
reasons in page geometry —

1. `_merge_fragment_rows` — docling splits one tall row into several `<tr>`s;
   fragment cells are mid-chain runs of a column chain whose prefix is a cell
   of the previous row → merge upward (pp. 311/315 class).
2. `_split_glued_cells` — now requires side-by-side x-ranges (stacked lines
   are a wrapped cell, not a glue) and ignores fnref spans (p.253 class).
3. `_resplit_misjoined_cells` — two adjacent cells re-split at the true span
   boundary when neither matches but the concat does (p.82 `99.70% (±` class).
4. `_extend_truncated_cells` — a cell equal to a column-run prefix whose
   adjacent continuation is claimed by no cell gets the dropped lines back
   (p.72 `Claude Mythos [Preview]`, p.311 `conversations?`).
5. `_repair_rotation` — per-row pools restricted to the y-band (duplicate
   values like `N/A, N/A` no longer steal other rows' coordinates), argsort by
   x; `_rebuild_row` as last resort under **char-multiset equality** (pure
   re-segmentation; tolerates in-band fnref digits), cell count ≥ docling's
   (un-glue only, so x-overlapping wide columns never fuse).
6. `_restyle_cells` — geometric per-segment styling: each cell is greedily
   segmented into its row-band spans and each segment styled by its own
   span's flags (bold `97.88%` inside `97.88% (± 0.66%)`); near-uniform-bold
   suppression now ≥0.9 share (was ≤0.5, which silenced legend-promised
   bolds).
7. Matching robustness: HTML entities decoded (`&#x27;`), curly/straight
   quotes folded — comparison-only; output text always comes from oracle
   spans.
8. `_inject_fnrefs` absorbs the stray literal digit docling kept
   (`GDPval-AA 29` → `GDPval-AA<sup>[^29]</sup>`; same class fixed `Sonnet
   4.6 4` on p.51).

Non-table:

9. **Footnote continuation** (oracle + assemble + serialize + FN1): footnote
   lines now processed in visual order; unmarked small lines chained above a
   page's first marker are keyed `cont` and merged into the previous page's
   footnote (fn15/16, p.114). FN1 body-mismatch minors 2→1.
10. **Wrapped-heading continuation** (assemble + ST3 mirror): an unnumbered
    gray line hugging a heading (<6pt gap; body sits ≥8pt below) joins the
    heading (p.177). ST3 staying at 0 doubles as proof of no false merges.
11. **Lettered sub-lists**: `[a-z][.)]` + ZWSP recognized as list markers
    (p.65), with the marker's space restored on output.
12. Empty-block guard (stray `> ` on p.207) and caption bracket-lead spacing
    (`[Figure 6.5.4.3.A]Stealth` class — T1 minors 173→143).

Gate trajectory across the wave (majors): FN1 1→**0**, S1 4 (known sites),
ST1 1 (known), T1 6 (known chip-order/typed sites). T1 minors 198→143.
Model-name-displacement detector across all tables: 13→**0**.

## Round E — verification sweep (this round)

Two agents against fresh `vsweep3` slices (`pipeline/slice_pages.py`, now a
committed tool):

- **flagged set**: every page with a round-C/D major (30 pages) — verdict per
  prior finding + anything new.
- **random sample**: 30 untouched pages (seed 42) — no-regression estimate.

**Result:** see `findings-*.jsonl` in `pipeline/.cache/vsweep3/` and the
convergence report in `docs/v2/state.md`.

## Conclusion

Filled in after round E lands: the loop converges if the flagged set verifies
fixed and the sample finds no new major classes.
