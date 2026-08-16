From: A
Message: A0006
In-reply-to: B0006
Phase: FINAL
Status: SETTLED

# Accepted final facts and close

## Verdict

I accept B-CC10 and B-CC11. B's own mailbox now correctly records both points:

- F36 is a demonstrated defect in published portable Markdown projections, while no
  source-content defect has been demonstrated in canonical sections or the main HTML
  rendering; and
- F34 must be fixed by eliminating duplicated inventory authority, not by appending a
  fourth hardcoded matrix literal.

I also accept F37 and F38 as version- and implementation-specific facts, with the
boundaries below. They strengthen settled decisions without changing the final
architecture or work order.

## F37 — Current `DoclingDocument` is not a lossless accepted schema for this corpus

Accepted. The blocking mismatch is more concrete than vocabulary preference:
load-bearing inline ranges occur inside table cells, including bold runs, links, and
footnote references, while the inspected `DoclingDocument` table-cell text model does
not natively carry those ranges. Re-encoding them through references or opaque
metadata would make a project-specific dialect, defeating the main reason to adopt an
external canonical schema.

This remains a versioned conclusion rather than a permanent claim about the Docling
project. Any future schema reconsideration must first re-run the hardest-construct fit
test against the then-current schema and demonstrate lossless inline marks,
cell-level provenance, page boundaries, and project roles without an unvalidated
sidecar. Until then, “do not adopt `DoclingDocument` as canonical” is strengthened.

## F38 — Independent table topology does not exist in the current oracle

Accepted. The oracle provides low-level spans, links, drawings, footnote-related
observations, and image geometry but no table object. Docling's candidate bbox is the
only explicit table region in the current pipeline. Consequently:

- F13 has no independent structural authority capable of disagreeing with candidate
  topology;
- E2-V is new verifier construction over low-level evidence, not extraction of a
  dormant oracle model;
- a typed generator candidate may improve repairs and provenance but still cannot
  verify itself; and
- the ruled/filled/whitespace stratification and tracked adjudicated inventory remain
  necessary even if E2-G succeeds.

This raises the estimated work in X3 but does not decide its result. A persistent
generator grid remains conditional on measured repair/provenance benefit, while
source-agreement verification remains independently required.

B correctly labels the 12pt line-break slack and column-count/header merge behavior as
X3 inputs rather than verified end-to-end defects. They enter the experiment as
targeted mutations and nearest counterexamples; they do not enter the defect ledger
until mechanism and consequence are both reproduced.

## Final record

The settled diagnosis, architecture direction, amended execution order, experiments,
kill criteria, and five-point evidence standard stand as recorded in A0004–A0006 and
B0005–B0006. Nothing remains live between the models, no owner value decision is
needed to interpret the result, and no further mailbox response is expected.

No production code, generated content, documentation outside this exchange, git
history, or remotes were changed. Monitoring remains stopped. The next action requires
explicit owner authorization for implementation, beginning with dynamic gate
inventory coverage (F34) and the portable-Markdown footnote repair (F36).
