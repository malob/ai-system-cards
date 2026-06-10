"""Docling table extraction with a persistent per-page cache (D14: docling is
the table-structure authority). Converts docling bottom-left bboxes to PyMuPDF
top-left, emits clean HTML for the v1 renderer + verifier.

    uv run --with docling --with pymupdf python pipeline/generate/tables.py 20 252 253
    (no args = all pages with v1 tables)
"""

import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "cards/anthropic/claude-fable-5"
CACHE = REPO / "pipeline/.cache/tables.json"


def _load() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def get_tables(page_no: int, oracle_page: dict | None = None) -> list[dict]:
    """[{bbox:[x0,y0,x1,y1] top-left, html}] for a page (cached). Empty if
    uncached. Post-processing on load:
    - strip docling-absorbed <caption> (D23: captions are our block, never in
      the table box — also they duplicated);
    - repair column rotation against oracle span geometry (docling TableFormer
      cyclically mis-assigns columns on wide numeric tables, e.g. 4.4.2.A)."""
    out = []
    for t in _load().get(str(page_no), []):
        html = re.sub(r"<caption>.*?</caption>", "", t["html"], flags=re.S)
        if oracle_page is not None:
            # split BEFORE rotation repair: a glued cell defeats x-matching,
            # leaving its row rotated; once split, the row becomes repairable
            html = _merge_fragment_rows(html, t["bbox"], oracle_page)
            html = _split_glued_cells(html, t["bbox"], oracle_page)
            html = _resplit_misjoined_cells(html, t["bbox"], oracle_page)
            html = _extend_truncated_cells(html, t["bbox"], oracle_page)
            html = _repair_rotation(html, t["bbox"], oracle_page)
            html = _restyle_cells(html, t["bbox"], oracle_page)
            html = _inject_fnrefs(html, t["bbox"], oracle_page)
        out.append({**t, "html": html})
    return out


def _table_spans(oracle_page, bbox):
    for s in oracle_page["spans"]:
        sb = s["bbox"]
        if (bbox[0] - 3 <= sb[0] and sb[2] <= bbox[2] + 3
                and bbox[1] - 3 <= sb[1] and sb[3] <= bbox[3] + 3):
            yield s


