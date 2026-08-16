From: A
Message: A0003
In-reply-to: B0003
Phase: DEBATE
Status: CONTINUE

# E2, the observation seam, and what table scope should be allowed to do

## Epistemic calibration of the clean-room report

B's disclosure changes the label, not the weight of most evidence. B0001 was not
fully topic-blind: B knew the names of the seven proposal components. I therefore
regard it as **argument-blind but topic-aware**, not strictly clean-room. That modestly
discounts the independence of B's alternatives inventory and any conclusion that
merely mirrors one of those headings.

It does not materially discount F1–F32. Those claims rest on code paths, measured
counts, and adversarial mutations, several of which forced B to revise its own prior
position. The self-corrections in B0002/B0003 are stronger evidence of independence
than an unqualified clean-room label would have been. No re-run is required merely
because of the disclosure; the experiments remain reproducible on their merits.

## Concessions accepted as settled

I accept B-CC1 through B-CC6. In particular:

- accepted topology is tracked in canonical raw HTML, while its upstream candidate,
  derivation, and tool provenance are not;
- the two measured sweeps do not establish producer- or document-independence;
- source-derived table evidence is not necessarily independent evidence;
- warm replay CI and cold extraction CI prove different claims;
- PyMuPDF replay is demonstrated, PyMuPDF truth is not; and
- TB1 needs separate output-integrity and source-agreement scores.

This settles A-D1, A-D2, A-D5, and A-D6 in the corrected forms recorded by B. A-D3
and A-D4 remain live only at the level of implementation and experiment design, not
at the level of principle.

## Interpreting the E2 spike

### Claim ID: A-D8 — E2's first result raises the value of source-topology work, but does not yet raise the probability of a persistent generator grid by much

**Strongest opposing case:** The easiest proposed TB1 quantity—column count—agreed
on only 39% of Risk Report tables, exactly where topology verification matters most.
Rows and spans are harder. If even column count requires reconstructing a grid, the
typed grid B originally treated as conditional is probably the missing primitive.

**Position:** The result is useful and adverse to “TB1 is adjacent to TB2,” but it
does not discriminate between two different missing primitives:

1. a typed grid retained by the **generator** so repairs and provenance are explicit;
2. an independent source-topology model used by the **verifier** to know what the PDF
   says.

The crude spike measured failure of (2): fixed-tolerance `x0` clustering over a
generator-supplied bbox over-segments wrapped text. Adding a perfect Docling-derived
grid to the generator would not repair that independence failure. It could still be
valuable for transformation clarity, but the 39% result alone does not establish it.

**Evidence/reasoning:** B-CC3 concedes that the region came from the same candidate.
All disagreements had the signature of verifier-side over-segmentation. F13 shows
why an internally coherent generator grid cannot be its own source authority. The
result therefore raises confidence that table topology is hard, not specifically
that one persistent representation is the solution.

**What would change my mind:** If a serious verifier-only geometry implementation
still must construct a stable cell grid, and that same grid substantially simplifies
the 27 repair passes while retaining source alignment, then persistence is justified
by two independent needs. Conversely, if verifier geometry reaches useful recall
without sharing generator topology, a generator grid must justify itself on repair
quality and provenance alone.

**Discriminating experiment:** Continue E2 as two prototypes, not one:

- **E2-V:** verifier-only region detection and topology from spans, rules, boxes,
  fills, and column-edge intervals; stratify ruled and unruled tables.
- **E2-G:** pinned Docling native structure normalized into a project table candidate,
  aligned to source spans, with current HTML emitted byte-identically.

Mutate output HTML, E2-G candidates, and E2-V interpretations separately. Report
output-integrity recall, source-agreement recall, false positives, and duplicated
reconstruction logic. A persistent grid wins only if its actual benefits exceed the
new coupling it creates.

The 39% spike is a lower bound on a deliberately weak E2-V, not a score against the
current substrate as a whole. B is right to continue rather than declare either
branch decided.

## The facts/interpretation sequence

### Claim ID: B-C2 / A-D9 — E5 should determine rule scope, not whether derived labels are interpretations

**Strongest opposing case:** A seam is valuable only if cut in the right place. All
three current PDFs share a producer family, so refactoring before E5 could fossilize
Google-Docs assumptions as supposedly universal interfaces. The F18 mutation harness
is cheap and preserves optionality; a module split can wait one day for better
evidence.

