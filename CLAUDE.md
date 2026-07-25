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

The D35 question — one shared pipeline vs per-document pipelines — got its first
empirical answer on 2026-07-25: the **Claude Opus 5 card (193pp) converted through the
shared pipeline** with per-card config only (a `style-manifest.yaml` whose hexes map to
a FIXED role vocabulary, section stubs from the PDF's own bookmarks) plus a handful of
generalization fixes where the first card's heuristics had over-fit (turn-label
grammar, partial-span links, bullet-bold interactions — see D38–D40). Within
Anthropic's Google-Docs-exported document family, one pipeline serves. Other vendors'
PDFs (different producers, different visual grammar) remain untested — expect the
oracle and manifest roles to carry, and the assembler heuristics to need new cases.

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
   deep links, footnotes into sidenotes, per-page OG images, md exports (`card.md`,
   one `.md` per top-level section, `llms.txt` index — all with provenance headers);
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

The pipeline targets the card named by the `CARD` env var (`vendor/slug`; default
`anthropic/claude-fable-5` — see `pipeline/cardcfg.py`, D38). Regenerate the card's
markdown from its PDF, then run the verifier gates (`uv` fetches the Python deps
inline — `pymupdf`, and `docling` for tables):

```sh
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE

# the second card
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/generate/run.py --all
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

The gate passes at **0 majors**; typed residual baselines: fable-5 `L1 31` / `T1 44`,
opus-5 `T1 13` (post-D41/D42 fix batches) — accepted noise, not regressions; re-baseline
here whenever an owner-approved fix batch moves them. `calibrate.py` takes a
git ref or the literal `WORKTREE` (the current sections), not a path. **Any pipeline
change must leave the OTHER card's `sections/` byte-identical** (regen + `git diff`)
— that regression net caught real damage repeatedly during the second onboarding.

Build and serve the site:

```sh
cd site && pnpm install && pnpm dev   # local dev (search needs a production build)
pnpm build && pnpm preview            # dist/ + Pagefind index
```

Pushing to `main` deploys to GitHub Pages via Actions — never push without explicit
owner request (D13).

## Adding (or generalizing for) a card

The site picks up any new card under `cards/<vendor>/<slug>/` automatically. The
procedure that onboarded claude-opus-5 (2026-07-25, one session):

1. Create `cards/<vendor>/<slug>/` with `source.pdf` and a `meta.yaml` (copy the
   existing field shape; `source_pages` is read by the pipeline).
2. **Census the signals** (pymupdf probe over all pages: text colors, fill colors,
   fonts, per-page counts) and author `style-manifest.yaml`: every recurring hex gets a
   role from the fixed vocabulary (D39) — verify ambiguous ones against page renders,
   never guess. Same hex, different card, different role is NORMAL (D39). Set
   `document: toc_pages` (the PDF's own contents pages). No chips → `chips: {}`.
3. Extract ground truth: oracle (auto-cached per-card on first run), page renders
   (`pdftoppm -png -r 150 source.pdf extracted/pages/p`), figures (`pdfimages -p -png`
   + `extract_figures.py` — note the `-p`), docling tables (`tables.py <pages>` with
   candidate pages from a rule-line scan; chart-page false positives are harmless —
   docling returns 0 tables).
4. Create `sections/*.md` stubs from the PDF's bookmark TOC: one file per top-level
   section, `<!-- source: source.pdf pages AAA-BBB -->` headers, split >40pp sections
   at page-top subsection boundaries. Non-overlapping ranges when sections start on
   fresh pages (the shared-page machinery only engages for mid-page boundaries).
5. Run assemble + gates (`CARD=… run.py --all` / `calibrate.py WORKTREE`), iterate to
   0 majors. Fix CLASSES in `pipeline/`, never instances; after every fix regen BOTH
   cards — the other card's diff must stay empty.
6. Seam audit, mutation test (if the verifier changed), then the two agent sweeps
   (rulebook template: `docs/experiments/09-round-g/rulebook.md`) to convergence.
7. Build the site, verify the card page (deep links, sidenotes, turns, search).
8. **Owner scroll pass before certification.** The sweep stack verifies per-page
   CONTENT; it is demonstrably weak on visual-layout classes — cross-element
   overlap (page-marker smear), intra-cell typography tiers, bubble scoping,
   seam artifacts. The opus-5 owner scroll found five such issues after full
   sweep convergence (2026-07-25, state.md). Compare suspicious constructs
   against `extracted/pages/p-NNN.png` side by side.

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
