# Opus 5.5 inspector rulebook (o55-sweep2)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/claude-opus-5-5/sections/` (raw-HTML tables, `:::caption`
directives, `<!-- p.N -->` page markers), rendered to a single web page
(snapshot provided). You surface findings; you NEVER edit or fix anything.
The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/claude-opus-5-5/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/o55-sweep2/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Served HTML snapshot: `pipeline/.cache/o55-sweep2/served.html` (the whole
  card is ONE page, production build). Find your region by grepping
  distinctive phrases from the slice (e.g. `grep -n -A5 'phrase' served.html`,
  or python). This pane shows what the reader actually gets: check structure
  (tags, list types, table cells, `<b>`, `<u>`, `<sup>`, blockquote nesting)
  — it is the arbiter when md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense boxes, small text,
  styling questions). Full-page renders are vision-downscaled (~1.15MP) — do
  NOT judge glyph-level detail (bold extents, underlines, decimals,
  superscripts) from a full page. Render a crop first:
  `env CARD=anthropic/claude-opus-5-5 uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=anthropic/claude-opus-5-5 uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root. Other inspectors run in parallel and write crops to the same folder;
  that is fine (names are page+bbox keyed).

## Page → section map

| file                          | pages   |
| ----------------------------- | ------- |
| (cover — NOT converted)       | 1       |
| 00-executive-summary.md       | 2–4     |
| (table of contents — NOT converted) | 5–10 |
| 01-introduction.md            | 11–13   |
| 02-rsp-evaluations.md         | 14–46   |
| 03-cyber.md                   | 47–60   |
| 04-safeguards-harmlessness.md | 61–78   |
| 05-agentic-safety.md          | 79–91   |
| 06a-alignment-1.md            | 92–121  |
| 06b-alignment-2.md            | 122–150 |
| 07-model-welfare.md           | 151–173 |
| 08a-capabilities-1.md         | 174–188 |
| 08b-capabilities-2.md         | 189–221 |
| 09-appendix.md                | 222–230 |

## DO NOT FLAG — adjudicated, by design (carried from earlier cards + this card)

1. **Literal markup characters**: `*`, `` ` ``, `<` that the PDF shows as
   characters appear backslash-escaped in md (`\*`, `` \` ``, `\<`) and
   render literally — correct. p.102's prose `` `gsutil -m rm -r [path]` ``
   is set in the body serif in the PDF with literal backticks; the web page
   shows the backticks in body text by design.
2. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   row labels — visually identical; don't flag th-vs-td when the rendered
   weight matches the PDF. Dark sub-header rows ('API, without a system
   prompt' / 'Claude.ai') are `<th>` rows by design.
3. **Green placeholder pills** (p.98, inside Transcript 6.2.1.B: '[a phrase
   quoted from the task statement]', '[one requirement of the task]') render
   as `<span class="ph">…</span>` pills — by design. There are NO smart chips
   in this document; DO flag any other green pill or chip-like label in a PDF
   render that the md lacks.
4. **`:::caption` blocks** = figure/table/transcript captions, uniform gray
   render. By design.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
6. **Raw `<table>` HTML in md** is by design. Multi-page tables are stitched
   into ONE table — a "missing" page break inside a table is correct, and a
   header row REPEATED on the continuation page in the PDF (Table 9.1.A
   pp.222–226) appears ONCE in the stitched table. Table 9.1.A's 'Training
   still to come' question is cut mid-cell by the p.225/226 break — in the web
   table it is one complete cell, by design; its group label spans all six
   questions.
7. Smart quotes / typographic glyphs in md come straight from PDF spans —
   don't flag curly-vs-straight. Docling table-cell text may normalize odd
   punctuation — known typed residual, don't re-flag.
8. **Merged header corners**: a dark 'Model' / 'Evaluation' corner the PDF
   draws as one cell over two header rows (and two label columns in Table
   8.1.A p.174) is a `rowspan`/`colspan` cell by design. DO flag an empty
   cell where the PDF draws one merged cell, or a merge the PDF does not have.
9. **Unlabeled cream boxes**: the §6.1.3 prompt + Claude's review (pp.95–96)
   and Transcript 6.2.1.B (p.98) render as label-less bubbles; the left accent
   color is site styling, not attribution. p.98's bold inline lead
   'Assistant (thinking):' becomes that bubble's label (the turn-label
   convention of the earlier cards) — by design. DO flag invented speaker
   labels or box content merged into surrounding prose.
10. **§9.2 blocklist** (pp.226–230) is one visual code box across pages (one
    fence per PDF page in md, joined by the renderer with the page label
    inside at the true page turn); its info string `None` is the PDF's gray
    code-box language label. Whether the DOM shows the `None` label is not a
    finding. DO flag missing, garbled, or re-ordered blocklist lines.
11. **Footnote defs render as sidenotes/footnotes** — the body position
    differs from the PDF's page-bottom placement by design. Footnotes 11 and
    12 (pp.136–137) are set in the PDF at body type size; they are still
    footnotes (below the footnote rule) and must render as such.
12. **Internal section links** resolve to heading anchors (`#22-cb-evaluations`)
    instead of page numbers — by design. DO flag links pointing at the WRONG
    section, or PDF links missing entirely.
13. **Green monospace effort levels** (`max`, `xhigh`, `low`, …) render as
    inline code spans; the code color is site styling. DO flag a code span
    covering the wrong words.
14. Section-heading gray (#666666) and page-number footers are layout; the
    site draws its own heading styles and TOC. The bold black '2.3.5.3 AECI
    values and trend' line above Table 2.3.5.3.A (p.39) is a bookmarked
    heading in the PDF and renders as a heading — by design.
15. Charts and diagrams are raster images in this PDF; text inside them is not
    transcribed. A figure is correct when the right image sits with the
    right caption.

## Round-1 outcomes (experiment 18 README)

Fixed after round 1 — VERIFY each in the served DOM and a crop:
- p.42: the METR quote's underlined run ('This report was written … details of
  their reasoning.') and the word 'separate' in 'this separate investigation'
  are underlined (`<u>`), with the bold runs inside intact.
- p.98: the wrapped placeholder pill's second piece is exactly 'statement]';
  the ' —' after it is plain text.
- p.174: Table 8.1.A's two header rows are `<th>` in the header band
  ('Evaluation' 2×2 corner, 'Claude family models' colspan 3, 'Other models');
  the caption's Opus 5 System Card link carries no extra `<u>` and 'for' is
  not underlined.
- p.179: '--bare' is an inline code span.

Adjudicated source-faithful in round 1 — do NOT re-flag: duplicated clause
p.31; Figure 2.3.5.3.A/B citation p.40; 'USage Policy' p.56; italic '(LMCA)'
p.41; bold ')' p.57; caption bold extents pp.31/54; '11.13%--a' p.88;
'attackcovering' p.96; Figure 6.2.1.B/C citation p.99; 'Mythos' vs 'Fable'
naming p.15; underline on a non-second-best value p.71; bold+underline p.81;
missing caption period p.205; literal '[Figure 8.12.3.E]' p.197; italic '64.8'
p.178; p.166 '. .' (a stray publisher period line). Deferred typed minors, not
findings: p.225 `<p>` in the seam-merged cell; 'Transcript' chrome on
pp.95–96; p.228 wrapped blocklist entries as two lines.

## Severity

- **major** — a reader is misled or loses content: text lost / garbled /
  duplicated / misplaced; structure wrong (split or merged paragraph, item,
  heading, table row; wrong list nesting or type; wrong quote nesting);
  meaning-bearing styling wrong (bold leads, underlines that mark second-best
  scores, table headers, superscripts); broken table cell placement or
  merges; figure/caption missing or mis-associated; page-seam damage
  (mid-sentence hard break, lost line, unstitched continuation).
- **minor** — visible cosmetic nit (spacing, marginal typography) that does
  not change meaning.

Calibration: the automated gate converged at 0 majors and this is the FIFTH
card through the pipeline; most pages will be clean. Do not manufacture
findings — "clean" is a perfectly good verdict, and false positives cost
orchestrator time. But DO look hard: on earlier cards this layer found real
majors the gates could not see (scrambled table rows, merged header corners
emitted as empty cells, split captions, literal `**`, stranded seam rows).
Table-heavy pages (18, 39, 62–63, 66–67, 69, 71, 76–78, 80–82, 87, 89–90,
174, 211, 222–226), the boxed pages (95–96, 98), the blocklist (226–230), the
figure-dense alignment pages (98–150) and every footnote-bearing page deserve
the closest look; verify footnote defs against the page bottom.

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
    python3 -c "import json; open('pipeline/.cache/o55-sweep2/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
