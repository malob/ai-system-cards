import sys, json
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1680, "height": 1100}, device_scale_factor=1.5)
    pg.goto(url, wait_until="networkidle")
    pg.wait_for_timeout(1500)
    # wait for webfonts (italics judged too early read as upright) and hide the
    # sticky masthead, which otherwise covers rows of tall full-page captures
    pg.evaluate("() => document.fonts.ready")
    pg.add_style_tag(content=".masthead, header { position: static !important; }")
    items = pg.evaluate("""() => {
      const marks = [...document.querySelectorAll('.pagemark')];
      const pageOf = el => { let p = null; for (const m of marks) { if (m.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING || m === el || el.contains(m)) { if (!el.contains(m)) p = m.id; } } return p; };
      const els = [...document.querySelectorAll('.article .table-wrap, .article .box, .article pre')];
      return els.map((e, i) => { e.setAttribute('data-shot', i); const r = e.getBoundingClientRect(); return {i, kind: e.className || e.tagName, page: pageOf(e), h: Math.round(r.height)}; });
    }""")
    for it in items:
        el = pg.locator(f'[data-shot="{it["i"]}"]')
        el.scroll_into_view_if_needed()
        pg.wait_for_timeout(150)
        # include the caption that follows
        box = el.bounding_box(); sy = pg.evaluate("() => window.scrollY")
        nxt = pg.evaluate(f"""() => {{ const e = document.querySelector('[data-shot="{it["i"]}"]'); const n = e.nextElementSibling; const r = n && /caption/.test(n.className) ? n.getBoundingClientRect() : null; return r ? r.bottom - e.getBoundingClientRect().top : null; }}""")
        h = max(box["height"], nxt or 0) + 8
        fn = f"{out}/{it['i']:02d}-{it['page']}-{it['kind'].split()[0]}.png"
        pg.screenshot(path=fn, clip={"x": box["x"] - 90, "y": box["y"] + sy - 8, "width": box["width"] + 100, "height": min(h, 6000)}, full_page=True)
        it["file"] = fn
    json.dump(items, open(f"{out}/index.json", "w"), indent=1)
    print(len(items))
    b.close()
