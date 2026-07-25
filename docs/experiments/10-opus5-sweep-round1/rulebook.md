# opus-sweep1 inspector rulebook (claude-opus-5, round 1)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/anthropic/claude-opus-5/sections/` (raw-HTML tables, `:::caption`
directives, `:::turn` bubbles, `<span class="ph">` placeholder pills,
`<!-- p.N -->` page markers), rendered to a single web page (snapshot
provided). You surface findings; you NEVER edit or fix anything. The
orchestrator owns all fixes.

## Inputs

- PDF page renders: `cards/anthropic/claude-opus-5/extracted/pages/p-NNN.png`
  (3-digit page number).
- Per-page md slices: `pipeline/.cache/opus-sweep1/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible prose content).
- Served HTML snapshot: `pipeline/.cache/opus-sweep1/served.html` (the whole
  card is ONE page). Find your region by grepping distinctive phrases from the
  slice (e.g. `grep -n -A5 'phrase' served.html`, or python). This pane shows
  what the reader actually gets: check structure (tags, list types, table
  cells, `<b>`, `<u>`, `<span class="ph">`, blockquote nesting) — it is the
  arbiter when md syntax is ambiguous.
- HIGH-ZOOM CROPS for dense constructs (tables, dense transcripts, small
  text, styling questions). Full-page renders are vision-downscaled (~1.15MP)
  — do NOT judge glyph-level detail (bold extents, underlines, decimals,
  superscripts) from a full page. Render a crop first:
  `env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page ≈ 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from repo
  root. ALWAYS pass the CARD env or you will crop the WRONG document.

## Page → section map

| file | pages |
| --- | --- |
| 00-executive-summary.md | 2–4 |
| (table of contents — NOT converted, by design) | 5–9 |
| 01-introduction.md | 10–11 |
| 02-rsp-evaluations.md | 12–34 |
| 03-cyber.md | 35–50 |
| 04-safeguards-harmlessness.md | 51–67 |
| 05-agentic-safety.md | 68–77 |
| 06a-alignment-1.md | 78–105 |
| 06b-alignment-2.md | 106–118 |
| 07-model-welfare.md | 119–147 |
| 08a-capabilities-1.md | 148–168 |
| 08b-capabilities-2.md | 169–190 |
| 09-appendix.md | 191–193 |

Page 1 is the cover (declared exclusion — title/date/logo only; not
converted).

## DO NOT FLAG — typed/accepted for THIS card (gate-adjudicated)

1. **Docling table character normalization**: inside `<table>` cells, curly
   quotes may appear straight (`"That` → `'That`) and en/em dashes as hyphens
   (`12–65%` → `12-65%`), notably pp. 140–141. Known typed residual (same
   class accepted on the first card); the orchestrator tracks it. Don't
   re-report each instance.
2. **Literal markup in transcripts**: `*`, `` ` ``, `**`, `<answer>`,
   `<score>`, `<result>` appearing as characters in model-output transcripts
   are IN the PDF (raw model output) and must render literally. In md they
   appear backslash-escaped (`\*`, `` \` ``, `\<answer>`) — that escaping is
   correct, not a defect.
3. **Turn labels keep source brackets** (`[Assistant]:`); label-less cream
   bubbles render with no label — both as printed in the PDF.
4. **Green placeholder ranges** render via raw `<span class="ph">…</span>`
   (green pill, matches PDF green highlights — `[…]`, `[tool use]`, narrator
   pills). The raw HTML in md is by design. DO flag PDF green-highlighted
   ranges with NO ph span, or ph spans covering wrong text.
5. **`<td><b>…</b></td>` vs `<th>`**: bold data cells where the PDF has bold
   sub-labels — visually identical to header cells; accepted parity. Don't
   flag th-vs-td choices when the rendered weight matches the PDF.
6. **`:::caption` blocks** = figure/table/transcript captions
   (`[Table 2.2.3.A] …`, `[Transcript 6.3.A] …`), uniform gray render. By
   design.
7. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
8. **Raw `<table>` HTML in md** is by design. Multi-page tables are stitched
   into ONE table — a "missing" page break inside a table is correct.
9. **Pages 5–9 (table of contents)**: not converted, by design.
10. Smart quotes / typographic glyphs in PROSE come straight from PDF spans —
    don't flag curly-vs-straight outside tables (inside tables see rule 1).
11. **Code boxes with bold/green content** render as `<pre>` with `<b>` /
    ph spans instead of a fence. By design.
12. **Mono spans in prose** (`web_fetch`, `aiohttp`) render as inline code.
    The PDF's literal backticks around such tokens (`` `WebSearch` ``) render
    as code styling without the backtick glyphs — accepted (typed).
13. **Footnotes render as sidenotes** on wide screens; the `[^N]` defs at
    section end are the md form. By design.
14. **Table sub-header rows** (mid-gray `#4d4c48` cells, white text — e.g.
    the 'Opus 5 / Opus 4.8 / Fable 5 / GPT 5.6 Sol' row p.148) may render as
    header-styled rows. Match against the PDF crop before flagging.

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

Calibration: this is the FIRST sweep round for this card (the pipeline
converged on a sibling document; this document passed the automated gate at
0 majors). Expect most pages clean, but this card has constructs the gates
can't judge — look hard at tables (column assignment, merged cells, header
tiers), transcript boxes (turn boundaries, nested code boxes, pill
placement), figures (presence + caption association), and page seams.
Do not manufacture findings — "clean" is a good verdict; false positives
cost orchestrator time.

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
