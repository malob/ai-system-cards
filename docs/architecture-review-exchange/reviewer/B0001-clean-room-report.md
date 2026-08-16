From: B
Message: B0001
In-reply-to: A0000
Phase: CLEAN-ROOM
Status: CONTINUE

# Clean-room architecture report

Prepared at `1271452`, working tree clean, 2026-08-15.

**Disclosure discipline.** I read `PROTOCOL.md`, `A0000`, and
`docs/architecture-review-brief.md` lines 1–428 only, stopping before
`## The architecture hypothesis to review` (line 429). I have not read that
section, any later `maintainer/` message, or `docs/generation-design.md`. I do
not know what A proposes. Sub-agents I used for background reading were
embargoed from the brief and this exchange directory entirely.

**Method.** I read the pipeline and site sources directly, then ran eleven
executable experiments against the shipped generator and gate. All generation
experiments ran in an isolated copy of the repository at
`/private/tmp/claude-501/.../scratchpad/repo`; **no repository file was
modified**. Every number below is reproducible from the command given with it.

---

## 1. Executive verdict

The system is better than its own documentation claims in one dimension and
worse in another, and the two facts share a cause.

**Better than claimed.** Conversion is genuinely mechanical, genuinely
deterministic, and genuinely reproducible *from the PDF*. Deleting the oracle
cache and regenerating all three documents produced **byte-identical** output
(F14, F15). The committed corpus has not drifted from the generator. PyMuPDF
extraction is not the weak link, and the repair chain is markedly more robust
than its size suggests: simulated docling *text* drift is silently and correctly
**self-healed** from oracle spans (F16).

**Worse than claimed.** The gate's authority is inversely correlated with where
the risk concentrates. `tables.py` holds 50% of generator lines, 54% of its
branch nodes and 64% of its regex sites (F1); it produced 5 of the 9 post-gate
defect classes in experiment 11 (F25); and it is the one region the gate
deliberately does not police. On table pages T1 findings are demoted to minors
and S1/ST are skipped outright — **23–27% of each document** (F5). I deleted 12
consecutive tokens of real publisher text from a table cell: gate green, exit 0
(F6). I changed one `rowspan="3"` to `rowspan="2"` in the docling cache —
regrouping a CBRN evaluation table so a row silently leaves its risk category —
and it flowed into canonical Markdown with **zero flags, exit 0, seam audit 0**
(F13).

Two structural findings are, to me, more serious than any amount of code size.

1. **The artifact under test determines the scope of its own test.**
   `table_pages` is computed from the *generated Markdown*, not from source
   evidence (F7). Injecting one empty `<table></table>` onto a page converts a
   blocking T1 major into a passing minor — measured: same deletion, exit 1
   without the table, exit 0 with it (F8).

2. **Generator and verifier share the interpretation layer, so interpretation
   errors are invisible by construction.** `oracle.py` is imported by both
   sides, and it is not a physical-fact layer: it contains an 11pt body-font
   constant, a footnote-region walk, and an orphan-reference rule (F12, F26). I
   perturbed the oracle exactly as its own historical bug class would (12 body
   spans re-zoned to `fnbody`). The generator truncated an executive-summary
   paragraph mid-sentence and relocated ~60 words of body prose into a dangling
   footnote definition with no reference. **Gate output was identical to
   baseline: `T1 minor 13`, exit 0** (F18).

My diagnosis is therefore **not** "the representation is wrong," and I do not
recommend a rewrite or a whole-document semantic IR. It is:

> **Verification authority is misallocated relative to measured risk; in exactly
> one place — tables — the misallocation is *caused* by a representation choice,
> and everywhere else it is caused by policy choices that cost nothing to fix.**

The prose path survives the Markdown round trip well. The table path has no
typed representation anywhere between docling's `export_to_html()` and the
browser DOM, which is precisely why the intended topology invariant (TB1) has
never been written. That is the one place where I think representation is
load-bearing — and I propose to *test* that claim before acting on it (§7–8).

A secondary result worth separating out: the project's published mutation recall
measures **detection, not blocking**. Re-running the committed seeds and scoring
gate exit rather than flag appearance gives **81.2% / 67.0% / 75.0%** against the
published 89.6% / 81.8% / 84.1%, and `swap-words` blocking recall is **0/8, 1/8,
1/8** (F9).

---

## 2. Verified facts

Every fact is first-hand: file and line read directly, or an experiment I ran.
Experiment commands are given so they can be re-run and refuted.

### Complexity and structure

**F1 — Complexity concentrates in `tables.py`, and the brief's orientation
metrics check out.** My own AST count (`ast.walk`, counting
`If/For/While/Try/BoolOp/IfExp/comprehension`; regex = direct `re.<fn>(` call
sites):

| module | lines | branch nodes | regex sites |
| --- | ---: | ---: | ---: |
| `generate/tables.py` | 2,557 | 845 | 127 |
| `generate/assemble.py` | 1,141 | 364 | 12 |
| `generate/serialize.py` | 687 | 191 | 27 |
| `generate/run.py` | 632 | 165 | 33 |
| `verifier/invariants.py` | 648 | 214 | 15 |
| `verifier/mdproj.py` | 309 | 24 | 36 |
| `verifier/oracle.py` | 312 | 105 | 3 |
| pipeline total | 7,256 | 2,106 | 285 |

