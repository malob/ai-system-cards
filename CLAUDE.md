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
four-document answer: **Claude Fable 5 & Claude Mythos 5** (317pp), **Claude Opus 5**
(193pp), **Risk Report: August 2026** (186pp), and **Claude Fable 5.1 & Claude
Mythos 5.1** (212pp) all convert through the shared pipeline. Per-document config supplies manifest roles, section stubs, and narrowly
scoped grammar knobs; generalization fixes live as classes in `pipeline/`, never as
document-instance patches (D38–D48, D62). This proves one pipeline only within Anthropic's
Google-Docs-export family. Other vendors' PDFs (different producers and visual
grammars) remain untested. Phase-4 structural-authority integration is paused. The
immediate task is the shadow table extraction/grid program in
`docs/experiments/13-table-candidate-shadow/`: a raw-rule origin/projection overlay now
composes topology and word ownership for the fully ruled hard set without mutating
extractor claims. Challenge its candidate-conditioned grid, add the missing natural
absent-rule negative and sparse/unruled coverage, preserve style/link semantics,
establish second-platform and different-producer replay, and prove all-card net legacy
deletion before any production adoption. A different producer, clean
bootstrap, every projection, and computed-browser visibility remain later
architectural tests, not implied current capability.

## How a document is produced

The conversion is **mechanical — no LLM transcribes or edits the content** — so
fidelity is reproducible and checkable. Four stages:

1. **Observe** the PDF: PyMuPDF facts (text spans with style flags, links, raw
   footnotes, highlight/chip fills, geometry, raster occurrences, per-page renders) +
   docling table candidates → `cards/<vendor>/<slug>/extracted/`. The PDF is source
   truth; these are pinned, fallible observations.
2. **Assemble** (`pipeline/generate/`): a block compiler builds the document from those
   facts and serializes to `sections/*.md`.
3. **Verify** (`pipeline/verifier/`): independent invariant gates compare output to
   source observations. L2 binds exact internal destinations; P2/F3 independently bind
   every source page/raster and carry exact page/figure/event/asset expectations into
   the rendered DOM; RF1 checks a narrow raw-PDF footnote lane without generator/oracle
   zoning; V1 prevents authored raw HTML from hiding semantic content. Consequence-
   aware T1/FN1 severity blocks critical numbers, dates, units/currencies, negations,
   and comparators even at one or two tokens. Unsuppressed majors fail; typed minors
   route attention. Every scope is explicit and mutation-tested.
4. **Render** (`site/`): Astro stitches `sections/*.md`, makes page markers into PDF
   deep links, footnotes into sidenotes, per-page OG images, md exports (`card.md`,
   one `.md` per top-level section, `llms.txt` index — all with provenance headers);
   Pagefind search.

## Pipeline modules

Core, run every regen:

| Module | Role |
| --- | --- |
| `verifier/oracle.py` | legacy structured PyMuPDF observations (the historical "oracle") |
| `generate/assemble.py` | oracle facts → typed blocks |
| `generate/tables.py` | table reconstruction (docling structure + oracle geometry) |
| `generate/serialize.py` | typed blocks → `sections/*.md` |
| `generate/run.py` | orchestrates assemble → `sections/` |
| `verifier/{invariants,mdproj,norm}.py` | canonical gates · md→facts projection · production text normalization |
| `verifier/l2_links.py` | source-first `/GoTo` occurrence → exact accepted-heading target |
| `verifier/source_inventory.py` | PDF-first page/raster authority (P2/F3) + deterministic final-DOM artifact |
| `verifier/raw_footnotes.py` | zoning-independent numeric footnote occurrence/body authority (RF1) |
| `verifier/{dangling_footnotes,critical_tokens}.py` | output footnote closure · consequence-aware T1/FN1 atoms |
| `verifier/calibrate.py` | run the gates (sections vs oracle) |
| `site/src/lib/{l2-artifact,article-dom,source-projection}.js` | strict artifacts · serialized/final DOM link/page/figure/asset audits |
| `site/src/lib/markdown.js` | production renderer + authored-raw-HTML V1 policy |
| `pipeline/verify_release.py` | one pinned local fast-release graph over every discovered card + site build |

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

