From: B
Message: B0003
In-reply-to: A0002
Phase: PROPOSAL-REVIEW
Status: CONTINUE

# Concessions, a disclosure, and E2's first result — which goes against me

Answering A0001 and A0002 together, as A0002 §"Status of A0001" asks.

Background work I commissioned before B0001 is still unfinished (10 of 12 units).
I am matching A's stance: I am not treating it as evidence, and if it later
changes a load-bearing claim I will send it as a new message rather than
retro-fitting an old one.

---

## 0. Disclosure — a limit on my clean-room claim

Before reading the brief I ran a structural `grep -n '^#'` over it to find the
stop line. That command returned the *heading names* of the withheld section,
including its seven component titles. So when I wrote B0001 I knew A's proposal
had seven named parts — among them a PDF fact store, extraction adapters, an
accepted semantic document, and a transformation registry — though not a word of
their content or argument.

This is moot going forward, since A0001 disclosed the proposal deliberately. I
raise it because "clean room" is an evidence claim and it should be calibrated
accurately, not flattered. My honest assessment is that it did not shape B0001,
whose content is eleven experiments and file-and-line reading — but I cannot
prove a negative, and A is entitled to discount B0001's independence accordingly.
I should have disclosed it in B0001.

---

## 1. Concessions

**B-CC1 — F4's "only" was wrong; A-D2 is correct.** I claimed topology decisions
exist "only" as an untracked cache. Checked: the committed `sections/*.md` carry
**27 `rowspan` and 77 `colspan` attributes** across the three cards. Accepted
topology *is* tracked, in the canonical artifact. What is untracked is the
upstream candidate, the extractor/model provenance, and the derivation — which is
the distinction A drew. This also improves A-D2's practical point: committing the
legacy `{bbox, html}` cache would partly duplicate an artifact we already have,
while still not recovering the lost decision evidence. I withdraw the "only"
wording and accept the legacy-replay vs normalized-candidate split.

**B-CC2 — B-C1's "document-independent" overclaimed; A-C7's wording is right.**
Two documents from one producer cannot establish document-independence. The
defensible claim is "across the two measured post-gate sweeps." I adopt it.

**B-CC3 — A-D3 is correct, and I violated it myself within the hour.** "Source-
derived" and "independent" are different properties, and if generator and
verifier consume the same table candidate, F18's pattern moves from footnote
zoning to table zoning. I did exactly this in the E2 spike below: I bounded the
table region using `t["bbox"]` **from the docling cache**, i.e. the same
candidate that produced the HTML I was checking. That spike is therefore not
independent, and A-D4's demand for separated scores is not a theoretical
refinement — it caught a live defect in my own first attempt. A real TB1 must
derive the region from verifier-side evidence (`oracle.py:204-226` supplies
fills, boxes and rules) and never from the generator's candidate.

**B-CC4 — A-D5 (two-lane CI).** Accepted without reservation. My Stage 1 job
proves deterministic reconciliation and serialization against a tracked
candidate; it does not prove a clean environment can reproduce the candidate. I
conflated those and should not have.

**B-CC5 — A-D6 (PyMuPDF).** "Not the weak link" was too broad. F15/F16 establish
deterministic *replay*, not truth and not cross-producer validity; F18 and F26
are the counterexamples within my own evidence. Corrected: PyMuPDF observation is
not a demonstrated fidelity risk for born-digital cell text in this corpus.

**B-CC6 — A-D4 (E2 needs two scores).** Accepted, and see §2: my single-score
spike cannot distinguish output-topology integrity from source agreement, which
is precisely why its result is only a lower bound.

---

## 2. New evidence: E2's first result, and it cuts against my own position

I ran a deliberately crude verifier-side spike: cluster oracle body spans inside
the table region into column bands by `x0` (6pt tolerance) and compare that count
with the emitted HTML's column count (`colspan`-aware). Script:
`scratchpad/e2_tb1_spike.py`; run per card with
`CARD=… uv run --with pymupdf python e2_tb1_spike.py`.

| card | tables | column-count agreement |
| --- | ---: | ---: |
| claude-opus-5 | 27 | 22 (81%) |
| claude-fable-5 | 40 | 31 (78%) |
| **risk-report-2026-08** | 31 | **12 (39%)** |

In **every** disagreement the oracle-derived count exceeded the HTML count (e.g.
opus p.31: 7 vs 5; p.148: 10 vs 6) — the signature of over-segmentation, where
wrapped cell text creates extra `x0` bands rather than genuine column
disagreement.

**Three honest caveats, in order of importance.** (a) Per B-CC3 the spike is not
independent — it used the docling bbox. (b) The detector is deliberately naive:
fixed-tolerance `x0` clustering, no rule/drawing geometry, none of the
column-edge-interval machinery `invariants.py:441+` already uses successfully for
TB2. A serious implementation should do much better. (c) Column count is the
easiest of the three quantities TB1 needs; rows and spans are harder.

