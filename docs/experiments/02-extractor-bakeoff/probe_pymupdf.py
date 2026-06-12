"""Feasibility probe: can PyMuPDF surface the oracle signals the verification
contract's gates need? (S1 bold/italic runs, S2 chip signals, L1 URI+GoTo links,
FN1 superscripts, F1 image bboxes, TB1 table structure.)

Run from the repo root:
    uv run --with pymupdf python docs/experiments/02-extractor-bakeoff/probe_pymupdf.py

Writes probe-summary.json next to this script and prints a human-readable report.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF

CARD = Path("cards/anthropic/claude-fable-5")
OUT = Path(__file__).parent / "probe-summary.json"

# Probe pages (1-based), chosen in experiment 02 README. Signal under test:
PROBE_PAGES = {
    3: "plain prose + bold leads (PM-01 example page)",
    19: "merged-cell table (rowspan)",
    20: "merged-cell table continuation",
    26: "figures + bold-lead captions (FL-04)",
    39: "smart chips list (FL-02)",
    40: "chips + transcript turns (FL-03)",
    41: "chips + transcript turns",
    42: "chips + transcript turns",
    74: "chart-heavy page (4 figure images)",
    100: "cross-reference dense (23 GoTo links expected)",
    101: "cross-reference dense (26 GoTo links expected)",
}

BOLD, ITALIC, SUPERSCRIPT = 16, 2, 1


def hexcolor(c: int) -> str:
    return f"#{c:06x}"


def span_runs(page):
    """All text spans with style facts."""
    runs = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                if not s["text"].strip():
                    continue
                runs.append(
                    {
                        "text": s["text"],
                        "font": s["font"],
                        "size": round(s["size"], 1),
                        "bold": bool(s["flags"] & BOLD) or "Bold" in s["font"],
                        "italic": bool(s["flags"] & ITALIC) or "Italic" in s["font"],
                        "superscript": bool(s["flags"] & SUPERSCRIPT),
                        "color": hexcolor(s["color"]),
                        "bbox": [round(v, 1) for v in s["bbox"]],
                    }
                )
    return runs


def link_facts(page):
    links = {"uri": [], "goto": [], "other": []}
    for l in page.get_links():
        anchor = page.get_text(clip=fitz.Rect(l["from"])).strip().replace("\n", " ")
        if l["kind"] == fitz.LINK_URI:
            links["uri"].append({"anchor": anchor, "uri": l["uri"]})
        elif l["kind"] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
            links["goto"].append({"anchor": anchor, "dest_page": l.get("page", -1) + 1})
        else:
            links["other"].append({"anchor": anchor, "kind": l["kind"]})
    return links


def drawing_fills(page):
    """Filled vector rects — candidate chip-pill backgrounds, panel boxes, rules."""
    fills = Counter()
    rects = []
    for d in page.get_drawings():
        if d.get("fill") is None:
            continue
        col = "#" + "".join(f"{int(round(c * 255)):02x}" for c in d["fill"])
        r = d["rect"]
        fills[col] += 1
        # pill-sized boxes only (heuristic: shortish, not page-wide)
        if 6 < r.height < 30 and 20 < r.width < 400:
            rects.append({"color": col, "bbox": [round(v, 1) for v in r]})
    return fills, rects


def text_in(page, bbox):
    return page.get_text(clip=fitz.Rect(bbox)).strip().replace("\n", " ")


def table_facts(page):
    out = []
    for t in page.find_tables().tables:
        grid = t.extract()
        ncells = sum(1 for row in grid for c in row)
        nempty = sum(1 for row in grid for c in row if c in (None, ""))
        out.append(
            {
                "rows": t.row_count,
                "cols": t.col_count,
                "empty_cells": f"{nempty}/{ncells}",
                "first_row": [str(c)[:28] if c else c for c in grid[0]],
            }
        )
    return out


def main():
    doc = fitz.open(CARD / "source.pdf")
    expected_goto = {
        int(k): len(v)
        for k, v in json.loads((CARD / "extracted/internal-links.json").read_text()).items()
    }

    summary = {}
    for pno, why in PROBE_PAGES.items():
        page = doc[pno - 1]
        runs = span_runs(page)
        links = link_facts(page)
        fills, pill_rects = drawing_fills(page)
        body = Counter(r["color"] for r in runs).most_common(1)[0][0]
        colored = [r for r in runs if r["color"] != body]
        pills = [
            {"color": p["color"], "text": text_in(page, p["bbox"])}
            for p in pill_rects
            if text_in(page, p["bbox"])
        ]

        summary[pno] = {
            "why": why,
            "spans": len(runs),
            "body_color": body,
            "colored_spans": [
                {"text": r["text"][:40], "color": r["color"]} for r in colored[:12]
            ],
            "bold_samples": [r["text"][:48] for r in runs if r["bold"]][:8],
            "italic_count": sum(r["italic"] for r in runs),
            "superscript_samples": [r["text"] for r in runs if r["superscript"]][:10],
            "links": {
                "uri": len(links["uri"]),
                "goto": len(links["goto"]),
                "goto_expected": expected_goto.get(pno, 0),
                "goto_samples": links["goto"][:5],
            },
            "images": len(page.get_images(full=True)),
            "filled_rects_by_color": dict(fills.most_common(8)),
            "pill_candidates": pills[:12],
            "tables": table_facts(page),
        }

        s = summary[pno]
        print(f"\n=== p.{pno} — {why} ===")
        print(
            f"spans={s['spans']} bold={len(s['bold_samples'])}(+) italics={s['italic_count']} "
            f"super={len(s['superscript_samples'])} images={s['images']}"
        )
        print(
            f"links: uri={s['links']['uri']} goto={s['links']['goto']} "
            f"(expected goto={s['links']['goto_expected']})"
        )
        if s["colored_spans"]:
            print("colored spans:", s["colored_spans"][:6])
        if s["pill_candidates"]:
            print("pill candidates:", s["pill_candidates"][:6])
        if s["superscript_samples"]:
            print("superscripts:", s["superscript_samples"])
        if s["tables"]:
            print("tables:", s["tables"])

    OUT.write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
