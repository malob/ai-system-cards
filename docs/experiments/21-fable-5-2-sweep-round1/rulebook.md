# Fable 5.2 inspector rulebook (f52-sweep1)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/claude-fable-5-2/sections/` (raw-HTML tables, `:::caption`
directives, `<!-- p.N -->` page markers), rendered to a single web page
(snapshot provided). You surface findings; you NEVER edit or fix anything.
The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/claude-fable-5-2/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/f52-sweep1/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Section files (linters): read the SNAPSHOT in
  `pipeline/.cache/f52-sweep1/sections/`, not the live card folder — the
  orchestrator may be regenerating the live files while you work.
- Served HTML snapshot: `pipeline/.cache/f52-sweep1/served.html` (the whole
  card is ONE page, production build). Find your region by grepping
  distinctive phrases from the slice (e.g. `grep -n -A5 'phrase' served.html`,
  or python). This pane shows what the reader actually gets: check structure
  (tags, list types, table cells, `<b>`, `<u>`, `<sup>`, blockquote nesting)
  — it is the arbiter when md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense boxes, small text,
  styling questions). Full-page renders are vision-downscaled (~1.15MP) — do
  NOT judge glyph-level detail (bold extents, underlines, decimals,
  superscripts, quote glyphs) from a full page. Render a crop first:
  `env CARD=anthropic/claude-fable-5-2 uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=anthropic/claude-fable-5-2 uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
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
| 02-rsp-evaluations.md         | 14–45   |
| 03-cyber.md                   | 46–58   |
| 04-safeguards-harmlessness.md | 59–77   |
| 05-agentic-safety.md          | 78–88   |
| 06a-alignment-1.md            | 89–126  |
| 06b-alignment-2.md            | 127–157 |
| 06c-alignment-3.md            | 158–184 |
| 07-model-welfare.md           | 185–206 |
| 08a-capabilities-1.md         | 207–242 |
| 08b-capabilities-2.md         | 243–254 |
| 09-appendix.md                | 255–264 |

## DO NOT FLAG — adjudicated, by design (carried from earlier cards + this card)

1. **Literal markup characters**: `*`, `` ` ``, `<`, a leading `-` that the
   PDF shows as characters appear backslash-escaped in md (`\*`, `` \` ``,
   `\<`, `\-`) and render literally — correct (p.102 'Bash(python3:\*)').
2. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   row labels — visually identical; don't flag th-vs-td when the rendered
   weight matches the PDF. Dark sub-header rows (`#4d4c48`) are `<th>` rows by
   design.
3. **Green placeholder pills** (pp.93, 102–105, 142, 175: '[Claude Mythos
   5.2]', '[person]', '[…]', '[post]', '[typescript block: run_redblue.ts]',
   the pills inside p.104's code lines) render as `<span class="ph">…</span>`
   pills — by design. There are NO smart chips in this document; DO flag any
   other green pill or chip-like label in a PDF render that the md lacks.
4. **`:::caption` blocks** = figure/table/transcript captions, uniform gray
   render. By design.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
6. **Raw `<table>` HTML in md** is by design. Multi-page tables are stitched
   into ONE table — a "missing" page break inside a table is correct, and a
   header row REPEATED on the continuation page in the PDF (Table 9.1.A
   pp.255–259) appears ONCE in the stitched table. Table 9.1.A's question cut
   by the p.258/259 break ('…some other treatment, or a' / 'combination.') is
   one complete cell in the web table, by design.
7. **Quote glyphs print exactly as the PDF prints them (D73)** — curly where
   the PDF is curly, straight where it is straight; the site does no
   typographic conversion. DO flag a glyph that differs from the PDF, but
   only from a high-zoom crop.
8. **Merged header corners**: a dark 'Model' / 'Evaluation' corner the PDF
   draws as one cell over two header rows (and two label columns in Table 8.1
   p.207), and 'Our models' spanning three columns, are `rowspan`/`colspan`
   cells by design. DO flag an empty cell where the PDF draws one merged
   cell, or a merge the PDF does not have.
9. **Transcript boxes**: the cream (`#faf9f5`) boxes on pp.93–94 (the human
   prompt + Claude's review) and pp.102–103 (quoted model output) render as
   label-less bubbles inside a 'Transcript' box — the box label and the left
   accent color are site styling, not attribution. Bold inline leads
   ('[System prompt]', '[User]', '[Assistant]') become the bubble's label
   (pp.104–105, 142, 175) — by design. DO flag invented speaker labels, a
   wrong speaker, or box content merged into surrounding prose.
10. **KNOWN, being fixed — do not spend time on it**: p.104's two WHITE
    tool-call panels inside the '[Assistant]' box (monospace lines with green
    pills) currently render as inline code inside paragraphs, and the second
    shows a literal `<span class="ph">` in its code. Everything else on p.104
    is in scope.
11. **p.175 Transcript 6.6.4.8.B**: the '[User]' prompt's typed '- …' lines
    render as separate lines (`<br>`) with literal hyphens — by design (D75);
    they are not a bulleted list in the PDF.
12. **§9.2 blocklist** (pp.259–264) is one visual code box across pages (one
    fence per PDF page in md, joined by the renderer with the page label
    inside at the true page turn); its info string `None` is the PDF's gray
    code-box language label. Whether the DOM shows the `None` label is not a
    finding. DO flag missing, garbled, or re-ordered blocklist lines.
13. **Footnote defs render as sidenotes/footnotes** — the body position
    differs from the PDF's page-bottom placement by design. Footnotes 10–11
    sit under Table 8.1 on p.207 in the PDF; they are page footnotes.
14. **Internal section links** resolve to heading anchors (`#22-cb-evaluations`)
    instead of page numbers — by design. DO flag links pointing at the WRONG
    section, or PDF links missing entirely.
15. **Green monospace effort levels** (`max`, `xhigh`, `low`, …) render as
    inline code spans; the code color is site styling. DO flag a code span
    covering the wrong words.
16. Section-heading gray (#666666) and page-number footers are layout; the
    site draws its own heading styles and TOC.
17. Charts and diagrams are raster images in this PDF; text inside them is not
    transcribed. A figure is correct when the right image sits with the
    right caption.
18. The METR quote (pp.39–42) is set in the PDF as an indented run with a
    left rule; it renders as a blockquote — by design. DO flag lost
    underlines, lost bold leads, or text that escapes the quote.

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

Calibration: the automated gate converged at 0 majors and this is the
SEVENTH card through the pipeline; most pages will be clean. Do not
manufacture findings — "clean" is a perfectly good verdict, and false
positives cost orchestrator time. But DO look hard: on earlier cards this
layer found real majors the gates could not see (scrambled table rows, merged
header corners emitted as empty cells, split captions, literal `**`, stranded
seam rows, lost underlines, header rows emitted as data). Table-heavy pages
(16, 37, 60–61, 64–65, 67, 69, 74–76, 79–80, 82, 87–88, 207–208, 255–259),
the boxed pages (93–94, 102–105, 142, 175), the blocklist (259–264), the
figure-dense alignment pages (89–184) and every footnote-bearing page deserve
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
    python3 -c "import json; open('pipeline/.cache/f52-sweep1/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
