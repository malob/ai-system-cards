"""Build source-only ruled-region discovery evidence.

The executable observer boundary is deliberately narrow: pinned PyMuPDF reopens
each archived PDF, records every stroked axis-aligned ``l`` item and every word,
and calls ``Page.find_tables(strategy="lines_strict", use_layout=False)``.  The
result is a proposal plane of *ruled-grid regions*, not semantic table authority.

Human visual labels, PDF structure-tag challenges, and caption interpretations are
written to a separate review manifest.  They are never inputs to observation.
Accepted Markdown, legacy HTML, Docling candidates, and reviewed cell labels are
not read anywhere in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

PINNED_PYMUPDF_VERSION = "1.28.2"
COORDINATE_SPACE = "pdf-top-left-points"
AXIS_TOLERANCE = 0.02
INTERSECTION_TOLERANCE = 0.75
WORD_CONTAINMENT_TOLERANCE = 0.75
RAW_MATCH_MIN_IOU = 0.80

SOURCE_ARTIFACT = HERE / "source-pages.json"
REVIEW_ARTIFACT = HERE / "review-manifest.json"


@dataclass(frozen=True)
class DocumentSpec:
    key: str
    path: str


DOCUMENTS = (
    DocumentSpec("opus", "cards/anthropic/claude-opus-5/source.pdf"),
    DocumentSpec("fable", "cards/anthropic/claude-fable-5/source.pdf"),
    DocumentSpec("risk", "cards/anthropic/risk-report-2026-08/source.pdf"),
)

# These whole-page payloads exercise a regular grid, a complex span grid, a
# publisher-captioned figure grid, dense box/callout negatives, a false PDF-tag
# challenge, and the true-blank control. Selection is review metadata; observe_page
# itself knows nothing about these labels.
FULL_PAGE_FIXTURES = {
    "opus": (16, 37, 43, 56, 85, 104),
    "fable": (39, 60, 94),
    "risk": (72, 115, 172),
}


@dataclass(frozen=True)
class CaptionLocator:
    document: str
    page: int
    prefix: str
    claim: str


CAPTION_LOCATORS = (
    CaptionLocator("opus", 16, "[Table 2.2.3.A]", "table"),
    CaptionLocator("opus", 37, "[Figure 3.3.1.A]", "figure"),
    CaptionLocator("fable", 60, "[Figure 3.2.1.A]", "figure"),
)


@dataclass(frozen=True)
class TagChallenge:
    document: str
    page: int
    table_ordinal: int
    rows: int
    cells: int
    visual_class: str


# Each source tag claims a multi-cell Table, but complete-page visual inspection
# found a chart legend, list, or quote rather than a semantic table. These are
# advisory challenges to source tags, never detector inputs.
TAG_CHALLENGES = (
    TagChallenge("opus", 43, 0, 1, 2, "chart-legend-and-quote"),
    TagChallenge("opus", 104, 0, 1, 2, "quoted-numbered-list"),
    TagChallenge("fable", 50, 1, 1, 2, "quoted-bulleted-list"),
    TagChallenge("fable", 64, 0, 1, 2, "quoted-numbered-list"),
    TagChallenge("fable", 66, 0, 1, 3, "quoted-paragraphs"),
    TagChallenge("fable", 129, 0, 1, 2, "quoted-bulleted-list"),
    TagChallenge("fable", 214, 0, 1, 2, "quoted-bulleted-list"),
    TagChallenge("risk", 32, 0, 1, 3, "quoted-paragraph"),
    TagChallenge("risk", 35, 0, 1, 3, "quoted-paragraph"),
    TagChallenge("risk", 37, 0, 1, 3, "quoted-paragraph"),
)


# Complete pages rendered from the archived PDFs and inspected visually. This list
# is deliberately separate from FULL_PAGE_FIXTURES and from observe_page().
VISUAL_REVIEW = {
    "opus": {
        16: "regular-ruled-grid-table-caption",
        37: "ruled-grid-figure-caption",
        43: "chart-and-quote-no-grid",
        56: "two-complex-ruled-grids",
        85: "nested-transcript-boxes-no-grid",
        86: "nested-transcript-boxes-no-grid",
        93: "nested-transcript-boxes-no-grid",
        104: "quoted-list-no-grid",
    },
    "fable": {
        39: "nested-callout-boxes-no-grid",
        40: "nested-callout-boxes-no-grid",
        41: "nested-callout-boxes-no-grid",
        42: "nested-callout-boxes-no-grid",
        43: "nested-callout-boxes-no-grid",
        50: "ruled-grid-plus-quoted-list",
        60: "ruled-grid-figure-caption",
        64: "quoted-list-no-grid",
        66: "quoted-paragraphs-no-grid",
        94: "complex-span-ruled-grid",
        129: "quoted-list-no-grid",
        214: "quoted-list-no-grid",
    },
    "risk": {
        32: "quoted-paragraph-no-grid",
        35: "quoted-paragraph-no-grid",
        37: "quoted-paragraph-no-grid",
        72: "single-transcript-box-no-grid",
        84: "single-transcript-box-no-grid",
        85: "single-transcript-box-no-grid",
        86: "single-transcript-box-no-grid",
        115: "complex-span-ruled-grid-with-bounded-blank",
        130: "ruled-grid-continuation-fragment",
        155: "ruled-grid-fragment",
        172: "high-vector-text-page-no-grid",
    },
}


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round(value: float) -> float:
    return round(float(value), 6)


def _bbox(value: Iterable[float]) -> list[float]:
    return [_round(item) for item in value]


def _overlaps(first: Iterable[float], second: Iterable[float]) -> bool:
    a = tuple(first)
    b = tuple(second)
    return a[2] > b[0] and a[0] < b[2] and a[3] > b[1] and a[1] < b[3]


def _source_id(source_sha256: str) -> str:
    return f"pdf-{source_sha256[:16]}"


def _point(value: Any) -> list[float] | None:
    if value is None or not hasattr(value, "x") or not hasattr(value, "y"):
        return None
    return [_round(value.x), _round(value.y)]


def _word_features(
    word_bbox: list[float],
    text: str,
    spans: list[dict[str, Any]],
    links: list[dict[str, Any]],
) -> dict[str, Any]:
    center_y = (word_bbox[1] + word_bbox[3]) / 2
    styles = []
    for span in spans:
        box = span["bbox"]
        if box[2] <= word_bbox[0] or box[0] >= word_bbox[2]:
            continue
        if not box[1] < center_y < box[3]:
            continue
        styles.append(
            {
                "bbox": box,
                "font": span["font"],
                "size": span["size"],
                "flags": span["flags"],
                "color": span["color"],
                "superscript": bool(span["flags"] & 1),
                "text_sha256": hashlib.sha256(span["text"].encode()).hexdigest(),
            }
        )
    word_links = []
    for link in links:
        if not _overlaps(word_bbox, link["from"]):
            continue
        word_links.append(
            {
                "kind": link["kind"],
                "uri": link.get("uri"),
                "page": link.get("page"),
                "to": _point(link.get("to")),
                "xref": link.get("xref"),
            }
        )
    return {
        "punctuation": [
            char for char in text if unicodedata.category(char).startswith("P")
        ],
        "styles": styles,
        "links": word_links,
        "superscript": any(item["superscript"] for item in styles),
    }


def _page_words(page: Any, *, rich_features: bool) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    if rich_features:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    spans.append(
                        {
                            "text": span["text"],
                            "bbox": _bbox(span["bbox"]),
                            "font": span["font"],
                            "size": _round(span["size"]),
                            "flags": int(span["flags"]),
                            "color": int(span["color"]),
                        }
                    )
        for link in page.get_links():
            links.append({**link, "from": _bbox(link["from"])})

    result = []
    for ordinal, raw in enumerate(page.get_text("words", sort=True)):
        x0, y0, x1, y1, text, block, line, word = raw
        box = _bbox((x0, y0, x1, y1))
        record = {
            "word_id": f"p{page.number + 1}:b{block}:l{line}:w{word}",
            "ordinal": ordinal,
            "text": text,
            "bbox": box,
            "features": {},
        }
        if rich_features:
            record["features"] = _word_features(box, text, spans, links)
        result.append(record)
    return result


def _axis_segments(page: Any) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Return every visible stroked axis-aligned ``l`` item.

    Rectangle items are never decomposed. Fill-only rectangles remain visible in
    the companion counts but cannot become rule input.
    """

    segments: list[dict[str, Any]] = []
    counts: defaultdict[str, int] = defaultdict(int)
    for drawing_index, drawing in enumerate(page.get_drawings()):
        counts["drawing_paths"] += 1
        path_type = str(drawing.get("type") or "")
        stroke_visible = (
            "s" in path_type
            and drawing.get("color") is not None
            and float(drawing.get("stroke_opacity", 1.0)) > 0
        )
        if stroke_visible:
            counts["stroked_paths"] += 1
        if "f" in path_type:
            counts["filled_paths"] += 1
        for item_index, item in enumerate(drawing["items"]):
            kind = item[0]
            counts[f"item_{kind}"] += 1
            if kind == "re":
                if not stroke_visible:
                    counts["fill_only_rect_items"] += 1
                else:
                    counts["stroked_rect_items_not_decomposed"] += 1
                continue
            if kind != "l" or not stroke_visible:
                continue
            start, end = item[1], item[2]
            if abs(start.y - end.y) <= AXIS_TOLERANCE:
                orientation = "horizontal"
                fixed = (start.y + end.y) / 2
                axis_start, axis_end = sorted((float(start.x), float(end.x)))
            elif abs(start.x - end.x) <= AXIS_TOLERANCE:
                orientation = "vertical"
                fixed = (start.x + end.x) / 2
                axis_start, axis_end = sorted((float(start.y), float(end.y)))
            else:
                counts["non_axis_stroked_line_items"] += 1
                continue
            if axis_end - axis_start <= AXIS_TOLERANCE:
                counts["degenerate_axis_line_items"] += 1
                continue
            segments.append(
                {
                    "segment_id": (
                        f"p{page.number + 1}:d{drawing_index}:i{item_index}:l"
                    ),
                    "item_kind": "l",
                    "drawing_id": f"p{page.number + 1}:d{drawing_index}",
                    "item_index": item_index,
                    "orientation": orientation,
                    "fixed": _round(fixed),
                    "start": _round(axis_start),
                    "end": _round(axis_end),
                    "stroke_width": _round(drawing.get("width") or 0.0),
                }
            )
    segments.sort(
        key=lambda item: (
            item["orientation"],
            item["fixed"],
            item["start"],
            item["end"],
            item["segment_id"],
        )
    )
    counts["axis_stroked_line_segments"] = len(segments)
    return segments, dict(sorted(counts.items()))


