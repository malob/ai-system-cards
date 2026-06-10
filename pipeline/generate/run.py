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


def first_headings() -> dict:
    """section name -> squashed first-heading text from v1's files. Used to
    split SHARED boundary pages (v1 ranges overlap: 02a ends and 02b begins on
    p.36): content before the incoming section's heading belongs to the
    previous section."""
    import norm
    out = {}
    for p in sorted((CARD / "sections").glob("*.md")):
        for line in p.read_text().splitlines():
            if line.startswith("#"):
                out[p.name] = norm.squash(line.lstrip("# "))[:40]
                break
    return out


def heading_index(blocks: list, head_key: str):
    import norm
    for i, blk in enumerate(blocks):
        if blk["type"] == "heading":
            t = norm.squash(" ".join(l["text"] for l in blk["lines"]))
            if t.startswith(head_key[:24]) or head_key.startswith(t[:24]):
                return i
    return None


def manifest_chips() -> dict:
    mtext = (CARD / "style-manifest.yaml").read_text()
    block = re.search(r"^chips:\n((?:  .+\n)+)", mtext, re.M)
    return {m.group(2): m.group(1).strip()
            for m in re.finditer(r"^  (.+?):\s+\"(#[0-9a-f]{6})\"", block.group(1), re.M)}


UNTERMINATED = tuple(".!?:”\"’")
TR = re.compile(r"<tr>.*?</tr>", re.S)


def _tbl_rows(html):
    return TR.findall(html)


def _row_squash(row):
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "|", row))


def _merge_tables(prev_html: str, next_html: str, next_page: int = 0) -> str | None:
    """Merge two adjacent-page docling fragments of one logical table: same
    column count, repeated header rows dropped (p.20-21, p.252-253, the
    nine-page appendix table)."""
    r1, r2 = _tbl_rows(prev_html), _tbl_rows(next_html)
    if not r1 or not r2:
        return None
    ncols = lambda r: len(re.findall(r"<t[hd]", r))
    if ncols(r2[0]) != ncols(r1[0]) and ncols(r2[0]) != ncols(r1[-1]):
        return None
    # drop fragment-2 header rows that repeat fragment-1's
    i = 0
    while i < len(r2) and i < len(r1) and _row_squash(r2[i]) == _row_squash(r1[i]):
        i += 1
    body = "".join(r2[i:])
    if body and next_page:
        # the page marker rides INSIDE the merged table between fragments
        # (v1's convention; renderer turns it into an anchor)
        body = f"<!-- p.{next_page} -->" + body
    if not body:
        return prev_html
    if "</tbody>" in prev_html:
        return prev_html.replace("</tbody>", body + "</tbody>", 1)
    return prev_html.replace("</table>", body + "</table>", 1)


def join_quote_blocks(md: str) -> str:
    """Adjacent quote blocks separated by a blank line render as SEPARATE
    blockquotes in markdown (owner-flagged on the METR quote, §2.3.8); a bare
    '>' on the separator keeps them one quote. A standalone page marker
    between quote blocks (quote spans a page break, §2.3.8/§3.3.1) moves
    INSIDE the quote as '> <!-- p.N -->'."""
    lines = md.split("\n")
    # pass 1: markers sandwiched between quote lines become quoted markers
    def neighbor(idx, step):
        j = idx + step
        while 0 <= j < len(lines) and lines[j] == "":
            j += step
        return lines[j] if 0 <= j < len(lines) else ""
    for i, l in enumerate(lines):
        if (re.fullmatch(r"<!-- p\.\d+ -->", l.strip())
                and neighbor(i, -1).startswith(">") and neighbor(i, 1).startswith(">")):
            lines[i] = "> " + l.strip()
    # pass 2: blank separators between quote lines become '>'
    out = []
    for i, l in enumerate(lines):
        if (l == "" and out and out[-1].startswith(">")
                and i + 1 < len(lines) and lines[i + 1].startswith(">")):
            out.append(">")
        else:
            out.append(l)
    return "\n".join(out)


