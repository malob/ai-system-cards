# Experiment 12 — source-bound structure authority

## Question

Can the phase-4 structural work start from source-bound investigation notes and
replay candidates instead of a headline count, mutable sweep caches, or whichever
Markdown happens to be current?

## Inventory correction

The architecture review described "16 sweep findings" owned by ST1/ST2. That number
is the sum of **seven Opus raw reports and nine Risk Report raw reports**. Comparator
and linter reports overlap. They reduce to **ten distinct historical defects**:

- four on Claude Opus 5 (pp.44, 83 twice, and 104); and
- six on the Risk Report (pp.9, 42 twice, 85 twice, and 155).

[`replay-candidates.json`](replay-candidates.json) records those ten defects and the
Risk Report p.113 table-cell sibling that the review count omitted because inspectors
labelled it `table`, even though its failure mechanism is the same lost-list structure
as p.155. All eleven defects appear fixed in the output at baseline `5b752ae`. Their
historical bad projections are candidate positive replays, and the current locators
and expected DOM shapes are candidate controls. They are not yet an executable corpus
or a verification floor.

## Evidence boundary

Each candidate case contains:

- the archived source-PDF SHA-256 and physical page;
- manually selected text/geometry lines from a PyMuPDF observation cache, copied into
  this tracked note and bound to the recorded PDF hash and baseline `5b752ae`, but not
  yet asserted by an executable replay;
- a manually classified structural-shape hypothesis from the earlier sweeps;
- a candidate minimized replay based on the historical Markdown/HTML syntax, or an
  exact contiguous historical fragment where `input_kind` says so;
- the reported bad projection signature, pending executable confirmation;
- an exact baseline section locator and a hypothesized good projection shape; and
- tracked sweep/fix provenance, plus the original ignored finding-file name where the
  Risk Report's per-agent record was never committed.

The ignored `pipeline/.cache/**/findings-*.jsonl` files are provenance only. Before a
case can become a fixture, its replay must run from this tracked note plus the archived
PDF and repository; it must not read those caches.

`source_evidence.lines` are recorded observations. `manual_source_shape_hypothesis`
is a human interpretation from the PDF/Markdown/DOM sweeps, not an independent fact.
Keeping the two fields separate prevents expected topology from masquerading as a raw
PDF observation. These notes require executable replay and source-grounded controls
before promotion.

## What the investigation suggests about invariant ownership

These cases should not all be forced into ST2:

| Authority | Defect shapes |
| --- | --- |
| ST1 item occurrence | unrecognized square/`o`/typed/table-cell items |
| ST2 block segmentation | a source list line emitted as a new paragraph or several source lines collapsed into one block |
| List topology (a new stable structural identity is likely warranted) | wrong parent, depth, ordered type, or quote ownership |
| Final-DOM structure | Markdown that becomes `<pre>`, a detached `<blockquote>`, literal marker text, or invalid visible emphasis |
| Table-local structure | source cell items and their continuation paragraphs; a table must enable this check, not exempt the page |

The candidate case `taxonomy` values preserve those distinctions so a future harness
can measure each authority separately.

## Observer spike

The first implementation spike tested whether those authorities can be observed
without importing generator decisions or treating current Markdown as the source of
truth:

- the source observer asks pinned PyMuPDF 1.28.2 for tagged structure with
  `TEXT_COLLECT_STRUCTURE`, retaining list/list-item hierarchy, source pages, bboxes,
  exact full and item-owned text, the strings on each side of the first raw zero-width
  separator, independently nullable boundary-glyph bboxes, tool version, and source
  hash;
- the output observer parses the production article HTML with HTML5 tree-building and
  records visible list/item type, parentage, depth, sibling order, page/section
  context, quote/table ancestry, and item tokens; and
- the output census excludes only the renderer-owned footnote subtree. It reports the
  excluded items separately instead of silently mixing footnote numbering into body
  list structure.

