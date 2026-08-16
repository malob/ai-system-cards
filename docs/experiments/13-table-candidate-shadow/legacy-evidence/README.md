# Legacy table evidence

## Question

What must a clean table-candidate model explain without inheriting the design of
`pipeline/generate/tables.py`?  This directory turns the legacy implementation
into falsifiable evidence: exact raw cache candidates, accepted-output locators,
the legacy passes that currently change each candidate, and nearest-negative
controls where the same pass must stay inert.

This is deliberately **not** a porting plan.  A legacy transform names a failure
class and points to a counterexample; it does not prescribe the clean model's
representation or algorithm.

## Method

The capture was made at commit `4842ab1b8b90e55f22faf9fd728fc02b0f8a4a36`.

1. Scan all 98 non-empty candidates in the three local table caches through the
   exact per-page pass order in `tables.get_tables()`.
2. Select a minimal stratified set covering topology, cross-page behavior, and
   cell semantics.  Pair each positive with the closest available negative: the
   adjacent fragment, sibling table, or same-page table family.
3. Copy the selected raw `{bbox, html}` cache entries into `fixtures/`.  The
   production caches are ignored and have no Docling package/model/config
   metadata, so each fixture also binds the source PDF and whole source-cache
   hashes and marks the Docling version as unknown.
4. Bind every accepted result to a section path, zero-based table index, caption,
   source pages, exact current line locator, and table-substring SHA-256.
5. Replay the per-page legacy chain and five logical multi-page tails.  Record
   both raw and post-process hashes plus the exact passes that change bytes.
6. Validate all of the above mechanically with `validate_manifest.py`.

`inspect_legacy_passes.py` loads only the three table-merge helpers from
`run.py`'s AST for logical-table replay.  This avoids importing or running the
rest of the generation pipeline.  Neither script writes caches or canonical
Markdown.

## Fixture set

| Case | Positive evidence | Nearest-negative control | Main burden |
| --- | --- | --- | --- |
| `fable-rowspan-header-p95` | Fable p.95, Table 5.2.2.2.A | p.94 sibling | rowspans, colspans, covered subrows, header continuation |
| `fable-welfare-megatable-307-316` | Fable pp.307–316, Table 9.1.A | complete adjacent fragments pp.308/310 around truncated p.309 | sparse/unruled body, lost line, nine seams, paragraphs, glyphs |
| `opus-numeric-resegmentation` | Opus p.52 Table 4.1.1.A and p.56 Table 4.2.B | p.53 sibling and the other table on p.56 | misjoined cells, glued+empty split, rotation |
| `risk-overflow-and-links-78-80` | Risk pp.78/80 | p.79 fragment in the same family | surplus cells, reordered fragments, links, rotation |
| `risk-table-3-10a-113-114` | Risk pp.113–114, Table 3.10.A | pp.115–116: same seam-row merge, no list | row coalescence, lists, paragraphs, links, footnotes, bold/italic |
| `risk-ruled-table-6-6a-182-185` | Risk pp.182–185, Table 6.6.A | the case itself for truncation; p.309 is the positive | strong ruling, dense multi-page rows, links/labels, ownership guard |
| Auxiliary: `opus-capability-seam-148-149` | Opus pp.148–149, Table 8.1.A | contrasts with row-coalescing seams | fragments concatenate, but no logical row merges |

Together these span:

- strongly ruled, short-rule/filled-rectangle, and sparse/unruled-body tables;
- rowspan and colspan structure;
- glued, split, misjoined, truncated, overflowed, and rotated cells;
- simple concatenation versus true cross-page row continuation;
- paragraphs, real lists, links, footnote references, glyph restoration, bold,
  italic, and underline reconstruction.

The exact locators and hashes—not this prose summary—live in `manifest.json`.

## Result

