# Gemini 4 Argon inspector rulebook (g4a-sweep2)

You are inspecting a PDF→web conversion for FAITHFULNESS defects. Source of
truth: the PDF page render. The conversion: markdown in
`cards/google-deepmind/gemini-4-argon/sections/` (raw-HTML tables, `:::caption`
directives, `<!-- p.N -->` page markers), rendered to a single web page
(snapshot provided). You surface findings; you NEVER edit or fix anything.
The orchestrator owns all fixes.

This is the archive's FIRST non-Anthropic document (Google DeepMind's Safety &
Security Report). Same exporter (Google Docs) as the earlier cards, but a
different house style: Google Sans type, blue headings, light-blue table header
bands, bold `Figure 3.18:` caption labels BELOW figures and tables, gray
footnotes. Expect classes the earlier cards never exercised.

## Inputs

- PDF page renders: `cards/google-deepmind/gemini-4-argon/extracted/pages/p-NNN.png`
  (3-digit PDF page number). NOTE: the PDF's PRINTED page numbers are one less
  than the PDF page (the cover is unnumbered); everything here uses PDF pages.
- Per-page md slices: `pipeline/.cache/g4a-sweep2/slices/p-NNN.md` — every md
  run attributed to page N. A missing slice = nothing attributed to that page
  (flag only if the PDF render clearly shows convertible content).
- Served HTML snapshot: `pipeline/.cache/g4a-sweep2/served.html` (the whole
  card is ONE page, production build). Find your region by grepping
  distinctive phrases from the slice (`grep -n -A5 'phrase' served.html`, or
  python). It is the arbiter when md syntax is ambiguous: check tags, list
  types, table cells, `<b>`, `<i>`, `<u>`, `<sup>`, `<br>`, spans.
- HIGH-ZOOM CROPS for dense constructs (tables, small text, styling
  questions). Full-page renders are vision-downscaled — do NOT judge
  glyph-level detail (bold extents, italics, decimals, superscripts) from a
  full page. Render a crop first:
  `env CARD=google-deepmind/gemini-4-argon uv run --with pymupdf python pipeline/render_region.py PAGE`
  (every docling table bbox on the page, zoom 5) or
  `env CARD=google-deepmind/gemini-4-argon uv run --with pymupdf python pipeline/render_region.py PAGE x0 y0 x1 y1 [ZOOM]`
  (PDF points, origin top-left, page 612×792). Crops →
  `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`; Read the crop. Run from the
  repo root. Other inspectors write crops to the same folder; that is fine.

## Page → section map

| file                             | pages   |
| -------------------------------- | ------- |
| (cover — NOT converted)          | 1       |
| (table of contents — NOT converted) | 2–5  |
| 01-introduction.md               | 6–8     |
| 02-mitigations.md                | 9–13    |
| 03a-frontier-safety-misuse.md    | 14–40   |
| 03b-manipulation-safeguards.md   | 41–63   |
| 03c-loss-of-control.md           | 64–90   |
| 03d-alignment-assessment.md      | 91–112  |
| 03e-cot-transparency.md          | 113–156 |
| 03f-evaluation-awareness.md      | 157–162 |
| 04-content-safety.md             | 163–174 |
| 05-aligned-interactions.md       | 175–202 |
| 06-third-party-harm.md           | 203–212 |
| 07-cyber-defense.md              | 213–217 |

## DO NOT FLAG — adjudicated, by design

1. **Literal markup characters**: `<`, `*`, `` ` `` that the PDF shows as
   characters appear backslash-escaped in md (`\<thought>`) or inside inline
   code (`` `<thought>` ``) and render literally — correct.
2. **`<td><b>…</b></td>` vs `<th>`**: don't flag th-vs-td when the rendered
   weight matches the PDF. The light-blue header bands are site-styled table
   headers; their blue text color is not reproduced.
3. **No chips or placeholder pills** exist in this document. The ONE
   meaningful highlight is Figure 3.43 (p.155): the orange-highlighted
   commands and 'Monitor Suspicion: 2/10' render as
   `<span class="hl-orange">` — by design. DO flag any other highlighted text
   the web page lacks, or highlight on the wrong words.
4. **`:::caption` blocks** = figure/table captions (gray render). Caption
   labels are bold as in the PDF; in some captions the colon after the label
   is regular weight (`**Table 3.2**:`) — that follows the PDF.
5. **`<!-- p.N -->` / `<!-- source: … -->`** comments are infrastructure.
6. **Raw `<table>` HTML** is by design. Multi-page tables are stitched into
   ONE table; a header row repeated on a continuation page appears once. Known
   seam renderings (don't re-flag): Table 3.1 (pp.16–18) is one table with
   'CBRN' spanning 2 rows and 'Loss of Control' spanning 3; Table 3.6
   (pp.92–93) groups 'Terminal drives … / eval' over 3 rows (the Gram row's
   cut cell rejoined); Table 5.3's 'Fabricating data' row, cut at pp.184/185,
   is one complete row; Table 5.2's last row continues on p.184 — its
   'Expected Behavior' cells render as a second sub-row under a two-row
   label (a known approximation of one row broken across the page).
7. Smart quotes / typographic glyphs come straight from PDF spans — don't
   flag curly-vs-straight.
8. **Known structure limitations, tracked for the owner (don't re-flag;
   DO flag text lost, garbled, duplicated or reordered inside them):**
   - the bordered single-column CCL DEFINITION BOXES (pp.22, 34, 41, 64) render
     as ordinary bold-lead paragraphs without a box;
   - Figure 3.38 (p.147): the table's spanning first row (System prompt / User
     prompt) renders as prose above the table, and the answer options A)–G)
     join into one paragraph;
   - in-cell CODE lines (Figure 3.43, pp.154–155): a line break is restored
     only where the next token would have fit on the line, so some code lines
     still join.
9. **Headings** follow the PDF's heading styles: 22pt black → `##`, 16pt blue
   → `###`, 14pt dark gray → `####`, 12pt gray → `#####`, 11pt italic gray →
   `######`. Unnumbered heads ('Executive Summary') take their style's level.
   The italic 'Summary' line in 03e is a plain paragraph in the PDF (not a
   bookmarked heading) and renders as italic text — by design. DO flag a
   heading with wrong text or wrong level for its PDF style.