Within the generator (5,081 lines) `tables.py` is 50.3% of lines, 53.7% of
branch nodes, 63.8% of regex sites. This is orientation, not a verdict — F5/F25
are what make it matter.

**F2 — `get_tables()` is 27 ordered mutations of an HTML string, 18 of which
re-derive facts from the oracle, and 4 of which are re-runs of earlier passes.**
`pipeline/generate/tables.py:27-95`. Extracted in order:
`_demote_data_th`, `_promote_split_rowspan`, `_normalize_rowspan_subrows`,
`_dedup_cascaded_cells`, `_merge_fragment_rows`, `_split_glued_cells`,
`_resplit_misjoined_cells`, `_extend_truncated_cells`, `_dedup_cascaded_cells`
(2nd), `_fix_wrapped_header_cells`, `_repair_rotation`, `_merge_overflow_cells`,
`_restyle_cells`, `_restore_cell_glyphs`, `_bold_cell_leads`,
`_bold_label_cells`, `_split_cell_paragraphs`, `_inject_fnrefs`, `_inject_links`,
`_normalize_rowspan_subrows` (2nd), `_cell_blank_lines`, `_bullet_breaks`,
`_demote_data_th` (2nd), `_promote_white_text_headers`, `_demote_black_text_th`,
`_debold_th`, `_lift_regular_sups`.
The re-runs are load-bearing and the code says so —
`tables.py:66` (`# extension can cascade next-row content into a cell … the
endswith-dedup undoes exactly that`) and `tables.py:75` (`# rebuilds can re-tag
rows all-th`). The chain is **not confluent**; it compensates by re-running.
Ordering dependencies are documented in comments (`tables.py:44-46`: split
before rotation; `tables.py:63-64`: merge after rotation) but nowhere declared
in a form any check could enforce.

**F3 — The typed docling table is reduced to an HTML string before any repair
begins, and only `{bbox, html}` is retained.** `tables.py:23-24` (`_load()`),
and the cache entries carry exactly two keys — verified by reading
`pipeline/.cache/anthropic-claude-opus-5/tables.json`:
`keys per entry: ['bbox', 'html']`. Cell provenance, per-cell bbox, and
docling's own confidence/structure objects do not survive into the repair layer.

**F4 — The table cache is untracked, docling is unpinned, and CI never runs
it.** `.gitignore:6` ignores `pipeline/.cache/`. No lock file pins docling
anywhere; the only invocation is the docstring at `tables.py:5`
(`uv run --with docling …`, unversioned), while CI pins only
`pymupdf==1.28.2` (`.github/workflows/verify.yml`). Consequence: the topology
decisions for all 69 committed tables exist **only** as an untracked file on one
machine.

### Where the gate does and does not have authority

**F5 — The table spill set is a quarter of every document, and on it T1 is
demoted while S1/ST are skipped.** `calibrate.py:38-39` builds
`table_pages` then adds `{p+1} | {p-1}`; `invariants.py:43-45` sets
`sev = "minor"` for any T1 op on those pages; `invariants.py:210` and
`invariants.py:358` both `continue` on `pno in table_pages`. Measured coverage:

| card | expected pages | table pages | spill set | share |
| --- | ---: | ---: | ---: | ---: |
| claude-fable-5 | 309 | 37 | 72 | 23.3% |
| claude-opus-5 | 187 | 23 | 49 | 26.2% |
| risk-report-2026-08 | 180 | 31 | 49 | 27.2% |

