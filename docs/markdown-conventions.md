# Markdown conventions for system card transcription

These rules govern how system card PDFs are transcribed into markdown. The goal is a
**faithful, complete** transcription — every sentence, number, table value, and footnote
from the source, in clean semantic markdown. Never paraphrase, summarize, or omit body
content. Preserve the original wording exactly, including hedges, typos, and
British/American spelling as found.

## Headings

Heading level = section depth + 1. Keep the section numbers.

```
## 2 RSP evaluations
### 2.1 RSP risk assessment process
#### 2.1.1 Risk Reports and updates to our risk assessments
##### 2.1.2.1 On autonomy risks
###### 2.2.4.2.1 Black-box RNA sequence modeling and design
```

Unnumbered front-matter sections (e.g. Executive Summary) are `##`.

## Page markers

At the point in the text where each new PDF page begins, insert an HTML comment on its
own line: `<!-- p.42 -->`. If a sentence straddles the page break, put the marker at the
nearest paragraph boundary before the break. These are stripped at render time and used
for verification and deep-linking back to the PDF.

## What NOT to transcribe

- Running headers/footers and bare page numbers
- The PDF's table of contents (regenerated from headings at build time)
- Decorative images (logos, cover art) — note them in an HTML comment instead

## Figures

Extracted figure images live in `assets/figures/`, named `pPPP-K.png` (PDF page number,
1-based index of the figure on that page). The file `extracted/figures-map.json` maps each
page to its figure files. Reference every figure at the position it appears:

```
![Chart: ExploitBench solve rates for Claude models from Sonnet 3.7 through Mythos 5](assets/figures/p060-1.png)
*Figure caption exactly as printed in the PDF, if one exists.*
```

The alt text is your own concise description of what the figure shows (it is not in the
PDF). The italic caption line directly below is the PDF's printed caption, transcribed
exactly; omit the line if the figure has no caption. Every figure file for your pages must
either appear in the markdown or be noted in an HTML comment as skipped (with reason).

## Tables

Use GitHub-flavored pipe tables. Right-align numeric columns is not required. If a table
genuinely cannot be represented (merged cells spanning rows), use an HTML `<table>`.
Transcribe every cell exactly — table values are the highest-stakes content in these
documents. A table that continues across pages is one markdown table (put the page marker
comment before or after the table, not inside it).

## Footnotes

Use markdown footnotes with the original footnote numbers: `[^17]` in the text,
definitions collected at the end of the file:

```
[^17]: The footnote text exactly as printed.
```

## Hyperlinks

The PDF's link annotations are dumped in `extracted/links.json` (page number → list of
URLs). Match each URL to its anchor text by context and write inline links:
`[launch blog post](https://...)`. If you cannot confidently match a URL to text on the
page, leave the text unlinked and record `<!-- unmatched link p.NN: URL -->` at the end of
the file.

## Transcripts and example boxes

System cards include shaded boxes with prompts, model transcripts, and example exchanges.
Wrap each in a container directive, preserving the box's title/label if it has one:

```
:::transcript{title="Example 3: Claude attempted to claim its code came from a human"}
**User:** the prompt text…

**Claude Mythos 5:** the response text…
:::
```

Use `:::example` for non-conversational boxed content (prompt templates, rubric text,
blocklists). Inside the box, transcribe exactly; use bold role labels only where the PDF
shows speaker turns.

## Text details

- Write real Unicode characters (—, é, ≤). Straight quotes are fine; the renderer
  smartens them.
- Preserve bold and italic emphasis from the source.
- Bulleted/numbered lists keep their structure and nesting.
- Inline code styling for evaluation names is NOT added — keep prose as prose.

## File header

Every section file begins with:

```
<!-- source: source.pdf pages NNN-NNN -->
```
