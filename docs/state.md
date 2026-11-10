# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-11-09. **Six cards LIVE; a seventh converged locally,
NOT pushed.** Anthropic released the **Claude Fable 5.2 & Claude Mythos 5.2
System Card** (`anthropic/claude-fable-5-2`, 264pp, cover-dated 2026-11-09,
canonical pointer `anthropic.com/claude-fable-5-2-mythos-5-2-system-card`)
and the owner asked to onboard it. Same Google Docs export family (Skia/PDF
m159). Onboarded, gated, swept (two rounds), rendered-pass checked and
mutation-baselined in one session (D75 + addendum, experiment 21). The six
live cards are unchanged except two PDF-verified one-hunk canon moves the
owner approved (opus-5 p.97, risk-report p.181). Gemini 4 Argon went live 2026-10-29 (`038d146`,
D70–D74).

## Fable 5.2 onboarding (D75, experiment 21)

- **Census → manifest:** Opus 5.5's table/appendix vocabulary plus opus-5's
  turn-structured transcript (p.104: `#f3f3f3` '[System prompt]', `#e2decf`
  '[User]', '[Assistant]' in a `#faf9f5` container). `#e2decf` is also Table
  8.1's row-label tint (table-owned); `#faf9f5` stays `transcript-container`.
  TOC pp.5–10; 13 stubs (§6 split at page-top 6.5 and 6.6.3, §8 at 8.15);
  docling 2.124.0 on 23 black-ruled pages; inventory 257 pages / 132 figures.
- **Card knob** `box_fit_breaks` (deliberate returns inside turn boxes, p.175).
  The same test finds 45 candidates on certified cards (fable-5 27, risk 13,
  opus-5 5), most already line-structured — an owner question, not done.
- **Shared classes** (all in D75 + addendum): docling-absorbed table footnotes
  dropped; misjoined-cell re-split skips composite keys; two-or-more flanking
  literal asterisks escaped; typed leading '- ' in transcripts literal; white
  mono panels in transcripts are code boxes (one `<pre>` per box); wide
  placeholder fills mark pills; quoted sub-lists stay quoted across pages;
  bold-pair line breaks; mid-line hyphen-space guarded on both T1 sides;
  open-item tiers carried across a page; one page-top continuation per block;
  bidi marks invisible; wrapped pill pieces end at their own bracket.
- **Sweeps:** round 1 (8 comparators + 3 linters, 270 units, 245 clean) → 5
  major classes + the known p.104 class, all fixed; round 2 (12 fix + 15
  seeded clean pages) 27/27 clean.
- **Rendered visual pass:** DOM audit clean at 1338/1680/375px (257 labels, 25
  sidenotes, 132 images); 35 construct screenshots, 0 major, 3 minor (known
  classes).
- **Release:** fast release gate PASSED with seven cards (184 verifier tests,
  built audit 0 findings: 3,660 ids, 2,997 fragment links, 1,579 page markers,
  694 figures, 702 assets).

## Open owner decisions

1. **Deploy** the seventh card (push to main triggers Pages).
2. Later, optional: `box_fit_breaks` on the certified cards (45 candidates).

Resolved 2026-11-09: the owner approved both certified hunks (opus-5 p.97,
risk-report p.181; D75 addendum 2). Resolved 2026-10-29: quotes print as each
PDF prints them (D73); gutter labels stay PDF indices (D74).

## Current card gates

| card | accepted majors | typed minors | L2 | P2/F3 | RF1 |
| --- | --- | --- | --- | --- | --- |
| fable-5 | 20 T1 | L1 34 / T1 21 | 109/109 | 309/151 | 76/76 |
| opus-5 | 4 T1 | T1 4 | 54/54 | 192/100 | 36/36 |
| risk-report-2026-08 | 1 T1 | FN1 1 / T1 5 / TB2 1 | 121/121 | 180/14 | 93/92 (p.126 disposition) |
| claude-fable-5-1 | 5 T1 | T1 3 | 66/66 | 206/103 | 30/30 |
| claude-opus-5-5 | 2 T1 (p.226) | T1 3 | 84/84 | 223/109 | 32/32 |
| gemini-4-argon | 3 T1 (pp.184–185) | T1 7 / TB2 4 | 23/23 | 212/85 | 28/28 |
| claude-fable-5-2 | 2 T1 (p.259) | T1 3 | 96/96 | 257/132 | 25/25 |

All 0 unsuppressed majors, seams 0. 184 verifier tests. Built audit: 7 cards,
3,660 ids, 2,997 fragment links, 1,579 page markers, 694 figures, 702 exact
assets, 0 findings.

## Mutation evidence

Strict schema-v2 baselines, eight trials/class, seed 5. The six certified
replays held byte-identically on the D75 verifier (including opus-5 and the
risk report after their one-hunk moves). The Fable 5.2 baseline was generated
on its final canon (`results-anthropic-claude-fable-5-2.json`; its row is in
`.github/workflows/mutations.yml`).

| card | classes | trials | detected | intended-major | major-blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 | 184 | 185 |
| Opus | 24 | 192 | 175 | 167 | 170 |
| Risk Report | 24 | 192 | 173 | 166 | 171 |
| Fable 5.1 | 24 | 192 | 178 | 170 | 170 |
| Opus 5.5 | 24 | 192 | 177 | 169 | 169 |
| Gemini 4 Argon | 24 | 192 | 186 | 178 | 178 |
| Fable 5.2 | 24 | 192 | 177 | 169 | 171 |

## Deferred typed minors (owner list, unchanged in kind)

`<p>`-wrapped seam-merged cells (opus-5-5 p.225, fable-5-2 p.258, TB2 class);
'Transcript' chrome on label-less boxes; p.228 soft-wrapped blocklist entries;
p.166 stray '. .'; caption underlines that stop before a trailing period /
colon (fable-5-2 pp.74/79/87/88, Gemini pp.78–79); in-cell smaller type
('(Helpful-only)', Table 5.1.3.A); footnote-internal line breaks (fable-5-2
fn 1); Gemini: link anchors that include a period the PDF rect covers, the
p.66/67 join after a period-less sentence, decorative section-end rules.

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

- **Source revisions:** Anthropic's canonical `https://anthropic.com/<doc-slug>`
  redirects are the authority for "current" (D66). Gemini's source is a Google
  Cloud Storage object: compare its `x-goog-generation` / hash to `meta.yaml`.
- **Different producer** is still untested: every card so far is Skia/PDF Google
  Docs Renderer. The table-evidence ask (D61) still wants sparse/unruled
  positives and a natural absent-rule negative from another producer.
- **Visual-pass capture speed:** `shoot.py` full-page clips take ~25 s per
  construct on a 264-page card (experiment 21 made it resumable); element
  screenshots would be the fix.
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
[decisions.md](decisions.md) (D1…D75),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). D75 and
experiment 21 are the most recent full onboarding — the template for another
Anthropic card (D67–D68 / experiment 18 before it); D70–D71 and experiment 20
the template for a new vendor's Google Docs export; D66 / experiment 16 record how a certified card follows a
publisher revision. For a changed corpus, experiment 11 remains the
regression-sweep template.
