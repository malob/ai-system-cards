"""PDF | live site | new build composites for the certified-canon hunks of the
D76 batch (experiment 21's hunks.py, re-pointed; the capture widens LEFT to
take in the gutter page labels, which these hunks move). Run from the repo root with
the production build served on :4321:

    uv run --with playwright --with pymupdf --with pillow python \
      docs/experiments/22-gemini-4-carbon-sweep-round1/hunks.py OUTDIR
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

S = Path(sys.argv[1])
(S / "hunks").mkdir(parents=True, exist_ok=True)
# (label, card, page, PDF clip, locator, needle)
H = [("gemini-4-argon pp.87-88 — page label at the cut row's seam", "google-deepmind/gemini-4-argon", 87,
      (60, 600, 552, 760), ".article tr", "only a tiny"),
     ("gemini-4-argon pp.88-89 — page label at the cut row's seam", "google-deepmind/gemini-4-argon", 88,
      (60, 600, 552, 760), ".article tr", "High monitor coverage"),
     ("gemini-4-argon pp.154-155 — page label at the cut row's seam (Figure 3.43)", "google-deepmind/gemini-4-argon", 154,
      (60, 560, 552, 760), ".article tr", "CODEBASE RECONNAISSANCE")]


def web(pg, url, sel, needle, out):
    pg.goto(url, wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    loc = pg.locator(sel).filter(has_text=needle).first
    loc.scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    bb = loc.bounding_box()
    pg.screenshot(path=out, clip={"x": max(0, bb["x"] - 140), "y": bb["y"] - 10,
                                  "width": bb["width"] + 150, "height": min(bb["height"] + 20, 900)})


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 1000}, device_scale_factor=1.5)
    for i, (label, card, page, clip, sel, needle) in enumerate(H):
        doc = pymupdf.open(f"cards/{card}/source.pdf")
        doc[page - 1].get_pixmap(clip=pymupdf.Rect(*clip), dpi=200).save(S / f"hunks/{i}-pdf.png")
        web(pg, f"https://malob.github.io/ai-system-cards/{card}/", sel, needle, S / f"hunks/{i}-live.png")
        web(pg, f"http://localhost:4321/ai-system-cards/{card}/", sel, needle, S / f"hunks/{i}-new.png")
    b.close()

font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
for i, (label, *_) in enumerate(H):
    ims = [Image.open(S / f"hunks/{i}-{k}.png").convert("RGB") for k in ("pdf", "live", "new")]
    W = max(im.width for im in ims)
    heads = ["PDF (source of truth)", "Live site today", "New build (proposed)"]
    Ht = sum(im.height + 50 for im in ims) + 60
    out = Image.new("RGB", (W + 40, Ht), "white")
    d = ImageDraw.Draw(out)
    d.text((20, 15), label, fill="black", font=font)
    y = 60
    for h, im in zip(heads, ims):
        d.text((20, y), h, fill=(150, 60, 30), font=font)
        y += 40
        out.paste(im, (20, y))
        y += im.height + 10
    out.save(S / f"hunks/hunk-{i}.png")
print("ok")
