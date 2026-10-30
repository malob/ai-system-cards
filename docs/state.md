# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-10-29 (D73 quotes). **Five cards LIVE; a sixth converged locally, NOT
pushed.** The owner handed over Google DeepMind's **Gemini 4 Argon Safety &
Security Report** (`google-deepmind/gemini-4-argon`, 217pp, released
2026-10-13; the fetched storage object is a 2026-10-15 re-upload — see
`meta.yaml`). It is the archive's first non-Anthropic document: a different
vendor and visual grammar, but the SAME producer (Skia/PDF Google Docs Renderer
m157). Onboarded, gated, swept (two rounds) and rendered-pass checked in one
session (D70, D71, experiment 20). Certified cards stayed byte-identical
throughout. Awaiting the owner: the full scroll D69 requires for a new visual
grammar, the judgment calls below, and the deploy decision.

## Gemini 4 Argon onboarding (D70, D71, experiment 20)

- **Template census:** Google Sans; RobotoMono green inline code; the Google Docs
  DEFAULT heading styles with many unnumbered heads; #e8f0fe header bands with
  blue header text; gray 10pt footnotes; bold `Figure N:` / `Table N:` captions
  below their constructs; page numbers 50pt up the bottom margin; a meaningful
  #fdb895 orange highlight (Figure 3.43); three JPEG figures; fully ruled tables.
- **Card config:** `headings:` style tiers + `heading_source: outline` (181/181
  headings equal the PDF outline), `link_text_resolution: geometry` (three
  publisher links jump to a different section than they name — reproduced),
  `cell_fit_breaks`, `header_rows_by_fill`, `cell_run_restyle`, a `highlight`
  fill with class `hl-orange`. Stubs: 12 files (§3 split at page-top 3.2.3, 3.4,
  3.4.4, 3.4.5, 3.5). TOC pp.2–5. Docling 2.124.0 on 26 rule-scanned pages.
- **Shared classes** (all certified cards byte-identical from fresh oracles):
  footer page number above the 45pt band; adjacent footnote refs ('⁷⁸'); a
  footnote tail alone under the separator continues the previous note; bold
  caption labels (colon or period); github-slugger order; PyMuPDF-decoded JPEGs;
  hyphen and roman-numeral list markers; ruled-table rehome / rowspan / reproject
  / pad repairs (oracle additive `hrules`/`vrules`); entity-safe seam merges and
  rowspan-aligned continuations; italic `<i>` flanking fallback; relocated
  footnote links paired by reference page (L2); projection keeps literal '<' and
  '|' (fable-5 T1 24→21, opus-5 T1 7→4); regular-weight row-label `th` → `td`.
- **Sweeps:** round 1 (7 comparators + 2 linters, 224 units, 185 clean) → 33
  majors collapsing to ~9 classes, all fixed (experiment 20 README). Round 2:
  24 fix pages (21 clean; the one major, a stray blank line on p.92, fixed) +
  17 seeded clean pages (17 clean).
- **Rendered visual pass:** DOM audit at 1338/1680/375px clean (212 labels, 28
  sidenotes at 1680, 0 overlaps, no horizontal scroll, 85 lazy figures decode);
  14 table screenshots: 12 clean, the p.92 blank line (already fixed) and a
  highlight sliver (fixed: breaks land outside highlight spans)
  (`docs/experiments/20-gemini-4-argon-sweep-round1/visual-findings.jsonl`).
- **Release:** fast release gate PASSED with six cards (all gates, artifacts,
  seams, 170 verifier + 45 site tests, clean build, 0 audit findings).

## Owner scroll feedback and D72 (2026-10-15 afternoon)

The owner scrolled the card: naming approved; Figure 3.43's line breaks are all
real; the bordered CCL definition boxes are a semantic loss as paragraphs;
Figure 3.38 must be reproduced at fidelity. D72 makes the PDF's TAGGED
structure (Google Docs exports Table/TR/TD/P tags) the table authority on this
card (`tagged_tables` knob, oracle additive `tags`): the four boxes are now
bordered one-column tables, Figure 3.38 is one table with its spanning prompt
row and one line per answer option, Figure 3.43 matches the PDF line for line
with 'STEPS 1–6' rejoined across the page, and every in-cell break follows the
PDF's paragraphs and soft returns (a line ending in U+200B). Some continuation
lines are untagged (pp.89, 93) — the legacy path covers them. Certified cards
byte-identical; their PDFs are tagged too (a later candidate).

## Open owner decisions

None. Resolved 2026-10-29 (D73): quotes print exactly as each PDF prints them — the
renderer's smart-quote pass is gone; the risk report's p.113 low quote '‚' is
restored (its only canon change; the other cards were already glyph-exact).
Resolved 2026-10-29 (D74): gutter labels stay PDF indices (Gemini's printed
footer is index − 1; one convention, and the label names the linked page).

## Current card gates

