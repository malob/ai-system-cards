# AI System Cards

Archive of system cards from AI companies, each converted from its source PDF into a faithful
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
6. [docs/verification-methodology.md](docs/verification-methodology.md) — how output is
   checked: extraction inputs, the automated gate, the two agent inspection sweeps
   (markdown-smell linter + triple-pane comparator), and the convergence loop.
   [docs/verification-contract.md](docs/verification-contract.md) holds the invariant IDs.

## Where this is headed

The pipeline is **heavily specialized to this first document** — its chip vocabulary,
table shapes, transcript styles, the hard-coded card paths, and gates calibrated to
*its* specific defects. It likely won't generalize cleanly even to Anthropic's *other*
system cards, let alone other companies'. It's a strong starting point, not a general
tool — and we don't pretend otherwise.

**Next milestone (empirical):** convert a *second* document and find out whether one
shared pipeline (with per-card config/manifests) can serve many, or whether each
document needs its own pipeline. That question is open until we try. Shipping the
first card does not depend on resolving it.

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

## Pipeline modules

Core, run every regen:

| Module | Role |
| --- | --- |
| `verifier/oracle.py` | extract ground-truth facts from the PDF (the "oracle") |
| `generate/assemble.py` | oracle facts → typed blocks |
| `generate/tables.py` | table reconstruction (docling structure + oracle geometry) |
| `generate/serialize.py` | typed blocks → `sections/*.md` |
| `generate/run.py` | orchestrates assemble → `sections/` |
| `verifier/{invariants,mdproj,norm}.py` | the gates · md→facts projection · text normalization |
| `verifier/calibrate.py` | run the gates (sections vs oracle) |

Not per-regen: `generate/extract_figures.py` (PDF figure images → `assets/figures/` +
`extracted/figures-map.json`; run once when onboarding a card), `verifier/mutate.py`
(mutation-tests the gates' recall — run when you change the verifier), `slice_pages.py` /
`render_region.py` (per-page md slices / zoom crops for the sweeps), `audit_table_seams.py`
(table cross-page seam check).

## Running the pipeline

Regenerate the card's markdown from its PDF, then run the verifier gates (`uv` fetches
the Python deps inline — `pymupdf`, and `docling` for tables):

```sh
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

The gate passes at **0 majors**; `L1 31` and `T1 ~70` are accepted typed residuals
(the current baseline), not regressions. `calibrate.py` takes a git ref or the literal
`WORKTREE` (the current sections), not a path.

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
2. Extract the per-page oracle (`verifier/oracle.py`), figure images
   (`generate/extract_figures.py`), and table structure (docling) from the PDF.
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
- **Never rewrite the verifier calibration corpus** — the pre-fix git refs (`f60899a`,
  `fb483fb`) and the retired `tools/` / old `sections/` (removed in D28, intact in git
  history); the gates calibrate against those refs (D5). The *working-tree*
  `cards/*/*/extracted/` carries only what the current process uses — the figure map,
  image inventory, and page renders (D36); dead v1 extraction artifacts were removed
  (recoverable from the refs, regenerable from `source.pdf`).
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
