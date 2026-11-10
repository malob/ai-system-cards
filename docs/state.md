# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-11-10. **Seven cards LIVE; an eighth converged locally,
NOT pushed.** The owner handed over Google DeepMind's **Gemini 4 Carbon Safety &
Security Report** (`google-deepmind/gemini-4-carbon`, 94pp, published with the
2026-11-10 general-availability post; storage generation in `meta.yaml`) as
first priority, then asked to look into D75's in-box line-break knob on the
older cards. Both done in one session (D76 + addendum, D77, experiment 22).
Four certified one-hunk canon moves await the owner (below). Fable 5.2 went
live 2026-11-09 (`8e69334`, D75).

## Gemini 4 Carbon onboarding (D76, experiment 22)

- **Template:** the gemini-4-argon knobs unchanged; body and 22pt heads
  `#101010`, footnotes `#101010` 10pt, no code or highlight, table rules
  `#dadce0`. TOC pp.2–4; 7 stubs; docling 2.124.0 on 13 ruled pages; the CCL
  boxes pp.18/20 from the tags; 90 pages / 48 figures.
- **Classes** (Anthropic cards byte-identical): a tagged cut row's page marker
  at the exact seam; tagged lines in the footnote zone dropped; docling split
  rows yield to a full tag grid that spells all their text; no column-rotation
  repair on a tag grid; no style from a reused span instance; an untagged
  sparse continuation is a cut row.
- **Verifier fixes** found by the mutation suite: S1 checks every manifest
  body colour; a numbered heading is not an ordered item (projection). No
  card's gate changed; three certified floors rose (Opus drop-bold 6→7,
  Fable 5.1 drop-bold 5→7, Argon item-to-paragraph 6→7).
- **Sweeps:** round 1 (4 comparators + 2 linters, 97 units, 87 clean) → one
  major class, fixed; round 2 (8 fix + 10 seeded pages) confirmed the fixes and
  caught one stale cell (p.61 bold, regenerated). Visual pass: DOM audit clean
  at three widths; 8 constructs, 0 major.
- **Release:** fast release gate PASSED with eight cards (191 verifier tests;
  built audit 0 findings: 3,875 ids, 3,177 fragment links, 1,669 page markers,
  742 figures, 751 assets).

## D77 — in-box returns by default

D75's `box_fit_breaks` measured on the certified cards: fable-5 and the risk
report regenerate byte-identical, opus-5 changes one line (p.147 'ARGH ARGH
ARGH.' | 'OK. Gun to head…', two lines in the PDF). The knob is retired; the
behaviour is default.

## Open owner decisions

1. **Four certified hunks** (composites in
   `docs/experiments/22-gemini-4-carbon-sweep-round1/hunks/`): gemini-4-argon
   pp.87–88, 88–89, 154–155 — the page-marker label moves to the line where a
   cut row's page turns (content unchanged; D76); opus-5 p.147 — 'ARGH ARGH
   ARGH.' ends its line as printed (D77).
2. **Deploy** the eighth card (push to main triggers Pages). One local commit
   from the Fable 5.2 deploy (`state.md`) rides along.

## Current card gates

| card | accepted majors | typed minors | L2 | P2/F3 | RF1 |
| --- | --- | --- | --- | --- | --- |
| fable-5 | 20 T1 | L1 34 / T1 21 | 109/109 | 309/151 | 76/76 |
| opus-5 | 4 T1 | T1 4 | 54/54 | 192/100 | 36/36 |
| risk-report-2026-08 | 1 T1 | FN1 1 / T1 5 / TB2 1 | 121/121 | 180/14 | 93/92 (p.126 disposition) |
| claude-fable-5-1 | 5 T1 | T1 3 | 66/66 | 206/103 | 30/30 |
| claude-opus-5-5 | 2 T1 (p.226) | T1 3 | 84/84 | 223/109 | 32/32 |
| gemini-4-argon | 3 T1 (pp.184–185) | T1 7 / TB2 7 | 23/23 | 212/85 | 28/28 |
| claude-fable-5-2 | 2 T1 (p.259) | T1 3 | 96/96 | 257/132 | 25/25 |
| gemini-4-carbon | 3 T1 (pp.33–34) | T1 1 / TB2 3 | 36/36 | 90/48 | 4/4 |

All 0 unsuppressed majors, seams 0. 191 verifier tests. Built audit: 8 cards,
3,875 ids, 3,177 fragment links, 1,669 page markers, 742 figures, 751 exact
assets, 0 findings.

## Mutation evidence

Strict schema-v2 baselines, eight trials/class, seed 5, all on the D76
verifier. Certified replays held byte-identically except the three raised
floors above; Carbon's baseline is new (`results-google-deepmind-gemini-4-carbon.json`,
row in `.github/workflows/mutations.yml`).

| card | classes | trials | detected | intended-major | major-blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 | 184 | 185 |
| Opus | 24 | 192 | 176 | 168 | 171 |
| Risk Report | 24 | 192 | 173 | 166 | 171 |
| Fable 5.1 | 24 | 192 | 180 | 172 | 172 |
| Opus 5.5 | 24 | 192 | 177 | 169 | 169 |
| Gemini 4 Argon | 24 | 192 | 187 | 179 | 179 |
| Fable 5.2 | 24 | 192 | 177 | 169 | 171 |
| Gemini 4 Carbon | 24 | 192 | 179 | 171 | 173 |

## Deferred typed minors (owner list, unchanged in kind)

`<p>`-wrapped seam-merged cells (opus-5-5 p.225, fable-5-2 p.258, gemini-4-carbon
p.34; TB2 class); 'Transcript' chrome on label-less boxes; p.228 soft-wrapped
blocklist entries; p.166 stray '. .'; caption underlines stopping before a
trailing period / colon (fable-5-2 pp.74/79/87/88, Gemini pp.78–79); in-cell
smaller type ('(Helpful-only)'); footnote-internal line breaks (fable-5-2 fn
1); a mid-word wrap printed with a space in a narrow docling cell
(gemini-4-carbon p.32); one dropped in-cell italic (gemini-4-carbon p.16);
Gemini: link anchors that include a period the PDF draws in link style,
decorative section-end and heavier group rules.

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
[decisions.md](decisions.md) (D1…D77),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). D75 / experiment
21 is the most recent Anthropic onboarding (D67–D68 / experiment 18 before
it); D76 / experiment 22 the most recent Google DeepMind one (D70–D72 /
experiment 20 for the template's first card); D66 / experiment 16 record how a certified card follows a
publisher revision. For a changed corpus, experiment 11 remains the
regression-sweep template.
