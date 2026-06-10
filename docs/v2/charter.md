# v2 charter

The durable statement of what the v2 conversion pipeline is for, the principles it
runs on, and how the design effort itself stays resumable. Read together with
[state.md](state.md) (current status) and [decisions.md](decisions.md) (why things
are the way they are). The v1 retrospective lives in
[../v2-design-brief.md](../v2-design-brief.md) — historical record, superseded
wherever decisions.md says so.

## North star

Given a new system-card PDF, the pipeline runs unattended — spending as many tokens
and as much wall-clock as it needs — and produces a web version faithful enough to be
the canonical HTML edition people cite instead of the PDF. The owner's role is a
short, flag-directed review (minutes to an hour, not a 319-page read), and that role
shrinks card over card as the spec and verifiers mature.

**Non-goals:** minimizing token spend; zero human involvement on the first v2 card
(trust is earned by measurement, not assumed); preserving v1 pipeline code.

## The crux

v1 failed because the human was the test suite. An unbounded token budget converts
into faithfulness only when a trustworthy oracle decides "not done yet — here's
what's wrong." So **v2 is a verifier-engineering problem first and a
generator-engineering problem second.** Generation quality reduces loop iterations;
verification quality is what makes the green light mean something.

## Principles

1. **Every defect class has a designated catcher.** The verification contract maps
   each way the output can be wrong to the mechanism that catches it (mechanical
   invariant, N-version diff, vision judge, or human escalation). A defect later
   found by a human that no catcher flagged is a process bug; closing that gap is
   part of fixing the defect.
2. **Gates vs. advisors.** Exact mechanical checks (text-stream equality, link-set
   equality, style runs, table shape, pagination offsets) are gates: the loop cannot
   pass until they do, and their pass is authoritative. Probabilistic judges (vision
   page-diff, LLM judges) start as advisors — they direct attention, but their
   silence proves nothing — and may be promoted to gate status only on measured
   recall (see 3) plus track record.
3. **Calibrate, don't assume.** v1's git history is a labeled defect corpus: run
   candidate verifiers against pre-fix states and measure whether they catch what
   the human caught. Supplement with mutation testing — inject synthetic defects of
   each class, measure recall per class. Verifier trust is a number, not a vibe.
4. **Independence.** Verifiers never share context with generators (self-review
   rationalizes its own mistakes — a v1 lesson). Where no mechanical oracle exists,
   run N independent conversions and tree-diff them: agreement is evidence,
   disagreement localizes exactly where an arbiter or human must look.
5. **Two-phase artifact lifecycle.** *During conversion*, fixes are expressed as
   rules/spec changes, never hand edits — re-runs clobber edits, and rules fix all
   instances and compound. *After acceptance*, the card is ordinary content: hand
   edits (reader-reported typos, small polish) are fine and never trigger a re-run.
   Edits that reveal a systematic miss get an errata note feeding the next card's
   spec.
6. **Free-form polish only behind gates.** A final LLM polish pass is welcome, but
   every edit is re-validated by the exact invariants — polish can't silently drop a
   sentence or break a link, because the gates re-run after it.
7. **The compounding assets are the spec, the verifier suite, and the decision
   log** — not any single converted card. Each card converted should make the next
   one cheaper.
8. **Universal core, scoped idioms (D16).** The invariants and schema are
   vendor-agnostic and essentially fixed; each card's visual idioms live in a
   small per-card style manifest derived from a mechanical signal census and
   confirmed by the owner once. The closure rule — no unexplained recurring
   signal — is how new conventions surface without being anticipated. Rules
   never accumulate globally, so there is no house of cards to topple.
9. **Capture is fidelity; presentation is editorial (D17).** The model records
   semantic identity with source provenance; how the site styles those roles is
   a design decision, reviewed by the owner, never fidelity-gated.

## Architecture sketch

Structure-aware extraction (spans + styles + links + bboxes + pages; PyMuPDF
presumed in-stack, layout model TBD by bake-off) serves as both conversion input
and validation oracle. Canonical output is a typed document model (JSON); markdown,
HTML, and llms.txt are projections. The LLM proposes semantic structure *over*
extracted facts it cannot contradict. Conversion proceeds in staged waves with a
living spec: issues are triaged by type, the owner decides each type once, a judge
model applies existing rules and escalates only novel types. Layered verification
per the principles above; escalations land in a worklist; final flag-directed human
review; then acceptance and publish. Details and rationale: brief §4 plus
decisions.md.

## Roadmap

1. Catalog v1's defects from git history into a structured eval set.
2. Write the verification contract (defect class → catcher → gate/advisor).
3. Extractor bake-off, scored on which invariants each tool makes enforceable.
4. Build the mechanical verifier suite; calibrate against the v1 corpus; mutation-
   test recall per class.
5. Build the generation loop (extraction → semantic proposal → repair loop →
   N-version arbitration → visual sweep → escalation worklist).
6. Re-convert the Fable 5 card; use v1's human-verified range (≤ §6) as a partial
   regression oracle per brief §8.
7. Owner review, acceptance, publish; retrospective; fold lessons into spec.

## Meta-process (how this effort stays durable)

The conversation is ephemeral; the repo is the memory. Decisions are recorded in
decisions.md **when made**, not at session end. state.md is rewritten before any
stopping point. Experiments are committed as re-runnable scripts with writeups, not
shell history. Sub-agent findings land in files, never only in conversation. The
acceptance test for all of it: a cold session, given only this repo, continues the
work correctly — if it can't, fixing the docs is part of the task.
