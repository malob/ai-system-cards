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
CAPTION_LEAD = re.compile(r"^\[(Figure|Table|Transcript)\b")
# Google Docs exports mark list markers with a zero-width space after the
# glyph/number: "●​Text", "1.​Text" — a mechanical signature that
# also distinguishes ordered-list markers from prose lines starting with digits
LIST_MARKER = re.compile(r"^([●•◦▪‣○]|\d{1,2}[.)]|[a-z][.)])​")  # incl. lettered sub-lists


def _classify(line, page, in_figure):
    if line["fnbody"]:
        return "fnbody"
    body_colors = {s["color"] for _, _, s in line["segs"] if s["zone"] == "body"}
    if line["size"] >= 12.6 or (body_colors == {HEADING_GRAY} and HEAD_NUM.match(line["text"])):
        return "heading"
    # deep headings (h5/h6, e.g. "2.3.4.1 Example 1: …") are bold body-size
    # black text — heading iff the whole line is bold AND it leads with a
    # multi-component section number (≥3 components; bold leads have no number,
    # ordered items carry the ZWSP marker)
    m = HEAD_NUM.match(line["text"])
    if (m and m.group(1).count(".") >= 2
            and all(s["bold"] for _, _, s in line["segs"] if s["zone"] == "body")):
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
    # captions are a first-class construct (D23): size-9 text with the
    # bracket-lead signature ([Figure|Table|Transcript N…]) anywhere, or any
    # small text inside a figure region
    if line["size"] <= 9.5 and (in_figure or CAPTION_LEAD.match(line["text"].lstrip())):
        return "caption"
    if LIST_MARKER.match(line["text"].lstrip()) or line["text"].lstrip()[:1] in BULLETS:
        return "item"
    return "prose"


def _chip_only(line, page, manifest_chips) -> bool:
    """A line consisting only of chip pills (+punctuation): its own block —
    the PDF renders chip rows on their own line (owner-flagged at 2.3.3)."""
    pills = [p for p in page.get("pills", []) if p.get("color") in manifest_chips]
    if not pills:
        return False
    found = False
    for _, _, s in line["segs"]:
        if s["zone"] != "body":
            continue
        t = s["text"].strip()
        if not t or not re.search(r"\w", t):
            continue
        if any(_rect_contains(p["bbox"], s["bbox"], slack=2.5) for p in pills):
            found = True
        else:
            return False
    return found


QUOTE_X0 = 112  # blockquote indent (body=72, item-continuation=108, quote=118+)


