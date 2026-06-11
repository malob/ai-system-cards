# AI System Cards

A readable archive of AI model system cards. Labs publish system cards as long PDFs;
this project converts each one into a faithful, responsive web page — every sentence,
table, figure, and footnote, with deep links back to the source PDF — plus clean
markdown for machine consumption (`card.md` per card, `llms.txt` index).

**Site:** https://malob.github.io/ai-system-cards/

## Layout

```
cards/<vendor>/<slug>/
  meta.yaml          # title, vendor, release date, source URL
  source.pdf         # the original PDF
  sections/*.md      # faithful markdown, mechanically generated, ordered by filename
  assets/figures/    # figure images extracted from the PDF (pPPP-K.png)
  extracted/         # mechanical extraction artifacts (ground truth + per-page renders)
  style-manifest.yaml# per-card visual vocabulary (chip/highlight fills, role colors)
pipeline/            # the conversion pipeline (extract → assemble → verify)
docs/v2/             # design notes, decisions log, and experiments
site/                # Astro site rendering cards/ to static HTML
```

## How a card is produced

The conversion is **mechanical — no LLM transcribes or edits the content** — so
fidelity is reproducible and checkable by construction.

1. **Extract** ground truth from the PDF: a PyMuPDF "oracle" (text spans with
   style flags, links, footnotes, highlight/chip fills, page geometry, per-page
   renders) plus docling for table structure.
2. **Assemble**: a block compiler builds the document straight from those facts —
   paragraphs, lists, headings, tables, transcripts, figures, footnotes — and
   serializes to `sections/*.md` (`pipeline/generate/`).
3. **Verify**: independent invariant gates compare the output against the oracle
   — text tokens, links, bold/chip styling, block structure, tables, figures,
   footnotes, page-marker continuity — and fail on any unexplained divergence
   (`pipeline/verifier/`). The gates are calibrated against the project's own
   labeled history of real defects and mutation-tested for recall.
4. **Render**: the Astro site stitches `sections/*.md`, turns page markers into
   PDF deep links, footnotes into margin sidenotes, and serves `card.md` +
   `llms.txt` alongside the HTML. Search by Pagefind.

## Development

Regenerate a card from its PDF, then run the verifier gates:

```sh
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

Build and serve the site:

```sh
cd site
pnpm install
pnpm dev        # local dev (search requires a production build)
pnpm build      # dist/ + Pagefind index
pnpm preview
```

Deploys to GitHub Pages via Actions on push to `main`.

## A note on content

The documents reproduced here are published by their respective labs for public
consumption; this archive reproduces them faithfully and links each page back to the
original PDF. All document content belongs to its publisher.
