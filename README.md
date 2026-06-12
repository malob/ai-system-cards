# AI System Cards

A readable archive of AI model system cards. Labs publish system cards as long PDFs;
this project converts each one into a faithful, responsive web page — every sentence,
table, figure, and footnote, with deep links back to the source PDF — plus clean
markdown for machine consumption (`card.md` per card, `llms.txt` index).

**Site:** https://malob.github.io/ai-system-cards/

## Status

The pipeline has been built and validated end-to-end on its first card (Claude Fable 5
& Mythos 5, 319 pp.). The **site** renders any card present under `cards/`, but the
**conversion pipeline is currently specialized to that first card**: the card path is
hard-coded in a few modules, and the verifier gates are calibrated against this card's
own labeled defect history. Generalizing the pipeline to arbitrary cards is the natural
next step — see [Adding a card](#adding-a-card).

## Layout

```
cards/<vendor>/<slug>/
  meta.yaml           # title, slug, vendor, models, release_date, source_url,
                      #   source_pages, description, and the chip-label vocabulary
  source.pdf          # the original PDF
  style-manifest.yaml # per-card visual vocabulary (chip/highlight fills, role colors)
  sections/*.md       # faithful markdown, mechanically generated, ordered by filename
  assets/figures/     # figure images extracted from the PDF (pPPP-K.png)
  extracted/          # extraction artifacts: oracle inputs, links, per-page renders
pipeline/             # the conversion pipeline (extract → assemble → verify)
site/                 # Astro site rendering cards/ to static HTML (deploys to Pages)
docs/                 # design notes, decision log, and re-runnable experiments
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
   PDF deep links, footnotes into margin sidenotes, generates per-page Open Graph
   images, and serves `card.md` + `llms.txt` alongside the HTML. Search by Pagefind.

## Running it

Regenerate the card's markdown from its PDF, then run the verifier gates
(`uv` fetches the Python dependencies inline — `pymupdf`, and `docling` for tables):

```sh
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/verifier/calibrate.py cards/anthropic/claude-fable-5/sections
```

Build and serve the site:

```sh
cd site
pnpm install
pnpm dev        # local dev (search requires a production build)
pnpm build      # dist/ + Pagefind index
pnpm preview
```

Pushing to `main` deploys to GitHub Pages via the Actions workflow.

## Adding a card

The site picks up any new card under `cards/<vendor>/<slug>/` automatically. The
pipeline is currently wired to the first card, so onboarding a second is partly a
generalization exercise. In outline:

1. Create `cards/<vendor>/<slug>/` with the `source.pdf`, a `meta.yaml` (copy the
   existing one for the field shape), and a `style-manifest.yaml`.
2. Extract the per-page oracle, figure images, and table structure from the PDF.
3. Point the pipeline at the new card — the `CARD` path is hard-coded in
   `pipeline/generate/run.py`, `pipeline/generate/tables.py`, and
   `pipeline/verifier/calibrate.py` (generalizing this is the main shared work).
4. Run assemble + the verifier gates and iterate on any divergences.
5. Author the card's `style-manifest.yaml` (chip/highlight and role colors) and its
   chip-label vocabulary in `meta.yaml`.
6. Open a PR with the new `cards/<vendor>/<slug>/` directory.

Issues and PRs are welcome — including the pipeline generalization itself.
[`docs/`](docs/) holds the design: the [charter](docs/charter.md),
the [decision log](docs/decisions.md), the
[verification contract](docs/verification-contract.md), and re-runnable
experiments. That's design history — useful background, not required reading to use
the tool.

## A note on content

The documents reproduced here are published by their respective labs for public
consumption; this archive reproduces them faithfully and links each page back to the
original PDF. All document content belongs to its publisher.

## License

[MIT](LICENSE), for the code and pipeline. The reproduced system-card documents under
`cards/` belong to their respective publishers (see the note above).
