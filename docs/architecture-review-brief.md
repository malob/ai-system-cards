# Independent architecture review brief

Prepared against clean `main` at repository commit `cbd5978` on 2026-08-15;
`HEAD` equaled `origin/main`. This is a review prompt, not an accepted design
decision. It deliberately separates observed facts from one maintainer's proposed
direction so another model can inspect the repository, challenge the proposal, and
recommend a different architecture if the evidence supports one. The opening status
paragraph in `docs/state.md` still describes that commit series as local/unpushed and
is stale; do not let that deployment-state mismatch distract from the architecture
review.

## How to use this review pack

Use a two-stage disclosure if a genuinely independent second opinion matters:

1. Give the reviewing model the assignment, constraints, repository background,
   current-implementation facts, and **Clean-room questions** below. Ask it to commit
   its diagnosis and target architecture to writing with stable claim IDs.
2. Only after that first report, disclose **The architecture hypothesis to review**
   and ask for a claim-by-claim response. This prevents the proposal from becoming the
   frame through which every repository fact is first interpreted.

If operational convenience requires giving the entire file at once, the reviewer
should still write and freeze its clean-room diagnosis before evaluating the proposed
architecture. That is weaker evidence than staged disclosure and should be labeled as
such.

### Epistemic rules for both models

The objective is the truest diagnosis and best architecture—not consensus,
compromise, politeness, or a predetermined number of rounds.

- Neither model has a duty to move toward the other. Stand by a conclusion while its
  evidence and reasoning remain stronger.
- Concede explicitly and promptly when evidence or argument defeats a claim. Name the
  exact evidence or reasoning that changed the conclusion; do not offer a cosmetic
  concession to make the exchange look balanced.
- Never split the difference merely because two positions persist. A hybrid design is
  acceptable only when it is independently the best-supported design, not because it
  gives each advocate half of what it wanted.
- Steelman the opposing claim before rejecting it. Attack the claim's strongest form,
  not an easy paraphrase.
- Repetition is not progress. A later round should add repository evidence, a sharper
  causal argument, a counterexample, a changed premise, or a discriminating
  experiment.
- There is no arbitrary round limit. Many productive rounds are evidence that a
  load-bearing issue remains unresolved, not a reason to manufacture agreement.
- When argument alone stalls, narrow the disagreement into claims that an experiment
  could falsify. If the required evidence is unavailable, preserve the disagreement
  honestly and state what would resolve it.
- Keep factual disputes, predictions, value judgments, and reversible engineering
  preferences separate. They require different kinds of resolution.

## Assignment

Act as an independent principal engineer reviewing this repository's PDF-conversion
architecture. Do not edit the repository. Inspect the implementation and durable
experiments rather than accepting this brief, code comments, or design documents as
authoritative when they conflict.

The project owner wants a machine that improves as it converts more PDFs: each new
document should make later documents cheaper and more reliable. The default response
to a novel PDF construct should be to improve reusable primitives, evidence,
verification, or a properly scoped producer-family rule—not to add another opaque
global heuristic or document-specific patch.

Evaluate both:

1. what should be refactored in the existing working system; and
2. what we would build differently if we were designing the system today with the
   evidence accumulated from three completed documents.

Treat the proposed architecture later in this brief as a hypothesis to falsify. Give
the strongest case against it, compare serious alternatives, and say clearly which
parts you accept, reject, or would defer pending an experiment.

## Product objective and non-negotiable constraints

The repository publishes readable, responsive web editions of AI system cards and
safety reports. Its north star is unattended conversion followed by bounded,
evidence-directed owner review. Review effort should shrink as the corpus, rules,
fixtures, and verifiers improve.

The constraints that should survive an architecture change are:

- The source PDF is the sole content authority. Faithfulness includes faithfully
  reproducing publisher mistakes; the converter does not silently correct or polish.
- Capture is mechanical. Agents may inspect, classify, and propose fixes, but they do
  not transcribe or rewrite publisher text.
- Generated document content is never fixed by hand. A defect is fixed in the
  pipeline, schema, renderer, or an explicit acceptance/exception mechanism, then the
  affected corpus is regenerated and checked.
- Exact checks may gate; probabilistic or visual judgments advise until measured
  recall justifies more authority. Silence from an advisor is not proof.
- The verifier must not merely repeat the generator's conclusions. Independent
  evidence and projections are valuable even when they cost more runtime.
- Runtime and token minimization are not primary goals. Auditability, replayability,
  deterministic outputs, and fidelity are.
- Existing certified site content must remain stable during a structural migration
  unless a source-evidenced improvement is intentionally approved.
- The current three PDFs are all from Anthropic's Google-Docs-export family. They
  prove within-family reuse, not cross-producer generality.

