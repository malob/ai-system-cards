"""Extract a card's figure images from its PDF → assets/figures/ + figures-map.json.

Run ONCE when onboarding a card. The figure map it writes is committed and read by
`generate/run.py` and `verifier/calibrate.py`; it is not part of every regen.

The raw-image dump is not scripted here (it needs poppler's `pdfimages`) — produce it
first, then run this:

    cd cards/<vendor>/<slug>
    pdfimages -png  source.pdf assets/figures/raw          # raw-PPP-NNN.png images
    pdfimages -list source.pdf > extracted/images-list.txt # the image inventory
    uv run --with pillow python ../../../pipeline/generate/extract_figures.py

This renames each image to pPPP-K.png (page, k-th figure on that page), composites any
soft-mask (smask) as alpha, and writes extracted/figures-map.json (page → [filenames]).
"""
import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "cards/anthropic/claude-fable-5"
figdir = CARD / "assets/figures"

rows = []
for line in (CARD / "extracted/images-list.txt").read_text().splitlines()[2:]:
    parts = line.split()
    if len(parts) < 16:
        continue
    rows.append({"page": int(parts[0]), "num": int(parts[1]), "type": parts[2], "objid": parts[11]})

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

(CARD / "extracted/figures-map.json").write_text(json.dumps(mapping, indent=1))
print("{} figures on {} pages".format(sum(len(v) for v in mapping.values()), len(mapping)))
