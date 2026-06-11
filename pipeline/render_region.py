"""High-zoom region renders for vision inspection (round G).

Full pages are capped by the vision API's ~1.15MP downscale, so sharper
full-page renders gain nothing for agents. CROPS at high zoom land under
the ceiling and arrive glyph-sharp.

    uv run --with pymupdf python pipeline/render_region.py PAGE [x0 y0 x1 y1] [ZOOM]
    (no bbox = every docling-table bbox on the page; default zoom 5)

Output: pipeline/.cache/crops/p{page}-{x0}x{y0}.png — regenerable, uncommitted.
"""
import json
import sys
from pathlib import Path

import fitz

REPO = Path(__file__).resolve().parents[1]
PDF = REPO / "cards/anthropic/claude-fable-5/source.pdf"
OUT = REPO / "pipeline/.cache/crops"


def render(page_no: int, bbox, zoom: float = 5.0) -> Path:
    doc = fitz.open(PDF)
    page = doc[page_no - 1]
    clip = fitz.Rect(*bbox) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"p{page_no}-{int(bbox[0])}x{int(bbox[1])}.png"
    pix.save(out)
    return out


if __name__ == "__main__":
    pno = int(sys.argv[1])
    if len(sys.argv) >= 6:
        bbox = [float(v) for v in sys.argv[2:6]]
        zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0
        print(render(pno, bbox, zoom))
    else:
        tables = json.loads((REPO / "pipeline/.cache/tables.json").read_text())
        for t in tables.get(str(pno), []):
            b = t["bbox"]
            pad = [b[0] - 6, b[1] - 6, b[2] + 6, b[3] + 6]
            print(render(pno, pad))
