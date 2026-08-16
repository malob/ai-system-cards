# Table-candidate shadow experiment

## Status

**Continue the table work in shadow; do not adopt this model in production yet.**

Experiment 13 establishes that the project can retain a rich, deterministic Docling
table proposal instead of flattening it immediately to HTML, that a small typed
topology transform can make source-justified changes, and that one typed source-word
assignment primitive can repair isolated cell-ownership errors across two document
families. A follow-up raw-rule origin/projection resolver now composes topology and
word ownership for this fully ruled hard set. It does not establish that the typed
representation simplifies the complete production repair pipeline, discovers grids
independently, handles sparse/unruled or styled/linked tables, works portably, or
should become canonical.

Everything under this directory is experiment-only. Nothing in `pipeline/`,
`cards/`, or `site/` imports it. The experiment changed no generated section,
canonical card content, site output, or release behavior.

## Question

Can the table pipeline approach its largest repair boundary with fresh structure
without discarding what the legacy implementation has learned?

The experiment deliberately separates six questions:

| Track | Question | Result |
| --- | --- | --- |
| [Legacy evidence](legacy-evidence/README.md) | Which present and historical failure classes must a fresh model explain? | A hash-bound counterexample corpus replays 29 raw candidates, 32 manifest references, 13 accepted canonical tables, and five logical multipage shadows. |
| [Clean model](clean-model/README.md) | Can a small project-owned type preserve Docling's public grid and explicit provenance without copying the legacy HTML architecture? | Yes in shadow: an immutable, deterministic `TableCandidate` retains cells, spans, roles, geometry, tool fields, and caller-supplied source/tool identity. |
| [Reproducibility](reproducibility/README.md) | Can the rich Docling proposal and its effective runtime be bound and replayed deterministically? | Yes for two offline runs of Fable source p.20 in one warm local environment after deterministic mini-PDF creation. Portability is unproved. |
| [Topology slice](topology-slice/README.md) | Does one narrow typed repair become source-grounded and locally reviewable? | Yes for three merges on a six-page hard set, with one conservative false negative and no genuine real source-negative in that set. |
| [Word alignment](word-alignment/README.md) | Can exact source words be projected to typed cells without inheriting Docling text ownership or the legacy HTML pass order? | Yes for isolated ownership errors: one source-bound rule made 43 cell-text changes across four tables and preserved three natural controls. Three coupled or surface-sensitive cases failed closed and motivated the origin/projection follow-up below. |
| [Origin/projection](origin-projection/README.md) | Can raw PDF rules and word occurrences resolve coupled topology and ownership before comparing immutable extractor claims? | Yes for the fully ruled, candidate-located hard set: one order-independent resolver derived all 274 reviewed ranges, assigned all 790 words, and jointly resolved Opus p.56 table 1 and raw Fable p.95. Production adoption remains blocked. |

This is a clean-model experiment, not a clean-slate evidence policy. The new
representation was designed without translating the legacy repair functions; the
legacy code was mined separately for positives, nearest negatives, accepted-output
locators, and pass-order evidence.

## Results

### Rich candidates are feasible

Docling's public `TableData` can be adapted without going through HTML. The shadow
candidate has a total rectangular grid, stable source/range-derived identities,
half-open row and column ranges, explicit spans, header roles, fillability, cell
bboxes with their coordinate origins, source regions, extractor/model/settings
provenance, and canonical JSON. Unknown tool fields remain evidence rather than
silently becoming project semantics.

The p.20 probe produced one 6-by-3 table with 16 unique cells. Two offline runs agreed
at all three checked boundaries:

- deterministic one-page PDF SHA-256;
- raw rich candidate SHA-256
  `3d28033f91d00a5cfe9e74fa3f53325f0158387dd8ab37c5d33fec9654944110`;
  and
- complete source/tool/config/model/schema envelope SHA-256
  `eb0514d5e19c22962b9188edda2a7d354ac2659559560ad4d305670a01f9c97f`.

That is a **runtime-bound warm replay result**, not a portability result. It was one
page, one machine, one resolved environment, and two runs. The live environment was
still assembled from unpinned package resolution and library-default model lookup;
the probe recorded and validated what was actually initialized. Production would
need an explicit locked package/model artifact bundle, immutable revisions or byte
manifests, and fail-closed cache binding.

