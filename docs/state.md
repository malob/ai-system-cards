# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-08-14 (late evening) — **third card converted and
converged, awaiting the owner scroll pass.** Anthropic published its **Risk
Report: August 2026** (public redacted edition, 186pp, RSP v3.4 — the
archive's first non-system-card document, D44) at ~17:41 UTC; it went through
the full pipeline the same day: census → manifest → stubs → assemble → 0
majors → seam audit → mutation test → two full agent sweep rounds → site
build, all local. **NOT deployed** — pushes only on explicit owner request
(D13).

## Status

- **fable-5: live**, byte-identical through every pipeline change today.
  Gate: 0 majors / `L1 31` / `T1 44`.
- **opus-5: live**, byte-identical likewise. Gate: 0 majors / `T1 13`.
- **risk-report-2026-08: converged, awaiting owner scroll pass (step 8) +
  deploy decision.** Gate: 0 majors / `FN1 1` (declared orphan-ref source
  defect — the PDF's own stray superscript 18 on p.126, D45) / `T1 26`
  (docling cell tokenization + seam displacement noise). Seam audit 0.
  Mutation recall at the calibrated band (loss classes 100%). 10/10
  rendered-page assertions pass on the production build.

## What today established (pointers, not narrative)

1. **D44** — the archive's scope now includes non-system-card safety
   documents; slug convention `risk-report-YYYY-MM`; `doc_type` meta field
   drives the eyebrow/OG/export labels.
2. **D45** — onboarding generalizations: footnote-region walk (long quoted
   footnotes), orphan-fnref source-defect rule, links inside docling table
   cells (`_inject_links`), in-bubble list items.
3. **D46 + experiment 11** — the sweeps found ~40 distinct majors in 9
   classes that the gates cannot see (tables/anchors/styling); all fixed at
   class level; `link_text_resolution: extended` is a per-card manifest knob
   because the same rules would re-anchor certified fable/opus links (owner
   may enable later). Round 2: 15-page regression sample fully clean; 7
   residuals fixed and directly verified.
4. **The byte-identity regression net caught five real canon breaks** during
   the fix batches — it is the load-bearing safety mechanism for shared-
   pipeline evolution.

## Open — owner attention needed

- **Owner scroll pass** on the risk-report page (step 8; sweeps are
  content-strong, visual-layout-weak). Table-dense stretches: pp.10-14, 22,
  78-80, 115-119, 123-132, 155-156, 182-185; boxed prompts pp.72-74/84-86.
- **Deploy decision** (push to main → Pages).
- **Deferred typed minors** (experiment 11 README §Deferred): p.13 cell
  paragraph merge, p.153 shallow-indent quotes, p.36 code-span color,
  footnote URL wrap spaces, p.42 blockquote-wrapped sub-list.
- **Editorial flags:** index-page intro copy is system-card-specific ("when
  AI companies release a new model…") — may want a line acknowledging risk
  reports; p.22's color-coded rating cells render as plain cells (text
  carries the ratings — declared exclusion; a renderer treatment is possible
  if wanted); `link_text_resolution: extended` could be enabled for
  fable/opus after adjudicating the handful of anchor changes it implies.

## Cold-start capsule

The first attempt converted one card but needed so much manual review the owner
judged it unmaintainable. The rebuild's goal: hand over a PDF, the pipeline runs
unattended, the owner certifies after a short flag-directed review.
Verification-first: the gates were built and calibrated before the generator.
Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D46),
[design-brief.md](design-brief.md) (§2 defect taxonomy), and
[verification-methodology.md](verification-methodology.md) (4 layers: gates →
agent sweeps → convergence loop → owner scroll). Three cards have now proven
the architecture: within Anthropic's Google-Docs-export family, one pipeline
serves with per-card config (manifest roles, stubs, and now grammar knobs like
`link_text_resolution`); every fix is a class in `pipeline/`, never an
instance; the other cards' byte-identity is the regression net for all of it.
A different vendor's PDF (different producer) remains the next architectural
test.