Read `docs/charter.md`, `docs/state.md`, `docs/verification-methodology.md`, and
`docs/verification-contract.md` for the current process. Read D16, D47, D49, and D50
in `docs/decisions.md`. The older `docs/design-brief.md` and
`docs/generation-design.md` are valuable historical evidence, but several proposed
mechanisms in them did not ship and were superseded by D50.

## Current corpus and evidence base

The repository contains three completed documents:

- `cards/anthropic/claude-fable-5/source.pdf` — 317 pages;
- `cards/anthropic/claude-opus-5/source.pdf` — 193 pages; and
- `cards/anthropic/risk-report-2026-08/source.pdf` — 186 pages.

Together they contain 696 PDF pages, 43 generated section files, and 69 serialized
HTML tables.

All three currently pass the executable gate with zero unsuppressed majors and zero
table-seam flags. Some typed minor residuals and exact owner-accepted findings remain;
the current counts and their limits are documented in `docs/state.md` and
`docs/verification-contract.md`.

Important historical evidence includes:

- `docs/design-brief.md` section 2: the first implementation's defect taxonomy;
- `docs/experiments/01-v1-defect-catalog/`: labeled real defects;
- `docs/experiments/02-extractor-bakeoff/`: the original extractor comparison;
- `docs/experiments/03-signal-census/`: early visual-signal inventory;
- `docs/experiments/04-verifier-calibration/`: historical verifier calibration;
- `docs/experiments/05-mutation-testing/`: current per-document mutation evidence;
- experiments 06–11: reconversion, inspection sweeps, owner findings, convergence,
  and regression-control history.

The existing corpus is unusually valuable as a behavioral characterization suite,
but it is also dangerously homogeneous. Do not infer that a rule is universal merely
because it works across these three documents.

## Current implementation: observed architecture

At a high level:

```text
source.pdf + meta/style configuration
        |
        v
PyMuPDF extraction cache (called the oracle)
        |                         Docling table extraction
        |                                  |
        +---------------+------------------+
                        v
              transient typed dictionaries
                        |
                  cross-page stitching
                        |
                Markdown serialization
                        |
              tracked sections/*.md
                 /               \
                v                 v
       independent Markdown      Astro site and
       projection + gates        machine exports
```

The principal modules are:

- `pipeline/verifier/oracle.py`: PyMuPDF-derived spans, styles, links, geometry,
  drawing signals, footnotes, and images.
- `pipeline/generate/assemble.py`: page facts to transient typed block dictionaries,
  including inline mark reconstruction.
- `pipeline/generate/tables.py`: Docling table candidates plus extensive
  source-geometry reconciliation and repairs.
- `pipeline/generate/run.py`: orchestration, page/section selection, cross-page
  stitching, and internal-link resolution.
- `pipeline/generate/serialize.py`: typed blocks to the repository's Markdown and
  directive dialect.
- `pipeline/verifier/mdproj.py`: an independent but regex-heavy projection from
  Markdown into facts for verification.
- `pipeline/verifier/invariants.py`: executable text, link, style, structure, table,
  figure, footnote, and provenance checks.
- `site/`: Astro renderer, exports, social images, deep links, and search.

The object called the oracle is not yet a purely physical fact layer. It includes
interpretations such as an 11-point body-font assumption, footnote-region heuristics,
orphan-reference logic, drawing classifications, and geometry thresholds. See the
constants and classification paths near the beginning and end of
`pipeline/verifier/oracle.py`. A proposed `PdfFacts` layer should not merely rename
this mixture; it must decide which observations are raw, which are normalized views,
and which are semantic candidates.

The site is another semantic recovery layer, not a passive Markdown renderer.
`site/src/lib/cards.js` relocates page markers around raw tables, creates hidden
footnote shims, and rewrites table references. `site/src/lib/markdown.js` interprets
the directive dialect and converts constructs such as lettered lists. The card page
also performs browser-time layout correction for page markers and sidenotes. Include
these transformations when judging whether semantic work is duplicated.

The generator is about 5,081 lines:

| Module | Lines | Main responsibility |
| --- | ---: | --- |
| `generate/tables.py` | 2,557 | table extraction, reconstruction, styling, and repair |
| `generate/assemble.py` | 1,141 | block classification and inline geometry |
| `generate/serialize.py` | 687 | Markdown/directive emission |
| `generate/run.py` | 632 | orchestration, stitching, links, section boundaries |
| `generate/extract_figures.py` | 64 | figure extraction support |

An AST-based static audit counted roughly 1,250 branch-like nodes and 204 direct
regular-expression call sites in the generator. `tables.py` contains about half of
the generator's code and branching and roughly two thirds of its direct regex use.
Treat these as orientation metrics, not a quality verdict; verify them if they affect
your argument.

### Generalization is real but incomplete

There are no known executable generator/verifier branches on a card slug. `CARD`
primarily selects paths and isolated caches. Per-card divergence is mostly data in
`meta.yaml`, `style-manifest.yaml`, figure maps, assets, and table caches. The Risk
Report enables the only two explicit grammar switches currently found:
`link_text_resolution: extended` and `bubble_page_continuation: true`.

