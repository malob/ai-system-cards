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

## Gaps exposed (the point of the exercise) — and closed same-session

1. ~~L1 set-vs-count~~ — **fixed**: count-based URIs + wrapped-annotation
   merge → drop-link 3/8 → 7/8.
2. ~~Footnote bodies invisible~~ — **fixed**: FN1 now compares per-number body
   text (oracle marker-digit-keyed bodies vs md defs) → delete-sentence and
   swap-words **6/6** on re-run. The body-text check runs ADVISORY (minor)
   until the oracle's stacked-footnote boundary detection is hardened (it can
   glue adjacent bodies — confirmed md is correct at the 2 HEAD advisories,
   p.16 / p.113-114 region).
3. **S1's table blind spot stands by design** (cell bolds belong to TB1): TB1
   must carry styling inside tables when it lands. drop-bold stays 5/8 with
   that declared boundary.
4. ~~S2 window masking~~ — **fixed**: strict same-page counts with a
   windowed-deficit fallback for marker slop → flatten-chip **6/6**, HEAD
   still clean.

**Post-fix recall: 8 of 9 classes at 88–100%; the one at 62% (drop-bold) is a
written, owned boundary, not a mystery.**

## Conclusion

Structural invariants (P1/F1/FN1-count) are at 100%; text-family strong
(75–100%) with all misses traced to two named blind spots (footnote bodies,
table interiors) that have designated owners in the contract; L1 reached 88%
after the fixes this experiment forced. The verifier's trust level is now a
measured quantity with a written boundary — exactly what D6 demanded. Re-run
this suite after every verifier extension; recall regressions are bugs.
