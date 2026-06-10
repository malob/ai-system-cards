"""Apply the PDF's internal cross-reference links to the markdown.

The first conversion captured only external (/URI) links; internal (/GoTo)
links were dropped. extract_internal_links.py recovers them as
{source-page -> [{text, dest_page}]}. This tool:

  1. builds an ordered heading map (page, anchor-id) by pairing markdown
     headings with the authoritative ids from the rendered HTML,
  2. resolves each link's destination page to the nearest section anchor,
  3. merges multi-line link fragments, fuzzy-matches the anchor phrase back
     into the markdown near its source page, and wraps it as [text](#id).

Never alters text — only wraps existing spans in link syntax. Skips spans that
already contain link/marker/directive syntax.

Usage: python3 tools/apply_internal_links.py <card-dir> [--apply] [--pages a,b,c]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

WORD = re.compile(r"[a-z0-9]+")
PAGE_MARK = re.compile(r"<!--\s*p\.(\d+)\s*-->")
HEADING = re.compile(r"^(#{2,6})\s+(.*)$")
SRC_HDR = re.compile(r"<!--\s*source: source\.pdf pages (\d+)-(\d+)\s*-->")


def norm(s):
    return WORD.findall(unicodedata.normalize("NFKD", s).lower())


def build_heading_pages(card_dir):
    """Ordered [(page, heading_text)] across all section files."""
    out = []
    for f in sorted((card_dir / "sections").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = SRC_HDR.search(text)
        page = int(m.group(1)) if m else 1
        for line in text.split("\n"):
            pm = PAGE_MARK.search(line)
            if pm:
                page = int(pm.group(1))
            h = HEADING.match(line)
            if h:
                out.append((page, h.group(2)))
    return out


def heading_anchor_map(card_dir):
    """page -> anchor-id list, built by zipping markdown headings (for pages)
    with the rendered HTML's heading ids (authoritative slugs)."""
    html = (card_dir / ".." / ".." / ".." / "site" / "dist" / "anthropic" / card_dir.name / "index.html")
    ids = re.findall(r'<h[2-6][^>]*\bid="([^"]+)"', html.read_text(encoding="utf-8"))
    ids = [i for i in ids if i != "footnote-label"]  # rehype back-matter, not a content heading
    headings = build_heading_pages(card_dir)
    if len(ids) != len(headings):
        print(f"WARN: {len(ids)} html content ids vs {len(headings)} md headings — anchor map may be misaligned")
    # ordered (page, id)
    return [(pg, hid) for (pg, _), hid in zip(headings, ids)]


def resolve_anchor(dest_page, ordered):
    """nearest heading anchor at or before dest_page (last in doc order)."""
    best = None
    for pg, hid in ordered:
        if pg <= dest_page:
            best = hid
        else:
            break
    return best


def tokenize(text):
    """(word, start, end) over markdown with comments blanked (preserve offsets)."""
    blanked = re.sub(r"<!--.*?-->", lambda m: " " * len(m.group(0)), text, flags=re.S)
    return [(m.group(0).lower(), m.start(), m.end()) for m in WORD.finditer(blanked.lower())]


def find_span(tokens, phrase, near, window=4000):
    """char (start,end) of the best contiguous match of phrase tokens, nearest `near`."""
    n = len(phrase)
    if n == 0:
        return None
    best = None
    for i in range(len(tokens) - n + 1):
        if tokens[i][0] != phrase[0]:
            continue
        if [t[0] for t in tokens[i : i + n]] == phrase:
            s, e = tokens[i][1], tokens[i + n - 1][2]
            if abs(s - near) <= window and (best is None or abs(s - near) < abs(best[0] - near)):
                best = (s, e)
    return best


def process(card_dir, apply, only_pages):
    links = json.loads((card_dir / "extracted" / "internal-links.json").read_text())
    ordered = heading_anchor_map(card_dir)

    # which file + offset hosts each source page's marker
    files = {}
    for f in sorted((card_dir / "sections").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        hdr = SRC_HDR.search(text)
        rng = range(int(hdr.group(1)), int(hdr.group(2)) + 1) if hdr else range(0)
        files[f] = {
            "text": text,
            "range": rng,
            "marks": {int(m.group(1)): m.start() for m in PAGE_MARK.finditer(text)},
            "toks": tokenize(text),
        }

    edits = {}  # file -> list of (start, end, anchor) wraps
    stats = {"matched": 0, "nomatch": 0, "skip": 0}
    for spage, frags in sorted(links.items(), key=lambda kv: int(kv[0])):
        sp = int(spage)
        if only_pages and sp not in only_pages:
            continue
        # group consecutive same-dest fragments (a multi-line link)
        groups = []
        for fr in frags:
            if groups and groups[-1]["dest_page"] == fr["dest_page"]:
                groups[-1]["parts"].append(fr["text"])
            else:
                groups.append({"dest_page": fr["dest_page"], "parts": [fr["text"]]})
        # candidate host files (a boundary page can live in two files)
        candidates = [f for f, d in files.items() if sp in d["range"]]
        if not candidates:
            continue

        def try_wrap(text, anchor):
            """Try to wrap `text` in any candidate file. Returns 'matched',
            'skip' (handled but not wrapped), or 'nomatch'."""
            for host in candidates:
                d = files[host]
                near = d["marks"].get(sp, 0)
                span = find_span(d["toks"], norm(text), near)
                if not span:
                    continue
                s, e = span
                sub = d["text"][s:e]
                already = d["text"][s - 1 : s] == "[" and d["text"][e : e + 2] == "]("
                if already or re.search(r"\]\(|\[\^|<!--|\n", sub):
                    if not already:
                        print(f"  SKIP (markup in span) p{sp}: {sub[:50]!r}")
                    return "skip"
                edits.setdefault(host, []).append((s, e, anchor))
                print(f"  LINK p{sp}->#{anchor}: {sub[:55]!r}")
                return "matched"
            return "nomatch"

        for g in groups:
            if not g["dest_page"]:
                stats["skip"] += 1
                continue
            anchor = resolve_anchor(g["dest_page"], ordered)
            if not anchor:
                stats["skip"] += 1
                continue
            # whole multi-line phrase first; fall back to per-fragment
            r = try_wrap(" ".join(g["parts"]), anchor)
            if r == "nomatch":
                results = [try_wrap(p, anchor) for p in g["parts"]]
                r = "matched" if all(x != "nomatch" for x in results) else "nomatch"
            if r == "matched":
                stats["matched"] += 1
            elif r == "skip":
                stats["skip"] += 1
            else:
                stats["nomatch"] += 1
                print(f"  NOMATCH p{sp}->p{g['dest_page']}: {' '.join(g['parts'])[:60]!r}")

    # apply per file, rear-to-front, skipping overlaps
    for host, ed in edits.items():
        ed.sort(key=lambda x: x[0], reverse=True)
        text = files[host]["text"]
        last_start = len(text) + 1
        for s, e, anchor in ed:
            if e > last_start:  # overlaps a later (already-applied) link
                continue
            text = text[:s] + f"[{text[s:e]}](#{anchor})" + text[e:]
            last_start = s
        if apply:
            host.write_text(text, encoding="utf-8")

    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {stats['matched']} linked, "
          f"{stats['nomatch']} unmatched, {stats['skip']} skipped")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pg_arg = next((a for a in sys.argv if a.startswith("--pages=")), None)
    only = set(int(x) for x in pg_arg.split("=")[1].split(",")) if pg_arg else None
    process(Path(args[0]), "--apply" in sys.argv, only)
