"""v2 conversion driver: pages → sections-v2/*.md → verifier gates.

    uv run --with pymupdf python pipeline/generate/run.py --pages 3 26
    uv run --with pymupdf python pipeline/generate/run.py --seed
    uv run --with pymupdf python pipeline/generate/run.py --all

Section file boundaries mirror v1's (same names + page ranges), so the
verifier and site consume the output unchanged.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[0] / "verifier"))
sys.path.insert(0, str(HERE))

import assemble  # noqa: E402
import oracle  # noqa: E402
import serialize  # noqa: E402
import tables  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "cards/anthropic/claude-fable-5"
OUT = CARD / "sections-v2"
SEED = [3, 19, 20, 26, 39, 40, 41, 42, 43, 44, 74, 95, 100, 107, 118, 139,
        235, 236, 252, 253, 309, 310, 311, 318, 319]
TOC = set(range(4, 11))


def section_ranges() -> list[tuple[str, int, int]]:
    out = []
    for p in sorted((CARD / "sections").glob("*.md")):
        m = re.search(r"pages (\d+)-(\d+)", p.read_text()[:200])
        if m:
            out.append((p.name, int(m.group(1)), int(m.group(2))))
    return out


def manifest_chips() -> dict:
    mtext = (CARD / "style-manifest.yaml").read_text()
    block = re.search(r"^chips:\n((?:  .+\n)+)", mtext, re.M)
    return {m.group(2): m.group(1).strip()
            for m in re.finditer(r"^  (.+?):\s+\"(#[0-9a-f]{6})\"", block.group(1), re.M)}


def stitch(blocks: list[dict]) -> list[dict]:
    """Merge a paragraph split across a page break: previous page ends with an
    unterminated paragraph and the next begins lowercase (v1 join heuristic)."""
    out = []
    for blk in blocks:
        if (out and blk["type"] == "paragraph" and out[-1]["type"] == "paragraph"
                and blk["page"] == out[-1]["page"] + 1):
            prev_text = out[-1]["lines"][-1]["text"].rstrip()
            nxt = blk["lines"][0]["text"].lstrip()
            if prev_text and prev_text[-1] not in ".!?:”\"’" and nxt[:1].islower():
                out[-1]["lines"].extend(blk["lines"])
                out[-1]["break_page"] = blk["page"]
                continue
        out.append(blk)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", nargs="*", type=int)
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    want = set(args.pages or (SEED if args.seed else [])) or (
        set(range(2, 320)) - TOC if args.all else set()
    )
    if not want:
        ap.error("give --pages, --seed, or --all")

    pages = oracle.extract(CARD / "source.pdf", cache=REPO / "pipeline/.cache/oracle.json")
    figures_map = json.loads((CARD / "extracted/figures-map.json").read_text())
    chips = manifest_chips()
    OUT.mkdir(exist_ok=True)

    written = []
    for name, a, b in section_ranges():
        sel = [p for p in range(a, b + 1) if p in want and p not in TOC]
        if not sel:
            continue
        blocks = []
        for pno in sel:
            blocks += assemble.assemble_page(pno, pages[pno - 1], figures_map.get(str(pno), []),
                                             chips, tables.get_tables(pno))
        blocks = stitch(blocks)
        md, _ = serialize.serialize_blocks(blocks, page_of_prev_block=-1, oracle_pages=pages, chips=chips)
        (OUT / name).write_text(f"<!-- source: source.pdf pages {a:03d}-{b:03d} -->\n\n{md}")
        written.append((name, sel))
        print(f"{name}: pages {sel[0]}..{sel[-1]} ({len(sel)} pages, {len(blocks)} blocks)")
    print(f"\nwrote {len(written)} files to {OUT}")
    print("gate with:")
    names = " ".join(sorted({n.split('-')[0] for n, _ in written}))
    print(f"  uv run --with pymupdf python pipeline/verifier/calibrate.py {OUT} --sections {names}")


if __name__ == "__main__":
    main()
