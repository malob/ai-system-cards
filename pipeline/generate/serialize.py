"""Blocks → v1 markdown dialect (generation-design.md): the existing site and
the calibrated verifier consume the output unchanged."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "verifier"))
from assemble import block_text_and_marks  # noqa: E402


def _apply_marks(text: str, marks: list) -> str:
    """Insert markdown syntax by char range, end-first so offsets hold.
    Overlapping marks of different kinds nest by application order."""
    ins: list[tuple[int, int, str, str]] = []  # (pos, prio, open/close, s)
    for kind, a, b, data in marks:
        if kind == "bold":
            ins += [(a, 2, "o", "**"), (b, 2, "c", "**")]
        elif kind == "italic":
            ins += [(a, 3, "o", "*"), (b, 3, "c", "*")]
        elif kind == "chip":
            ins += [(a, 1, "o", ":chip["), (b, 1, "c", "]")]
        # placeholder: detected + recorded, but serialized as plain bracketed
        # text until the renderer/verifier gain a :ph directive (FL-07 deferred,
        # presentation-editorial per D17)
        elif kind == "link":
            ins += [(a, 0, "o", "["), (b, 0, "c", f"]({data})")]
        elif kind == "fnref":
            ins += [(a, 0, "o", ""), (b, 0, "c", "")]  # replaced below
    out = text
    for kind, a, b, data in sorted(marks, key=lambda m: -m[1]):
        if kind == "fnref":
            out = out[:a] + f"[^{data}]" + out[b:]
    applied = sorted((p for p in ins if True), key=lambda t: (-t[0], t[1]))
    # simple two-pass: apply non-fnref marks end-first
    for pos, _, oc, s in sorted([i for i in ins if i[3]], key=lambda t: (-t[0], 0 if t[2] == "c" else 1)):
        out = out[:pos] + s + out[pos:]
    return out


def _hyphen_join(text: str) -> str:
    text = re.sub(r"(\w)- (?=[a-z])", r"\1", text)   # end-of-line hyphenation (A1)
    text = text.replace("​", "").replace("­", "")  # zero-width, soft hyphen
    return re.sub(r"[ \t]{2,}", " ", text).strip()   # collapse layout double-spaces (A2)


def serialize_blocks(blocks: list[dict], page_of_prev_block: int, oracle_pages, chips) -> tuple[str, int]:
    """Render an ordered block list to markdown. Emits a `<!-- p.N -->` marker
    whenever the page advances. Returns (markdown, last_page)."""
    out = []
    cur_page = page_of_prev_block
    footnotes = []
    transcript_open = False

    def marker_if_new(pno):
        nonlocal cur_page
        if pno != cur_page:
            out.append(f"<!-- p.{pno} -->\n")
            cur_page = pno

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
            if not transcript_open:
                out.append("::::transcript\n")
                transcript_open = True
        else:
            close_transcript()
            marker_if_new(pno)

        if t == "heading":
            text, _ = block_text_and_marks(blk, page, chips)
            out.append("#" * blk["level"] + " " + text.strip() + "\n")
        elif t == "paragraph":
            text, marks = block_text_and_marks(blk, page, chips)
            out.append(_hyphen_join(_apply_marks(text, marks)).strip() + "\n")
        elif t == "item":
            text, marks = block_text_and_marks(blk, page, chips)
            body = _hyphen_join(_apply_marks(text, marks)).strip().lstrip("●•◦▪‣○ ")
            out.append("- " + body + "\n")
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
            text, marks = block_text_and_marks(blk, page, chips)
            label = ""
            bolds = [m for m in marks if m[0] == "bold"]
            if bolds and bolds[0][1] == 0:
                label = text[: bolds[0][2]].strip().rstrip(":")
                text = text[bolds[0][2]:].lstrip(" :")
                marks = [m for m in marks if m[0] != "bold" or m[1] != 0]
            role = blk.get("role", "assistant")
            out.append(f':::turn{{role={role} label="{label}"}}\n{_hyphen_join(text).strip()}\n:::\n')
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
        out.append("\n")

    close_transcript()
    for fb in sorted(footnotes, key=lambda b: b["n"]):
        out.append(f"[^{fb['n']}]: {fb['text'].strip()}\n\n")
    return "".join(out), cur_page