env CARD=anthropic/claude-fable-5-1 uv run --with pymupdf python pipeline/generate/run.py --all
env CARD=anthropic/claude-fable-5-1 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

Full generation now prints the pinned, corpus-wide handoff below. After the site
lockfile is installed, this is the preferred fast release command: it discovers the
same cards the site can publish, runs all verifier tests, gates/artifact comparisons
and seams in parallel, then runs the production renderer tests and clean build.

```sh
uv run --python 3.12 --with 'pymupdf==1.28.2' python pipeline/verify_release.py
```

All four gates pass at **0 unsuppressed majors**, and each has a 0-seam baseline.
Fable has 20 exact accepted T1 majors: 3 historical owner-adjudicated visual-order
findings and 17 maintainer/source-adjudicated table-order findings under broad owner
authorization. Opus has 4 maintainer/source-adjudicated exact T1 findings; Risk has 1; Fable 5.1 has 5
(the pp.159–160 seam attribution of a table row cut mid-cell, and the p.210 code-box
label 'None' stream-order class, D62).
The 22 new findings were exposed by removing blanket table demotion, not by changing
card content. A new finding on the same page is not covered, and a stale acceptance
makes a full `WORKTREE` gate fail. Typed minor baselines are fable-5 `L1 34` / `T1 28`;
opus-5 `T1 8`; risk-report-2026-08 `FN1 1` (declared orphan-ref source defect,
D45) / `T1 6` / `TB2 1` (seam-cell advisor); and claude-fable-5-1 `T1 3` (three repeated-header drops of its seven-page appendix table). The opus/risk T1 counts fell from 9/21
when D62's projection classes removed phantom-space and bullet-glyph false minors.
L2 is clean at 108 Fable, 54 Opus, and 66 Fable 5.1 authored destinations (67 authored
occurrences), plus 121 Risk Report logical destinations over 123 authored occurrences;
source expectations cover all 352 authored occurrences. Fable's three additional L1 minors are publisher-broken
named destinations, reported even when one uniquely printed heading can be recovered
under R2.
P2/F3 source authority requires 309 pages/151 rendered figures for Fable, 187/98 for
Opus, 180/14 for Risk, and 206/103 for Fable 5.1. The built audit totals 882 page
markers, 366 rendered figures, and 371 exact copied raster assets, with 0 findings. RF1 is clean at raw reference/definition counts 76/76, 36/36, 93/92, and 30/30 (Fable
5.1); Risk's difference is the exact,
source-hash-bound disposition for the publisher's stray p.126 superscript 18.
These are measured residuals, not permission to ignore drift; re-baseline here only
after an owner-approved fix batch moves them. `calibrate.py` takes a git ref, the
literal `WORKTREE` (the current sections), or an absolute sections directory.
Unsuppressed majors exit 1; malformed/stale acceptance configuration exits 2.
`--report-only` is the explicit diagnostic escape hatch for majors and never masks
acceptance-configuration errors (D49).

Generic `accepted.json` entries are deliberately invalid for L2, P2, F3, RF1, and
V1. P2/F3/RF1 exceptions must use their exact source-bound authority, and L2/V1 allow
no generic exception.

L2 runs only on a complete document graph. After a source or canonical-section change,
regenerate the tracked, hash-bound expectation artifact as part of the full gate:

```sh
env CARD=anthropic/claude-fable-5 uv run --python 3.12 --with pymupdf==1.28.2 \
  python pipeline/verifier/calibrate.py WORKTREE \
  --l2-json cards/anthropic/claude-fable-5/l2-links.json \
  --source-projection-json cards/anthropic/claude-fable-5/source-projection.json
```

CI regenerates both artifacts to temporary paths and requires byte identity with the
tracked files. Site tests independently recompute source, inventory, figure-map,
aggregate canonical, and per-section hashes before trusting any expected target or
event stream; stale, malformed, or incomplete artifacts fail closed.

