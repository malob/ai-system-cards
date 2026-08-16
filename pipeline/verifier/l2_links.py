"""Independent PDF-destination -> Markdown-anchor verification (L2).

This module deliberately does not import the generator.  It reopens source.pdf,
builds source heading identities from the PDF outline plus printed full-heading
geometry, reads /GoTo annotations directly, and compares those facts with a
sequential projection of the canonical Markdown.

The public entry point is :func:`verify`.  Its :class:`L2Report` is stable and
JSON-serializable so the site-side verifier can consume ``expected_links`` after
an Astro build without sharing slug or destination-resolution code.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

import fitz

import norm


MAX_HEADING_DISTANCE = 24.0

RE_HEADER = re.compile(r"<!--\s*source: source\.pdf pages (\d+)-(\d+)\s*-->")
RE_EVENT = re.compile(
    r"(?P<marker><!--\s*p\.(?P<page>\d+)\s*-->)"
    r"|(?P<heading>^(?P<hashes>#{1,6})[ \t]+(?P<heading_text>[^\n]+)$)"
    r"|(?P<html><a\b[^>]*\bhref=(?P<quote>[\"'])(?P<html_href>#[^\"']*)"
    r"(?P=quote)[^>]*>(?P<html_text>.*?)</a>)"
    r"|(?P<markdown>(?<!!)\[(?P<md_text>[^\]\n]*)\]\((?P<md_href>#[^)]*)\))",
    re.I | re.M | re.S,
)


def _plain(text: str) -> str:
    """Visible text for the small Markdown/HTML subset used by headings/links."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\[\^\d+\]", "", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?<!\\)[*_~]", "", text)
    text = re.sub(r"\\([*_[\]()#`~.!|])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def text_key(text: str) -> str:
    """Case/space/punctuation-insensitive occurrence matching key."""
    folded = norm.normalize(_plain(text), calibration=True).casefold()
    return "".join(ch for ch in folded if ch.isalnum())


def heading_key(text: str) -> str:
    """Outline/Markdown title key; punctuation remains semantically visible."""
    return norm.squash(_plain(text), calibration=True).casefold()


def _base_github_slug(text: str) -> str:
    """Independent equivalent of github-slugger for visible heading text.

    github-slugger retains letters, marks, numbers, ``-``/``_`` and literal
    spaces, removes punctuation/symbol/control code points, then changes spaces
    to hyphens.  The final DOM lane observes the real rehype-generated IDs.
    """
    out = []
    for ch in _plain(text).lower():
        category = unicodedata.category(ch)
        if ch == " " or ch in "-_" or category[0] in "LMN":
            out.append(ch)
    return "".join(out).replace(" ", "-")


def github_slugs(titles: Iterable[str]) -> list[str]:
    """Return github-slugger-compatible, occurrence-disambiguated slugs."""
    occurrences: dict[str, int] = {}
    result = []
    for title in titles:
        base = _base_github_slug(title)
        slug = base
        while slug in occurrences:
            occurrences[base] = occurrences.get(base, 0) + 1
            slug = f"{base}-{occurrences[base]}"
        occurrences.setdefault(base, 0)
        occurrences[slug] = 0
        result.append(slug)
    return result


@dataclass(frozen=True)
class SourceLine:
    text: str
    bbox: tuple[float, float, float, float]
    size: float
    bold: bool


@dataclass(frozen=True)
class OutlineItem:
    ordinal: int
    level: int
    path: tuple[int, ...]
    title: str
    page: int
    raw_y: float | None


@dataclass(frozen=True)
class SourceAnnotation:
    source_id: str
    page: int
    anchor: str
    rect: tuple[float, float, float, float]
    line_start_x: float | None
    dest_page: int
    dest_y: float | None
    raw_dest_y: float | None
    dest_x: float | None
    name: str
    unresolvable: bool
    xref: int

    @property
    def destination_key(self) -> tuple:
        return (
            self.dest_page,
            None if self.dest_y is None else round(self.dest_y, 1),
            self.name,
            self.unresolvable,
        )


@dataclass(frozen=True)
class SourceModel:
    pdf: str
    sha256: str
    page_heights: tuple[float, ...]
    lines: tuple[tuple[SourceLine, ...], ...]
    outline: tuple[OutlineItem, ...]
    annotations: tuple[SourceAnnotation, ...]


@dataclass(frozen=True)
class MarkdownHeading:
    md_id: str
    file: str
    ordinal: int
    level: int
    title: str
    page: int
    slug: str = ""


@dataclass(frozen=True)
class Heading:
    identity: str
    md_id: str | None
    file: str
    ordinal: int
    level: int
    title: str
    page: int
    slug: str | None
    outline_ordinal: int | None
    outline_path: tuple[int, ...]
    bbox: tuple[float, float, float, float] | None


@dataclass(frozen=True)
class OutputOccurrence:
    output_id: str
    file: str
    ordinal: int
    text: str
    target: str
    page: int
    start: int
    end: int
    relocated_footnote: bool
    separator: str = ""


@dataclass(frozen=True)
class ParsedMarkdown:
    headings: tuple[MarkdownHeading, ...]
    links: tuple[OutputOccurrence, ...]


@dataclass(frozen=True)
class SourceLink:
    source_id: str
    page: int
    anchor: str
    members: tuple[str, ...]
    dest_page: int
    dest_y: float | None
    name: str
    unresolvable: bool
    rects: tuple[tuple[float, float, float, float], ...]


@dataclass(frozen=True)
class OutputLink:
    output_id: str
    file: str
    ordinal: int
    page: int
    text: str
    target: str
    members: tuple[str, ...]
    member_texts: tuple[str, ...]
    member_ordinals: tuple[int, ...]
    relocated_footnote: bool


@dataclass
class L2Report:
    schema_version: int
    card_id: str
    source_pdf: str
    source_sha256: str
    canonical_sections_sha256: str
    section_sha256: dict[str, str]
    stats: dict[str, int]
    flags: list[dict]
    canonical_links: list[dict] = field(default_factory=list)
    expected_links: list[dict] = field(default_factory=list)
    exclusions: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "card_id": self.card_id,
            "source_pdf": self.source_pdf,
            "source_sha256": self.source_sha256,
            "canonical_sections_sha256": self.canonical_sections_sha256,
            "section_sha256": dict(self.section_sha256),
            "stats": dict(self.stats),
            "flags": list(self.flags),
            "canonical_links": list(self.canonical_links),
            "expected_links": list(self.expected_links),
            "exclusions": list(self.exclusions),
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, ensure_ascii=False, sort_keys=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_lines(page) -> tuple[SourceLine, ...]:
    lines = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = [s for s in line.get("spans", []) if s.get("text", "").strip()]
            if not spans:
                continue
            spans.sort(key=lambda s: s["bbox"][0])
            text = "".join(s["text"] for s in spans)
            bbox = (
                min(s["bbox"][0] for s in spans),
                min(s["bbox"][1] for s in spans),
                max(s["bbox"][2] for s in spans),
                max(s["bbox"][3] for s in spans),
            )
            bold = all(bool(s.get("flags", 0) & 16) or "Bold" in s.get("font", "")
                       for s in spans)
            lines.append(SourceLine(text, tuple(round(v, 2) for v in bbox),
                                    max(float(s.get("size", 0)) for s in spans), bold))
    return tuple(sorted(lines, key=lambda line: (line.bbox[1], line.bbox[0])))


def _outline(doc) -> tuple[OutlineItem, ...]:
    items = []
    ancestors: dict[int, int] = {}
    for ordinal, row in enumerate(doc.get_toc(simple=False)):
        level, title, page = int(row[0]), str(row[1]), int(row[2])
        dest = row[3] if len(row) > 3 and isinstance(row[3], dict) else {}
        point = dest.get("to")
        raw_y = None
        if point is not None:
            try:
                raw_y = float(point.y)
            except (AttributeError, TypeError, ValueError):
                pass
        ancestors[level] = ordinal
        ancestors = {k: v for k, v in ancestors.items() if k <= level}
        path = tuple(ancestors[k] for k in sorted(ancestors))
        items.append(OutlineItem(ordinal, level, path, title, page, raw_y))
    return tuple(items)


def _source_annotations(doc, source_hash: str,
                        document_lines: tuple[tuple[SourceLine, ...], ...]) -> tuple[SourceAnnotation, ...]:
    annotations = []
    for pidx in range(doc.page_count):
        page = doc[pidx]
        for lidx, link in enumerate(page.get_links()):
            if link.get("kind") not in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                continue
            rect = fitz.Rect(link["from"])
            anchor = page.get_text(clip=rect).strip().replace("\n", " ")
            line_hits = [line for line in document_lines[pidx]
                         if min(line.bbox[3], rect.y1) - max(line.bbox[1], rect.y0) > 2]
            line_start_x = min((line.bbox[0] for line in line_hits), default=None)
            dest_page = int(link.get("page", -1)) + 1
            raw_y = dest_y = dest_x = None
            point = link.get("to")
            if point is not None:
                try:
                    raw_y = float(point.y)
                    dest_x = float(point.x)
                    if 0 < dest_page <= doc.page_count:
                        # PDF destinations are bottom-up while extracted span
                        # geometry is top-down.  Use the destination page's
                        # height: mixed-size PDFs must not borrow the source H.
                        dest_y = float(doc[dest_page - 1].rect.height) - raw_y
                except (AttributeError, TypeError, ValueError):
                    raw_y = dest_y = dest_x = None
            unresolvable = dest_page == 0
            name = (link.get("nameddest") or link.get("name") or "") if unresolvable else ""
            rect_tuple = tuple(round(float(v), 2) for v in rect)
            fingerprint = json.dumps(
                [source_hash, pidx + 1, lidx, rect_tuple, dest_page,
                 None if raw_y is None else round(raw_y, 3), name],
                ensure_ascii=False, separators=(",", ":"),
            ).encode()
            source_id = hashlib.sha256(fingerprint).hexdigest()[:20]
            annotations.append(SourceAnnotation(
                source_id, pidx + 1, anchor, rect_tuple, line_start_x, dest_page,
                None if dest_y is None else round(dest_y, 2),
                None if raw_y is None else round(raw_y, 2),
                None if dest_x is None else round(dest_x, 2), name,
                unresolvable, int(link.get("xref", 0) or 0),
            ))
    return tuple(annotations)


@lru_cache(maxsize=8)
def _load_source_cached(path_text: str, source_hash: str) -> SourceModel:
    path = Path(path_text)
    doc = fitz.open(path)
    try:
        heights = tuple(float(doc[i].rect.height) for i in range(doc.page_count))
        lines = tuple(_source_lines(doc[i]) for i in range(doc.page_count))
        outline = _outline(doc)
        annotations = _source_annotations(doc, source_hash, lines)
    finally:
        doc.close()
    return SourceModel(str(path.resolve()), source_hash, heights, lines, outline, annotations)


def load_source(pdf_path: Path) -> SourceModel:
    """Hash and reopen ``source.pdf``; facts are cached by the actual digest.

    Stat metadata is intentionally not authoritative: replacing bytes while
    preserving size and mtime must never reuse an older source model.
    """
    path = pdf_path.resolve()
    return _load_source_cached(str(path), _sha256(path))


def _in_footnote_definition(text: str, pos: int) -> bool:
    line_start = text.rfind("\n", 0, pos) + 1
    line = text[line_start:text.find("\n", pos) if "\n" in text[pos:] else len(text)]
    if re.match(r"\[\^\d+\]:", line):
        return True
    if not line.startswith("    "):
        return False
    cursor = line_start
    while cursor > 0:
        previous_end = cursor - 1
        previous_start = text.rfind("\n", 0, previous_end) + 1
        previous = text[previous_start:previous_end]
        if re.match(r"\[\^\d+\]:", previous):
            return True
        if previous and not previous.startswith("    "):
            return False
        cursor = previous_start
    return False


def parse_markdown(sections_text: Iterable[tuple[str, str]]) -> ParsedMarkdown:
    """Sequentially project canonical headings and internal-link occurrences."""
    headings = []
    links = []
    heading_ordinal = link_ordinal = 0
    for filename, text in sections_text:
        header = RE_HEADER.search(text)
        page = int(header.group(1)) if header else 0
        prior_internal_end = None
        for event in RE_EVENT.finditer(text):
            if event.group("marker"):
                page = int(event.group("page"))
                continue
            if event.group("heading"):
                title = _plain(event.group("heading_text"))
                headings.append(MarkdownHeading(
                    f"{filename}:h{heading_ordinal}", filename, heading_ordinal,
                    len(event.group("hashes")), title, page,
                ))
                heading_ordinal += 1
                continue
            if event.group("html"):
                label, target = _plain(event.group("html_text")), event.group("html_href")
            else:
                label, target = _plain(event.group("md_text")), event.group("md_href")
            separator = text[prior_internal_end:event.start()] if prior_internal_end is not None else ""
            links.append(OutputOccurrence(
                f"{filename}:l{link_ordinal}", filename, link_ordinal, label,
                target, page, event.start(), event.end(),
                _in_footnote_definition(text, event.start()), separator,
            ))
            prior_internal_end = event.end()
            link_ordinal += 1

    slugs = github_slugs(h.title for h in headings)
    headings = [MarkdownHeading(**{**asdict(h), "slug": slug})
                for h, slug in zip(headings, slugs)]
    return ParsedMarkdown(tuple(headings), tuple(links))


def _bbox_union(lines: Iterable[SourceLine]) -> tuple[float, float, float, float]:
    lines = tuple(lines)
    return (
        min(line.bbox[0] for line in lines), min(line.bbox[1] for line in lines),
        max(line.bbox[2] for line in lines), max(line.bbox[3] for line in lines),
    )


def _heading_bbox_candidates(lines: tuple[SourceLine, ...], title: str) -> list[tuple]:
    target = heading_key(title)
    candidates = []
    for start in range(len(lines)):
        combined = ""
        for end in range(start, min(len(lines), start + 8)):
            if end > start and lines[end].bbox[1] - lines[end - 1].bbox[3] > 18:
                break
            combined += heading_key(lines[end].text)
            if combined == target:
                candidates.append(_bbox_union(lines[start:end + 1]))
                break
            if len(combined) > len(target) or not target.startswith(combined):
                break
    return candidates


def _coord_distance(raw_y: float | None, height: float,
                    bbox: tuple[float, float, float, float]) -> float:
    if raw_y is None:
        return bbox[1]
    # PyMuPDF has exposed outline coordinates in both conventions across PDF
    # producers.  This coordinate only disambiguates duplicate printed title
    # occurrences; link destinations below always use the explicit conversion.
    return min(abs(raw_y - bbox[1]), abs((height - raw_y) - bbox[1]))


def accept_headings(source: SourceModel, parsed: ParsedMarkdown) -> tuple[list[Heading], list[dict]]:
    """Build source-first heading identities, then bind Markdown headings.

    Destination resolution must never derive its candidate inventory from the
    output under test.  Otherwise deleting a true child heading and repointing
    its link to the surviving parent shrinks the candidate set and can pass.
    """
    flags = []
    source_headings = []
    # Cover typography and empty/ornamental bookmarks are not canonical
    # article headings.  Every meaningful post-cover outline item is source
    # authority even when the Markdown under test has deleted it.
    for item in source.outline:
        if item.page <= 1 or len(text_key(item.title)) < 3:
            continue
        candidates = (_heading_bbox_candidates(source.lines[item.page - 1], item.title)
                      if 0 < item.page <= len(source.lines) else [])
        bbox = None
        if candidates:
            height = source.page_heights[item.page - 1]
            bbox = min(candidates,
                       key=lambda b: (_coord_distance(item.raw_y, height, b), b[1], b[0]))
        if bbox is None:
            flags.append(_l2_flag(item.page, "source-heading-bbox-unlocated",
                                  heading=item.title, outline_ordinal=item.ordinal))
        source_headings.append(Heading(
            f"outline:{item.ordinal}", None, "", -1, item.level, _plain(item.title),
            item.page, None, item.ordinal, item.path, bbox,
        ))

    source_by_key: dict[tuple[int, str], list[int]] = {}
    for index, heading in enumerate(source_headings):
        source_by_key.setdefault((heading.page, heading_key(heading.title)), []).append(index)
    source_use: dict[tuple[int, str], int] = {}
    markdown_only = []
    for md in parsed.headings:
        key = (md.page, heading_key(md.title))
        choices = source_by_key.get(key, [])
        use = source_use.get(key, 0)
        source_use[key] = use + 1
        if use >= len(choices):
            flags.append(_l2_flag(md.page, "heading-outline-unmatched",
                                  heading=md.title, file=md.file))
            candidates = (_heading_bbox_candidates(source.lines[md.page - 1], md.title)
                          if 0 < md.page <= len(source.lines) else [])
            markdown_only.append(Heading(
                f"md:{md.md_id}", md.md_id, md.file, md.ordinal, md.level, md.title,
                md.page, md.slug, None, (), candidates[0] if candidates else None,
            ))
        else:
            index = choices[use]
            source_headings[index] = replace(
                source_headings[index], md_id=md.md_id, file=md.file,
                ordinal=md.ordinal, level=md.level, title=md.title, slug=md.slug,
            )

    for heading in source_headings:
        if heading.md_id is None:
            flags.append(_l2_flag(
                heading.page, "target-heading-missing", heading=heading.title,
                outline_ordinal=heading.outline_ordinal,
            ))
    return source_headings + markdown_only, flags


def _rect_adjacent(a: SourceAnnotation, b: SourceAnnotation) -> bool:
    ax0, ay0, ax1, ay1 = a.rect
    bx0, by0, bx1, by1 = b.rect
    ah, bh = ay1 - ay0, by1 - by0
    overlap = min(ay1, by1) - max(ay0, by0)
    if overlap >= 0.35 * max(1.0, min(ah, bh)):
        return -3 <= bx0 - ax1 <= max(24.0, 1.8 * max(ah, bh))
    # A wrapped annotation continues back at the same or a smaller indent.
    # Merely sharing a destination is not enough: adjacent list items can link
    # independently to the same heading (Opus p.79).
    begins_line = b.line_start_x is not None and abs(bx0 - b.line_start_x) <= 4.0
    line_gap = by0 - ay1
    # Raw table text can expose a whole row as one PDF line, so the local cell
    # continuation is not the page-line x0.  Exact/touching line boxes are the
    # stronger signal there; ordinary prose wraps also require a true line start.
    return (0 <= line_gap <= max(8.0, 0.8 * max(ah, bh))
            and (line_gap <= 0.75 or begins_line) and bx0 <= ax0 + 36.0)


def group_source_annotations(annotations: Iterable[SourceAnnotation]) -> list[SourceLink]:
    groups = []
    ordered = sorted(annotations, key=lambda a: (a.page, a.rect[1], a.rect[0], a.source_id))
    current: list[SourceAnnotation] = []
    for annotation in ordered:
        if (current and annotation.page == current[-1].page
                and annotation.destination_key == current[-1].destination_key
                and _rect_adjacent(current[-1], annotation)):
            current.append(annotation)
            continue
        if current:
            groups.append(_source_group(current))
        current = [annotation]
    if current:
        groups.append(_source_group(current))
    return groups


def _source_group(members: list[SourceAnnotation]) -> SourceLink:
    first = members[0]
    gid = hashlib.sha256("|".join(m.source_id for m in members).encode()).hexdigest()[:20]
    return SourceLink(
        gid, first.page, " ".join(m.anchor for m in members).strip(),
        tuple(m.source_id for m in members), first.dest_page, first.dest_y,
        first.name, first.unresolvable, tuple(m.rect for m in members),
    )


def blank_source_disposition(link: SourceLink) -> str | None:
    """Classify the measured empty-clipped-annotation source artifact.

    Risk p.184 contains a 2.89pt-wide blank /GoTo sliver.  Only that mechanical
    shape is excluded; a wider blank annotation is unreadable source evidence
    and must fail closed.
    """
    if text_key(link.anchor):
        return None
    widths = [rect[2] - rect[0] for rect in link.rects]
    return ("blank-anchor-sliver" if widths and max(widths) < 3.0
            else "source-anchor-unreadable")


def _joinable_output(a: OutputOccurrence, b: OutputOccurrence) -> bool:
    if a.file != b.file or a.page != b.page or a.target != b.target:
        return False
    return bool(re.fullmatch(r"[\s*_`~:;,.()§\-–—]*", b.separator)
                or re.fullmatch(r"[\s*_`~:;,.()§\-–—]*and[\s*_`~:;,.()§\-–—]*",
                                b.separator, re.I))


def group_output_occurrences(occurrences: Iterable[OutputOccurrence]) -> list[OutputLink]:
    groups = []
    current: list[OutputOccurrence] = []
    for occurrence in occurrences:
        if current and _joinable_output(current[-1], occurrence):
            current.append(occurrence)
            continue
        if current:
            groups.append(_output_group(current))
        current = [occurrence]
    if current:
        groups.append(_output_group(current))
    return groups


def _output_group(members: list[OutputOccurrence]) -> OutputLink:
    first = members[0]
    return OutputLink(
        "+".join(m.output_id for m in members), first.file, first.ordinal,
        first.page, " ".join(m.text for m in members).strip(), first.target,
        tuple(m.output_id for m in members), tuple(m.text for m in members),
        tuple(m.ordinal for m in members), any(m.relocated_footnote for m in members),
    )


def pair_links(source_links: list[SourceLink], output_links: list[OutputLink]) -> tuple[dict[int, int], list[dict]]:
    """Pair source/output logical occurrences without consulting destinations."""
    pairs: dict[int, int] = {}
    notes = []

    # Exact same-page keys, including repeated labels, pair in reading order.
    pages = sorted({s.page for s in source_links} | {o.page for o in output_links})
    for page in pages:
        keys = sorted({text_key(s.anchor) for s in source_links if s.page == page}
                      | {text_key(o.text) for o in output_links if o.page == page})
        for key in keys:
            sis = [i for i, s in enumerate(source_links)
                   if i not in pairs and s.page == page and text_key(s.anchor) == key]
            used_outputs = set(pairs.values())
            ois = [i for i, o in enumerate(output_links)
                   if i not in used_outputs and o.page == page and text_key(o.text) == key]
            if sis and len(sis) == len(ois):
                for si, oi in zip(sis, ois):
                    pairs[si] = oi

    # The one canonical relocation class: a link in a footnote definition is
    # moved to the section tail.  Only a globally unique printed label may
    # override page identity.
    unmatched_sources = [i for i in range(len(source_links)) if i not in pairs]
    unmatched_outputs = [i for i in range(len(output_links)) if i not in set(pairs.values())]
    for oi in unmatched_outputs:
        output = output_links[oi]
        if not output.relocated_footnote:
            continue
        key = text_key(output.text)
        sis = [si for si in unmatched_sources if text_key(source_links[si].anchor) == key]
        ois = [oj for oj in unmatched_outputs if text_key(output_links[oj].text) == key]
        if len(sis) == len(ois) == 1:
            pairs[sis[0]] = oi
            unmatched_sources.remove(sis[0])
            notes.append({"kind": "relocated-footnote", "source": source_links[sis[0]].source_id,
                          "output": output.output_id})
    return pairs, notes


def _printed_heading_candidates(anchor: str, headings: list[Heading]) -> list[Heading]:
    headings = [h for h in headings if h.outline_ordinal is not None]
    plain = norm.normalize(_plain(anchor), calibration=True).casefold().strip(" .,:;()[]")
    direct = [h for h in headings
              if norm.normalize(_plain(h.title), calibration=True).casefold() == plain]
    if direct:
        return direct
    reference = re.fullmatch(r"(?:(?:section|appendix)\s+)?(\d+(?:\.\d+)*)", plain)
    if reference:
        number = reference.group(1)
        return [h for h in headings
                if re.match(rf"^{re.escape(number)}(?:\s|$)",
                            norm.normalize(_plain(h.title), calibration=True).casefold())]
    claim = re.fullmatch(r"claim\s+(\d+)", plain)
    if claim:
        return [h for h in headings
                if re.search(rf"(?:^|\s)claim\s+{claim.group(1)}(?::|\s|$)",
                             norm.normalize(_plain(h.title), calibration=True).casefold())]
    return []


def resolve_destination(source: SourceLink, headings: list[Heading]) -> tuple[Heading | None, str]:
    """Return the uniquely accepted heading identity for a raw PDF destination."""
    if source.dest_page == 0 or source.unresolvable:
        candidates = _printed_heading_candidates(source.anchor, headings)
        return (candidates[0], "printed-heading-recovery") if len(candidates) == 1 else (None, "source-unresolvable")
    candidates = [h for h in headings
                  if h.outline_ordinal is not None
                  and h.page == source.dest_page and h.bbox is not None]
    if not candidates:
        return None, "destination-page-has-no-heading"
    if source.dest_y is None:
        printed = _printed_heading_candidates(source.anchor, candidates)
        if len(printed) == 1:
            return printed[0], "printed-heading-no-coordinate"
        if len(candidates) == 1:
            return candidates[0], "single-heading-no-coordinate"
        return None, "destination-coordinate-missing"
    # Google Docs destinations normally sit in the whitespace immediately
    # ABOVE the intended heading.  A nearest-edge rule then selects the parent
    # heading above on dense pages.  Full bboxes give the independent rule:
    # contain first; otherwise activate the first heading that begins below the
    # point.  Only fall back upward after the final heading on the page.
    inside = [h for h in candidates if h.bbox[1] <= source.dest_y <= h.bbox[3]]
    if len(inside) == 1:
        return inside[0], "geometry"
    if len(inside) > 1:
        return None, "destination-heading-ambiguous"
    below = sorted((h.bbox[1] - source.dest_y, h) for h in candidates
                   if h.bbox[1] > source.dest_y)
    ranked = below or sorted((source.dest_y - h.bbox[3], h) for h in candidates
                             if h.bbox[3] < source.dest_y)
    if not ranked:
        return None, "destination-heading-ambiguous"
    best_distance, best = ranked[0]
    if best_distance > MAX_HEADING_DISTANCE:
        return None, "destination-outside-heading-band"
    return best, "geometry"


def _l2_flag(page: int, kind: str, **detail) -> dict:
    return {"invariant": "L2", "page": page, "severity": "major",
            "detail": {"kind": kind, **detail}}


def _card_id(source_pdf: str) -> str:
    parts = Path(source_pdf).parts
    try:
        index = parts.index("cards")
        return "/".join(parts[index + 1:index + 3])
    except (ValueError, IndexError):
        return ""


def evaluate(source: SourceModel, headings: list[Heading], heading_flags: list[dict],
             source_links: list[SourceLink], output_links: list[OutputLink],
             exclusions: list[dict], canonical_sections_sha256: str = "") -> L2Report:
    pairs, pairing_notes = pair_links(source_links, output_links)
    flags = list(heading_flags)
    expected_links = []
    target_headings = {f"#{h.slug}": h for h in headings if h.slug is not None}
    recovered = unresolved = matched = 0

    # DOM expectations locate by visible link text plus its occurrence among
    # links with that text.  This remains stable when the renderer inserts its
    # own footnote/backlink anchors, unlike a global article-link index.
    member_occurrence: dict[str, int] = {}
    member_locator: dict[str, tuple[str, int]] = {}
    members_in_order = sorted(
        ((ordinal, member, text)
         for link in output_links
         for ordinal, member, text in zip(link.member_ordinals, link.members, link.member_texts)),
        key=lambda item: item[0],
    )
    for _, member, text in members_in_order:
        visible = re.sub(r"\s+", " ", text).strip()
        occurrence = member_occurrence.get(visible, 0)
        member_occurrence[visible] = occurrence + 1
        member_locator[member] = (visible, occurrence)

    for si, oi in sorted(pairs.items()):
        source_link, output_link = source_links[si], output_links[oi]
        expected, resolution = resolve_destination(source_link, headings)
        normalized_target = "#" + unquote(output_link.target[1:]) if output_link.target.startswith("#") else output_link.target
        actual = target_headings.get(normalized_target)
        if resolution.startswith("printed-heading"):
            recovered += 1
        if expected is None and resolution == "source-unresolvable":
            unresolved += 1
            flags.append(_l2_flag(source_link.page,
                                  "empty-target" if output_link.target == "#"
                                  else "unresolved-source-linked",
                                  text=output_link.text[:100], target=output_link.target,
                                  source_id=source_link.source_id))
            continue
        if expected is None:
            flags.append(_l2_flag(source_link.page, "destination-unresolved",
                                  reason=resolution, text=source_link.anchor[:100],
                                  dest_page=source_link.dest_page, dest_y=source_link.dest_y,
                                  source_id=source_link.source_id))
            continue
        if expected.slug is None:
            flags.append(_l2_flag(source_link.page, "target-heading-missing-for-link",
                                  text=source_link.anchor[:100],
                                  expected_heading=expected.title[:100],
                                  source_id=source_link.source_id))
            continue
        expected_href = f"#{expected.slug}"
        for member, member_ordinal in zip(output_link.members, output_link.member_ordinals):
            visible, occurrence = member_locator[member]
            expected_links.append({
                "key": f"{source_link.source_id}/{member}",
                "targetId": expected.slug,
                "linkText": visible,
                "occurrence": occurrence,
                "source_id": source_link.source_id,
                "output_id": member,
                "file": output_link.file,
                "ordinal": member_ordinal,
                "authoredLinkIndex": member_ordinal,
                "source_page": source_link.page,
                "expected_heading_id": expected.identity,
                "expected_href": expected_href,
                "actual_href": output_link.target,
                "resolution": resolution,
            })
        if actual is None:
            flags.append(_l2_flag(source_link.page, "dead-target",
                                  text=output_link.text[:100], target=output_link.target,
                                  expected=expected_href, output_id=output_link.output_id))
        elif actual.identity != expected.identity:
            flags.append(_l2_flag(source_link.page, "wrong-existing-target",
                                  text=output_link.text[:100], target=output_link.target,
                                  expected=expected_href, expected_heading=expected.title[:100],
                                  actual_heading=actual.title[:100], output_id=output_link.output_id))
        else:
            matched += 1

    paired_outputs = set(pairs.values())
    for si, source_link in enumerate(source_links):
        if si not in pairs:
            expected, resolution = resolve_destination(source_link, headings)
            if expected is None and resolution == "source-unresolvable":
                unresolved += 1
                exclusions.append({"kind": "source-unresolvable-plain-text",
                                   "page": source_link.page,
                                   "source_id": source_link.source_id})
                continue
            flags.append(_l2_flag(source_link.page, "missing-output-link",
                                  text=source_link.anchor[:100], dest_page=source_link.dest_page,
                                  source_id=source_link.source_id))
    for oi, output_link in enumerate(output_links):
        if oi not in paired_outputs:
            flags.append(_l2_flag(output_link.page, "unexplained-output-link",
                                  text=output_link.text[:100], target=output_link.target,
                                  output_id=output_link.output_id,
                                  dead_target=output_link.target not in target_headings))

    flags.sort(key=lambda f: (f["page"], f["detail"].get("kind", ""),
                              f["detail"].get("source_id", ""),
                              f["detail"].get("output_id", "")))
    expected_links.sort(key=lambda e: (e["ordinal"], e["source_id"]))
    exclusions.sort(key=lambda e: (e.get("page", 0), e.get("kind", ""),
                                   e.get("source_id", "")))
    stats = {
        "source_annotations": len(source.annotations),
        "source_logical_links": len(source_links),
        "output_occurrences": sum(len(link.members) for link in output_links),
        "output_logical_links": len(output_links),
        "paired_logical_links": len(pairs),
        "exact_destinations": matched,
        "printed_heading_recoveries": recovered,
        "unresolvable_source_links": unresolved,
        "excluded": len(exclusions),
        "pairing_notes": len(pairing_notes),
        "major_findings": len(flags),
    }
    return L2Report(
        schema_version=1,
        card_id=_card_id(source.pdf),
        source_pdf=Path(source.pdf).name,
        source_sha256=source.sha256,
        canonical_sections_sha256=canonical_sections_sha256,
        section_sha256={},
        stats=stats,
        flags=flags,
        expected_links=expected_links,
        exclusions=exclusions,
    )


def sections_sha256(sections_text: Iterable[tuple[str, str]]) -> str:
    """Digest canonical section names and exact UTF-8 bytes in input order."""
    digest = hashlib.sha256()
    for filename, text in sections_text:
        name = filename.encode("utf-8")
        body = text.encode("utf-8")
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(body).to_bytes(8, "big"))
        digest.update(body)
    return digest.hexdigest()


