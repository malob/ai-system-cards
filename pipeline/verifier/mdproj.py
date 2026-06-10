"""v1 markdown sections → comparable projection (text stream, links, bold runs,
markers, images, footnotes), with per-page attribution via the `<!-- p.N -->`
markers v1 embeds.

v1-calibration shims (documented, removed for v2's typed model):
- turn-directive labels re-emit as `Label:` text (the PDF renders the colon);
- straight-quote folding happens in norm.py's calibration mode.
"""

import html
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import norm

SECTIONS_DIR = "cards/anthropic/claude-fable-5/sections"

RE_HEADER = re.compile(r"<!--\s*source: source\.pdf pages (\d+)-(\d+)\s*-->")
RE_MARKER = re.compile(r"<!--\s*p\.(\d+)\s*-->")
RE_FIGSKIP = re.compile(r"<!--\s*figure (p(\d+)-\d+\.png) skipped: ([^>]*?)\s*-->")
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
RE_FNDEF = re.compile(
    r"^\[\^(\d+)\]:[ \t]*(.*(?:\n(?:[ ]{4}.*|[ \t]*(?=\n[ ]{4})))*)", re.M
)  # incl. indented continuations, allowing blank lines between them
RE_AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
RE_FNREF = re.compile(r"\[\^(\d+)\]")
RE_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
RE_DIRECTIVE = re.compile(r"^:{3,}(\w*)(\{[^}]*\})?\s*$", re.M)
RE_TURN_LABEL = re.compile(r'label="([^"]*)"')
RE_CHIP = re.compile(r":chip\[([^\]]+)\]")
RE_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*|__([^_]+(?:_[^_]+)*?)__")
RE_SUP = re.compile(r"<sup>(.*?)</sup>", re.S)
RE_TABLE = re.compile(r"<table.*?</table>", re.S)
RE_TAG = re.compile(r"</?[a-zA-Z][^>]*>")


@dataclass
class Section:
    name: str
    page_start: int
    page_end: int
    tokens: list = field(default_factory=list)        # [(token, page)]
    links: list = field(default_factory=list)         # [(text, target, page)]
    bolds: list = field(default_factory=list)         # [(text, page)]
    images: dict = field(default_factory=dict)        # page -> count
    markers: list = field(default_factory=list)       # pages in order of appearance
    fn_defs: dict = field(default_factory=dict)       # n -> text
    fn_refs: list = field(default_factory=list)       # [(n, page)]
    table_pages: set = field(default_factory=set)     # pages containing tables
    fig_skips: dict = field(default_factory=dict)     # page -> [(file, reason)]
    chips: list = field(default_factory=list)         # [(label, page)]
    headings: list = field(default_factory=list)      # [(text, page)]
    turn_labels: list = field(default_factory=list)   # [(label, page)]


def sections_at_ref(repo: Path, ref: str) -> list[tuple[str, str]]:
    """[(filename, content)] for all section files at a git ref, 'WORKTREE',
    or an absolute directory path (used by the mutation tester)."""
    if ref == "WORKTREE":
        return [(p.name, p.read_text()) for p in sorted((repo / SECTIONS_DIR).glob("*.md"))]
    if Path(ref).is_absolute() and Path(ref).is_dir():
        return [(p.name, p.read_text()) for p in sorted(Path(ref).glob("*.md"))]
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, SECTIONS_DIR],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.split()
    out = []
    for n in sorted(names):
        if not n.endswith(".md"):
            continue
        content = subprocess.run(
            ["git", "show", f"{ref}:{n}"], cwd=repo, capture_output=True, text=True, check=True
        ).stdout
        out.append((Path(n).name, content))
    return out


def _table_to_text(m: re.Match, sec: "Section", page: int) -> str:
    t = m.group(0)

    def sup(sm):  # footnote refs inside tables, e.g. <sup>[11](#fn)</sup>
        for d in re.findall(r"\d+", sm.group(1)):
            sec.fn_refs.append((int(d), page))
        return " "
    t = RE_SUP.sub(sup, t)
    t = t.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    t = RE_TAG.sub(" ", t)
    return t


def _strip_sentinels(s: str) -> str:
    return RE_SENTINEL.sub(" ", s).strip()


