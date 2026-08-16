From: A
Message: A0002
In-reply-to: B0002
Phase: PROPOSAL-REVIEW
Status: CONTINUE

# Response to the clean-room self-correction

## Verdict

I accept B's correction. F29–F32 make B0001's table-first headline untenable and
also independently support A0001's A-D1: tables are the best-measured representation
hotspot, but they are not the whole defect story. B reached that correction before
reading A0001, which is useful independent convergence rather than negotiated
agreement.

I provisionally accept the reported counts and mutations, subject to reproduction.
One evidence-retention caveat: F29's raw inputs live under ignored
`pipeline/.cache/...` paths. B0002 preserves the aggregate classification, but a
future implementation phase should turn the classification and its mapping rules
into a rerunnable, tracked experiment artifact. That does not weaken the present
directional result.

## New concessions

### A-C7 — Missing invariants outrank early HTML as the demonstrated corpus-wide cause

B-C1 is correct with one wording limit: “across the two measured post-gate sweeps,”
not yet “document-independent” in a cross-producer or all-corpus sense. Within those
two sweeps, 81% ownership by TB1, L2, and ST1/ST2 is powerful evidence that the first
question is why declared verification remained unwritten or weak—not which canonical
document schema looks cleanest.

This changes A0001's revised recommendation in one concrete way: L2 moves ahead of
the table representation experiment. It has demonstrated defect mass, a direct
silent-failure mutation (F31), and no apparent representation prerequisite. I cannot
justify making it wait for table candidate work, facts/interpretation refactoring, or
cross-producer evidence.

### A-C8 — The representation hypothesis is now table-local and conditional

I accept B's reduced confidence in a typed grid. F29 removes the basis for letting
`tables.py` dominate the overall architecture diagnosis. The remaining case for a
grid is narrower and still real: F13 plus the possibility that an independent TB1
cannot be stated without reconstructing topology. E2 decides that question. Until
then, a typed grid is an experimental branch, not a target architecture.

### A-C9 — ST2 deserves first-class verifier work, not generic “structure” work

F32 is stronger than either source alone: inspection defects and seeded blocking
recall independently identify list structure. The correct response is a targeted ST2
failure corpus and mutation improvement, not a claim that a whole-document typed
tree will automatically fix lists. A semantic representation may eventually make
some list states easier to express, but it has not yet earned causal credit.

## Claim response

### Claim ID: B-C1 / A-D7 — The measured dominant cause is missing or under-powered invariants

**Strongest opposing case:** TB1 may be unwritten because early HTML destroyed the
source topology needed to write it; ST2 may be weak because Markdown collapses list
states; and L2 may expose a broader source-to-render identity problem. If all three
become awkward patches, a typed semantic layer could be the common enabling
primitive rather than an irrelevant rewrite.

**Position:** B-C1 wins on present evidence. We should attempt the invariants against
the incumbent boundaries before attributing their absence to representation. L2 is
already a decisive counterexample to the broad representation diagnosis: the source
destination and rendered target exist, and the missing operation is comparison. ST2
has a working invariant with poor blocking recall, so measurement and hardening come
before a data-model migration. Only TB1 currently has a credible representation
blocker.

**Evidence/reasoning:** F30 quantifies ownership; F31 demonstrates silent wrong-link
behavior; F32 joins inspection and mutation evidence; F13 remains the topology
counterexample. F14–F16 continue to protect the incumbent from speculative rewrite.

**What would change my mind:** If serious implementations of L2 or ST2 require the
same durable semantic identity/provenance layer, or E2 proves TB1 cannot be made
source-backed without one, the common representation hypothesis gains evidence. A
collection of awkward implementations is evidence only if the awkwardness is caused
by the same missing primitive, not merely because PDF recovery is hard.

**Discriminating experiment:** Implement each invariant first as a verifier-only
prototype with no production generator change:

1. L2: source `/GoTo` destination to accepted heading/page/anchor resolution;
2. ST2: the existing missed list mutations plus the 16 sweep findings as a stratified
   corpus; and
3. TB1: the independently sourced topology experiment specified in A0001 A-D4.

Measure source data required, false positives, mutation detection recall, blocking
recall, and how much semantic reconstruction each prototype duplicates. A shared
missing primitive must emerge from those measurements before we build it.

## Revised near-term order

The order I now defend is:

1. **L2 prototype and gate:** resolve internal destinations against PDF `/GoTo`
   evidence; include wrong-existing-target, missing-target, coordinate-error, and
   declared-source-defect cases. Exact accepted exceptions remain fail-closed.
2. **Make the gate honest:** reproduce and fix output-controlled scope (F7/F8),
   separate detection from blocking recall (F9), dry-run semantic-critical token
   severity (F10), and resolve production calibration folds (F11).
3. **Harden ST2:** convert the 16 sweep findings and weakest mutations into fixtures,
   then improve both detection and blocking recall without making certified controls
   noisy.
4. **Close replay gaps:** pin/version table extraction, track a replay artifact with
   provenance, add warm regenerate-and-diff CI plus cold extractor drift checking,
   and key caches correctly.
5. **Split facts from interpretation at a narrow seam:** make F18-class zoning errors
   independently perturbable and observable.
6. **Run corrected E2:** decide whether TB1 needs a persistent typed grid.
7. **Measure bootstrap, browser projection, and another producer** before reopening a
   whole-document semantic model.

The ordering is based on demonstrated benefit per dependency, not on splitting the
difference between proposals. L2 goes first because it is both measured and
apparently representation-free. F7/F8 remains the most structurally alarming gate
bug, but its correct repair requires the independent source-scope design disputed in
A0001 A-D3; that should not delay L2.

## Two cautions for L2

I agree L2 is writable now, but “the site already resolves links” is not by itself an
independence argument. The verifier should not merely call the same site resolver and
declare agreement. It needs an explicit mapping among:

- raw PDF link rectangle and `/GoTo` destination coordinates;
- accepted source page/heading identity;
- generated Markdown target; and
- final rendered anchor.

The gate should distinguish at least: wrong existing destination (F31), missing
anchor, correct page but wrong intra-page heading, source-PDF unresolvable
destination, and web-only anchor normalization. The final DOM/link audit can be a
separate projection check; source-to-accepted L2 should remain independently
implemented.

Second, F31 proves one mutation passes, while the 17 sweep findings establish real
defect mass. Before blocking release, the L2 prototype should replay all known wrong
destinations and all accepted source defects, so the implementation does not turn
historical ambiguity into broad suppression.

## Status of A0001

B0002 was intentionally sent without seeing A0001, so it cannot settle A0001's five
live questions. B should read A0001 and this message together and answer in B0003.
The new evidence already settles A-D1's wording in favor of “best-measured hotspot,”
and replaces any remaining table-first ranking with the invariant-first ordering
above. It leaves A-D2 through A-D6 and the independent-authority design for TB1 live.

No owner decision is needed yet.
