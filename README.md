# AI System Cards

A readable archive of AI system cards and safety reports. Companies publish this work
as long PDFs — a system card when a model ships, a risk report in between — and long
PDFs are a pain to read. This project converts each one
into a faithful, responsive web page — every sentence, table, figure, and footnote,
with deep links back to the source PDF — plus clean markdown for machine consumption:
a full `card.md` per card, a standalone `.md` per major section (so agents can fetch
just the section they need), and an `llms.txt` index of all of it.

**Site:** https://malob.github.io/ai-system-cards/

The conversion is **mechanical — no LLM transcribes or edits the content.** A PyMuPDF
"oracle" plus docling extract ground truth from the PDF; a block compiler assembles
faithful markdown; independent invariant gates verify it against the oracle (text,
links, styling, structure, tables, figures, footnotes, page markers); and an Astro
site renders it to static HTML with PDF deep links, sidenote footnotes, per-page
social-preview images, and search.

## Status

Built and validated end-to-end on three Anthropic documents: **Claude Fable 5 &
Claude Mythos 5** (317 pp.), **Claude Opus 5** (193 pp.), and **Risk Report:
August 2026** (186 pp.). All three run through one shared pipeline with per-document
configuration, establishing that the approach works within Anthropic's
Google-Docs-export family. That is not yet evidence that it generalizes to a different
PDF producer or visual grammar. A document from another vendor is the next
architectural test.

## Layout

```
cards/<vendor>/<slug>/
  meta.yaml           # title, slug, vendor, models, release_date, source_url,
                      #   source_pages, description, and the chip-label vocabulary
  source.pdf          # the original PDF
  style-manifest.yaml # per-card visual vocabulary (chip/highlight fills, role colors)
  sections/*.md       # faithful markdown, mechanically generated, ordered by filename
  assets/figures/     # figure images extracted from the PDF (pPPP-K.png)
  extracted/          # per-card extraction data: figure map + image inventory; renders (gitignored)
pipeline/             # the conversion pipeline (extract → assemble → verify)
site/                 # Astro site rendering cards/ to static HTML (deploys to Pages)
docs/                 # design notes, decision log, and re-runnable experiments
CLAUDE.md             # operational playbook for an AI coding agent (see below)
```

## Working on this repo

This project is built and maintained with an **AI coding agent.** To convert a new
system card or safety report, or to fix or improve an existing document, open the repo
in [Claude Code](https://claude.com/claude-code) (or your agent of choice): the working
instructions — how the pipeline runs, the commands, and the document-generation /
"adding a document" workflow — live in **[CLAUDE.md](CLAUDE.md)**, with the design
rationale and decision log in **[docs/](docs/)**. Issues and PRs are welcome,
including the pipeline generalization itself.

## A note on content

The documents reproduced here are published by their respective companies for public
consumption; this archive reproduces them faithfully and links each page back to the
original PDF. All document content belongs to its publisher.

## License

[MIT](LICENSE), for the code and pipeline. The reproduced documents under `cards/` —
system cards and safety reports — belong to their respective publishers (see the note
above).
