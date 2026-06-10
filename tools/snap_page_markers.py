"""Snap page markers to their exact page-break position using the PDF text layer.

Each `<!-- p.N -->` marker should sit at the precise point where PDF page N
begins. The pdftotext output (pages split by form-feed) gives the ground-truth
first words of every page; we find that text in the markdown near the existing
marker and relocate the marker there — inline at a word boundary when the break
falls mid-block, on its own line when the page starts a fresh block.

Usage:
    python3 tools/snap_page_markers.py <card-dir> [--apply]

Without --apply it is a dry run: prints proposed moves and a validation summary
but writes nothing. Markers whose page-start text cannot be confidently located
near their current position are left untouched and reported.
"""
import re
import sys
import unicodedata
from pathlib import Path

WORD_RE = re.compile(r"[a-z0-9]+")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MARKER_RE = re.compile(r"<!--\s*p\.(\d+)\s*-->")
ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")
FOOTER_RE = re.compile(r"^\s*\d{1,3}\s*$")
FINGERPRINT_WORDS = 8
SEARCH_WINDOW = 2500  # chars either side of the current marker


def norm_words(s):
    s = unicodedata.normalize("NFKD", s)
    return WORD_RE.findall(s.lower())


def page_fingerprints(raw_text):
    """page number -> list of normalized first words of that page."""
    pages = raw_text.split("\f")
    fps = {}
    for idx, pg in enumerate(pages):
        n = idx + 1
        words = []
        for line in pg.splitlines():
            if not line.strip() or FOOTER_RE.match(line):
                continue
            words.extend(norm_words(line))
            if len(words) >= FINGERPRINT_WORDS:
                break
        if words:
            fps[n] = words[:FINGERPRINT_WORDS]
    return fps


def tokenize(text):
    """(word, start_offset) for each word, with HTML comments blanked out so a
    marker's own 'p N' tokens never match."""
    blanked = COMMENT_RE.sub(lambda m: " " * len(m.group(0)), text)
    return [(m.group(0).lower(), m.start()) for m in WORD_RE.finditer(blanked.lower())]


def find_offset(tokens, fingerprint, near_offset):
    """Offset of the best contiguous match of `fingerprint` in `tokens`,
    preferring matches closest to `near_offset`. Returns None if not found."""
    fp = fingerprint
    n = len(fp)
    if n < 4:
        return None  # too short to disambiguate
    best = None
    for i in range(len(tokens) - n + 1):
        if tokens[i][0] != fp[0]:
            continue
        if [t[0] for t in tokens[i : i + n]] == fp:
            off = tokens[i][1]
            if abs(off - near_offset) <= SEARCH_WINDOW:
                if best is None or abs(off - near_offset) < abs(best - near_offset):
                    best = off
    return best


def placement(text, offset, page):
    """Return (delete_start, insert_text) for placing the marker so page-text
    begins at `offset`, choosing inline vs block to avoid breaking lists."""
    marker = f"<!-- p.{page} -->"
    # back up over whitespace immediately before the page-start word
    j = offset
    while j > 0 and text[j - 1] in " \t":
        j -= 1
    if j > 0 and text[j - 1] != "\n":
        # mid-block: inline marker right after the previous word
        return j, marker + " "
    # page starts at the beginning of a line
    line_end = text.find("\n", offset)
    line = text[offset : line_end if line_end != -1 else len(text)]
    m = ITEM_RE.match(line)
    if m:
        # list item: inline right after the "- " / "1. " prefix
        return offset + m.end(), marker
    # heading or paragraph start: standalone marker line before the block
    return j, marker + "\n\n"


def after_matches(text, marker_end, fp):
    """True if the fingerprint words appear immediately after `marker_end`."""
    after = norm_words(COMMENT_RE.sub(" ", text[marker_end : marker_end + 260]))
    return after[: len(fp)] == fp


def process(card_dir, apply):
    raw = (card_dir / "extracted" / "text-raw.txt").read_text(encoding="utf-8")
    fps = page_fingerprints(raw)
    moved = already = left = 0
    for f in sorted((card_dir / "sections").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        edits = []  # (old_start, old_end, insert_offset, insert_text, page)
        for mk in MARKER_RE.finditer(text):
            page = int(mk.group(1))
            fp = fps.get(page)
            if not fp:
                left += 1
                continue
            # already at the exact boundary?
            if after_matches(text, mk.end(), fp):
                already += 1
                continue
            tokens = tokenize(text)
            target = find_offset(tokens, fp, mk.start())
            if target is None:
                print(f"  LEAVE {f.name} p.{page}: boundary not locatable (structural page start)")
                left += 1
                continue
            ins_off, ins_text = placement(text, target, page)
            # simulate the move and require the page's first words to land
            # right after the new marker; otherwise don't touch it
            sim = text[:ins_off] + ins_text + text[ins_off:]
            new_end = ins_off + ins_text.index("-->") + 3
            if not after_matches(sim, new_end, fp):
                print(f"  LEAVE {f.name} p.{page}: move did not validate")
                left += 1
                continue
            edits.append((mk.start(), mk.end(), ins_off, ins_text, page))
        if not edits:
            continue
        edits.sort(key=lambda e: e[0], reverse=True)
        new = text
        for old_s, old_e, ins_off, ins_text, page in edits:
            ds, de = old_s, old_e
            while de < len(new) and new[de] in " \t":
                de += 1
            if de < len(new) and new[de] == "\n" and ds > 0 and new[ds - 1] == "\n":
                de += 1  # swallow one trailing newline of a former block marker
            if ins_off > old_s:
                new = new[:ins_off] + ins_text + new[ins_off:]
                new = new[:ds] + new[de:]
            else:
                new = new[:ds] + new[de:]
                new = new[:ins_off] + ins_text + new[ins_off:]
            moved += 1
        if apply:
            f.write_text(new, encoding="utf-8")

    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {moved} moved (validated), "
          f"{already} already exact, {left} left alone")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    process(Path(args[0]), apply)
