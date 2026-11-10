# Experiment 22 — gemini-4-carbon inspection sweep (2026-11-10)

**Question:** after the automated gate converged at 0 unsuppressed majors on
the eighth card (google-deepmind/gemini-4-carbon — Gemini 4 Carbon Safety &
Security Report, 94pp, the second report in the gemini-4-argon template, D76),
what does the layer-2 agent inspection find that the gates cannot see?

**Method:** the experiment-21 design with Argon's template rules
(`rulebook.md` here): 4 triple-pane comparators over all 90 content pages + 2
markdown-smell linters over the 7 section files, reading a sections snapshot.
Inputs: `pipeline/.cache/g4c-sweep1/` (slices, served production HTML,
sections snapshot); findings copied to `findings-round1/`.

**Context going in:** gate at 0 unsuppressed majors (3 exact pp.33–34 seam
acceptances), TB2 2; L2 36/36; P2/F3 90/48; RF1 4/4; seams 0; fast release
gate green with eight cards.

## Round 1 result

6 agents, 97 units (90 pages + 7 files), 87 clean. 2 major findings (one
distinct class), 8 confirmed minors, 15 source-faithful notes.

| class | pages | root cause → fix (D76 addendum) |
| --- | --- | --- |
| cut row rendered as a label-group sub-row | 32–33 | Table 3.2's 'Specification gaming / eval' finding continues on p.33 as UNTAGGED text, so the tags name the next row first and the legacy seam test treated the tail (a digit start) as a new member of the row's label group → under `tagged_tables`, a first row with text only under columns the host row fills and an interior column empty is a cut row (`run._sparse_continuation`) |

**Minors, not fixed, recorded:** p.16 one Table 3.1 cell's italic
'(carried forward from Argon)' dropped (a restyle miss independent of D76);
p.32 'inverse-probability-w eighted' (a mid-word wrap in a narrow docling cell;
both T1 sides join lines with a space, so a fix needs the tags' P structure on
both sides); p.34 the stitched cut row's `<td><p>` wrappers (the opus-5-5 TB2
class); p.79 an italic colon after a bold lead; the section-end rule (p.57)
and Table 5.1's heavier group rule (p.61), both recorded on gemini-4-argon.

**Source-faithful (rulebook growth):** p.20 'Section 7.1.1' links to an
internal docs.google.com draft (the PDF's own annotation); 'Termina-Bench 4.0'
(p.32); p.88's double-encoded bughunters URL; link anchors including a period
the PDF draws in link style; unlinked 'Section N' references where the PDF has
no annotation; p.66's bold lead ending before ')'.

## Round 2 result (fix verification)

2 comparators over the 8 fix pages (15–17, 31–34, 61) plus 10 seeded clean
pages (`random.seed(22)`: 8, 18, 23, 25, 35, 41, 43, 56, 70, 91),
`rulebook-round2.md`: the sample was 10/10 clean; every D76 table fix held
(19 table links on pp.15–17 jump where the PDF's do, page markers at the exact
seams, footnote 2 only as a footnote, both cut rows one row). **One major:**
p.61's third '99.4' was bold again — not a class regression but a stale
canon: a debugging run with the reuse-style rule disabled had regenerated the
card and the restored code was never re-run before the commit. Regenerated
from the committed code (only that cell changed); every other card
byte-identical.

## Rendered visual pass

DOM audit (browser pane, production build): 1338px — 90 page labels, 0
overlaps, 48 images decoded, no horizontal scroll; 1680px — 4 sidenotes, 0
collisions; 375px — no horizontal scroll, nothing outside its scroll wrapper.
8 construct screenshots (6 tables, 2 bordered CCL boxes) reviewed against the
PDF (`visual-findings.jsonl`): 0 major, 3 minor — the p.16 italic and the p.32
mid-word wrap above, and the p.61 bold (the stale canon, since regenerated).

## Verifier finding from the mutation suite

The new card's first baseline showed drop-bold (S1) recall 1/8: S1 compared
bold runs only in `#000000`, and Carbon sets most body text — its bold leads
included — in `#101010`. S1 now checks every colour the card's manifest maps
to the body role (`calibrate` passes them). No card gains an S1 flag.

## Certified hunks for the owner (`hunks/`)

- `hunk-0..2`: gemini-4-argon's three tagged cut rows (pp.87–88, 88–89,
  154–155) take their page marker at the exact seam (D76) — the gutter label
  moves to the line where the page turns; content unchanged.
- `hunk-3`: opus-5 p.147 'ARGH ARGH ARGH.' ends its line, as printed (D77).
