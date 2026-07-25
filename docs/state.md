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

## The D41/D42 fix batch (2026-07-25 afternoon)

Owner review walkthrough adjudicated ALL eight deferred minors as fixes (D41,
D42) — every one landed same-day, each with the per-fix D25 loop (regen both
cards → page-diff review → gates):

1. **Glyph repair** (`_restore_cell_glyphs`): column-aligned oracle-glyph
   restoration for cells the row-band can't segment (tall passage rows).
   Opus pp.140–141 + fable pp.243–245/appendix; all changed files verified
   fold-identical. Sweep caught one miss (fable p.243 row 3 — a lone ZWSP
   span broke column contiguity); invisibles are now transparent to the
   alignment.
2. **Cell italics** from oracle flags (`(Helpful-only)`, `No tools`, `256K` —
   both cards).
3. **Row-band ordinal fallback** for rows whose every anchor recurs (p.75
   missed bold).
4. **Stacked-cell `<br>`**: sentence-terminal reflow test with 12pt slack —
   first cut fired on 76 sites; shipped version fires on exactly the opus
   p.31 + fable p.48 threshold cells (both crop-verified stacks).
5. **Quote band context**: x0 106–112 classifies as quote only when no page
   list claims the tier (BBQ examples pp.64–65 → blockquotes).
6. **Code-box chrome** → fence info string (```None), mdproj projects info
   strings (3 opus + 1 fable boxes; phantom blocklist pattern gone).
7. **Fence blank lines** re-emitted at full line-height gaps (opus p.85 +
   fable p.317, both crop-verified).
8. **hl coalescing** across line wraps, ph-style stacking guard (p.138).

Batch verification: seams 0 (both cards); mutation recall at baseline; spot
re-sweep of every touched page (14 opus + 11 fable, 3 inspectors) — all
clean after the ZWSP follow-up; all fixes verified in the served DOM.
New typed baselines: **opus T1 13**, **fable L1 31 / T1 44**.

## Open

- **Push:** owner reviews the batch summary, then pushes (`main` → Pages
  deploys BOTH the opus-5 card and fable-5's collateral fidelity fixes).
- **Typed minors, sweep-noted (non-blocking):** docling-lost space in a
  restored cell (fable p.243 `” —robust`, spacing only — the repair
  deliberately keeps docling spacing; owner-accepted as typed, 2026-07-25). The
  renderer typographer question is DECIDED (owner, 2026-07-25): keep the
  educator as-is — the affected interview-table text isn't verbatim-formatted
  in the source either; md/card.md/llms.txt remain the fidelity artifacts.
- **In-table page-marker overlap (owner-spotted, FIXED):** markers between
  table rows were foster-parented out of the table and stacked at its top
  (nine-marker smear beside fable's appendix interview table, live since
  June). cards.js now anchors an in-table marker inside the following row's
  first cell (contained by `.doc`, so the table's scroll wrapper can't clip
  it) — all 15 in-table markers across both cards verified at their rows,
  zero overlaps.
- **Owner scroll-review round (2026-07-25 afternoon, post-batch):** the owner's
  manual scroll found FIVE more issues — all fixed same-day, each with the
  D25 loop: (1) in-table page-marker overlap (foster-parenting smear — renderer
  fix, cards.js); (2) intra-cell size tiers flattened (header parentheticals,
  '(Helpful-only)' — <br> at size drops + <small>, 38 sites both cards);
  (3) blank lines lost in band-less cells (constitution frequency column —
  _cell_blank_lines column-alignment pass, 11 sites); (4) hl highlight split
  at the page seam (joined; marker lives inside the span); (5) same-bubble
  turn split at nested code boxes (p.93 [Assistant] bubble — turn_cont merge;
  labeled resumes like fable's 'Assistant, turn N:' unchanged). Lesson for the
  methodology: the sweep stack verifies per-page content faithfully but is
  weak on VISUAL-LAYOUT classes (cross-element, tier typography, bubble
  scoping) — a human scroll pass belongs in the onboarding procedure before
  certification (now CLAUDE.md onboarding step 8). Sixth find: spanning
  sub-headers ('API, without a system prompt' colspan=2) showed no span
  extent — renderer CSS now centers spanning header cells over an inset
  rule (booktabs cmidrule style; header rows only, body colspan labels
  untouched; 19 opus + 24 fable cells).
- **Final pre-push sweep (owner-requested belt-and-braces):** 2 inspectors,
  18 pages covering every scroll-round fix site on both cards
  (`findings-final-sweep.jsonl`): zero regressions, all fixes verified
  faithful against crops. Two residual MINORS for owner triage, neither
  batch-caused: opus p.140 col-1 bold §-headings join their quote with a
  space where the PDF line-breaks (candidate bold-boundary <br> class);
  fable p.252 PDF bolds two placeholder dashes, output renders plain
  (pre-existing).
- **md exports (owner-requested):** card.md gains a provenance header
  (title/vendor/date/links + converted-note) and a linked Contents; every
  top-level section is now a STANDALONE .md route (10 opus + 11 fable,
  `/[card]/<n>-<slug>.md`) so agents can fetch one section; llms.txt nests
  the per-section index with page ranges. Grouping is mechanical (h2-opening
  file starts a group) — future cards get it free.
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

- **fable-5: live** at malob.github.io/ai-system-cards (June 11 revision, D37),
  with UNPUSHED D41/D42 fidelity fixes in the worktree (glyphs, italics, br
  stack, chrome, blank line). Gate: 0 majors / L1 31 / T1 44.
- **opus-5: converted, converged, committed, unpushed.** Gate: 0 majors / T1 13
  typed minors; seams 0; sweep rounds 1+2 + D42 batch spot re-sweep all clean;
  visual pass done; site builds clean. Awaiting owner push.
- Verifier calibration corpus (D5) untouched: refs `f60899a`/`fb483fb`.
