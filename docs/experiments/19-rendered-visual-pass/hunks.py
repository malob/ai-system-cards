import sys, pymupdf
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
H = [("fable-5 p.45", "claude-fable-5", 45, (72, 305, 540, 345), "pkill"),
     ("opus-5 p.87", "claude-opus-5", 87, (72, 62, 540, 112), "WebSearch"),
     ("fable-5-1 Table 8.1.A caption", "claude-fable-5-1", 168, (72, 60, 540, 125), "for evaluation details of earlier")]
def web(pg, url, needle, out):
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(800)
    loc = pg.locator(".article p, .article li, .article .caption").filter(has_text=needle).first
    loc.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    loc.screenshot(path=out)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 1000}, device_scale_factor=1.5)
    for i, (label, card, page, clip, needle) in enumerate(H):
        doc = pymupdf.open(f"cards/anthropic/{card}/source.pdf")
        doc[page - 1].get_pixmap(clip=pymupdf.Rect(*clip), dpi=200).save(f"{S}/hunks/{i}-pdf.png")
        web(pg, f"https://malob.github.io/ai-system-cards/anthropic/{card}/", needle, f"{S}/hunks/{i}-live.png")
        web(pg, f"http://localhost:4321/ai-system-cards/anthropic/{card}/", needle, f"{S}/hunks/{i}-new.png")
    b.close()
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
for i, (label, *_ ) in enumerate(H):
    ims = [Image.open(f"{S}/hunks/{i}-{k}.png").convert("RGB") for k in ("pdf", "live", "new")]
    W = max(im.width for im in ims)
    heads = ["PDF (source of truth)", "Live site today", "New build (proposed)"]
    Ht = sum(im.height + 50 for im in ims) + 60
    out = Image.new("RGB", (W + 40, Ht), "white"); d = ImageDraw.Draw(out)
    d.text((20, 15), label, fill="black", font=font); y = 60
    for h, im in zip(heads, ims):
        d.text((20, y), h, fill=(150, 60, 30), font=font); y += 40
        out.paste(im, (20, y)); y += im.height + 10
    out.save(f"{S}/hunks/hunk-{i}.png")
print("ok")
