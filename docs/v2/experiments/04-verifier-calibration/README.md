# Experiment 04 — verifier v0 calibration against v1 history

**Question.** Do the mechanical gate invariants, run against the PDF oracle,
rediscover the defects a careful human found in v1 (D4/D5)? And what do they
find that the human didn't?

**Method.** `pipeline/verifier/` (oracle.py = PyMuPDF facts with zone tagging;
mdproj.py = v1 markdown → comparable projection; invariants.py = T1/L1/P1/F1/FN1;
calibrate.py = driver). Run at the pre-fix baseline and at HEAD:

```sh
uv run --with pymupdf python pipeline/verifier/calibrate.py f60899a
uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
```

Flag dumps: [prefix-flags.json](prefix-flags.json) (@ f60899a),
[head-flags.json](head-flags.json) (@ HEAD). Eight iteration rounds drove HEAD
noise from 980 flags to **zero unexplained majors**; every exclusion/
normalization added en route is in code comments and the contract's allowlist.

**Bottom line: 141 major flags at pre-fix `f60899a` vs 4 at HEAD** — and the 4
are one understood class (chip-cluster order, below).

## Recall vs the defect catalog

| catalog class            | @ f60899a (pre-fix)            | @ HEAD       | verdict |
|--------------------------|--------------------------------|--------------|---------|
| FL-01 internal links     | **134 L1 major**               | 2            | **caught** (the 111 recovered links + more; see "new finds") |
| PM-06 duplicate markers  | **5 P1 major — the exact 5 pages** (36, 162, 232, 264, 291) | 0 | **caught exactly** |
| PM-01/02 marker damage   | text side-effects caught (p.3 paragraph damage) | 0 | partial: token-level effects caught; pure *structural* splits need the v2 typed model (by design) |
| FN1 footnotes            | count-clean                    | count-clean  | pass both states |
| F1 figures               | 2 majors                       | 3 majors     | **new finds** (below) |
| CA-02 mojibake `⌐`       | not present in md layer (was a render-chain bug) | — | belongs to SC2/V1, not T1 |
| FL-04 caption bold       | —                              | —            | S1 not implemented in v0 (next) |
| FL-02/03/05/07 chips/turns/quotes/highlights | —              | —            | S2/N1 manifest classes, post-v0 |
| ~~CA-01 stray dashes~~   | **RETRACTED** — see below      | —            | catalog entry falsified |

## New finds at HEAD — triaged

1. **p.100 "missing links" → source-PDF defect.** `a limited evaluation` and
   `shows that Fable 5 is generally less vulnerable` (plain text in
   `06a-alignment-intro-behavioral.md:26`) are named-destination links in the
   PDF — pointing at Google-Docs heading id `h.6c8a0mx55isl`, which **does not
   resolve in the PDF's own name tree**. The source document's links are
   broken; v1's plain text is defensible. New flag class:
   `source-defect-unresolvable-dest` (minor, reported). The verifier found a
   defect in *Anthropic's* PDF.
2. **Figure-count mismatches → v1 was right, verifier learned.** The md
   contains documented skip comments (`<!-- figure p139-2.png skipped:
   duplicate extraction… -->`, `p151-1.png skipped: text-only fragment`) — v1
   already had the contract's declared-exclusion pattern. F1 now honors them;
   p.139/150/151 go clean (2 residual off-by-one-page minors).
3. **p.139 caption → verifier bug, fixed.** The caption is text-layer content
   overlapped by an oversized chart rect. Raster-internal text is *pixels*, so
   the image-rect text exclusion was wrong wholesale and is removed (vector
   chart furniture remains an open, separate exclusion via drawing clusters).
4. **T1 chip-cluster order** on p.38/p.44 (the 4 remaining majors): chips appear
   in a different order in md vs PDF reading order (content all present).
   T2-class; the typed model with bbox provenance settles which order is true.

## Retraction: CA-01 was a phantom

Experiment 01 cataloged "stray lone `-` lines injected" based on reading
`grep -B/-A` output of the fix diff — but those `--` lines were **grep group
separators**, not diff content. `git show f60899a:…02b… | grep -c '^-[ ]*$'` = 0.
The catalog and its README now carry this correction. The bidirectional T1
principle CA-01 motivated stays (it is independently justified and costs
nothing; mutation testing (D6) will quantify it). Lesson recorded: derive
catalog entries from `git show` output directly, never from grep context
windows.

## Residual noise at HEAD (all classified)

- T1 minor ×121: table-zone traversal order (TB1/docling's job), T2
  displacements, 1–2-token punctuation (PDF span-join artifacts like
  `voice ;` vs `voice;`).
- L1 minor ×36: Google-Docs auto-links (`http://` + anchor==URL, the appendix
  blocklist tables; v1 renders them as code, correctly — needs a one-line spec
  rule) + the 2 source-defect dests.
- F1 minor ×2: off-by-one page attribution at figure-led page boundaries.

## Conclusions

- **The verifier-first bet pays**: every mechanically-checkable catalog class
  is either caught (FL-01 exactly, PM-06 exactly — all 5 pages, PM-01/02
  token effects), explicitly deferred to a named later layer
  (S1/S2/N1/TB1/SC2), or retracted with evidence. Nothing is silently
  uncovered.
- **The loop works end to end**: 141 majors pre-fix → 4 understood ones at
  HEAD, with each interim finding triaged to a root cause (one source-PDF
  defect, one v1 convention the verifier had to learn, one verifier bug).
- **Triage sharpened the system itself**: v1's figure-skip comments became a
  recognized declared-exclusion convention; unresolvable named dests became a
  flag class; the image-rect text exclusion was removed on evidence.
- v0 scope gaps to close next: S1 bold/italic runs, S2 chips via the style
  manifest, TB1 via docling, L2 dest resolution, mutation testing (D6) for
  measured per-class recall.
