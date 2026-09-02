# Certified-card regression review rulebook (review1)

You are judging whether two shared-pipeline improvements, developed on the fourth
card, are improvements or at least neutral when applied to a PREVIOUSLY CERTIFIED
card. Source of truth: the PDF page render. You surface verdicts; you NEVER edit
or fix anything. The orchestrator owns all changes.

## The two changes under review

1. **Fill-geometry cell merges** (`merge_cells_by_fill`, D63): where the PDF draws
   ONE cell spanning two header rows and/or two label columns (the dark 'Model' /
   'Evaluation' corner over a sub-header row such as 'API, without a system
   prompt / Claude.ai' or 'Attempts / Scenarios'), or one row label spanning two
   sub-rows, the web table now carries the matching `rowspan` / `colspan` instead
   of a header cell plus empty cells. Judge each changed table's header/label
   structure against the PDF crop: are the merged cells exactly the PDF's merged
   cells, with no data cell displaced?
2. **Code boxes across page breaks** (D65): a code box that continues onto the next
   PDF page is now ONE fence per page in the markdown with the page marker between
   the fences, and the renderer joins adjacent fences into one box, placing each
   page label inside the box beside the line where the page turns. Judge: is every
   line present once and in order across the join? Does the gutter label sit at
   the first line of the new page (not stacked under the box)? Is the box visually
   one box? A continuation fence's dropped `None` chrome line is by design.

3. **Wrapped links joined** (round 2, inputs under `pipeline/.cache/review2/`):
   a link the PDF wraps across a line arrives as two annotations sharing one
   destination and rendered as two adjacent anchors with an unlinked space
   between ('Section' + '7.2.1'). Two internal anchors separated only by
   whitespace and pointing at one target are now ONE anchor. Judge: is the
   joined anchor text exactly the PDF's link text (crop the link's blue run),
   does it point at the same heading as before, and did no neighbouring text
   get pulled into the link?

## Inputs (per card, under `pipeline/.cache/review1/<card>/` — round 2 under `review2/`)

- `diff.patch` — the exact markdown change (`git diff -U2` on the card's sections).
  Every hunk is what you are judging; read it first.
- `slices/p-NNN.md` — the NEW markdown attributed to each changed page.
- `served.html` — the NEW built page (one HTML file per card); grep a distinctive
  phrase to find your table or code box.
- PDF renders: `cards/anthropic/<card>/extracted/pages/p-NNN.png`; zoom crops via
  `env CARD=anthropic/<card> uv run --python 3.12 --with pymupdf==1.28.2 python pipeline/render_region.py PAGE`
  (every docling table bbox on the page) or `… PAGE x0 y0 x1 y1 [ZOOM]`; crops land
  in `pipeline/.cache/crops/`. Full-page renders are downscaled — use crops for
  any cell-level judgement.

## Verdicts

Append ONE JSON line per changed page to your findings file as you finish it:

    {"card": "anthropic/claude-opus-5", "page": 56, "verdict": "improvement",
     "change": "fill-merge", "desc": "Model cell now spans both header rows; sub-header row lost its empty lead; all values in place"}

`verdict` ∈ improvement | neutral | regression. `change` ∈ fill-merge | code-box.
A `regression` needs `evidence` (crop name vs served.html excerpt). Describe what
the reader sees before/after in one sentence. Do not manufacture findings; a
merged cell that matches the PDF is an improvement, a cosmetic no-op is neutral,
and anything misplaced, lost, or duplicated is a regression.

Final message: a 3-line summary (pages covered, verdict counts, anything you could
not check).
