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

## D19 — First spec rule decided; Fable 5 manifest roles confirmed (2026-06-10)

Owner decided the auto-link issue-type (blocklist URLs are not links) — now
rule R1 in docs/v2/spec-rules.md, the living spec's first entry, exercising the
D2 flow end to end. Owner also confirmed the Fable 5 style-manifest role names
("all these names look about right… things we want to be tracking"); manifest
status flips to owner-confirmed, with `#467886` still verify-at-conversion.

## D20 — Overnight autonomy protocol (2026-06-10, ~01:45)

Owner authorized the long unattended stretch: (1) **provisional-rule-and-
continue** — novel issue-types get a best-judgment rule marked PROVISIONAL in
spec-rules.md + the worklist, conversion continues, owner reviews the batch at
check-in (cheap to re-derive: fixes are rules); (2) **full re-conversion
authorized** — if the seed wave passes the gates, run all 319 pages overnight,
ending in verifier runs, a rendered site build, and a triage worklist. All
local; nothing publishes (D13).

## D21 — No LLM alt-text pass; captions suffice (2026-06-10, ~02:25)

Owner's call: figure/table captions are good enough; drop the planned per-figure
LLM alt-text pass. Alt text may be derived mechanically from the caption lead
(or left empty) — an accessibility-presentation detail under D17. Consequence:
the conversion pipeline is now **fully mechanical** end to end; LLM involvement
reduces to adjudication of flagged ambiguities only (N1).

## D22 — Overnight run #2 scope (2026-06-10, ~02:55)

Owner, heading to bed: (1) **full 319-page V1 visual sweep authorized** (vision
agents, rendered page vs PDF render, ~3–6M tokens), findings triaged into fixes
overnight; (2) **v1 shipped card FROZEN** — no post-acceptance patches; all
improvements flow through the v2 re-conversion he reviews. D20's
provisional-rule protocol remains in force.

## D23 — Morning-tour decisions: caption block, blockquotes, underlines (2026-06-10, ~10:40, owner)

