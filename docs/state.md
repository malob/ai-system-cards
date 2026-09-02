# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-09-01 evening. **Two certified cards re-onboarded locally on
publisher revisions (D66, experiment 16) — NOT pushed:** Claude Opus 5 now converts
the August 19, 2026 revision (198pp; changelog, new §5.2.2.1 bug bounty, re-run
Cowork table) and Claude Fable 5 the July 16 print with the June 25 changelog
("very low" alignment risk, repaired §7.2.1 link, BenchCAD correction). Both gates
are at 0 unsuppressed majors, the corpus-wide release gate is green, and a 33-page
agent sweep found 0 findings. Both mutation replays landed (Opus re-sampled −1,
Fable identical). The deployed site is still `4579d5d` (D65) with the
old prints; the next push deploys the revisions plus three unpushed docs-only
commits. Earlier today the fourth card, Claude Fable 5.1 & Claude Mythos 5.1, was
onboarded and published (D62–D65); the previous baseline was the phase-3 docs
commit `5b752ae` (hosted run
[31938330163](https://github.com/malob/ai-system-cards/actions/runs/31938330163)).
The fourth card, `anthropic/claude-fable-5-1` (212pp, cover-dated 2026-09-01, same
Google-Docs/Skia export family), converted the same day through the shared
pipeline: census → manifest → stubs → figures → source inventory → docling
2.124.0 over 29 rule-scanned pages → 11 majors → 0 in two onboarding class batches
(D62) → experiment-14 agent sweep round 1 → five more generator classes (D63) →
round-2 fix verification, 48/49 clean, one residual class-fixed (D64). The owner
walked the built preview (seven stops) and asked to publish: `8eb82c6` was pushed
2026-09-01 17:16 PDT; hosted fast-release / Pages run
[33574671083](https://github.com/malob/ai-system-cards/actions/runs/33574671083)
passed (all four card gates, clean build, deploy) and the card is live at
https://malob.github.io/ai-system-cards/anthropic/claude-fable-5-1/ (HTTP 200,
merged table corners present, listed on the index). The hosted mutation sensitivity run
[33574670996](https://github.com/malob/ai-system-cards/actions/runs/33574670996)
on the same commit passed for all four cards: Opus 10m25s, Fable 5.1 14m54s,
Risk Report 18m55s, Fable 38m03s (inside the 45-minute job limit).

## Current card gates

- **fable-5 (July 16 print, June 25 changelog — local, D66):** 20 exact accepted
  T1 majors (all fingerprints still valid), 0 unsuppressed; `L1 34` / `T1 27`
  minors; L2 109/109 (the repaired §7.2.1 'Appendix 9.1' link is now an exact
  internal destination; 1 source-unresolvable remains); P2/F3 309/151; RF1 76/76;
  seam 0. Canon moved on pp.2–3, 220, 243, 281–288 only.
- **opus-5 (August 19 revision — local, D66):** 4 exact accepted T1 majors,
  re-fingerprinted on pp.33/144/145 (same digests; were pp.32/140/141), 0
  unsuppressed; `T1 8` minors; L2 54/54; P2/F3 192/100 (192 content pages, 100
  figures; TOC now pp.6–10); RF1 36/36; seam 0. Every page marker shifted (+1
  from p.3, +4 from p.78); content changed on pp.2, 75–81, 152–154, 156, 197.
- **risk-report-2026-08:** 1 exact accepted T1 major, 0 unsuppressed; `FN1 1`
  (declared orphan-ref source defect) / `T1 6` (was 21: phantom-space link-anchor
  false minors removed) / `TB2 1`; L2 121/121 over 123 occurrences; P2/F3 180/14;
  RF1 93/92 with the exact p.126 disposition; seam 0. Canon unchanged.
- **claude-fable-5-1 (deployed 2026-09-01):** 5 exact accepted T1 majors (the pp.159–160
  seam attribution of a table row the PDF cuts mid-cell, and the p.210 §9.2
  code-box label 'None' stream-order class merged with Table 9.1.A's dropped
  repeated header), 0 unsuppressed; `T1 3` minors (three repeated-header drops of the
  seven-page appendix table); L2 66/66 exact (67 authored occurrences); P2/F3 206
  required content pages / 103 required figures / 309 DOM events; RF1 30/30;
  seam 0.

The pinned corpus-wide fast-release gate passed with four cards after the
re-onboarding (160 verifier tests; built audit: 2,178 ids, 1,875 fragment links,
887 page markers, 368 rendered figures, 373 exact assets, 0 findings). Five
unit-test fixtures that pinned source page numbers or counts were re-pinned
(D66); the risk report and fable-5-1 stayed byte-identical.

**Mutation replay after the re-onboarding:** Opus 5 175 / 167 / 170 of 192
(was 176 / 168 / 171; re-sampled trial sites, strict classes 8/8; baseline
regenerated). Fable 5 held 191 / 184 / 185 of 200 with every per-class count
unchanged (baseline file refreshed). Corpus totals over 776 trials: 717 / 687 /
696.

## What the fourth card changed (D62, D63)

Generator classes, all regression-proven byte-identical on the certified cards:

- tables: cascade dedup cuts only at a whitespace boundary ('100%' over '0%');
  multiset-anchored row rebuild when docling detaches a label's first word and
  rotates the values; rebuilt short rows refill docling's own empty cells by
  column interval; `_promote_split_rowspan` skips all-header rows.
- tables: **fill-geometry cell merges** (`_merge_cells_by_fill`) — one drawn fill
  under a non-empty cell that also covers an empty neighbour proves colspan /
  rowspan (2×2 header corners, two-row labels). The oracle gained an additive
  `fills` key. The pass runs behind the per-card manifest knob
  `merge_cells_by_fill`; the certified cards carry the same corner shape and
  their canon moves only after owner adjudication (D46 precedent).
- run: list re-tiering after stitch; seam continuation rows with an empty lead
  join the host's last group start when the seam does not flow; a code box split
  over three pages chains through its last merged page.
- assemble: caption continuation by the line's dominant span size; Inconsolata is
  a mono font.
- serialize: a bold whose `**` cannot flank is emitted as raw `<b>`; a source
  backslash before ASCII punctuation is doubled so the renderer keeps it.

Verifier projection classes (verifier code changed; every mutation baseline was
replayed): inline tags strip to nothing in the projection; `__` is bold only at
word boundaries; ■/□ join the bullet sets; the projection reads `\\` back as one
backslash.

`merge_cells_by_fill: true` is now on for EVERY card (D65, after experiment 15's
review); on the new card `link_text_resolution` stays off (tried for 'Appendix 9.1' p.142 — L2's
source-first geometry binds that destination to the parent heading that shares
p.206's top; the D46 knob is for wrong destinations, not coarse ones).

## Experiment 14 — sweep status

Round 1: 8 comparators over all 206 content pages + 3 linters over 11 files; 217
units, 190 clean; 5 distinct majors (p.88 header corner, p.106 literal `**`,
p.199 split caption, pp.207–209 stranded seam rows, p.212 second fence) and ~12
actionable minors, all class-fixed; 38 source-faithful notes recorded in
`rulebook-round2.md`. Round 2 (fresh `f51-sweep2/` inputs): two fix-verification
comparators over the 34 affected pages + one rotating 15-page clean sample — 49
units, 48 clean, zero regressions; the one residual (p.88's corner, a reading-order
miss in the glued-cell splitter) was class-fixed and verified in the regenerated
section (D64).

Deferred typed minors (owner list): p.159 `<p>`-wrapped seam-merged cells (TB2
class); p.207 a wrapped internal link as two adjacent anchors with one target;
p.55 link span excluding the trailing comma the PDF's link rect covers; p.59
'Fable 5.1/ Mythos' wrap space from the PDF's text layer; the renderer's
typographer curling the p.95–96 shell command's straight quotes (site-wide);
the 'Transcript' chrome on the label-less §6.1.3 boxes (site styling).

## Mutation evidence

Strict schema-v2 baselines at eight trials/class, seed 5:

| card | classes | trials | detected | intended-major | major-blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fable | 25 | 200 | 191 | 184 | 185 |
| Opus | 24 | 192 | 176 | 168 | 171 |
| Risk Report | 24 | 192 | 173 | 166 | 171 |
| Fable 5.1 | 24 | 192 | 178 | 170 | 170 |

`flatten-chip` is inapplicable on the three chip-less cards. The three certified baselines held byte-identically (key-sorted) after both
verifier changes of the day (the D62 projection classes and the oracle `fills`
key); the fourth card's baseline was regenerated on its final canon after round 2
(totals unchanged at 178 / 170 / 170). The fourth
card's committed baseline is `docs/experiments/05-mutation-testing/results-anthropic-claude-fable-5-1.json`;
`.github/workflows/mutations.yml` carries its matrix row.

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

## Open / next

Owner walkthrough of the built preview completed 2026-09-01 (seven stops: merged
header corners, the §6.1.3 boxes, Table 9.1.A's seams, the §9.2 code box, the
p.142 link, the p.42 nested bullets, the p.106 bold lead). Verdict: nothing blocks
publication. Post-publish improvement list, in the owner's priority order — each
item is to be scoped for cost and brittleness before deciding, not assumed worth it:

1. **Done (D65):** page labels after a fenced code box — the canon keeps one fence
   per PDF page with the marker between, and the renderer joins them into one box
   with each label at the true page turn (fable-5, opus-5, fable-5-1).
2. **Done (D65, experiment 15):** `merge_cells_by_fill` enabled on the certified
   cards after agent review of every changed page (26 improvements, 1 neutral, 0
   regressions across all three changes).
3. **Done (D65):** adjacent same-target anchors from a wrapped PDF link are one
   anchor (fable-5-1 p.207, risk-report pp.12/114); eight lines after destination
   resolution, L2 pairing unchanged.
4. **Scoped, not built:** label-less prompt/response boxes (§6.1.3 here, §2.20/§2.24
   in the risk report) have no non-brittle role signal — both boxes share one fill
   and only a prose cue ('we prompted it with:') distinguishes them, which is the
   special-casing the owner declined.
5. **Scoped, deferred:** 'Appendix 9.1' precision needs L2 to accept a heading the
   anchor text names on the destination page, plus mutation reruns, for one link.

The D65 batch (items 1–3) was pushed at the owner's request 2026-09-01 18:04 PDT
(`4579d5d`); hosted fast-release / Pages run
[33577924053](https://github.com/malob/ai-system-cards/actions/runs/33577924053)
passed (all four gates, clean build, deploy) and the live pages carry the
changes: merged header corners on Opus 5 (11), Fable 5 (10) and Fable 5.1 (12),
every blocklist box joined with its page labels inside, and no adjacent
same-target anchors left on any card. The hosted mutation replay
[33577923899](https://github.com/malob/ai-system-cards/actions/runs/33577923899)
on the same commit passed for all four cards: Opus 8m35s, Fable 5.1 14m51s, Risk
Report 20m32s, Fable 39m58s (inside the 45-minute job limit).

- **Source revisions (2026-09-01 check, acted on the same evening — D66):** the
  canonical `https://anthropic.com/<doc-slug>` redirect is the authority for the
  current file. Opus 5 → `ceaf5c7f…` (August 19 revision, 198pp; the July 24
  reprint `b514064a…` found first was itself superseded); Fable 5 →
  `57a52ea7…` (July 16 print, June 25 changelog); Fable 5.1 current; the Risk
  Report has no slug and its URL serves unchanged bytes. Both revised cards are
  re-onboarded locally (experiment 16) and await the owner's push. Method for
  the next check: follow each slug redirect, re-fetch every `source_url`, and
  identify the hash-only PDFs the transparency page links by title and page
  count. The transparency page also lists a Sonnet 5 System Card — a candidate
  fifth card, not requested.
- **Table evidence (unchanged from D61):** bind sparse/unruled positives and a
  natural absent-rule-but-separate negative from a genuinely different PDF
  producer before more table-model work; the fourth card is again the same
  producer family, so it adds no such evidence.
- **Paused phase 4** and the later authority work are unchanged.
- **Secondary cleanup:** separate section-plan input from generated Markdown.

## Cold-start capsule

The first attempt converted one card but made the human the test suite. The
rebuild's goal is unattended mechanical conversion followed by bounded,
evidence-directed review. Read [charter.md](charter.md),
[decisions.md](decisions.md) (D1…D66),
[architecture-roadmap.md](architecture-roadmap.md),
[verification-contract.md](verification-contract.md), and
[verification-methodology.md](verification-methodology.md). D62–D64 record the
fourth card's onboarding; experiment 14 is its sweep; D66 / experiment 16 record
how a certified card follows a publisher revision. For a changed corpus,
experiment 11 remains the regression-sweep template: changed pages plus renderer
controls, the PDF as sole authority, and prompts that ask rather than assert the
expected answer.
