"""Blocks → v1 markdown dialect (generation-design.md): the existing site and
the calibrated verifier consume the output unchanged."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "verifier"))
from assemble import BULLETS, LIST_MARKER, block_text_and_marks  # noqa: E402


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
    # inline text highlight (a line-height tint strip under prose — the
    # opus-5 p.137 cream constitution quotes), NOT a box
    "highlight": ('<span class="hl">', "</span>"),
    # ORPHAN footnote ref (oracle-tagged source artifact): superscript digits
    # with no def to point at — raw HTML like <u>/<span>
    "sup": ("<sup>", "</sup>"),
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
            # leave '…on ' — a space-flanked '**' is not a valid delimiter).
            # Zero-widths/soft hyphens count as space: _hyphen_join deletes
            # them AFTER marks apply, so a ZWSP-only piece (a bullet's ​
            # split off by a bold link, opus-5 p.79) became a literal '****'
            # that desynced every later bold pair in the projection.
            invis = "​­‌‍⁠﻿"
            for pa, pb in pieces:
                while pb > pa and (text[pb - 1].isspace() or text[pb - 1] in invis):
                    pb -= 1
                while pa < pb and (text[pa].isspace() or text[pa] in invis):
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
            # raw-HTML marks (placeholder/underline/highlight/sup) sit
            # OUTERMOST: a span tag inside backticks renders literally
            r_open = 2 if kind in ("placeholder", "underline", "highlight", "sup") else 0
            r_close = -1 if kind in ("placeholder", "underline", "highlight", "sup") else 1
            ops.append((a, 1, b, r_open, lambda t, a=a, o=o: t[:a] + o + t[a:]))
            ops.append((b, 2, a, r_close, lambda t, b=b, c=c: t[:b] + c + t[b:]))
    if escape_literals:
        # transcript bodies are RAW model/user text: literal '*'/'`' in the
        # source must render literally, not as markdown (p.43/44 class).
        # Phase 0.5: the backslash hugs its char, left of it; opens/closes
        # at the same position land further left (applied later)
        covered = [(a, b) for kind, a, b, _ in marks if kind in ("fnref", "code")]
        for i, ch in enumerate(text):
            if ch in "*`" and not any(a <= i < b for a, b in covered):
                ops.append((i, 0.5, 0, 0, lambda t, i=i: t[:i] + "\\" + t[i:]))
    # ALWAYS: a raw '<' before a letter or '/' opens an HTML tag and the
    # renderer swallows it ('<link>' in p.216 prose vanished); '\<' renders
    # as the character in every md text context. Code-marked ranges are
    # backtick-wrapped (remark escapes them) and must stay backslash-free.
    code_cov = [(a, b) for kind, a, b, _ in marks if kind == "code"]
    for m in re.finditer(r"<(?=[A-Za-z/])", text):
        i = m.start()
        if not any(a <= i < b for a, b in code_cov):
            ops.append((i, 0.5, 0, 0, lambda t, i=i: t[:i] + "\\" + t[i:]))
    out = text
    for _, _, _, _, edit in sorted(ops, key=lambda x: (-x[0], x[1], x[2], x[3])):
        out = edit(out)
    return out


def _table_lines(html: str) -> str:
    """Serialize tables one <tr> per line (owner-approved whitespace-only
    canon change): the row is the unit agents grep, git diffs show, and
    viewers truncate at — one-line tables made all three opaque. Only exact
    `</tr><tr` seams split; a seam carrying an inline page marker
    (`</tr><!-- p.N --><tr>`) stays on one line so downstream marker regexes
    are untouched. Newlines between rows are insignificant to HTML parsing
    and to the (re.S) verifier/seam-audit patterns."""
    html = html.replace("<table><tbody>", "<table><tbody>\n")
    html = html.replace("</tr><tr", "</tr>\n<tr")
    return html.replace("</tbody></table>", "\n</tbody></table>")


def _code_raw(lines) -> str:
    """Fence body: PDF line breaks kept, and a BLANK line re-emitted where
    consecutive lines sit a full line-height apart (the p.85 cube-net box's
    two thinking fragments read as one, D42). A blank line has no span to
    carry it — the gap is the only record."""
    out = []
    for i, l in enumerate(lines):
        if i:
            prev = lines[i - 1]
            h = prev["bbox"][3] - prev["bbox"][1]
            if l["bbox"][1] - prev["bbox"][3] > 0.6 * h:
                out.append("")
        out.append(l["text"])
    return "\n".join(out)


def _hyphen_join(text: str) -> str:
    text = re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1", text)  # A1; keep suspended compounds ("single- and")
    text = text.replace("​", "").replace("­", "")  # zero-width, soft hyphen
    return re.sub(r"[ \t]{2,}", " ", text).strip()   # collapse layout double-spaces (A2)


def _mono_line(l) -> bool:
    """Mono-DOMINANT by char count: card-puzzle lines mix emoji-font spans
    (the skulls) into otherwise-mono lines; all-spans-mono missed every one."""
    segs = [s for _, _, s in l.get("segs", []) if s.get("zone") == "body"]
    if not segs:
        return False
    mono = sum(len(s["text"]) for s in segs if "Mono" in s.get("font", ""))
    total = sum(len(s["text"]) for s in segs)
    return total > 0 and mono / total >= 0.5


def _pre_html(blk, page, chips) -> str:
    """Code box -> <pre> with <b> and green placeholder spans applied per
    line (fences can't carry styling; positions stay line-local)."""
    import html as _h
    rows = []
    for l in blk["lines"]:
        lb = {**blk, "lines": [l], "code_lines": None, "page_break": None, "breaks": []}
        tt, mm = block_text_and_marks(lb, page, chips)
        mm = [m for m in mm if m[0] in ("bold", "placeholder")]
        # sentinel-tag application: insert end-first, escape, then swap
        ins = []
        for kind, a, b, _ in mm:
            tag = "B" if kind == "bold" else "P"
            ins.append((a, 0, "\x01" + tag))   # opens first at a tie ->
            ins.append((b, 1, "\x02" + tag))   # close ends up leftmost
        out = tt
        for pos, _, tok in sorted(ins, key=lambda x: (-x[0], x[1])):
            out = out[:pos] + tok + out[pos:]
        out = _h.escape(out, quote=False)
        out = (out.replace("\x01B", "<b>").replace("\x02B", "</b>")
                  .replace("\x01P", '<span class="ph">').replace("\x02P", "</span>"))
        rows.append(out)
    return "<pre>" + "\n".join(rows).replace("</b>\n<b>", "\n") + "</pre>"


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
    prev_quote = None

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
        # block separator, decided AGAINST THE PREDECESSOR: consecutive list
        # items stay tight (one blank anywhere makes the whole list loose in
        # CommonMark — every li gains <p> margins and children drift)
        if last_type is not None and not (
                t == "item" and last_type == "item"
                and blk.get("quote") == prev_quote):
            out.append("\n")
        if t in ("turn", "commentary") or (t == "code" and blk.get("in_transcript")):
            # a code box nested in a turn keeps the transcript OPEN (the
            # assistant's mono output belongs inside the box — p.198), unlike a
            # standalone code block (§9.2 blocklist), which closes it
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
                body = re.sub(r"^(\**)[●•◦▪‣○■□​‌ ]+", r"\1", body.lstrip("●•◦▪‣○■□​‌ "))
                # Word-style lone-'o' marker (p.104): regex, not lstrip — a
                # char-set strip would eat the 'O' of the following word
                raw0_o = blk["lines"][0]["text"] if blk.get("lines") else ""
                if re.match(r"^\s*o[\s​]+\S", raw0_o):
                    body = re.sub(r"^o[\s​]+", "", body)
                # the strip can leave an EMPTY bold pair when the bullet's
                # bold run ends before a following link ('**○​** [**Reckless…',
                # opus-5 p.79) — a literal '****' desyncs every later bold
                # pair in the projection
                body = re.sub(r"^\*\*\*\*\s*", "", body)
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
                # a page marker BEFORE a lettered marker ('- <!-- p.44 -->a. On…')
                # makes remark parse the whole line as one raw-HTML block, which
                # defeats the renderer's lettered-list transform — emit the
                # marker AFTER the letter (same line, same page attribution)
                ml = re.match(r"^([a-z][.)]\s+)", body)
                if inline_marker and ml:
                    out.append(f"{q}{indent}- " + ml.group(1) + inline_marker + body[ml.end():] + "\n")
                else:
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
            # multi-paragraph turns: gap-recorded breaks, falling back to
            # short-line breaks (PDF intra-turn paragraphs are plain hard
            # returns with no extra spacing — the signal is a line ending
            # short of the right edge). The fallback applies ONLY when the
            # turn has no gap breaks: a turn that separates its paragraphs
            # with visible gaps also uses tight hard returns WITHIN a
            # paragraph ('ARGH ARGH ARGH.' | 'OK. Gun to head:', opus-5
            # p.143, sweep round 2) — there the gap signal is authoritative
            geo = []
            if not blk.get("breaks"):
                maxx = max(l["bbox"][2] for l in blk["lines"])
                # a short line is a paragraph break only at a sentence
                # boundary: terminal punctuation, or the next line opening a
                # new sentence — bare width split mid-sentence at wrap
                # points (p.44/153)
                geo = [i + 1 for i, l in enumerate(blk["lines"][:-1])
                       if l["bbox"][2] < maxx - 50
                       and (re.search(r"[.!?:…\"”'\)\]]\s*$", l["text"].rstrip())
                            or blk["lines"][i + 1]["text"].lstrip()[:1].isupper())]
            # a LIST-MARKER line inside a bubble starts its own segment,
            # rendered as a markdown item — in-box lists were flattening to
            # prose (the §2.24 rubric bullets, ST1 p.85 items-missing 12→2);
            # continuation lines of a wrapped item stay in its segment
            def _item_lead(l):
                t = l["text"].lstrip()
                return bool(LIST_MARKER.match(t)) or t[:1] in BULLETS
            item_brks = {i for i in range(1, len(blk["lines"]))
                         if _item_lead(blk["lines"][i])}
            brks = sorted(set(blk.get("breaks", [])) | set(geo) | item_brks)
            idxs = [0] + brks + [len(blk["lines"])]
            seg_bodies, seg_item = [], []
            for i0, i1 in zip(idxs, idxs[1:]):
                tt, mm = block_text_and_marks({**blk, "lines": blk["lines"][i0:i1]}, page, chips)
                seg_bodies.append((tt, mm))
                seg_item.append(_item_lead(blk["lines"][i0]))
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
            elif (re.fullmatch(r"\[[^\]]{1,30}\]:?\s*", text.strip())
                  and not any(k == "placeholder" for k, _, _, _ in marks)):
                # a bracket-only line that is a GREEN PILL is a D15 placeholder
                # ('[tool use]', opus-5 p.93), not a speaker label — leave it
                # as the turn's body so the pill span survives
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
            def _item_line(txt):
                # marker → markdown item: ZWSPs are already gone (_hyphen_join)
                mo = re.match(r"^(\d{1,2})[.)]\s*", txt)
                if mo:
                    return f"{mo.group(1)}. " + txt[mo.end():]
                return "- " + re.sub(r"^(\**)[●•◦▪‣○■□‌ ]+", r"\1",
                                     txt.lstrip("●•◦▪‣○■□‌ "))
            body = _hyphen_join(_apply_marks(text, marks, escape_literals=True)).strip()
            if seg_item[0] and body:
                body = _item_line(body)
            for k, (tt, mm) in enumerate(seg_bodies[1:], start=1):
                txt = _hyphen_join(_apply_marks(tt, mm, escape_literals=True)).strip()
                if not txt:
                    continue
                if seg_item[k]:
                    txt = _item_line(txt)
                # consecutive items stay tight (a blank line makes the whole
                # list loose in CommonMark); anything else keeps the
                # paragraph break
                body += ("\n" if (seg_item[k] and seg_item[k - 1]) else "\n\n") + txt
            if blk.get("code_lines"):  # displaced code box merged into this turn
                # the box may continue on the next page (code_cont, stitched):
                # each segment's marks come from ITS OWN page's pills/links
                segs_cl = [(page, blk["code_lines"])]
                if blk.get("code_cont"):
                    cont = blk["code_cont"]
                    segs_cl.append((oracle_pages[cont["page"] - 1], cont["lines"]))
                styled = False
                for pg_, cl_ in segs_cl:
                    _, probe_marks = block_text_and_marks({**blk, "lines": cl_}, pg_, chips)
                    if any(s.get("bold") for l in cl_ for _, _, s in l.get("segs", [])) \
                            or any(m[0] == "placeholder" for m in probe_marks):
                        # bold or green placeholders — fences can't hold either
                        styled = True
                if styled:
                    raws = [_pre_html({**blk, "lines": cl_}, pg_, chips) for pg_, cl_ in segs_cl]
                    raw = raws[0]
                    for r in raws[1:]:
                        raw = raw[: -len("</pre>")] + "\n" + r[len("<pre>"):]
                    body = (body + "\n\n" if body else "") + raw
                else:
                    raw = "\n".join(_code_raw(cl_) for _, cl_ in segs_cl)
                    body = (body + "\n\n" if body else "") + "```\n" + raw + "\n```"
            # same-bubble continuation (assemble's turn_cont, D42): splice
            # this body into the previous :::turn instead of opening a
            # second bubble for one physical box. Look back past block
            # separators; anything else between (a page marker) vetoes the
            # splice and the turn falls back to its own directive.
            j = len(out) - 1
            while j >= 0 and out[j] == "\n":
                j -= 1
            if (blk.get("turn_cont") and j >= 0
                    and out[j].startswith(":::turn{")
                    and out[j].endswith("\n:::\n")):
                out[j] = out[j][: -len(":::\n")] + "\n" + body + "\n:::\n"
                del out[j + 1:]
            else:
                out.append(f':::turn{{role={role} label="{label}"}}\n{body}\n:::\n')
            if blk.get("code_lines") and blk.get("code_cont"):
                # marker after the box, never inside it (fence convention)
                marker_if_new(blk["code_cont"]["page"])
                emit_marker(False)
        elif t == "commentary":
            text, marks = block_text_and_marks(blk, page, chips)
            out.append(_hyphen_join(_apply_marks(text, marks, escape_literals=True)).strip() + "\n")
        elif t in ("example", "code"):
            text, marks = block_text_and_marks(blk, page, chips)
            if t == "example":
                parts = []
                for l in blk["lines"]:
                    lb = {**blk, "lines": [l], "breaks": [], "page_break": None}
                    tt, mm = block_text_and_marks(lb, page, chips)
                    mm = [m for m in mm if m[0] != "code"]
                    parts.append((_hyphen_join(_apply_marks(tt, mm, escape_literals=True)).strip(),
                                  _mono_line(l)))
                body2, prev_mono = "", None
                for txt, mono in parts:
                    if not txt:
                        continue
                    if body2:
                        # consecutive MONO lines keep the PDF's line breaks
                        # (code-ish examples); prose lines flow normally
                        body2 += "\\\n" if (mono and prev_mono) else " "
                    body2 += txt
                    prev_mono = mono
                out.append(":::example\n" + body2 + "\n:::\n")
            else:
                _, probe = block_text_and_marks(blk, page, chips)
                if any(m[0] in ("bold", "placeholder") for m in probe):
                    out.append(_pre_html(blk, page, chips) + "\n")
                else:
                    # Google-Docs code boxes print their language chooser as
                    # a non-mono chrome line at the box top ('None',
                    # pp.191-193 D42) — that's the fence INFO STRING, not
                    # content (a reader copying the blocklist must not get a
                    # phantom 'None' pattern)
                    body_lines = blk["lines"]
                    lang = ""
                    if (body_lines and not _mono_line(body_lines[0])
                            and re.fullmatch(r"\w+", body_lines[0]["text"].strip())):
                        lang = body_lines[0]["text"].strip()
                        body_lines = body_lines[1:]
                    raw = _code_raw(body_lines)
                    out.append(f"```{lang}\n" + (raw + "\n" if raw else "")
                               + "```\n")
                for tp in blk.get("trailing_pages", []):
                    marker_if_new(tp)
                    emit_marker(False)
        elif t == "table_html":
            out.append(_table_lines(blk["html"]) + "\n")
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
        prev_quote = blk.get("quote")

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
        out.append(_fn_def(n, body))
    return "".join(out), cur_page


def _fn_def(n, body: str) -> str:
    """A footnote whose body carries '●' bullets is a list the PDF set inside
    the note (fn1 p.36): lead-in, then items. Emit a GFM footnote with a
    4-space-indented list (continuation lines belong to the note) instead of
    leaving the glyphs inline. Only fires with ≥2 bullets."""
    if "●" in body:
        parts = [p.strip() for p in body.split("●")]
        lead, items = parts[0].rstrip(), [p for p in parts[1:] if p]
        if len(items) >= 2:
            # 4-space continuation, NO blank line: the verifier's footnote-def
            # projection captures contiguous `\n    .*` continuations but stops
            # at a blank line (blank-tolerance was removed — it over-swallowed)
            lines = [f"[^{n}]: {lead}".rstrip()]
            lines += [f"    - {it}" for it in items]
            return "\n".join(lines) + "\n\n"
    return f"[^{n}]: {body}\n\n"
