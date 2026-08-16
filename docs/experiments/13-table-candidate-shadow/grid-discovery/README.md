# Candidate-independent ruled-region census

## Decision

**Retain the source census; kill the parallel grid-discovery model.** Independent
review scored the complete slice **7/12** and rejected both a shadow-model milestone
and production adoption. The model, its synthetic tests, replay builder, and replay
artifact are not committed. The retained material is limited to the
[candidate-free source evidence](evidence/README.md), its tests, and this decision
note.

This result changes no production converter, canonical card, site artifact, release
gate, or website output.

## What the retained evidence establishes

Pinned PyMuPDF 1.28.2
`find_tables(strategy="lines_strict", use_layout=False)` and a distinct
PyMuPDF-derived graph over raw stroked `l` segments inspect the archived PDFs without
reading Docling table candidates, accepted Markdown, legacy HTML, reviewed cell
labels, or case-specific IDs. They are separate representations from one observer
library, not independent parsers.

Across all **696 pages**, that source-only census records:

- **98 multi-cell ruled regions**: 40 Fable, 27 Opus, and 31 Risk Report;
- **77 one-cell vector boxes** kept as natural non-grid controls;
- **13,607 source-word occurrences** assigned exactly once inside the 98 regions;
- **1,774 outer atomic boundary slots** and **3,326 present internal boundary
  slots** with exact raw-rule coverage measurements; and
- 143 absent-rule internal adjacencies represented as merges rather than silently
  treated as separate cells.

The source and review planes are physically separate and hash-bound. The retained
`source-pages.json` SHA-256 is
`1775484321573f10691ccd246c21599b197f8f34e2e64e623e0886a77e97e8a1`; the
source-bound `review-manifest.json` SHA-256 is
`4b2c064dc8608ebf25948daa9cfe926dd811d28c6ab29bcc3ed7012211c40818`.
Geometry is reported only as a **ruled region**: it cannot decide semantic table
versus figure, as confirmed by the two publisher-captioned figure grids in this
family.

## Why the model was killed

The census is complete only for the observed ruled family. The corpus contains no
natural sparse or unruled table positive and no natural case where an absent rule
must nevertheless keep adjacent cells separate. All three PDFs were emitted by the
same Google Docs/Skia producer family and replayed on only one platform.

Those are load-bearing gaps. If a separator is actually deleted from the PDF, the two
PyMuPDF-derived representations can agree on a silently coarsened topology. If a
connector is added, both can agree on a fused topology that absorbs intervening
prose. Blocking materialization is honest, but it does not recover the missing truth.

The full pre-reduction slice added 3,319 Python lines and about 2.9 MB without
deleting production code or changing output. The killed model, synthetic tests,
builder, and replay were removed; the retained evidence boundary is 1,662 Python
lines and about 2.8 MB. Its score was:

| Criterion | Score |
| --- | ---: |
| Source independence | 2/2 |
| Current-corpus completeness and natural-negative/sparse safety | 1/2 |
| Immutable source/review planes | 1/1 |
| Deterministic, hash-bound, label-free replay | 1/1 |
| Mutation robustness | 1/2 |
| Portability and different producer | 0/1 |
| Word conservation and fail-closed materialization | 1/1 |
| Proportionality and net legacy deletion | 0/2 |
| **Total** | **7/12** |

## Next discriminator

Do not elaborate another grid model on this corpus. First bind a genuinely different
PDF producer with sparse or unruled table positives and an absent-rule-but-separate
negative. Then test the smallest source-only detector against those cases. If that
evidence does not support a compact, fail-closed rule with measured net production
deletion, keep the existing HTML representation and refactor the legacy table helpers
locally.

## Reproduce retained evidence

Run only the retained nine-test source-evidence suite:

```sh
PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/grid-discovery/evidence \
  -p 'test_*.py' -v
```
