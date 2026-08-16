from __future__ import annotations

import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [
    str(HERE.parent / "clean-model"),
    str(HERE.parent / "topology-slice"),
    str(HERE),
]

import table_candidate as model
from extract_alignment_cases import load_candidate, load_reviewed_evidence
from topology_reconcile import RuleEvidence, reconcile_missing_header_rules
from word_alignment import (
    WORD_SELECTION,
    GridEvidence,
    SourceWord,
    align_words,
    reassign_cell_text,
)

SOURCE_HASH = "a" * 64


def _raw(row: int, column: int, text: str) -> dict:
    return {
        "row_span": 1,
        "col_span": 1,
        "start_row_offset_idx": row,
        "end_row_offset_idx": row + 1,
        "start_col_offset_idx": column,
        "end_col_offset_idx": column + 1,
        "text": text,
    }


def _candidate(
    cells: list[dict], rows: int = 2, columns: int = 2
) -> model.TableCandidate:
    source = model.SourceProvenance(
        "synthetic",
        SOURCE_HASH,
        "p1:table-0",
        (model.SourceRegion(1, None),),
    )
    tool = model.ToolProvenance("synthetic", "1", "1", ())
    return model.adapt_docling_table_data(
        {"num_rows": rows, "num_cols": columns, "table_cells": cells},
        source=source,
        tool=tool,
    )


def _word(
    block: int, text: str, box: tuple[float, float, float, float], ordinal: int
) -> SourceWord:
    return SourceWord(f"p1:b{block}:l0:w0", ordinal, text, box, block, 0, 0)


def _evidence(words: tuple[SourceWord, ...]) -> GridEvidence:
    return GridEvidence(
        "synthetic",
        SOURCE_HASH,
        1,
        "p1:table-0",
        (0.0, 50.0, 100.0),
        (0.0, 20.0, 40.0),
        words,
        "synthetic",
        json.dumps({"word_selection": WORD_SELECTION}),
    )


