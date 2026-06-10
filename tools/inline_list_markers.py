"""Inline page markers that sit between list items so the list stays intact.

A column-0 `<!-- p.N -->` between two list items is parsed as an HTML block and
splits one list into two `<ul>`/`<ol>`s, adding a visible gap. When the marker
falls at the start of a list item (the page begins on that item), move it inline
right after the item's `- ` / `1. ` prefix; the list then renders as one.

Only fires when the previous content is also list content (item or indented
continuation) — i.e. the marker genuinely sits *inside* a list.

Usage: python3 tools/inline_list_markers.py <card-dir> [--apply]
"""
import re
import sys
from pathlib import Path

MARKER = re.compile(r"^<!-- p\.(\d+) -->$")
ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")


def process(card_dir, apply):
    fixed = 0
    for f in sorted((card_dir / "sections").glob("*.md")):
        lines = f.read_text(encoding="utf-8").split("\n")
        edits = []
        for i, line in enumerate(lines):
            m = MARKER.match(line)
            if not m:
                continue
            p = i - 1
            while p >= 0 and not lines[p].strip():
                p -= 1
            q = i + 1
            while q < len(lines) and not lines[q].strip():
                q += 1
            if p < 0 or q >= len(lines):
                continue
            prev_list = bool(ITEM.match(lines[p])) or bool(re.match(r"^\s{2,}\S", lines[p]))
            nxt = ITEM.match(lines[q])
            if prev_list and nxt:
                edits.append((i, p, q, m.group(0), nxt.end()))
        for i, p, q, marker, prefix_end in sorted(edits, key=lambda e: e[0], reverse=True):
            print(f"  INLINE {f.name} {marker}: between list items -> into next item")
            lines[q] = lines[q][:prefix_end] + marker + lines[q][prefix_end:]
            # remove the blank lines between the items so the list stays tight
            # (a single blank line would make the whole list render "loose")
            del lines[p + 1 : q]
            fixed += 1
        if apply:
            f.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {fixed} list-splitting markers inlined")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    process(Path(args[0]), "--apply" in sys.argv)
