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
- **risk-report-2026-08: converged; owner scroll pass IN PROGRESS.** Gate:
  0 majors / `FN1 1` (declared orphan-ref source defect — the PDF's own
  stray superscript 18 on p.126, D45) / `T1 22` (docling cell tokenization
  + seam displacement noise) / `TB2 1` (seam-cell advisor). Seam audit 0.
  NEW GATE TB2 (owner-requested): table-cell order integrity from markdown
  alone — the scramble class the sweeps used to own; contract updated. Mutation recall at the
  calibrated band. Scroll findings so far (experiment 11 §findings log,
  both class-fixed same session): p.42 taxonomy sub-list (spurious
  blockquote + bold-letter-defeated `<ol type="a">` transform, `8d96f1a`);
  cross-page bubble splits §2.24/§2.20 (geometry continuation rule,
  `076161f`); Table 3.10.A cell paragraphs + in-cell italics
  (`c3d046c`/`2eee70e`); seam page marker foster-parented to the table top
  (`e0d4d34`); dead ↩ backlinks on table-only footnotes (`a05e334`); and the
  owner-re-adjudicated deferred batch — wrap-join corruption, in-cell
  punctuation spaces, quote folds, indented RSP quotations (`e8f8f61`).
- **RESOLVED (owner asked for a judgment, 2026-08-14 ~22:10):** the
  bubble-continuation rule initially also merged fable-5's §6.2.4
  pilot-quote box — judged NOT a fidelity fix there (fable's convention is
  box-per-paragraph: its p.102 continuation paragraph sits in its own
  closed box mid-page; the risk report's p.72 twin of the same quote holds
  both paragraphs in one box). Rule gated behind
  `bubble_page_continuation: true` (risk report on, fable/opus off);
  fable canon restored byte-for-byte (`fdda931`).

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

- **Ship decision.** Sweep round 3 (the ship gate, 2026-08-15) found 4
  major classes, all fixed — including a LATENT link-destination bug that
  affected both live cards. Convergence state in experiment 11 §Round 3.
- **One editorial call outstanding:** in-cell bulleted lists render as
  literal ● + `<br><br>` rather than `<ul>/<li>` (p.113, p.155), so a
  bullet's follow-on paragraphs lose their association. Long-standing
  convention on all three cards; changing it is a D17 presentation call.
- **Deploy decision** (push to main → Pages).
- **Deferred typed minors** — now just ONE: p.36's code span (the PDF sets
  'sed' black and the rest green; the renderer styles code uniformly). All
  others were re-adjudicated as real and fixed 2026-08-15.
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
