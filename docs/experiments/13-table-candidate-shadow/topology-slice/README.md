# Typed topology vertical slice

## Verdict

There is one narrow, source-justified correction worth retaining in shadow:
extend an existing typed header through the immediately lower adapter gap when
the PDF omits that part of the row rule. The transform made three merges on two
pages. It conservatively refused a fourth source-supported span because Docling
placed `API,` in the would-be gap. That false negative does not justify
production adoption or a general table-repair subsystem.

This slice is isolated here. It imports the sibling `clean-model` adapter at
runtime and does not edit it. It does not import production table code or write
production, canonical, or site output.

## Fresh hard-set evidence

Each source page was copied to a reproducible one-page PDF and extracted twice
offline with Docling. The actual public `TableData` object was adapted to the
typed clean model. PyMuPDF `Page.get_drawings()` supplied source-derived vector
rulings and `Page.get_text("words")` supplied ordered word centers from the
original PDF. This geometry path is still candidate-conditioned by Docling's
table bounding box and grid dimensions. It is shadow-generator evidence, not an
independent verification authority.

| Case | Typed tables | Topology result | Typed/PDF text-slot mismatches |
| --- | --- | --- | --- |
| Opus p52 | `6x3` | No-op: every row rule is complete | `11 -> 11` |
| Opus p56 | `7x5`, `7x3` | Merge `Model` in table 0; source supports the same span in table 1, but the transform conservatively blocks because Docling put `API,` in lower col0 | `2 -> 2`, `11 -> 11` |
| Risk p78 | `6x3` | No-op: every row rule is complete | `15 -> 15` |
| Risk p79 | `4x5` | No-op | `0 -> 0` |
| Risk p80 | `10x5` | No-op | `0 -> 0` |
| Fable p95 | `8x6` | Merge `Model` over two columns and `Claude Opus 4.8` over two rows | `2 -> 0` |

The p52, p56-table-1, and p78 errors are word-to-cell assignment errors. The PDF
supports a `Model` rowspan in p56 table 1, but this topology-only transform
cannot safely remove its observed lower cell. That is a conservative false
negative caused by upstream assignment, not source evidence against the span.
No genuine real source-negative was found in this hard set. Risk pp79-80 are
internally correct segments of a multipage logical table; cross-page stitching
is deliberately outside this slice.

Accepted outputs were consulted only as migration baselines. Fable's accepted
output agrees with the `Claude Opus 4.8` row span. Its `Model` header and Opus's
`Model` header instead retain explicit empty second-row cells, although the PDF
rulings support a vertical span. That semantic difference needs renderer and
migration review; the accepted output was not treated as source truth.

## The single transform

`extend-header-through-adapter-gap-at-missing-rule/v1` proposes a one-row
extension only when all of these are true:

1. Source SHA-256, one-based page, orientation, and grid dimensions match.
2. The upper cell is an existing typed header and ends at the boundary.
3. The PDF has no horizontal rule across the full header width but does have a
   rule on another column at the same boundary, proving a real row boundary.
4. Every lower slot is a distinct `1x1` adapter-generated gap covering exactly
   the upper cell width.
5. Ordered source words across the extended rectangle equal the existing typed
   header payload after whitespace/format-character normalization.
6. The proposal does not overlap another proposal.

Ambiguity records a `blocked` decision and leaves the candidate byte-identical.
Successful changes use `dataclasses.replace`; the clean-model constructor then
rechecks the total grid. Assertions preserve source/tool provenance, all
non-target cells, and every header field other than ID and row extent.

## Proportionality

Only three frozen records are introduced:

- `RuleEvidence` binds the minimum independent geometry needed by the rule:
  grid edges, horizontal line segments, ordered word centers, source identity,
  page, extractor, and tolerance.
- `Decision` makes each merge or refusal inspectable instead of hiding a
  heuristic branch.
- `Reconciliation` returns the immutable candidate with input, evidence, and
  output hashes plus decisions.

`reconcile_missing_header_rules` is the only mutation rule and is pure. The
extractor is a fixed six-page replay harness, not a reusable extraction layer.
The artifact intentionally omits full candidates and raw geometry: their
canonical hashes bind them, while only rule masks, decision-relevant cells, and
up to three mismatch examples remain for review. It also records SHA-256 hashes
of the clean model, transform, and extractor; tests compare those hashes with
the current files so stale evidence fails closed.

## Adoption / kill evidence

Adopt only for continued shadow evaluation of the exact preconditions above.
The transform realizes Opus p56 table 0 and the two Fable p95 spans; all preserve
payload and validate against the typed total grid. Opus p56 table 1 is a known
false negative: the source supports the same `Model` rowspan, but the typed
candidate contains a misplaced observed `API,` cell and therefore fails the
adapter-gap precondition. Synthetic controls verify that a fully ruled boundary
is a byte-identical no-op and an observed lower cell fails closed. There is no
genuine real source-negative in this six-page set.

Kill production/canonical adoption for now. Three positive spans are too small a
sample; one real positive already depends on upstream word assignment; several
hard pages still contain unrelated slot errors; accepted-output header semantics
differ; and no cross-platform replay has been established. In particular, do
not generalize this into “merge across every missing rule” or add text
reassignment to this topology transform.

## Reproduce

Unit and artifact-contract tests (no extraction runtime required):

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model \
/Users/malo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python \
  -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/topology-slice \
  -p 'test_*.py' -v
```

Fresh two-run offline extraction:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --with docling --with pymupdf \
  python docs/experiments/13-table-candidate-shadow/topology-slice/extract_hard_set.py \
  --runs 2 \
  --output docs/experiments/13-table-candidate-shadow/topology-slice/artifacts/hard-set.json
```

Recorded versions are Docling 2.120.1, docling-core 2.91.0, and PyMuPDF 1.28.2.
The 13,555-byte canonical artifact is deterministic across both runs and has
SHA-256 `329128c4c388d40cd687aabca61c0127e8167a3be511419494f15e5a3eaedfc6`.
