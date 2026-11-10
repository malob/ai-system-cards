# Experiment 21 — claude-fable-5-2 inspection sweep (2026-11-09)

**Question:** after the automated gate converged at 0 unsuppressed majors on
the seventh card (anthropic/claude-fable-5-2 — Claude Fable 5.2 & Claude Mythos
5.2, 264pp, same Google-Docs export family, D75), what does the layer-2 agent
inspection find that the gates cannot see?

**Method:** the experiment-18 design, re-rulebooked for this card
(`rulebook.md` here): 8 triple-pane comparators over all 257 content pages
(PDF render vs md slice vs served production HTML, zoom crops for dense
constructs) + 3 markdown-smell linters over the 13 section files, reading a
SNAPSHOT of the sections so the orchestrator could fix in parallel. Inputs:
`pipeline/.cache/f52-sweep1/` (slices from `slice_pages.py`, `served.html`
copied from the production build, `sections/` snapshot). The findings files
are copied into `findings-round1/` (the cache is gitignored).

**Context going in:** gate at 0 unsuppressed majors (2 exact p.259
stream-order residuals), typed T1 3; L2 96/96; P2/F3 257/132; RF1 clean; seam
audit 0; fast release gate green with seven cards. One construct was already
known and fixed during the sweep (rulebook item 10): p.104's white tool-call
panels.

## Round 1 result

11 agents, 270 units (257 pages + 13 files), 245 clean. 13 major findings
(all confirmed), 12 confirmed minors, 1 uncertain, 13 `source-faithful` notes.
Overlaps between comparators and linters collapse the majors to five
distinct classes, plus the known p.104 class — none visible to the gates
(structure, quote nesting and seam placement are below T1's token resolution;
the hyphen join ran identically on both T1 sides):

