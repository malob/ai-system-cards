# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-08-15 (D55 phase 3 implemented; fast release validated locally;
not yet pushed or deployed). The live site is still phase 2 commit `ff9b6e3`, whose hosted
fast release, Pages deployment, and three mutation jobs succeeded. Everything below
headed “phase 3” describes the current local worktree only.

## Current card gates

- **fable-5:** 20 exact accepted T1 majors (3 prior visual-order adjudications +
  17 newly surfaced table-order residuals), 0 unsuppressed majors; `L1 34` / `T1 28`
  minors; L2 108/108 exact authored destinations; P2/F3/RF1/V1 clean; 309 required
  content pages and 151 required rendered figures; seam 0.
- **opus-5:** 4 exact accepted table-order T1 majors, 0 unsuppressed majors; `T1 9`
  minors; L2 54/54 exact authored destinations; P2/F3/RF1/V1 clean; 187 required
  content pages and 98 required rendered figures; seam 0.
- **risk-report-2026-08:** 1 exact accepted table-order T1 major, 0 unsuppressed
  majors; `FN1 1` (declared publisher orphan-ref artifact) / `T1 21` / `TB2 1`
  minors; L2 121/121 logical destinations over 123 authored occurrences;
  P2/F3/RF1/V1 clean; 180 required content pages and 14 required rendered figures;
  seam 0.

The 25 accepted majors are exact full-finding fingerprints, not broad permissions.
All 22 new entries were checked against the PDFs and are reading-order/projection
residuals on table-attributed pages, not missing or invented canonical content.
Fable p.316's one-token `None` remains a critical-negation major before its exact
acceptance. The acceptance files now state their rationale. L2, P2, F3, RF1, and V1
cannot be waived through generic `accepted.json`; their stronger source/projection
authority either supplies an exact disposition or permits no exception.

## What phase 3 changed

Phase 3 repaired the general verification shape behind several apparent one-off
failures: generation and verification could inherit the same wrong exclusion or
semantic classification. The release graph now separates three questions:

1. **What does the archived PDF contain?** `source_inventory.py` independently
   observes every page and raw raster occurrence. Every occurrence is required unless
   a checked-in, PDF-hash/tool/schema/observation-bound `source-inventory.json`
   explicitly dispositions it. Generator TOC settings and `figures-map.json` are
   checked claims, never omission authority.
2. **Did canonical Markdown preserve the source facts?** The existing text, link,
   structure, table, footnote, and style gates now run alongside P2/F3 and RF1. Table
   attribution no longer demotes arbitrary T1 differences, and one- or two-token
   changes to numbers, dates, units/currencies, negations, and quantified comparators
   are major. Full digests bind long findings and displacement matching.
3. **Did the actual published projection preserve them?** A deterministic
   `source-projection.json` carries source-bound page/figure expectations into the
   production Markdown renderer and an HTML5-normalized DOM audit. The audit checks
   exact page/figure/accepted-skip order and identity, plus the copied source PDF and
   PNG bytes. Across all cards it sees 676 page markers, 263 rendered figures, and
   267 exact source raster assets, with 0 findings.

The F18 replay fixture proves why the split matters: reclassifying body spans and
moving the same prose into a dangling footnote definition can make the old body
streams agree on the same wrong omission. A section-local definition without a
reference is now an independent FN1 major. RF1 additionally reopens the PDF without
the generator/oracle zoning model and binds raw numeric superscript references and
small bottom-region numeric definitions to canonical occurrences and bodies. It
observes 76 references/76 definitions for Fable, 36/36 for Opus, and 93/92 for the
Risk Report. The latter is clean only because the publisher's stray p.126 superscript
18 has one exact source-hash-bound disposition. RF1 deliberately does not claim
symbol/letter footnotes or endnotes.

V1 closes another projection loophole before rendering: authored raw HTML may not
hide semantic content via browser-hidden elements/attributes, closed controls, or the
site's hidden classes. Active/reserved markup and inline style are rejected as well.
This is a static authored-HTML policy, not a computed-browser-layout oracle; hidden
content caused by CSS stylesheets, responsive breakpoints, clipping, occlusion, or a
particular viewport remains phase 9 work.

The final-DOM lane supports reason-bound figure-skip sentinels, but no current card
uses an allowed skip. Exact asset synchronization also prevents stale files from
surviving an incremental build. These are authority and release-safety changes, not
content edits.

## Mutation evidence

The mutation suite now runs the Python source/canonical gates and the production
JavaScript transform/render/DOM audit over the same exact mutated section bytes. It
keeps four distinct signals rather than calling every printed warning a successful
release test:

