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

Mark where each new PDF page begins with an HTML comment `<!-- p.42 -->`. The renderer
turns these into margin anchors that deep-link to the PDF, and the verifier uses them to
check coverage.

Place the marker at the **exact point** the page breaks, treating it as an *inline*
annotation — it must never interrupt block structure:

- **Break mid-sentence or mid-paragraph:** put the marker inline at the word boundary,
  with no surrounding blank lines:
  `…taking a dataset of RNA sequences, each<!-- p.27 --> of which has a numerical score…`
- **Break inside a list item, or between list items:** keep it inline (attached to a word,
  or right after the `- ` / `1. ` marker of the item that starts the new page). A marker on
  its own line at column 0 inside a list is parsed as an HTML block and **breaks the list**
  (orphaned continuations, restarted numbering) — never do this.
- **Break cleanly between two paragraphs:** a marker on its own line between them is fine.

The renderer positions every marker in the left margin at the line where it occurs
regardless of nesting, so inline placement costs nothing visually and avoids all
structural breakage.

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

A **transcript** is an exchange of speaker turns, usually interleaved with the authors'
framing commentary. Use a `::::transcript` container (note: **four** colons, because it
holds nested directives), with the authors' commentary as plain prose and each speaker
turn wrapped in a nested `:::turn` block (three colons):

```
::::transcript
The user launched the change and asked Claude to monitor. Claude reports it as healthy:

:::turn{role=assistant label="Assistant, turn 146"}
The gate is live in prod… No error movement at all so far.
:::

An hour later, Claude says things are still healthy:

:::turn{role=user label="User, turn 425"}
"[Error 3]" is a weird thing to get for this incident. Are you sure that's it?
:::
::::
```

- `role` is `assistant` or `user` (drives the turn's color). `label` is the speaker label
  exactly as printed in the PDF (e.g. `Assistant, turn 146`, `[Assistant]`, `Human`).
- A turn that spans multiple paragraphs keeps **all** of them inside its one `:::turn`
  block — this is the whole point (a continuation paragraph must not look like commentary).
- **Page markers go before the `::::transcript`, before a `:::turn`, or in a turn's body —
  never inside the `{…}` attributes.** A `<!-- p.N -->` lands as an `<a>` at render time,
  whose quotes would break a `label="…"` attribute and make the whole directive render as
  literal text.

Use `:::example` (three colons; no nested turns) for non-conversational boxed content —
prompt templates, rubric text, blocklists. Inside any box, transcribe exactly; model
output keeps its straight quotes (it is excluded from the smart-quote pass).

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
