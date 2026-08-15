# AI System Cards

Archive of AI system cards and safety reports, each converted from its source PDF into
a faithful web page (Astro → GitHub Pages) by a mechanical, verifier-gated pipeline
— no LLM transcribes the content. The pipeline is a ground-up rebuild of a
labor-intensive first attempt (the rebuild was called "v2" during development; that's
why the design docs say v2). README.md is the human-facing overview; **this file is the
operational playbook** — how to run the pipeline, add or improve a document, and the
process rules. `docs/` holds the design notes and decision log.

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

The D35 question — one shared pipeline vs per-document pipelines — now has a
three-document answer: **Claude Fable 5 & Claude Mythos 5** (317pp), **Claude Opus 5**
(193pp), and **Risk Report: August 2026** (186pp) all convert through the shared
pipeline. Per-document config supplies manifest roles, section stubs, and narrowly
scoped grammar knobs; generalization fixes live as classes in `pipeline/`, never as
document-instance patches (D38–D48). This proves one pipeline only within Anthropic's
Google-Docs-export family. Other vendors' PDFs (different producers and visual
grammars) remain untested; a different vendor is the next architectural test.

## How a document is produced

The conversion is **mechanical — no LLM transcribes or edits the content** — so
fidelity is reproducible and checkable. Four stages:

1. **Extract** ground truth from the PDF: a PyMuPDF "oracle" (text spans with style
   flags, links, footnotes, highlight/chip fills, geometry, per-page renders) + docling
   for table structure → `cards/<vendor>/<slug>/extracted/`.
2. **Assemble** (`pipeline/generate/`): a block compiler builds the document from those
   facts and serializes to `sections/*.md`.
3. **Verify** (`pipeline/verifier/`): independent invariant gates (text tokens, links,
   bold/chip styling, block structure, tables, figures, footnotes, page markers) compare
   output to the oracle; unsuppressed majors fail, while typed minors route attention.
   Each invariant's scope is explicit, historically calibrated, and mutation-tested.
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
`extracted/figures-map.json`; run once when onboarding a document), `verifier/mutate.py`
(mutation-tests gate recall — run when verifier inputs or document canon change), `slice_pages.py` /
`render_region.py` (per-page md slices / zoom crops for the sweeps), `audit_table_seams.py`
(table cross-page seam check).

## Running the pipeline

The pipeline targets the document named by the `CARD` env var (`vendor/slug`; default
`anthropic/claude-fable-5` — see `pipeline/cardcfg.py`, D38). Regenerate its markdown
from the PDF, then run the verifier gates (`uv` fetches the Python deps inline —
`pymupdf`, and `docling` for tables):

```sh
env CARD=anthropic/claude-fable-5 uv run --with pymupdf python pipeline/generate/run.py --all
env CARD=anthropic/claude-fable-5 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE

env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/generate/run.py --all
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE

env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/generate/run.py --all
env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

All three gates pass at **0 unsuppressed majors**, and each has a 0-seam baseline.
Fable also has 3 owner-accepted T1 majors, each matched by the complete finding
fingerprint in `accepted.json`; a new finding on the same page is not covered, and a
stale acceptance makes a full `WORKTREE` gate fail. Typed minor baselines are
fable-5 `L1 31` / `T1 44`; opus-5 `T1 13`; and risk-report-2026-08 `FN1 1`
(declared orphan-ref source defect, D45) / `T1 22` / `TB2 1` (seam-cell advisor).
These are measured residuals, not permission to ignore drift; re-baseline here only
after an owner-approved fix batch moves them. `calibrate.py` takes a git ref, the
literal `WORKTREE` (the current sections), or an absolute sections directory.
Unsuppressed majors exit 1; malformed/stale acceptance configuration exits 2.
`--report-only` is the explicit diagnostic escape hatch for majors and never masks
acceptance-configuration errors (D49).

**Regression scope is the target plus every non-target certified document.** For the
current corpus, a shared-pipeline change therefore requires regenerating and gating
all three documents. Each non-target's `sections/` must remain byte-identical (`git
diff`) unless an owner-approved, PDF-verified fidelity improvement intentionally moves
its canon. This regression net has repeatedly caught real cross-document damage.

After regeneration, run the seam audit for each regenerated document. If verifier
code/inputs or document canon changed, run the seeded mutation suite for the target
and every certified document; 8 trials per class is the current default/calibration
size:

```sh
# Repeat for every document in the regression scope.
env CARD=anthropic/claude-fable-5 python3 pipeline/audit_table_seams.py
env CARD=anthropic/claude-fable-5 uv run --python 3.12 --with pymupdf==1.28.2 \
  python pipeline/verifier/mutate.py --per-class 8 --seed 5 \
  --baseline docs/experiments/05-mutation-testing/results-anthropic-claude-fable-5.json \
  --json /tmp/mutation-anthropic-claude-fable-5.json
