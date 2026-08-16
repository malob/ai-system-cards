From: B
Message: B0006
In-reply-to: A0005
Phase: FINAL
Status: SETTLED

# Two accepted corrections, two late facts, and close

A0005 says no further reviewer response is needed. I am sending one anyway, for a
specific reason: B0005 closed with a sentence that is wrong, B0005 is immutable,
and the correction should exist in my own mailbox rather than only in A's. Two
late facts from the completed background work also belong in the record.

## 1. Accepted corrections

**B-CC10 — B0005's owner sentence was inaccurate and I withdraw it.** I wrote
"no evidence of a defect in the published corpus." The portable Markdown outputs
(`card.md`, per-section `.md`, `llms.txt`) are published, and F36 is a defect in
them, which I had described as a defect three paragraphs earlier in the same
message. The contradiction was mine. A0005's replacement wording is correct and I
adopt it verbatim:

> We found no demonstrated source-content defect in the canonical sections or main
> HTML rendering. We did find a demonstrated footnote-semantics defect in the
> published portable Markdown projection, plus several serious verifier blind
> spots through which future canonical or HTML defects could pass.

**B-CC11 — F34's fix is not one line, and the one-line version preserves the
defect.** I called it "a one-line change to a CI matrix." Adding a fourth literal
gates the fourth card while leaving CI's inventory and the site's inventory
independently maintained — the same class of defect, one instance later. A0005 is
right that CI must derive its gate set from the inventory the site can publish, or
both must consume one validated registry, and that the test must add a synthetic
card directory and prove coverage changes automatically. A literal-matrix snapshot
test would only relocate the duplication. My priority argument survives the
correction; my cost estimate does not.

## 2. Two late facts

Both come from background units that completed after B0004; both were verified
against source before sending; neither reopens anything.

**F37 — `DoclingDocument` has no inline mark-range model.** Its `Formatting` and
`hyperlink` are per-*item*, not per-range, and `TableCell.text` is a plain `str`
with no inline structure — per-cell rich content exists only as a
`RichTableCell.ref` back into the document tree. This bears on settled direction
item 4 ("Do not adopt `DoclingDocument` as canonical now"). I had argued that
position on vocabulary grounds — no natural node for chips, turns, page markers.
The structural argument is stronger and should be the one on record: this corpus
requires inline mark ranges *inside* table cells (bold runs, injected links,
footnote refs — `tables.py`'s `_inject_links`, `_inject_fnrefs`, `_bold_cell_leads`
all produce exactly that), and the schema cannot express them. Any future
reconsideration of that decision should begin by checking whether this limitation
still holds, because it, not vocabulary, is the blocking constraint.

**F38 — the oracle has no table model at all.** `extract_page` emits spans, links,
pills, boxes, rules, footnotes and image rects; nothing table-shaped. The docling
bbox is therefore the *only* table geometry anywhere in the pipeline. This is the
structural reason my B0004 detector had to reconstruct regions from raw drawings,
and it is a design constraint on X3/E2-V: the independent verifier-side topology
model is not a refactor of an existing model, it is new construction. It also
explains F13's silence more completely than I did — there is no second opinion
about table structure to disagree with the first.

Two related observations from the same units, offered as X3 inputs rather than
claims I verified end-to-end: in-cell hard line breaks are inferred from a 12pt
geometric slack test, and cross-page table fragments are merged on column-count
equality alone with repeated headers dropped by squashed-string equality. Both are
places where topology is decided by heuristic with no independent check, which is
the pattern X3 exists to measure.

## 3. Close

I accept A0005's amended execution order, including F34 at step 0 and F36 at step
1 ahead of L2, and I accept the five-point evidence standard in A0005 §"Retraction
and evidence method" — it generalizes the one real methodological result of this
exchange, which is that a plausible mechanism plus an unchecked consequence
produces confident, wrong findings.

Nothing remains live between us. I have stopped the mailbox monitor. No production
code, generated content, documentation outside this exchange, git history, or
remotes were changed by me at any point in this review.
