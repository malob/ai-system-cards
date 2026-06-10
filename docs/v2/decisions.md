# Decision log

Append-only. One entry per settled question, with date, provenance, and rationale.
New entries go at the bottom. If a decision is reversed, append a new entry that
supersedes it — don't rewrite history.

---

## D1 — Canonical representation: typed document model, not markdown (2026-06-09)

Decided with Opus 4.8 during the v1 retro (brief §4.0). The conversion produces a
typed JSON tree; markdown/HTML/llms.txt are serializers off it. Page numbers and
bboxes are per-node provenance, never inline artifacts — this removes the entire v1
page-marker bug class by construction, and validation becomes tree-diff instead of
fuzzy text matching.

## D2 — Triage: amortized human judgment via living spec + judge model (2026-06-09)

Decided with Opus 4.8 during the v1 retro (brief §4.3). Issues surface during
conversion grouped by issue-type; the owner decides each type once; the decision is
recorded as a rule; a judge model applies existing rules and escalates only novel
types. Implies staged conversion (seed wave, then bulk), not a simultaneous fan-out.

## D3 — Scope: ground-up rebuild, no carried debt (2026-06-09)

Decided with Opus 4.8 during the v1 retro (brief §4 decisions box). Keep the Astro
renderer as a projection target; mine v1 repair scripts for logic, then retire them.

## D4 — Verification-first sequencing (2026-06-09)

Decided with Fable 5 in the v2 planning session. Build and calibrate the verifier
suite *before* rebuilding generation. Rationale: unbounded token budgets convert to
quality only through a trustworthy stop-condition; verification is the load-bearing
component and the only one we can test before the pipeline exists.

## D5 — v1 artifacts are calibration data; preserve them (2026-06-09)

Decided with Fable 5. The v1 git history (notably fb483fb, 975460f, and the §2
taxonomy in the brief) is a labeled corpus of real, human-found defects with fixes.
Candidate verifiers are calibrated by running them against pre-fix states and
measuring whether they rediscover the human-found defects. Therefore: never clean up
`tools/`, `cards/*/*/extracted/`, or rewrite pre-fix history. Caveat: this corpus is
censored (one reviewer, through ~§6) — passing it is necessary, not sufficient (see
D6).

## D6 — Mutation testing measures verifier recall (2026-06-09)

Decided with Fable 5. Synthetically inject defects of each class (drop a link,
flatten a chip, split a paragraph at a page break, transpose table cells, delete a
footnote, swap a word…) into known-good content and measure each verifier's recall
per class, at scale. This turns "do we trust the verifier?" into a number and
covers the censorship gap in D5.

## D7 — N-version redundancy where no mechanical oracle exists (2026-06-09)

Decided with Fable 5. For judgment calls (transcript turn boundaries, chip
categorization, heading-vs-bold, reading order), run N independent conversions
(different prompts/models, no shared context) and tree-diff. Agreement under
independence is acceptance evidence; disagreement localizes arbitration. Verifiers
never share context with generators — v1's self-verifying agents rationalized their
own errors.

## D8 — Gates vs. advisors; probabilistic judges earn gate status (2026-06-09)

Decided with Fable 5. Exact mechanical checks are gates (authoritative pass/fail).
Vision page-diff and other LLM judges start as advisors: they direct human
attention, their silence proves nothing. Promotion to gate status requires measured
recall on injected-defect suites (D6) plus track record across cards. For the first
v2 card, the owner reviews flagged pages plus a random sample.

## D9 — Two-phase edit policy (2026-06-09)

Decided with Fable 5, at the owner's instigation. During conversion: fixes are
rules, never hand edits (re-runs clobber edits; rules fix all instances and
compound). After acceptance: the card is ordinary content — hand edits for small
fixes are fine and never require a pipeline re-run. Systematic lessons from
post-acceptance edits are recorded as errata feeding the next card's spec. The
pipeline is a one-shot converter with a clean handoff, not a build step the content
lives inside forever.

## D10 — Final LLM polish pass, constrained by gates (2026-06-09)

Decided with Fable 5. A free-form LLM polish pass at the end of conversion is
allowed (the owner wants one). It is safe only because every edit it makes is
re-validated by the mechanical gates — fidelity cannot be silently broken by
polish.

## D11 — Meta-process: the repo is the memory (2026-06-09)

