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


def _repair_rotation(html: str, bbox: list, oracle_page: dict) -> str:
    """Verify each body cell's column against its span x-position; if rows
    share a consistent non-identity column permutation, invert it."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if len(rows) < 3:
        return html
    # oracle spans inside the table bbox, keyed by squashed text -> x-centers
    spans_x: dict[str, list[float]] = {}
    for s in oracle_page["spans"]:
        sb = s["bbox"]
        if (bbox[0] - 3 <= sb[0] and sb[2] <= bbox[2] + 3
                and bbox[1] - 3 <= sb[1] and sb[3] <= bbox[3] + 3):
            spans_x.setdefault(_squash(s["text"]), []).append((sb[0] + sb[2]) / 2)

    # per-row repair: each row is reordered by ITS OWN measured x-permutation
    # (docling rotated only data rows on 4.4.2.A — the header was correct, so a
    # majority-global permutation would corrupt it)
    out = html
    for r in rows:
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        if len(tags) < 2 or any("colspan" in a or "rowspan" in a for _, a, _ in tags):
            continue
        plain = [_squash(re.sub(r"<[^>]+>", "", c)) for _, _, c in tags]
        xs = [spans_x.get(p, [None])[0] for p in plain]
        if any(x is None for x in xs) or len(set(xs)) != len(xs):
            continue
        perm = tuple(sorted(range(len(xs)), key=lambda i: xs[i]))
        if perm == tuple(range(len(xs))):
            continue
        inner = [tags[i][2] for i in perm]
        rebuilt = "<tr>" + "".join(
            f"<{t}{a}>{c}</{t}>" for (t, a, _), c in zip(tags, inner)) + "</tr>"
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
