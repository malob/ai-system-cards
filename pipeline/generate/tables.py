"""Docling table extraction with a persistent per-page cache (D14: docling is
the table-structure authority). Converts docling bottom-left bboxes to PyMuPDF
top-left, emits clean HTML for the v1 renderer + verifier.

    uv run --with docling --with pymupdf python pipeline/generate/tables.py 20 252 253
    (no args = all pages with v1 tables)
"""

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cardcfg  # noqa: E402

REPO = cardcfg.REPO
CARD = cardcfg.CARD
CACHE = cardcfg.TABLES_CACHE


def _load() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def get_tables(page_no: int, oracle_page: dict | None = None) -> list[dict]:
    """[{bbox:[x0,y0,x1,y1] top-left, html}] for a page (cached). Empty if
    uncached. Post-processing on load:
    - strip docling-absorbed <caption> (D23: captions are our block, never in
      the table box — also they duplicated);
    - repair column rotation against oracle span geometry (docling TableFormer
      cyclically mis-assigns columns on wide numeric tables, e.g. 4.4.2.A)."""
    out = []
    for t in _load().get(str(page_no), []):
        t = {**t, "html": _demote_data_th(t["html"])}
        t = {**t, "html": _promote_split_rowspan(t["html"])}
        t = {**t, "html": _normalize_rowspan_subrows(t["html"])}
        t = {**t, "html": _dedup_cascaded_cells(t["html"])}
        html = re.sub(r"<caption>.*?</caption>", "", t["html"], flags=re.S)
        if oracle_page is not None:
            # split BEFORE rotation repair: a glued cell defeats x-matching,
            # leaving its row rotated; once split, the row becomes repairable
            html = _merge_fragment_rows(html, t["bbox"], oracle_page)
            html = _split_glued_cells(html, t["bbox"], oracle_page)
            html = _resplit_misjoined_cells(html, t["bbox"], oracle_page)
            html = _extend_truncated_cells(html, t["bbox"], oracle_page)
            # extension can cascade next-row content into a cell in dense
            # rule-less tables — the endswith-dedup undoes exactly that
            html = _dedup_cascaded_cells(html)
            html = _fix_wrapped_header_cells(html, t["bbox"], oracle_page)
            html = _repair_rotation(html, t["bbox"], oracle_page)
            # AFTER rotation: the pp.78/80 label-cell split (an extra cell
            # per row) is produced by the earlier repairs, not raw docling
            html = _merge_overflow_cells(html, t["bbox"], oracle_page)
            html = _restyle_cells(html, t["bbox"], oracle_page)
            html = _restore_cell_glyphs(html, t["bbox"], oracle_page)
            html = _bold_cell_leads(html, t["bbox"], oracle_page)
            html = _bold_label_cells(html, t["bbox"], oracle_page)
            html = _split_cell_paragraphs(html, t["bbox"], oracle_page)
            html = _inject_fnrefs(html, t["bbox"], oracle_page)
            html = _inject_links(html, t["bbox"], oracle_page)
            html = _normalize_rowspan_subrows(html)
            html = _cell_blank_lines(html, t["bbox"], oracle_page)
            html = _bullet_breaks(html)
            html = _demote_data_th(html)   # rebuilds can re-tag rows all-th
            # AFTER demotion: a white-text header sub-row reads as a mixed row
            # (empty leads + labels) and _demote_data_th would revert it
            html = _promote_white_text_headers(html, t["bbox"], oracle_page)
            html = _demote_black_text_th(html, t["bbox"], oracle_page)
            html = _debold_th(html)
        # hyphen-wrap join in cells the rebuild didn't touch (short label cells
        # like 'Self- knowledge'): keep the hyphen, drop only the wrap space.
        # Both directions, same rules as the shared A1 (norm.join_wrap_hyphens)
        # so the oracle's text stream transforms identically for T1:
        # 'Self- knowledge' and 'national-security -relevant' (p.184) join;
        # suspended compounds ('well-resourced and -staffed') keep the space.
        html = re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1-", html)
        # mirror direction, cells only: docling has no line info, so the
        # preceding token must itself be HYPHENATED for the space to read as
        # a wrap inside one compound ('national-security -relevant', p.184).
        # That test keeps 'sed -i' and 'and -staffed' — plain preceding
        # tokens — exactly as they are.
        html = re.sub(r"(\w+-\w+) (-[a-z])", r"\1\2", html)
        # docling emits punctuation as its own run, so a link anchor is
        # joined to a following ',' / '.' / ')' by a space the PDF never has
        # ('More below .', p.115; 'actors , but', p.12 — six instances,
        # owner-flagged). Only after a LINK close, where the artifact lives.
        html = re.sub(r"(</a>(?:</[a-z]+>)*)\s+([,.;:)])", r"\1\2", html)
        # a footnote superscript is set at REGULAR weight in the PDF even when
        # its label is bold — lift a trailing sup out of the bold run
        # (pp.125/126/128, sweep round 3)
        html = re.sub(r"(<sup>(?:\[\^)?\d+\]?</sup>)</b>", r"</b>\1", html)
        out.append({**t, "html": html})
    return out


def _header_text_hexes() -> set:
    """Hexes the card's manifest marks `table-header-text` (D16). Was
    hardcoded to #ffffff, so this card's CREAM header text (#faf9f5) never
    promoted a demoted header row back to <th> — Tables 1.2.A/B/C read as
    body rows while their twins on pp.13-14 read as headers (sweep round 3,
    3 majors)."""
    try:
        mtext = (cardcfg.CARD / "style-manifest.yaml").read_text()
    except OSError:
        return {"#ffffff"}
    m = re.search(r"^text_colors:\n((?:[ \t]+.*\n)+)", mtext, re.M)
    if not m:
        return {"#ffffff"}
    hexes = {mm.group(1) for mm in re.finditer(
        r'^  "(#[0-9a-f]{6})":\s*\{\s*role:\s*table-header-text', m.group(1), re.M)}
    return hexes or {"#ffffff"}


HEADER_TEXT = _header_text_hexes()


def _header_blobs(hdr_spans: list) -> list:
    """Header-colored text concatenated per COLUMN (x0 clusters, top-down).
    A header cell's text often arrives as several spans, and reading order
    interleaves the columns of a multi-column header row — so containment is
    tested per column, never against one global stream."""
    cols: dict = {}
    for s in hdr_spans:
        k = next((k for k in cols if abs(k - s["bbox"][0]) <= 3), s["bbox"][0])
        cols.setdefault(k, []).append(s)
    blobs = []
    for mem in cols.values():
        mem.sort(key=lambda s: s["bbox"][1])
        blob = "".join(_squash(s["text"]) for s in mem)
        if blob:
            blobs.append(blob)
    return blobs


def _table_spans(oracle_page, bbox):
    for s in oracle_page["spans"]:
        sb = s["bbox"]
        if (bbox[0] - 3 <= sb[0] and sb[2] <= bbox[2] + 3
                and bbox[1] - 3 <= sb[1] and sb[3] <= bbox[3] + 3):
            yield s


def _split_cells(row: str) -> list[str]:
    return re.findall(r"<t[hd][^>]*>.*?</t[hd]>", row, re.S)


def _reading_seq(spans: list) -> list:
    """Table spans in READING order (visual rows top-to-bottom, then x).
    x0-column chains can't reconstruct cells whose lines hold several spans
    ('**Non-novel …production.** AI systems …' continues on the same line at
    a new x0, risk-report p.155; 'See the' + linked 'Claude Opus 5 System
    Card', p.183) — a consecutive run of the reading sequence can."""
    return sorted((s for s in spans),
                  key=lambda s: (round((s["bbox"][1] + s["bbox"][3]) / 8), s["bbox"][0]))


def _column_regions(spans: list) -> list:
    """Per-COLUMN reading sequences: spans bucketed by the column-edge
    intervals (x0 clusters with ≥3 members), reading order inside each
    bucket. A TALL cell whose lines mix x0s (a bold lead ending mid-line,
    a link mid-sentence) is consecutive here but in neither an x0 chain
    (mid-line x0s split it) nor the global reading order (other columns'
    spans interleave row-wise)."""
    cl: dict[float, list] = {}
    for s in spans:
        k = next((k for k in cl if abs(k - s["bbox"][0]) <= 2), s["bbox"][0])
        cl.setdefault(k, []).append(s)

    def _mid_line(mem):
        # an "edge" whose every span directly continues another span on its
        # own line (p.183: three aligned 'Claude ' spans after 'See the ')
        # is an intra-cell wrap position, not a column start — keeping it
        # would sever the cell's span run
        for s in mem:
            sb = s["bbox"]
            # a true wrap position abuts its predecessor within a space
            # width (~6pt); column gutters are wider (p.113's two-column
            # table was swallowed whole by a 40pt window)
            if not any(o is not s
                       and sb[0] - 6 <= o["bbox"][2] <= sb[0] + 2
                       and min(o["bbox"][3], sb[3]) - max(o["bbox"][1], sb[1]) > 2
                       for o in spans):
                return False
        return True

    edges = sorted(k for k, mem in cl.items() if len(mem) >= 3 and not _mid_line(mem))
    if not edges:
        return []
    regions: list[list] = [[] for _ in edges]
    for s in spans:
        i = max((j for j, e in enumerate(edges) if s["bbox"][0] >= e - 2), default=0)
        regions[i].append(s)
    for r in regions:
        r.sort(key=lambda s: (round((s["bbox"][1] + s["bbox"][3]) / 8), s["bbox"][0]))
    return [r for r in regions if r]


def _merge_overflow_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling splits a cell at an inline style boundary (the pp.78/80 label
    cells with embedded links), yielding a row with MORE cells than the
    table's modal width — and sometimes REORDERS the fragments. Merge an
    adjacent overflow pair when the pair's combined char-MULTISET equals a
    consecutive column-chain run's; the cell is rebuilt from the RUN in span
    order, which also undoes the scramble."""
    from collections import Counter
    import html as _h
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if len(rows) < 2:
        return html
    # the table's width authority is the HEADER row's colspan-aware logical
    # width (rowspan-continuation rows are legitimately short and a
    # plain-row modal undercounts — the opus sub-header regression);
    # rowspan/colspan rows have their own arithmetic and are never
    # candidates
    modal = sum(int(m.group(1)) if m else 1
                for m in (re.search(r'colspan="(\d+)"', tag)
                          for tag in re.findall(r"<t[hd][^>]*>", rows[0])))
    plain_rows = [r for r in rows if "rowspan" not in r and "colspan" not in r]
    counts = {id(r): len(re.findall(r"<t[hd]", r)) for r in plain_rows}
    if not any(n > modal for n in counts.values()):
        return html
    spans = [s for s in _table_spans(oracle_page, bbox) if s["text"].strip()]
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 3), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    chains = [sorted(c, key=lambda s: s["bbox"][1]) for c in by_x.values()]
    # split cells with an embedded link mix x0s (p.78) — only the column
    # region / reading order holds their true run
    cols = chains + _column_regions(spans) + [_reading_seq(spans)]

    def _complete(sq):
        # a cell equal to a consecutive x0-CHAIN run is a whole cell of its
        # own; adjacent whole cells are consecutive in reading order too, so
        # without this gate the multiset test is tautological and merges
        # ordinary neighbors (the opus 'Evaluation|Relevance' regression)
        for col in chains:
            for st in range(len(col)):
                acc = ""
                for j in range(st, len(col)):
                    acc += _squash(col[j]["text"])
                    if acc == sq:
                        return True
                    if len(acc) >= len(sq):
                        break
        return False

    spans_xy = _row_spans_xy(oracle_page, bbox)
    out = html
    for r in plain_rows:
        if counts[id(r)] <= modal:
            continue
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        cells = [c for _, _, c in tags]
        # the row's y-band (anchored by its value cells) pins the true run:
        # multiset coincidences exist ACROSS rows ('MonitorBench Hard
        # (n=60' repeats three times on p.80) and matched a run crossing a
        # row boundary in scrambled order
        band = _row_band([_cell_sq(c) for c in cells], spans_xy)
        changed = False
        while len(cells) > modal:
            merged = False
            for i in range(len(cells) - 1):
                a_sq, b_sq = _cell_sq(cells[i]), _cell_sq(cells[i + 1])
                # BOTH fragments non-empty: docling's empty grid cells are
                # structure (the fable p.251 sub-header's blank leads), never
                # split-cell halves — and at least one must be a FRAGMENT
                # (no complete chain run of its own)
                if not a_sq or not b_sq:
                    continue
                both_complete = _complete(a_sq) and _complete(b_sq)
                pair = Counter(a_sq + b_sq)
                target = sum(pair.values())
                hit = None
                for col in cols:
                    for st in range(len(col)):
                        y0 = (col[st]["bbox"][1] + col[st]["bbox"][3]) / 2
                        if band is not None and not (band[0] - 4 <= y0 <= band[1] + 4):
                            continue   # run must START in this row's band
                        acc: Counter = Counter()
                        run = []
                        for j in range(st, len(col)):
                            acc += Counter(_squash(col[j]["text"]))
                            run.append(col[j])
                            if sum(acc.values()) >= target:
                                break
                        if acc == pair:
                            hit = run
                            break
                    if hit:
                        break
                if hit and both_complete and "".join(
                        _squash(s["text"]) for s in hit) == a_sq + b_sq:
                    # two ADJACENT WHOLE cells are trivially a consecutive
                    # reading-order run in cell order (the opus 'Evaluation|
                    # Relevance' regression) — a real split proves itself by
                    # a run whose ORDER differs (p.78: '…from | Treutlein
                    # 2026 | (conversation)') or by a fragment half
                    hit = None
                if hit:
                    cells[i:i + 2] = [_h.escape(
                        _join_wrapped(s["text"] for s in hit), quote=False)]
                    changed = merged = True
                    break
            if not merged:
                break
        if changed and len(cells) == modal:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>"
                for (tg, a, _), c in zip(tags[:len(cells)], cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _demote_black_text_th(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling tags a continuation chunk's leading DATA row all-<th> (the
    §4.5/§6.6 model rows opening the p.131/p.183 chunks), which renders as a
    header band mid-table. A header in this document family sits on a DARK
    fill (white/cream text) — a continuation chunk carries no header at all,
    so the gate is geometric: an all-th row whose band overlaps no dark box
    and whose text matches no white span is data → td. Runs before
    _debold_th so restyled <b> survives the demotion."""
    def _lum(hexcol: str) -> float:
        r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    dark = [b["bbox"] for b in oracle_page.get("boxes", [])
            if re.fullmatch(r"#[0-9a-f]{6}", b.get("color", ""))
            and _lum(b["color"]) < 0.35]
    whites = _header_blobs([s for s in _table_spans(oracle_page, bbox)
                            if s["text"].strip() and s.get("color") in HEADER_TEXT])
    spans_xy = _row_spans_xy(oracle_page, bbox)
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        if "<td" in r or "<th" not in r:
            continue
        plain = [_cell_sq(c)
                 for c in re.findall(r"<th[^>]*>(.*?)</th>", r, re.S)]
        # a row whose ANY cell text is header-colored is a header row, never
        # demote it. (Per-cell containment: the row's full text spans several
        # columns and can never be inside one column's blob — testing that way
        # demoted every real header row on both certified cards.)
        if not any(plain) or any(p2 and any(p2 in b for b in whites) for p2 in plain):
            continue
        band = _row_band(plain, spans_xy)
        if band is None:
            continue   # can't locate the row — leave it alone
        yc = (band[0] + band[1]) / 2
        if any(bb[1] - 2 <= yc <= bb[3] + 2 for bb in dark):
            continue   # sits on a dark header band
        out = out.replace(r, r.replace("<th", "<td").replace("</th>", "</td>"), 1)
    return out