def _is_quote(line, page) -> bool:
    """Indented quote region (p.130 UK AISI): x0 >= ~118 outside any box,
    distinct from item hanging-indent (108) and body (72)."""
    if line["bbox"][0] < QUOTE_X0:
        return False
    return _box_role(line, page)[0] is None


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
        # an invisible-only line (a ZWSP-bearing empty paragraph — Google
        # Docs blank line) is a PARAGRAPH SEPARATOR: it must break the
        # continuation chain, never contribute content (p.87 glue)
        if not norm.INVISIBLES.sub("", line["text"]).strip():
            flush()
            cur = None
            continue
        kind = _classify(line, page, in_figure)
        # figure blocks are emitted once, when we first pass their region
        if img_rects and not fig_done and line["bbox"][1] > img_rects[0][1]:
            flush()
            for i, f in enumerate(figures):
                blocks.append({"type": "figure", "file": f, "page": pno,
                               "alt": "", "caption_lines": []})
            fig_done = True
        if kind == "prose" and cur and cur["type"] == "heading":
            # wrapped heading continuation: the second line of a wrapped
            # heading has no leading number so it classifies as paragraph
            # (p.177 'patterns in coding environments'). Title-wrap pitch is
            # ~2-4pt vs >=8pt heading->body spacing; require identical style
            # (colors + uniform boldness) so adjacent body text never merges
            prev = cur["lines"][-1]
            def _prof(l):
                segs = [s for _, _, s in l["segs"] if s["zone"] == "body"]
                return (frozenset(s["color"] for s in segs),
                        all(s["bold"] for s in segs) if segs else False)
            if (line["bbox"][1] - prev["bbox"][3] < 6
                    and abs(line["size"] - prev["size"]) < 0.6
                    and _prof(line) == _prof(prev)):
                cur["lines"].append(line)
                continue
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
            if (cur and cur["type"] == "caption"
                    and not CAPTION_LEAD.match(line["text"].lstrip())):
                cur["lines"].append(line)
            else:
                # a bracket lead starts its OWN caption — two figures' captions
                # were merging into one block (7.5.1.A/B)
                flush()
                cur = {"type": "caption", "lines": [line], "page": pno}
        elif kind == "item":
            flush()
            cur = {"type": "item", "lines": [line], "page": pno,
                   "marker_x0": line["bbox"][0],
                   "quote": _is_quote(line, page)}
            marker_x0s.add(round(line["bbox"][0]))
        elif kind in ("turn", "commentary", "example", "code"):
            role = _box_role(line, page)[1] if kind == "turn" else None
            # a new turn starts when the role changes or a bold label leads
            new_turn = (kind == "turn" and cur and cur.get("type") == "turn"
                        and (cur.get("role") != role
                             or (line["segs"] and line["segs"][0][2]["bold"])))
            if cur and cur["type"] == kind and not new_turn:
                # paragraph breaks INSIDE turns/boxes (PDF turn 229 has two
                # paragraphs): record split indices for the serializer
                prev_l = cur["lines"][-1]
                gap = line["bbox"][1] - prev_l["bbox"][3]
                if gap > max(4.0, 0.55 * (prev_l["bbox"][3] - prev_l["bbox"][1])):
                    cur.setdefault("breaks", []).append(len(cur["lines"]))
                cur["lines"].append(line)
            else:
                flush()
                cur = {"type": kind, "lines": [line], "page": pno}
                if kind == "turn":
                    cur["role"] = role
        else:  # prose
            # caption continuation: small text directly under an open caption
            if (cur and cur["type"] == "caption" and line["size"] <= 9.5
                    and line["bbox"][1] - cur["lines"][-1]["bbox"][3] < 8):
                cur["lines"].append(line)
                continue
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
                # vertical gap is the paragraph signal (Google Docs exports
                # whole columns as one PDF block, and chip pills fragment block
                # ids mid-paragraph — block identity is unreliable both ways).
                # A bold-lead start breaks ONLY when the previous line also
                # ended short of the column edge — run-in bold leads
                # ('**Results** On the long-form…') continue the paragraph
                # when the prior line is full-width (ST2-found class)
                col_right = max([l["bbox"][2] for l in cur["lines"]] + [line["bbox"][2]])
                prev_short = prev["bbox"][2] < col_right - 40
                starts_bold_lead = (line["segs"] and line["segs"][0][2]["bold"]
                                    and prev["text"].rstrip().endswith((".", "!", "?", ":", "”", '"'))
                                    and prev_short)
                chip_boundary = (_chip_only(line, page, manifest_chips)
                                 or _chip_only(prev, page, manifest_chips))
                same_para = (gap < max(4.0, 0.55 * line_h)
                             and not starts_bold_lead
                             and not chip_boundary
                             and cur.get("quote", False) == _is_quote(line, page))
            if same_para:
                cur["lines"].append(line)
            else:
                flush()
                cur = {"type": "paragraph", "lines": [line], "page": pno,
                       "quote": _is_quote(line, page)}
    flush()
    for tb in pending_tables:  # tables below all prose
        blocks.append(tb)

    # nested-list levels from marker-x0 tiers (level 0 = leftmost markers),
    # computed separately inside and outside quotes (quote bullets start ~127
    # but are level 0 within their quote)
    for in_quote in (False, True):
        xs = sorted({round(b["marker_x0"]) for b in blocks
                     if b["type"] == "item" and b.get("quote", False) == in_quote})
        merged_tiers = []
        for x in xs:
            if not merged_tiers or x - merged_tiers[-1] > 4:
                merged_tiers.append(x)
        for blk in blocks:
            if blk["type"] == "item" and blk.get("quote", False) == in_quote:
                x = round(blk["marker_x0"])
                blk["level"] = next((i for i, t in enumerate(merged_tiers) if abs(x - t) <= 4), 0)

    # a label-only turn followed by a code/example box is ONE construct: the
    # turn's content is the boxed code (p.118 displaced-thinking class)
    merged = []
    for blk in blocks:
        if (merged and merged[-1]["type"] == "turn" and blk["type"] in ("code", "example")
                and _turn_is_label_only(merged[-1])):
            merged[-1]["code_lines"] = blk["lines"]
            continue
        merged.append(blk)
    blocks = merged

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
    # "cont" (cross-page continuation of the previous page's last footnote)
    # precedes this page's own numbered footnotes in document order
    for n in sorted(fn_lines_by_n, key=lambda n: -1 if n == "cont" else n):
        blocks.append({"type": "footnote", "n": n, "lines": fn_lines_by_n[n], "page": pno})
    return blocks


