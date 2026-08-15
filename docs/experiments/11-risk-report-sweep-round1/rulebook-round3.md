# Risk-report inspector rulebook — ROUND 3 (rr-sweep3, ship gate)

Same design as the round-1 rulebook in this directory; read that one for the
method. This file supersedes it for round 3 and differs in two ways that
matter, both from a process failure found in round 2:

1. **This rulebook describes the PDF, never the fixes.** Round 2's prompts
   told inspectors what the repaired output should look like, so they could
   only confirm the repair instead of comparing against the source. If a
   construct is wrong, the PDF is the only authority.
2. **The do-not-flag list holds OWNER decisions only.** Round 1's list had
   entries the orchestrator had adjudicated itself; those are removed. If
   you think something is wrong, flag it — an orchestrator's earlier
   judgement is not evidence.

## Inputs

- PDF page renders: `cards/anthropic/risk-report-2026-08/extracted/pages/p-NNN.png`
- Per-page md slices: `pipeline/.cache/rr-sweep3/slices/p-NNN.md`
- Served HTML snapshot: `pipeline/.cache/rr-sweep3/served.html` (whole card,
  one page — grep for a distinctive phrase to find your region)
- High-zoom crops for any dense construct (REQUIRED before judging
  glyph-level detail — full pages are vision-downscaled):
  `env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/render_region.py PAGE [x0 y0 x1 y1] [ZOOM]`
  → `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`, then Read it. Repo root.

## Page → section map

| file | pages |
| --- | --- |
| (cover p.1, contents pp.2–6 — not converted, by design) | 1–6 |
| 01-introduction.md | 7–16 |
| 02a-autonomy-misalignment-1.md | 17–35 |
| 02b-autonomy-misalignment-2.md | 36–64 |
| 02c-autonomy-misalignment-3.md | 65–92 |
| 03-automated-rd.md | 93–114 |
| 04a-chem-bio-1.md | 115–134 |
| 04b-chem-bio-2.md | 135–157 |
| 05-cross-cutting.md | 158–174 |
| 06-appendices.md | 175–186 |

## DO NOT FLAG — owner-adjudicated only

1. **Page markers / `<!-- source: -->` comments** are infrastructure.
2. **Raw `<table>` HTML in md** is by design; a multi-page table is stitched
   into ONE table, and a header row the PDF reprints on the continuation
   page appears once (print artifact, deduped).
3. **Footnotes render as sidenotes/margin notes**, not at the page bottom.
4. **Internal links resolve to heading anchors**, not page numbers.
5. **Green `[…]` pills** render as `<span class="ph">`.
6. **p.126's superscript 18** has no footnote anywhere in the document (a
   source artifact); it renders as a bare `<sup>18</sup>` deliberately.
7. **p.22's rating cells** drop the PDF's green/red/yellow background tints
   (owner decision 2026-08-15: the cell text carries the rating).
8. **p.36's code span** renders uniformly green where the PDF sets `sed`
   black (owner decision 2026-08-15: ignore).
9. **Literal `*` / `` ` `` inside quoted model output** are source content
   and appear backslash-escaped in md — correct, not a defect.
10. Curly vs straight quotes coming from PDF spans are source-faithful.

Everything else is fair game, including constructs an earlier round called
acceptable.

## Severity

- **major** — a reader is misled or loses content: text lost, garbled,
  duplicated, misplaced, or out of order; structure wrong (split/merged
  paragraph, item, heading, row; wrong list type or nesting; a quotation
  that does not read as a quotation); meaning-bearing styling lost (bold
  leads, italics, table headers, superscripts); table cells misplaced;
  figure/caption missing or mis-associated; page-seam damage.
- **minor** — a visible cosmetic nit that does not change meaning.

Calibration: this document has been through two sweep rounds, an owner
scroll pass, and ~23 commits of fixes since the last full inspection. Most
pages will be clean. Do not manufacture findings. But the fixes since the
last sweep touched **every table cell in the document** (cell alignment
tolerance), **every page marker** (a runtime layout pass), footnote
backlinks, quotations, and list/quote classification — so look hardest at:
tables (any page with one), page-marker placement vs where the page truly
starts, footnote refs and their ↩ backlinks, blockquotes, and lists.

## Output

Append to YOUR findings file (path in your task) ONE JSON line per page (or
per file, for linters) AS YOU FINISH IT — never batch at the end.

    {"page": 42, "status": "clean"}
    {"page": 43, "status": "flagged", "findings": [{"severity": "major",
     "construct": "table", "desc": "row 3 values shifted one column left",
     "evidence": "crop p43-90x300.png vs <tr> in served.html",
     "verdict": "confirmed"}]}

`construct` ∈ table | list | turn | figure | caption | heading | paragraph |
footnote | link | pill | code | seam | marker | other.
`verdict` ∈ confirmed | uncertain | source-faithful.

Final message: 3 lines — pages covered, counts by severity, anything you
could not check and why.
