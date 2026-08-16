"""v2 conversion driver: pages → sections/*.md → verifier gates.

    uv run --with pymupdf python pipeline/generate/run.py --pages 3 26
    uv run --with pymupdf python pipeline/generate/run.py --seed
    uv run --with pymupdf python pipeline/generate/run.py --all

Section file boundaries mirror v1's (same names + page ranges), so the
verifier and site consume the output unchanged.
"""

import argparse
import hashlib
import json
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[0] / "verifier"))
sys.path.insert(0, str(HERE.parents[0]))
sys.path.insert(0, str(HERE))

import assemble  # noqa: E402
import cardcfg  # noqa: E402
import oracle  # noqa: E402
import serialize  # noqa: E402
import tables  # noqa: E402

REPO = cardcfg.REPO
CARD = cardcfg.CARD
OUT = CARD / "sections"
# first card's calibration seed pages (only meaningful with --seed there)
SEED = [3, 19, 20, 26, 39, 40, 41, 42, 43, 44, 74, 95, 100, 107, 118, 139,
        235, 236, 252, 253, 309, 310, 311, 318, 319]
TOC = cardcfg.TOC_PAGES

DEST_MARKDOWN_RE = re.compile(r"\[([^\]]*)\]\(DEST:(\d+):(-?\d+)\)")
DEST_HTML_RE = re.compile(
    r'<a href="DEST:(\d+):(-?\d+)">(.*?)</a>', re.S)


class DestinationResolutionError(ValueError):
    """A PDF destination could not be represented by a truthful web link."""


def resolve_destination_placeholders(
        md: str, *, anchor_for, text_resolution, pooled: dict) -> str:
    """Resolve internal PDF destinations without manufacturing ``href="#"``.

    Page zero is the sentinel for a broken named destination. Its visible text
    is retained as prose unless that text independently identifies one unique
    heading. For real page destinations, absence of any heading is an
    invariant failure: writing an empty fragment would create a misleading
    jump to the top of the document. Any placeholder missed by the deliberately
    narrow Markdown/HTML parsers also fails closed before the section is
    written.
    """
    def resolve_link(match):
        text, pg_text, y_text = match.group(1), match.group(2), match.group(3)
        pg, y = int(pg_text), int(y_text)
        # The pool only serves SHORT fragments of a wrapped link; a full
        # anchor phrase keeps its own geometry (p.121).
        pooled_hit = (pooled.get((pg_text, y_text))
                      if len(text.split()) <= 2 else None)
        explicit = text_resolution(text) or pooled_hit
        if pg == 0 and not explicit:
            return text
        slug = explicit or anchor_for(pg, y)
        if not slug:
            raise DestinationResolutionError(
                f"destination page {pg} has no heading anchor for {text!r}")
        return f"[{text}](#{slug})"

    def resolve_html(match):
        # Goto links injected into table HTML carry the same placeholder as
        # body links, so they follow exactly the same resolution policy.
        pg_text, y_text, text = match.group(1), match.group(2), match.group(3)
        pg, y = int(pg_text), int(y_text)
        plain = re.sub(r"<[^>]+>", "", text)
        pooled_hit = (pooled.get((pg_text, y_text))
                      if len(plain.split()) <= 2 else None)
        explicit = text_resolution(plain) or pooled_hit
        if pg == 0 and not explicit:
            return text
        slug = explicit or anchor_for(pg, y)
        if not slug:
            raise DestinationResolutionError(
                f"destination page {pg} has no heading anchor for {plain!r}")
        return f'<a href="#{slug}">{text}</a>'

    resolved = DEST_MARKDOWN_RE.sub(resolve_link, md)
    resolved = DEST_HTML_RE.sub(resolve_html, resolved)
    if "DEST:" in resolved:
        at = resolved.index("DEST:")
        context = resolved[max(0, at - 40):at + 80].replace("\n", "\\n")
        raise DestinationResolutionError(
            f"unresolved destination placeholder remains near {context!r}")
    return resolved


