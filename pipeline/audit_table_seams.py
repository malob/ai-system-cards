"""Seam auditor for merged tables: flags paragraph-structure damage that the
text gates can't see (T1 excludes tables).

    python3 pipeline/audit_table_seams.py

Checks every <table> in sections-v2:
- S1: bare text directly followed by a block <p> inside a cell (mixed
  flat/block — renders a spurious line break);
- S2: a paragraph boundary '</p><p>' where the next paragraph starts
  lowercase/'(' (suspicious mid-sentence break);
- S3: a cell's last paragraph ending without terminal punctuation while the
  NEXT ROW's same column starts lowercase (unmerged continuation row).
"""
import re
import sys
from pathlib import Path

SECTIONS = Path(__file__).resolve().parents[1] / "cards/anthropic/claude-fable-5/sections-v2"
flags = 0
for f in sorted(SECTIONS.glob("*.md")):
    text = f.read_text()
    for tbl in re.findall(r"<table>.*?</table>", text, re.S):
        rows = re.findall(r"<tr>.*?</tr>", tbl, re.S)
        grid = [re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S) for r in rows]
        for ri, cells in enumerate(grid):
            for ci, c in enumerate(cells):
                if "<p>" in c and re.match(r"\s*[^<\s]", c):
                    print(f"S1 {f.name} row{ri}: flat+block mix: {re.sub(r'<[^>]+>', '¶', c)[:90]!r}")
                    flags += 1
                for m in re.finditer(r"</p>\s*<p>\s*([a-z(‘’])", c):
                    ctx = re.sub(r"<[^>]+>", " ", c[max(0, m.start()-60):m.end()+60])
                    print(f"S2 {f.name} row{ri}c{ci}: mid-sentence <p> break: …{' '.join(ctx.split())}…")
                    flags += 1
                last = re.sub(r"<[^>]+>", "", c).strip()
                if (last and not re.search(r"[.!?:;…\"”')\]]$|^$", last)
                        and ri + 1 < len(grid) and ci < len(grid[ri + 1])):
                    nxt = re.sub(r"<[^>]+>", "", grid[ri + 1][ci]).strip()
                    if nxt and re.match(r"[a-z(‘’]", nxt):
                        print(f"S3 {f.name} row{ri}c{ci}: unmerged continuation: …{last[-50:]!r} -> {nxt[:40]!r}")
                        flags += 1
print(f"\n{flags} seam flag(s)")
sys.exit(1 if flags else 0)
