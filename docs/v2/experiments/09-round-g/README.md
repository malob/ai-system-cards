# Experiment 09 — round G: AI manual inspection (two check types)

**Question.** After six convergence rounds reached a 0-major gate, does a
rulebook-armed AI manual inspection — the owner-designed pair of checks —
still surface real faithfulness defects the gates and prior sweeps missed?
And does the D25 orchestrator-owned diff-per-fix protocol hold up at fleet
scale?

**Method.** Two inspector fleets over all 319 pages, launched 2026-06-10
~22:55 (this directory's `rulebook.md` is the exact prompt-side rulebook,
compiled from D24/D25 + `pipeline/verifier/accepted.json` + experiment
07/08 adjudications + a page→section map):

1. **Markdown-smell linter** (7 agents, 21 section files): read the md
   itself for suspicious patterns (mid-token emphasis ends, dangling markup,
   inconsistent row styling, spacing/structure smells), then cross-check
   every hit against the PDF page render (high-zoom crops via
   `pipeline/render_region.py` for glyph-level claims) before reporting.
2. **Triple-pane comparator** (16 agents, pages 2–319): PDF page render vs
   per-page md slice (`pipeline/slice_pages.py` → vsweep6/slices) vs
   served-HTML snapshot (single-page card, dev server :4322) — flag anything
   in pane 1 the other two fail to capture.

Findings append per page/file to `pipeline/.cache/vsweep6/findings-*.jsonl`
(schema in rulebook). Inspectors report only; the ORCHESTRATOR owns every
fix (D25): diagnose → class fix in pipeline/ (or owner-adjudicated patch
layer for true one-offs) → regen → `git diff` the tracked sections-v2 output
(expected change + regression scan) → preview verify → seam audit + gate →
commit pipeline+output together.

**Launch baseline (re-confirmed at 22:55):** 0 majors (3 owner-accepted
suppressions needed, down from 6 — three accepted sites now pass naturally),
L1 31 minors (typed v1-parity), T1 73 minors (census in state.md), seam
auditor 0.

**Result.** 25 inspector runs landed (16 comparators + 7 linters + 1 relaunch
after a content-filter kill on the §9.2 blocklist range + a crop-tool infra
fix). 312 pages + 21 section files inspected. After orchestrator adversarial
re-verification, the real defect classes and their fixes (full log in
`pipeline/.cache/vsweep6/triage.md`):

| class | sites | fix |
| --- | --- | --- |
| table-only footnote defs dropped + global renumber | 5 defs / whole doc | hidden shim refs (`cards.js`) |
| cross-page paragraph seams (mid-sentence) | 9 | ragged-right wrap fit-test |
| cross-page caption continuation | 1 (6.5.2.B) | caption-size stitch |
| cross-page boxed-turn continuation | 1 (p.107-108) | per-page-pill `<pre>` splice |
| inconsistently-split rowspan group | 1 (Opus 4.8 p.96) | consistency-gated promote |
| white-text header sub-rows as `<td>` | pp.82/95/96/98 | header-band promote |
| compound hyphen dropped / spurious space | 2 | keep-hyphen join + verifier fold |
| PDF double-drawn image → 2 copies | 1 (p.139) | rect+content dedupe |
| sub-bullets lose nesting across page | 3 (p.215-216) | section-level tiering |
| body-size caption not classified | 1 (6.5.4.2.A) | bracket-lead any-size + absorb |
| green pill backtick-wrapped → code | 1 (p.118) | ph suppresses code mark |
| literal `<link>` swallowed as tag | 1 (p.216) | escape `<` before letter |
| wrapped-heading doubled space | 8 | join-separator guard |
| standalone bold label run into body | 11 | bold-label split |
| blank lines dropped inside `<pre>` | 1 (p.118) | keep ZWSP box lines |
| bare-number §-ref resolved by geometry | 7 | resolve by heading number |

**Adversarial value:** orchestrator re-verification refuted a reported major
(p.118 namespaced `<thinking>` tag IS in the PDF glyphs — crop-proven,
source-faithful) and absorbed several dup reports (the footnote class
surfaced on 6 pages = one root cause). Two would-be regressions were caught
by the diff/gate before commit: a 15→24-row welfare-table blowup (rowspan
promotion ungated) and a +1 T1 from the hyphen fix (resolved by a mirror
fold in `norm.py`).

Gate held at every commit: **0 majors** (3 owner-accepted suppressions),
L1 31, T1 73→**72**, seam auditor 0. Mutation recall re-run unchanged
(content detectors delete-sentence/drop-image/drop-fndef/dup-marker all
100%; structural classes at pre-existing bounds) — the verifier changes
(wrap-hyphen fold, figure dedup) did not weaken detection.

**Residual (owner steer):** the constitution-edits table (7.4.3, pp.244-245)
keeps all cell text but does not recover the bold passage-name lead in its
tall multi-line cells (restyle's band/pool matching); deferred rather than
risk the just-stabilized welfare/dense-cell family. Adjudication items (no
code): a single footnote's internal `●` list flattened; p.224 `I`ts (PDF
sets the `I` in italic — source slip); p.153 inline-code colour; p.198
`:::example` serif-vs-mono.

**Conclusion.** Round G converged. Two rulebook-armed AI inspection modes
(smell-lint + triple-pane) over all 319 pages surfaced 16 real defect
classes past a 0-major gate; every one was diagnosed to a root cause and
fixed at the class level under the D25 diff-per-fix protocol (regen → diff
read twice → preview/crop verify → gate → commit pipeline+output together),
the orchestrator owning all fixes and adversarially re-verifying each
inspector claim. The gate never regressed. The loop works at fleet scale.
