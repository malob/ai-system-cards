# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-09 (late evening) — meta scaffolding session with Fable 5.

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

- **Phase:** 0 (meta scaffolding) — complete.
- Charter, decision log (D1–D11), this file, and root CLAUDE.md created. No v2
  code exists yet. No experiments run yet.

## Next actions (in order)

1. **Catalog v1 defects into a structured eval set** — `docs/v2/experiments/01-v1-defect-catalog/`.
   Mine the brief's §2 taxonomy + commits `fb483fb`, `975460f`, `e9046f9` (diff
   pre-fix → post-fix states) into a machine-usable list: defect id, class, page,
   pre-fix content, post-fix content. This grounds the verification contract and is
   the calibration corpus for step 4 (decision D5).
2. **Draft the verification contract** — `docs/v2/verification-contract.md`.
   Every defect class (from the catalog + imagination) mapped to its catcher:
   mechanical invariant / N-version diff / vision judge / human escalation, each
   marked gate or advisor (D8). This is the spine of v2.
3. **Extractor bake-off** — `docs/v2/experiments/02-extractor-bakeoff/`.
   Candidates and test pages per brief §6 (PyMuPDF, marker, docling, MinerU,
   vision-LLM baseline). Score primarily on *which contract invariants each tool
   makes enforceable*, not output prettiness.
4. **Build mechanical verifier v0; calibrate.** Run against v1 pre-fix states —
   must rediscover the human-found defects; then mutation-test recall per class
   (D6). Gaps → new checks or explicit human-coverage notes in the contract.
5. **Design + build the generation loop** (only after 1–4): typed document model
   schema, semantic-proposal prompts, repair loop against gates, N-version
   arbitration, vision sweep, escalation worklist.
6. **Re-convert Fable 5**; v1's human-verified range (≤ §6) is a partial regression
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