def verifier_command(*, full: bool, section_prefixes: list[str]) -> str:
    """Shell-safe verifier handoff for this process's generated scope.

    A full generation must run the complete release graph, including every
    card's source artifacts and the final rendered-DOM/asset audit. Partial
    generation is diagnostic and keeps the selected-card absolute-directory +
    prefix form, which intentionally disables document-wide release checks.
    """
    if full:
        command = [
            "uv", "run", "--python", "3.12", "--with", "pymupdf==1.28.2",
            "python", "pipeline/verify_release.py",
        ]
        return shlex.join(command)

    command = [
        "env", f"CARD={cardcfg.CARD_ID}", "uv", "run", "--python", "3.12",
        "--with", "pymupdf==1.28.2", "python",
        "pipeline/verifier/calibrate.py", str(OUT), "--sections",
        *section_prefixes,
    ]
    return shlex.join(command)


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
                out[p.name] = norm.squash(
                    line.lstrip("# "), calibration=True)[:40]
                break
    return out


def heading_index(blocks: list, head_key: str):
    import norm
    for i, blk in enumerate(blocks):
        if blk["type"] == "heading":
            t = norm.squash(
                " ".join(l["text"] for l in blk["lines"]), calibration=True)
            if t.startswith(head_key[:24]) or head_key.startswith(t[:24]):
                return i
    return None


def manifest_chips() -> dict:
    mtext = (CARD / "style-manifest.yaml").read_text()
    block = re.search(r"^chips:\n((?:  .+\n)+)", mtext, re.M)
    if not block:   # a card with no smart-chip vocabulary (e.g. claude-opus-5)
        return {}
    return {m.group(2): m.group(1).strip()
            for m in re.finditer(r"^  (.+?):\s+\"(#[0-9a-f]{6})\"", block.group(1), re.M)}


UNTERMINATED = tuple(".!?:”\"’")

# per-card grammar knob (D16): merge a bubble that continues across a page
# cut into ONE bubble. Both conventions exist in this family and both draw
# box borders at the cut, so geometry can't discriminate: the risk report
# sets one box around many paragraphs (§2.24 spans pp.84-86 — owner-flagged
# when split), while fable's pilot quotes are box-PER-PARAGRAPH (its p.102
# continuation paragraph sits in its own closed box mid-page) and must stay
# separate bubbles.
BUBBLE_CONT = bool(re.search(
    r"^\s*bubble_page_continuation:\s*true",
    (cardcfg.CARD / "style-manifest.yaml").read_text(), re.M))
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
    # normalize fragment rows to the host's dominant shape: docling gives
    # the continuation fragment PLAIN first cells where the host's body rows
    # carry a label colspan ('8.1.A ARC-AGI-2/3', p.149 — every data cell
    # shifted one column left in the render)
    def _eff_w(row):
        return sum(int(m.group(1)) if m else 1
                   for m in (re.search(r'colspan="(\d+)"', tag)
                             for tag in re.findall(r"<t[hd][^>]*>", row)))
    from collections import Counter as _Counter
    host_shapes = _Counter()
    for hr in r1[1:]:
        mfc = re.search(r"<t[hd][^>]*?colspan=\"(\d+)\"", hr.split("</t", 1)[0])
        host_shapes[(_eff_w(hr), int(mfc.group(1)) if mfc else 1)] += 1
    if host_shapes:
        (host_w, host_c), _n = host_shapes.most_common(1)[0]
        if host_c > 1:
            fixed = []
            pending_rowspan = 0   # rows still covered by an earlier rowspan
            for r in r2[i:]:
                if (pending_rowspan == 0 and _eff_w(r) == host_w - (host_c - 1)
                        and "colspan" not in r and "rowspan" not in r):
                    r = re.sub(r"(<t[hd])(?=[ >])", rf'\1 colspan="{host_c}"', r, count=1)
                elif pending_rowspan:
                    # a rowspan-continuation row is SUPPOSED to be one cell
                    # short (fable 'Harvey's Held-Out Set') — leave it alone
                    pending_rowspan -= 1
                mrs = re.search(r'rowspan="(\d+)"', r)
                if mrs:
                    pending_rowspan = max(pending_rowspan, int(mrs.group(1)) - 1)
                fixed.append(r)
            r2[i:] = fixed
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