def _merge_fragment_rows(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling splits one tall logical row into several <tr>s (welfare
    interview tables: a 4-line question becomes a row + fragment rows, often
    with fragments landing in the WRONG columns). A fragment cell's text is a
    mid-chain run of some column chain whose PREFIX is an existing cell of
    the previous row: merge it into that cell and drop the fragment row."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    chains = _column_chains(spans)
    if not chains:
        return html
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    out_rows = []
    for r in rows:
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        frags = [_cell_sq(c) for _, _, c in tags if _cell_sq(c)]
        merged_all = bool(frags) and out_rows and not any(
            "rowspan" in a or "colspan" in a for _, a, _ in tags)
        if merged_all:
            prev = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", out_rows[-1], re.S)
            prev_cells = [c for _, _, c in prev]
            plan = []  # (prev_cell_idx, full_text)
            for f in frags:
                hit = None
                for ch in chains:
                    accs = [""]
                    for s in ch:
                        accs.append(accs[-1] + _squash(s["text"]))
                    for k in range(1, len(ch)):
                        for m in range(k + 1, len(ch) + 1):
                            if accs[m][len(accs[k]):] != f:
                                continue
                            for ci, pc in enumerate(prev_cells):
                                if _cell_sq(pc) == accs[k]:
                                    cand = (ci, " ".join(
                                        x["text"].strip() for x in ch[:m]))
                                    hit = cand if hit is None else hit
                    if hit:
                        break
                if not hit:
                    merged_all = False
                    break
                plan.append(hit)
            if merged_all and len({ci for ci, _ in plan}) == len(plan):
                import html as _h
                for ci, full in plan:
                    prev_cells[ci] = _h.escape(full, quote=False)
                out_rows[-1] = "<tr>" + "".join(
                    f"<{tg}{a}>{c}</{tg}>"
                    for (tg, a, _), c in zip(prev, prev_cells)) + "</tr>"
                continue
        out_rows.append(r)
    if len(out_rows) == len(rows):
        return html
    # reassemble in order, preserving everything outside the rows
    out = html
    for r in rows:
        pass
    body = "".join(out_rows)
    return re.sub(r"(<tbody>).*(</tbody>)", lambda m: m.group(1) + body + m.group(2), html, flags=re.S) \
        if "<tbody>" in html else re.sub(r"(<table[^>]*>).*(</table>)", lambda m: m.group(1) + body + m.group(2), html, flags=re.S)


def _split_glued_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes glues two cells' values into one cell, leaving an
    empty cell in the row ('88.1 97.5' | '' — p.85 Sonnet row). When a glued
    cell's text equals the concatenation of exactly two oracle spans and the
    row has exactly one empty cell, split by span x-order."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s.get("zone") != "fnref"]
    sq = {_squash(s["text"]): s for s in spans}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        empties = [i for i, (_, _, c) in enumerate(tags) if not _cell_sq(c)]
        if len(empties) != 1:
            continue
        for i, (tg, attr, c) in enumerate(tags):
            plain = _cell_sq(c)
            if not plain or i == empties[0]:
                continue
            parts = plain.split()  # squash removed spaces; split won't work —
            # find a 2-span partition instead
            hit = None
            for k1, s1 in sq.items():
                if plain.startswith(k1) and plain[len(k1):] in sq:
                    hit = (s1, sq[plain[len(k1):]])
                    break
            if not hit:
                continue
            a, b2 = sorted(hit, key=lambda s: s["bbox"][0])
            # the two pieces must be SIDE BY SIDE (different columns): two
            # stacked lines are one wrapped cell, not a glue (p.253 Gemini)
            if b2["bbox"][0] < a["bbox"][2] - 2:
                continue
            cells = [c2 for _, _, c2 in tags]
            # place by x-order: glued cell gets the piece nearer its column,
            # empty cell gets the other — empty left of glued => takes the
            # left span
            left_first = empties[0] < i
            cells[i] = b2["text"].strip() if left_first else a["text"].strip()
            cells[empties[0]] = a["text"].strip() if left_first else b2["text"].strip()
            rebuilt = "<tr>" + "".join(
                f"<{tg2}{at2}>{c2}</{tg2}>" for (tg2, at2, _), c2 in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
            break
    return out


def _inject_fnrefs(html: str, bbox: list, oracle_page: dict) -> str:
    """Footnote refs inside tables: docling drops superscripts, so re-attach
    `<sup>[^N]</sup>` after the nearest-left text of each in-table ref span
    (the FN1 major: refs 11/12/28/29 in the safeguards/capabilities tables)."""
    spans = list(_table_spans(oracle_page, bbox))
    out = html
    for ref in spans:
        if ref.get("zone") != "fnref":
            continue
        n = ref["text"].strip()
        rb = ref["bbox"]
        left = [s for s in spans
                if s.get("zone") == "body" and s["bbox"][2] <= rb[0] + 2
                and min(s["bbox"][3], rb[3]) - max(s["bbox"][1], rb[1]) > 0]
        if not left:
            continue
        anchor = max(left, key=lambda s: s["bbox"][2])["text"].strip()
        if not anchor:
            continue
        # absorb a stray literal digit docling captured from the superscript
        # ('GDPval-AA 29' -> 'GDPval-AA<sup>[^29]</sup>')
        pat = re.compile("(" + re.escape(anchor) + r")(\s*" + re.escape(n) + r"\b)?(?![^<]*</sup>)")
        out, k = pat.subn(lambda m: m.group(1) + f"<sup>[^{n}]</sup>", out, count=1)
    return out


def _restyle_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Recover bold (best-score) and underline (second-best, FL-09) styling
    from oracle facts. Cells are segmented GEOMETRICALLY: each row's y-band
    yields its candidate spans (plus wrapped/sub-line continuations), each
    cell's text is greedily split into those spans, and every segment is
    styled by its own span's flags — a bold '97.88%' inside the cell
    '97.88% (± 0.66%)' gets <b> on just the bold part."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s.get("zone") != "fnref"]
    rules = oracle_page.get("rules", [])
    # bold only signifies when it DEVIATES from the table's dominant weight:
    # some tables (2.2.1.A) are set entirely in Lora-Bold, where the visual
    # weight reads regular and 'bold' carries no information (owner-flagged).
    # white header text excluded from the count (the 4.4.2 regression)
    boldish = [s for s in spans
               if s["text"].strip() and s.get("color") not in ("#ffffff", "#faf9f5")]
    bold_share = sum(1 for s in boldish if s.get("bold")) / max(1, len(boldish))
    # suppress only NEAR-UNIFORM bold (the all-Lora-Bold case): a table with
    # bold row labels + bold best scores can reach ~0.6 share and its bolds
    # are exactly the legend's promise (p.82/98 missing-bold cluster)
    bold_signifies = bold_share < 0.9

    def underlined(s):
        sb = s["bbox"]
        for ru in rules:
            rb = ru["bbox"]
            if (sb[3] - 2.5 <= rb[1] <= sb[3] + 5.0
                    and min(sb[2], rb[2]) - max(sb[0], rb[0]) > 0.5 * (sb[2] - sb[0])):
                return True
        return False

    spans_xy = _row_spans_xy(oracle_page, bbox)
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        # row's spans: in band, plus wrapped/sub-line continuations hanging
        # below a member (the small '± 1.4%' second line)
        chosen = [s for s in spans if s["text"].strip()
                  and band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1]]
        for _ in range(3):
            for s in spans:
                if s in chosen or not s["text"].strip():
                    continue
                sb = s["bbox"]
                if any(min(sb[2], m["bbox"][2]) - max(sb[0], m["bbox"][0]) > 0
                       and -1 <= sb[1] - m["bbox"][3] < 9 for m in chosen):
                    chosen.append(s)
        # pool: squash key -> span instances in x-order (cells consume L->R)
        pool: dict[str, list] = {}
        for s in sorted(chosen, key=lambda s: (s["bbox"][0], s["bbox"][1])):
            pool.setdefault(_squash(s["text"]), []).append(s)
        used: dict[str, int] = {}

        def segment(sq):
            """Greedy longest-prefix split of a cell's squash into pool keys."""
            segs, pos = [], 0
            while pos < len(sq):
                best = None
                for k in pool:
                    if k and sq.startswith(k, pos) and (best is None or len(k) > len(best)):
                        best = k
                if best is None:
                    return None
                segs.append(best)
                pos += len(best)
            return segs

        cells = [c for _, _, c in tags]
        changed = False
        for i, (c, p2) in enumerate(zip(cells, plain)):
            if not p2 or "<" in c:
                continue
            segs = segment(p2)
            if not segs:
                continue
            # map each segment's squash range back to the raw cell text
            raw_idx = [j for j, ch in enumerate(c) if not ch.isspace()]
            pieces, cur, sq_pos = [], 0, 0
            styled_any = False
            for k in segs:
                inst = pool[k][min(used.get(k, 0), len(pool[k]) - 1)]
                used[k] = used.get(k, 0) + 1
                wraps = []
                if inst.get("bold") and bold_signifies and len(k) >= 2:
                    wraps.append(("<b>", "</b>"))
                if underlined(inst) and len(k) >= 2:
                    wraps.append(("<u>", "</u>"))
                st, en = raw_idx[sq_pos], raw_idx[sq_pos + len(k) - 1] + 1
                sq_pos += len(k)
                if wraps:
                    seg_text = c[st:en]
                    for o, cl in wraps:
                        seg_text = o + seg_text + cl
                    pieces.append(c[cur:st] + seg_text)
                    cur = en
                    styled_any = True
            pieces.append(c[cur:])
            if styled_any:
                cells[i] = "".join(pieces)
                changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c2}</{tg}>" for (tg, a, _), c2 in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


