# Verification & QA methodology

How a converted card is checked for faithfulness to its source PDF. The PDF is
the ground truth; the current `sections/*.md` + rendered site are the accepted
output. Nothing is checked against the retired first attempt — that only ever
served as a labeled test corpus for tuning the gates (see `decisions.md` D5).

Three checking layers, over a common set of extracted inputs.

## Inputs — what everything works from

All derived from `cards/<vendor>/<slug>/source.pdf`:

| Input | Produced by | Path |
| --- | --- | --- |
| Per-page PDF renders | `pdftoppm` (gitignored, regenerable) | `extracted/pages/p-NNN.png` |
| The "oracle" — PyMuPDF facts (text spans + style flags, links, footnotes, highlight/chip fills, page geometry) | `pipeline/verifier/oracle.py` | `pipeline/.cache/oracle.json` |
| Figure images + map | `extracted/process_assets.py` | `assets/figures/`, `extracted/figures-map.json` |
| Internal-link targets | `extracted/extract_internal_links.py` | `extracted/internal-links.json` |
| Table structure | docling | `pipeline/.cache/tables.json` |
| Per-page markdown slices (every md run attributed to page N) | `pipeline/slice_pages.py` | `.cache/<sweep>/slices/p-NNN.md` |
| Served HTML (what the reader gets) | the dev server, or a built snapshot | `localhost:PORT/...` / `served.html` |
| High-zoom region crops (full pages are vision-downscaled to ~1.15MP, too soft for glyph-level checks) | `pipeline/render_region.py PAGE [x0 y0 x1 y1 ZOOM]` | `pipeline/.cache/crops/` |

## Layer 1 — the automated gate

`pipeline/verifier/calibrate.py WORKTREE` runs the invariant gates
(`pipeline/verifier/invariants.py`: T1 text tokens, L1 links, FN1 footnotes,
S1 bold, S2 chips, ST structure, …) comparing the markdown (projected to
comparable facts by `mdproj.py`, normalized by `norm.py`) against the oracle.
It fails on any unexplained divergence. Calibrated against the labeled defect
history and mutation-tested for recall (`mutate.py`). Baseline = **0 majors**;
`L1 31` / `T1 ~70` are accepted typed residuals. See `verification-contract.md`
for the invariant IDs and exclusions.

This layer is token/link/style/structure level. It **cannot see** layout and
visual structure — split list items, mis-merged paragraphs, a value shifted one
table column, a swallowed line. That's layer 2.

## Layer 2 — agent inspection sweeps

Two complementary fleets of AI inspectors, each **armed with a rulebook** (the
accepted-divergence list, severity definitions, the page→section map, and the
output schema). Inspectors **report only — they never edit anything**; the
orchestrator owns every fix (layer 3). A reusable rulebook template lives at
`docs/experiments/09-round-g/rulebook.md` (update its paths/sweep name per run).

**(a) Markdown-smell linter.** Agents read the `sections/*.md` for suspicious
patterns — mid-token emphasis ends (`<b>Mythos</b> 5`), dangling markup,
inconsistent row styling, spacing/structure smells — then cross-check every hit
against the PDF page render (high-zoom crops for any glyph-level claim) before
reporting. Good at catching defects that are invisible once rendered.

**(b) Triple-pane comparator.** For each page, agents compare three views and
flag anything in pane 1 the others fail to capture:
1. the **PDF page render** (`extracted/pages/p-NNN.png`) — source of truth;
2. the **per-page md slice** (`slice_pages.py`) — what was transcribed;
3. the **served-HTML DOM** — what the reader actually gets (the arbiter when md
   syntax is ambiguous: tags, list types, table cells, `<b>`/`<u>`, pills,
   blockquote nesting).
Dense constructs (tables, transcripts, small text) are judged from crops, not
full pages.

Each agent appends one JSON line per page/file as it finishes (partials must
survive a killed run): `{page, status, findings:[{severity, construct, desc,
evidence, verdict}]}`. `verdict` ∈ confirmed | uncertain | source-faithful
(looked sus, the PDF agrees — reported so the rulebook can grow).

## Layer 3 — the convergence loop (orchestrator-owned, D25)

Per finding: **diagnose → fix the CLASS** (in `pipeline/`, never the single
instance, never by hand-editing generated files) **→ regen → `git diff` the
`sections/` output** (confirm the expected change AND scan for regressions) **→
preview-verify** if renderer-visible **→ seam audit + gate → commit pipeline +
output together.** Then **re-sweep** the affected pages plus a rotating sample,
and repeat until a round comes back clean. The owner sees editorial decisions
and converged results, not per-fix demos.

## Provenance

The build ran this loop to convergence over many rounds; the record is in
`docs/experiments/` (07 = first vision sweep; 08 = convergence; 09 = the
two-check round-G design + its rulebook), with the accepted divergences and the
diff-per-fix protocol settled in `decisions.md` (D24, D25).
