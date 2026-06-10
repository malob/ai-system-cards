# Retrospective & v2 design brief: PDF → faithful web rendering

**Audience:** a fresh designer (human or model) tasked with re-architecting the
system-card conversion pipeline to be reliable enough that handing over a new PDF
yields a faithful site with only light spot-checking.

**Status:** v1 shipped one card (Claude Fable 5 & Mythos 5, 319 pp) at
`malob.github.io/ai-system-cards`. It is **much more faithful than the raw
conversion, but not fully faithful** — manual review reached only ~section 6 of 9
before the owner called it, and even within that range some noticed defects were
left unfixed. So there are **known-unfixed defects past ~section 6, and certainly
unnoticed ones throughout**. The §2 taxonomy below lists the defects we *found and
fixed*; it is a lower bound on what v1 gets wrong, not a complete accounting. This
brief is the lived record of what broke and why, and an opinionated proposal for
v2. Treat the proposal as a strong prior, not gospel — the bake-off (§6) is the
load-bearing unknown.

---

## 1. What v1 does (the parts worth keeping)

Pipeline: PDF → mechanical extraction (`pdftotext` plain + `-layout`; `pdfimages`
by page; pypdf `/URI` link dump; `pdftoppm` 150-dpi page renders) → ~20 parallel
LLM agents transcribe page-range chunks to markdown following
`docs/markdown-conventions.md`, each self-verifying with a word-diff against the
text layer → a coverage sweep checks page-marker continuity and distinctive-line
presence → Astro renders `cards/<vendor>/<slug>/sections/*.md` to a static site
(scroll-spy TOC, sidenote footnotes, Pagefind search, `card.md` + `llms.txt`).

**Keep in v2:**
- Markdown as the canonical, human-editable artifact; Astro static render; the
  `card.md` / `llms.txt` machine outputs.
- Per-page figure-image extraction (`pdfimages` worked fine; charts must stay as
  images regardless of how good text extraction gets).
- The directive vocabulary we *evolved* (define it up front in v2): `:chip[]`,
  `:::turn{role,label}` inside `::::transcript`, `:::example`, figure captions.
- The **verification mindset** — but upgraded from coverage-only to structural
  (see §4).

---

## 2. Failure taxonomy (the actual bugs, as evidence)

These are real defects found by the human reviewer *after* conversion, grouped.
The point of listing them exhaustively: almost all trace to 2–3 root causes (§3),
and almost all are **mechanically detectable from a structure-aware extraction**
— i.e. they should have been caught by tooling, not eyes.

### 2a. Page markers (by far the largest category)
v1 represents page boundaries as `<!-- p.N -->` HTML comments the *agent* places
inline. This interacts badly with markdown block structure and was placed
imprecisely. Symptoms and the repair scripts they each needed:
- Imprecise placement — marker snapped to a nearby block boundary, not the exact
  word where the page breaks. (`snap_page_markers.py`)
- Paragraph split across a page break — the continuation rendered as a *separate*
  paragraph. (`join_page_break_paragraphs.py`)
- Ordered/unordered list split — a column-0 marker between items is parsed as an
  HTML block, breaking the list / restarting numbering. (`inline_list_markers.py`;
  an earlier re-indent hack was tried and rejected as fragile)
- Blockquote split — marker between two `>` chunks splits one `<blockquote>` in two.
- Figure-led page — marker stranded in the figure's *caption* below the charts
  instead of at the figure that opens the page. (`anchor_figure_markers.py`)
- Duplicate markers at section-file boundaries (5 pages) → duplicate HTML ids.
- Marker absorbed into a directive attribute (`label="[<!-- p.198 -->…]"`) during
  the transcript conversion, breaking the directive into literal text.
