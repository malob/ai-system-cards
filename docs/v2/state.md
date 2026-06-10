# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-10 (~05:00) — overnight run #2 complete: ST invariant,
vision sweep (319pp), verifier hardening, sweep-driven fixes; with Fable 5.

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

**OVERNIGHT RUN #2 — done (~05:00).** Landed: ST1/2/3 structural invariants
(+3 mutation classes; ST3 6/6); visual-row reconstruction in the assembler
(fixed the p.38 bullet-misassociation class + chip row order); multi-line
heading merge; nested list levels; flush-left item continuations; count-based
S1 (drop-bold 4/6, residue = duplicate-key + table boundary, documented); two
document-spanning projection bugs fixed (greedy fn-def regex; RE_BOLD crossing
newlines via ZWSP-'****' — generator no longer emits invisible emphasis);
suspended-hyphen A1 fix ('single- and'); ordered-list marker robustness;
docling re-run over ALL pages (cache; v1-derived table-page list missed
continuation pages like p.21). **Vision sweep: 16 agents, 312 pages, 134
findings / 69 majors in 40 classes — experiment 07 + worklist.md** (sweep
snapshot PREDATES some same-night fixes; re-sweep after next regen is the
clean baseline). Commits from ~04:30 unsigned (1Password locked).

**MORNING TOUR OUTCOMES (2026-06-10 ~10:40, D23):** caption = first-class
block (`:::caption`, uniform render, never inside table boxes); AISI quotes =
standard blockquotes; underline capture required (FL-09, with bold-in-cells
restyle). Diagnostic: caption-row-in-grid is the suspected cause of table
column rotation (clean tall tables vs rotated wide ones). Table stitching:
third multi-page table confirmed (p.19–21).

**MIDDAY STRETCH (2026-06-10 ~11:30) landed:** table class COMPLETE (rotation
per-row repair, glued-cell split-before-rotation, caption strip, bold+underline
cell restyle from span flags + stroked thin rules — FL-09); blockquotes
(x0≥112 outside boxes, quote-aware nesting, stitch-compatible); turn-code
merging (label-only turn + code box = one turn with fenced body; fences fixed
<thinking>-tag eating); label-derived turn roles (p.153 flip); boundary-page
ownership split at incoming heading (p.35-36 dup/orphan); footnote-adjacency
stitch fix; bold body-size deep headings (h5/h6 anchors); gap-only paragraph
continuation (chip-row splits). **TRIAGE FIRST NEXT SESSION: S1 5→11 after the
quote/restyle batch** (suspect: bold leads inside AISI quote items). Then:
`:::caption` block + renderer directive (D23), cross-page table stitching
(p.19-21/252-253/309-318), L2 dest resolution, FN1 table-cell refs, ST2×10
triage, full re-sweep (expect way under 69 majors), mutation re-run.

**OPERATING MODE CHANGE (owner feedback 2026-06-10 ~12:40):** autonomous
convergence loop — regen → re-slice → re-sweep → triage → fix → repeat,
self-verifying in the rendered DOM; owner sees editorial decisions and
converged results only (also in CLAUDE.md). Queued residuals from the midday
batches: caption-underline word (prose underline marks reverted after T1
6→33 over-fire; needs rule context filtering), one extra <b> in 4.4.2.A to
adjudicate, cross-page TABLE stitching (quotes now stitch; tables still
don't: p.20-21/252-253/309-318), :::caption block + renderer, L2, FN1
table-cell refs, S1×10 + ST2×12 triage, then FULL RE-SWEEP for convergence.

**CONVERGENCE LOOP ROUND A (~13:00) done:** ST2 12→0 (full-line mutual-prefix
matching; the Results/Rationale flags were verifier truncation artifacts —
page render confirmed those are standalone bold lead-lines, currently run-in
in md, defensible). S1 10→4 (turn-label bracket fidelity restored; bold-lead
paragraph break now requires prev-short-line — run-in '**Results** On…' leads
no longer split; example boxes now apply marks). Remaining S1 ×4, each
characterized: p.45 'Category:' (count/attribution puzzle — md HAS the bold),
p.153 '[Assistant]' (label recorded, still flagged — attribution?), p.182
REAL FIND (bold sentence 'This is a classic agentic safety test.' absent from
md; only its quoted paraphrase present — check example-box content on p.182),
p.222 '[Bottom left:]' (caption sublabel, lands with D23 caption rebuild).

**LOOP ROUNDS REMAINING:** B = cross-page table stitching (p.20-21/252-253/
309-318) + :::caption block + renderer directive + caption-underline word
(rule context filtering). C = L2 dest resolution + FN1 table-cell refs +
S1 residuals above + the +1 bold in 4.4.2.A. D = full re-sweep (16 agents,
fresh slices) → convergence report vs 69-major baseline. THEN owner review.

**ROUNDS B+C done (~13:30):** cross-page table stitching (all 3 spanners
whole; p.252-253 = 28 rows matching v1 exactly); :::caption first-class block
end to end (assembler→serializer→remark directive→CSS; 169 captions,
DOM-verified uniform style incl. transcript captions); L2 resolution
(DEST:N→heading slugs, 427 internal links 0 broken in DOM); table footnote
refs re-injected (FN1 76/77, ref-12 site logged). Gate: T1=6/S1=4/FN1=1/ST1=1
— all characterized. Round D (re-sweep, 4 agents, fresh vsweep2 slices)
RUNNING → convergence report vs 69-major baseline. Residuals for after:
p.38 chip-order T1 (×2, reading-order, typed-model territory), p.182 S1 real
find, ref-12 fnref, caption-underline word, prose-underline context filter.

**NEXT (priority order, sweep-driven):**
1. table-scrambled ×11 (§4 tables pp.51–91): diagnose ONE root cause
   (docling grid traversal vs y-slot insertion); add TB2 cell-order check.
2. Transcript box-mapping: label-only bubbles → empty turns with content
   displaced to :::example (pp.107/118/120/161) + one role flip (p.153).
3. Blockquote detection (unimplemented; pp.51/65/67/130/216) + ST4 check.
4. Caption continuation/association (×7); stacked-footnote oracle boundary
   (p.113/132) then FN1 body-text → gate; table-cell fnrefs (FN1 major);
   L2 dest resolution (DEST:N → anchors); ST2 v2 ×12 triage; T1 ×6 triage.
5. Regen → re-sweep (expect majors well under 69) → full gate+mutations →
   site build → owner review toward acceptance.

**Earlier context (owner feedback ~02:25, the wrapped-bullet incident):**
the current gates are token/marks/count-based and CANNOT see token-preserving
structural damage (split list items, split headings — the most human-visible
class). Two mechanisms, in order:
- **ST structural invariant**: derive layout block boundaries (marker-ZWSP
  signature, hanging indents, gaps) from oracle geometry as an independent
  check against output block structure; mutation-test it (split-a-bullet,
  split-a-heading, merge-two-paragraphs must all flag).
- **V1 visual sweep** (the unbuilt advisor): vision compare of rendered page
  regions vs PDF page renders over a sample; becomes a mandatory pre-review
  step before any "look at it" handoff. Process rule: no preview handoff
  without it.
Same class to audit for: paragraph merge/split from the gap heuristic,
multi-line heading splits (TOC "circumstances" bug), nested list levels
(currently flattened), caption-figure association, blockquote structure
(unimplemented). D21: alt-text pass dropped (captions suffice, owner call).

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
