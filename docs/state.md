# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-07-25 (post-ship rewrite) — **two cards LIVE** at
malob.github.io/ai-system-cards. The Claude Opus 5 card (193pp, PDF released
2026-07-24) shipped 2026-07-25 — converted, converged, and deployed the day after
release, answering D35's question for the within-Anthropic case: **one shared
pipeline serves, with per-card config** (D38–D40).

## Status

- **fable-5: live** (June 11 PDF revision, D37, plus the 2026-07-25 fidelity and
  renderer improvements — same-construct fixes carried over from the opus work).
  Gate: 0 majors / `L1 31` / `T1 44`.
- **opus-5: live** (2026-07-25). Gate: 0 majors / `T1 13`.
- Baselines are re-recorded in CLAUDE.md §"Running the pipeline" whenever an
  owner-approved batch moves them. Verifier calibration corpus (D5) untouched:
  refs `f60899a`/`fb483fb`.

## How the second card converged (pointers, not narrative)

One day, four phases — details live in the decision log and experiment 10:

1. **Onboard + gate** (D38–D40): census → manifest → stubs → assemble → 0 majors
   same day. Procedure: CLAUDE.md §"Adding a card".
2. **Sweeps** (experiment 10): round 1 found 15 majors in 8 classes (all class-
   fixed); round 2 verified fixes + found 1 more; both cards held as each
   other's regression net throughout.
3. **Owner adjudication batches** (D41/D42): all eight deferred minors fixed
   (glyph repair, cell italics/bolds, stacked lines, blockquotes, fence chrome,
   fence blank lines, hl coalescing), verified by a 25-unit spot re-sweep that
   caught one repair miss (ZWSP alignment).
4. **Owner scroll review**: six further visual-layout finds, all fixed and
   final-swept (18 units, zero regressions). Lesson institutionalized:
   onboarding step 8 (CLAUDE.md) + verification-methodology layer 4 — the
   sweeps are content-strong but visual-layout-weak; a human scroll pass
   belongs before certification.

Also shipped 2026-07-25: **md export suite** (card.md with provenance header +
linked contents; a standalone `.md` per top-level section; llms.txt index of
everything) and **D43** (tables serialize one `<tr>` per line — canon
whitespace change, proven newline-collapse-identical and render-inert).

## Open

- Nothing blocking. Typed residuals (`T1 13` / `L1 31 + T1 44`) are owner-
  accepted noise. One typed cosmetic on the books: docling-lost space in one
  restored cell (fable p.243 `” —robust`; the glyph repair deliberately keeps
  docling spacing — owner-accepted).
- Renderer typographer decision recorded (owner, 2026-07-25): the quote
  educator stays on; md/card.md/llms.txt remain the fidelity artifacts.
- **Next milestone:** a third document from a *different vendor* (different PDF
  producer) — the real test of the oracle/manifest architecture beyond
  Google-Docs exports. Expect the oracle and manifest roles to carry; expect
  new assembler cases.

## Cold-start capsule

The first attempt converted one card but needed so much manual review the owner
judged it unmaintainable. The rebuild's goal: hand over a PDF, the pipeline runs
unattended, the owner certifies after a short flag-directed review.
Verification-first: the gates were built and calibrated before the generator.
Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D43),
[design-brief.md](design-brief.md) (§2 defect taxonomy), and
[verification-methodology.md](verification-methodology.md) (4 layers: gates →
agent sweeps → convergence loop → owner scroll). The second card validated the
architecture end-to-end: census → manifest → stubs → assemble → gate → sweeps →
scroll, with the other card held byte-identical as the regression net for every
pipeline change.