Decided with Fable 5, at the owner's instigation. All process state is
externalized to version-controlled files so the effort survives compaction, session
loss, and handoffs: decisions recorded here when made; docs/v2/state.md rewritten
before stopping; experiments committed as re-runnable scripts + writeups under
docs/v2/experiments/; sub-agent findings written to files. Acceptance test: a cold
session given only the repo continues correctly ("fresh-session test").

## D12 — Standing commit authorization; commit often (2026-06-09)

Granted by the owner. Claude commits in this repo without asking, at milestones and
decision points, so that git history is itself a queryable record of the process.
Imperative, concise messages per the owner's global git conventions.

## D13 — Never push; v2 work stays local until the owner publishes (2026-06-09)

Owner's call. Pushing is reserved for explicit owner request — partly because push
to main triggers the GitHub Pages deploy, and partly because the v2 effort should
be pushed as a whole once it's something worth publishing. Liberal local commits
(D12) are unaffected.

## D14 — Extraction stack: PyMuPDF oracle + docling table authority + LLM semantics (2026-06-10)

Settled empirically by experiment 02 (the brief's §6 bake-off, resolved in two
probes instead of five candidates). PyMuPDF supplies the verification oracle and
prose backbone: text spans with style flags, URI+GoTo links (exact on probe
pages), chip pill fills, gray-commentary signal, superscripts, image rects, page
geometry. Docling (2.100.0) supplies table structure — merged cells exact, zero
false-positive tables where PyMuPDF hallucinated — and corroborates block order;
its paragraph segmentation is too mushy to be the backbone. The LLM proposes the
semantic layer on top of facts it cannot contradict. marker/MinerU/pymupdf_layout
left unprobed — nothing left for them to answer. Revisit if verifier-v0
calibration finds docling-resistant tables.

*(2026-06-10, owner asked for more:* part 3 ran docling and marker on the hard
table set — p.95/98 mixed spans, the p.252 15×8 monster, the p.309–318 nine-page
table. Docling: all 2-D merges exact, multi-page tables come back as clean
per-page fragments to stitch in-pipeline. See experiment 02 README part 3 for
marker's result. D14 stands.)*

## D15 — FL-07 resolved: preserve placeholder/redaction highlights (2026-06-10)

Owner's call ("I think it would be nice to preserve them"). The light-green
`#d9ead3` placeholder/redaction signals become a typed mark in the document
model. The census shows they occur both as inline pills (`[Error 1]`) and as
larger multi-line boxes, so the mark needs inline and block forms. How they
*look* on the site is editorial (D17); that they're captured is fidelity.

## D16 — Stratified spec: universal core + per-card style manifests + closure (2026-06-10)

Resolves the owner's "house of cards" worry about cross-card/cross-vendor growth.
Three strata:

1. **Universal invariants** (the verification contract) — defined against any
   PDF's mechanical facts; mention no vendor idioms; do not grow per card.
2. **Universal schema** (typed document model) — heading/para/list/table/figure/
   footnote/link/emphasis plus a small extensible set of semantic marks (chip,
   turn, placeholder…). Grows rarely, by owner decision.
3. **Per-card style manifest** — a small *data* file mapping that card's visual
   signals to semantic roles ("fill #ffe5a0 ↦ chip(yellow)"; "text #444444 in
   transcript boxes ↦ commentary"). Derived mechanically by the signal census
   (experiment 03), confirmed by the owner in one sitting, scoped to the card so
   manifests can never conflict across cards.

The **closure rule** makes this generalize: any recurring distinctive signal the
manifest doesn't explain is a flag, not a pass-through. A new vendor's idioms
don't need anticipating — the census surfaces them, the owner maps them once,
conversion proceeds. What compounds across cards is machinery (census, gates,
manifest workflow) and the schema — never a global rule pile.

## D17 — Capture is fidelity-bound; presentation is editorial (2026-06-10)

Owner's framing. The document model captures *semantic identity* with source
provenance (chip role + registry color family, placeholder mark, code span —
with exact source colors stored as provenance). How the site *renders* those
roles (palette, dark mode, pill styling) is a design-system decision the owner
makes at render review — it is recorded but not fidelity-gated. Consequently the
V1 vision judge compares structure and semantics ("same content, same emphasis,
same grouping"), never exact pixels or hex values.

## D18 — v2 pipeline code lives in `pipeline/` (2026-06-10)

Not `v2/`: the directory will outlive the version label. Structure grows as
needed; first resident is `pipeline/verifier/`. v1 leftovers (`tools/`,
`extracted/` scripts) stay untouched as calibration data (D5).
