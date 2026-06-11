"""PDF → per-page mechanical facts (the verification oracle, decision D14).

Dumb by design: emits facts with zone tags; *policy* (what's excluded from which
invariant) lives in invariants.py + the card's style manifest. Caches to JSON.

Zones:
  body          regular content text
  pagenum       bare page-number footer (excluded from T1)
  fnref         superscript footnote reference digits (counted by FN1, not T1)
  fnbody        footnote body text at page bottom (FN1 stream, not main T1)
  figure        text inside a raster image rect (excluded from T1 — charts)
"""

import json
import re
from pathlib import Path

import fitz

BOLD, ITALIC, SUPER = 16, 2, 1
BODY_SIZE = 11.0  # this card's body font size


def _hex(c: int) -> str:
    return f"#{c:06x}"


def _image_rects(page) -> list[fitz.Rect]:
    rects = []
    for img in page.get_images(full=True):
        rects.extend(page.get_image_rects(img[0]))
    return rects


def _zone(span, page_height, image_rects):
    # NOTE: no exclusion for text "inside" raster image rects — raster-internal
    # text is pixels, not text-layer spans; any text-layer span overlapping an
    # image rect is real overlay text (typically a caption under an oversized
    # chart bbox — see p.139). Vector-chart furniture text is a separate, still
    # open exclusion (drawing-cluster zones; experiment 03).
    text = span["text"].strip()
    if fitz.Rect(span["bbox"]).y1 > page_height - 45 and re.fullmatch(r"\d+", text):
        return "pagenum"
    if span["flags"] & SUPER and re.fullmatch(r"\d+", text):
        return "fnref"
    return "body"


