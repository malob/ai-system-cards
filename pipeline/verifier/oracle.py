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
    text = span["text"].strip()
    r = fitz.Rect(span["bbox"])
    if r.y1 > page_height - 45 and re.fullmatch(r"\d+", text):
        return "pagenum"
    if span["flags"] & SUPER and re.fullmatch(r"\d+", text):
        return "fnref"
    italic = bool(span["flags"] & ITALIC)
    if not italic:  # captions (italic) may overlay chart image rects — spare them
        for ir in image_rects:
            if ir.contains(r) or (ir.intersects(r) and abs(ir & r) > 0.6 * abs(r)):
                return "figure"
    return "body"


def extract_page(page) -> dict:
    H = page.rect.height
    image_rects = _image_rects(page)
    spans = []
    line_id = 0
    for blk in page.get_text("dict")["blocks"]:
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
                        "bbox": [round(v, 1) for v in s["bbox"]],
                        "flags": s["flags"],
                        "line": line_id,
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
    for _, line_spans in sorted(lines.items()):
        body_spans = [s for s in line_spans if s["zone"] == "body"]
        if not body_spans:
            continue
        first = body_spans[0]
        small = first["size"] <= BODY_SIZE - 0.8
        if not fn_mode:
            # a real footnote body line leads with the marker digit in tiny
            # type (~6.6pt vs 11pt body) — the only reliable signature
            if (
                first["size"] <= 7.5
                and re.fullmatch(r"\d{1,2}", first["text"].strip())
                and first["bbox"][1] > H * 0.6
            ):
                fn_mode = True
        elif not small:
            fn_mode = False
        if fn_mode:
            for s in body_spans:
                s["zone"] = "fnbody"

    links = {"uri": [], "goto": []}
    for l in page.get_links():
        anchor = page.get_text(clip=fitz.Rect(l["from"])).strip().replace("\n", " ")
        if l["kind"] == fitz.LINK_URI:
            links["uri"].append({"anchor": anchor, "uri": l["uri"]})
        elif l["kind"] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
            links["goto"].append({"anchor": anchor, "dest_page": l.get("page", -1) + 1})

    return {
        "spans": spans,
        "links": links,
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
    text = re.sub(r"(\w)- (?=[a-z])", r"\1", text)
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
