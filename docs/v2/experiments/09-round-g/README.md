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

**Result.** _(running — to be filled from findings + fix log)_

**Conclusion.** _(pending)_
