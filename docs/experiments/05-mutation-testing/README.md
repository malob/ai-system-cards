# Experiment 05 — mutation testing (D6): detection, severity, and release recall

**Question.** When a defect is *known* to exist because we injected it, does the
intended verifier notice it, classify it as release-worthy, and actually stop the
production gate? Keeping those questions separate prevents a warning, unrelated major,
or stale acceptance from masquerading as proof that the intended defense works.

## Method

[mutate.py](../../../pipeline/verifier/mutate.py) injects one synthetic defect into a
temporary copy of the current canonical sections. Each trial then sends the **same
exact mutated section bytes** through two authority lanes:

1. the Python source/canonical gates, including L2, P2/F3 source inventory, FN1/RF1,
   production normalization, exact acceptances, and consequence-aware severity; and
2. a persistent Node worker running the production Markdown transform, HTML renderer,
   raw-authored-HTML policy, and HTML5-normalized page/figure DOM audit in memory.

The worker never rereads `WORKTREE` for a trial. The unmutated composite result must
first pass the real release acceptance semantics; otherwise the run stops rather than
crediting every mutation with a pre-existing failure.

Four signals are recorded independently:

- **detected** — the intended invariant emitted a new full-fingerprint finding;
- **intended-major** — at least one such intended finding is major;
- **major-blocked** — after applying exact acceptances, an unsuppressed major remains;
- **gate-blocked** — the production gate exits nonzero. This includes acceptance-
  configuration failures, so it is diagnostic rather than a detector-recall floor.

The calibration is eight trials/class at seed 5. Each class has a digest-derived RNG
stream, so adding/reordering a class cannot resample the others. The current strict
schema-v2 artifact binds `card_id`, seed, trials/class, complete class/invariant set,
all four aggregates, and every trial's evidence. It has no legacy fallback. Baseline
validation happens before mutations or output writes; `--json` may not resolve to the
baseline and defaults to an explicit temporary result path.

The original Fable-only historical record remains [results.json](results.json). The
enforceable schema-v2 baselines are:

- [Fable 5](results-anthropic-claude-fable-5.json)
- [Opus 5](results-anthropic-claude-opus-5.json)
- [Risk Report: August 2026](results-anthropic-risk-report-2026-08.json)

```sh
env CARD=anthropic/claude-fable-5 uv run --python 3.12 --with pymupdf==1.28.2 \
  python pipeline/verifier/mutate.py --per-class 8 --seed 5 \
  --baseline docs/experiments/05-mutation-testing/results-anthropic-claude-fable-5.json \
  --json /tmp/mutation-anthropic-claude-fable-5.json
```

With `--baseline`, removed/new classes, changed invariants, card/seed/sample drift,
malformed aggregate/detail evidence, or a decrease in **detected**,
**intended-major**, or **major-blocked** fails. Improved recall passes. Per-site sample
movement remains evidence rather than a floor because a legitimate source edit can
move a deterministic sampling site.

## Current three-document baselines (2026-08-15)

| document | eligible classes | trials | detected | intended-major | major-blocked | gate-blocked | not applicable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Claude Fable 5 & Claude Mythos 5 | 25 | 200 | 191 (95.5%) | 184 (92.0%) | 185 (92.5%) | 185 (92.5%) | — |
| Claude Opus 5 | 24 | 192 | 176 (91.7%) | 168 (87.5%) | 171 (89.1%) | 171 (89.1%) | `flatten-chip` |
| Risk Report: August 2026 | 24 | 192 | 173 (90.1%) | 166 (86.5%) | 171 (89.1%) | 171 (89.1%) | `flatten-chip` |
| **Total** | — | **584** | **540 (92.5%)** | **518 (88.7%)** | **527 (90.2%)** | **527 (90.2%)** | — |

These artifacts combine independent per-class runs with the final hide-image/V1
refresh and pass the strict schema-v2 validator. Hosted run
[31929996953](https://github.com/malob/ai-system-cards/actions/runs/31929996953)
then replayed the exact final tree successfully: downloaded artifacts, normalized
with key-sorted `jq`, match all three committed baselines exactly. The gate steps took
12m54s for Opus (05:52:08–06:05:02), 20m05s for the Risk Report
(05:52:12–06:12:17), and 37m36s for Fable (05:52:09–06:29:45). The first hosted run,
[31928741823](https://github.com/malob/ai-system-cards/actions/runs/31928741823),
was cancelled solely when Fable exceeded the old 30-minute timeout; the follow-up
raised that operational limit to 45 minutes and completed the unchanged floor.

The 25 possible classes cover:

- ST1/ST2/ST3 list and heading structure;
- L1 dropped URI links and L2 wrong-but-existing internal destinations;
- T1 deletion, duplication, ordinary word order, and critical
  number/date/unit/currency/negation/comparator changes;
- FN1 dropped definitions and critical footnote value/negation changes;
- S1 bold loss and S2 chip flattening;
- V1 browser-hidden authored prose;
- F3 missing, wrong-path, hidden, and reordered figures; and
- P2 duplicated and missing page markers.

Every V1, P2, F3, L2, body-critical, and footnote-critical class is detected,
classified major, and major-blocking in all 8/8 trials on every eligible card.
`repoint-link` still proves the important distinction: the fragment graph remains
valid while only the independent source destination identity catches the wrong
heading. Page/figure classes now measure P2/F3 through the real renderer rather than
the narrower legacy P1/F1 projections.

The misses are localized rather than averaged away:

| class | Fable detected / intended-major / blocked | Opus | Risk Report |
| --- | --- | --- | --- |
| `split-item` (ST2) | 3 / 3 / 3 | 3 / 3 / 3 | 3 / 3 / 3 |
| `item-to-paragraph` (ST1) | 6 / 6 / 6 | 4 / 4 / 4 | 4 / 4 / 4 |
| `split-heading` (ST3) | 8 / 8 / 8 | 6 / 6 / 8 | 4 / 4 / 8 |
| `drop-link` (L1) | 8 / 8 / 8 | 5 / 5 / 5 | 7 / 7 / 7 |
| `swap-words` (ordinary T1) | 7 / 0 / 1 | 8 / 0 / 1 | 7 / 0 / 1 |
| `drop-bold` (S1) | 7 / 7 / 7 | 6 / 6 / 6 | 4 / 4 / 4 |

For `split-heading`, a different production major can stop release even when ST3
itself misses; that is useful defense-in-depth but correctly does not inflate
intended-major recall. Ordinary two-word swaps are usually detected but remain below
the consequence-aware major threshold. Phase 4 owns ST2 hardening; L1/S1 and the
other structural gaps remain explicit sweep/control obligations. These totals are
floors, not a claim of universal defect recall. The scoped/weekly GitHub Actions
workflow runs all three baselines separately from the fast release gate.

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
repairs. The current composite experiment adds the missing distinction between
detection, severity, and actual release behavior and proves the new source/final-DOM
and critical-value defenses at 8/8 wherever eligible. It also says where the system
is still weak: list/block structure and bold/link occurrence coverage, not page,
figure, destination, visibility-policy, or critical-token projection. Re-run all
three strict artifacts after every verifier, renderer, source-authority, or canonical
change; a fall in any committed detection/intended-major/major-blocking floor is a
gate failure, not an observation to overlook.
