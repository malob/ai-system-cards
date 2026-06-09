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
  sections/*.md      # faithful markdown transcription, ordered by filename
  assets/figures/    # figure images extracted from the PDF (pPPP-K.png)
  extracted/         # mechanical extraction artifacts (ground truth + verification)
docs/
  markdown-conventions.md   # transcription rules all cards follow
site/                # Astro site rendering cards/ to static HTML
```

## How a card is produced

1. **Extract** ground truth: `pdftotext` text layer, `pdfimages` figures,
   link annotations, per-page renders.
2. **Transcribe**: parallel Claude agents convert page-range chunks to markdown
   following [docs/markdown-conventions.md](docs/markdown-conventions.md), each
   self-verifying with a word-level diff against the text layer.
3. **Verify**: an independent sweep checks page-marker continuity and that every
   page's distinctive sentences appear in the stitched markdown
   (`extracted/verify_coverage.py`).
4. **Render**: the Astro site stitches `sections/*.md`, turns page markers into
   PDF deep links, footnotes into margin sidenotes, and serves `card.md` +
   `llms.txt` alongside the HTML. Search by Pagefind.

## Development

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