| class | pages | root cause → fix |
| --- | --- | --- |
| white mono tool-call panels as inline code, a literal `<span class="ph">` in backticks (known going in) | 104 | a `#ffffff` panel nested in a turn/transcript box whose text is ALL monospace is a code box; adjacent code boxes keep their own `<pre>` (assemble flags each further box's first line, serialize splits); wide line-height placeholder fills (313–400pt × 11.9pt — between the pill and box extractors' caps) mark their pills from the oracle `fills` key. Certified: one opus-5 hunk (p.97 '[tool use]' becomes its own code box, as drawn) |
| METR quote's ○ sub-bullets escape the blockquote (quote split into fragments, nesting lost) | 39–42 | inside a quote the sub-list steps 18pt, so a ○ sits 10.5pt from its 36pt-grid home and failed `shift_ok` → a deeper item directly under a quoted item is quoted too, carried across the page break (p.42 opens on a ○) |
| two bold lines merged into one paragraph | 40 | '2) Summary of findings' has no end punctuation (bold-lead test) and the next line is bold too (label test) → two all-bold lines break when the next line's first word would have fit |
| 'no-chain-of- thought' (mid-line hyphen-space) joined to 'no-chain-ofthought' | 44 | the A1 wrap join ran on joined text, so a mid-line hyphen-space joined like a line-end one — identically on both T1 sides → a same-length guard on mid-span hyphen-spaces, both sides (`norm.guard_inline_hyphens`). Corpus census: one other occurrence, certified — risk-report p.181 'Opus- and Sonnet- class' (the wrap falls after 'and'; canon had 'Sonnet-class') |
| a bullet's continuation paragraphs rendered as blockquotes | 102 | the 106–112 band is a quote unless a list on the page claims the tier; this bullet's marker is on p.101 → an item left open at a page's end lends its tiers to the next page |
| two paragraphs merged across a page seam, marker two lines late | 164–165 | after absorbing p.165's first paragraph the merged block still reported p.164, so 'However…' re-qualified as a continuation; a trailing ZWSP also hid the period → one page-top continuation per block, invisibles stripped before the terminator test |
| code-box label `None` emitted as the first blocklist line | 259 | the label carries U+200E → bidi marks join `norm.INVISIBLES` (the corpus's only one) and the label test strips invisibles |

**Minors fixed:** p.105 two adjacent pills merged (a wrapped pill piece took
the next pill's close bracket → it ends at the first close with no open
before it).

**Not fixed, recorded:** caption underlines whose PDF extent includes the
trailing period (pp.74, 79, 87, 88 — the caption path trims punctuation by
design; the Gemini deferred class); footnote 1's internal line break (p.14);
p.258's `<p>`-wrapped seam-merged cell (the opus-5-5 p.225 TB2 class).

**Source-faithful (rulebook growth):** 'C. trachomatis' / 'C. caviae' and
'78-YEAR-OLD' are inside Lora-Italic spans in the text layer (the comparators
read the capitals as upright); p.112 '**Overrefusa**l'; the p.82 near-duplicate
sentence; p.39 'AI R&D - relevant'; mixed `-`/`–` in Table 8.1; footnote 12
repeating footnote 11's text; p.209's run-on; plain 'medium'/'high' on p.209;
two blocklist URLs wrapped as the PDF wraps them; 'system cards' styled as a
link with no annotation (p.245).

**Regression net:** every class regenerated all six certified cards. Two
certified hunks moved, both PDF-verified fidelity improvements awaiting owner
adjudication: opus-5 p.97 (`[tool use]` in its own code box) and
risk-report p.181 ('Sonnet- class'). Everything else byte-identical.

## Round 2 result (fix verification)

3 comparators over the 12 fix pages (39–42, 44, 102–105, 164–165, 259) plus
15 seeded clean pages (`random.seed(21)` over the content pages less the fix
pages: 55, 59, 68, 85, 124, 138, 139, 146, 148, 152, 181, 195, 221, 225, 234),
`rulebook-round2.md`, inputs `pipeline/.cache/f52-sweep2/` (findings copied to
`findings-round2/`): **27/27 clean**, every fix confirmed in the served HTML,
no regression on the sample. One more source-faithful note: p.42 '(LMCA)'
looks upright but sits in a Lora-Italic span.

## Rendered visual pass (experiment 19 method)

- **DOM audit** (browser pane, production build): 1338px — 257 page labels,
  0 overlaps, 132 images decoded, no horizontal scroll, nothing wider than the
  column; 1680px — 25 sidenotes, 0 sidenote/sidenote, sidenote/label or
  sidenote/body overlaps; 375px — no horizontal scroll, nothing outside its
  scroll wrapper (gutter labels hidden by design).
- **Construct screenshots** (`shoot.py` here: experiment 19's, made resumable —
  a 264-page card takes ~25 s per full-page clip): 35 constructs (18 tables, 13
  transcript boxes, 4 code boxes), three reviewer agents vs the PDF
  (`visual-findings.jsonl`): **0 major, 3 minor**, all known classes — the
  p.74 caption underline stops before its period (the deferred caption
  punctuation class), p.82's '(Helpful-only)' loses its smaller in-cell size
  (an in-cell type tier the renderer does not express; the same table on the
  certified cards), and p.258's `<p>`-wrapped seam cell (the opus-5-5 TB2
  class).
- **Certified hunks** (`hunks.py` here): one PDF | live | new composite each in
  `hunks/` — opus-5 p.97 (`[tool use]` in its own code box, as drawn) and
  risk-report p.181 ('Sonnet- class' as printed).

## Mutation evidence

All six certified replays (seed 5, 8 per class) are byte-identical to their
committed baselines after every batch in this experiment, including opus-5 and
the risk report with their one-hunk canon moves. The new card's baseline,
generated on its final canon: 24 classes / 192 trials, 177 detected / 169
intended-major / 171 major-blocked; misses in the known weak classes (ST2
split-item 1/8, as on opus-5-5; ST1 6/8; ST3 6/8 detected; L1 6/8; S1 6/8;
advisory swap-words).

**Conclusion:** converged — round 1's five major classes and one known class
fixed at the class level, round 2 clean, visual pass clean of majors. Owner
items: the two certified hunks (composites above) and the deploy decision.