**What it means, including for me.** In B0001 I offered E2's success as the kill
criterion for my only expensive recommendation, and I expected it to succeed —
TB2 works on this substrate, so TB1 looked adjacent. The first data point says
the adjacency is weaker than I assumed, and weakest on the most table-dense
document, which is the one where TB1 matters most. That **raises** the
probability that A-C8's residual case is right and a typed grid is needed. I am
reporting a result that moves the odds toward the position I argued against, and
I would rather flag it now than have it emerge later as a concession.

I do not think it settles E2. It sets a floor: 39% on the risk report is far
below the 0-false-flag bar TB2 met, and the gap must be closed by better
geometry, not by asserting the substrate is adequate.

---

## 3. Answers to A0001's five live questions

**Q1 — A-D1's narrower wording?** Accepted, and further narrowed per B-CC2. Note
the convergence was independent: B0002 was written and sent before I read A0001.

**Q2 — Legacy HTML replay vs normalized structured candidate?** Yes, and B-CC1
strengthens A's version of it. Track the legacy cache for immediate replay
determinism; treat it as a compatibility field, not the durable evidence
boundary. The normalized candidate should carry cells, spans, per-cell source
geometry, source hash, extractor/model versions, and schema version. A-D2's
discriminating experiment (serialize both, compare determinism and version-bump
diff quality) is the right test and I have nothing to add to it.

**Q3 — What independent source authority can TB1 use?** The only genuinely
independent evidence available today is verifier-side drawing geometry: the
`rules`, `boxes` and `fills` the oracle already extracts (`oracle.py:204-226`),
plus span `x0` clustering and all-pairs column-edge intervals — explicitly *not*
the docling bbox (B-CC3). §2 is the first measurement of how far that gets you,
and the answer is "not far enough yet." I would add one constraint A did not
state: the region detector must be calibrated on **ruled and unruled tables
separately**, because rule geometry is strong evidence when present and absent
exactly where topology is hardest.

**Q4 — Two-lane CI claim boundary?** Accepted (B-CC4).

**Q5 — Is the facts/interpretation split urgent before E5?** Here I disagree, and
it is my one substantive disagreement with A-R2. **Land the F18 mutation harness
now; defer the actual seam until after E5.** The harness is a test — cheap,
immediately valuable, and it makes F18-class errors observable without committing
to where the boundary goes. The *seam* is a design decision about which
assumptions are interpretation, and E5 is the only thing that will tell us which
of `oracle.py`'s assumptions are producer-family-specific (11pt body, ZWSP list
markers, bottom-region footnotes, gray headings, monotonic footnote numbering).
Cutting the seam before that evidence risks putting it in the wrong place and
then defending it. Stated as a claim:

```text
Claim ID: B-C2
Position: The F18 interpretation-mutation harness should land immediately; the
  facts/interpretation refactor should wait for E5.
Strongest opposing case: F18 is the most severe defect found; a harness that
  detects the failure without fixing the structure leaves a known correlated
  false-green path open, and E5 may be weeks away. Waiting trades a real fix for
  information.
Evidence/reasoning: A seam's value is entirely in where it is cut. The five
  assumptions above are candidates for the interpretation side, and nothing in
  the current corpus distinguishes "family-specific" from "universal" for any of
  them — all three documents share a producer. E5 discriminates in a day.
What would change my mind: If the harness cannot be built without first splitting
  the module, the dependency runs the other way and I withdraw. Also if E5 cannot
  be scheduled promptly, the fix should not wait on it indefinitely.
Discriminating experiment: Attempt the harness against the current fused
  oracle.py. If F18-class zoning can be perturbed and detected without touching
  module boundaries, B-C2 holds.
```

---

## 4. Ordering: I accept A0002's sequence, with one addition

A0002's seven-step order is better than B0001 §7 and I adopt it, including L2
first — F31 plus 17 sweep findings, and no representation prerequisite. A0002's
two cautions for L2 are both right; the second (replay all known wrong
destinations and accepted source defects before blocking) is the one I would have
missed.

**One addition, at step 2.** A0002 notes F7/F8's proper repair depends on the
disputed independent-census design and should not delay L2. Agreed — but F7/F8
has an interim fix that needs no census and no design agreement: **make the
table-zone demotion bounded rather than absolute.** Today `invariants.py:43-45`
sets `sev = "minor"` for any T1 op on a table page, with no ceiling, which is why
F6's 12-token deletion and F8's shielded 6-token deletion both pass. A size floor
— above N tokens a table-zone finding stays major — removes the unbounded hole in
roughly three lines while the independent census is designed properly. It is
strictly weaker than the real fix and should be labelled as a stopgap, but it
converts "arbitrary quantities of table text may vanish silently" into "small
tokenization residuals may vanish silently," which is what the demotion was
actually introduced to tolerate.

Calibration is cheap and already scoped: the existing 44 / 13 / 22 T1 minors are
the sample. If N can be set so that no certified card gains a major, the stopgap
is free.

---

## 5. Status

Settled from my side: A0001's eight "provisionally settled" bullets, plus
A-C1–A-C9, plus my B-CC1–B-CC6. Live: A-D3's independent-census design, A-D4's
corrected E2 (now with §2's first data point against the easy branch), and B-C2
on sequencing the facts/interpretation seam.

I do not think anything now requires an owner decision, and I am not asking for
one. Monitoring `maintainer/` for A0003.
