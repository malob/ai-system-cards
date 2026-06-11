# v2 state

Rewritable snapshot of where the v2 effort stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-10 (~afternoon) — convergence rounds D+E: re-sweep
found 25 majors (vs 69 baseline), ALL 24 actionable fixed at class level;
verification sweep (flagged 30pp + random 30pp) launched; with Fable 5.

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

- **Phase:** 2 (generation) — convergence loop, round E (verification) running.
- **Headline:** loop is converging. Sweep #1: 69 majors → fixes → re-sweep
  (round D, 4 agents, all 319pp): **25 majors** → fix wave (this session):
  **all 24 actionable closed at class level** (1 adjudicated source-faithful,
  p.43). Gate: **FN1 major 0** (was 1), S1 4 / ST1 1 / T1 6 — all known typed
  sites; T1 minors 198→143. Model-name displacement across all tables: 13→0.
  Round E (verify 30 flagged + 30 random pages, fresh `vsweep3` slices via the
  now-committed `pipeline/slice_pages.py`) running in background; results land
  in `pipeline/.cache/vsweep3/findings-*.jsonl`. Experiment
  [08](experiments/08-convergence/) is the record. NOT accept-ready until
  round E verdicts + final mutation re-run + owner H2 review.
- **Round-D fix inventory (all in `pipeline/generate/tables.py` unless noted):**
  fragment-row merge; glue-split x-guard + fnref exclusion; misjoin re-split;
  truncated-cell extension (column-run prefix); y-band rotation pools +
  char-multiset row rebuild; geometric per-segment bold/underline restyle
  (suppression ≥0.9); entity/quote folding (compare-only); stray fnref-digit
  absorb. Elsewhere: cross-page footnote continuation (oracle `cont` key →
  serialize merge; FN1 mirror), wrapped-heading continuation (assemble + ST3
  mirror), lettered list markers + space, empty-block guard, caption
  bracket-lead spacing.

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
refs re-injected.

**ROUND D done (~afternoon):** re-sweep all 319pp → 25 majors (was 69);
fix wave closed all 24 actionable (see Status above + experiment 08); gate
now FN1 0 / S1 4 / ST1 1 / T1 6 majors, all typed. Detector sweep:
model-name displacement 13→0 across every table.

**ROUND E DONE + fix batch:** sample 30pp: 0 majors (22 clean / 8 minor);
flagged 30pp: 20 fixed / 4 still-broken / 5 known-residual / 1 by-design.
ALL round-E findings fixed at class level same session (see experiment 08):
prefix-anchored bands + empty-cell rebuild (the 4 stragglers), fnref-tolerant
restyle, GPT-5.5 wrap join, th demotion, transcript literal-markup escaping,
sentence-bounded turn splits, caption underline, straddle-split + nesting
rank, semantic section links (28/28), entity-safe restyle, paragraph
separators, inline-code marks (RobotoMono), and a LATENT bug: marks in
labeled turns were offset by len(label) — now shifted. Suspect-row detector:
0 repo-wide. Site builds clean; DOM-verified (27 code spans, 15 underlines,
0 escape leaks).

**ROUND F DONE (15:45):** 11/15 fixed; 4 still-broken + 3 new finds, ALL
root-caused and fixed same session (header sub-rows, prefix anchors ≥4,
digit-dot wrap join, fragment th demotion, fnref-digit through tags, glued
span virtual split, slicer snap fix). Verified per page in regenerated md;
displaced 0; T1 minors 128. Experiment 08 has the full record + conclusion:
**the loop converges** (69 → 25 → 7 → 0 open majors). Next: owner H2 review
toward acceptance; optionally one more full 319-page sweep from the
0-known-majors baseline.