def _turn_is_label_only(blk) -> bool:
    """A turn whose entire text is a bracketed label like '[Assistant:]'."""
    text = " ".join(l["text"] for l in blk["lines"]).strip()
    return bool(re.fullmatch(r"\[[^\]]{1,30}\]:?\s*", text))


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
            if "Mono" in s.get("font", "") and s["zone"] == "body":
                # monospace span = inline code (RobotoMono in this card);
                # code styling dominates — no bold/italic inside
                marks.append(("code", m_start, m_end, None))
                continue
            if s["bold"]:
                marks.append(("bold", m_start, m_end, None))
            if s["italic"]:
                marks.append(("italic", m_start, m_end, None))
            # prose underline: CAPTION blocks only (the legend's literal
            # 'underlined' word). The unrestricted version over-fired on
            # chart-axis/table-border rules under ordinary prose (T1 6->33);
            # in this card prose underline occurs only in captions. The rule
            # must hug the baseline and span most of the word, nothing more.
            if block.get("type") == "caption" and s["zone"] == "body":
                sb = s["bbox"]
                scy = (sb[1] + sb[3]) / 2
                # linked text is underlined by LINK styling — never mark it
                # (a <u> straddling '[text](url)' also breaks the syntax)
                in_link = any(
                    lr[1] <= scy <= lr[3]
                    and min(sb[2], lr[2]) - max(sb[0], lr[0]) > 0.5 * (sb[2] - sb[0])
                    for lk in page["links"]["uri"] + page["links"]["goto"]
                    for lr in (lk.get("rects") or [lk.get("rect")]) if lr)
                if not in_link and len(t.strip()) > 1:
                    for ru in page.get("rules", []):
                        rb = ru["bbox"]
                        if not (sb[3] - 2.5 <= rb[1] <= sb[3] + 5.0):
                            continue
                        ov0, ov1 = max(sb[0], rb[0]), min(sb[2], rb[2])
                        if ov1 - ov0 <= 2:
                            continue
                        # the rule usually covers a few WORDS of a longer
                        # span ('underlined' inside the legend sentence):
                        # map its x-range to chars proportionally, snap to
                        # word boundaries, drop trailing punctuation
                        # a word is underlined iff its estimated CENTER sits
                        # under the rule — robust to proportional-width drift
                        # (end-mapping pulled in the next word: 'underlined (but')
                        cw = (sb[2] - sb[0]) / max(1, len(t))
                        words = [(w.start(), w.end())
                                 for w in re.finditer(r"\S+", t)]
                        hit = [(ws, we) for ws, we in words
                               if ov0 - 1 <= sb[0] + cw * (ws + we) / 2 <= ov1 + 1]
                        if not hit:
                            continue
                        a2, b2 = start + hit[0][0], start + hit[-1][1]
                        while b2 > a2 and t[b2 - start - 1] in ".,;:":
                            b2 -= 1
                        if b2 > a2:
                            marks.append(("underline", a2, b2, None))
            for pi, pill in enumerate(pills):
                if "bbox" not in pill:
                    continue
                if _rect_contains(pill["bbox"], s["bbox"], slack=2.5):
                    if pill["color"] in manifest_chips:
                        # data = pill identity so two distinct chips don't merge
                        marks.append(("chip", m_start, m_end, pi))
                    elif pill["color"] == PLACEHOLDER:
                        marks.append(("placeholder", m_start, m_end, pi))
                    break
                if pill["color"] == PLACEHOLDER:
                    # green placeholder pills highlight a RANGE INSIDE a longer
                    # span (unlike chips, which own theirs): map the pill's
                    # x-range to chars proportionally, snap to whitespace
                    pb, sb = pill["bbox"], s["bbox"]
                    if (min(sb[3], pb[3]) - max(sb[1], pb[1])
                            > 0.6 * (pb[3] - pb[1])
                            and min(sb[2], pb[2]) - max(sb[0], pb[0]) > 2):
                        cw = (sb[2] - sb[0]) / max(1, len(t))
                        i0 = max(0, int((pb[0] - sb[0]) / cw))
                        i1 = min(len(t), int((pb[2] - sb[0]) / cw + 0.5))
                        # most pills highlight a BRACKETED token: snap to the
                        # bracket pair near the estimate (whitespace-snapping
                        # swallowed neighbors: '[user]-authored,', 'Create [')
                        lb = t.find("[", max(0, i0 - 2), min(len(t), i0 + 3))
                        # the matching close is the FIRST ']' after the open —
                        # an estimate-window search grabbed the NEXT pill's
                        # bracket when two pills sit side by side
                        rb = t.find("]", lb + 1, min(len(t), i1 + 4)) if lb >= 0 else -1
                        if lb >= 0 and rb >= 0 and rb > lb:
                            i0, i1 = lb, rb + 1
                        else:
                            while i0 > 0 and not t[i0 - 1].isspace():
                                i0 -= 1
                            while i1 < len(t) and not t[i1].isspace():
                                i1 += 1
                        seg = t[i0:i1]
                        a2 = start + i0 + (len(seg) - len(seg.lstrip()))
                        b2 = start + i1 - (len(seg) - len(seg.rstrip()))
                        if b2 > a2:
                            marks.append(("placeholder", a2, b2, pi))
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
                    target = l.get("uri") or "DEST:{}:{}".format(
                        l.get("dest_page", 0), int(l.get("dest_y", -1)))
                    marks.append(("link", m_start, m_end, target))
                    break
    text = "".join(text_parts)
    # drop emphasis over invisible-only text: a ZWSP-only bold serializes to
    # '**​**' → '****' after invisible-stripping, and a literal '****'
    # re-pairs every later '**' in the document during verification
    marks = [m for m in marks
             if not (m[0] in ("bold", "italic", "chip")
                     and not text[m[1]:m[2]].translate(_INVIS))]
    # emphasis over punctuation-only text ('**;**' after chips) is
    # meaningless — but filter AFTER merging, so a bold ':' that belongs to
    # an adjacent bold run joins it instead of dying ('[Bottom left:]')
    import re as _re
    merged = _merge_marks(marks)
    merged = [m for m in merged
              if not (m[0] in ("bold", "italic")
                      and not _re.search(r"\w", text[m[1]:m[2]]))]
    return text, merged


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
