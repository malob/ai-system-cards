"""Enumerate v1's hand-built HTML tables and rank by hardness (rowspan/colspan,
size, multi-page span) to pick part-3 probe pages.

Run from the repo root:  python3 docs/v2/experiments/02-extractor-bakeoff/find_hard_tables.py
"""

import re
from pathlib import Path

SECTIONS = sorted(Path("cards/anthropic/claude-fable-5/sections").glob("*.md"))

rows = []
for f in SECTIONS:
    text = f.read_text()
    for m in re.finditer(r"<table.*?</table>", text, re.S):
        t = m.group(0)
        before = text[: m.start()]
        pages_before = re.findall(r"<!-- p\.(\d+) -->", before)
        page = int(pages_before[-1]) if pages_before else None
        inside = re.findall(r"<!-- p\.(\d+) -->", t)
        rows.append(
            {
                "file": f.name,
                "page": page,
                "tr": len(re.findall(r"<tr", t)),
                "rowspan": len(re.findall(r"rowspan", t)),
                "colspan": len(re.findall(r"colspan", t)),
                "pages_inside": [int(p) for p in inside],
                "chars": len(t),
            }
        )

rows.sort(key=lambda r: (len(r["pages_inside"]), r["rowspan"] + r["colspan"], r["tr"]), reverse=True)
print(f"{len(rows)} HTML tables in v1 sections; hardest first:\n")
for r in rows[:15]:
    multi = f" MULTI-PAGE{r['pages_inside']}" if r["pages_inside"] else ""
    print(
        f"p.{r['page']:<4} {r['file']:<38} tr={r['tr']:<3} "
        f"rowspan={r['rowspan']:<2} colspan={r['colspan']:<2} {r['chars']}ch{multi}"
    )

# markdown pipe tables, for completeness
md_tables = 0
for f in SECTIONS:
    md_tables += len(re.findall(r"^\|.*\|\n\|[-| :]+\|", f.read_text(), re.M))
print(f"\n(plus {md_tables} markdown pipe tables)")
