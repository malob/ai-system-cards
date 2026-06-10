# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-09 (late evening) — meta scaffolding + experiment 01, with Fable 5.

## Cold-start capsule

v1 converted one card (Claude Fable 5 & Mythos 5, 319 pp, live at
malob.github.io/ai-system-cards) but required so much manual review/repair that the
owner judged the process not worth maintaining. v2 is a ground-up rebuild whose goal
is: hand over a PDF, the pipeline runs unattended at any token cost, and the owner
certifies the result after a short flag-directed review. The governing idea is
**verification-first** — build and calibrate the thing that says "done" before
rebuilding the thing that generates. Read [charter.md](charter.md) for goal and
principles, [decisions.md](decisions.md) for settled questions,
[../v2-design-brief.md](../v2-design-brief.md) for the v1 retrospective (defect
taxonomy in its §2 is load-bearing).

## Status

- **Phase:** 1 (groundwork) — in progress.
- Done: meta scaffolding (charter, decisions D1–D12, this file, root CLAUDE.md);
  **experiment 01, the v1 defect catalog**
  ([experiments/01-v1-defect-catalog/](experiments/01-v1-defect-catalog/)) — 18
  defect classes with detection signals, counts, and calibration refs
  (`f60899a` = pre-fix content baseline, `fb483fb` = pre-link baseline). Two
  classes found beyond the brief's taxonomy (CA-01 injected artifact lines —
  hence bidirectional text equality; FL-06 directive nesting). No v2 code yet.

## Next actions (in order)

1. **Draft the verification contract** — `docs/v2/verification-contract.md`.
   Every defect class (start from the catalog's `detection:` fields + imagination)
   mapped to its catcher: mechanical invariant / N-version diff / vision judge /
   human escalation, each marked gate or advisor (D8). Must include
   **bidirectional** text equality (see CA-01). This is the spine of v2.
2. **Extractor bake-off** — `docs/v2/experiments/02-extractor-bakeoff/`.
   Candidates and test pages per brief §6 (PyMuPDF, marker, docling, MinerU,
   vision-LLM baseline). Score primarily on *which contract invariants each tool
   makes enforceable*, not output prettiness.
3. **Build mechanical verifier v0; calibrate.** Run against `f60899a` sections —
   must rediscover the cataloged defects (recall scored per experiment 01's
   "how to use" section); then mutation-test recall per class (D6). Gaps → new
   checks or explicit human-coverage notes in the contract.
4. **Design + build the generation loop** (only after 1–3): typed document model
   schema, semantic-proposal prompts, repair loop against gates, N-version
   arbitration, vision sweep, escalation worklist.
5. **Re-convert Fable 5**; v1's human-verified range (≤ §6) is a partial regression
   oracle (brief §8.3 caveats apply). Owner review → acceptance → publish.

## Open questions

- Document-model schema scope (drive from bake-off output + what these docs contain).
- Chunk/wave granularity (per-page validation vs cross-page constructs).
- Escalation/triage UX — start with the dumbest thing (a flat worklist file);
  invest only if volume demands.
- Where v2 pipeline code lives (`v2/`? `pipeline/`?) — decide when first code lands.

## Protocol reminders

Decisions → decisions.md when made. Rewrite this file before stopping. Experiments
re-runnable from their writeups. Sub-agent findings land in files. v1 artifacts are
calibration data — don't clean them up (D5).