def extract_page(page) -> dict:
    H = page.rect.height
    image_rects = _image_rects(page)
    spans = []
    line_id = 0
    for blk_id, blk in enumerate(page.get_text("dict")["blocks"]):
        if blk["type"] != 0:
            continue
        for line in blk["lines"]:
            line_id += 1
            for s in line["spans"]:
                if not s["text"].strip():
                    continue
                spans.append(
                    {
                        "text": s["text"],
                        "size": round(s["size"], 1),
                        "bold": bool(s["flags"] & BOLD) or "Bold" in s["font"],
                        "italic": bool(s["flags"] & ITALIC) or "Italic" in s["font"],
                        "super": bool(s["flags"] & SUPER),
                        "color": _hex(s["color"]),
                        "font": s["font"],
                        "bbox": [round(v, 1) for v in s["bbox"]],
                        "flags": s["flags"],
                        "line": line_id,
                        "block": blk_id,
                    }
                )
    for s in spans:
        s["zone"] = _zone(s, H, image_rects)

    # footnote bodies: line-level pass. A footnote starts at a small-font line
    # in the bottom ~28% whose text begins with a 1-2 digit marker; subsequent
    # small-font lines continue it until a body-size line appears.
    lines: dict[int, list[dict]] = {}
    for s in spans:
        lines.setdefault(s["line"], []).append(s)
    fn_mode = False
    cur_n = None
    footnotes: dict = {}
    # iterate by VISUAL position: PyMuPDF block order can put a marker line
    # before unmarked lines that sit ABOVE it (the p.114 fn15/16 graft)
    infos = []
    for _, line_spans in sorted(lines.items(),
                                key=lambda kv: min(s["bbox"][1] for s in kv[1])):
        body_spans = [s for s in line_spans if s["zone"] == "body"]
        if not body_spans:
            continue
        first = body_spans[0]
        small = first["size"] <= BODY_SIZE - 0.8
        is_marker = (
            first["size"] <= 7.5
            and re.fullmatch(r"\d{1,2}", first["text"].strip())
            and first["bbox"][1] > H * 0.6
        )
        infos.append({"body_spans": body_spans, "first": first, "small": small,
                      "is_marker": bool(is_marker),
                      "top": min(s["bbox"][1] for s in body_spans),
                      "bottom": max(s["bbox"][3] for s in body_spans)})
    # cross-page continuation: unmarked small bottom-region lines chained
    # immediately ABOVE the page's first marker line are the tail of the
    # PREVIOUS page's last footnote -> keyed "cont"
    cont_idx = set()
    mi = next((i for i, inf in enumerate(infos) if inf["is_marker"]), None)
    if mi is not None:
        edge = infos[mi]["top"]
        j = mi - 1
        while j >= 0:
            inf = infos[j]
            if (not inf["small"] or inf["is_marker"]
                    or inf["top"] <= H * 0.6 or edge - inf["bottom"] > 14):
                break
            cont_idx.add(j)
            edge = inf["top"]
            j -= 1
    for idx in sorted(cont_idx):
        bs = infos[idx]["body_spans"]
        for s in bs:
            s["zone"] = "fnbody"
            s["fn"] = "cont"
        footnotes.setdefault("cont", "")
        footnotes["cont"] += " " + "".join(s["text"] for s in bs)
    for idx, inf in enumerate(infos):
        if idx in cont_idx:
            continue
        body_spans, first = inf["body_spans"], inf["first"]
        small, is_marker = inf["small"], inf["is_marker"]
        if is_marker:
            # a footnote body line leads with the marker digit in tiny type
            # (~6.6pt vs 11pt body) — the only reliable signature
            fn_mode = True
            cur_n = int(first["text"].strip())
            footnotes.setdefault(cur_n, "")
        elif fn_mode and not small:
            fn_mode, cur_n = False, None
        if fn_mode:
            for s in body_spans:
                s["zone"] = "fnbody"
                s["fn"] = cur_n
            if is_marker:
                first["fn_marker"] = True   # the leading digit, not body text
            if cur_n is not None:
                body = "".join(s["text"] for s in body_spans if not (is_marker and s is first))
                footnotes[cur_n] += " " + body

    links = {"uri": [], "goto": []}
    seen_uris = {}
    for l in page.get_links():
        anchor = page.get_text(clip=fitz.Rect(l["from"])).strip().replace("\n", " ")
        if l["kind"] == fitz.LINK_URI:
            # a line-wrapped URL yields multiple annotations for ONE logical
            # link — merge same-URI annotations on a page
            rect = [round(v, 1) for v in fitz.Rect(l["from"])]
            if l["uri"] in seen_uris:
                seen_uris[l["uri"]]["anchor"] += anchor
                seen_uris[l["uri"]]["rects"].append(rect)
            else:
                entry = {"anchor": anchor, "uri": l["uri"], "rects": [rect]}
                seen_uris[l["uri"]] = entry
                links["uri"].append(entry)
        elif l["kind"] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
            dest_page = (l.get("page") if l.get("page") is not None else -1) + 1
            entry = {"anchor": anchor, "dest_page": dest_page,
                     "rects": [[round(v, 1) for v in fitz.Rect(l["from"])]]}
            if l.get("to") is not None:   # dest y disambiguates multi-heading pages
                try:
                    entry["dest_y"] = round(l["to"].y, 1)
                except Exception:
                    pass
            if dest_page == 0:  # named dest that doesn't resolve in the PDF's name tree
                entry["unresolvable"] = True
                entry["name"] = l.get("nameddest") or l.get("name") or ""
            links["goto"].append(entry)

    pills, boxes, rules = [], [], []
    for d in page.get_drawings():
        if d.get("fill") is None:
            # stroke-only paths: thin horizontal strokes are underline rules
            r = d["rect"]
            if d.get("color") is not None and r.height <= 2.5 and 8 <= r.width <= 250:
                col = "#" + "".join(f"{int(round(v * 255)):02x}" for v in d["color"])
                rules.append({"color": col, "bbox": [round(v, 1) for v in r]})
            continue
        r = d["rect"]
        col = "#" + "".join(f"{int(round(v * 255)):02x}" for v in d["fill"])
        is_box = (r.height >= 30 and r.width >= 100) or (r.height >= 12 and r.width >= 250)
        if is_box:
            # wide rect = container/bubble/panel (incl. single-line turn bubbles)
            boxes.append({"color": col, "bbox": [round(v, 1) for v in r]})
        elif 6 < r.height < 30 and 9 < r.width < 250:  # 9pt: tiny '[…]' placeholder pills count
            # narrow rect = inline pill (chip / placeholder / code span)
            t = page.get_text(clip=r).strip().replace("\n", " ")
            if t:
                pills.append({"color": col, "text": t, "bbox": [round(v, 1) for v in r]})
        elif r.height <= 2.5 and 8 <= r.width <= 250:
            # thin rule = underline candidate (FL-09: legend-bearing underlines)
            rules.append({"color": col, "bbox": [round(v, 1) for v in r]})

    return {
        "spans": spans,
        "links": links,
        "pills": pills,
        "boxes": boxes,
        "rules": rules,
        "footnotes": footnotes,
        "image_rects": [[round(v, 1) for v in r] for r in image_rects],
        "n_raster_images": len(set(map(tuple, [tuple(r) for r in image_rects]))),
    }


def page_body_text(p: dict) -> str:
    """Body text of an extracted page: spans joined within a line (inserting a
    space only when there is a real x-gap between spans), lines joined with
    spaces, end-of-line hyphenations joined (allowlist A1)."""
    lines: dict[int, list[dict]] = {}
    for s in p["spans"]:
        if s["zone"] == "body":
            lines.setdefault(s["line"], []).append(s)
    rendered = []
    for _, spans in sorted(lines.items()):
        buf = spans[0]["text"]
        for prev, cur in zip(spans, spans[1:]):
            gap = cur["bbox"][0] - prev["bbox"][2]
            buf += (" " if gap > 1.0 else "") + cur["text"]
        rendered.append(buf)
    text = " ".join(rendered)
    # join end-of-line hyphenations: "self- verifying" -> "self-verifying"
    text = re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1", text)  # keep suspended compounds
    return text


def page_footnotes(p: dict) -> str:
    return " ".join(s["text"] for s in p["spans"] if s["zone"] == "fnbody")


def extract(pdf_path: Path, cache: Path | None = None) -> list[dict]:
    if cache and cache.exists():
        return json.loads(cache.read_text())
    doc = fitz.open(pdf_path)
    pages = [extract_page(doc[i]) for i in range(len(doc))]
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(pages))
    return pages
