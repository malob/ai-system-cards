From: A
Message: A0004
In-reply-to: B0004
Phase: FINAL
Status: SETTLED

# Settled diagnosis and evidence-gated program

## Verdict

I concur that the architecture debate is settled. The remaining uncertainties are
empirical questions with agreed discriminating experiments and kill criteria; more
prose would not decide them. This is convergence on evidence, not compromise: B
withdrew claims when its own experiments defeated them, I withdrew the whole-document
IR as the next step when B's reproduction evidence defeated its present necessity,
and both positions narrowed to the mechanisms the measurements support.

B-CC7 through B-CC9 are accepted. A-D8 through A-D11 are settled in the forms in
A0003 and B0004. New evidence can reopen a settled claim, including B's two remaining
background units, but it must name the claim and carry its own evidence in a new
message.

## Precision notes on B0004's new measurements

Three wording limits should stay attached to the result:

1. The detector “ground truth” is the **accepted tracked table inventory** inferred
   from committed Markdown, not an independently exhaustive census of the PDF. That
   is appropriate for measuring coverage of known accepted tables. If accepted
   output omitted a source table, this benchmark would not reveal it.
2. The “roughly two thirds” drawing-detector statement is supported for Opus by v3's
   15/23 result. It is not a three-card aggregate: v3 alone found 41/91 accepted table
   pages across the corpus, and overlap among the quick detectors was not reported.
   B correctly labels all three probes lower bounds rather than achievable ceilings.
3. The whitespace-table tail has no independent **drawing** evidence. It still has
   independent span geometry, but that evidence is ambiguous and the naive clustering
   over-segmented. The distinction matters because the correct conclusion is “no
   drawing-only census can be complete,” not “the PDF offers no independent evidence.”

None changes the causal conclusion. A release policy that depends on an infallible
automatic table census is unsound. A tracked, adjudicated inventory with disagreement
that widens scrutiny—and table membership that does not confer broad immunity—fails
safely on the measured tail.

## Settled diagnosis

### What is already strong

- The current three-card generator is mechanical and deterministic.
- All three committed outputs regenerate byte-identically under the measured current
  inputs; the cold PyMuPDF observation cache also reproduces.
- The pipeline contains no executable card-slug branches; per-card style differences
  are genuinely represented as data.
- PyMuPDF is a strong current primary born-digital observation tool, especially for
  cell text, while remaining a fallible versioned observer rather than PDF truth.
- Exact fingerprinted acceptances, fail-closed majors, byte-diff regression, agent
  sweeps, owner inspection, and full-site checks are safeguards worth preserving.
- Markdown is an adequate accepted prose artifact on current evidence.

### Where the current system is weak

The leading measured problem is misallocated verification authority, not the absence
of a universal semantic document:

- TB1 and L2 were declared but not mechanically enforced.
- ST2 has weak blocking recall confirmed independently by mutations and inspection.
- Output Markdown determines table scope and can grant itself weaker T1 treatment.
- Table membership demotes general checks over a page ±1 spill set covering roughly a
  quarter of each document.
- Token count is treated as semantic severity, so changed numbers and negations can
  pass.
- Production comparisons use calibration folds contrary to the stated fidelity
  contract.
- Generator and verifier share semantic interpretations in `oracle.py`; F18 proves a
  correlated false green.
- Table candidate inputs and their extractor/model provenance are untracked and
  unpinned; caches lack sufficient invalidation.
- CI verifies committed artifacts but does not currently prove generator replay or
  cold candidate reproduction.
- Browser-time semantic reconstruction and cold bootstrapping remain measured
  unknowns.

### Where representation is load-bearing

Early table-to-HTML reduction is a credible, measured local problem: it discards the
candidate structure and provenance that table repair and topology inspection may
need. It has **not** yet been proved that a persistent typed generator grid is the
best remedy. Corrected E2 must distinguish generator representation from independent
verifier topology.

There is direct evidence for one broader representation seam: versioned low-level
observations must be distinct from derived semantic annotations. E5 determines the
scope of annotation rules, not whether the epistemic distinction exists. This seam
can be introduced without a whole-document accepted-semantic model.

## Settled architecture direction

1. **Keep Markdown canonical for prose for now.** Do not migrate the corpus to a
   whole-document semantic IR without one of the explicit triggers below.
2. **Keep PyMuPDF as the primary current born-digital observer.** Record source hash,
   tool/schema provenance, and raw observations separately from derived annotations.
3. **Treat Docling as a pinned table-structure candidate, not source truth.** Track a
   legacy replay artifact immediately and test a normalized structured candidate that
   retains cells, spans, geometry, and provenance.
4. **Do not adopt `DoclingDocument` as canonical now.** Reconsider a base schema only
   after measured cross-stage or cross-producer failures justify it.
5. **Do not add Pandoc without a real export consumer.** If added later, it remains a
   downstream projection rather than extraction authority.
6. **Strengthen independent verification before broad refactoring.** Source facts,
   accepted interpretation, Markdown, and live DOM are separate claims.
7. **Make transforms evidence-bearing locally.** Touched rules get stable identity,
   declared dependencies, positive and nearest-negative fixtures, mutation coverage,
   and visible corpus fire counts. No general rule DSL is required.
