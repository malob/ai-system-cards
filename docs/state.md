# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-09-28 11:25 PDT. **Fifth card onboarded locally and
converged: Claude Opus 5.5** (`anthropic/claude-opus-5-5`, 230pp, cover-dated
2026-09-22), from the owner-supplied canonical URL
https://anthropic.com/claude-opus-5-5-system-card (redirects to
`fc1b4471…/Claude Opus 5.5 System Card.pdf`). Nothing is pushed. The deployed
site is still `0e7e3a7` (four cards); ten commits sit on top of it (four
docs-only from 2026-09-02, six from this session).

**Awaiting the owner (after the 2026-09-28 curated review):**

1. **Owner scroll → replaced, pending approval, by experiment 19's rendered
   visual pass**: DOM layout audit at three widths (clean) + screenshots of all
   26 tables/boxes/code blocks reviewed against the PDF (25 clean, 1 cosmetic
   p.82 column-width wrap). The owner spotted a split wrapped pill (p.98) in
   the curated review; fixed as a class in `9aed2f4` (certified cards
   byte-identical). Proposed: make this pass onboarding step 9 for same-family
   cards (CLAUDE.md edit awaits the owner's yes).
2. **Adjudicate the literal-backtick hunks** on fable-5 p.45 and opus-5 p.87
   (composites in experiment 19's method: PDF | live | new — the new build
   matches the PDF). The fable-5-1 caption hunk is visually identical (Markdown
   cleanup only) and needs no decision.
3. **Deploy decision** — a push to `main` deploys all five cards.

## Onboarding summary (D67, D68, experiment 18)

- Census → manifest: fable-5.1-shaped vocabulary plus `#d9ead3` placeholder
  pills (p.98), `#e2decf` Table 8.1.A row tint, pure-black Table 9.1.A header
  fill, `#fafafa` caption highlight furniture. Stubs: 12 files; §6 split at the
  page-top 6.4.11 boundary (p.122), §8 at 8.12 (p.189). TOC pp.5–10 (p.10 the
  five-link tail, reviewed). Docling 2.124.0 on 24 table pages (pp.95–96
  excluded — box borders); the pin is recorded in `meta.yaml`.
- First gate: 20 majors → 2 exact. Classes (D67): fill-aware column chains;
  cascade dedup needs a character surplus, extension a deficit; the seam group
  rule continues past a flowing first row; the 144pt footnote separator opens
  the footnote region at any type size (oracle and RF1, independently); prose
  backticks escaped and the projection keeps them.
- Sweep round 1 (8 comparators + 3 linters, 235 units, 215 clean): 2 majors +
  4 minors fixed as classes (D68): oracle additive `underlines` key for prose
  underline, centred header columns, wrapped pill close bracket, link-rect
  underline, Consolas mono. Round 2: 19/19 clean, fixes verified.
- Production preview DOM-checked: the p.42 underline run, Table 8.1.A header
  band, p.98 pills, footnotes 11/12 as sidenotes, `--bare` code, literal
  backticks, 'Training still to come' rowspan 6; the index lists the card.

## Current card gates

| card | accepted majors | typed minors | L2 | P2/F3 | RF1 |
| --- | --- | --- | --- | --- | --- |
| fable-5 | 20 T1 | L1 34 / T1 24 | 109/109 | 309/151 | 76/76 |
| opus-5 | 4 T1 | T1 7 | 54/54 | 192/100 | 36/36 |
| risk-report-2026-08 | 1 T1 | FN1 1 / T1 6 / TB2 1 | 121/121 | 180/14 | 93/92 (p.126 disposition) |
| claude-fable-5-1 | 5 T1 | T1 3 | 66/66 | 206/103 | 30/30 |
| claude-opus-5-5 | 2 T1 (p.226) | T1 3 | 84/84 | 223/109 | 32/32 |

All 0 unsuppressed majors, seams 0. Fast release gate green: 160 verifier
tests; built audit 5 cards, 2,667 ids, 2,275 fragment links, 1,110 page
markers, 477 figures, 483 exact assets, 0 findings. fable-5/opus-5 T1 minors
fell 27/8 → 24/7 when the projection stopped dropping escaped backticks.

## Mutation evidence

Strict schema-v2 baselines, eight trials/class, seed 5:

| card | classes | trials | detected | intended-major | major-blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 | 184 | 185 |
| Opus | 24 | 192 | 175 | 167 | 170 |
| Risk Report | 24 | 192 | 173 | 166 | 171 |
| Fable 5.1 | 24 | 192 | 178 | 170 | 170 |
| Opus 5.5 | 24 | 192 | 177 | 169 | 169 |

After this session's verifier changes (oracle footnote region + `underlines`
key, RF1 separator, mdproj backticks) the four certified replays are
byte-identical to their committed baselines (key-sorted `jq`). The new card's
misses sit in the known weak classes (ST1/ST2, L1, S1, advisory swap-words);
its `split-item` 1/8 equals opus-5's. `.github/workflows/mutations.yml` has its
matrix row. A hosted replay happens on the next push.

## Deferred typed minors (owner list, unchanged in kind)

p.225 `<p>`-wrapped seam-merged cell (TB2 class, as fable-5-1 p.159);
'Transcript' chrome on label-less boxes (pp.95–96, 98; site styling); p.228
soft-wrapped blocklist entries kept as two code lines (line-for-line
faithful); p.166 a stray publisher '.' line joins as '. .'.

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
  advise. The owner scroll remains mandatory for layout classes outside those
  scopes.
- Generic acceptance cannot weaken a source-bound or final-projection authority.
- Commit early and append decisions. Never push without an explicit owner request.
- Don't regenerate `sections/` or delete oracle caches while a mutation suite or
  a sweep is reading them (mutate.py loads sections once at start, but agents
  read files live).

## Open / next (after the three owner items above)

- **Source revisions:** the canonical `https://anthropic.com/<doc-slug>` redirect
  is the authority for "current" (D66). Method for the next check: follow each
  slug redirect, re-fetch every `source_url`, compare hashes. The transparency
  page also lists a Sonnet 5 System Card — a candidate further card, not
  requested.
- **Mutation-suite speed (parked 2026-09-02):** serial, ~3.5–4 s per trial;
  a process pool and per-class hosted sharding are the semantics-free wins
  (experiment 17 has the analysis).
- **Table evidence (unchanged from D61):** bind sparse/unruled positives and a
  natural absent-rule-but-separate negative from a genuinely different PDF
  producer before more table-model work; Opus 5.5 is again the same producer
  family.
- **Scoped, not built:** label-less box roles (no non-brittle signal); 'Appendix
  9.1'-style L2 precision (fable-5-1 p.142).
- **Paused phase 4** and the later authority work are unchanged.
- **Secondary cleanup:** separate section-plan input from generated Markdown.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The
rebuild's goal is unattended mechanical conversion followed by bounded,
evidence-directed review. Read [charter.md](charter.md),
[decisions.md](decisions.md) (D1…D68),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). D67–D68 and
experiment 18 are the most recent full onboarding (the template for the next
card); D62–D64 / experiment 14 the previous one; D66 / experiment 16 record how
a certified card follows a publisher revision. For a changed corpus, experiment
11 remains the regression-sweep template.
