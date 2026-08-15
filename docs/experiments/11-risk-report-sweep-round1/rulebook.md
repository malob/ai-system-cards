# Risk-report inspector rulebook (rr-sweep1)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/risk-report-2026-08/sections/` (raw-HTML tables, `:::caption`
directives, `<span class="ph">` placeholder pills, `<!-- p.N -->` page
markers), rendered to a single web page (snapshot provided). You surface
findings; you NEVER edit or fix anything. The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/risk-report-2026-08/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/rr-sweep1/slices/p-NNN.md` — every md run
  attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Served HTML snapshot: `pipeline/.cache/rr-sweep1/served.html` (the whole card
  is ONE page). Find your region by grepping distinctive phrases from the
  slice (e.g. `grep -n -A5 'phrase' served.html`, or python). This pane shows
  what the reader actually gets: check structure (tags, list types, table
  cells, `<b>`, `<sup>`, `<span class="ph">`, blockquote nesting) — it is the
  arbiter when md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense boxes, small text,
  styling questions). Full-page renders are vision-downscaled (~1.15MP) — do
  NOT judge glyph-level detail (bold extents, superscripts, decimals) from a
  full page. Render a crop first:
  `env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root.

## Page → section map

| file | pages |
| --- | --- |
| (cover — NOT converted, by design) | 1 |
| (table of contents — NOT converted, by design) | 2–6 |
| 01-introduction.md | 7–16 |
| 02a-autonomy-misalignment-1.md | 17–35 |
| 02b-autonomy-misalignment-2.md | 36–64 |
| 02c-autonomy-misalignment-3.md | 65–92 |
| 03-automated-rd.md | 93–114 |
| 04a-chem-bio-1.md | 115–134 |
| 04b-chem-bio-2.md | 135–157 |
| 05-cross-cutting.md | 158–174 |
| 06-appendices.md | 175–186 |

## DO NOT FLAG — adjudicated, by design (carried from rounds G/10 + this card)

1. **Literal markup in boxed prompts/reviews**: `*`, `` ` ``, `**` appearing
   as characters in box content are IN the PDF and must render literally. In
   md they appear backslash-escaped (`\*`, `` \` ``) — correct, not a defect.
2. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   sub-labels — visually identical; don't flag th-vs-td when the rendered
   weight matches the PDF.
3. **Green placeholder ranges** render via raw `<span class="ph">…</span>`
   (green pill, matches the PDF's `[…]` pills). DO flag PDF green pills with
   NO ph span, or ph spans covering wrong text.
4. **`:::caption` blocks** = figure/table captions, uniform gray render. By
   design.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
6. **Raw `<table>` HTML in md** is by design. Multi-page tables are stitched
   into ONE table — a "missing" page break inside a table is correct, and a
   table-header row REPEATED on the continuation page in the PDF (pp.10–14,
   115, 155–156, 182–185 etc.) appears ONCE in the stitched table — the
   repeat is a print artifact, deduped by design.
7. Smart quotes / typographic glyphs in md come straight from PDF spans —
   don't flag curly-vs-straight. Docling table-cell text may normalize odd
   punctuation (low-9 comma ‚ → ,) — known typed residual, don't re-flag.
8. **p.126 superscript 18** after 'Catastrophic biological scenario uplift
   trial' renders as a plain `<sup>18</sup>` with no footnote link: the
   document defines no footnote 18 anywhere (its numbering runs 57→58 here) —
   a source artifact, kept as a bare superscript by design.
9. **Unlabeled cream boxes** (§2.20 prompt + Claude's review pp.72–74; §2.24
   prompt pp.84–86) render as label-less bubbles (`.turn` with no
   `.turn-label`); the left accent color is site styling, not attribution.
   The p.86 continuation bubble carries the PDF's bold lead 'Output format'
   as its label — bold-lead parity, accepted. DO flag wrong/invented speaker
   labels or box content merged into surrounding prose.
10. **p.22 rating-cell background tints** (green/yellow/red) are dropped —
    declared exclusion; the cell TEXT carries the rating. DO flag wrong cell
    text/placement. (Owner sees this page in the scroll pass.)
11. **Footnote defs render as sidenotes/footnotes at the section end** — the
    body position differs from the PDF's page-bottom placement by design.
    Long footnotes quoting whole paragraphs (pp.50, 117) are genuine
    footnotes in the PDF, not body text.
12. **Internal section links** resolve to heading anchors (`#22-threat-model`)
    instead of page numbers — by design. DO flag links pointing at the WRONG
    section, or PDF links missing entirely.
13. **Lettered sub-lists**: md keeps literal `a.` / `b.` bullet text; the
    RENDERER converts consecutive lettered bullets to `<ol type="a">`. DO
    flag if the DOM fails to show lettered numbering where the PDF has it.

## Severity

- **major** — a reader is misled or loses content: text lost / garbled /
  duplicated / misplaced; structure wrong (split or merged paragraph, item,
  heading, table row; wrong list nesting or type; wrong quote nesting);
  meaning-bearing styling wrong (bold leads, green pills, table headers,
  superscripts); broken table cell placement or merges; figure/caption
  missing or mis-associated; page-seam damage (mid-sentence hard break, lost
  line, unstitched continuation).
- **minor** — visible cosmetic nit (spacing, marginal typography) that does
  not change meaning.

Calibration: the automated gate converged at 0 majors and this is the THIRD
card through the pipeline; most pages will be clean. Do not manufacture
findings — "clean" is a perfectly good verdict, and false positives cost
orchestrator time. But DO look hard: on the previous card this layer found 15
real majors the gates could not see (scrambled table rows, phantom turn
boxes, flattened list nesting). Table-heavy pages (10–14, 22, 78–80, 93–94,
113–119, 123–132, 155–156, 182–185) and the boxed-content pages (72–74,
84–86) deserve the closest look; footnote-heavy pages (36–37, 50, 117,
122–125) had oracle-side fixes this round — verify their defs against the
page bottom.

## Output

Append to YOUR OWN findings file (path in your task) ONE JSON line per page
(comparators) or per section file (linters), AS YOU FINISH EACH UNIT — never
batch at the end (your run may be killed; partials must survive). Schema:

    {"page": 42, "status": "clean"}
    {"page": 43, "status": "flagged", "findings": [{"severity": "major",
     "construct": "table", "desc": "row 3 values shifted one column left",
     "evidence": "crop p43-90x300.png vs <tr> in served.html: 41.8% under
     wrong model", "verdict": "confirmed"}]}

(linters use "file" instead of "page", and include "page" inside each
finding.) `construct` ∈ table | list | turn | figure | caption | heading |
paragraph | footnote | link | pill | code | seam | other. `verdict` ∈
confirmed (you verified against the page render/crop) | uncertain (needs
orchestrator eyes) | source-faithful (looked sus, PDF agrees — report so the
rulebook can grow).

Append safely from repo root, e.g.:
    python3 -c "import json; open('pipeline/.cache/rr-sweep1/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
