# Charter

The durable statement of what the conversion pipeline is for, the principles it
runs on, and how the design effort itself stays resumable. Read together with
[state.md](state.md) (current status) and [decisions.md](decisions.md) (why things
are the way they are). The retrospective on the labor-intensive first attempt lives
in [design-brief.md](design-brief.md) — historical record, superseded wherever
decisions.md says so.

## North star

Given a new AI system-card or safety-report PDF, the pipeline runs unattended —
spending as much wall-clock as it needs — and produces a web version faithful enough
to be the canonical HTML edition people cite instead of the PDF. The owner's role is
a bounded flag-directed review plus the final scroll, and that role shrinks document
over document as the spec and verifiers mature.

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
   each way the output can be wrong to the mechanism that owns it (mechanical
   invariant, rulebook-driven inspection sweep, or owner escalation). A defect later
   found by a human that no catcher flagged is a process bug; closing that gap is
   part of fixing the defect.
2. **Gates vs. advisors.** An unsuppressed major from an executable mechanical check
   blocks the loop; a pass is authoritative only for that invariant's stated scope.
   Probabilistic/vision inspection directs attention, but its silence proves nothing.
   Any automated probabilistic judge would earn gate status only through measured
   recall (see 3) plus a cross-document track record.
3. **Calibrate, don't assume.** v1's git history is a labeled defect corpus: run
   candidate verifiers against pre-fix states and measure whether they catch what
   the human caught. Supplement with mutation testing — inject synthetic defects of
   each class, measure recall per class. Verifier trust is a number, not a vibe.
4. **Independence.** Verifiers never inherit a generator's conclusions (self-review
   rationalizes its own mistakes — a v1 lesson). Where no mechanical oracle exists,
   inspectors report from the PDF without editing; the orchestrator owns fixes, and
   owner decisions alone enter the accepted-divergence list.
5. **Generated artifacts stay generated.** Fixes are expressed as class-level
   pipeline/spec changes, never as hand edits to `sections/*.md` — re-runs clobber
   edits, and rules fix all instances and compound. Reader-reported defects re-enter
   the same regenerate/diff/gate/sweep loop.
6. **No transcription or free-form polish.** The PDF's extracted facts are assembled
   mechanically. Agents inspect and classify; they do not rewrite publisher text.
   Every pipeline change is re-validated by the implemented invariants and inspection
   layers.
7. **The compounding assets are the spec, the verifier suite, and the decision
   log** — not any single converted card. Each card converted should make the next
   one cheaper.
8. **Universal core, scoped idioms (D16).** The invariants and typed role vocabulary
   are vendor-agnostic and essentially fixed; each document's visual idioms live in a
   small per-card style manifest derived from a mechanical signal census and
   confirmed by the owner once. The closure rule — no unexplained recurring
   signal — is how new conventions surface without being anticipated. Rules
   never accumulate globally, so there is no house of cards to topple.
9. **Capture is fidelity; presentation is editorial (D17).** The generator records
   semantic roles in tracked markdown with page provenance; how the site presents
   those captured roles is a design decision reviewed by the owner.

## Built architecture (D50; supersedes the pre-build architecture decisions)

PyMuPDF supplies the immutable span/style/link/geometry oracle; docling supplies
table candidates. The generator assigns transient typed block dictionaries and
serializes them directly to tracked `sections/*.md`. Astro consumes that markdown
for HTML, `card.md`, `llms.txt`, social images, and search. There is no canonical JSON
tree and no LLM transcription, semantic proposal, N-version conversion, or polish
pass in the shipped pipeline.

Verification is layered: fail-closed mechanical gates → independent rulebook-driven
page/markdown/DOM sweeps → orchestrator-owned class fixes and regression controls →
owner scroll. Exact owner acceptances fingerprint a complete observed finding.
Per-document visual grammar lives in the style manifest; shared fixes live in
`pipeline/`.

## Roadmap status and next test

The original seven-step build roadmap is complete in its shipped, mechanical form:
the defect corpus, contract, extractor bake-off, calibrated/mutation-tested verifier,
generation loop, Fable reconversion, owner review, and publication all landed. Opus
and the Risk Report subsequently proved one shared pipeline across three documents
from Anthropic's Google-Docs-export family. The next architectural experiment is a
document from a different vendor/PDF producer; until then, cross-vendor generality is
an open hypothesis rather than a project claim.

## Meta-process (how this effort stays durable)

The conversation is ephemeral; the repo is the memory. Decisions are recorded in
decisions.md **when made**, not at session end. state.md is rewritten before any
stopping point. Experiments are committed as re-runnable scripts with writeups, not
shell history. Sub-agent findings land in files, never only in conversation. The
acceptance test for all of it: a cold session, given only this repo, continues the
work correctly — if it can't, fixing the docs is part of the task.