The probe also found that PyMuPDF's default one-page save produces differing file IDs.
Using `reproducible=True, no_new_id=True` made the wrapper bytes deterministic. Cell
bboxes and table provenance use different coordinate origins, the table page number
refers to mini-PDF page 1 rather than source page 20, and the observed table charspan
was `[0,0]`; all must remain explicit rather than guessed.

### The legacy code is evidence, not a scaffold

The committed evidence slice contains 29 unique raw flattened candidates. The
validator checks 32 candidate references, 13 canonical accepted tables, and five
logical multipage shadows. Selected per-page replay matches current
`tables.get_tables()` when the matching PyMuPDF observations are available, while
the committed source, cache, fixture, implementation, canonical-table, and logical
hashes make skipped or stale evidence visible.

Across all 98 current cached candidates, two legacy passes change nothing:

- `merge_fragment_rows`; and
- `dedup_cascaded_cells`.

They may encode real historical failures, but they must not be ported on reputation.
Recover a raw historical counterexample or treat them as retirement candidates.
Other passes have exact positives and nearest negatives and remain requirements to
explain, not algorithms to translate.

### The first typed transform is useful but insufficient

The topology slice ran fresh two-pass extraction on six source pages, yielding seven
typed tables. One pure rule extends an existing typed header through immediately
lower adapter-generated gaps only when partial PDF ruling and ordered source words
support the extension.

It made three source-justified merges:

- Opus p.56 table 0: `Model`;
- Fable p.95: `Model`; and
- Fable p.95: `Claude Opus 4.8`.

It conservatively refused the same source-supported `Model` span in Opus p.56 table
1 because Docling had misassigned `API,` to the lower cell. This is one real false
negative caused by upstream word-to-cell assignment, not evidence against the PDF
span. Several other hard pages also retain unrelated assignment errors.

No genuine real source-negative for this rule was found in the six-page set. The
synthetic suite proves a fully ruled boundary is a byte-identical no-op and an
observed lower cell fails closed, but those are not a substitute for naturally
occurring source negatives. The PDF geometry is also **candidate-conditioned**: the
extractor uses Docling's table bbox and grid dimensions. It is shadow-generator
evidence, not an independent verifier authority.

Accepted HTML was used as a migration baseline, never as source truth. Some accepted
headers retain explicit empty cells where the PDF supports a semantic span; that
difference still requires renderer and migration review.

### Typed source-word assignment repairs isolated ownership, not composition

The [word-alignment slice](word-alignment/README.md) projects every positive-area
PyMuPDF word/grid overlap into the typed candidate while ignoring Docling cell text
and cell boxes as assignment authority. Its source-bound evidence covers 10 cases on
nine pages, 790 PDF words, and 274 reviewed cell labels. Two fresh offline extraction
runs produced identical bytes for all 10 cases; the five source-evidence tests and 12
alignment/replay tests pass.

One all-or-nothing primitive made 43 source-justified cell-text changes: 11 on Opus
p.52, 15 on Opus p.53, two on Opus p.56 table 0, and 15 on Risk p.78. Risk pp.79-80
and Fable p.20 are natural byte-identical no-ops. The rule fails closed on Opus p.56
table 1 because three words land in an adapter gap, on Fable p.94 because the source
and proposal tokenize styled superscript text differently, and on raw Fable p.95
because two words cross atomic cell boundaries. Applying the already-proven topology
merges first makes p.95 a no-op and exactly matches its reviewed associations; that
confirms the topology result rather than creating another alignment repair.

The coupled cases are the important architecture result. A single typed assignment
primitive localizes isolated ownership errors, but p.56 table 1 cannot be completed by
merely ordering topology and alignment passes: even after its adapter-gap payload is
resolved, the lower `Model` cell remains Docling-observed rather than
adapter-generated, so the topology rule still refuses it. A production design would
need a typed origin/projection overlay that preserves source observations, candidate
claims, and derived ownership separately. That was the next hypothesis tested below;
an ordered repair pass was not added.

This remains shadow-generator research. Accepted output was neither source truth nor
label authority, and no alignment result is an independent verifier expectation.

### One raw-rule projection resolves the coupled ruled cases

