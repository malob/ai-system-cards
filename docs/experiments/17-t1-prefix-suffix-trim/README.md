# Experiment 17 — prefix/suffix trimming for the T1 token diff (2026-09-01)

**Question.** T1 hands the whole document's oracle and markdown token streams
to `difflib.SequenceMatcher` (junk heuristics off) on every gate run, and the
mutation suite runs the gate once per trial; profiling one Opus 5 trial put
that diff at about half of the ~3.5 s per trial. Does trimming the shared
prefix and suffix before the quadratic matcher runs give a large speedup
while leaving every opcode — hence every acceptance fingerprint and mutation
digest — byte-identical?

**Method.** `trimmed-t1.patch` (not applied; `git apply` restores it) adds
`invariants.trimmed_opcodes`: strip the common prefix P and suffix S, run
difflib on the window between them, offset the opcodes back. Plain trimming
is NOT difflib-exact: difflib takes the longest block first with ties broken
earliest-in-a then earliest-in-b, so when a repeated run sits at the edge of
the change it may align a shifted copy instead of P or S (218 of 2,000
small-alphabet random cases differed only in position, 209 in the phrasing
of the same edit; 72 of 500 real-prose windows differed). The patch therefore
guards the trim: a shifted block can only pre-empt P if it is longer than P,
or S if it is at least as long as S, and any such block must carry either the
`w`-token window on the far side of the boundary (continuing across it) or
the boundary region minus `w` tokens to a shifted position in the other
stream. Eight NUL-joined C substring searches test those necessary
conditions; if any hits, or if P or S is shorter than `w`, the full matcher
runs. `test_t1_trim.py` (in the patch) replays the equivalence against
difflib on seeded random, binary, periodic, and real-prose corpora.

**Result.**

- Exactness: 0 mismatches against difflib over 68,000 randomized cases
  (small and binary alphabets, periodic runs, prose windows with one to four
  local edits, 3,000-token prose with mutation-suite-shaped edits); all four
  cards' gate flags byte-identical; all four mutation replays byte-identical
  to the committed baselines (776 trials — even the unguarded plain trim was,
  so the corpus has no ambiguous boundary today).
- Speed: almost none, because the window is not the mutation — it runs from
  the FIRST residual difference in the document to the LAST, and every card
  carries typed T1 minors near both ends:

  | card | tokens | window after trimming | T1 diff before → after |
  | --- | --- | --- | --- |
  | claude-opus-5 | 47,059 | 84% of the document | 0.84 s → 0.64 s |
  | claude-fable-5 | 78,178 | 88% | 2.78 s → 2.30 s |
  | risk-report-2026-08 | 60,419 | 36%, guard fell back (repeated boilerplate at the boundary) | 1.37 s → 1.37 s |
  | claude-fable-5-1 | 53,815 | 21% | 0.83 s → 0.05 s |

  Mutation trials widen the window further whenever the mutation site lies
  outside the residual span. The four concurrent replays took 264 / 713 /
  192 / 167 s (Opus / Fable / Risk / Fable 5.1), within noise of the untrimmed
  runs. The fallback fires on 16% of mutation-shaped single edits in 3,000-
  token prose and more often on repetitive text.

**Conclusion.** Not adopted (working tree reverted; the patch is the record).
Trimming is exact only with a guard whose subtlety is out of proportion to a
~20% saving on the diff of two cards. The real lever for T1 is anchoring:
diff piecewise between long common blocks that occur once in each stream, so
each residual costs its own small window. That is a different deterministic
algorithm, not difflib-equivalent in ambiguous cases, and would need a
decision, a re-acceptance pass, and regenerated baselines. Independent of the
diff, the trial loop is serial: a process pool with one Node worker per
process is the semantics-free speedup (6 performance cores here), and the
hosted job could shard classes the same way.
