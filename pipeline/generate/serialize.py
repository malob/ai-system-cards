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
    "underline": ("<u>", "</u>"),  # inline raw HTML, like v1's <sup> usage
    "code": ("`", "`"),
    # D15/D17 green placeholder pills — raw HTML, NOT :ph[] directive:
    # the highlighted ranges are full of brackets ('[user]', '[Error 1]')
    # which break directive-label parsing on both ends
    "placeholder": ('<span class="ph">', "</span>"),
    # placeholder: plain text until the renderer gains :ph (FL-07/D17)
}


def _apply_marks(text: str, marks: list, escape_literals: bool = False) -> str:
    """Apply ALL mark edits in one strictly end-first pass so earlier offsets
    never go stale. (A two-pass version replaced fnrefs '11'->'[^11]' first,
    shifting every later mark by +3 per ref — the 'in Section 6.' bug.)

    Equal-position ordering (inserts at the same index stack right-to-left:
    the LAST insert ends up LEFTMOST):
    - an OPEN for following text processes before a CLOSE for preceding text,
      so the close lands left of the open ("]:chip[" not ":chip[]");
    - among opens, inner (shorter) first so outer ends up leftmost;
    - among closes, outer (earlier start) first so inner ends up leftmost."""
    # emphasis straddling a link boundary nests illegally
    # ('[**text](#u)**' renders literal asterisks): clip each emphasis mark
    # against every link range, splitting at the boundary
    links = [(a, b) for kind, a, b, _ in marks if kind == "link"]
    fixed = []
    for kind, a, b, data in marks:
        if kind in ("bold", "italic", "underline"):
            pieces = [(a, b)]
            for la, lb in links:
                nxt = []
                for pa, pb in pieces:
                    if pa < la < pb or pa < lb < pb:
                        cuts = sorted({pa, max(pa, min(pb, la)),
                                       max(pa, min(pb, lb)), pb})
                        nxt.extend((c1, c2) for c1, c2 in zip(cuts, cuts[1:])
                                   if c2 > c1)
                    else:
                        nxt.append((pa, pb))
                pieces = nxt
            # re-trim each piece to non-space (a split at the link edge can
            # leave '…on ' — a space-flanked '**' is not a valid delimiter)
            for pa, pb in pieces:
                while pb > pa and text[pb - 1].isspace():
                    pb -= 1
                while pa < pb and text[pa].isspace():
                    pa += 1
                if pb > pa:
                    fixed.append((kind, pa, pb, data))
        else:
            fixed.append((kind, a, b, data))
    marks = fixed
    ops = []  # (pos, phase, tiebreak, rank, edit)
    # rank breaks FULL ties (same pos+phase+range): emphasis nests INSIDE the
    # link ('[**text**](url)') — link-open lands leftmost (applied last, rank
    # 1) and link-close rightmost (applied first, rank 0); unbroken ties
    # interleaved the two ('[**text](url)**', literal asterisks)
    for kind, a, b, data in marks:
        if kind == "fnref":
            ops.append((a, 0, 0, 0, lambda t, a=a, b=b, d=data: t[:a] + f"[^{d}]" + t[b:]))
        elif kind == "link":
            ops.append((a, 1, b, 1, lambda t, a=a: t[:a] + "[" + t[a:]))
            ops.append((b, 2, a, 0, lambda t, b=b, d=data: t[:b] + f"]({d})" + t[b:]))
        elif kind in SYNTAX:
            o, c = SYNTAX[kind]
            ops.append((a, 1, b, 0, lambda t, a=a, o=o: t[:a] + o + t[a:]))
            ops.append((b, 2, a, 1, lambda t, b=b, c=c: t[:b] + c + t[b:]))
    if escape_literals:
        # transcript bodies are RAW model/user text: literal '*'/'`' in the
        # source must render literally, not as markdown (p.43/44 class).
        # Phase 0.5: the backslash hugs its char, left of it; opens/closes
        # at the same position land further left (applied later)
        covered = [(a, b) for kind, a, b, _ in marks if kind in ("fnref", "code")]
        for i, ch in enumerate(text):
            if ch in "*`" and not any(a <= i < b for a, b in covered):
                ops.append((i, 0.5, 0, 0, lambda t, i=i: t[:i] + "\\" + t[i:]))
    out = text
    for _, _, _, _, edit in sorted(ops, key=lambda x: (-x[0], x[1], x[2], x[3])):
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
            # invisibles poison the renderer's anchor slugs (p.146 class)
            text = re.sub("[​‌‍﻿­]", "", text)
            out.append("#" * blk["level"] + " " + text.strip() + "\n")
        elif t == "paragraph":
            body = _render_body(blk, page, oracle_pages, chips, marker_if_new, emit_marker)
            if not body.strip():  # invisible-only lines: never emit a bare '> '
                continue
            out.append(q + body + "\n")
        elif t == "item":
            body = _render_body(blk, page, oracle_pages, chips, marker_if_new, emit_marker)
            # 2-space nesting inside quotes (4 spaces would read as code there)
            # 3 spaces inside quotes: enough to nest under an ordered parent
            # ('1. ' is 3 chars), still short of indented-code territory
            indent = ("   " if q else "    ") * blk.get("level", 0)
            m = re.match(r"^[‌ ]*(\d{1,2})[.)]​?\s*", body)
            if m:  # ordered item: keep the number, real space after it
                out.append(f"{q}{indent}{m.group(1)}. " + inline_marker + body[m.end():] + "\n")
            else:
                body = re.sub(r"^(\**)[●•◦▪‣○​‌ ]+", r"\1", body.lstrip("●•◦▪‣○​‌ "))
                # lettered sub-list marker ('a.​On' — ZWSP eaten by the join):
                # restore the space, gated on the RAW line's marker signature
                raw0 = blk["lines"][0]["text"] if blk.get("lines") else ""
                if re.match(r"^\s*[a-z][.)]\u200b", raw0):
                    body = re.sub(r"^(\**[a-z][.)])(?=\S)", r"\1 ", body)
                    # lettered markers are SUB-items by definition in this
                    # card; a page break resets the tier baseline and dropped
                    # one to level 0 (p.66 item 2b)
                    if blk.get("level", 0) == 0:
                        indent = "   " if q else "    "
                out.append(f"{q}{indent}- " + inline_marker + body + "\n")
        elif t == "figure":
            out.append(f"![{blk['alt']}](assets/figures/{blk['file']})\n")
            if blk["caption_lines"]:  # legacy in-figure captions (rare)
                cap_blk = {"lines": blk["caption_lines"], "page": pno}
                text, marks = block_text_and_marks(cap_blk, page, chips)
                cap = re.sub(r"\](?=[A-Za-z0-9])", "] ",
                             _hyphen_join(_apply_marks(text, marks)).strip())
                out.append(":::caption\n" + cap + "\n:::\n")
        elif t == "caption":
            # first-class caption block (D23): marks applied (bold leads,
            # sub-labels), rendered uniformly by the :::caption directive
            body = _render_body(blk, page, oracle_pages, chips, marker_if_new, emit_marker)
            # bracket-lead glue: '[Figure 6.5.4.3.A]Stealth' — the lead span
            # abuts the title span; ']' before a letter/digit takes a space
            # ('](' stays: link syntax)
            body = re.sub(r"\](?=[A-Za-z0-9])", "] ", body)
            out.append(":::caption\n" + body + "\n:::\n")
        elif t == "turn":
            # multi-paragraph turns: gap-recorded breaks UNION short-line
            # breaks (PDF intra-turn paragraphs are plain hard returns with no
            # extra spacing — the signal is a line ending short of the right edge)
            maxx = max(l["bbox"][2] for l in blk["lines"])
            # a short line is a paragraph break only at a sentence boundary:
            # terminal punctuation, or the next line opening a new sentence —
            # bare width split mid-sentence at wrap points (p.44/153)
            geo = [i + 1 for i, l in enumerate(blk["lines"][:-1])
                   if l["bbox"][2] < maxx - 50
                   and (re.search(r"[.!?:…\"”'\)\]]\s*$", l["text"].rstrip())
                        or blk["lines"][i + 1]["text"].lstrip()[:1].isupper())]
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
                cap = bolds[0][2]
                mb = re.match(r"\[[^\]]{1,30}\]:?", text)
                resid_bold = None
                if mb and mb.end() < cap:
                    # the PDF's bold run continues past the bracket label into
                    # the body lead-in ('[Assistant]: One thing worth noting') —
                    # the label ends at the bracket; the rest stays a body bold
                    cap = mb.end()
                    resid_bold = bolds[0][2]
                label = text[:cap].strip().rstrip(":")
                rest = text[cap:]
                delta = cap + (len(rest) - len(rest.lstrip(" :")))
                text = rest.lstrip(" :")
                # remaining marks must shift with the trimmed prefix — stale
                # offsets displaced every later mark by len(label) (p.153
                # code spans wrapped the wrong characters)
                marks = [(k, max(0, a - delta), max(0, b - delta), d)
                         for k, a, b, d in marks
                         if not (k == "bold" and a == 0) and b > delta]
                if resid_bold is not None and resid_bold - delta > 0:
                    marks.append(("bold", 0, resid_bold - delta, None))
            elif re.fullmatch(r"\[[^\]]{1,30}\]:?\s*", text.strip()):
                label = text.strip().rstrip(":").strip("[]").rstrip(":")
                text = ""
                marks = []
            # the label text outranks the bubble fill for role (p.153: assistant
            # turns in #faf9f5 bubbles were mis-roled user by fill alone)
            low = label.lower()
            label_role = ("assistant" if ("assistant" in low or "claude" in low)
                          else "user" if (low.startswith("user") or "human" in low)
                          else None)
            role = label_role or blk.get("role") or "assistant"
            # label keeps its source form (brackets and all): fidelity outranks
            # cosmetics, and stripping made the bold label vanish from S1's view
            body = _hyphen_join(_apply_marks(text, marks, escape_literals=True)).strip()
            for tt, mm in seg_bodies[1:]:
                body += "\n\n" + _hyphen_join(_apply_marks(tt, mm, escape_literals=True)).strip()
            if blk.get("code_lines"):  # displaced code box merged into this turn
                clines = blk["code_lines"]
                if any(s.get("bold") for l in clines for _, _, s in l.get("segs", [])):
                    # the box carries BOLD emphasis (p.182 'classic agentic
                    # safety test') — fences can't hold it; styled <pre> can
                    import html as _h
                    rows = []
                    for l in clines:
                        segs = "".join(
                            (f"<b>{_h.escape(s['text'], quote=False)}</b>"
                             if s.get("bold") else _h.escape(s["text"], quote=False))
                            for _, _, s in l.get("segs", []))
                        rows.append(segs)
                    raw = "<pre>" + "\n".join(rows).replace("</b><b>", "") + "</pre>"
                    body = (body + "\n\n" if body else "") + raw
                else:
                    raw = "\n".join(l["text"] for l in clines)
                    body = (body + "\n\n" if body else "") + "```\n" + raw + "\n```"
            out.append(f':::turn{{role={role} label="{label}"}}\n{body}\n:::\n')
        elif t == "commentary":
            text, marks = block_text_and_marks(blk, page, chips)
            out.append(_hyphen_join(_apply_marks(text, marks, escape_literals=True)).strip() + "\n")
        elif t in ("example", "code"):
            text, marks = block_text_and_marks(blk, page, chips)
            if t == "example":
                out.append(":::example\n" + _hyphen_join(_apply_marks(text, marks, escape_literals=True)).strip() + "\n:::\n")
            else:
                raw = "\n".join(l["text"] for l in blk["lines"])
                out.append("```\n" + raw + "\n```\n")
        elif t == "table_html":
            out.append(blk["html"] + "\n")
            # a merged multi-page table carries embedded page markers: advance
            # the tracker so those pages don't re-emit duplicate markers later
            embedded = [int(n) for n in re.findall(r"<!-- p\.(\d+) -->", blk["html"])]
            if embedded:
                cur_page = max(cur_page, max(embedded))
        else:
            # never silently drop a block: emit its text so T1 catches issues
            text, marks = block_text_and_marks(blk, page, chips)
            if text.strip():
                out.append(f"<!-- UNHANDLED-BLOCK:{t} -->\n" + _hyphen_join(text).strip() + "\n")
        last_type = t
        out.append("\n")

    close_transcript()

    def _fn_body(fb):
        page = oracle_pages[fb["page"] - 1]
        if fb.get("lines"):
            text, marks = block_text_and_marks(fb, page, chips)
            return _hyphen_join(_apply_marks(text, marks)).strip()
        return _hyphen_join(fb.get("text", "")).strip()

    # document order: (page, cont-first, n); a "cont" block is the tail of the
    # PREVIOUS page's last footnote — merge it into that body (rendered with
    # its own page's facts so links/chips resolve)
    ordered = sorted(footnotes, key=lambda b: (
        b["page"], 0 if b["n"] == "cont" else 1,
        b["n"] if isinstance(b["n"], int) else 0))
    merged = []
    for fb in ordered:
        if fb["n"] == "cont" and merged:
            merged[-1] = (merged[-1][0], merged[-1][1] + " " + _fn_body(fb))
        elif fb["n"] == "cont":
            sys.stderr.write(f"WARN: orphan footnote continuation on p.{fb['page']}\n")
            out.append("<!-- UNHANDLED-FOOTNOTE-CONT -->\n" + _fn_body(fb) + "\n\n")
        else:
            merged.append((fb["n"], _fn_body(fb)))
    for n, body in merged:
        out.append(f"[^{n}]: {body}\n\n")
    return "".join(out), cur_page
