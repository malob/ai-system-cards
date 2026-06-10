"""Blocks → v1 markdown dialect (generation-design.md): the existing site and
the calibrated verifier consume the output unchanged."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "verifier"))
from assemble import block_text_and_marks  # noqa: E402


SYNTAX = {
    "bold": ("**", "**"),
    "italic": ("*", "*"),
    "chip": (":chip[", "]"),
    # placeholder: plain text until the renderer gains :ph (FL-07/D17)
}


def _apply_marks(text: str, marks: list) -> str:
    """Apply ALL mark edits in one strictly end-first pass so earlier offsets
    never go stale. (A two-pass version replaced fnrefs '11'->'[^11]' first,
    shifting every later mark by +3 per ref — the 'in Section 6.' bug.)

    Equal-position ordering (inserts at the same index stack right-to-left:
    the LAST insert ends up LEFTMOST):
    - an OPEN for following text processes before a CLOSE for preceding text,
      so the close lands left of the open ("]:chip[" not ":chip[]");
    - among opens, inner (shorter) first so outer ends up leftmost;
    - among closes, outer (earlier start) first so inner ends up leftmost."""
    ops = []  # (pos, phase, tiebreak, edit)
    for kind, a, b, data in marks:
        if kind == "fnref":
            ops.append((a, 0, 0, lambda t, a=a, b=b, d=data: t[:a] + f"[^{d}]" + t[b:]))
        elif kind == "link":
            ops.append((a, 1, b, lambda t, a=a: t[:a] + "[" + t[a:]))
            ops.append((b, 2, a, lambda t, b=b, d=data: t[:b] + f"]({d})" + t[b:]))
        elif kind in SYNTAX:
            o, c = SYNTAX[kind]
            ops.append((a, 1, b, lambda t, a=a, o=o: t[:a] + o + t[a:]))
            ops.append((b, 2, a, lambda t, b=b, c=c: t[:b] + c + t[b:]))
    out = text
    for _, _, _, edit in sorted(ops, key=lambda x: (-x[0], x[1], x[2])):
        out = edit(out)
    return out


def _hyphen_join(text: str) -> str:
    text = re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1", text)  # A1; keep suspended compounds ("single- and")
    text = text.replace("​", "").replace("­", "")  # zero-width, soft hyphen
    return re.sub(r"[ \t]{2,}", " ", text).strip()   # collapse layout double-spaces (A2)


def _render_body(blk: dict, page, oracle_pages, chips, marker_if_new, emit_marker) -> str:
    """Block lines → marked-up text. If the block carries page_break=(pno, i),
    render in two segments with the page marker spliced inline at the break
    (v1's convention: 'word<!-- p.N --> continuation')."""
    if blk.get("page_break"):
        bp, i = blk["page_break"]
        first = {**blk, "lines": blk["lines"][:i], "page_break": None}
        rest = {**blk, "lines": blk["lines"][i:], "page_break": None}
        t1, m1 = block_text_and_marks(first, page, chips)
        t2, m2 = block_text_and_marks(rest, oracle_pages[bp - 1], chips)
        marker_if_new(bp)
        mk = emit_marker(True)
        return (_hyphen_join(_apply_marks(t1, m1)).strip()
                + mk + " " + _hyphen_join(_apply_marks(t2, m2)).strip())
    text, marks = block_text_and_marks(blk, page, chips)
    return _hyphen_join(_apply_marks(text, marks)).strip()


def serialize_blocks(blocks: list[dict], page_of_prev_block: int, oracle_pages, chips) -> tuple[str, int]:
    """Render an ordered block list to markdown. Emits a `<!-- p.N -->` marker
    whenever the page advances. Returns (markdown, last_page)."""
    out = []
    cur_page = page_of_prev_block
    footnotes = []
    transcript_open = False
    pending_marker = ""
    last_type = None

    def marker_if_new(pno):
        # markers are buffered: standalone between blocks, but INLINE inside a
        # list item that continues a list across a page break (v1's PM-03
        # lesson — a standalone marker between items splits the <ul>)
        nonlocal cur_page, pending_marker
        if pno != cur_page:
            pending_marker = f"<!-- p.{pno} -->"
            cur_page = pno

    def emit_marker(inline_into_item: bool) -> str:
        nonlocal pending_marker
        m, pending_marker = pending_marker, ""
        if not m:
            return ""
        if inline_into_item:
            return m
        out.append(m + "\n\n")
        return ""

    def close_transcript():
        nonlocal transcript_open
        if transcript_open:
            out.append("::::\n")
            transcript_open = False

    for blk in blocks:
        pno = blk["page"]
        page = oracle_pages[pno - 1]
        t = blk["type"]
        if t == "footnote":
            footnotes.append(blk)
            continue
        if t in ("turn", "commentary"):
            marker_if_new(pno)
            inline_marker = ""
            emit_marker(False)
            if not transcript_open:
                out.append("::::transcript\n")
                transcript_open = True
        else:
            close_transcript()
            marker_if_new(pno)
            inline_marker = emit_marker(inline_into_item=(t == "item" and last_type == "item"))

        q = "> " if blk.get("quote") else ""
        if t == "heading":
            text, _ = block_text_and_marks(blk, page, chips)
            out.append("#" * blk["level"] + " " + text.strip() + "\n")
        elif t == "paragraph":
            out.append(q + _render_body(blk, page, oracle_pages, chips, marker_if_new, emit_marker) + "\n")
        elif t == "item":
            body = _render_body(blk, page, oracle_pages, chips, marker_if_new, emit_marker)
            # 2-space nesting inside quotes (4 spaces would read as code there)
            indent = ("  " if q else "    ") * blk.get("level", 0)
            m = re.match(r"^[‌ ]*(\d{1,2})[.)]​?\s*", body)
            if m:  # ordered item: keep the number, real space after it
                out.append(f"{q}{indent}{m.group(1)}. " + inline_marker + body[m.end():] + "\n")
            else:
                body = re.sub(r"^(\**)[●•◦▪‣○​‌ ]+", r"\1", body.lstrip("●•◦▪‣○​‌ "))
                out.append(f"{q}{indent}- " + inline_marker + body + "\n")
        elif t == "figure":
            out.append(f"![{blk['alt']}](assets/figures/{blk['file']})\n")
            if blk["caption_lines"]:
                cap_blk = {"lines": blk["caption_lines"], "page": pno}
                text, marks = block_text_and_marks(cap_blk, page, chips)
                bolds = [m for m in marks if m[0] == "bold"]
                text = _hyphen_join(text).strip()
                if bolds and bolds[0][1] <= 1:
                    lead_end = bolds[0][2]
                    out.append(f"*__{text[:lead_end].strip()}__{text[lead_end:]}*\n")
                else:
                    out.append(f"*{text}*\n")
        elif t == "turn":
            # multi-paragraph turns: gap-recorded breaks UNION short-line
            # breaks (PDF intra-turn paragraphs are plain hard returns with no
            # extra spacing — the signal is a line ending short of the right edge)
            maxx = max(l["bbox"][2] for l in blk["lines"])
            geo = [i + 1 for i, l in enumerate(blk["lines"][:-1]) if l["bbox"][2] < maxx - 50]
            brks = sorted(set(blk.get("breaks", [])) | set(geo))
            idxs = [0] + brks + [len(blk["lines"])]
            seg_bodies = []
            for i0, i1 in zip(idxs, idxs[1:]):
                tt, mm = block_text_and_marks({**blk, "lines": blk["lines"][i0:i1]}, page, chips)
                seg_bodies.append((tt, mm))
            text, marks = seg_bodies[0]
            label = ""
            bolds = [m for m in marks if m[0] == "bold"]
            if bolds and bolds[0][1] == 0:
                label = text[: bolds[0][2]].strip().rstrip(":")
                text = text[bolds[0][2]:].lstrip(" :")
                marks = [m for m in marks if m[0] != "bold" or m[1] != 0]
            elif re.fullmatch(r"\[[^\]]{1,30}\]:?\s*", text.strip()):
                label = text.strip().rstrip(":").strip("[]").rstrip(":")
                text = ""
            # the label text outranks the bubble fill for role (p.153: assistant
            # turns in #faf9f5 bubbles were mis-roled user by fill alone)
            low = label.lower()
            label_role = ("assistant" if ("assistant" in low or "claude" in low)
                          else "user" if (low.startswith("user") or "human" in low)
                          else None)
            role = label_role or blk.get("role") or "assistant"
            label = label.strip("[]").rstrip(":")  # '[Assistant:]' -> 'Assistant'
            body = _hyphen_join(_apply_marks(text, marks)).strip()
            for tt, mm in seg_bodies[1:]:
                body += "\n\n" + _hyphen_join(_apply_marks(tt, mm)).strip()
            if blk.get("code_lines"):  # displaced code box merged into this turn
                raw = "\n".join(l["text"] for l in blk["code_lines"])
                body = (body + "\n\n" if body else "") + "```\n" + raw + "\n```"
            out.append(f':::turn{{role={role} label="{label}"}}\n{body}\n:::\n')
        elif t == "commentary":
            text, marks = block_text_and_marks(blk, page, chips)
            out.append(_hyphen_join(_apply_marks(text, marks)).strip() + "\n")
        elif t in ("example", "code"):
            text, marks = block_text_and_marks(blk, page, chips)
            if t == "example":
                out.append(":::example\n" + _hyphen_join(text).strip() + "\n:::\n")
            else:
                raw = "\n".join(l["text"] for l in blk["lines"])
                out.append("```\n" + raw + "\n```\n")
        elif t == "table_html":
            out.append(blk["html"] + "\n")
        else:
            # never silently drop a block: emit its text so T1 catches issues
            text, marks = block_text_and_marks(blk, page, chips)
            if text.strip():
                out.append(f"<!-- UNHANDLED-BLOCK:{t} -->\n" + _hyphen_join(text).strip() + "\n")
        last_type = t
        out.append("\n")

    close_transcript()
    for fb in sorted(footnotes, key=lambda b: b["n"]):
        page = oracle_pages[fb["page"] - 1]
        if fb.get("lines"):
            text, marks = block_text_and_marks(fb, page, chips)
            body = _hyphen_join(_apply_marks(text, marks)).strip()
        else:
            body = _hyphen_join(fb.get("text", "")).strip()
        out.append(f"[^{fb['n']}]: {body}\n\n")
    return "".join(out), cur_page