def _interval_covered(
    intervals: list[tuple[float, float]], start: float, end: float
) -> bool:
    cursor = start
    clipped = sorted(
        (max(start, left), min(end, right))
        for left, right in intervals
        if right >= start - INTERSECTION_TOLERANCE
        and left <= end + INTERSECTION_TOLERANCE
    )
    for left, right in clipped:
        if left > cursor + INTERSECTION_TOLERANCE:
            return False
        cursor = max(cursor, right)
    return cursor >= end - INTERSECTION_TOLERANCE


def _interval_coverage(
    intervals: list[tuple[float, float]], start: float, end: float
) -> tuple[float, float]:
    """Return exact union coverage ratio and missing length without tolerance fill."""

    clipped = sorted(
        (max(start, left), min(end, right))
        for left, right in intervals
        if right > start and left < end
    )
    covered = 0.0
    cursor: float | None = None
    extent_end = 0.0
    for left, right in clipped:
        if cursor is None or left > extent_end:
            covered += right - left
            cursor = left
            extent_end = right
        elif right > extent_end:
            covered += right - extent_end
            extent_end = right
    length = end - start
    missing = max(0.0, length - covered)
    return covered / length, missing


def _raw_enveloped_components(
    source_id: str, page_1based: int, segments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Independent raw-stroke graph used only to challenge the built-in observer."""

    parent = list(range(len(segments)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        left, right = find(first), find(second)
        if left != right:
            parent[right] = left

    horizontal = [
        (index, item)
        for index, item in enumerate(segments)
        if item["orientation"] == "horizontal"
    ]
    vertical = [
        (index, item)
        for index, item in enumerate(segments)
        if item["orientation"] == "vertical"
    ]
    for h_index, h in horizontal:
        for v_index, v in vertical:
            if (
                h["start"] - INTERSECTION_TOLERANCE
                <= v["fixed"]
                <= h["end"] + INTERSECTION_TOLERANCE
                and v["start"] - INTERSECTION_TOLERANCE
                <= h["fixed"]
                <= v["end"] + INTERSECTION_TOLERANCE
            ):
                union(h_index, v_index)

    groups: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, item in enumerate(segments):
        groups[find(index)].append(item)

    pending = []
    for group in groups.values():
        hs = [item for item in group if item["orientation"] == "horizontal"]
        vs = [item for item in group if item["orientation"] == "vertical"]
        if len(hs) < 2 or len(vs) < 2:
            continue
        x_edges = sorted({item["fixed"] for item in vs})
        y_edges = sorted({item["fixed"] for item in hs})
        left, right = x_edges[0], x_edges[-1]
        top, bottom = y_edges[0], y_edges[-1]
        outer = (
            _interval_covered(
                [
                    (item["start"], item["end"])
                    for item in hs
                    if abs(item["fixed"] - top) <= INTERSECTION_TOLERANCE
                ],
                left,
                right,
            )
            and _interval_covered(
                [
                    (item["start"], item["end"])
                    for item in hs
                    if abs(item["fixed"] - bottom) <= INTERSECTION_TOLERANCE
                ],
                left,
                right,
            )
            and _interval_covered(
                [
                    (item["start"], item["end"])
                    for item in vs
                    if abs(item["fixed"] - left) <= INTERSECTION_TOLERANCE
                ],
                top,
                bottom,
            )
            and _interval_covered(
                [
                    (item["start"], item["end"])
                    for item in vs
                    if abs(item["fixed"] - right) <= INTERSECTION_TOLERANCE
                ],
                top,
                bottom,
            )
        )
        if not outer:
            continue

        outer_side_measurements = []
        for side, y in (("top", top), ("bottom", bottom)):
            coverage, missing = _interval_coverage(
                [
                    (item["start"], item["end"])
                    for item in hs
                    if abs(item["fixed"] - y) <= INTERSECTION_TOLERANCE
                ],
                left,
                right,
            )
            outer_side_measurements.append(
                {
                    "boundary_id": side,
                    "orientation": "horizontal",
                    "fixed": _round(y),
                    "start": _round(left),
                    "end": _round(right),
                    "coverage_ratio": round(coverage, 12),
                    "missing_points": _round(missing),
                }
            )
        for side, x in (("left", left), ("right", right)):
            coverage, missing = _interval_coverage(
                [
                    (item["start"], item["end"])
                    for item in vs
                    if abs(item["fixed"] - x) <= INTERSECTION_TOLERANCE
                ],
                top,
                bottom,
            )
            outer_side_measurements.append(
                {
                    "boundary_id": side,
                    "orientation": "vertical",
                    "fixed": _round(x),
                    "start": _round(top),
                    "end": _round(bottom),
                    "coverage_ratio": round(coverage, 12),
                    "missing_points": _round(missing),
                }
            )

        rows = len(y_edges) - 1
        columns = len(x_edges) - 1
        outer_slot_measurements = []
        for side, y in (("top", top), ("bottom", bottom)):
            intervals = [
                (item["start"], item["end"])
                for item in hs
                if abs(item["fixed"] - y) <= INTERSECTION_TOLERANCE
            ]
            for column in range(columns):
                coverage, missing = _interval_coverage(
                    intervals, x_edges[column], x_edges[column + 1]
                )
                outer_slot_measurements.append(
                    {
                        "boundary_id": f"{side}:c{column}",
                        "orientation": "horizontal",
                        "slot_index": column,
                        "fixed": _round(y),
                        "start": _round(x_edges[column]),
                        "end": _round(x_edges[column + 1]),
                        "coverage_ratio": round(coverage, 12),
                        "missing_points": _round(missing),
                    }
                )
        for side, x in (("left", left), ("right", right)):
            intervals = [
                (item["start"], item["end"])
                for item in vs
                if abs(item["fixed"] - x) <= INTERSECTION_TOLERANCE
            ]
            for row in range(rows):
                coverage, missing = _interval_coverage(
                    intervals, y_edges[row], y_edges[row + 1]
                )
                outer_slot_measurements.append(
                    {
                        "boundary_id": f"{side}:r{row}",
                        "orientation": "vertical",
                        "slot_index": row,
                        "fixed": _round(x),
                        "start": _round(y_edges[row]),
                        "end": _round(y_edges[row + 1]),
                        "coverage_ratio": round(coverage, 12),
                        "missing_points": _round(missing),
                    }
                )
        slot_parent = list(range(rows * columns))

        def slot_find(index: int, parents: list[int] = slot_parent) -> int:
            while parents[index] != index:
                parents[index] = parents[parents[index]]
                index = parents[index]
            return index

        def slot_union(
            first: int, second: int, parents: list[int] = slot_parent
        ) -> None:
            left_root = slot_find(first, parents)
            right_root = slot_find(second, parents)
            if left_root != right_root:
                parents[right_root] = left_root

        present_separations = 0
        absent_merges = 0
        present_internal_measurements = []
        horizontal_support = []
        for boundary, y in enumerate(y_edges[1:-1], 1):
            present = []
            for column in range(columns):
                x = (x_edges[column] + x_edges[column + 1]) / 2
                observed = any(
                    abs(item["fixed"] - y) <= INTERSECTION_TOLERANCE
                    and item["start"] - INTERSECTION_TOLERANCE
                    <= x
                    <= item["end"] + INTERSECTION_TOLERANCE
                    for item in hs
                )
                present.append(observed)
                index = (boundary - 1) * columns + column
                if observed:
                    present_separations += 1
                    coverage, missing = _interval_coverage(
                        [
                            (item["start"], item["end"])
                            for item in hs
                            if abs(item["fixed"] - y) <= INTERSECTION_TOLERANCE
                        ],
                        x_edges[column],
                        x_edges[column + 1],
                    )
                    present_internal_measurements.append(
                        {
                            "boundary_id": f"h{boundary}:c{column}",
                            "orientation": "horizontal",
                            "axis_index": boundary,
                            "slot_index": column,
                            "fixed": _round(y),
                            "start": _round(x_edges[column]),
                            "end": _round(x_edges[column + 1]),
                            "coverage_ratio": round(coverage, 12),
                            "missing_points": _round(missing),
                        }
                    )
                else:
                    absent_merges += 1
                    slot_union(index, boundary * columns + column)
            horizontal_support.append(sum(present) / len(present))

        vertical_support = []
        for boundary, x in enumerate(x_edges[1:-1], 1):
            present = []
            for row in range(rows):
                y = (y_edges[row] + y_edges[row + 1]) / 2
                observed = any(
                    abs(item["fixed"] - x) <= INTERSECTION_TOLERANCE
                    and item["start"] - INTERSECTION_TOLERANCE
                    <= y
                    <= item["end"] + INTERSECTION_TOLERANCE
                    for item in vs
                )
                present.append(observed)
                index = row * columns + boundary - 1
                if observed:
                    present_separations += 1
                    coverage, missing = _interval_coverage(
                        [
                            (item["start"], item["end"])
                            for item in vs
                            if abs(item["fixed"] - x) <= INTERSECTION_TOLERANCE
                        ],
                        y_edges[row],
                        y_edges[row + 1],
                    )
                    present_internal_measurements.append(
                        {
                            "boundary_id": f"v{boundary}:r{row}",
                            "orientation": "vertical",
                            "axis_index": boundary,
                            "slot_index": row,
                            "fixed": _round(x),
                            "start": _round(y_edges[row]),
                            "end": _round(y_edges[row + 1]),
                            "coverage_ratio": round(coverage, 12),
                            "missing_points": _round(missing),
                        }
                    )
                else:
                    absent_merges += 1
                    slot_union(index, row * columns + boundary)
            vertical_support.append(sum(present) / len(present))

        derived_cells = len({slot_find(index) for index in range(rows * columns)})
        ids = sorted(item["segment_id"] for item in group)
        pending.append(
            {
                "source_id": source_id,
                "page_1based": page_1based,
                "bbox": [_round(left), _round(top), _round(right), _round(bottom)],
                "rows": rows,
                "columns": columns,
                "atomic_slots": rows * columns,
                "derived_cells": derived_cells,
                "span_bearing": derived_cells < rows * columns,
                "present_rule_separations": present_separations,
                "absent_rule_merges": absent_merges,
                "horizontal_axis_support": [
                    round(item, 12) for item in horizontal_support
                ],
                "vertical_axis_support": [round(item, 12) for item in vertical_support],
                "minimum_internal_axis_support": round(
                    min(horizontal_support + vertical_support, default=1.0), 12
                ),
                "boundary_coverage": {
                    "outer_min_ratio": round(
                        min(item["coverage_ratio"] for item in outer_slot_measurements),
                        12,
                    ),
                    "outer_max_missing_points": _round(
                        max(item["missing_points"] for item in outer_slot_measurements)
                    ),
                    "present_internal_min_ratio": round(
                        min(
                            (
                                item["coverage_ratio"]
                                for item in present_internal_measurements
                            ),
                            default=1.0,
                        ),
                        12,
                    ),
                    "present_internal_max_missing_points": _round(
                        max(
                            (
                                item["missing_points"]
                                for item in present_internal_measurements
                            ),
                            default=0.0,
                        )
                    ),
                    "outer_sides": outer_side_measurements,
                    "outer_boundary_slots": outer_slot_measurements,
                    "present_internal_boundary_slots": present_internal_measurements,
                },
                "segment_count": len(group),
                "segment_ids_sha256": _digest(ids),
            }
        )

    pending.sort(key=lambda item: (item["bbox"], item["rows"], item["columns"]))
    for ordinal, item in enumerate(pending):
        item["component_id"] = f"{source_id}:p{page_1based}:c{ordinal}"
    return pending


def _iou(first: list[float], second: list[float]) -> float:
    intersection = max(0.0, min(first[2], second[2]) - max(first[0], second[0])) * max(
        0.0, min(first[3], second[3]) - max(first[1], second[1])
    )
    first_area = (first[2] - first[0]) * (first[3] - first[1])
    second_area = (second[2] - second[0]) * (second[3] - second[1])
    return intersection / (first_area + second_area - intersection)


def _observe_ruled_regions(
    page: Any,
    source_id: str,
    words: list[dict[str, Any]],
    raw_multi: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tables = page.find_tables(strategy="lines_strict", use_layout=False).tables
    tables = [item for item in tables if item.row_count * item.col_count > 1]
    tables.sort(key=lambda item: tuple(item.bbox))
    if len(tables) != len(raw_multi):
        raise ValueError(
            f"{source_id}:p{page.number + 1}: built-in/raw multi-cell count drift "
            f"{len(tables)} != {len(raw_multi)}"
        )

    available = set(range(len(raw_multi)))
    records = []
    for ordinal, table in enumerate(tables):
        table_bbox = _bbox(table.bbox)
        choices = sorted(
            (
                _iou(table_bbox, raw_multi[index]["bbox"]),
                index,
            )
            for index in available
        )
        match_iou, match_index = choices[-1]
        if match_iou < RAW_MATCH_MIN_IOU:
            raise ValueError(
                f"{source_id}:p{page.number + 1}: raw cross-check IoU {match_iou}"
            )
        available.remove(match_index)
        raw = raw_multi[match_index]
        if (table.row_count, table.col_count) != (raw["rows"], raw["columns"]):
            raise ValueError(
                f"{source_id}:p{page.number + 1}: raw/built-in shape drift"
            )

        cells = [_bbox(cell) for cell in table.cells]
        assignments = []
        overlapping = 0
        for word in words:
            box = word["bbox"]
            if not _overlaps(box, table_bbox):
                continue
            overlapping += 1
            options = [
                index
                for index, cell in enumerate(cells)
                if box[0] >= cell[0] - WORD_CONTAINMENT_TOLERANCE
                and box[1] >= cell[1] - WORD_CONTAINMENT_TOLERANCE
                and box[2] <= cell[2] + WORD_CONTAINMENT_TOLERANCE
                and box[3] <= cell[3] + WORD_CONTAINMENT_TOLERANCE
            ]
            if len(options) != 1:
                raise ValueError(
                    f"{source_id}:p{page.number + 1}:{word['word_id']}: "
                    f"expected one ruled-cell owner, observed {options}"
                )
            assignments.append([word["word_id"], options[0]])

        cell_rows = [
            [None if cell is None else _bbox(cell) for cell in row.cells]
            for row in table.rows
        ]
        max_delta = max(abs(a - b) for a, b in zip(table_bbox, raw["bbox"]))
        records.append(
            {
                "region_id": f"{source_id}:p{page.number + 1}:r{ordinal}",
                "source_id": source_id,
                "page_1based": page.number + 1,
                "bbox": table_bbox,
                "row_count": table.row_count,
                "column_count": table.col_count,
                "cells": cells,
                "cell_rows": cell_rows,
                "non_null_cells": len(cells),
                "word_ownership": {
                    "bbox_overlap_words": overlapping,
                    "assigned_once": len(assignments),
                    "ambiguous": 0,
                    "outside": 0,
                    "assignment_sha256": _digest(assignments),
                },
                "raw_stroke_crosscheck": {
                    "component_id": raw["component_id"],
                    "iou": round(match_iou, 12),
                    "max_bbox_edge_delta_points": _round(max_delta),
                    "shape_equal": True,
                },
            }
        )
    return records


def observe_page(document: Any, page_1based: int) -> dict[str, Any]:
    """Return a hash-bound, label-free live observation bundle for one page.

    ``document`` must be an open, file-backed PyMuPDF document. Requiring the
    original path prevents a reserialized ``document.tobytes()`` payload from
    masquerading as the archived source bytes. The caller supplies no grid,
    candidate bbox, expected shape, card ID, or review label.
    """

    import pymupdf

    observed_version = importlib.metadata.version("pymupdf")
    if observed_version != PINNED_PYMUPDF_VERSION:
        raise RuntimeError(
            f"expected PyMuPDF {PINNED_PYMUPDF_VERSION}, observed {observed_version}"
        )
    if not 1 <= page_1based <= len(document):
        raise ValueError("page_1based is outside the document")

    document_name = getattr(document, "name", None)
    if not isinstance(document_name, str) or not document_name:
        raise ValueError("observe_page requires a file-backed PyMuPDF document")
    source_path = Path(document_name).resolve()
    if not source_path.is_file():
        raise ValueError(f"document source path is not a file: {source_path}")
    source_sha256 = _sha256(source_path)
    source_id = _source_id(source_sha256)

    page = document[page_1based - 1]
    segments, drawing_counts = _axis_segments(page)
    words = _page_words(page, rich_features=True)
    page_payload = {
        "source_id": source_id,
        "page_1based": page_1based,
        "width": _round(page.rect.width),
        "height": _round(page.rect.height),
        "segments": segments,
        "words": words,
    }
    raw_components = _raw_enveloped_components(source_id, page_1based, segments)
    raw_multi = [item for item in raw_components if item["atomic_slots"] > 1]
    regions = _observe_ruled_regions(page, source_id, words, raw_multi)
    finder_regions = []
    for region in regions:
        finder_regions.append(
            {
                "finder_region_id": region["region_id"],
                "bbox": region["bbox"],
                "row_count": region["row_count"],
                "column_count": region["column_count"],
                "cells": region["cells"],
                "cell_rows": region["cell_rows"],
                "word_ownership": region["word_ownership"],
                "raw_stroke_crosscheck": region["raw_stroke_crosscheck"],
            }
        )

    pymupdf_module_path = Path(pymupdf.__file__).resolve()
    return {
        "schema": "ai-system-cards/grid-discovery-live-page/v1",
        "source_id": source_id,
        "source_sha256": source_sha256,
        "source_path": str(source_path),
        "observer": {
            "engine": "PyMuPDF",
            "version": observed_version,
            "module_sha256": _sha256(pymupdf_module_path),
            "extractor_sha256": _sha256(Path(__file__).resolve()),
            "ruled_region_call": {
                "strategy": "lines_strict",
                "use_layout": False,
                "all_other_arguments": "PyMuPDF 1.28.2 defaults",
            },
        },
        "page": page_payload,
        "drawing_provenance": drawing_counts,
        "raw_enveloped_components": raw_components,
        "finder_regions": finder_regions,
    }


def _observe_page_bound(
    page: Any, source_id: str, segments: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "page_1based": page.number + 1,
        "width": _round(page.rect.width),
        "height": _round(page.rect.height),
        "segments": segments,
        "words": _page_words(page, rich_features=True),
    }


def build_source() -> dict[str, Any]:
    import pymupdf

    observed_version = importlib.metadata.version("pymupdf")
    if observed_version != PINNED_PYMUPDF_VERSION:
        raise RuntimeError(
            f"expected PyMuPDF {PINNED_PYMUPDF_VERSION}, observed {observed_version}"
        )

    documents = []
    page_payloads = []
    page_provenance = []
    raw_components = []
    ruled_regions = []

    for spec in DOCUMENTS:
        path = ROOT / spec.path
        source_hash = _sha256(path)
        source_id = _source_id(source_hash)
        document = pymupdf.open(path)
        document_components = []
        document_regions = []
        drawing_totals: defaultdict[str, int] = defaultdict(int)
        fixture_pages = set(FULL_PAGE_FIXTURES[spec.key])

        for page in document:
            segments, drawing_counts = _axis_segments(page)
            for key, value in drawing_counts.items():
                drawing_totals[key] += value
            components = _raw_enveloped_components(source_id, page.number + 1, segments)
            multi = [item for item in components if item["atomic_slots"] > 1]
            basic_words = _page_words(page, rich_features=False)
            regions = _observe_ruled_regions(page, source_id, basic_words, multi)
            document_components.extend(components)
            document_regions.extend(regions)
            if page.number + 1 in fixture_pages:
                page_payloads.append(_observe_page_bound(page, source_id, segments))
                page_provenance.append(
                    {
                        "source_id": source_id,
                        "page_1based": page.number + 1,
                        "drawing_counts": drawing_counts,
                    }
                )

        raw_multi = [item for item in document_components if item["atomic_slots"] > 1]
        raw_single = [item for item in document_components if item["atomic_slots"] == 1]
        documents.append(
            {
                "source_id": source_id,
                "source_path": spec.path,
                "source_sha256": source_hash,
                "page_count": len(document),
                "fixture_pages": sorted(fixture_pages),
                "census": {
                    "raw_enveloped_components": len(document_components),
                    "raw_multi_cell_components": len(raw_multi),
                    "raw_single_cell_components": len(raw_single),
                    "pymupdf_ruled_regions": len(document_regions),
                    "pages_with_ruled_regions": len(
                        {item["page_1based"] for item in document_regions}
                    ),
                    "ruled_region_bbox_overlap_words": sum(
                        item["word_ownership"]["bbox_overlap_words"]
                        for item in document_regions
                    ),
                    "drawing_counts": dict(sorted(drawing_totals.items())),
                },
            }
        )
        raw_components.extend(document_components)
        ruled_regions.extend(document_regions)
        document.close()

    page_payloads.sort(key=lambda item: (item["source_id"], item["page_1based"]))
    page_provenance.sort(key=lambda item: (item["source_id"], item["page_1based"]))
    raw_components.sort(
        key=lambda item: (item["source_id"], item["page_1based"], item["bbox"])
    )
    ruled_regions.sort(
        key=lambda item: (item["source_id"], item["page_1based"], item["bbox"])
    )

    return {
        "schema": "ai-system-cards/grid-discovery-source/v1",
        "implementation": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": _sha256(Path(__file__).resolve()),
        },
        "authority_boundary": {
            "source_inputs": "hash-bound archived PDFs only",
            "accepted_markdown_used": False,
            "legacy_html_used": False,
            "docling_used": False,
            "reviewed_cell_labels_used": False,
            "semantic_role_decided": False,
        },
        "observer": {
            "engine": "PyMuPDF",
            "version": observed_version,
            "coordinate_space": COORDINATE_SPACE,
            "ruled_region_call": {
                "strategy": "lines_strict",
                "use_layout": False,
                "all_other_arguments": "PyMuPDF 1.28.2 defaults",
            },
            "raw_stroke_policy": {
                "items": "visible stroked axis-aligned l items only",
                "rectangle_items_decomposed": False,
                "axis_tolerance_points": AXIS_TOLERANCE,
                "intersection_tolerance_points": INTERSECTION_TOLERANCE,
            },
            "word_policy": {
                "extraction": "page.get_text(words, sort=True)",
                "full_bbox_cell_containment_tolerance_points": WORD_CONTAINMENT_TOLERANCE,
            },
        },
        "documents": documents,
        "pages": page_payloads,
        "page_drawing_provenance": page_provenance,
        "raw_enveloped_components": raw_components,
        "ruled_regions": ruled_regions,
    }


def _role(block: dict[str, Any]) -> str | None:
    return block.get("std") or block.get("raw")


def _tag_tables(page: Any) -> list[dict[str, Any]]:
    import pymupdf

    flags = pymupdf.TEXTFLAGS_RAWDICT | pymupdf.TEXT_COLLECT_STRUCTURE
    result = []

    def walk(block: Any) -> None:
        if not isinstance(block, dict):
            return
        if block.get("type") == 2 and _role(block) == "Table":
            rows = [
                child
                for child in block.get("blocks", [])
                if isinstance(child, dict)
                and child.get("type") == 2
                and _role(child) == "TR"
            ]
            cells = [
                cell
                for row in rows
                for cell in row.get("blocks", [])
                if isinstance(cell, dict)
                and cell.get("type") == 2
                and _role(cell) in {"TH", "TD"}
            ]
            result.append(
                {
                    "table_ordinal": len(result),
                    "bbox": _bbox(block["bbox"]),
                    "direct_rows": len(rows),
                    "direct_cells": len(cells),
                }
            )
        for child in block.get("blocks", []):
            walk(child)

    walk(page.get_text("rawdict", flags=flags))
    return result


def _caption_line(page: Any, prefix: str) -> dict[str, Any]:
    lines = [line.strip() for line in page.get_text("text", sort=True).splitlines()]
    matches = [line for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(
            f"p{page.number + 1}: expected one caption line {prefix!r}, got {matches}"
        )
    rects = page.search_for(prefix)
    if len(rects) != 1:
        raise ValueError(f"p{page.number + 1}: caption prefix geometry drift")
    return {
        "prefix": prefix,
        "extracted_first_line": matches[0],
        "first_line_sha256": hashlib.sha256(matches[0].encode()).hexdigest(),
        "prefix_bbox": _bbox(rects[0]),
    }


def build_review(source: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    """Build review-only annotations after the source proposal plane is frozen."""

    import pymupdf

    documents = {item["source_path"]: item for item in source["documents"]}
    by_key = {spec.key: documents[spec.path] for spec in DOCUMENTS}
    caption_claims = []
    tag_challenges = []
    table_caption_counts = {}

    for spec in DOCUMENTS:
        document_record = by_key[spec.key]
        document = pymupdf.open(ROOT / spec.path)
        table_labels = 0
        for page in document:
            table_labels += sum(
                bool(re.match(r"^\[Table\s+[^]]+\]", line.strip()))
                for line in page.get_text("text", sort=True).splitlines()
            )
        table_caption_counts[document_record["source_id"]] = table_labels

        for locator in [item for item in CAPTION_LOCATORS if item.document == spec.key]:
            page = document[locator.page - 1]
            claim = _caption_line(page, locator.prefix)
            regions = [
                item
                for item in source["ruled_regions"]
                if item["source_id"] == document_record["source_id"]
                and item["page_1based"] == locator.page
            ]
            if len(regions) != 1:
                raise ValueError(
                    f"{spec.key}:p{locator.page}: caption control expected one region"
                )
            caption_claims.append(
                {
                    "source_id": document_record["source_id"],
                    "page_1based": locator.page,
                    "region_id": regions[0]["region_id"],
                    "publisher_caption_claim": locator.claim,
                    "caption": claim,
                    "authority": "source publisher claim; semantic role remains reviewable",
                }
            )

        for locator in [item for item in TAG_CHALLENGES if item.document == spec.key]:
            page = document[locator.page - 1]
            tables = _tag_tables(page)
            if locator.table_ordinal >= len(tables):
                raise ValueError(f"{spec.key}:p{locator.page}: tag ordinal drift")
            observed = tables[locator.table_ordinal]
            if (observed["direct_rows"], observed["direct_cells"]) != (
                locator.rows,
                locator.cells,
            ):
                raise ValueError(f"{spec.key}:p{locator.page}: tag shape drift")
            tag_challenges.append(
                {
                    "source_id": document_record["source_id"],
                    "page_1based": locator.page,
                    "source_tag_claim": observed,
                    "visual_review_class": locator.visual_class,
                    "ruled_region_count": sum(
                        item["source_id"] == document_record["source_id"]
                        and item["page_1based"] == locator.page
                        for item in source["ruled_regions"]
                    ),
                    "conclusion": "tag claim is not a semantic table and is not detector authority",
                }
            )
        document.close()

    multi = [
        item for item in source["raw_enveloped_components"] if item["atomic_slots"] > 1
    ]
    single = [
        item for item in source["raw_enveloped_components"] if item["atomic_slots"] == 1
    ]
    visual_records = []
    for spec in DOCUMENTS:
        doc = by_key[spec.key]
        for page, classification in VISUAL_REVIEW[spec.key].items():
            visual_records.append(
                {
                    "source_id": doc["source_id"],
                    "page_1based": page,
                    "classification": classification,
                    "review_surface": "complete rendered source page",
                }
            )
    visual_records.sort(key=lambda item: (item["source_id"], item["page_1based"]))

    return {
        "schema": "ai-system-cards/grid-discovery-review/v1",
        "source_plane": {
            "path": str(SOURCE_ARTIFACT.relative_to(ROOT)),
            "sha256": source_sha256,
            "frozen_before_review": True,
        },
        "authority_boundary": {
            "runtime_detector_reads_review": False,
            "caption_claims": "source publisher claims, not geometry-derived roles",
            "structure_tags": "advisory source claims with known false positives",
            "visual_classes": "human review labels on complete source-page renders",
        },
        "corpus_census": {
            "archived_pdfs": 3,
            "source_pages": sum(item["page_count"] for item in source["documents"]),
            "pymupdf_ruled_regions": len(source["ruled_regions"]),
            "raw_multi_cell_enveloped_components": len(multi),
            "raw_single_cell_enveloped_components": len(single),
            "ruled_region_bbox_overlap_words": sum(
                item["word_ownership"]["bbox_overlap_words"]
                for item in source["ruled_regions"]
            ),
            "ruled_region_words_assigned_once": sum(
                item["word_ownership"]["assigned_once"]
                for item in source["ruled_regions"]
            ),
            "word_assignment_ambiguous": 0,
            "word_assignment_outside": 0,
            "present_rule_separations": sum(
                item["present_rule_separations"] for item in multi
            ),
            "absent_rule_merges": sum(item["absent_rule_merges"] for item in multi),
            "internally_complete_regions": sum(
                not item["span_bearing"] for item in multi
            ),
            "span_bearing_regions": sum(item["span_bearing"] for item in multi),
            "minimum_internal_axis_support": min(
                item["minimum_internal_axis_support"] for item in multi
            ),
            "minimum_outer_boundary_raw_coverage_ratio": min(
                item["boundary_coverage"]["outer_min_ratio"] for item in multi
            ),
            "maximum_outer_boundary_total_missing_points": max(
                item["boundary_coverage"]["outer_max_missing_points"] for item in multi
            ),
            "minimum_present_internal_slot_raw_coverage_ratio": min(
                item["boundary_coverage"]["present_internal_min_ratio"]
                for item in multi
            ),
            "maximum_present_internal_slot_total_missing_points": max(
                item["boundary_coverage"]["present_internal_max_missing_points"]
                for item in multi
            ),
            "table_caption_label_counts": table_caption_counts,
            "publisher_captioned_figure_grids": 2,
            "publisher_captioned_logical_grid_claims": sum(
                table_caption_counts.values()
            )
            + 2,
            "semantic_sparse_or_unruled_tables_found_in_reviewed_challenges_and_controls": 0,
            "caption_census_proves_semantic_recall": False,
        },
        "caption_claim_controls": sorted(
            caption_claims,
            key=lambda item: (item["source_id"], item["page_1based"]),
        ),
        "structure_tag_challenges": sorted(
            tag_challenges,
            key=lambda item: (item["source_id"], item["page_1based"]),
        ),
        "visual_review": visual_records,
        "natural_absent_rule_keep_separate": {
            "found": False,
            "scope": "the complete current three-PDF ruled-region census plus ten source-tag sparse challenges and representative complete-page visual controls",
            "conclusion": "This is a missing negative and a coverage limit, not evidence that absent rules universally authorize merges.",
        },
        "adversarial_limits": [
            {
                "id": "low-support-real-axis",
                "finding": "A >=0.5 internal-axis support guard rejects genuine regions: Opus p148 reaches 2/17 and Fable p252 reaches 2/13.",
            },
            {
                "id": "single-separator-mutation",
                "finding": "Deleting one separator can silently change row/column count or join cells; the exact baseline does not establish mutation safety.",
            },
            {
                "id": "split-edge-mutation",
                "finding": "A small split or shifted half-edge can create a missing boundary or phantom coordinate under fixed tolerances.",
            },
            {
                "id": "connector-fusion",
                "finding": "Added connectors can fuse adjacent ruled regions and absorb intervening prose; semantic zoning remains required.",
            },
            {
                "id": "optional-layout-drift",
                "finding": "use_layout must remain explicitly false because optional pymupdf_layout changes the observer path.",
            },
        ],
        "kill_or_block_criteria": [
            "Block semantic adoption if geometry is allowed to decide table versus figure.",
            "Block sparse/unruled claims until a natural positive and an absent-rule-keep-separate negative are source-bound.",
            "Block production adoption until mutation cliffs fail closed and a different producer plus second platform replay.",
            "Kill this boundary if external candidate boxes, Docling edges, accepted output, or reviewed cell labels enter observe_page.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-output", type=Path, required=True)
    parser.add_argument("--review-output", type=Path, required=True)
    args = parser.parse_args()

    source = build_source()
    source_bytes = _canonical(source)
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    review = build_review(source, source_hash)
    review_bytes = _canonical(review)

    args.source_output.parent.mkdir(parents=True, exist_ok=True)
    args.review_output.parent.mkdir(parents=True, exist_ok=True)
    args.source_output.write_bytes(source_bytes)
    args.review_output.write_bytes(review_bytes)
    print(
        f"source={len(source_bytes)} bytes sha256={source_hash}; "
        f"review={len(review_bytes)} bytes "
        f"sha256={hashlib.sha256(review_bytes).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