The selected fixtures contain 29 unique raw candidates.  Some candidates are
referenced twice when they serve as both a positive and a negative control.
Every selected per-page replay currently matches `tables.get_tables()` exactly.
The validator checks 32 such manifest references, 13 accepted canonical tables,
and five logical multi-page shadows.

The most important archaeology result is negative: across all 98 candidates in
the three hash-bound current caches, neither `_merge_fragment_rows` nor
`_dedup_cascaded_cells` changes a candidate.  Their historical motivations may
have been real, but today's cache cannot reproduce them.  A clean implementation
must not port them on reputation alone.  We should first recover a historical raw
counterexample; otherwise they are retirement candidates.

Other passes remain demonstrably load-bearing:

- `promote_split_rowspan` fires on Fable p.95 but not its p.94 sibling;
- `extend_truncated_cells` fires on Fable p.309 but not pp.308/310, and must
  remain inert on Risk pp.182–185 after that table exposed a cross-row ownership
  failure;
- `resplit_misjoined_cells` fires on Opus p.52 but not p.53;
- `split_glued_cells` fires in the second p.56 table but not the first;
- `merge_overflow_cells` fires on Risk pp.78/80 but not p.79;
- Table 3.10.A changes under both cross-page row coalescence and final list
  construction; the pp.115–116 control coalesces a row but correctly constructs
  no list.

These discriminations are stronger requirements than “produce the current HTML”:
they state where a repair is allowed to generalize and where it must stop.

## Replay

Run the full validation from the repository root with Python 3.12:

```sh
uv run --python 3.12 python \
  docs/experiments/13-table-candidate-shadow/legacy-evidence/validate_manifest.py
```

Inspect one fixture's pass trace:

```sh
env CARD=anthropic/claude-opus-5 uv run --python 3.12 python \
  docs/experiments/13-table-candidate-shadow/legacy-evidence/inspect_legacy_passes.py \
  --fixture docs/experiments/13-table-candidate-shadow/legacy-evidence/fixtures/opus-cache-pages.json \
  52 53 56
```

Inspect a complete logical table:

```sh
env CARD=anthropic/risk-report-2026-08 uv run --python 3.12 python \
  docs/experiments/13-table-candidate-shadow/legacy-evidence/inspect_legacy_passes.py \
  --logical \
  --fixture docs/experiments/13-table-candidate-shadow/legacy-evidence/fixtures/risk-cache-pages.json \
  113 114
```

All selected cases can be replayed **without regenerating Docling** because the
raw flattened candidates are in the fixtures. Exact legacy post-processing also
needs the matching PyMuPDF oracle cache. If that ignored cache is absent, it can
be mechanically regenerated from the committed, hash-bound PDF without invoking
Docling; the validator still checks fixture and canonical hashes and reports the
post-processing replay as skipped. Fixture post-processing does not require the
ignored full table cache. When that complete cache is present and matches its
recorded hash, the validator additionally checks byte equality with production
`get_tables()`; otherwise only that extra production-equivalence comparison is
skipped.

## Boundaries

- The legacy cache retained only a bbox and exported HTML.  These fixtures cannot
  recover Docling's discarded cell/span/provenance objects and therefore are not
  input fixtures for the clean typed adapter.  They are behavioral evidence and
  comparison targets.
- Accepted HTML is a migration baseline, not source truth.  A shadow difference
  must be classified against the PDF rather than rejected automatically.
- The cache snapshots are exact but provenance-incomplete: the Docling version,
  model artifacts, and conversion options were never recorded.  The clean-model
  experiment must record those facts for its own candidates.
- The table-local pass tracer does not reproduce later heading-target resolution
  and serialization.  Consequently the logical-shadow hashes are separately
  bound and are not asserted equal to canonical-table hashes.

## Conclusion

Use the old pipeline as a counterexample mine, not as a scaffold.  A fresh model
has earned adoption only when it explains these positives, respects these
nearest-negative controls, and makes the repair boundaries more local and
legible than the present ordered HTML pass chain.
