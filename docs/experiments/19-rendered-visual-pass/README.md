# Experiment 19 — rendered visual pass in place of the owner scroll (2026-09-28)

**Question:** can the owner scroll pass (CLAUDE.md onboarding step 9) — the gate
for visual-layout defects the content sweeps miss — be replaced by a mechanical
render audit plus agent review of screenshots of every non-prose construct?

**Why now:** the owner asked for only what he actually needs to see on the
fifth card (Claude Opus 5.5, 230pp). During the curated review the owner
spotted — and the orchestrator had just fixed (`9aed2f4`) — a green
placeholder pill rendered as two adjacent pills: the PDF draws one pill wrapped
across a line, the markup looked correct, so the content sweep (experiment 18)
passed it. Only the rendered page showed it. That is exactly the class the
owner scroll exists for.

**Method** (production build served by `pnpm preview`):

1. **DOM layout audit** in the browser at 1338px, 1680px (sidenotes on) and
   375px: overlapping gutter page labels, sidenote/sidenote,
   sidenote/page-label and sidenote/body overlaps, horizontal page scroll,
   overflowing tables/code outside their scroll wrappers, text wider than the
   column, broken images.
2. **Screenshots** of every table, transcript box and code block with its
   caption (`shoot.py`: Playwright driving the installed Chrome, 1680px, 1.5×)
   — 26 constructs for this card.
3. **Three reviewer agents** compare each screenshot with the PDF page render(s)
   for what only shows visually: cell placement and merges, header-vs-body
   rows, emphasis appearance, empty cells, caption attachment, box scoping,
   code-box order and page labels (`findings.jsonl`).
4. **Certified-canon hunks** get a PDF | live site | new build composite
   (`hunks.py`) so the owner adjudicates from one image each.

**Result:** DOM audit clean at all three widths (223 page labels, 32 sidenotes,
109 images, 0 overlaps, 0 overflows; at 375px wide tables and the blocklist
scroll inside their own wrappers, as on every card). Screenshots: 25/26 clean;
1 cosmetic minor — p.82 Table 5.1.3.A's auto layout gives the model column
little width, so 'Claude Mythos 5.1' wraps (site-wide table layout, content and
structure correct). The three certified hunks: the two literal-backtick hunks
visibly match the PDF where the live site shows a code chip; the fable-5-1
caption hunk is visually identical (it only removes a redundant `<u>` from the
Markdown).

**Known render-level polish, not new with this card:** a merged 2×2 header
corner (e.g. 'Evaluation', Table 8.1.A) carries the thin inset rule the site
draws under every spanning header cell (`global.css` colspan rule); the same
corners have been live on the certified cards since D65.

**Conclusion (proposed, owner decision):** for same-family cards, the owner
scroll becomes this pass — DOM audit + construct screenshots reviewed by
agents + one composite per certified-canon hunk — with the owner seeing only
the adjudication composites and any flagged screenshot. Re-run with:

    uv run --with playwright python docs/experiments/19-rendered-visual-pass/shoot.py \
      http://localhost:4321/ai-system-cards/anthropic/<slug>/ <outdir>