Therefore the main problem is not a conventional collection of
`if card == "opus"` patches. It is subtler: rules learned from individual failures
were often added to one global, order-sensitive heuristic stack. Comments throughout
`assemble.py`, `tables.py`, `serialize.py`, `run.py`, and verifier normalization cite
the pages and documents that motivated those rules. The behavior may be generic, but
its applicability, evidence, dependencies, and counterexamples are usually not
machine-readable.

### Primary complexity concentrations

1. **Tables.** `generate/tables.py::get_tables()` applies more than twenty ordered
   HTML repair/transformation passes. `_restyle_cells()` and related helpers reconcile
   Docling output with PyMuPDF geometry, rebuild merged cells, split glued spans,
   restore formatting, inject links and footnotes, and repair reading order. The
   ordering dependencies are implicit. Docling is currently run on one-page mini-PDFs
   and each structured table is immediately reduced to HTML with
   `TableItem.export_to_html()` near the end of `tables.py`. Much of Docling's typed
   table structure and provenance is therefore discarded before the largest repair
   layer begins.

2. **Block and inline reconstruction.** `assemble_page()` and
   `block_text_and_marks()` combine style roles, font flags, coordinates, fills,
   rules, pills, annotations, and gap thresholds. The code has accumulated useful
   knowledge, but universal geometry primitives, producer-family grammar, and
   card-level vocabulary are not cleanly separated.

3. **Cross-page structure.** `run.py::stitch()` contains separate continuation
   grammars for paragraphs, lists, tables, code, captions, transcript turns, and
   boxes. Internal-link resolution similarly combines destination geometry and
   textual heuristics.

4. **Serialization and reparsing.** `serialize_blocks()` is a large state machine for
   page provenance, directives, list nesting, tables, footnotes, code, and turns.
   Markdown is the tracked canonical artifact, so the verifier and site must recover
   semantic facts from that serialization. `mdproj.py` is independent of the
   generator, which is valuable, but both sides remain coupled to repository-specific
   Markdown conventions.

5. **Configuration and bootstrapping.** Several modules independently parse pieces
   of `meta.yaml` and `style-manifest.yaml` with regular expressions rather than one
   validated schema. `run.py::section_ranges()` and `first_headings()` also read
   existing generated Markdown to determine how to regenerate it, making prior output
   part of the generation input.

6. **Generator regression coverage.** CI gates committed Markdown, seam behavior,
   verifier unit tests, mutation recall, and the site build. The fast workflow does
   not regenerate documents and assert a clean diff. There is not yet a focused suite
   of construct-level generator fixtures with positive and nearest-negative cases.

7. **Lossy representation boundaries.** The most concentrated version of the current
   path is:

   ```text
   Docling structured table
     -> cached HTML string
     -> ordered regex/geometry repair chain
     -> transient block dictionary
     -> Markdown + directives + raw HTML
     -> regex verifier projection
     -> Markdown/HAST/DOM transformations
     -> browser-time layout repairs
   ```

   This does not prove that a semantic IR will remove the underlying ambiguity. It is
   a concrete hypothesis that repeated flattening makes corrections harder to scope,
   trace, compose, and verify.

### Bootstrap and reproducibility boundaries

A new card is not currently a one-command operation. `CLAUDE.md` instructs the
maintainer to create a manifest and section stubs, inventory signals and figures,
identify table pages, run Docling separately, and then invoke generation. In
particular:

- `run.py` derives section ranges and first-heading boundary keys from pre-existing
  generated Markdown;
- absent table cache data silently means “no tables” to `get_tables()`;
- running `tables.py` without explicit pages tries to recover table pages from
  existing Markdown, then falls back to a hard-coded first-document page list;
- oracle and table caches are ignored rather than committed;
- no Python project lock file currently pins the complete generation environment; and
- CI pins PyMuPDF for verification, while the documented Docling generation command
  does not pin Docling or its model artifacts.

These are separate problems from semantic representation, but they matter to the
owner's goal of a machine that runs itself from a clean clone.

### What a green gate does and does not prove

The fail-closed gate and mutation floors are real strengths, but their authority is
intentionally bounded. The contract documents, among other things, no executable
table-topology/span gate, incomplete internal-destination validation, no italic gate,
count-only figure checking, and inspection-owned visual grouping and exact page-break
placement.

This is not theoretical. Experiment 11 began after the Risk Report reached zero
automated majors and zero seam flags; the subsequent PDF/Markdown/DOM sweep found 66
overlapping major reports, approximately 40 distinct defects in nine classes. Many
were table, anchor, or styling failures outside the mechanical gates' designed
resolution. Mutation testing currently mutates final Markdown and measures verifier
recall; it does not characterize generator-rule behavior.