def _clean_segment(seg: str, sec: Section, start: int) -> str:
    """Strip markup from the whole section, recording facts (page-attributed
    via the sentinels already embedded in `seg`) as we go."""

    def pg(m):
        return _page_at(m.string, m.start(), start)

    def table(m):
        sec.table_pages.add(pg(m))
        for sm in RE_SENTINEL.finditer(m.group(0)):   # multi-page tables
            sec.table_pages.add(int(sm.group(1)))
        return _table_to_text(m, sec, pg(m))
    seg = RE_TABLE.sub(table, seg)

    def figskip(m):
        # v1's declared-exclusion convention for deliberately omitted figures
        sec.fig_skips.setdefault(int(m.group(2)), []).append((m.group(1), m.group(3)))
        return " "
    seg = RE_FIGSKIP.sub(figskip, seg)
    seg = RE_COMMENT.sub(" ", seg)

    def piperule(m):
        sec.table_pages.add(pg(m))
        return " "
    seg = re.sub(r"^\|[-| :]+\|$", piperule, seg, flags=re.M)  # pipe-table rules
    seg = seg.replace("|", " ")                                # pipe-table cells

    def fndef(m):
        body = m.group(2)
        for lm in RE_LINK.finditer(body):          # citations live in footnotes
            sec.links.append((_strip_sentinels(lm.group(1)), lm.group(2), pg(m)))
        for lm in RE_AUTOLINK.finditer(body):
            sec.links.append((lm.group(1), lm.group(1), pg(m)))
        body_text = RE_LINK.sub(lambda l: l.group(1), body)
        body_text = RE_AUTOLINK.sub(r"\1", body_text)
        body_text = re.sub(r"(?m)^\s*[-*+][ \t]+", " ", body_text)  # list markers in defs
        sec.fn_defs[int(m.group(1))] = _strip_sentinels(body_text)
        return " "
    seg = RE_FNDEF.sub(fndef, seg)

    def image(m):
        p = pg(m)
        sec.images[p] = sec.images.get(p, 0) + 1
        return " "
    seg = RE_IMAGE.sub(image, seg)

    def directive(m):
        label = RE_TURN_LABEL.search(m.group(2) or "")
        if label:
            sec.turn_labels.append((_strip_sentinels(label.group(1)), pg(m)))
            return f"{label.group(1)}:"
        return " "
    seg = RE_DIRECTIVE.sub(directive, seg)

    def chip(m):
        sec.chips.append((_strip_sentinels(m.group(1)), pg(m)))
        return m.group(1)
    seg = RE_CHIP.sub(chip, seg)

    def link(m):
        sec.links.append((_strip_sentinels(m.group(1)), m.group(2), pg(m)))
        return m.group(1)
    seg = RE_LINK.sub(link, seg)

    def autolink(m):
        sec.links.append((m.group(1), m.group(1), pg(m)))
        return m.group(1)
    seg = RE_AUTOLINK.sub(autolink, seg)

    def fnref(m):
        sec.fn_refs.append((int(m.group(1)), pg(m)))
        return " "
    seg = RE_FNREF.sub(fnref, seg)

    def bold(m):
        text = m.group(1) or m.group(2)
        sec.bolds.append((_strip_sentinels(text), pg(m)))
        return text
    seg = RE_BOLD.sub(bold, seg)

    seg = RE_SUP.sub(" ", seg)
    seg = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", seg)   # italics

    def heading(m):
        sec.headings.append((_strip_sentinels(m.group(1)), pg(m)))
        return m.group(1)
    seg = re.sub(r"^#{1,6}\s+(.*)$", heading, seg, flags=re.M)
    seg = re.sub(r"^>\s?", "", seg, flags=re.M)               # blockquotes
    # unordered bullets: require same-line whitespace so a LONE "-" line (the
    # CA-01 artifact class!) is NOT consumed — it must surface as an extra token
    seg = re.sub(r"^[ \t]*[-*+][ \t]+", "", seg, flags=re.M)
    seg = re.sub(r"^```.*$", " ", seg, flags=re.M)            # code fences
    seg = seg.replace("`", "")
    seg = RE_TAG.sub(" ", seg)
    seg = html.unescape(seg)
    seg = re.sub(r"\\([*_\[\]()#`~.!|])", r"\1", seg)         # md escapes
    return seg


SENTINEL = "XQPAGEQX{n}XQX"
RE_SENTINEL = re.compile(r"XQPAGEQX(\d+)XQX")


def _page_at(seg: str, pos: int, start: int) -> int:
    """Page of a char position = last sentinel before it (else section start)."""
    last = None
    for m in RE_SENTINEL.finditer(seg, 0, pos):
        last = m
    return int(last.group(1)) if last else start


def project(name: str, text: str) -> Section:
    """Clean the WHOLE section in one pass (inline page markers must not split
    emphasis/captions); page attribution via sentinel tokens."""
    h = RE_HEADER.search(text)
    start, end = (int(h.group(1)), int(h.group(2))) if h else (0, 0)
    sec = Section(name=name, page_start=start, page_end=end)

    def marker(m):
        sec.markers.append(int(m.group(1)))
        return f" {SENTINEL.format(n=m.group(1))} "
    text = RE_MARKER.sub(marker, text)

    cleaned = _clean_segment(text, sec, start)

    page = start
    for tok in norm.tokens(cleaned, calibration=True):
        sm = RE_SENTINEL.fullmatch(tok)
        if sm:
            page = int(sm.group(1))
            continue
        sec.tokens.append((tok, page))
    return sec
