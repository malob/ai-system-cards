"""One pure shadow correction for typed tables with missing PDF rules."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, replace
from itertools import pairwise
from typing import Any

from table_candidate import TableCandidate, TableCell

TRANSFORM = "extend-header-through-adapter-gap-at-missing-rule/v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_INVARIANTS = (
    "source-hash-and-page-bound",
    "only-typed-headers-and-adapter-gaps-removed",
    "header-payload-and-non-target-cells-preserved",
    "clean-model-total-grid-revalidated",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: str) -> str:
    visible = "".join(c for c in value if unicodedata.category(c) != "Cf")
    return " ".join(visible.split())


def _finite(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


@dataclass(frozen=True)
class RuleEvidence:
    """Minimal independent evidence: grid edges, rulings, and ordered word centers.

    ``horizontal_segments`` are ``(x0, y, x1)`` triples. ``words`` are ordered
    ``(text, center_x, center_y)`` triples from PyMuPDF's public word API.
    """

    source_sha256: str
    page_number: int
    x_edges: tuple[float, ...]
    y_edges: tuple[float, ...]
    horizontal_segments: tuple[tuple[float, float, float], ...]
    words: tuple[tuple[str, float, float], ...]
    extractor: str
    tolerance: float = 1.25

    def __post_init__(self) -> None:
        if not _SHA256.fullmatch(self.source_sha256):
            raise ValueError("evidence requires a lowercase source SHA-256")
        if isinstance(self.page_number, bool) or self.page_number < 1:
            raise ValueError("evidence page must be a positive integer")
        if not self.extractor:
            raise ValueError("evidence extractor must be named")
        if not _finite(self.tolerance) or self.tolerance <= 0:
            raise ValueError("evidence tolerance must be positive and finite")
        for name, edges in (("x", self.x_edges), ("y", self.y_edges)):
            if len(edges) < 2 or not all(_finite(value) for value in edges):
                raise ValueError(f"{name} edges must be finite")
            if any(right <= left for left, right in pairwise(edges)):
                raise ValueError(f"{name} edges must be strictly increasing")
        segments = tuple(sorted(self.horizontal_segments))
        if any(
            len(item) != 3
            or not all(_finite(value) for value in item)
            or item[2] <= item[0]
            for item in segments
        ):
            raise ValueError("horizontal segments must be finite (x0,y,x1) triples")
        if any(
            len(item) != 3
            or not isinstance(item[0], str)
            or not item[0]
            or not _finite(item[1])
            or not _finite(item[2])
            for item in self.words
        ):
            raise ValueError("words must be non-empty (text,cx,cy) triples")
        object.__setattr__(self, "horizontal_segments", segments)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "page_number": self.page_number,
            "coordinate_origin": "TOPLEFT",
            "x_edges": list(self.x_edges),
            "y_edges": list(self.y_edges),
            "horizontal_segments": [list(item) for item in self.horizontal_segments],
            "words": [list(item) for item in self.words],
            "extractor": self.extractor,
            "tolerance": self.tolerance,
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())

    def has_rule(self, boundary_row: int, column: int) -> bool:
        y = self.y_edges[boundary_row]
        x = (self.x_edges[column] + self.x_edges[column + 1]) / 2
        return any(
            abs(segment_y - y) <= self.tolerance
            and x0 - self.tolerance <= x <= x1 + self.tolerance
            for x0, segment_y, x1 in self.horizontal_segments
        )

    def text_in(
        self, row_start: int, row_end: int, column_start: int, column_end: int
    ) -> str:
        x0, x1 = self.x_edges[column_start], self.x_edges[column_end]
        y0, y1 = self.y_edges[row_start], self.y_edges[row_end]
        return " ".join(
            word
            for word, center_x, center_y in self.words
            if x0 < center_x < x1 and y0 < center_y < y1
        )


@dataclass(frozen=True)
class Decision:
    boundary_row: int
    column_range: tuple[int, int]
    upper_cell_id: str
    lower_cell_ids: tuple[str, ...]
    status: str
    reason: str
    output_cell_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_row": self.boundary_row,
            "column_range": list(self.column_range),
            "upper_cell_id": self.upper_cell_id,
            "lower_cell_ids": list(self.lower_cell_ids),
            "status": self.status,
            "reason": self.reason,
            "output_cell_id": self.output_cell_id,
        }


@dataclass(frozen=True)
class Reconciliation:
    candidate: TableCandidate
    input_sha256: str
    evidence_sha256: str
    output_sha256: str
    decisions: tuple[Decision, ...]

    def provenance_dict(self) -> dict[str, Any]:
        return {
            "name": TRANSFORM,
            "input_candidate_sha256": self.input_sha256,
            "evidence_sha256": self.evidence_sha256,
            "output_candidate_sha256": self.output_sha256,
            "decisions": [item.to_dict() for item in self.decisions],
            "invariants": list(_INVARIANTS),
        }


def _candidate_digest(candidate: TableCandidate) -> str:
    return hashlib.sha256(candidate.to_json_bytes()).hexdigest()


def _cell_id(candidate: TableCandidate, cell: TableCell, row_end: int) -> str:
    return (
        f"{candidate.candidate_id}#r{cell.row_start}-{row_end}:"
        f"c{cell.column_start}-{cell.column_end}"
    )


def _blocked(
    boundary: int, upper: TableCell, lower_ids: tuple[str, ...], reason: str
) -> Decision:
    return Decision(
        boundary,
        (upper.column_start, upper.column_end),
        upper.cell_id,
        lower_ids,
        "blocked",
        reason,
    )


def reconcile_missing_header_rules(
    candidate: TableCandidate, evidence: RuleEvidence
) -> Reconciliation:
    """Extend a typed header by one row, but only across proven adapter gaps."""

    if candidate.source.source_sha256 != evidence.source_sha256:
        raise ValueError("evidence source hash does not match candidate")
    if evidence.page_number not in {r.page_number for r in candidate.source.regions}:
        raise ValueError("evidence page is absent from candidate provenance")
    if candidate.orientation != "rot_0":
        raise ValueError("only rot_0 candidates are supported")
    if (
        len(evidence.x_edges) != candidate.num_columns + 1
        or len(evidence.y_edges) != candidate.num_rows + 1
    ):
        raise ValueError("evidence edge counts do not match candidate dimensions")

    input_hash = _candidate_digest(candidate)
    grid = candidate.grid_cell_ids()
    by_id = {cell.cell_id: cell for cell in candidate.cells}
    decisions: list[Decision] = []
    proposals: list[tuple[TableCell, tuple[TableCell, ...], TableCell]] = []
    claimed: set[str] = set()

    for boundary in range(1, candidate.num_rows):
        reviewed: set[str] = set()
        for column in range(candidate.num_columns):
            upper_id, lower_id = grid[boundary - 1][column], grid[boundary][column]
            if upper_id == lower_id or upper_id in reviewed:
                continue
            upper = by_id[upper_id]
            reviewed.add(upper_id)
            if upper.row_end != boundary:
                continue
            columns = range(upper.column_start, upper.column_end)
            mask = [evidence.has_rule(boundary, item) for item in columns]
            if all(mask):
                continue
            lower_ids = tuple(dict.fromkeys(grid[boundary][item] for item in columns))

            if any(mask):
                decisions.append(
                    _blocked(
                        boundary, upper, lower_ids, "partial-rule-across-upper-cell"
                    )
                )
                continue
            if not any(
                evidence.has_rule(boundary, item)
                for item in range(candidate.num_columns)
                if not upper.column_start <= item < upper.column_end
            ):
                decisions.append(
                    _blocked(
                        boundary,
                        upper,
                        lower_ids,
                        "no-adjacent-rule-to-prove-row-boundary",
                    )
                )
                continue
            if not upper.header_roles:
                decisions.append(
                    _blocked(
                        boundary, upper, lower_ids, "upper-cell-is-not-a-typed-header"
                    )
                )
                continue
            lowers = tuple(by_id[item] for item in lower_ids)
            if (
                len(lowers) != upper.column_span
                or {cell.column_start for cell in lowers} != set(columns)
                or not all(
                    cell.adapter_generated
                    and cell.row_start == boundary
                    and cell.row_end == boundary + 1
                    and cell.row_span == cell.column_span == 1
                    for cell in lowers
                )
            ):
                decisions.append(
                    _blocked(
                        boundary,
                        upper,
                        lower_ids,
                        "lower-range-is-not-exact-adapter-gaps",
                    )
                )
                continue
            source_text = evidence.text_in(
                upper.row_start,
                boundary + 1,
                upper.column_start,
                upper.column_end,
            )
            if _text(source_text) != _text(upper.text):
                decisions.append(
                    _blocked(
                        boundary,
                        upper,
                        lower_ids,
                        "extended-source-words-do-not-match-header-payload",
                    )
                )
                continue
            if upper.cell_id in claimed or claimed.intersection(lower_ids):
                decisions.append(
                    _blocked(
                        boundary,
                        upper,
                        lower_ids,
                        "merge-overlaps-another-proposal",
                    )
                )
                continue

            output_id = _cell_id(candidate, upper, boundary + 1)
            extended = replace(
                upper,
                cell_id=output_id,
                row_end=boundary + 1,
                row_span=boundary + 1 - upper.row_start,
            )
            claimed.update((upper.cell_id, *lower_ids))
            proposals.append((upper, lowers, extended))
            decisions.append(
                Decision(
                    boundary,
                    (upper.column_start, upper.column_end),
                    upper.cell_id,
                    lower_ids,
                    "merged",
                    "typed-header-adapter-gaps-and-source-missing-rule-agree",
                    output_id,
                )
            )

    output = candidate
    if proposals:
        removed = {
            cell.cell_id for upper, lowers, _ in proposals for cell in (upper, *lowers)
        }
        cells = [cell for cell in candidate.cells if cell.cell_id not in removed]
        cells.extend(extended for _, _, extended in proposals)
        output = replace(candidate, cells=tuple(cells))  # revalidates total grid
        if output.source != candidate.source or output.tool != candidate.tool:
            raise AssertionError("transform changed provenance")
        output_by_id = {cell.cell_id: cell for cell in output.cells}
        if any(
            output_by_id.get(cell.cell_id) != cell
            for cell in candidate.cells
            if cell.cell_id not in removed
        ):
            raise AssertionError("transform changed a non-target cell")
        for upper, _, extended in proposals:
            restored = replace(
                extended,
                cell_id=upper.cell_id,
                row_end=upper.row_end,
                row_span=upper.row_span,
            )
            if restored != upper:
                raise AssertionError("transform changed header payload")

    return Reconciliation(
        output,
        input_hash,
        evidence.sha256,
        _candidate_digest(output),
        tuple(decisions),
    )
