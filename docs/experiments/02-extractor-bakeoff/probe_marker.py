"""Bake-off part 3, challenger: marker on the hard-table pages.

Same shape as probe_docling.py: build a mini PDF, convert, dump markdown, report
table structure stats. First run downloads marker's models (~GBs) from HF.

Run from the repo root:
    uv run --with marker-pdf --with pymupdf python docs/experiments/02-extractor-bakeoff/probe_marker.py 95 98 252 309 310 311
"""

import re
import sys
import tempfile
from pathlib import Path

import fitz

CARD = Path("cards/anthropic/claude-fable-5")
HERE = Path(__file__).parent
PAGES = [int(a) for a in sys.argv[1:]] or [19, 20, 40, 42, 74, 100]
SUFFIX = f"-p{PAGES[0]}-{PAGES[-1]}"

mini_path = Path(tempfile.mkdtemp()) / "probe-pages.pdf"
src = fitz.open(CARD / "source.pdf")
mini = fitz.open()
for p in PAGES:
    mini.insert_pdf(src, from_page=p - 1, to_page=p - 1)
mini.save(mini_path)
print(f"mini PDF: {mini_path} ({len(PAGES)} pages: {PAGES})")

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

rendered = PdfConverter(artifact_dict=create_model_dict())(str(mini_path))
text, _, images = text_from_rendered(rendered)

out_md = HERE / f"probe-marker-output{SUFFIX}.md"
out_md.write_text(text)
print(f"markdown export: {len(text)} chars -> {out_md.name}")
print(f"images extracted: {len(images)}")

html_tables = len(re.findall(r"<table", text))
pipe_headers = len(re.findall(r"^\|[-| :]+\|$", text, re.M))
print(f"tables: {html_tables} html, {pipe_headers} pipe")
print(f"rowspan attrs: {len(re.findall(r'rowspan', text))}, colspan attrs: {len(re.findall(r'colspan', text))}")
