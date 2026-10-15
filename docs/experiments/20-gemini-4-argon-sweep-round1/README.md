# Experiment 20 — gemini-4-argon inspection sweep (2026-10-15)

**Question:** after the automated gate converged at 0 unsuppressed majors on
the archive's first non-Anthropic document (Google DeepMind's Gemini 4 Argon
Safety & Security Report, 217pp, same Google Docs exporter, different house
style — D70/D71), what does the layer-2 agent inspection find that the gates
cannot see?

**Method:** the experiment-18 design, re-rulebooked for this card
(`rulebook.md` here): 7 triple-pane comparators over all 212 content pages
(PDF render vs md slice vs served production HTML, zoom crops for dense
constructs) + 2 markdown-smell linters over the 12 section files. Inputs:
`pipeline/.cache/g4a-sweep1/` (slices from `slice_pages.py`, `served.html`
from the production build, `findings-*.jsonl`). Re-runnable from the rulebook
and this README.

**Context going in:** gate 0 unsuppressed majors (8 exact T1 acceptances:
p.147 column-order stream, pp.184–185 seam attribution), L2 23/23, P2/F3
212/85, RF1 clean, seam audit 0.

## Round 1 result

9 agents, 224 units (212 pages + 12 files), 185 clean. 33 major findings
(32 confirmed, 1 uncertain), 25 minor (21 confirmed, 4 uncertain), 15
source-faithful notes. Overlaps between comparators and linters collapse the
majors to these distinct classes — all invisible to the gates (structure,
styling and seam classes below T1's token resolution):

| class | pages | root cause → fix (D71) |
| --- | --- | --- |
| roman-numeral list broken (i./ii./iii.) | 15 | LIST_MARKER knew lettered markers only; Google Docs right-aligns roman numerals, so x0 split one list into tiers → roman markers join the grammar (generator + verifier mirror), tiered on the item TEXT less the 18pt hanging indent |
| footnote tail stranded in the body, splitting a sentence | 35–37 | a page whose footnote region holds only the previous note's tail has no marker; oracle and RF1 refused to guess → the 2in separator opens the region, so everything below it continues the open note (both, independently) |
| list inside a footnote flattened | 35 | numbered marker lines inside a note now break with `<br>` (RF1/FN1 read `<br>` as whitespace) |
| literal asterisks from a mis-flanked italic | 35 | italic run opening at a comma after a word → `<i>` fallback, as bold already had; footnote-ref edges count as safe delimiters (a first version misfired on risk-report §4, caught by the net) |
| caption split at a page seam | 107–108, 114–115 | body-size captions continue at their own size; a continuation opening on a bold lead never joins (p.129 '**Analysis**:' after Figure 3.30's period-less caption) |
| caption with a period label not recognized | 144–145 | `Figure 3.36.` — the bold caption grammar accepts a period |
| header band emitted as data rows | 44, 183 | card knob `header_rows_by_fill`: a table's leading rows on the #e8f0fe/#f3f3f3 band are `<th>` — run AFTER the dark-band demotion; repeated labels match through every run |
| bold labels lost / paragraphs merged / bold bleeding in tall cells | 88–89, 92–93 | card knob `cell_run_restyle`: each cell's bold extents and paragraph gaps from its own span run (row bands cannot segment tall or page-cut cells) |
| regular-weight row labels rendered bold | 178, 194 | a row-label `<th>` whose spans are all regular becomes `<td>` |

Run matching for these passes now ignores zero-width marks and reads centred
stacks ('Gemini 4 Argon' / '(Model C)').

**Not fixed, recorded:** Figure 3.43's 'STEPS 1–6' row cut by the p.154/155
break renders as two rows (no lowercase / unterminated signal; the label ends
in a colon); in-cell stacked values ('1.8%' / '(1/55)') whose second line would
not have fit; Table 5.1's 2pt group rule; the decorative section-end rules
(pp.8, 174, 202); link anchors that include a sentence period where the PDF
link rect covers it but its styling does not (p.167); underline extents that
include a trailing colon (pp.78–79); the p.66/67 seam join after a period-less
sentence (ambiguous: the outgoing line is full-width).

**Source-faithful notes (rulebook growth):** duplicated §2.5 sentence (p.12);
sibling bullet leads with bold vs regular colons; period-bearing link anchors
whose PDF rect covers the period (pp.14, 115, 142); standalone 11pt black
pseudo-subheads ('Honeypots', 'LinuxArena', …) that are not outline headings;
'3.5.1'–'3.5.3' set as bold body type but bookmarked as level-4 heads; a bold
final 's' in 'results' (p.93, the PDF's own span); literal `$p < 0.001$`
(p.147).