def _dedupe_figures(page: dict, figs: list[str]) -> tuple[dict, list[str]]:
    """The PDF sometimes draws ONE image twice into overlapping space (p.139
    xref 828): the reader sees one figure, extraction yields two identical
    files + two overlapping rects. Drop a figure whose rect overlaps an
    earlier one (>0.8 of the smaller area) AND whose file bytes match."""
    rects = page.get("image_rects", [])
    if len(figs) < 2 or len(rects) < 2:
        return page, figs
    def md5(f):
        p = CARD / "assets/figures" / f
        return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else f
    keep_r, keep_f = [], []
    for r, f in zip(rects, figs):
        dup = False
        for r2, f2 in zip(keep_r, keep_f):
            ix = max(0, min(r[2], r2[2]) - max(r[0], r2[0])) * \
                 max(0, min(r[3], r2[3]) - max(r[1], r2[1]))
            amin = min((r[2] - r[0]) * (r[3] - r[1]),
                       (r2[2] - r2[0]) * (r2[3] - r2[1]))
            if amin > 0 and ix / amin > 0.8 and md5(f) == md5(f2):
                dup = True
                break
        if not dup:
            keep_r.append(r)
            keep_f.append(f)
    keep_r += rects[len(figs):]   # index-aligned prefixes; keep any tail
    keep_f += figs[len(rects):]
    if len(keep_f) == len(figs):
        return page, figs
    return {**page, "image_rects": keep_r}, keep_f


def _wrap_fit(prev: dict, nxt_text: str) -> bool:
    """Ragged-right wrap test: the continuation's first word would NOT have
    fit in the outgoing line's right slack, so that line break is a wrap,
    not a paragraph end (slack varies with word length — a fixed threshold
    misses long-word wraps). Char width comes from the outgoing line itself.
    Multi-line blocks only: a lone short line (a bold lead label) never
    qualifies."""
    ls = prev["lines"]
    if len(ls) < 2 or not ls[-1]["text"].strip():
        return False
    last = ls[-1]
    cw = (last["bbox"][2] - last["bbox"][0]) / max(len(last["text"]), 1)
    slack = max(l["bbox"][2] for l in ls) - last["bbox"][2]
    word = (nxt_text.split() or [""])[0]
    return slack < (len(word) + 1) * cw


