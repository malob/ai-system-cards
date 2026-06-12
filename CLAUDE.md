# AI System Cards

Archive of AI-lab system cards, each converted from its source PDF into a faithful
web page (Astro → GitHub Pages) by a mechanical, verifier-gated pipeline — no LLM
transcribes the content. The pipeline is a ground-up rebuild of a labor-intensive
first attempt (the rebuild was called "v2" during development; that's why the design
docs say v2). README.md is the human-facing overview; **this file is the operational
playbook** — how to run the pipeline, add or improve a card, and the process rules.
`docs/` holds the design notes and decision log.

## Orientation — read before working

1. [docs/state.md](docs/state.md) — current status, next actions, cold-start
   capsule. **Always read this first.**
2. [docs/charter.md](docs/charter.md) — goal, principles, roadmap.
3. [docs/decisions.md](docs/decisions.md) — append-only decision log (D1…).
4. [docs/design-brief.md](docs/design-brief.md) — retrospective on the labor-intensive
   first attempt; its §2 defect taxonomy is load-bearing. Superseded where decisions.md says so.
5. [docs/markdown-conventions.md](docs/markdown-conventions.md) — early transcription
   rules (input to the spec, not gospel).

## How a card is produced

The conversion is **mechanical — no LLM transcribes or edits the content** — so
fidelity is reproducible and checkable. Four stages:

1. **Extract** ground truth from the PDF: a PyMuPDF "oracle" (text spans with style
   flags, links, footnotes, highlight/chip fills, geometry, per-page renders) + docling
   for table structure → `cards/<vendor>/<slug>/extracted/`.
2. **Assemble** (`pipeline/generate/`): a block compiler builds the document from those
   facts and serializes to `sections/*.md`.
3. **Verify** (`pipeline/verifier/`): independent invariant gates (text tokens, links,
   bold/chip styling, block structure, tables, figures, footnotes, page markers) compare
   output to the oracle and fail on any unexplained divergence; calibrated against the
   labeled defect history and mutation-tested.
4. **Render** (`site/`): Astro stitches `sections/*.md`, makes page markers into PDF
   deep links, footnotes into sidenotes, per-page OG images, `card.md` + `llms.txt`;
   Pagefind search.

## Running the pipeline

Regenerate the card's markdown from its PDF, then run the verifier gates (`uv` fetches
the Python deps inline — `pymupdf`, and `docling` for tables):

```sh
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/verifier/calibrate.py cards/anthropic/claude-fable-5/sections
```

Build and serve the site:

```sh
cd site && pnpm install && pnpm dev   # local dev (search needs a production build)
pnpm build && pnpm preview            # dist/ + Pagefind index
```

Pushing to `main` deploys to GitHub Pages via Actions — never push without explicit
owner request (D13).

## Adding (or generalizing for) a card

The site picks up any new card under `cards/<vendor>/<slug>/` automatically. The
pipeline, though, is currently wired to the first card, so onboarding a second is
partly a generalization exercise:

1. Create `cards/<vendor>/<slug>/` with `source.pdf`, a `meta.yaml` (copy the existing
   one for the field shape), and a `style-manifest.yaml`.
2. Extract the per-page oracle, figure images, and table structure from the PDF.
3. Point the pipeline at the new card — the `CARD` path is hard-coded in
   `pipeline/generate/run.py`, `pipeline/generate/tables.py`, and
   `pipeline/verifier/calibrate.py` (generalizing this is the main shared work).
4. Run assemble + the verifier gates and iterate on divergences.
5. Author the `style-manifest.yaml` (chip/highlight + role colors) and the chip-label
   vocabulary in `meta.yaml`.
6. Open a PR with the new `cards/<vendor>/<slug>/` directory.

## Process rules

- **Commit early and often, without asking** — standing authorization from the
  owner (D12). Commit at milestones and decision points so git history is
  queryable; imperative, concise messages.
- **Never push** — pushes happen only on explicit owner request; push to main
  also triggers the Pages deploy (D13).
- **Record decisions in decisions.md when they're made**, not at session end —
  sessions can compact or die at any time. Append-only; supersede, don't rewrite.
- **Rewrite state.md before stopping** or after any milestone. It's a snapshot;
  git and decisions.md are the history.
- **Experiments** live in `docs/experiments/NN-name/` with a README (question,
  method, result, conclusion) and committed scripts — re-runnable from the writeup
  alone.
- **Sub-agent findings must land in files**, never only in conversation.
- **Diff-per-fix (D25):** `sections/` is git-tracked. After every fix:
  regen → `git diff` the output → confirm the expected change AND scan for
  unexpected ones (regression catch) → preview-check if renderer-visible →
  commit pipeline + output together. Never hand-edit generated files.
- **Never clean up the verifier calibration data** — `cards/*/*/extracted/` and the
  pre-fix git refs (`f60899a`, `fb483fb`); the gates calibrate against them (D5). The
  retired first-attempt working files (`tools/`, the old `sections/`) were removed in
  D28 but remain in git history.
- **Fresh-session test:** these docs must let a cold session continue correctly.
  If they didn't orient you, fixing them is part of your task.
- **Look at the page when data is ambiguous** (owner-encouraged): per-page
  renders live at `cards/*/*/extracted/pages/p-NNN.png` — Read them to resolve
  anything the structured extraction leaves unclear, and `open` them for the
  owner when discussing a page.
- **Never gate on the owner for visual verification** (owner feedback
  2026-06-10): after each fix batch, verify in the rendered DOM/preview and
  page renders YOURSELF, then run the convergence loop — regen → re-slice →
  re-sweep (affected pages + rotating sample) → triage → fix → repeat. The
  owner sees only editorial decisions and converged results, not per-fix
  demos.
