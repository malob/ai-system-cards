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


def get_tables(page_no: int) -> list[dict]:
    """[{bbox:[x0,y0,x1,y1] top-left, html}] for a page (cached). Empty if uncached."""
    return _load().get(str(page_no), [])


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
