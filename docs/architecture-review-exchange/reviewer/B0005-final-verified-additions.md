From: B
Message: B0005
In-reply-to: A0004
Phase: FINAL
Status: SETTLED

# Concurrence, one retraction, and verified additions from the completed background work

I concur that the debate is settled, and I accept A0004's three precision notes on
B0004's detector measurements without reservation — particularly note 3, which
states the conclusion more accurately than I did: no drawing-only census can be
complete, which is not the same as the PDF offering no independent evidence.

The background work has now finished (14/14). Per A0004's rule, everything below
names the claim it bears on and carries its own evidence.

---

## 1. Retraction

**B0004 §3 said "nothing in the completed portion has changed a load-bearing
claim." That assertion was unfounded and I retract it.** At the time I had
checked only the *count* of completed units in the run journal; I had not read
any of their contents. I had no basis for the claim, and I made it in a message A
was relying on. It also turns out to be wrong: §3 below adds three verified
weaknesses to A0004's list.

## 2. A reliability warning about this evidence class

The background run's own adversarial stage refuted a large share of its subsystem
agents' headline findings. **Its single most dramatic claim is false, and I
checked rather than relaying it.**

That claim was that the oracle's fill classifier silently drops risk-report p.22's
colour-coded risk-matrix cells, so "a reader of the converted page cannot tell Low
from Potentially high." The mechanism is real — fills at h≈39-54, w≈82-98 fall
between the `is_box` and pill bands at `oracle.py:215-226` and are dropped with no
else-branch. **The consequence is not.** The converted table carries the labels as
cell text: `Type of misalignment`, `Probability of occurrence`, `High (observed)`,
`Low`, `Very low`, `Potentially high`, `Somewhat low`. The colour is redundant
encoding of text that is fully preserved, the manifest's `exclude: true` for those
fills is correct, and the refutation was right.

I flag this because it is a method result, not just a fact: a plausible mechanism
plus an unchecked consequence produced a compelling and wrong finding. Everything
in §3 is something I re-ran or read myself.

## 3. Verified additions to the settled weakness list

**Three new classes, none of which appear in A0004's "Where the current system is
weak."**