def stitch(blocks: list[dict]) -> list[dict]:
    """Merge blocks split across a page break (v1's PM-02/03 lessons):
    - paragraph + paragraph: previous unterminated, next starts lowercase;
    - item + paragraph: next page's first block is the hanging-indent
      continuation of a wrapped list item.
    Records page_break = (page, line_index) so the serializer can splice the
    page marker inline at the exact break point."""
    out = []
    for blk in blocks:
        # adjacent-page table fragments merge into one logical table
        if (out and blk["type"] == "table_html" and out[-1]["type"] == "table_html"
                and blk["page"] == out[-1].get("last_page", out[-1]["page"]) + 1):
            merged = _merge_tables(out[-1]["html"], blk["html"], blk["page"])
            if merged is not None:
                out[-1]["html"] = tables.merge_continuation_rows(merged)
                out[-1]["last_page"] = blk["page"]  # chain across many pages
                continue
        if (out and blk["page"] == out[-1]["page"] + 1 and blk["type"] == "paragraph"
                and out[-1]["type"] in ("paragraph", "item")):
            prev = out[-1]
            prev_text = prev["lines"][-1]["text"].rstrip()
            nxt_line = blk["lines"][0]
            nxt = nxt_line["text"].lstrip()
            joinable = prev_text and prev_text[-1] not in UNTERMINATED
            if prev["type"] == "paragraph" and joinable and nxt[:1].islower():
                prev["page_break"] = (blk["page"], len(prev["lines"]))
                prev["lines"].extend(blk["lines"])
                continue
            if (prev["type"] == "item" and joinable
                    and nxt_line["bbox"][0] > prev.get("marker_x0", 0) + 6):
                prev["page_break"] = (blk["page"], len(prev["lines"]))
                prev["lines"].extend(blk["lines"])
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

    # exclusive page→section assignment: v1 section ranges overlap by one page
    # at each boundary (…-036 / 036-…), so a page goes to the LAST section whose
    # start ≤ it (that's where its content belongs). Prevents duplicate markers.
    ranges = section_ranges()
    starts = sorted((a, name) for name, a, b in ranges)
    owner = {}
    for name, a, b in ranges:
        for p in range(a, b + 1):
            best = max((s for s, _ in starts if s <= p), default=a)
            owner[p] = next(n for s, n in starts if s == best)

    firsts = first_headings()
    shared = {a for _, a, _ in ranges} & {b for _, _, b in ranges}

    heading_anchors = []  # (page, y, slug) in document order
    num2slug: dict[str, str] = {}  # '8.17.6' -> its heading slug

    def slugify(text):
        s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
        return re.sub(r"[\s]+", "-", s)

    written = []
    for si, (name, a, b) in enumerate(ranges):
        sel = [p for p in range(a, b + 1) if p in want and p not in TOC and owner.get(p) == name]
        if not sel:
            continue
        blocks = []
        start_midpage = False
        for pno in sel:
            pblocks = assemble.assemble_page(pno, pages[pno - 1], figures_map.get(str(pno), []),
                                             chips, tables.get_tables(pno, pages[pno - 1]))
            if pno == a and pno in shared:
                # shared start page: this section's content begins at its heading
                i = heading_index(pblocks, firsts.get(name, ""))
                if i:
                    pblocks = pblocks[i:]
                    start_midpage = True
            blocks += pblocks
        # shared END page (owned by the next section): the pre-heading slice
        # belongs HERE, so the boundary paragraph can stitch across pages
        if si + 1 < len(ranges) and ranges[si + 1][1] == b and b in want and b not in TOC \
                and owner.get(b) != name:
            pblocks = assemble.assemble_page(b, pages[b - 1], figures_map.get(str(b), []),
                                             chips, tables.get_tables(b, pages[b - 1]))
            i = heading_index(pblocks, firsts.get(ranges[si + 1][0], ""))
            if i:
                blocks += pblocks[:i]
        # footnote blocks live at page ends and would break cross-page
        # stitching adjacency (the p.19-20 split); they serialize at section
        # end regardless, so lift them out before stitching
        for bl in blocks:
            if bl["type"] == "heading":
                htext = " ".join(l["text"] for l in bl["lines"]).strip()
                heading_anchors.append((bl["page"],
                                        bl["lines"][0]["bbox"][1],
                                        slugify(htext)))
                mnum = re.match(r"(\d+(?:\.\d+)*)[.\s]", htext + " ")
                if mnum:
                    num2slug.setdefault(mnum.group(1), slugify(htext))
        fn_blocks = [bl for bl in blocks if bl["type"] == "footnote"]
        blocks = stitch([bl for bl in blocks if bl["type"] != "footnote"]) + fn_blocks
        # a mid-page start suppresses the leading page marker (the previous
        # section already carries it — v1's shared-page convention, P1-checked)
        md, _ = serialize.serialize_blocks(blocks, page_of_prev_block=(a if start_midpage else -1),
                                           oracle_pages=pages, chips=chips)
        md = join_quote_blocks(md)
        (OUT / name).write_text(f"<!-- source: source.pdf pages {a:03d}-{b:03d} -->\n\n{md}")
        written.append((name, sel))
        print(f"{name}: pages {sel[0]}..{sel[-1]} ({len(sel)} pages, {len(blocks)} blocks)")
    # L2: resolve DEST:N placeholders to the first heading anchor on page N,
    # else the nearest heading before it (v1's apply_internal_links logic)
    def anchor_for(n, y=-1):
        on_page = [(hy, s) for pg, hy, s in heading_anchors if pg == n]
        if on_page:
            if y >= 0:
                # the dest y lands AT the target heading or anywhere inside
                # its section (sloppy PDF dests point mid-section): the
                # OWNING heading is the last one at-or-above y(+8); a dest
                # above every heading takes the first one below
                own = [s for hy, s in on_page if hy <= y + 8]
                if own:
                    return own[-1]
                return on_page[0][1]
            return on_page[0][1]
        before = [s for pg, hy, s in heading_anchors if pg <= n]
        return before[-1] if before else ""
    def resolve_link(m):
        text, pg, y = m.group(1), int(m.group(2)), int(m.group(3))
        # anchors that NAME their target ('Section 8.17.6') resolve exactly
        # by heading number — the PDF's dest coordinates are sloppy in both
        # directions (13/28 landed on a neighboring section by geometry)
        mnum = re.search(r"(?:Section|§)\s*(\d+(?:\.\d+)*)", text)
        if mnum and mnum.group(1).rstrip(".") in num2slug:
            return f"[{text}](#{num2slug[mnum.group(1).rstrip('.')]})"
        return f"[{text}](#{anchor_for(pg, y)})"
    for name, _ in written:
        f = OUT / name
        md = f.read_text()
        md = re.sub(r"\[([^\]]*)\]\(DEST:(\d+):(-?\d+)\)", resolve_link, md)
        md = re.sub(r"\(DEST:0(?::-?\d+)?\)", "(#)", md)
        f.write_text(md)

    all_pages = sorted({p for _, sel in written for p in sel})
    (REPO / "pipeline/.cache/genpages.json").write_text(json.dumps(all_pages))
    print(f"\nwrote {len(written)} files to {OUT}")
    print("gate with:")
    names = " ".join(sorted({n.split('-')[0] for n, _ in written}))
    print(f"  uv run --with pymupdf python pipeline/verifier/calibrate.py {OUT} --sections {names}")


if __name__ == "__main__":
    main()