_QUOTE_FOLD = {0x2019: 0x27, 0x2018: 0x27, 0x201C: 0x22, 0x201D: 0x22}


def _squash(s: str) -> str:
    """Comparison key: whitespace-free, quote-variant-folded (docling
    normalizes curly quotes; the oracle preserves the PDF's). Output text
    always comes from the oracle spans, so fidelity is unaffected."""
    return re.sub(r"\s+", "", s).translate(_QUOTE_FOLD)


def _cell_sq(c: str) -> str:
    """Squash of a cell's visible text: tags stripped, HTML entities decoded
    (docling emits &#x27; etc., which can never match oracle span text)."""
    import html as _h
    return _squash(_h.unescape(re.sub(r"<[^>]+>", "", c)))


def _row_spans_xy(oracle_page, bbox):
    """squash text -> [(x0, y_center)] for body spans inside the table bbox.
    Includes COMPOSITES: a wrapped cell renders as 2-3 stacked spans sharing a
    left edge ('Claude Mythos' / 'Preview') — their concatenation is offered
    as a candidate too, keyed at the stack's x0 and mean y."""
    spans = [s for s in _table_spans(oracle_page, bbox) if s["text"].strip()]
    m: dict[str, list[tuple[float, float]]] = {}
    for s in spans:
        sb = s["bbox"]
        m.setdefault(_squash(s["text"]), []).append((sb[0], (sb[1] + sb[3]) / 2))
    # stacked runs: same x0 (±2), vertically adjacent (gap < 9pt)
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        for i in range(len(col)):
            for j in range(i + 1, min(i + 6, len(col))):
                if col[j]["bbox"][1] - col[j - 1]["bbox"][3] >= 9:
                    break
                run = col[i:j + 1]
                key = _squash("".join(s["text"] for s in run))
                # keyed at the TOP span's y: cells are top-aligned, so a
                # wrapped cell's first line is coplanar with its single-line
                # row-mates (mean y drifted 7pt and broke band agreement)
                y0 = (run[0]["bbox"][1] + run[0]["bbox"][3]) / 2
                m.setdefault(key, []).append((run[0]["bbox"][0], y0))
    return m


