# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-07-25 — **the second card is converted.** Anthropic released
the **Claude Opus 5 system card** (2026-07-24, 193pp) and it went through the pipeline
in one session, answering D35's question for the within-Anthropic case: **one shared
pipeline serves, with per-card config** (D38–D40). Everything is committed on `main`,
**not pushed** (D13 — owner pushes).

## What happened (2026-07-25, one session)

- **Pipeline generalized (D38):** `pipeline/cardcfg.py` + `CARD` env var select the
  card; per-document constants come from the card's own `meta.yaml` /
  `style-manifest.yaml`; caches per-card; `accepted.json` lives in the card dir.
- **Style roles manifest-driven (D39):** assemble.py reads hex→role from the card's
  manifest; the role vocabulary is fixed in code. Mattered immediately — opus-5 reuses
  fable-5 hexes for different roles (#e2decf turn-user → table tint, #141413 chart
  panel → table header fill, #4d4c48 figure legend → table sub-header).
- **Onboarding procedure** (now in CLAUDE.md §"Adding a card"): census → manifest →
  ground-truth extraction (oracle/renders/figures/docling on rule-line candidate
  pages) → section stubs from the PDF's own bookmarks → assemble → gate. First
  assemble of all 187 content pages produced **12 majors**; the gate converged to
  **0 majors** the same day. Typed residual baseline: **T1 ~36 minors** (docling
  quote/dash ASCII-ization in tables ~27 — same class as fable's accepted p.243
  family; literal markdown-in-transcript projection nits; T2 spill displacements).
  Fable-5's baseline is now **L1 31 / T1 66** (4 old minors were projection
  artifacts of label-less turns, now fixed verifier-side).
- **Generalization fixes with fable-5 held byte-identical throughout** (the
  regression bar for every change): turn-label grammar (bold paragraphs inside turns
  are not labels), bubble-identity turn splits, container-scoped code-box label
  inheritance, partial-span links (URI-only, anchor-snapped), empty-bold-pair and
  mark-coalescing fixes, ZWSP-tolerant label detection, HEAD_NUM trailing-dot
  tolerance, ■/□/Word-'o' bullet glyphs, glyph-tier quote detection, docling
  scrambled-row band-discovery repair, fragment colspan normalization, cross-page
  label-cell row merge, thin-strip inline highlights (`.hl`).
- **Verifier changed → mutation-tested:** recall profile within noise of the
  committed baseline (drop-bold 7/10 vs 8/10, split-item 4/10 vs 5/10, ST3 10/10 vs
  8/10 — the corpus itself changed since; the known S1 gap is common-word runs
  covered by heading text, documented in invariants.py).
- **Inspection sweeps ran (experiment 10):** 8 comparators (all 187 pages) + 3
  linters (all 12 sections), rulebook adapted from round G. **15 confirmed majors in
  8 classes** — all fixed at class level (see
  `docs/experiments/10-opus5-sweep-round1/README.md` for the full fix map); seam
  auditor 0; site builds clean. **Round 2 re-sweep done** (28 units,
  `findings-round2.jsonl`): all 13 fixes verified in place, no regressions;
  15-page rotating sample surfaced **1 new major (p.143)** — turn serializer's
  short-line fallback split a tight hard return into two paragraphs; fixed at
  class level (fallback only when no gap breaks exist), fable-5 byte-identical,
  both gates at baseline, DOM verified. Converged.
- **Site:** auto-discovered the card (homepage lists it first, date-sorted; 187 PDF
  deep links to the archived in-repo PDF; OG image; card.md; llms.txt; Pagefind 433
  section records). Renderer: label-less turn bubbles emit no empty label element;
  `.hl` inline-highlight style; lettered-list transform hardened (page marker now
  emitted after the letter). **Visual pass done** (2026-07-25, desktop-app built-in
  browser on the production preview): homepage order, masthead/TOC/scrollspy, 187
  page markers → archived PDF (asset 200), sidenotes 36 visible / 0 overlaps at
  1680px, turn bubbles (labeled + label-less), `.hl` spans inline (no double
  spaces), p.69 tables match crops cell-for-cell in light AND dark theme, Pagefind
  search returns cross-card results, OG PNG built. The one odd-looking link
  (`…Sonnet 5 System Card.pdf#page=56.64`, p.72) is verbatim in the PDF —
  source-faithful. NOTE: the old "preview screenshots blank on tall pages"
  limitation is gone in the desktop-app browser pane; real Chrome no longer
  needed for this.

## Open

- **Owner review + push:** the opus-5 card is converged and committed; deploy is on
  owner request (push `main` → Pages). Owner should adjudicate the typed residuals
  (T1 ~36) — same acceptance shape as fable's.
- **Typed/deferred minors** (listed in experiment 10's README): docling table char
  normalization (candidate shared repair, would also fix fable's p.243 family —
  changes D28-canonical output, needs owner sign-off); italic-in-table-cell
  unsupported; one missed bold cell (p.75); p.31 stacked cell lines; p.64 indented
  quotations render flush; appendix `None` code-box chrome; p.85 mono blank line;
  adjacent `.hl` spans split at wraps.
- **Next milestone:** a third document from a *different vendor* (different PDF
  producer) — the real test of the oracle/manifest architecture beyond Google-Docs
  exports.

## Cold-start capsule

The first attempt converted one card (Claude Fable 5 & Mythos 5) but required so much
manual review that the owner judged it unmaintainable. The rebuild's goal: hand over a
PDF, the pipeline runs unattended, the owner certifies after a short flag-directed
review. Verification-first: the gates were built and calibrated before the generator.
Read [charter.md](charter.md), [decisions.md](decisions.md) (D1…D40),
[design-brief.md](design-brief.md) (§2 defect taxonomy),
[verification-methodology.md](verification-methodology.md). The second card validated
the architecture: census → manifest → stubs → assemble → gate → sweeps, with the
other card as a byte-identity regression net.

## Status

- **fable-5: live** at malob.github.io/ai-system-cards (June 11 revision, D37).
  Gate: 0 majors / L1 31 / T1 66.
- **opus-5: converted, converged, committed, unpushed.** Gate: 0 majors / T1 36
  typed minors; seams 0; sweep rounds 1+2 done (round 2: 1 major found+fixed);
  visual pass done; site builds clean. Ready for owner review + push.
- Verifier calibration corpus (D5) untouched: refs `f60899a`/`fb483fb`.
