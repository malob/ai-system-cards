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
