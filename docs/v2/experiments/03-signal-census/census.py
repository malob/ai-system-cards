"""Document-wide visual-signal census: every fill color and text color in the
card, with counts, sample pages, and sample text. This enumerates the card's
entire visual vocabulary — the data a per-card style manifest is derived from
(D16), and the ground the S2/closure gate stands on.

Run from the repo root:
    uv run --with pymupdf python docs/v2/experiments/03-signal-census/census.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import fitz

CARD = Path("cards/anthropic/claude-fable-5")
OUT = Path(__file__).parent / "census.json"


def hexcolor_int(c: int) -> str:
    return f"#{c:06x}"


def hexcolor_tuple(t) -> str:
    return "#" + "".join(f"{int(round(v * 255)):02x}" for v in t)


def classify(r: fitz.Rect) -> str:
    if r.height <= 2.5 or r.width <= 2.5:
        return "rule"
    if 6 < r.height < 30 and 20 < r.width < 420:
        return "pill"
    return "box"


doc = fitz.open(CARD / "source.pdf")
fills = defaultdict(lambda: {"count": 0, "pages": set(), "kinds": Counter(), "samples": []})
textcolors = defaultdict(lambda: {"count": 0, "pages": set(), "samples": []})

for pno in range(len(doc)):
    page = doc[pno]
    for d in page.get_drawings():
        if d.get("fill") is None:
            continue
        col = hexcolor_tuple(d["fill"])
        kind = classify(d["rect"])
        e = fills[col]
        e["count"] += 1
        e["pages"].add(pno + 1)
        e["kinds"][kind] += 1
        if kind != "rule" and len(e["samples"]) < 3:
            t = page.get_text(clip=d["rect"]).strip().replace("\n", " ")[:48]
            if t and t not in e["samples"]:
                e["samples"].append(t)
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for line in blk["lines"]:
            for s in line["spans"]:
                if not s["text"].strip():
                    continue
                col = hexcolor_int(s["color"])
                e = textcolors[col]
                e["count"] += 1
                e["pages"].add(pno + 1)
                if len(e["samples"]) < 3 and s["text"].strip() not in e["samples"]:
                    e["samples"].append(s["text"].strip()[:48])


def pack(d):
    out = {}
    for col, e in sorted(d.items(), key=lambda kv: -kv[1]["count"]):
        pages = sorted(e["pages"])
        out[col] = {
            "count": e["count"],
            "n_pages": len(pages),
            "pages": pages[:12] + ([f"+{len(pages)-12} more"] if len(pages) > 12 else []),
            **({"kinds": dict(e["kinds"])} if "kinds" in e else {}),
            "samples": e["samples"],
        }
    return out


census = {"fills": pack(fills), "text_colors": pack(textcolors)}
OUT.write_text(json.dumps(census, indent=1, ensure_ascii=False))

print(f"fill colors: {len(census['fills'])}, text colors: {len(census['text_colors'])}\n")
print("=== fills (by count) ===")
for col, e in census["fills"].items():
    print(f"{col} ×{e['count']:<5} pages={e['n_pages']:<3} {e['kinds']} {e['samples'][:2]}")
print("\n=== text colors (by count) ===")
for col, e in census["text_colors"].items():
    print(f"{col} ×{e['count']:<6} pages={e['n_pages']:<3} {e['samples'][:2]}")
print(f"\nwrote {OUT}")
