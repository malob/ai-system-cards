"""Build the compact source/origin/projection evidence manifest.

The large word census and rich candidate fixtures already exist in the preceding
shadow slice.  This extractor hash-binds and transitively validates those inputs,
then emits only the exact locators needed to test the new three-layer boundary.
Accepted Markdown is never read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXPERIMENT = HERE.parents[1]
WORD_EVIDENCE = EXPERIMENT / "word-alignment/evidence/source-word-evidence.json"
ALIGNMENT_ARTIFACT = EXPERIMENT / "word-alignment/artifacts/alignment-cases.json"
RISK_LEGACY_FIXTURE = EXPERIMENT / "legacy-evidence/fixtures/risk-cache-pages.json"

sys.path[:0] = [
    str(EXPERIMENT / "clean-model"),
    str(EXPERIMENT / "word-alignment"),
]

from extract_alignment_cases import load_candidate


@dataclass(frozen=True)
class Locator:
    evidence_case: str
    source_range: tuple[int, int, int, int]
    claim_ranges: tuple[tuple[int, int, int, int], ...]
    label: str
    note: str
    boundary_row: int | None = None
    boundary_columns: tuple[int, int] | None = None
    expected_boundary_rule: bool | None = None


LOCATORS = (
    Locator(
        "opus-p56-t0",
        (1, 2, 0, 1),
        ((1, 2, 0, 1),),
        "adapter-empty-source-supported-span",
        "The adapter-created empty atomic slot is covered by the source Model rowspan; it is not a true blank.",
        1,
        (0, 1),
        False,
    ),
    Locator(
        "opus-p56-t1",
        (1, 2, 0, 1),
        ((1, 2, 0, 1),),
        "observed-source-empty-misprojected-payload",
        "Docling observed API, here, but the source slot has no words and belongs to the Model rowspan. Source-empty does not change its immutable observed origin into a gap.",
        1,
        (0, 1),
        False,
    ),
    Locator(
        "opus-p56-t1",
        (1, 2, 1, 2),
        ((1, 2, 1, 2),),
        "observed-populated-keep-separate",
        "The adjacent source cell contains API, without a system prompt and has a present rule above; it is the nearest natural keep-separate control.",
        1,
        (1, 2),
        True,
    ),
    Locator(
        "opus-p56-t1",
        (4, 5, 1, 2),
        ((4, 5, 1, 2),),
        "adapter-empty-with-source-words",
        "The adapter-created empty slot contains the source occurrence 88% (+/- 5%); an adapter gap cannot authorize omission.",
    ),
    Locator(
        "fable-p94-t0",
        (6, 8, 0, 1),
        ((6, 8, 0, 1),),
        "styled-superscript-word-trap",
        "One PyMuPDF word is 4.610 while its spans remain ordinary 4.6 plus superscript 10. Projection must preserve occurrence and style evidence without rewriting it.",
    ),
    Locator(
        "fable-p95-t0",
        (4, 6, 0, 1),
        ((4, 5, 0, 1), (5, 6, 0, 1)),
        "observed-plus-adapter-source-supported-span",
        "The source Claude Opus 4.8 label spans the absent row boundary while the extractor claim is one observed upper cell plus one adapter lower slot.",
        5,
        (0, 1),
        False,
    ),
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _overlaps(first: list[float], second: list[float]) -> bool:
    return (
        first[2] > second[0]
        and first[0] < second[2]
        and first[3] > second[1]
        and first[1] < second[3]
    )


def _word_index(page: Any) -> dict[str, dict[str, Any]]:
    result = {}
    for ordinal, raw in enumerate(page.get_text("words", sort=True)):
        x0, y0, x1, y1, text, block, line, word = raw
        word_id = f"p{page.number + 1}:b{block}:l{line}:w{word}"
        result[word_id] = {
            "word_id": word_id,
            "ordinal": ordinal,
            "text": text,
            "bbox": [round(float(v), 6) for v in (x0, y0, x1, y1)],
            "block": block,
            "line": line,
            "word": word,
        }
    return result


def _line_segments(page: Any) -> tuple[list[list[float]], list[list[float]]]:
    horizontal: list[list[float]] = []
    vertical: list[list[float]] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "l":
                continue
            start, end = item[1], item[2]
            x0, x1 = sorted((float(start.x), float(end.x)))
            y0, y1 = sorted((float(start.y), float(end.y)))
            if abs(start.y - end.y) <= 0.5:
                horizontal.append([round(x0, 6), round((y0 + y1) / 2, 6), round(x1, 6)])
            elif abs(start.x - end.x) <= 0.5:
                vertical.append([round((x0 + x1) / 2, 6), round(y0, 6), round(y1, 6)])
    return horizontal, vertical


def _contains_segment(actual: list[list[float]], expected: list[float]) -> bool:
    return any(
        all(abs(a - b) <= 0.02 for a, b in zip(item, expected)) for item in actual
    )


def _source_words_in_range(
    case: dict[str, Any], cell_range: tuple[int, ...]
) -> list[dict[str, Any]]:
    r0, r1, c0, c1 = cell_range
    x_edges = case["geometry"]["x_edges"]
    y_edges = case["geometry"]["y_edges"]
    selected = []
    for word in case["words"]:
        x0, y0, x1, y1 = word["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if x_edges[c0] < cx < x_edges[c1] and y_edges[r0] < cy < y_edges[r1]:
            selected.append(word)
    return selected


def _boundary_rule(
    case: dict[str, Any], boundary_row: int, columns: tuple[int, int]
) -> bool:
    y = case["geometry"]["y_edges"][boundary_row]
    x_edges = case["geometry"]["x_edges"]
    for column in range(*columns):
        x = (x_edges[column] + x_edges[column + 1]) / 2
        if not any(
            abs(segment[1] - y) <= 1.25 and segment[0] - 1.25 <= x <= segment[2] + 1.25
            for segment in case["geometry"]["horizontal_rules"]
        ):
            return False
    return True


def _ruled_masks(
    case_id: str,
    x_edges: list[float],
    y_edges: list[float],
    horizontal: list[list[float]],
    vertical: list[list[float]],
    tolerance: float = 1.25,
) -> tuple[list[list[bool]], list[list[bool]], dict[str, bool]]:
    """Require a bounded ruled grid, then return internal boundary masks."""

    rows = len(y_edges) - 1
    columns = len(x_edges) - 1

    def horizontal_at(y: float, column: int) -> bool:
        x = (x_edges[column] + x_edges[column + 1]) / 2
        return any(
            abs(segment[1] - y) <= tolerance
            and segment[0] - tolerance <= x <= segment[2] + tolerance
            for segment in horizontal
        )

    def vertical_at(x: float, row: int) -> bool:
        y = (y_edges[row] + y_edges[row + 1]) / 2
        return any(
            abs(segment[0] - x) <= tolerance
            and segment[1] - tolerance <= y <= segment[2] + tolerance
            for segment in vertical
        )

    outer = {
        "top": all(horizontal_at(y_edges[0], col) for col in range(columns)),
        "bottom": all(horizontal_at(y_edges[-1], col) for col in range(columns)),
        "left": all(vertical_at(x_edges[0], row) for row in range(rows)),
        "right": all(vertical_at(x_edges[-1], row) for row in range(rows)),
    }
    if not all(outer.values()):
        raise ValueError(f"{case_id}: incomplete outer ruled envelope {outer}")

    horizontal_mask = [
        [horizontal_at(y_edges[boundary], col) for col in range(columns)]
        for boundary in range(1, rows)
    ]
    vertical_mask = [
        [vertical_at(x_edges[boundary], row) for boundary in range(1, columns)]
        for row in range(rows)
    ]
    missing_horizontal = [
        boundary + 1 for boundary, mask in enumerate(horizontal_mask) if not any(mask)
    ]
    missing_vertical = [
        boundary
        for boundary in range(1, columns)
        if not any(vertical_mask[row][boundary - 1] for row in range(rows))
    ]
    if missing_horizontal or missing_vertical:
        raise ValueError(
            f"{case_id}: wholly missing internal ruled boundary "
            f"horizontal={missing_horizontal} vertical={missing_vertical}"
        )
    return horizontal_mask, vertical_mask, outer


def _rule_topology(case: dict[str, Any]) -> dict[str, Any]:
    """Re-open raw rulings and mechanically derive rectangular grid components."""

    import pymupdf

    source = ROOT / case["source"]["path"]
    document = pymupdf.open(source)
    page = document[case["source"]["page_number"] - 1]
    horizontal, vertical = _line_segments(page)
    document.close()
    x_edges = case["geometry"]["x_edges"]
    y_edges = case["geometry"]["y_edges"]
    left, right = x_edges[0], x_edges[-1]
    top, bottom = y_edges[0], y_edges[-1]
    horizontal = [
        item
        for item in horizontal
        if top - 2 <= item[1] <= bottom + 2
        and item[2] >= left - 2
        and item[0] <= right + 2
    ]
    vertical = [
        item
        for item in vertical
        if left - 2 <= item[0] <= right + 2
        and item[2] >= top - 2
        and item[1] <= bottom + 2
    ]

    rows = len(y_edges) - 1
    columns = len(x_edges) - 1
    horizontal_mask, vertical_mask, outer = _ruled_masks(
        case["case_id"], x_edges, y_edges, horizontal, vertical
    )

    parent = list(range(rows * columns))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(first: int, second: int) -> None:
        left_root, right_root = find(first), find(second)
        if left_root != right_root:
            parent[right_root] = left_root

    for row in range(rows):
        for col in range(columns):
            index = row * columns + col
            if row + 1 < rows and not horizontal_mask[row][col]:
                union(index, (row + 1) * columns + col)
            if col + 1 < columns and not vertical_mask[row][col]:
                union(index, row * columns + col + 1)
    components: dict[int, list[tuple[int, int]]] = {}
    for row in range(rows):
        for col in range(columns):
            components.setdefault(find(row * columns + col), []).append((row, col))
    derived_ranges = []
    for slots in components.values():
        row_values = [slot[0] for slot in slots]
        col_values = [slot[1] for slot in slots]
        cell_range = [
            min(row_values),
            max(row_values) + 1,
            min(col_values),
            max(col_values) + 1,
        ]
        expected_slot_count = (cell_range[1] - cell_range[0]) * (
            cell_range[3] - cell_range[2]
        )
        if expected_slot_count != len(slots):
            raise ValueError(f"{case['case_id']}: nonrectangular rule component")
        derived_ranges.append(cell_range)
    derived_ranges.sort()
    reviewed_ranges = sorted(cell["range"] for cell in case["expected_cells"])
    if derived_ranges != reviewed_ranges:
        raise ValueError(f"{case['case_id']}: raw-rule topology differs from review")

    containment_tolerance = 0.75
    assignments = []
    ambiguous = []
    outside = []
    reviewed_word_ranges = {
        word_id: cell["range"]
        for cell in case["expected_cells"]
        for word_id in cell["word_ids"]
    }
    for word in case["words"]:
        x0, y0, x1, y1 = word["bbox"]
        options = []
        for cell_range in derived_ranges:
            r0, r1, c0, c1 = cell_range
            if (
                x0 >= x_edges[c0] - containment_tolerance
                and x1 <= x_edges[c1] + containment_tolerance
                and y0 >= y_edges[r0] - containment_tolerance
                and y1 <= y_edges[r1] + containment_tolerance
            ):
                options.append(cell_range)
        if not options:
            outside.append(word["word_id"])
            continue
        if len(options) != 1:
            ambiguous.append({"word_id": word["word_id"], "options": options})
            continue
        assignments.append({"word_id": word["word_id"], "range": options[0]})
        if reviewed_word_ranges.get(word["word_id"]) != options[0]:
            raise ValueError(
                f"{case['case_id']}:{word['word_id']}: full-bbox assignment differs from review"
            )
    if ambiguous or outside or len(assignments) != len(case["words"]):
        raise ValueError(f"{case['case_id']}: source-word containment is not total")
    return {
        "case_id": case["case_id"],
        "source": case["source"],
        "candidate_conditioned_grid": {
            "table_key": case["candidate_context"]["table_key"],
            "shape": case["candidate_context"]["shape"],
            "x_edges": x_edges,
            "y_edges": y_edges,
            "status": "grid envelope and atomic edges remain candidate-conditioned locator context",
        },
        "raw_horizontal_segments": horizontal,
        "raw_vertical_segments": vertical,
        "segment_observer": "PyMuPDF 1.28.2 page.get_drawings line items in PDF top-left points",
        "rule_tolerance_points": 1.25,
        "horizontal_internal_rule_mask": horizontal_mask,
        "vertical_internal_rule_mask": vertical_mask,
        "ruled_eligibility": {
            "complete_outer_envelope": outer,
            "wholly_missing_internal_horizontal_boundaries": [],
            "wholly_missing_internal_vertical_boundaries": [],
            "eligible": True,
        },
        "mechanically_derived_rectangular_ranges": derived_ranges,
        "full_bbox_assignment": {
            "containment_tolerance_points": containment_tolerance,
            "assigned": len(assignments),
            "ambiguous": 0,
            "outside": 0,
            "assignment_sha256": hashlib.sha256(_canonical(assignments)).hexdigest(),
            "matches_reviewed_word_ranges": True,
        },
        "reviewed_range_set_sha256": hashlib.sha256(
            _canonical(reviewed_ranges)
        ).hexdigest(),
        "derived_matches_reviewed_range_set": True,
    }


def _validate_referenced_source_case(case: dict[str, Any]) -> None:
    import pymupdf

    source_path = ROOT / case["source"]["path"]
    if _sha256(source_path) != case["source"]["sha256"]:
        raise ValueError(f"{case['case_id']}: source hash drift")
    document = pymupdf.open(source_path)
    page = document[case["source"]["page_number"] - 1]
    current_words = _word_index(page)
    grid = case["geometry"]
    grid_bbox = [
        grid["x_edges"][0],
        grid["y_edges"][0],
        grid["x_edges"][-1],
        grid["y_edges"][-1],
    ]
    current_overlap = {
        word_id
        for word_id, word in current_words.items()
        if _overlaps(word["bbox"], grid_bbox)
    }
    evidence_overlap = {word["word_id"] for word in case["words"]}
    if current_overlap != evidence_overlap:
        raise ValueError(f"{case['case_id']}: bbox-overlap word census drift")
    for word in case["words"]:
        current = current_words[word["word_id"]]
        for field in ("ordinal", "text", "bbox", "block", "line", "word"):
            if current[field] != word[field]:
                raise ValueError(
                    f"{case['case_id']}:{word['word_id']}: source word {field} drift"
                )
    horizontal, vertical = _line_segments(page)
    for segment in grid["horizontal_rules"]:
        if not _contains_segment(horizontal, segment):
            raise ValueError(f"{case['case_id']}: horizontal rule drift {segment}")
    # The evidence extractor stores the long vertical rules that define x edges.
    for x_edge in grid["x_edges"]:
        if not any(abs(segment[0] - x_edge) <= 0.02 for segment in vertical):
            raise ValueError(f"{case['case_id']}: vertical edge drift {x_edge}")
    document.close()


def _candidate_cells(
    alignment_case: dict[str, Any], ranges: tuple[tuple[int, int, int, int], ...]
) -> list[dict[str, Any]]:
    candidate = load_candidate(alignment_case["candidate"])
    selected = []
    for expected in ranges:
        matches = [
            cell
            for cell in candidate.cells
            if (
                cell.row_start,
                cell.row_end,
                cell.column_start,
                cell.column_end,
            )
            == expected
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{alignment_case['case_id']}: expected one claim cell at {expected}"
            )
        selected.append(matches[0].to_dict())
    return selected


def _typed_record(
    locator: Locator,
    source_case: dict[str, Any],
    alignment_case: dict[str, Any],
) -> dict[str, Any]:
    words = _source_words_in_range(source_case, locator.source_range)
    if locator.expected_boundary_rule is not None:
        observed = _boundary_rule(
            source_case,
            locator.boundary_row or 0,
            locator.boundary_columns or (0, 0),
        )
        if observed != locator.expected_boundary_rule:
            raise ValueError(f"{locator.label}: boundary rule label drift")
    else:
        observed = None
    return {
        "case_id": f"{locator.evidence_case}:{locator.label}",
        "source_evidence_case_id": locator.evidence_case,
        "source_evidence_case_sha256": hashlib.sha256(
            _canonical(source_case)
        ).hexdigest(),
        "source": source_case["source"],
        "candidate_context": source_case["candidate_context"],
        "source_range": list(locator.source_range),
        "source_occupancy": "words" if words else "empty",
        "source_word_refs": [
            {
                "word_id": word["word_id"],
                "ordinal": word["ordinal"],
                "text": word["text"],
                "bbox": word["bbox"],
                "source_features": word["source_features"],
            }
            for word in words
        ],
        "boundary": None
        if observed is None
        else {
            "row": locator.boundary_row,
            "column_range": list(locator.boundary_columns or ()),
            "source_rule_present": observed,
        },
        "extractor_claim": {
            "candidate_sha256": alignment_case["candidate"]["candidate_sha256"],
            "cells": _candidate_cells(alignment_case, locator.claim_ranges),
            "origin_is_immutable": True,
        },
        "derived_projection_label": locator.label,
        "label_authority": "human-reviewed source-grounded test label; not runtime authority",
        "note": locator.note,
    }


def _risk_true_blank() -> dict[str, Any]:
    import pymupdf

    path = ROOT / "cards/anthropic/risk-report-2026-08/source.pdf"
    source_hash = _sha256(path)
    document = pymupdf.open(path)
    page = document[114]
    bbox = [69.5, 252.504, 156.5, 278.504]
    words = [
        word for word in _word_index(page).values() if _overlaps(word["bbox"], bbox)
    ]
    horizontal, vertical = _line_segments(page)
    required_horizontal = [[69.0, 252.504, 542.0], [69.0, 278.504, 542.0]]
    required_vertical = [[69.5, 253.004, 690.004], [156.5, 253.004, 690.004]]
    if words:
        raise ValueError("risk-p115 true-blank slot unexpectedly contains source words")
    if not all(_contains_segment(horizontal, item) for item in required_horizontal):
        raise ValueError("risk-p115 true-blank horizontal boundary drift")
    if not all(_contains_segment(vertical, item) for item in required_vertical):
        raise ValueError("risk-p115 true-blank vertical boundary drift")
    document.close()

    legacy = json.loads(RISK_LEGACY_FIXTURE.read_bytes())
    page_claims = legacy["pages"]["115"]
    if (
        len(page_claims) != 1
        or "<tr><td></td><th>CB-1 threat model" not in page_claims[0]["html"]
    ):
        raise ValueError("risk-p115 committed legacy locator drift")
    return {
        "case_id": "risk-p115-t0:true-blank-source-only-control",
        "source": {
            "document_id": "anthropic/risk-report-2026-08",
            "path": "cards/anthropic/risk-report-2026-08/source.pdf",
            "sha256": source_hash,
            "page_number": 115,
        },
        "slot_bbox": bbox,
        "source_occupancy": "empty",
        "source_word_refs": [],
        "source_word_overlap_count": 0,
        "required_horizontal_segments": required_horizontal,
        "required_vertical_segments": required_vertical,
        "derived_projection_label": "true-blank-fully-bounded-source-only-control",
        "label_authority": "human-reviewed source-grounded test label; not runtime authority",
        "executable_typed_candidate": False,
        "candidate_note": "No typed candidate fixture is committed for this page. The committed legacy Docling HTML contains an empty top-left td, but cannot establish observed-versus-adapter origin.",
        "legacy_locator": {
            "fixture_path": str(RISK_LEGACY_FIXTURE.relative_to(ROOT)),
            "fixture_sha256": _sha256(RISK_LEGACY_FIXTURE),
            "page": 115,
            "claim_sha256": hashlib.sha256(_canonical(page_claims[0])).hexdigest(),
        },
    }


def build() -> dict[str, Any]:
    word_raw = WORD_EVIDENCE.read_bytes()
    alignment_raw = ALIGNMENT_ARTIFACT.read_bytes()
    word_artifact = json.loads(word_raw)
    alignment_artifact = json.loads(alignment_raw)
    if word_artifact["schema"] != "ai-system-cards/source-word-alignment-evidence/v1":
        raise ValueError("unexpected source-word evidence schema")
    if alignment_artifact["schema"] != "ai-system-cards/word-alignment-cases/v1":
        raise ValueError("unexpected word-alignment artifact schema")
    source_cases = {case["case_id"]: case for case in word_artifact["cases"]}
    alignment_cases = {case["case_id"]: case for case in alignment_artifact["cases"]}
    required = {locator.evidence_case for locator in LOCATORS}
    for source_case in source_cases.values():
        _validate_referenced_source_case(source_case)
    for case_id in required:
        if alignment_cases[case_id]["source_evidence_case_id"] != case_id:
            raise ValueError(f"{case_id}: alignment/source evidence locator drift")

    typed_cases = [
        _typed_record(
            locator,
            source_cases[locator.evidence_case],
            alignment_cases[locator.evidence_case],
        )
        for locator in LOCATORS
    ]
    p56_words = source_cases["opus-p56-t1"]["words"]
    by_id = {word["word_id"]: word for word in p56_words}
    repeated_ids = ["p56:b23:l1:w0", "p56:b24:l1:w0"]
    if [by_id[word_id]["text"] for word_id in repeated_ids] != ["88%", "88%"]:
        raise ValueError("p56 repeated-token occurrence control drift")

    return {
        "schema": "ai-system-cards/origin-projection-source-evidence/v1",
        "authority_boundary": {
            "source_observations": "mechanical PyMuPDF observations re-opened from hash-bound archived PDFs",
            "extractor_claims": "immutable typed Docling candidate origins replayed from the hash-bound alignment artifact",
            "derived_projection_labels": "human-reviewed source-grounded test labels; never runtime authority",
            "accepted_markdown_used": False,
        },
        "inputs": {
            "implementation": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "source_word_evidence": {
                "path": str(WORD_EVIDENCE.relative_to(ROOT)),
                "sha256": hashlib.sha256(word_raw).hexdigest(),
            },
            "word_alignment_artifact": {
                "path": str(ALIGNMENT_ARTIFACT.relative_to(ROOT)),
                "sha256": hashlib.sha256(alignment_raw).hexdigest(),
            },
        },
        "typed_cases": typed_cases,
        "rule_topology_cases": [
            _rule_topology(case) for case in word_artifact["cases"]
        ],
        "source_only_controls": [_risk_true_blank()],
        "repeated_token_occurrence_control": {
            "source_evidence_case_id": "opus-p56-t1",
            "text": "88%",
            "word_ids": repeated_ids,
            "ordinals": [by_id[word_id]["ordinal"] for word_id in repeated_ids],
            "require_distinct_occurrence_identity": True,
        },
        "natural_absent_rule_keep_separate_negative": False,
        "natural_absent_rule_keep_separate_note": "The selected corpus still has no natural source-empty absent-rule cell that must remain separate. Risk p115 is a true blank only because all four boundaries are present. Do not generalize an absent-rule merge.",
        "all_source_overlap_censuses_transitively_revalidated": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = _canonical(build()) + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        f"wrote {args.output} ({len(payload)} bytes, sha256={hashlib.sha256(payload).hexdigest()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