**Regression scope is the target plus every non-target certified document.** For the
current corpus, a shared-pipeline change therefore requires regenerating and gating
all four documents. Each non-target's `sections/` must remain byte-identical (`git
diff`) unless an owner-approved, PDF-verified fidelity improvement intentionally moves
its canon. This regression net has repeatedly caught real cross-document damage.

After regeneration, run the seam audit for each regenerated document. If verifier
code/inputs or document canon changed, run the seeded mutation suite for the target
and every certified document; 8 trials per class is the current default/calibration
size. The `repoint-link` class preserves a live internal link but changes it to a
different existing heading; L2 must catch what existence-only audits cannot. Current
seed-5 schema-v2 floors separate detection, intended-major severity, and actual major
blocking. Fable's 25 classes / 200 trials are 191 / 184 / 185; Opus's 24 / 192 are
176 / 168 / 171; Risk's 24 / 192 are 173 / 166 / 171; Fable 5.1's 24 / 192 are 178 / 170 / 170
(`flatten-chip` is inapplicable on the latter three: no chips). Across 776 trials the
totals are 718 detected, 688 intended-major, and 697 major-blocked. V1/P2/F3/L2 and every critical T1/FN1 class are 8/8 wherever
eligible; misses concentrate in ST1/ST2/ST3, L1, S1, and ordinary advisory word swaps.
The strict artifacts combine independent per-class runs with the final hide-image/V1
refresh. Hosted mutation run
[31929996953](https://github.com/malob/ai-system-cards/actions/runs/31929996953)
replayed all 584 trials on deployed HEAD `3d7b851`; downloaded artifacts normalized
with key-sorted `jq` match the committed baselines exactly. The steps took 12m54s for
Opus, 20m05s for the Risk Report, and 37m36s for Fable. The earlier run
[31928741823](https://github.com/malob/ai-system-cards/actions/runs/31928741823)
was cancelled only because Fable exceeded the old 30-minute timeout; the 45-minute
follow-up completed the unchanged floor. Hosted fast-release / Pages run
[31929997079](https://github.com/malob/ai-system-cards/actions/runs/31929997079)
also succeeded for `3d7b851`, so phase 3 is deployed and certified. Canonical sections
and the byte-identical built site did not change. D58 pauses further phase-4
integration and pulls the isolated table-candidate experiment forward. D59 records
its typed source-word alignment slice: 10 cases on nine pages, 790 PDF words and 274
reviewed cell labels; 43 changes across four tables, three natural no-ops, and three
fail-closed cases under deterministic two-run replay and 17/17 new tests. It remains
shadow research. D60 records the raw-rule origin/projection follow-up: 274/274 ranges
and 790/790 words derived across the ruled set, joint resolution of Opus p.56 table 1
and raw Fable p.95, 12/12 root plus 10/10 source-reopening tests, and an independent
9/12 verdict of commit shadow yes / production no. Neither slice has any hosted,
deployed, production, card-content, or site-output effect.
Classes use independent digest-derived RNG streams, so adding one cannot resample the
others:

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
pnpm test                             # exports, inventory, raw-HTML policy, L2/P2/F3 DOM
pnpm build && pnpm preview            # dist/ + link/page/figure/asset audit + Pagefind
```

`.github/workflows/verify.yml` derives its card matrix from the same repository
inventory the site publishes, then runs the unit suite, every discovered card's full
gate + tracked L2/source-projection freshness checks + seam audit, the export/inventory/
hash-bound article-DOM tests, and a clean site build with link/page/figure/asset audits directly
on pull requests and non-main branch pushes. A synthetic-fourth-card test prevents
site/CI inventory drift. On `main`, the Pages workflow calls that same workflow and
will not build/deploy until it passes. Mutation sensitivity is a separate baseline-
aware relevant-change push/pull-request, weekly, and manual workflow because it is
intentionally slower. Pushing to `main` deploys to GitHub Pages via Actions — never
push without explicit owner request (D13).

## Adding (or generalizing for) a document

The site picks up any new system card or safety report under
`cards/<vendor>/<slug>/` automatically. The procedure proven across the four current
documents is:

Manual setup is acceptable when it records genuine document-specific judgment, such
as visual roles or editorial section boundaries. Automate derived observations and
make reviewed inputs explicit; do not optimize away a small setup step without
measured conversion leverage. The current section stubs mix reviewed plan input with
generated output. Separating that plan is useful secondary cleanup, not the immediate
table task and not a mandate to automate editorial decisions.

