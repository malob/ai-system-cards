# Docling candidate reproducibility probe

This directory tests a prerequisite for the shadow table experiment: can the rich
Docling table proposal be serialized and replayed deterministically before any
project repair transforms run?

It is intentionally isolated from `pipeline/generate/tables.py`. It neither reads
nor writes production caches, canonical sections, or site output.

## Why this exists

The production cache currently stores only this for each detected table:

```json
{"bbox": [72.0, 120.0, 540.0, 680.0], "html": "<table>...</table>"}
```

Across the three cards, the caches contain 98 table entries and every entry has
exactly those two keys. They carry no source hash, extractor version, effective
configuration, model revision, schema version, or typed cell data. Because the
caches were produced by an unpinned `uv run --with docling` command at different
times, the exact environment that produced each existing cache cannot be recovered
from the artifact itself.

Docling's public `TableData` model is directly JSON-serializable and retains:

- row and column count plus table orientation;
- each cell's row/column interval and row/column span;
- cell text, bbox, header/section/fillable roles;
- optional rich-cell references; and
- table-level page, bbox, and character-span provenance.

That is enough to preserve the extractor's proposal without adopting Docling as
truth or as the project's permanent schema.

## Binding contract

The probe's artifact binds a candidate to:

1. full source-PDF SHA-256 and 1-based source page number;
2. the exact one-page mini-PDF recipe and resulting mini-PDF SHA-256;
3. package versions for Docling, its schema/model/parser packages, PyMuPDF,
   RapidOCR, and relevant numerical/model runtimes;
4. the SHA-256 of the experiment extractor/serializer implementation itself;
5. the complete effective PDF pipeline options, including option class/kind,
   layout model, TableFormer mode/cell matching, resolved device, and OCR option;
6. the DoclingDocument version and a hash of the complete TableData JSON schema;
7. the pipeline option, global `DOCLING_ARTIFACTS_PATH` setting, initialized
   `pipeline.artifacts_path`, and Docling's priority choice among them;
8. the model directories/files exposed by the *initialized* layout, TableFormer,
   and OCR stages, matched fail-closed to their repository/config identities;
9. a canonical manifest of those exact layout/TableFormer directories and hashes
   of the three actual RapidOCR checkpoint files plus its recognition dictionary;
   and
10. initialized stage classes/options, including the OCR engine that `auto`
   actually selected in this runtime.

The model binding deliberately does not call `snapshot_download` independently or
look up a revision that Docling was expected to use. For the default flow it reads
the loaded Transformers model path, TableFormer's initialized
`tm_config.model.save_dir`, and RapidOCR's initialized reader configuration. A
Hugging Face directory must match exactly one
`models--ORG--REPO/snapshots/COMMIT` identity. With an explicit artifacts root it
must match Docling's repo-scoped layout (or TableFormer's documented deprecated
unscoped layout). An unknown engine, missing file, ambiguous loaded path, stale
global setting, or identity mismatch is a probe failure, not incomplete metadata.

The candidate and complete envelope get separate canonical hashes. Paths identifying
the initialized artifact roots are retained deliberately, alongside byte manifests;
the recorded envelope is therefore host-specific as well as content-bound.
Timestamps, durations, and log output are excluded. Canonical JSON is UTF-8 with
sorted object keys, significant list order, no insignificant whitespace, and no
NaN/Infinity.

Recording provenance is not the same as pinning it. A production implementation
must also resolve exact package versions from a checked lock, fetch models by
immutable revision (or a verified artifact bundle), verify the recorded artifact
manifest before inference, and reject rather than reuse a cache whose binding
differs.

## Run

The unit tests need only the standard library:

```sh
python3 -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/reproducibility \
  -p 'test_*.py'
```

The live probe deliberately requires an already-cached environment and models.
The offline flags prevent it from silently downloading or following a moved model
branch:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
uv run --offline --with docling --with pymupdf \
  python docs/experiments/13-table-candidate-shadow/reproducibility/docling_repro_probe.py \
  --source cards/anthropic/claude-fable-5/source.pdf \
  --page 20 --runs 2 \
  --output docs/experiments/13-table-candidate-shadow/reproducibility/probe-result-p20.json \
  --summary-output docs/experiments/13-table-candidate-shadow/reproducibility/probe-result-summary.json