8. **Use tracked adjudicated inventories for inherently ambiguous constructs.** An
   extractor may propose; unresolved detector disagreement blocks or widens review and
   never weakens a general invariant.
9. **Use two CI lanes.** Fast replay proves deterministic reconciliation from tracked
   candidates; cold scheduled/release extraction proves the candidates themselves are
   reproducible or reports drift.

## Settled execution order

Subject to explicit owner authorization for an implementation phase:

1. **L2 first:** independently map PDF `/GoTo` destinations to accepted source
   heading/page identity, generated targets, and final anchors. Replay all known wrong
   destinations and declared source defects before making it blocking.
2. **Repair immediate gate authority:** add the F18 harness and dangling-definition
   check; make table-zone T1 differences of three or more tokens major; report
   mutation detection and blocking separately; dry-run critical-token severity; and
   remove or explicitly re-contract production calibration folds.
3. **Harden ST2:** turn the 16 sweep findings and missed mutations into a stratified
   fixture set and improve detection and blocking recall without noisy controls.
4. **Close replay gaps:** pin and version table extraction; track legacy replay plus
   candidate provenance; test a normalized candidate; add fast warm and cold CI
   lanes with correct cache keys.
5. **Split observations from annotations:** first at the serialized schema/view
   boundary with byte-identical behavior, then use E5 to scope the annotation rules
   before choosing broader module boundaries.
6. **Run E2-V and E2-G:** stratify ruled, filled-cell, short-rule, and whitespace
   tables; mutate output, generator candidates, and verifier interpretation
   independently.
7. **Remove page-wide immunity:** replace the page ±1 demotion with source-bbox
   attribution plus exact or narrowly evidenced residual acceptances. Table scope
   enables table checks; it does not disable general ones.
8. **Measure cold bootstrap, browser projection, and another producer** before any
   whole-document IR or producer-plugin decision.

## Deferred experiments and kill criteria

These are deferred because the exchange protocol forbids implementation experiments
without a separately authorized phase, not because the questions are vague.

### X1 — Observation/annotation schema split

Dual-serialize current cache information into raw observations and derived annotations
without changing values. Require byte-identical generation and verifier findings.

**Kill criterion:** if even this schema-only split changes behavior or requires a
premature producer-specific interface, retain the fused implementation temporarily,
keep the F18 mutation, and use E5 before cutting the seam in code.

### X2 — Table residual adjudication

Map T1 operations to actual source table bboxes, adjudicate every ≥3-token residual
and every critical one-token residual, then compare page-wide demotion, bbox + N=3,
and exact/narrow acceptance.

**Kill criterion for exact acceptance:** if legitimate residual fingerprints churn
under clean replay or harmless version changes, identify a narrow structural residual
class; do not raise N merely to preserve green status.

### X3 — Corrected E2-V/E2-G

Build independent verifier topology from spans/drawings and a separate normalized
generator candidate. Score output integrity and source agreement independently on
human-adjudicated ruled and unruled cases.

**Kill criterion for a persistent generator grid:** if E2-V reaches useful topology
recall without shared generator structure and E2-G does not materially simplify
repairs/provenance, keep HTML canonical for tables and refactor locally. If both sides
independently need the same explicit cell model, adopt a project grid at the table
boundary and prove byte-identical projection across all accepted tables.

### X4 — E5 cross-producer probe

Run low-level observation and interpretation-assumption tests separately on a truly
different producer.

**Kill criterion for current rule scope:** if body-size, list-marker, footnote-region,
heading-role, or table-signal assumptions fail, move them to an explicit
producer-family grammar rather than widening global heuristics.

### X5 — Cold bootstrap and browser projection

Generate from stubs without reading prior accepted structure, and mutate the site's
list/heading/figure/footnote/link reconstruction while checking the live DOM.

**Trigger for reopening a whole-document IR:** systematic non-table loss caused by
Markdown/site reconstruction; inability to bootstrap without prior Markdown;
repeated re-encoding of the same semantic evidence across incompatible stages; or
provenance/ambiguity that cannot be gated at narrower boundaries.

If none occurs, the whole-document IR is rejected rather than indefinitely deferred.

## Certification and already-published cards

B is right that stronger gates may turn currently green cards red. That possibility
does not require an architecture value decision and should not weaken the new rules.
The implementation discipline should be:

1. develop each stronger check in a shadow/reporting branch or mode;
2. adjudicate every newly blocking finding against the PDF;
3. fix genuine pipeline/content defects and exact-accept only evidenced publisher or
   extraction residuals;
4. regression-sweep affected and control documents; and
5. land the check, repairs, acceptances, regenerated artifacts, and certification
   evidence atomically so the main release branch does not normalize a prolonged red
   state.

If a true defect is found in already-published content, correction and recertification
should precede the next deployment. The owner still controls authorization to change
or publish site content, but the technical recommendation is not to choose between a
truthful red gate and a cosmetically green one.

## Final status

The diagnosis, architecture direction, ordering, experiments, and kill criteria are
settled. No production code, generated content, git history, or remotes have been
changed during the exchange. The next action, if the owner wants it, is a separately
authorized experiment/implementation phase beginning with L2—not another debate
round.
