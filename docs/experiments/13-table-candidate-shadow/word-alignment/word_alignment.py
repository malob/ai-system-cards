"""Pure source-word to typed-table-cell alignment.

The aligner deliberately ignores Docling cell text and cell bounding boxes.  It
combines only a validated ``TableCandidate`` topology with source-PDF word boxes and
source-PDF grid edges.  It returns a separate projection; it never mutates or
authorizes the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass, replace
from itertools import pairwise
from typing import Any

from table_candidate import TableCandidate, TableCell

SCHEMA_VERSION = "word-cell-alignment/v1"
COORDINATE_SPACE = "pdf-top-left-points"
WORD_SELECTION = "positive-bbox-overlap-with-full-grid-rectangle"
DEFAULT_EDGE_TOLERANCE_POINTS = 0.75
IGNORABLE_COMPARISON_CHARACTER = "\u200b"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_STATUSES = frozenset(("assigned", "adapter_gap", "ambiguous", "outside_grid"))
WordBox = tuple[float, float, float, float]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _nonempty(value: str, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def _finite(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


@dataclass(frozen=True)
class SourceWord:
    word_id: str
    ordinal: int
    text: str
    bbox: WordBox
    block_index: int
    line_index: int
    word_index: int

    def __post_init__(self) -> None:
        _nonempty(self.word_id, "word_id")
        _nonempty(self.text, "word text")
        for name in ("ordinal", "block_index", "line_index", "word_index"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not isinstance(self.bbox, tuple) or len(self.bbox) != 4:
            raise TypeError("bbox must be a four-coordinate tuple")
        bbox = tuple(_finite(value, "bbox") for value in self.bbox)
        if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
            raise ValueError("word boxes must have positive width and height")
        object.__setattr__(self, "bbox", bbox)

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_id": self.word_id,
            "ordinal": self.ordinal,
            "text": self.text,
            "bbox": list(self.bbox),
            "source_order": [self.block_index, self.line_index, self.word_index],
        }


@dataclass(frozen=True)
class GridEvidence:
    document_id: str
    source_sha256: str
    page_number: int
    table_key: str
    x_edges: tuple[float, ...]
    y_edges: tuple[float, ...]
    words: tuple[SourceWord, ...]
    observer: str
    settings_json: str = "{}"
    coordinate_space: str = COORDINATE_SPACE

    def __post_init__(self) -> None:
        _nonempty(self.document_id, "document_id")
        _nonempty(self.table_key, "table_key")
        _nonempty(self.observer, "observer")
        if not isinstance(self.source_sha256, str) or not _SHA256_RE.fullmatch(
            self.source_sha256
        ):
            raise ValueError("source_sha256 must be lowercase SHA-256")
        if (
            isinstance(self.page_number, bool)
            or not isinstance(self.page_number, int)
            or self.page_number < 1
        ):
            raise ValueError("page_number must be a positive integer")
        if self.coordinate_space != COORDINATE_SPACE:
            raise ValueError(f"coordinate_space must be {COORDINATE_SPACE!r}")
        for name in ("x_edges", "y_edges"):
            values = tuple(_finite(item, name) for item in getattr(self, name))
            if len(values) < 2 or any(a >= b for a, b in pairwise(values)):
                raise ValueError(f"{name} must be strictly increasing")
            object.__setattr__(self, name, values)
        words = tuple(sorted(self.words, key=lambda item: (item.ordinal, item.word_id)))
        if any(not isinstance(item, SourceWord) for item in words):
            raise TypeError("words must contain SourceWord values")
        if len({item.word_id for item in words}) != len(words):
            raise ValueError("word IDs must be unique")
        if len({item.ordinal for item in words}) != len(words):
            raise ValueError("word ordinals must be unique")
        if any(a.ordinal >= b.ordinal for a, b in pairwise(words)):
            raise ValueError("word page ordinals must be strictly increasing")
        for item in words:
            expected = (
                f"p{self.page_number}:b{item.block_index}:"
                f"l{item.line_index}:w{item.word_index}"
            )
            if item.word_id != expected:
                raise ValueError(
                    f"word ID must equal stable source address {expected!r}"
                )
        object.__setattr__(self, "words", words)
        try:
            settings = json.loads(self.settings_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("settings_json must be valid JSON") from exc
        if not isinstance(settings, dict):
            raise TypeError("settings_json must contain a JSON object")
        if settings.get("word_selection") != WORD_SELECTION:
            raise ValueError("settings must declare the complete word-selection policy")
        object.__setattr__(self, "settings_json", _canonical_json(settings))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "word-grid-evidence/v1",
            "source": {
                "document_id": self.document_id,
                "source_sha256": self.source_sha256,
                "page_number": self.page_number,
                "table_key": self.table_key,
            },
            "coordinate_space": self.coordinate_space,
            "x_edges": list(self.x_edges),
            "y_edges": list(self.y_edges),
            "words": [item.to_dict() for item in self.words],
            "observer": self.observer,
            "settings": json.loads(self.settings_json),
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class WordAssignment:
    word_id: str
    status: str
    cell_id: str | None
    reason: str
    options: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        _nonempty(self.word_id, "assignment word_id")
        if self.status not in _STATUSES:
            raise ValueError("unknown assignment status")
        _nonempty(self.reason, "assignment reason")
        if self.status in {"assigned", "adapter_gap"} and self.cell_id is None:
            raise ValueError("resolved assignments require a cell_id")
        if self.status in {"ambiguous", "outside_grid"} and self.cell_id is not None:
            raise ValueError("unresolved assignments cannot choose a cell")
        for option_cell, fraction in self.options:
            _nonempty(option_cell, "option cell_id")
            if not 0 < _finite(fraction, "overlap_fraction") <= 1:
                raise ValueError("overlap_fraction must be in (0, 1]")
        if self.cell_id is not None and self.cell_id not in dict(self.options):
            raise ValueError("chosen cell must occur in options")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CellProjection:
    cell_id: str
    source_text: str
    assigned_word_ids: tuple[str, ...]
    ambiguous_word_ids: tuple[str, ...]
    adapter_generated: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Alignment:
    input_candidate_sha256: str
    evidence_sha256: str
    edge_tolerance_points: float
    assignments: tuple[WordAssignment, ...]
    cells: tuple[CellProjection, ...]

    def __post_init__(self) -> None:
        tolerance = _finite(self.edge_tolerance_points, "edge_tolerance_points")
        if tolerance < 0 or tolerance > 2:
            raise ValueError("edge_tolerance_points must be between 0 and 2")
        object.__setattr__(self, "edge_tolerance_points", tolerance)
        for name in ("input_candidate_sha256", "evidence_sha256"):
            if not isinstance(
                value := getattr(self, name), str
            ) or not _SHA256_RE.fullmatch(value):
                raise ValueError(f"{name} must be lowercase SHA-256")
        assignment_ids = [item.word_id for item in self.assignments]
        if len(assignment_ids) != len(set(assignment_ids)):
            raise ValueError("alignment contains duplicate word assignments")
        cell_ids = [item.cell_id for item in self.cells]
        if len(cell_ids) != len(set(cell_ids)):
            raise ValueError("alignment contains duplicate cell projections")
        known_cells = set(cell_ids)
        for assignment in self.assignments:
            if assignment.cell_id is not None and assignment.cell_id not in known_cells:
                raise ValueError("assignment chooses an unknown projected cell")
            if any(option[0] not in known_cells for option in assignment.options):
                raise ValueError("assignment option names an unknown projected cell")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "input_candidate_sha256": self.input_candidate_sha256,
            "evidence_sha256": self.evidence_sha256,
            "policy": {"edge_tolerance_points": self.edge_tolerance_points},
            "assignments": [item.to_dict() for item in self.assignments],
            "cells": [item.to_dict() for item in self.cells],
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class CellTextChange:
    cell_id: str
    before: str
    after: str
    words: tuple[SourceWord, ...]

    def __post_init__(self) -> None:
        _nonempty(self.cell_id, "change cell_id")
        if not isinstance(self.before, str) or not isinstance(self.after, str):
            raise TypeError("change text values must be strings")
        if self.before == self.after:
            raise ValueError("text change must change bytes")
        if len({word.word_id for word in self.words}) != len(self.words):
            raise ValueError("text change contains duplicate words")

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "before": self.before,
            "after": self.after,
            "words": [word.to_dict() for word in self.words],
        }


@dataclass(frozen=True)
class TextReassignment:
    candidate: TableCandidate
    alignment: Alignment
    status: str
    reason: str
    input_candidate_sha256: str
    output_candidate_sha256: str
    changes: tuple[CellTextChange, ...]
    surface_only_cell_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in {"applied", "blocked", "noop"}:
            raise ValueError("unknown text reassignment status")
        _nonempty(self.reason, "reassignment reason")
        if self.status != "applied" and (
            self.changes or self.input_candidate_sha256 != self.output_candidate_sha256
        ):
            raise ValueError(
                "blocked/no-op results must preserve bytes without changes"
            )

    def provenance_dict(self) -> dict[str, Any]:
        return {
            "name": "replace-cell-text-from-unambiguous-source-words/v1",
            "status": self.status,
            "reason": self.reason,
            "input_candidate_sha256": self.input_candidate_sha256,
            "evidence_sha256": self.alignment.evidence_sha256,
            "alignment_sha256": self.alignment.sha256,
            "output_candidate_sha256": self.output_candidate_sha256,
            "changes": [change.to_dict() for change in self.changes],
            "surface_only_cell_ids": list(self.surface_only_cell_ids),
            "invariants": [
                "every-evidence-word-has-exactly-one-explicit-status",
                "only-unambiguous-non-gap-assignments-may-change-text",
                "assigned-word-ids-are-conserved-exactly-once",
                "only-cell-text-may-change",
                "source-tool-topology-and-unknown-fields-are-preserved",
            ],
        }


def _rectangle(
    cell: TableCell, evidence: GridEvidence
) -> tuple[float, float, float, float]:
    return (
        evidence.x_edges[cell.column_start],
        evidence.y_edges[cell.row_start],
        evidence.x_edges[cell.column_end],
        evidence.y_edges[cell.row_end],
    )


def _intersection_fraction(
    word: WordBox, rectangle: tuple[float, float, float, float]
) -> float:
    left, top, right, bottom = rectangle
    width = max(0.0, min(word[2], right) - max(word[0], left))
    height = max(0.0, min(word[3], bottom) - max(word[1], top))
    return width * height / ((word[2] - word[0]) * (word[3] - word[1]))


def _contains(
    word: WordBox,
    rectangle: tuple[float, float, float, float],
    tolerance: float,
) -> bool:
    left, top, right, bottom = rectangle
    return (
        word[0] >= left - tolerance
        and word[1] >= top - tolerance
        and word[2] <= right + tolerance
        and word[3] <= bottom + tolerance
    )


def _validate_contract(candidate: TableCandidate, evidence: GridEvidence) -> None:
    if candidate.source.document_id != evidence.document_id:
        raise ValueError("evidence document_id does not match candidate")
    if candidate.source.source_sha256 != evidence.source_sha256:
        raise ValueError("evidence source hash does not match candidate")
    if candidate.source.table_key != evidence.table_key:
        raise ValueError("evidence table_key does not match candidate")
    if evidence.page_number not in {
        region.page_number for region in candidate.source.regions
    }:
        raise ValueError("evidence page is absent from candidate provenance")
    if candidate.orientation != "rot_0":
        raise ValueError("only rot_0 candidates are supported")
    if len(evidence.x_edges) != candidate.num_columns + 1:
        raise ValueError("x edge count does not match candidate columns")
    if len(evidence.y_edges) != candidate.num_rows + 1:
        raise ValueError("y edge count does not match candidate rows")


def align_words(
    candidate: TableCandidate,
    evidence: GridEvidence,
    edge_tolerance_points: float = DEFAULT_EDGE_TOLERANCE_POINTS,
) -> Alignment:
    """Project source words onto typed topology without modifying either input."""

    if not isinstance(candidate, TableCandidate):
        raise TypeError("candidate must be a TableCandidate")
    if not isinstance(evidence, GridEvidence):
        raise TypeError("evidence must be GridEvidence")
    tolerance = _finite(edge_tolerance_points, "edge_tolerance_points")
    if tolerance < 0 or tolerance > 2:
        raise ValueError("edge_tolerance_points must be between 0 and 2")
    _validate_contract(candidate, evidence)

    rectangles = {cell.cell_id: _rectangle(cell, evidence) for cell in candidate.cells}
    by_id = {cell.cell_id: cell for cell in candidate.cells}
    assignments: list[WordAssignment] = []

    for word in evidence.words:
        overlaps = [
            (cell.cell_id, round(fraction, 9))
            for cell in candidate.cells
            if (fraction := _intersection_fraction(word.bbox, rectangles[cell.cell_id]))
            > 0
        ]
        overlaps.sort(key=lambda item: (-item[1], item[0]))
        center_x = (word.bbox[0] + word.bbox[2]) / 2
        center_y = (word.bbox[1] + word.bbox[3]) / 2
        if not (
            evidence.x_edges[0] < center_x < evidence.x_edges[-1]
            and evidence.y_edges[0] < center_y < evidence.y_edges[-1]
        ):
            assignments.append(
                WordAssignment(
                    word.word_id,
                    "outside_grid",
                    None,
                    "word-center-is-outside-grid-envelope",
                    tuple(overlaps),
                )
            )
            continue
        containers = [
            cell.cell_id
            for cell in candidate.cells
            if _contains(
                word.bbox,
                rectangles[cell.cell_id],
                tolerance,
            )
        ]
        if len(containers) == 1:
            cell = by_id[containers[0]]
            status = "adapter_gap" if cell.adapter_generated else "assigned"
            reason = (
                "word-contained-by-adapter-gap"
                if cell.adapter_generated
                else "word-contained-by-one-typed-cell"
            )
            assignments.append(
                WordAssignment(
                    word.word_id, status, cell.cell_id, reason, tuple(overlaps)
                )
            )
        elif not overlaps:
            assignments.append(
                WordAssignment(
                    word.word_id,
                    "outside_grid",
                    None,
                    "word-does-not-overlap-grid",
                    (),
                )
            )
        else:
            reason = (
                "word-contained-by-multiple-cells"
                if containers
                else "word-crosses-cell-or-table-boundary"
            )
            assignments.append(
                WordAssignment(word.word_id, "ambiguous", None, reason, tuple(overlaps))
            )

    words = {word.word_id: word for word in evidence.words}
    assigned_by_cell: dict[str, list[str]] = {
        cell.cell_id: [] for cell in candidate.cells
    }
    ambiguous_by_cell: dict[str, list[str]] = {
        cell.cell_id: [] for cell in candidate.cells
    }
    for assignment in assignments:
        if assignment.cell_id is not None:
            assigned_by_cell[assignment.cell_id].append(assignment.word_id)
        elif assignment.status == "ambiguous":
            for option in assignment.options:
                ambiguous_by_cell[option[0]].append(assignment.word_id)

    cells = tuple(
        CellProjection(
            cell.cell_id,
            " ".join(words[word_id].text for word_id in assigned_by_cell[cell.cell_id]),
            tuple(assigned_by_cell[cell.cell_id]),
            tuple(ambiguous_by_cell[cell.cell_id]),
            cell.adapter_generated,
        )
        for cell in candidate.cells
    )
    result = Alignment(
        hashlib.sha256(candidate.to_json_bytes()).hexdigest(),
        evidence.sha256,
        tolerance,
        tuple(assignments),
        cells,
    )
    if {item.word_id for item in result.assignments} != {
        item.word_id for item in evidence.words
    }:
        raise AssertionError("assignment envelope does not cover every evidence word")
    if {item.cell_id for item in result.cells} != {
        item.cell_id for item in candidate.cells
    }:
        raise AssertionError("projection envelope does not cover every candidate cell")
    return result


def _comparison_key(text: str) -> str:
    """NFC, evidenced U+200B removal, and whitespace collapse; no glyph folds."""

    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace(IGNORABLE_COMPARISON_CHARACTER, "")
    return " ".join(normalized.split())


def _table_tokens(texts: tuple[str, ...]) -> Counter[str]:
    return Counter(token for text in texts for token in _comparison_key(text).split())


def reassign_cell_text(
    candidate: TableCandidate,
    evidence: GridEvidence,
    edge_tolerance_points: float = DEFAULT_EDGE_TOLERANCE_POINTS,
) -> TextReassignment:
    """Replace cell text only when every source word resolves to a real cell.

    Any ambiguous, outside-grid, or adapter-gap assignment makes the transform an
    all-or-nothing byte-identical no-op.  Empty source cells are intentionally
    cleared: this is how a misplaced observed token becomes an explicit empty cell
    without changing topology.
    """

    alignment = align_words(candidate, evidence, edge_tolerance_points)
    input_hash = hashlib.sha256(candidate.to_json_bytes()).hexdigest()
    blockers = [
        item
        for item in alignment.assignments
        if item.status in {"ambiguous", "outside_grid", "adapter_gap"}
    ]
    if blockers:
        statuses = ",".join(sorted({item.status for item in blockers}))
        return TextReassignment(
            candidate,
            alignment,
            "blocked",
            f"unresolved-source-word-status:{statuses}",
            input_hash,
            input_hash,
            (),
        )

    candidate_tokens = _table_tokens(
        tuple(cell.text for cell in candidate.cells if not cell.adapter_generated)
    )
    source_tokens = Counter(_comparison_key(word.text) for word in evidence.words)
    if candidate_tokens != source_tokens:
        return TextReassignment(
            candidate,
            alignment,
            "blocked",
            "candidate-and-source-token-inventories-differ",
            input_hash,
            input_hash,
            (),
        )

    projections = {item.cell_id: item for item in alignment.cells}
    source_words = {item.word_id: item for item in evidence.words}
    assigned_ids = [
        word_id
        for projection in alignment.cells
        for word_id in projection.assigned_word_ids
    ]
    if len(assigned_ids) != len(set(assigned_ids)) or set(assigned_ids) != set(
        source_words
    ):
        raise AssertionError("assigned source word IDs are not conserved exactly once")

    changes: list[CellTextChange] = []
    surface_only: list[str] = []
    cells: list[TableCell] = []
    for cell in candidate.cells:
        projection = projections[cell.cell_id]
        after = projection.source_text
        if cell.adapter_generated:
            if after:
                raise AssertionError("adapter gap acquired text after blocker check")
            cells.append(cell)
            continue
        if cell.text == after:
            cells.append(cell)
            continue
        if _comparison_key(cell.text) == _comparison_key(after):
            cells.append(cell)
            surface_only.append(cell.cell_id)
            continue
        updated = replace(cell, text=after)
        if replace(updated, text=cell.text) != cell:
            raise AssertionError("text replacement changed another cell field")
        cells.append(updated)
        changes.append(
            CellTextChange(
                cell.cell_id,
                cell.text,
                after,
                tuple(source_words[item] for item in projection.assigned_word_ids),
            )
        )

    if not changes:
        return TextReassignment(
            candidate,
            alignment,
            "noop",
            "source-word-projection-already-matches-cell-text",
            input_hash,
            input_hash,
            (),
            tuple(surface_only),
        )

    output = replace(candidate, cells=tuple(cells))
    if (
        output.source != candidate.source
        or output.tool != candidate.tool
        or output.num_rows != candidate.num_rows
        or output.num_columns != candidate.num_columns
        or output.orientation != candidate.orientation
        or output.tool_fields_json != candidate.tool_fields_json
    ):
        raise AssertionError(
            "text replacement changed candidate provenance or topology"
        )
    output_hash = hashlib.sha256(output.to_json_bytes()).hexdigest()
    return TextReassignment(
        output,
        alignment,
        "applied",
        "all-source-words-resolved-to-real-typed-cells",
        input_hash,
        output_hash,
        tuple(changes),
        tuple(surface_only),
    )
