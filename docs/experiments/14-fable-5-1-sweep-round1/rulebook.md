# Fable 5.1 inspector rulebook (f51-sweep1)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/claude-fable-5-1/sections/` (raw-HTML tables, `:::caption`
directives, `<!-- p.N -->` page markers), rendered to a single web page
(snapshot provided). You surface findings; you NEVER edit or fix anything.
The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/claude-fable-5-1/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/f51-sweep1/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Served HTML snapshot: `pipeline/.cache/f51-sweep1/served.html` (the whole
  card is ONE page). Find your region by grepping distinctive phrases from the
  slice (e.g. `grep -n -A5 'phrase' served.html`, or python). This pane shows
  what the reader actually gets: check structure (tags, list types, table
  cells, `<b>`, `<u>`, `<sup>`, blockquote nesting) — it is the arbiter when
  md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense boxes, small text,
  styling questions). Full-page renders are vision-downscaled (~1.15MP) — do
  NOT judge glyph-level detail (bold extents, underlines, decimals,
  superscripts) from a full page. Render a crop first:
  `env CARD=anthropic/claude-fable-5-1 uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=anthropic/claude-fable-5-1 uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root.

## Page → section map

| file | pages |
| --- | --- |
| (cover — NOT converted, by design) | 1 |
| 00-executive-summary.md | 2–5 |
| (table of contents — NOT converted, by design) | 6–10 |
| 01-introduction.md | 11–13 |
| 02-rsp-evaluations.md | 14–44 |
| 03-cyber.md | 45–58 |
| 04-safeguards-harmlessness.md | 59–76 |
| 05-agentic-safety.md | 77–89 |
| 06a-alignment-1.md | 90–121 |
| 06b-alignment-2.md | 122–138 |
| 07-model-welfare.md | 139–166 |
| 08-capabilities.md | 167–205 |
| 09-appendix.md | 206–212 |

## DO NOT FLAG — adjudicated, by design (carried from rounds G/10/11 + this card)

1. **Literal markup in boxed content**: `*`, `` ` ``, `<` appearing as
   characters in the PDF render literally; in md they appear
   backslash-escaped (`\*`, `` \` ``, `\<`) — correct. Likewise the p.96
   shell command's `\"` appears as `\\"` in md so the browser shows the one
   source backslash. Not defects.
2. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   row labels — visually identical; don't flag th-vs-td when the rendered
   weight matches the PDF. Dark sub-header rows ('API, without a system
   prompt' / 'Claude.ai') are `<th>` rows by design.
3. **This document has NO green placeholder pills and NO smart chips** (the
   signal census found neither). DO flag any green pill or chip-like label
   in a PDF render that the md lacks.
4. **`:::caption` blocks** = figure/table captions, uniform gray render. By
   design.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
6. **Raw `<table>` HTML in md** is by design. Multi-page tables are stitched
   into ONE table — a "missing" page break inside a table is correct, and a
   table-header row REPEATED on the continuation page in the PDF (Table 9.1.A
   pp.206–210, Table 7.4.3.A pp.159–160) appears ONCE in the stitched table.
   Table 7.4.3.A's third row is cut mid-cell by the p.159/160 page break —
   in the web table it is one complete row, by design.
7. Smart quotes / typographic glyphs in md come straight from PDF spans —
   don't flag curly-vs-straight. Docling table-cell text may normalize odd
   punctuation — known typed residual, don't re-flag.
8. **Empty table cells** in the §4 tables (the Claude Mythos 5 rows' Claude.ai
   columns, pp.60–76) are genuinely empty (light-gray) in the PDF. DO flag a
   value sitting in the wrong column or an empty cell where the PDF has one.
9. **Unlabeled cream boxes** (§6.1.3 prompt + Claude's review, pp.93–94)
   render as label-less bubbles (`.turn` with no `.turn-label`); the left
   accent color is site styling, not attribution. The review box continues
   across the p.93→94 break as ONE bubble. DO flag invented speaker labels or
   box content merged into surrounding prose.
10. **§9.2 blocklist** (pp.210–212) is one fenced code block; its info
    string `None` is the PDF's gray code-box language label (same as opus-5).
    Whether the DOM shows the `None` label is not a finding. DO flag missing,
    garbled, or re-ordered blocklist lines.
11. **Footnote defs render as sidenotes/footnotes at the section end** — the
    body position differs from the PDF's page-bottom placement by design.
12. **Internal section links** resolve to heading anchors (`#22-cb-evaluations`)
    instead of page numbers — by design. DO flag links pointing at the WRONG
    section, or PDF links missing entirely.
13. **Green monospace effort levels** (`low`, `medium`, `xhigh`, e.g. p.132)
    render as inline code spans; the code color is site styling. DO flag a
    code span covering the wrong words.
14. **Third-level ■ bullets** (p.42) nest as level-2 list items inside the
    blockquote. DO flag any list whose nesting differs from the PDF's
    ●/○/■ tiers.
15. Section-heading gray (#666666) and page-number footers are layout; the
    site draws its own heading styles and TOC.

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

Calibration: the automated gate converged at 0 majors and this is the FOURTH
card through the pipeline; most pages will be clean. Do not manufacture
findings — "clean" is a perfectly good verdict, and false positives cost
orchestrator time. But DO look hard: on earlier cards this layer found real
majors the gates could not see (scrambled table rows, phantom turn boxes,
flattened list nesting). Table-heavy pages (18, 20, 60–61, 65, 67, 69, 73–76,
78–80, 85–89, 152, 159–160, 167, 194, 206–210), the boxed pages (93–94), the
blocklist (210–212), the figure-dense alignment pages (98–126) and every
footnote-bearing page deserve the closest look; verify footnote defs against
the page bottom.

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
    python3 -c "import json; open('pipeline/.cache/f51-sweep1/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
