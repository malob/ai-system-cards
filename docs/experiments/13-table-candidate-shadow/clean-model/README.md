# Clean-room TableCandidate shadow model

## Question

Can a small, project-owned immutable model preserve Docling's public table grid and
the provenance Docling leaves outside `TableData`, while producing deterministic,
reviewable JSON and changing no production behavior?

This is the clean-model half of experiment 13. It is intentionally shadow-only:
[`table_candidate.py`](table_candidate.py) imports neither Docling nor any production
pipeline module, and nothing in `pipeline/`, `cards/`, or `site/` imports it.

## Evidence boundary

The adapter was designed from the public `docling-core` shape paired with the
project's recorded Docling 2.100.0 probe (`docling-core` 2.80.0), not from the
production table implementation. The public fields inspected were:

- `TableData`: `table_cells`, `num_rows`, `num_cols`, and `orientation`;
- `TableCell`: optional `bbox`, half-open row/column offsets, explicit row/column
  spans, `text`, `column_header`, `row_header`, `row_section`, and `fillable`; and
- `RichTableCell`: all `TableCell` fields plus `ref`.

An adapter smoke test instantiated the actual cached `docling-core` 2.80.0
`TableData`, `TableCell`, and `BoundingBox` classes and passed that object directly
to this dependency-free adapter. The normalized 2-by-2 merged-header grid and its
diagnostic logical payload matched the public fields. A second actual-object smoke
used `RichTableCell` and proved that its normal model-dumped `ref`
(`{"cref":"#/texts/0"}`) and persisted by-alias form
(`{"$ref":"#/texts/0"}`) produce byte-identical candidates. The candidate's
canonical spelling is `cref`.

A separate live probe with Docling 2.120.1 / `docling-core` 2.91.0 on Fable source
p.20 found the same public field set. It produced a 6-by-3 `rot_0` grid with 16
unique plain `TableCell` objects, all cell bboxes populated in `TOPLEFT` coordinates,
three `column_header` cells, and no `RichTableCell.ref`, `row_header`, `row_section`,
or `fillable` values. Its two expected row merges were present. The containing
`TableItem` provenance instead used mini-PDF page 1, a `BOTTOMLEFT` table bbox, and
charspan `[0, 0]`. Therefore original-page remapping and coordinate conversion cannot
be inferred from `TableData`; they must be explicit upstream inputs.

## Method

[`table_candidate.py`](table_candidate.py) defines frozen, dependency-free
dataclasses for:

- source identity and one or more source regions, including source SHA-256, a
  caller-owned stable table key, physical page, bbox origin, and optional char range;
- extractor, data-model, model-artifact, and settings provenance;
- bboxes that retain their own coordinate origin;
- unique cells with stable IDs, exact text, half-open ranges, redundant checked
  spans, optional bbox/page, header roles, and fillability; and
- a total rectangular `TableCandidate` grid.

The candidate ID is a SHA-256 of schema version plus stable source identity. A cell
ID is that candidate ID plus its row/column range. IDs therefore survive input-order,
text, header-role, and bbox changes, while a topology range change deliberately
changes the cell ID. Stability depends on the caller supplying a durable `table_key`;
the adapter does not pretend Docling provides one.

The adapter reads either mappings or objects exposing Docling's public attributes.
It validates positive dimensions, exact span/range agreement, bounds, non-overlap,
and full grid coverage. A slot omitted from `TableData.table_cells` becomes an empty
1-by-1 `adapter_generated` placeholder. That marker is load-bearing: observed cells
and adapter completion are never conflated, and placeholders are excluded from the
diagnostic Docling payload.

All unknown JSON-valued Docling fields are retained in sorted canonical
`tool_fields`. They are provenance and forward-diff evidence only; no unknown field
can silently become a header, span, bbox, or other project semantic. The one explicit
external-schema normalization is known `RichTableCell.ref`: Pydantic's field-name
`cref` and serialization alias `$ref` normalize to `cref`, while conflicting dual
values fail closed. Opaque and non-finite values also fail closed instead of being
stringified.

`TableCandidate.to_json()` uses UTF-8 text, sorted object keys, compact separators,
strict finite numbers, stable cell order, and one trailing newline. The
`diagnostic_docling_payload()` method demonstrates retention of the logical public
payload. It does **not** promise byte reconstruction or recreation of third-party
Pydantic objects: input cell order is canonicalized, enums become scalar values, the
computed `grid` projection is regenerated from cells, and placeholders are omitted.

## Tests

Run the dependency-free synthetic suite from the repository root:

```sh
python3 -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/clean-model \
  -p 'test_*.py' -v
```

Then run the local static checks:

```sh
ruff check docs/experiments/13-table-candidate-shadow/clean-model
ruff format --check docs/experiments/13-table-candidate-shadow/clean-model
```

The 15 synthetic tests cover:

- rowspan/colspan slot identity and a marked sparse-cell completion;
- exact range/span, bbox-origin, header-role, fillability, and Unicode-text retention;
- rejection of span mismatches, overlaps, out-of-bounds cells, and uncovered grids;
- explicit page selection for multi-region provenance;
- source/range-stable IDs under cell reordering and text drift;
- byte-identical canonical JSON under cell and mapping reordering;
- `RichTableCell.ref` and forward-field retention without semantic promotion;
- byte identity between object-style `ref.cref` and persisted `ref.$ref`, plus
  fail-closed disagreement handling;
- omission of adapter-generated gaps from the diagnostic Docling payload;
- frozen public state; and
- fail-closed behavior for opaque metadata and non-finite geometry.

Result on 2026-08-16: **15/15 passed**; `ruff check`, `ruff format --check`,
`py_compile`, and `git diff --check` also passed.

## Fields Docling does not supply here

`TableData` alone does not carry:

- source document identity or SHA-256;
- the original physical page after mini-PDF extraction, table-level bbox/charspan, or
  a stable source table ID;
- Docling, `docling-core`, model-artifact, or extraction-settings provenance;
- table- or cell-level confidence; or
- stable cell IDs.

`TableCell` has an optional bbox but no page number, raw source-span/token IDs,
cell-level charspan, or confidence. Its normal text field is a plain string.
`RichTableCell.ref` can point back into a larger `DoclingDocument`, but the table data
is not self-contained and does not natively retain this corpus's required inline
bold, link, and footnote-reference ranges inside cell text. The live p.20 probe used
only plain cells. Its `[0, 0]` table charspan is retained if supplied but is not
evidence of meaningful character provenance.

The project model makes those absences visible: source and tool provenance are
mandatory adapter arguments, absent model artifact labels remain an explicit empty
tuple, bbox origins remain per-box rather than being guessed into one coordinate
system, and forward fields remain untrusted metadata.

## Conclusion

**Viable for continued shadow testing, not viable as an authority or production
replacement yet.** The model is small enough to make Docling topology replayable and
reviewable, retains the public TableData semantics without trusting tool extensions,
and gives phase-7 generator experiments an immutable grid on which independent
mutations can operate.

It does not create independent table truth: the cells and topology still come from
Docling. It also does not close cold reproducibility, original-page remapping,
mixed-origin coordinate conversion, inline mark/source-span provenance, multi-page
stitch identity, or the corpus-level A/B question of whether a persistent grid
materially simplifies repairs. Those require the separate provenance/replay probe
and independent verifier-side topology experiment before any production adoption.

No production import, generated card, canonical Markdown, site output, or release
gate changed in this experiment.