def _row_band(plain, cand, tol=7.0):
    """Median y of the row's uniquely-matchable cells (usually the model
    name) — the anchor that ties HTML rows back to page geometry."""
    ys = [cand[p][0][1] for p in plain if p and len(cand.get(p, [])) == 1]
    if not ys:
        return None
    ys.sort()
    ymed = ys[len(ys) // 2]
    # all anchors must agree (a stray unique match off-row poisons the band)
    if ys[-1] - ys[0] > tol:
        return None
    return ymed - tol, ymed + tol


def _resplit_misjoined_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes splits two cells' text at the WRONG boundary
    ('99.70% (±' | '0.17%) 0.09% (± 0.07%)'). When two adjacent cells match
    no span individually but their concatenation equals exactly two banded
    spans, re-split at the true span boundary."""
    spans_xy = _row_spans_xy(oracle_page, bbox)
    sq2text = {_squash(s["text"]): s["text"].strip()
               for s in _table_spans(oracle_page, bbox)}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        banded = {k for k, v in spans_xy.items() if any(band[0] <= y <= band[1] for _, y in v)}
        cells = [c for _, _, c in tags]
        changed = False
        for i in range(len(plain) - 1):
            if plain[i] in banded or plain[i + 1] in banded or not plain[i]:
                continue
            joined = plain[i] + plain[i + 1]
            for k1 in banded:
                if joined.startswith(k1) and joined[len(k1):] in banded:
                    cells[i], cells[i + 1] = sq2text[k1], sq2text[joined[len(k1):]]
                    changed = True
                    break
            if changed:
                break
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal):
    """Rebuild a garbled row directly from its banded spans (x-order), merging
    stacked wraps and sub-line annotations (the small '±1.4%' under a score).
    Fires only when the merged-cell count == modal columns AND the char
    multiset of the row's cells equals the spans' — pure re-segmentation."""
    inviz = re.compile("[\u200b\u200c\u200d\ufeff\u00ad]")
    allspans = [s for s in _table_spans(oracle_page, bbox)
                if inviz.sub("", s["text"]).strip() and s.get("zone") != "fnref"]
    chosen = [s for s in allspans
              if band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1]]
    # absorb sub-lines: x-overlapping spans hanging <= 5pt below a member
    # (wrapped cell second lines, small ± uncertainty rows)
    for _ in range(2):
        for s in allspans:
            if s in chosen:
                continue
            sb = s["bbox"]
            for m in chosen:
                mb = m["bbox"]
                if (min(sb[2], mb[2]) - max(sb[0], mb[0]) > 0
                        and -1 <= sb[1] - mb[3] <= 5):
                    chosen.append(s)
                    break
    chosen.sort(key=lambda s: s["bbox"][0])
    # merge into cells by x-range overlap (a sub-span may start a few pt
    # right of its column's number when centered)
    cells2 = []  # [x0, x1, [spans]]
    for s in chosen:
        sb = s["bbox"]
        if cells2 and min(sb[2], cells2[-1][1]) - max(sb[0], cells2[-1][0]) > 0:
            cells2[-1][1] = max(cells2[-1][1], sb[2])
            cells2[-1][2].append(s)
        else:
            cells2.append([sb[0], sb[2], [s]])
    # re-segmentation can only UN-glue: never fewer cells than docling
    # emitted (x-overlapping true columns fuse and are correctly rejected
    # here, e.g. the wide sentence-cell welfare tables)
    if len(cells2) < max(2, len(tags)):
        return None
    texts = []
    for _, _, members in cells2:
        members.sort(key=lambda s: (round(s["bbox"][1]), s["bbox"][0]))
        texts.append(inviz.sub("", " ".join(s["text"].strip() for s in members)).strip())
    have = sorted(inviz.sub("", "".join(plain)))
    want = sorted(_squash("".join(texts)))
    if have != want:
        # tolerate surplus equal to in-band fnref digits docling absorbed into
        # a cell ('Sonnet 4.6' + ref '4' -> 'Sonnet 4.64', p.51); the ref is
        # re-injected as a proper <sup> afterwards
        from collections import Counter as _C2
        fn = "".join(_squash(s["text"]) for s in _table_spans(oracle_page, bbox)
                     if s.get("zone") == "fnref"
                     and band[0] <= (s["bbox"][1] + s["bbox"][3]) / 2 <= band[1])
        if not fn or _C2(have) - _C2(sorted(fn)) != _C2(want):
            return None
    tg = tags[0][0]
    return "<tr>" + "".join(f"<{tg}>{c}</{tg}>" for c in texts) + "</tr>"


def _column_chains(spans):
    """Maximal vertical chains of spans sharing a left-edge cluster with
    < 9pt line gaps — the geometry of a wrapped (multi-line) table cell."""
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    chains = []
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        cur = [col[0]]
        for s in col[1:]:
            if s["bbox"][1] - cur[-1]["bbox"][3] < 9:
                cur.append(s)
            else:
                chains.append(cur)
                cur = [s]
        chains.append(cur)
    return [c for c in chains if len(c) > 1]


def _extend_truncated_cells(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling sometimes drops the trailing line(s) of a wrapped cell
    ('Claude Mythos' sans 'Preview' p.72; a tall interview cell sans its
    final 'conversations?' line p.311). When a cell's text equals a
    consecutive span run of an x-column and the run's IMMEDIATE continuation
    (vertically adjacent, < 9pt) is claimed by no cell in the table, extend
    the cell with that continuation."""
    spans = [s for s in _table_spans(oracle_page, bbox)
             if s["text"].strip() and s.get("zone") != "fnref"]
    by_x: dict[float, list] = {}
    for s in spans:
        key = next((k for k in by_x if abs(k - s["bbox"][0]) <= 2), None)
        by_x.setdefault(s["bbox"][0] if key is None else key, []).append(s)
    cols = []
    for col in by_x.values():
        col.sort(key=lambda s: s["bbox"][1])
        cols.append(col)
    spans_xy = _row_spans_xy(oracle_page, bbox)
    all_cells = {_cell_sq(c)
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", html, re.S)}
    out = html
    for r in re.findall(r"<tr>.*?</tr>", html, re.S):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        plain = [_cell_sq(c) for _, _, c in tags]
        band = _row_band(plain, spans_xy)
        cells = [c for _, _, c in tags]
        changed = False
        for i, p2 in enumerate(plain):
            # without a band (a mega-cell continuation row too tall for
            # composite anchors, p.311) the text match itself is the anchor —
            # but only for substantial text, where it's unique
            if not p2 or (band is None and len(p2) < 12):
                continue
            cand = []
            for col in cols:
                for st in range(len(col)):
                    y0 = (col[st]["bbox"][1] + col[st]["bbox"][3]) / 2
                    if band is not None and not band[0] <= y0 <= band[1]:
                        continue
                    acc = ""
                    for j in range(st, len(col)):
                        acc += _squash(col[j]["text"])
                        if len(acc) > len(p2):
                            break
                        if acc == p2:
                            # immediate adjacent continuation run below
                            tail = []
                            k = j + 1
                            while (k < len(col)
                                   and col[k]["bbox"][1] - col[k - 1]["bbox"][3] < 9):
                                tail.append(col[k])
                                k += 1
                            if tail and all(_squash(s["text"]) not in all_cells
                                            for s in tail):
                                cand.append(col[st:j + 1] + tail)
                            break
            if len(cand) != 1:
                continue
            import html as _h
            cells[i] = _h.escape(" ".join(s["text"].strip() for s in cand[0]),
                                 quote=False)
            changed = True
        if changed:
            rebuilt = "<tr>" + "".join(
                f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, cells)) + "</tr>"
            out = out.replace(r, rebuilt, 1)
    return out


def _repair_rotation(html: str, bbox: list, oracle_page: dict) -> str:
    """Docling TableFormer cyclically mis-assigns columns on wide numeric
    tables. Repair per row from geometry: anchor the row's y-band via its
    unique-text cells, take each cell's span x within that band (duplicate
    values consume banded x's in order), and reorder cells by x. Rows that
    can't be fully matched are left alone — never half-repair."""
    rows = re.findall(r"<tr>.*?</tr>", html, re.S)
    if len(rows) < 3:
        return html
    spans_xy = _row_spans_xy(oracle_page, bbox)
    from collections import Counter as _C
    _counts = _C()
    for r in rows:
        tg = re.findall(r"<(t[hd])([^>]*)>", r)
        if not any("colspan" in a or "rowspan" in a for _, a in tg):
            _counts[len(tg)] += 1
    modal = _counts.most_common(1)[0][0] if _counts else 0

    out = html
    for ri, r in enumerate(rows):
        tags = re.findall(r"<(t[hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
        if len(tags) < 2 or any("colspan" in a or "rowspan" in a for _, a, _ in tags):
            continue
        plain = [_cell_sq(c) for _, _, c in tags]
        if any(not p for p in plain):
            continue
        band = _row_band(plain, spans_xy)
        if band is None:
            continue
        from collections import Counter
        need = Counter(plain)
        pool = {t2: sorted(x for x, y in spans_xy.get(t2, []) if band[0] <= y <= band[1])
                for t2 in need}
        if any(len(pool[t2]) < n2 for t2, n2 in need.items()):
            # last resort for garbled rows (mis-glued AND rotated, p.269/297):
            # rebuild the whole row from the band's spans in x-order, but only
            # under char-multiset equality — same content, re-segmented
            rb = _rebuild_row(r, tags, plain, band, oracle_page, bbox, modal)
            if rb:
                out = out.replace(r, rb, 1)
            continue
        if ri == 0:
            continue
        taken = {t2: 0 for t2 in need}
        cell_x = []
        for p2 in plain:
            cell_x.append(pool[p2][taken[p2]])
            taken[p2] += 1
        if len(set(cell_x)) != len(cell_x):
            continue
        perm = sorted(range(len(cell_x)), key=lambda i: cell_x[i])
        if perm == list(range(len(cell_x))):
            continue
        inner = [tags[i][2] for i in perm]
        rebuilt = "<tr>" + "".join(
            f"<{tg}{a}>{c}</{tg}>" for (tg, a, _), c in zip(tags, inner)) + "</tr>"
        out = out.replace(r, rebuilt, 1)
    return out


def _clean_html(html: str) -> str:
    html = re.sub(r"\s+", " ", html).replace("> <", "><").strip()
    return html


def extract(page_nos: list[int]):
    import fitz
    from docling.document_converter import DocumentConverter

    src = fitz.open(CARD / "source.pdf")
    conv = DocumentConverter()
    cache = _load()
    for pno in page_nos:
        H = src[pno - 1].rect.height
        mini = fitz.open()
        mini.insert_pdf(src, from_page=pno - 1, to_page=pno - 1)
        mp = Path(tempfile.mkdtemp()) / "p.pdf"
        mini.save(mp)
        doc = conv.convert(mp).document
        entries = []
        for t in doc.tables:
            bb = t.prov[0].bbox
            # docling BOTTOMLEFT -> PyMuPDF TOPLEFT (same page dimensions)
            x0, x1 = bb.l, bb.r
            y0, y1 = H - bb.t, H - bb.b
            entries.append({"bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                            "html": _clean_html(t.export_to_html(doc))})
        cache[str(pno)] = entries
        print(f"p.{pno}: {len(entries)} table(s)")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1))
    print(f"cached {len(cache)} pages -> {CACHE}")


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:]]
    if not pages:
        import re as _re
        pages = sorted({int(m) for p in (CARD / "sections").glob("*.md")
                        for blk in _re.findall(r"<table.*?</table>", p.read_text(), _re.S)
                        for m in _re.findall(r"<!-- p\.(\d+) -->",
                                             p.read_text()[:p.read_text().find(blk)][-4000:])[-1:]})
        # simpler: just pass pages explicitly; fall back to known table pages
        pages = pages or [19, 20, 49, 51, 61, 72, 73, 77, 79, 80, 82, 85, 86, 89, 91,
                          95, 96, 98, 235, 236, 244, 252, 253, 264, 269, 297,
                          309, 310, 311, 312, 313, 314, 315, 316, 317, 318]
    extract(pages)
