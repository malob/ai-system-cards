# Fable 5.1 inspector rulebook — round 2 (f51-sweep2)

Read `rulebook.md` in this directory FIRST; everything there applies. Round 2
uses fresh inputs: slices in `pipeline/.cache/f51-sweep2/slices/p-NNN.md`,
served HTML snapshot `pipeline/.cache/f51-sweep2/served.html`, findings files
`pipeline/.cache/f51-sweep2/findings-XXX.jsonl`. Same output schema.

## What round 1 fixed (verify these on your pages)

| pages | fix to verify |
| --- | --- |
| 60–61, 65, 67, 69, 75–76, 85–89 | 'Model' header cell now spans both header rows (`rowspan`), the sub-header row no longer carries an empty lead cell; p.88's corner is one `colspan=2 rowspan=2` 'Model' cell |
| 100 | `admin / admin123` is a code span |
| 106 | item 5's bold lead renders bold with the em dash inside it, no literal `**` |
| 167 | 'Evaluation' is one 2×2 header cell; 'Humanity's Last Exam' spans its two sub-rows |
| 199 | Figure 8.17.2.A's caption is one caption block through "…Shown with 95% CI." |
| 206–210 | Table 9.1.A: every group label spans exactly its questions across page seams (Autonomy & Anthropic's power = 7, Creation ethics & moral status = 2); no question sits in the Group column; no empty Group cells |
| 210–212 | the §9.2 blocklist is ONE fenced block; page markers 211/212 follow the fence |

## Additional DO NOT FLAG — source-faithful, adjudicated in round 1

- p.23 the caption label `[Figure 2.2.3.1.A]` is bold-italic in the PDF.
- p.28 bracketed row labels `[Top row:]` etc. inside the bold caption lead.
- p.46 the sentence ending "…cannot run on Fable" has no terminal period in the PDF.
- p.55 `**universality)**` (bold closing paren) is the PDF's own bold extent.
- p.61 a cell both bold and underlined; p.67 three underlined 0.45% cells — PDF styling.
- p.73 bold sentence nested inside the italic BBQ quotation with a roman bracket note.
- p.80 `(Helpful-only)` bold italic; p.85 '0.3%' with one decimal — PDF values/styles.
- p.88 '*high* effort' is italic in the PDF, not a green code span.
- p.89 a continuation-page model row as `<td><b>…</b></td>` — visually identical to `<th>`.
- p.93 the 'Transcript' chrome header on the two label-less cream boxes is site styling.
- p.94 'Section 2.23.1 of our August 2026 Risk Report' is verbatim.
- p.95–96 `mcp__claude_ai_Google_ Calendar__*` carries the PDF text layer's wrap space; the
  renderer's typographer curls the shell command's straight quotes (site-wide behavior).
- p.106 '(Section 6.4.8)', p.127 '(Section 6.6.2)', p.176/179 'Appendix 9.2' / 'Section 8.13.x',
  p.209 '(Section 7.2.1 only)' rows: unlinked in the PDF too.
- pp.110–111 `C**ontrolled-substance…**`, `**Overrefusa**l:` — one letter set regular in the PDF.
- p.115 'Metrics' lead-ins vary bold/plain as in the PDF; p.164 colon inside/outside bold as in the PDF.
- p.129 the double negative in Figure 6.6.1.A's caption is verbatim.
- p.132/169 only the words set in green mono are code spans; 'maximum'/'medium' in Lora stay prose.
- p.134/145 bold or italic closing before the period follows the PDF's span extents.
- p.142 'Appendix 9.1' links to `#9-appendix`: the PDF destination is the top of p.206, where
  the '9 Appendix' heading sits directly above 9.1 (L2 source-first geometry).
- p.159 literal ' * ' in the quoted passage; p.160 'individual group' — verbatim.
- p.159 the seam-merged row's cells are `<p>`-wrapped (typed TB2 seam class), not a finding.
- p.162 ASCII '>=' in the caption is the PDF's text.
- p.168 the Opus 5 System Card link wrapped in `<u>` where the PDF underlines it in black.
- p.180 footnotes 16 and 19 are byte-identical citations in the PDF.
- p.202 'Claude Mythos 5.1' naming in §8.19 prose is verbatim.
- p.207 a wrapped internal link as two adjacent anchors with one correct target (typed minor).
- p.211 two blocklist entries wrap over two lines exactly as printed (the fence keeps the PDF's lines).

## Rotating clean sample

The sample agent re-inspects pages that were clean in round 1 to catch regressions from the
fix batch: treat any difference from round 1's verdict as a finding.