Do not use this evidence to dismiss the gates. Use it to avoid treating “zero majors”
as proof of end-to-end semantic equivalence and to identify what a redesigned system
must make independently testable.

### Historical warning for a renewed IR proposal

D1 and the early design brief already proposed a canonical typed JSON document with
provenance. D50 later superseded that artifact mechanism because the implementation
that actually shipped used transient block dictionaries and canonical Markdown. A new
semantic-IR proposal must therefore explain why introducing it now removes measured
failure modes rather than adding an attractive but unvalidated layer. It should also
state how its migration can be abandoned safely if the schema-fit or dual-write
experiments fail.

The extractor choice should likewise be reopened empirically rather than inherited as
folklore. Experiment 02 was a careful but narrow June 2026 comparison on the first
document family: it tested then-current PyMuPDF, Docling, and Marker behavior on a
limited set of difficult pages. It did not test several newer/current alternatives,
whole-document structured Docling against the later corpus, or a different producer.
Later decisions also record cases where the repair chain—not raw Docling—introduced
table damage.

### Existing strengths that a rewrite could accidentally destroy

- The source text and geometry are extracted mechanically rather than transcribed.
- Card selection and caches are already generalized and isolated.
- Style meanings are data-driven per document; the same color may correctly mean
  different things in different documents.
- Existing outputs and history form a substantial regression corpus.
- Verifier failures now genuinely block deployment.
- Accepted divergences are exact finding fingerprints rather than page-wide waivers.
- Mutation tests measure several verifier blind spots instead of assuming coverage.
- Full-document regression and owner-scroll practices have repeatedly caught defects
  that local fixes and automated checks missed.
- D47's instance-evidence rule is important: a motivating example may suggest a
  general rule, but each application must be justified by that instance's source
  facts.

Do not recommend replacing working evidence and checks merely to make the code look
cleaner.

## Clean-room questions

Answer these before reading the proposing maintainer's architecture hypothesis:

1. Reconstruct the actual architecture at HEAD. What is canonical at each stage, and
   where is information discarded, reconstructed, duplicated, or reparsed?
2. Rank the causes of complexity. Separate ambiguity inherent to PDFs from accidental
   complexity caused by representations, lossy boundaries, global rule scope,
   output-dialect constraints, and process history.
3. Is a persistent semantic representation necessary, or would a smaller
   modularization of the current transient-block/Markdown design produce most of the
   benefit?
4. Which current primitives or boundaries cause the most damage? Demonstrate the
   answer through difficult constructs rather than file size alone.
5. What should count as immutable source evidence, an extractor proposal, an accepted
   semantic interpretation, and a rendered artifact? Should those be separate models?
6. How independent is the verifier in practice? Identify generator assumptions that
   could produce correlated false greens.
7. Steelman at least four target architectures, including “keep Markdown canonical
   and refactor locally.” Recommend one without assuming that a rewrite, custom IR,
   Docling, PyMuPDF, or Pandoc must be part of it.
8. Which existing safeguards and hard-won behavior must survive any redesign?
9. Is a foundational refactor justified before a different-producer PDF is available?
   What can the current corpus decide, and what can it not decide?
10. State the strongest evidence against your own recommendation and the experiment
    most likely to falsify it.

At minimum, steelman these architectural families rather than comparing the current
code only with one favored rewrite:

- keep canonical Markdown and refactor the worst modules behind typed interfaces;
- retain the overall flow but persist a small validated project-owned semantic model;
- adopt or adapt `DoclingDocument` as the accepted semantic model;
- adopt Pandoc, HAST/HTML, or another established AST plus any principled sidecar;
- use separate immutable source evidence and accepted semantic models;
- make a full-document extractor the primary document authority and use low-level
  facts mainly for checking;
- keep a universal evidence/verifier core but use producer-family grammar plugins;
  and
- at least one serious alternative devised by the reviewer.

Judge them on fidelity, provenance, ambiguity representation, deterministic replay,
schema evolution, verifier independence, renderer fit, cross-producer behavior,
dependency/model drift, licensing, migration cost, and whether future onboarding
produces compounding evidence instead of compounding code.

Freeze this first report with stable fact, inference, and uncertainty identifiers
before proceeding.

The clean-room report should contain:

1. an executive verdict;
2. `F1...Fn` verified facts with file-and-line evidence;
3. `I1...In` architectural inferences, each linked to its supporting facts;
4. `U1...Un` unknowns or claims current evidence cannot decide;
5. a ranked decomposition of essential and accidental complexity;
6. an alternatives matrix that includes retaining the current architecture;
7. the reviewer's preferred target architecture and smallest reversible first step;
8. experiments and kill criteria capable of falsifying that recommendation;
9. the strongest case against the reviewer's own recommendation; and
10. confidence by major conclusion and what would change it.

## The architecture hypothesis to review

The current maintainer's proposal is not “replace everything with Docling.” It is to
separate evidence, proposals, accepted semantics, and rendering so each can evolve
and be tested independently.

