# AI System Cards

A readable archive of AI model system cards. Companies usually publish a model's
system card as a long PDF, and long PDFs are a pain to read. This project converts each one
into a faithful, responsive web page — every sentence, table, figure, and footnote,
with deep links back to the source PDF — plus clean markdown for machine consumption
(`card.md` per card, `llms.txt` index).

**Site:** https://malob.github.io/ai-system-cards/

The conversion is **mechanical — no LLM transcribes or edits the content.** A PyMuPDF
"oracle" plus docling extract ground truth from the PDF; a block compiler assembles
faithful markdown; independent invariant gates verify it against the oracle (text,
links, styling, structure, tables, figures, footnotes, page markers); and an Astro
site renders it to static HTML with PDF deep links, sidenote footnotes, per-page
social-preview images, and search.

## Status

Built and validated end-to-end on its first card (Claude Fable 5 & Mythos 5, 319 pp.).
The site renders any card under `cards/`; the conversion pipeline is currently
specialized to that first card (the card path is hard-coded and the gates are
calibrated against its own defect history), so generalizing it to arbitrary cards is
the next step.

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
CLAUDE.md             # operational playbook for an AI coding agent (see below)
```

## Working on this repo

This project is built and maintained with an **AI coding agent.** To convert a new
system card, or to fix or improve an existing one, open the repo in
[Claude Code](https://claude.com/claude-code) (or your agent of choice): the working
instructions — how the pipeline runs, the commands, and the card-generation /
"adding a card" workflow — live in **[CLAUDE.md](CLAUDE.md)**, with the design
rationale and decision log in **[docs/](docs/)**. Issues and PRs are welcome,
including the pipeline generalization itself.

## A note on content

The documents reproduced here are published by their respective companies for public
consumption; this archive reproduces them faithfully and links each page back to the
original PDF. All document content belongs to its publisher.

## License

[MIT](LICENSE), for the code and pipeline. The reproduced system-card documents under
`cards/` belong to their respective publishers (see the note above).
