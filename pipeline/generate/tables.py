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
            html = _repair_rotation(html, t["bbox"], oracle_page)
        out.append({**t, "html": html})
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
