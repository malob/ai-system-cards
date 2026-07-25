"""Which card the pipeline targets (the D35 generalization seam).

Select with the CARD environment variable (vendor/slug):

    CARD=anthropic/claude-opus-5 uv run --with pymupdf python pipeline/generate/run.py --all

Default: anthropic/claude-fable-5 (the first card — the verifier's calibration
corpus lives at that card's git refs, D5, so it stays the reference target).

Per-document constants come from the card's own committed files:
- meta.yaml            `source_pages` — physical page count;
- style-manifest.yaml  `document: toc_pages` — the PDF's own contents pages
  (excluded from conversion; the site builds its own TOC).

Caches (oracle facts, docling tables, generated-page lists) are per-card
under pipeline/.cache/<vendor>-<slug>/ — gitignored, regenerable.
"""

import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CARD_ID = os.environ.get("CARD", "anthropic/claude-fable-5").strip().strip("/")
CARD = REPO / "cards" / CARD_ID
if not CARD.is_dir():
    raise SystemExit(f"cardcfg: no such card directory: {CARD}")


def _source_pages() -> int:
    m = re.search(r"^source_pages:\s*(\d+)", (CARD / "meta.yaml").read_text(), re.M)
    if not m:
        raise SystemExit(f"cardcfg: {CARD_ID}/meta.yaml lacks `source_pages:`")
    return int(m.group(1))


def _toc_pages() -> set[int]:
    mtext = (CARD / "style-manifest.yaml").read_text()
    m = re.search(r"^\s*toc_pages:\s*\[([^\]]*)\]", mtext, re.M)
    return {int(x) for x in m.group(1).split(",") if x.strip()} if m else set()


SOURCE_PAGES = _source_pages()
TOC_PAGES = _toc_pages()
# pages the conversion covers and P1 expects markers for: everything except
# the cover (p.1, declared exclusion) and the PDF's own contents listing
EXPECTED_PAGES = [p for p in range(2, SOURCE_PAGES + 1) if p not in TOC_PAGES]

SECTIONS = CARD / "sections"
CACHE = REPO / "pipeline/.cache" / CARD_ID.replace("/", "-")
ORACLE_CACHE = CACHE / "oracle.json"
TABLES_CACHE = CACHE / "tables.json"
