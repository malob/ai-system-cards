"""Extract internal (GoTo) link annotations: anchor text + destination page."""
import json
from pathlib import Path
import pdfplumber
from pypdf import PdfReader

reader = PdfReader("source.pdf")

# resolve named destinations -> page index
named = {}
try:
    for name, dest in reader.named_destinations.items():
        try:
            named[name] = reader.get_destination_page_number(dest)
        except Exception:
            pass
except Exception:
    pass

# map each indirect page object id -> page index
pageid_to_idx = {}
for idx, pg in enumerate(reader.pages):
    pageid_to_idx[pg.indirect_reference.idnum] = idx


def dest_page(obj):
    a = obj.get("/A")
    dest = None
    if a and a.get_object().get("/S") == "/GoTo":
        dest = a.get_object().get("/D")
    elif "/Dest" in obj:
        dest = obj["/Dest"]
    if dest is None:
        return None
    if isinstance(dest, str):
        return named.get(dest)
    try:
        d = dest.get_object() if hasattr(dest, "get_object") else dest
        first = d[0]
        ref = first.indirect_reference if hasattr(first, "indirect_reference") else first
        return pageid_to_idx.get(ref.idnum)
    except Exception:
        return None


# collect raw GoTo annotations per source page: (rect, dest_page_idx)
raw = {}
for pno, pg in enumerate(reader.pages):
    if "/Annots" not in pg:
        continue
    for a in pg["/Annots"]:
        o = a.get_object()
        if o.get("/Subtype") != "/Link":
            continue
        act = o.get("/A")
        is_goto = act and act.get_object().get("/S") == "/GoTo"
        if not (is_goto or "/Dest" in o):
            continue
        dp = dest_page(o)
        rect = [float(x) for x in o["/Rect"]]
        raw.setdefault(pno, []).append((rect, dp))

# pull anchor text under each rect with pdfplumber
out = {}
total = 0
with pdfplumber.open("source.pdf") as pdf:
    for pno, items in raw.items():
        page = pdf.pages[pno]
        H = page.height
        for rect, dp in items:
            x0, y0, x1, y1 = rect
            # pdf rect is bottom-left origin; pdfplumber is top-left
            bbox = (max(0, x0 - 1), max(0, H - y1 - 1), min(page.width, x1 + 1), min(H, H - y0 + 1))
            try:
                text = page.crop(bbox).extract_text() or ""
            except Exception:
                text = ""
            text = " ".join(text.split())
            if not text:
                continue
            out.setdefault(str(pno + 1), []).append(
                {"text": text, "dest_page": (dp + 1) if dp is not None else None}
            )
            total += 1

Path("extracted/internal-links.json").write_text(json.dumps(out, indent=1))
print(f"{total} internal links across {len(out)} pages")
# sample
for p in ["100", "101", "102"]:
    for l in out.get(p, []):
        print(f"  p{p} -> p{l['dest_page']}: {l['text'][:70]!r}")