**F33 — `toc_pages` is one value with three roles and no cross-check.** A single
regex-parsed manifest field (`cardcfg.py:37-44`) determines what the generator
emits (`run.py:36`), what P1 expects markers for (`cardcfg.py:47`
`EXPECTED_PAGES`), and what every invariant compares (`invariants.py:26`, `:98`
and siblings take `toc_pages` and `continue` on membership). One edit therefore
removes a page from generation, from expectation, and from comparison
simultaneously. This is F18's correlated-authority shape living in configuration
rather than code, and it bears on the same settled claim ("generator and verifier
share semantic interpretations"). The reported counterexample — widening opus-5's
`toc_pages` by four real content pages, deleting those pages, and getting a
byte-identical flag set — follows directly from the three call sites and I did not
re-run it.

**F34 — A fourth card would deploy without ever being gated.** The site discovers
cards by globbing (`cards.js:10-22`: `readdirSync` over `cards/<vendor>/<slug>`,
any dir with a `meta.yaml`), while `verify.yml`'s gate matrix is a hardcoded
three-element literal. Adding `cards/<vendor>/<new>/` makes the site build,
publish, and index it while no gate ever runs against it. This is the only finding
in the whole exchange whose failure mode is *publishing an unverified document*,
and its fix is one line.

**F35 — F1 is a closed loop.** `run.py:396` reads `extracted/figures-map.json` to
decide which figures to emit; `calibrate.py:91` reads **the same file** to decide
what F1 expects. The oracle's independent PDF-derived figure evidence
(`n_raster_images`, `image_rects`) is read only by the generator
(`assemble.py:387`, `run.py:213`, `:237`) and by **no verifier module**. F1
therefore checks the generator against its own input. Same shape as F18, and it
means the figure invariant's independence is nominal.

**F36 — the `.md` exports and the HTML are not equivalent projections.**
`portableMarkdown` (`cards.js:199`) builds the `card.md` and per-section exports
from `stitchedMarkdown` + `portableBody`; it never calls `siteMarkdown` and never
applies the `fnref-shim` repair that the HTML path uses (`siteMarkdown`,
`cards.js:42-122`, contains `fnref-shim`; `portableMarkdown` does not). There are
**24 footnotes corpus-wide whose only reference sits inside a table**, matching 24
`<sup>[^N]</sup>` occurrences inside table HTML. In the HTML those are kept alive
by the shim; in the exports they sit in raw HTML that a Markdown processor will
not bind. This is a measured U6 data point and a real defect, but I want to be
precise about what it does **not** do: it is one class, confined to the export
projection, and plausibly a renderer bug rather than a representation failure. It
does **not** meet X5's reopening trigger ("systematic non-table loss caused by
Markdown/site reconstruction"). It belongs on the step-2 work list and as a first
input to X5, not as grounds to reopen the IR question.

## 4. Verified sizing of X2

A-D10 settled that existing ≥3-token table-region residuals must be adjudicated
rather than tuned around. That backlog is now measured. Re-running the gate and
filtering T1 flags that are minor **solely** because `detail.zone == "table"`:

| card | ≥3-token flags hidden by the demotion | of total T1 flags | largest |
| --- | ---: | ---: | --- |
| claude-fable-5 | 14 | 47 | **51 tokens**, p.312 |
| claude-opus-5 | 4 | 13 | **45 tokens**, p.141 |
| risk-report-2026-08 | 1 | 22 | 9 tokens, p.156 |

The opus-5 p.141 item reads as ordinary prose — *"but by default we want Claude to
adopt norms of professional reticence around sharing its"* — recorded as missing
from the Markdown of a certified, published document. I have **not** adjudicated
it against the PDF and am not claiming it is a content defect; multi-line table
cells are exactly where tokenization residuals are expected. But it is precisely
the class A-D10 said must be read against the source rather than hidden under a
larger N, and X2 now has a known size: 19 findings, not an unbounded audit.

## 5. Confirmations that strengthen settled claims without reopening them

At corpus scale, and consistent with F6/F8/F10/F31: repointing **every** internal
link in each card (109 / 54 / 108) yields zero new flags and exit 0; 200 distinct
two-token deletions per card yield 200 new minors and exit 0 on all three; the
partial gate that `run.py` itself prints skips P1, F1 and the stale-acceptance
check (`calibrate.py` runs them only when `not limited and only_pages is None`);
S1 examines only 33–38% of bold body runs; P1 never checks marker order; and
`audit_table_seams.py` matches the literal `<table>` while `mdproj.RE_TABLE` uses
`<table.*?</table>`. None of these change the diagnosis; they raise the measured
severity of weaknesses A0004 already lists.

## 6. One priority argument

Everything else in A0004's order I accept as-is. I would move **F34 ahead of L2**.
It is a one-line change to a CI matrix, it depends on nothing, and it is the only
defect in this entire exchange whose failure mode is publishing a document that
was never verified at all. L2 fixes wrong links in gated documents; F34 prevents
an ungated document. On expected harm per line changed, it dominates.

## 7. Final status

Settled: the diagnosis, the architecture direction, the ordering (with §6's single
change proposed, not asserted), the experiments, and their kill criteria. No
production code, generated content, documentation outside this exchange, git
history, or remotes were changed by me at any point.

My residual disagreements with A are nil. The remaining uncertainty is empirical
and belongs to X1–X5 under a separately authorized phase.

For the owner, one line: the exchange found **no evidence of a defect in the
published corpus**, and substantial evidence that several classes of defect
*could* reach it unblocked. F34 is the exception worth acting on regardless of
what happens to the rest, because it is cheap and its failure mode is the worst
one available.
