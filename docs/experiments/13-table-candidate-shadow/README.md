# Table-candidate shadow experiment

## Status

**Continue the table work in shadow; do not adopt this model in production yet.**

Experiment 13 establishes that the project can retain a rich, deterministic Docling
table proposal instead of flattening it immediately to HTML, and that a small typed
topology transform can make source-justified changes. It does not establish that the
typed representation simplifies the complete production repair pipeline, works
portably, or should become canonical.

Everything under this directory is experiment-only. Nothing in `pipeline/`,
`cards/`, or `site/` imports it. The experiment changed no generated section,
canonical card content, site output, or release behavior.

## Question

Can the table pipeline approach its largest repair boundary with fresh structure
without discarding what the legacy implementation has learned?

The experiment deliberately separates four questions:

| Track | Question | Result |
| --- | --- | --- |
| [Legacy evidence](legacy-evidence/README.md) | Which present and historical failure classes must a fresh model explain? | A hash-bound counterexample corpus replays 29 raw candidates, 32 manifest references, 13 accepted canonical tables, and five logical multipage shadows. |
| [Clean model](clean-model/README.md) | Can a small project-owned type preserve Docling's public grid and explicit provenance without copying the legacy HTML architecture? | Yes in shadow: an immutable, deterministic `TableCandidate` retains cells, spans, roles, geometry, tool fields, and caller-supplied source/tool identity. |
| [Reproducibility](reproducibility/README.md) | Can the rich Docling proposal and its effective runtime be bound and replayed deterministically? | Yes for two offline runs of Fable source p.20 in one warm local environment after deterministic mini-PDF creation. Portability is unproved. |
| [Topology slice](topology-slice/README.md) | Does one narrow typed repair become source-grounded and locally reviewable? | Yes for three merges on a six-page hard set, with one conservative false negative and no genuine real source-negative in that set. |

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

## Proportionality

The experiment scripts total **4,169 Python lines**. Much of that is defensive
provenance discovery, artifact hashing, runtime introspection, replay validation, and
fail-closed test scaffolding. That is acceptable for a bounded architecture probe; it
is not a production implementation to port wholesale.

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

1. **Genuine source-negative controls:** find natural tables where the same visual
   preconditions nearly hold but the header must not merge.
2. **Typed word-to-cell alignment:** test whether exact PyMuPDF words and geometry can
   repair the demonstrated p.52, p.56, and p.78 assignments without importing the
   legacy HTML pass order.
3. **Locked portable replay:** rerun a representative hard set in a clean locked
   environment and on a second platform with explicit CPU/device/thread policy.
4. **Complexity and provenance comparison:** implement enough topology and alignment
   to compare rule count, ordering dependencies, provenance, counterexamples, and
   output differences against the legacy path before migrating anything.

Only then decide whether to migrate incrementally or retain HTML and refactor the
legacy helpers locally. Manual, judgmentful new-document setup remains acceptable;
separating the section plan from generated Markdown is useful but secondary to this
conversion experiment.

## Validation

The four suites contain **15 + 17 + 2 + 8 = 42 unit tests**:

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

uv run --python 3.12 python \
  docs/experiments/13-table-candidate-shadow/legacy-evidence/validate_manifest.py
```

Result on 2026-08-16: all 42 unit tests passed. The separate legacy validator passed
with `32 locators, 13 canonical tables, 5 logical shadows`.

No hosted run, full release graph, production generation, canonical output
comparison, or deployed-site validation is claimed by this experiment.

## Current artifact file hashes

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
