From: A
Message: A0001
In-reply-to: B0001
Phase: PROPOSAL-REVIEW
Status: CONTINUE

# Proposal response: the evidence narrows the refactor

## Scope and epistemic status

This message responds to B0001 as committed. B says some background work was still
running when it sent B0001. I am not treating unfinished work as evidence and I am
not delaying this response for it. If later work changes a load-bearing claim, B
should send it in a new immutable message and I will reopen the claim explicitly.

I have not independently rerun B's eleven experiments yet. I provisionally accept
F1–F28 because the report gives concrete mutations, commands, outputs, and causal
paths, not because B and I happen to agree. A failed reproduction would reopen the
affected claim.

## The withheld proposal

The proposal B had not seen was the four-layer architecture in
`docs/architecture-review-brief.md:429-451`:

1. immutable project-owned PDF facts;
2. extractor outputs as proposals rather than authority;
3. an accepted semantic document distinct from those proposals; and
4. independently verified renderer projections.

It tentatively preferred a thin project extension over `DoclingDocument`
(`docs/architecture-review-brief.md:501-555`), Pandoc only as downstream
interchange, a scoped transformation registry (`:557-582`), fixture-driven rule
promotion (`:584-611`), and incremental migration (`:633-655`). It explicitly
proposed testing those choices rather than declaring them settled (`:658-701`).

B0001 defeats the proposed *sequence* and substantially raises the burden for a
whole-document accepted-semantic layer. It does not defeat the evidence/proposal/
interpretation distinction; F18 is the first direct experiment showing why that
distinction matters. The right conclusion is narrower than my initial hypothesis,
not an average of our two starting positions.

## Explicit concessions

### A-C1 — Whole-document semantic IR is not justified as the next move

I concede this. F14–F16 show that all three documents regenerate byte-identically,
the prose path is stable, and even Docling cell-text drift is repaired from source
spans. I cannot name a measured whole-document failure that an accepted
`SemanticDocument` fixes more cheaply than B's scoped repairs. U6 could change that,
but an unmeasured browser-stage risk is not a license to migrate the whole corpus.

Consequences:

- Markdown remains the accepted prose artifact for now.
- We do not adopt `DoclingDocument` as the repository's canonical schema now.
- We do not run the whole schema-fit gauntlet before fixing demonstrated gate bugs.
- Any future whole-document IR must beat the incumbent on measured failures, clean
  bootstrap, and cross-producer evidence—not on architectural tidiness.

### A-C2 — Several urgent defects are gate-policy defects, not representation defects

I concede I underweighted this. F7/F8, F10, and F11 are direct counterexamples:
output-controlled gate scope, token-count severity, and calibration-only folds each
remove release authority without requiring a new document model. They should not be
made contingent on an IR migration.

F7/F8 is the most severe: an artifact must never be able to grant itself a weaker
test regime merely by containing an empty tag. F10 proves that “minor” currently
means “small token count,” not “small semantic consequence.” F11 is either an
implementation defect or a contract defect; the current contradiction is untenable.

### A-C3 — Published mutation recall needs two names and two scores

I concede F9. “Detected” and “would block release” are different properties. The
current 89.6% / 81.8% / 84.1% figures are detection recall; B's 81.2% / 67.0% /
75.0% figures are blocking recall under the current policy. Neither should be
substituted for the other. Mutation artifacts and CI should report both, by class and
severity, with the scoring definition in the artifact.

### A-C4 — The current oracle is not a fact store

I concede this more strongly than my original brief stated. F12/F18/F26/F27 show
that `oracle.py` fuses reproducible observations with producer-family assumptions
and semantic zoning, then supplies the same interpretation to generator and
verifier. F18 demonstrates the correlated false green: both projections agree to
discard the same mis-zoned prose.

This is direct evidence for a facts/interpretation seam. It is not yet evidence for
the full character-addressed `PdfFacts` design proposed at
`docs/architecture-review-brief.md:453-479`. The immediate implementation should be
the smallest split that makes F18-class interpretations independently perturbable
and gives caches source/tool/schema invalidation keys.

### A-C5 — Docling is not currently the cell-text authority

I concede B's I5 within its evidence boundary. F16 shows that the present system
uses Docling mainly as a table-topology proposal and PyMuPDF spans as cell-text
authority. Therefore an extractor bake-off is not the first task, and replacing
Docling wholesale has no demonstrated payoff. The unresolved issue is topology,
versioned replay, and independent checking—not cell-text extraction.

### A-C6 — B's experiment ordering is better than mine

E1, E2, E3, E5, and E6 answer narrower questions more cheaply than my proposed
whole-schema gauntlet. I adopt them with the independence corrections below. In
particular, the typed table grid must earn its existence by enabling a source-backed
TB1 that cannot be stated cleanly otherwise.

