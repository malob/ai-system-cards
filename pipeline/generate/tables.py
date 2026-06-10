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

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "cards/anthropic/claude-fable-5"
CACHE = REPO / "pipeline/.cache/tables.json"


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
        html = re.sub(r"<caption>.*?</caption>", "", t["html"], flags=re.S)
        if oracle_page is not None:
            # split BEFORE rotation repair: a glued cell defeats x-matching,
            # leaving its row rotated; once split, the row becomes repairable
            html = _split_glued_cells(html, t["bbox"], oracle_page)
            html = _resplit_misjoined_cells(html, t["bbox"], oracle_page)
            html = _extend_truncated_cells(html, t["bbox"], oracle_page)
            html = _repair_rotation(html, t["bbox"], oracle_page)
            html = _restyle_cells(html, t["bbox"], oracle_page)
            html = _inject_fnrefs(html, t["bbox"], oracle_page)
        out.append({**t, "html": html})
    return out


def _table_spans(oracle_page, bbox):
    for s in oracle_page["spans"]:
        sb = s["bbox"]
        if (bbox[0] - 3 <= sb[0] and sb[2] <= bbox[2] + 3
                and bbox[1] - 3 <= sb[1] and sb[3] <= bbox[3] + 3):
            yield s


def _split_glued_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes glues two cells' values into one cell, leaving an
    empty cell in the row ('88.1 97.5' | '' — p.85 Sonnet row). When a glued
    cell's text equals the concatenation of exactly two oracle spans and the
    row has exactly one empty cell, split by span x-order."""
    spans = list(_table_spans(oracle_page, bbox))
    sq = {_squash(s["text"]): s for s in spans}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        empties = [i for i, (_, _, c) in enumerate(tags) if not _squash(re.sub(r"<[^>]+>", "", c))]
        if len(empties) != 1:
            continue
        for i, (tg, attr, c) in enumerate(tags):
            plain = _squash(re.sub(r"<[^>]+>", "", c))
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
        pat = re.compile("(" + re.escape(anchor) + r")(?![^<]*</sup>)")
        out, k = pat.subn(lambda m: m.group(1) + f"<sup>[^{n}]</sup>", out, count=1)
    return out


def _restyle_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Recover bold (best-score) and underline (second-best, FL-09) styling in
    table cells from oracle facts: bold span flags; thin rules under spans."""
    spans = list(_table_spans(oracle_page, bbox))
    rules = oracle_page.get("rules", [])
    # bold only signifies when it DEVIATES from the table's dominant weight:
    # some tables (2.2.1.A) are set entirely in Lora-Bold, where the visual
    # weight reads regular and 'bold' carries no information (owner-flagged)
    # exclude header text (white-on-dark) from the dominance count, else
    # data-cell bolds get suppressed in tables with bold headers + bold
    # row-label columns (the 4.4.2 regression)
    boldish = [s for s in spans
               if s["text"].strip() and s.get("color") not in ("#ffffff", "#faf9f5")]
    bold_share = sum(1 for s in boldish if s.get("bold")) / max(1, len(boldish))
    bold_signifies = bold_share <= 0.5

    def underlined(s):
        sb = s["bbox"]
        for ru in rules:
            rb = ru["bbox"]
            if (sb[3] - 2.5 <= rb[1] <= sb[3] + 5.0
                    and min(sb[2], rb[2]) - max(sb[0], rb[0]) > 0.5 * (sb[2] - sb[0])):
                return True
        return False

    out = html
    for s in spans:
        text = s["text"].strip()
        if not text or len(text) < 2:
            continue
        wraps = []
        if s.get("bold") and bold_signifies:
            wraps.append(("<b>", "</b>"))
        if underlined(s):
            wraps.append(("<u>", "</u>"))
        if not wraps:
            continue
        styled = text
        for o, c in wraps:
            styled = f"{o}{styled}{c}"
        # wrap the first un-styled occurrence of this exact cell text
        pat = re.compile(r"(<t[hd][^>]*>)" + re.escape(text) + r"(</t[hd]>)")
        out, n = pat.subn(lambda m: m.group(1) + styled + m.group(2), out, count=1)
    return out


def _squash(s: str) -> str:
    return re.sub(r"\s+", "", s)


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
            for j in range(i + 1, min(i + 3, len(col))):
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


def _row_band(plain, cand, tol=7.0):
    """Median y of the row's uniquely-matchable cells (usually the model
    name) — the anchor that ties HTML rows back to page geometry."""
    ys = [cand[p][0][1] for p in plain if p and len(cand.get(p, [])) == 1]
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
        plain = [_squash(re.sub(r"<[^>]+>", "", c)) for _, _, c in tags]
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
                    cells[i], cells[i + 1] = sq2text[k1], sq2text[joined[len(k1):]]
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
    # re-segmentation can only UN-glue: never fewer cells than docling
    # emitted (x-overlapping true columns fuse and are correctly rejected
    # here, e.g. the wide sentence-cell welfare tables)
    if len(cells2) < max(2, len(tags)):
        return None
    texts = []
    for _, _, members in cells2:
        members.sort(key=lambda s: (round(s["bbox"][1]), s["bbox"][0]))
        texts.append(inviz.sub("", " ".join(s["text"].strip() for s in members)).strip())
    have = sorted(inviz.sub("", "".join(plain)))
    want = sorted(_squash("".join(texts)))
    if have != want:
        return None
    tg = tags[0][0]
    return "<tr>" + "".join(f"<{tg}>{c}</{tg}>" for c in texts) + "</tr>"


def _extend_truncated_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes keeps only the FIRST line of a wrapped cell
    ('Claude Mythos' sans 'Preview', p.72). When a cell's text equals the top
    span of a stacked run whose continuation is claimed by no cell anywhere
    in the table, extend the cell to the run's full text."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s["text"].strip()]
    spans_xy = _row_spans_xy(oracle_page, bbox)
    # stacked runs keyed by top-span squash
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    runs: dict[str, list] = {}
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        for i in range(len(col) - 1):
            run = [col[i]]
            for j in range(i + 1, min(i + 3, len(col))):
                if col[j]["bbox"][1] - col[j - 1]["bbox"][3] >= 9:
                    break
                run.append(col[j])
            if len(run) > 1:
                runs.setdefault(_squash(run[0]["text"]), []).append(run)
    if not runs:
        return html
    all_cells = {_squash(re.sub(r"<[^>]+>", "", c))
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", html, re.S)}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_squash(re.sub(r"<[^>]+>", "", c)) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        cells = [c for _, _, c in tags]
        changed = False
        for i, p2 in enumerate(plain):
            cand = [run for run in runs.get(p2, [])
                    if band[0] <= (run[0]["bbox"][1] + run[0]["bbox"][3]) / 2 <= band[1]
                    and all(_squash(s["text"]) not in all_cells for s in run[1:])]
            if len(cand) != 1:
                continue
            cells[i] = " ".join(s["text"].strip() for s in cand[0])
            changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, cells)) + "</tr>"
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
        plain = [_squash(re.sub(r"<[^>]+>", "", c)) for _, _, c in tags]
        if any(not p for p in plain):
            continue
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        from collections import Counter
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
