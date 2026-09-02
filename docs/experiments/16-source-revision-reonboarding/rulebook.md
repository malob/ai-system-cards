# Source-revision re-onboarding rulebook (sweep16)

Two certified cards were re-converted from NEWER publisher revisions of their
source PDFs: **Claude Opus 5** (August 19, 2026 revision, 198 pp; was the
July 24 reprint, 193 pp) and **Claude Fable 5 & Claude Mythos 5** (June 25,
2026 changelog entries in the July 16 print, 317 pp; was the June 11
revision). The pipeline is unchanged; the docling table cache was rebuilt on
the exact previously reviewed table pages with the pinned docling 2.115.0.
You inspect the PAGES WHOSE MARKDOWN CHANGED (plus a rotating regression
sample of shifted pages) for FAITHFULNESS defects against the PDF page
render. You surface findings; you NEVER edit or fix anything. The
orchestrator owns all fixes.

Read the card's earlier rulebook FIRST for the DO-NOT-FLAG list that was
adjudicated when the card was certified; everything there still applies:

- opus-5: `docs/experiments/10-opus5-sweep-round1/rulebook.md`
- fable-5: `docs/experiments/09-round-g/rulebook.md`

The general adjudications of `docs/experiments/14-fable-5-1-sweep-round1/rulebook.md`
§"DO NOT FLAG" (literal markup escapes, `<td><b>` vs `<th>`, `:::caption`,
page-marker comments, stitched multi-page tables, sidenote footnotes, heading
anchors instead of page numbers, code-span colors, gray headings) apply to both.

## Inputs (per card, under `pipeline/.cache/sweep16/<opus|fable>/`)

- `slices/p-NNN.md` — every md run attributed to page N (3-digit page number).
- `served.html` — the freshly built web page for the whole card (ONE page).
  Find your region by grepping a distinctive phrase from the slice
  (`grep -n -A5 'phrase' served.html`). It is the arbiter of structure
  (tags, list types, table cells, `<b>`, `<u>`, `<sup>`, anchors).
- PDF renders: `cards/anthropic/<card>/extracted/pages/p-NNN.png` — regenerated
  from the NEW PDF. Full-page renders are vision-downscaled; for any
  glyph-level judgement (bold extents, underlines, decimals, superscripts,
  table cells) render a crop first:
  `env CARD=anthropic/<card> uv run --python 3.12 --with pymupdf==1.28.2 python pipeline/render_region.py PAGE`
  (every docling table bbox on the page) or `… PAGE x0 y0 x1 y1 [ZOOM]` (PDF
  points, origin top-left, page ≈ 612×792). Crops land in
  `pipeline/.cache/crops/`. Run from the repo root.
- `diff.patch` — the markdown diff against the previously certified canon
  (page markers shifted for every Opus page; read the hunks on your pages).

## What changed in each source (verify these exactly)

**Opus 5 (August 19 revision).** p.2 is a new Changelog page (two bullets).
§5.2.2.1 "Live bug bounty across surfaces" is NEW (pp.75–77: two paragraphs,
Figure 5.2.2.1.A + caption, two paragraphs, Figure 5.2.2.1.B + caption); the
old 5.2.2.1–5.2.2.3 renumber to 5.2.2.2–5.2.2.4 (Table 5.2.2.2.A → 5.2.2.3.A).
§5.2.2.4 Browser use (pp.79–81): the intro paragraph lost its two product
links, the Cowork table has five single "With thinking" rows (Opus 5, Opus
4.8, Sonnet 5, Mythos 5, Fable 5 — no "Without thinking" rows, no rowspans),
the caption and the results paragraph changed, and footnote 5 (p.81) is a new
text. Table 8.1.A (p.152) FrontierBench row: 43.3 / 21.1 / 33.8 / 34.4
(Codex). p.154: a new "Note: There is a decline in FrontierCode score above
high effort…" paragraph and the two FrontierCode sentences joined in one
paragraph. p.156: FrontierBench paragraph gained a sentence. p.197: the
react-pdf code listing gained four `diegomura__react-pdf-…` entries. Every
other page shifted by +1 (pp.3–74) or +4 (pp.78 on) with otherwise identical
content — the rotating sample (pp.33, 53, 63, 124, 144, 149, 196) checks that
the shifted pages, their tables, and their page markers still match the PDF.
Page → section: 00-changelog 2 · 00-executive-summary 3–5 · (TOC 6–10, not
converted) · 01-introduction 11–12 · 02-rsp-evaluations 13–35 · 03-cyber
36–51 · 04-safeguards 52–68 · 05-agentic-safety 69–81 · 06a-alignment-1
82–109 · 06b-alignment-2 110–122 · 07-model-welfare 123–151 · 08a 152–172 ·
08b 173–194 · 09-appendix 195–198.

**Fable 5 (June 25 entries, July 16 print).** p.2: the Changelog gained a
"June 25, 2026" block with three bullets. p.3: the Executive Summary's RSP
paragraph now says alignment risk is "very low". p.220 (§7.2.1): the
"Appendix 9.1" link is now an internal link to the per-question welfare
interview results heading (it was a broken Google Docs URL). p.243 (Table
7.4.3.A row "§ How we think about corrigibility"): the PDF now prints
"“firm promise” — robust" with a space after the em dash. pp.281–288
(§8.15.4 BenchCAD): "two minor modifications", a re-ordered second/third
modification sentence, a new "However, unlike the first two changes…"
sentence ending "…in future system cardsWe" (verify whether the PDF really
runs "cards" into "We" — report what the render shows), and page breaks
shifted through p.288. Page → section: 00-changelog 1–2 · 00-executive-summary
3–4 · (TOC 5–11) · 01-introduction 12–14 · 02a 15–35 · 02b 35–56 · 03-cyber
57–69 · 04 70–86 · 05 87–97 · 06a 98–108 · 06b 108–132 · 06c 132–150 · 06d
150–161 · 06e 161–180 · 06f 181–194 · 06g 195–216 · 07a 217–231 · 07b 231–250
· 08a 251–262 · 08b 262–276 · 08c 277–289 · 08d 289–306 · 09-appendix 307–317.

## Severity

- **major** — a reader is misled or loses content: text lost / garbled /
  duplicated / misplaced; structure wrong (split or merged paragraph, item,
  heading, table row; wrong list nesting or type); meaning-bearing styling
  wrong (bold leads, underlines marking second-best scores, table headers,
  superscripts); broken table cell placement or merges; figure/caption
  missing or mis-associated; page-seam damage; a link to the wrong heading;
  a page marker on the wrong page.
- **minor** — visible cosmetic nit that does not change meaning.

Calibration: both cards were certified at 0 majors before the revision and
the automated gate is again at 0 unsuppressed majors; most pages will be
clean. Do not manufacture findings — "clean" is a good verdict. But look
hard at the NEW content (it never went through a human sweep) and at the
Cowork table, Table 8.1.A, and the react-pdf listing.

## Output

Append to YOUR OWN findings file (path in your task) ONE JSON line per page,
AS YOU FINISH EACH PAGE — never batch at the end. Schema:

    {"page": 75, "status": "clean"}
    {"page": 80, "status": "flagged", "findings": [{"severity": "major",
     "construct": "table", "desc": "Fable 5 row 0.25% not underlined",
     "evidence": "crop p80-… vs <tr> in served.html", "verdict": "confirmed"}]}

`construct` ∈ table | list | turn | figure | caption | heading | paragraph |
footnote | link | code | seam | marker. `verdict` ∈ confirmed | suspected.

Final message: a 3-line summary (pages covered, finding counts, anything you
could not check).