Neither observer participates in generation, and no structural observation or
alignment result accepts or rejects card content. Their unit tests do run inside the
existing fast-release graph. The source tags are publisher claims, not truth:
disagreement is evidence for geometry review and can never authorize an omission.
The source observer is deliberately policy-free: it has no marker regex, geometry
threshold, semantic authority label, or table special case. Null separator/box fields
mean absent or unavailable raw evidence, not a verdict.

The provisional interpretation and exact matcher are deliberately colocated with
this experiment in [`structure_alignment.py`](structure_alignment.py), with its
focused and opt-in corpus checks in
[`test_structure_alignment.py`](test_structure_alignment.py). They are not normal
verifier modules. The
[PDF observer](../../../pipeline/verifier/pdf_structure.py) remains in
`pipeline/verifier/`, and the
[browser-normalized DOM observer](../../../site/src/lib/list-structure.js) remains in
`site/src/lib/`. Neither contains these experimental marker/geometry thresholds.

### Snapshot binding

The following census is a recorded advisory snapshot, not a generated artifact. It is
bound to baseline `5b752ae`, PyMuPDF 1.28.2, source-observer schema 1, DOM-observer
schema 2, token digest `visible-list-tokens.sha256-json.v1`, and these source hashes:

| card | source PDF SHA-256 |
| --- | --- |
| Fable | `c29ffa55ecefab591916dfdefc5ba3fd4e07c27cbef96ca3c05f7601aaebd033` |
| Opus | `fed3c0e6d150a6ba855f0f117a632d2b27dbb5886fd42815caa92e3e20db1d25` |
| Risk Report | `d76815f8c0bd284a33c7017d642d0734ba903ae63f7c1e6ca7778b35b2c40fa4` |

Normal verification does not refresh these counts. Rerun the opt-in census before
relying on them after any observer, renderer, source, or schema change.

### Recorded source-tag census

| card | tagged lists | tagged items | provisionally suspicious in manual review | other tag items |
| --- | ---: | ---: | ---: | ---: |
| Fable | 126 | 364 | 26 | 338 |
| Opus | 56 | 195 | 0 | 195 |
| Risk Report | 83 | 300 | 0 | 300 |

Manual review provisionally classifies 26 Fable claims on pp.251–252 as suspicious
because their raw facts have the exact dash-only, empty-suffix `/LI` shape inside table
cells. Neither observer makes that judgment. The matcher retains all 26 as full-text,
unmatched claims because there is no nonempty, geometry-corroborated suffix to strip.
The classification is advisory and never omission authority. Legitimate one-item
lists in table cells remain ordinary tag claims. This is why tags alone cannot be the
gate.

Raw item-page evidence coverage is also recorded:

| card | item-page rows | first raw separator | prefix first/last boxes | suffix first-nonspace box |
| --- | ---: | ---: | ---: | ---: |
| Fable | 372 | 364 | 364 | 338 |
| Opus | 199 | 194 | 194 | 194 |
| Risk Report | 302 | 300 | 300 | 300 |

These are observation-availability counts, not list correctness judgments.

### Recorded final-body-DOM census

| card | body lists | body items | excluded renderer-footnote items |
| --- | ---: | ---: | ---: |
| Fable | 106 | 368 | 76 |
| Opus | 60 | 224 | 36 |
| Risk Report | 80 | 305 | 92 |

### Recorded exact item-match probe

| card | unique matches | ambiguous matches resolved by page | source residuals | DOM residuals |
| --- | ---: | ---: | ---: | ---: |
| Fable | 297 | 0 | 67 | 71 |
| Opus | 181 | 0 | 14 | 43 |
| Risk Report | 259 | 2 | 39 | 44 |
| **Total** | **737** | **2** | **120** | **158** |

At baseline `5b752ae`, manual inspection provisionally classified the residuals as
follows:

- 60 DOM residuals appear to be table-cell list items omitted by the PDF tags;
- five more appear to be Risk Report items on pp.84–85 omitted by the PDF tags;
- 93 of 120 source residuals appear to have a same-page DOM counterpart but do not
  match exactly enough for a safe item-local join;
- 26 are the retained suspicious dash-only, empty-body Fable tag claims; and
- the remaining source residual appears to be an empty phantom tag on Opus p.104.

The next experiment should test global source/output token intervals rather than
exact whole-item equality, plus bbox-local geometry fallback where tags are absent or
disputed. Page-wide or output-derived exclusions would recreate the correlated
authority failure this work is meant to remove.

Manual review of the recorded snapshot suggests that nine of the eleven candidate
cases have usable native tag evidence. The two Risk Report p.85 candidates are useful
tests for geometry fallback. This motivates the next experiment; it neither proves
that split nor claims 9/11 or 11/11 executable replay coverage.

This README is the canonical record of the counts and provisional manual accounting;
there is deliberately no hand-maintained duplicate results file.

### Reproduce

After installing the locked site dependencies, the observer and advisory census are
rerunnable without the ignored sweep caches:

```sh
pnpm --dir site install --frozen-lockfile
uv run --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest pipeline/verifier/test_pdf_structure.py
pnpm --dir site test
uv run --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest \
    docs/experiments/12-structure-authority/test_structure_alignment.py
RUN_STRUCTURE_ALIGNMENT_CORPUS=1 \
  uv run --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest \
    docs/experiments/12-structure-authority/test_structure_alignment.py
```

The normal verifier-unit job deliberately skips the cross-language corpus census:
the spike is advisory and that job does not install Node dependencies. The explicit
opt-in run above recomputes the advisory census for all three PDFs through the
production renderer and checks the recorded counts.

Final validation of the reduced tree passed: 13/13 source-observer tests; the focused
experiment suite with its expected corpus skip; the opt-in corpus suite 12/12; the
complete fast-release gate with 160 Python tests, every card gate, exact artifacts,
and seams; 45/45 site tests; and the production build with zero final-DOM findings.
Canonical sections remained unchanged. A detached build comparison against baseline
`5b752ae` found all 995 built files byte-identical; the later proportionality pass
changed only Python experiment/observer code and documentation, not production site
inputs.

## Replay contract

A future harness should turn the candidate cases into executable fixtures by:

1. validating the selected source PDF against `source_documents` and the recorded
   probe/tool/schema binding;
2. rendering `candidate_bad_replay.replay_fragment` through the relevant
   Markdown/raw-HTML projection path and requiring the recorded bad signature to be
   detected as major;
3. loading the baseline section by `current_locator`, rendering with the production
   renderer, and requiring `candidate_current_control.expected_dom` with no structural
   major;
4. adding nearest-negative controls before any new structural rule blocks release;
   and
5. running every case so a fix for one document cannot rewrite another.

The replay fragment is intentionally small. `input_kind` states whether it is a
complete Markdown mini-document, a contiguous historical substring, or a raw table
cell body that the harness must place in a neutral one-cell table wrapper.

## Result

The phase-4 investigation inventory is now explicit: **16 raw reports → 10 distinct
historical defects, plus one classification-adjacent table sibling.** All eleven look
fixed in baseline `5b752ae`, but they remain replay candidates until a harness proves
the bad and good sides independently. The spike identifies a promising primitive
pair to test: a source-only structural constraint artifact and an independently
observed final DOM, joined by global token intervals with bbox-local geometry
fallback. The next implementation should test that structural family against these
cases and the schema-v2 mutation misses, not tune the random sampler or add
card-specific generation branches.

This experiment remains **advisory**. No structural finding or alignment result gates
card content, although observer unit tests run in the existing release graph. It made
no generation, canonical-content, or published-output change. It may become blocking
only after the source artifact and matcher catch all 11 executable historical replay
candidates and deterministic structural mutations while all current-output and
nearest-negative controls remain clean.
