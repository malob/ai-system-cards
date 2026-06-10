"""Move a page marker that begins a figure-led page to sit before that figure.

When a PDF page starts with a figure, its text lives inside the image and the
snap tool can't prose-match it, so the marker stays where the agent left it —
usually inside the figure's caption, below the charts. Figure filenames encode
their page (`p026-1.png` = first figure of page 26), so the correct anchor is
deterministic: the first figure of page N.

Self-limiting rule: only relocate a `<!-- p.N -->` marker that is currently
*trapped inside a figure block* — i.e. everything between the first figure
`pN-1.png` and the marker is blank lines, other `pN-*` figures, or caption
(italic) lines. This can never fire on a prose page, where prose would sit
between the figure and the marker.

Usage: python3 tools/anchor_figure_markers.py <card-dir> [--apply]
"""
import re
import sys
from pathlib import Path

CAPTION = re.compile(r"^\s*[*_]")  # italic/bold caption line
IMG = re.compile(r"^\s*!\[")


def process(card_dir, apply):
    moved = 0
    for f in sorted((card_dir / "sections").glob("*.md")):
        lines = f.read_text(encoding="utf-8").split("\n")
        # gather (page, marker_line_idx) for every marker
        edits = []
        for i, line in enumerate(lines):
            for m in re.finditer(r"<!-- p\.(\d+) -->", line):
                page = int(m.group(1))
                fig = f"p{page:03d}-1.png"
                img_idx = next((j for j, l in enumerate(lines) if fig in l and IMG.match(l)), None)
                if img_idx is None or img_idx >= i:
                    continue  # no first-figure image before this marker
                between = lines[img_idx + 1 : i]
                ok = all(
                    (not l.strip()) or IMG.match(l) or CAPTION.match(l) for l in between
                )
                if ok:
                    edits.append((page, i, img_idx, m.group(0)))
        if not edits:
            continue
        # apply bottom-up: strip marker from its line, insert standalone before figure
        for page, i, img_idx, marker in sorted(edits, key=lambda e: e[1], reverse=True):
            print(f"  ANCHOR {f.name} p.{page}: caption/figure-block -> before figure (line {img_idx + 1})")
            lines[i] = re.sub(r"\s*" + re.escape(marker) + r"\s?", "", lines[i], count=1)
            lines.insert(img_idx, marker)
            lines.insert(img_idx + 1, "")
            moved += 1
        if apply:
            f.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {moved} figure-led markers anchored")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    process(Path(args[0]), "--apply" in sys.argv)
