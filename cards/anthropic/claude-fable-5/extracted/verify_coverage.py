"""Independent coverage sweep: check page-marker continuity and that each PDF
page's distinctive sentences appear in the stitched markdown."""
import re
import unicodedata
from pathlib import Path

SECTIONS = sorted(Path("sections").glob("*.md"))
raw_pages = Path("extracted/text-raw.txt").read_text().split("\f")

md_all = "\n".join(p.read_text() for p in SECTIONS)
# strip markdown link targets, HTML tags, and image lines so mid-sentence
# markup does not break contiguous matching
md_all = re.sub(r"\]\([^)]*\)", "]", md_all)
md_all = re.sub(r"<[^>\n]+>", "", md_all)
md_all = re.sub(r"^!\[.*$", "", md_all, flags=re.M)
md_all = re.sub(r"https?://\S+", "", md_all)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("‑", "-").replace("–", "-").replace("—", "-")
    s = re.sub(r"[​‌﻿]", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s.lower())
    return s


md_norm = norm(md_all)

# 1. Page marker continuity
markers = set()
for p in SECTIONS:
    for m in re.finditer(r"<!--\s*p\.(\d+)\s*-->", p.read_text()):
        markers.add(int(m.group(1)))
    hdr = re.search(r"<!--\s*source: source\.pdf pages (\d+)-(\d+)\s*-->", p.read_text())
    if hdr:
        markers.add(int(hdr.group(1)))
markers.add(1)  # title page transcribed without numeric marker
expected = set(range(1, 320)) - set(range(4, 11))  # skip TOC pages 4-10
missing_markers = sorted(expected - markers)
print("pages missing a marker:", missing_markers if missing_markers else "NONE")

# 2. Distinctive-sentence presence per page
problems = []
for pno in sorted(expected):
    text = raw_pages[pno - 1]
    lines = [ln.strip() for ln in text.splitlines()]
    # drop bare page-number footers and short fragments
    cands = [ln for ln in lines if len(ln) > 60]
    cands.sort(key=len, reverse=True)
    misses = []
    for ln in cands[:3]:
        if norm(ln) not in md_norm:
            misses.append(ln)
    if misses:
        problems.append((pno, misses))

print("pages with unmatched distinctive lines:", len(problems))
for pno, misses in problems:
    print("--- p.%d" % pno)
    for ln in misses:
        print("   ", ln[:110])
