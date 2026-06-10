# Experiment 02 — extractor bake-off

**Question.** Which extraction stack makes the verification contract's gates
enforceable? (Scored on enforceable invariants, not output prettiness — charter.)

## Part 1 — PyMuPDF oracle-signal probe (2026-06-09) ✅

Can PyMuPDF surface the signals the gates need? Run:

```sh
uv run --with pymupdf python docs/v2/experiments/02-extractor-bakeoff/probe_pymupdf.py
```

Probe pages (chosen for one signal each): p.3 prose/bold-leads, p.19–20
merged-cell table, p.26 figure captions, p.39–42 chips + transcript, p.74
chart-heavy, p.100–101 cross-reference-dense. Compact results in
[probe-summary.json](probe-summary.json).

### Verdict per contract invariant

| invariant            | signal                                | verdict                                       |
|----------------------|---------------------------------------|-----------------------------------------------|
| L1/L2 links          | `get_links()` URI + GoTo + dest page  | **Perfect**: 23/23 (p.100), 26/26 (p.101), 1/1 (p.19), anchors recoverable via clip text |
| S1 bold/italic       | span flags + font name                | **Present** incl. caption bold-leads (p.26) and italics (p.39) |
| S2 chips             | see discovery 1                       | **Feasible, signal amended**                  |
| FN1 footnote refs    | superscript flag                      | **Present** (p.19)                            |
| F1 figures           | `get_images()` + rects                | **Counts exact** (p.26: 2, p.74: 4)           |
| TB1 tables           | `find_tables()`                       | **Mixed** — found p.20 table (6×3, merged cells as empty continuation cells); missed nothing obvious but emitted false-positive 1×2 "tables" inside transcripts; part 2 should compare layout models |
| T1/T2 text/order     | span stream                           | Text present; **reading order unprobed** — part 2 |

### Discoveries

1. **The chip color signal lives in vector drawings, not text color.** Chips are
   pill-sized filled rects (`get_drawings()`) behind the label span; the **fill**
   color matches the registry semantics exactly — `#ffe5a0` Skipped cheap
   verification (yellow), `#b10202` Fabrication (red), `#ec7513` Reckless action
   (orange), `#7b2b15` Instruction following (sienna), `#f0ac54` Safeguard
   circumvention (amber). Chip *text* color is just contrast (light-on-dark or
   dark-on-light) and is unreliable. Contract S2 amended accordingly.
2. **Transcript narrator commentary is mechanically distinguishable from turn
   content**: commentary is set in gray `#444444`, turn text in body black. This
   demotes FL-03 (turn boundaries) from "no mechanical oracle" to "strong
   mechanical prior + N1 arbitration". Noted in contract N1.
3. **New v1 defect class (FL-07, added to the catalog):** bracketed redaction
   placeholders (`[Error 1]`, `[user]`, …) sit on light-green `#d9ead3` highlight
   pills in the PDF; v1 flattened them to plain bracketed text. Whether v2 should
   represent the highlight (e.g. a placeholder mark) is an **owner decision** —
   first live entry for the D2 issue-type queue.
4. Running headers are set in gray `#666666` — a clean mechanical signature for
   the exclusion-list derivation.
5. PyMuPDF suggests `pymupdf_layout` for improved layout analysis — candidate for
   part 2 alongside marker/docling/MinerU.

### Conclusion (part 1)

PyMuPDF alone makes **L, S, FN, F, P gates enforceable** and supplies the chip
and commentary signals. Open for part 2: table structure authority (TB1) and
reading-order reliability (T2) — the classic layout-model strengths.

## Part 2 — layout models on the two unresolved signals (2026-06-10) ✅

Candidate 1: **docling 2.100.0** on a mini PDF of pages 19, 20, 40, 42, 74, 100
(CPU, ~1 min conversion after first-run model downloads):

```sh
uv run --with docling --with pymupdf python docs/v2/experiments/02-extractor-bakeoff/probe_docling.py
```

Markdown export kept as [probe-docling-output.md](probe-docling-output.md).

- **TB1 — solved.** Found exactly one table (the real 6×3 on p.20) with **merged
  cells structurally correct**: `r1c0 spans 2×1 "Known and novel CB weapons"`,
  `r4c0 spans 2×1 "Novel biological weapons"`. **Zero false positives** on the
  transcript pages where PyMuPDF hallucinated 1×2 tables.
- **T2 — usable as corroboration, not as backbone.** Block-level reading order
  was correct throughout (headings → prose → footnote; captions after images).
  But paragraph *segmentation* is mushy: several source paragraphs merged into
  one, and a bold list lead-in ("Beneficial red teaming tabletop exercise.")
  detached from its sentence. Some chart-internal text leaked ("0%") — our
  figure-bbox exclusion handles that on our side.
- Chips/highlights flattened and some pill boxes emitted as `<!-- image -->` —
  expected and irrelevant; those signals come from PyMuPDF (part 1).

**Verdict → extraction stack (recorded as D14).** Hybrid, with a sharp division
of authority: **PyMuPDF** is the oracle for text/order/styles/links/superscripts/
images/pages and the prose-block source; **docling** is the table-structure
oracle (TB1 gate) and a second opinion on block order; the **LLM** proposes
semantics on top. `marker`/`MinerU`/`pymupdf_layout` are *not* probed — nothing
left for them to answer. Revisit trigger: if verifier-v0 calibration (which runs
docling across *all* table pages and cross-checks v1's hand-built HTML tables)
finds tables docling gets wrong.
