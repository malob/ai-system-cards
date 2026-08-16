# Source-grounded word-alignment evidence

## Verdict

This is a useful shadow test set, not production authority. Ten reviewed tables from
nine source pages provide 790 mechanically observed PDF words, 274 reviewed semantic
cell ranges, eight source-supported spans, and seven natural full-rule
keep-separate controls. The set is strong enough to test whether typed alignment
repairs the known p.52, p.53, p.56, and p.78 failures without disturbing accurate
tables. It is not strong enough to authorize a general missing-rule merge: the
review found **no natural current-corpus case where a header boundary rule was absent
but the source still required two separate cells**.

Nothing here imports production table code or changes a card, generated section, or
site output.

## Authority boundary

The archived PDF is source truth, but not every field in the fixture is a mechanical
fact:

- PyMuPDF mechanically observes source words, word boxes, page-wide ordinals,
  stable block/line/word identities, style spans, links, punctuation, rulings, and
  source hashes.
- The declared Docling table box, shape, and table index are **candidate-conditioned
  locator context**. They determine which grid is being tested; they do not prove
  that grid.
- The cell ranges are **human-reviewed source-topology adjudications**, checked
  against the PDF geometry and page renders. They are test labels, not a production
  lookup table and not mechanically self-authorizing PDF truth.
- Cell text is then selected mechanically from exact PyMuPDF words inside each
  reviewed range. No agent retyped table content.

The artifact includes every page word whose bounding box has positive-area overlap
with the source grid envelope. Center position affects the expected status, never
whether the word is visible to the test. A regression reopens all nine source pages
and proves that no overlapping word was omitted.

## Cases

| Case | Role in the test set |
| --- | --- |
| Opus p.52 table 0 | Positive: fully ruled 6x3 numeric table with widespread proposal misjoins. |
| Opus p.53 table 0 | Positive nearest-family control: regular source geometry with body-cell rotation in the proposal. |
| Opus p.56 table 0 | Mixed: a source-supported `Model` rowspan plus one adjacent numeric misjoin. |
| Opus p.56 table 1 | Hard positive diagnosis: `API,` belongs in the adjacent API header, but the candidate also has unrelated gap/row assignment damage. The current fail-closed aligner blocks the whole table before changing either problem. |
| Risk p.78 table 0 | Positive: fully ruled 6x3 table whose proposal cyclically shifts every body row. |
| Risk pp.79-80 | Natural no-change controls: two accurate fragments of one multipage logical table. |
| Fable p.20 table 0 | Natural span control: deterministic rich-proposal page with two long body rowspans. |
| Fable p.94 table 0 | Natural nearest control for p.95: same six-column grammar, with both two-row model labels already represented as spans. |
| Fable p.95 table 0 | Mixed: two source-supported topology repairs, including a model label whose words cross the internal row boundary. |

All relevant page renders were visually checked in addition to the exact geometry.
The fixture contains 16 words whose bboxes cross an internal grid edge. These are
not outer-edge ambiguities: they largely sit in cells that genuinely span the crossed
edge. A correct aligner must resolve them through the reviewed/candidate span rather
than mark them ambiguous merely because their ink crosses an atomic slot boundary.

The complete overlap census found zero natural words with a bbox overlapping the
outer grid while its center was outside or exactly on an interior boundary. The
fixture says that explicitly through empty `overlap_controls`; synthetic boundary
and outside cases remain necessary model tests. Internal bbox crossings are a
different class and do not fill that evidentiary gap.

## Text-conservation trap

Fable p.94 exposes why alignment must move associations, not rewrite tokens.
PyMuPDF's word API returns `4.610` as one word, while its style spans retain ordinary
`4.6` plus superscript footnote reference `10`. The fixture carries both levels.
Similarly, four linked word occurrences and all punctuation/style evidence stay
attached to their exact source word IDs.

An aligner may use this evidence to decide which typed cell owns a word. It may not
silently normalize, split, strip, or regenerate that word. Inline style, links, and
footnote handling remain separate transforms with their own evidence.

## Adopt / kill tests

Continue the typed approach in shadow only if the alignment slice:

1. accounts for every selected source word exactly once as assigned, ambiguous, or
   outside, while preserving page-wide ordinal and stable source ID;
2. produces assignments compatible with all 274 reviewed cell associations (each
   raw candidate range is a subrange of its reviewed range), and reproduces the
   p.95 associations exactly after the already-proven topology-first merge;
3. produces the reviewed p.52, p.53, p.56, and p.78 associations without unresolved
   source-word statuses while leaving the Risk pp.79-80, Fable p.20, and Fable p.94
   controls unchanged (the current replay does not meet this bar for p.56 table 1);
4. treats all 16 internal bbox crossings consistently with the semantic spans;
5. conserves word text, bbox, punctuation, styles, links, and superscript evidence;
   and
6. leaves topology as a separately named transform: even if a future aligner fully
   resolves p.56 table 1, its observed lower `Model` cell must remain topology-blocking
   unless a separate source-grounded rule explicitly permits an observed-but-empty
   lower cell.

Kill or redesign the slice if it drops bbox-overlapping words, renumbers page
ordinals, mutates text while assigning it, needs the hand-reviewed expected ranges at
runtime, or makes an internal crossing ambiguous even when every crossed slot belongs
to one span.

Do not generalize the missing-rule topology rule yet. The seven natural
keep-separate controls all have full source rules; they are genuine negatives for the
action, but they do not answer the harder absent-rule negative. The eight natural
missing-rule observations in this set all support spans. Absence of a counterexample
in one publisher family is not proof of universal safety.

In particular, the current alignment transform does **not change p.56 table 1 at
all**. Its all-or-nothing policy first encounters three source words, `88% (± 5%)`,
in an adapter-gap slot at `r4-5:c1-2` and blocks the table as unresolved. The source
diagnosis remains useful: `API,` belongs in the adjacent header, and a future aligner
capable of resolving the complete table would remove that payload conflict. Even
then, the lower `Model` cell would retain its Docling-observed identity and
`adapter_generated=False`, so the prior topology transform would still refuse to
treat it as an adapter gap. An observed-empty topology rule needs separate
justification and controls; this evidence slice does not add one.

## Reproduce

Regenerate the source-bound artifact:

```sh
PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python docs/experiments/13-table-candidate-shadow/word-alignment/evidence/extract_source_evidence.py \
  --output docs/experiments/13-table-candidate-shadow/word-alignment/evidence/source-word-evidence.json
```

Run the artifact/source census and contract tests:

```sh
PYTHONDONTWRITEBYTECODE=1 \
uv run --offline --python 3.12 --with 'pymupdf==1.28.2' \
  python -m unittest discover \
  -s docs/experiments/13-table-candidate-shadow/word-alignment/evidence \
  -p 'test_*.py' -v
```

Result on 2026-08-16: 5/5 tests passed. The 448,460-byte canonical artifact has
SHA-256 `22e2fcb220cd29f03ee1b299c22e05f34759919812a13990a6e40682b20365cc`.
It binds extractor SHA-256
`30dc7c6ff81d7bbfdfbcb48976075fec3c3930c29d045fdce526587897f9e5f8`
and the exact source SHA-256 for every case.