class PureAlignmentTests(unittest.TestCase):
    def test_text_only_reassignment_conserves_repeated_words_and_is_idempotent(
        self,
    ) -> None:
        candidate = _candidate(
            [
                _raw(0, 0, "right"),
                _raw(0, 1, "left"),
                _raw(1, 0, "repeat"),
                _raw(1, 1, "repeat"),
            ]
        )
        evidence = _evidence(
            (
                _word(1, "left", (5, 5, 20, 15), 10),
                _word(2, "right", (60, 5, 80, 15), 11),
                _word(3, "repeat", (5, 25, 25, 35), 12),
                _word(4, "repeat", (60, 25, 85, 35), 13),
            )
        )
        original = candidate.to_json_bytes()
        result = reassign_cell_text(candidate, evidence)
        self.assertEqual("applied", result.status)
        self.assertEqual(original, candidate.to_json_bytes())
        projections = {cell.cell_id: cell for cell in result.alignment.cells}
        grid = candidate.grid_cell_ids()
        self.assertEqual("left", projections[grid[0][0]].source_text)
        self.assertEqual("right", projections[grid[0][1]].source_text)
        self.assertEqual(2, len(result.changes))
        before = {cell.cell_id: cell for cell in candidate.cells}
        for cell in result.candidate.cells:
            prior = before[cell.cell_id].to_dict()
            after = cell.to_dict()
            prior.pop("text")
            after.pop("text")
            self.assertEqual(prior, after)
        changed_word_ids = [
            word.word_id for change in result.changes for word in change.words
        ]
        self.assertEqual(2, len(changed_word_ids))
        replay = reassign_cell_text(result.candidate, evidence)
        self.assertEqual("noop", replay.status)
        self.assertEqual(result.output_candidate_sha256, replay.output_candidate_sha256)

    def test_boundary_ambiguity_and_adapter_gap_are_all_or_nothing(self) -> None:
        ambiguous_candidate = _candidate(
            [_raw(0, 0, "left"), _raw(0, 1, "right")], 1, 2
        )
        ambiguous = _evidence(
            (
                _word(1, "left", (45, 5, 55, 15), 5),
                _word(2, "right", (60, 5, 80, 15), 6),
            )
        )
        ambiguous = replace(ambiguous, y_edges=(0.0, 20.0))
        result = reassign_cell_text(ambiguous_candidate, ambiguous)
        self.assertEqual("blocked", result.status)
        self.assertIn("ambiguous", result.reason)
        self.assertEqual(result.input_candidate_sha256, result.output_candidate_sha256)
        crossing = next(
            item
            for item in result.alignment.assignments
            if item.word_id.endswith("b1:l0:w0")
        )
        self.assertEqual("ambiguous", crossing.status)
        self.assertEqual(2, len(crossing.options))

        gap_candidate = _candidate([_raw(0, 0, "left")], 1, 2)
        gap = _evidence(
            (
                _word(1, "left", (5, 5, 20, 15), 5),
                _word(2, "right", (60, 5, 80, 15), 6),
            )
        )
        gap = replace(gap, y_edges=(0.0, 20.0))
        result = reassign_cell_text(gap_candidate, gap)
        self.assertEqual("blocked", result.status)
        self.assertIn("adapter_gap", result.reason)
        self.assertEqual(
            1,
            sum(item.status == "adapter_gap" for item in result.alignment.assignments),
        )

    def test_bbox_overlap_with_center_outside_is_explicit_and_blocks(self) -> None:
        candidate = _candidate([_raw(0, 0, "edge")], 1, 1)
        evidence = GridEvidence(
            "synthetic",
            SOURCE_HASH,
            1,
            "p1:table-0",
            (0.0, 50.0),
            (0.0, 20.0),
            (_word(1, "edge", (-10, 5, 2, 15), 5),),
            "synthetic",
            json.dumps({"word_selection": WORD_SELECTION}),
        )
        result = reassign_cell_text(candidate, evidence)
        assignment = result.alignment.assignments[0]
        self.assertEqual("outside_grid", assignment.status)
        self.assertEqual("word-center-is-outside-grid-envelope", assignment.reason)
        self.assertEqual(1, len(assignment.options))
        self.assertEqual("blocked", result.status)
        self.assertEqual(result.input_candidate_sha256, result.output_candidate_sha256)

    def test_token_inventory_and_surface_drift_fail_safe(self) -> None:
        candidate = _candidate([_raw(0, 0, "wrong")], 1, 1)
        evidence = GridEvidence(
            "synthetic",
            SOURCE_HASH,
            1,
            "p1:table-0",
            (0.0, 50.0),
            (0.0, 20.0),
            (_word(1, "right", (5, 5, 20, 15), 5),),
            "synthetic",
            json.dumps({"word_selection": WORD_SELECTION}),
        )
        result = reassign_cell_text(candidate, evidence)
        self.assertEqual("blocked", result.status)
        self.assertEqual("candidate-and-source-token-inventories-differ", result.reason)

        candidate = _candidate([_raw(0, 0, "monitor,")], 1, 1)
        evidence = replace(
            evidence,
            words=(_word(1, "monitor,\u200b", (5, 5, 20, 15), 5),),
        )
        result = reassign_cell_text(candidate, evidence)
        self.assertEqual("noop", result.status)
        self.assertEqual(candidate.to_json_bytes(), result.candidate.to_json_bytes())
        self.assertEqual(1, len(result.surface_only_cell_ids))

        evidence = replace(
            evidence,
            words=(_word(1, "mon\u200ditor,", (5, 5, 20, 15), 5),),
        )
        result = reassign_cell_text(candidate, evidence)
        self.assertEqual("blocked", result.status)
        self.assertEqual("candidate-and-source-token-inventories-differ", result.reason)
        self.assertEqual((), result.surface_only_cell_ids)

    def test_irrelevant_input_permutations_are_deterministic(self) -> None:
        raw = [_raw(0, 0, "left"), _raw(0, 1, "right")]
        first = _candidate(raw, 1, 2)
        second = _candidate(list(reversed(raw)), 1, 2)
        words = (
            _word(1, "left", (5, 5, 20, 15), 5),
            _word(2, "right", (60, 5, 80, 15), 6),
        )
        evidence_a = replace(_evidence(words), y_edges=(0.0, 20.0))
        evidence_b = replace(_evidence(tuple(reversed(words))), y_edges=(0.0, 20.0))
        self.assertEqual(first.to_json_bytes(), second.to_json_bytes())
        self.assertEqual(
            align_words(first, evidence_a).to_dict(),
            align_words(second, evidence_b).to_dict(),
        )

    def test_source_contract_and_stable_word_address_fail_closed(self) -> None:
        candidate = _candidate([_raw(0, 0, "x")], 1, 1)
        evidence = GridEvidence(
            "synthetic",
            SOURCE_HASH,
            1,
            "p1:table-0",
            (0.0, 50.0),
            (0.0, 20.0),
            (_word(1, "x", (5, 5, 20, 15), 5),),
            "synthetic",
            json.dumps({"word_selection": WORD_SELECTION}),
        )
        with self.assertRaisesRegex(ValueError, "source hash"):
            align_words(candidate, replace(evidence, source_sha256="b" * 64))
        with self.assertRaisesRegex(ValueError, "stable source address"):
            replace(evidence, words=(replace(evidence.words[0], word_id="arbitrary"),))


class SourceBoundArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = HERE / "artifacts" / "alignment-cases.json"
        cls.raw = cls.path.read_bytes()
        cls.data = json.loads(cls.raw)
        cls.cases = {item["case_id"]: item for item in cls.data["cases"]}
        cls.source_path = HERE / "evidence" / "source-word-evidence.json"
        cls.source_raw = cls.source_path.read_bytes()
        cls.source_data = json.loads(cls.source_raw)
        cls.source_cases = {item["case_id"]: item for item in cls.source_data["cases"]}

    def test_artifact_is_canonical_bound_complete_and_two_run_deterministic(
        self,
    ) -> None:
        self.assertEqual(
            json.dumps(
                self.data,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
            + b"\n",
            self.raw,
        )
        self.assertEqual(
            hashlib.sha256(self.source_raw).hexdigest(),
            self.data["source_word_evidence_sha256"],
        )
        self.assertEqual(set(self.source_cases), set(self.cases))
        self.assertEqual(10, len(self.cases))
        self.assertTrue(self.data["deterministic"])
        for case in self.cases.values():
            self.assertTrue(case["extraction_deterministic"])
            self.assertEqual(2, len(case["extraction_run_sha256"]))
            self.assertEqual(1, len(set(case["extraction_run_sha256"])))
        for relative, expected in self.data["implementation_sha256"].items():
            self.assertEqual(
                expected, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            )

    def test_minimal_evidence_is_mechanically_identical_to_independent_census(
        self,
    ) -> None:
        for case_id, case in self.cases.items():
            source = self.source_cases[case_id]
            candidate = load_candidate(case["candidate"])
            evidence, _ = load_reviewed_evidence(source, candidate)
            self.assertEqual(source["source"]["sha256"], evidence.source_sha256)
            self.assertEqual(source["source"]["page_number"], evidence.page_number)
            self.assertEqual(tuple(source["geometry"]["x_edges"]), evidence.x_edges)
            self.assertEqual(tuple(source["geometry"]["y_edges"]), evidence.y_edges)
            self.assertEqual(
                [item["word_id"] for item in source["words"]],
                [item.word_id for item in evidence.words],
            )
            self.assertEqual(case_id, case["source_evidence_case_id"])
            self.assertEqual(0, source["word_census"]["omitted_bbox_overlaps"])

    def test_every_case_replays_with_word_and_cell_conservation(self) -> None:
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                candidate = load_candidate(case["candidate"])
                evidence, _ = load_reviewed_evidence(
                    self.source_cases[case_id], candidate
                )
                alignment = align_words(candidate, evidence)
                result = reassign_cell_text(candidate, evidence)
                self.assertEqual(case["result"], result.provenance_dict())
                self.assertEqual(
                    {word.word_id for word in evidence.words},
                    {item.word_id for item in alignment.assignments},
                )
                self.assertEqual(
                    {cell.cell_id for cell in candidate.cells},
                    {item.cell_id for item in alignment.cells},
                )
                self.assertEqual(
                    len(evidence.words), sum(case["assignment_counts"].values())
                )

    def test_target_fixes_natural_noops_and_hard_blocks_are_exact(self) -> None:
        expected = {
            "opus-p52-t0": ("applied", 11),
            "opus-p53-t0": ("applied", 15),
            "opus-p56-t0": ("applied", 2),
            "opus-p56-t1": ("blocked", 0),
            "risk-p78-t0": ("applied", 15),
            "risk-p79-t0": ("noop", 0),
            "risk-p80-t0": ("noop", 0),
            "fable-p20-t0": ("noop", 0),
            "fable-p94-t0": ("blocked", 0),
            "fable-p95-t0": ("blocked", 0),
        }
        for case_id, pair in expected.items():
            case = self.cases[case_id]
            self.assertEqual(pair, (case["result"]["status"], case["change_count"]))
        self.assertEqual(1, self.cases["risk-p79-t0"]["surface_only_count"])

    def test_all_reviewed_cell_labels_agree_with_word_associations(self) -> None:
        self.assertEqual(
            274,
            sum(len(case["expected_cells"]) for case in self.source_cases.values()),
        )
        for case_id, case in self.cases.items():
            candidate = load_candidate(case["candidate"])
            evidence, _ = load_reviewed_evidence(self.source_cases[case_id], candidate)
            alignment = align_words(candidate, evidence)
            expected = {
                word_id: tuple(cell["range"])
                for cell in self.source_cases[case_id]["expected_cells"]
                for word_id in cell["word_ids"]
            }
            self.assertEqual(set(expected), {word.word_id for word in evidence.words})
            cells = {cell.cell_id: cell for cell in candidate.cells}
            for assignment in alignment.assignments:
                expected_range = expected[assignment.word_id]
                option_ids = (
                    (assignment.cell_id,)
                    if assignment.cell_id is not None
                    else tuple(item[0] for item in assignment.options)
                )
                self.assertTrue(option_ids)
                for cell_id in option_ids:
                    cell = cells[cell_id]
                    actual = (
                        cell.row_start,
                        cell.row_end,
                        cell.column_start,
                        cell.column_end,
                    )
                    self.assertGreaterEqual(actual[0], expected_range[0])
                    self.assertLessEqual(actual[1], expected_range[1])
                    self.assertGreaterEqual(actual[2], expected_range[2])
                    self.assertLessEqual(actual[3], expected_range[3])

    def _rule_evidence(
        self, case_id: str, candidate: model.TableCandidate
    ) -> RuleEvidence:
        evidence, rules = load_reviewed_evidence(self.source_cases[case_id], candidate)
        return RuleEvidence(
            evidence.source_sha256,
            evidence.page_number,
            evidence.x_edges,
            evidence.y_edges,
            rules,
            tuple(
                (
                    word.text,
                    (word.bbox[0] + word.bbox[2]) / 2,
                    (word.bbox[1] + word.bbox[3]) / 2,
                )
                for word in evidence.words
            ),
            evidence.observer,
        )

    def test_topology_composition_limits_are_explicit(self) -> None:
        p56 = self.cases["opus-p56-t1"]
        candidate = load_candidate(p56["candidate"])
        evidence, _ = load_reviewed_evidence(
            self.source_cases["opus-p56-t1"], candidate
        )
        alignment = reassign_cell_text(candidate, evidence)
        self.assertEqual("blocked", alignment.status)
        topology = reconcile_missing_header_rules(
            candidate, self._rule_evidence("opus-p56-t1", candidate)
        )
        self.assertEqual("blocked", topology.decisions[0].status)
        self.assertEqual(
            "lower-range-is-not-exact-adapter-gaps", topology.decisions[0].reason
        )

        p95 = self.cases["fable-p95-t0"]
        candidate = load_candidate(p95["candidate"])
        evidence, _ = load_reviewed_evidence(
            self.source_cases["fable-p95-t0"], candidate
        )
        raw = reassign_cell_text(candidate, evidence)
        self.assertEqual("blocked", raw.status)
        topology = reconcile_missing_header_rules(
            candidate, self._rule_evidence("fable-p95-t0", candidate)
        )
        self.assertEqual(2, sum(item.status == "merged" for item in topology.decisions))
        after = reassign_cell_text(topology.candidate, evidence)
        self.assertEqual("noop", after.status)
        self.assertEqual(topology.output_sha256, after.output_candidate_sha256)
        self.assertTrue(
            all(item.status == "assigned" for item in after.alignment.assignments)
        )
        expected = {
            word_id: tuple(cell["range"])
            for cell in self.source_cases["fable-p95-t0"]["expected_cells"]
            for word_id in cell["word_ids"]
        }
        cells = {cell.cell_id: cell for cell in topology.candidate.cells}
        for assignment in after.alignment.assignments:
            cell = cells[assignment.cell_id]
            self.assertEqual(
                expected[assignment.word_id],
                (cell.row_start, cell.row_end, cell.column_start, cell.column_end),
            )


if __name__ == "__main__":
    unittest.main()
