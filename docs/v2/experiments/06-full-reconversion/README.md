# Experiment 06 — first full v2 re-conversion of the Fable 5 card

**Question.** Does the generation loop (mechanical assembly over immutable oracle
spans → v1-dialect markdown → gates), run across all 319 pages, produce output
that passes the verifier and renders as a site?

**Method.** `pipeline/generate/` — `assemble.py` (block compiler), `tables.py`
(docling table cache), `serialize.py` (v1-dialect), `run.py` (wave driver),
`worklist.py` (gate report). Output to `sections-v2/` (gitignored; regenerated).

```sh
uv run --with docling --with pymupdf python pipeline/generate/tables.py   # cache all table pages
uv run --with pymupdf python pipeline/generate/run.py --all
uv run --with pymupdf python pipeline/generate/worklist.py                # -> docs/v2/worklist.md
```

## Result: 26 major flags across 319 pages

Trajectory over the night's iterations (full-doc major flags):
**112 → 93 → 84 → 26**, each step a root-cause fix, not flag-suppression:

| fix | flags addressed |
|---|---|
| exclusive page→section assignment | P1 9→1 (boundary-page duplicate markers) |
| docling table integration | T1 113→~11 (tables were scrambled prose) |
| transcript box-priority + bubble capture | turns were silently dropped |
| chip-bold overlap suppression | S2/S3 → 1 each (leaked `**` in labels) |
| link span center/overlap matching | goto anchors (63→3 goto) |
| footnote blocks w/ link marks | L1 63→5 (citation links were dropped) |

**Final by invariant:** T1 4, P1 1, L1 5, S1 13, S2 1, S3 1, FN1 1.
The fidelity-critical gates (T1 text, P1 structure) are essentially clean across
the whole document. Remaining majors live in known-incomplete layers — and the
biggest bucket (S1 ×13) is verifier run-segmentation noise, not lost emphasis
(see triage below), so the *content-loss* surface is far smaller than 26.

## Render proof

Site builds clean against `sections-v2/` (Astro + Pagefind, no errors). The
rendered card HTML (774 KB) contains: 28 chip pills, 88 transcript turns, 38
tables, 153 figures, 51 arXiv citation links — i.e. every construct family
survived assembly → serialization → render.

## Remaining 26 majors — all triaged, none systemic

- **S1 ×13** — diagnosed 2026-06-10: **the emphasis is present in v2, not
  dropped.** The flags arise because v2 sometimes *segments* a bold run that the
  oracle merges (e.g. p.223 `**…uncertainty** **rather…**` for one PDF bold run),
  which defeats S1's run-substring match. Verified: the flagged text is bold in
  the v2 markdown and correctly page-attributed; v1 HEAD is clean on these pages
  (so it's v2 segmentation, not a shared issue). **Root cause is verifier-side**:
  S1 should compare bold *token coverage* (every source-bold token is bold in the
  output), not run-as-substring — robust to segmentation. Deferred because
  changing a gate's semantics requires re-running S1's mutation (drop-bold) +
  v1-calibration suites; that's the top next-action, not a rushed late-night
  edit. A subset (p.222 `[Bottom left:]`, p.304/307 captions) may be genuine
  caption-lead-extent cases surfaced once the token fix removes the noise.
- **L1 ×5** — 3 goto links needing L2 destination resolution (page→section
  anchor; mine v1's `apply_internal_links.py`); 2 URI edge cases.
- **T1 ×4** — chip legend row (p.44) + 2 figure-caption number-format spacing.
- **FN1 ×1** — footnote refs inside table cells (docling flattens cell `<sup>`).
- **S2/S3/P1 ×1 each** — one chip near a page break; p.87 has no text line to
  anchor a marker (figure/table-only page).

## Known designed-deferred gaps (not in the flag count)

- **Figure alt text** empty — pending the LLM alt-text pass (the one genuinely
  LLM-required step; everything above is mechanical).
- **Placeholder highlights** (D15/FL-07) pass through as plain bracketed text
  until the renderer/verifier gain a `:ph` directive.

## Conclusion

The architecture is validated end to end: **structure assigned over immutable
oracle spans yields text fidelity by construction, and the gates confirm it** —
4 text flags and 1 structure flag across 319 pages, from a fully mechanical
pass with zero LLM calls. The remaining work is well-scoped and bounded
(caption-lead rule, L2 link resolution, table-cell footnote refs, the alt-text
LLM pass), not open-ended. This is a mechanical pre-LLM draft, **not** an
accept-ready card; per D20 the bulk run produced a reviewable artifact + worklist
for the owner, nothing published (D13).

## Lesson logged

The site-build swap (`mv sections sections-v1bak`) left v1 stranded when the
restore used `rm -f` on a directory. Restored byte-identically from git. Future
render proofs: build via an env-pointed sections dir or a temp card slug, never
by moving the live one.
