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
    def key(s: str) -> str:
        # space-free token-normalized form: immune to PDF span-join artifacts
        # ("isoverall"), glued bullets, and md bold-run segmentation
        return "".join(norm.tokens(s, True))

    md_by_page: dict[int, list[str]] = {}
    for text, pg in md_emphasis:
        md_by_page.setdefault(pg, []).append(key(text))

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

        # md bolds joined in document order: a glued oracle run spanning two
        # adjacent md bolds still matches as a substring
        hay = key(" ".join(t for p in (pno - 1, pno, pno + 1) for t in md_by_page.get(p, [])))
        for run in runs:
            t = key(run["text"].strip(".,;: "))
            if len(t) < 6:
                continue
            if t not in hay:
                flags.append(_flag("S1", pno, "major",
                                   {"kind": "bold-run-missing", "text": run["text"][:80]}))
    return flags


def s2_chips(md_chips, oracle_pages, page_range, chip_colors, registry) -> list[dict]:
    """Chip coverage (S2): every pill whose fill is a manifest chip color has a
    matching :chip[label] nearby. S3: every markdown chip label ∈ registry."""
    md_by_page: dict[int, list[str]] = {}
    for label, pg in md_chips:
        md_by_page.setdefault(pg, []).append(norm.normalize(label, True))

    flags = []
    for pno in page_range:
        if pno > len(oracle_pages):
            continue
        for pill in oracle_pages[pno - 1].get("pills", []):
            if pill["color"] not in chip_colors:
                continue
            want = norm.normalize(pill["text"], True).strip()
            hay = " | ".join(t for p in (pno - 1, pno, pno + 1) for t in md_by_page.get(p, []))
            if want not in hay:
                flags.append(_flag("S2", pno, "major",
                                   {"kind": "chip-missing", "text": want[:60],
                                    "color": pill["color"],
                                    "registry_label": chip_colors[pill["color"]]}))
    for label, pg in md_chips:
        if label not in registry:
            flags.append(_flag("S3", pg, "major", {"kind": "label-not-in-registry", "label": label[:60]}))
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
    return flags