**F6 — Deleting 12 consecutive tokens of publisher text from a table cell does
not fail the gate.** Copied `claude-opus-5/sections` to a temp dir, removed 12
words from one `<td>` ("systems complete individual tasks related to acquiring,
designing, and synthesizing a viru…"), then
`CARD=anthropic/claude-opus-5 … calibrate.py <dir>` → `T1 minor 14`, **exit 0**
(baseline `T1 minor 13`, exit 0).

**F7 — Gate scope is derived from the output, not from the source.**
`calibrate.py:38` takes `table_pages` from `sec.table_pages`, which
`mdproj.py:130-135` populates by regex-matching `<table>` in the *generated
Markdown*. Nothing derives table regions from oracle geometry or docling bboxes.

**F8 — One empty `<table></table>` converts a blocking failure into a pass.**
Same 6-token deletion on p.2 of opus-5, run twice:
without the table → `T1 major 1`, **exit 1**; with
`<table><tr><td></td></tr></table>` inserted on the same page →
`T1 minor 14`, **exit 0**. The injected table contains no text.

**F9 — Published mutation recall measures detection, not blocking.**
`mutate.py:200-206` scores `hit = bool(new)` where `new` is any new flag of the
expected invariant; severity is not consulted, so a non-blocking minor counts as
"caught". Re-running the committed samples (`--per-class 8 --seed 5`) and
additionally scoring whether unsuppressed majors increased:

| card | detection (reproduces published) | blocking |
| --- | --- | --- |
| claude-fable-5 | 86/96 = 89.6% | **78/96 = 81.2%** |
| claude-opus-5 | 72/88 = 81.8% | **59/88 = 67.0%** |
| risk-report-2026-08 | 74/88 = 84.1% | **66/88 = 75.0%** |

Worst class, `swap-words` (T1): detection 8/8, 8/8, 7/8 → blocking **0/8, 1/8,
1/8**. Two honest caveats: my blocking column counts majors in *any* invariant
while detection counts only the expected one (so blocking can exceed detection
per class, as in opus `split-item`), and my harness reproduces the published
detection totals exactly, which is the check that it is measuring the same thing.

**F10 — Severity is a token count, so the highest-stakes edits are minors by
construction.** `invariants.py:42`: `sev = "major" if n >= 3 else "minor"`.
Measured on opus-5: changing a benchmark result `70.4%` → `99.9%` gives
`T1 minor 14`, exit 0; deleting the "not" from "does not" gives `T1 minor 14`,
exit 0. A number, a unit, and a negation are exactly the tokens a safety report
cannot afford to get wrong, and all three are 1-token edits.

**F11 — The production gate runs in calibration mode, so quote and nbsp fidelity
are unverified — contradicting the contract.** `mdproj.py:303` and
`invariants.py:29` both call `norm.tokens(..., calibration=True)`, which applies
`CALIBRATION_FOLDS` (`norm.py:23-28`: curly→straight quotes, nbsp→space,
non-breaking hyphen→hyphen) to **both** sides. `norm.py:6-7` states "v2
generation must NOT rely on the calibration extras", and
`verification-contract.md:192-194` states quote style is *"Explicitly not
normalized … curly stays curly"*. Measured: replacing 6 curly quotes with
straight ones, and 3 non-breaking spaces with ordinary ones, produced **zero**
new flags in both cases (`T1 minor 13`, exit 0).

**F12 — Generator and verifier share both the oracle and the normalizer.**
`run.py:26` imports `oracle`; `invariants.py:9` and `calibrate.py:24` import the
same module and read the same cache (`run.py:395`, `calibrate.py:108`,
`calibrate.py:153` all call `oracle.extract(..., cache=cardcfg.ORACLE_CACHE)`).
`norm` is imported by `oracle.py:20`, `assemble.py:14`, `serialize.py:9`,
`mdproj.py:19`, `invariants.py:8`. `norm.py:45-51` is explicit that A1 hyphen
joining is "the OUTPUT-side transform **shared by the serializer and the
oracle's body-text projection** so T1 sees both sides identically."

**F13 — Table topology drift reaches canonical Markdown silently.** In the
isolated copy I changed one cached `rowspan="3"` → `rowspan="2"` (opus-5 p.16,
Table 2.2.3.A CB evaluations), regenerated, and diffed: the canonical Markdown
changed as expected — "Non-novel biological weapons" now spans 2 rows instead of
3, so "DNA Synthesis Screening Evasion" silently loses its risk-category
grouping. Gate: `T1 minor 13`, **exit 0**. Seam audit: **0 flags**. The
verification contract already declares this (`TB1 … No TB1 flag is emitted
today`); this measures what that declaration costs end-to-end.

**F18 — A shared-oracle interpretation error produces a correlated false
green.** I re-zoned 12 real body spans on opus-5 p.2 from `body` to `fnbody`
(`fn: 99`) in the oracle cache — the same class of error the footnote-region
walk is documented to have made in the other direction (`oracle.py:109-113`,
D45). Result: the "Cyber evaluations" paragraph is truncated mid-sentence
("…Opus 5's safeguards match&lt;!-- p.3 --&gt; responses tend to be lengthier…"),
the **"Safeguards and harmlessness" paragraph disappears from the body**, and
~60 words are relocated into a `[^99]` definition with **no reference anywhere
in the corpus** (a dangling footnote). Gate: `T1 minor 13`, **exit 0** — byte
for byte the baseline result. Cause: `mdproj.py:158-169` removes footnote-def
text from the token stream and `oracle.page_body_text` (`oracle.py:240-247`)
includes only `zone == "body"`, so both sides excluded the same text on the
strength of the same interpretation.

### Reproducibility and bootstrapping

**F14 — All three documents regenerate byte-identically today.** Copied
`pipeline/` and all three cards to a scratch tree, ran
`run.py --all` for each, `diff -rq` against the committed sections:
**identical for all three**. Determinism and generator/corpus agreement are real.

**F15 — The oracle is fully reproducible from `source.pdf`.** Deleting
`oracle.json` and regenerating opus-5 still produced byte-identical output
(7.4s cold vs 0.7s warm). The extraction layer is not a reproducibility risk.

**F16 — The repair chain self-heals docling *text* drift.** I truncated a cached
docling cell (dropped "synthesizing a virus?"), regenerated, and the output was
**byte-identical to canon** — `_extend_truncated_cells` / `_restore_cell_glyphs`
restored the text from oracle spans. Docling is already, in practice, a
*topology proposer*; the oracle is the text authority. This materially weakens
any argument that the extractor choice is a live fidelity risk for cell text.

**F17 — A missing table cache fails loudly, not silently.** Deleting
`tables.json` and regenerating opus-5 dropped all 24 tables; the gate returned
`T1 major 122`, `ST2 major 8`, **exit 1**. `tables.py:24` does return `{}` for an
absent cache, but the consequence is caught. Absence is loud; *drift* (F13) is
silent. That asymmetry is the actual hazard.

**F19 — CI never regenerates; it gates the committed Markdown.**
`.github/workflows/verify.yml` runs unit tests, `calibrate.py WORKTREE` per card,
`audit_table_seams.py`, and a site build. No job runs `run.py` and asserts a
clean diff. The "regenerate all three and require byte identity" regression net
described in `CLAUDE.md` is a **human procedure, not an enforced one**. Cost of
enforcing it, measured: 0.7s per card warm, 7.4s cold.

**F20 — Generation reads its own prior output.** `run.py:57-64`
(`section_ranges()`) parses `pages (\d+)-(\d+)` out of existing `sections/*.md`;
`run.py:67-79` (`first_headings()`) reads each existing file's first heading to
split shared boundary pages. Prior output is therefore an input. F14 shows the
system is at a stable fixed point; it does not show the fixed point is unique or
reachable from stubs.

**F21 — Configuration is parsed by ad-hoc regex in at least five places, with
silent fallbacks to the first card's constants.** `cardcfg.py:31` and
`cardcfg.py:39` regex `meta.yaml` / `style-manifest.yaml`; `run.py:99-104`
(`manifest_chips()`); `run.py:109-112` (`BUBBLE_CONT`); `assemble.py:15-25`
(`_style_roles`); `calibrate.py:53-59` re-parses the chip block again. No schema,
no validation. `assemble.py:38` and `assemble.py:54` fall back to
`"#666666"` / `"#d9ead3"` — fable-5's hexes — when a manifest omits the role,
which is a silent pass-through in exactly the situation D16's closure rule says
must be a flag. `assemble.py:38/54` also use `next(iter(set))`, so a manifest
mapping two hexes to one singular role would resolve nondeterministically; no
current card does, so this is latent, not live.

**F26 — `BODY_SIZE = 11.0` is duplicated as a bare constant in two modules**
(`oracle.py:23`, commented "this card's body font size"; `assemble.py:37`) and is
a producer-family assumption applied to all three documents.

**F27 — The oracle cache has no invalidation key.** `oracle.py:280-281` returns
the cached JSON if the file exists, regardless of PDF hash or oracle code
version. Both generator and verifier read it (F12), so a stale cache is stale on
both sides simultaneously.

### Facts that defend the current design

I went looking for these deliberately; they constrain what I am willing to
recommend.

**F22 — There are no executable card-slug branches.** Grepping the whole
pipeline for `fable|opus|risk-report` outside comments returns only docstrings
and `cardcfg.py:24`'s default value. The brief's claim is correct.

**F23 — The per-card manifest layer is real and load-bearing, not decorative.**
Comparing the three manifests' `{hex → role}` maps: 35 / 28 / 18 entries, only 8
identical across all three, and **5 hexes carry genuinely different roles in
different cards** — e.g. `#faf9f5` is `turn-user` (fable), `turn-assistant`
(opus), `transcript-container` (risk report); `#141413` is `figure-furniture`
(fable) but `table-header-fill` (opus, risk report). D39's "same hex, different
card, different role" is empirically exercised, not aspirational.

**F24 — D47 is a measured instance of the failure mode, and nothing mechanical
caught it.** A styling rule generalized from 3 motivating cells de-bolded 4 of
205 in-table footnote references; `decisions.md` D47 records that the gates
"count refs and tokens, not their weight" and that a human regression sweep
found it. Every affected instance was inside a table.

**F25 — Experiment 11: ~40 distinct majors in 9 classes surfaced *after* the
gate reached zero.** `docs/experiments/11-risk-report-sweep-round1/README.md`
records 66 overlapping major findings, ~40 distinct. By my classification of its
own table, **5 of the 9 classes are table-internal** (table repair cascade;
label-cell split/scramble; bold cell leads dropped; all-`th` data rows; in-cell
lists flattened), one is link resolution, three are prose/layout. Experiment 10
(opus-5) reports 15 majors in 8 classes on the same pattern.

**F28 — The gate is genuinely fail-closed and acceptances are genuinely exact.**
`acceptance.py` fingerprints the complete finding (SHA-256 of canonical JSON);
`calibrate.py` exits 1 on unsuppressed majors and 2 on stale/malformed
acceptance config. D49's hardening is real, and I could not find a way around it
short of the scope manipulations above.

---

## 3. Architectural inferences

**I1 — The system's risk profile is inverted: verification authority is lowest
exactly where complexity, change rate, and measured defect density are highest.**
(F1, F5, F6, F13, F24, F25.) This, not code size, is why `tables.py` matters. A
2,557-line module that were fully gated would be a maintenance problem; one that
is 27 unconfluent string passes with no topology invariant is a *correctness*
problem.

**I2 — The single representation choice that is genuinely load-bearing is
`export_to_html()`.** (F2, F3, F13.) Once the table is an HTML string, there is
no object whose shape an invariant could compare against source geometry — which
is precisely why TB1 was specified and never written. Note the direction of the
argument: I am not claiming the string is lossy for *text* (F16 refutes that);
I am claiming it is lossy for *topology assertions*.

**I3 — Verifier independence is real at the projection layer and absent at the
interpretation layer.** (F12, F18.) `mdproj.py` is an honest independent
re-derivation of facts from Markdown, and that has caught real bugs. But both
sides consume the same `oracle.py` and the same `norm.py`, and `oracle.py`
contains interpretation (body-font constant, footnote region walk, orphan rule).
Anything the oracle mis-decides is agreed on by both sides. F18 makes this
concrete rather than theoretical: a paragraph can vanish from the body of a
published safety report with a green gate.

**I4 — Some of the verifier's weakness is policy, not architecture, and costs
nothing to fix.** (F7, F10, F11.) Deriving gate scope from the output,
thresholding severity on token count, and running production comparisons in
calibration mode are three independent decisions, each reversible in a small
patch, each currently removing real authority. None of them require a document
model. I would be suspicious of any proposal that bundles them into an
architecture change, because that makes cheap fixes hostage to an expensive one.

**I5 — Docling has already been demoted in practice to a topology proposer.**
(F2: 18 of 27 passes consult the oracle; F16: text drift self-heals.) This
reframes the extractor question. The live risk is not "is docling's text good
enough" but "docling's *structure* decisions are unpinned, untracked, unreviewed
and ungated" (F4, F13). Committing the cache and gating topology addresses the
real exposure without reopening the extractor choice at all.

**I6 — The corpus proves within-family reuse of the *machinery*, and the
manifest layer is doing genuine work, but the rule pile is where growth is
actually happening.** (F22, F23 vs F1, F25.) D16 stratified the design into
universal invariants, a universal typed schema, and per-card data, and warned
that "what compounds across cards is machinery … never a global rule pile."
Stratum 3 shipped and works (F23). Stratum 2 did not ship (D50). What absorbed
stratum 2's job is the ordered rule stack in `tables.py`/`assemble.py`. The
project is currently violating its own D16 in the exact place D16 warned about.

**I7 — Reproducibility is strong at the layer that is tracked and absent at the
layer that is not.** (F4, F14, F15, F17.) A clean clone can rebuild the oracle
bit-exactly and cannot rebuild the tables at all without an unpinned dependency
and an untracked artifact. The 69 tables are the least reproducible and least
verified part of the corpus, and they are also the part most likely to contain
the numbers a reader cites.

**I8 — CI enforces the committed artifact against the PDF but never enforces the
generator against the artifact.** (F19, F20.) Combined with F14 the current state
is healthy; the *mechanism* that keeps it healthy is maintainer discipline. A
regenerate-and-diff job would convert a process rule into an invariant for one
line of YAML and ~25 seconds of runtime.

---

## 4. Unknowns

**U1 — Whether the block model survives a different producer.** Nothing in the
current corpus can decide it. The oracle's 11pt body constant (F26), the ZWSP
list-marker signature (`norm.py:78-82`), the bottom-region footnote walk, and
the gray-heading role are all Google-Docs-export regularities. Cheap to probe
(§8, E5); impossible to settle by argument.

**U2 — Whether TB1 can be written against the current HTML string plus oracle
geometry.** This is the pivotal unknown for my recommendation. TB2 was written
against exactly that substrate and calibrated to 0 false flags on 69 tables, so
the answer is plausibly yes — in which case no typed grid is needed. §8 E2 is
designed to settle it.

**U3 — How much of the ~40 experiment-11 defects a topology gate plus severity
reform would actually have caught.** Re-classifiable from the committed sweep
findings; I did not do it in the time available, and I would not defend a
priority ordering that rests on my guess rather than that count.

**U4 — Whether the current T1 minor baselines (44 / 13 / 22) contain real
defects.** They are unread residuals by definition. Reclassifying severity (§8
E3) will surface the answer; until then nobody can claim the corpus is clean at
1-token resolution, only that it is clean at ≥3-token resolution outside tables.

**U5 — Whether generation from stub sections reproduces the corpus.** F20 shows
prior output is an input; F14 shows the current state is a fixed point. Whether a
cold bootstrap converges to the same point is untested and testable (§8 E6).

**U6 — How much semantic work the site does that the verifier cannot see.**
`site/src/lib/cards.js` relocates page markers, injects hidden footnote shims and
rewrites table references (`cards.js:50-118`); `site/src/lib/markdown.js`
reconstructs lettered lists that Markdown cannot express (`markdown.js:70-112`),
re-derives heading numbering (`markdown.js:354-383`), and regroups figures
(`markdown.js:200-270`). The verifier stops at `sections/*.md`, so none of it is
gated. I have read this code but have not measured its defect contribution, and I
decline to rank it without that measurement.

---

## 5. Essential versus accidental complexity, ranked

**Essential — inherent to converting these PDFs; no architecture removes it.**

1. Table topology recovery. Ruled and unruled grids, merged cells, and multi-row
   label groups must be inferred from geometry. Irreducible.
2. Reading order and cross-page continuation. Paragraph/list/table/turn
   continuation across a page cut is genuinely ambiguous (`run.py:257-265` is
   honest about why the lowercase heuristic failed on nine real seams).
3. Style→semantics mapping. Colour and geometry mean different things in
   different documents; F23 shows this is real. The manifest is the right shape
   for it.
4. Footnote region identification. Structural, not absolute-height — the D45
   region walk is a genuine improvement over what it replaced.
5. Faithfully reproducing publisher defects (orphan refs, unresolvable
   destinations) rather than repairing them.

**Accidental — created by choices, ranked by measured harm.**

1. **`export_to_html()` as the boundary into the repair layer** (I2). Creates
   both the 27-pass string chain and the impossibility of a topology invariant.
2. **Severity thresholded on token count** (F10). Makes a changed benchmark
   number and a deleted negation non-blocking, in a corpus whose entire value is
   that its numbers are right.
3. **Gate scope derived from the output** (F7, F8). Self-referential; degrades
   silently as table detection improves.
4. **Interpretation living inside the shared oracle** (F12, F18). Converts a
   whole class of extraction errors into correlated false greens.
5. **Production comparison running in calibration mode** (F11). Silently
   un-verifies a fidelity property the contract explicitly claims.
6. **Untracked, unpinned table inputs** (F4, F13, I7). The least reproducible
   and least verified artifacts in the repository are the tables.
7. **Prior output as generation input** (F20) and **ad-hoc regex config parsing
   with card-1 fallbacks** (F21). Bootstrap friction and a closure-rule hole;
   real but currently low-harm.
8. Rule provenance being unmachine-readable — the "why" of a rule lives in
   comments and commit messages (D47's own lesson) rather than in fixtures.

I deliberately do **not** rank "Markdown is canonical" as a top accidental cost
for prose. The evidence does not support it: prose round-trips, the projection is
independent, and the constructs Markdown cannot express are few and recovered at
render time (U6). It *is* a cost for tables, where the canonical form is already
raw HTML (7.4–10.4% of canonical bytes across the three cards) rather than
Markdown at all.

---

## 6. Alternatives matrix

Scored on the brief's criteria. **F** fidelity · **P** provenance · **A**
ambiguity representation · **R** deterministic replay · **V** verifier
independence · **X** cross-producer headroom · **M** migration cost (low is
good) · **C** compounding evidence rather than compounding code.

| # | architecture | F | P | A | R | V | X | M | C |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | keep Markdown canonical, refactor locally behind typed interfaces | = | = | – | = | = | – | low | – |
| A2 | persist a small project-owned whole-document semantic model | + | ++ | + | + | = | + | high | + |
| A3 | adopt `DoclingDocument` as the accepted model | = | + | – | – | – | ? | high | – |
| A4 | Pandoc / HAST AST + sidecar | – | – | – | = | – | = | high | – |
| A5 | separate immutable evidence + accepted-semantics models | + | ++ | ++ | + | + | + | v.high | ++ |
| A6 | full-document extractor as primary authority, facts for checking | – | – | – | – | ++ | ? | high | = |
| A7 | universal core + producer-family grammar plugins | = | = | + | = | = | ++ | med | + |
| **A8** | **verification-first; typed structure only where an invariant cannot otherwise be stated (mine)** | **+** | **+** | **+** | **++** | **++** | **=** | **low** | **++** |

Notes that matter more than the grid:

> **A1 (status quo + local refactor)** is the incumbent and must be beaten, not
> assumed away. Its real strengths: F14/F15 determinism, F22 no slug branches,
> F23 a working manifest layer, F28 a fail-closed gate, and a corpus that is
> itself a regression suite. Its fatal gap is that no amount of tidying
> `tables.py` behind typed interfaces makes TB1 writable if the interface still
> terminates in an HTML string — and TB1 is what F13 shows is missing.

> **A2 (whole-document IR)** buys the most in provenance and ambiguity
> representation, and is the direction D16 stratum 2 originally chose. Against
> it: D50 records that this exact artifact was specified and did not ship, and
> my evidence says the prose path — which is most of the document — does not
> currently fail in ways an IR would fix. It would be paying whole-document
> migration cost to solve a table-shaped problem.

> **A3 (`DoclingDocument`)** inverts F16's lesson. The repair chain exists
> because docling's output needs oracle correction; making docling's model the
> accepted semantics adopts an external schema, an unpinned model artifact
> (F4), and a vocabulary with no home for chips, turns/bubbles, page markers, or
> per-document colour roles. It also couples schema evolution to a third party.

> **A4 (Pandoc / HAST)** is the weakest fit. The corpus's distinguishing
> constructs — chip pills, transcript turns, sidenote footnotes, page-marker
> provenance, per-document colour semantics — have no natural node types, so
> everything lands in a sidecar and the AST buys little. Pandoc would also
> introduce a normalization layer that fights the "reproduce publisher mistakes"
> constraint.

> **A5 (separate evidence and accepted-semantics models)** is, in my judgement,
> the *correct* long-run shape and the right answer to clean-room question 5:
> raw observation, extractor proposal, accepted interpretation, and rendered
> artifact genuinely are four different things, and F18 is a direct consequence
> of collapsing the first three into `oracle.py`. I do not recommend building it
> now, because on current evidence it is a large migration justified mostly by
> a generality claim (U1) the corpus cannot support.

> **A7 (producer-family plugins)** is the right answer to a question nobody can
> yet ask. Building a plugin boundary before seeing a second producer would
> hard-code this family's shape into the seam. E5 comes first.

> **A8 (mine)** treats the gate, not the document model, as the primary
> artifact, and admits typed structure only where a needed invariant is
> unstatable without it. It is the only option whose first two stages are pure
> subtraction of accidental weakness, and the only one that contains an explicit
> test for whether the expensive stage is needed at all.

---

## 7. Preferred architecture and smallest reversible first step

### Target

**Keep Markdown canonical. Keep the oracle. Make verification authority match
measured risk, and introduce typed structure only where an invariant provably
cannot be written without it.** Concretely, four stages, each independently
valuable and each abandonable:

**Stage 1 — pin and track the table inputs.** Commit the per-card `tables.json`
(or a normalized structural form of it), pin docling and its model artifacts, and
add a CI job that regenerates all three cards and asserts a clean `git diff`
(measured cost: ~25s total, F14/F19). This converts the least reproducible
artifact in the repository into a reviewable, diffable one, and converts D25's
regeneration discipline from a process rule into an invariant. Nothing about the
architecture is decided by it.

**Stage 2 — repair verification authority. No architecture change.**
(a) Derive `table_pages` from oracle/docling geometry rather than from the
generated Markdown (F7, F8). (b) Replace the token-count severity rule with a
class-aware one: numerals, units, negations and named entities are major at n=1
(F10). (c) Stop running the production gate in calibration mode, or amend the
contract to say it does (F11) — the current state is a documentation defect
either way. (d) Split `oracle.py` into `facts` (spans, links, drawings,
geometry) and `interpretation` (zones, footnote regions, orphan rule), and make
the *interpretation* an input the verifier can vary — F18's failure is invisible
only because both sides consume one fused object.

**Stage 3 — attempt TB1 on the current substrate.** Write the topology
invariant — per-table row/column counts, span structure, and header rows —
against oracle rule geometry and column-edge intervals, exactly the substrate
TB2 already succeeds on. **This stage is the experiment that decides Stage 4.**

**Stage 4 — only if Stage 3 fails: a typed cell grid inside `tables.py`.**
Rows × cells with spans, per-cell provenance (source spans and bbox), and style,
with the existing 27 passes rewritten as functions over the grid and HTML emitted
at the end. Success criterion is byte-identical output for all 69 tables. This is
contained entirely within one module and does not touch the canonical artifact,
the verifier's projection, or the site.

I explicitly reject bundling Stages 1–2 into Stage 4. They are cheap, they are
independently justified, and holding them hostage to a refactor is how the
current gaps persisted.

### Smallest reversible first step

**Commit the docling table cache and add the regenerate-and-assert-clean-diff CI
job.** One commit, no production code touched, trivially revertible.

Why this one: it is a precondition for measuring anything else (you cannot
evaluate a table refactor whose input floats), it closes the worst
reproducibility hole (I7), it makes F13-class drift appear as a reviewable diff
instead of a silent canon change, and it immediately produces new evidence — the
diff under a docling version bump measures how much the unpinned dependency
actually matters (E4). It commits the project to nothing.

---

## 8. Experiments and kill criteria

**E1 — Reclassify the experiment-10/11 findings against the proposed gates.**
Take the ~40 distinct majors and mark each as: would-be-caught by TB1, by
class-aware severity, by scope-from-source, or by none. *Kill criterion:* if
fewer than half would be caught by Stages 2–3, my priority ordering is wrong and
the effort belongs in the inspection layer instead. This is the cheapest and most
decisive experiment and should run first. (Resolves U3.)

**E2 — Write TB1 against the current HTML + oracle geometry.** Calibrate on the
69 certified tables. *Kill criterion for Stage 4:* if TB1 reaches 0 false flags
with acceptable recall on seeded topology mutations (rowspan/colspan changes,
row/column drops, header retagging), **the typed grid is unnecessary and I
withdraw Stage 4.** *Kill criterion for TB1-on-strings:* if stating the invariant
requires reconstructing a grid from the string anyway, that reconstruction *is*
the grid, and Stage 4 is justified by demonstration rather than by taste.
(Resolves U2.)

**E3 — Severity reclassification dry run.** Apply class-aware severity to the
existing 44/13/22 T1 minors and read every newly-major finding against the PDF.
*Kill criterion:* if the reclassification turns the certified corpus red without
surfacing a single true defect, the rule is too blunt and needs narrowing to
numerals and negations only. (Resolves U4.)

**E4 — Docling version bump against a committed cache.** After Stage 1, bump
docling and diff the regenerated cache. *Kill criterion:* a near-empty diff means
the pinning concern is overstated and F4's severity should be downgraded — I
would say so.

**E5 — Cross-producer extraction probe (no conversion).** Run `oracle.py` over
one non-Anthropic system card and count how many of its interpretive assumptions
hold: 11pt body, ZWSP list markers, bottom-region footnotes, gray headings,
increasing footnote numbering. *Kill criterion for the whole "defer generality"
stance:* if most assumptions break, the interpretation/facts split (Stage 2d)
becomes urgent rather than hygienic, and A7 rises sharply. This is a day of work
and it is the only thing that can decide U1.

**E6 — Cold bootstrap.** Reduce one card's `sections/*.md` to stubs (header +
first heading) and regenerate. *Kill criterion:* if output differs from canon,
F20's coupling is not benign and Stage 1's CI job must bootstrap from stubs, not
from the committed corpus. (Resolves U5.)

**Falsifier for my central claim.** If E1 shows the post-gate defects are
predominantly prose/layout rather than table-internal, and E2 shows TB1 is
straightforward, then my "risk-inversion" diagnosis is mostly wrong: the right
answer would be to invest in the inspection layer and the render-time semantics
(U6), not in tables at all.

---

## 9. The strongest case against my own recommendation

**The system works, and my most dramatic findings are perturbations I injected
rather than defects I found.** I did not demonstrate a single incorrect byte in
the shipped corpus. F13, F18 and F8 are all "if X were wrong, nothing would
notice" — and the project's answer is that something *does* notice: the sweeps
and the owner scroll, which caught D47 and 40 more (F24, F25). A reviewer who
weighs demonstrated defects over demonstrated blind spots should conclude the
layered design is functioning exactly as documented, since the contract *already
declares* every hole I measured (no TB1, S1 skips tables, F1 count-only). On that
reading I have re-derived the contract's own §Calibration status with better
numbers and called it a finding.

**The self-healing result cuts against Stage 4 specifically.** F16 is the most
surprising thing I measured: the repair chain is *more* robust than its structure
suggests, because nearly every pass re-derives from the oracle. If topology is
the only thing docling still owns, then the honest minimal fix is to gate
topology (Stage 3) and pin the input (Stage 1) — and a typed grid is 2,500 lines
of churn against a working, byte-stable module, risking exactly the regression
class the corpus exists to prevent. I have tried to build that objection into my
own plan as E2's kill criterion, but it deserves stating plainly: **Stage 4 may
well be unnecessary, and I would not fight for it before E2.**

**Severity reform could be worse than the disease.** With 44 T1 minors on
fable-5, promoting 1-token classes could convert a green corpus to red for
reasons that are mostly extraction noise, and a gate that cries wolf gets
`--report-only`'d. E3 exists because I think this objection is serious.

**And the deepest one:** the owner's stated goal is a machine that improves as it
converts more PDFs. My recommendation spends its first three stages on
verification of the *existing* three documents and defers every generality
question to E5. If the binding constraint is really cross-producer reuse, then
A5 or A7 — which I ranked below my own option — are the ones that compound, and I
have optimized for auditability of a corpus that is already published.

---

## 10. Confidence, and what would change my mind

| conclusion | confidence | what would change it |
| --- | --- | --- |
| F1–F28 as stated | **very high** | any failed re-run; all commands are given |
| Gate authority is misallocated relative to risk (I1) | **high** | E1 showing post-gate defects are mostly non-table |
| Verifier is independent at projection, not at interpretation (I3) | **high** | showing a path by which an oracle zoning error surfaces; F18 would have to be wrong |
| Cheap policy fixes recover most missing authority (I4) | **high** | E3 showing severity reform is unusably noisy |
| A whole-document IR is **not** justified now (vs A2/A5) | **medium** | U6 measured large, or E5 showing the block model is family-specific — either would move me toward A5 |
| A typed cell grid (Stage 4) is needed | **low–medium** | E2 succeeding on strings; I would withdraw it |
| Deferring producer-generality work is correct (vs A7) | **medium** | E5 breaking most oracle assumptions |
| Markdown-canonical should be retained for prose | **high** | evidence that render-time recovery (U6) is a defect source, not just an inelegance |

I hold I1–I4 firmly and expect to defend them. I hold Stage 4 loosely and have
written its kill criterion before being argued into it. If A's proposal is a
whole-document IR, the burden I will press is D50's: name the *measured* failures
it removes that Stages 1–3 do not, and state how it is abandoned safely. If A's
proposal is narrower than mine, I will concede whatever it does better.

---

## Appendix: reproducing the experiments

All run from the repository root. Generation experiments were run against a copy
of `pipeline/` + `cards/` in a scratch directory; the gate accepts an absolute
sections directory, so gate-only experiments need no copy.

```sh
# baseline
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE

# F6/F8/F10/F11: copy sections to a temp dir, apply the described one-line edit, then
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/verifier/calibrate.py /abs/path/to/mutated-sections

# F5: table spill-set coverage
#   union sec.table_pages over mdproj.project(...), expand by +/-1, intersect cardcfg.EXPECTED_PAGES

# F9: blocking vs detection recall — rerun mutate.py's seeded samples, scoring
#   len(unsuppressed majors) > baseline instead of mutate.py's `hit = bool(new)`

# F13/F16/F18: perturb pipeline/.cache/<card>/{tables,oracle}.json in a COPY of the
#   tree, then run.py --all and diff against the committed sections
env CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/generate/run.py --all

# F14/F15: rm the oracle/table caches in the copy, regenerate, diff -rq
```
