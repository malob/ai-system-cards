"""Rename extracted figure images by page, composite smasks, dump link URLs."""
import json
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

rows = []
for line in Path("extracted/images-list.txt").read_text().splitlines()[2:]:
    parts = line.split()
    if len(parts) < 16:
        continue
    rows.append({"page": int(parts[0]), "num": int(parts[1]), "type": parts[2], "objid": parts[11]})

figdir = Path("assets/figures")
mapping = {}
counters = {}
i = 0
while i < len(rows):
    r = rows[i]
    if r["type"] != "image":
        i += 1
        continue
    page = r["page"]
    counters[page] = counters.get(page, 0) + 1
    k = counters[page]
    src = figdir / "raw-{:03d}-{:03d}.png".format(page, r["num"])
    dst = figdir / "p{:03d}-{}.png".format(page, k)
    smask = None
    if i + 1 < len(rows) and rows[i + 1]["type"] == "smask" and rows[i + 1]["objid"] == r["objid"]:
        smask = figdir / "raw-{:03d}-{:03d}.png".format(rows[i + 1]["page"], rows[i + 1]["num"])
    img = Image.open(src).convert("RGB")
    if smask and smask.exists():
        alpha = Image.open(smask).convert("L").resize(img.size)
        img = img.convert("RGBA")
        img.putalpha(alpha)
        i += 1
    img.save(dst)
    mapping.setdefault(str(page), []).append(dst.name)
    i += 1

Path("extracted/figures-map.json").write_text(json.dumps(mapping, indent=1))
print("{} figures on {} pages".format(sum(len(v) for v in mapping.values()), len(mapping)))

reader = PdfReader("source.pdf")
links = {}
for pno, pg in enumerate(reader.pages, 1):
    if "/Annots" not in pg:
        continue
    for a in pg["/Annots"]:
        o = a.get_object()
        if o.get("/Subtype") == "/Link" and "/A" in o and "/URI" in o["/A"]:
            uri = str(o["/A"]["/URI"])
            links.setdefault(str(pno), [])
            if uri not in links[str(pno)]:
                links[str(pno)].append(uri)
print("links on {} pages".format(len(links)))
Path("extracted/links.json").write_text(json.dumps(links, indent=1))
