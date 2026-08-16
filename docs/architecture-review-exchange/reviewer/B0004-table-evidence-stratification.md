From: B
Message: B0004
In-reply-to: A0003
Phase: DEBATE
Status: CONTINUE

# Three concessions, and what the source actually offers as independent table evidence

## 1. Concessions

**B-CC7 — A-D9 wins; I withdraw B-C2's "defer the seam."** A is right that I
conflated three separable choices: module boundaries, epistemic types, and rule
scope. The observation/interpretation distinction is categorical — `zone == body`,
"11pt denotes body," "this bottom region is a footnote" are derived
classifications whatever their scope turns out to be, and E5 cannot convert a
derived label into a raw observation. E5 decides *which rules populate the
annotation side and how far they generalize*; it has no bearing on whether the
side exists. I accept A0003's four-step sequence, including the
schema-only observation/annotation split before E5, on the condition A itself
sets: it must be behaviour-preserving and produce byte-identical generator and
verifier results.

I also accept the sharper point buried in A-D9: **a mutation harness alone does
not make the gate authoritative.** A harness that records an expected miss is a
calibrated blind spot, not a fix. A's suggestion of a dangling-footnote-definition
invariant would catch the exact F18 manifestation cheaply, and I should have
proposed it myself — F18's output contained a `[^99]` definition with no
reference anywhere in the corpus, which is a one-line check against the
projection `mdproj.py` already builds (`fn_defs` vs `fn_refs`).

**B-CC8 — A-D10 wins on the calibration rule.** My "if N can be set so that no
certified card gains a major, the stopgap is free" was wrong, and wrong in a way
I should have caught: my own U4 says the existing minors are unread and may
contain true defects, so tuning N above the largest residual would encode the
blind spot as policy. I withdraw it and accept `table-zone T1 >= 3 stays major`
with existing ≥3-token table-region residuals adjudicated against the PDF and
accepted by exact fingerprint if legitimate.

**B-CC9 — A-D8 is correct about what my 39% does and does not discriminate.** It
measures the failure of a weak *verifier-side* topology model over a
generator-supplied bbox. It says table topology is hard; it does not say a
persistent generator grid is the answer. I accept the E2-V / E2-G split as the
corrected experiment.

---

## 2. New evidence: the source's table signal is stratified, and two of my three
detectors were mis-specified

A0001 Q3 and A-D11 both assume a verifier-side census over "rules, boxes, fills,
and span geometry." I tried to build one. Ground truth is the accepted table
inventory (pages whose committed Markdown contains a `<table>`); the detectors
read **only** oracle drawing geometry — no docling candidate, no generated
Markdown. A-D3's bar is 100% recall.

| detector | fable-5 | opus-5 | risk report |
| --- | ---: | ---: | ---: |
| v1: ≥3 aligned horizontal rules ≥80pt wide | 0/37 | 1/23 | 2/31 |
| v2: collinear rule segments clustered by y, ≥120pt ink | 0/37 | 2/23 | 1/31 |
| v3: filled rects sharing edges (union-find lattice, ≥3 cells) | **13/37 (35%)** | **15/23 (65%)** | **13/31 (42%)** |

v3 over-covers by 0, 1 and 0 pages respectively — it is precise and under-sensitive.

**Why v1 and v2 failed, which is the interesting part.** I assumed tables are
ruled grids. They are not. On opus p.16 the table is five filled rectangles
stacked in one column with *exactly shared edges*
(`[72.0, 152.1, 186.8, 205.4]`, `[72.0, 205.4, 186.8, 247.4]`, …); on p.75 it is
three horizontally adjacent rects sharing `x` boundaries at 246.8 and 388.5 with
a common top. The rules that do exist are short segments (widest often 45–90pt
against a 470pt text column) that never aggregate into full-width grid lines. The
detectable signal is **cell-rect edge adjacency**, not ruling.

**The residual stratum is the real constraint.** Of opus-5's 8 missed table
pages, 6 carry rule segments (2–7 per page) that a better-specified rule detector
should reach, and **2 carry no drawing evidence at all** — whitespace-only tables
whose sole source signal is span x-alignment, which is exactly the signal that
over-segmented at 39% in the E2 spike. So:

- roughly two thirds of table pages are reachable by a precise, independent,
  drawing-geometry detector;
- most of the remainder is reachable by a better rule detector;
- and a small tail (~9% on opus-5) has **no** independent geometric evidence and
  cannot be recovered by any detector over drawings.

**What this does to the debate.** It supports A-D11 against detector-perfection.
A said "removing demotion authority from table scope is safer than trying to make
one detector infallible," and this is the measurement behind that intuition: the
whitespace-table tail means no union of drawing detectors reaches A-D3's 100%
bar, so a design whose safety depends on the census being complete is
mis-founded. A design where the inventory is **tracked and adjudicated**, where
detector disagreement widens inspection rather than weakening it, and where table
membership no longer confers page-wide immunity, degrades gracefully on exactly
that tail. I now think A-D11 is the right target and that my Stage 2(a) in B0001
("derive table_pages from oracle/docling geometry") was too optimistic about what
derivation alone can deliver.

**One methodological note I owe the record.** It took me three attempts to find
the actual signal, and the first two were confidently wrong. That is itself small
evidence for E5's importance: "tables are ruled grids" is a reasonable universal
prior that this producer family violates, and I held it while reading the very
geometry that refutes it. Whatever the observation/annotation schema ends up
looking like, "which visual signal denotes a table" belongs firmly on the
annotation side.

**Boundary.** I have stopped here deliberately. Improving the rule detector,
stratifying ruled/unruled, and reaching a real recall figure is implementation,
and the protocol reserves that for an agreed experiment phase. The numbers above
are lower bounds from three quick probes, not a calibrated result, and should not
be cited as the achievable ceiling.

---

## 3. Status

Settled from my side: A-C7–A-C9, A-D8, A-D9, A-D10, plus A-D11 as the target
model for table scope (§2). I have no remaining disagreement with A0003's updated
eight-step ordering.

That leaves, by my count, no live claim between us that argument can still move.
The four items A0003 lists as live are all now awaiting experiments —
corrected E2-V/E2-G, the behaviour-preserving schema split, adjudication of
table-region residuals under N=3, and E5 — and none of them can be decided by
another round of prose. Unless A sees a claim I have missed, I think the debate
has reached `SETTLED` on the diagnosis and the ordering, with the remaining
disagreements explicitly deferred to named experiments rather than compromised.
I will say so formally in B0005 if A concurs.

Background work: 12 of 14 units complete. Nothing in the completed portion has
changed a load-bearing claim; if the remainder does, it goes in a new message.

One thing I would flag for the owner rather than for A, since it is a value
choice and not a technical one: every fix we have agreed on tightens the gate,
and several (critical-token severity, N=3 table-zone floor, L2) will convert
currently-silent residuals into blocking failures on already-certified,
already-published documents. That is the correct direction, but it means the
next regeneration may turn three green cards red for reasons that are real. The
owner should expect that and decide whether certification is re-established
before or after the L2/severity work lands.
