from __future__ import annotations

import copy
import json
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import table_candidate as model


class Origin(Enum):
    TOPLEFT = "TOPLEFT"


class Orientation(Enum):
    ROT_90 = "rot_90"


class PydanticLikeCell:
    """Faithful public-API stand-in: attributes plus model_dump(mode='json')."""

    def __init__(self, payload: dict):
        self._payload = copy.deepcopy(payload)

    def __getattr__(self, name: str):
        try:
            return self._payload[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def model_dump(self, **_kwargs) -> dict:
        return copy.deepcopy(self._payload)


def source() -> model.SourceProvenance:
    return model.SourceProvenance(
        document_id="anthropic/synthetic",
        source_sha256="a" * 64,
        table_key="p0020-table-00",
        regions=(
            model.SourceRegion(
                page_number=20,
                bbox=model.BBox(10.0, 20.0, 210.0, 180.0, "TOPLEFT"),
                char_start=100,
                char_end=240,
            ),
        ),
    )


def tool() -> model.ToolProvenance:
    return model.ToolProvenance(
        extractor_name="docling",
        extractor_version="2.100.0",
        data_model_version="docling-core 2.80.0",
        model_artifacts=("tableformer:accurate@probe", "layout:model@probe"),
        settings_json={"table_mode": "accurate", "do_ocr": False},
    )


def cell(
    row_start: int,
    row_end: int,
    column_start: int,
    column_end: int,
    text: str,
    *,
    column_header: bool = False,
    row_header: bool = False,
    row_section: bool = False,
    fillable: bool = False,
    extra: dict | None = None,
) -> dict:
    result = {
        "bbox": {
            "l": float(column_start * 50),
            "t": float(row_start * 20),
            "r": float(column_end * 50),
            "b": float(row_end * 20),
            "coord_origin": Origin.TOPLEFT,
            "bbox_detector_note": "observed",
        },
        "row_span": row_end - row_start,
        "col_span": column_end - column_start,
        "start_row_offset_idx": row_start,
        "end_row_offset_idx": row_end,
        "start_col_offset_idx": column_start,
        "end_col_offset_idx": column_end,
        "text": text,
        "column_header": column_header,
        "row_header": row_header,
        "row_section": row_section,
        "fillable": fillable,
    }
    result.update(extra or {})
    return result


def raw_table() -> dict:
    # Deliberately omit r2c2.  The adapter must materialize and label that gap.
    return {
        "num_rows": 3,
        "num_cols": 3,
        "orientation": Orientation.ROT_90,
        "table_cells": [
            cell(
                0,
                1,
                0,
                2,
                "Mérgé α",
                column_header=True,
                extra={
                    "ref": {"cref": "#/texts/3"},
                    "future_header_guess": True,
                },
            ),
            cell(0, 1, 2, 3, "B", column_header=True, fillable=True),
            cell(1, 3, 0, 1, "Rows", row_header=True, row_section=True),
            cell(1, 2, 1, 2, "11"),
            cell(1, 2, 2, 3, "12"),
            cell(2, 3, 1, 2, "21"),
        ],
        "future_table_field": {"z": 2, "a": [3, 1]},
    }


def candidate(raw: dict | None = None) -> model.TableCandidate:
    return model.adapt_docling_table_data(
        raw_table() if raw is None else raw,
        source=source(),
        tool=tool(),
    )


class GridInvariantTests(unittest.TestCase):
    def test_adapter_builds_total_grid_and_marks_only_the_missing_slot(self):
        table = candidate()
        self.assertEqual((table.num_rows, table.num_columns), (3, 3))
        self.assertEqual(table.orientation, "rot_90")
        self.assertEqual(len(table.cells), 7)

        gaps = [cell for cell in table.cells if cell.adapter_generated]
        self.assertEqual(len(gaps), 1)
        gap = gaps[0]
        self.assertEqual(
            (gap.row_start, gap.row_end, gap.column_start, gap.column_end),
            (2, 3, 2, 3),
        )
        self.assertEqual(gap.text, "")
        self.assertIsNone(gap.bbox)

        grid = table.grid_cell_ids()
        merged_header = next(cell for cell in table.cells if cell.text == "Mérgé α")
        row_header = next(cell for cell in table.cells if cell.text == "Rows")
        self.assertEqual(grid[0][0], merged_header.cell_id)
        self.assertEqual(grid[0][1], merged_header.cell_id)
        self.assertEqual(grid[1][0], row_header.cell_id)
        self.assertEqual(grid[2][0], row_header.cell_id)
        self.assertTrue(all(slot for row in grid for slot in row))

    def test_ranges_spans_headers_bboxes_and_text_are_retained_exactly(self):
        table = candidate()
        header = next(cell for cell in table.cells if cell.text == "Mérgé α")
        self.assertEqual((header.row_start, header.row_end, header.row_span), (0, 1, 1))
        self.assertEqual(
            (header.column_start, header.column_end, header.column_span),
            (0, 2, 2),
        )
        self.assertEqual(header.header_roles, ("column_header",))
        self.assertEqual(header.source_page_number, 20)
        self.assertEqual(header.bbox.coord_origin, "TOPLEFT")
        self.assertEqual(
            json.loads(header.bbox.tool_fields_json),
            {"bbox_detector_note": "observed"},
        )

        row_header = next(cell for cell in table.cells if cell.text == "Rows")
        self.assertEqual(row_header.header_roles, ("row_header", "row_section"))
        fillable = next(cell for cell in table.cells if cell.text == "B")
        self.assertTrue(fillable.fillable)

    def test_span_mismatch_is_rejected(self):
        raw = raw_table()
        raw["table_cells"][0]["col_span"] = 1
        with self.assertRaisesRegex(ValueError, "column_span does not match"):
            candidate(raw)

    def test_overlap_is_rejected(self):
        raw = raw_table()
        raw["table_cells"].append(cell(0, 1, 0, 1, "overlap"))
        with self.assertRaisesRegex(ValueError, "overlap at row 0, column 0"):
            candidate(raw)

    def test_out_of_bounds_cell_is_rejected(self):
        raw = raw_table()
        raw["table_cells"][1] = cell(0, 1, 2, 4, "outside")
        with self.assertRaisesRegex(ValueError, "outside the table grid"):
            candidate(raw)

    def test_candidate_constructor_rejects_an_uncovered_grid(self):
        table = candidate()
        observed_only = tuple(
            cell for cell in table.cells if not cell.adapter_generated
        )
        with self.assertRaisesRegex(ValueError, "uncovered slots"):
            replace(table, cells=observed_only)

    def test_multi_region_source_requires_explicit_cell_page(self):
        multi_source = replace(
            source(),
            regions=(
                source().regions[0],
                model.SourceRegion(21, model.BBox(10, 20, 210, 180, "TOPLEFT")),
            ),
        )
        with self.assertRaisesRegex(ValueError, "multi-region"):
            model.adapt_docling_table_data(
                raw_table(), source=multi_source, tool=tool()
            )


class IdentityAndSerializationTests(unittest.TestCase):
    def test_ids_are_source_and_range_stable_not_text_or_input_order_derived(self):
        first = candidate()
        changed_raw = raw_table()
        changed_raw["table_cells"].reverse()
        changed_raw["table_cells"][-1]["text"] = "changed extraction text"
        second = candidate(changed_raw)

        self.assertEqual(first.candidate_id, second.candidate_id)
        first_by_range = {
            (
                cell.row_start,
                cell.row_end,
                cell.column_start,
                cell.column_end,
            ): cell.cell_id
            for cell in first.cells
        }
        second_by_range = {
            (
                cell.row_start,
                cell.row_end,
                cell.column_start,
                cell.column_end,
            ): cell.cell_id
            for cell in second.cells
        }
        self.assertEqual(first_by_range, second_by_range)
        self.assertNotEqual(first.to_json_bytes(), second.to_json_bytes())

    def test_serialization_is_byte_deterministic_across_mapping_and_cell_order(self):
        raw_a = raw_table()
        raw_b = copy.deepcopy(raw_a)
        raw_b["table_cells"].reverse()
        raw_b["future_table_field"] = {"a": [3, 1], "z": 2}
        raw_b["table_cells"][-1]["ref"] = {"cref": "#/texts/3"}
        raw_b["table_cells"][-1]["future_header_guess"] = True

        first = candidate(raw_a).to_json_bytes()
        second = candidate(raw_b).to_json_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertIn("Mérgé α".encode(), first)
        self.assertNotIn(b"\\u03b1", first)

        decoded = json.loads(first)
        self.assertEqual(decoded["schema_version"], model.SCHEMA_VERSION)
        self.assertEqual(decoded["grid"]["num_columns"], 3)
        self.assertEqual(decoded["tool_fields"]["future_table_field"]["a"], [3, 1])

    def test_rich_ref_and_unknown_fields_are_retained_but_not_interpreted(self):
        table = candidate()
        header = next(cell for cell in table.cells if cell.text == "Mérgé α")
        unknown = json.loads(header.tool_fields_json)
        self.assertEqual(unknown["ref"], {"cref": "#/texts/3"})
        self.assertTrue(unknown["future_header_guess"])
        self.assertEqual(header.header_roles, ("column_header",))

        diagnostic = table.diagnostic_docling_payload()
        self.assertNotIn("grid", diagnostic)
        self.assertEqual(len(diagnostic["table_cells"]), 6)
        restored_header = next(
            cell for cell in diagnostic["table_cells"] if cell["text"] == "Mérgé α"
        )
        self.assertEqual(restored_header["ref"], {"cref": "#/texts/3"})
        self.assertEqual(restored_header["col_span"], 2)
        self.assertEqual(diagnostic["future_table_field"], {"a": [3, 1], "z": 2})

    def test_rich_ref_object_and_by_alias_mapping_are_byte_identical(self):
        object_raw = raw_table()
        object_cell = object_raw["table_cells"][0]
        object_cell["ref"] = {"cref": "#/texts/3"}
        object_raw["table_cells"][0] = PydanticLikeCell(object_cell)

        alias_raw = raw_table()
        alias_raw["table_cells"][0]["ref"] = {"$ref": "#/texts/3"}

        object_candidate = candidate(object_raw)
        alias_candidate = candidate(alias_raw)
        self.assertEqual(
            object_candidate.to_json_bytes(), alias_candidate.to_json_bytes()
        )
        header = next(cell for cell in alias_candidate.cells if cell.text == "Mérgé α")
        self.assertEqual(
            json.loads(header.tool_fields_json)["ref"],
            {"cref": "#/texts/3"},
        )

    def test_disagreeing_rich_ref_aliases_fail_closed(self):
        raw = raw_table()
        raw["table_cells"][0]["ref"] = {
            "cref": "#/texts/3",
            "$ref": "#/texts/4",
        }
        with self.assertRaisesRegex(ValueError, "aliases disagree"):
            candidate(raw)

    def test_model_is_deeply_immutable_at_its_public_boundaries(self):
        table = candidate()
        self.assertIsInstance(table.cells, tuple)
        self.assertIsInstance(table.source.regions, tuple)
        with self.assertRaises(FrozenInstanceError):
            table.num_rows = 99
        with self.assertRaises(FrozenInstanceError):
            table.cells[0].text = "mutated"

    def test_non_json_tool_field_fails_closed(self):
        raw = raw_table()
        raw["opaque_runtime_object"] = object()
        with self.assertRaisesRegex(ValueError, "non-JSON value"):
            candidate(raw)

    def test_nonfinite_bbox_fails_closed(self):
        raw = raw_table()
        raw["table_cells"][0]["bbox"]["l"] = float("nan")
        with self.assertRaisesRegex(ValueError, "must be finite"):
            candidate(raw)


if __name__ == "__main__":
    unittest.main()
