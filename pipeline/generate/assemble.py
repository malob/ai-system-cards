"""Mechanical block compiler (generation-design.md): oracle page facts +
style manifest → typed blocks with provenance and ambiguity flags. The LLM
never types text — structure is assigned over the immutable span stream;
inline marks are attached from oracle facts (flags, link rects, pill fills).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "verifier"))
import norm  # noqa: E402

BODY_SIZE = 11.0
HEADING_GRAY = "#666666"
COMMENTARY_GRAY = "#444444"
TRANSCRIPT_BOXES = {"#f3f3f3"}
TURN_FILLS = {"#ebc9b7": "assistant", "#e2decf": "user", "#faf9f5": "user"}
EXAMPLE_BOXES = {"#f0eee6"}
CODE_BOXES = {"#f1f3f4"}
PLACEHOLDER = "#d9ead3"
BULLETS = "●•◦▪‣○"


def _rect_contains(outer, inner, slack=2.0):
    return (outer[0] - slack <= inner[0] and outer[1] - slack <= inner[1]
            and outer[2] + slack >= inner[2] and outer[3] + slack >= inner[3])


def _overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _lines(page):
    """Group spans into VISUAL ROWS (gap-aware x-ordered join). PyMuPDF line
    ids fragment a row — chip pills, lone bullet glyphs (often with offset y),
    and side-by-side spans come back as separate 'lines', sometimes out of
    order (p.38). Rows are rebuilt by y-overlap clustering, then spans joined
    left-to-right."""
    by_line = {}
    for s in page["spans"]:
        if s["zone"] in ("pagenum",):
            continue
        by_line.setdefault(s["line"], []).append(s)

    frags = []
    for _, spans in sorted(by_line.items()):
        y0 = min(s["bbox"][1] for s in spans)
        y1 = max(s["bbox"][3] for s in spans)
        frags.append({"spans": spans, "y0": y0, "y1": y1})

    rows = []
    for f in sorted(frags, key=lambda f: (f["y0"], f["spans"][0]["bbox"][0])):
        placed = False
        for r in rows[-4:]:
            ov = min(r["y1"], f["y1"]) - max(r["y0"], f["y0"])
            h = min(r["y1"] - r["y0"], f["y1"] - f["y0"])
            if h > 0 and ov / h > 0.5:
                r["spans"].extend(f["spans"])
                r["y0"], r["y1"] = min(r["y0"], f["y0"]), max(r["y1"], f["y1"])
                placed = True
                break
        if not placed:
            rows.append(dict(f))

    lines = []
    for i, r in enumerate(rows):
        spans = sorted(r["spans"], key=lambda s: s["bbox"][0])
        parts, segs = [], []  # segs: (start, end, span) char offsets into text
        pos = 0
        for j, s in enumerate(spans):
            if j and s["bbox"][0] - spans[j - 1]["bbox"][2] > 0.5:
                parts.append(" ")
                pos += 1
            parts.append(s["text"])
            segs.append((pos, pos + len(s["text"]), s))
            pos += len(s["text"])
        body = [s for s in spans if s["zone"] == "body"]
        lines.append({
            "id": i, "text": "".join(parts), "segs": segs,
            "bbox": [min(s["bbox"][0] for s in spans), r["y0"],
                     max(s["bbox"][2] for s in spans), r["y1"]],
            "block": spans[0]["block"],
            "size": max((s["size"] for s in body), default=spans[0]["size"]),
            "fnbody": all(s["zone"] == "fnbody" for s in spans),
            "mono": any(("Mono" in s["font"] or "Courier" in s["font"]) for s in spans),
        })
    return lines


def _box_role(line, page):
    """Most-specific containing box wins: a turn bubble nested inside a
    transcript container must classify as the turn, not the container."""
    containing = [b for b in page.get("boxes", [])
                  if _rect_contains(b["bbox"], line["bbox"], slack=4.0)]
    # smallest-area box first
    containing.sort(key=lambda b: (b["bbox"][2] - b["bbox"][0]) * (b["bbox"][3] - b["bbox"][1]))
    in_transcript = any(b["color"] in TRANSCRIPT_BOXES for b in containing)
    for b in containing:
        c = b["color"]
        if c in TURN_FILLS:
            return ("turn", TURN_FILLS[c], in_transcript)
        if c in EXAMPLE_BOXES:
            return ("example", None, in_transcript)
        if c in CODE_BOXES:
            return ("code", None, in_transcript)
        if c in TRANSCRIPT_BOXES:
            return ("transcript", None, in_transcript)
    return (None, None, in_transcript)


HEAD_NUM = re.compile(r"^(\d+(?:\.\d+)*)\s+\S")
# Google Docs exports mark list markers with a zero-width space after the
# glyph/number: "●​Text", "1.​Text" — a mechanical signature that
# also distinguishes ordered-list markers from prose lines starting with digits
LIST_MARKER = re.compile(r"^([●•◦▪‣○]|\d{1,2}[.)])​")


def _classify(line, page, in_figure):
    if line["fnbody"]:
        return "fnbody"
    body_colors = {s["color"] for _, _, s in line["segs"] if s["zone"] == "body"}
    if line["size"] >= 12.6 or (body_colors == {HEADING_GRAY} and HEAD_NUM.match(line["text"])):
        return "heading"
    role, _, in_transcript = _box_role(line, page)
    if role == "turn":
        return "turn"
    if role in ("example", "code"):
        return role
    if role == "transcript":
        # inside the container but not in a bubble: gray = narrator commentary,
        # black = an untinted turn (rare; treated as its own turn block)
        return "commentary" if COMMENTARY_GRAY in body_colors else "turn"
    if in_figure and line["size"] <= 9.5:
        return "caption"
    if LIST_MARKER.match(line["text"].lstrip()) or line["text"].lstrip()[:1] in BULLETS:
        return "item"
    return "prose"


def assemble_page(pno: int, page: dict, figures: list[str], manifest_chips: dict,
                  page_tables: list[dict] | None = None) -> list[dict]:
    """One page → ordered block dicts. Cross-page joining happens in stitch.
    Lines inside a docling table bbox are removed from prose flow; the table is
    emitted as an HTML block at its vertical position (D14)."""
    page_tables = page_tables or []

    def _in_table(line):
        cx = (line["bbox"][0] + line["bbox"][2]) / 2
        cy = (line["bbox"][1] + line["bbox"][3]) / 2
        return any(t["bbox"][0] - 3 <= cx <= t["bbox"][2] + 3
                   and t["bbox"][1] - 3 <= cy <= t["bbox"][3] + 3 for t in page_tables)

    lines = [l for l in _lines(page) if not l["fnbody"] and not _in_table(l)]
    img_rects = page.get("image_rects", [])
    # table blocks slotted by their top y-coordinate
    table_blocks = [{"type": "table_html", "html": t["html"], "page": pno,
                     "_y": t["bbox"][1]} for t in page_tables]

    blocks = []
    cur = None
    marker_x0s: set[int] = set()

    def flush():
        nonlocal cur
        if cur:
            blocks.append(cur)
            cur = None

    fig_done = False
    pending_tables = sorted(table_blocks, key=lambda b: b["_y"])
    for line in sorted(lines, key=lambda l: (round(l["bbox"][1]), l["bbox"][0])):
        # emit any table whose top is above this line, in reading order
        while pending_tables and pending_tables[0]["_y"] <= line["bbox"][1]:
            flush()
            blocks.append(pending_tables.pop(0))
        in_figure = any(_overlaps(r, line["bbox"]) for r in img_rects)
        kind = _classify(line, page, in_figure)
        # figure blocks are emitted once, when we first pass their region
        if img_rects and not fig_done and line["bbox"][1] > img_rects[0][1]:
            flush()
            for i, f in enumerate(figures):
                blocks.append({"type": "figure", "file": f, "page": pno,
                               "alt": "", "caption_lines": []})
            fig_done = True
        if kind == "heading":
            # multi-line headings (wrapped titles) merge into one block — a
            # split heading produced the duplicate-TOC-entry bug
            if (cur and cur["type"] == "heading"
                    and line["bbox"][1] - cur["lines"][-1]["bbox"][3] < 10
                    and abs(line["size"] - cur["lines"][-1]["size"]) < 0.6):
                cur["lines"].append(line)
                continue
            flush()
            m = HEAD_NUM.match(line["text"])
            level = (m.group(1).count(".") + 2) if m else 2
            cur = {"type": "heading", "level": min(level, 6),
                   "lines": [line], "page": pno}
        elif kind == "caption":
            if blocks and blocks[-1]["type"] == "figure":
                blocks[-1]["caption_lines"].append(line)
            else:
                cur = _extend(cur, "paragraph", line, pno, flush_cb=flush)
        elif kind == "item":
            flush()
            cur = {"type": "item", "lines": [line], "page": pno,
                   "marker_x0": line["bbox"][0]}
            marker_x0s.add(round(line["bbox"][0]))
        elif kind in ("turn", "commentary", "example", "code"):
            role = _box_role(line, page)[1] if kind == "turn" else None
            # a new turn starts when the role changes or a bold label leads
            new_turn = (kind == "turn" and cur and cur.get("type") == "turn"
                        and (cur.get("role") != role
                             or (line["segs"] and line["segs"][0][2]["bold"])))
            if cur and cur["type"] == kind and not new_turn:
                cur["lines"].append(line)
            else:
                flush()
                cur = {"type": kind, "lines": [line], "page": pno}
                if kind == "turn":
                    cur["role"] = role
        else:  # prose
            # continuation of a wrapped list item — two layouts in this card:
            # hanging indent (text ~18pt right of marker, p.12) and flush-left
            # (chip-definition lists, p.38: continuation at the marker x0, only
            # joinable when the item is mid-sentence)
            if cur and cur["type"] == "item":
                prev = cur["lines"][-1]
                gap = line["bbox"][1] - prev["bbox"][3]
                hanging = line["bbox"][0] > cur["marker_x0"] + 6
                prev_open = prev["text"].rstrip()[-1:] not in ".!?;:”\"’"
                flush_left = (abs(line["bbox"][0] - cur["marker_x0"]) <= 2
                              and (prev_open or line["text"].lstrip()[:1].islower()))
                if gap < 8 and (hanging or flush_left):
                    cur["lines"].append(line)
                    continue
            same_para = False
            if cur and cur["type"] == "paragraph":
                prev = cur["lines"][-1]
                gap = line["bbox"][1] - prev["bbox"][3]
                line_h = prev["bbox"][3] - prev["bbox"][1]
                # Google Docs exports whole columns as one PDF block: split
                # paragraphs on vertical gaps and on bold-lead starts
                starts_bold_lead = (line["segs"] and line["segs"][0][2]["bold"]
                                    and prev["text"].rstrip().endswith((".", "!", "?", ":", "”", '"')))
                same_para = (line["block"] == prev["block"]
                             and gap < max(4.0, 0.55 * line_h)
                             and not starts_bold_lead)
            if same_para:
                cur["lines"].append(line)
            else:
                flush()
                cur = {"type": "paragraph", "lines": [line], "page": pno}
    flush()
    for tb in pending_tables:  # tables below all prose
        blocks.append(tb)

    # nested-list levels from marker-x0 tiers (level 0 = leftmost markers)
    tiers = sorted(marker_x0s)
    merged_tiers = []
    for x in tiers:
        if not merged_tiers or x - merged_tiers[-1] > 4:
            merged_tiers.append(x)
    for blk in blocks:
        if blk["type"] == "item":
            x = round(blk["marker_x0"])
            blk["level"] = next((i for i, t in enumerate(merged_tiers) if abs(x - t) <= 4), 0)

    if not fig_done and figures:
        for f in figures:
            blocks.append({"type": "figure", "file": f, "page": pno, "alt": "", "caption_lines": []})

    # footnote blocks built from fnbody spans (grouped by number) so links/
    # emphasis inside citations attach via block_text_and_marks
    fn_lines_by_n: dict[int, list] = {}
    for line in _lines(page):
        body = [s for s in line["segs"] if s[2]["zone"] == "fnbody"]
        if not body:
            continue
        n = body[0][2].get("fn")
        if n is None:
            continue
        # drop the leading marker-digit span from the first line of a footnote
        segs = [(a, b, s) for a, b, s in line["segs"] if not s.get("fn_marker")]
        if segs:
            fn_lines_by_n.setdefault(n, []).append({**line, "segs": segs})
    for n in sorted(fn_lines_by_n):
        blocks.append({"type": "footnote", "n": n, "lines": fn_lines_by_n[n], "page": pno})
    return blocks


def _extend(cur, kind, line, pno, flush_cb):
    if cur and cur["type"] == kind:
        cur["lines"].append(line)
        return cur
    flush_cb()
    return {"type": kind, "lines": [line], "page": pno}


def block_text_and_marks(block: dict, page: dict, manifest_chips: dict) -> tuple[str, list]:
    """Join a block's lines into text; compute inline marks as char ranges:
    bold/italic from span flags; links from annotation rects; chips and
    placeholders from pill fills; footnote refs from superscript spans."""
    text_parts, marks = [], []
    pos = 0
    pills = page.get("pills", [])
    links = page["links"]["uri"] + page["links"]["goto"]
    for li, line in enumerate(block.get("lines", [])):
        if li:
            text_parts.append(" ")
            pos += 1
        for a, b, s in line["segs"]:
            start = pos
            t = s["text"]
            text_parts.append(t)
            pos += len(t)
            # trim mark range to non-space content
            t_strip_l = len(t) - len(t.lstrip())
            t_strip_r = len(t) - len(t.rstrip())
            m_start, m_end = start + t_strip_l, pos - t_strip_r
            if s["zone"] == "fnref":
                marks.append(("fnref", m_start, m_end, int(s["text"].strip())))
                continue
            if s["bold"]:
                marks.append(("bold", m_start, m_end, None))
            if s["italic"]:
                marks.append(("italic", m_start, m_end, None))
            for pi, pill in enumerate(pills):
                if "bbox" in pill and _rect_contains(pill["bbox"], s["bbox"], slack=2.5):
                    if pill["color"] in manifest_chips:
                        # data = pill identity so two distinct chips don't merge
                        marks.append(("chip", m_start, m_end, pi))
                    elif pill["color"] == PLACEHOLDER:
                        marks.append(("placeholder", m_start, m_end, pi))
                    break
            for l in links:
                # span belongs to a link if its vertical center sits in the
                # rect's y-band AND >50% of its width overlaps the rect — recovers
                # thin URI rects while excluding edge-touching neighbor words
                sx0, sy0, sx1, sy1 = s["bbox"]
                scy = (sy0 + sy1) / 2
                sw = max(sx1 - sx0, 0.1)
                if any(r[1] - 1 <= scy <= r[3] + 1
                       and (min(sx1, r[2]) - max(sx0, r[0])) / sw > 0.5
                       for r in l.get("rects", [])):
                    target = l.get("uri") or f"DEST:{l.get('dest_page', 0)}"
                    marks.append(("link", m_start, m_end, target))
                    break
    text = "".join(text_parts)
    # drop emphasis over invisible-only text: a ZWSP-only bold serializes to
    # '**​**' → '****' after invisible-stripping, and a literal '****'
    # re-pairs every later '**' in the document during verification
    marks = [m for m in marks
             if not (m[0] in ("bold", "italic", "chip")
                     and not text[m[1]:m[2]].translate(_INVIS))]
    return text, _merge_marks(marks)


_INVIS = str.maketrans("", "", "​‌‍﻿­ \t")


def _merge_marks(marks):
    """Drop bold/italic inside chip ranges FIRST (chips render as pills, not
    emphasis), then coalesce adjacent same-kind marks. Order matters: filtering
    after merging lets a bold bridge across a chip boundary and re-leak '**'
    into the label."""
    atomic = [m for m in marks if m[0] in ("chip", "fnref")]
    marks = [m for m in marks
             if not (m[0] in ("bold", "italic")
                     and any(c[1] <= m[1] and m[2] <= c[2] for c in atomic))]
    out = []
    for kind, a, b, data in sorted(marks, key=lambda m: (m[0], m[1])):
        # tolerance 2: span trailing-space trim + the line-join space leave a
        # 2-char gap at line wraps; without this, wrapped links/bolds fragment
        # ("Project|Glasswing" double anchors; "**…** **…**" split bolds)
        if out and out[-1][0] == kind and out[-1][3] == data and a <= out[-1][2] + 2:
            out[-1][2] = max(out[-1][2], b)
        else:
            out.append([kind, a, b, data])
    return out