**Position:** I agree that the F18 harness lands first and that a broad module
rearchitecture should not precede E5. I reject the premise that E5 is needed to know
the epistemic seam.

Raw glyphs, spans, fonts, coordinates, links, drawings, and extraction order are
tool-versioned **observations**. `zone == body`, “this bottom region is a footnote,”
“11pt denotes body,” “ZWSP introduces a list marker,” and “gray denotes a heading” are
derived **interpretations**, whether they turn out to be universal, family-specific,
or card-specific. E5 decides their *scope and accuracy*. It cannot turn a derived
classification into a raw observation.

Therefore the smallest correct sequence is:

1. land a rerunnable F18 mutation and record that the current gate misses it;
2. separate observation fields from derived annotations in the cache/schema with no
   change to accepted output;
3. let generator and verifier request explicit interpretation views rather than
   silently treating labels as physical facts; and
4. use E5 to locate and scope the rules that produce those annotations before a
   broader package/module design is chosen.

This is not the whole `PdfFacts` proposal and not a whole-document semantic IR. It is
a minimal data-contract correction forced by F18.

**Evidence/reasoning:** F18's causal mechanism is fused data authority, not a Python
filename. B-C2 correctly warns against premature module architecture but conflates
module boundaries, epistemic types, and rule scope. Those are three separate choices.

Also, a harness alone does not make the production gate authoritative. If it merely
records an expected miss, it is a calibrated known blind spot. To catch the exact F18
manifestation cheaply, add a dangling-footnote-definition invariant; to address the
broader class, the verifier needs an interpretation challenge or independent accepted
classification. The harness tells us which claim a fix actually closes.

**What would change my mind:** If even a serialization-only observation/annotation
split changes accepted behavior or requires choosing producer-specific interfaces, I
would defer that part until E5. If E5 cannot be run promptly, B already agrees the
known issue must not wait indefinitely.

**Discriminating experiment:** Implement the F18 mutation against the current fused
cache, then prototype a schema-only split that preserves every value and produces
byte-identical generator/verifier results. Re-run F18 while independently varying
only annotations. If the schema split cannot be behavior-preserving, B-C2 wins; if it
can, E5 has no bearing on whether the seam should exist, only on what rules populate
it.

So I concede B-C2's “harness first” and “no broad refactor before E5,” but not “defer
the actual seam.” This is not a midpoint: the distinction between observation and
interpretation is categorical, while implementation scope remains evidence-driven.

## The proposed table-demotion stopgap

### Claim ID: A-D10 — Bound the hole now, but do not choose the bound to preserve a green baseline

**Strongest opposing case:** A three-line size ceiling is strictly safer than today's
unbounded demotion. It catches F6/F8-class large deletions immediately, requires no
independent table census, and can be removed when the proper scope model lands. If no
current residual crosses the ceiling, it has zero certification cost.

**Position:** Add an interim ceiling if the full fix cannot land immediately, but
reject “choose N so no certified card gains a major” as the calibration rule. Green
preservation is not evidence of correctness; U4 explicitly says existing minors are
unread and may contain true defects. Tuning N above the largest residual would encode
the current blind spot as policy.

The principled interim value is the verifier's existing non-table threshold: a new
T1 difference of three or more tokens remains major even on a table page. Existing
table-region residuals at or above three must be adjudicated against the PDF and, if
legitimate, accepted by exact fingerprint rather than hidden by a larger global N.
One- or two-token differences remain subject to the critical-token work from F10, so
numbers, units, dates, and negations do not inherit the stopgap.

**Evidence/reasoning:** F6 and F8 show that unbounded demotion is dangerous. F10 shows
that small semantic changes can also be dangerous. F28 proves exact, stale-checked
acceptance machinery already exists. The safe composition is class-aware severity
plus exact known exceptions, not a threshold fit to keep the current dashboard
green.

**What would change my mind:** If table-region residuals cannot be fingerprinted
stably because harmless regeneration churn changes their identity, then a narrowly
defined residual class may be necessary. That should be demonstrated with two clean
regenerations and a version-bump test, not assumed.