def section_sha256(sections_text: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {filename: hashlib.sha256(text.encode("utf-8")).hexdigest()
            for filename, text in sections_text}


def verify(pdf_path: Path, sections_text: Iterable[tuple[str, str]],
           toc_pages: Iterable[int] = ()) -> L2Report:
    """Run the independent L2 source-to-canonical comparison."""
    sections_text = tuple(sections_text)
    source = load_source(pdf_path)
    parsed = parse_markdown(sections_text)
    headings, heading_flags = accept_headings(source, parsed)
    excluded_pages = {1, *map(int, toc_pages)}
    page_scoped_annotations = []
    exclusions = []
    for annotation in source.annotations:
        if annotation.page in excluded_pages:
            exclusions.append({"kind": "cover-or-toc", "page": annotation.page,
                               "source_id": annotation.source_id})
        else:
            page_scoped_annotations.append(annotation)
    # Group first: a printed "Section 2.7" can be two adjacent annotations
    # whose individual "2.7" fragment is shorter than the exclusion floor.
    source_links = []
    for link in group_source_annotations(page_scoped_annotations):
        disposition = blank_source_disposition(link)
        if disposition == "blank-anchor-sliver":
            exclusions.append({"kind": disposition, "page": link.page,
                               "source_id": link.source_id, "text": link.anchor})
        elif disposition == "source-anchor-unreadable":
            heading_flags.append(_l2_flag(
                link.page, disposition, source_id=link.source_id,
                rects=[list(rect) for rect in link.rects],
            ))
        else:
            source_links.append(link)
    # Group before classifying blank labels: `[Section](#x) [3.6](#x)` is one
    # source link and both authored members must share its exact expectation.
    # Output-only blank anchors are NOT excluded: they remain unexplained and
    # fail closed even if their href names a real heading.
    output_links = group_output_occurrences(parsed.links)
    report = evaluate(source, headings, heading_flags, source_links, output_links,
                      exclusions, sections_sha256(sections_text))
    semantic = {entry["output_id"]: entry for entry in report.expected_links}
    report.canonical_links = []
    for occurrence in sorted(parsed.links, key=lambda item: item.ordinal):
        expectation = semantic.get(occurrence.output_id)
        report.canonical_links.append({
            "authoredLinkIndex": occurrence.ordinal,
            "file": occurrence.file,
            "sourcePage": occurrence.page,
            "text": occurrence.text,
            "href": occurrence.target,
            "output_id": occurrence.output_id,
            "relocatedFootnote": occurrence.relocated_footnote,
            "key": expectation.get("key") if expectation else None,
            "source_id": expectation.get("source_id") if expectation else None,
            "expected_target_id": expectation.get("targetId") if expectation else None,
        })
    report.section_sha256 = section_sha256(sections_text)
    return report