10. **Footnotes render as sidenotes/footnotes** — position differs from the
    PDF's page bottom by design. The adjacent superscripts '⁷⁸' (p.34) are two
    references, 7 and 8.
11. **Internal links** resolve to heading anchors. Three PDF links jump to a
    different section than their text names (p.6 'Section 2' → 2.2, 'Section
    3.4' → 3.4.1.4; p.181 'Section 3.2' → 4.2); the web page reproduces where
    the PDF jumps — source-faithful. DO flag any other wrong target or a
    missing link.
12. **Green monospace text** (RobotoMono: `0.49`, `<thought>`) renders as
    inline code; the color is site styling.
13. Page-number footers and the TOC are layout, not content.
14. Charts and diagrams are raster images; text inside them is not
    transcribed. A figure is correct when the right image sits with the
    right caption.
15. **Hyphen bullets** ('-' markers, p.179) render as ordinary bullets.

## Severity

- **major** — a reader is misled or loses content: text lost / garbled /
  duplicated / misplaced; structure wrong (split or merged paragraph, item,
  heading, table row; wrong list nesting or type); meaning-bearing styling
  wrong (bold leads, italic terms, table headers, superscripts); broken table
  cell placement or merges; figure/caption missing or mis-associated;
  page-seam damage (mid-sentence hard break, lost line, unstitched
  continuation).
- **minor** — visible cosmetic nit (spacing, marginal typography) that does
  not change meaning.

Calibration: the automated gate converged at 0 unsuppressed majors (8 exact,
source-adjudicated order/seam acceptances on pp.147 and 184–185). Do not
manufacture findings — "clean" is a good verdict. But DO look hard: this is a
new house style, and on earlier cards this layer found real majors the gates
could not see (scrambled table rows, merged header corners emitted as empty
cells, split captions, stranded seam rows, lost underlines). Closest look:
table pages (16–18, 26–27, 44, 87–90, 92–93, 108, 147, 154–155, 161, 178,
183–185, 194), the definition boxes (22, 34, 41, 64), every caption, and every
footnote-bearing page (verify footnote text against the page bottom).

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
finding.) `construct` ∈ table | list | figure | caption | heading | paragraph
| footnote | link | code | highlight | seam | other. `verdict` ∈ confirmed
(you verified against the page render/crop) | uncertain (needs orchestrator
eyes) | source-faithful (looked sus, PDF agrees — report so the rulebook can
grow).

Append safely from repo root, e.g.:
    python3 -c "import json; open('pipeline/.cache/g4a-sweep2/findings-XXX.jsonl','a').write(json.dumps({...})+'\n')"

Final message: a 3-line summary (pages/files covered, counts by severity,
anything you could not check and why). Details belong in the findings file,
not the final message.

## Round 2 additions — round-1 outcomes (verify the fixes; don't re-flag the rest)

Round 1 fixed these classes (D71); VERIFY each on its pages and flag any
regression nearby: the i./ii./iii. list (p.15, three sibling items at one
level); footnote 11 (p.35) complete — its TAC-1…TAC-4 lines and closing
sentence break with line breaks, and its p.36 tail is IN the footnote, not the
body; the p.36→37 body sentence 'models 1) score at the TAC-4 level' is one
paragraph; 'each, *conditional on* access' italic (p.35, no literal
asterisks); Figure 3.20 / 3.22 captions complete across pp.107–108 / 114–115;
Figure 3.36's caption (label 'Figure 3.36.') is a caption; the p.129
'**Analysis**:' paragraph is NOT part of the Figure 3.30 caption; Table 3.4
(p.44) and Table 5.2 (p.183) header rows are `<th>`; Table 3.5 (pp.87–89)
bold 'Uncertainties & verification:' labels, each its own line; Table 3.6
(pp.92–93) bold key findings ('; 0 external monitor tampering', '98%') and no
bold 'capability'; Table 5.1 (p.178) and Table 5.4 (p.194) row labels regular
weight.

Adjudicated — DO NOT FLAG (round 1, recorded in the experiment README):
16. Figure 3.43's 'STEPS 1–6' row renders as two rows across the p.154/155
    break (no textual continuation signal).
17. In-cell stacked values whose second line would not have fit ('1.8%' /
    '(1/55)', Table 3.4; Table 5.1's '68.8' / '(56.5)') join on one line.
18. Decorative rules (section-end rules pp.8/174/202, Table 5.1's heavier
    group rule) are not reproduced.
19. Link anchors that include a sentence period or paren the PDF link rect
    covers (pp.14, 115, 142, 167).
20. Underline extents that include a trailing colon (pp.78–79).
21. The p.66/67 seam join after the period-less 'catastrophic harm)'.
22. Source-faithful as printed: the duplicated §2.5 sentence (p.12); bold vs
    regular colons after sibling bullet leads; standalone 11pt black
    pseudo-subheads ('Honeypots', 'LinuxArena', …) as plain paragraphs;
    '3.5.1'–'3.5.3' as `####` heads (bookmarked level 4, set as bold body);
    the bold final 's' of 'results' (p.93 Honeypots row — the PDF's span);
    literal `$p < 0.001$` (p.147); the bold colon after a footnote ref
    (p.41) and bold ')' after an italic (p.87) are minor nits, not findings.
