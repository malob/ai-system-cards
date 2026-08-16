From: B
Message: B0002
In-reply-to: A0000
Phase: CLEAN-ROOM
Status: CONTINUE

# Clean-room addendum: I falsified part of my own headline

This is not a reply to A0001, which has not arrived. It is a correction to
B0001, sent before A replies so that A is not arguing against a framing I have
already partly defeated. I ran the experiment I named in B0001 §8 as "the
cheapest and most decisive" and as the one most likely to be wrong (E1,
resolving U3), and it went against me. B0001 remains sent and unedited per
protocol; this message supersedes its §1 emphasis and §5 ranking where they
conflict.

Still clean-room: I have not read `## The architecture hypothesis to review`,
any `maintainer/` message after A0000, or `docs/generation-design.md`.

---

## 1. What I got wrong

B0001 §1 led with tables and ranked `export_to_html()` as the **first**
accidental complexity. That framing is too narrow. It is well supported on the
Risk Report and materially weaker on Claude Opus 5.

**F29 — Classifying every major finding in the two post-gate inspection sweeps
by construct, tables are a plurality, not the story.** Source:
`pipeline/.cache/rr-sweep1/findings-*.jsonl` (experiment 11) and
`pipeline/.cache/opus-sweep1/findings-*.jsonl` (experiment 10), read directly;
the rr total of 66 matches that experiment's README, which is my check that I
parsed the right records.

| construct | risk report | opus-5 | total |
| --- | ---: | ---: | ---: |
| table | 31 | 11 | 42 |
| link | 15 | 2 | 17 |
| list | 9 | 7 | 16 |
| paragraph | 5 | 1 | 6 |
| seam | 3 | 1 | 4 |
| turn | 1 | 2 | 3 |
| heading | 0 | 2 | 2 |
| other / code | 2 | 1 | 3 |
| **total majors** | **66** | **27** | **93** |

Table-attributed (by construct label *or* by the page being a table page):
**39/66 = 59% on the Risk Report but only 11/27 = 41% on Opus 5**; 50/93 = 54%
overall. Pages carrying majors that sit inside the T1-demoted / S1-ST-skipped
spill set: **69% on the Risk Report, 31% on Opus 5.** The table-centric
diagnosis is document-dependent — it tracks how table-dense the document is
(the Risk Report has 31 table pages in 180; Opus 5 has 23 in 187 and its
defects skew to lists, headings, turns and code). B0001's §1 generalized from
the more table-heavy document.

## 2. The framing that survives both documents

Sorting the same 93 findings by *which invariant should have owned them* rather
than by construct produces a diagnosis that holds across both sweeps:

**F30 — 81% of post-gate majors fall in two invariants the contract declares
but never implemented, plus the one implemented invariant with the weakest
blocking recall.**

| owning invariant | status in `verification-contract.md` | findings | share |
| --- | --- | ---: | ---: |
| TB1 — table topology/spans | *"design target; inspection-owned today… No `TB1` flag is emitted"* | 42 | 45% |
| L2 — destination resolution | *"covered by the site/link audit rather than a separately emitted `L2` verifier flag"* | 17 | 18% |
| ST1/ST2 — list & block structure | implemented, weakest measured blocking recall | 16 | 17% |
| everything else | — | 18 | 19% |

**F31 — L2's absence is silent end-to-end, exactly as TB1's is (B0001 F13).**
The Risk Report contains 108 internal links across 66 distinct anchors. I
repointed one at a different existing section
(`#61-threat-model-criteria` → `#35-acceleration-of-ai-progress-due-to-automated-ai-rd`),
leaving the link text untouched, so the reader is sent to the wrong section of a
safety report. Gate output was byte-identical to baseline —
`FN1 minor 1 / T1 minor 22 / TB2 minor 1`, **exit 0**. Reproduce:

```sh
env CARD=anthropic/risk-report-2026-08 uv run --with pymupdf python pipeline/verifier/calibrate.py /abs/path/to/mutated-sections
```

This is the same shape as F13 and it accounts for the 15 link majors experiment
11 found (its README lists wrong `GoTo` destinations on pp. 12, 26–27, 60, 82,
114, 146, 183).

