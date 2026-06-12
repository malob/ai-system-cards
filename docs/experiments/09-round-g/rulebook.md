# Round G inspector rulebook (vsweep6)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/claude-fable-5/sections-v2/` (raw-HTML tables, `:::caption`
directives, `<span class="ph">` placeholder pills, `<!-- p.N -->` page
markers), rendered to a single web page (snapshot provided). You surface
findings; you NEVER edit or fix anything. The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/claude-fable-5/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/vsweep6/slices/p-NNN.md` — every md run
  attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Served HTML snapshot: `pipeline/.cache/vsweep6/served.html` (the whole card
  is ONE page). Find your region by grepping distinctive phrases from the
  slice (e.g. `grep -n -A5 'phrase' served.html`, or python). This pane shows
  what the reader actually gets: check structure (tags, list types, table
  cells, `<b>`, `<u>`, `<span class="ph">`, blockquote nesting) — it is the
  arbiter when md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense transcripts, small
  text, styling questions). Full-page renders are vision-downscaled (~1.15MP)
  — do NOT judge glyph-level detail (bold extents, underlines, decimals,
  superscripts) from a full page. Render a crop first:
  `uv run --with pymupdf python pipeline/render_region.py PAGE` (every
  docling table bbox on the page, zoom 5) or
  `uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root.

## Page → section map

| file | pages |
| --- | --- |
| 00-executive-summary.md | 1–3 |
| (table of contents — NOT converted, by design) | 4–10 |
| 01-introduction.md | 11–14 |
| 02a-rsp-process-chembio.md | 15–36 |
| 02b-rsp-aird-alignment.md | 36–57 |
| 03-cyber.md | 58–70 |
| 04-safeguards-harmlessness.md | 71–87 |
| 05-agentic-safety.md | 88–98 |
| 06a-alignment-intro-behavioral.md | 99–109 |
| 06b-alignment-audit-external.md | 109–133 |
| 06c-targeted-evaluations-1.md | 133–151 |
| 06d-targeted-evaluations-2.md | 151–162 |
| 06e-whitebox-analyses.md | 162–181 |
| 06f-reliability-1.md | 182–195 |
| 06g-reliability-2.md | 196–217 |
| 07a-model-welfare-1.md | 218–232 |
| 07b-model-welfare-2.md | 232–251 |
| 08a-capabilities-1.md | 252–264 |
| 08b-capabilities-2.md | 264–278 |
| 08c-capabilities-3.md | 279–291 |
| 08d-capabilities-4.md | 291–308 |
| 09-appendix.md | 309–319 |

## DO NOT FLAG — owner-adjudicated, by design (D24/D25, experiments 07/08)

1. **Chip/pill reading order, pp. 38/44/56/57**: drawn pills/legend text sit
   at PDF stream positions that differ from visual order; the md follows
   VISUAL order. Owner-accepted.
2. **Literal markup in transcripts**: `*`, `` ` ``, `**`, `—` appearing as
   characters in model-output transcripts are IN the PDF (raw model output)
   and must render literally. In md they appear backslash-escaped (`\*`,
   `` \` ``) — that escaping is correct, not a defect.
3. **Turn labels keep source brackets**: `[Assistant]:`, `[User]:`,
   `[Bottom left:]` etc. render with brackets, as printed.
4. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   sub-labels/covered-row labels — visually identical to header cells;
   accepted parity. Don't flag th-vs-td choices when the rendered weight
   matches the PDF.
5. **'With thinking' / 'Without thinking' bolds (pp. 95–98, 252)** are bold
   IN the PDF. Correct as rendered.
6. **'GDP.pdf' (p. 253)** is a real benchmark name, not a typo.
7. **§9.2 blocklist link cosmetics**: the PDF auto-linked bare domains; 31
   known anchor-text diffs are accepted (v1 parity).
8. **Lettered sub-lists**: md keeps literal `a.` / `b.` bullet text; the
   RENDERER converts consecutive lettered bullets to `<ol type="a">`. Literal
   letters in md = by design. DO flag if the DOM fails to show lettered
   numbering where the PDF has it.
9. **Green placeholder ranges** render via raw `<span class="ph">…</span>`
   (green pill, matches PDF green highlights). The raw HTML in md is by
   design. DO flag PDF green-highlighted ranges with NO ph span, or ph spans
   covering wrong text.
10. **`:::caption` blocks** = figure captions, uniform gray render; captions
    sit under their own figure (interleaved per figure). By design.
11. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
12. **Raw `<table>` HTML in md** is by design (merged cells need it).
    Multi-page tables are stitched into ONE table — a "missing" page break
    inside a table is correct.
13. **Cross-page transcript continuation role color** (e.g. p. 104): not
    inferable from the source; accepted as-is.
14. **Table row hover** was removed from the renderer deliberately.
15. **Code boxes with bold/green content** render as `<pre>` with `<b>` /
    ph spans (p. 182) instead of a fence. By design.
16. **Pages 4–10 (table of contents)**: not converted, by design.
17. Smart quotes / typographic glyphs in md come straight from PDF spans —
    don't flag curly-vs-straight.

## Severity

- **major** — a reader is misled or loses content: text lost / garbled /
  duplicated / misplaced; structure wrong (split or merged paragraph, item,
  heading, table row; wrong list nesting or type; wrong quote nesting);
  meaning-bearing styling wrong (bold model names, underlined best scores,
  green pills, turn roles/labels, table headers); broken table cell
  placement or merges; figure/caption missing or mis-associated; page-seam
  damage (mid-sentence hard break, lost line, unstitched continuation).
- **minor** — visible cosmetic nit (spacing, marginal typography) that does
  not change meaning.

Calibration: the pipeline has been through 6 convergence rounds; the page
mostly IS faithful. Expect most pages clean. Do not manufacture findings —
"clean" is a perfectly good verdict, and false positives cost orchestrator
time. But DO look hard: recent real catches were exactly one-of-a-kind
(a swallowed `<thinking>` opener, a half-bold model name `**Mythos** 5`).

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
    python3 -c "import json; open('pipeline/.cache/vsweep6/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
