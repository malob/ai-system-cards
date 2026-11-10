"""PDF | live site | new build composites for the certified-canon hunks of the
D75 batch (experiment 19's hunks.py, re-pointed). Run from the repo root with
the production build served on :4321:

    uv run --with playwright --with pymupdf --with pillow python \
      docs/experiments/21-fable-5-2-sweep-round1/hunks.py OUTDIR
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

S = Path(sys.argv[1])
(S / "hunks").mkdir(parents=True, exist_ok=True)
# (label, card, page, PDF clip, locator, needle)
H = [("opus-5 p.97 — '[tool use]' panel", "anthropic/claude-opus-5", 97,
      (72, 380, 540, 600), ".article .turn", "[tool use]"),
     ("risk-report p.181 — 'Opus- and Sonnet- class'", "anthropic/risk-report-2026-08", 181,
      (72, 240, 540, 300), ".article p, .article li", "bioclassifier exemption for Opus")]


def web(pg, url, sel, needle, out):
    pg.goto(url, wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    loc = pg.locator(sel).filter(has_text=needle).first
    loc.scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    loc.screenshot(path=out)


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
