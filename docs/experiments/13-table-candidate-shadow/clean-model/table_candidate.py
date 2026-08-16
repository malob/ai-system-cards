"""Project-owned shadow model for normalized table candidates.

This module is deliberately dependency-free and does not import production code or
Docling.  ``adapt_docling_table_data`` consumes the public, attribute-or-mapping
shape of Docling's ``TableData`` and ``TableCell`` models.

The normalized grid is total: source cells may span several slots, and uncovered
slots become explicitly marked adapter-generated cells.  Unknown Docling fields are
retained as canonical JSON for provenance and forward-diffing only.  They are never
interpreted as project semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

SCHEMA_VERSION = "table-candidate/v1"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MISSING = object()
_HEADER_ROLE_ORDER = ("column_header", "row_header", "row_section")
_HEADER_ROLES = frozenset(_HEADER_ROLE_ORDER)
_BBOX_FIELDS = frozenset(("l", "t", "r", "b", "coord_origin"))
_CELL_FIELDS = frozenset(
    (
        "bbox",
        "row_span",
        "col_span",
        "start_row_offset_idx",
        "end_row_offset_idx",
        "start_col_offset_idx",
        "end_col_offset_idx",
        "text",
        "column_header",
        "row_header",
        "row_section",
        "fillable",
    )
)
_TABLE_FIELDS = frozenset(
    ("table_cells", "num_rows", "num_cols", "orientation", "grid")
)


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{label} must be a boolean")
    return value


def _enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _json_ready(value: Any, path: str = "$.$tool_fields") -> Any:
    """Return a strict JSON value or fail instead of stringifying opaque state."""

    value = _enum_value(value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} contains a non-string object key")
            result[key] = _json_ready(child, f"{path}.{key}")
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _json_ready(child, f"{path}[{index}]") for index, child in enumerate(value)
        ]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            dumped = model_dump(mode="json", exclude_computed_fields=True)
        except TypeError:
            dumped = model_dump(mode="json")
        return _json_ready(dumped, path)
    raise ValueError(f"{path} contains non-JSON value of type {type(value).__name__}")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_ready(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _canonical_object_json(value: Any, label: str) -> str:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} must be valid JSON") from exc
    value = _json_ready(value, f"$.{label}")
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a JSON object")
    return _canonical_json(value)


def _read(value: Any, name: str, default: Any = _MISSING) -> Any:
    if isinstance(value, Mapping):
        if name in value:
            return value[name]
    elif hasattr(value, name):
        return getattr(value, name)
    if default is not _MISSING:
        return default
    raise ValueError(f"Docling value is missing required field {name!r}")


def _snapshot(value: Any) -> dict[str, Any]:
    """Best-effort public JSON snapshot used only to retain unknown fields."""

    if isinstance(value, Mapping):
        return dict(value)
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            dumped = model_dump(mode="json", exclude_computed_fields=True)
        except TypeError:
            dumped = model_dump(mode="json")
        if not isinstance(dumped, Mapping):
            raise TypeError("Docling model_dump() must return a mapping")
        return dict(dumped)
    public = getattr(value, "__dict__", None)
    if isinstance(public, Mapping):
        return {key: child for key, child in public.items() if not key.startswith("_")}
    return {}


def _unknown_fields_json(value: Any, known: frozenset[str], label: str) -> str:
    snapshot = _snapshot(value)
    unknown = {key: child for key, child in snapshot.items() if key not in known}
    return _canonical_object_json(unknown, label)


def _cell_unknown_fields_json(value: Any, label: str) -> str:
    """Retain cell extensions with a canonical RichTableCell ref spelling."""

    snapshot = _snapshot(value)
    unknown = {key: child for key, child in snapshot.items() if key not in _CELL_FIELDS}
    if "ref" not in unknown:
        return _canonical_object_json(unknown, label)

    ref = _json_ready(unknown["ref"], f"$.{label}.ref")
    if not isinstance(ref, dict):
        raise TypeError("Docling RichTableCell.ref must be a JSON object")
    has_cref = "cref" in ref
    has_alias = "$ref" in ref
    if not has_cref and not has_alias:
        raise ValueError("Docling RichTableCell.ref must contain 'cref' or '$ref'")
    if has_cref and has_alias and ref["cref"] != ref["$ref"]:
        raise ValueError("Docling RichTableCell.ref aliases disagree")
    cref = ref["cref"] if has_cref else ref["$ref"]
    if not isinstance(cref, str) or not cref:
        raise TypeError("Docling RichTableCell.ref target must be a non-empty string")

    canonical_ref = dict(ref)
    canonical_ref.pop("$ref", None)
    canonical_ref["cref"] = cref
    unknown["ref"] = canonical_ref
    return _canonical_object_json(unknown, label)


def _object_from_json(text: str) -> dict[str, Any]:
    value = json.loads(text)
    if not isinstance(value, dict):  # Constructors validate this; defensive only.
        raise TypeError("canonical object JSON stopped being an object")
    return value


@dataclass(frozen=True)
class BBox:
    """A Docling-compatible box without assuming vertical coordinate direction."""

    l: float
    t: float
    r: float
    b: float
    coord_origin: str
    tool_fields_json: str = "{}"

    def __post_init__(self) -> None:
        for name in ("l", "t", "r", "b"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"bbox.{name} must be numeric")
            if not math.isfinite(float(value)):
                raise ValueError(f"bbox.{name} must be finite")
        if self.r < self.l:
            raise ValueError("bbox.r must not be left of bbox.l")
        _require_nonempty_string(self.coord_origin, "bbox.coord_origin")
        canonical = _canonical_object_json(self.tool_fields_json, "bbox.tool_fields")
        if _BBOX_FIELDS.intersection(_object_from_json(canonical)):
            raise ValueError("bbox.tool_fields must not shadow normalized bbox fields")
        object.__setattr__(self, "tool_fields_json", canonical)

    def to_dict(self) -> dict[str, Any]:
        return {
            "l": self.l,
            "t": self.t,
            "r": self.r,
            "b": self.b,
            "coord_origin": self.coord_origin,
            "tool_fields": _object_from_json(self.tool_fields_json),
        }

    def diagnostic_docling_dict(self) -> dict[str, Any]:
        payload = _object_from_json(self.tool_fields_json)
        payload.update(
            {
                "l": self.l,
                "t": self.t,
                "r": self.r,
                "b": self.b,
                "coord_origin": self.coord_origin,
            }
        )
        return payload


def _bbox_from_docling(value: Any) -> BBox | None:
    if value is None:
        return None
    coord_origin = _enum_value(_read(value, "coord_origin"))
    coord_origin = _require_nonempty_string(coord_origin, "bbox.coord_origin")
    return BBox(
        l=_read(value, "l"),
        t=_read(value, "t"),
        r=_read(value, "r"),
        b=_read(value, "b"),
        coord_origin=coord_origin,
        tool_fields_json=_unknown_fields_json(value, _BBOX_FIELDS, "bbox.tool_fields"),
    )


@dataclass(frozen=True)
class SourceRegion:
    """Source location supplied from the containing Docling TableItem provenance."""

    page_number: int
    bbox: BBox | None
    char_start: int | None = None
    char_end: int | None = None

    def __post_init__(self) -> None:
        page_number = _require_int(self.page_number, "source page_number")
        if page_number < 1:
            raise ValueError("source page_number must be one-based and positive")
        if (self.char_start is None) != (self.char_end is None):
            raise ValueError("source char range must supply both start and end")
        if self.char_start is not None:
            start = _require_int(self.char_start, "source char_start")
            end = _require_int(self.char_end, "source char_end")
            if start < 0 or end < start:
                raise ValueError("source char range must be non-negative and half-open")

    def _sort_key(self) -> tuple[Any, ...]:
        bbox_key: tuple[Any, ...]
        if self.bbox is None:
            bbox_key = ()
        else:
            bbox_key = (
                self.bbox.l,
                self.bbox.t,
                self.bbox.r,
                self.bbox.b,
                self.bbox.coord_origin,
            )
        return (
            self.page_number,
            -1 if self.char_start is None else self.char_start,
            -1 if self.char_end is None else self.char_end,
            bbox_key,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "bbox": None if self.bbox is None else self.bbox.to_dict(),
            "char_range": (
                None if self.char_start is None else [self.char_start, self.char_end]
            ),
        }


@dataclass(frozen=True)
class SourceProvenance:
    """Stable source identity plus one or more TableItem source regions."""

    document_id: str
    source_sha256: str
    table_key: str
    regions: tuple[SourceRegion, ...]

    def __post_init__(self) -> None:
        _require_nonempty_string(self.document_id, "source document_id")
        _require_nonempty_string(self.table_key, "source table_key")
        if not isinstance(self.source_sha256, str) or not _SHA256_RE.fullmatch(
            self.source_sha256
        ):
            raise ValueError(
                "source_sha256 must be 64 lowercase hexadecimal characters"
            )
        regions = tuple(sorted(self.regions, key=SourceRegion._sort_key))
        if not regions:
            raise ValueError("source provenance requires at least one region")
        if len(set(regions)) != len(regions):
            raise ValueError("source provenance contains duplicate regions")
        object.__setattr__(self, "regions", regions)

    def identity_dict(self) -> dict[str, str]:
        """Identity deliberately excludes observed geometry and text."""

        return {
            "document_id": self.document_id,
            "source_sha256": self.source_sha256,
            "table_key": self.table_key,
        }

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = self.identity_dict()
        result["regions"] = [region.to_dict() for region in self.regions]
        return result


@dataclass(frozen=True)
class ToolProvenance:
    """Required extractor/schema identity and explicit model artifact labels."""

    extractor_name: str
    extractor_version: str
    data_model_version: str
    model_artifacts: tuple[str, ...]
    settings_json: str = "{}"

    def __post_init__(self) -> None:
        _require_nonempty_string(self.extractor_name, "tool extractor_name")
        _require_nonempty_string(self.extractor_version, "tool extractor_version")
        _require_nonempty_string(self.data_model_version, "tool data_model_version")
        artifacts = tuple(sorted(self.model_artifacts))
        if any(not isinstance(item, str) or not item for item in artifacts):
            raise ValueError("tool model_artifacts must contain non-empty strings")
        if len(set(artifacts)) != len(artifacts):
            raise ValueError("tool model_artifacts must be unique")
        object.__setattr__(self, "model_artifacts", artifacts)
        object.__setattr__(
            self,
            "settings_json",
            _canonical_object_json(self.settings_json, "tool.settings"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "extractor_name": self.extractor_name,
            "extractor_version": self.extractor_version,
            "data_model_version": self.data_model_version,
            "model_artifacts": list(self.model_artifacts),
            "settings": _object_from_json(self.settings_json),
        }


def _candidate_id(source: SourceProvenance) -> str:
    identity = {
        "schema_version": SCHEMA_VERSION,
        "source": source.identity_dict(),
    }
    digest = hashlib.sha256(_canonical_json(identity).encode("utf-8")).hexdigest()
    return f"tc_{digest}"


def _cell_id(
    candidate_id: str,
    row_start: int,
    row_end: int,
    column_start: int,
    column_end: int,
) -> str:
    return f"{candidate_id}#r{row_start}-{row_end}:c{column_start}-{column_end}"


@dataclass(frozen=True)
class TableCell:
    """One unique cell; its half-open ranges may cover several grid slots."""

    cell_id: str
    row_start: int
    row_end: int
    column_start: int
    column_end: int
    row_span: int
    column_span: int
    text: str
    bbox: BBox | None
    source_page_number: int | None
    header_roles: tuple[str, ...]
    fillable: bool
    adapter_generated: bool
    tool_fields_json: str = "{}"

    def __post_init__(self) -> None:
        _require_nonempty_string(self.cell_id, "cell_id")
        for name in (
            "row_start",
            "row_end",
            "column_start",
            "column_end",
            "row_span",
            "column_span",
        ):
            _require_int(getattr(self, name), f"cell {name}")
        if self.row_start < 0 or self.column_start < 0:
            raise ValueError("cell ranges must start at non-negative offsets")
        if self.row_end <= self.row_start or self.column_end <= self.column_start:
            raise ValueError("cell ranges must be non-empty and half-open")
        if self.row_span != self.row_end - self.row_start:
            raise ValueError("cell row_span does not match its half-open row range")
        if self.column_span != self.column_end - self.column_start:
            raise ValueError(
                "cell column_span does not match its half-open column range"
            )
        if not isinstance(self.text, str):
            raise TypeError("cell text must be a string")
        if self.source_page_number is not None:
            page = _require_int(self.source_page_number, "cell source_page_number")
            if page < 1:
                raise ValueError("cell source_page_number must be positive")
        roles = tuple(
            role for role in _HEADER_ROLE_ORDER if role in tuple(self.header_roles)
        )
        supplied_roles = tuple(self.header_roles)
        if set(supplied_roles) - _HEADER_ROLES or len(set(supplied_roles)) != len(
            supplied_roles
        ):
            raise ValueError("cell header_roles contains an unknown or duplicate role")
        object.__setattr__(self, "header_roles", roles)
        _require_bool(self.fillable, "cell fillable")
        _require_bool(self.adapter_generated, "cell adapter_generated")
        canonical = _canonical_object_json(self.tool_fields_json, "cell.tool_fields")
        if _CELL_FIELDS.intersection(_object_from_json(canonical)):
            raise ValueError("cell.tool_fields must not shadow normalized cell fields")
        object.__setattr__(self, "tool_fields_json", canonical)
        if self.adapter_generated and (
            self.row_span != 1
            or self.column_span != 1
            or self.text
            or self.bbox is not None
            or self.header_roles
            or self.fillable
            or canonical != "{}"
        ):
            raise ValueError(
                "adapter-generated cells must be empty 1x1 placeholders without semantics"
            )

    def _sort_key(self) -> tuple[Any, ...]:
        return (
            self.row_start,
            self.column_start,
            self.row_end,
            self.column_end,
            self.cell_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "row_range": [self.row_start, self.row_end],
            "column_range": [self.column_start, self.column_end],
            "row_span": self.row_span,
            "column_span": self.column_span,
            "text": self.text,
            "bbox": None if self.bbox is None else self.bbox.to_dict(),
            "source_page_number": self.source_page_number,
            "header_roles": list(self.header_roles),
            "fillable": self.fillable,
            "adapter_generated": self.adapter_generated,
            "tool_fields": _object_from_json(self.tool_fields_json),
        }

    def diagnostic_docling_dict(self) -> dict[str, Any]:
        """Return a normalized logical snapshot, not a third-party object factory."""

        if self.adapter_generated:
            raise ValueError("adapter-generated gaps are not Docling-emitted cells")
        payload = _object_from_json(self.tool_fields_json)
        payload.update(
            {
                "bbox": (
                    None if self.bbox is None else self.bbox.diagnostic_docling_dict()
                ),
                "row_span": self.row_span,
                "col_span": self.column_span,
                "start_row_offset_idx": self.row_start,
                "end_row_offset_idx": self.row_end,
                "start_col_offset_idx": self.column_start,
                "end_col_offset_idx": self.column_end,
                "text": self.text,
                "column_header": "column_header" in self.header_roles,
                "row_header": "row_header" in self.header_roles,
                "row_section": "row_section" in self.header_roles,
                "fillable": self.fillable,
            }
        )
        return payload


@dataclass(frozen=True)
class TableCandidate:
    """Immutable, total table grid with explicit source and tool provenance."""

    candidate_id: str
    source: SourceProvenance
    tool: ToolProvenance
    num_rows: int
    num_columns: int
    orientation: str
    cells: tuple[TableCell, ...]
    tool_fields_json: str = "{}"

    def __post_init__(self) -> None:
        if self.candidate_id != _candidate_id(self.source):
            raise ValueError("candidate_id does not match stable source identity")
        rows = _require_int(self.num_rows, "table num_rows")
        columns = _require_int(self.num_columns, "table num_columns")
        if rows < 1 or columns < 1:
            raise ValueError("table dimensions must both be positive")
        _require_nonempty_string(self.orientation, "table orientation")
        canonical_fields = _canonical_object_json(
            self.tool_fields_json, "table.tool_fields"
        )
        if _TABLE_FIELDS.intersection(_object_from_json(canonical_fields)):
            raise ValueError(
                "table.tool_fields must not shadow normalized table fields"
            )
        object.__setattr__(self, "tool_fields_json", canonical_fields)

        cells = tuple(sorted(self.cells, key=TableCell._sort_key))
        object.__setattr__(self, "cells", cells)
        if not cells:
            raise ValueError("table candidate must contain cells")

        source_pages = {region.page_number for region in self.source.regions}
        seen_ids = set()
        grid: list[list[str | None]] = [
            [None for _ in range(columns)] for _ in range(rows)
        ]
        for cell in cells:
            expected_id = _cell_id(
                self.candidate_id,
                cell.row_start,
                cell.row_end,
                cell.column_start,
                cell.column_end,
            )
            if cell.cell_id != expected_id:
                raise ValueError(f"cell {cell.cell_id!r} is not its stable range ID")
            if cell.cell_id in seen_ids:
                raise ValueError(f"duplicate cell ID {cell.cell_id!r}")
            seen_ids.add(cell.cell_id)
            if cell.row_end > rows or cell.column_end > columns:
                raise ValueError(f"cell {cell.cell_id!r} lies outside the table grid")
            if (
                cell.source_page_number is not None
                and cell.source_page_number not in source_pages
            ):
                raise ValueError(
                    f"cell {cell.cell_id!r} page is absent from source provenance"
                )
            for row in range(cell.row_start, cell.row_end):
                for column in range(cell.column_start, cell.column_end):
                    prior = grid[row][column]
                    if prior is not None:
                        raise ValueError(
                            f"cell overlap at row {row}, column {column}: "
                            f"{prior!r} and {cell.cell_id!r}"
                        )
                    grid[row][column] = cell.cell_id
        missing = [
            (row, column)
            for row in range(rows)
            for column in range(columns)
            if grid[row][column] is None
        ]
        if missing:
            raise ValueError(f"table grid has uncovered slots: {missing}")

    @property
    def schema_version(self) -> str:
        return SCHEMA_VERSION

    def grid_cell_ids(self) -> tuple[tuple[str, ...], ...]:
        grid: list[list[str | None]] = [
            [None for _ in range(self.num_columns)] for _ in range(self.num_rows)
        ]
        for cell in self.cells:
            for row in range(cell.row_start, cell.row_end):
                for column in range(cell.column_start, cell.column_end):
                    grid[row][column] = cell.cell_id
        return tuple(tuple(value or "" for value in row) for row in grid)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "candidate_id": self.candidate_id,
            "source": self.source.to_dict(),
            "tool": self.tool.to_dict(),
            "grid": {
                "num_rows": self.num_rows,
                "num_columns": self.num_columns,
                "orientation": self.orientation,
            },
            "cells": [cell.to_dict() for cell in self.cells],
            "tool_fields": _object_from_json(self.tool_fields_json),
        }

    def to_json(self) -> str:
        """Canonical UTF-8 JSON text with one terminating newline."""

        return _canonical_json(self.to_dict()) + "\n"

    def to_json_bytes(self) -> bytes:
        return self.to_json().encode("utf-8")

    def diagnostic_docling_payload(self) -> dict[str, Any]:
        """Normalize the retained logical payload for inspection and diffing.

        This intentionally does not promise reconstruction of a Docling Pydantic
        object.  Input ordering is canonicalized, enum values are scalarized, and
        adapter-generated gaps are omitted.
        """

        payload = _object_from_json(self.tool_fields_json)
        payload.update(
            {
                "table_cells": [
                    cell.diagnostic_docling_dict()
                    for cell in self.cells
                    if not cell.adapter_generated
                ],
                "num_rows": self.num_rows,
                "num_cols": self.num_columns,
                "orientation": self.orientation,
            }
        )
        return payload


def adapt_docling_table_data(
    data: Any,
    *,
    source: SourceProvenance,
    tool: ToolProvenance,
    default_cell_page_number: int | None = None,
) -> TableCandidate:
    """Normalize a public Docling ``TableData``-shaped value.

    ``source`` and ``tool`` are mandatory because ``TableData`` itself does not
    contain source-file identity, TableItem provenance, extractor versions, or model
    artifact identity.  A single source region supplies the cell page automatically;
    callers adapting a multi-region value must name ``default_cell_page_number``.
    """

    if not isinstance(source, SourceProvenance):
        raise TypeError("source must be a SourceProvenance")
    if not isinstance(tool, ToolProvenance):
        raise TypeError("tool must be a ToolProvenance")

    num_rows = _require_int(_read(data, "num_rows"), "Docling num_rows")
    num_columns = _require_int(_read(data, "num_cols"), "Docling num_cols")
    if num_rows < 1 or num_columns < 1:
        raise ValueError("Docling table dimensions must both be positive")
    orientation_value = _enum_value(_read(data, "orientation", "rot_0"))
    orientation = _require_nonempty_string(orientation_value, "Docling orientation")

    if default_cell_page_number is None and len(source.regions) == 1:
        default_cell_page_number = source.regions[0].page_number
    if default_cell_page_number is not None:
        default_cell_page_number = _require_int(
            default_cell_page_number, "default_cell_page_number"
        )
        source_pages = {region.page_number for region in source.regions}
        if default_cell_page_number not in source_pages:
            raise ValueError("default cell page is absent from source provenance")
    elif len(source.regions) > 1:
        raise ValueError(
            "multi-region TableData requires an explicit default_cell_page_number"
        )

    raw_cells = _read(data, "table_cells")
    if not isinstance(raw_cells, Sequence) or isinstance(
        raw_cells, (str, bytes, bytearray)
    ):
        raise TypeError("Docling table_cells must be a sequence")

    candidate_id = _candidate_id(source)
    cells = []
    occupied: list[list[str | None]] = [
        [None for _ in range(num_columns)] for _ in range(num_rows)
    ]
    for index, raw in enumerate(raw_cells):
        row_start = _require_int(
            _read(raw, "start_row_offset_idx"),
            f"Docling cell {index} start_row_offset_idx",
        )
        row_end = _require_int(
            _read(raw, "end_row_offset_idx"),
            f"Docling cell {index} end_row_offset_idx",
        )
        column_start = _require_int(
            _read(raw, "start_col_offset_idx"),
            f"Docling cell {index} start_col_offset_idx",
        )
        column_end = _require_int(
            _read(raw, "end_col_offset_idx"),
            f"Docling cell {index} end_col_offset_idx",
        )
        row_span = _require_int(
            _read(raw, "row_span", 1), f"Docling cell {index} row_span"
        )
        column_span = _require_int(
            _read(raw, "col_span", 1), f"Docling cell {index} col_span"
        )
        text = _read(raw, "text")
        if not isinstance(text, str):
            raise TypeError(f"Docling cell {index} text must be a string")

        roles = tuple(
            role
            for role, field_name in (
                ("column_header", "column_header"),
                ("row_header", "row_header"),
                ("row_section", "row_section"),
            )
            if _require_bool(
                _read(raw, field_name, False),
                f"Docling cell {index} {field_name}",
            )
        )
        fillable = _require_bool(
            _read(raw, "fillable", False), f"Docling cell {index} fillable"
        )
        cell_id = _cell_id(candidate_id, row_start, row_end, column_start, column_end)
        cell = TableCell(
            cell_id=cell_id,
            row_start=row_start,
            row_end=row_end,
            column_start=column_start,
            column_end=column_end,
            row_span=row_span,
            column_span=column_span,
            text=text,
            bbox=_bbox_from_docling(_read(raw, "bbox", None)),
            source_page_number=default_cell_page_number,
            header_roles=roles,
            fillable=fillable,
            adapter_generated=False,
            tool_fields_json=_cell_unknown_fields_json(
                raw, f"cell_{index}.tool_fields"
            ),
        )
        if cell.row_end > num_rows or cell.column_end > num_columns:
            raise ValueError(f"Docling cell {index} lies outside the table grid")
        for row in range(cell.row_start, cell.row_end):
            for column in range(cell.column_start, cell.column_end):
                prior = occupied[row][column]
                if prior is not None:
                    raise ValueError(
                        f"Docling cell overlap at row {row}, column {column}: "
                        f"{prior!r} and {cell.cell_id!r}"
                    )
                occupied[row][column] = cell.cell_id
        cells.append(cell)

    for row in range(num_rows):
        for column in range(num_columns):
            if occupied[row][column] is not None:
                continue
            gap_id = _cell_id(candidate_id, row, row + 1, column, column + 1)
            cells.append(
                TableCell(
                    cell_id=gap_id,
                    row_start=row,
                    row_end=row + 1,
                    column_start=column,
                    column_end=column + 1,
                    row_span=1,
                    column_span=1,
                    text="",
                    bbox=None,
                    source_page_number=default_cell_page_number,
                    header_roles=(),
                    fillable=False,
                    adapter_generated=True,
                )
            )

    return TableCandidate(
        candidate_id=candidate_id,
        source=source,
        tool=tool,
        num_rows=num_rows,
        num_columns=num_columns,
        orientation=orientation,
        cells=tuple(cells),
        tool_fields_json=_unknown_fields_json(data, _TABLE_FIELDS, "table.tool_fields"),
    )
