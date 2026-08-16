# Source-word alignment shadow slice

## Verdict

The fresh geometry model finds a real simplification, but it does **not** yet solve
the table pipeline. It deterministically repairs the demonstrated word rotations on
Opus pp.52-53, the isolated numeric split in Opus p.56 table 0, and every rotated
body row on Risk p.78. It leaves three known-correct tables byte-identical and fails
closed on three coupled or surface-sensitive cases. Keep the primitive in shadow;
do not migrate production yet.

This directory is isolated from `pipeline/`, `cards/`, and `site/`. Nothing here
changes canonical Markdown, the website, or accepted output. Accepted output was not
consulted as truth or as a label source.

## Fresh model

`word_alignment.py` uses two inputs only:

1. the sibling clean `TableCandidate` for immutable source/tool provenance and cell
   ranges; and
2. PDF-top-left grid edges plus every PyMuPDF word box with positive-area overlap
   against the full grid envelope.

It deliberately ignores Docling cell text and cell boxes while assigning. A word is
assigned only when its center is strictly inside the grid and its full box (with a
declared 0.75-point tolerance) is contained by exactly one typed cell. A word whose
box overlaps but whose center is outside is `outside_grid`; competing or crossing
cells are `ambiguous`; a unique generated placeholder is `adapter_gap`. Every word
gets exactly one explicit status, and all alternatives retain overlap fractions.

The optional text transform is all-or-nothing. It applies only when:

- every selected source word is assigned to a non-gap cell exactly once;
- the candidate and source have identical table-wide token multisets after NFC,
  removal of the source-evidenced U+200B zero-width space, and whitespace splitting;
  and
- replacing text preserves every source, tool, topology, bbox, role, fillable flag,
  adapter marker, and retained unknown field.

U+200B removal is comparison-only. Other format controls, including joiners and bidi
controls, remain significant. If an already-correct cell differs only by U+200B or
whitespace, its original bytes are retained. Every substantive change records
before/after text and the exact word IDs, page ordinals, boxes, and source addresses
that justify it. Ambiguity, an outside-center word, a word in an adapter gap, or
unequal token inventories returns the original candidate bytes.

## Independent source evidence

`evidence/source-word-evidence.json` is a ten-case, source-SHA-bound census with 274
human-reviewed cell-range labels and 790 mechanically extracted words. Candidate
boxes and shapes only locate the test; the labels are reviewed PDF-geometry
adjudications, not mechanically self-authorizing truth. Word text, boxes, page-wide
ordinals, style spans, punctuation, links, rulings, and overlap census come from the
archived PDFs through PyMuPDF 1.28.2.

The selection includes every positive-area bbox overlap, not only center-inside
words. Across these ten real cases it found no natural outer-edge center-outside word
or generic boundary-refusal control; the tests therefore retain synthetic versions
of both. Sixteen real words cross an internal grid line. Fourteen are correctly
contained by typed spanning cells; raw p.95 leaves the other two ambiguous because
its candidate topology is not yet merged.

The alignment artifact consumes that evidence rather than recomputing a second word
stream. It stores the independent artifact SHA-256, and tests check all ten case IDs,
source hashes, pages, shapes, edges, and word IDs. Tests establish that raw candidate
associations are compatible subranges of all 274 reviewed labels; exact equality is
asserted after the proven topology-first composition on p.95.

## Results

| Case | Source words | Result | Cell-text changes | Meaning |
| --- | ---: | --- | ---: | --- |
| Opus p.52 t0 | 58 | applied | 11 | Repairs the observed numeric/label rotations. |
| Opus p.53 t0 | 56 | applied | 15 | Adjacent same-family positive behaves the same way. |
| Opus p.56 t0 | 75 | applied | 2 | Repairs the isolated `99.95%` / `0.63%` split. |
| Opus p.56 t1 | 60 | blocked | 0 | Three `88% (± 5%)` words land in an adapter gap. |
| Risk p.78 t0 | 58 | applied | 15 | Repairs all five cyclically shifted body rows. |
| Risk p.79 t0 | 78 | no-op | 0 | Correct control; preserves typed `monitor,` instead of injecting a source ZWSP. |
| Risk p.80 t0 | 146 | no-op | 0 | Correct continuation control. |
| Fable p.20 t0 | 133 | no-op | 0 | Existing long rowspans remain intact. |
| Fable p.94 t0 | 63 | blocked | 0 | Source merges styled `4.6` + superscript `10` into `4.610`; token gate refuses. |
| Fable p.95 t0 | 63 | blocked | 0 | Raw topology leaves two boundary-straddling words ambiguous. |

