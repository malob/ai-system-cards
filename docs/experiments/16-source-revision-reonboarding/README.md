# Experiment 16 — re-onboarding two certified cards on publisher revisions (2026-09-01)

**Question:** Anthropic revises system cards in place at new content-addressed CDN
hashes. The 2026-09-01 revision check (docs/state.md) found that both the Claude
Opus 5 System Card and the Claude Fable 5 & Claude Mythos 5 System Card had
newer canonical revisions than the archived copies. Does the shared pipeline
re-convert a certified card from a revised source with no per-document work
beyond the revision's own facts, and does the result stay certifiable?

**Sources (canonical `https://anthropic.com/<doc-slug>` redirects, authoritative):**

- Opus 5: `ceaf5c7f…/Claude Opus 5 System Card.pdf`, **August 19, 2026**
  revision, 198 pp (archived: `c5fbac3f…`, July 2026 print, 193 pp; the July 24
  reprint `b514064a…` found first is superseded). Changelog p.2: bug-bounty
  results added as §5.2.2.1; Cowork results in §5.2.2.4 re-run on one harness
  with "thinking disabled" rows removed and Claude Fable 5 added. The July 24
  changes (Table 8.1.A FrontierBench row, FrontierCode effort note, FrontierBench
  harness sentence, react-pdf appendix listings) ride along. Pagination shifts
  +1 from p.3 and +4 from p.78.
- Fable 5: `57a52ea7…/Claude Fable 5 & Claude Mythos 5 System Card.pdf`,
  **July 16, 2026** print carrying the **June 25, 2026** changelog entries,
  317 pp (archived: the June 11 revision). Changelog: Executive Summary
  alignment risk "low" → "very low"; the §7.2.1 "Appendix 9.1" hyperlink
  repaired (a Google Docs URL became a working internal named destination);
  §8.15.4 BenchCAD description corrected ("two minor modifications", the
  grading change moved to a forward-looking sentence). Pagination shifts only
  through pp.283–288.

**Method.** Replace `source.pdf`, update `meta.yaml` (`source_url`,
`source_pages`), re-render pages and re-extract figures, rebuild
`source-inventory.json` with the same review rules (Opus TOC pages moved to
6–10; Fable's p.138 duplicate-draw carried), rebuild the docling table cache
**with the pinned docling 2.115.0 on the exact previously reviewed table-page
sets** (a fresh rule-line scan with docling 2.124.0 produced phantom tables
from transcript boxes and re-structured unchanged tables — the reason the pin
is now recorded in `meta.yaml` and CLAUDE.md step 3), regenerate, gate,
re-fingerprint the exact acceptances that moved pages, regenerate the
hash-bound L2/source-projection artifacts, re-pin the unit-test fixtures that
carry source page numbers, run the corpus-wide release gate, replay the
mutation suites, then sweep every changed page with the comparator rulebook
here (`rulebook.md`) plus a rotating sample of Opus pages whose content did
not change but whose page number did.

**Result.**

- Fable 5 regenerates with 22 insertions / 16 deletions on 13 pages — exactly
  the June 25 content plus two edits the changelog omits (p.243 "promise” —
  robust" gained a space; p.282 runs "cards" into "We"), both verified in the
  PDF. The gate stayed at 0 unsuppressed majors with all 20 exact acceptances
  valid; L2 rose 108 → 109 exact destinations (the repaired link), typed T1
  minors 28 → 27, L1 34 unchanged; RF1 76/76; seam 0.
- Opus 5: content diff, page markers and figure names normalized, is the
  revision's own changes only. The four exact T1 acceptances moved
  pp.32/140/141 → 33/144/145 with identical digests and were re-fingerprinted;
  0 unsuppressed majors, T1 8 minors unchanged; L2 54/54; P2/F3 192 content
  pages / 100 figures (was 187/98); RF1 36/36; seam 0.
- Five unit-test fixtures pinned source page numbers or counts and were
  re-pinned: the two Opus known-wrong-destination replay pages (79/80 → 83/84),
  the PDF-structure count tables for both cards, the Opus inventory tuple, and
  the RF1 fixture's footnote-1 page (36 → 37). Corpus-wide release gate: 160
  verifier tests, four card gates with byte-identical artifacts, seams 0, site
  tests, clean build with 887 page markers / 368 figures / 373 exact assets /
  2,178 ids / 1,875 fragment links, 0 findings.
- Mutation replay (seed 5, 8 per class): Opus 175 / 167 / 170 of 192 (was
  176 / 168 / 171 — the trial sites re-sampled on the changed text; split-item
  fell 3 → 1 detected and one swap-words trial lost its major block, both
  advisory-weak classes, while every strict class held 8/8). Baseline
  regenerated. Fable 5 held 191 / 184 / 185 of 200 with every per-class count
  unchanged; its baseline file is refreshed so the recorded trial sites match
  the new text.
- Sweep: three comparator agents, 33 pages (Fable 2, 3, 220, 243, 244, 281–288;
  Opus 2, 75–81, 152–154, 156, 197 and the shifted sample 33, 53, 63, 124, 144,
  149, 196): **0 findings**. Findings files `findings-*.jsonl` here.

**Conclusion:** a publisher revision re-onboards through the shared pipeline
with configuration-only changes (source bytes, `meta.yaml`, inventory, table
cache, acceptance fingerprints, fixture page pins). Recorded as D66. The
docling pin is load-bearing for reproducing a certified table set; a scan-based
table-page list is not a substitute for the reviewed one.