def _promote_split_rowspan(html: str) -> str:
    """docling inconsistently merges 2-row label groups: in one table it gives
    'Claude Opus 4.8' a th rowspan=2 over its With/Without-thinking sub-rows
    but emits a sibling as a plain th + a SEPARATE empty-lead row (p.96
    5.2.2.2.A — Opus split while Sonnet merged). A col-0 th without rowspan
    immediately followed by a same-width row whose col-0 is empty and whose
    rest is real data is exactly that miss: give the th rowspan=2; the empty
    lead is then dropped by _normalize_rowspan_subrows."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    # consistency-only: act solely when the table ALREADY merges at least one
    # label group with rowspan=2 (docling proved the pattern) — so this never
    # speculatively merges rows in tables that legitimately have empty leads
    # (the welfare mega-table's multi-paragraph continuation fragments)
    if not any('rowspan="2"' in r for r in rows):
        return html
    out = html
    for i, r in enumerate(rows[:-1]):
        cells = _split_cells(r)
        m = re.match(r"<tr><th([^>]*)>(.*?)</th>", r, re.S)
        if not cells or not m or "rowspan" in m.group(1) or not m.group(2).strip():
            continue
        ncells = _split_cells(rows[i + 1])
        if len(ncells) != len(cells):
            continue
        lead = re.match(r"<t[hd][^>]*>(\s*)</t[hd]>", ncells[0])
        rest_nonempty = any(re.sub(r"<[^>]+>", "", c).strip() for c in ncells[1:])
        if lead and rest_nonempty:
            promoted = "<tr><th rowspan=\"2\"" + m.group(1) + ">" + m.group(2) + "</th>" + r[len(m.group(0)):]
            out = out.replace(r, promoted, 1)
    return out


def _normalize_rowspan_subrows(html: str) -> str:
    """A row covered by an earlier row's first-column rowspan must not also
    have a leading EMPTY cell — that renders a phantom column shifting every
    value one right (docling emits some, and the lead-restore pass added
    others under rowspan headers)."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    covered = 0
    out = html
    for r in rows:
        m = re.match(r'<tr><t[hd][^>]*rowspan="(\d+)"', r)
        if covered <= 0 and m:
            covered = int(m.group(1)) - 1
            continue
        if covered > 0:
            covered -= 1
            lead = re.match(r"<tr><(t[hd])([^>]*)>(\s*)</t[hd]>", r)
            if lead and "rowspan" not in lead.group(2):
                out = out.replace(r, "<tr>" + r[len(lead.group(0)):], 1)
                continue
            # a covered row's leading th is a SUB-label, not a row label —
            # demote to td so both 'Without thinking' rows match (p.95)
            th = re.match(r"<tr><th([^>]*)>(.*?)</th>", r, re.S)
            if th and "rowspan" not in th.group(1):
                fixed = "<tr><td" + th.group(1) + ">" + th.group(2) + "</td>" + r[len(th.group(0)):]
                out = out.replace(r, fixed, 1)
    return out


def _demote_data_th(html: str) -> str:
    """Docling sometimes emits a DATA row as all-<th> (p.253 RiemannBench),
    rendering every value bold. A non-first row whose cells are majority
    numeric is data: th -> td."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    out = html
    for r in rows:
        if "<td" in r and "<th" in r:
            # mixed row = data row: demote every th EXCEPT a first-column
            # row label (model names are legitimately bold)
            first = re.match(r"<tr><th([^>]*)>(.*?)</th>", r, re.S)
            if first:
                fixed = first.group(0) + r[len(first.group(0)):] \
                    .replace("<th", "<td").replace("</th>", "</td>")
            else:
                fixed = r.replace("<th", "<td").replace("</th>", "</td>")
            if fixed != r:
                out = out.replace(r, fixed, 1)
            continue
    for r in rows:   # incl. row 0: a merged fragment can OPEN with a data row
        cells = re.findall(r"<th([^>]*)>(.*?)</th>", r, re.S)
        if not cells or "<td" in r:
            continue
        plain = [re.sub(r"<[^>]+>", "", c).strip() for _, c in cells]
        numeric = sum(1 for c in plain if re.match(r"^[\d.,%±()\s/x×*+-]+$", c or "x"))
        if numeric < max(2, len(plain) // 2 + 1):
            continue
        out = out.replace(r, r.replace("<th", "<td").replace("</th>", "</td>"), 1)
    return out


def _debold_th(html: str) -> str:
    """th renders bold via CSS; inner <b> double-bolds (p.82 group labels).
    Strip EVERY b-tag inside the cell — a single non-greedy pair mangled
    multi-run cells ('Claude</b> <b>Mythos 5')."""
    return re.sub(r"(<th[^>]*>)(.*?)(</th>)",
                  lambda m: m.group(1) + re.sub(r"</?b>", "", m.group(2)) + m.group(3),
                  html, flags=re.S)


def _bullet_breaks(html: str) -> str:
    """FINAL normalizer: in any multi-bullet cell, bullets render one per
    line (v1's convention). Idempotent: strips existing breaks around
    bullets, then re-inserts uniformly."""
    def fix(m):
        c = m.group(3)
        for g in ("•", "●"):   # ● is the risk-report family's cell glyph
            if c.count(g) >= 2:
                c = re.sub(rf"(?:<br\s*/?>)?\s*{g}\s*", f"<br>{g} ", c.strip())
                c = re.sub(r"^((?:<[^>]+>)*)<br>", r"\1", c)
                break
        return f"<{m.group(1)}{m.group(2)}>{c}</{m.group(1)}>"
    return re.sub(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", fix, html, flags=re.S)


def _cell_lists(html: str, ctx) -> str:
    """In-cell bulleted lists become REAL lists (owner-approved 2026-08-15).

    The PDF sets these with a hanging indent: the glyph sits at the cell's
    own left edge and the bullet's text — including its follow-on paragraphs
    — is indented one step further. Rendered as literal '●' glyphs joined by
    <br>, that indent is lost and a bullet's sub-paragraphs read as
    cell-level text (p.113 Table 3.10.A, p.155; same shape on both certified
    cards). Each cell segment is located in the source spans through the
    shared alignment, so its x0 is exact: a glyph segment opens an <li>, a
    segment indented past the cell edge continues the current <li>, one back
    at the edge closes the list. Cells that cannot be located are untouched.
    """
    import html as _h
    G = "●•◦▪‣○■□"
    if not any(g in html for g in G) or ctx is None:
        return html

    out, pos = [], 0
    for m in re.finditer(r"(<t[hd][^>]*>)(.*?)(</t[hd]>)", html, re.S):
        out.append(html[pos:m.start()])
        pos = m.end()
        inner = m.group(2)
        if not any(g in inner for g in G):
            out.append(m.group(0))
            continue
        matched = _match_cell_chars(_h.unescape(re.sub(r"<[^>]+>", "", inner)), ctx)
        if matched is None:
            out.append(m.group(0))
            continue
        srcs, _raw = matched
        # a cell rebuilt by _split_cell_paragraphs is wrapped in <p>…</p>;
        # splitting on <br> would leave the closing tag inside the last <li>
        # (an empty trailing paragraph in the DOM)
        wrapped = False
        if inner.startswith("<p>") and inner.endswith("</p>"):
            depth, ok = 0, True
            for mm in re.finditer(r"<p>|</p>", inner):
                depth += 1 if mm.group(0) == "<p>" else -1
                if depth == 0 and mm.end() < len(inner):
                    ok = False
                    break
            if ok:
                inner, wrapped = inner[3:-4], True
        parts = [p for p in re.split(r"<br\s*/?>(?:\s*<br\s*/?>)?", inner) if p.strip()]
        info, ordinal = [], 0
        ok = True
        for p2 in parts:
            plain = _h.unescape(re.sub(r"<[^>]+>", "", p2))
            sq = (_squash(plain).translate(_INVIS_DEL).translate(_BULLET_DEL)
                  .translate(ctx["LOW9"]).translate(_QALL))
            if ordinal >= len(srcs) or not sq:
                ok = False
                break
            sp = srcs[ordinal]
            glyph = plain.strip()[:1] in G
            info.append((p2, sp["bbox"][0], glyph))
            ordinal += len(sq)
        if not ok or not any(g for _, _, g in info):
            out.append(m.group(0))
            continue
        base = min(x0 for _, x0, _ in info)
        items, lead, tail = [], [], []
        for p2, x0, glyph in info:
            body = re.sub(r"^((?:<[^>]+>)*)[" + G + r"\s\u200b]+", r"\1", p2.strip())
            if not re.sub(r"<[^>]+>", "", body).strip():
                continue          # a segment that strips to nothing adds no <p>
            if glyph:
                items.append([body])
            elif items and x0 > base + 6:
                items[-1].append(body)
            elif items:
                tail.append(p2)
            else:
                lead.append(p2)
        if not items:
            out.append(m.group(0))
            continue
        lis = "".join(
            "<li>" + (parts_[0] if len(parts_) == 1
                      else "".join(f"<p>{x}</p>" for x in parts_)) + "</li>"
            for parts_ in items)
        def _blk(segs):
            if not segs:
                return ""
            return ("".join(f"<p>{x}</p>" for x in segs) if wrapped
                    else "<br><br>".join(segs) + "<br><br>")
        rebuilt = _blk(lead) + "<ul>" + lis + "</ul>" + _blk(tail)
        out.append(m.group(1) + rebuilt + m.group(3))
    out.append(html[pos:])
    return "".join(out)


def _dedup_cascaded_cells(html: str) -> str:
    """Docling cascade bug (7.4.1.A/B): each cell also contains every LATER
    row's same-column content (bullet counts 12/9/6/3 for a uniform-3 table).
    Invariant: a polluted cell ENDS WITH the next row's entire cell — so
    truncating to the prefix is provably content-safe. Bullets then join with
    <br> (v1's convention for these cells)."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if len(rows) < 3:
        return html
    grid = [re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S) for r in rows]
    orig_sq = [[_cell_sq(c) for _, _, c in row] for row in grid]
    out = html
    changed = False
    for ri in range(len(grid) - 1):
        for ci in range(min(len(grid[ri]), len(grid[ri + 1]))):
            a, b = orig_sq[ri][ci], orig_sq[ri + 1][ci]
            if not b or len(a) <= len(b) or not a.endswith(b):
                continue
            g, attr, c = grid[ri][ci]
            keep = len(a) - len(b)
            import html as _h
            c_dec = _h.unescape(re.sub(r"<[^>]+>", "", c))
            idx = [j for j, ch in enumerate(c_dec) if not ch.isspace()]
            if keep > len(idx):
                continue
            cut = idx[keep - 1] + 1 if keep else 0
            new_c = _h.escape(c_dec[:cut].rstrip(), quote=False)
            old_cell = f"<{g}{attr}>{c}</{g}>"
            new_cell = f"<{g}{attr}>{new_c}</{g}>"
            if old_cell in out:
                out = out.replace(old_cell, new_cell, 1)
                changed = True
    return out


def _join_wrapped(parts):
    """Join wrapped-cell lines: no space when a version number wraps after
    '.'/'-' ('GPT-5.' + '5' -> 'GPT-5.5')."""
    out = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if out and not (out[-1] in ".-" and part[:1].isdigit()):
            out += " "
        out += part
    return out


def _bold_cell_leads(html: str, bbox: list, oracle_page: dict) -> str:
    """A tall single-paragraph cell that _row_band can't anchor (the
    constitution-edits table 7.4.3, pp.244-245) loses the bold of its leading
    run: a passage name '§ How we think about corrigibility' set bold, then a
    regular-weight quote at uniform line pitch (no ≥9pt gap, so it is one
    paragraph and restyle/_split_cell_paragraphs both skip it). For a PLAIN
    cell (no tags) whose text equals a column-chain run with a LEADING bold
    span run followed by regular spans, wrap just the leading bold text in
    <b>. Cells already styled (<b>) or paragraph-split (<p>) are skipped, so
    the welfare mega-table — bold labels already tagged, summary cells already
    <p> — is untouched."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    # docling cells can carry a stray fnref DIGIT the span side excludes
    # ('Expert red-teaming 57', risk-report pp.125/128): matching tolerates
    # the cell text with one trailing ref-digit occurrence removed
    ref_digits = {s["text"].strip() for s in _table_spans(oracle_page, bbox)
                  if s.get("zone") == "fnref"}
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 3), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    cols = [sorted(c, key=lambda s: s["bbox"][1]) for c in by_x.values()]
    # reading-order + column-region sequences join the candidate pool:
    # cells whose bold lead ends mid-line (p.155) never equal an x0-chain
    # run, and TALL such cells only appear consecutive within their column
    # region
    cols.append(_reading_seq(spans))
    cols.extend(_column_regions(spans))
    out = html
    for m in re.finditer(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", html, re.S):
        c = m.group(3)
        if "<" in c:                 # already tagged (styled / paragraph-split)
            continue
        p2 = _cell_sq(c)
        if len(p2) < 8:
            continue
        variants = {p2} | {p2[: -len(d)] for d in ref_digits
                           if d and p2.endswith(d) and len(p2) > len(d) + 4}
        # ref digits can also sit MID-cell, several of them ('…harm.78That
        # is…team79could…', p.156): offer variants with each occurrence
        # removed, and one with every ref digit removed
        v_all = p2
        for d in sorted(ref_digits, key=len, reverse=True):
            if not d:
                continue
            for mm in re.finditer(rf"(?<![\d]){re.escape(d)}(?![\d])", p2):
                variants.add(p2[:mm.start()] + p2[mm.start() + len(d):])
            v_all = re.sub(rf"(?<![\d]){re.escape(d)}(?![\d])", "", v_all)
        variants.add(v_all)
        for col in cols:
            for st in range(len(col)):
                acc, run = "", []
                for j in range(st, len(col)):
                    acc += _squash(col[j]["text"])
                    run.append(col[j])
                    if acc in variants or len(acc) >= len(p2):
                        break
                if acc not in variants or not run[0].get("bold"):
                    continue
                k = 0
                while k < len(run) and run[k].get("bold"):
                    k += 1
                if k == len(run) and acc == p2:
                    break   # all-bold cell: not a lead transition (canon path)
                # an all-bold cell matched via a DIGIT VARIANT is the
                # bold+fnref class (pp.125/128): restyle's cell matching is
                # defeated by the stray ref digit — wrap the bold text here,
                # leaving the digit for _inject_fnrefs to absorb
                lead_sq = _squash("".join(s["text"] for s in run[:k]))
                # map lead_sq's length to a char cut in the raw cell text
                cnt, i = 0, 0
                while i < len(c) and cnt < len(lead_sq):
                    if not c[i].isspace():
                        cnt += 1
                    i += 1
                while i > 0 and c[i - 1].isspace():
                    i -= 1
                if i and _cell_sq(c[:i]) == lead_sq:
                    fixed = f"<{m.group(1)}{m.group(2)}><b>{c[:i]}</b>{c[i:]}</{m.group(1)}>"
                    out = out.replace(m.group(0), fixed, 1)
                else:
                    # HTML entities desync the raw-char count ('R&amp;D' is
                    # five chars for the three-char span text, p.113): remap
                    # on the DECODED text and re-escape the halves
                    import html as _h
                    cd = _h.unescape(c)
                    cnt, i = 0, 0
                    while i < len(cd) and cnt < len(lead_sq):
                        if not cd[i].isspace():
                            cnt += 1
                        i += 1
                    while i > 0 and cd[i - 1].isspace():
                        i -= 1
                    if i and _squash(cd[:i]).translate(_QUOTE_FOLD) == lead_sq:
                        fixed = (f"<{m.group(1)}{m.group(2)}><b>"
                                 + _h.escape(cd[:i], quote=False) + "</b>"
                                 + _h.escape(cd[i:], quote=False)
                                 + f"</{m.group(1)}>")
                        out = out.replace(m.group(0), fixed, 1)
                break
            else:
                continue
            break
    return out


def _bold_label_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """First-column label cells whose PDF spans are ALL bold get a whole-cell
    <b> when restyle's segmentation missed or fumbled them (the §6.6 dense
    chunks: '<b>Claude</b> <u>Mythos Preview</u>'; unbolded 'Claude Opus
    4.8' / 'Claude Sonnet 5' / 'Legacy models…' labels). Existing b/u tags
    are stripped first (the false <u> came from a cell border rule). A bold
    that restyle LEAKED onto the next cell's duplicate first word ('Legacy'
    opening the description, p.184) is removed when that cell's own span is
    regular-weight."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 3), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    seqs = [sorted(c, key=lambda s: s["bbox"][1]) for c in by_x.values()]
    seqs += _column_regions(spans) + [_reading_seq(spans)]

    def _match_run(sq):
        for col in seqs:
            for st in range(len(col)):
                acc, run = "", []
                for j in range(st, len(col)):
                    acc += _squash(col[j]["text"])
                    run.append(col[j])
                    if len(acc) >= len(sq):
                        break
                if acc == sq:
                    return run
        return None

    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        cells = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        if len(cells) < 2 or cells[0][0] == "th":
            continue
        tg, attr, c = cells[0]
        # only cells whose ONLY markup is b/u: structured labels
        # (<br>, <i>, links, sups) are restyle's territory and already
        # correct in the certified cards
        if re.search(r"<(?!/?[bu]>)", c):
            continue
        inner = re.sub(r"</?[bu]>", "", c)
        plain = _cell_sq(inner)
        if len(plain) < 6 or not re.search(r"[A-Za-z]{3}", plain):
            continue
        run = _match_run(plain)
        if not run or not all(s.get("bold") for s in run):
            continue
        inner_s = inner.strip()
        m_sup = re.search(r"(<sup>.*?</sup>)\s*$", inner_s)
        if m_sup:
            new_c = f"<b>{inner_s[:m_sup.start()].strip()}</b>{m_sup.group(1)}"
        else:
            new_c = f"<b>{inner_s}</b>"
        old_cell = f"<{tg}{attr}>{c}</{tg}>"
        if f"<b>{inner.strip()}</b>" == c:
            new_cell = old_cell   # already exactly bold
        else:
            new_cell = f"<{tg}{attr}>{new_c}</{tg}>"
            if old_cell in out:
                out = out.replace(old_cell, new_cell, 1)
        # leaked duplicate-word bold on the neighbor cell: '<b>Legacy</b>
        # commercial…' where the description's own span is regular
        ntg, nattr, nc = cells[1]
        mword = re.match(r"<b>(\w[\w.-]*)</b>(\s)", nc)
        first_word = inner.strip().split()[0] if inner.strip().split() else ""
        if mword and mword.group(1) == first_word and "<b>" not in nc[mword.end():]:
            fixed_nc = mword.group(1) + mword.group(2) + nc[mword.end():]
            old_n = f"<{ntg}{nattr}>{nc}</{ntg}>"
            if old_n in out:
                out = out.replace(old_n, f"<{ntg}{nattr}>{fixed_nc}</{ntg}>", 1)
    return out