Both fresh offline Docling extractions produced identical case bytes for all ten
cases. All 790 source words were assigned or explicitly blocked; none disappeared.
The four applied tables make 43 cell-text changes. The three no-op controls preserve
candidate bytes. The three blocked tables also preserve candidate bytes.

## Ordering and unsolved composition

The order of stages matters and is explicit:

- **Raw Fable p.95 -> alignment:** blocked. After the already-proven topology slice
  merges its two source-supported spans, the same alignment becomes a clean no-op and
  all reviewed word associations exactly match the merged cells.
- **Raw Opus p.56 table 1 -> alignment:** blocked all-or-nothing because a different
  row puts three words in an adapter gap. The transform therefore does not even
  partially move `API,`. More importantly, merely clearing that payload in a future
  complete resolver would leave its lower `Model` cell Docling-observed rather than
  adapter-generated; the existing topology transform would still refuse the merge.
  Reclassifying observed-empty cells as gaps would require a separate source-grounded
  rule and negative controls. This experiment does not smuggle one in.

Fable p.94 shows a second boundary: geometry assignment can be correct while source
and proposal tokenize a styled superscript differently. Character/glyph
reconstruction is a separate problem and is deliberately not folded into this rule.

## Proportionality

The full defensive model is 652 physical lines (580 nonblank); its two
decision-bearing functions are about 252 physical lines. That is much smaller than
porting the roughly 660-line legacy alignment core as decision logic, but the total
typed/provenance envelope is not yet a dramatic code reduction. The extractor and
artifact replay are experiment scaffolding, not production code to port. Production
adoption must replace this discovery harness with the already-planned locked artifact
bundle and show a net deletion of legacy behavior, not just parallel machinery.

## Adoption / kill criteria

Continue the shadow primitive because it fixes two document families with one pure
geometry rule, preserves the known-correct controls, is deterministic, and exposes
its refusals instead of guessing.

Do not adopt it in production until a follow-up can:

1. explain or safely compose the p.56 table-1 adapter-gap and observed-empty cases;
2. keep p.94's styled superscript out of assignment repair;
3. replay the locked bundle on a second platform;
4. regenerate all three cards and prove the exact intended output changes; and
5. demonstrate net complexity reduction against the legacy path.

## Reproduce

Offline unit and artifact replay (no Docling required):

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=docs/experiments/13-table-candidate-shadow/clean-model:docs/experiments/13-table-candidate-shadow/topology-slice:docs/experiments/13-table-candidate-shadow/word-alignment \
/Users/malo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python \
  -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/word-alignment \
  -p 'test_*.py' -v
```

Fresh two-run extraction:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --with docling --with pymupdf \
  python docs/experiments/13-table-candidate-shadow/word-alignment/extract_alignment_cases.py \
  --runs 2 \
  --output docs/experiments/13-table-candidate-shadow/word-alignment/artifacts/alignment-cases.json
```

Recorded versions are Docling 2.120.1, docling-core 2.91.0, and PyMuPDF 1.28.2.
The 138,187-byte alignment artifact has SHA-256
`c317522f77d91408bc71353695ad6afa490301dd39e7a3cf4d05643704f12e16`; its
independent source-word evidence has SHA-256
`22e2fcb220cd29f03ee1b299c22e05f34759919812a13990a6e40682b20365cc`.
The offline suite passes 12/12 tests.