```

Build and serve the site:

```sh
cd site && pnpm install && pnpm dev   # local dev (search needs a production build)
pnpm build && pnpm preview            # dist/ + Pagefind index
```

`.github/workflows/verify.yml` runs the unit suite, all three full gates + seam
audits, and a clean site build directly on pull requests and non-main branch pushes.
On `main`, the Pages workflow calls that same workflow and will not build/deploy
until it passes. Mutation sensitivity is a separate relevant-change push/pull-request,
weekly, and manual workflow because it is intentionally slower. Pushing to `main`
deploys to GitHub Pages via Actions — never push without explicit owner request
(D13).

## Adding (or generalizing for) a document

The site picks up any new system card or safety report under
`cards/<vendor>/<slug>/` automatically. The procedure proven across the three current
documents is:

1. Create `cards/<vendor>/<slug>/` with `source.pdf` and a `meta.yaml` (copy the
   existing field shape; `source_pages` is read by the pipeline).
2. **Census the signals** (pymupdf probe over all pages: text colors, fill colors,
   fonts, per-page counts) and author `style-manifest.yaml`: every recurring hex gets a
   role from the fixed vocabulary (D39) — verify ambiguous ones against page renders,
   never guess. Same hex, different card, different role is NORMAL (D39). Set
   `document: toc_pages` (the PDF's own contents pages). No chips → `chips: {}`.
3. Extract ground truth: oracle (auto-cached per-document on first run), page renders
   (`pdftoppm -png -r 150 source.pdf extracted/pages/p`), figures (`pdfimages -p -png`
   + `extract_figures.py` — note the `-p`), docling tables (`tables.py <pages>` with
   candidate pages from a rule-line scan; chart-page false positives are harmless —
   docling returns 0 tables).
4. Create `sections/*.md` stubs from the PDF's bookmark TOC: one file per top-level
   section, `<!-- source: source.pdf pages AAA-BBB -->` headers, split >40pp sections
   at page-top subsection boundaries. Non-overlapping ranges when sections start on
   fresh pages (the shared-page machinery only engages for mid-page boundaries).
5. Run assemble + gates (`CARD=… run.py --all` / `calibrate.py WORKTREE`), iterate to
   0 majors. Fix CLASSES in `pipeline/`, never instances. After every fix, regenerate
   and gate the target plus every non-target certified document; inspect every diff,
   and require non-target byte identity unless a PDF-verified canon improvement was
   explicitly approved.
6. Run the seam audit. If verifier code/inputs or document canon changed, run the
   8-trial, seed-5 mutation suite across the target and every certified document.
   Then run the two agent sweeps (rulebook template:
   `docs/experiments/09-round-g/rulebook.md`) to convergence.
7. Build the site (`cd site && pnpm build`), then verify the document page, deep links,
   sidenotes, turns, exported markdown, and search in the production preview.
8. **Owner scroll pass before certification.** The sweep stack verifies per-page
   CONTENT; it is demonstrably weak on visual-layout classes — cross-element
   overlap (page-marker smear), intra-cell typography tiers, bubble scoping,
   seam artifacts. Every current document has completed this gate; the opus-5
   owner scroll found six such issues after full sweep convergence (2026-07-25), and
   the risk-report owner scroll completed on 2026-08-15. Compare suspicious constructs
   against `extracted/pages/p-NNN.png` side by side. An owner scroll is certification
   evidence, not permission to push; the no-push rule below still applies.

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