```text
                                 +------------------------+
                                 | extraction candidates  |
                                 | Docling / tables / OCR |
                                 +-----------+------------+
                                             |
PDF --> immutable PdfFacts ----------------->| reconciliation
                                             v
                               Accepted SemanticDocument
                                  /         |          \
                                 v          v           v
                              HTML       Markdown    Pandoc/export
                                 \          |           /
                                  +---- projections ---+
                                             |
                                  independent verification
```

### 1. Project-owned immutable PDF fact store

Create a versioned `PdfFacts` representation of what low-level PDF tools can observe,
without assigning document semantics. Candidate fields include:

- source hash, PDF metadata, page boxes, rotations, and normalized coordinate system;
- stable IDs for characters, spans, lines, images, drawings, annotations, and links;
- exact text/glyph sequence, font/style/color information, bounding boxes and quads;
- original PDF/extraction order separately from any inferred reading order;
- raw values separately from explicitly versioned normalization views;
- image references and vector paths/rules/fills;
- URI and internal link annotations with source rectangles and raw destinations;
- page render references and extraction-tool/version provenance; and
- declared raw-extraction discrepancies when two low-level engines disagree; and
- every excluded source fact with an explicit, versioned reason.

PyMuPDF would remain the likely primary extractor for born-digital PDFs, but
“PyMuPDF oracle” would no longer mean “infallible truth.” The PDF is truth; PyMuPDF is
one reproducible observation of it. A second engine or rendered evidence may challenge
it where confidence is low.

Accepted semantic nodes would ideally reference fact IDs rather than only copying
their text. That could make coverage testable: every accepted output character has
source provenance, and every in-scope source fact is consumed, shared deliberately,
unresolved, or excluded explicitly. The reviewer should challenge both the value and
feasibility of that property, including the necessary character/span granularity and
what stable identity can mean when extractor versions fragment spans differently.

### 2. Candidate extraction adapters

Docling, deterministic table extractors, OCR engines, or VLMs would emit candidates,
not canonical content. Preserve each candidate's native structured output, model and
tool version, confidence, provenance, and proposed source-fact alignment. Do not
reduce structured candidates to HTML or Markdown before reconciliation.

For the present born-digital corpus, a plausible initial ensemble is:

- PyMuPDF for character/style/geometry/link/drawing facts;
- Docling for hierarchy, layout, and table proposals;
- one deterministic table challenger such as Camelot, pdfplumber, or PyMuPDF's table
  finder; and
- OCR/VLM adapters only for scanned, hybrid, or explicitly low-confidence regions.

The reviewer should independently assess whether these are currently the right tools,
including accuracy, determinism, maintenance, performance, model/version pinning,
licensing, and credible alternatives. Commercial services are in scope for comparison
even if the final recommendation remains local/open source.

### 3. Accepted semantic document

Do not invent a complete general-purpose document AST unless existing models fail a
measured schema-fit test. The current leading hypothesis is:

- use `docling-core`'s `DoclingDocument` as the base semantic model because it already
  supports typed content, hierarchy, tables, pictures, body/furniture separation,
  bounding boxes, and provenance, and can be constructed independently of Docling's
  parser; and
- wrap or extend it with a small, project-versioned layer for stable `PdfFacts`
  references, exact inline ranges, accepted versus proposed interpretations,
  project-specific roles, source hash, and rule/evidence/decision traces.

The semantic document would be the accepted interpretation of the source—not raw
Docling output. A reconciler could construct it from multiple candidates and exact
facts.

Pandoc's AST is the leading proposed *downstream interchange/export* representation,
not the canonical extraction representation. Pandoc has mature block/inline/table
types, filters, and writers, but does not natively model all the PDF provenance,
candidate evidence, confidence, and rule traces needed here. Encoding those as
generic `Div`/`Span` attributes may create a bespoke dialect disguised as a standard.

Review this conclusion rather than assuming it. Compare at least:

- a minimal project-owned AST;
- `DoclingDocument` alone;
- `DoclingDocument` plus a thin project extension;
- Pandoc AST plus attributes;
- relevant alternatives such as HTML/HAST, ProseMirror, TEI, JATS, ALTO/PAGE XML, or
  another document-AI schema; and
- retaining Markdown as canonical while improving internal typed stages.

Distinguish a schema's fitness from the quality of the parser that happens to emit
it. Also consider schema stability, migration burden, dependency ownership, and the
risk of stuffing load-bearing facts into unvalidated metadata maps.

The fit test should explicitly ask whether each candidate can naturally represent:

- overlapping inline marks and many-to-many source references;
- page-spanning paragraphs and page boundaries inside blocks or cells;
- nested transcript containers, label-less turns, commentary, and nested code;
- multi-page tables, repeated headers, continued cells, row/column spans, cell-level
  links, footnotes, and styling;