```

Each run creates a new mini-PDF and a fresh `DocumentConverter`. A successful
result requires equality at all three boundaries: mini-PDF bytes, raw rich
candidate, and the complete provenance envelope. On a mismatch, all variant
artifacts are retained in the report for structural diffing.

`probe-result-p20.json` is the canonical complete report. The smaller
`probe-result-summary.json` is generated from it by the same command and carries
the full report's canonical SHA-256. A unit test re-derives the checked summary,
so it cannot become an untraceable hand-copied account of the result.

The raw candidate uses Pydantic's `exclude_computed_fields=True` and rejects the
serialization if `TableData.grid` is still present. `grid` is a computed rectangular
view that repeats merged cells; the declared `table_cells` collection is the
lossless extractor proposal and avoids binding the artifact to a redundant
Docling implementation detail.

The initial live run reproduced production's default `mini.save(path)` behavior.
The two mini-PDF SHA-256 values differed despite identical source/page/recipe;
their rich candidate hashes were nevertheless identical. PyMuPDF 1.28.2 exposes
two relevant settings. `reproducible=True` alone still produced different file
IDs; `save(..., reproducible=True, no_new_id=True)` produced byte-identical
mini-PDFs in an isolated two-build check, so the experiment uses both explicitly.
This is a small but real extraction-boundary defect: without these settings,
binding the candidate to the exact mini-PDF bytes creates noisy cache invalidation
even when inference is stable.

## Scope and next decision

One same-machine, same-version two-run match proves only warm deterministic replay
for that page. It does not prove determinism across CPU architectures, operating
systems, thread counts, dependency builds, or future model/package versions. The
useful next ladder is:

1. two fresh-process runs on one representative table page;
2. repeat on hard merged, rotated, and multipage fragments;
3. replay in a clean locked environment on the same machine;
4. replay on CI/Linux with explicitly pinned CPU/thread settings; and
5. make drift explicit by diffing typed candidates under an intentional version
   or model bump.

Do not make this a production cache until the clean table model experiment decides
which raw Docling fields belong in the project-owned candidate and which remain
tool-specific evidence.

## First result (2026-08-16)

The offline two-run probe on Fable source p.20 passed all three equality checks
after making the mini-PDF wrapper deterministic:

| Boundary | Two-run result |
| --- | --- |
| one-page input PDF | identical |
| raw rich Docling candidate | identical |
| full source/tool/config/model/schema-bound envelope | identical |

The candidate is one 6×3 table containing 16 unique cells, all with cell bboxes,
three structural column headers, and the two expected 2×1 merged cells. No cell
used `RichTableCell.ref`. Cell bboxes use `TOPLEFT`, while the table-level
provenance bbox uses `BOTTOMLEFT`; its `page_no` is the mini-PDF page 1 rather
than source page 20, and its `charspan` is `[0,0]`. The project adapter therefore
must remap page identity, normalize coordinate origins, and must not treat
`charspan` or rich refs as universally populated.

The live environment resolved unpinned `docling` to 2.120.1 with
`docling-core` 2.91.0, TableFormer accurate/cell-matching mode, Heron layout, and
Auto OCR selecting RapidOCR's torch backend. The loaded Heron path matched the
requested `main` repository identity at immutable commit `8f39ad3c…`.
TableFormer's actual initialized `save_dir` matched the `docling-models` snapshot
at `fc0f2d45…`; that claim no longer depends on a separately resolved assumed
revision. The three checkpoint filenames and byte hashes come from the initialized
RapidOCR config. Exact package versions, model manifests/file hashes, schema hash,
candidate hash, and envelope hash are in the canonical
[`full report`](probe-result-p20.json); the review-sized values are in its derived
[`summary`](probe-result-summary.json).

The full raw table now contains only the declared `num_rows`, `num_cols`,
`orientation`, and 16 unique `table_cells`; the redundant computed `grid` is absent.
The second two-run execution again matched the mini-PDF, candidate, and complete
envelope. Its effective artifact source was `library_defaults`: the pipeline option,
global setting, and initialized `artifacts_path` were all null, while relevant
global performance/inference settings and the cache root were recorded explicitly.

This is a positive feasibility result, not yet a portability claim. It shows that
we do not need to flatten `TableData` to HTML to obtain a compact deterministic
artifact. It also exposes three things the productionized experiment must make
explicit: deterministic mini-PDF creation, immutable model revision/artifact
verification, and an explicit OCR/device policy rather than runtime-dependent
`auto` selection.
