# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-10 (~01:15) — groundwork + verifier v0 session with Fable 5.

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
  - **Experiment 02 — extractor bake-off, COMPLETE (3 parts)**
    ([experiments/02-extractor-bakeoff/](experiments/02-extractor-bakeoff/)):
    Part 1 (PyMuPDF): links/styles/superscripts/images gate-feasible (GoTo
    exact); chip color lives in pill *fills*; narrator commentary gray #444444;
    FL-07 found. Part 2 (docling): merged cells exact, zero false positives →
    TB1 enforceable. **Stack decided: D14.** Part 3 (hard tables, owner-requested):
    docling exact on the 15×8 two-level-merge monster (p.252) and mixed-span
    tables (p.95/98); nine-page table (p.309–318) → per-page fragments, so
    **cross-page table stitching is a pipeline stage to build**; marker
    eliminated (pipe tables can't represent merges). Calibration flag: v1 p.252
    has 28 `<tr>` vs docling 15 rows — adjudicate against the PDF.
  - **Experiment 03 — signal census**
    ([experiments/03-signal-census/](experiments/03-signal-census/)): the card's
    entire visual vocabulary = 33 fills + 21 text colors ≈ ~15 roles, enumerated
    in ~40 s → empirical basis for per-card style manifests (D16). Found: code
    styling (#f8f8f8/#188038), turn-bubble role colors, vector-drawn chart
    furniture (→ exclusion zones must cover drawing clusters, not just raster
    images), #fefdfb micro-pills ×91 on 2 pages, near-black paste artifacts.
  - **Decisions D15–D18**: placeholders preserved (FL-07 resolved); stratified
    spec (universal core + per-card manifests + closure rule — the
    house-of-cards answer); capture-fidelity vs presentation-editorial split;
    pipeline code in `pipeline/`.
  - **Style manifest seeded** —
    [cards/anthropic/claude-fable-5/style-manifest.yaml](../../cards/anthropic/claude-fable-5/style-manifest.yaml)
    (D16 worked example; owner confirmation pending).
  - **Verifier v0 BUILT + CALIBRATED** (`pipeline/verifier/`; experiment 04):
    T1/L1/P1/F1/FN1 implemented over the PyMuPDF oracle. At `f60899a` it
    rediscovers FL-01 (134 L1 majors vs 2 at HEAD) and PM-06 (exact 5 pages);
    at HEAD it found **new latent v1 defects** — 2 missing named-destination
    links (p.100, `06a:26`) + figure-count anomalies (p.139/150/151). **CA-01
    retracted** (was a grep-separator misread; bidirectional T1 stays).
- Nothing pushed (D13).

## Pending owner decisions (D2 issue-type queue)

- None right now. (FL-07 resolved → D15.) Census follow-ups queued for
  conversion time, listed in experiment 03's README; presentation/palette
  choices are owner-editorial at render review (D17).

## Next actions (in order)

1. **Triage the verifier's new finds** (experiment 04): eyeball p.139/150/151
   page renders vs md (figure counts + the p.139 caption question); fix the two
   p.100 links in v1 content (post-acceptance hand-edit per D9 — v1 is shipped
   content) or leave for the v2 re-conversion; decide the auto-link spec rule.
2. **Extend verifier**: S1 bold/italic runs, S2/S3 chips via style manifest,
   TB1 via docling (incl. cross-check of all 12 v1 HTML tables and the p.252
   row-count discrepancy), L2 destination resolution.
3. **Mutation-test the verifier (D6)**: inject per-class synthetic defects,
   measure recall, close gaps. This turns "calibrated on history" into a
   number.
4. **Design + build the generation loop**: typed document model schema (informed
   by what the oracle emits), semantic-proposal prompts, repair loop against
   gates, N-version arbitration, **cross-page table stitching stage**, vision
   sweep, escalation worklist.
5. **Re-convert Fable 5**; v1's human-verified range (≤ §6) is a partial regression
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
