# Generation loop design (v2 conversion)

Governs the implementation in `pipeline/generate/`. Written 2026-06-10 ~01:50
before the overnight run (D20). The verifier (`pipeline/verifier/`, calibrated
+ mutation-tested, experiments 04–05) is the gatekeeper for everything below.

## The central move: structure assignment over immutable text

The LLM never types document text. The oracle (PyMuPDF, D14) supplies the span
stream; generation *assigns structure* to it — block boundaries, block types,
semantic roles — referencing the facts, never altering them. Text fidelity
(T1) holds by construction and is still gate-checked afterward (belt +
suspenders). Marks are attached **mechanically** from oracle facts: links from
annotations, bold/italic from span flags, chips from pill fills + manifest,
placeholders from #d9ead3, footnote refs from superscripts.

## What is mechanical vs LLM (from the manifest + experiments)

Mechanical-first compiler (`assemble.py`) with confidence tags:
- Headings: size 13/14/16 or gray #666666 + numbering regex.
- Paragraph boundaries: PyMuPDF blocks; page-break joins by the v1 heuristic
  (no terminal punctuation + lowercase continuation) — tagged for review when
  ambiguous.
- Lists: bullet glyphs / numbering + indentation.
- Transcripts: container fill #f3f3f3; turn roles from bubble fills (#ebc9b7
  assistant, #e2decf/#faf9f5 user); narrator commentary = gray #444444 text;
  labels = bold leads inside bubbles.
- Code/example boxes: #f1f3f4 / #f0eee6 + mono fonts.
- Figures: raster rects + size-9 captions below; tables: docling fragments.
- Chips/placeholders/links/footnotes: as above.

LLM passes (sub-agents, parallel):
1. **Adjudicator** — short per-page list of flagged ambiguities (block-type
   conflicts, weird reading order, caption association). Sees the page render.
2. **Alt-text author** — per figure, from the page render.
3. **N-version arbitration** — only for pages where two independent assembly
   adjudications disagree (D7).

## Document model (minimal, per D1)

JSON per page-range chunk; nodes carry `{page, bbox?}` provenance:
blocks: `heading{level,number} | paragraph | list{ordered} | item | table{grid,
spans} | figure{file,alt,caption} | transcript{children} | turn{role,label} |
commentary | example | codeblock | footnote{n}`; inline marks over span ranges:
`bold | italic | link{target,kind} | chip{label} | placeholder | code |
fnref{n}`.

## Serialization = v1's markdown dialect

`serialize.py` emits exactly the dialect the site + verifier already consume
(`<!-- p.N -->` markers placed mechanically from provenance, `:chip[]`,
`::::transcript`/`:::turn`, HTML tables with spans, `![alt](...)` + `*__lead__
rest*` captions, `[^n]` footnotes). Consequences: the existing Astro renderer
works unchanged, and the **calibrated verifier applies to v2 output as-is**.
Output to `cards/anthropic/claude-fable-5/sections-v2/` (v1 stays shipped
until acceptance, D9); `calibrate.py` gains a `--dir` to point at it.

## Loop

Per wave (~16 pp, cut at section boundaries where possible):
assemble → adjudicate flags → serialize → **verifier gates** → repair loop
(failures re-adjudicated with flag context, max 3 iters) → wave accepted when
zero unexplained majors. Cross-page constructs handled by `stitch.py`
(paragraph joins; table fragment stitching — column-alignment + header-repeat
heuristics; two known multi-page tables: p.252–253, p.309–318).

Seed wave first (the construct gauntlet): pages 3, 19–20, 26, 39–44, 74, 95,
100, 107, 118, 139, 235–236, 252–253, 309–311, 318–319. Then bulk waves in
parallel. Escalations per D20: provisional rule + continue; everything logged
to `docs/worklist.md` for the morning check-in.

## Morning check-in artifact

`docs/worklist.md`: provisional rules adopted, escalations, per-wave gate
results, residual flags with page links, site build status, and the
spot-check menu (flagged pages + a random sample).
