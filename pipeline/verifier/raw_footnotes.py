"""Independent source-PDF authority for Markdown footnote dispositions.

This module intentionally does *not* import :mod:`oracle` and does not consume
the generator's ``zone`` / ``fn`` annotations.  It reopens ``source.pdf`` and
observes two pieces of typography directly:

* superscript numeric reference glyphs; and
* body-relative smaller, left-margin numeric definition markers followed by
  the contiguous smaller-type region at the bottom of the source page.

The verifier then binds each canonical definition occurrence by
``(section, number, reference pages)`` to one concrete source occurrence
``(marker page, marker bbox)``.  A bare integer is deliberately not an
identity: PDFs commonly restart numbering in later sections.

This is a narrow authority seam, not a general-purpose footnote parser.  Its
current contract covers numeric superscript references and numeric left-margin
definition markers set smaller than the document body, with the definition
beginning on the same or adjacent page. Symbol/letter markers and endnotes are
outside the observer contract and must not be claimed as covered.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:  # PyMuPDF 1.24+
    import pymupdf as fitz
except ImportError:  # pragma: no cover - compatibility with the repo's v1 env
    import fitz  # type: ignore[no-redef]


SUPER = 1
OBSERVER_SCHEMA_VERSION = 1
PYMUPDF_VERSION = str(getattr(fitz, "__version__", "unknown"))
SMALL_TYPE_GAP = 0.8
LEFT_MARGIN_SLOP = 5.0
FOOTER_BAND = 42.0
VERTICAL_GAP = 16.0

_NUMERIC = re.compile(r"\d{1,3}")
_HEADER = re.compile(r"<!--\s*source: source\.pdf pages (\d+)-(\d+)\s*-->")
_PAGE_MARKER = re.compile(r"<!--\s*p\.(\d+)\s*-->")
_FN_DEFINITION = re.compile(r"^\[\^(\d+)\]:[ \t]*(.*(?:\n[ ]{4}.*)*)", re.M)
_FN_REFERENCE = re.compile(r"\[\^(\d+)\]")
_FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)")
_RAW_BLOCK_OPEN = re.compile(r"<(?P<tag>pre|code|script|style)\b[^>]*>", re.I)
_INLINE_CODE = re.compile(r"(?<!`)(?P<ticks>`+)(?!`)[^\n]*?(?P=ticks)(?!`)")
_INDENTED_CODE = re.compile(
    r"(?m)^(?: {4}(?![-+*]\s|\d+[.)]\s)|\t).*?(?:\n|$)"
)
_MD_IMAGE = re.compile(r"!\[[^\]\n]*\]\([^\n)]*\)")
_MD_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\((?P<destination>[^\n)]*)\)")
_REFERENCE_LINK = re.compile(
    r"(?m)^(?!\[\^\d+\]:)\[[^\]\n]+\]:[ \t]*(?P<destination>\S.*)$"
)
_HTML_TAG = re.compile(r"<[^>\n]+>")
_ESCAPED_PUNCTUATION = re.compile(r"\\[\\`*{}\[\]()#+.!_<>-]")
_INVISIBLES = re.compile("[\u00ad\u200b\u200c\u200d\u2060\ufeff]")
_WRAP_HYPHEN = re.compile(r"(\w)-\s+(?=[a-z])")
_A1_HYPHEN = re.compile(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])")
_LIGATURES = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi",
    "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
}


@dataclass(frozen=True)
class RawSpan:
    text: str
    size: float
    flags: int
    font: str
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class RawLine:
    page: int
    spans: tuple[RawSpan, ...]
    bbox: tuple[float, float, float, float]

    @property
    def text(self) -> str:
        return _join_spans(self.spans)

    @property
    def max_size(self) -> float:
        return max((span.size for span in self.spans), default=0.0)

    @property
    def min_x(self) -> float:
        return min((span.bbox[0] for span in self.spans), default=0.0)


@dataclass(frozen=True)
class RawReference:
    number: int
    page: int
    bbox: tuple[float, float, float, float]

    @property
    def source_id(self) -> str:
        x0, y0, _x1, _y1 = self.bbox
        return f"p{self.page}:ref{self.number}@{x0:.1f},{y0:.1f}"


@dataclass(frozen=True)
class RawDefinition:
    number: int
    marker_page: int
    marker_bbox: tuple[float, float, float, float]
    end_page: int
    text: str
    line_bboxes: tuple[tuple[int, tuple[float, float, float, float]], ...]

    @property
    def source_id(self) -> str:
        x0, y0, _x1, _y1 = self.marker_bbox
        return f"p{self.marker_page}:fn{self.number}@{x0:.1f},{y0:.1f}"


@dataclass(frozen=True)
class RawObservation:
    source_pdf: str
    source_sha256: str
    definitions: tuple[RawDefinition, ...]
    references: tuple[RawReference, ...]


@dataclass(frozen=True)
class CanonicalReference:
    section: str
    number: int
    page: int
    offset: int
    page_start: int
    page_end: int


@dataclass(frozen=True)
class CanonicalDefinition:
    section: str
    number: int
    text: str
    page_start: int
    page_end: int
    offset: int


@dataclass(frozen=True)
class CanonicalObservation:
    references: tuple[CanonicalReference, ...]
    definitions: tuple[CanonicalDefinition, ...]


def _flag(page: int, kind: str, **detail: Any) -> dict:
    return {
        "invariant": "RF1",
        "page": page,
        "severity": "major",
        "detail": {"kind": kind, **detail},
    }


def _join_spans(spans: Sequence[RawSpan]) -> str:
    if not spans:
        return ""
    out = spans[0].text
    previous = spans[0]
    for span in spans[1:]:
        gap = span.bbox[0] - previous.bbox[2]
        if (gap > 0.8 and out and not out[-1].isspace()
                and span.text and not span.text[0].isspace()):
            out += " "
        out += span.text
        previous = span
    return out


def _join_lines(lines: Sequence[RawLine]) -> str:
    out = ""
    for line in lines:
        text = line.text.strip()
        if not text:
            continue
        if not out:
            out = text
            continue
        if out[-1:].isalnum() and re.match(r"^-[a-z]", text, re.I):
            out += text
        else:
            out += " " + text
    # Source line-wrap hyphenation is a typography artifact, not content.
    def remove_a1(match: re.Match) -> str:
        prefix = out[max(0, match.start() - 40):match.start()]
        if re.search(r"\w- (?:and|or|to)\b", prefix):
            return match.group(1) + "-"
        return match.group(1)
    return _A1_HYPHEN.sub(remove_a1, out)


def _comparison_key(text: str) -> str:
    """Conservative, whitespace-insensitive source/output comparison key."""
    text = unicodedata.normalize("NFC", text)
    for source, replacement in _LIGATURES.items():
        text = text.replace(source, replacement)
    text = _INVISIBLES.sub("", text)
    text = _WRAP_HYPHEN.sub(r"\1-", text)
    # mdproj preserves emphasis delimiters inside definitions; they are not
    # printed glyphs and therefore cannot appear in the PDF observation.
    text = text.replace("*", "")
    text = text.translate(str.maketrans("", "", "●•◦▪‣○"))
    return "".join(text.split())


def _text_evidence(text: str) -> dict[str, Any]:
    key = _comparison_key(text)
    return {
        "sample": text[:160],
        "normalized_length": len(key),
        "normalized_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
    }


def _canonical_plain(text: str) -> str:
    text = _mask_comments(text)
    text = re.sub(r"\[([^\]]+)\]\((?:https?://)?[^)]+\)", r"\1", text)
    text = re.sub(r"<(https?://[^>\s]+)>", r"\1", text)
    text = re.sub(r"</?(?:pre|code)\b[^>]*>", "", text, flags=re.I)
    text = re.sub(r"(?m)^(?:`{3,}|~{3,})[^\n]*$", "", text)
    text = text.replace("`", "")
    text = re.sub(r"(?m)^\s*[-*+]\s+", " ", text)
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def _mask_matches(text: str, pattern: re.Pattern) -> str:
    chars = list(text)
    for match in pattern.finditer(text):
        for index in range(match.start(), match.end()):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def _mask_group(text: str, pattern: re.Pattern, group: str) -> str:
    chars = list(text)
    for match in pattern.finditer(text):
        for index in range(match.start(group), match.end(group)):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def _mask_source_matches(target: str, source: str, pattern: re.Pattern) -> str:
    """Apply match offsets found in an unmodified syntax view to target."""
    chars = list(target)
    for match in pattern.finditer(source):
        for index in range(match.start(), match.end()):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def _mask_fenced_code(text: str) -> str:
    """Mask CommonMark fences, including long closers and missing closers."""
    chars = list(text)
    fence_character = None
    fence_length = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        mask_line = fence_character is not None
        if fence_character is None:
            match = _FENCE_OPEN.match(body)
            if match and not (
                match.group("fence").startswith("`") and "`" in match.group("info")
            ):
                fence_character = match.group("fence")[0]
                fence_length = len(match.group("fence"))
                mask_line = True
        else:
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*",
                body,
            )
            if closing:
                fence_character = None
                fence_length = 0
        if mask_line:
            for index in range(offset, offset + len(line)):
                if chars[index] not in "\r\n":
                    chars[index] = " "
        offset += len(line)
    return "".join(chars)


def _mask_raw_blocks(text: str) -> str:
    """Mask raw code/hidden HTML regions, including unclosed blocks."""
    chars = list(text)
    cursor = 0
    while match := _RAW_BLOCK_OPEN.search(text, cursor):
        closing = re.compile(
            rf"</{re.escape(match.group('tag'))}\s*>", re.I
        ).search(text, match.end())
        end = closing.end() if closing else len(text)
        for index in range(match.start(), end):
            if chars[index] not in "\r\n":
                chars[index] = " "
        cursor = end
    return "".join(chars)


def _mask_comments(text: str, *, preserve_structural: bool = False) -> str:
    """Mask HTML comments through their closer or EOF.

    When discovering page topology, preserve only comments whose complete
    contents are exactly a section header or page marker. A nested marker in a
    larger/unclosed comment therefore cannot alter reference attribution.
    """
    chars = list(text)
    cursor = 0
    while True:
        start = text.find("<!--", cursor)
        if start < 0:
            break
        close = text.find("-->", start + 4)
        end = close + 3 if close >= 0 else len(text)
        segment = text[start:end]
        keep = preserve_structural and (
            _HEADER.fullmatch(segment) is not None
            or _PAGE_MARKER.fullmatch(segment) is not None
        )
        if not keep:
            for index in range(start, end):
                if chars[index] not in "\r\n":
                    chars[index] = " "
        cursor = end
    return "".join(chars)


def observe_canonical(sections_text: Iterable[tuple[str, str]]) -> CanonicalObservation:
    """Parse every definition occurrence without dict-key collisions.

    This deliberately consumes the raw section strings rather than
    ``mdproj.Section.fn_defs``.  A dict cannot represent duplicate definitions
    and would make restarted numbering / accidental duplicates disappear.
    """
    references: list[CanonicalReference] = []
    definitions: list[CanonicalDefinition] = []
    for name, text in sections_text:
        # Remove code before recognizing structural comments, so a page marker
        # or definition-looking string inside a literal example has no power.
        structural = _mask_fenced_code(text)
        structural = _mask_raw_blocks(structural)
        structural = _mask_matches(structural, _INLINE_CODE)
        topology = _mask_comments(structural, preserve_structural=True)
        header = _HEADER.search(topology)
        page_start, page_end = (
            (int(header.group(1)), int(header.group(2))) if header else (0, 0)
        )
        markers = [
            (match.start(), int(match.group(1)))
            for match in _PAGE_MARKER.finditer(topology)
        ]

        def page_at(offset: int) -> int:
            page = page_start
            for marker_offset, marker_page in markers:
                if marker_offset > offset:
                    break
                page = marker_page
            return page

        syntax = _mask_comments(structural)
        syntax = _mask_matches(syntax, _MD_IMAGE)
        syntax = _mask_group(syntax, _MD_LINK, "destination")
        syntax = _mask_group(syntax, _REFERENCE_LINK, "destination")
        # Mask tags but preserve their displayed contents. Thus a real
        # <sup>[^1]</sup> remains observable, while [^1] in an HTML attribute
        # has no authority.
        syntax = _mask_matches(syntax, _HTML_TAG)
        syntax = _mask_matches(syntax, _ESCAPED_PUNCTUATION)
        masked = list(syntax)
        for match in _FN_DEFINITION.finditer(syntax):
            definitions.append(
                CanonicalDefinition(
                    section=name,
                    number=int(match.group(1)),
                    # Match offsets come from same-length masks. Extract the
                    # displayed body from original Markdown so legitimate code
                    # content remains part of the text comparison.
                    text=_canonical_plain(text[match.start(2):match.end(2)]),
                    page_start=page_start,
                    page_end=page_end,
                    offset=match.start(),
                )
            )
            for index in range(match.start(), match.end()):
                masked[index] = " " if masked[index] != "\n" else "\n"
        ref_text = "".join(masked)
        # Detect indentation against the pre-tag-mask source. Replacing an
        # opening <table>/<sup> tag with spaces must not turn its visible text
        # into a fabricated four-space code block.
        ref_text = _mask_source_matches(ref_text, structural, _INDENTED_CODE)
        seen_offsets: set[int] = set()
        for match in _FN_REFERENCE.finditer(ref_text):
            seen_offsets.add(match.start())
            references.append(
                CanonicalReference(
                    name, int(match.group(1)), page_at(match.start()), match.start(),
                    page_start, page_end,
                )
            )
        # Raw HTML tables sometimes use <sup>[11]</sup> rather than [^11].
        for sup in re.finditer(r"<sup>(.*?)</sup>", ref_text, re.S | re.I):
            for marker in re.finditer(r"\[\^?(\d+)\]", sup.group(1)):
                offset = sup.start(1) + marker.start()
                if offset in seen_offsets:
                    continue
                references.append(
                    CanonicalReference(
                        name, int(marker.group(1)), page_at(offset), offset,
                        page_start, page_end,
                    )
                )
    return CanonicalObservation(tuple(references), tuple(definitions))


def _page_lines(page: Any, page_number: int) -> list[RawLine]:
    lines: list[RawLine] = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for source_line in block.get("lines", []):
            spans = []
            for source_span in source_line.get("spans", []):
                if not source_span.get("text", "").strip():
                    continue
                spans.append(
                    RawSpan(
                        text=source_span["text"],
                        size=round(float(source_span["size"]), 2),
                        flags=int(source_span.get("flags", 0)),
                        font=str(source_span.get("font", "")),
                        bbox=tuple(round(float(v), 2) for v in source_span["bbox"]),
                    )
                )
            if not spans:
                continue
            spans.sort(key=lambda span: (span.bbox[0], span.bbox[1]))
            bbox = (
                min(span.bbox[0] for span in spans),
                min(span.bbox[1] for span in spans),
                max(span.bbox[2] for span in spans),
                max(span.bbox[3] for span in spans),
            )
            lines.append(RawLine(page_number, tuple(spans), bbox))
    lines.sort(key=lambda line: (line.bbox[1], line.bbox[0]))
    # Google Docs sometimes emits an inline bullet as a separate PDF "line"
    # that geometrically overlaps the prose line it introduces.  Coalesce by
    # visual baseline before establishing reading order; otherwise p.16's
    # footnote list reads prose-then-bullet even though the bullet is leftmost.
    coalesced: list[RawLine] = []
    for line in lines:
        match = next(
            (
                index for index in range(len(coalesced) - 1, -1, -1)
                if abs(coalesced[index].bbox[1] - line.bbox[1]) <= 2.0
                and min(coalesced[index].bbox[3], line.bbox[3])
                    - max(coalesced[index].bbox[1], line.bbox[1]) > 4.0
            ),
            None,
        )
        if match is None:
            coalesced.append(line)
            continue
        prior = coalesced[match]
        spans = tuple(sorted(prior.spans + line.spans, key=lambda span: span.bbox[0]))
        coalesced[match] = RawLine(
            page_number,
            spans,
            (
                min(prior.bbox[0], line.bbox[0]),
                min(prior.bbox[1], line.bbox[1]),
                max(prior.bbox[2], line.bbox[2]),
                max(prior.bbox[3], line.bbox[3]),
            ),
        )
    return sorted(coalesced, key=lambda line: (line.bbox[1], line.bbox[0]))


def _body_size(lines: Sequence[RawLine]) -> float:
    weighted: Counter[float] = Counter()
    for line in lines:
        for span in line.spans:
            if 9.5 <= span.size <= 13.5:
                weighted[round(span.size, 1)] += max(1, len(span.text.strip()))
    return weighted.most_common(1)[0][0] if weighted else 11.0


def _left_margin(lines: Sequence[RawLine], body_size: float) -> float:
    xs = sorted(
        line.min_x for line in lines
        if any(span.size >= body_size - 0.2 for span in line.spans)
    )
    if not xs:
        xs = sorted(line.min_x for line in lines)
    return xs[max(0, int(len(xs) * 0.05) - 1)] if xs else 0.0


def _footer_number(line: RawLine, page_height: float) -> bool:
    return (
        line.bbox[3] >= page_height - FOOTER_BAND
        and bool(_NUMERIC.fullmatch(line.text.strip()))
        and len(line.spans) == 1
        and line.spans[0].size >= 8.0
    )


def _marker_number(line: RawLine, body_size: float, left_margin: float) -> int | None:
    first = line.spans[0]
    text = first.text.strip()
    if not _NUMERIC.fullmatch(text):
        return None
    if first.flags & SUPER:
        return None
    # Relative typography is the authority. An 8pt marker in an 11pt-body PDF
    # is as real as this corpus's 6pt marker; an absolute cap silently loses
    # new document families.
    if first.size > body_size - 0.5:
        return None
    if first.bbox[0] > left_margin + LEFT_MARGIN_SLOP:
        return None
    # A definition marker must introduce actual small-type prose on its line;
    # this rejects leftmost chart/table digits that happen to use a small font.
    if len(line.spans) < 2:
        return None
    trailing = [span for span in line.spans[1:] if span.text.strip()]
    if not trailing or max(span.size for span in trailing) > body_size + 0.1:
        return None
    return int(text)


def _bottom_small_region(
    lines: Sequence[RawLine], body_size: float, page_height: float,
) -> tuple[int, int] | None:
    """Return [start, end) for the contiguous small-type region at page bottom."""
    eligible = [i for i, line in enumerate(lines) if not _footer_number(line, page_height)]
    if not eligible:
        return None
    end = eligible[-1] + 1
    index = eligible[-1]
    while index >= 0:
        line = lines[index]
        if _footer_number(line, page_height):
            index -= 1
            continue
        if line.max_size > body_size - SMALL_TYPE_GAP:
            break
        if index + 1 < end:
            following = lines[index + 1]
            if (not _footer_number(following, page_height)
                    and following.bbox[1] - line.bbox[3] > VERTICAL_GAP):
                break
        index -= 1
    start = index + 1
    return (start, end) if start < end else None


@lru_cache(maxsize=8)
def _observe_cached(source_path: str, expected_sha256: str) -> RawObservation:
    source_pdf = Path(source_path)
    source_bytes = source_pdf.read_bytes()
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(f"source PDF changed while observing footnotes: {source_pdf}")

    page_data: list[tuple[list[RawLine], float]] = []
    references: list[RawReference] = []
    with fitz.open(stream=source_bytes, filetype="pdf") as document:
        for page_index, page in enumerate(document):
            page_number = page_index + 1
            lines = _page_lines(page, page_number)
            page_data.append((lines, float(page.rect.height)))

            for line in lines:
                for span in line.spans:
                    text = span.text.strip()
                    # Superscript references are authoritative by shape, not
                    # by an absolute font-size cap.  A 9.13pt ``<sup>`` in an
                    # 11pt document is the same semantic observation as this
                    # corpus's smaller glyphs.  Retaining every numeric SUPER
                    # span also makes unfamiliar typography fail closed: the
                    # canonical output must preserve or exactly disposition
                    # the occurrence instead of losing it during observation.
                    if span.flags & SUPER and _NUMERIC.fullmatch(text):
                        references.append(
                            RawReference(int(text), page_number, span.bbox)
                        )

    # Infer the document's body size once. A long footnote can dominate a
    # single page (risk report pp.50/117), so per-page modal size mistakes the
    # 10pt note for body and makes its markers disappear.
    document_lines = [line for lines, _height in page_data for line in lines]
    body_size = _body_size(document_lines)
    left_margin = _left_margin(document_lines, body_size)
    page_regions: list[tuple[list[RawLine], int, int, float, float]] = []
    for lines, page_height in page_data:
        region = _bottom_small_region(lines, body_size, page_height)
        if region:
            page_regions.append((lines, region[0], region[1], body_size, left_margin))
        else:
            page_regions.append((lines, 0, 0, body_size, left_margin))

    definitions: list[RawDefinition] = []
    open_definition: tuple[int, int] | None = None  # (definition index, source page)
    for page_index, (lines, start, end, body_size, left_margin) in enumerate(page_regions):
        page_number = page_index + 1
        if start == end:
            open_definition = None
            continue
        region_lines = lines[start:end]
        marker_offsets = [
            offset for offset, line in enumerate(region_lines)
            if _marker_number(line, body_size, left_margin) is not None
        ]
        if not marker_offsets:
            # There is no source marker to distinguish a true continuation
            # from a small caption/table at page bottom.  Do not guess.  The
            # document family represents observed cross-page tails as the
            # unmarked prefix immediately above the next numbered definition.
            open_definition = None
            continue

        # Lines before the first marker are the previous page's continued tail.
        first_marker = marker_offsets[0]
        if first_marker and open_definition and open_definition[1] == page_number - 1:
            definition_index, _ = open_definition
            previous = definitions[definition_index]
            continuation_lines = region_lines[:first_marker]
            definitions[definition_index] = RawDefinition(
                previous.number,
                previous.marker_page,
                previous.marker_bbox,
                page_number,
                (previous.text + " " + _join_lines(continuation_lines)).strip(),
                previous.line_bboxes
                + tuple((page_number, line.bbox) for line in continuation_lines),
            )

        for marker_position, offset in enumerate(marker_offsets):
            stop = marker_offsets[marker_position + 1] if marker_position + 1 < len(marker_offsets) else len(region_lines)
            definition_lines = list(region_lines[offset:stop])
            marker_line = definition_lines[0]
            number = _marker_number(marker_line, body_size, left_margin)
            assert number is not None
            marker = marker_line.spans[0]
            definition_lines[0] = RawLine(
                marker_line.page,
                tuple(marker_line.spans[1:]),
                marker_line.bbox,
            )
            definitions.append(
                RawDefinition(
                    number=number,
                    marker_page=page_number,
                    marker_bbox=marker.bbox,
                    end_page=page_number,
                    text=_join_lines(definition_lines),
                    line_bboxes=tuple((page_number, line.bbox) for line in definition_lines),
                )
            )
        open_definition = (len(definitions) - 1, page_number)

    return RawObservation(
        source_pdf=str(source_pdf),
        source_sha256=actual_sha256,
        definitions=tuple(definitions),
        references=tuple(references),
    )


def observe(source_pdf: str | Path) -> RawObservation:
    """Hash on every call; cache expensive parsing only by content digest."""
    source_pdf = Path(source_pdf).resolve()
    digest = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
    return _observe_cached(str(source_pdf), digest)


def _disposition_sets(
    observation: RawObservation,
    dispositions: Mapping[str, Any] | Any | None,
) -> tuple[set[str], set[str], list[dict]]:
    if dispositions is None:
        return set(), set(), []
    if not isinstance(dispositions, Mapping):
        return set(), set(), [_flag(0, "invalid-disposition-document")]
    flags: list[dict] = []
    if dispositions.get("schema_version") != 1:
        flags.append(_flag(0, "invalid-disposition-schema",
                           schema_version=dispositions.get("schema_version")))
        return set(), set(), flags
    if dispositions.get("observer_schema_version") != OBSERVER_SCHEMA_VERSION:
        flags.append(_flag(
            0, "stale-disposition-observer-schema",
            expected=OBSERVER_SCHEMA_VERSION,
            configured=dispositions.get("observer_schema_version"),
        ))
        return set(), set(), flags
    if dispositions.get("pymupdf_version") != PYMUPDF_VERSION:
        flags.append(_flag(
            0, "stale-disposition-pymupdf-version",
            expected=PYMUPDF_VERSION,
            configured=dispositions.get("pymupdf_version"),
        ))
        return set(), set(), flags
    if dispositions.get("source_sha256") != observation.source_sha256:
        flags.append(_flag(0, "stale-disposition-source",
                           expected=observation.source_sha256,
                           configured=dispositions.get("source_sha256")))
        return set(), set(), flags

    known_references = {reference.source_id for reference in observation.references}
    known_definitions = {definition.source_id for definition in observation.definitions}
    excluded_references: set[str] = set()
    excluded_definitions: set[str] = set()
    for key, known, destination in (
        ("excluded_references", known_references, excluded_references),
        ("excluded_definitions", known_definitions, excluded_definitions),
    ):
        entries = dispositions.get(key, [])
        if not isinstance(entries, list):
            flags.append(_flag(0, "invalid-disposition-list", field=key))
            continue
        for entry in entries:
            source_id = entry.get("source_id") if isinstance(entry, dict) else None
            reason = entry.get("reason") if isinstance(entry, dict) else None
            if (
                not isinstance(entry, dict)
                or set(entry) != {"source_id", "reason"}
                or not isinstance(source_id, str)
                or not source_id.strip()
                or not isinstance(reason, str)
                or not reason.strip()
            ):
                flags.append(_flag(0, "invalid-disposition-entry", field=key, entry=entry))
                continue
            if source_id not in known:
                flags.append(_flag(0, "stale-disposition-observation",
                                   field=key, source_id=source_id))
                continue
            if source_id in destination:
                flags.append(_flag(0, "duplicate-disposition-observation",
                                   field=key, source_id=source_id))
                continue
            destination.add(source_id)
    return excluded_references, excluded_definitions, flags


def _source_id_collision_flags(observation: RawObservation) -> list[dict]:
    """Reject raw occurrences whose public disposition identity is ambiguous.

    ``source_id`` is intentionally stable across observer runs so that a
    reviewed disposition can bind to one concrete PDF occurrence.  Stability
    is only useful when the identifier is injective, though: a dict or set
    keyed by a colliding identifier would silently coalesce distinct source
    glyphs.  Detect that condition before disposition or matching logic gets
    any opportunity to collapse it.
    """
    flags: list[dict] = []
    for source_kind, occurrences, page_attribute in (
        ("reference", observation.references, "page"),
        ("definition", observation.definitions, "marker_page"),
    ):
        counts = Counter(occurrence.source_id for occurrence in occurrences)
        first_by_id = {
            occurrence.source_id: occurrence for occurrence in occurrences
        }
        for source_id, count in sorted(counts.items()):
            if count <= 1:
                continue
            occurrence = first_by_id[source_id]
            flags.append(_flag(
                int(getattr(occurrence, page_attribute)),
                "duplicate-raw-source-id",
                source_kind=source_kind,
                source_id=source_id,
                count=count,
            ))
    return flags


def _unique_nearest(items: Sequence[Any], page: int, page_attr: str) -> list[Any]:
    if not items:
        return []
    distances = [abs(int(getattr(item, page_attr)) - page) for item in items]
    minimum = min(distances)
    return [item for item, distance in zip(items, distances) if distance == minimum]


def verify(
    source_pdf: str | Path,
    sections_text: Iterable[tuple[str, str]],
    *,
    dispositions: Mapping[str, Any] | None = None,
    observation: RawObservation | None = None,
) -> list[dict]:
    """Verify canonical refs/defs against occurrence-bound raw PDF evidence.

    ``sections_text`` is the raw ``(filename, Markdown)`` sequence.  Parsing it
    here is intentional: ``mdproj.fn_defs`` is a dict and therefore cannot
    preserve duplicate same-number definitions.  No source-zone facts or
    generator metadata enter this lane.

    ``dispositions`` may exclude exact raw occurrences only when bound to this
    PDF's SHA-256.  Ambiguous observations otherwise remain release-blocking.
    """
    observation = observation or observe(source_pdf)
    identity_flags = _source_id_collision_flags(observation)
    if identity_flags:
        # A disposition naming this ID would necessarily apply to more than
        # one occurrence.  Stop before any set/dict/disposition matching can
        # turn the collision into a false green.
        return sorted(
            identity_flags,
            key=lambda flag: (
                flag["page"], flag["detail"]["kind"],
                flag["detail"].get("source_kind", ""),
                flag["detail"].get("source_id", ""),
            ),
        )
    canonical = observe_canonical(sections_text)
    excluded_refs, excluded_defs, flags = _disposition_sets(observation, dispositions)

    raw_definitions_by_number: dict[int, list[RawDefinition]] = defaultdict(list)
    for definition in observation.definitions:
        raw_definitions_by_number[definition.number].append(definition)

    # First bind every raw superscript occurrence to a concrete nearby source
    # definition occurrence. Nothing disappears merely because that binding is
    # absent or ambiguous.
    for reference in observation.references:
        if reference.source_id in excluded_refs:
            continue
        candidates = [
            definition for definition in raw_definitions_by_number[reference.number]
            if definition.source_id not in excluded_defs
            and abs(definition.marker_page - reference.page) <= 1
        ]
        nearest = _unique_nearest(candidates, reference.page, "marker_page")
        if len(nearest) != 1:
            flags.append(_flag(
                reference.page,
                "raw-reference-definition-ambiguous",
                number=reference.number,
                source_id=reference.source_id,
                candidates=[definition.source_id for definition in nearest],
            ))

    # Match canonical reference occurrences one-to-one to raw glyphs. Page
    # attribution allows one-page slop for inline page sentinels at a wrap;
    # section range + raw bbox preserve occurrence identity.
    unused_raw_refs = {
        reference.source_id: reference for reference in observation.references
        if reference.source_id not in excluded_refs
    }
    matched_ref_pages: dict[tuple[str, int], list[int]] = defaultdict(list)
    for reference in sorted(canonical.references, key=lambda item: (item.section, item.offset)):
        candidates = [
            raw_reference for raw_reference in unused_raw_refs.values()
            if raw_reference.number == reference.number
            and reference.page_start - 1 <= raw_reference.page <= reference.page_end + 1
            and abs(raw_reference.page - reference.page) <= 1
        ]
        nearest = _unique_nearest(candidates, reference.page, "page")
        same_page_tie = bool(nearest) and len({candidate.page for candidate in nearest}) == 1
        if len(nearest) != 1 and not same_page_tie:
            flags.append(_flag(
                reference.page,
                "canonical-reference-occurrence-ambiguous",
                number=reference.number,
                section=reference.section,
                candidates=[candidate.source_id for candidate in nearest],
            ))
            continue
        # Repeated references to the same definition on one page have no
        # output bbox. Their order is still observable on both sides, so bind
        # canonical offset order to source (y, x) order deterministically.
        source_reference = sorted(
            nearest, key=lambda item: (item.page, item.bbox[1], item.bbox[0])
        )[0]
        unused_raw_refs.pop(source_reference.source_id)
        matched_ref_pages[(reference.section, reference.number)].append(source_reference.page)

    for reference in unused_raw_refs.values():
        flags.append(_flag(
            reference.page,
            "source-reference-without-canonical-occurrence",
            number=reference.number,
            source_id=reference.source_id,
        ))

    duplicate_counts = Counter((definition.section, definition.number)
                               for definition in canonical.definitions)
    for (section, number), count in sorted(duplicate_counts.items()):
        if count > 1:
            flags.append(_flag(
                next(definition.page_start for definition in canonical.definitions
                     if definition.section == section and definition.number == number),
                "duplicate-canonical-definition",
                number=number, section=section, count=count,
            ))

    unused_raw_defs = {
        definition.source_id: definition for definition in observation.definitions
        if definition.source_id not in excluded_defs
    }
    for definition in sorted(canonical.definitions, key=lambda item: (item.section, item.offset)):
        reference_pages = matched_ref_pages.get((definition.section, definition.number), [])
        candidates = [
            source_definition for source_definition in unused_raw_defs.values()
            if source_definition.number == definition.number
            and definition.page_start - 1 <= source_definition.marker_page <= definition.page_end + 1
        ]
        target_page = reference_pages[0] if reference_pages else definition.page_start
        nearest = _unique_nearest(candidates, target_page, "marker_page")
        if len(nearest) != 1:
            flags.append(_flag(
                target_page,
                "canonical-definition-occurrence-ambiguous",
                number=definition.number,
                section=definition.section,
                reference_pages=sorted(reference_pages),
                candidates=[candidate.source_id for candidate in nearest],
            ))
            continue
        source_definition = nearest[0]
        unused_raw_defs.pop(source_definition.source_id)
        if _comparison_key(definition.text) != _comparison_key(source_definition.text):
            flags.append(_flag(
                source_definition.marker_page,
                "definition-text-mismatch",
                number=definition.number,
                section=definition.section,
                source_id=source_definition.source_id,
                source=_text_evidence(source_definition.text),
                canonical=_text_evidence(definition.text),
            ))

    # Bidirectional by default: every raw definition is required even if its
    # source reference is absent or ambiguous. Only exact, hash-bound
    # dispositions may remove it from authority.
    for definition in unused_raw_defs.values():
        flags.append(_flag(
            definition.marker_page,
            "source-definition-without-canonical-occurrence",
            number=definition.number,
            source_id=definition.source_id,
            source=_text_evidence(definition.text),
        ))

    return sorted(
        flags,
        key=lambda flag: (
            flag["page"], flag["detail"]["kind"],
            flag["detail"].get("section", ""), flag["detail"].get("number", -1),
        ),
    )
