"""Bake-off part 2, candidate 1: docling on the TB1/T2 probe pages.

Builds a mini PDF of the probe pages from source.pdf, converts with docling, and
reports: table structure (merged cells = row_span/col_span > 1), false-positive
tables on transcript pages, and the markdown export for reading-order inspection.

Run from the repo root (first run downloads docling's layout/table models):
    uv run --with docling --with pymupdf python docs/v2/experiments/02-extractor-bakeoff/probe_docling.py
"""

import tempfile
from pathlib import Path

import fitz

CARD = Path("cards/anthropic/claude-fable-5")
HERE = Path(__file__).parent
# mini-PDF page i (1-based) = source page PAGES[i-1]
PAGES = [19, 20, 40, 42, 74, 100]  # tables / transcript FP check / charts / links

mini_path = Path(tempfile.mkdtemp()) / "probe-pages.pdf"
src = fitz.open(CARD / "source.pdf")
mini = fitz.open()
for p in PAGES:
    mini.insert_pdf(src, from_page=p - 1, to_page=p - 1)
mini.save(mini_path)
print(f"mini PDF: {mini_path} ({len(PAGES)} pages: {PAGES})")

import docling
from docling.document_converter import DocumentConverter

print(f"docling version: {getattr(docling, '__version__', 'unknown')}")
result = DocumentConverter().convert(mini_path)
doc = result.document

md = doc.export_to_markdown()
(HERE / "probe-docling-output.md").write_text(md)
print(f"markdown export: {len(md)} chars -> probe-docling-output.md")

print(f"\ntables found: {len(doc.tables)}")
for i, t in enumerate(doc.tables):
    page_no = None
    try:
        page_no = PAGES[t.prov[0].page_no - 1]
    except Exception:
        pass
    try:
        d = t.data
        merged = [
            f"r{c.start_row_offset_idx}c{c.start_col_offset_idx} "
            f"spans {c.row_span}x{c.col_span}: {c.text[:30]!r}"
            for row in d.grid
            for c in row
            if (c.row_span > 1 or c.col_span > 1)
        ]
        # grid repeats spanned cells; dedupe
        merged = sorted(set(merged))
        print(
            f"  [{i}] source p.{page_no}: {d.num_rows}x{d.num_cols}, "
            f"merged cells: {merged if merged else 'none'}"
        )
    except Exception as e:
        print(f"  [{i}] source p.{page_no}: structure introspection failed: {e}")
        try:
            print(t.export_to_markdown(doc)[:400])
        except Exception:
            pass
