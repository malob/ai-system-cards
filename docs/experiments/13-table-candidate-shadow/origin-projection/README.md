# Raw-rule origin/projection shadow

## Verdict

The missing three-plane abstraction is viable for this ruled-table hard set. One
order-independent resolver derives topology from raw PDF rulings, assigns raw PDF
word occurrences to those components, and only then compares the result with
immutable extractor claims. It resolves the coupled Opus p.56 table 1 and raw Fable
p.95 cases without calling the earlier topology and alignment transforms and without
mutating a candidate.

This is a strong shadow result, not a production adoption decision. The atomic grid
edges are still candidate-conditioned locator context, the selected corpus contains
no natural absent-rule/keep-separate negative, and the model deliberately blocks
text materialization for the p.94 styled-token boundary. Nothing here changes
`pipeline/`, `cards/`, `site/`, canonical Markdown, or the website.

## Commit and kill criteria

The slice was retained only if one generic resolver, with no case IDs or reviewed
cell ranges in its decision logic, could:

- derive all 274 reviewed ranges across the existing ten cases from raw horizontal
  and vertical line segments;
- associate all 790 source word occurrences exactly once by full-bbox containment;
- jointly derive the p.56 table 1 `Model` rowspan and `API, without a system prompt`
  ownership, while retaining Docling's wrong `API,` cell as an **observed** claim and
  its populated adapter slot as an **adapter-gap** claim;
- resolve raw p.95, preserve the three natural no-change controls, and retain p.94 as
  association-success/materialization-blocked;
- fail closed for sparse rules, nonrectangular components, boundary words, and
  incomplete semantic materialization; and
- keep every candidate byte-identical with exact source/evidence/tool hashes.

All of those criteria pass. The slice would have been killed if it needed an ordered
repair stack, runtime access to the reviewed labels or accepted Markdown, case-local
ranges, silent word loss, origin rewriting, or partial output after a blocker.

Production adoption has a higher bar and does **not** pass yet: locked
cross-platform replay, another PDF producer, a natural absent-rule negative,
style/link-aware serialization, and demonstrated net production-code reduction are
still missing.

## The three planes

`origin_projection.py` defines frozen values for:

1. **Raw source observations:** source identity/hash, every selected PyMuPDF word and
   its full feature payload, candidate-conditioned atomic edges, and raw horizontal
   and vertical line segments.
2. **Extractor claims:** the complete typed Docling candidate, including retained
   non-text payload and immutable `observed` versus `adapter_gap` origin.
3. **Derived projection:** rectangular rule-connected components, occurrence-ID
   associations, optional mechanically joined text, and explicit claim conflicts.

The resolver requires a complete outer border and at least one observed rule segment
somewhere on every internal row and column boundary. It unions adjacent atomic slots
only where the corresponding raw segment is absent, rejects nonrectangular connected
components, and then uses 0.75-point full-bbox containment to associate words. This
single connected-component calculation handles rowspans and colspans together; its
result cannot depend on whether a topology or text pass runs first.

Reviewed source ranges appear only in tests. They are not constructible model input
and cannot authorize a projection. The PDF word feature dictionaries are retained
byte-for-byte through canonical JSON; p.94's `4.6` plus superscript `10` therefore
associates successfully but blocks all table text materialization instead of being
flattened to `4.610`.

`no-op` has a deliberately narrow meaning: source-derived topology and normalized
plain-text payload agree with the extractor claims. It does not adjudicate candidate
header roles or bboxes, nor does it prove style/link rendering. Style and link facts
remain transitively attached to stable source word IDs, but this experiment does not
serialize them; that alone blocks production adoption.

## Results

| case | result | mechanically derived cells | effect |
| --- | --- | ---: | --- |
| Opus p.52 | proposed | 18 | exposes 11 candidate topology/payload conflicts |
| Opus p.53 | proposed | 18 | exposes 15 conflicts |
| Opus p.56 table 0 | proposed | 32 | resolves the rowspan, colspans, and numeric ownership together |
| Opus p.56 table 1 | proposed | 20 | resolves coupled topology/ownership; retains one observed-empty and one occupied-gap contradiction |
| Risk p.78 | proposed | 18 | exposes 15 rotated-cell conflicts |
| Risk pp.79-80 | no-op | 20 / 50 | natural correct controls remain unchanged |
| Fable p.20 | no-op | 16 | existing rowspans remain unchanged |
| Fable p.94 | blocked | 41 | all 63 words associate; styled token prevents materialization |
| Fable p.95 | proposed | 41 | raw rules jointly recover the two missing spans |

Risk p.115 supplies a source-only true-blank control: zero source-word overlaps and
four present boundaries classify the top-left slot as `true_blank`. No typed candidate
fixture exists for that page, so extractor origin remains explicitly unknown; the
control cannot say whether Docling observed an empty cell or the adapter created one.

The selected cases still contain no natural source-empty slot with an absent boundary
that must remain separate. The resolver therefore refuses wholly missing internal
boundaries rather than generalizing the observed span rule to sparse or unruled
tables.

## Proportionality

The root slice contains 792 lines of model/types, 250 lines of artifact loading and
binding, and 410 lines of tests. The actual rule/association/overlay kernel begins at
`_rule_present` and is about 309 lines; the rest is frozen schemas, canonical hashing,
and validation. The evidence sub-slice adds 678 extractor and 209 test lines. The
compact replay is under 9 KB and references, rather than duplicates, the existing
source-word and candidate artifacts.

This is not yet net code reduction against production. Its value is architectural:
one derivation replaces the *conceptual need* for ordered topology-then-text repairs
and makes origin contradictions first-class. A production spike must shrink the
adapter/provenance envelope and delete more legacy decision logic than it adds.

## Reproduce

The compact replay consumes only checked-in artifacts:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 \
  docs/experiments/13-table-candidate-shadow/origin-projection/build_replay.py

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/origin-projection \
  -p 'test_origin_projection.py' -v
```

The source-reopening evidence suite is separately documented in
[`evidence/README.md`](evidence/README.md). The root suite passes 12/12 tests; the
evidence suite passes 10/10. Exact artifact and implementation hashes are recorded in
`artifacts/origin-projection-replay.json`.
