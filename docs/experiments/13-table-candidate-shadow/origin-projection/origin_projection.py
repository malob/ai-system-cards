"""One-shot raw-rule/word to extractor-claim overlay.

``SourcePlane`` retains immutable PDF words, features, grid edges, and raw rules.
``ClaimPlane`` retains immutable extractor claims, including observed-versus-adapter
origin. ``OverlayResult`` contains derived components and contradictions. Reviewed
cell ranges are test labels only and are not accepted by this module.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

SCHEMA_VERSION = "origin-projection/v2"
COORDINATE_SPACE = "pdf-top-left-points"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _object_json(value: Any, label: str) -> str:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} must be valid JSON") from exc
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a JSON object")
    return _json(value)


def _require_sha(value: str, label: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{label} must be lowercase SHA-256")


def _text_key(value: str) -> str:
    # The hard set contains one source-evidenced U+200B surface difference.
    return " ".join(unicodedata.normalize("NFC", value).replace("\u200b", "").split())


def classify_bounded_slot(
    source_word_overlap_count: int, boundary_present: tuple[bool, bool, bool, bool]
) -> str:
    """Classify a source-only slot without inferring extractor origin.

    Boundary order is top, bottom, left, right.  An unbounded slot fails closed;
    ``true_blank`` says only that the source region is empty and fully bounded.
    """

    if (
        isinstance(source_word_overlap_count, bool)
        or not isinstance(source_word_overlap_count, int)
        or source_word_overlap_count < 0
    ):
        raise ValueError("source_word_overlap_count must be a non-negative integer")
    if len(boundary_present) != 4 or any(
        not isinstance(value, bool) for value in boundary_present
    ):
        raise TypeError("boundary_present must contain four booleans")
    if not all(boundary_present):
        return "blocked_unbounded"
    return "true_blank" if source_word_overlap_count == 0 else "occupied"


@dataclass(frozen=True, order=True)
class GridRange:
    row_start: int
    row_end: int
    column_start: int
    column_end: int

    def __post_init__(self) -> None:
        values = (self.row_start, self.row_end, self.column_start, self.column_end)
        if any(
            isinstance(value, bool) or not isinstance(value, int) for value in values
        ):
            raise TypeError("grid range coordinates must be integers")
        if self.row_start < 0 or self.column_start < 0:
            raise ValueError("grid ranges must start at non-negative offsets")
        if self.row_end <= self.row_start or self.column_end <= self.column_start:
            raise ValueError("grid ranges must be non-empty and half-open")

    def slots(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (row, column)
            for row in range(self.row_start, self.row_end)
            for column in range(self.column_start, self.column_end)
        )

    def to_list(self) -> list[int]:
        return [self.row_start, self.row_end, self.column_start, self.column_end]


@dataclass(frozen=True)
class RuleSegment:
    orientation: str
    fixed: float
    start: float
    end: float

    def __post_init__(self) -> None:
        if self.orientation not in {"horizontal", "vertical"}:
            raise ValueError("rule orientation must be horizontal or vertical")
        values = tuple(float(value) for value in (self.fixed, self.start, self.end))
        if not all(math.isfinite(value) for value in values) or values[2] <= values[1]:
            raise ValueError("rule segment must be finite with positive length")
        object.__setattr__(self, "fixed", values[0])
        object.__setattr__(self, "start", values[1])
        object.__setattr__(self, "end", values[2])

    def to_dict(self) -> dict[str, Any]:
        return {
            "orientation": self.orientation,
            "fixed": self.fixed,
            "start": self.start,
            "end": self.end,
        }


@dataclass(frozen=True)
class SourceWord:
    word_id: str
    ordinal: int
    text: str
    bbox: tuple[float, float, float, float]
    features_json: str

    def __post_init__(self) -> None:
        if not isinstance(self.word_id, str) or not self.word_id:
            raise ValueError("word_id must be non-empty")
        if isinstance(self.ordinal, bool) or not isinstance(self.ordinal, int):
            raise TypeError("word ordinal must be an integer")
        if not isinstance(self.text, str) or not self.text:
            raise ValueError("word text must be non-empty")
        if not isinstance(self.bbox, tuple) or len(self.bbox) != 4:
            raise TypeError("word bbox must contain four coordinates")
        box = tuple(float(value) for value in self.bbox)
        if (
            not all(math.isfinite(value) for value in box)
            or box[2] <= box[0]
            or box[3] <= box[1]
        ):
            raise ValueError("word bbox must be finite with positive area")
        object.__setattr__(self, "bbox", box)
        object.__setattr__(
            self, "features_json", _object_json(self.features_json, "word features")
        )

    @property
    def has_styled_token_boundary(self) -> bool:
        features = json.loads(self.features_json)
        return bool(
            features.get("numeric_superscript_candidate") or features.get("superscript")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_id": self.word_id,
            "ordinal": self.ordinal,
            "text": self.text,
            "bbox": list(self.bbox),
            "features": json.loads(self.features_json),
        }


@dataclass(frozen=True)
class SourcePlane:
    case_id: str
    document_id: str
    source_sha256: str
    page_number: int
    table_key: str
    rows: int
    columns: int
    x_edges: tuple[float, ...]
    y_edges: tuple[float, ...]
    words: tuple[SourceWord, ...]
    rules: tuple[RuleSegment, ...]
    source_word_evidence_sha256: str
    origin_evidence_sha256: str
    rule_tolerance_points: float = 1.25
    word_tolerance_points: float = 0.75
    candidate_conditioned_grid: bool = True

    def __post_init__(self) -> None:
        if not all((self.case_id, self.document_id, self.table_key)):
            raise ValueError("source identity fields must be non-empty")
        for value, label in (
            (self.source_sha256, "source_sha256"),
            (self.source_word_evidence_sha256, "source_word_evidence_sha256"),
            (self.origin_evidence_sha256, "origin_evidence_sha256"),
        ):
            _require_sha(value, label)
        if self.page_number < 1 or self.rows < 1 or self.columns < 1:
            raise ValueError("source page and dimensions must be positive")
        if not self.candidate_conditioned_grid:
            raise ValueError(
                "this slice must disclose candidate-conditioned grid edges"
            )
        for name, supplied, size in (
            ("x_edges", self.x_edges, self.columns),
            ("y_edges", self.y_edges, self.rows),
        ):
            edges = tuple(float(item) for item in supplied)
            if len(edges) != size + 1 or any(a >= b for a, b in pairwise(edges)):
                raise ValueError(f"{name} must be strictly increasing and grid-sized")
            object.__setattr__(self, name, edges)
        for name in ("rule_tolerance_points", "word_tolerance_points"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0 or value > 2:
                raise ValueError(f"{name} must be finite and in [0, 2]")
            object.__setattr__(self, name, value)
        words = tuple(sorted(self.words, key=lambda item: (item.ordinal, item.word_id)))
        if len({word.word_id for word in words}) != len(words) or len(
            {word.ordinal for word in words}
        ) != len(words):
            raise ValueError("source word IDs and ordinals must be unique")
        rules = tuple(
            sorted(
                self.rules,
                key=lambda item: (item.orientation, item.fixed, item.start, item.end),
            )
        )
        if len({(r.orientation, r.fixed, r.start, r.end) for r in rules}) != len(rules):
            raise ValueError("raw rule segments must be unique")
        object.__setattr__(self, "words", words)
        object.__setattr__(self, "rules", rules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "raw-source-plane/v1",
            "case_id": self.case_id,
            "source": {
                "document_id": self.document_id,
                "sha256": self.source_sha256,
                "page_number": self.page_number,
                "table_key": self.table_key,
            },
            "grid": {
                "rows": self.rows,
                "columns": self.columns,
                "x_edges": list(self.x_edges),
                "y_edges": list(self.y_edges),
                "coordinate_space": COORDINATE_SPACE,
                "candidate_conditioned": self.candidate_conditioned_grid,
            },
            "words": [word.to_dict() for word in self.words],
            "rules": [rule.to_dict() for rule in self.rules],
            "policy": {
                "rule_tolerance_points": self.rule_tolerance_points,
                "word_tolerance_points": self.word_tolerance_points,
                "eligibility": "complete-outer-envelope-and-each-internal-axis-boundary-observed",
            },
            "input_hashes": {
                "source_word_evidence_sha256": self.source_word_evidence_sha256,
                "origin_evidence_sha256": self.origin_evidence_sha256,
            },
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class ClaimCell:
    claim_id: str
    range: GridRange
    text: str
    origin: str
    payload_json: str

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, str) or not self.claim_id:
            raise ValueError("claim_id must be non-empty")
        if self.origin not in {"observed", "adapter_gap"}:
            raise ValueError("claim origin must be observed or adapter_gap")
        if not isinstance(self.text, str):
            raise TypeError("claim text must be a string")
        if self.origin == "adapter_gap" and self.text:
            raise ValueError("adapter-gap claims cannot contain text")
        payload_json = _object_json(self.payload_json, "claim payload")
        payload = json.loads(payload_json)
        required = {
            "cell_id": self.claim_id,
            "row_range": [self.range.row_start, self.range.row_end],
            "column_range": [self.range.column_start, self.range.column_end],
            "text": self.text,
            "adapter_generated": self.origin == "adapter_gap",
        }
        if any(payload.get(key) != value for key, value in required.items()):
            raise ValueError("claim payload disagrees with normalized claim fields")
        object.__setattr__(self, "payload_json", payload_json)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "range": self.range.to_list(),
            "text": self.text,
            "origin": self.origin,
            "payload": json.loads(self.payload_json),
        }


@dataclass(frozen=True)
class ClaimPlane:
    case_id: str
    document_id: str
    source_sha256: str
    page_number: int
    table_key: str
    rows: int
    columns: int
    candidate_sha256: str
    tool_json: str
    cells: tuple[ClaimCell, ...]

    def __post_init__(self) -> None:
        _require_sha(self.source_sha256, "claim source_sha256")
        _require_sha(self.candidate_sha256, "candidate_sha256")
        object.__setattr__(
            self, "tool_json", _object_json(self.tool_json, "claim tool")
        )
        cells = tuple(sorted(self.cells, key=lambda item: (item.range, item.claim_id)))
        if len({cell.claim_id for cell in cells}) != len(cells):
            raise ValueError("claim IDs must be unique")
        slots: dict[tuple[int, int], str] = {}
        for cell in cells:
            if cell.range.row_end > self.rows or cell.range.column_end > self.columns:
                raise ValueError("claim cell exceeds grid")
            for slot in cell.range.slots():
                if slot in slots:
                    raise ValueError("claim cells overlap")
                slots[slot] = cell.claim_id
        expected = {
            (row, column) for row in range(self.rows) for column in range(self.columns)
        }
        if set(slots) != expected:
            raise ValueError("claim cells must cover every atomic slot exactly once")
        object.__setattr__(self, "cells", cells)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "extractor-claim-plane/v1",
            "case_id": self.case_id,
            "source": {
                "document_id": self.document_id,
                "sha256": self.source_sha256,
                "page_number": self.page_number,
                "table_key": self.table_key,
            },
            "grid": {"rows": self.rows, "columns": self.columns},
            "candidate_sha256": self.candidate_sha256,
            "tool": json.loads(self.tool_json),
            "cells": [cell.to_dict() for cell in self.cells],
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class WordAssociation:
    word_id: str
    status: str
    component_range: GridRange | None
    options: tuple[GridRange, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_id": self.word_id,
            "status": self.status,
            "component_range": None
            if self.component_range is None
            else self.component_range.to_list(),
            "options": [item.to_list() for item in self.options],
        }


@dataclass(frozen=True)
class ComponentProjection:
    range: GridRange
    word_ids: tuple[str, ...]
    materialized_text: str | None
    overlapping_claim_ids: tuple[str, ...]
    decision: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "range": self.range.to_list(),
            "word_ids": list(self.word_ids),
            "materialized_text": self.materialized_text,
            "overlapping_claim_ids": list(self.overlapping_claim_ids),
            "decision": self.decision,
        }


@dataclass(frozen=True)
class Conflict:
    kind: str
    range: GridRange
    claim_ids: tuple[str, ...]
    word_ids: tuple[str, ...]
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "range": self.range.to_list(),
            "claim_ids": list(self.claim_ids),
            "word_ids": list(self.word_ids),
            "detail": self.detail,
        }


@dataclass(frozen=True)
class OverlayResult:
    status: str
    reason: str
    source_plane_sha256: str
    claim_plane_sha256: str
    input_candidate_sha256: str
    output_candidate_sha256: str
    components: tuple[ComponentProjection, ...]
    associations: tuple[WordAssociation, ...]
    conflicts: tuple[Conflict, ...]

    def __post_init__(self) -> None:
        if self.status not in {"noop", "proposed", "blocked"}:
            raise ValueError("unknown overlay status")
        for value in (
            self.source_plane_sha256,
            self.claim_plane_sha256,
            self.input_candidate_sha256,
            self.output_candidate_sha256,
        ):
            _require_sha(value, "overlay hash")
        if self.input_candidate_sha256 != self.output_candidate_sha256:
            raise ValueError("the shadow overlay may not mutate candidate bytes")
        if self.status == "blocked" and any(
            item.materialized_text is not None for item in self.components
        ):
            raise ValueError("blocked overlays cannot expose partial materialized text")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "status": self.status,
            "reason": self.reason,
            "source_plane_sha256": self.source_plane_sha256,
            "claim_plane_sha256": self.claim_plane_sha256,
            "input_candidate_sha256": self.input_candidate_sha256,
            "output_candidate_sha256": self.output_candidate_sha256,
            "components": [item.to_dict() for item in self.components],
            "associations": [item.to_dict() for item in self.associations],
            "conflicts": [item.to_dict() for item in self.conflicts],
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_dict())


def _rule_present(
    rules: tuple[RuleSegment, ...],
    orientation: str,
    fixed: float,
    position: float,
    tolerance: float,
) -> bool:
    return any(
        rule.orientation == orientation
        and abs(rule.fixed - fixed) <= tolerance
        and rule.start - tolerance <= position <= rule.end + tolerance
        for rule in rules
    )


def _rule_masks(source: SourcePlane) -> tuple[list[list[bool]], list[list[bool]]]:
    horizontal = [
        [
            _rule_present(
                source.rules,
                "horizontal",
                source.y_edges[row],
                (source.x_edges[column] + source.x_edges[column + 1]) / 2,
                source.rule_tolerance_points,
            )
            for column in range(source.columns)
        ]
        for row in range(1, source.rows)
    ]
    vertical = [
        [
            _rule_present(
                source.rules,
                "vertical",
                source.x_edges[column],
                (source.y_edges[row] + source.y_edges[row + 1]) / 2,
                source.rule_tolerance_points,
            )
            for column in range(1, source.columns)
        ]
        for row in range(source.rows)
    ]
    return horizontal, vertical


def _eligible(
    source: SourcePlane, horizontal: list[list[bool]], vertical: list[list[bool]]
) -> bool:
    tolerance = source.rule_tolerance_points
    top = all(
        _rule_present(
            source.rules, "horizontal", source.y_edges[0], (a + b) / 2, tolerance
        )
        for a, b in pairwise(source.x_edges)
    )
    bottom = all(
        _rule_present(
            source.rules, "horizontal", source.y_edges[-1], (a + b) / 2, tolerance
        )
        for a, b in pairwise(source.x_edges)
    )
    left = all(
        _rule_present(
            source.rules, "vertical", source.x_edges[0], (a + b) / 2, tolerance
        )
        for a, b in pairwise(source.y_edges)
    )
    right = all(
        _rule_present(
            source.rules, "vertical", source.x_edges[-1], (a + b) / 2, tolerance
        )
        for a, b in pairwise(source.y_edges)
    )
    return (
        top
        and bottom
        and left
        and right
        and all(any(row) for row in horizontal)
        and all(
            any(vertical[row][column] for row in range(source.rows))
            for column in range(source.columns - 1)
        )
    )


def _components(source: SourcePlane) -> tuple[GridRange, ...]:
    horizontal, vertical = _rule_masks(source)
    if not _eligible(source, horizontal, vertical):
        raise ValueError(
            "raw rules do not satisfy conservative ruled-table eligibility"
        )
    parent = {
        (row, column): (row, column)
        for row in range(source.rows)
        for column in range(source.columns)
    }

    def find(slot: tuple[int, int]) -> tuple[int, int]:
        while parent[slot] != slot:
            parent[slot] = parent[parent[slot]]
            slot = parent[slot]
        return slot

    def union(left: tuple[int, int], right: tuple[int, int]) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for row in range(source.rows - 1):
        for column in range(source.columns):
            if not horizontal[row][column]:
                union((row, column), (row + 1, column))
    for row in range(source.rows):
        for column in range(source.columns - 1):
            if not vertical[row][column]:
                union((row, column), (row, column + 1))
    groups: dict[tuple[int, int], set[tuple[int, int]]] = {}
    for slot in parent:
        groups.setdefault(find(slot), set()).add(slot)
    ranges = []
    for slots in groups.values():
        rows, columns = [slot[0] for slot in slots], [slot[1] for slot in slots]
        value = GridRange(min(rows), max(rows) + 1, min(columns), max(columns) + 1)
        if set(value.slots()) != slots:
            raise ValueError("raw-rule connected component is not rectangular")
        ranges.append(value)
    return tuple(sorted(ranges))


def _contains(word: SourceWord, component: GridRange, source: SourcePlane) -> bool:
    left, right = (
        source.x_edges[component.column_start],
        source.x_edges[component.column_end],
    )
    top, bottom = source.y_edges[component.row_start], source.y_edges[component.row_end]
    tolerance = source.word_tolerance_points
    return (
        word.bbox[0] >= left - tolerance
        and word.bbox[1] >= top - tolerance
        and word.bbox[2] <= right + tolerance
        and word.bbox[3] <= bottom + tolerance
    )


def _contract(source: SourcePlane, claims: ClaimPlane) -> None:
    if (
        source.case_id,
        source.document_id,
        source.source_sha256,
        source.page_number,
        source.table_key,
        source.rows,
        source.columns,
    ) != (
        claims.case_id,
        claims.document_id,
        claims.source_sha256,
        claims.page_number,
        claims.table_key,
        claims.rows,
        claims.columns,
    ):
        raise ValueError("source and claim planes have different identities or grids")


def resolve_overlay(source: SourcePlane, claims: ClaimPlane) -> OverlayResult:
    """Derive source components and overlay claims without mutation/pass ordering."""

    _contract(source, claims)
    source_hash, claim_hash = source.sha256, claims.sha256
    try:
        ranges = _components(source)
    except ValueError as exc:
        return OverlayResult(
            "blocked",
            str(exc),
            source_hash,
            claim_hash,
            claims.candidate_sha256,
            claims.candidate_sha256,
            (),
            (),
            (),
        )
    associations: list[WordAssociation] = []
    words_by_range: dict[GridRange, list[SourceWord]] = {value: [] for value in ranges}
    unresolved = False
    for word in source.words:
        options = tuple(value for value in ranges if _contains(word, value, source))
        if len(options) == 1:
            association = WordAssociation(word.word_id, "assigned", options[0], options)
            words_by_range[options[0]].append(word)
        elif not options:
            association = WordAssociation(word.word_id, "outside", None, ())
            unresolved = True
        else:
            association = WordAssociation(word.word_id, "ambiguous", None, options)
            unresolved = True
        associations.append(association)
    associations.sort(key=lambda item: item.word_id)
    claim_by_slot = {
        slot: claim for claim in claims.cells for slot in claim.range.slots()
    }
    styled = any(word.has_styled_token_boundary for word in source.words)
    conflicts: list[Conflict] = []
    projections: list[ComponentProjection] = []
    for component in ranges:
        words = tuple(sorted(words_by_range[component], key=lambda item: item.ordinal))
        word_ids, text = (
            tuple(word.word_id for word in words),
            " ".join(word.text for word in words),
        )
        overlapping = tuple(
            sorted({claim_by_slot[slot].claim_id for slot in component.slots()})
        )
        exact = [
            claim
            for claim in claims.cells
            if claim.range == component and claim.origin == "observed"
        ]
        if len(exact) == 1 and _text_key(exact[0].text) == _text_key(text):
            decision = "preserve-observed-claim"
        else:
            decision = "source-supported-projection"
            conflicts.append(
                Conflict(
                    "topology-or-payload-contradiction",
                    component,
                    overlapping,
                    word_ids,
                    "mechanical raw-rule/word component differs from extractor topology or payload",
                )
            )
        if any(word.has_styled_token_boundary for word in words):
            decision = "association-only-styled-token"
        projections.append(
            ComponentProjection(
                component,
                word_ids,
                None if styled or unresolved else text,
                overlapping,
                decision,
            )
        )
    for claim in claims.cells:
        # Diagnose physical occupancy across the claim's complete range.  This keeps
        # a valid spanning claim from looking empty merely because some atomic slots
        # within its range contain no glyphs, while still exposing p56's observed
        # one-slot ``API,`` claim over a physically empty source slot.
        claim_words = tuple(
            word.word_id
            for word in source.words
            if _contains(word, claim.range, source)
        )
        if claim.origin == "adapter_gap" and claim_words:
            conflicts.append(
                Conflict(
                    "source-words-overlap-adapter-gap",
                    claim.range,
                    (claim.claim_id,),
                    claim_words,
                    "adapter-created absence is contradicted by source occupancy",
                )
            )
        elif claim.origin == "observed" and claim.text and not claim_words:
            conflicts.append(
                Conflict(
                    "observed-payload-over-source-empty-range",
                    claim.range,
                    (claim.claim_id,),
                    (),
                    "observed origin is immutable although its payload belongs elsewhere",
                )
            )
    conflicts.sort(
        key=lambda item: (item.kind, item.range, item.claim_ids, item.word_ids)
    )
    if unresolved:
        status, reason = (
            "blocked",
            "one-or-more-source-words-cannot-be-associated-exactly-once",
        )
    elif styled:
        status, reason = (
            "blocked",
            "associations-succeed-but-styled-token-materialization-is-unsupported",
        )
    elif any(item.decision == "source-supported-projection" for item in projections):
        status, reason = (
            "proposed",
            "complete-mechanical-source-projection-differs-from-extractor-claims",
        )
    else:
        status, reason = (
            "noop",
            "extractor-topology-and-payload-match-mechanical-source-projection",
        )
    return OverlayResult(
        status,
        reason,
        source_hash,
        claim_hash,
        claims.candidate_sha256,
        claims.candidate_sha256,
        tuple(projections),
        tuple(associations),
        tuple(conflicts),
    )