def stitch(blocks: list[dict]) -> list[dict]:
    """Merge blocks split across a page break (v1's PM-02/03 lessons):
    - paragraph + paragraph: previous unterminated, next starts lowercase —
      or, when the outgoing line is a full-width wrap (or ends ','/';'), ANY
      continuation: proper nouns, acronyms, digits and open quotes defeated
      the lowercase test on nine real seams (round G);
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
                # bullet breaks re-run AFTER the seam join: a cross-page
                # bullet arrives with the continuation chunk and the merged
                # cell's third '●' had no <br> (p.113→114)
                out[-1]["html"] = tables._bullet_breaks(
                    tables.merge_continuation_rows(merged))
                out[-1]["last_page"] = blk["page"]  # chain across many pages
                out[-1].setdefault("parts", []).extend(blk.get("parts", []))
                continue
        if (out and blk["page"] == out[-1]["page"] + 1 and blk["type"] == "code"
                and out[-1]["type"] == "code"):
            # one logical code block split by the page break (9.2 blocklist):
            # merge; the marker re-emits after the fence (a comment inside a
            # fence would render literally)
            out[-1]["lines"].extend(blk["lines"])
            out[-1].setdefault("trailing_pages", []).append(blk["page"])
            continue
        if (out and blk["page"] == out[-1]["page"] + 1
                and blk["type"] in ("example", "code")
                and out[-1]["type"] == "turn" and out[-1].get("code_lines")
                and not out[-1].get("code_cont")
                and out[-1]["code_lines"][-1]["bbox"][3] >= 680
                and blk["lines"][0]["bbox"][1] <= 120):
            # a labeled turn's code box continues on the next page as a bare
            # box (no label -> classified example/code): the p.107 puzzle box
            # ran to the page bottom and resumed at the next page's top
            out[-1]["code_cont"] = {"page": blk["page"], "lines": blk["lines"]}
            continue
        if (out and blk["page"] == out[-1]["page"] + 1 and blk["type"] == "turn"
                and out[-1]["type"] == "turn"
                and out[-1].get("role") == blk.get("role")
                and not blk.get("code_lines") and not out[-1].get("code_lines")):
            prev = out[-1]
            prev_text = prev["lines"][-1]["text"].rstrip()
            nxt = blk["lines"][0]["text"].lstrip()
            if prev_text and prev_text[-1] not in UNTERMINATED and (
                    nxt[:1].islower() or prev_text[-1] in ",;" or _wrap_fit(prev, nxt)):
                off = len(prev["lines"])
                prev["page_break"] = (blk["page"], off)
                prev["lines"].extend(blk["lines"])
                if blk.get("breaks"):
                    prev.setdefault("breaks", []).extend(i + off for i in blk["breaks"])
                continue
        if (BUBBLE_CONT and out and blk["type"] == "turn" and out[-1]["type"] == "turn"
                and blk["page"] == out[-1].get("last_page", out[-1]["page"]) + 1
                and out[-1].get("role") == blk.get("role")
                and out[-1].get("fill") and out[-1].get("fill") == blk.get("fill")
                and not blk.get("code_lines") and not out[-1].get("code_lines")
                and out[-1].get("last_container", out[-1].get("container"))
                and blk.get("container")
                and out[-1].get("last_container", out[-1]["container"])[3] >= 670
                and blk["container"][1] <= 120
                and blk.get("lines") and not assemble._label_lead(blk["lines"][0])):
            # the SAME physical box continuing across the page break — the
            # §2.24 prompt box spans pp.84-86, one bubble in the PDF but
            # split into per-page bubbles here (the p.86 fragment even got
            # its bold lead promoted to a label). The text tests above
            # rightly refuse a SENTENCE splice; the geometry (same fill, box
            # to the bottom margin, resuming at the top) proves the bubble.
            # Merge with a paragraph break at the seam; the serializer
            # emits the page marker inline and uses each segment's own
            # page facts (the p.86 placeholder pill).
            prev = out[-1]
            off = len(prev["lines"])
            prev.setdefault("page_breaks_multi", []).append((blk["page"], off))
            prev.setdefault("breaks", []).append(off)
            prev["lines"].extend(blk["lines"])
            if blk.get("breaks"):
                prev["breaks"] = sorted(set(prev["breaks"])
                                        | {i + off for i in blk["breaks"]})
            prev["last_page"] = blk["page"]          # chain 3+-page bubbles
            prev["last_container"] = blk["container"]
            continue
        if (out and blk["page"] == out[-1]["page"] + 1 and blk["type"] == "paragraph"
                and out[-1]["type"] == "caption"
                and blk["lines"][0].get("size", 11) <= 9.5):
            # caption wrapped across the page break: the continuation has no
            # bracket lead and no figure region, so it classified as a body
            # paragraph — but caption-size lines betray it (6.5.2.B class)
            prev = out[-1]
            prev_text = prev["lines"][-1]["text"].rstrip()
            nxt = blk["lines"][0]["text"].lstrip()
            if prev_text and prev_text[-1] not in UNTERMINATED and (
                    nxt[:1].islower() or prev_text[-1] in ",;" or _wrap_fit(prev, nxt)):
                prev["page_break"] = (blk["page"], len(prev["lines"]))
                prev["lines"].extend(blk["lines"])
                continue
        if (out and blk["page"] == out[-1]["page"] + 1 and blk["type"] == "paragraph"
                and out[-1]["type"] in ("paragraph", "item")):
            prev = out[-1]
            prev_text = prev["lines"][-1]["text"].rstrip()
            nxt_line = blk["lines"][0]
            nxt = nxt_line["text"].lstrip()
            joinable = prev_text and prev_text[-1] not in UNTERMINATED
            if prev["type"] == "paragraph" and joinable and (
                    nxt[:1].islower()
                    or (prev.get("quote") == blk.get("quote")
                        and (prev_text[-1] in ",;" or _wrap_fit(prev, nxt)))):
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
        set(cardcfg.EXPECTED_PAGES) if args.all else set()
    )
    if not want:
        ap.error("give --pages, --seed, or --all")

    pages = oracle.extract(CARD / "source.pdf", cache=cardcfg.ORACLE_CACHE)
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
    claim2slug: dict[str, str] = {}  # '7' -> slug of the 'Claim 7: …' heading
    title2slug: dict[str, str | None] = {}  # squashed title -> slug (None = collision)

    def slugify(text):
        s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
        return re.sub(r"[\s]+", "-", s)

    written = []
    for si, (name, a, b) in enumerate(ranges):
        sel = [p for p in range(a, b + 1) if p in want and p not in TOC and owner.get(p) == name]
        if not sel:
            continue
        blocks = []
        qcarry = False
        start_midpage = False
        for pno in sel:
            pg, figs = _dedupe_figures(pages[pno - 1], figures_map.get(str(pno), []))
            pblocks = assemble.assemble_page(pno, pg, figs,
                                             chips, tables.get_tables(pno, pages[pno - 1]),
                                             quote_carry=qcarry)
            if pno == a and pno in shared:
                # shared start page: this section's content begins at its heading
                i = heading_index(pblocks, firsts.get(name, ""))
                if i:
                    pblocks = pblocks[i:]
                    start_midpage = True
            blocks += pblocks
            qcarry = next((b.get("quote", False) for b in reversed(pblocks)
                           if b["type"] in ("paragraph", "item")), qcarry)
        # shared END page (owned by the next section): the pre-heading slice
        # belongs HERE, so the boundary paragraph can stitch across pages
        if si + 1 < len(ranges) and ranges[si + 1][1] == b and b in want and b not in TOC \
                and owner.get(b) != name:
            pg, figs = _dedupe_figures(pages[b - 1], figures_map.get(str(b), []))
            pblocks = assemble.assemble_page(b, pg, figs,
                                             chips, tables.get_tables(b, pages[b - 1]),
                                             quote_carry=qcarry)
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
                # text-addressable headings: 'Claim N…:' leads (risk-report §2
                # links say '[Claim 7]' with dest coords that land on the
                # neighboring claim) and unique bare titles ('specific
                # pathways' → 2.2.1). Colliding titles poison their key.
                mc = re.search(r"\bClaim\s+(\d+(?:\.\d+)*):", htext)
                if mc:
                    claim2slug.setdefault(mc.group(1), slugify(htext))
                title = htext[min(mnum.end(), len(htext)):] if mnum else htext
                tkey = re.sub(r"[^a-z0-9]", "", title.lower())
                if tkey:
                    title2slug[tkey] = (None if tkey in title2slug
                                        else slugify(htext))
        # re-tier nested lists over the whole section: a page that holds only
        # sub-bullets (a list continued across a page break, UK AISI p.215→216)
        # tiered them to level 0 in isolation; the full block list has the
        # level-0 siblings from the previous page
        assemble.assign_list_levels(blocks)
        fn_blocks = [bl for bl in blocks if bl["type"] == "footnote"]
        blocks = stitch([bl for bl in blocks if bl["type"] != "footnote"]) + fn_blocks
        # in-cell bulleted lists are built on the COMPLETE logical table, so a
        # bullet split by a page break stays one <li> (owner-approved
        # 2026-08-15). Per-fragment construction produced two <ul>s with the
        # seam paragraph stranded between them.
        for bl in blocks:
            if bl["type"] == "table_html" and bl.get("parts"):
                ctx = tables._cell_align_ctx(
                    [(bx, pages[pg - 1]) for bx, pg in bl["parts"]])
                bl["html"] = tables._cell_lists(bl["html"], ctx)
        # a mid-page start suppresses the leading page marker (the previous
        # section already carries it — v1's shared-page convention, P1-checked)
        md, _ = serialize.serialize_blocks(blocks, page_of_prev_block=(a if start_midpage else -1),
                                           oracle_pages=pages, chips=chips)
        md = join_quote_blocks(md)
        # an inline highlight split ONLY by a page marker is one continuous
        # range — the PDF breaks it because the page physically ends, but the
        # web paragraph reflows, so the seam is an artifact (owner-flagged,
        # p.137→138). The marker anchor legally lives inside the span. The
        # nearest opener must itself be an hl span (a bare </span> could
        # close a ph pill — fusing those would restyle the pill's text).
        def _hl_seam(m):
            before = md_cur[: m.start()]
            opener = before.rfind("<span")
            if opener != -1 and before[opener:].startswith('<span class="hl">'):
                return m.group(1)
            return m.group(0)
        md_cur = md
        md = re.sub(r'</span>(\s*<!-- p\.\d+ -->\s*)<span class="hl">',
                    _hl_seam, md)
        (OUT / name).write_text(f"<!-- source: source.pdf pages {a:03d}-{b:03d} -->\n\n{md}")
        written.append((name, sel))
        print(f"{name}: pages {sel[0]}..{sel[-1]} ({len(sel)} pages, {len(blocks)} blocks)")
    # L2: resolve DEST:N placeholders to the first heading anchor on page N,
    # else the nearest heading before it (v1's apply_internal_links logic)
    def anchor_for(n, y=-1):
        on_page = sorted((hy, s) for pg, hy, s in heading_anchors if pg == n)
        if on_page:
            if y >= 0:
                # A PDF destination sits slightly ABOVE the heading it names
                # — measured across all three cards, 0-40pt above, modes at
                # 15/17pt (99% of dests have a heading within 40pt below).
                # So the target is the FIRST heading at-or-below the dest;
                # only a dest past the last heading falls back to it.
                # (The old rule took the last heading ABOVE the dest, which
                # combined with the bottom-up dest_y bug meant multi-heading
                # destination pages resolved to their first heading.)
                below = [s for hy, s in on_page if hy >= y - 2]
                if below:
                    return below[0]
                return on_page[-1][1]
            return on_page[0][1]
        before = [s for pg, hy, s in heading_anchors if pg <= n]
        return before[-1] if before else ""
    # EXTENDED text-based link resolution (Appendix/Claim/unique-title/pooled)
    # is a per-card grammar knob in the style manifest (D16: scoped idioms):
    # the certified cards keep the original geometry + Section-number
    # resolution byte-for-byte; the risk report opts in (its Claim 6/7 links
    # land swapped by dest coords, 'Appendix 6.4' resolves to 6.3, and split
    # link halves diverge).
    extended_res = bool(re.search(
        r"^\s*link_text_resolution:\s*extended",
        (cardcfg.CARD / "style-manifest.yaml").read_text(), re.M))

    def text_resolution(plain):
        # anchors that NAME their target ('Section 8.17.6') resolve exactly —
        # the PDF's dest coordinates are sloppy in both directions (13/28
        # landed on a neighboring section by geometry on the first card)
        numpat = (r"(?:Section|§|Appendix)\s*(\d+(?:\.\d+)*)" if extended_res
                  else r"(?:Section|§)\s*(\d+(?:\.\d+)*)")
        mnum = (re.search(numpat, plain)
                or re.fullmatch(r"(\d+(?:\.\d+)+)\.?", plain.strip()))
        if mnum and mnum.group(1).rstrip(".") in num2slug:
            return num2slug[mnum.group(1).rstrip(".")]
        if not extended_res:
            return None
        mc = re.search(r"\bClaim\s+(\d+(?:\.\d+)*)", plain)
        if mc and mc.group(1) in claim2slug:
            return claim2slug[mc.group(1)]
        tkey = re.sub(r"[^a-z0-9]", "", plain.lower())
        return title2slug.get(tkey) or None

    # pooled per-destination resolution: a line-wrapped link arrives as TWO
    # annots ('Section' + '3.6') sharing one dest — when any anchor bearing a
    # dest resolves by text, every anchor with that dest inherits it (the
    # p.114 split link pointed its halves at different sections). Never for
    # page 0: every unresolvable dest shares the (0,-1) sentinel and pooling
    # them would stamp one target on all of them.
    pooled = {}
    if extended_res:
        for name, _ in written:
            md0 = (OUT / name).read_text()
            for mm in DEST_MARKDOWN_RE.finditer(md0):
                # pooling exists for a WRAPPED link arriving as two annots
                # ('Section' + '3.6'), so only short fragments seed the pool:
                # a full anchor phrase sharing a dest with a section-numbered
                # link elsewhere was inheriting the coarser target
                # ('previous threat model' → §4.2 where the dest names
                # §4.2.1, p.121, sweep round 3)
                if len(mm.group(1).split()) > 2:
                    continue
                r = text_resolution(mm.group(1))
                if r and mm.group(2) != "0":
                    pooled.setdefault((mm.group(2), mm.group(3)), r)
            for mm in DEST_HTML_RE.finditer(md0):
                r = text_resolution(re.sub(r"<[^>]+>", "", mm.group(3)))
                if r and mm.group(1) != "0":
                    pooled.setdefault((mm.group(1), mm.group(2)), r)

    for name, _ in written:
        f = OUT / name
        md = resolve_destination_placeholders(
            f.read_text(), anchor_for=anchor_for,
            text_resolution=text_resolution, pooled=pooled)
        f.write_text(md)

    all_pages = sorted({p for _, sel in written for p in sel})
    cardcfg.CACHE.mkdir(parents=True, exist_ok=True)
    (cardcfg.CACHE / "genpages.json").write_text(json.dumps(all_pages))
    print(f"\nwrote {len(written)} files to {OUT}")
    print("gate with:")
    prefixes = sorted({n.split('-')[0] for n, _ in written})
    print("  " + verifier_command(full=args.all, section_prefixes=prefixes))


if __name__ == "__main__":
    main()