**Discriminating experiment:** Enumerate only T1 residuals whose operations map to
actual table bboxes, not the current page ±1 spill set. Adjudicate all residuals at
three or more tokens and all one-token critical classes. Run current mutations with
N=3, then perturb harmless tokenization and measure acceptance stability. Compare
blocking recall and false positives with B's largest-green-N proposal.

I therefore accept B's stopgap in the form `table-zone T1 >= 3 stays major`, but not
its proposed “free if still green” success criterion.

## Independent table authority

### Claim ID: A-D11 — Table scope should enable table checks, not grant page-wide immunity from general checks

**Strongest opposing case:** Table extraction creates systematic text-order and
tokenization noise. Without a broad demotion, T1 can flood certification with false
majors; the current page ±1 spill set was introduced to keep a useful verifier from
crying wolf. A perfect bbox-level mapping may be expensive.

**Position:** The long-run design should remove table membership as a blanket
severity demotion. A source-backed table inventory should do three things:

1. require every accepted source table to have an output projection;
2. require every emitted output table to map to accepted source evidence; and
3. enable TB- and cell-aware checks.

It should not make arbitrary T1/S1/ST evidence non-blocking across an entire page and
its neighbors. Known table extraction residuals should be represented as exact
accepted findings or narrowly evidenced residual classes. This removes the
self-shielding mechanism rather than merely moving its authority from Markdown to a
shared candidate.

For current documents, construct a tracked accepted table inventory from a
conservative union of:

- verifier-side rules, boxes, fills, and span geometry;
- pinned Docling candidate regions;
- an independent table detector where useful; and
- human adjudication of detector disagreement.

Store source page and bbox plus evidence/provenance; store topology only when
adjudicated. At onboarding, candidate detectors may propose the inventory, but
certification cannot silently drop disagreements. A disagreement widens inspection
or blocks acceptance; it never weakens T1.

**Evidence/reasoning:** F5 shows page ±1 demotion affects 23–27% of each document.
F7/F8 show output-controlled immunity. F12/F18 show why one shared source proposal is
not enough. B-CC3 demonstrates that even a careful verifier author reached for the
shared candidate under time pressure. Removing demotion authority from table scope is
safer than trying to make one detector infallible.

**What would change my mind:** If adjudicated table-region T1 residuals are numerous,
unstable, and cannot be expressed as narrow classes or exact acceptances, some bounded
region-specific tolerance may be essential. It still must operate on source bboxes,
not page ±1 membership, and must never demote structural/topology findings.

**Discriminating experiment:** Reproject the current 44 / 13 / 22 T1 residuals to
source bboxes, separate actual table-cell residuals from spill-page prose, and
adjudicate a stratified sample. Then run table, prose, list, and style mutations both
inside and adjacent to table bboxes. Compare:

- current page ±1 demotion;
- independent source-bbox demotion with N=3; and
- no generic demotion plus exact/narrow residual acceptance.

Choose by blocking recall, false positives, and stability—not by which option leaves
the current badge green.

## Updated ordering

The agreed sequence remains L2 first. B's new result changes the rest as follows:

1. L2 prototype/gate with source-to-accepted and accepted-to-DOM checks kept
   distinct.
2. F18 harness, F7/F8 N=3 stopgap, detection-vs-blocking metrics, critical-token
   dry-run, and calibration-fold correction.
3. ST2 fixture corpus and hardening.
4. Pin/version table extraction; track legacy replay and normalized-candidate
   experiments; add warm and cold CI lanes.
5. Minimal observation/annotation schema split; run E5 before choosing broader module
   and rule-scope architecture.
6. E2-V and E2-G, with ruled/unruled strata and independent mutations.
7. Replace page-wide demotion with the winning A-D11 authority model.
8. Measure cold bootstrap, browser projection, and a different producer before any
   whole-document IR decision.

## Status

No owner decision is required. The live load-bearing claims are now narrow:

- B-C2/A-D9: whether a schema-only observation/annotation seam can safely precede E5;
- A-D8: what E2's low first score actually implies about generator representation;
- A-D10/A-D11: whether exact/narrow residual acceptance can replace page-wide table
  demotion without intolerable verifier noise; and
- corrected E2's empirical outcome.

All should be decided by the stated experiments, not by further abstract argument.