- **detected:** the intended invariant emitted a new exact finding;
- **intended-major:** that intended finding had blocking severity;
- **major-blocked:** after exact acceptances, at least one unsuppressed major remained;
- **gate-blocked:** the production command exited nonzero, including configuration
  failures, so this last signal is diagnostic rather than detector recall.

At eight trials/class and seed 5:

| card | eligible classes | trials | detected | intended-major | major-blocked | gate-blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 (95.5%) | 184 (92.0%) | 185 (92.5%) | 185 (92.5%) |
| Opus | 24 | 192 | 176 (91.7%) | 168 (87.5%) | 171 (89.1%) | 171 (89.1%) |
| Risk Report | 24 | 192 | 173 (90.1%) | 166 (86.5%) | 171 (89.1%) | 171 (89.1%) |
| **Total** | — | **584** | **540 (92.5%)** | **518 (88.7%)** | **527 (90.2%)** | **527 (90.2%)** |

`flatten-chip` is the only inapplicable class on Opus and the Risk Report. Every V1,
P2, F3, L2, body-critical, and footnote-critical class is 8/8 on every card where it
applies. The remaining misses are concentrated where the evidence says they are:
ST1/ST2/ST3, L1 occurrence coverage, S1 bold coverage, and ordinary two-word swaps
that T1 can detect while intentionally leaving advisory. Phase 4 therefore remains
ST2 hardening rather than another representation rewrite.

Mutation artifacts are strict schema-v2 envelopes bound to the card, seed,
trials/class, complete class/invariant set, aggregate counts, and per-trial evidence.
There is no legacy-baseline fallback. Output defaults to a temporary file and may not
resolve to the baseline path. The committed floors cover detection, intended-major,
and major-blocking independently.

## Validation and output effect

- The pinned local fast release command passed: shared card inventory, 147 Python
  verifier tests, all three gates, exact L2 and source-projection artifact comparisons,
  all three zero-seam audits, 31 site tests, and a clean production build.
- The built audit found 1,716 ids, 1,506 fragment links, 676 required page markers,
  263 rendered figures, and 267 copied raster assets, with 0 findings and all source
  PDF/PNG hashes matching.
- All three strict mutation baselines were regenerated from 584 trials and validated
  against the schema-v2 evidence contract. Exact final-tree replay of every trial is
  pending the hosted mutation jobs after push.
- `git diff -- cards/*/*/sections` is empty. No canonical card content changed.
- A clean 995-file `site/dist`, including Pagefind output, is byte-identical to
  pre-change HEAD.
  The published page content and search index therefore do not change in this phase.
- Full generation now hands off to the pinned, corpus-wide
  `pipeline/verify_release.py` command; partial generation remains an explicitly
  non-release diagnostic.
- Nothing in D55 has been pushed or deployed yet. Do not describe the live site as
  phase 3 until the hosted fast and mutation workflows and Pages deployment succeed.

## Durable process invariants

- The PDF is the sole content truth. PyMuPDF is a pinned, fallible observer; reproduce
  publisher errors rather than silently proofreading them.
- Capture is mechanical. Agents inspect and report; they do not transcribe or polish
  publisher text.
- Fix classes in `pipeline/`, never instances or generated sections. Regenerate,
  inspect the exact output diff, preview visible changes, run the corpus-wide gate,
  then re-sweep affected pages and controls.
- A shared-pipeline change covers the target plus every non-target certified card.
- Mechanical majors gate within their written scope; probabilistic/visual checks
  advise. The owner scroll remains mandatory for layout classes outside those scopes.
- Generic acceptance cannot weaken a source-bound or final-projection authority.
- Commit early and append decisions. Never push without an explicit owner request.

## Open / next

- **Phase 4:** harden ST2 using the 16 sweep findings, known mutation misses, and
  nearest-negative controls.
- **Later authority work:** pin/cold-replay extraction (phase 5), serialize the
  observation/annotation boundary (phase 6), independently test table topology and a
  persistent grid (phases 7–8), then exercise clean bootstrap, every projection,
  computed browser visibility, and a different PDF producer (phase 9).
- **Nonblocking R2 presentation question:** whether the web edition visibly annotates
  a source-unresolvable internal destination remains open; recovery/plain-text
  behavior is already settled.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The rebuild's
goal is unattended mechanical conversion followed by bounded, evidence-directed
review. Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D55),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). The immediate task is
phase 4, not a whole-document IR migration. For a changed corpus, experiment 11 is the
regression-sweep template: changed pages plus renderer controls, the PDF as sole
authority, and prompts that ask rather than assert the expected answer.