def _split_cell_paragraphs(html: str, bbox: list, oracle_page: dict) -> str:
    """Tall interview-style cells hold MULTIPLE PARAGRAPHS (Q1/Q2/Q3 with
    ~18pt gaps vs 2pt line pitch — exactly where column chains break).
    Docling flattens them; rebuild any long unstyled cell whose text equals a
    consecutive chain run as <p>-separated, span-true paragraphs."""
    import html as _h
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 3), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    cols = []
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        cols.append(col)
    out = html
    for m in re.finditer(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", html, re.S):
        c = m.group(3)
        p2 = _cell_sq(c)
        if len(p2) < 120 or "<" in c:
            continue
        def scan(columns, topk, botk, textk):
            for col in columns:
                for st in range(len(col)):
                    acc, paras = "", [[col[st]]]
                    for j in range(st, len(col)):
                        if j > st:
                            if col[j][topk] - col[j - 1][botk] >= 9:
                                paras.append([])
                            paras[-1].append(col[j])
                        acc += _squash(col[j][textk] if textk else col[j]["text"])
                        if len(acc) >= len(p2):
                            break
                    if acc == p2 and len(paras) > 1:
                        return paras
            return None

        cols_b = [[{"text": s["text"], "top": s["bbox"][1], "bottom": s["bbox"][3]}
                   for s in col] for col in cols]
        best = scan(cols_b, "top", "bottom", "text")
        if not best:
            # FALLBACK: visual line segments — a line can hold several spans
            # ('(interview' + 'only)') whose later spans fall outside the
            # x-cluster; rebuilt lines see the full text. Fallback-only so
            # already-matching cells can't regress.
            segs = []
            for s in sorted(spans, key=lambda s: (round((s["bbox"][1] + s["bbox"][3]) / 8), s["bbox"][0])):
                sb = s["bbox"]
                if (segs and abs((sb[1] + sb[3]) / 2 - segs[-1]["yc"]) < 4
                        and 0 <= sb[0] - segs[-1]["x1"] <= 15):
                    segs[-1]["text"] += s["text"]
                    segs[-1]["x1"] = max(segs[-1]["x1"], sb[2])
                    segs[-1]["bottom"] = max(segs[-1]["bottom"], sb[3])
                else:
                    segs.append({"text": s["text"], "x0": sb[0], "x1": sb[2],
                                 "top": sb[1], "bottom": sb[3],
                                 "yc": (sb[1] + sb[3]) / 2})
            fb: dict[float, list] = {}
            for ln in segs:
                # looser cluster than the primary (an indented wrap line like
                # '(interview' sits a few pt right of its column)
                key = next((k for k in fb if abs(k - ln["x0"]) <= 8), None)
                fb.setdefault(ln["x0"] if key is None else key, []).append(ln)
            fcols = [sorted(v, key=lambda l: l["top"]) for v in fb.values()]
            best = scan(fcols, "top", "bottom", "text")
        if not best:
            continue
        body = "".join(
            "<p>" + _h.escape(_join_wrapped(e["text"] for e in para), quote=False) + "</p>"
            for para in best if para)
        out = out.replace(m.group(0), f"<{m.group(1)}{m.group(2)}>{body}</{m.group(1)}>", 1)
    return out


def _split_inline_questions(html: str) -> str:
    """Last-mile normalizer: a cell that already has Q-numbered paragraphs
    but still carries an inline '…? Q6.' run (one fragment cell resisted
    geometric matching) gets the remaining splits. Scoped: fires only inside
    cells with >=2 existing <p>QN. paragraphs; prose never matches '? QN.'."""
    out = html
    for m in re.finditer(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", html, re.S):
        c = m.group(3)
        if len(re.findall(r"<p>\s*Q\d+\.", c)) < 2:
            continue
        fixed = re.sub(r"([?.!\u201d\u2019)\]])\s+(Q\d+\.\s)", r"\1</p><p>\2", c)
        if fixed != c:
            out = out.replace(m.group(0), f"<{m.group(1)}{m.group(2)}>{fixed}</{m.group(1)}>", 1)
    return out


def _extend_rowspans_over_short_rows(html: str) -> str:
    """A cross-page continuation row one cell SHORT of the table width that
    no first-column rowspan covers belongs to the category above it (the
    p.20-21 CB table: 'Viral sequence-to-function' under 'Novel biological
    weapons' rowspan=2 -> 3). Extend that rowspan instead of letting the row
    shift into the first column."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)

    def logical(row):
        n = 0
        for a in re.findall(r"<t[hd]([^>]*)>", row):
            m = re.search(r'colspan="(\d+)"', a)
            n += int(m.group(1)) if m else 1
        return n

    if not rows:
        return html
    full = max(logical(r) for r in rows)
    covered = 0
    last_span_row = None   # (row_html, span_value)
    out = html
    for r in rows:
        m = re.match(r'<tr><t[hd][^>]*rowspan="(\d+)"', r)
        if m and covered <= 0:
            covered = int(m.group(1)) - 1
            last_span_row = [r, int(m.group(1))]
            continue
        if covered > 0:
            covered -= 1
            continue
        if logical(r) == full - 1 and last_span_row is not None:
            old_r, span = last_span_row
            new_span = span + 1
            new_r = old_r.replace(f'rowspan="{span}"', f'rowspan="{new_span}"', 1)
            cur = out.replace(old_r, new_r, 1)
            if cur != out:
                out = cur
                last_span_row = [new_r, new_span]
            continue
        last_span_row = None
    return out


def merge_continuation_rows(html: str) -> str:
    """After cross-page table stitching: a row whose FIRST cell is empty and
    whose content continues the previous row mid-sentence is the same logical
    row split by the page break — merge cell-wise. The seam paragraph joins
    when the continuation starts lowercase/'('; otherwise it stays its own
    <p>. (v1's hand-built 9-page welfare table is the shape target.)"""
    parts = re.split(r"(<tr>.*?</tr>)", html, flags=re.S)
    out_parts = []
    last_row_idx = None
    rows_merged = 0
    for pi, part in enumerate(parts):
        if not part.startswith("<tr>"):
            out_parts.append(part)   # inter-row content (page markers) kept
            continue
        r = part
        last_row_of_table = not any(p2.startswith("<tr>") for p2 in parts[pi + 1:])
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        prev_tags = (re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", out_parts[last_row_idx], re.S)
                     if last_row_idx is not None else None)
        starts_lower = any(re.match(r"[a-z(\u2018\u2019]", re.sub(r"<[^>]+>", "", c).strip())
                           for _, _, c in tags[1:] if _cell_sq(c))
        # the FIRST cell may itself continue across the page (opus-5 p.140\u2192141
        # welfare table: the row-label quote wraps): treat it as a continuation
        # when prev's first cell ends mid-sentence and cur's starts lowercase
        first_continues = False
        if plain[0] and prev_tags and prev_tags[0][2].strip():
            pt = re.sub(r"<[^>]+>", "", prev_tags[0][2]).strip()
            ct = re.sub(r"<[^>]+>", "", tags[0][2]).strip()
            first_continues = bool(pt and ct
                                   and not re.search(r"[.!?:;\u2026\"\u201d')\]]$", pt)
                                   and re.match(r"[a-z(\u2018\u2019]", ct))
        if (prev_tags and len(tags) == len(prev_tags) and tags
                and (not plain[0] or first_continues)
                and any(plain[1:]) and starts_lower
                and not any("colspan" in a for _, a, _ in tags)):
            # the page marker that rode BETWEEN the fragments must move
            # INSIDE the merged cell at its seam: left between </tr> and
            # </tbody> it gets foster-parented out of the table by the HTML
            # parser and its gutter label renders at the table TOP
            # (Table 3.10.A p.114, owner-spotted)
            seam_marker = ""
            if last_row_of_table:
                # only when leaving it WOULD foster-parent (no row follows);
                # a marker before a surviving <tr> is already tucked into
                # that row's first cell by the renderer (canon placement)
                for j in range(last_row_idx + 1, len(out_parts)):
                    mks = re.findall(r"<!--\s*p\.\d+\s*-->", out_parts[j])
                    if mks:
                        seam_marker += "".join(mks)
                        out_parts[j] = re.sub(r"<!--\s*p\.\d+\s*-->", "", out_parts[j])
            cells = []
            for (pg, pa, pc), (_, _, cc) in zip(prev_tags, tags):
                if not _cell_sq(cc):
                    cells.append((pg, pa, pc))
                    continue
                cur = cc.strip()
                prev_c = pc.rstrip()
                cur_plain = re.sub(r"<[^>]+>", "", cur).strip()
                prev_plain = re.sub(r"<[^>]+>", "", prev_c).strip()
                # flows on a lowercase continuation OR when the previous side
                # ends mid-sentence \u2014 'do not yet meet our | CB-2 threshold'
                # (p.115\u2192116) starts uppercase and still flows
                seam_flows = bool(re.match(r"[a-z(\u2018\u2019]", cur_plain)
                                  or (prev_plain and not re.search(
                                      r"[.!?:;\u2026\"\u201d')\]]$", prev_plain)))
                # normalize BOTH sides to <p>-wrapped form first (a flat side
                # mixed with a block side renders spurious line breaks), then
                # a flowing seam merges prev's last <p> with cur's first
                a2 = prev_c if prev_c.endswith("</p>") else f"<p>{prev_c}</p>"
                b2 = cur if cur.startswith("<p>") else f"<p>{cur}</p>"
                if seam_flows:
                    joined = a2[:-4] + seam_marker + " " + b2[3:]
                else:
                    joined = a2 + seam_marker + b2
                seam_marker = ""   # first joined cell carries the marker
                cells.append((pg, pa, joined))
            out_parts[last_row_idx] = "<tr>" + "".join(
                f"<{g}{a}>{c}</{g}>" for g, a, c in cells) + "</tr>"
            rows_merged += 1
            continue
        out_parts.append(r)
        last_row_idx = len(out_parts) - 1
    merged_html = "".join(out_parts) if rows_merged else html
    return _split_inline_questions(_extend_rowspans_over_short_rows(merged_html))


def _merge_fragment_rows(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling splits one tall logical row into several <tr>s (welfare
    interview tables: a 4-line question becomes a row + fragment rows, often
    with fragments landing in the WRONG columns). A fragment cell's text is a
    mid-chain run of some column chain whose PREFIX is an existing cell of
    the previous row: merge it into that cell and drop the fragment row."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    chains = _column_chains(spans)
    if not chains:
        return html
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    out_rows = []
    for r in rows:
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        frags = [_cell_sq(c) for _, _, c in tags if _cell_sq(c)]
        merged_all = bool(frags) and out_rows and not any(
            "rowspan" in a or "colspan" in a for _, a, _ in tags)
        if merged_all:
            prev = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", out_rows[-1], re.S)
            prev_cells = [c for _, _, c in prev]
            plan = []  # (prev_cell_idx, full_text)
            for f in frags:
                hit = None
                for ch in chains:
                    accs = [""]
                    for s in ch:
                        accs.append(accs[-1] + _squash(s["text"]))
                    for k in range(1, len(ch)):
                        for m in range(k + 1, len(ch) + 1):
                            if accs[m][len(accs[k]):] != f:
                                continue
                            for ci, pc in enumerate(prev_cells):
                                if _cell_sq(pc) == accs[k]:
                                    cand = (ci, _join_wrapped(
                                        x["text"] for x in ch[:m]))
                                    hit = cand if hit is None else hit
                    if hit:
                        break
                if not hit:
                    merged_all = False
                    break
                plan.append(hit)
            if merged_all and len({ci for ci, _ in plan}) == len(plan):
                import html as _h
                for ci, full in plan:
                    prev_cells[ci] = _h.escape(full, quote=False)
                out_rows[-1] = "<tr>" + "".join(
                    f"<{tg}{a}>{c}</{tg}>"
                    for (tg, a, _), c in zip(prev, prev_cells)) + "</tr>"
                continue
        out_rows.append(r)
    if len(out_rows) == len(rows):
        return html
    # reassemble in order, preserving everything outside the rows
    out = html
    for r in rows:
        pass
    body = "".join(out_rows)
    return re.sub(r"(<tbody>).*(</tbody>)", lambda m: m.group(1) + body + m.group(2), html, flags=re.S) \
        if "<tbody>" in html else re.sub(r"(<table[^>]*>).*(</table>)", lambda m: m.group(1) + body + m.group(2), html, flags=re.S)


def _split_glued_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes glues two cells' values into one cell, leaving an
    empty cell in the row ('88.1 97.5' | '' — p.85 Sonnet row). When a glued
    cell's text equals the concatenation of exactly two oracle spans and the
    row has exactly one empty cell, split by span x-order."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s.get("zone") != "fnref"]
    sq = {_squash(s["text"]): s for s in spans}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        empties = [i for i, (_, _, c) in enumerate(tags) if not _cell_sq(c)]
        if len(empties) != 1:
            continue
        for i, (tg, attr, c) in enumerate(tags):
            plain = _cell_sq(c)
            if not plain or i == empties[0]:
                continue
            parts = plain.split()  # squash removed spaces; split won't work —
            # find a 2-span partition instead
            hit = None
            for k1, s1 in sq.items():
                if plain.startswith(k1) and plain[len(k1):] in sq:
                    hit = (s1, sq[plain[len(k1):]])
                    break
            if not hit:
                continue
            a, b2 = sorted(hit, key=lambda s: s["bbox"][0])
            # the two pieces must be SIDE BY SIDE (different columns): two
            # stacked lines are one wrapped cell, not a glue (p.253 Gemini)
            if b2["bbox"][0] < a["bbox"][2] - 2:
                continue
            cells = [c2 for _, _, c2 in tags]
            # place by x-order: glued cell gets the piece nearer its column,
            # empty cell gets the other — empty left of glued => takes the
            # left span
            left_first = empties[0] < i
            cells[i] = b2["text"].strip() if left_first else a["text"].strip()
            cells[empties[0]] = a["text"].strip() if left_first else b2["text"].strip()
            rebuilt = "<tr>" + "".join(
                f"<{tg2}{at2}>{c2}</{tg2}>" for (tg2, at2, _), c2 in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
            break
    return out


def _inject_fnrefs(html: str, bbox: list, oracle_page: dict) -> str:
    """Footnote refs inside tables: docling drops superscripts, so re-attach
    `<sup>[^N]</sup>` after the nearest-left text of each in-table ref span
    (the FN1 major: refs 11/12/28/29 in the safeguards/capabilities tables)."""
    spans = list(_table_spans(oracle_page, bbox))
    out = html
    for ref in spans:
        if ref.get("zone") != "fnref":
            continue
        n = ref["text"].strip()
        rb = ref["bbox"]
        left = [s for s in spans
                if s.get("zone") == "body" and s["bbox"][2] <= rb[0] + 2
                and min(s["bbox"][3], rb[3]) - max(s["bbox"][1], rb[1]) > 0]
        if not left:
            continue
        anchor = max(left, key=lambda s: s["bbox"][2])["text"].strip()
        if not anchor:
            continue
        # an ORPHAN ref (oracle-tagged: no def anywhere in the document) is a
        # source artifact — render the superscript digits, not a dangling [^N]
        sup = f"<sup>{n}</sup>" if ref.get("orphan") else f"<sup>[^{n}]</sup>"
        # absorb a stray literal digit docling captured from the superscript
        # ('GDPval-AA 29' -> 'GDPval-AA<sup>[^29]</sup>')
        pat = re.compile("(" + re.escape(anchor) + r")(\s*" + re.escape(n) + r"\b)?(?![^<]*</sup>)")
        out, k = pat.subn(lambda m: m.group(1) + sup, out, count=1)
    # a stray literal digit can survive BEHIND a closing tag the absorb
    # above can't see ('<b>X<sup>[^3]</sup></b> 3'): drop it
    out = re.sub(r"(<sup>\[?\^?(\d+)\]?</sup>)((?:</\w+>)*)\s*\2\b", r"\1\3", out)
    return out


def _inject_links(html: str, bbox: list, oracle_page: dict) -> str:
    """Hyperlinks inside tables: docling emits cell text only, so links whose
    rects fall inside the table bbox are re-attached by wrapping their anchor
    text in <a> (risk-report L1 class: exec-summary and model-list tables).
    URI links keep their target; goto links carry the DEST placeholder that
    run.py resolves to a heading anchor, same as body links. Anchor matching
    is whitespace/tag-tolerant — clip-text anchors arrive space-mashed
    ('ProjectGlasswing') while docling cells keep the spaces — and stays
    inside ONE cell so a wrap can never straddle a td boundary."""
    import html as _h

    def _sq(s):
        return re.sub(r"[^A-Za-z0-9]", "", s)

    def _row_ctx(rect):
        # squashed text left/right of the rect on its visual row — the
        # disambiguator when the same anchor words appear in several cells
        # (p.12 'relevant threat actors' lives in two rows of Table 1.2.C)
        y0, y1 = rect[1], rect[3]
        row = sorted((s for s in oracle_page["spans"]
                      if min(s["bbox"][3], y1) - max(s["bbox"][1], y0) > 2),
                     key=lambda s: s["bbox"][0])
        pre = "".join(s["text"] for s in row if s["bbox"][2] <= rect[0] + 1)
        post = "".join(s["text"] for s in row if s["bbox"][0] >= rect[2] - 1)
        return _sq(pre), _sq(post)

    links = []
    for l in oracle_page["links"]["uri"] + oracle_page["links"]["goto"]:
        rects = [r for r in (l.get("rects") or [])
                 if min(r[2], bbox[2]) - max(r[0], bbox[0]) > 1
                 and min(r[3], bbox[3]) - max(r[1], bbox[1]) > 1]
        if not rects:
            continue
        chars = [c for c in (l.get("anchor") or "") if not c.isspace()]
        if len(chars) < 3:
            continue
        target = l.get("uri") or "DEST:{}:{}".format(
            l.get("dest_page", 0), int(l.get("dest_y", -1)))
        sep = r"(?:\s|<[^>]+>)*"

        def esc(c):
            # docling cells hold HTML — entity-escape tolerant matching
            # ('Fable 5 &amp; Mythos 5' vs the anchor's literal '&')
            return {"&": "(?:&amp;|&)", "<": "(?:&lt;|<)", ">": "(?:&gt;|>)"}.get(c) or re.escape(c)
        # the oracle merges same-URI annots per page, CONCATENATING their
        # anchors — two identical links in one table (the p.183 'Fable 5 &
        # Mythos 5 System Card' rows) arrive as one doubled string that can
        # never match. A k-fold periodic anchor is k instances of its unit.
        text_all = "".join(chars)
        n_inst = next((k for k in (2, 3, 4)
                       if len(text_all) % k == 0
                       and text_all == text_all[: len(text_all) // k] * k), 1)
        unit = text_all[: len(text_all) // n_inst]
        pre, _ = _row_ctx(rects[0])
        _, post = _row_ctx(rects[-1])
        links.append({"pat": re.compile(sep.join(esc(c) for c in unit)),
                      "target": target, "sq": _sq(unit),
                      "pre": pre[-10:], "post": post[:10], "n": n_inst})
    if not links:
        return html

    cells = list(re.finditer(r"(<t[hd][^>]*>)(.*?)(</t[hd]>)", html, re.S))
    inners = [m.group(2) for m in cells]

    def _cell_sq(i):
        return _sq(_h.unescape(re.sub(r"<[^>]+>", "", inners[i])))

    for lk in links:
        # candidate cells containing the anchor; row context outranks bare
        # containment so the link lands in ITS cell, not a lookalike
        cands = [i for i in range(len(inners)) if lk["sq"] in _cell_sq(i)]
        scored = sorted(
            cands,
            key=lambda i: (0 if ((lk["pre"] and lk["pre"] + lk["sq"] in _cell_sq(i))
                                 or (lk["post"] and lk["sq"] + lk["post"] in _cell_sq(i)))
                           else 1, i))
        remaining = lk["n"]
        for i in scored:
            if remaining == 0:
                break
            for mm in lk["pat"].finditer(inners[i]):
                before = inners[i][:mm.start()]
                if before.count("<a ") > before.count("</a>"):
                    continue   # already inside an anchor
                inners[i] = (before + f'<a href="{lk["target"]}">' + mm.group(0)
                             + "</a>" + inners[i][mm.end():])
                remaining -= 1
                break
    out, pos = [], 0
    for i, m in enumerate(cells):
        out.append(html[pos:m.start()])
        out.append(m.group(1) + inners[i] + m.group(3))
        pos = m.end()
    out.append(html[pos:])
    return "".join(out)


def _restyle_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Recover bold (best-score) and underline (second-best, FL-09) styling
    from oracle facts. Cells are segmented GEOMETRICALLY: each row's y-band
    yields its candidate spans (plus wrapped/sub-line continuations), each
    cell's text is greedily split into those spans, and every segment is
    styled by its own span's flags — a bold '97.88%' inside the cell
    '97.88% (± 0.66%)' gets <b> on just the bold part."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s.get("zone") != "fnref"]
    rules = oracle_page.get("rules", [])
    # bold only signifies when it DEVIATES from the table's dominant weight:
    # some tables (2.2.1.A) are set entirely in Lora-Bold, where the visual
    # weight reads regular and 'bold' carries no information (owner-flagged).
    # white header text excluded from the count (the 4.4.2 regression)
    boldish = [s for s in spans
               if s["text"].strip() and s.get("color") not in ("#ffffff", "#faf9f5")]
    bold_share = sum(1 for s in boldish if s.get("bold")) / max(1, len(boldish))
    # suppress only NEAR-UNIFORM bold (the all-Lora-Bold case): a table with
    # bold row labels + bold best scores can reach ~0.6 share and its bolds
    # are exactly the legend's promise (p.82/98 missing-bold cluster)
    bold_signifies = bold_share < 0.9

    def underlined(s):
        sb = s["bbox"]
        # LINKED text is underlined by link styling, never a word underline
        # (body text already guards this; cells didn't) — the double markup
        # '<u><a …>' painted a second underline in the cell's text color
        # over the link's own (SLEIGHT-Bench, owner-flagged)
        scy = (sb[1] + sb[3]) / 2
        for lk in oracle_page["links"]["uri"] + oracle_page["links"]["goto"]:
            for lr in lk.get("rects", []):
                if (lr[1] - 1 <= scy <= lr[3] + 1
                        and min(sb[2], lr[2]) - max(sb[0], lr[0]) > 0.5 * (sb[2] - sb[0])):
                    return False
        for ru in rules:
            rb = ru["bbox"]
            if (sb[3] - 2.5 <= rb[1] <= sb[3] + 5.0
                    and min(sb[2], rb[2]) - max(sb[0], rb[0]) > 0.5 * (sb[2] - sb[0])
                    and (rb[2] - rb[0]) < (sb[2] - sb[0]) * 3 + 24
                    # a rule overhanging the span >12pt on BOTH sides is a
                    # CELL border under a dense row (the p.182 'Mythos
                    # Preview' false underline), never a word underline
                    and not (rb[0] < sb[0] - 12 and rb[2] > sb[2] + 12)):
                # width guard: word underlines hug their word; a table-width
                # row border under a TALL row false-fired ('2/14' on p.96)
                return True
        return False

    spans_xy = _row_spans_xy(oracle_page, bbox)
    # column left edges (x0 clusters with >=3 members), for the stacked-line
    # reflow test: a cell's usable width runs to the NEXT column's edge
    _cl: dict[float, int] = {}
    for s in spans:
        k2 = next((k for k in _cl if abs(k - s["bbox"][0]) <= 2), s["bbox"][0])
        _cl[k2] = _cl.get(k2, 0) + 1
    col_edges = sorted(k for k, n in _cl.items() if n >= 3)
    out = html
    seen_rows: dict[str, int] = {}   # key -> prior HTML rows containing it
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy, ordinal=seen_rows)
        for p in set(p for p in plain if p):
            seen_rows[p] = seen_rows.get(p, 0) + 1
        if band is None:
            continue
        # row's spans: in band, plus wrapped/sub-line continuations hanging
        # below a member (the small '± 1.4%' second line). Absorb to a
        # FIXPOINT: a 3-pass cap only reached ~4 stacked lines, leaving the
        # tall passage cells of the constitution-edits table (pp.140-141)
        # unsegmentable — their docling glyph folds then survived (D41)
        chosen = [s for s in spans if s["text"].strip()
                  and band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1]]
        grew = True
        while grew:
            grew = False
            for s in spans:
                if s in chosen or not s["text"].strip():
                    continue
                sb = s["bbox"]
                if any(min(sb[2], m["bbox"][2]) - max(sb[0], m["bbox"][0]) > 0
                       and -1 <= sb[1] - m["bbox"][3] < 9 for m in chosen):
                    chosen.append(s)
                    grew = True
        # pool: squash key -> span instances in x-order (cells consume L->R)
        pool: dict[str, list] = {}
        for s in sorted(chosen, key=lambda s: (s["bbox"][0], s["bbox"][1])):
            pool.setdefault(_squash(s["text"]), []).append(s)
        used: dict[str, int] = {}
        # one span can GLUE two cells' text across columns ('99.96% (± 0.04%)
        # 0.51% (± 0.25%)', p.77 4.2.A): split it at the cell boundary into
        # virtual instances with proportional bboxes so segmentation matches
        # and the underline rule sees the correct half-width
        for p2 in plain:
            if not p2 or p2 in pool:
                continue
            for key in list(pool):
                if key.startswith(p2) and len(key) > len(p2) and pool[key]:
                    inst = pool[key].pop(0)
                    if not pool[key]:
                        del pool[key]
                    raw = inst["text"]
                    ridx = [j for j, ch in enumerate(raw) if not ch.isspace()]
                    cut_r = ridx[len(p2) - 1] + 1
                    sb = inst["bbox"]
                    cut_x = sb[0] + (sb[2] - sb[0]) * cut_r / max(1, len(raw))
                    left = {**inst, "text": raw[:cut_r],
                            "bbox": [sb[0], sb[1], cut_x, sb[3]]}
                    right = {**inst, "text": raw[cut_r:],
                             "bbox": [cut_x, sb[1], sb[2], sb[3]]}
                    pool.setdefault(p2, []).append(left)
                    if _squash(raw[cut_r:]):
                        pool.setdefault(_squash(raw[cut_r:]), []).append(right)
                    break
        # fnref digits docling baked into cell text ('LLM training3') are
        # consumable but unstyled; _inject_fnrefs converts them to <sup> later
        fn_keys = {_squash(s["text"]) for s in _table_spans(oracle_page, bbox)
                   if s.get("zone") == "fnref" and _squash(s["text"])}

        def segment(sq):
            """Greedy longest-prefix split of a cell's squash into pool keys
            (baked-in footnote digits pass through unstyled)."""
            segs, pos = [], 0
            while pos < len(sq):
                best = None
                for k in pool:
                    if k and sq.startswith(k, pos) and (best is None or len(k) > len(best)):
                        best = k
                if best is None:
                    for k in fn_keys:
                        if sq.startswith(k, pos):
                            best = k
                            break
                if best is None:
                    return None
                segs.append(best)
                pos += len(best)
            return segs

        cells = [c for _, _, c in tags]
        changed = False
        import html as _h
        for i, (c, p2) in enumerate(zip(cells, plain)):
            if not p2 or "<" in c:
                continue
            segs = segment(p2)
            if not segs:
                continue
            # positions live in DECODED text: mapping over the escaped cell
            # shifted every boundary 4 chars per '&amp;' ('<b>amp; contin</b>')
            c_dec = _h.unescape(c)
            raw_idx = [j for j, ch in enumerate(c_dec) if not ch.isspace()]
            pieces, cur, sq_pos = [], 0, 0
            prev_inst = None
            cell_insts, brk_bounds, tier_breaks, blank_breaks = [], [], [], []
            for k in segs:
                if k not in pool:   # baked-in fnref digit: pass through
                    st, en = raw_idx[sq_pos], raw_idx[sq_pos + len(k) - 1] + 1
                    sq_pos += len(k)
                    pieces.append(c_dec[cur:en])
                    cur = en
                    continue
                inst = pool[k][min(used.get(k, 0), len(pool[k]) - 1)]
                used[k] = used.get(k, 0) + 1
                wraps = []
                # single ALNUM segments can carry style (the wrapped '5' of
                # 'Mythos 5' lost its bold to a len>=2 guard); lone
                # punctuation stays unstyled — UNLESS it is the whole cell
                # (fable p.252 bolds two placeholder dashes, final sweep)
                styleable = len(k) >= 2 or k.isalnum() or k == p2
                if inst.get("bold") and bold_signifies and styleable:
                    wraps.append(("<b>", "</b>"))
                if inst.get("italic") and styleable:
                    # bold-italic sub-labels ('(Helpful-only)', pp.71/148)
                    # keep their slant (D42)
                    wraps.append(("<i>", "</i>"))
                if underlined(inst) and styleable:
                    wraps.append(("<u>", "</u>"))
                # a run set >=1.5pt below the cell's lead size is a QUIETER
                # TIER — the header parenthetical '(refusal rate)' /
                # '(median campaign execution score…)' (owner-spotted,
                # pp.69/71 family). <small> is outermost.
                lead_size = (cell_insts[0] if cell_insts else inst).get("size", 0)
                if styleable and inst.get("size", 0) <= lead_size - 1.5:
                    wraps.append(("<small>", "</small>"))
                st, en = raw_idx[sq_pos], raw_idx[sq_pos + len(k) - 1] + 1
                sq_pos += len(k)
                # emit the SPAN's text, not docling's: restores characters
                # docling folds (em-dashes, curly quotes) wherever the cell
                # is fully matchable
                seg_text = _h.escape(inst["text"].strip(), quote=False)
                for o, cl in wraps:
                    seg_text = o + seg_text + cl
                gap = c_dec[cur:st]
                if pieces and prev_inst is not None:
                    # at a LINE BREAK between segments: a wrapped version
                    # number rejoins without a space ('GPT-5.' / '5'); any
                    # other glued break gets one ('...1 h eq.200x...')
                    line_break = inst["bbox"][1] > prev_inst["bbox"][3] - 2
                    if line_break:
                        # version wrap = DIGIT-dot then digit ('GPT-5.'/'5');
                        # letter-dot is a sentence stack ('h eq.'/'200x...')
                        tail = re.sub(r"<[^>]+>", "", pieces[-1])
                        head = re.sub(r"<[^>]+>", "", seg_text)[:1]
                        wrap_join = bool(re.search(r"(\d\.|-)$", tail)) and head.isdigit()
                        if wrap_join:
                            gap = ""
                        else:
                            gap = gap or " "
                            # a BLANK LINE inside the cell (full line-height
                            # gap — '80% (Claude Opus 5)' | gap | '12–65%
                            # (other models)', constitution table
                            # edit-frequency column, owner-spotted) — same
                            # signal as the fence blank-line rule
                            line_gap = inst["bbox"][1] - prev_inst["bbox"][3]
                            line_h = prev_inst["bbox"][3] - prev_inst["bbox"][1]
                            if line_gap > 0.6 * line_h:
                                blank_breaks.append(len(pieces))
                            # a FONT-SIZE DROP at the line boundary is an
                            # unambiguous tier change — wraps never resize
                            # mid-cell ('Voter Suppression scenario' 11pt |
                            # '(median campaign…)' 9pt; '(Helpful-only)'
                            # 10pt) — hard break, no reflow test needed
                            elif inst.get("size", 0) <= prev_inst.get("size", 0) - 0.5:
                                tier_breaks.append(len(pieces))
                            # INTENTIONAL stack vs width wrap (D42, p.31
                            # '4x = 1 h eq.' | '200x = 8 h eq.'): only a
                            # SENTENCE-TERMINAL line qualifies (an unfenced
                            # reflow test fired on 76 sites across both cards
                            # — header wraps, value/± stacks, mid-sentence
                            # prose); if the next line's first word would
                            # have FIT with clear slack, the break was a hard
                            # return — recorded, patched to <br> once the
                            # cell's full extent is known
                            elif re.search(r"[.!?]$", tail.rstrip()):
                                brk_bounds.append((len(pieces), prev_inst, inst))
                pieces.append(gap + seg_text)
                cell_insts.append(inst)
                prev_inst = inst
                cur = en
            pieces.append(c_dec[cur:])
            for pi in tier_breaks:
                pieces[pi] = "<br>" + pieces[pi].lstrip(" ")
            for pi in blank_breaks:
                pieces[pi] = "<br><br>" + pieces[pi].lstrip(" ")
            # reflow test for recorded line-break boundaries: available width
            # runs to the cell's COLUMN boundary (next column edge, or table
            # right edge); the first word's width is scaled from its span.
            # Space width ~ 0.25em.
            if brk_bounds and cell_insts:
                cell_x2 = max(i["bbox"][2] for i in cell_insts)
                right = min([e for e in col_edges if e > cell_x2 + 2],
                            default=bbox[2]) - 6
                for pi, pv, nx in brk_bounds:
                    word = nx["text"].strip().split(" ")[0]
                    if not word or not nx["text"].strip():
                        continue
                    w = (nx["bbox"][2] - nx["bbox"][0]) * len(word) / max(1, len(nx["text"].rstrip()))
                    em = (pv["bbox"][3] - pv["bbox"][1])
                    # 12pt slack margin: estimated widths are noisy; a
                    # marginal fit is not evidence of a hard return
                    if pv["bbox"][2] + 0.25 * em + w <= right - 12:
                        pieces[pi] = "<br>" + pieces[pi].lstrip(" ")
            rebuilt_cell = "".join(pieces)
            # hyphen-wrap join artifact: a compound wrapped after its hyphen
            # ('introspection- based' -> 'introspection-based'). This card has
            # no syllabic mid-word hyphenation (surveyed), so the hyphen is
            # always part of the word — drop only the space, keep the hyphen
            # (suspended compounds 'single- and' keep both)
            rebuilt_cell = re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1-", rebuilt_cell)
            # adjacent same-style runs read as ONE run ('<b>Mythos</b> <b>5</b>')
            # small first: it is outermost, and merging it exposes the inner
            # b/i adjacencies for the merges below
            rebuilt_cell = re.sub(r"</small>(\s*)<small>", r"\1", rebuilt_cell)
            rebuilt_cell = re.sub(r"</b>(\s*)<b>", r"\1", rebuilt_cell)
            rebuilt_cell = re.sub(r"</i>(\s*)<i>", r"\1", rebuilt_cell)
            rebuilt_cell = re.sub(r"</u>(\s*)<u>", r"\1", rebuilt_cell)
            if rebuilt_cell != c:
                cells[i] = rebuilt_cell
                changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c2}</{tg}>" for (tg, a, _), c2 in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _cell_align_ctx(parts, oracle_page=None):
    """Per-table alignment context: the column / interval character streams a
    cell's text is matched against, plus their span and raw-char parallels.
    Factored out of _cell_blank_lines so other cell repairs (in-cell list
    reconstruction) can locate a cell's characters in the source spans
    instead of re-deriving lines from scratch."""
    """Blank lines INSIDE cells the row-band machinery can't reach (tall
    constitution rows): '80% (Claude Opus 5)' | gap | '12–65% (other
    models)' reads as one run (owner-spotted, D42). Column-align the cell's
    visible text to its span run (same alignment as _restore_cell_glyphs,
    but tag-tolerant and char→span indexed); where consecutive chars cross
    spans separated by a full line-height gap, the joining space becomes
    <br><br>. Ambiguous or unlocatable cells are left alone."""
    if oracle_page is not None:          # single-page call site
        parts = [(parts, oracle_page)]
    spans = []
    for i, (bx, pg) in enumerate(parts):
        for s in _table_spans(pg, bx):
            if (s.get("zone") == "fnref" or not s["text"].strip()
                    or s["text"].strip() in tuple("●•◦▪‣○■□")):
                continue
            if i:   # keep later pages after earlier ones in every ordering
                s = {**s, "bbox": [s["bbox"][0], s["bbox"][1] + 10000 * i,
                                   s["bbox"][2], s["bbox"][3] + 10000 * i]}
            spans.append(s)
    if not spans:
        return None
    clusters: dict[float, int] = {}
    for s in spans:
        key = next((k for k in clusters if abs(k - s["bbox"][0]) <= 2),
                   s["bbox"][0])
        clusters[key] = clusters.get(key, 0) + 1
    edges = sorted(k for k, n in clusters.items() if n >= 3)
    if not edges:
        return None
    cols: list[list] = [[] for _ in edges]
    for s in spans:
        i = max((j for j, e in enumerate(edges) if s["bbox"][0] >= e - 2), default=0)
        cols[i].append(s)
    def _colify(mem, by_band=False):
        mem = sorted(mem, key=(lambda s: (round((s["bbox"][1] + s["bbox"][3]) / 8),
                                          s["bbox"][0])) if by_band
                     else (lambda s: ((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0])))
        chars, srcs = [], []
        for s in mem:
            for ch in s["text"]:
                # glyph chars can be GLUED into a text span ('●​No user…')
                # and QUOTE glyphs fold unpredictably (docling turns double
                # quotes into singles — the p.13 'dramatic acceleration'
                # cell) — both dropped from BOTH sides of the alignment
                # quote glyphs are KEPT (folded only for comparison) so the
                # arrays stay parallel with the cell's chars and docling's
                # fold can be repaired from the span's true glyph
                if (not ch.isspace() and ch not in _INVIS
                        and ch not in "●•◦▪‣○■□"):
                    chars.append(ch)
                    srcs.append(s)
        return "".join(chars), srcs

    col_chars, col_spans = [], []
    for col in cols:
        chars, srcs = _colify(col)
        col_chars.append(chars)
        col_spans.append(srcs)
    # low-9 comma ‚ folds locally (docling normalizes it to ',' in cells;
    # the p.113 'standard‚' broke alignment mid-cell) — _QUOTE_FOLD itself
    # stays untouched, other repairs depend on its exact reach
    _LOW9 = str.maketrans({"‚": ","})
    col_folds = [c.translate(_QUOTE_FOLD).translate(_LOW9).translate(_QALL)
                 for c in col_chars]
    # FALLBACK families: pairwise edge intervals in band order — a cell whose
    # sub-structure spans two x0 tiers (an intro line at the cell edge plus
    # bullet text at a hanging indent, Table 3.10.A) matches no single-edge
    # column. Tried only when the canon single-column match fails, so
    # previously-matching cells keep their exact behavior.
    int_chars, int_spans = [], []
    seen_int = set()
    for i in range(len(edges)):
        for j in range(i + 1, len(edges) + 1):
            right = edges[j] - 2 if j < len(edges) else 1e9
            mem = [s for s in spans if edges[i] - 2 <= s["bbox"][0] < right]
            if len(mem) < 2:
                continue
            chars, srcs = _colify(mem, by_band=True)
            if chars in seen_int:
                continue
            seen_int.add(chars)
            int_chars.append(chars)
            int_spans.append(srcs)
    int_folds = [c.translate(_QUOTE_FOLD).translate(_LOW9).translate(_QALL)
                 for c in int_chars]

    import html as _h
    return {"col_chars": col_chars, "col_spans": col_spans, "col_folds": col_folds,
            "int_chars": int_chars, "int_spans": int_spans, "int_folds": int_folds,
            "edges": edges, "spans": spans, "LOW9": _LOW9}


def _match_cell_chars(plain: str, ctx: dict):
    """(srcs, raw) for a cell's visible characters, or None when the cell
    cannot be located unambiguously. Same matcher _cell_blank_lines uses."""
    if ctx is None:
        return None
    sq = (_squash(plain).translate(_INVIS_DEL).translate(_BULLET_DEL)
          .translate(ctx["LOW9"]).translate(_QALL))
    if len(sq) < 8:
        return None
    col_folds, int_folds = ctx["col_folds"], ctx["int_folds"]
    hits = [(ci, cf.find(sq)) for ci, cf in enumerate(col_folds) if cf.count(sq) == 1]
    hits = [h for h in hits if h[1] >= 0]
    if len(hits) == 1 and not any(cf.count(sq) > 1 for cf in col_folds):
        ci, at = hits[0]
        return ctx["col_spans"][ci][at:at + len(sq)], ctx["col_chars"][ci][at:at + len(sq)]
    if hits or any(cf.count(sq) > 1 for cf in col_folds):
        return None
    ihits = sorted(((len(int_folds[ci]), ci, int_folds[ci].find(sq))
                    for ci in range(len(int_folds)) if int_folds[ci].count(sq) == 1))
    ihits = [h for h in ihits if h[2] >= 0]
    if not ihits:
        return None
    _, ci, at = ihits[0]
    return ctx["int_spans"][ci][at:at + len(sq)], ctx["int_chars"][ci][at:at + len(sq)]


def _cell_blank_lines(html: str, bbox: list, oracle_page: dict) -> str:
    """Blank lines INSIDE cells the row-band machinery can't reach (tall
    constitution rows): '80% (Claude Opus 5)' | gap | '12–65% (other
    models)' reads as one run (owner-spotted, D42). Column-align the cell's
    visible text to its span run (same alignment as _restore_cell_glyphs,
    but tag-tolerant and char→span indexed); where consecutive chars cross
    spans separated by a full line-height gap, the joining space becomes
    <br><br>. Ambiguous or unlocatable cells are left alone."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s.get("zone") != "fnref" and s["text"].strip()
             # bullet glyphs sit in their OWN x0 cluster and defeated the
             # cell↔column char alignment for every bulleted cell (the
             # 3.10.A sub-paragraph gaps, owner-flagged) — drop them from
             # both sides of the alignment
             and s["text"].strip() not in tuple("●•◦▪‣○■□")]
    if not spans:
        return html
    clusters: dict[float, int] = {}
    for s in spans:
        key = next((k for k in clusters if abs(k - s["bbox"][0]) <= 2),
                   s["bbox"][0])
        clusters[key] = clusters.get(key, 0) + 1
    edges = sorted(k for k, n in clusters.items() if n >= 3)
    if not edges:
        return html
    cols: list[list] = [[] for _ in edges]
    for s in spans:
        i = max((j for j, e in enumerate(edges) if s["bbox"][0] >= e - 2), default=0)
        cols[i].append(s)
    def _colify(mem, by_band=False):
        mem = sorted(mem, key=(lambda s: (round((s["bbox"][1] + s["bbox"][3]) / 8),
                                          s["bbox"][0])) if by_band
                     else (lambda s: ((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0])))
        chars, srcs = [], []
        for s in mem:
            for ch in s["text"]:
                # glyph chars can be GLUED into a text span ('●​No user…')
                # and QUOTE glyphs fold unpredictably (docling turns double
                # quotes into singles — the p.13 'dramatic acceleration'
                # cell) — both dropped from BOTH sides of the alignment
                # quote glyphs are KEPT (folded only for comparison) so the
                # arrays stay parallel with the cell's chars and docling's
                # fold can be repaired from the span's true glyph
                if (not ch.isspace() and ch not in _INVIS
                        and ch not in "●•◦▪‣○■□"):
                    chars.append(ch)
                    srcs.append(s)
        return "".join(chars), srcs

    col_chars, col_spans = [], []
    for col in cols:
        chars, srcs = _colify(col)
        col_chars.append(chars)
        col_spans.append(srcs)
    # low-9 comma ‚ folds locally (docling normalizes it to ',' in cells;
    # the p.113 'standard‚' broke alignment mid-cell) — _QUOTE_FOLD itself
    # stays untouched, other repairs depend on its exact reach
    _LOW9 = str.maketrans({"‚": ","})
    col_folds = [c.translate(_QUOTE_FOLD).translate(_LOW9).translate(_QALL)
                 for c in col_chars]
    # FALLBACK families: pairwise edge intervals in band order — a cell whose
    # sub-structure spans two x0 tiers (an intro line at the cell edge plus
    # bullet text at a hanging indent, Table 3.10.A) matches no single-edge
    # column. Tried only when the canon single-column match fails, so
    # previously-matching cells keep their exact behavior.
    int_chars, int_spans = [], []
    seen_int = set()
    for i in range(len(edges)):
        for j in range(i + 1, len(edges) + 1):
            right = edges[j] - 2 if j < len(edges) else 1e9
            mem = [s for s in spans if edges[i] - 2 <= s["bbox"][0] < right]
            if len(mem) < 2:
                continue
            chars, srcs = _colify(mem, by_band=True)
            if chars in seen_int:
                continue
            seen_int.add(chars)
            int_chars.append(chars)
            int_spans.append(srcs)
    int_folds = [c.translate(_QUOTE_FOLD).translate(_LOW9).translate(_QALL)
                 for c in int_chars]

    import html as _h

    def cell_breaks(c):
        """Break map for one cell's inner HTML: char ordinal -> break tag.
        '<br><br>' at a full line-height gap (a blank line). '<br>' at a
        bold→non-bold LINE boundary when either (a) the cell's leading
        all-bold run ends there — a label construct, breaking like prose's
        standalone bold labels ('§ …' headings, final-sweep p.140; sibling
        rows must render uniformly, and a wrap exactly at a lead's end is
        not observed in either card) — or (b) mid-cell, when the next
        line's first word would have FIT (a deliberate return, not a
        wrap)."""
        plain = _h.unescape(re.sub(r"\[\^\d+\]", "", re.sub(r"<[^>]+>", "", c)))
        sq = (_squash(plain).translate(_INVIS_DEL).translate(_BULLET_DEL)
              .translate(_LOW9).translate(_QALL))
        if len(sq) < 8:
            return {}, {}, {}, {}
        hits = [(ci, cf.find(sq)) for ci, cf in enumerate(col_folds)
                if cf.count(sq) == 1]
        hits = [h for h in hits if h[1] >= 0]
        if len(hits) == 1 and not any(cf.count(sq) > 1 for cf in col_folds):
            ci, at = hits[0]
            srcs = col_spans[ci][at:at + len(sq)]
            raw = col_chars[ci][at:at + len(sq)]
        else:
            if hits or any(cf.count(sq) > 1 for cf in col_folds):
                return {}, {}, {}, {}
            # interval fallback: tightest family holding the cell exactly once
            ihits = sorted(((len(int_folds[ci]), ci, int_folds[ci].find(sq))
                            for ci in range(len(int_folds))
                            if int_folds[ci].count(sq) == 1))
            ihits = [h for h in ihits if h[2] >= 0]
            if not ihits:
                return {}, {}, {}, {}
            _, ci, at = ihits[0]
            srcs = int_spans[ci][at:at + len(sq)]
            raw = int_chars[ci][at:at + len(sq)]
        # GLYPH REPAIR: docling folds the PDF's curly quotes to straight
        # ones ('dramatic acceleration', p.13). The alignment folds every
        # quote variant, so any position where the cell's char and the
        # span's raw char are both quote-ish but differ is a fold to undo.
        cellraw = [ch for ch in _squash(plain).translate(_INVIS_DEL)
                   .translate(_BULLET_DEL).translate(_LOW9)]
        subs = {}
        if len(cellraw) == len(raw):
            for k, (a2, b2) in enumerate(zip(cellraw, raw)):
                if a2 != b2 and a2 in "'\"“”‘’" and b2 in "'\"“”‘’":
                    subs[k] = b2
        cell_x2 = max(s["bbox"][2] for s in srcs)
        right = min([e for e in edges if e > cell_x2 + 2], default=bbox[2]) - 6
        breaks = {}
        for k in range(1, len(srcs)):
            a, b = srcs[k - 1], srcs[k]
            if a is b:
                continue
            if b["bbox"][1] <= a["bbox"][3] - 2:
                continue  # same line
            line_h = a["bbox"][3] - a["bbox"][1]
            gap = b["bbox"][1] - a["bbox"][3]
            if gap > 0.6 * line_h and "<p>" not in c:
                # paragraph-split cells keep their <p> boundary as the blank
                breaks[k - 1] = "<br><br>"
                continue
            if not (a.get("bold") and not b.get("bold")):
                continue
            is_lead = all(s.get("bold") for s in srcs[:k])
            word = b["text"].strip().split(" ")[0]
            w = ((b["bbox"][2] - b["bbox"][0]) * len(word)
                 / max(1, len(b["text"].rstrip())))
            fits = bool(word) and a["bbox"][2] + 0.25 * line_h + w <= right - 12
            if is_lead or fits:
                breaks[k - 1] = "<br>"
        # ITALIC runs (D42's in-cell italics live in restyle's segmentation,
        # which these tall/bulleted cells defeat — Table 3.10.A 'double the
        # rate of progress…', owner-flagged): the same char→span map knows
        # each char's slant. Only for cells restyle left untouched (no <i>),
        # runs of ≥2 chars.
        opens, closes = {}, {}
        if "<i>" not in c:
            run_start = None
            for k in range(len(srcs) + 1):
                it = bool(srcs[k].get("italic")) if k < len(srcs) else False
                if it and run_start is None:
                    run_start = k
                elif not it and run_start is not None:
                    if k - run_start >= 2:
                        opens[run_start] = "<i>"
                        closes[k - 1] = "</i>"
                    run_start = None
        return breaks, opens, closes, subs

    def fix_cell(m):
        tg, attrs, c = m.groups()
        breaks, opens, closes, subs = cell_breaks(c)
        if not breaks and not opens and not subs:
            return m.group(0)
        # walk the TAGGED cell as (tag | entity | char) tokens, counting
        # visible non-space chars; after ordinal k in `breaks`, a pending
        # <br><br> is emitted before the NEXT visible char (tags pass
        # through; the joining whitespace is swallowed)
        toks = re.findall(r"<[^>]+>|&[a-zA-Z0-9#]{1,8};|\[\^\d+\]|.", c, re.S)
        out, k, pending = [], -1, False
        for t in toks:
            if t.startswith("[^"):
                # footnote-ref token: outside the alignment (the family
                # stream excludes fnref spans); pending breaks ride past it
                out.append(t)
                continue
            if t.startswith("<"):
                if pending and re.fullmatch(r"<br\s*/?>", t):
                    # the cell already breaks here (a _restyle_cells tier
                    # break) — don't double it
                    pending = False
                out.append(t)
                continue
            vis = _h.unescape(t)
            if vis.isspace() or vis in _INVIS:
                if not pending:
                    out.append(t)
                continue
            if vis in "●•◦▪‣○■□":
                # bullet glyphs are outside the alignment — pass through,
                # and a pending break lands BEFORE the glyph
                if pending:
                    out.append(pending)
                    pending = False
                out.append(t)
                continue
            if pending:
                out.append(pending)
                pending = False
            k += 1
            if k in opens:
                out.append(opens.pop(k))
            out.append(_h.escape(subs[k], quote=False) if k in subs else t)
            if k in closes:
                out.append(closes.pop(k))
            if k in breaks:
                pending = breaks.pop(k)
        return f"<{tg}{attrs}>{''.join(out)}</{tg}>"

    return re.sub(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", fix_cell, html, flags=re.S)


def _restore_cell_glyphs(html: str, bbox: list, oracle_page: dict) -> str:
    """Glyph repair for cells _restyle_cells cannot segment (D41): tall
    multi-line passage rows (constitution-edits table, opus-5 pp.140-141 /
    fable-5 pp.243-245) defeat the row-band anchor, so their text stays
    docling's — with curly quotes folded to straight and dashes to hyphens.

    Repair by COLUMN alignment: a cell's lines are contiguous top-to-bottom
    within its column, so the cell's whitespace-free fold-squash occurs as a
    substring of the column's. When that occurrence is UNIQUE across all
    columns, map the oracle glyphs back 1:1 over non-space chars (docling's
    spacing kept). Squash-equality means only fold-class characters can
    change; ambiguous or unlocatable cells are left untouched."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s.get("zone") != "fnref" and s["text"].strip()]
    if not spans:
        return html
    # column edges = x0 clusters with enough members to be a real column
    # start (mid-line style-boundary spans have stray x0s and must not
    # found a column of their own)
    clusters: dict[float, int] = {}
    for s in spans:
        key = next((k for k in clusters if abs(k - s["bbox"][0]) <= 2),
                   s["bbox"][0])
        clusters[key] = clusters.get(key, 0) + 1
    edges = sorted(k for k, n in clusters.items() if n >= 3)
    if not edges:
        return html
    cols: list[list] = [[] for _ in edges]
    for s in spans:
        i = max((j for j, e in enumerate(edges) if s["bbox"][0] >= e - 2), default=0)
        cols[i].append(s)
    col_chars = []
    for col in cols:
        col.sort(key=lambda s: ((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0]))
        # zero-widths are TRANSPARENT to alignment: a lone ZWSP span between
        # 'Inserts:' and its quote (fable p.243 row 3) broke contiguity and
        # the cell silently kept its docling folds
        col_chars.append("".join(ch for s in col for ch in s["text"]
                                 if not ch.isspace() and ch not in _INVIS))
    col_folds = [c.translate(_QUOTE_FOLD) for c in col_chars]

    import html as _h

    def fix_cell(m):
        tg, attrs, c = m.groups()
        if "<" in c:
            return m.group(0)
        c_dec = _h.unescape(c)
        sq = _squash(c_dec).translate(_INVIS_DEL)
        if len(sq) < 8:          # short cells: containment too ambiguous
            return m.group(0)
        hits = [(ci, cf.find(sq)) for ci, cf in enumerate(col_folds)
                if cf.count(sq) == 1]
        hits = [h for h in hits if h[1] >= 0]
        if len(hits) != 1 or any(cf.count(sq) > 1 for cf in col_folds):
            return m.group(0)
        ci, at = hits[0]
        true_chars = col_chars[ci][at:at + len(sq)]
        out_chars, k = [], 0
        for ch in c_dec:
            if ch.isspace() or ch in _INVIS:
                out_chars.append(ch)
            else:
                out_chars.append(true_chars[k])
                k += 1
        new_dec = "".join(out_chars)
        if new_dec == c_dec:
            return m.group(0)
        return f"<{tg}{attrs}>{_h.escape(new_dec, quote=False)}</{tg}>"

    return re.sub(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", fix_cell, html, flags=re.S)


# zero-width/invisible characters, transparent to glyph-repair alignment
_INVIS = "​‌‍⁠﻿­"
_QALL = str.maketrans({c: '"' for c in "'\"“”‘’"})
_QDEL = str.maketrans("", "", "'\"“”‘’")
_BULLET_DEL = str.maketrans("", "", "●•◦▪‣○■□")
_INVIS_DEL = {ord(c): None for c in _INVIS}

# comparison-only fold: ALL quote variants to one class (docling and PyMuPDF
# can disagree on single vs double for the same glyph), dashes to hyphen
_QUOTE_FOLD = {0x2019: 0x27, 0x2018: 0x27, 0x201C: 0x27, 0x201D: 0x27,
               0x22: 0x27, 0x2014: 0x2D, 0x2013: 0x2D}


def _squash(s: str) -> str:
    """Comparison key: whitespace-free, quote-variant-folded (docling
    normalizes curly quotes; the oracle preserves the PDF's). Output text
    always comes from the oracle spans, so fidelity is unaffected."""
    return re.sub(r"\s+", "", s).translate(_QUOTE_FOLD)


def _cell_sq(c: str) -> str:
    """Squash of a cell's visible text: tags stripped, HTML entities decoded
    (docling emits &#x27; etc., which can never match oracle span text)."""
    import html as _h
    return _squash(_h.unescape(re.sub(r"<[^>]+>", "", c)))


def _row_spans_xy(oracle_page, bbox):
    """squash text -> [(x0, y_center)] for body spans inside the table bbox.
    Includes COMPOSITES: a wrapped cell renders as 2-3 stacked spans sharing a
    left edge ('Claude Mythos' / 'Preview') — their concatenation is offered
    as a candidate too, keyed at the stack's x0 and mean y."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s["text"].strip()]
    m: dict[str, list[tuple[float, float]]] = {}
    for s in spans:
        sb = s["bbox"]
        m.setdefault(_squash(s["text"]), []).append((sb[0], (sb[1] + sb[3]) / 2))
    # stacked runs: same x0 (±2), vertically adjacent (gap < 9pt)
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        for i in range(len(col)):
            for j in range(i + 1, min(i + 6, len(col))):
                if col[j]["bbox"][1] - col[j - 1]["bbox"][3] >= 9:
                    break
                run = col[i:j + 1]
                key = _squash("".join(s["text"] for s in run))
                # keyed at the TOP span's y: cells are top-aligned, so a
                # wrapped cell's first line is coplanar with its single-line
                # row-mates (mean y drifted 7pt and broke band agreement)
                y0 = (run[0]["bbox"][1] + run[0]["bbox"][3]) / 2
                m.setdefault(key, []).append((run[0]["bbox"][0], y0))
    return m


def _row_band(plain, cand, tol=7.0, ordinal=None):
    """Median y of the row's uniquely-matchable cells (usually the model
    name) — the anchor that ties HTML rows back to page geometry."""
    ys = [cand[p][0][1] for p in plain if p and len(cand.get(p, [])) == 1]
    if not ys:
        # a unique key PREFIXING a garbled cell ('Claude Fable 5' inside
        # 'Claude Fable 5 88% (±') anchors too — exactly the rows that
        # need rebuilding
        for p in plain:
            if not p:
                continue
            hits = [v for k, v in cand.items()
                    if len(k) >= 4 and p.startswith(k) and len(v) == 1]
            if len(hits) == 1:
                ys.append(hits[0][0][1])
    if not ys:
        # fully-scrambled row (docling hallucinated a wrap and rotated the
        # fragments — opus-5 p.52 'Sonnet 5 96.65% | … | Claude (± 0.07%)'):
        # no cell equals or prefixes any span, but a unique span key is still
        # CONTAINED in the row's concatenated text. The char-multiset guard
        # in _rebuild_row keeps a false anchor from doing damage.
        concat = "".join(plain)
        for k, v in cand.items():
            if len(k) >= 6 and len(v) == 1 and k in concat:
                ys.append(v[0][1])
    if not ys and ordinal is not None:
        # every anchor is AMBIGUOUS (all the row's values recur elsewhere —
        # p.75 'Without thinking' / '0.41%' / '8/40', D42): HTML rows and
        # span instances share y-order, so the row's ordinal among prior
        # rows containing the key picks the instance. The agreement check
        # below still rejects a bad pick.
        for p in plain:
            v = cand.get(p) if p else None
            if v and len(v) > 1:
                idx = ordinal.get(p, 0)
                if idx < len(v):
                    ys.append(sorted(inst[1] for inst in v)[idx])
    if not ys:
        return None
    ys.sort()
    ymed = ys[len(ys) // 2]
    # all anchors must agree (a stray unique match off-row poisons the band)
    if ys[-1] - ys[0] > tol:
        return None
    return ymed - tol, ymed + tol


def _resplit_misjoined_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes splits two cells' text at the WRONG boundary
    ('99.70% (±' | '0.17%) 0.09% (± 0.07%)'). When two adjacent cells match
    no span individually but their concatenation equals exactly two banded
    spans, re-split at the true span boundary."""
    spans_xy = _row_spans_xy(oracle_page, bbox)
    sq2text = {_squash(s["text"]): s["text"].strip()
               for s in _table_spans(oracle_page, bbox)}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        banded = {k for k, v in spans_xy.items() if any(band[0] <= y <= band[1] for _, y in v)}
        cells = [c for _, _, c in tags]
        changed = False
        for i in range(len(plain) - 1):
            if plain[i] in banded or plain[i + 1] in banded or not plain[i]:
                continue
            joined = plain[i] + plain[i + 1]
            for k1 in banded:
                if joined.startswith(k1) and joined[len(k1):] in banded:
                    import html as _h
                    cells[i] = _h.escape(sq2text[k1], quote=False)
                    cells[i + 1] = _h.escape(sq2text[joined[len(k1):]], quote=False)
                    changed = True
                    break
            if changed:
                break
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal):
    """Rebuild a garbled row directly from its banded spans (x-order), merging
    stacked wraps and sub-line annotations (the small '±1.4%' under a score).
    Fires only when the merged-cell count == modal columns AND the char
    multiset of the row's cells equals the spans' — pure re-segmentation."""
    inviz = re.compile("[\u200b\u200c\u200d\ufeff\u00ad]")
    allspans = [s for s in _table_spans(oracle_page, bbox)
                if inviz.sub("", s["text"]).strip() and s.get("zone") != "fnref"]
    chosen = [s for s in allspans
              if band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1]]
    # absorb sub-lines: x-overlapping spans hanging <= 5pt below a member
    # (wrapped cell second lines, small ± uncertainty rows)
    for _ in range(2):
        for s in allspans:
            if s in chosen:
                continue
            sb = s["bbox"]
            for m in chosen:
                mb = m["bbox"]
                if (min(sb[2], mb[2]) - max(sb[0], mb[0]) > 0
                        and -1 <= sb[1] - mb[3] <= 5):
                    chosen.append(s)
                    break
    chosen.sort(key=lambda s: s["bbox"][0])
    # merge into cells by x-range overlap (a sub-span may start a few pt
    # right of its column's number when centered)
    cells2 = []  # [x0, x1, [spans]]
    for s in chosen:
        sb = s["bbox"]
        if cells2 and min(sb[2], cells2[-1][1]) - max(sb[0], cells2[-1][0]) > 0:
            cells2[-1][1] = max(cells2[-1][1], sb[2])
            cells2[-1][2].append(s)
        else:
            cells2.append([sb[0], sb[2], [s]])
    # a row whose spans start far right of the table edge has an EMPTY
    # leading cell docling dropped (p.82 'API, without a system prompt'
    # header sub-row: PDF has [_, span(2-3), Claude.ai])
    if len(cells2) == len(tags) - 1 and cells2 and cells2[0][0] - bbox[0] > 60:
        cells2.insert(0, [bbox[0], bbox[0], []])

    # re-segmentation can only UN-glue: never fewer cells than docling
    # emitted (x-overlapping true columns fuse and are correctly rejected
    # here, e.g. the wide sentence-cell welfare tables)
    if len(cells2) < max(2, len(tags)):
        return None
    texts = []
    for _, _, members in cells2:
        members.sort(key=lambda s: (round(s["bbox"][1]), s["bbox"][0]))
        import html as _h
        texts.append(_h.escape(inviz.sub("", _join_wrapped(s["text"] for s in members)).strip(),
                               quote=False) if members else "")
    have = sorted(inviz.sub("", "".join(plain)))
    want = sorted(_squash("".join(texts)))
    if have != want:
        # tolerate surplus equal to in-band fnref digits docling absorbed into
        # a cell ('Sonnet 4.6' + ref '4' -> 'Sonnet 4.64', p.51); the ref is
        # re-injected as a proper <sup> afterwards
        from collections import Counter as _C2
        fn = "".join(_squash(s["text"]) for s in _table_spans(oracle_page, bbox)
                     if s.get("zone") == "fnref"
                     and band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1])
        if not fn or _C2(have) - _C2(sorted(fn)) != _C2(want):
            return None
    tg = tags[0][0]
    return "<tr>" + "".join(f"<{tg}>{c}</{tg}>" for c in texts) + "</tr>"


def _column_chains(spans):
    """Maximal vertical chains of spans sharing a left-edge cluster with
    < 9pt line gaps — the geometry of a wrapped (multi-line) table cell."""
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    chains = []
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        cur = [col[0]]
        for s in col[1:]:
            if s["bbox"][1] - cur[-1]["bbox"][3] < 9:
                cur.append(s)
            else:
                chains.append(cur)
                cur = [s]
        chains.append(cur)
    return [c for c in chains if len(c) > 1]


def _extend_truncated_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes drops the trailing line(s) of a wrapped cell
    ('Claude Mythos' sans 'Preview' p.72; a tall interview cell sans its
    final 'conversations?' line p.311). When a cell's text equals a
    consecutive span run of an x-column and the run's IMMEDIATE continuation
    (vertically adjacent, < 9pt) is claimed by no cell in the table, extend
    the cell with that continuation."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    cols = []
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        cols.append(col)
    spans_xy = _row_spans_xy(oracle_page, bbox)
    all_cells = {_cell_sq(c)
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", html, re.S)}
    # OWNERSHIP: spans consumed by any cell's exact chain match may never be
    # appended as another cell's "continuation" — the §6.6 damage class:
    # 'Claude Opus 4.8' anchored onto its mid-sentence twin inside the
    # Sonnet row's capability cell and swallowed that cell's tail; 'See
    # the … System Card' fragments leaked across rows the same way.
    owned: set[int] = set()
    for sq in all_cells:
        if not sq:
            continue
        # x0-chains, the reading-order sequence, AND column regions: a cell
        # containing a link matches in reading order; a TALL one only
        # within its column region
        for col in cols + [_reading_seq(spans)] + _column_regions(spans):
            for st in range(len(col)):
                acc, run = "", []
                for j in range(st, len(col)):
                    acc += _squash(col[j]["text"])
                    run.append(col[j])
                    if len(acc) >= len(sq):
                        break
                if acc == sq:
                    owned.update(id(s) for s in run)
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        cells = [c for _, _, c in tags]
        changed = False
        for i, p2 in enumerate(plain):
            # without a band (a mega-cell continuation row too tall for
            # composite anchors, p.311) the text match itself is the anchor —
            # but only for substantial text, where it's unique
            if not p2 or (band is None and len(p2) < 12):
                continue
            cand = []
            for col in cols:
                for st in range(len(col)):
                    y0 = (col[st]["bbox"][1] + col[st]["bbox"][3]) / 2
                    if band is not None and not band[0] <= y0 <= band[1]:
                        continue
                    acc = ""
                    for j in range(st, len(col)):
                        acc += _squash(col[j]["text"])
                        if len(acc) > len(p2):
                            break
                        if acc == p2:
                            # immediate adjacent continuation run below — but
                            # never across a horizontal table rule: in dense
                            # tables the next ROW starts <9pt below and the
                            # old guard cascaded its bullets into this cell
                            rules_y = [ru["bbox"][1] for ru in oracle_page.get("rules", [])
                                       if min(col[j]["bbox"][2], ru["bbox"][2])
                                       - max(col[j]["bbox"][0], ru["bbox"][0]) > 4]
                            tail = []
                            k = j + 1
                            while (k < len(col)
                                   and col[k]["bbox"][1] - col[k - 1]["bbox"][3] < 9
                                   and id(col[k]) not in owned
                                   and not any(col[k - 1]["bbox"][3] - 1 <= ry
                                               <= col[k]["bbox"][1] + 1
                                               for ry in rules_y)):
                                tail.append(col[k])
                                k += 1
                            if tail and all(_squash(s["text"]) not in all_cells
                                            for s in tail):
                                cand.append(col[st:j + 1] + tail)
                            break
            if len(cand) != 1:
                continue
            import html as _h
            cells[i] = _h.escape(_join_wrapped(s["text"] for s in cand[0]),
                                 quote=False)
            changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _promote_white_text_headers(html: str, bbox: list, oracle_page: dict) -> str:
    """A header sub-row that docling tagged <td>: the column sub-labels
    ('Attempts'/'Scenarios') under a colspan group sit in the dark header
    band as bold WHITE text, but rendered plain (p.95/96/98 prompt-injection
    tables). White text occurs only in header bands in this card, so a
    non-first row whose every non-empty cell is white-text is a header
    continuation — promote its non-empty <td> to <th>."""
    hdr = [s for s in _table_spans(oracle_page, bbox)
           if s["text"].strip() and s.get("color") in HEADER_TEXT]
    # a header cell can span several spans ('Non-novel chemical/ biological
    # weapons' + 'production', p.12) — test containment in the header stream
    # rather than equality with one span, and group by COLUMN: reading order
    # interleaves the columns of a multi-column header row
    white_blobs = _header_blobs(hdr)
    if not white_blobs:
        return html
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    out = html
    for r in rows:   # incl. row 0 — docling tagged the p.115 header <td>
        cells = re.findall(r"<(t[dh])([^>]*)>(.*?)</t[hd]>", r, re.S)
        nonempty = [(tg, a, c) for tg, a, c in cells if re.sub(r"<[^>]+>", "", c).strip()]
        if not nonempty or not all(
                any(_squash(re.sub(r"<[^>]+>", "", c)) in b for b in white_blobs)
                for _, _, c in nonempty):
            continue
        fixed = r
        for tg, a, c in cells:
            if tg == "td" and re.sub(r"<[^>]+>", "", c).strip():
                fixed = fixed.replace(f"<td{a}>{c}</td>", f"<th{a}>{c}</th>", 1)
        out = out.replace(r, fixed, 1)
    return out


def _fix_wrapped_header_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Colspan header sub-rows damaged by docling (p.82 family):
    (1) one span's text split across two adjacent cells ('API,' +
        'without a system prompt') -> merge to the span's true text;
    (2) the leading EMPTY cell dropped (the span starts well inside the
        table) -> restore it."""
    spans_xy = _row_spans_xy(oracle_page, bbox)
    sq2text = {}
    for s in _table_spans(oracle_page, bbox):
        if s["text"].strip():
            sq2text.setdefault(_squash(s["text"]), s["text"].strip())

    def logical_cols(row_tags):
        n = 0
        for _, a, _ in row_tags:
            m = re.search(r'colspan="(\d+)"', a)
            n += int(m.group(1)) if m else 1
        return n

    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if not rows:
        return html
    full = logical_cols(re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", rows[0], re.S))
    out = html
    for r in rows:
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        # colspan rows are header-ish and always eligible; colspan-free
        # rows only when logically NARROWER than the table — full-width
        # data rows must never gain a spurious lead cell (the 0->35
        # displaced regression)
        has_colspan = any("colspan" in a for _, a, _ in tags)
        if len(tags) < 2 or (not has_colspan and logical_cols(tags) >= full):
            continue
        plain = [_cell_sq(c) for _, _, c in tags]
        changed = False
        # (1) merge a same-span split across cells 0/1
        if plain[0] and plain[1]:
            key = plain[0] + plain[1]
            if key in spans_xy and len(spans_xy[key]) == 1:
                tg, attr1 = tags[1][0], tags[1][1]
                import html as _h
                tags = ([(tg, attr1, _h.escape(sq2text[key], quote=False))]
                        + tags[2:])
                plain = [key] + plain[2:]
                changed = True
        # (2) restore the dropped empty lead cell
        hit = spans_xy.get(plain[0])
        if plain[0] and hit and len(hit) == 1 and hit[0][0] - bbox[0] > 60:
            tags = [(tags[0][0], "", "")] + tags
            changed = True
        # (3) distribute group labels over their column groups: ['', 'API…',
        # 'Claude.ai'] over 4 data columns -> colspan=2 each, so the label
        # visibly spans its group like the PDF (owner-flagged ambiguity)
        labels = [i for i, (_, a, c) in enumerate(tags)
                  if _cell_sq(c) and "colspan" not in a]
        if (tags and not _cell_sq(tags[0][2]) and labels
                and labels == list(range(1, len(tags)))):
            data_cols = full - 1
            n = len(labels)
            if n and data_cols % n == 0 and data_cols // n > 1:
                k = data_cols // n
                # group labels are bold in the PDF (span flags confirm on
                # every instance); rebuilt rows lost it — enforce uniformly
                tags = [tags[0]] + [
                    (g, f' colspan="{k}"',
                     c if "<b>" in c or g == "th" else f"<b>{c}</b>")
                    for g, a, c in tags[1:]]
                changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{g}{a}>{c}</{g}>" for g, a, c in tags) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _repair_rotation(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling TableFormer cyclically mis-assigns columns on wide numeric
    tables. Repair per row from geometry: anchor the row's y-band via its
    unique-text cells, take each cell's span x within that band (duplicate
    values consume banded x's in order), and reorder cells by x. Rows that
    can't be fully matched are left alone — never half-repair."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if len(rows) < 3:
        return html
    spans_xy = _row_spans_xy(oracle_page, bbox)
    from collections import Counter as _C
    _counts = _C()
    for r in rows:
        tg = re.findall(r"<(t[hd])([^>]*)>", r)
        if not any("colspan" in a or "rowspan" in a for _, a in tg):
            _counts[len(tg)] += 1
    modal = _counts.most_common(1)[0][0] if _counts else 0

    out = html
    for ri, r in enumerate(rows):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        if len(tags) < 2 or any("colspan" in a or "rowspan" in a for _, a, _ in tags):
            continue
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        if any(not p for p in plain):
            # an empty cell defeats pool matching but not the geometric
            # rebuild (p.82 row with '' + glued 'N/A N/A')
            rb = _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal)
            if rb:
                out = out.replace(r, rb, 1)
            continue
        if modal and len(tags) != modal:
            # cell count differs from the table's column count: shape damage
            # (a wrapped header cell split in two + dropped empty, p.82) —
            # geometric rebuild, never per-cell reorder
            rb = _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal)
            if rb:
                out = out.replace(r, rb, 1)
            continue
        from collections import Counter
        fn_digits = [_squash(s["text"]) for s in _table_spans(oracle_page, bbox)
                     if s.get("zone") == "fnref"
                     and band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1]]
        keymap = {}
        for t2 in set(plain):
            if t2 in spans_xy:
                keymap[t2] = t2
                continue
            # 'LLMtraining3(avgspeedup)': the 3 is a baked-in fnref digit —
            # match the digit-stripped variant instead of rebuilding
            for d in fn_digits:
                v = t2.replace(d, "", 1)
                if v in spans_xy:
                    keymap[t2] = v
                    break
        plain = [keymap.get(p2, p2) for p2 in plain]
        need = Counter(plain)
        pool = {t2: sorted(x for x, y in spans_xy.get(t2, []) if band[0] <= y <= band[1])
                for t2 in need}
        if any(len(pool[t2]) < n2 for t2, n2 in need.items()):
            # last resort for garbled rows (mis-glued AND rotated, p.269/297):
            # rebuild the whole row from the band's spans in x-order, but only
            # under char-multiset equality — same content, re-segmented
            rb = _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal)
            if rb:
                out = out.replace(r, rb, 1)
            continue
        if ri == 0:
            continue
        taken = {t2: 0 for t2 in need}
        cell_x = []
        for p2 in plain:
            cell_x.append(pool[p2][taken[p2]])
            taken[p2] += 1
        if len(set(cell_x)) != len(cell_x):
            continue
        perm = sorted(range(len(cell_x)), key=lambda i: cell_x[i])
        if perm == list(range(len(cell_x))):
            continue
        inner = [tags[i][2] for i in perm]
        rebuilt = "<tr>" + "".join(
            f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, inner)) + "</tr>"
        out = out.replace(r, rebuilt, 1)
    return out


def _clean_html(html: str) -> str:
    html = re.sub(r"\s+", " ", html).replace("> <", "><").strip()
    return html


def extract(page_nos: list[int]):
    import fitz
    from docling.document_converter import DocumentConverter

    src = fitz.open(CARD / "source.pdf")
    conv = DocumentConverter()
    cache = _load()
    for pno in page_nos:
        H = src[pno - 1].rect.height
        mini = fitz.open()
        mini.insert_pdf(src, from_page=pno - 1, to_page=pno - 1)
        mp = Path(tempfile.mkdtemp()) / "p.pdf"
        mini.save(mp)
        doc = conv.convert(mp).document
        entries = []
        for t in doc.tables:
            bb = t.prov[0].bbox
            # docling BOTTOMLEFT -> PyMuPDF TOPLEFT (same page dimensions)
            x0, x1 = bb.l, bb.r
            y0, y1 = H - bb.t, H - bb.b
            entries.append({"bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                            "html": _clean_html(t.export_to_html(doc))})
        cache[str(pno)] = entries
        print(f"p.{pno}: {len(entries)} table(s)")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1))
    print(f"cached {len(cache)} pages -> {CACHE}")


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:]]
    if not pages:
        import re as _re
        pages = sorted({int(m) for p in (CARD / "sections").glob("*.md")
                        for blk in _re.findall(r"<table.*?</table>", p.read_text(), _re.S)
                        for m in _re.findall(r"<!-- p\.(\d+) -->",
                                             p.read_text()[:p.read_text().find(blk)][-4000:])[-1:]})
        # simpler: just pass pages explicitly; fall back to known table pages
        pages = pages or [19, 20, 49, 51, 61, 72, 73, 77, 79, 80, 82, 85, 86, 89, 91,
                          95, 96, 98, 235, 236, 244, 252, 253, 264, 269, 297,
                          309, 310, 311, 312, 313, 314, 315, 316, 317, 318]
    extract(pages)
