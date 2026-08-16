# Source-first ruled-grid evidence

This directory retains the candidate-free census and investigation evidence for
the grid-discovery experiment. It answers a deliberately narrow question: can
ruled regions and their source words be proposed directly from the three archived
PDFs, without first consulting an accepted Markdown table, legacy HTML, a Docling
candidate, or reviewed cell labels?

The answer on this corpus is **yes for source-derived ruled-grid regions**, with
important limits. It is not evidence that geometry decides whether a region is a
semantic table, and it does not establish sparse or unruled-table competence.

## Retained boundary

`extract_grid_discovery_evidence.py` pins PyMuPDF 1.28.2 and exposes
`observe_page(document, page_1based)`. The document must be file-backed. The
observer hashes the original file bytes, extracts every visible stroked
axis-aligned `l` path item and every source word, and invokes exactly:

```python
page.find_tables(strategy="lines_strict", use_layout=False)
```

The result is a **ruled-grid proposal**, not direct PDF boundary truth. PyMuPDF's
finder may normalize or synthesize geometry internally. A separately computed graph
over raw stroked `l` segments therefore cross-checks every multi-cell proposal by
shape and outer-box overlap. Both representations come from pinned PyMuPDF; they are
distinct calculations, not independent parser implementations. Fill-only rectangles
remain drawing provenance and `re` items are never decomposed into rules.

The observer returns the hash/settings bundle plus a minimal label-free page
payload and finder regions. No discovery model or production adapter is retained
here. The evidence extractor does not import accepted output or semantic review
data.

## Frozen artifacts

- `source-pages.json` is the source plane: document and implementation hashes,
  settings, representative complete page observations, all raw enveloped
  components, all finder regions, word-ownership digests, and every accepted
  boundary-slot coverage measurement.
- `review-manifest.json` is a physically separate post-freeze review plane:
  publisher caption claims, PDF structure-tag challenges, complete-page visual
  classifications, negative controls, and kill criteria.

The review manifest binds the exact SHA-256 of the source plane. Rebuilding is
byte deterministic under the pinned observer.

## Census

| Source | Pages | Ruled regions | Raw 1x1 boxes | Owned words |
|---|---:|---:|---:|---:|
| Claude Opus 5 | 193 | 27 | 17 | 2,253 |
| Claude Fable 5 | 317 | 40 | 54 | 5,617 |
| Risk Report | 186 | 31 | 6 | 5,737 |
| **Total** | **696** | **98** | **77** | **13,607** |

All 98 finder proposals have exactly one raw multi-cell enveloped component with
the same row/column shape and IoU at least 0.80. All 13,607 words whose boxes
overlap a proposal fit exactly one non-null finder cell using 0.75-point full-box
containment tolerance; none are outside or ambiguous.

The raw graph observes 73 internally complete regions and 25 span-bearing
regions, comprising 3,326 present-rule atomic-slot separations and 143 absent-rule
merges. Internal-axis support can be very sparse across a region: the corpus
minimum is 2/17 (0.117647), so an axis-wide 50% support rule would reject a real
source shape.

## Cumulative-gap guard

Midpoint/tolerance contact is not enough: many individually sub-tolerance gaps
can accumulate into a mostly missing rule. The source artifact therefore stores
exact union coverage and total missing length for all 1,774 outer atomic boundary
slots and all 3,326 accepted internal boundary slots.

| Boundary class | Minimum exact coverage | Maximum total missing length |
|---|---:|---:|
| Outer atomic slot | 0.980769219675 | 0.5 pt |
| Present internal slot | 0.979166666667 | 0.5 pt |

For this corpus, requiring at least 0.95 exact coverage and no more than 0.75 pt
of cumulative missing length retains every observed boundary. This is a
corpus-backed mutation guard, not a universal constant.

## Semantic and negative controls

Geometry cannot authorize a table role. Two ruled regions are explicitly
publisher-captioned figures (Opus p.37 and Fable p.60). The PDFs contain 67
`[Table ...]` captions plus those two figure grids, but that caption census only
corroborates the observed family; it does not prove semantic recall or stitching.

Natural false-positive controls include Fable pp.39-43 (dense nested
callout/transcript boxes), Opus pp.85-86 and p.93, and Risk p.172. They contain
many orthogonal vectors but produce no multi-cell ruled-grid proposal. Ten
multi-cell PDF structure-tag claims visually resolve to chart legends, lists, or
quotes rather than semantic tables, so source tags are advisory only.

No natural sparse/unruled semantic table and no natural
"absent rule but keep adjacent cells separate" case was found in the reviewed
challenge/control set. That is a missing negative and blocks any claim of general
sparse-table support. It is not evidence that an absent rule always means merge.

## Failure boundaries

The exact baseline remains vulnerable to source mutations: deleting a single
separator silently coarsens a grid; shifting or splitting a half-edge can create a
phantom axis; and connectors can fuse neighboring regions while absorbing prose.
The experiment must fail closed when the raw and finder planes disagree, when
word ownership is ambiguous, or when geometry is asked to decide semantic role.

Production adoption remains blocked until mutation cliffs are guarded, a natural
absent-rule-keep-separate negative and sparse/unruled positives are bound, and the
source-first investigation succeeds on another producer and a second platform.

## Reproduce

From the repository root:

```sh
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python docs/experiments/13-table-candidate-shadow/grid-discovery/evidence/extract_grid_discovery_evidence.py \
  --source-output docs/experiments/13-table-candidate-shadow/grid-discovery/evidence/source-pages.json \
  --review-output docs/experiments/13-table-candidate-shadow/grid-discovery/evidence/review-manifest.json

uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/grid-discovery/evidence \
  -p 'test_*.py' -v
```

This experiment changes no production conversion, card, or website output.