- orphan footnote references and footnote bodies crossing pages;
- internal PDF destinations whose source coordinates are wrong or ambiguous;
- figures, captions, multipanel figures, and vector graphics; and
- candidates, rejected alternatives, confidence, rule evidence, and decision history
  without hiding the system in opaque metadata.

For `DoclingDocument`, compare wrapping/adapting with subclassing or forking and define
the compatibility policy when `docling-core` changes. For Pandoc, require a concrete
demonstration that page/bbox provenance, multiple source facts, page boundaries,
candidate history, and project roles survive without an untyped attribute/sidecar
dialect before recommending it as canonical.

### 4. Explicit, scoped transformation system

Replace implicit chronological repair ordering with named transforms or rules that
declare:

- stable rule ID and version;
- pipeline stage and ordering dependencies;
- applicability scope: universal primitive, mechanically identified producer family,
  card profile, or exact accepted exception;
- typed predicate and action, or a registered complex implementation;
- source facts and evidence required for each application;
- expected semantic delta;
- positive fixtures and nearest counterexamples;
- documents/pages/construct IDs matched; and
- provenance linking the rule to an experiment, defect, and decision.

Conflicting same-stage rules should fail or surface a decision rather than silently
winning by source-code order. Proposed broader rules can run in shadow mode before
promotion. A rule learned on one card begins at the narrowest demonstrated scope;
promotion to producer-family or universal scope requires cross-document evidence and
counterexamples, not merely more occurrences.

The reviewer should determine how much of this should be declarative. Complex table
reconstruction may remain ordinary code; the proposal only requires it to register
scope, dependencies, fixtures, and a trace rather than pretending all transformations
fit a small rule DSL.

### 5. Fixtures and a compounding learning loop

Every novel defect or construct should contribute executable evidence:

```text
fixtures/<scope>/<construct>/<case>/
  case.yaml             # source, scope, rule, expected behavior
  facts.json            # minimal stable PdfFacts slice
  candidates/           # relevant extractor outputs
  expected.semantic.json
  expected.md
  expected.dom.json     # when rendering semantics matter
  crop.png              # only when visual evidence is load-bearing
```

A behavioral fix should normally add:

- a positive case that must trigger;
- the nearest negative/counterexample that must not trigger;
- a reproduction of the original failure or a corresponding mutation when practical;
- semantic-delta assertions preventing unrelated changes; and
- full-corpus replay for affected scopes.

Over time, automation may cluster similar card/family rules and propose a shared
abstraction. Such “self-abstraction” is only accepted if it is behaviorally equivalent
on old fixtures and full documents, rejects mined near-misses, produces no undeclared
semantic deltas, and actually reduces total scoped complexity. An agent may propose
the abstraction; evidence and gates decide whether it lands.

### 6. Projection-specific verification

The accepted semantic document should not eliminate independent verification.
Potential layers are:

- `PdfFacts` integrity and cross-engine disagreements;
- semantic-document schema, provenance completeness, tree integrity, and unresolved
  candidate conflicts;
- source facts versus accepted semantics for text, links, styles, figures, tables,
  footnotes, and reading order;
- semantic document versus each renderer projection;
- live DOM, links, visual controls, and page provenance;
- mutations targeting both semantic transforms and verifiers; and
- mandatory owner inspection for demonstrated blind spots until automation earns
  coverage.

One open design question is how to retain meaningful independence without duplicating
the entire parser. Another is whether accepted semantics should be tracked in git,
regenerated in CI, or derived reproducibly from facts and configuration. Address both.

### 7. Incremental migration rather than flag-day rewrite

A plausible migration sequence is:

1. Freeze current outputs as behavioral fixtures and add deterministic generator
   replay in CI.
2. Define and emit versioned `PdfFacts` beside the existing oracle cache without
   changing Markdown.
3. Persist Docling's structured output and create a table candidate interface while
   retaining the current table result as a legacy adapter.
4. Run a schema-fit experiment on the hardest existing constructs before choosing the
   semantic representation.
5. Emit the new semantic document in shadow mode and compare its rendered Markdown
   byte-for-byte and semantically with current output.
6. Move one construct family at a time—possibly tables first because they contain the
   largest complexity concentration, or not first because they are the highest-risk
   case.
7. Make the semantic document authoritative only after full-corpus equivalence,
   verifier/mutation coverage, visual controls, and owner review.
8. Retire legacy heuristics only when their behavior is captured by fixtures and the
   replacement demonstrates equivalence or an explicitly approved improvement.

Challenge this ordering. In particular, say whether tables should be the first
vertical slice, the last migration, or split into smaller primitives.

### Proposed discriminating experiments

The following are candidates, not mandatory conclusions. Improve or replace them if
another experiment separates the hypotheses more efficiently.