**OWNER H2 REVIEW IN PROGRESS (16:50):** verdicts so far: p.182 bold-in-code
FIX (build styled <pre>); p.38/44 chips ACCEPT+whitelist; em-dash item ABSORBED
by the mega-table rebuild. Owner caught a MISSED CLASS: multi-paragraph cells
+ cross-page row continuations in the welfare table (now fixed: cell paragraph
reconstruction, marker-preserving continuation-row merge, normalized seam
join; `pipeline/audit_table_seams.py` is the committed mechanical checker, 0
flags). Owner directive: systematic image-vs-DOM audit of ALL tables —
running as background agent → `pipeline/.cache/vsweep5/findings.jsonl`.
STILL OPEN: label cosmetics verdicts (p.153/222/45), adjudication blessings
(p.43 literal markup, bracket labels), `:::ph` green placeholder highlights
(owner-requested build, FL-07/D17), p.182 styled-<pre> build, S1/T1
whitelist entries for accepted residuals.

**TABLE AUDIT ROUND (17:15) — vsweep5, all 36 table pages image-vs-md:**
9 majors found; root-caused and FIXED: p.297 Toolathlon (my width-cap
regression — removed; fnref-feasibility now guards the p.49 case instead),
pp.77/80/252/253 phantom columns (`_normalize_rowspan_subrows`: a row covered
by a first-column rowspan must not carry a leading empty cell). Findings:
`pipeline/.cache/vsweep5/findings.jsonl`.

**TABLE AUDIT: ALL ITEMS CLOSED (18:00).** Welfare paragraphs complete (0
inline Q-seams, 71 <p>; unified quote-class fold — docling/PyMuPDF disagree
on quote glyphs — + line-segment fallback matcher + inline-question
normalizer). CB table p.20-21: rowspan extended over the cross-page
continuation row (`_extend_rowspans_over_short_rows`). 7.4.1.A/B cascade:
created by `_extend_truncated_cells` in dense rule-less tables — fixed by
running the endswith `_dedup_cascaded_cells` after extension (3 bullets/cell,
PDF-exact). Adjudicated source-faithful: 'With/Without thinking' bold
(pp.95-98/252 — PDF bolds them; audit-agent error) and 'GDP.pdf' (real
benchmark name, p.253). T1 minors at 100 (was 198). Seam auditor 0.

**H2 REVIEW COMPLETE (18:40) — GATE AT 0 MAJORS.** All verdicts in D24.
Built: `.ph` green placeholder pills (sub-span pill→char mapping; raw-HTML
spans — directive syntax broke on bracketed content), styled `<pre>` for the
p.182 bold code box (S1 → 0). Verifier bookkeeping fixes during review:
S1 punctuation-key symmetry (p.45 was never a content defect), ST1
sentinel-padding item regex (p.149 ditto), owner-accepted whitelist
(`pipeline/verifier/accepted.json`, suppressions printed). Review also
caught + fixed: label-overflow into turn pills (marks-offset class),
[Bottom left:] split-bold (merge-before-filter), GPT-5.5 etc. Remaining
gate: FN1 minor 1 (ref-12), L1 minor 31 (anchor cosmetics), T1 minor 100
(squash-level join noise). Site builds clean; 21 ph pills + 169 captions +
styled pre DOM-verified.

**OWNER READING FLAGS (18:30) — 4 fixed, 1 queued:** figure-caption merge
(7.5.1.A+B in one block) → captions split at every bracket lead; UK-AISI
quote lettered items now nest under their ordered parents (3-space quote
indent); group-label double-bold (th+<b>) stripped; table row-hover CSS
removed entirely (owner verdict — misbehaved on merged tables in v1).
**LATE FLAGS FIXED (18:40):** lettered sub-lists render as <ol type="a">
(renderer plugin: consecutive-letter bullets convert, prefixes stripped —
md keeps literal letters, gates untouched); figure captions interleave under
their own figures (per-figure emission); p.66 cross-page lettered item
nests; [so it] pill exact (bracket windows ±4). 38 pills, 0 nested.

