# Gemini 4 Carbon inspector rulebook (g4c-sweep1)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/google-deepmind/gemini-4-carbon/sections/` (raw-HTML tables,
`:::caption` directives, `<!-- p.N -->` page markers), rendered to a single web
page (snapshot provided). You surface findings; you NEVER edit or fix anything.
The orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/google-deepmind/gemini-4-carbon/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/g4c-sweep1/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Section files (linters): read the SNAPSHOT in
  `pipeline/.cache/g4c-sweep1/sections/`, not the live card folder.
- Served HTML snapshot: `pipeline/.cache/g4c-sweep1/served.html` (the whole
  card is ONE page, production build). Find your region by grepping
  distinctive phrases from the slice. It is the arbiter when md syntax is
  ambiguous: check tags, list types, table cells, `<b>`, `<u>`, `<sup>`,
  blockquote nesting.
- HIGH-ZOOM CROPS for dense constructs (tables, boxes, small text, styling
  questions). Full-page renders are vision-downscaled — do NOT judge
  glyph-level detail (bold extents, underlines, decimals, superscripts,
  quote glyphs) from a full page. Render a crop first:
  `env CARD=google-deepmind/gemini-4-carbon uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=google-deepmind/gemini-4-carbon uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root. Write any helper scripts you need into a folder named after YOUR
  findings file (other inspectors run in parallel).

## Page → section map

The PDF's printed page numbers are PDF page − 1 (unnumbered cover); this
rulebook and the renders use PDF page indices.

| file                        | pages   |
| --------------------------- | ------- |
| (cover — NOT converted)     | 1       |
| (table of contents — NOT converted) | 2–4 |
| 01-introduction.md          | 5–7     |
| 02-mitigations.md           | 8–11    |
| 03-frontier-safety.md       | 12–47   |
| 04-content-safety.md        | 48–57   |
| 05-aligned-interactions.md  | 58–81   |
| 06-prompt-injection.md      | 82–87   |
| 07-cyber-defense.md         | 88–94   |

## DO NOT FLAG — adjudicated, by design (from gemini-4-argon + this card)

1. **Literal markup characters** the PDF shows as characters appear
   backslash-escaped in md and render literally — correct.
2. **`<td><b>…</b></td>` vs `<th>`**: don't flag th-vs-td when the rendered
   weight matches the PDF. The light-blue header bands are site-styled table
   headers; their blue text color is not reproduced.
3. **No chips, placeholder pills, highlights or monospace code** exist in this
   document. DO flag any highlighted or code-styled text the web page lacks.
4. **`:::caption` blocks** = figure/table captions (gray render). Caption
   labels are bold as in the PDF ('**Table 3.1:**'); a colon set in regular
   weight follows the PDF.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure. A
   page marker can sit INSIDE a table cell where a row is cut by a page break
   — it marks the exact seam.
6. **Raw `<table>` HTML** is by design. Multi-page tables are stitched into
   ONE table; a header row repeated on a continuation page appears once; a
   row cut by a page break is one complete row (Table 3.1 pp.15–17, Table 3.2
   pp.31–34).
7. **The bordered CCL definition boxes** (pp.18, 20) render as bordered
   one-column tables — by design (they are tables in the PDF's structure).
8. **Quote glyphs print exactly as the PDF prints them** — curly where curly,
   straight where straight. DO flag a mismatch, but only from a crop.
9. **Headings** follow the PDF's heading styles: 22pt → `##`, 16pt blue →
   `###`, 14pt dark gray → `####`, 12pt gray → `#####`, 11pt italic gray →
   `######`. Unnumbered heads ('Executive Summary') take their style's level.
   DO flag a heading with wrong text or wrong level for its PDF style, and a
   bookmarked heading rendered as prose or vice versa.
10. **Footnotes render as sidenotes/footnotes** — position differs from the
    PDF's page bottom by design.
11. **Internal links** resolve to heading anchors and follow where the PDF's
    link JUMPS, even when that differs from the anchor text (source-faithful).
    DO flag a missing link or one that jumps somewhere the PDF's does not.
12. Page-number footers and the TOC are layout, not content.
13. Charts and diagrams are raster images; text inside them is not
    transcribed. A figure is correct when the right image sits with the
    right caption.
14. **Hyphen bullets** ('-' markers) render as ordinary bullets.

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
EIGHTH card through the pipeline (the second in this Google DeepMind template); most pages will be clean. Do not
manufacture findings — "clean" is a perfectly good verdict, and false
positives cost orchestrator time. But DO look hard: on earlier cards this
layer found real majors the gates could not see (scrambled table rows, merged
header corners emitted as empty cells, split captions, literal `**`, stranded
seam rows, lost underlines, header rows emitted as data). Table-heavy pages
(15–18, 20, 31–34, 46, 61, 66–67), the CCL boxes (18, 20) and every
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
    python3 -c "import json; open('pipeline/.cache/g4c-sweep1/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.
