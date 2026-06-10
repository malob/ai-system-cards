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

Flag dumps: [prefix-flags.json](prefix-flags.json) (298 @ f60899a),
[head-flags.json](head-flags.json) (166 @ HEAD). Six iteration rounds drove HEAD
noise from 980 flags to ~160 classified ones; every exclusion/normalization
added en route is in code comments and the contract's allowlist.

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

## New true-positive candidates at HEAD (latent v1 defects)

1. **Two missing internal links on p.100** — `a limited evaluation` and `shows
   that Fable 5 is generally less vulnerable` are plain text in
   `06a-alignment-intro-behavioral.md:26`. They are *named-destination* GoTo
   links, which v1's `extract_internal_links.py` (page-destination based) never
   saw. Confirmed real by inspection.
2. **Figure-count mismatches**: p.139 (2 images extracted, 1 in md), and a
   p.150/p.151 relocation (HEAD has 4+0 where the map says 3+2; pre-fix had
   3+1). Need eyeball triage against page renders — could be md omission,
   map duplicates, or marker-anchoring side effects.
3. **T1 chip-cluster order** on p.38/p.44: chips appear in different order in md
   vs PDF reading order (content all present). T2-class; the typed model with
   bbox provenance settles which order is "true".

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
- L1 minor ×34: Google-Docs auto-links (`http://` + anchor==URL, the appendix
  blocklist tables) — v1 renders them as code, correctly. Needs a one-line spec
  rule (owner decision folded into the living spec at conversion time).
- The five T1 majors: chip-order ×4 + the p.139 caption (tied to find #2 —
  caption text may live inside the raster chart, which also explains the image
  count).

## Conclusions

- **The verifier-first bet pays**: every mechanically-checkable catalog class
  is either caught (FL-01 exactly, PM-06 exactly, PM-01/02 effects), explicitly
  deferred to a named later layer (S1/S2/N1/TB1/SC2), or retracted with
  evidence. Nothing is silently uncovered.
- **It found real defects a careful human read missed** (p.100 links — inside
  the §6 reviewed range!), supporting the "verifier passes ≈ human wouldn't
  find anything" goal.
- v0 scope gaps to close next: S1 bold/italic runs, S2 chips via the style
  manifest, TB1 via docling, mutation testing (D6) for measured recall.
