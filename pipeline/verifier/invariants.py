"""Gate invariants (verification contract IDs). Each check returns a list of
flag dicts: {invariant, page, severity, detail}. Severity: 'major' (≥3 tokens or
a whole link/figure), 'minor' (1–2 tokens, punctuation-scale)."""

import difflib
import re

import norm
import oracle


def _flag(inv, page, severity, detail):
    return {"invariant": inv, "page": page, "severity": severity, "detail": detail}


def t1_text(md_tokens, oracle_pages, page_range, toc_pages, table_pages=frozenset()) -> list[dict]:
    """Bidirectional, order-sensitive token-stream equality (T1/T2), run over
    the whole document at once (sections share boundary pages). Ops on pages
    containing tables are tagged 'table-zone' and demoted to minor: cell
    *presence* is still caught here, but traversal order belongs to TB1."""
    md_toks = [t for t, _ in md_tokens]
    md_pages = [p for _, p in md_tokens]

    o_toks, o_pages = [], []
    for pno in page_range:
        if pno in toc_pages or pno > len(oracle_pages):
            continue
        text = oracle.page_body_text(oracle_pages[pno - 1])
        for tok in norm.tokens(text, calibration=True):
            o_toks.append(tok)
            o_pages.append(pno)

    flags = []
    sm = difflib.SequenceMatcher(a=o_toks, b=md_toks, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        page = o_pages[i1] if i1 < len(o_pages) else (o_pages[-1] if o_pages else 0)
        missing = " ".join(o_toks[i1:i2])
        extra = " ".join(md_toks[j1:j2])
        n = max(i2 - i1, j2 - j1)
        sev = "major" if n >= 3 else "minor"
        detail = {"op": op, "missing_from_md": missing[:160], "extra_in_md": extra[:160], "n_tokens": n}
        if page in table_pages:
            detail["zone"] = "table"
            sev = "minor"
        flags.append(_flag("T1", page, sev, detail))
    return flags


def pair_displacements(flags: list[dict]) -> list[dict]:
    """Insert+delete pairs with identical text are order displacements (T2),
    not content loss — merge each pair into one minor flag."""
    inserts, deletes, rest = [], [], []
    for f in flags:
        if f["invariant"] == "T1" and f["detail"]["op"] == "insert":
            inserts.append(f)
        elif f["invariant"] == "T1" and f["detail"]["op"] == "delete":
            deletes.append(f)
        else:
            rest.append(f)
    used = set()
    for ins in inserts:
        text = ins["detail"]["extra_in_md"]
        match = next(
            (i for i, d in enumerate(deletes)
             if i not in used and d["detail"]["missing_from_md"] == text
             and abs(d["page"] - ins["page"]) <= 2),
            None,
        )
        if match is None:
            rest.append(ins)
        else:
            used.add(match)
            rest.append(_flag("T1", ins["page"], "minor",
                              {"op": "displaced", "text": text[:120],
                               "from_page": deletes[match]["page"], "zone": "T2-displacement"}))
    rest.extend(d for i, d in enumerate(deletes) if i not in used)
    return rest


AUTO_LINK = re.compile(r"^https?://[\w.-]+/?$")


def l1_links(md_links, oracle_pages, page_range, toc_pages, table_pages=frozenset()) -> list[dict]:
    """Link-set coverage: every PDF link must exist in the markdown (L1).
    Checked against the global markdown link set (boundary pages span files)."""
    from collections import Counter

    md_link_text = " | ".join(norm.normalize(t, True) for t, _, _ in md_links)
    md_uri_counts = Counter(target.rstrip("/") for _, target, _ in md_links)

    # URI links: count-based, whole-document — a global SET misses dropped
    # duplicate instances (mutation-testing finding), while page windows
    # false-positive on footnote citations whose md def sits pages away.
    oracle_uri_occurrences: dict[str, list[dict]] = {}
    for pno in page_range:
        if pno in toc_pages or pno > len(oracle_pages):
            continue
        for l in oracle_pages[pno - 1]["links"]["uri"]:
            oracle_uri_occurrences.setdefault(l["uri"].rstrip("/"), []).append({**l, "page": pno})

    flags = []
    for uri, occs in oracle_uri_occurrences.items():
        deficit = len(occs) - md_uri_counts.get(uri, 0)
        for l in occs[:max(0, deficit)]:
            # PDF auto-links: scheme-less anchor text auto-promoted to an
            # http:// URL by Google Docs (appendix blocklist tables) — v1
            # renders them as code, not links (spec rule R1).
            anchor = l["anchor"].strip().rstrip("/")
            auto = uri.startswith("http://") and (anchor in uri or not anchor)
            flags.append(_flag("L1", l["page"], "minor" if auto else "major",
                               {"kind": "auto-link" if auto else "uri", "missing": uri, "anchor": l["anchor"][:80]}))

    for pno in page_range:
        if pno in toc_pages or pno > len(oracle_pages):
            continue
        links = oracle_pages[pno - 1]["links"]
        for l in links["goto"]:
            # PDF link rects over/under-shoot; trim edge punctuation/whitespace
            anchor = norm.normalize(l["anchor"], True).strip().strip("'\"().,;:§[] ")
            if len(anchor) < 3:
                continue
            if anchor not in md_link_text:
                if l.get("unresolvable"):
                    # the SOURCE PDF's named destination doesn't resolve — a
                    # source-document defect; md cannot link to nowhere
                    flags.append(_flag("L1", pno, "minor",
                                       {"kind": "source-defect-unresolvable-dest",
                                        "anchor": anchor[:80], "name": l.get("name", "")}))
                else:
                    flags.append(_flag("L1", pno, "major", {"kind": "goto", "anchor": anchor[:80], "dest_page": l["dest_page"]}))
    return flags


def p1_markers(sections, expected_pages) -> list[dict]:
    """Page-marker continuity and uniqueness across all sections (P1)."""
    seen = {}
    flags = []
    for sec in sections:
        for pg in sec.markers:
            if pg in seen:
                flags.append(_flag("P1", pg, "major", {"kind": "duplicate", "also_in": seen[pg], "file": sec.name}))
            seen.setdefault(pg, sec.name)
        seen.setdefault(sec.page_start, sec.name)  # section start counts as marked
    missing = sorted(set(expected_pages) - set(seen))
    for pg in missing:
        flags.append(_flag("P1", pg, "major", {"kind": "missing-marker"}))
    return flags


def f1_figures(sections, figures_map) -> list[dict]:
    """Per-page figure-image count vs the extracted figures map (F1). Figures
    deliberately omitted via v1's `<!-- figure ... skipped: reason -->` comments
    count as declared exclusions (contract operating rule 4)."""
    md_counts = {}
    for sec in sections:
        for pg, n in sec.images.items():
            md_counts[pg] = md_counts.get(pg, 0) + n
        for pg, skips in sec.fig_skips.items():
            md_counts[pg] = md_counts.get(pg, 0) + len(skips)
    flags = []
    expected = {int(p): len(files) for p, files in figures_map.items()}
    expected.pop(1, None)  # cover art: declared exclusion (title rendered by site)
    # ±1-page neighborhood: marker placement vs figure page can legitimately
    # differ by one at page boundaries (figure-led pages)
    pgs = sorted(set(expected) | set(md_counts))
    for pg in pgs:
        e, m = expected.get(pg, 0), md_counts.get(pg, 0)
        if e == m:
            continue
        neighborhood_e = sum(expected.get(p, 0) for p in (pg - 1, pg, pg + 1))
        neighborhood_m = sum(md_counts.get(p, 0) for p in (pg - 1, pg, pg + 1))
        if neighborhood_e == neighborhood_m:
            flags.append(_flag("F1", pg, "minor", {"expected": e, "in_md": m, "kind": "off-by-one-page"}))
        else:
            flags.append(_flag("F1", pg, "major", {"expected": e, "in_md": m}))
    return flags


def s1_bold(md_emphasis, oracle_pages, page_range, toc_pages, table_pages=frozenset(),
            body_color="#000000") -> list[dict]:
    """Bold-run coverage (S1): every bold body-text run in the source appears as
    markdown emphasis (or a heading / turn label, which consume bold runs as
    typed conversions). Table pages skipped — cell bolds belong to TB1's layer.
    One direction for v0.5: source→output (the FL-04 'dropped lead' class)."""
    # HYBRID matching: exact squash-substring first (precise); when that fails,
    # SUPPRESS the flag if the run's tokens are fully covered by the emphasis
    # token set (handles run SEGMENTATION differences — '**…a** **b…**' vs one
    # PDF run). A genuinely-unbolded run fails both and flags. Pure token-set
    # matching was tried and rejected: it loses run identity (drop-bold recall
    # collapsed to 1/6 because common words elsewhere covered dropped runs).
    from collections import Counter

    def key(s: str) -> str:
        return "".join(norm.tokens(s, True))

    md_by_page: dict[int, list[str]] = {}
    md_keys_by_page: dict[int, Counter] = {}
    for text, pg in md_emphasis:
        # same trailing-punctuation strip as the oracle-run keys below —
        # asymmetry made 'Category:' (md) miss 'Category' (oracle)
        k = key(text.strip(".,;: "))
        md_by_page.setdefault(pg, []).append(key(text))
        md_keys_by_page.setdefault(pg, Counter())[k] += 1

    flags = []
    for pno in page_range:
        if pno in toc_pages or pno in table_pages or pno > len(oracle_pages):
            continue
        # merge consecutive bold spans on the same line into runs
        runs, cur = [], None
        for s in oracle_pages[pno - 1]["spans"]:
            ok = (s["zone"] == "body" and s["bold"] and s["color"] == body_color
                  and s["size"] < 12.5)
            if ok:
                if cur and cur["line"] == s["line"]:
                    cur["text"] += s["text"]
                else:
                    if cur:
                        runs.append(cur)
                    cur = {"line": s["line"], "text": s["text"]}
            elif cur:
                runs.append(cur)
                cur = None
        if cur:
            runs.append(cur)

        hay = key(" ".join(t for p in (pno - 1, pno, pno + 1) for t in md_by_page.get(p, [])))
        # duplicate-key accounting (mutation finding: dropping one of two
        # identical '**Sonnet 4.6**' bolds was covered by its twin): exact-key
        # runs are counted per page with a windowed-deficit fallback, like S2
        want = Counter()
        exacts = {}
        for run in runs:
            t = key(run["text"].strip(".,;: "))
            if len(t) >= 6:
                want[t] += 1
                exacts.setdefault(t, run)
        have_page = md_keys_by_page.get(pno, Counter())
        have_window = Counter()
        for p in (pno - 1, pno, pno + 1):
            have_window.update(md_keys_by_page.get(p, Counter()))
        for t, n in want.items():
            run = exacts[t]
            if have_page.get(t, 0) >= n or have_window.get(t, 0) >= n:
                continue
            if t in hay and n == 1:
                continue  # glued/segmented but present once
            # NOTE: a token-coverage suppression was tried here and removed —
            # it ate real drops (recall collapsed: common words elsewhere
            # covered dropped runs). Residual segmentation noise is accepted
            # and triaged by name instead.
            flags.append(_flag("S1", pno, "major",
                               {"kind": "bold-run-missing", "text": run["text"][:80]}))
    return flags


def s2_chips(md_chips, oracle_pages, page_range, chip_colors, registry) -> list[dict]:
    """Chip coverage (S2): every pill whose fill is a manifest chip color has a
    matching :chip[label] nearby. S3: every markdown chip label ∈ registry."""
    from collections import Counter

    md_by_page: dict[int, Counter] = {}
    for label, pg in md_chips:
        md_by_page.setdefault(pg, Counter())[norm.squash(label)] += 1

    flags = []
    for pno in page_range:
        if pno > len(oracle_pages):
            continue
        # count-based per page (mutation gap 4): a same-label chip on an
        # adjacent page must not satisfy this page's pill
        want_counts = Counter()
        for pill in oracle_pages[pno - 1].get("pills", []):
            if pill["color"] in chip_colors:
                want_counts[norm.squash(pill["text"])] += 1
        if not want_counts:
            continue
        # strict same-page counts: ±1 windows sum so much on chip-dense pages
        # that single drops are masked (mutation finding). Marker slop is
        # tolerated via max() against the window AVERAGE only when strict
        # fails — i.e. flag iff strict fails AND the window also shows deficit.
        have = md_by_page.get(pno, Counter())
        window = Counter()
        for p in (pno - 1, pno, pno + 1):
            window.update(md_by_page.get(p, Counter()))
        for label, n in want_counts.items():
            if have.get(label, 0) < n and window.get(label, 0) < sum(
                c.get(label, 0)
                for c in (
                    Counter(
                        norm.squash(pill["text"])
                        for pill in oracle_pages[p - 1].get("pills", [])
                        if pill["color"] in chip_colors
                    )
                    for p in (pno - 1, pno, pno + 1)
                    if 0 < p <= len(oracle_pages)
                )
            ):
                flags.append(_flag("S2", pno, "major",
                                   {"kind": "chip-missing", "text": label[:60],
                                    "have": have.get(label, 0), "want": n}))
    for label, pg in md_chips:
        if label not in registry:
            flags.append(_flag("S3", pg, "major", {"kind": "label-not-in-registry", "label": label[:60]}))
    return flags


def _olines(page):
    """Oracle body lines: (text, x0, y0, y1, size, colors) in reading order."""
    by_line = {}
    for s in page["spans"]:
        if s["zone"] == "body":
            by_line.setdefault(s["line"], []).append(s)
    out = []
    for _, spans in sorted(by_line.items()):
        spans.sort(key=lambda s: s["bbox"][0])
        out.append({
            "text": "".join(s["text"] for s in spans),
            "x0": spans[0]["bbox"][0],
            "y0": min(s["bbox"][1] for s in spans),
            "y1": max(s["bbox"][3] for s in spans),
            "size": max(s["size"] for s in spans),
            "colors": {s["color"] for s in spans},
            "bold": all(s["bold"] for s in spans),
        })
    return out


HEAD_NUM_ST = re.compile(r"^(\d+(?:\.\d+)*)\s+\S")


def st_structure(sections, oracle_pages, page_range, toc_pages, table_pages=frozenset()) -> list[dict]:
    """ST structural invariant: token-preserving structural damage (the
    wrapped-bullet class) is invisible to T1 — check layout-derived structure.
    ST1: list-marker lines (ZWSP signature) ↔ markdown list items, count per page.
    ST2: no markdown block starts with a hanging-indent continuation line's text.
    ST3: each heading line-group renders as ONE markdown heading (split/missing)."""
    md_items_by_page, md_blocks_by_page, md_heads_by_page = {}, {}, {}
    for sec in sections:
        for t, pg in sec.items:
            md_items_by_page.setdefault(pg, []).append(norm.squash(t))
        for t, pg in sec.block_starts:
            md_blocks_by_page.setdefault(pg, []).append(norm.squash(t))
        for t, pg in sec.headings:
            md_heads_by_page.setdefault(pg, []).append(norm.squash(t))

    flags = []
    for pno in page_range:
        if pno in toc_pages or pno in table_pages or pno > len(oracle_pages):
            continue
        lines = _olines(oracle_pages[pno - 1])

        # --- ST1: item counts (strict page, window fallback à la S2)
        o_marks = [l for l in lines if norm.LIST_MARKER.match(l["text"].lstrip())]
        n_md = len(md_items_by_page.get(pno, []))
        if len(o_marks) and n_md < len(o_marks):
            window_md = sum(len(md_items_by_page.get(p, [])) for p in (pno - 1, pno, pno + 1))
            window_o = 0
            for p in (pno - 1, pno, pno + 1):
                if 0 < p <= len(oracle_pages) and p not in toc_pages:
                    window_o += sum(1 for l in _olines(oracle_pages[p - 1])
                                    if norm.LIST_MARKER.match(l["text"].lstrip()))
            if window_md < window_o:
                flags.append(_flag("ST1", pno, "major",
                                   {"kind": "items-missing", "oracle": len(o_marks), "md": n_md,
                                    "sample": o_marks[0]["text"][:60]}))

        # --- ST2: every md block must start where an oracle LINE starts.
        # A block whose first chars appear only mid-line in the source is a
        # split (wrapped item/paragraph broken at an arbitrary point).
        # Matching is mutual-prefix with FULL line squashes: a complete short
        # line ('Results', a chip row) is a legitimate block start even though
        # it is shorter than the key (truncated line-starts false-flagged).
        line_starts_full = [norm.squash(l["text"]) for l in lines]
        page_blob = norm.squash(" ".join(l["text"] for l in lines))
        for b in md_blocks_by_page.get(pno, []):
            key = b[:24]
            if len(key) < 14:
                continue
            if any(ls and (ls.startswith(key) or (len(ls) >= 6 and key.startswith(ls)))
                   for ls in line_starts_full):
                continue
            if key in page_blob:  # present, but only mid-line → split
                flags.append(_flag("ST2", pno, "major",
                                   {"kind": "block-starts-mid-line", "text": b[:60]}))

        # --- ST3: heading groups render as one heading
        groups, cur = [], None
        for l in lines:
            m_h = HEAD_NUM_ST.match(l["text"])
            is_head = (l["size"] >= 12.6
                       or (l["colors"] == {"#666666"} and m_h)
                       # deep headings (h5/h6): bold body-size lines led by a
                       # >=3-component section number — assemble's rule
                       or bool(m_h and m_h.group(1).count(".") >= 2 and l["bold"]))
            # wrapped continuation: an unnumbered line hugging the heading
            # above it (title-wrap pitch < 6pt; body sits >= 8pt below) with
            # the SAME style profile is the heading's second line
            if (not is_head and cur
                    and (l["y0"] - cur["y1"]) < 6
                    and abs(l["size"] - cur["size"]) < 0.6
                    and l["colors"] == cur["colors"] and l["bold"] == cur["bold"]
                    and (l["colors"] == {"#666666"} or cur["bold"])):
                is_head = True
            if is_head:
                if cur and (l["y0"] - cur["y1"]) < 10 and abs(l["size"] - cur["size"]) < 0.6:
                    cur["text"] += " " + l["text"]
                    cur["y1"] = l["y1"]
                else:
                    if cur:
                        groups.append(cur)
                    cur = dict(l)
            else:
                if cur:
                    groups.append(cur)
                cur = None
        if cur:
            groups.append(cur)
        heads = [h for p in (pno - 1, pno, pno + 1) for h in md_heads_by_page.get(p, [])]
        for g in groups:
            gsq = norm.squash(g["text"])
            if len(gsq) < 4:
                continue
            # exact match only: prefix tolerance let split headings pass
            # (mutation testing, split-heading 0/6)
            if gsq not in heads:
                flags.append(_flag("ST3", pno, "major",
                                   {"kind": "heading-split-or-missing", "text": g["text"][:70]}))
    return flags


def fn1_footnotes(sections, oracle_pages, page_range, toc_pages) -> list[dict]:
    """Footnote refs and bodies present (FN1), global — sections share boundary
    pages, so per-section ranges double-count. Count-level for v0."""
    flags = []
    o_refs = []
    for pno in page_range:
        if pno in toc_pages or pno > len(oracle_pages):
            continue
        for s in oracle_pages[pno - 1]["spans"]:
            if s["zone"] == "fnref":
                o_refs.append((s["text"].strip(), pno))
    md_refs = sum(len(sec.fn_refs) for sec in sections)
    if len(o_refs) != md_refs:
        flags.append(_flag("FN1", 0, "major",
                           {"oracle_refs": len(o_refs), "md_refs": md_refs,
                            "oracle_ref_details": o_refs[:10]}))
    for sec in sections:
        defs = sec.fn_defs
        for n, pg in sec.fn_refs:
            if n not in defs:
                flags.append(_flag("FN1", pg, "major", {"kind": "ref-without-def", "n": n, "section": sec.name}))

    # body-text equality per footnote number (mutation-testing gap 2):
    # footnote bodies are excluded from T1's main stream, so edits inside them
    # are invisible without this check
    oracle_fns: dict[int, str] = {}
    fn_page: dict[int, int] = {}
    for pno in page_range:
        if pno in toc_pages or pno > len(oracle_pages):
            continue
        items = list((oracle_pages[pno - 1].get("footnotes") or {}).items())
        # "cont" = cross-page tail of the previous page's last footnote;
        # numbers ascend through the document, so that's the current max
        for n, t in sorted(items, key=lambda kv: str(kv[0]) != "cont"):
            if str(n) == "cont":
                if oracle_fns:
                    oracle_fns[max(oracle_fns)] += " " + t
                continue
            n = int(n)
            oracle_fns[n] = oracle_fns.get(n, "") + " " + t
            fn_page.setdefault(n, pno)
    md_defs: dict[int, str] = {}
    collisions = set()
    for sec in sections:
        for n, t in sec.fn_defs.items():
            collisions.add(n) if n in md_defs else md_defs.setdefault(n, t)
    for n, t in oracle_fns.items():
        if n in collisions:
            continue
        if n not in md_defs:
            flags.append(_flag("FN1", fn_page[n], "major", {"kind": "body-without-def", "n": n}))
        elif norm.squash(md_defs[n]) != norm.squash(t):
            # ADVISORY (minor) until the oracle's footnote-boundary detection
            # is hardened: stacked footnotes can glue (n=16/17 on p.114 — md
            # verified correct there). Promote to major once boundaries hold.
            flags.append(_flag("FN1", fn_page[n], "minor",
                               {"kind": "body-text-mismatch", "n": n,
                                "oracle": t.strip()[:80], "md": md_defs[n][:80]}))
    return flags
