# Experiment 05 — mutation testing (D6): per-class verifier recall

**Question.** When a defect is *known* to exist (because we injected it), does
the verifier catch it? This turns "calibrated on history" into a number and
covers the censorship gap in the v1 corpus (D5/D6).

**Method.** [mutate.py](../../../pipeline/verifier/mutate.py) injects one
synthetic defect into a temporary copy of the current sections, runs the full
invariant suite, and counts a catch iff a flag of the expected invariant appears
that was not in the unmutated baseline. The current calibration is 8
mutations/class with seed 5. The original Fable-only record remains
[results.json](results.json); the enforceable current baselines are:

- [Fable 5](results-anthropic-claude-fable-5.json)
- [Opus 5](results-anthropic-claude-opus-5.json)
- [Risk Report: August 2026](results-anthropic-risk-report-2026-08.json)

```sh
env CARD=anthropic/claude-fable-5 uv run --python 3.12 --with pymupdf==1.28.2 \
  python pipeline/verifier/mutate.py --per-class 8 --seed 5 \
  --baseline docs/experiments/05-mutation-testing/results-anthropic-claude-fable-5.json \
  --json /tmp/mutation-anthropic-claude-fable-5.json
```

With `--baseline`, the command exits nonzero if an expected class disappears,
an unbaselined class appears, its invariant or sample count changes, or its caught
count falls. Improvements pass. Per-site details remain evidence rather than the
gate because an otherwise harmless source edit can move a seeded sample.

## Current three-document baselines (2026-08-15)

| document | eligible classes | caught | recall | not applicable |
| --- | ---: | ---: | ---: | --- |
| Claude Fable 5 & Claude Mythos 5 | 12 | 86/96 | 89.6% | — |
| Claude Opus 5 | 11 | 72/88 | 81.8% | `flatten-chip` |
| Risk Report: August 2026 | 11 | 74/88 | 84.1% | `flatten-chip` |

These are floors, not a claim of universal defect recall. The weakest measured
classes are structural splits and S1 bold removal; the agent inspection layers
remain their explicit backstop. The scoped/weekly GitHub Actions mutation workflow
runs all three baselines independently of the fast per-change verifier gate.

## Original Fable calibration (historical)

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

The initial experiment established the method and forced concrete L1/FN1/S2
repairs. The three current, per-document artifacts turn that measurement into a
checked floor: structural invariants remain strongest, while the documented
structural/style blind spots remain assigned to the inspection layers. Re-run the
suite after every verifier extension or source/canon change; a drop below a
committed floor is a gate failure, not an observation to overlook.
