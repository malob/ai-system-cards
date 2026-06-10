# Experiment 03 — document-wide visual-signal census

**Question.** What is the card's *entire* visual vocabulary — and is it small
enough that a per-card style manifest (D16) is a one-sitting artifact rather than
a growing rule pile?

**Method.** [census.py](census.py) sweeps all 319 pages with PyMuPDF and counts
every vector fill color (classified pill/box/rule by geometry) and every text
color, with sample pages and sample text. ~40 s. Full data:
[census.json](census.json).

```sh
uv run --with pymupdf python docs/v2/experiments/03-signal-census/census.py
```

**Result: 33 fill colors + 21 text colors ≈ ~15 semantic roles.**

- **Body & chrome:** black body text; link blue `#1155cc` (356 spans, 127 pages);
  running-header gray `#666666` (120 pages — clean exclusion signature).
- **Chips:** all 12 registry labels appear as pill fills with stable colors
  (`#b10202` Fabrication, `#ffe5a0` Skipped cheap verification, …), each with a
  paired text-color / thin-rule artifact in the matching hue.
- **Placeholders/redactions:** `#d9ead3` ×76 across 14 pages — both inline pills
  (`[Error 1]`) and **larger multi-line boxes**, so the typed mark needs an
  inline and a block form (D15).
- **Transcript anatomy:** container `#f3f3f3`; assistant bubbles `#ebc9b7`
  ("Assistant, turn 146:"); user bubbles `#e2decf`/`#faf9f5`; commentary text
  `#444444`. Turn structure is even more mechanical than part 1 suggested —
  *roles* are color-coded too.
- **Code styling:** `#f8f8f8` pills behind inline code (`huggingface.co`) and
  green `#188038` code text (`mean_age=35.24`, 54 spans on 4 pages).
- **Chart/panel furniture (vector!):** `#dedcd1` ×192, `#141413` ×96, white
  boxes; legend-key pills `#4d4c48` ×35 on 9 pages. Some figures are **vector
  drawings, not raster images** — exclusion zones must be defined over drawing
  clusters too, not just `get_images()` rects (affects F1/exclusion design).
- **Oddities to resolve at conversion:** `#fefdfb` micro-pills ×91 on just 2
  pages (bulleted scenario tags?); near-black paste artifacts (`#1d1c1d`,
  `#242424`, `#1f1f1e` — text pasted into the source doc with not-quite-black
  color); white-on-dark table-header text `#faf9f5`.

**Conclusion.** A 319-page card's full visual language enumerates mechanically in
under a minute and maps to roughly fifteen roles in one read — empirical basis
for D16 (per-card manifests are small data files, not accumulating code) and for
the closure rule (every signal above must be explained by a manifest entry or it
flags). The census tool itself becomes pipeline machinery: run it first on any
new card, and the manifest session *is* triage of its output.

**Census follow-ups** (candidate issue-types, queued for conversion time, no
owner decision needed yet): vector-figure exclusion zones; inline-code
green-vs-plain presentation (D17 territory); the `#fefdfb` micro-pill pages;
near-black → body-black normalization mapping.