1. **Schema-fit gauntlet.** Select the hardest existing examples of page-spanning
   prose and emphasis, nested/lettered lists, wrapped headings, overlapping marks,
   literal Markdown/HTML-like text, links, footnotes, transcript variants, complex and
   multi-page tables, figures/captions, running furniture, and declared source
   defects. Encode the same accepted semantics using a minimal custom model, plain
   `DoclingDocument`, `DoclingDocument` plus an extension, and Pandoc plus any proposed
   sidecar. Score losslessness, native typing, extension surface, diffability, schema
   stability, projection simplicity, and round-trip behavior.
2. **Structured-table boundary A/B.** Preserve native Docling table grids and align
   them directly to PyMuPDF facts for a deliberately adversarial table set. Compare
   the required repairs, topology accuracy, cell text/mark provenance, deterministic
   replay, and regression behavior with the current early-HTML path. This tests
   whether premature flattening is causal rather than merely aesthetically suspect.
3. **Behavior-preserving vertical slice.** Introduce validated configuration and a
   versioned fact/typed-block artifact for a small construct family, dual-write the
   current Markdown, and require clean-clone regeneration without reading old output.
   Measure whether source identity, debugging, fixtures, and CI become materially
   stronger before committing to a repository-wide migration.

Useful properties to test include:

- facts and accepted semantic artifacts round-trip losslessly through serialization;
- every accepted character maps to source facts and every unused in-scope fact is
  explained;
- repeated identical text does not change which source instance is selected;
- table topology and cell provenance survive every projection;
- transformations are idempotent and declare ordering dependencies;
- harmless coordinate translation/scaling and span fragmentation do not alter
  semantics;
- structural rules preserve character identity unless stronger evidence explicitly
  restores a source glyph;
- rule fire-count changes across certified documents are visible; and
- generator/semantic mutations are tested, not only final-Markdown mutations.

## Questions the review must answer

1. What is the actual root cause of present complexity: poor module boundaries,
   Markdown as canonical, premature HTML reduction, limitations of PDF extraction,
   inherently ambiguous document recovery, process choices, or something else?
   Rank causes and distinguish essential from accidental complexity.
2. Is a durable semantic IR necessary, or can the current transient-block/Markdown
   design be made self-improving with much less disruption?
3. Are we reinventing an existing format? Which existing schema is the best fit, and
   what exact information would still require project-owned extensions?
4. Is `DoclingDocument` a sound base schema independent of Docling extraction, or does
   adopting it create coupling and migration risk that outweigh the benefit?
5. Should Pandoc be canonical, a downstream projection, or absent? Demonstrate the
   answer using the project's hardest constructs rather than generic format features.
6. Are PyMuPDF and Docling the right primary starting tools today? Assign each a
   precise authority boundary and recommend challengers or replacements where needed.
7. Should there be one project-owned `PdfFacts` model, or should native extractor
   output remain primary with adapters/views? What would stable source identity mean
   across extractor-version changes?
8. How should multi-page tables, reading order, overlapping inline marks, internal PDF
   destinations, transcript boxes, page boundaries, and producer-specific visual
   grammar be represented?
9. Which current heuristics encode valuable general knowledge, and which should be
   narrowed, replaced, or deleted? Sample concrete rules from the code.
10. How should rule scope and promotion work without creating either global accretion
    or hundreds of permanent one-card rules?
11. What is the smallest fixture/evaluation corpus that would make an architectural
    decision evidence-based using the three available PDFs? What claims cannot be
    tested until a different producer arrives?
12. What would make the system genuinely self-improving while preventing an agent
    from rationalizing its own regressions?
13. What should CI regenerate and compare? Which checks belong on every change versus
    a scheduled or release lane?
14. What are the migration's biggest failure modes, and what explicit kill criteria
    should stop or reverse it?
15. What should remain untouched because it is already a strong primitive or
    institutional safeguard?

## Requested review method

At minimum, inspect these implementation points:

- `pipeline/cardcfg.py`;
- `pipeline/verifier/oracle.py`;
- `pipeline/generate/assemble.py`, especially `_classify()`, `assemble_page()`, and
  `block_text_and_marks()`;
- `pipeline/generate/tables.py`, especially `get_tables()`, `_restyle_cells()`, and
  `extract()`;
- `pipeline/generate/run.py`, especially section bootstrapping, `stitch()`, and link
  resolution;
- `pipeline/generate/serialize.py`, especially `_apply_marks()` and
  `serialize_blocks()`;
- `pipeline/verifier/mdproj.py`, `invariants.py`, and `mutate.py`;
- `site/src/lib/cards.js`, `site/src/lib/markdown.js`, and the document page's
  browser-time layout code;
- the three `style-manifest.yaml` files;
- `.github/workflows/verify.yml` and `mutations.yml`; and
- the experiments most relevant to any claim you make.

Trace at least three difficult constructs end to end from source evidence through
extraction, assembly, serialization, verification, and rendered DOM. Include a
merged or multi-page table and choose two of: transcript/highlight structure,
internal links, footnotes, figures/captions, or page boundaries.