## Proposal scorecard after B0001

| Original component | Current position | Reason |
| --- | --- | --- |
| Project-owned immutable facts | **Keep, narrow first implementation** | F18 proves the seam; it does not prove a grand whole-document fact model is needed now. |
| Candidate extraction adapters | **Keep first for tables only** | F3/F4/F13 locate the measured exposure there. Defer a multi-extractor ensemble. |
| Accepted whole-document semantic model | **Defer; burden not met** | F14–F16 and the absence of a measured prose failure favor the incumbent. |
| `DoclingDocument` as base schema | **Do not adopt now** | External-schema coupling buys no demonstrated current repair. Test only after a trigger. |
| Pandoc | **Absent unless an export consumer appears** | B's A4 analysis agrees with the original downstream-only limit and gives no reason to add it now. |
| Independent projection verification | **Keep and strengthen** | F18 shows independence must include interpretation, not merely Markdown projection code. |
| Scoped transforms and fixtures | **Keep, introduce locally** | F2 needs explicit ordering/dependencies and counterexamples, but a universal rule DSL is not required. |
| Incremental migration | **Keep, reorder** | Gate repairs and discriminating experiments precede semantic migration. |

## Consequential disagreements and refinements

### Claim ID: A-D1 — Tables are the best-measured hotspot, not proven to be the only load-bearing representation problem

**Strongest opposing case:** F1/F2/F3/F13/F24/F25 form an unusually coherent
causal chain. Half the generator and most regex sites are in `tables.py`; topology
is flattened early; a topology mutation passes; and five of nine post-gate defect
classes were table-internal. No other representation problem has comparable
evidence.

**Position:** I accept tables as the first representation experiment. I reject
B0001's “in exactly one place” formulation as stronger than the evidence. U6 says
browser code reconstructs lists, figures, headings, footnote shims, and table
references after the verifier stops. F20 also says prior Markdown controls section
boundaries. Until U6 and cold bootstrap are measured, “only tables” is an unearned
universal conclusion.

**Evidence/reasoning:** Demonstrating one dominant hotspot does not establish that
all other representation boundaries are harmless. B correctly declined to rank U6;
the executive verdict should inherit that uncertainty.

**What would change my mind:** A DOM/projection audit plus E6 showing no semantic or
bootstrap failures outside tables would make “tables are the only current
representation problem” supportable for this corpus.

**Discriminating experiment:** Extend E1 to classify experiment-10/11 defects by
the stage that could have caught them, run E6, and seed mutations into the browser
transforms named in U6. Count source-to-Markdown, Markdown-to-DOM, and topology
failures separately.

### Claim ID: A-D2 — Tracking the legacy HTML cache is necessary for replay but insufficient as the new primitive

**Strongest opposing case:** B's Stage 1 is almost costless, makes a floating input
reviewable, and enables deterministic regenerate-and-diff CI. B explicitly allowed
“a normalized structural form,” so it need not canonize the legacy cache forever.

**Position:** Track enough of the current `{bbox, html}` cache to reproduce the
incumbent immediately, but do not mistake it for the durable table candidate. F3
shows it is already downstream of the information-losing choice under review. The
durable candidate should retain normalized cells, spans, cell/source geometry,
confidence where available, source hash, extractor/model versions, and schema
version. HTML should be a replay compatibility field or projection, not the only
structure.

Also, F4's statement that topology decisions exist “only” in the untracked cache is
slightly overstated: accepted topology is serialized into tracked raw HTML in the
canonical Markdown. What is missing is the upstream candidate, extraction
provenance, and reproducible derivation. That distinction matters because committing
only the legacy HTML cache duplicates the accepted artifact without recovering the
lost decision evidence.

**Evidence/reasoning:** F3 identifies exactly what `{bbox, html}` discarded. A cache
manifest closes F27; a structured candidate makes the topology decision inspectable.
These are separate goals and both are small at the table boundary.

**What would change my mind:** If current Docling APIs cannot serialize a stable
normalized grid without importing opaque/version-volatile internals, I would retain
the legacy cache and derive a minimal project-owned grid only when E2 requires it.

**Discriminating experiment:** For the 69 current tables, serialize (a) the legacy
cache and (b) a minimal normalized grid adapter from pinned Docling output. Compare
size, determinism across two clean runs, version-bump diff quality, source alignment,
and ability to reproduce canonical HTML byte-identically. Kill the normalized
candidate if it cannot reproduce or yields less reviewable diffs.

### Claim ID: A-D3 — Source-derived table scope must not merely move the shared-authority bug upstream

**Strongest opposing case:** Any source-side table census is better than regexing the
artifact under test. Docling bboxes and oracle rule geometry already exist, and a
conservative table-page union can remove F8 quickly.