The [origin/projection slice](origin-projection/README.md) replaces topology-then-text
pass composition with one calculation over three immutable planes: raw PDF
observations, typed extractor claims, and a derived source projection. It builds
connected components from raw horizontal and vertical rule segments, then assigns
source word **occurrences** by full-bbox containment before comparing either result
with Docling's claims. Reviewed ranges appear only in tests; accepted or generated
Markdown is never read.

Across the same 10 table cases, the resolver mechanically derives all **274/274**
reviewed ranges and assigns all **790/790** words exactly once. It jointly resolves
the `Model` rowspan and `API, without a system prompt` ownership in Opus p.56 table 1,
and resolves raw Fable p.95 without calling the earlier topology or alignment
transforms. Fable p.20 and Risk pp.79–80 remain no-ops. Fable p.94 associates all 63
words but blocks text materialization because flattening its styled superscript would
lose source semantics. Risk p.115 is a source-only, fully bounded true blank; without
a typed candidate it cannot make an extractor-origin claim.

Every extractor claim and input `TableCandidate` remains immutable and byte-identical.
The compact replay is also exact and implementation-bound:

- replay SHA-256
  `d255e733b26e9a811dbf629e72557c9b5b92a955a4709fd0d3d6c86bbc913b26`;
- source-reopening evidence SHA-256
  `37bdedacdaafdf77284c07ca39d88d350c40da89cb5cdec9b8a2634df1029a88`;
- `origin_projection.py` SHA-256
  `089cc0d355c9535778ee79457f8dc7e5242aa8a383d184df80d3956a1d9a8924`;
  and
- `build_replay.py` SHA-256
  `7fb111dd1e00e42fb6420fe57dc1fbdd364c60b03d765bc5ef281e964dbb9b5d`.

This closes the previous *ruled-set composition* question, not the production-grid
question. The atomic grid envelope remains candidate-conditioned; there is still no
natural absent-rule-but-keep-separate negative; sparse and unruled tables are out of
scope; and style/link-aware serialization is not implemented. The result is a shadow
generator proposal, not independent verifier authority.

## Proportionality

The experiment scripts now total **8,957 Python lines**, including 2,339 in the new
origin/projection model, evidence extraction, replay builder, and tests. Much of that
is defensive provenance discovery, artifact hashing, runtime introspection, replay
validation, and fail-closed test scaffolding. That is acceptable for a bounded
architecture probe; it is not a production implementation to port wholesale.

A production path should prefer:

- an explicit locked package/model artifact bundle rather than dynamically probing
  every possible Docling resolution path;
- a smaller adapter around the chosen, verified runtime;
- typed source observations and named pure transforms; and
- one final serializer rather than repeated HTML parsing and rewriting.

Adoption must demonstrate **net complexity reduction** against the legacy pipeline.
Moving 2,557 lines of repair complexity into a new model, adapter, or provenance
layer without making the repairs more local and legible is failure, not progress.

## Decision and next discriminating work

Pause further phase-4 structural-authority integration. Pull the table
extraction/grid shadow work forward, but keep it isolated from production until these
questions are answered:

1. **Independent grid and negative coverage:** remove candidate-conditioned atomic
   edges where possible, and find a natural absent-rule-but-keep-separate case before
   widening the merge interpretation.
2. **Table-family coverage:** test sparse and unruled tables; the current
   connected-component result applies only to fully ruled, candidate-located tables.
3. **Semantic serialization:** preserve and emit style, links, footnotes, and other
   word-bound semantics; p.94 correctly blocks rather than flattening them today.
4. **Portable extraction:** repeat under a locked environment on a second platform
   and a genuinely different PDF producer.
5. **Migration proof:** regenerate all three cards in shadow and demonstrate measured
   net deletion of legacy decision logic, not merely equivalent new code and richer
   provenance.

Only then decide whether to migrate incrementally or retain HTML and refactor the
legacy helpers locally. Manual, judgmentful new-document setup remains acceptable;
separating the section plan from generated Markdown is useful but secondary to this
conversion experiment.

## Validation

The six main suites contain **15 + 17 + 2 + 8 + 12 + 12 = 66 unit tests**. The two
source-reopening evidence suites add **5 + 10 = 15**, so **81 test methods pass
overall**:

```sh
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/clean-model -p 'test_*.py' -v
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/reproducibility -p 'test_*.py' -v
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/legacy-evidence -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model \
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/topology-slice -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/word-alignment/evidence -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model:docs/experiments/13-table-candidate-shadow/topology-slice:docs/experiments/13-table-candidate-shadow/word-alignment \
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/word-alignment -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 \
uv run --python 3.12 python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/origin-projection \
  -p 'test_origin_projection.py' -v
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model:docs/experiments/13-table-candidate-shadow/word-alignment:docs/experiments/13-table-candidate-shadow/origin-projection/evidence \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/origin-projection/evidence \
  -p 'test_*.py' -v

uv run --python 3.12 python \
  docs/experiments/13-table-candidate-shadow/legacy-evidence/validate_manifest.py
```

Result on 2026-08-16: all 66 main experiment unit tests and all 15 independent
source-reopening evidence tests passed. The separate legacy validator passed with
`32 locators, 13 canonical tables, 5 logical shadows`. Rebuilding the compact
origin/projection replay produced byte-identical output.

Independent review scored the word-alignment slice **10/12**: full credit for independence,
conservation/fail-closed behavior, natural controls, and provenance/determinism; one
point each for locality/order-independence and proportionality/complexity. Its verdict
was **commit the shadow milestone; do not adopt or migrate production**. At that
stage, the reduced scores reflected unresolved coupled composition and the lack of a
demonstrated net legacy deletion, not a correctness blocker for retaining the
experiment.

The origin/projection follow-up then closed that composition question for the fully
ruled hard set and received an independent score of **9/12**. Its verdict is likewise
**commit the shadow milestone: yes; production adoption: no**. The remaining points
are load-bearing blockers listed above, not documentation polish.

No hosted run, full release graph, production generation, canonical output
comparison, or deployed-site validation is claimed by this experiment.

## Current artifact and implementation hashes

These are SHA-256 values of the checked-in file bytes at this milestone:

| Artifact | SHA-256 |
| --- | --- |
| `legacy-evidence/manifest.json` | `eeee9c8c1e63bec02d713a69ca7acaadec46701ec4d738b1819f69c013873f1b` |
| `legacy-evidence/fixtures/fable-cache-pages.json` | `3e002799554adae2f11a43c227d1b3dac5476663b7255bc9892905bb4e51327b` |
| `legacy-evidence/fixtures/opus-cache-pages.json` | `8752257c06c45e25ee366ce2d33e1748684f523bf66766cee0fa57e9c1ce8562` |
| `legacy-evidence/fixtures/risk-cache-pages.json` | `d5c7de9c8c85939e11aecea9364911e6b5f62cbdb395a9fe37758ba79f8e354a` |
| `reproducibility/probe-result-p20.json` | `b079d332849235bced5f5f46dfc0b5f311babc9a577255d8fab2dcffefca3e1c` |
| `reproducibility/probe-result-summary.json` | `4b47f66a5be1638fe8fab2d0f5137bd41931e15e23c4d09c37e905fccbbbe8d1` |
| `topology-slice/artifacts/hard-set.json` | `329128c4c388d40cd687aabca61c0127e8167a3be511419494f15e5a3eaedfc6` |
| `word-alignment/evidence/source-word-evidence.json` | `22e2fcb220cd29f03ee1b299c22e05f34759919812a13990a6e40682b20365cc` |
| `word-alignment/artifacts/alignment-cases.json` | `c317522f77d91408bc71353695ad6afa490301dd39e7a3cf4d05643704f12e16` |
| `origin-projection/artifacts/origin-projection-replay.json` | `d255e733b26e9a811dbf629e72557c9b5b92a955a4709fd0d3d6c86bbc913b26` |
| `origin-projection/evidence/origin-projection-evidence.json` | `37bdedacdaafdf77284c07ca39d88d350c40da89cb5cdec9b8a2634df1029a88` |
| `origin-projection/origin_projection.py` | `089cc0d355c9535778ee79457f8dc7e5242aa8a383d184df80d3956a1d9a8924` |
| `origin-projection/build_replay.py` | `7fb111dd1e00e42fb6420fe57dc1fbdd364c60b03d765bc5ef281e964dbb9b5d` |
