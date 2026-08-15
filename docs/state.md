# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-08-15 (midday) — **third card converged and the two
certified cards regression-swept clean. Awaiting the owner's deploy
decision.** Anthropic's **Risk Report: August 2026** (public redacted
edition, 186pp, RSP v3.4 — the archive's first non-system-card document,
D44) went through the full pipeline on 2026-08-14, then a ship-gate sweep,
an owner scroll pass, and a certified-card regression sweep on 2026-08-15.
**NOT deployed** — pushes only on explicit owner request (D13).

## Status

- **fable-5: live.** Gate 0 majors / `L1 31` / `T1 44`. Seam 0.
- **opus-5: live.** Gate 0 majors / `T1 13`. Seam 0.
- **risk-report-2026-08: converged, certification-ready.** Gate 0 majors /
  `FN1 1` (declared orphan-ref source defect — the PDF's own stray
  superscript 18 on p.126, D45) / `T1 22` (docling cell tokenization + seam
  displacement noise) / `TB2 1` (seam-cell advisor). Seam 0. Mutation recall
  at the calibrated band.

Both certified cards' output DID change this session — deliberately, and
every change is verified as an improvement (see the regression sweep below).
Byte-identity remains the net for *unintended* change; it is asserted per fix
within a batch, not across an approved canon change.

## What this session established

1. **D44 / D45 / D46** — non-system-card scope and slug convention; the
   onboarding generalizations (footnote-region walk, orphan-fnref rule,
   links inside docling cells, in-bubble lists); and the round-1 sweep's ~40
   distinct majors in 9 classes, all class-fixed.
2. **D47 — a styling rule reads per-instance oracle evidence, never a
   class-wide sample.** Forced by the one real regression this session (see
   below). Its process half matters more than its code half: a fix's own
   commit message is not evidence, and an inspector prompt must pose the
   question rather than assert the answer.
3. **A LATENT bug in both live cards, found at the ship gate:** PDF link
   destinations are stored bottom-up while span geometry is top-down, so
   every geometric comparison failed and a multi-heading destination page
   resolved to its FIRST heading. Fixed at the oracle; 12 links re-anchored.
4. **TB2** (owner-requested): table-cell order integrity from markdown alone
   — the scramble class the agent sweeps used to own, now mechanical.
5. **New gate on the sweep design itself:** three rounds each produced a
   finding the previous round's prompts had *told* inspectors was fine.
   Round 2's prompts described the fixes; round 3's message asserted a
   premise the regression sweep disproved. The rulebooks now describe the
   PDF only, and the do-not-flag list holds owner decisions only.

## Certified-card regression sweep (2026-08-15) — the ship evidence

5 agents; `docs/experiments/11-risk-report-sweep-round1/rulebook-regression.md`.

| scope | result |
| --- | --- |
| fable 8 changed pages | 12 major improvements, 2 minor regressions (one class) |
| opus 5 changed pages | 5 major improvements, 1 minor regression (same class) |
| fable 12 control pages | 11 clean, 1 improvement, 0 regressions |
| opus 11 control pages | 10 clean, 1 improvement, 0 regressions |
| all 163 internal links, both cards | **0 mismatches** |

The control samples cover the three RENDERER-level changes that touch every
page regardless of markdown (marker realign pass, footnote backlink anchor,
table CSS); both control agents verified in the live DOM. Card-wide: all 155
fable inline markers within 6px of their page's first line; 76/76 and 36/36
footnote backlinks resolving.

The link audit is the load-bearing result: all 94 number-named anchors now
resolve to the exactly-matching numbered heading (text and geometry agree
94/94; before the coordinate fix they disagreed), parent/child destinations
on one page stay distinct, and the single dead `](#)` on fable p.99 is the
already-declared source defect (the PDF names a destination absent from its
own name tree).

**The one real regression, fixed (D47):** round 3's footnote-superscript lift
was a whole-table regex asserting the PDF sets in-table markers at regular
weight. 9 of the corpus's 205 in-table refs are `Lora-Bold`; the rule
de-bolded four. `tables._lift_regular_sups` now matches each marker to its
own oracle fnref span. Source fidelity only — the site pins footnote refs to
a uniform mono citation style, so no rendered page changed; it reaches
readers through the `.md` exports.

## Open — owner attention needed

- **Deploy decision** (push to main → Pages). Nothing is blocking it
  technically: 0 majors on all three cards, seam 0, site builds clean.
- **Editorial:** the index-page intro copy is still system-card-specific
  ("when AI companies release a new model… the system card is usually a long
  PDF") — worth a line acknowledging risk reports now that one is archived.
- **Optional:** enable `link_text_resolution: extended` for fable/opus. It
  would re-anchor a handful of certified links — likely improvements, but
  canon changes wanting adjudication.
- **Owner-closed 2026-08-15:** p.22 rating-cell tints ("plain is fine");
  p.36's part-black/part-green code span ("fine to ignore"); table column
  width ratios ("don't want to force the ratios"); in-cell bulleted lists
  (approved and shipped, all three cards).

## Cold-start capsule

The first attempt converted one card but needed so much manual review the owner
judged it unmaintainable. The rebuild's goal: hand over a PDF, the pipeline runs
unattended, the owner certifies after a short flag-directed review.
Verification-first: the gates were built and calibrated before the generator.
Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D47),
[design-brief.md](design-brief.md) (§2 defect taxonomy), and
[verification-methodology.md](verification-methodology.md) (4 layers: gates →
agent sweeps → convergence loop → owner scroll). Three cards have now proven
the architecture: within Anthropic's Google-Docs-export family, one pipeline
serves with per-card config (manifest roles, stubs, and grammar knobs like
`link_text_resolution` and `bubble_page_continuation`); every fix is a class
in `pipeline/`, never an instance. A different vendor's PDF (different
producer) remains the next architectural test.

**If you are picking this up cold and the cards changed under you:** the
regression sweep in experiment 11 is the template — changed pages plus a
control sample for renderer-level changes, the PDF as sole authority, and
one question per page ("as good as, or better than, before?").
