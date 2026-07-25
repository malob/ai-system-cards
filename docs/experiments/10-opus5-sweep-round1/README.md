# Experiment 10 — claude-opus-5 inspection sweep, round 1 (2026-07-25)

**Question:** after the automated gate converged at 0 majors on the second card
(claude-opus-5), what does the layer-2 agent inspection find that the gates
can't see — and do the round-G sweep design + rulebook generalize to a new
document?

**Method:** the two-check round-G design (experiment 09), re-rulebooked for
this card (`rulebook.md` here): 8 triple-pane comparators over all 187 content
pages (PDF render vs md slice vs served HTML, crops for dense constructs) + 3
markdown-smell linters over the 12 section files. 199 findings lines
(`findings.jsonl`, one per page/file), each finding verified by its inspector
against the page render before reporting.

**Result:** 158 clean units. 15 confirmed majors in 8 classes, all with
mechanical root causes; ~12 confirmed minors; ~25 source-faithful reports
(defects present in the PDF itself, kept verbatim by design — the rulebook
grows these). The major classes and their fixes (all class-level, in
`pipeline/`, each verified against BOTH cards):

| class | pages | root cause → fix |
| --- | --- | --- |
| table rows scrambled | 52, 56, 69 | docling hallucinated wraps + rotated fragments; no cell matched a span so the repair's band anchor failed → substring-containment band fallback, `_rebuild_row` under char-multiset equality |
| column shift in merged table | 149 | continuation fragment lacked the host's label `colspan` → fragment rows normalized to host modal shape (rowspan-continuations exempt) |
| phantom transcript | 137–138 | line-height cream strip classified as a turn box → boxes under 20pt are inline highlights (`.hl` spans), text flows in its paragraph |
| list nesting flattened | 83, 104 | ■ (U+25A0) not in the bullet set; Word-style `o​` marker unknown → both added |
| spurious quote bars | 83 | x0-only quote test can't tell quoted-L0 from nested-L1 bullets → glyph-tier shift check (≥12pt beyond the glyph's home column) |
| fabricated link | 81 | partial-span link fallback matched a sloppy GoTo rect from the stitched block's other page → fallback is URI-only + anchor-text snapping |
| heading outranks parent | 10 | the doc's own `1.1.` trailing-dot typo defeated HEAD_NUM → dot tolerated |
| lettered list defeated | 44 | inline page marker before `a.` made remark parse the line as raw HTML → marker emitted after the letter |

Plus: bold-label split defeated by a trailing ZWSP span (14), and mark
coalescing bridging a non-space gap merged two code spans (193) — both fixed.

**Open (typed or deferred, owner-visible):** docling table char normalization
(curly quotes/dashes → ASCII, ~27 T1 minors, same class as fable-5's accepted
p.243 family — candidate for a shared tables.py repair); italic-in-table-cell
unsupported (bold-italic sub-labels render bold-only, pp.71/148); one missed
bold cell (p.75); stacked cell lines joined without breaks (p.31); the BBQ
example quotations render flush instead of indented (p.64); appendix code-box
`None` language chrome rendered as fence content (pp.191–193); a lost blank
line inside a mono box (p.85); adjacent `.hl` spans split at line wraps
(cosmetic).

**Conclusion:** the sweep design transfers to a new document unchanged; the
rulebook needed only path/page-map/accepted-list edits. Every major had a
mechanical class fix — none required hand-editing output. Round 2 (fix
verification + rotating sample) ran after the fix batch; see git history for
its result.
