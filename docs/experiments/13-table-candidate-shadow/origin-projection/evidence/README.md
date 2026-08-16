# Source/origin/projection evidence

## Verdict

The raw-rule experiment is stronger than the previous hand-reviewed topology
slice, but still bounded. Across the same 10 tables, mechanically observed
horizontal and vertical PDF rule segments form rectangular connected components
that exactly reproduce all 274 reviewed source cell ranges. Full-word-bbox
containment with a 0.75-point tolerance assigns all 790 overlapping source words
to those derived ranges with zero ambiguous, outside, or wrong assignments.

That is evidence that these **fully ruled, candidate-located tables** can obtain a
source projection without feeding the reviewed ranges into the resolver. It is
not evidence that the grid envelope and atomic edges can yet be discovered
independently: those remain explicitly candidate-conditioned locator context.
Sparse or unruled tables remain out of scope.

Nothing in this directory changes production code, card content, accepted
Markdown, or the website.

## Three distinct layers

The compact manifest keeps three facts separate:

1. **Source observation:** hash-bound PDF words, bboxes, styles, and raw rule
   segments re-opened with PyMuPDF.
2. **Extractor claim:** the immutable typed Docling cell range, payload, bbox, and
   `adapter_generated` origin replayed from the preceding alignment artifact.
3. **Derived projection:** a source-grounded test label. It is review evidence,
   never a runtime lookup or mechanical authority.

This distinction matters on Opus p.56. Table 0 row 1 column 0 is an
adapter-created empty slot under a source-supported `Model` span. Table 1's same
atomic slot is an **observed** Docling cell containing `API,`, even though the
physical source slot is empty and the word belongs in the adjacent header. Source
emptiness does not retroactively turn an observed claim into an adapter gap.

## Minimal natural cases

| Case | What it distinguishes |
| --- | --- |
| Opus p.56 t0 r1c0 | Adapter-empty atomic slot inside a source-supported rowspan. |
| Opus p.56 t1 r1c0 | Observed nonempty extractor claim over a source-empty span slot; this is a misprojected payload, not a gap. |
| Opus p.56 t1 r1c1 | Adjacent natural keep-separate control: present rule plus source words `API, without a system prompt`. |
| Opus p.56 t1 r4c1 | Adapter-empty claim with real source words `88% (± 5%)`; adapter origin cannot authorize omission. |
| Fable p.94 t0 | Style trap: the word API reports `4.610`, while exact spans retain ordinary `4.6` plus superscript `10`. |
| Fable p.95 t0 | One source rowspan represented as an observed upper claim plus an adapter-created lower slot. |
| Risk p.115 t0 | True blank source-only control: zero overlapping words inside a cell bounded on all four sides. No typed candidate fixture exists, so this case is deliberately non-executable. |

Repeated `88%` tokens on Opus p.56 retain different source word IDs and page
ordinals. The evidence moves occurrences, not strings.

## Fail-closed boundary

The resolver is eligible only when the candidate-conditioned atomic grid has a
complete ruled outer envelope and every internal horizontal and vertical boundary
has at least one observed segment. Partial internal masks can then express spans.
A wholly absent internal boundary, missing outer side, nonrectangular component,
ambiguous word placement, or word outside every derived range must block.

All 10 current cases meet the ruled-eligibility condition. The suite removes a
whole internal horizontal boundary, a whole internal vertical boundary, and an
outer border in turn and requires all three mutations to fail closed.

There is still **no natural absent-rule-but-keep-separate negative** in this
corpus. The Risk p.115 true blank is useful precisely because it has all four
rules; it cannot justify treating every source-empty, absent-rule slot as a span.
Do not generalize that merge.

## Authority and compactness

The 41,135-byte artifact does not copy the preceding 448 KB word census or the
full candidate fixtures. It binds them by exact SHA-256, transitive case hashes,
candidate hashes, word IDs, and cell IDs. Regeneration reopens every referenced
PDF page, recomputes the complete bbox-overlap census, validates raw horizontal
and vertical rules, replays each typed candidate, and checks the exact locators.
Accepted or generated Markdown is never read.

Artifact SHA-256:
`37bdedacdaafdf77284c07ca39d88d350c40da89cb5cdec9b8a2634df1029a88`.
It binds extractor SHA-256
`c805e45015cf3dcd8cf4d2db8ef8d9ba501ad768595ba1d3f9702f44b93a1dc4`,
as well as
It binds source-word evidence SHA-256
`22e2fcb220cd29f03ee1b299c22e05f34759919812a13990a6e40682b20365cc`
and alignment-artifact SHA-256
`c317522f77d91408bc71353695ad6afa490301dd39e7a3cf4d05643704f12e16`.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model:docs/experiments/13-table-candidate-shadow/word-alignment \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python docs/experiments/13-table-candidate-shadow/origin-projection/evidence/extract_origin_projection_evidence.py \
  --output docs/experiments/13-table-candidate-shadow/origin-projection/evidence/origin-projection-evidence.json

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model:docs/experiments/13-table-candidate-shadow/word-alignment:docs/experiments/13-table-candidate-shadow/origin-projection/evidence \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/origin-projection/evidence \
  -p 'test_*.py' -v
```

Result on 2026-08-16: 10/10 tests passed.