**F32 — The list finding converges with my own mutation measurement.** Lists are
the #2 construct in *both* sweeps (9 and 7). Independently, `split-item` (ST2)
is the weakest class in my blocking-recall run (B0001 F9): **3/8, 3/8, 5/8 =
11/24 = 46%**. Two unrelated evidence sources — agent inspection of the shipped
corpus, and seeded mutation of it — point at the same weak invariant. I trust a
convergence like that more than either source alone.

## 3. What this changes, and what it does not

**Changed — B0001 §5's accidental-complexity ranking.** The first entry should
not be `export_to_html()`. It should be: *invariants that the contract declares
and no one wrote.* TB1 and L2 together are 63% of the post-gate defect mass, and
neither is blocked on a representation decision — L2 needs no new data structure
at all, only an anchor-resolution check the site already performs at build time.
`export_to_html()` drops to the cause of *one* of the two, and only for the
topology half of it.

**Changed — B0001 §7 Stage 3.** "Attempt TB1" was too narrow. Stage 3 is now
*write both unwritten invariants and harden the weak one*: TB1 (topology), L2
(destination resolution — cheapest of the three and the highest ratio of defects
caught per line), and ST2 recall. On this evidence L2 should be done **first**,
ahead of anything table-shaped: it is the smallest, it needs no new
representation, and it closes 18% of the measured defect mass.

**Changed — my confidence in Stage 4.** B0001 rated the typed cell grid
"low–medium". F29 lowers it further: if only ~45% of post-gate defects are
table-shaped and the topology gate (E2) may be writable on the current
substrate, the grid is justified by a shrinking slice. I would now want E1's
result *and* E2's before defending it at all.

**Unchanged — B0001 §1's structural findings.** Nothing here touches F7/F8
(scope derived from the output), F12/F18 (correlated false green through the
shared oracle), F10 (severity as a token count), or F11 (production gate running
in calibration mode). Those are policy defects independent of construct mix, and
F18 in particular — a paragraph silently relocated out of an executive summary
into a dangling footnote, gate green — remains the most serious single thing I
found. The cheap Stage 1 and Stage 2 work is, if anything, better justified now:
it is the part of my recommendation that does not depend on which document you
sampled.

**Unchanged — my rejection of a whole-document IR as the answer.** F29 cuts both
ways and I should say so plainly: a diagnosis that spreads defects across
tables, links, lists, headings and turns is *more* congenial to a uniform
document model than a table-only diagnosis was. The reason I still reject it is
F31 — the largest single non-table class is wrong link *destinations*, which no
document model fixes. You fix it by resolving anchors and comparing them to the
PDF's `/GoTo` targets, which the oracle already extracts
(`oracle.py:183-202`, including the `dest_y` top-down conversion). A typed IR
would carry that defect through unchanged.

## 4. Standing claim for the debate

```text
Claim ID: B-C1
Position: The dominant, document-independent cause of the shipped corpus's
  residual defects is unwritten and under-powered verification, not the
  canonical representation. 81% of post-gate majors across both inspection
  sweeps belong to two declared-but-unimplemented invariants (TB1, L2) and the
  implemented invariant with the weakest measured blocking recall (ST2).
Strongest opposing case: Those invariants went unwritten for a reason. TB1 in
  particular may be unwritable against an HTML string, in which case the
  representation IS the cause and I have merely described the symptom. A
  proposal that makes all three invariants cheap to write is then better than
  one that writes them against the current substrate.
Evidence/reasoning: F29-F32 above; F13 and F31 show both unwritten invariants
  fail silently end-to-end; F9's blocking-recall data independently identifies
  ST2 as weakest, matching the sweeps' #2 construct.
What would change my mind: E2 failing — i.e. a serious attempt at TB1 on the
  current substrate that cannot state the invariant without first
  reconstructing a cell grid. That would convert my "policy" diagnosis into a
  "representation" diagnosis for the table half, and I would concede it.
Discriminating experiment: E2 (B0001 §8). L2 is not in dispute: it is writable
  today against oracle `/GoTo` targets, and if anyone believes otherwise the
  disagreement is settled by trying it in an afternoon.
```

I am now watching `maintainer/` for A0001 on a live file monitor and will reply
in B0003.
