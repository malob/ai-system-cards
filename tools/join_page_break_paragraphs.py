"""Rejoin paragraphs that a transcription split at a page break.

Agents sometimes treat a paragraph that straddles a PDF page boundary as two
paragraphs, leaving a block page-marker between the halves. This detects those
cases — a column-0 `<!-- p.N -->` whose surrounding prose continues mid-sentence
across the break — and merges them into one paragraph with the marker inline.

Three independent signals must agree, to avoid merging genuinely separate
paragraphs (or list/blocklist entries):
  1. the markdown line before the marker ends without terminal punctuation,
  2. the markdown line after starts as a continuation (lowercase / open paren),
  3. the PDF text layer shows page N-1 ending mid-sentence too.
Both fragments must be multi-word (excludes domain blocklists etc.).

Usage: python3 tools/join_page_break_paragraphs.py <card-dir> [--apply]
"""
import re
import sys
import unicodedata
from pathlib import Path

MARKER = re.compile(r"^<!-- p\.(\d+) -->$")
FOOTER = re.compile(r"^\s*\d{1,3}\s*$")
TERMINAL = (".", "!", "?", ":", ";", '"', "”", "’", ")", "_", "*", "]")
# block-level line starts: heading, list item (marker + space), blockquote,
# table, directive fence, image, raw HTML. NOT `**bold**` prose leads.
IS_BLOCK = re.compile(r"^\s*(#{1,6} |([-*+]|\d+[.)]) |> |\||:::|!\[|<)")
# a continuation can begin lowercase, with a digit, or an opening quote/bracket
CONT_START = re.compile(r"[a-z0-9(“‘\"'\[]")


def last_content_line(page_text):
    for l in reversed(page_text.splitlines()):
        if l.strip() and not FOOTER.match(l):
            return l.strip()
    return ""


def process(card_dir, apply):
    pages = (card_dir / "extracted" / "text-raw.txt").read_text(encoding="utf-8").split("\f")
    joined = 0
    for f in sorted((card_dir / "sections").glob("*.md")):
        lines = f.read_text(encoding="utf-8").split("\n")
        # collect join sites (marker index, prev index, next index) bottom-up
        sites = []
        for i, line in enumerate(lines):
            m = MARKER.match(line)
            if not m:
                continue
            page = int(m.group(1))
            p = i - 1
            while p >= 0 and not lines[p].strip():
                p -= 1
            q = i + 1
            while q < len(lines) and not lines[q].strip():
                q += 1
            if p < 0 or q >= len(lines):
                continue
            prev, nxt = lines[p].rstrip(), lines[q].lstrip()
            if IS_BLOCK.match(lines[p]) or IS_BLOCK.match(lines[q]):
                continue
            if " " not in prev or " " not in nxt:  # not prose (e.g. blocklist)
                continue
            if prev.endswith(TERMINAL) or not CONT_START.match(nxt):
                continue
            if page < 2 or page > len(pages):
                continue
            if last_content_line(pages[page - 2]).endswith(TERMINAL):
                continue  # PDF says page N-1 ended a sentence -> not a split
            sites.append((i, p, q, page))
        for i, p, q, page in sorted(sites, reverse=True):
            print(f"  JOIN {f.name} p.{page}: ...{lines[p].rstrip()[-30:]!r} <> {lines[q].lstrip()[:30]!r}...")
            lines[p] = lines[p].rstrip() + f"<!-- p.{page} --> " + lines[q].lstrip()
            del lines[p + 1 : q + 1]
            joined += 1
        if apply:
            f.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {joined} paragraphs rejoined")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    process(Path(args[0]), "--apply" in sys.argv)