**Position:** Yes to output-independent scope, but no to treating the generator's
single table proposal as unquestionable scope authority. If generator and verifier
consume the same mistaken table candidate, F18's correlated-failure pattern simply
moves from footnote zoning to table zoning. The blocking spill set should come from a
conservative union of independently derived source signals—for example, verifier-side
rule/line geometry, pinned extractor candidates, and an explicit accepted table
inventory—with disagreement widening checks rather than weakening them.

**Evidence/reasoning:** F12/F18 demonstrate the general failure mode. “Source-derived”
and “independent” are separate properties. The table scope controls severity, so a
false negative is security-sensitive even if the underlying text invariant remains
correct.

**What would change my mind:** If one source-side detector demonstrates 100% recall
on all accepted tables plus adversarial near-table layouts and is versioned
independently from generation, the union may be unnecessary.

**Discriminating experiment:** Delete, add, and perturb table candidates while
holding the PDF fixed. Seed empty output tables, missing candidate tables, false
candidate tables, and ruled non-table layouts. The scope detector passes only if
output mutations cannot shrink authority and candidate disagreement never demotes a
finding.

### Claim ID: A-D4 — TB1 must compare against independent source evidence, not merely reconstruct output consistency

**Strongest opposing case:** TB2 already works on HTML plus oracle geometry. A grid
reconstructed from the current string can expose row/column/span mutations cheaply,
and E2 has an explicit kill criterion for a persistent typed grid.

**Position:** E2 is correct, but it needs two scores: output-topology integrity and
source-topology agreement. Parsing output HTML into a grid and checking its internal
shape is useful but cannot say whether `rowspan="2"` or `rowspan="3"` matches the
PDF. If expected topology is reconstructed from the same Docling proposal that
generated the HTML, it also cannot catch F13-class candidate drift. A source-backed
TB1 needs independent geometry or an independently accepted topology record.

**Evidence/reasoning:** F13 is not malformed HTML; it is semantically wrong grouping.
Internal consistency checks cannot distinguish the two valid rowspans. F18 warns
against a shared interpretation. If oracle geometry must itself reconstruct a cell
grid to answer the question, that is evidence for a typed *fact/candidate* model,
not necessarily for making the grid canonical.

**What would change my mind:** If a verifier-only geometry algorithm with no shared
Docling topology catches the full topology mutation set at acceptable false-positive
rate, I withdraw the need for a persistent accepted grid.

**Discriminating experiment:** E2 should mutate three layers separately: emitted
HTML, the Docling candidate, and verifier-side geometric interpretation. Calibrate
against human-adjudicated topology for a stratified adversarial table set and visual
crops. Report integrity recall and source-agreement recall separately.

### Claim ID: A-D5 — Regeneration CI needs a fast replay lane and a cold extraction lane

**Strongest opposing case:** Warm regeneration is fast and directly ensures the
generator reproduces committed sections. A single clean-diff job closes F19 with
minimal operational cost.

**Position:** Add that job, but name what it proves. A warm run against a tracked
candidate proves deterministic reconciliation and serialization. It does not prove
that a clean environment can reproduce the candidate. A second, slower scheduled or
release lane should run the pinned extractor, compare normalized candidates, then
regenerate. Cache hits must be keyed by PDF hash, extractor/model versions, schema,
and relevant code/config versions.

**Evidence/reasoning:** F14/F15 prove oracle cold replay; F4/F19/F27 show table
candidate and cache invalidation are the missing parts. Conflating the two lanes
would produce a green CI claim broader than the executed test.

**What would change my mind:** If cold pinned table extraction is cheap and stable
enough for every PR, collapse the two lanes into one cold job. If model artifacts
cannot be pinned reproducibly, the cold lane must report drift rather than silently
rewrite accepted candidates.

**Discriminating experiment:** Time two clean cold runs and two warm runs for all
three cards, compare normalized candidate hashes and rendered output, then repeat
after an extractor patch-version bump. Use the variance and diff quality to choose PR
versus scheduled placement.

### Claim ID: A-D6 — Deterministic PyMuPDF observation is strong; “not the weak link” is too broad

**Strongest opposing case:** F15 reproduces the oracle cold and F16 repairs table
text from PyMuPDF spans. No current experiment shows glyph/text extraction drift, so
replacing PyMuPDF is unjustified.

**Position:** Keep PyMuPDF as the primary born-digital fact extractor. But distinguish
raw observation from interpretation built on it. F18 and F26 show that body zoning,
footnote regions, and body-size assumptions can be wrong while extraction is
deterministic. Determinism establishes replay, not truth or cross-producer validity.

**Evidence/reasoning:** This is exactly the seam both proposals now support. No
extractor bake-off is warranted for present cell text, but interpretation mutations
and E5 remain necessary.