| card | accepted majors | typed minors | L2 | P2/F3 | RF1 |
| --- | --- | --- | --- | --- | --- |
| fable-5 | 20 T1 | L1 34 / T1 21 | 109/109 | 309/151 | 76/76 |
| opus-5 | 4 T1 | T1 4 | 54/54 | 192/100 | 36/36 |
| risk-report-2026-08 | 1 T1 | FN1 1 / T1 5 / TB2 1 | 121/121 | 180/14 | 93/92 (p.126 disposition) |
| claude-fable-5-1 | 5 T1 | T1 3 | 66/66 | 206/103 | 30/30 |
| claude-opus-5-5 | 2 T1 (p.226) | T1 3 | 84/84 | 223/109 | 32/32 |
| gemini-4-argon | 3 T1 (pp.184–185) | T1 7 / TB2 4 | 23/23 | 212/85 | 28/28 |

All 0 unsuppressed majors, seams 0. 170 verifier tests. Built audit: 6 cards,
3,129 ids, 2,571 fragment links, 1,322 page markers, 562 figures, 569 exact
assets, 0 findings.

## Mutation evidence

Strict schema-v2 baselines, eight trials/class, seed 5. The five certified
replays held byte-identically on this session's verifier (twice: after the
first and the final verifier batch). The Gemini baseline was generated on its
final canon (`results-google-deepmind-gemini-4-argon.json`; its row is in
`.github/workflows/mutations.yml`); its misses sit in the known weak classes
(ST2 split-item 5/8, ST1 6/8, L1 7/8, advisory swap-words).

| card | classes | trials | detected | intended-major | major-blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 | 184 | 185 |
| Opus | 24 | 192 | 175 | 167 | 170 |
| Risk Report | 24 | 192 | 173 | 166 | 171 |
| Fable 5.1 | 24 | 192 | 178 | 170 | 170 |
| Opus 5.5 | 24 | 192 | 177 | 169 | 169 |
| Gemini 4 Argon | 24 | 192 | 186 | 178 | 178 |

## Deferred typed minors (owner list, unchanged in kind)

p.225 `<p>`-wrapped seam-merged cell (opus-5-5, TB2 class); 'Transcript' chrome
on label-less boxes; p.228 soft-wrapped blocklist entries; p.166 stray '. .';
Gemini: link anchors that include a period the PDF rect covers, underline
extents with a trailing colon (pp.78–79), the p.66/67 join after a period-less
sentence, decorative section-end rules.

## Durable process invariants

- The PDF is the sole content truth. PyMuPDF is a pinned, fallible observer;
  reproduce publisher errors rather than silently proofreading them.
- Capture is mechanical. Agents inspect and report; they do not transcribe or
  polish publisher text.
- Fix classes in `pipeline/`, never instances or generated sections. Regenerate,
  inspect the exact output diff, preview visible changes, run the corpus-wide
  gate, then re-sweep affected pages and controls.
- A shared-pipeline change covers the target plus every non-target certified card;
  a per-card manifest knob is the device for a fidelity improvement whose
  certified-card canon change awaits owner adjudication.
- Mechanical majors gate within their written scope; probabilistic/visual checks
  advise. The rendered visual pass (D69; the owner scroll for a new producer or
  visual grammar) covers layout classes outside those scopes.
- Generic acceptance cannot weaken a source-bound or final-projection authority.
- Commit early and append decisions. Never push without an explicit owner request.
- Don't regenerate `sections/` or delete oracle caches while a mutation suite or
  a sweep is reading them (mutate.py loads sections once at start, but agents
  read files live). Sweep agents share the session scratchpad — give each its
  own subfolder.

## Open / next

- **Gemini deploy:** all owner decisions are settled (D72–D74); awaiting the
  owner's push request (Pages deploys; CI derives the matrix from `meta.yaml`).
- **Source revisions:** Anthropic's canonical `https://anthropic.com/<doc-slug>`
  redirects are the authority for "current" (D66). Gemini's source is a Google
  Cloud Storage object: compare its `x-goog-generation` / hash to `meta.yaml`.
- **Different producer** is still untested: every card so far is Skia/PDF Google
  Docs Renderer. The table-evidence ask (D61) still wants sparse/unruled
  positives and a natural absent-rule negative from another producer.
- **Mutation-suite speed (parked 2026-09-02):** serial, ~3.5–4 s per trial;
  a process pool and per-class hosted sharding are the semantics-free wins
  (experiment 17).
- **Scoped, not built:** label-less box roles; 'Appendix 9.1'-style L2
  precision; ruled single-cell boxes as tables (docling sees none; experiment
  13's grid discovery found them as one-cell controls).
- **Paused phase 4** and the later authority work are unchanged.
- **Secondary cleanup:** separate section-plan input from generated Markdown.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The
rebuild's goal is unattended mechanical conversion followed by bounded,
evidence-directed review. Read [charter.md](charter.md),
[decisions.md](decisions.md) (D1…D74),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). D70–D71 and
experiment 20 are the most recent full onboarding — the template for a new
vendor's Google Docs export; D67–D68 / experiment 18 the template for another
Anthropic card; D66 / experiment 16 record how a certified card follows a
publisher revision. For a changed corpus, experiment 11 remains the
regression-sweep template.
