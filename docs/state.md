# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-08-15 (maintainer hardening plus D51 phases 0–1, local and not
pushed). The three document editions are live; the published corpus commit is
`6fed282`. The current local series makes verification and deployment fail closed,
commits three-card mutation floors, reconciles the operational docs, records the
settled architecture review, dynamically gates every site-discoverable card, and
repairs portable table-footnote semantics. Per D13, none of this maintenance series
has been pushed.

## Status

- **fable-5: live.** 3 exact owner-accepted T1 majors; 0 unsuppressed majors;
  `L1 31` / `T1 44` minors; seam 0.
- **opus-5: live.** 0 majors; `T1 13` minors; seam 0.
- **risk-report-2026-08: live.** 0 majors; `FN1 1` (declared orphan-ref source
  defect, D45) / `T1 22` / `TB2 1` minors; seam 0.

The Risk Report push and deployment happened after the previous snapshot said they
were awaiting an owner decision. Local git recorded `origin/main` at `6fed282`, and
GitHub Pages run [31905426276](https://github.com/malob/ai-system-cards/actions/runs/31905426276)
completed successfully for that exact commit. The home page, report page, `llms.txt`,
exported `card.md`, and source PDF all returned HTTP 200. The maintenance commits
described below are newer local work and are not deployed.

## Maintainer hardening completed locally (D49/D50)

1. **Verifier is an enforceable gate.** `calibrate.py` exits 1 for unsuppressed
   majors and 2 for invalid acceptance configuration. `--report-only` is explicit.
   Fable's old `(invariant,page)` allowances were migrated to fingerprints of the
   complete finding; two stale entries were removed and the two distinct p.37
   findings are separate.
2. **Gate behavior is tested.** 15 verifier unit tests cover exact matching, stale/
   duplicate/invalid acceptance rejection, exit semantics, mutation-floor
   comparisons, and the generator's same-card/full-vs-partial verifier handoff. An
   isolated duplicate page-marker probe produced `P1 major 1` and exit 1;
   `--report-only` changed only that exit to 0.
3. **CI covers the real release path.** The reusable fast workflow runs unit tests,
   all three full gates + seam audits, and a clean site build. The Pages workflow
   depends on it; a verifier failure skips build and deployment. Pages/OIDC write
   permissions are confined to the final deploy job. `actionlint` 1.7.12 and YAML
   parsing report no workflow errors.
4. **Mutation recall has committed floors.** At 8 trials/class, seed 5: Fable
   86/96 (89.6%), Opus 72/88 (81.8%), Risk Report 74/88 (84.1%). The slower workflow
   runs on relevant changes, weekly, and manually; class/invariant/sample drift or a
   caught-count regression fails it.
5. **Repository truth is reconciled.** README/CLAUDE now describe all three
   documents and the within-family limit. D50 and the charter supersede the unbuilt
   pre-build JSON/LLM mechanisms in D1/D2/D7/D9/D10/D14 with the shipped mechanical
   compiler and inspection loop.

No generated `sections/*.md` changed during this maintenance work.

## Architecture review settled; phases 0–1 complete locally (D51/D52)

An adversarial two-model review found that the current representation is not the
first thing to replace. The three-card generator is deterministic and genuinely
shared; the leading measured weakness is correlated authority between generation and
verification. One present published defect was demonstrated: portable Markdown does
not preserve table-only footnote semantics correctly. No source-content defect was
demonstrated in canonical sections or the main HTML. Nineteen table-zone T1 residuals
of at least three tokens remain source-unadjudicated.

The owner authorized the implementation phase on 2026-08-15. Phases 0 and 1 are now
complete locally:

- **Every publishable card is gated.** Production and CI consume one dependency-free
  card inventory; a synthetic fourth card automatically enters the parallel full-gate
  matrix, while no-meta/nonexistent directories do not. The inventory cannot be empty.
- **Portable table footnotes work under the supported GFM projection.** Full-card and
  section exports turn raw-table refs into live anchors, retain definitions, preserve
  later numbering, and give repeated refs distinct backlinks. The main HTML path is
  byte-identical and canonical sections did not change.

Next is phase 2, L2 destination verification, followed by the remaining authority
loops. Broader representation work stays evidence-gated: keep Markdown canonical for
prose, keep PyMuPDF as the primary versioned observer, treat Docling as a pinned table
candidate, and introduce no whole-document IR unless narrower bootstrap/projection/
provenance experiments fail. Full phases, experiments, and kill criteria are in
[architecture-roadmap.md](architecture-roadmap.md).

## Validation evidence for this series

- Fresh no-cache baseline: all three full gates at the counts above; all seam audits
  0. Python 3.12 / uv 0.12.1 / PyMuPDF 1.28.2.
- Mutation artifacts regenerated from current sections: Fable 86/96, Opus 72/88,
  Risk Report 74/88. Risk Report was byte-identical to its prior committed artifact;
  Fable and Opus now have normalized per-document artifacts.
- Clean site install/build: local Node 24.18.1 / pnpm 11.20.0 (CI pins Node 22 /
  pnpm 11), 599 Pagefind records and all routes generated.
- Workflows: all parse, `actionlint` clean, dependency chain independently reviewed;
  deployment cannot reach the Pages job after a failed reusable verifier job.
- D51 phases 0–1: shared inventory tests 2/2; portable export tests 3/3; synthetic
  repeated backlinks and actual full-card/section fixtures pass; all built exports
  have 0 unresolved raw-table footnote refs; site production build remains 599
  Pagefind records. The workflow's dynamic matrix and new test step pass local YAML +
  `actionlint` validation. All 15 verifier tests, three full gates, and three seam
  audits remain at the certified baselines above.

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

- **Review/push decision for the local maintenance series.** No technical blocker is
  known, but the new CI can only be proven on GitHub-hosted runners after a push. Do
  not push without the owner's explicit instruction.
- **Architecture hardening program:** continue the ordered work in
  [architecture-roadmap.md](architecture-roadmap.md) at phase 2 (L2 destination
  verification). A different vendor/PDF producer is still the decisive later test of
  cross-family rule scope, not the immediate next task.
- **Nonblocking policy question:** whether the web edition should annotate an
  internal destination that is already unresolvable in the source PDF remains open
  in `spec-rules.md`.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The rebuild's
goal is unattended mechanical conversion followed by bounded, evidence-directed
review. Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D51),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). For a changed corpus,
experiment 11 is the regression-sweep template: changed pages plus renderer controls,
the PDF as sole authority, and prompts that ask rather than assert the expected
answer.