If internet access is available, use current primary documentation and current tool
versions when comparing Docling, docling-core, PyMuPDF, Pandoc, table extractors,
OCR/VLM systems, or commercial services. Separate measured repo evidence from vendor
claims and general benchmark claims.

For important conclusions, cite repository file and line evidence. If you did not run
an experiment, label the conclusion as an architectural inference. Do not use a clean
site build or zero-major gate as proof beyond the documented scope of those checks.

## Requested response format

1. **Executive verdict** — five to ten sentences, including whether to pursue a major
   refactor now.
2. **Current-system diagnosis** — essential versus accidental complexity, ranked.
3. **Proposal scorecard** — accept/reject/modify/defer for each of: `PdfFacts`,
   extractor candidates, Docling-based semantic document, Pandoc projection, scoped
   rule registry, fixtures/self-abstraction, and incremental migration.
4. **Alternatives comparison** — at least three credible target architectures with
   explicit tradeoffs and a recommendation.
5. **Tool assessment** — role-by-role recommendations for born-digital, scanned, and
   difficult-table inputs; include licensing and operational risks.
6. **Target architecture** — concrete components, ownership boundaries, data
   contracts, versioning, and failure behavior.
7. **Evidence plan** — schema-fit cases, extractor bake-off, fixtures, metrics, and
   falsifiable success/kill criteria.
8. **Migration plan** — small reversible stages that preserve current certified
   content.
9. **Strongest disagreement** — the most important thing this brief or its author is
   probably wrong about.
10. **Questions for the proposing maintainer** — only questions whose answers would
    materially change the recommendation.

End with a compact decision table separating:

- decisions that can be made from current evidence;
- experiments possible with the existing corpus; and
- decisions that should wait for a genuinely different PDF producer.

## Truth-seeking two-model exchange

For an actual debate rather than two independent essays or a negotiated compromise:

1. **Independent commitment.** The reviewing model produces and freezes its
   clean-room report with stable fact/inference/uncertainty IDs before seeing the
   proposal.
2. **Proposal challenge.** Reveal the proposal. The reviewer answers each major claim
   with `ACCEPT`, `REJECT`, or `MODIFY`, but `MODIFY` must describe the independently
   best-supported alternative—not a midpoint. It must say what changed from its
   clean-room view and why.
3. **Proposer response.** Return the independent report and challenge verbatim to the
   proposing maintainer. For each consequential disagreement, the proposer records:
   `claim ID | strongest steelman | agree/disagree | evidence | what would change my
   mind | discriminating experiment`. Supported corrections are conceded plainly.
4. **Reviewer reply.** Give the response verbatim to the reviewer. It should change a
   conclusion only where new evidence or better reasoning warrants it, and explicitly
   list both changed and unchanged conclusions.
5. **Continue without a round cap.** Repeat steps 3–4 while either model has a new
   argument, counterexample, repository finding, or experiment result. Do not end the
   exchange because positions have failed to move for an arbitrary number of rounds.
6. **Resolve claims individually.** A claim leaves active debate only when:
   - both models endorse the same conclusion for compatible reasons;
   - one model explicitly concedes it and names what convinced it;
   - a discriminating experiment decides it; or
   - the evidence required is presently unavailable, in which case it remains an
     explicit unresolved hypothesis rather than being averaged away.
7. **Record the result without forced synthesis.** The eventual decision record must
   preserve:
   - supported conclusions and their evidence;
   - genuine remaining disagreements, with each side's strongest case;
   - experiments capable of deciding them;
   - value choices that belong to the owner rather than either model; and
   - the smallest reversible action justified even if some questions remain open.

The value of the exchange is epistemic correction. Agreement is welcome when one
position persuades the other or the evidence independently supports the same answer;
it is not itself a success metric. Do not begin a large rewrite merely because both
models find the same diagram aesthetically appealing, and do not preserve a bad
design merely because rejecting it would make the exchange look one-sided.

## External references that motivated, but do not settle, the hypothesis

- DoclingDocument concept and construction APIs:
  <https://github.com/docling-project/docling/blob/main/docs/concepts/docling_document.md>
- DoclingDocument type reference:
  <https://docling-project.github.io/docling/reference/docling_document/>
- Docling confidence-score limits:
  <https://docling-project.github.io/docling/concepts/confidence_scores/>
- Pandoc AST/filter architecture: <https://pandoc.org/filters.html>
- Pandoc Lua element and table model: <https://pandoc.org/lua-filters.html>
- PyMuPDF character-level extraction:
  <https://pymupdf.readthedocs.io/en/latest/app1.html>
- PyMuPDF reading-order limitations:
  <https://pymupdf.readthedocs.io/en/latest/recipes-text.html>
- PyMuPDF licensing: <https://pymupdf.readthedocs.io/en/latest/about.html>

The reviewer should verify these against current versions and should not interpret
their inclusion as a requirement to select any of them.