**What would change my mind:** Cross-engine comparison showing PyMuPDF observation
loss on current born-digital facts would justify a challenger. E5 showing stable
observations but broken semantic assumptions would instead confirm that the problem
is interpretation, not extraction.

**Discriminating experiment:** On E5's non-Anthropic PDF, compare low-level character,
link, image, and drawing census across PyMuPDF and one independent engine before
testing any producer grammar. Keep observation disagreements separate from semantic
classification disagreements.

## Revised recommendation

The best current plan is verification-first and table-scoped, while preserving a
route to the long-run evidence/accepted-semantics split only when measurements demand
it.

### A-R1 — First close demonstrated authority and reproducibility holes

1. Reproduce B's F7/F8/F9/F10/F11/F13/F18 experiments in a rerunnable committed
   experiment before production changes.
2. Pin Docling and model provenance; version cache schemas and invalidate on source,
   tool/model, code/config, and schema changes.
3. Track a legacy replay input now and test a normalized structured table candidate;
   do not make early HTML the permanent evidence boundary by accident.
4. Add warm regenerate-and-clean-diff CI and a cold extractor-reproduction lane.
5. Replace output-derived table scope with the conservative independent source census
   in A-D3.
6. Stop production-only calibration folds unless the owner explicitly changes the
   fidelity contract.
7. Report mutation detection and blocking recall separately.
8. Dry-run critical-token severity on every existing residual before changing the
   release threshold. Start with numerals, units, dates, and negations; do not assume
   a generic named-entity detector is precise enough.

Items 2–8 are independently valuable. None waits for a semantic IR.

### A-R2 — Split facts from interpretation at the smallest useful seam

Refactor `oracle.py` so raw observations and versioned normalization views are
separate from body/table/footnote/list classifications. The generator may consume an
accepted interpretation; the verifier must be able to challenge or vary it. Add
oracle-interpretation mutations modeled on F18 and fail on unexplained source-fact
coverage loss. Do not require character-level stable IDs everywhere until repeated
text/provenance tests demonstrate that span-level identity is insufficient.

This is a scoped implementation of the long-run A5 shape both reports consider
correct—not a commitment to a whole-document semantic artifact.

### A-R3 — Run the table experiment before choosing the representation

Implement corrected E2 from A-D4. If independent TB1 reaches acceptable recall on
HTML plus source geometry, keep the current Markdown/raw-HTML canonical table and
refactor transforms incrementally behind typed function boundaries. If E2 must build
a durable grid to state the invariant or align cell provenance, adopt a typed grid
inside the table subsystem and prove byte-equivalent projection across all 69 tables.

For either outcome, each touched table transform gets a stable ID, declared ordering
dependencies, a positive fixture, the nearest negative fixture, and visible fire
counts. We do not need a general rule DSL to enforce those properties.

### A-R4 — Measure the two remaining triggers before reopening whole-document IR

Run E6 cold bootstrap and measure U6's Markdown-to-DOM semantic transforms. Then run
E5 on a genuinely different producer before designing producer plugins or declaring
the current block model universal.

Reopen a whole-document accepted semantic model only if at least one of these is
demonstrated:

- non-table defects systematically arise from lossy Markdown/site reconstruction;
- cold bootstrap cannot reproduce accepted structure without reading old output;
- cross-producer onboarding requires the same semantic evidence to be re-encoded in
  several incompatible stages; or
- source-to-output provenance and ambiguity cannot be gated at narrower boundaries.

If those triggers do not occur, reject the whole-document IR and keep the narrower
facts/interpretation and typed-table improvements. That is a genuine kill criterion,
not a postponed commitment.

## What is settled between the proposals, and what remains live

Provisionally settled unless B disputes the characterization:

- Do not replace everything with Docling.
- Keep PyMuPDF as the present primary born-digital observation tool.
- Do not use Pandoc as canonical; do not add it without an actual export need.
- Keep Markdown canonical for prose now.
- Fix demonstrated gate-policy bugs before architectural migration.
- Separate reproducible facts from interpretation, initially at a narrow seam.
- Treat typed table structure as an experimentally decided implementation, not an
  article of faith.
- Preserve independent verification, exact accepted exceptions, byte-diff regression,
  and owner inspection.

Live claims for B0002:

1. Does B accept A-D1's narrower “best-measured hotspot” wording?
2. Does B agree that the tracked artifact should distinguish legacy HTML replay from
   a normalized structured candidate?
3. What independent source authority can TB1 and table-scope severity use without
   recreating F18's shared-interpretation false green?
4. Does B accept the two-lane CI claim boundary?
5. Is the facts/interpretation split now urgent before E5, or should only the F18
   mutation harness land before cross-producer evidence?

No owner value choice or production authorization is required to continue the
debate. The next useful message is B's answer to these claims, plus any completed
background evidence that actually changes one of them.
