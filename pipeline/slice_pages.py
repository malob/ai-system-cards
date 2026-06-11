"""Per-page markdown slices for the vision sweep: each p-NNN.md holds every
markdown run attributed to PDF page N, concatenated across sections in
document order (a boundary page contributes from two sections).

    python3 pipeline/slice_pages.py OUTDIR [PAGE ...]
    (no pages = all)

Attribution: a section header comment `<!-- source: source.pdf pages A-B -->`
sets the section's first page A; from there, every `<!-- p.N -->` marker
(standalone or inline) advances the current page. Text between markers
belongs to the page in force where it appears.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SECTIONS = REPO / "cards/anthropic/claude-fable-5/sections"
MARK = re.compile(r"<!-- p\.(\d+) -->")
HEADER = re.compile(r"<!-- source: \S+ pages (\d+)-(\d+) -->")


def slices() -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for f in sorted(SECTIONS.glob("*.md")):
        text = f.read_text()
        m = HEADER.search(text)
        cur = int(m.group(1)) if m else 1
        pos = 0
        for mk in MARK.finditer(text):
            # snap to line start: an inline marker mid-item ('- <!-- p.N -->x')
            # otherwise strands the '- ' prefix in the previous page's slice
            ls = text.rfind("\n", 0, mk.start()) + 1
            pre = text[ls:mk.start()]
            # snap only when the pre-marker prefix is a short list marker;
            # a marker inside a long single-line table must split mid-line
            # or pages 310-317 of the one-line welfare table get no slice
            cut = ls if (pre.strip() and len(pre) <= 8) else mk.start()
            chunk = text[pos:cut]
            if chunk.strip():
                out.setdefault(cur, []).append(chunk)
            cur = int(mk.group(1))
            pos = cut if cut == ls else mk.end()
        chunk = text[pos:]
        if chunk.strip():
            out.setdefault(cur, []).append(chunk)
    return out


if __name__ == "__main__":
    outdir = Path(sys.argv[1])
    want = {int(a) for a in sys.argv[2:]} or None
    outdir.mkdir(parents=True, exist_ok=True)
    by_page = slices()
    n = 0
    for pno, chunks in sorted(by_page.items()):
        if want and pno not in want:
            continue
        (outdir / f"p-{pno:03d}.md").write_text("\n".join(c.strip("\n") for c in chunks) + "\n")
        n += 1
    print(f"{n} slices -> {outdir}")
