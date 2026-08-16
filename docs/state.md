# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-08-15 (D51 phase 2 deployed). The phase-2 implementation
commit `ff9b6e3` is live. Its hosted fast release gate, Pages deployment, and all three
slower mutation-sensitivity jobs succeeded; the follow-up below only reconciles the
repository snapshot with that result.

## Status

- **fable-5: live; L2 gate clean.** 3 exact owner-accepted T1 majors; 0
  unsuppressed majors; `L1 34` / `T1 44` minors; L2 108/108 exact authored
  destinations, including 1 printed-heading recovery; 1 additional source link is
  unresolvable and correctly remains plain; seam 0.
- **opus-5: live; L2 gate clean.** 0 majors; `T1 13` minors; L2 54/54 exact
  authored destinations; seam 0.
- **risk-report-2026-08: live; L2 gate clean.** 0 majors; `FN1 1` (declared
  orphan-ref source defect, D45) / `T1 22` / `TB2 1` minors; L2 121/121 exact logical
  destinations over 123 authored occurrences; seam 0.

GitHub Pages run
[31919737114](https://github.com/malob/ai-system-cards/actions/runs/31919737114)
completed successfully for `ff9b6e3`: hosted card discovery, all three parallel full
gates, fresh L2 artifact comparisons, seam audits, 38 verifier tests, 11 site tests,
the full-page link audit/build, and deployment all passed. Mutation run
[31919737009](https://github.com/malob/ai-system-cards/actions/runs/31919737009)
then passed the committed floor independently for Fable, Opus, and the Risk Report.
Live smoke checks returned HTTP 200 for the home page, all three cards, `llms.txt`, and
Fable's `card.md`; the repaired p.99 text is present and `href="#"` is absent.

## Maintainer hardening landed and deployed (D49/D50)

1. **Verifier is an enforceable gate.** `calibrate.py` exits 1 for unsuppressed
   majors and 2 for invalid acceptance configuration. `--report-only` is explicit.
   Fable's old `(invariant,page)` allowances were migrated to fingerprints of the
   complete finding; two stale entries were removed and the two distinct p.37
   findings are separate.
2. **Gate behavior is tested.** The current 38-test verifier suite covers exact
   matching, stale/duplicate/invalid acceptance rejection, exit semantics,
   mutation-floor comparisons, the generator's same-card/full-vs-partial verifier
   handoff, and L2 source/destination behavior. An isolated duplicate page-marker
   probe produced `P1 major 1` and exit 1; `--report-only` changed only that exit to 0.
3. **CI covers the real release path.** The reusable fast workflow runs unit tests,
   all three full gates + seam audits, and a clean site build. The Pages workflow
   depends on it; a verifier failure skips build and deployment. Pages/OIDC write
   permissions are confined to the final deploy job. `actionlint` 1.7.12 and YAML
   parsing report no workflow errors.
4. **Mutation recall has committed floors.** At 8 trials/class, seed 5: Fable
   95/104 (91.3%), Opus 80/96 (83.3%), Risk Report 77/96 (80.2%). `repoint-link` is
   8/8 on every card. The slower workflow runs on relevant changes, weekly, and
   manually; class/invariant/sample drift or a caught-count regression fails it.
5. **Repository truth is reconciled.** README/CLAUDE now describe all three
   documents and the within-family limit. D50 and the charter supersede the unbuilt
   pre-build JSON/LLM mechanisms in D1/D2/D7/D9/D10/D14 with the shipped mechanical
   compiler and inspection loop.

The D49/D50 maintenance changed no generated `sections/*.md`. Phase 2 intentionally
changes exactly one Fable p.99 canonical line: the publisher-broken internal link,
previously serialized with an empty `(#)` target, becomes plain text under R2. Opus
and Risk Report sections remain byte-identical.

## Architecture review settled; phases 0–2 deployed (D51–D54)

An adversarial two-model review found that the current representation is not the
first thing to replace. The three-card generator is deterministic and genuinely
shared; the leading measured weakness is correlated authority between generation and
verification. At review time, the demonstrated published defect was portable
Markdown's mishandling of table-only footnotes, and no source-content defect was
demonstrated in canonical sections or the main HTML. Phase 2 later exposed the
canonical dead-link projection defect recorded above. Nineteen table-zone T1
residuals of at least three tokens remain source-unadjudicated.

The owner authorized the implementation phase on 2026-08-15. Phases 0 and 1 are
deployed:

- **Every publishable card is gated.** Production and CI consume one dependency-free
  card inventory; a synthetic fourth card automatically enters the parallel full-gate
  matrix, while no-meta/nonexistent directories do not. The inventory cannot be empty.
- **Portable table footnotes work under the supported GFM projection.** Full-card and
  section exports turn raw-table refs into live anchors, retain definitions, preserve
  later numbering, and give repeated refs distinct backlinks. The main HTML path is
  byte-identical and canonical sections did not change.

Phase 2 is also deployed:

- **L2 checks destination identity, not merely link existence.** It independently
  derives source links and accepted headings from the PDF, pairs canonical occurrences
  without their destinations, and emits exact target expectations. All three cards
  have zero L2 majors, and 27/27 known historical wrong targets replay as blocking L2
  findings.
- **Expectations are byte-bound and projection-checked.** Each tracked artifact binds
  the exact source PDF and canonical section set by SHA-256. CI regenerates it; the
  site independently recomputes those hashes, parses serialized HTML using HTML5
  tree-building, and requires all 285 authored fragment links and source expectations
  to survive without insertion, deletion, reordering, or repointing.
- **R2 is explicit.** A publisher-broken named destination remains an L1 source-defect
  minor. A uniquely printed heading identity may be recovered and L2-verified;
  otherwise the anchor is plain text, never an empty `#` link.

Next is phase 3's remaining authority loops. Broader representation work stays
evidence-gated: keep Markdown canonical for prose, keep PyMuPDF as the primary
versioned observer, treat Docling as a pinned table candidate, and introduce no
whole-document IR unless narrower bootstrap/projection/provenance experiments fail.
Full phases, experiments, and kill criteria are in
[architecture-roadmap.md](architecture-roadmap.md).

## Validation evidence for this series

- Fresh no-cache baseline: all three full gates at the counts above; all seam audits
  0. Python 3.12 / uv 0.12.1 / PyMuPDF 1.28.2.
- Mutation artifacts regenerated from current sections with a deterministic RNG per
  class: Fable 95/104 (91.3%, 13 classes), Opus 80/96 (83.3%, 12 classes), and Risk
  Report 77/96 (80.2%, 12 classes). `repoint-link` is 8/8 on each card. This one-time
  rebaseline prevents future class insertion from resampling unrelated classes.
- Clean site install/build: local Node 24.18.1 / pnpm 11.20.0 (CI pins Node 22 /
  pnpm 11), 599 Pagefind records and all routes generated.
- Workflows: all parse, `actionlint` clean, dependency chain independently reviewed;
  deployment cannot reach the Pages job after a failed reusable verifier job.
- D51 phases 0–1: shared inventory tests 2/2; portable export tests 3/3; synthetic
  repeated backlinks and actual full-card/section fixtures pass; all built exports
  have 0 unresolved raw-table footnote refs; site production build remains 599
  Pagefind records. Run 31917054001 proved the dynamic matrix and deploy dependency on
  hosted runners.
- D51 phase 2: source-first L2 is clean at 108 Fable, 54 Opus, and 121 Risk Report
  logical destinations (123 authored Risk Report occurrences); historical wrong-target
  replay is 27/27; source expectations cover 285/285 authored occurrences. The Python
  suite is 38/38 and site tests are 11/11. The built-page audit sees 1,716 ids and
  1,506 fragment links with zero findings. The L2 artifacts fail closed on source or
  canonical hash drift. Runs 31919737114 and 31919737009 prove the fast release path
  and all three slower mutation floors on hosted runners for `ff9b6e3`.

## Durable process invariants

- The PDF is the sole content truth. Reproduce publisher errors; do not silently
  correct them.
- Capture is mechanical. Agents inspect and report; they do not transcribe or polish
  publisher text.
- Fix classes in `pipeline/`, never instances or generated sections. Regenerate,
  inspect the exact output diff, preview visible changes, run gate + seam, then
  re-sweep affected pages and controls.
- A shared-pipeline change covers the target plus every non-target certified
  document. Byte identity catches unintended movement; approved PDF-evidenced canon
  improvements may move a baseline only with a regression sweep.
- Mechanical majors gate within each invariant's documented scope;
  probabilistic/vision checks advise. The owner scroll remains mandatory because it
  catches layout classes disjoint from page sweeps.
- Commit early and append decisions. Never push without an explicit owner request.

## Open — owner attention needed

- **Architecture hardening program:** continue the ordered work in
  [architecture-roadmap.md](architecture-roadmap.md) at phase 3. A different
  vendor/PDF producer is still the decisive later test of cross-family rule scope, not
  the immediate next task.
- **Nonblocking R2 presentation question:** recovery-vs-plain-text behavior is settled;
  only whether the web edition should visibly annotate a source-unresolvable internal
  destination remains open in `spec-rules.md`.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The rebuild's
goal is unattended mechanical conversion followed by bounded, evidence-directed
review. Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D54),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). For a changed corpus,
experiment 11 is the regression-sweep template: changed pages plus renderer controls,
the PDF as sole authority, and prompts that ask rather than assert the expected
answer.
