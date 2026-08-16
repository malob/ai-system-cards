"""Build source-bound word/grid evidence for the typed alignment shadow.

This script deliberately does not import Docling, the clean candidate model, or the
production table pipeline.  Its declared table boxes, shapes, and semantic cell
ranges are reviewed proposal context.  PyMuPDF observations from the archived PDF
are the source evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import unicodedata
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


@dataclass(frozen=True)
class CellRange:
    row_start: int
    row_end: int
    column_start: int
    column_end: int

    def as_list(self) -> list[int]:
        return [self.row_start, self.row_end, self.column_start, self.column_end]


@dataclass(frozen=True)
class BoundaryControl:
    boundary_row: int
    column_start: int
    column_end: int
    verdict: str
    reason: str


@dataclass(frozen=True)
class Case:
    case_id: str
    document_id: str
    source_path: str
    page_number: int
    table_index: int
    bbox: tuple[float, float, float, float]
    rows: int
    columns: int
    classification: str
    why: str
    cells: tuple[CellRange, ...]
    boundaries: tuple[BoundaryControl, ...] = ()


def _atomic(rows: int, columns: int) -> tuple[CellRange, ...]:
    return tuple(
        CellRange(row, row + 1, col, col + 1)
        for row in range(rows)
        for col in range(columns)
    )


def _fable_attack_cells() -> tuple[CellRange, ...]:
    cells = [
        CellRange(0, 2, 0, 2),
        CellRange(0, 1, 2, 4),
        CellRange(0, 1, 4, 6),
        *(CellRange(1, 2, col, col + 1) for col in range(2, 6)),
    ]
    for row in (2, 3):
        cells.extend(CellRange(row, row + 1, col, col + 1) for col in range(6))
    for row in (4, 6):
        cells.append(CellRange(row, row + 2, 0, 1))
        cells.extend(CellRange(row, row + 1, col, col + 1) for col in range(1, 6))
        cells.extend(CellRange(row + 1, row + 2, col, col + 1) for col in range(1, 6))
    return tuple(cells)


CASES = (
    Case(
        "opus-p52-t0",
        "anthropic/claude-opus-5",
        "cards/anthropic/claude-opus-5/source.pdf",
        52,
        0,
        (69.9, 228.7, 541.7, 416.9),
        6,
        3,
        "alignment-positive",
        "Fully ruled numeric table whose rich proposal misjoins and rotates source words.",
        _atomic(6, 3),
        (
            BoundaryControl(
                1,
                0,
                1,
                "keep-separate",
                "full source rule and populated lower data cell",
            ),
        ),
    ),
    Case(
        "opus-p53-t0",
        "anthropic/claude-opus-5",
        "cards/anthropic/claude-opus-5/source.pdf",
        53,
        0,
        (69.9, 71.6, 541.6, 242.9),
        6,
        3,
        "alignment-positive-nearest-control",
        "Adjacent same-family table: source geometry is regular although the proposal rotates body cells.",
        _atomic(6, 3),
        (
            BoundaryControl(
                1,
                0,
                1,
                "keep-separate",
                "full source rule and populated lower data cell",
            ),
        ),
    ),
    Case(
        "opus-p56-t0",
        "anthropic/claude-opus-5",
        "cards/anthropic/claude-opus-5/source.pdf",
        56,
        0,
        (69.3, 71.5, 542.4, 316.2),
        7,
        5,
        "mixed-topology-and-alignment-positive",
        "Two-tier header plus one observed adjacent numeric-cell misjoin.",
        (
            CellRange(0, 2, 0, 1),
            *(CellRange(0, 1, col, col + 1) for col in range(1, 5)),
            CellRange(1, 2, 1, 3),
            CellRange(1, 2, 3, 5),
            *(
                CellRange(row, row + 1, col, col + 1)
                for row in range(2, 7)
                for col in range(5)
            ),
        ),
        (
            BoundaryControl(1, 0, 1, "span", "source rule is absent only below Model"),
            BoundaryControl(
                1,
                1,
                2,
                "keep-separate",
                "source rule separates the upper metric header from the lower API group header",
            ),
        ),
    ),
    Case(
        "opus-p56-t1",
        "anthropic/claude-opus-5",
        "cards/anthropic/claude-opus-5/source.pdf",
        56,
        1,
        (68.2, 404.6, 542.3, 607.9),
        7,
        3,
        "alignment-hard-positive-diagnostic",
        "The PDF places API, in the adjacent header and supports a Model rowspan. The candidate also has unrelated adapter-gap and row-assignment damage, so complete resolution is required before either conflict can be removed.",
        (
            CellRange(0, 2, 0, 1),
            CellRange(0, 1, 1, 2),
            CellRange(0, 1, 2, 3),
            CellRange(1, 2, 1, 2),
            CellRange(1, 2, 2, 3),
            *(
                CellRange(row, row + 1, col, col + 1)
                for row in range(2, 7)
                for col in range(3)
            ),
        ),
        (
            BoundaryControl(
                1,
                0,
                1,
                "span",
                "source rule is absent below Model and API text is wholly in the adjacent source cell",
            ),
            BoundaryControl(
                1,
                1,
                2,
                "keep-separate",
                "source rule and lower API text require separate header cells",
            ),
        ),
    ),
    Case(
        "risk-p78-t0",
        "anthropic/risk-report-2026-08",
        "cards/anthropic/risk-report-2026-08/source.pdf",
        78,
        0,
        (69.2, 356.1, 541.6, 585.8),
        6,
        3,
        "alignment-positive",
        "Fully ruled table whose proposal cyclically shifts every body row.",
        _atomic(6, 3),
        (
            BoundaryControl(
                1,
                0,
                1,
                "keep-separate",
                "full source rule and populated lower data cell",
            ),
        ),
    ),
    Case(
        "risk-p79-t0",
        "anthropic/risk-report-2026-08",
        "cards/anthropic/risk-report-2026-08/source.pdf",
        79,
        0,
        (58.2, 371.3, 554.1, 673.5),
        4,
        5,
        "natural-no-change-control",
        "First fragment of an accurately assigned multipage table.",
        _atomic(4, 5),
    ),
    Case(
        "risk-p80-t0",
        "anthropic/risk-report-2026-08",
        "cards/anthropic/risk-report-2026-08/source.pdf",
        80,
        0,
        (57.6, 71.7, 553.7, 679.1),
        10,
        5,
        "natural-no-change-control",
        "Continuation fragment with accurate source-slot assignment and no header row.",
        _atomic(10, 5),
    ),
    Case(
        "fable-p20-t0",
        "anthropic/claude-fable-5",
        "cards/anthropic/claude-fable-5/source.pdf",
        20,
        0,
        (71.4, 307.6, 541.8, 711.3),
        6,
        3,
        "natural-span-control",
        "Deterministic rich-proposal page with two long body rowspans.",
        (
            *(CellRange(0, 1, col, col + 1) for col in range(3)),
            CellRange(1, 3, 0, 1),
            CellRange(1, 2, 1, 2),
            CellRange(1, 2, 2, 3),
            CellRange(2, 3, 1, 2),
            CellRange(2, 3, 2, 3),
            *(CellRange(3, 4, col, col + 1) for col in range(3)),
            CellRange(4, 6, 0, 1),
            CellRange(4, 5, 1, 2),
            CellRange(4, 5, 2, 3),
            CellRange(5, 6, 1, 2),
            CellRange(5, 6, 2, 3),
        ),
        (
            BoundaryControl(
                2,
                0,
                1,
                "span",
                "source rule is absent under the first grouped relevance label",
            ),
            BoundaryControl(
                5,
                0,
                1,
                "span",
                "source rule is absent under the second grouped relevance label",
            ),
        ),
    ),
    Case(
        "fable-p94-t0",
        "anthropic/claude-fable-5",
        "cards/anthropic/claude-fable-5/source.pdf",
        94,
        0,
        (69.4, 71.4, 541.7, 342.5),
        8,
        6,
        "natural-nearest-control",
        "Same grammar as p95, with both two-row model labels already represented as source spans.",
        _fable_attack_cells(),
        (
            BoundaryControl(
                1,
                0,
                2,
                "span",
                "source rule is absent below the two-column Model header",
            ),
            BoundaryControl(
                1,
                2,
                4,
                "keep-separate",
                "source rule separates the attack-rate group from Attempts and Scenarios",
            ),
            BoundaryControl(
                5,
                0,
                1,
                "span",
                "source rule is absent inside the Claude Opus 4.8 label",
            ),
        ),
    ),
    Case(
        "fable-p95-t0",
        "anthropic/claude-fable-5",
        "cards/anthropic/claude-fable-5/source.pdf",
        95,
        0,
        (69.2, 242.4, 541.8, 510.1),
        8,
        6,
        "mixed-topology-and-alignment-positive",
        "Same grammar as p94; one model label is split across source rows in the proposal.",
        _fable_attack_cells(),
        (
            BoundaryControl(
                1,
                0,
                2,
                "span",
                "source rule is absent below the two-column Model header",
            ),
            BoundaryControl(
                1,
                2,
                4,
                "keep-separate",
                "source rule separates the attack-rate group from Attempts and Scenarios",
            ),
            BoundaryControl(
                5,
                0,
                1,
                "span",
                "source rule is absent inside the Claude Opus 4.8 label",
            ),
        ),
    ),
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cluster(values: list[float], tolerance: float = 1.5) -> tuple[float, ...]:
    clusters: list[list[float]] = []
    for value in sorted(values):
        if (
            not clusters
            or abs(value - sum(clusters[-1]) / len(clusters[-1])) > tolerance
        ):
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return tuple(round(sum(group) / len(group), 6) for group in clusters)


def _lines(
    page: Any, bbox: tuple[float, float, float, float]
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
    left, top, right, bottom = bbox
    height = bottom - top
    horizontal: list[tuple[float, float, float]] = []
    vertical: list[tuple[float, float, float]] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "l":
                continue
            start, end = item[1], item[2]
            x0, x1 = sorted((float(start.x), float(end.x)))
            y0, y1 = sorted((float(start.y), float(end.y)))
            if (
                abs(start.y - end.y) <= 0.5
                and x1 - x0 >= 2
                and top - 3 <= y0 <= bottom + 3
                and x1 >= left - 3
                and x0 <= right + 3
            ):
                horizontal.append((round(x0, 6), round((y0 + y1) / 2, 6), round(x1, 6)))
            elif (
                abs(start.x - end.x) <= 0.5
                and y1 - y0 >= height * 0.12
                and left - 3 <= x0 <= right + 3
                and y1 >= top - 3
                and y0 <= bottom + 3
            ):
                vertical.append((round((x0 + x1) / 2, 6), round(y0, 6), round(y1, 6)))
    return horizontal, vertical


def _grid_edges(
    case: Case,
    horizontal: list[tuple[float, float, float]],
    vertical: list[tuple[float, float, float]],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    width = case.bbox[2] - case.bbox[0]
    x_edges = _cluster([item[0] for item in vertical])
    y_edges = _cluster(
        [item[1] for item in horizontal if item[2] - item[0] >= width * 0.35]
    )
    if len(x_edges) != case.columns + 1 or len(y_edges) != case.rows + 1:
        raise ValueError(
            f"{case.case_id}: expected {(case.columns + 1, case.rows + 1)} edges, observed {(len(x_edges), len(y_edges))}"
        )
    return x_edges, y_edges


def _validate_cells(case: Case) -> None:
    slots: dict[tuple[int, int], CellRange] = {}
    for cell in case.cells:
        if not (
            0 <= cell.row_start < cell.row_end <= case.rows
            and 0 <= cell.column_start < cell.column_end <= case.columns
        ):
            raise ValueError(f"{case.case_id}: invalid cell range {cell}")
        for row in range(cell.row_start, cell.row_end):
            for column in range(cell.column_start, cell.column_end):
                if (row, column) in slots:
                    raise ValueError(
                        f"{case.case_id}: overlapping cell at {(row, column)}"
                    )
                slots[(row, column)] = cell
    expected = {(row, col) for row in range(case.rows) for col in range(case.columns)}
    if set(slots) != expected:
        raise ValueError(f"{case.case_id}: semantic cells do not cover the grid")


def _overlaps(
    first: tuple[float, float, float, float] | list[float],
    second: tuple[float, float, float, float] | list[float],
) -> bool:
    """Return whether two top-left rectangles have positive-area overlap."""

    return (
        first[2] > second[0]
        and first[0] < second[2]
        and first[3] > second[1]
        and first[1] < second[3]
    )


def _selection_status(
    center_x: float,
    center_y: float,
    x_edges: tuple[float, ...],
    y_edges: tuple[float, ...],
    tolerance: float = 0.01,
) -> str:
    if not (
        x_edges[0] < center_x < x_edges[-1] and y_edges[0] < center_y < y_edges[-1]
    ):
        return "bbox-overlap-center-outside"
    if any(abs(center_x - edge) <= tolerance for edge in x_edges[1:-1]) or any(
        abs(center_y - edge) <= tolerance for edge in y_edges[1:-1]
    ):
        return "center-on-grid-boundary"
    return "inside-by-center"


def _point(value: Any) -> list[float] | None:
    if value is None or not hasattr(value, "x") or not hasattr(value, "y"):
        return None
    return [round(float(value.x), 6), round(float(value.y), 6)]


def _word_features(
    record_bbox: list[float],
    text: str,
    spans: list[dict[str, Any]],
    links: list[dict[str, Any]],
) -> dict[str, Any]:
    def same_text_band(span: dict[str, Any]) -> bool:
        span_bbox = span["bbox"]
        span_center_y = (span_bbox[1] + span_bbox[3]) / 2
        return (
            span_bbox[2] > record_bbox[0]
            and span_bbox[0] < record_bbox[2]
            and record_bbox[1] < span_center_y < record_bbox[3]
        )

    styles = [
        {
            "text": span["text"],
            "bbox": span["bbox"],
            "font": span["font"],
            "size": span["size"],
            "flags": span["flags"],
            "color": span["color"],
            "superscript": bool(span["flags"] & 1),
        }
        for span in spans
        if same_text_band(span)
    ]
    word_links = [
        {
            "kind": link["kind"],
            "uri": link.get("uri"),
            "page": link.get("page"),
            "to": _point(link.get("to")),
            "xref": link.get("xref"),
        }
        for link in links
        if _overlaps(record_bbox, link["from"])
    ]
    punctuation = [char for char in text if unicodedata.category(char).startswith("P")]
    return {
        "punctuation": punctuation,
        "style_spans": styles,
        "links": word_links,
        "superscript": any(style["superscript"] for style in styles),
        "numeric_superscript_candidate": any(style["superscript"] for style in styles)
        and any(char.isdigit() for char in text),
    }


def _case_record(case: Case) -> dict[str, Any]:
    import pymupdf

    _validate_cells(case)
    source = ROOT / case.source_path
    document = pymupdf.open(source)
    page = document[case.page_number - 1]
    horizontal, vertical = _lines(page, case.bbox)
    x_edges, y_edges = _grid_edges(case, horizontal, vertical)
    grid_bbox = (x_edges[0], y_edges[0], x_edges[-1], y_edges[-1])
    spans = []
    for block in page.get_text("dict")["blocks"]:
        for line_record in block.get("lines", []):
            for span in line_record.get("spans", []):
                spans.append(
                    {
                        "text": span["text"],
                        "bbox": [round(float(value), 6) for value in span["bbox"]],
                        "font": span["font"],
                        "size": round(float(span["size"]), 6),
                        "flags": int(span["flags"]),
                        "color": int(span["color"]),
                    }
                )
    links = []
    for link in page.get_links():
        links.append(
            {
                **link,
                "from": [round(float(value), 6) for value in link["from"]],
            }
        )
    words = []
    page_words = page.get_text("words", sort=True)
    overlapping_word_ids = []
    for ordinal, raw in enumerate(page_words):
        x0, y0, x1, y1, text, block, line, word = raw
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        bbox = [round(x0, 6), round(y0, 6), round(x1, 6), round(y1, 6)]
        word_id = f"p{case.page_number}:b{block}:l{line}:w{word}"
        if not _overlaps(bbox, grid_bbox):
            continue
        overlapping_word_ids.append(word_id)
        selection_status = _selection_status(center_x, center_y, x_edges, y_edges)
        record = {
            "word_id": word_id,
            "ordinal": ordinal,
            "text": text,
            "bbox": bbox,
            "block": block,
            "line": line,
            "word": word,
            "selection_status": selection_status,
            "source_features": _word_features(bbox, text, spans, links),
        }
        words.append(record)

    cell_by_slot = {
        (row, column): cell
        for cell in case.cells
        for row in range(cell.row_start, cell.row_end)
        for column in range(cell.column_start, cell.column_end)
    }
    selected_by_cell = {cell: [] for cell in case.cells}
    for record in words:
        if record["selection_status"] != "inside-by-center":
            continue
        x0, y0, x1, y1 = record["bbox"]
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        row = bisect_right(y_edges, center_y) - 1
        column = bisect_right(x_edges, center_x) - 1
        selected_by_cell[cell_by_slot[(row, column)]].append(record)

    expected_cells = []
    assignment_occurrences: dict[str, int] = {}
    for cell in case.cells:
        selected = selected_by_cell[cell]
        for item in selected:
            assignment_occurrences[item["word_id"]] = (
                assignment_occurrences.get(item["word_id"], 0) + 1
            )
        expected_cells.append(
            {
                "range": cell.as_list(),
                "range_authority": "human-reviewed source-topology adjudication",
                "text_authority": "mechanically selected PyMuPDF words in the reviewed range",
                "text": " ".join(item["text"] for item in selected),
                "word_ids": [item["word_id"] for item in selected],
            }
        )
    assignment_errors = [
        item["word_id"]
        for item in words
        if item["selection_status"] == "inside-by-center"
        and assignment_occurrences.get(item["word_id"], 0) != 1
    ]
    if assignment_errors:
        raise ValueError(
            f"{case.case_id}: source words did not have exactly one expected assignment: {assignment_errors}"
        )

    crossings = []
    for record in words:
        x0, y0, x1, y1 = record["bbox"]
        crossed_x = [
            index for index, edge in enumerate(x_edges[1:-1], 1) if x0 < edge < x1
        ]
        crossed_y = [
            index for index, edge in enumerate(y_edges[1:-1], 1) if y0 < edge < y1
        ]
        if crossed_x or crossed_y:
            crossings.append(
                {
                    "word_id": record["word_id"],
                    "x_edges": crossed_x,
                    "y_edges": crossed_y,
                }
            )

    overlap_controls = [
        {
            "word_id": record["word_id"],
            "status": "ambiguous"
            if record["selection_status"] == "center-on-grid-boundary"
            else "outside",
            "reason": (
                "word center lies on an interior grid edge; no reviewed cell assignment is asserted"
                if record["selection_status"] == "center-on-grid-boundary"
                else "bbox overlaps the grid envelope but its center is outside; alignment must not silently drop or force it into a cell"
            ),
        }
        for record in words
        if record["selection_status"] != "inside-by-center"
    ]
    included_ids = [record["word_id"] for record in words]
    if included_ids != overlapping_word_ids:
        raise AssertionError(f"{case.case_id}: overlapping-word census drift")

    rule_segments = [
        [x0, y, x1]
        for x0, y, x1 in sorted(horizontal)
        if any(abs(y - edge) <= 1.25 for edge in y_edges)
    ]
    boundaries = []
    for control in case.boundaries:
        center_y = y_edges[control.boundary_row]
        centers = [
            (x_edges[col] + x_edges[col + 1]) / 2
            for col in range(control.column_start, control.column_end)
        ]
        mask = [
            any(
                abs(y - center_y) <= 1.25 and x0 - 1.25 <= center <= x1 + 1.25
                for x0, y, x1 in horizontal
            )
            for center in centers
        ]
        boundaries.append(
            {
                "boundary_row": control.boundary_row,
                "column_range": [control.column_start, control.column_end],
                "source_rule_mask": mask,
                "verdict": control.verdict,
                "reason": control.reason,
            }
        )

    document.close()
    return {
        "case_id": case.case_id,
        "classification": case.classification,
        "why": case.why,
        "source": {
            "document_id": case.document_id,
            "path": case.source_path,
            "sha256": _file_sha256(source),
            "page_number": case.page_number,
            "coordinate_space": "pdf-top-left-points",
        },
        "candidate_context": {
            "table_key": f"p{case.page_number}:table-{case.table_index}",
            "table_index": case.table_index,
            "bbox": list(case.bbox),
            "shape": [case.rows, case.columns],
            "status": "reviewed proposal context, not PDF authority",
        },
        "reviewed_topology_adjudication": {
            "status": "human-reviewed labels grounded in PDF geometry and page renders; not mechanically self-authorizing PDF truth",
            "cell_ranges": [cell.as_list() for cell in case.cells],
        },
        "geometry": {
            "x_edges": list(x_edges),
            "y_edges": list(y_edges),
            "horizontal_rules": rule_segments,
        },
        "selection_policy": "include every PyMuPDF word whose bbox has positive-area overlap with the source grid envelope; center position affects assignment status, never inclusion",
        "word_census": {
            "page_words": len(page_words),
            "bbox_overlapping_grid": len(overlapping_word_ids),
            "included": len(words),
            "inside_by_center": sum(
                record["selection_status"] == "inside-by-center" for record in words
            ),
            "bbox_overlap_center_outside": sum(
                record["selection_status"] == "bbox-overlap-center-outside"
                for record in words
            ),
            "center_on_grid_boundary": sum(
                record["selection_status"] == "center-on-grid-boundary"
                for record in words
            ),
            "omitted_bbox_overlaps": 0,
        },
        "words": words,
        "expected_cells": expected_cells,
        "word_bbox_crossings": crossings,
        "overlap_controls": overlap_controls,
        "topology_boundary_controls": boundaries,
    }


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        + b"\n"
    )


def build() -> dict[str, Any]:
    cases = [_case_record(case) for case in CASES]
    return {
        "schema": "ai-system-cards/source-word-alignment-evidence/v1",
        "implementation_sha256": _file_sha256(Path(__file__).resolve()),
        "source_observer": f"PyMuPDF {importlib.metadata.version('pymupdf')}:get_drawings+get_text(words,sort=True)",
        "coordinate_space": "pdf-top-left-points",
        "word_selection_policy": "positive-area bbox overlap with the source grid envelope; center-outside overlaps remain explicit outside controls",
        "candidate_conditioning": "Declared Docling table boxes and shapes locate the test. Cell ranges are human-reviewed source-topology labels, not mechanical PDF truth. Archived-PDF words, boxes, spans, links, and rulings are the mechanical source observations.",
        "natural_missing-rule_negative": None,
        "natural_missing_rule_negative_note": "No reviewed current-corpus table had a missing rule under a header that source truth required to remain two separate cells. Full-rule keep-separate controls are genuine natural negatives; existing-span cases are no-op controls. Do not infer universal safety from this absence.",
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = _canonical(build())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        f"{len(CASES)} cases, {len(payload)} bytes, sha256={hashlib.sha256(payload).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