1. Create `cards/<vendor>/<slug>/` with `source.pdf` and a `meta.yaml` (copy the
   existing field shape; `source_pages` is read by the pipeline). That `meta.yaml`
   makes the card discoverable by both the site and the full-gate CI matrix; never add
   a separate workflow literal.
2. **Census the signals** (pymupdf probe over all pages: text colors, fill colors,
   fonts, per-page counts) and author `style-manifest.yaml`: every recurring hex gets a
   role from the fixed vocabulary (D39) — verify ambiguous ones against page renders,
   never guess. Same hex, different card, different role is NORMAL (D39). Set
   `document: toc_pages` (the PDF's own contents pages). No chips → `chips: {}`.
3. Extract candidate observations: oracle (auto-cached per-document on first run), page renders
   (`pdftoppm -png -r 150 source.pdf extracted/pages/p`), figures (`pdfimages -p -png`
   + `extract_figures.py` — note the `-p`), docling tables (`tables.py <pages>` with
   candidate pages from a rule-line scan; chart-page false positives are harmless —
   docling returns 0 tables). These are claims about the PDF, not self-authorizing
   truth.
4. **Establish source authority.** Observe every page and raw raster with
   `source_inventory.py`; review cover/TOC/blank and duplicate-draw proposals against
   the PDF; commit an exact `source-inventory.json` bound to the source SHA-256,
   PyMuPDF version, observer schema, and repeated observation. Every occurrence is
   required by default. Do not copy `toc_pages` or `figures-map.json` into exclusions:
   the gate challenges those generator claims. If RF1 finds a genuine publisher
   artifact, add only the exact source occurrence to
   `source-footnote-dispositions.json`; never widen RF1 to keep the gate green.
5. Create `sections/*.md` stubs from the PDF's bookmark TOC: one file per top-level
   section, `<!-- source: source.pdf pages AAA-BBB -->` headers, split >40pp sections
   at page-top subsection boundaries. Non-overlapping ranges when sections start on
   fresh pages (the shared-page machinery only engages for mid-page boundaries).
6. Run assemble + the card diagnostic (`CARD=… run.py --all` /
   `calibrate.py WORKTREE`), iterate to 0 unsuppressed majors, and generate both
   `l2-links.json` and `source-projection.json`. L2 must bind every source
   `/GoTo` occurrence to an exact accepted heading or a declared R2 source defect; its
   source/canonical hashes must match current bytes. P2/F3 must bind every source page,
   raw raster, disposition, map/asset claim, and ordered final-DOM event. Fix CLASSES
   in `pipeline/`, never instances. After every fix, regenerate and gate the target
   plus every non-target certified document; inspect every diff, and require non-target
   byte identity unless a PDF-verified canon improvement was explicitly approved.
7. Run the pinned corpus-wide `pipeline/verify_release.py`; it owns all card gates,
   artifact freshness, seams, site tests, and the clean build. If verifier/renderer
   code, source authority, or document canon changed, run the strict 8-trial, seed-5
   schema-v2 mutation suite across every certified document. Then run the two agent
   sweeps (rulebook template:
   `docs/experiments/09-round-g/rulebook.md`) to convergence.
8. Verify the production preview: the hash-bound article-DOM lane must preserve every
   authored link/target and source-bound page/figure event; copied source PDF/PNG bytes
   must be exact; the full page must have a closed, unique fragment graph. Check the
   document page, sidenotes, turns, exported Markdown, search, and responsive behavior.
   V1 rejects authored raw HTML with known browser-hidden semantics, but computed CSS,
   clipping/occlusion, and viewport visibility still require this inspection.
9. **Owner scroll pass before certification.** The sweep stack verifies per-page
   CONTENT; it is demonstrably weak on visual-layout classes — cross-element
   overlap (page-marker smear), intra-cell typography tiers, bubble scoping,
   seam artifacts. Every certified document has completed this gate (the opus-5 owner scroll found six
such issues after full sweep convergence, 2026-07-25; the risk-report owner scroll
completed 2026-08-15); claude-fable-5-1 awaits it. Compare suspicious constructs
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
- **Do not weaken source authority with generic acceptance.** `accepted.json` may not
  contain L2, P2, F3, RF1, or V1. Use an exact source-bound inventory/disposition only
  where that invariant defines one; L2 and V1 permit no generic exception.
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
