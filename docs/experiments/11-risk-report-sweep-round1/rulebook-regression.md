# Certified-card regression rulebook (2026-08-15)

Two cards are already LIVE — claude-fable-5 and claude-opus-5. Today's work
on a third document changed their output too. Your job is **not** to find
new defects in old work: it is to answer one question per page —

> **Is this page as good as, or better than, it was before?**

The PDF is the only authority. A difference from the previous rendering is
fine when it matches the PDF better; it is a REGRESSION when it matches the
PDF worse, or when it breaks something that used to work.

## Inputs

- PDF page renders:
  `cards/anthropic/claude-fable-5/extracted/pages/p-NNN.png`
  `cards/anthropic/claude-opus-5/extracted/pages/p-NNN.png`
- Per-page md slices: `pipeline/.cache/regress/fable/p-NNN.md`,
  `pipeline/.cache/regress/opus/p-NNN.md`
- Served HTML: `pipeline/.cache/regress/fable-served.html`,
  `pipeline/.cache/regress/opus-served.html`
- PREVIOUS output for the same page, to diff against:
  `git show 2eee70e:cards/anthropic/<card>/sections/<file>.md`
  (find the file from the page→section header comment in the slice)
- High-zoom crops — REQUIRED before judging any glyph-level detail:
  `env CARD=anthropic/<card> uv run --with pymupdf python pipeline/render_region.py PAGE [x0 y0 x1 y1] [ZOOM]`
  → `pipeline/.cache/crops/p{PAGE}-{x}x{y}.png`, then Read it. Repo root.
- Screenshots of the live page are possible despite the page being ~190k px
  tall (the pane returns a blank frame when scrolled deep). Collapse the page
  around your target first, via the browser tools:
  `let el = TARGET; while (el && el !== document.body) { for (const s of [...el.parentElement.children]) if (s !== el) s.style.display='none'; el = el.parentElement; } window.scrollTo(0,0);`
  then screenshot. Reload to restore.

## What changed today (verify these specifically, then look wider)

1. **Internal link targets.** PDF link destinations were being read in the
   wrong coordinate space, so a destination page with several headings
   resolved to its FIRST heading. 10 links on fable, 2 on opus now resolve
   elsewhere. For every internal link on your pages: does the target heading
   match what the PDF's link actually points at, and does it match the link
   text's evident intent?
2. **In-cell bulleted lists** now render as real `<ul>/<li>` (was literal '●'
   glyphs joined by line breaks). Check: same items, same order, same text,
   nothing dropped or merged, sub-paragraphs under the right bullet.
3. **Footnote superscripts** lifted out of bold label runs in table cells.
   Check the PDF: is the superscript regular weight there?
4. **A header row promoted to `<th>`** (opus p.148). Check the PDF: is that
   row a header band (light text on dark) or a data row?
5. **Page markers**: a cross-page transcript's marker now sits inline at the
   seam rather than after the box; and a renderer pass re-aligns marker
   labels to the line their page starts on. Check a few markers on your
   pages against where the PDF page truly begins.

## Do not flag

- Smart quotes: the renderer's typographer is an owner decision (2026-07-25).
- Page markers / `<!-- source: -->` comments are infrastructure.
- Sidenote-style footnotes, heading-anchor links, and `<span class="ph">`
  placeholder pills are by design.
- Table cell background tints are a declared exclusion.

## Output

Append ONE JSON line per page to your findings file AS YOU FINISH IT:

    {"page": 100, "card": "fable", "status": "clean", "note": "3 links verified against PDF dests"}
    {"page": 234, "card": "fable", "status": "flagged", "findings": [{"severity": "major",
     "kind": "regression", "construct": "table", "desc": "...", "was": "...", "now": "...",
     "evidence": "crop p234-60x330.png", "verdict": "confirmed"}]}

`kind` ∈ regression | improvement | neutral-difference | pre-existing.
Record improvements too — they are the evidence the change was worth making.

Final message: 3 lines — pages covered, counts by kind/severity, anything
unverifiable and why.
