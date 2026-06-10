# Experiment 05 — mutation testing (D6): per-class verifier recall

**Question.** When a defect is *known* to exist (because we injected it), does
the verifier catch it? This turns "calibrated on history" into a number and
covers the censorship gap in the v1 corpus (D5/D6).

**Method.** [mutate.py](../../../pipeline/verifier/mutate.py) injects one
synthetic defect into a copy of the HEAD sections, runs the full invariant
suite, and counts a catch iff a flag of the expected invariant appears that was
not in the unmutated baseline. 8 mutations/class, seeded. Raw:
[results.json](results.json).

```sh
uv run --with pymupdf python pipeline/verifier/mutate.py --per-class 8
```

## Recall per class

| mutation            | invariant | recall      | misses explained                                  |
|---------------------|-----------|-------------|---------------------------------------------------|
| duplicate-paragraph | T1        | 8/8         |                                                    |
| drop-image          | F1        | 8/8         |                                                    |
| drop-fndef          | FN1       | 8/8         |                                                    |
| dup-marker          | P1        | 8/8         |                                                    |
| flatten-chip        | S2        | 7/8         | same-label chip nearby satisfies the ±1-page window |
| swap-words          | T1        | 7/8         | inside footnote-def text (see gap 2)               |
| drop-link           | L1        | **8→7/8***  | *after two fixes below; residual: footnote-def edge |
| delete-sentence     | T1        | 6/8         | inside footnote-def text (see gap 2)               |
| drop-bold           | S1        | 5/8         | table pages (S1's declared exclusion → TB1's layer) |

\* drop-link started at **3/8**; mutation testing exposed two verifier bugs,
both fixed in-session: (1) L1 compared URIs as a global *set*, so dropping one
instance of a repeated link passed — now count-based over the whole document;
(2) line-wrapped URLs produce multiple PDF annotations for one logical link —
the oracle now merges same-URI annotations per page (this had silently
inflated counts). Re-run: 7/8.

## Gaps exposed (the point of the exercise)

1. ~~L1 set-vs-count~~ — **fixed** (above).
2. **Footnote-def body text is invisible to T1** (excluded from the main
   stream on both sides) and FN1 is count-only — so edits *inside* a footnote
   body go uncaught. Fix direction: FN1 v2 compares per-number body text
   (oracle fnbody zone keyed by leading marker digit vs md def text).
3. **S1's table blind spot** is by design (cell bolds belong to TB1), but that
   means TB1 must carry styling inside tables when it lands.
4. **S2 window weakness**: a flattened chip whose label also appears as a chip
   on an adjacent page is missed; per-page count comparison would close it.

## Conclusion

Structural invariants (P1/F1/FN1-count) are at 100%; text-family strong
(75–100%) with all misses traced to two named blind spots (footnote bodies,
table interiors) that have designated owners in the contract; L1 reached 88%
after the fixes this experiment forced. The verifier's trust level is now a
measured quantity with a written boundary — exactly what D6 demanded. Re-run
this suite after every verifier extension; recall regressions are bugs.