**QUEUED (next session, first item):** group sub-row colspan distribution —
give 'API…'/'Claude.ai' labels colspan = data_cols/n_labels so they visibly
span their column groups, and normalize the 4.2.A-empty-cell vs
4.2.B-rowspan inconsistency. Mechanical (geometry supports it) but touches
the just-stabilized header-subrow family: do it fresh + re-run the table
audit after. One residual th<b> variant left (multiline attr form).

**READING ROUND 2 (18:50) — all fixed:** §6.1.2 'disaster' = items now
INHERIT quote context (cross-page carry via quote_carry param) instead of
deriving from x>=112 alone; same-line span-gap word spaces ('isoverall'
class, T1 minors 100→86); cross-page turn stitching (p.103/104 mid-sentence
bubble split); mono spans no longer early-out of marks (code boxes get bold
+ green pills: p.182 <b> in <pre> → S1 0, pp.107/108 […] pills incl.
own-line); example bodies drop code marks (CSS mono) with mono-line hard
breaks; lettered lists render <ol type=a> (renderer plugin); pill bracket
windows ±4 ([so it] exact). Adjudicated: transcript role color for p.104
continuation NOT inferable from source (owner: don't worry about it).

**FULL FAITHFULNESS PASS (21:30) — owner-directed.** Phases: (A) p.95/96
covered-row sub-labels unified td+b (values were already fixed); (B)
group-label colspans (API/Claude.ai span their column groups; uniform bold;
4.2.B-style 1-col groups correctly untouched); (C) T1-minor census-driven:
mdproj sentinel-protected literal markup (86→72; escaped stars were being
re-eaten by the italics stripper); (D) FN1 emphasis-fold (FN1 now ZERO);
L1×31 adjudicated v1-parity (PDF auto-linked blocklist domains). (E) MANUAL
TRIANGULATED SWEEP (PDF render + preview screenshot + served-HTML DOM):
p.96 5.2.2.2.A cell/style exact; CB table 2.2.1.A incl. cross-page AAV row;
p.85 BBQ pair incl. bold 100 (served HTML; screenshot was stale); p.118
transcript — sweep CAUGHT a class: multi-block boxed turns lost all but the
last block (the '<thinking>' opener) — code_lines now APPENDS; §9.2
blocklist; 7.5.1 figure/caption interleave. Gate: 0 majors, FN1 0, L1 31
(typed), T1 72 (join noise).

**ROUND G DESIGN (owner-proposed, 22:30) — two inspector checks:**
1. **Markdown-smell linter**: read the md itself for suspicious patterns
   (mid-name bold ends like '<b>Mythos</b> 5', dangling markup, odd
   spacing/structure), cross-check each hit against the page render, propose
   a class fix or a patch, re-verify after. VALIDATED live: the 8.1 header
   partial-bold was caught this way by the owner; root cause was a len>=2
   styleable gate + un-collapsed adjacent runs — both fixed.
2. **Triple-pane comparator**: PDF page screenshot vs WEB page screenshot vs
   the corresponding DOM span — flag anything in pane 1 the other two fail
   to capture. VALIDATED: this mode caught the swallowed '<thinking>' opener
   (21:30 sweep).
Build plan: both as rulebook-armed agent prompts (rules = D24 +
accepted.json + adjudications in experiments 07/08) over all 319 pages;
findings → class diagnoses (pipeline fixes preferred) + an owner-adjudicated
post-regen PATCH LAYER for true one-offs (applied by run.py, durable across
regens — never silent md edits). Owner role: adjudicate the disagreement
list.

**KNOWN RESIDUALS (typed, deliberate):** T1×6 majors = p.38/44 chip reading
order (typed-model territory) + 4 understood sites; S1×4 = p.45 'Category:',
p.153 '[Assistant]' label, p.182 missing-bold sentence (REAL find, example-box
content), p.222 '[Bottom left:]'; ST1×1; FN1 minor×1 (ref-12 site); L1
minor×31 (anchor-text cosmetics); caption-underline word + prose-underline
context filter (queued; reverted once for T1 6→33 over-fire).

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
