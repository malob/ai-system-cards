# Experiment 15 — certified-card regression review of the fourth card's improvements (2026-09-01)

**Question:** two shared-pipeline improvements developed on the fourth card
(experiment 14, D63) were held off the certified cards by byte-identity: the
fill-geometry cell merges (`merge_cells_by_fill`) and, from the post-publish list,
the code-box page-break treatment (D65). Applied to the certified cards, is every
resulting change an improvement or at least neutral against the PDF? This is the
owner's standing rule for shared improvements (2026-09-01): regenerate the earlier
cards with the change and have agents judge each diff hunk before their canon moves.

**Method:** enable the knob on all three certified manifests; regenerate all four
cards; for every changed page (found by mapping each diff hunk to its nearest
preceding page marker) stage the diff, the new per-page slice, and the freshly
built page under `pipeline/.cache/review1/<card>/`; one reviewer agent per card
judges each changed page against zoom crops with the rulebook here
(`rulebook.md`), recording improvement / neutral / regression per page.

**Scope:** fable-5 pages 76, 78, 81, 85, 94, 95, 97, 251 (tables) and 316–317
(code box); opus-5 pages 56, 58, 60, 66, 75, 76, 77, 148 (tables) and 191–193
(code boxes); fable-5-1 pages 210–212 (code box). The risk report is
byte-identical under the knob (no merged-corner tables). Gates before review:
every card at 0 unsuppressed majors with unchanged typed minors; L2 and
source-projection artifacts regenerated; built-page DOM audit 0 findings.

**Result:** four reviewer agents (one per card, plus a round-2 reviewer for the
wrapped-link join added while round 1 ran), 27 changed pages: **26 improvements,
1 neutral, 0 regressions.** fable-5: 8 fill-merge + 2 code-box improvements;
opus-5: 8 fill-merge + 3 code-box improvements (its p.191→192 box had been merged
by the old stitch rule, the p.192→193 box never had been — both now join in the
renderer with in-box labels); fable-5-1: code-box p.210 neutral, pp.211–212
improvements, p.207 link-join improvement; risk-report: pp.12/114 link-join
improvements. Findings: `pipeline/.cache/review1/findings-*.jsonl` and
`review2/findings-links.jsonl`. Adopted as D65; every card's canon moved and its
L2/source-projection artifacts and mutation baseline were regenerated.