- CSS `:only-child` collapse bug — the rule meant to flatten empty marker-only
  paragraphs also matched normal prose paragraphs whose single inline marker was
  their only *element* child (text nodes don't count for `:only-child`), zeroing
  real paragraphs so following content overprinted them.
- Baseline misalignment — the `font:` shorthand reset `line-height`, so the marker
  sat high relative to its line.
- Glyph mojibake — a `⌐` prefix char got mangled by the encoding/build chain.

### 2b. Formatting / faithfulness losses (agent couldn't see it in text)
- **Internal links missing entirely.** Extraction captured only `/URI`
  annotations; the PDF's internal cross-references are `/GoTo` annotations and
  were never extracted, so ~110 section/phrase links were silently dropped
  document-wide. (Recovered later via `extract_internal_links.py` +
  `apply_internal_links.py`.)
- **Smart chips flattened to bold.** Google-Docs colored "smart chip" labels
  (failure-pattern tags, transcript categories, mitigating-factor strengths)
  carry meaning in their color; the agent saw only text and rendered them as
  `**bold**`. (Recovered via a `:chip[]` directive + per-card color registry +
  `chipify_from_registry.py`.)
- **Transcript turns vs narrator commentary undifferentiated.** v1 put a whole
  transcript in one box with bold-prefix turns; multi-paragraph turns were
  indistinguishable from the authors' framing prose. (Recovered via `:::turn`.)
- **Caption bold-leads dropped** on 4 captions (one chunk's agent), plus one
  over-bold caption — emphasis isn't in the text layer, so it was guessed
  inconsistently.
- Straight vs curly quotes (handled at render with a smart-quote pass).

### 2c. Renderer bugs (the Astro/CSS layer, independent of conversion)
Loose-list spacing inconsistency; row-hover on rowspan tables; duplicate ids;
and a batch of design polish (chips, turn cards, dark-mode figure panels, theme
toggle, the Contents button, the orphan rule above the first heading, anchor-link
placement, `llms.txt` placement). These are normal frontend work; not the focus
of v2's reliability problem, but the **`:only-child` bug (2a) is a cautionary
tale**: derive structural facts in the renderer where you can filter properly,
never via brittle CSS selectors.

### 2d. Process failures (meta)
- Errors surfaced in **one big manual pass at the end**, not during conversion.
- Agents made **silent, inconsistent choices** instead of flagging ambiguity.
- Conventions were **discovered post-hoc** and never fed back into a shared spec,
  so different chunks handled the same construct differently.

---

## 3. Root-cause analysis

**A. We extracted *text*, and forced the agent to re-infer *structure*.**
`pdftotext` yields a flat character stream. Paragraph/list/table boundaries,
mid-sentence page breaks, bold/italic, chip colors, link targets — all had to be
reconstructed by the agent from page images. That reconstruction is lossy and,
fatally, **inconsistent across agents and chunks**. This single cause produces
every item in 2b and the placement guesswork in 2a. Internal links (2b) weren't
even *visible* to reconstruct — they live only in annotations.

**B. Page markers were the wrong abstraction.** Making page boundaries an
*agent-authored, block-level comment* guaranteed collisions with markdown block
structure (all of 2a). Page position is a mechanical fact; an LLM should never
have been placing it.

**C. Validation was coverage-only and end-of-process.** We checked that text was
*present*, never that *structure/formatting* matched the source, and only after
all 21 files were done. Nothing caught a missing link, a flattened chip, or a
split list at conversion time.

**D. No spec, no feedback loop.** Conventions lived in our heads and emerged late;
decisions weren't captured and re-applied, so consistency never accumulated.

**E. The human was the formatting oracle.** Because nothing mechanical knew what
"correct" looked like, the reviewer *was* the test suite. That doesn't scale and
is the source of the slog.

---

## 4. Proposed v2 architecture

One reframe drives everything: **almost everything we hand-fixed is mechanically
extractable, and therefore mechanically verifiable.** Make the extraction
structure-aware, and it serves double duty as the conversion source **and** the
validation oracle — so the PDF becomes its own test suite.

> **Decisions taken (2026-06-09, with the project owner).** The three big open
> questions below are now settled; they're folded into the architecture:
>
> - **Canonical representation = a typed structured document model (JSON), not
>   markdown.** Markdown, HTML, and `llms.txt` become *projections* of the model.
>   Rationale in §4.0. (Owner is not attached to markdown; wants the better
>   representation.)
> - **Triage = amortized human judgment.** Issues surface *during* conversion;
>   the owner decides each *issue-type* once; the decision is written into a living
>   spec; a judge model auto-applies existing rules and escalates only novel
>   issue-types. This implies **staged conversion** (waves / seed-then-bulk), not a
>   simultaneous fan-out, so decisions can feed forward. (§4.3.)
> - **Scope = ground-up rebuild, no carried debt.** Mine v1 for hard-won logic and
>   keep the Astro renderer (as the model→HTML projection); retire the repair
>   scripts after reading them for logic. Blank slate is acceptable where better.

0. **Canonical = a typed structured document model (JSON).** The conversion
   produces a typed tree, not markdown; markdown/HTML/`llms.txt` are serializers
   off it. Block nodes (heading, paragraph, list, **table with real row/col
   spans**, figure[image+alt+caption], blockquote, transcript, **turn**[role,
   label], example, codeblock) and inline marks (text, emphasis, **link**[href,
   internal|external], **chip**[label,color], footnoteRef). Page numbers and
   bboxes are **per-node provenance**, never inline artifacts — this removes the
   entire page-marker bug class (2a) by construction. Borrow the *shape* from
   Pandoc AST / Portable Text but keep it minimal — only node types these docs
   use. Why this over markdown: every v1 escape hatch (raw-HTML tables, chip/turn
   directives, marker comments) becomes first-class; the validation oracle (§4.3)
   becomes a clean **tree-diff** instead of fuzzy text matching; content and
   rendering fully separate. Cost: a small schema + three serializers, and humans
   review via the rendered site + triage tool rather than hand-editing JSON (clean
   markdown is still exported as `card.md`). The bake-off (§6) should inform the
   exact node/mark set — the model should match what the best extractor can give.

1. **Structure-aware extraction backbone.** Replace `pdftotext` with a tool (or
   stack) that preserves, per text span: font/size/**bold-italic flags**/**color**/
   bbox; **link annotations (both `/URI` and `/GoTo`) with rects + destinations**;
   reading order; and table structure. `PyMuPDF` (fitz) provides spans+links+
   positions deterministically in one pass; layout models (`marker`, `docling`,
   `MinerU`) provide tables/reading-order/markdown. The right answer is probably a
   hybrid; settle it empirically (§6).

2. **LLM does the *semantic* layer only.** On top of structured input, the model
   handles what extraction can't decide: is this colored pill a chip and which
   category; where do transcript turns begin/end vs commentary; figure alt text;
   occasional reading-order repair. A much smaller surface ⇒ far more consistent.

3. **Validation in the loop, per page, with amortized triage.** After each unit,
   auto-diff its document tree against the oracle: same set of links (by anchor
   text + destination), same bold/italic runs, same chip-colored spans, same table
   shape, same text. Each discrepancy is an automatic flag ("PDF p100 has 16
   links, output has 13 → here are the 3"). Plus the agent emits a **structured
   uncertainty log** ("rendered X as a chip, medium confidence"; "ambiguous table
   here"). Flags are grouped **by issue-type**. The triage model:
   - The owner decides each *issue-type* **once**; the decision is recorded as a
     rule in a **living spec**.
   - A **judge model amortizes** that judgment — it auto-applies flags that match
     an existing rule (low risk: it's pattern-matching to human-approved
     decisions, not making novel calls) and **escalates only novel issue-types**
     to the owner. As the spec grows, human load trends toward zero.
   - This requires **staged conversion** (a representative-sample pass to seed the
     spec, then the bulk with matured rules; or waves with the spec updated
     between them) — *not* a simultaneous 20-agent fan-out, which is precisely why
     v1 had no feedback loop and re-litigated the same constructs per chunk.

4. **Pagination as a mechanical overlay, not agent text.** With exact span
   positions, page boundaries are known precisely. The agent writes
   *page-agnostic* markdown; a build step maps page boundaries onto it by matching
   known page-end text (or stores them as a sidecar of offsets). This deletes the
   single largest bug category (all of 2a) from the agent's plate entirely.

5. **Spec up front.** Start from a defined directive vocabulary and a
   machine-checkable schema (the conventions we learned, encoded as rules), not a
   doc that grows as we trip over things.

---

## 5. What this buys us, mapped to the failures

| v1 failure | v2 mechanism that prevents it |
|---|---|
| Internal links dropped | `/GoTo` extracted; link diff flags any missing |
| Chips flattened | span color → chip candidates; color diff flags misses |
| Caption bold inconsistent | bold flags extracted; bold-run diff |
| Page-marker breakage (all) | pagination is a mechanical overlay, not agent text |
| Split paragraphs/lists/quotes | n/a — agent never places markers |
| Silent inconsistency | per-page structural diff + uncertainty log + spec feedback |
| Human as oracle | extraction *is* the oracle |

---

## 6. The load-bearing unknown: extraction-tool bake-off (do this first)

Don't commit to an architecture before settling this empirically. Run candidate
extractors on ~5 representative pages and score them:

- **Pages:** a chart-heavy page (§8 capabilities), a merged-cell table
  (e.g. §2.2.1 portfolio or §8.1 summary), a transcript with turns (§2.3.3.1), a
  smart-chip page (§2.3.3 / §2.4.3), and a cross-reference-dense page (§6.1.2).
- **Candidates:** `PyMuPDF`/fitz (spans+links+positions); `marker`; `docling`;
  `MinerU`; optionally a vision-LLM pass (Gemini/Claude on page images) and
  Mathpix as commercial baselines.
- **Score on:** text fidelity; table structure (merged cells!); reading order;
  **link capture (URI + GoTo + destinations)**; **styling capture (bold/italic/
  color)**; figure/chart handling; and how cleanly the output maps to our
  markdown + directive model.

Likely outcome (hypothesis to test): a layout model for the structural backbone +
PyMuPDF for precise styling/links/pagination overlay + LLM for the semantic layer.

---

## 7. Open questions for the v2 designer

*Resolved (see the decisions box in §4): canonical representation → structured
document model; pagination → per-node provenance; triage → amortized judge +
living spec with staged conversion.* Still genuinely open:

- **Determinism vs LLM:** how much can be fully mechanical (and thus verifiable)
  vs needs the model? Push the line as far toward mechanical as the bake-off
  allows; the answer depends on §6.
- **Chunk/stage granularity:** per-page validation argues for small units; weigh
  against cross-page context (a turn or paragraph spanning a page break) and cost.
  How big is the seed sample, and how are waves cut?
- **Triage surface:** the *approach* is decided (amortized judge + living spec);
  the *UX* is not — how are escalations presented to the owner (worklist? inline
  on the rendered page? a diff view?), and what's the spec's concrete form (rules
  a judge can mechanically match against)?
- **Chip/turn detection:** how reliably can span color + box geometry classify
  chips and transcript-turn boundaries mechanically before the LLM is needed?
- **Schema scope:** exact node/mark set for the document model — driven by what
  the chosen extractor emits (§6) and what these docs actually contain.

---

## 8. Recommended next steps

1. Bake-off (§6) — settle the extraction stack on real pages before designing further.
2. From the bake-off, a fresh planning pass turns this brief into a concrete v2
   plan (data model, validation contract, agent prompt, triage flow).
3. Re-convert the Fable 5 card with v2 and diff against v1's output — a useful but
   **partial** regression oracle. v1 is hand-verified only through ~section 6 (and
   incompletely even there), so a divergence is one of: a v2 bug, a v1 fix to
   preserve, **or a latent v1 defect that v2 got right**. Treat the verified range
   as the trustworthy oracle; treat divergence past it as a prompt to check the
   *PDF*, not to assume v1 was correct. Better still, v2's own structural oracle
   (§4.3) should catch most of these without needing v1 at all.

The existing v1 repair tools (`tools/*.py`) shouldn't be carried forward as-is,
but they encode hard-won detail (e.g. how to map a destination page to the nearest
section anchor; how page breaks fall inside lists/quotes/figures). Mine them for
logic, then retire them.
