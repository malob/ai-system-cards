# Experiment 01 — v1 defect catalog

**Question.** What, concretely and enumerably, did v1 get wrong — in a form a v2
verifier can be calibrated against (D5)?

**Method.** Cross-referenced the brief's §2 taxonomy against the actual fix
commits, mined representative pre/post hunks, and counted instances:

```sh
git show --stat f60899a e9046f9 605c428 fb483fb 975460f
git show fb483fb -- 'cards/**/sections/*.md'   # content fixes; grep for
                                               # :chip[, :::turn, <!-- p. counts
git show 975460f -- 'cards/**/sections/*.md'   # internal links; grep -o '](#'
```

**Result.** [defects.yaml](defects.yaml) — 19 defect classes (FL-07 added
retroactively by experiment 02's probe) across page-marker (7), formatting-loss
(7), content-artifact (2), renderer (2 grouped), process (3),
each with evidence refs, a detection signal for the verification contract, and
counts where enumerable (111 dropped internal links, ~100 reworked page markers,
37 transcript turns, 22 chip lines, 5 caption bold errors, 5 duplicate-marker
pages).

**Findings beyond the brief's taxonomy** (validating ground-truth mining over
memory):

1. ~~**CA-01, stray lone `-` artifact lines**~~ — **RETRACTED by experiment 04**:
   these were `grep -B/-A` group separators misread as diff content; the
   pre-fix files contain no such lines. The bidirectional-equality principle it
   motivated stays in the contract (independently justified). Lesson: catalog
   evidence comes from `git show` output directly, never grep context windows.
2. **FL-06, wrong directive nesting depth** (`:::transcript` → `::::transcript`)
   — a syntax-validity class that a typed document model (D1) eliminates by
   construction. (Verified against raw diff lines — real.)

**Key commit topology** (what makes calibration clean): `e9046f9` touches only
`site/`, `605c428` only tools/docs — so `f60899a` *is* the pre-fix content
baseline, and `fb483fb` the pre-fix baseline for links specifically.

**How to use for calibration (roadmap step 4).** Materialize
`cards/anthropic/claude-fable-5/sections/` at `f60899a`, run a candidate verifier
against the PDF-derived oracle, and score recall against the instances enumerable
from `git diff f60899a 975460f -- '…/sections/'`. Remember the censorship caveat
in defects.yaml: flags *not* in this catalog (especially past §6) are candidate
true positives to triage, not false positives.

**Conclusion.** The catalog supports the charter's claim: every content-defect
class except FL-03 (transcript-turn boundaries) and parts of FL-02 (chip
*categorization*, as opposed to detection) has an exact mechanical detection
signal. Those two are precisely where N-version redundancy (D7) and the vision
advisor (D8) earn their keep. Next: encode the `detection:` fields into the
verification contract (roadmap step 2).