(1) **Captions are a first-class block construct.** Figures, tables, AND
transcripts carry `[Figure|Table|Transcript N.N.N] lead. rest` captions, but
they rendered as three unrelated accidents (italic-sibling CSS,
docling-absorbed rows, plain bold paragraphs). One `:::caption` block in the
dialect / caption node in the model, attached to the preceding
figure/table/transcript; mechanical detection by the size-9 bracket-lead
signature; renderer styles captions uniformly once. Subsumes the owner's
caption-dedup rule (never inside the table box) and gives the sweep's
caption-split/misplaced/duplicated classes one checkable invariant.
(2) **Indented quote regions are standard blockquotes** — no special AISI
type. (3) **Underline capture required** (owner-found class FL-09): tables
whose captions promise underlined second-best scores must carry underlines;
detect via thin rule-fills under spans; restyle table cells from oracle spans
(same pass recovers bold best-scores, the sweep's emphasis-lost class).


## D24 — H2 review round 1: outcomes (2026-06-10)

Owner reviewed the converged v2 preview section by section. Verdicts:
- **Accepted residuals** (whitelisted in `pipeline/verifier/accepted.json`,
  suppression printed transparently by calibrate): T1 stream-order majors on
  pp. 38/44/56/57 — drawn pills/legend text extracted at z-order positions;
  the md follows VISUAL order, correct for a reader.
- **Blessed adjudications**: literal `\u2014`/`**` in transcripts kept
  verbatim (escaped to render as printed); turn labels keep source brackets.
- **Owner-caught classes, all fixed**: welfare-table cell paragraphs +
  cross-page row continuation; spurious seam line breaks. These drove the
  table-audit round (vsweep5) and its fix set.
- **Built on owner request**: `.ph` green placeholder ranges (D15/D17,
  sub-span pill mapping → raw-HTML spans); styled `<pre>` for bold code
  boxes (p.182).

Gate at close: **0 majors** (6 owner-accepted suppressed), FN1/L1/T1 minors
1/31/100.


## D25 — Orchestrator-owned fixes; tracked output; diff-per-fix protocol (2026-06-10)

Owner directives for round G and beyond:
- **Inspector agents surface findings; the ORCHESTRATOR owns every fix**
  (diagnosis, class-vs-patch call, application, verification).
- **`sections-v2/` is now git-tracked.** The per-fix protocol:
  pipeline change → regen → `git diff cards/.../sections-v2` → confirm the
  EXPECTED change is present AND nothing unexpected changed (the diff is
  primarily a REGRESSION detector) → visual/preview check when the change is
  renderer-visible → commit pipeline + output together, message naming the
  fix.
- Generated files are never hand-edited; the diff is read-only verification.
  One-off corrections go through the (planned) owner-adjudicated patch layer
  applied by run.py post-regen.

<!-- APPEND NEW DECISIONS BELOW THIS LINE (D27 next) — newest at the bottom. -->
<!-- (Three same-session attempts to insert above the tail prove the need.) -->

## D26 — fidelity line: fix our divergences, not the source's quirks (2026-06-11)

Owner call during round-G review (the p.224 italic "I"). The pipeline
corrects only its OWN divergences from the source — a hyphen *we* dropped
("introspectionbased"), a space *we* inserted ("Self- knowledge"), a
footnote *we* failed to render. It does NOT correct the source document's
own quirks: typos, font-slips, a stray italic glyph mid-word, a section
cross-reference the PDF itself points at the wrong place. Reproducing those
IS faithfulness; "fixing" them is proofreading — an open-ended mandate plus
fragile detector heuristics that mis-fire elsewhere, and it blurs the line
the whole v2 premise rests on (mechanical, faithful, no LLM in the loop).

Test for which side a defect is on: **would the same wrong thing be in the
PDF's own text/styling layer?** If yes → source quirk → reproduce it. If the
PDF is right and only our output is wrong → our divergence → fix it.

If an errata/correction layer is ever wanted, it is a deliberate, separate,
owner-driven feature — never smuggled in case-by-case during conversion.
(Round-G concretely: the "Its" italic mid-word slip is in the PDF → left
as-is. Bare-number section links resolving to the wrong subsection were OUR
geometry failing where the PDF's number was right → fixed.)


## D27 — transcript: interjections, continuation outputs, wrapped highlights (2026-06-11)

Owner review of the p.198 transcript (6.5.2.B) settled three transcript
representation rules, all now implemented:

- **Bracketed editorial interjections = inter-turn narration, not turns.** A
  turn whose entire body is one bracketed sentence ('[The model proceeds to
  work on the task.]') renders as `commentary` (plain framing prose between
  turn cards), like the gray narration in the #f3f3f3 transcripts (p.40-41) —
  NOT a user bubble. (Detection: whole-body `\[[^\]]{31,}\]`; the no-internal-
  `]` guard keeps real turns that merely start/end with `[…]` pills as turns.)
- **A continuation output box renders as its own [Assistant] card.** A mono
  output box nested in a turn, separated from its label by an interjection, is
  the assistant's continued output → its own [Assistant] turn card (inheriting
  the preceding turn's role + label), matching sibling cards. **Owner-accepted
  cost:** the PDF's output box has no label of its own, so the repeated
  '[Assistant]' adds one token not literally in the source (T1 minor 69→70).
  Accepted because the box IS the assistant's output — the label makes the
  PDF-established speaker explicit (presentation, not fabrication); this is the
  one sanctioned exception-shape to D26 for transcript continuation cards.
- **A wrapped full-width highlight is ONE pill.** A green highlight spanning
  two lines extracts as one box per line; the adjacent ph marks merge into one
  continuous pill — but only when the source boxes are vertically stacked, so
  distinct side-by-side pills ('[…] [Error 1]', p.40) stay separate.

Gate after: 0 majors / L1 31 / T1 70 (the +1 is this accepted continuation
label; still below the round-G baseline of 72).


## D28 — v2 is canonical; v1 retired (supersedes D22) (2026-06-11)

Owner's call after the owner-review polish: v2 is good enough to be THE
version. v1 is retired, not kept frozen alongside.

- **v2 output is now the card content.** `cards/anthropic/claude-fable-5/
  sections-v2/` was renamed to `sections/` (replacing the v1 transcription);
  the site's default `SECTIONS_DIR=sections` now serves v2, and the dev-server
  env override is gone. ~14 `sections-v2` path references updated across the
  pipeline, CLAUDE.md, and state.md; the historical decisions/experiments keep
  their `sections-v2` mentions (append-only — that was the name at the time).
- **v1 working files scrubbed:** the old `sections/` transcription and the v1
  repair scripts in `tools/` (D3: "mine, then retire") are deleted from the
  working tree. README rewritten to describe the v2 mechanical pipeline.
- **D5 is preserved, not violated.** The verifier calibrates against git REFS
  (`f60899a`, `fb483fb`, …) via `sections_at_ref`, not the working tree — and
  those refs still contain v1 in full. Deleting v1 in a *new commit* leaves the
  labeled-defect corpus intact; only *rewriting history* would break it, which
  we do not do. `extracted/` (per-page renders + oracle ground truth) and
  `source.pdf` are kept — shared infrastructure the v2 pipeline depends on.

Gate after the move: 0 majors / L1 31 / T1 70; seams 0; site builds clean.
Still nothing pushed (D13) — publishing remains an explicit owner step.


## D29 — multi-panel figures render as one card (render-step grouping) (2026-06-11)

A multi-panel figure (stacked chart panels) extracts as N separate image
strips. The PDF also repeats the figure's title as a thin running-header strip
atop each page the figure spans; that strip extracts as its own short-wide
image (e.g. `p151-1.png` 468×33, `p250-1.png` 446×22). Rendering one card per
image left those title strips as standalone boxes that read like headings
(owner flag, p.151). Only 2 such strips exist, but the underlying issue —
multi-panel figures fragmenting into N boxes — is general (7 multi-image groups).

**Decision: group consecutive figure images into ONE card at the render step**
(`site/src/lib/markdown.js`), not in the markdown. The `sections/*.md` stays
faithful (one `![]` per image); `rehypeArticle` merges adjacent image
paragraphs into a single `<figure>` and wraps all panels in a new
`.figure-card` (the card chrome moved off the per-image `.figure-zoom`, which
stays the per-panel lightbox link). The merge **stops at a page marker**, so a
figure spanning pages becomes one card per page with the `p.NNN` deep-link
correctly placed between them — and a repeated title strip always lands in the
same card as its same-page charts. Also stops at a caption or any non-image
block, so distinct back-to-back figures never fuse.

Render-only: markdown and the verifier gates (which compare md/extraction to
the oracle, not HTML) are unchanged — 141 figures → 141 single cards, build
clean. Considered but rejected: a pipeline flag to un-box just the 2 title
strips (treats the symptom, not the fragmentation) and dropping the redundant
title strips (less faithful; the title is part of the figure graphic).


## D30 — internal vs external links: underline style (2026-06-11)

Body links now signal their destination through underline style: **internal
section cross-references are dotted** ("jumps within this page"), **external
citations stay solid** ("leaves the archive"). The brown link colour is
unchanged for both — no second hue, keeping the warm palette intact.

- **Owner chose subtle.** Mocked up arrow markers (↗ on external) and a § glyph
  on internal; owner rejected both as "a little too much" — the source text
  already writes some refs as '§2.3.5', so our own § would double up. Just the
  underline-style difference.
- **CSS-only, scoped to `.article`.** `a[href^="#"]` → dotted, `a[href^="http"]`
  → solid. Excludes heading anchors (`.hanchor`), footnote ref/backref markers
  (`[data-footnote-ref]`/`[data-footnote-backref]`), page markers, and figure
  links — all keep their own treatment. 120 internal cross-refs affected; works
  in both themes (decoration colour is the already-themed accent). No md/gate
  impact.


## D31 — social-media preview images (Open Graph) (2026-06-11)

Per-page Open Graph / Twitter cards so a shared link renders a branded
1200×630 preview. Astro-native, generated at build time — no runtime/server.

- **Mechanism (confirmed against the live Astro docs via the new docs MCP):**
  a static endpoint `site/src/pages/og/[...path].png.ts` with `getStaticPaths`
  (one entry for home + one per card) returns `new Response(png)`; Astro writes
  a real PNG per path at build (`/og/home.png`, `/og/<vendor>/<slug>.png`).
  Rendering is Satori (element tree → SVG) + `@resvg/resvg-js` (SVG → PNG) in
  `site/src/lib/og.js`, in the site's own palette (warm paper, clay spine, ink)
  and fonts (Fraunces + IBM Plex Mono, static `.woff` — Satori rejects woff2).
  Astro has no built-in OG generator; the `.png.ts` endpoint + getStaticPaths
  IS the native mechanism the docs point to.
- **Tags** in `Base.astro`: og:type/site_name/title/description/url/image
  (+width/height) and twitter:card=summary_large_image, absolute URLs built
  from the configured `site` + `base`, plus a canonical link. New `ogImage`
  prop is a slug ('home' default; the card page passes '<vendor>/<slug>' +
  type 'article').
- **Design:** card = "VENDOR · SYSTEM CARD" eyebrow, Fraunces title, "date ·
  N pages · faithful HTML archive" (N = highest page marker). Home = wordmark +
  tagline + url. Owner judgment calls (reversible): the mockup design as shipped;
  X/Twitter handle attribution skipped (add via twitter:site/creator later).
- Build-only deps (devDependencies): satori, @resvg/resvg-js,
  @fontsource/fraunces. PNGs live in gitignored `dist/` (regenerated each
  build). Render-only — no markdown or verifier-gate impact.


## D32 — production niceties: sitemap, 404, favicon (2026-06-11)

Standard public-site set-up, reviewed against the live Astro docs (docs MCP):

- **Sitemap** — `@astrojs/sitemap` (uses the configured `site`), with a
  `filter` to the HTML pages only (URLs ending in `/` — home + cards), so the
  `og/*.png`, `card.md`, `llms.txt`, and `404.html` routes stay out. A
  `<link rel="sitemap">` is in the head; submit the URL to Search Console when
  the site is published.
- **Custom 404** — `src/pages/404.astro`, homepage type, centered between
  masthead and footer (the body is a flex column for the sticky footer, D-less
  footer commit).
- **Favicon + theme-color** — cream § on a clay rounded tile (owner picked the
  high-contrast tile over the paper-tile and bare-§ options); light/dark
  `theme-color` metas. Generated from the Fraunces § via Satori at build:
  `favicon.svg.ts` (vectorized — § as a `<path>`, intrinsic width/height) and
  `favicon.png.ts` (PNG fallback + apple-touch-icon). **The first cut was a
  static `<text>`-based `public/favicon.svg`, which Safari rendered
  inconsistently (showed on the home tab, blank on the card page):** a
  font-dependent, dimensionless SVG favicon is the trap — a vector path + PNG
  fallback is the fix. Safari caches favicons hard, so a reload/cache-clear may
  be needed to see the update.
- **robots.txt — DELIBERATELY SKIPPED.** On a GitHub Pages *project* sub-path
  site (`malob.github.io/ai-system-cards/`), the authoritative `robots.txt`
  lives at the user-site domain root, which this repo does not control; a
  `robots.txt` under the project path is not honored by crawlers. Do not
  "add it later" thinking it was forgotten.
- Considered and deferred: RSS (premature at one card), image optimization /
  link prefetch / JSON-LD (low payoff for a fidelity-sensitive, ~2-page site).

Config/render only; no markdown or verifier-gate impact.


## D33 — repo public-ready; pipeline is single-card (generalization deferred) (2026-06-11)

Owner-requested hygiene + contributor-readiness pass before publishing.

- **MIT license** for the code (`LICENSE`; owner chose MIT over Apache-2.0);
  reproduced card content stays with its publishers (README "note on content").
- **README rewritten** for outside readers: honest Status, "Running it", an
  "Adding a card" workflow, a `docs/v2` pointer (design history, optional), and a
  License section.
- **Hygiene:** untracked `pipeline/**/__pycache__/*.pyc` and the stale
  auto-generated `docs/v2/worklist.md`; gitignored both. Audited tracked files —
  **no secrets or personal data**, nothing to scrub from history.
- **Acknowledged honestly: the pipeline is a validated SINGLE-CARD proof, not
  turnkey for new cards.** The `CARD` path is hard-coded in `run.py`,
  `tables.py`, and `verifier/calibrate.py`; there's no general new-card
  extraction entry point; the style-manifest + chip vocab are hand-authored per
  card; the verifier gates are calibrated against this card's defect corpus (D5).
  The *site* (`listCards`) is multi-card; the *pipeline* is not. **Generalizing
  the pipeline to arbitrary cards is the next milestone** — left as a documented
  follow-up rather than faked as done.


## D34 — drop the "v2" label from current docs; flatten docs/v2 → docs (2026-06-11)

"v2" was the rebuild's name while v1 still existed; with v1 retired (D28) it's just
*the* project, so the live label was vestigial/confusing. Renamed the current-facing
instances:

- `docs/v2/` flattened into `docs/`; `docs/v2-design-brief.md` → `docs/design-brief.md`.
- CLAUDE.md reframed (no "designing v2" — it's the pipeline) with paths fixed; README
  + living-doc titles (`# Charter`, `# Project state`) de-v2'd; functional path refs
  fixed (worklist.py output, mutate.py default, experiment re-run commands).
- **Left the append-only history intact (owner's call):** the v1/v2 mentions inside
  `decisions.md` (D1–D33) and the experiment writeups stay — they record the v1→v2
  transition (e.g., D28 "v2 is canonical"), and that was the name at the time. (So
  D33's `docs/v2` path mentions, written just before this rename, are now historical.)
- Card content's own "v2" and `pnpm-lock.yaml` left alone — not our labels.


## D35 — pipeline is document-specialized; "one pipeline vs per-document" is open (2026-06-11)

The pipeline is **heavily specialized to the first document** — its chip vocabulary,
table shapes, transcript styles, the hard-coded card paths, and gates calibrated to
*its* specific defects. It likely won't generalize cleanly even to Anthropic's *other*
system cards, let alone other companies'. It's a strong starting point, not a general
tool, and we don't pretend otherwise (README + CLAUDE.md say so).

**Next milestone, empirical:** convert a *second* document and find out whether one
shared pipeline (with per-card config/manifests) can serve many, or whether each
document needs its own pipeline. The answer is genuinely unknown until we try — this
supersedes the looser "just generalize the hard-coded `CARD` path" framing of D33
(that's necessary but probably not sufficient).

Shipping the first card now (owner: "good to ship") does not depend on resolving this.

## D36 — extracted/ carries only current-process data; dead v1 artifacts removed (2026-06-11)

Narrows D5. D5 forbade cleaning `cards/*/*/extracted/` because the build's artifacts were
calibration/provenance. But the calibration corpus is really the **pre-fix git refs**
(`f60899a`, `fb483fb`) + the retired `tools/` — both intact in git history — not the
working tree. And only one file in `extracted/` is read by the current pipeline:
`figures-map.json` (by `run.py` + `calibrate.py`). Internal links resolve from the oracle's
`DEST:N:Y` placeholders, not from a separate dump.

So, per the owner (dead files confuse both humans and future AI sessions — "if they're not
in any way part of the current process, they shouldn't be here"):
- **Moved** the still-useful figure-extraction script `process_assets.py` →
  `pipeline/generate/extract_figures.py` (code belongs in `pipeline/`, not a card's data
  folder; dead `links.json`-writing half trimmed; header documents the flow).
- **Removed** `extract_internal_links.py` + `internal-links.json` (superseded by the
  oracle), `verify_coverage.py` (v1-era one-off), and `text-raw.txt` / `text-layout.txt` /
  `links.json` (unread `pdftotext` / URI dumps). All recoverable from git, regenerable from
  `source.pdf`.
- **Kept** `figures-map.json` (live input) + `images-list.txt` (the figure script's
  inventory input); `pages/` renders stay gitignored.

D5 still holds for what matters: never rewrite the pre-fix refs or `tools/`.

## D37 — publisher revisions: re-convert wholesale; page links pin to the archived PDF (2026-06-12)

Anthropic shipped a revised system card (June 11: changelog page + minor corrections +
frontier-LLM-safeguards rewrite; 317pp, was 319 — pagination shifted) and gave us the
**stable canonical URL** for "whatever the most recent PDF is" (Drake Thomas, Anthropic).
Policy decided with the owner:

- **Re-convert wholesale, never patch:** swap `source.pdf`, remap each section's
  `pages A-B` header via the doc's own TOC (geometry-verified), re-extract everything
  (oracle, renders, figures, docling tables), regen, re-gate. The revision converged at
  the same baseline (0 majors / L1 31 / T1 70) with `accepted.json` pages remapped (−1).
- **Links (owner):** the header "Original PDF" points at the publisher's **stable
  canonical URL** (`meta.source_url`); the per-page `p.N` deep links point at the
  **archived in-repo copy** — they must match the conversion's pagination even if the
  publisher revises again. The repo keeps the PDF version the conversion was built from.
- **The changelog page is content** — converted like any other page (and the verifier's
  old "p.2 = title furniture" exclusion is now p.1-only; p.2 is gated).
- Revision deltas verified item-by-item against the publisher's own changelog before
  shipping (all 7 items confirmed in the diff; remaining churn = pagemark renumbering,
  figure re-paths, and the en-GB→en-US sweep).

## D38 — per-card pipeline targeting: CARD env + cardcfg.py (2026-07-25)

Second document arrived (Claude Opus 5 System Card, 2026-07-24, 193pp) — the D35
generalization question got its empirical test. The card the pipeline targets is now
selected by the `CARD` environment variable (`CARD=anthropic/claude-opus-5 uv run …`),
resolved by `pipeline/cardcfg.py`; default remains `anthropic/claude-fable-5` (the
calibration corpus's card, D5). Per-document constants come from the card's own files —
`meta.yaml source_pages`, `style-manifest.yaml document.toc_pages` — never from code.
Caches are per-card (`pipeline/.cache/<vendor>-<slug>/`). `accepted.json` moved from
`pipeline/verifier/` into the card directory (it is card data: that document's
owner-accepted majors). Regression bar for every pipeline change since: **fable-5
sections byte-identical + gate at baseline** — held throughout.

## D39 — assemble reads style ROLES from the manifest; the role vocabulary is fixed (2026-07-25)

The block compiler's style hexes (turn fills, transcript containers, code boxes,
placeholder green, heading gray) were module constants — correct only for the first
card. They now load from the card's `style-manifest.yaml` (D16 made the manifest the
signal→role authority; this makes the assembler actually read it). The role VOCABULARY
is fixed in code (`heading`, `transcript-commentary`, `transcript-container`,
`turn-assistant`, `turn-user`, `code-block-bg`, `example-box`, `placeholder`); the
hex→role mapping is per-card config. This mattered immediately: opus-5 reuses fable-5's
hexes for different roles (#e2decf: turn-user there → table row-label tint here;
#141413: chart panel → table header fill; #4d4c48: figure legend → table sub-header).

## D40 — opus-5 onboarding: sections from the PDF's own bookmarks; turn-label grammar (2026-07-25)

- **Section files bootstrap from the PDF bookmark TOC** (level-1 entries), one file per
  top-level section, split at page-top level-2 boundaries when a section exceeds ~40pp
  (06a/06b at 6.5, 08a/08b at 8.12). All opus-5 top-level sections start on fresh pages,
  so ranges are non-overlapping — none of fable-5's shared-boundary-page machinery
  engages (it remains for cards that need it).
- **A merely-bold line is not a turn label.** Opus-5 turn bubbles carry whole bold
  paragraphs; fable-5's "any bold lead starts a new turn" heuristic shredded them. New
  turns start on role change, bubble-identity change (innermost turn-fill box), or a
  label GRAMMAR match: `[Bracket label]:` (≤30 chars) or a short bold run-in ending at a
  colon (`Assistant, turn 146:`). Green placeholder pills that are bracket-only lines
  (`[tool use]`) stay pill bodies, never labels; label-less bubbles emit `label=""` and
  the verifier re-emits nothing for them (this also removed 4 false minors from
  fable-5's typed baseline: 70 → 66).
- **Opus-5 typed residuals (gate at 0 majors, T1 ~41 minors, pending owner
  acceptance):** docling table character normalization (curly quotes/dashes → ASCII in
  cell text, ~27 flags, same class as fable-5's accepted p.243 family — candidate for a
  future tables.py repair benefiting both cards); literal markdown-in-transcript
  projection nits (`` `WebSearch` ``, `<answer>`, `<score>`, `<result>`); T2
  page-attribution spill at table seams and the p.191–193 'None' cells.

## D41 — shared docling-glyph repair approved: tables restore true glyphs from the oracle (2026-07-25)

Owner-approved (review walkthrough, 2026-07-25): build the shared `tables.py`
repair that replaces docling's ASCII-ized cell text (straight quotes, hyphens)
with the oracle's true glyphs (curly quotes, en/em dashes). This deliberately
CHANGES fable-5's D28-canonical `sections/` output — the p.243 T1 family and
kin are defects, not canon; D28's freeze governs unexplained drift, not
owner-approved fidelity fixes. Both cards' typed T1 baselines drop accordingly
(re-measure at the gate after the repair; spot re-sweep the affected pages).
The verifier calibration corpus (D5 refs) is untouched.

## D42 — owner adjudication of the opus-5 deferred minors: fix all (2026-07-25)

Review walkthrough (one item at a time, PDF crop vs preview side-by-side).
All eight deferred items approved for class-level fixes: D41 glyph repair;
italic-in-table-cell; p.75 duplicate-cell-text bold matching; p.31 stacked
cell lines → <br> (conservative geometry, owner asked for regression
vigilance); p.64–65 indented quotations → blockquote; pp.191–193 code-box
language chrome → fence info string (verifier projection typed accordingly);
p.85 mono-box blank lines from line-grid gaps; p.138 .hl coalescing across
line wraps (hl-scoped, code marks stay split). The p.31/p.64 heuristics and
any fable canon changes are guarded by per-fix both-cards diff review +
gates + spot re-sweep. Push: owner reviews batch results first, then pushes
(D13 unchanged).

## D43 — tables serialize one <tr> per line (2026-07-25)

Owner-approved whitespace-only canon change (supersedes D28's one-line table
form). The row is the unit agents grep, git diffs show, and viewers truncate
at; one-line tables made all three opaque (the D42 fix audits needed
char-level diff scripts for exactly this reason). Only exact `</tr><tr` seams
split; marker-carrying seams (`</tr><!-- p.N --><tr>`) stay on one line so
downstream marker regexes are untouched. Proven newline-collapse-identical
across all 17 changed files; gates/seams at baseline; DOM table/row/cell
counts unchanged; the fnref-shim anchor moved to the table's closing line
(mid-table lines now exist). Verifier untouched (its table patterns were
already re.S).

## D44 — third card: the archive accepts non-system-card safety documents (2026-08-14)

The owner handed the pipeline Anthropic's **Risk Report: August 2026** (public
redacted edition, 186pp, published 2026-08-14 — an RSP v3.4 company-wide risk
assessment, not a model card). Scope follows the hand-off: the archive carries
AI-lab safety documents generally, with system cards as the founding type.
Consequences:

- **Slug convention for periodic documents:** `risk-report-YYYY-MM` (sortable;
  these recur every 3–6 months per the RSP).
- **`doc_type` meta field** (default `System Card`): drives the card-page
  eyebrow and OG-image label ("Anthropic · Risk Report"). Both system cards
  unchanged.
- Same Google-Docs-export family as both system cards — the D35 within-family
  answer held again: per-card config (manifest, stubs) plus four class-level
  generalizations (D45), zero per-instance fixes. Same-day onboarding:
  census → manifest → stubs → assemble → 0 majors in one fix batch.

## D45 — risk-report onboarding generalizations: footnote region, orphan refs, table links, in-box lists (2026-08-14)

Four defect classes surfaced by the first gate run (25 majors), all fixed at
class level in `pipeline/`, both system cards regen byte-identical:

- **Footnote-marker gate y>0.6H → bottom contiguous small-font region walk**
  (oracle). This document's footnotes quote whole paragraphs and fill more
  than the bottom 40% of a page (pp.50, 117); the absolute-height gate missed
  their markers. The region walk keys on structure, not height.
- **Orphan footnote refs are a source-defect class.** p.126 carries a
  superscript "18" between fn57 and fn58 with no def anywhere — a stale
  paste artifact in the SOURCE (its number collides with the unrelated §2
  fn18, so document-wide def existence is not enough). Rule: a ref with no
  def on its own page whose number falls outside the def-sequence bracket
  around that page is orphaned — rendered as a plain `<sup>N</sup>` (a [^N]
  would print literally or mislink), FN1-classified as a declared
  source-defect minor (cf. `source-defect-unresolvable-dest`). In-band refs
  with missing defs still flag major (extraction-failure recall preserved).
- **Links inside docling table cells** (`tables._inject_links`): re-attached
  per-cell from oracle link rects, entity-/tag-tolerant anchor matching,
  never straddling a td boundary; the oracle's per-page same-URI anchor
  merge is undone by k-fold periodicity (two identical links in one table
  arrive as one doubled anchor). Goto links carry the DEST placeholder;
  run.py resolves the HTML form like body links; mdproj collects table
  anchors for L1. First card with links in tables — neither system card has
  any (their sections are the regression proof).
- **List items inside turn/transcript bubbles** (serialize): a LIST_MARKER
  line inside a bubble opens its own segment and renders as a markdown item
  (tight list); the §2.24 audit-rubric bullets had flattened into prose
  (ST1 12→2 on p.85).

Also: mutate.py results are per-card files now (`results-<vendor>-<slug>.json`)
and classes with no eligible section (chips here) report n/a instead of
crashing; the plain `results.json` remains the fable-5 calibration record.
Risk-report mutation recall: loss classes 100%, structural splits 50–62% —
the calibrated band (ST skips table pages by design; sweeps are the backstop).

## D46 — risk-report sweep round 1: nine fix classes; extended link resolution is a manifest knob (2026-08-14)

Experiment 11 (the layer-2 sweep on the third card) found ~40 distinct majors
in 9 mechanical classes — all invisible to the gates by design (tables,
anchors, styling). All fixed at class level; full table and root causes in
`docs/experiments/11-risk-report-sweep-round1/README.md`. Notables:

- **`link_text_resolution: extended`** (style-manifest `document:` block):
  Claim-number/Appendix/unique-title/pooled-split-half resolution for
  internal links. This document's dest coordinates are sloppy enough to SWAP
  the Claim 6/7 links and land 'Appendix 6.4' on the redacted 6.3 stub. The
  knob is per-card (D16 scoped idiom) because the same rules would re-anchor
  a handful of certified fable/opus links — likely improvements, but canon
  changes needing owner adjudication before enabling there.
- **Table-repair guards** (ownership, y-band anchoring, width authority,
  fragment-or-scramble proof): the §6.6/§2.23 damage was inflicted by the
  REPAIR chain itself over-extending and mis-merging — raw docling was
  often clean. The guards are structural (span geometry), not per-instance.
- **The regression net earned its keep**: four intermediate fix attempts
  broke system-card canon (fnref styling leak, overflow over-merge ×2,
  full-width bold split on the opus welfare run-in, split-cell region
  upgrade) and were caught by byte-identity within minutes each.

Deferred typed minors (owner-visible, README §Deferred): p.13 cell-paragraph
merge, p.153 shallow-indent quotes, p.36 code-span color, footnote URL wrap
spaces, p.42 blockquote-wrapped sub-list.

## D47 — a styling rule reads per-instance oracle evidence, never a class-wide sample (2026-08-15)

**Decision.** When a rule decides how to render a *styled* construct, it must
consult the oracle span for THAT instance. A rule may not generalize a
weight/colour/size reading from the handful of instances that motivated it.

**What forced it.** The round-3 fix "footnote superscripts are lifted out of
bold label runs — the PDF sets them at regular weight" was a whole-table
regex with no span access. The premise held for the three risk-report cells
that prompted it and was false elsewhere: across the corpus 9 of 205 in-table
footnote refs are set in `Lora-Bold` (fable pp.48/50/94/251/252, opus p.148,
risk-report pp.22/25/115), and the rule de-bolded four of them. Nothing
caught it — the gates count refs and tokens, not their weight; the sweeps
had been told the premise as fact. The certified-card regression sweep found
it, three inspectors independently, from the PDF.

**Now.** `tables._lift_regular_sups` matches each marker to its own fnref
span by digits and lifts only on that span's `bold` flag; no span, or
conflicting spans for one number, leaves the markup alone. Four cells
reverted to bold-inclusive, three genuinely regular ones stayed lifted.

**Consequence for process.** A fix's commit message is not evidence. Round
3's message stated the regular-weight premise, and the regression rulebook
inherited it as background — the wording that survived ("Check the PDF: is
the superscript regular weight there?") is what let the inspectors disagree
with it. Prompts must pose the question, never assert the answer; this is
the same independence failure recorded for round 2, in a new disguise.

**Renderer note.** The site pins footnote refs to a uniform mono citation
style (`sup.fn-html a`), so no rendered page changed — the fix is source
fidelity, and it reaches readers through the `.md` exports.

## D48 — `link_text_resolution: extended` stays off for the certified cards; the open question from D46 is closed (2026-08-15)

**Decision.** Leave the knob off for fable-5 and opus-5. Keep it on for the
risk report. D46 left this open on the belief that enabling it would
re-anchor "a handful" of certified links, needing owner adjudication.

**Measured, not assumed.** Enabling it on both certified cards and
regenerating changes **zero bytes** of either card's `sections/`. There is
nothing to adjudicate. This is consistent with the regression sweep's link
audit: after the D47-adjacent coordinate fix, all 94 number-named anchors on
those cards resolve identically by geometry and by text, so the extended
rules have nothing left to correct.

**And the converse: the risk report still needs it.** Turning it off there
and regenerating misroutes four links even with correct coordinates —
`Claim 6` lands on "Claim 7: Threat modeling is sufficient", `Claim 8` on
"2.15 Pathway-specific risk assessments", `Claim 3` on the 3.1 subsection,
and a `below` fragment one level too deep. So the two problems the knob was
built around are genuinely separate: the bottom-up/top-down coordinate bug
(now fixed, global) and this document's own sloppy destination placement
(per-card, still real). The D16 scoped-idiom framing holds.

**Method note.** Both directions were tested by flipping the manifest,
regenerating, and diffing — the same byte-identity net used for pipeline
changes, pointed at a config question. Config knobs left "open pending
adjudication" should be measured this way rather than carried as open items.

## D49 — verifier success is fail-closed; acceptances are exact findings; mutation recall has committed floors (2026-08-15)

**Problem found during maintainer takeover.** `calibrate.py` printed majors but
returned success, so neither a shell caller nor CI could distinguish a clean gate
from a failed one. Its acceptance key was only `(invariant, page)`: one Fable p.37
entry silently covered two distinct T1 findings and would also have covered any new
T1 major on that page. Two other entries (pp.55/56) no longer matched anything, yet
stayed silently active. `generate/run.py` only printed the follow-up verifier command,
and the Pages workflow built without running Python verification.

**Decision.** An acceptance is one complete observed major finding. Its strict entry
contains `invariant`, `page`, `severity`, `detail`, and the SHA-256 of their canonical
JSON. Only majors may be accepted; malformed, duplicate, fingerprint-mismatched, and
(on an unfiltered current `WORKTREE` run) stale entries are configuration errors.
Matching consumes one occurrence, so duplicates cannot hide behind one acceptance.
Historical and partial runs do not require every current acceptance to appear because
they intentionally observe only a different state or slice.

The generator remains generation-only, but its printed handoff is now safe: it
preserves the selected `CARD`, and `--all` points to the unfiltered `WORKTREE` gate.
Page/seed runs continue to print an absolute-directory + `--sections` partial check.
Previously an ephemeral `CARD=… run.py` invocation printed a command that could fall
back to Fable's oracle, and even `--all` incorrectly suggested partial-gate semantics.

`calibrate.py` now exits 1 for any unsuppressed major and 2 for acceptance
configuration errors. `--report-only` is the deliberate diagnostic escape hatch for
majors; it does not relax configuration errors. The migrated Fable file contains the
three exact current T1 findings and no stale entries. A deliberate duplicate-marker
probe produced `P1 major 1` and exit 1, then the same probe with `--report-only`
produced exit 0.

**CI consequence.** The reusable fast workflow runs verifier unit tests, the full
gate and seam audit for all three documents, and a clean production build. Pull
requests and non-main branch pushes invoke it directly; the Pages workflow invokes
it as a dependency, so failure skips both the artifact build and deployment. Pages
and OIDC write permissions exist only on the final deploy job. Tool versions are
pinned at Python 3.12, uv 0.12.1, PyMuPDF 1.28.2, Node 22, and pnpm 11.

**Mutation consequence.** `mutate.py --baseline` enforces the exact class set,
expected invariant, sample count, and a non-decreasing caught count; improved recall
passes, while per-site detail movement is evidence rather than a false failure.
Current 8-trial/seed-5 floors are Fable 86/96 (12 classes), Opus 72/88, and Risk
Report 74/88 (11 classes each; chips not applicable). A separate scoped-push/PR,
weekly, and manual workflow runs these slower checks; its card-input scope is the
complete `cards/**` tree.

## D50 — the shipped mechanical compiler supersedes the pre-build JSON/LLM architecture (2026-08-15)

D1/D2/D7/D9/D10/D14 were pre-build decisions and remained written as current
architecture after the implementation took a different, successful path. The
canonical artifact is the tracked `sections/*.md`, produced by mechanically assigning
PyMuPDF/docling facts to transient typed block dictionaries and serializing them
directly. Astro projects the markdown to HTML, `card.md`, `llms.txt`, social assets,
and search. No canonical JSON tree, schema gate, judge-model triage, LLM
transcription/semantic proposal, N-version conversion, post-acceptance hand-edit
phase, or free-form polish pass shipped.

The independence principle survives in its built form: mechanical major findings gate
within each invariant's documented scope; rulebook-driven inspectors compare PDF,
markdown, and live DOM but report only; the orchestrator alone implements class-level
fixes; the owner adjudicates true editorial choices and performs the final scroll.
This decision supersedes D1's artifact
mechanism and the incompatible mechanisms in D2/D7/D9/D10/D14, not the goals of
typed structure, source provenance, or layered verification that motivated them.

## D51 — strengthen verification authority before changing the canonical representation (2026-08-15)

Settled through the adversarial two-model review recorded in
`docs/architecture-review-exchange/`; the operating synthesis and experiment kill
criteria are in `docs/architecture-roadmap.md`.

**Finding.** The three-card mechanical generator is deterministic, byte-reproducible
under measured current inputs, free of executable card-slug branches, and adequately
served by Markdown as its accepted prose artifact. The dominant measured risk is
instead correlated verification authority: site and CI card inventories diverge;
generator and verifier share TOC, figure, table-scope, and semantic-zoning inputs;
internal destinations and some structural mutations do not block; table pages receive
broad T1 demotion; and candidate extraction/projection replay is incomplete. The
published portable-Markdown table-footnote path has one demonstrated defect. No
source-content defect was demonstrated in canonical sections or main HTML; 19 hidden
table-zone residuals remain unadjudicated.

**Decision.** Close release-inventory and portable-projection defects first, then
strengthen independent expectations and split raw observations from derived
annotations before broad refactoring. Keep PyMuPDF as the versioned primary
born-digital observer, Docling as a pinned table-structure candidate, and tracked
Markdown canonical for prose. Use separate fast replay and cold extraction CI lanes.
An ambiguous-construct inventory may be adjudicated and tracked, but detector
disagreement widens scrutiny and never weakens a general invariant.

Do not adopt a whole-document semantic IR, `DoclingDocument`, Pandoc, a producer
plugin layer, or a general rule DSL now. A persistent typed table grid is conditional
on independent verifier/generator experiments showing material topology,
repair, or provenance benefit. A whole-document IR is reconsidered only after a
measured non-table projection/bootstrap/provenance failure that cannot be gated at a
narrower boundary; absent such a trigger it is rejected, not indefinitely deferred.

Every future rule or architecture claim must demonstrate mechanism and accepted or
rendered consequence, check redundant semantic channels, distinguish a blind spot
from a present defect, and attempt to refute itself. Rules require positive and
nearest-negative fixtures, blocking mutation evidence, visible fire counts, and
full-corpus replay before their scope grows.

## D52 — site discovery is gate discovery; portable table footnotes are a tested projection (2026-08-15)

The owner authorized the first D51 hardening package. Its two leading findings are
closed locally without changing canonical `sections/*.md` or the main HTML edition.

**Release inventory (F34).** The site and fast verifier workflow no longer maintain
separate card lists. Dependency-free `site/src/lib/card-inventory.js` is the shared
repository discovery primitive: production `listCards()` consumes it, and
`site/scripts/card-matrix.mjs` emits the Actions JSON matrix. The workflow refuses an
empty inventory and fans every discovered `cards/<vendor>/<slug>/meta.yaml` out to one
full gate + seam job. A test creates a synthetic fourth card and proves it appears
automatically while no-meta/nonexistent directories do not. Adding another workflow
literal is specifically rejected: it would repair one instance while preserving the
authority split. The slower mutation workflow remains baseline-explicit because a new
card has no accepted mutation floor until onboarding establishes one.

**Portable table footnotes (F36).** GFM does not parse `[^N]` inside raw-HTML table
cells. The existing HTML projection already bridged those references; portable
full-card and section exports now use the same table scan in portable mode. Visible
table references become explicit anchors, and standard-hidden GFM shim references
immediately after the table keep definitions, document-order numbering, and distinct
repeated-reference backlinks alive under the supported renderer. The HTML mode is
behavior-preserving. Tests cover a synthetic repeated table-only reference followed
by prose, an actual Fable full-card + standalone-section export, and every current
card/section export; all built exports contain no unresolved `<sup>[^N]</sup>` table
reference.

The reusable verifier workflow runs these site tests before its production build.
Local evidence: inventory tests 2/2, export tests 3/3, production build 599 Pagefind
records, Action syntax/YAML clean, all 15 verifier unit tests pass, all three full
gates remain at their certified counts, and all seam audits remain zero. This closes
D51 phases 0 and 1 locally. Hosted dynamic-matrix execution remains unproven until an
owner-authorized push; D13 is unchanged.

## D53 — L2 binds source destinations to canonical and final-DOM targets (2026-08-15)

D52's hosted uncertainty is closed. Commit `685cba6` reached `origin/main`, and Pages
run [31917054001](https://github.com/malob/ai-system-cards/actions/runs/31917054001)
completed the shared inventory, all three parallel full-gate + seam jobs, verifier
tests, site tests/build, and deployment for that exact commit. That run proves phases
0 and 1 on hosted runners; the L2 work below is newer local work and is neither pushed
nor deployed.

**Source-first destination authority.** L2 reopens and hashes the archived
`source.pdf`, reads `/GoTo` annotations directly, accepts source heading identities
from the PDF outline plus printed heading geometry, and pairs source and canonical
link occurrences without consulting their destinations. It does not import generator
resolution or slug code. Each tracked `l2-links.json` binds its zero-flag expectation
set to the exact source SHA-256, aggregate canonical-sections SHA-256, and every
section SHA-256. The fast gate regenerates and byte-compares that artifact; the site
loader independently recomputes the hashes and fails closed on missing, stale,
wrong-card, nonzero-flag, or incomplete artifacts.

**R2 is settled.** A broken source named destination remains an L1
`source-defect-unresolvable-dest` minor whether or not recovery is possible. The web
edition may recover it only when the printed anchor uniquely identifies one accepted
source heading, and L2 verifies that identity. Otherwise the anchor is plain text;
`href="#"` is never an acceptable destination. Whether to add a visible *sic*-style
annotation remains a separate, nonblocking D17 presentation question.

**Projection authority.** The site parses serialized article HTML with HTML5
tree-building rather than inspecting the Markdown/HAST producer tree. It checks every
canonical authored fragment link in body and relocated-footnote lanes, every
source-derived expected target, and the complete rendered-page fragment graph for
missing, inserted, reordered, repointed, empty, malformed, dead, ambiguous, or
duplicate targets/ids. A synthetic wrong-but-existing target proves that the
source-derived expectation catches what existence-only link audits cannot.

**Evidence.** All three source-first gates have zero L2 majors: Fable has 108 authored
destinations, Opus 54, and the Risk Report 121 logical / 123 authored occurrences.
All 285 authored occurrences have source expectations. Twenty-seven known historical
wrong-target fixtures replay 27/27 as occurrence-tied L2 majors. Site tests pass 11/11;
the production-page audit observes 1,716 ids and 1,506 fragment links with zero
findings. The Python verifier suite passes 38/38. R2 raises Fable's truthful L1 minor
baseline from 31 to 34 and intentionally changes one p.99 canonical line by rendering
the publisher-broken empty-fragment link as plain text. Opus and Risk Report sections,
the other full-gate residuals, and all three zero-seam results are unchanged.

`mutate.py` now includes `repoint-link`: it preserves a valid internal link and points
it to a different existing heading, so an existence-only audit stays green while L2
must block. It scores 8/8 on every card. The regenerated seed-5, eight-trial floors are
Fable 95/104 (91.3%, 13 classes), Opus 80/96 (83.3%, 12 classes), and Risk Report
77/96 (80.2%, 12 classes). This is a one-time baseline shift to a separate,
digest-derived RNG stream per class; adding a future class can no longer resample
unrelated classes. Class identity, invariant, sample count, and non-decreasing caught
count remain CI-enforced.

This implements D51 phase 2 locally. Phase 3 is next; the L2 source hash does not by
itself complete extraction/cache provenance (phase 5), and the internal-link DOM lane
does not complete the all-projection/bootstrap work in phase 9.

## D54 — Phase 2 is deployed after hosted fast and mutation gates (2026-08-15)

The owner authorized a direct push after the local and independent adversarial gates
were clean. Implementation commit `ff9b6e3` reached `origin/main`. GitHub Pages run
[31919737114](https://github.com/malob/ai-system-cards/actions/runs/31919737114)
completed successfully: dynamic card discovery, 38 verifier tests, 11 site tests and
the production/full-page link build, all three full verifier gates, tracked L2
artifact byte comparisons, all three seam audits, Pages packaging, and deployment
passed for that exact commit.

The deliberately separate, slower mutation run
[31919737009](https://github.com/malob/ai-system-cards/actions/runs/31919737009)
also completed successfully for all three cards. This proves the committed Fable
95/104, Opus 80/96, and Risk Report 77/96 floors—including `repoint-link` at 8/8
each—on hosted runners. Live smoke checks returned HTTP 200 for the home page, every
card page, `llms.txt`, and Fable's `card.md`; Fable's repaired p.99 sentence is present
as plain text and no `href="#"` remains on the page.

D51 phase 2 is therefore deployed, not merely implemented locally. Phase 3 is next.
The mutation workflow remains intentionally separate from the faster Pages dependency
chain, and current `/GoTo` coverage is proven for the Anthropic Google-Docs-export
family; a different producer remains a later portability test rather than an implied
current capability.

## D55 — phase 3 separates source authority, projection authority, and release behavior (2026-08-15)

The owner explicitly rejected a one-off repair for the footnote-shaped symptom. The
problem was broader: several checks could agree with generation because both inherited
the same exclusion, zoning, or extraction decision. Phase 3 therefore changes the
authority structure of the release gate without changing the accepted documents.

**Pages and figures now start from the PDF, not generator metadata.** Every PDF page
and every raw raster occurrence is required by default. A reviewed
`source-inventory.json`, bound to the exact PDF SHA-256, PyMuPDF 1.28.2, observer
schema, and complete source observation, is the only authority for a cover/TOC/blank
page, duplicate draw, or allowed figure skip. Generator `toc_pages` and
`figures-map.json` are claims checked against that observation; they cannot erase
their own expectations. P2 owns page disposition and F3 owns raster identity. Missing,
malformed, stale, duplicated, or unsupported authority fails closed and leaves the
source occurrence required.

**The source expectation is carried through the real renderer.** Each card has a
deterministic `source-projection.json` binding the source PDF, inventory, figure map,
exact canonical-section digest, every page/figure disposition, image bytes and
dimensions, and the ordered page/figure/accepted-skip event stream. The site validates
that artifact strictly, renders the exact supplied Markdown through the production
pipeline, parses HTML with HTML5 tree-building, and requires the built article and
copied PDF/PNG bytes to match. Across the current corpus that is 676 required page
markers, 263 rendered figures, and 267 exact copied source raster assets. An accepted
skip must survive as a hidden, filename/page/reason-bound sentinel in the correct
event position; no current card uses one.

**Authored HTML cannot hide content before the audit sees it.** V1 rejects raw HTML
whose browser semantics hide authored content, including `hidden`, `inert`,
`aria-hidden=true`, closed popovers/details/dialogs, hidden form/control containers,
and the site's hidden classes. Active/reserved markup and inline style are rejected
separately. This policy is tested through the same renderer with `hide-prose`
mutations. It does not claim computed-CSS, responsive-layout, clipping, occlusion, or
viewport visibility; those remain phase 9 browser work.

**Footnote authority no longer depends only on semantic zoning.** The rerunnable F18
fixture proves the old correlated false green: genuine body spans can be re-zoned as a
footnote while the same prose moves to an unreferenced Markdown definition, leaving
the two body streams in agreement. Section-local `definition-without-ref` is now an
independent FN1 major. RF1 separately reopens the PDF without importing `oracle.py` or
generator zones and binds numeric superscript occurrences and smaller, left-margin
bottom-region numeric definitions to canonical occurrences and bodies. Its scope is
deliberately narrow: symbol/letter markers and endnotes are not claimed. The Risk
Report's stray p.126 superscript 18 is excluded only by an exact, source-hash-bound
disposition recording the publisher artifact.

**Severity reflects consequence, not table membership or token count alone.** The
blanket table-zone T1 demotion is removed. Differences of at least three tokens remain
major everywhere; table attribution is diagnostic only. One- and two-token changes to
numbers, dates, units/currencies, negations, and quantified comparators are also major,
including inside FN1 body comparisons. Current production comparisons no longer use
historical quote-style or non-breaking-hyphen calibration folds, and complete hashes
and token counts—not display-truncated samples—bind findings, displacements, and exact
acceptances.

PDF review found no new canonical-content repair. Removing table immunity exposed 22
legitimate table-order projection residuals: 17 Fable, 4 Opus, and 1 Risk Report. They
are exact accepted T1 findings, including Fable p.316's one-token `None` residual,
which correctly remains a critical-negation major before acceptance. Together with
Fable's three earlier visual-order adjudications, the corpus has 25 exact accepted
majors: Fable 20, Opus 4, Risk Report 1. Each `accepted.json` carries the rationale and
full fingerprints. Generic acceptance is forbidden for L2, P2, F3, RF1, and V1;
source/projection exceptions must use their stronger authority, and L2/V1 permit no
generic exception at all.

**Mutation evidence now distinguishes four questions.** The harness combines the
Python source/canonical gates with a persistent Node worker running the production
Markdown transform, HTML renderer, and DOM audit over the exact mutated section bytes.
It records intended-invariant detection, whether that intended finding is major,
whether an unsuppressed major remains after exact acceptances, and whether the
production gate exits nonzero. A strict schema-v2 envelope binds card, seed,
trials/class, class set, invariant, aggregates, and per-trial evidence; there is no
legacy fallback, and output cannot overwrite or alias the baseline. At seed 5 and
eight trials/class, Fable detects 191/200 and major-blocks 185/200, Opus 176/192 and
171/192, and Risk Report 173/192 and 171/192. Across 584 trials: 540 are detected, 518
produce an intended major, and 527 are major-blocked. V1, P2, F3, L2, all critical
T1/FN1 classes, and applicable chip coverage are 8/8; remaining misses concentrate in
ST1/ST2/ST3, L1, S1, and ordinary two-word swaps that are intentionally advisory.
The committed artifacts combine independent per-class runs with the final
hide-image/V1 refresh and pass strict schema validation. One exact 584-trial replay
against the final tree is not claimed locally; the hosted post-push mutation workflow
is the independent completion evidence.

The complete fast release graph is now one pinned command,
`pipeline/verify_release.py`, and full generation prints that handoff rather than a
single-card verifier command. All card gates, artifact comparisons, seams, site tests,
and the clean build pass locally (147 Python tests, 31 site tests). Canonical
`sections/*.md` did not change, and a clean 995-file `site/dist` including Pagefind is
byte-identical to pre-change HEAD. This decision is
implemented locally but not yet pushed or deployed. Phase 4 (ST2) is next.

## D56 — phase 3 is deployed and certified by exact hosted replay (2026-08-16)

The phase-3 implementation landed as `75fd8b9`; the mutation-timeout follow-up made
the deployed HEAD `3d7b851`. GitHub Pages / fast-release run
[31929997079](https://github.com/malob/ai-system-cards/actions/runs/31929997079)
succeeded for that HEAD: the complete verifier dependency graph, all card gates and
seams, tracked L2/source-projection freshness checks, production site tests/build,
Pages packaging, and deployment passed on hosted runners.

The deliberately separate mutation run
[31929996953](https://github.com/malob/ai-system-cards/actions/runs/31929996953)
also succeeded for all three strict schema-v2 baselines. The mutation gate steps took
12m54s for Opus (05:52:08–06:05:02), 20m05s for the Risk Report
(05:52:12–06:12:17), and 37m36s for Fable (05:52:09–06:29:45). Downloaded hosted
artifacts, normalized with key-sorted `jq`, match the committed baselines exactly.
This closes D55's deliberately unclaimed final-tree replay: all 584 trials and their
separate detection, intended-major, major-blocking, and gate evidence are now proven
on the deployed tree.

Run [31928741823](https://github.com/malob/ai-system-cards/actions/runs/31928741823)
was cancelled solely because Fable exceeded the old 30-minute job timeout; Opus and
Risk had already passed, and no detector/baseline failure occurred. The follow-up
raises the mutation job timeout to 45 minutes, after which the unchanged Fable floor
completed normally. Timeout capacity is operational configuration, not verifier
recall, and is recorded separately for that reason.

Phase 3 is therefore deployed and certified, not merely implemented locally. It
changed verification authority and release behavior, not card content: canonical
sections remained unchanged and the complete built site, including Pagefind, remained
byte-identical to pre-phase-3 HEAD. Phase 4 ST2 hardening is next.

## D57 — phase 4 is a structural-family experiment, not an ST2 threshold patch (2026-08-16)

The first spike found that the structural problem is broader than ST2's current
physical-line threshold and table exclusions. The historical reports span occurrence,
containment, list topology, final-DOM parsing, quote ownership, and table-local
structure. Phase 4 should therefore test source-only structural proposals against an
independently parsed final DOM, using geometry only as separately testable evidence;
fallible PDF tags or suspicious context may widen review but never authorize omission.

The eleven tracked records remain investigation notes and replay candidates, not
executable fixtures or an evidence floor. Phase 4 remains advisory: no structural
finding or alignment result gates card content, although observer unit tests run in
the existing release graph. The spike changed no generation, canonical content, or
published output. It may block only after an executable harness catches all eleven
historical candidates and deterministic structural mutations while current-output and
nearest-negative controls stay clean. Detailed evidence, provisional counts,
reproduction commands, and final reduced-tree validation live in
[Experiment 12](experiments/12-structure-authority/README.md).

## D58 — retain rich table candidates in shadow before changing production (2026-08-16)

The owner asked that the table architecture be approached with fresh eyes while the
existing 2,557-line repair pipeline is used as evidence rather than a design template.
[Experiment 13](experiments/13-table-candidate-shadow/README.md) ran four isolated
tracks: a hash-bound legacy counterexample corpus, a dependency-free immutable
`TableCandidate`, a runtime/provenance replay probe, and one typed topology vertical
slice. Nothing under the experiment is imported by production, and no generator,
canonical section, card, site, or release behavior changed.

**Evidence.** A rich Docling `TableData` proposal can be serialized without first
flattening it to HTML. Two offline runs on Fable source p.20 produced identical
deterministic mini-PDF bytes, rich candidate bytes, and complete
source/tool/config/model/schema-bound envelopes in the same warm local runtime. This
is feasibility evidence, not cross-platform or cold locked replay. The legacy corpus
binds 29 unique raw candidates, 32 manifest references, 13 accepted canonical tables,
and five logical multipage shadows. Across all 98 current cache candidates,
`merge_fragment_rows` and `dedup_cascaded_cells` are inert; they require recovered
historical raw positives or retirement rather than automatic porting.

The typed slice covered six source pages and seven tables. One pure, narrowly scoped
missing-rule transform made three PDF-supported header merges. It conservatively
refused a fourth supported span because Docling misassigned `API,` into the lower
cell. No genuine real source-negative occurred in that six-page set, and the geometry
path is conditioned on Docling's candidate bbox and grid. The result is therefore
shadow-generator evidence, not an independent verifier authority or a production
repair model. All 42 experiment unit tests (15 clean-model, 17 reproducibility, 2
legacy-evidence, 8 topology) and the separate 32-locator/13-canonical/5-logical legacy
validator pass.

**Decision.** Pause further phase-4 structural-authority integration and pull the
table extraction/grid shadow experiment forward. Do not adopt a production typed
grid yet. Next obtain genuine source-negative controls, test a typed PyMuPDF
word-to-cell alignment slice, establish clean locked cross-platform replay, and then
compare transform count, order dependence, provenance, and total complexity with the
legacy path. Adopt only if the representation materially reduces net production
complexity or makes repairs and their boundaries demonstrably more local and
reviewable; merely relocating complexity is a failed experiment.

The experiment's 4,169 Python lines are largely defensive provenance probing and
validation scaffolding. They are appropriate evidence machinery, not an
implementation to port wholesale. Production should use an explicit locked
package/model artifact bundle and a smaller adapter. Manual setup that records real
document-specific judgment remains acceptable; separating section-plan input from
generated Markdown is useful cleanup but secondary to the measured table work.

## D59 — keep typed source-word assignment in shadow; model origin before composition (2026-08-16)

Experiment 13's [word-alignment slice](experiments/13-table-candidate-shadow/word-alignment/README.md)
tests exact PyMuPDF words and grid geometry against the clean typed table candidate
without consulting accepted output as truth or importing the legacy HTML pass order.
The source-bound evidence covers 10 cases on nine pages, 790 PDF words, and 274
human-reviewed cell labels. Two fresh offline extraction runs produced identical
bytes for all 10 cases; all five source-evidence tests and all 12 alignment/replay
tests pass. The final 448,460-byte evidence artifact
SHA-256 is `22e2fcb220cd29f03ee1b299c22e05f34759919812a13990a6e40682b20365cc`;
the 138,187-byte alignment artifact SHA-256 is
`c317522f77d91408bc71353695ad6afa490301dd39e7a3cf4d05643704f12e16`.

**Evidence.** One all-or-nothing source-word assignment primitive makes 43
cell-text changes across four tables: Opus p.52 (11), Opus p.53 (15), Opus p.56
table 0 (2), and Risk p.78 (15). Risk pp.79-80 and Fable p.20 are natural
byte-identical no-ops. Opus p.56 table 1 fails closed because three `88% (± 5%)`
words land in an adapter gap; Fable p.94 fails closed because styled superscript text
and the candidate have different token inventories; raw Fable p.95 fails closed on
two atomic-cell ambiguities. After the already-proven topology transform merges the
two p.95 spans, alignment is a clean no-op and its reviewed associations exactly
match. Across the raw cases the 274 labels establish compatible reviewed ranges, not
exact reproduction of every spanning range.

The model therefore demonstrates a local simplification, not a complete pipeline.
Isolated word-ownership errors fit one typed, source-bound primitive. Coupled topology
and assignment defects do not reduce to pass order: even if a future resolver clears
p.56 table 1's adapter-gap payload, the lower `Model` cell remains Docling-observed
rather than adapter-generated, so the current topology rule still refuses the merge.
That distinction belongs in a typed origin/projection overlay preserving source
observations, candidate claims, and derived ownership separately. Do not encode the
missing semantics as another ordered repair pass.

**Decision.** Independent review scored the slice 10/12: 2/2 each for independence,
conservation/fail-closed behavior, natural controls, and provenance/determinism; 1/2
each for locality/order-independence and proportionality/complexity. Its verdict is
**commit the shadow milestone; do not adopt or migrate production**. Retain the
primitive in shadow and do not adopt a production typed grid yet. The model is 652
physical lines (580 nonblank), with roughly 252 physical lines in its two
decision-bearing functions: smaller than the roughly 660-line legacy
alignment core as decision logic, but not yet a demonstrated net complexity win once
the typed/provenance envelope and unresolved composition are counted. Next obtain the
missing natural missing-rule-but-keep-separate and outer-edge controls, test the typed
origin/projection boundary, establish clean locked second-platform replay, regenerate
all three cards in a later migration proof, and compare net deletions and provenance
against the legacy path.

This is shadow-generator research, not production or verifier authority. It changes
no generator, canonical section, card, site, deployed output, or release behavior.
No hosted run, production adoption, or output improvement is claimed.

## D60 — raw-rule origin/projection composes the ruled hard set in shadow, not production (2026-08-16)

Experiment 13's [origin/projection follow-up](experiments/13-table-candidate-shadow/origin-projection/README.md)
tests the distinction identified by D59 without adding another topology-then-text
pass. One generic resolver forms connected components from raw PDF horizontal and
vertical rules, assigns raw PDF word occurrences by full-bbox containment, and only
then compares that derived projection with immutable typed Docling claims. Reviewed
ranges occur only in tests; accepted and generated Markdown are never inputs.

**Evidence.** On the existing 10-case fully ruled hard set, the resolver derives
274/274 reviewed cell ranges and assigns 790/790 source words exactly once. It jointly
resolves Opus p.56 table 1's `Model` rowspan and `API, without a system prompt`
ownership, and resolves raw Fable p.95 without calling the earlier topology or word-
alignment transforms. Fable p.20 and Risk pp.79–80 remain no-ops. Fable p.94 assigns
all words but blocks text materialization because its styled superscript cannot be
flattened losslessly. Risk p.115 is a source-only, fully bounded true blank; no typed
candidate exists there, so extractor origin remains explicitly unknown. Every input
candidate and observed/adapter-gap claim remains unchanged.

The root suite passes 12/12 and the pinned PyMuPDF source-reopening evidence suite
passes 10/10. The compact replay rebuilds byte-identically at SHA-256
`d255e733b26e9a811dbf629e72557c9b5b92a955a4709fd0d3d6c86bbc913b26`;
source evidence is
`37bdedacdaafdf77284c07ca39d88d350c40da89cb5cdec9b8a2634df1029a88`,
the model is
`089cc0d355c9535778ee79457f8dc7e5242aa8a383d184df80d3956a1d9a8924`,
and the replay builder is
`7fb111dd1e00e42fb6420fe57dc1fbdd364c60b03d765bc5ef281e964dbb9b5d`.
Experiment 13 now has 66 main tests plus 15 source-reopening evidence tests; the
legacy validator remains separately clean.

**Decision.** Independent review scored the follow-up 9/12: **commit the shadow
milestone, yes; production adoption, no**. The ruled-set composition result is strong
enough to retain. It does not authorize a production model because the grid envelope
and atomic edges remain candidate-conditioned, the corpus has no natural absent-rule-
but-keep-separate negative, sparse/unruled tables are untested, style/link-aware
serialization is absent, second-platform and different-producer replay are absent,
all-card regeneration has not been attempted, and no measured net legacy deletion has
been demonstrated.

This decision changes no production module, canonical section, card, site, release
gate, deployed output, or website content. No hosted run, full release, output
improvement, push, or deployment is claimed by this documentation closeout.

## D61 — retain the candidate-free ruled census; kill its grid model (2026-08-16)

Experiment 13's [grid-discovery follow-up](experiments/13-table-candidate-shadow/grid-discovery/README.md)
reopened all three archived PDFs without consulting Docling candidates, accepted
Markdown, legacy HTML, reviewed cell labels, or case-specific IDs. Pinned PyMuPDF
`find_tables(strategy="lines_strict", use_layout=False)` proposals were checked
against a distinct PyMuPDF-derived graph of raw stroked `l` segments, with source
observations frozen before a physically separate review manifest. These are two
representations from one observer library, not independent parsers.

**Evidence.** Across 696 pages, the source-only census records 98 multi-cell ruled
regions (40 Fable, 27 Opus, 31 Risk Report), 77 one-cell vector boxes as natural
controls, and 13,607 overlapping source-word occurrences with exactly one cell owner.
It measures exact rule coverage for 1,774 outer and 3,326 present internal atomic
boundary slots. The geometry claim is deliberately only `ruled region`: two observed
grids are publisher-captioned figures rather than tables. The retained source
artifact SHA-256 is
`1775484321573f10691ccd246c21599b197f8f34e2e64e623e0886a77e97e8a1`; its bound
review manifest SHA-256 is
`4b2c064dc8608ebf25948daa9cfe926dd811d28c6ab29bcc3ed7012211c40818`.

The evidence is complete only for the observed ruled family. There is no natural
sparse or unruled table positive and no natural absent-rule-but-keep-separate
negative. All three inputs are from the same Google Docs/Skia producer family and
were replayed on one platform. A real source separator deletion or connector can make
both PyMuPDF-derived representations agree on a coarsened or fused topology. Refusing
materialization is safe, but does not reconstruct the missing truth.

**Decision.** Independent review scored the full slice **7/12**: 2/2 source
independence; 1/2 current-corpus completeness and natural-negative/sparse safety; 1/1
immutable source/review planes; 1/1 deterministic hash-bound label-free replay; 1/2
mutation robustness; 0/1 portability/different producer; 1/1 word conservation and
fail-closed materialization; and 0/2 proportionality/net legacy deletion. The verdict
is **KILL as a model/replay milestone; neither commit shadow nor adopt production**.
The full pre-reduction slice added 3,319 Python lines and about 2.9 MB while deleting
no production code and changing no output. The killed model/replay files were
removed; the retained evidence boundary is 1,662 Python lines and about 2.8 MB.

Retain only the source census evidence extractor, its tests and artifacts, the
evidence README, and the compact decision note. Do not commit the model, synthetic
tests, replay builder, or replay artifact. Before any replacement model, obtain a
different-producer corpus containing sparse/unruled positives and a natural
absent-rule-but-separate negative, then test the smallest source-only rule against
them. If it cannot demonstrate fail-closed behavior and measured net legacy deletion,
keep HTML and refactor the legacy table helpers locally.

This decision changes no production module, canonical section, card, site, release
gate, deployed output, or website content. No push, hosted run, deployment, or output
improvement is claimed.

## D62 — fourth card: Claude Fable 5.1 & Claude Mythos 5.1; three table classes, one list class, four projection classes (2026-09-01)

The owner handed the pipeline the URL of Anthropic's **Claude Fable 5.1 & Claude
Mythos 5.1 System Card** (212pp, cover-dated 2026-09-01, Skia/PDF Google Docs
producer — the same export family as the three certified documents). Slug
`claude-fable-5-1` (version dots become hyphens, sorting after `claude-fable-5`).
Onboarding followed CLAUDE.md steps 1–7 in one session:

- **Census → manifest.** 8 fills / 12 text colors, opus-5-shaped: the same dark
  header, row-label and sub-header table fills, green code text, and `#f1f3f4`
  appendix code boxes; NO chips, NO `#d9ead3` placeholder pills, NO turn labels.
  Two hexes carry roles that differ from opus-5 (D39 normal): `#faf9f5` is the
  unlabeled §6.1.3 prompt/review box → `transcript-container` (the risk-report
  reading, verified on p.93), and `#f3f3f3` is the text-free empty-cell tint of
  the §4 tables → `table-cell-bg` (every rect on pp.60–76 clips no text).
- **Stubs.** Eleven files from the bookmark TOC; §6 (49pp) split at the page-top
  6.5 boundary (p.122); §8 (39pp) kept whole under the >40pp rule. Nameless
  bookmarks (pp.10, 44, 58, 76, 89, 212) are continuation pages, as in D40/D44.
- **Tables.** Docling 2.124.0 over 29 candidate pages from a stroked-rule scan
  (this family draws table borders as strokes, not fills; the census's fill
  classifier cannot see them), 33 tables; pp.93–94 excluded up front because
  their rules are the transcript boxes' borders.
- **Source authority.** Inventory proposal: cover p.1 + TOC pp.6–10, no blank
  pages, no duplicate draws; 206 required content pages, 103 required figures
  (104 raster occurrences; the cover logo is excluded with its page), 0 flags.

The first gate showed 11 majors (9 T1 + 2 TB2). All fixed at class level with
all three certified documents byte-identical after every change:

- **Cascade dedup cuts only at a whitespace boundary** (`tables._dedup_cascaded_cells`).
  A value ending with the next row's value ('100%' over '0%') is a coincidence,
  not a docling cascade; the suffix cut left '10' in two cells of Table 4.4.3.A.
- **Multiset-anchored row rebuild** (`tables._band_by_multiset` → `_rebuild_row`).
  When docling detaches the label's first word AND rotates the values ('Opus 5 |
  100% | Claude 82.1%', p.73; 'Fable 5 88% | (± 6%) | Claude 93% (± 5%)', p.76)
  no cell equals, prefixes, or contains a unique span, so `_row_band` could not
  anchor the row. The row's character multiset still identifies its y-band
  exactly, and `_rebuild_row`'s own multiset guard bounds the repair. It fires
  only when cell contents move — a row it would merely re-space (a wrapped cell
  whose link span sits mid-line) keeps docling's spacing.
- **Rebuilt short rows refill docling's own empty cells by column interval**
  (`_rebuild_row`, `_column_edges`). 'Claude Mythos 5 100% | 0% | | |' (p.75)
  rebuilt to three cells and was refused by the never-fewer-cells guard; the
  shortfall is now accepted only when it equals docling's empty cells and every
  rebuilt cell lies inside one column interval (a straddling cell is still a
  fuse and still refused). The Mythos 5 rows of pp.61/65/69 and the p.78
  'Claude Sonnet | 90.7% 96.9% | 5' row repaired the same way.
- **List re-tiering runs AFTER stitch** (`run.py`). A wrapped item's page-break
  continuation paragraph is a separate block until stitch rejoins it; tiering
  before the join split the item run, and the orphan-indent shift flattened the
  following ■ sub-item to level 0 (p.41→42).

Four verifier-side projection classes then removed false typed minors
(verifier code changed, so the seeded mutation suites are re-run for every card):

- `mdproj`: INLINE tags (a/b/i/u/em/strong/small/span/sub/code/s) strip to
  nothing — a link anchor inside parentheses ('(Section 7.2.1 only)') or before
  punctuation ('Glasswing,') had projected a phantom space; block/cell tags stay
  a whitespace boundary. Risk-report typed T1 minors 21 → 6, opus-5 9 → 8.
- `mdproj`: `__` is bold only at word boundaries (CommonMark intraword rule; the
  production renderer agrees) — 'mcp__claude_ai_Google_Calendar__*'.
- `norm`: ■/□ join the bullet-glyph and list-marker sets, mirroring `assemble`.
- `serialize` + `mdproj`: a source backslash before ASCII punctuation is doubled
  so the renderer keeps it (the corpus's only such sequence: p.96 `\"`); the
  projection reads the pair back as one character.

Five exact T1 acceptances remain, render-checked: Table 7.4.3.A's third row is
cut mid-cell at the p.159/160 page break (seam page attribution; the merged row
is complete), and the p.210 §9.2 code-box label 'None' precedes the page's
table in PyMuPDF's stream order (the fable-5 p.316 / opus-5 pp.191–193 class),
merged with Table 9.1.A's dropped repeated header row. Gate: 0 unsuppressed
majors, T1 4 typed minors; L2 66/66; P2/F3 206 pages / 103 figures / 309 DOM
events; RF1 clean; seam 0. The agent sweeps (experiment 14), mutation replays,
owner scroll pass, and deploy decision follow; nothing is pushed.
