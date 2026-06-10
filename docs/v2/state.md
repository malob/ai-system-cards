# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-10 (~03:10) — full overnight stretch: verifier v0 + generation loop + first full v2 re-conversion; with Fable 5.

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

- **Phase:** 2 (generation) — first full mechanical re-conversion done; refining.
- **Headline:** the v2 loop converted all 319 pages mechanically (zero LLM calls)
  to **26 major gate flags total, T1=4 / P1=1** — text & structure essentially
  clean document-wide. Site builds + renders against the output (28 chips, 88
  turns, 38 tables, 153 figures, 51 citation links). NOT accept-ready: a
  mechanical pre-LLM draft with a triaged worklist ([worklist.md](worklist.md),
  experiment [06](experiments/06-full-reconversion/)). Output in `sections-v2/`
  (gitignored); v1 still shipped (D9); nothing pushed (D13).

### Earlier groundwork (phase 1, complete)
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
  - **Verifier v0 BUILT + CALIBRATED + finds TRIAGED** (`pipeline/verifier/`;
    experiment 04): T1/L1/P1/F1/FN1 over the PyMuPDF oracle. **141 major flags
    at pre-fix `f60899a` vs 4 understood ones at HEAD** (chip-cluster order).
    Rediscovers FL-01 and PM-06 exactly. Triage outcomes: p.100 "missing
    links" = **source-PDF defect** (unresolvable Google-Docs named dests; new
    flag class); figure-count anomalies = v1's documented skip comments, now
    honored as declared exclusions; p.139 caption = verifier bug, fixed
    (image-rect text exclusion removed). **CA-01 retracted** (grep-separator
    misread; bidirectional T1 stays).
- Nothing pushed (D13).

## Pending owner decisions (D2 issue-type queue)

- None right now. (FL-07 resolved → D15.) Census follow-ups queued for
  conversion time, listed in experiment 03's README; presentation/palette
  choices are owner-editorial at render review (D17).

## Next actions (in order)

Close the 26 worklist majors (all triaged in experiment 06), biggest first:
1. **S1 token-coverage refinement** (S1 ×13): the emphasis is PRESENT in v2 but
   run-segmented differently than the oracle, defeating S1's substring match
   (diagnosed — not lost bold). Change S1 to compare bold *token coverage*, then
   RE-RUN its mutation (drop-bold) + v1-calibration suites before trusting it.
   Residual genuine caption-lead-extent cases (p.304/307) surface after.
2. **L2 destination resolution** (L1 ×5 = 3 goto + 2 uri): resolve `DEST:<page>`
   goto targets to section anchors — mine v1's `tools/apply_internal_links.py`.
3. **Table-cell footnote refs** (FN1 ×1): re-attach `<sup>` refs docling flattens.
4. **LLM alt-text pass** — the one genuinely LLM-required step; per figure from
   page renders. Then an adjudicator pass for residual ambiguities (N1).
5. **`:ph` placeholder directive** in renderer + verifier (FL-07/D15), then emit it.
6. **Cross-page table stitching** (p.252–253, p.309–318 come as per-page fragments).
7. Owner review of rendered v2 vs PDF → acceptance → publish.

Deferred verifier polish (interleave): harden stacked-footnote boundary detection
→ promote FN1 body-text advisory to gate; full mutation-suite re-run for the record.

Living spec started: [spec-rules.md](spec-rules.md) — R1 auto-links (decided,
D19), R2 unresolvable dests (proposed default in effect; sic-note presentation
question open, non-blocking). Fable 5 manifest roles owner-confirmed (D19).

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
