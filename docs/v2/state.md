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
- Done:
  - Meta scaffolding (charter, decisions D1–D13, this file, root CLAUDE.md).
  - **Experiment 01 — v1 defect catalog**
    ([experiments/01-v1-defect-catalog/](experiments/01-v1-defect-catalog/)):
    19 defect classes with detection signals, counts, calibration refs
    (`f60899a` = pre-fix content baseline, `fb483fb` = pre-link baseline).
  - **Verification contract** ([verification-contract.md](verification-contract.md))
    — the spine: stable invariant IDs (T/L/S/TB/F/FN/P/SC gates, N/V advisors,
    H human surface), normalization allowlist, exclusions, traceability map.
  - **Experiment 02 — extractor bake-off, COMPLETE**
    ([experiments/02-extractor-bakeoff/](experiments/02-extractor-bakeoff/)):
    Part 1 (PyMuPDF): links/styles/superscripts/images gate-feasible (GoTo
    exact). Discoveries: chip color lives in pill *fills* (S2 amended); narrator
    commentary is gray #444444 (mechanical prior for turns); FL-07 found.
    Part 2 (docling): merged-cell table structure exact, zero false positives →
    TB1 enforceable. **Extraction stack decided: D14** (PyMuPDF oracle + docling
    tables + LLM semantics).
- No v2 pipeline code yet. Nothing pushed (D13).

## Pending owner decisions (D2 issue-type queue)

- **FL-07:** should v2 represent the light-green redaction-placeholder highlights
  (`[Error 1]`, `[user]`…) as a typed mark, or intentionally drop them? (First
  live entry; decide once, it becomes a spec rule.)

## Next actions (in order)

1. **Build mechanical verifier v0; calibrate.** Implement the gate invariants on
   the D14 oracle stack (PyMuPDF + docling for tables); run against `f60899a`
   sections — must rediscover the cataloged defects (recall per experiment 01's
   "how to use"); then mutation-test per class (D6). Gaps → new checks or
   explicit human-coverage notes in the contract. Also the docling revisit
   trigger lives here: cross-check all tables against v1's hand-built HTML.
2. **Design + build the generation loop** (only after 1): typed document model
   schema (informed by what the oracle emits), semantic-proposal prompts, repair
   loop against gates, N-version arbitration, vision sweep, escalation worklist.
3. **Re-convert Fable 5**; v1's human-verified range (≤ §6) is a partial regression
   oracle (brief §8.3 caveats apply). Owner review → acceptance → publish.

## Open questions

- Document-model schema scope (drive from bake-off output + what these docs contain).
- Chunk/wave granularity (per-page validation vs cross-page constructs).
- Escalation/triage UX — start with the dumbest thing (a flat worklist file);
  invest only if volume demands.
- Where v2 pipeline code lives (`v2/`? `pipeline/`?) — decide when first code lands.
- ~~Chip/turn mechanical detectability (brief §7)~~ — largely answered by
  experiment 02: chip = pill fill color; commentary = gray text. Residual
  ambiguity goes to N1.

## Protocol reminders

Decisions → decisions.md when made. Rewrite this file before stopping. Experiments
re-runnable from their writeups. Sub-agent findings land in files. v1 artifacts are
calibration data — don't clean them up (D5).
