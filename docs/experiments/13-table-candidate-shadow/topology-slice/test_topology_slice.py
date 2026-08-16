from __future__ import annotations

import hashlib
import json
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(HERE.parent / "clean-model"), str(HERE)]

import table_candidate as model
from topology_reconcile import RuleEvidence, reconcile_missing_header_rules

SOURCE_HASH = "a" * 64


def _raw(
    row: int, column: int, text: str, *, end: int | None = None, header: bool = False
) -> dict:
    end = column + 1 if end is None else end
    return {
        "row_span": 1,
        "col_span": end - column,
        "start_row_offset_idx": row,
        "end_row_offset_idx": row + 1,
        "start_col_offset_idx": column,
        "end_col_offset_idx": end,
        "text": text,
        "column_header": header,
    }


def _candidate(observed_lower: bool = False) -> model.TableCandidate:
    cells = [_raw(0, 0, "Header", end=2, header=True), _raw(0, 2, "H2", header=True)]
    if observed_lower:
        cells.extend((_raw(1, 0, ""), _raw(1, 1, "")))
    cells.append(_raw(1, 2, "V2"))
    source = model.SourceProvenance(
        "synthetic.pdf",
        SOURCE_HASH,
        "p1:table-0",
        (model.SourceRegion(1, None),),
    )
    tool = model.ToolProvenance("synthetic", "1", "1", ())
    return model.adapt_docling_table_data(
        {"num_rows": 2, "num_cols": 3, "table_cells": cells},
        source=source,
        tool=tool,
    )


def _evidence(
    *, full_rule: bool = False, unexpected_word: bool = False
) -> RuleEvidence:
    words = [("Header", 10.0, 10.0), ("H2", 110.0, 10.0), ("V2", 110.0, 30.0)]
    if unexpected_word:
        words.append(("extra", 10.0, 30.0))
    internal = (0.0, 20.0, 150.0) if full_rule else (100.0, 20.0, 150.0)
    return RuleEvidence(
        SOURCE_HASH,
        1,
        (0.0, 50.0, 100.0, 150.0),
        (0.0, 20.0, 40.0),
        ((0.0, 0.0, 150.0), internal, (0.0, 40.0, 150.0)),
        tuple(words),
        "synthetic",
    )


class PureTransformTests(unittest.TestCase):
    def test_colspan_header_merge_is_immutable_valid_and_idempotent(self) -> None:
        original, evidence = _candidate(), _evidence()
        original_bytes = original.to_json_bytes()
        result = reconcile_missing_header_rules(original, evidence)
        self.assertEqual(original_bytes, original.to_json_bytes())
        merged = next(cell for cell in result.candidate.cells if cell.text == "Header")
        self.assertEqual(
            (0, 2, 0, 2),
            (
                merged.row_start,
                merged.row_end,
                merged.column_start,
                merged.column_end,
            ),
        )
        self.assertEqual(("column_header",), merged.header_roles)
        self.assertEqual("merged", result.decisions[0].status)
        self.assertEqual(
            hashlib.sha256(result.candidate.to_json_bytes()).hexdigest(),
            result.output_sha256,
        )
        replay = reconcile_missing_header_rules(result.candidate, evidence)
        self.assertIs(result.candidate, replay.candidate)
        self.assertEqual((), replay.decisions)

    def test_full_rule_control_is_byte_identical(self) -> None:
        original = _candidate()
        result = reconcile_missing_header_rules(original, _evidence(full_rule=True))
        self.assertIs(original, result.candidate)
        self.assertEqual((), result.decisions)
        self.assertEqual(result.input_sha256, result.output_sha256)

    def test_fail_closed_guards_block_ambiguous_gaps(self) -> None:
        cases = (
            (
                _candidate(observed_lower=True),
                _evidence(),
                "lower-range-is-not-exact-adapter-gaps",
            ),
            (
                _candidate(),
                _evidence(unexpected_word=True),
                "extended-source-words-do-not-match-header-payload",
            ),
        )
        for candidate, evidence, reason in cases:
            with self.subTest(reason=reason):
                result = reconcile_missing_header_rules(candidate, evidence)
                self.assertIs(candidate, result.candidate)
                self.assertEqual("blocked", result.decisions[0].status)
                self.assertEqual(reason, result.decisions[0].reason)

    def test_evidence_is_frozen_content_bound_and_source_checked(self) -> None:
        evidence = _evidence()
        self.assertEqual(evidence.sha256, replace(evidence).sha256)
        with self.assertRaises(FrozenInstanceError):
            evidence.page_number = 2  # type: ignore[misc]
        with self.assertRaisesRegex(ValueError, "source hash"):
            reconcile_missing_header_rules(
                _candidate(),
                replace(evidence, source_sha256="b" * 64),
            )


class HardSetArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = HERE / "artifacts" / "hard-set.json"
        cls.raw = cls.path.read_bytes()
        cls.data = json.loads(cls.raw)
        cls.cases = {item["case_id"]: item for item in cls.data["cases"]}

    def test_artifact_is_canonical_compact_and_two_run_deterministic(self) -> None:
        self.assertLess(len(self.raw), 40_000)
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
        self.assertTrue(self.data["deterministic"])
        self.assertEqual(6, len(self.cases))
        for case in self.cases.values():
            self.assertEqual(2, len(case["run_sha256"]))
            self.assertEqual(1, len(set(case["run_sha256"])))

    def test_artifact_is_bound_to_current_implementation_files(self) -> None:
        expected = {
            "docs/experiments/13-table-candidate-shadow/clean-model/table_candidate.py",
            "docs/experiments/13-table-candidate-shadow/topology-slice/topology_reconcile.py",
            "docs/experiments/13-table-candidate-shadow/topology-slice/extract_hard_set.py",
        }
        recorded = self.data["implementation_sha256"]
        self.assertEqual(expected, set(recorded))
        for relative, expected_hash in recorded.items():
            with self.subTest(path=relative):
                self.assertEqual(
                    expected_hash,
                    hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                )

    def test_positive_blocked_and_noop_evidence_is_explicit(self) -> None:
        decisions = {
            case_id: [item for table in case["tables"] for item in table["decisions"]]
            for case_id, case in self.cases.items()
        }
        self.assertEqual(
            ["merged", "blocked"], [d["status"] for d in decisions["opus-p56"]]
        )
        self.assertEqual(
            ["merged", "merged"], [d["status"] for d in decisions["fable-p95"]]
        )
        self.assertEqual(
            "lower-range-is-not-exact-adapter-gaps",
            decisions["opus-p56"][1]["reason"],
        )
        for case_id in ("opus-p52", "risk-p78", "risk-p79", "risk-p80"):
            self.assertEqual([], decisions[case_id])
            for table in self.cases[case_id]["tables"]:
                self.assertEqual(
                    table["input_candidate_sha256"], table["output_candidate_sha256"]
                )

    def test_residual_text_assignment_scope_stays_visible(self) -> None:
        before = {
            case_id: [table["text_slots_before"]["count"] for table in case["tables"]]
            for case_id, case in self.cases.items()
        }
        self.assertEqual(
            {
                "opus-p52": [11],
                "opus-p56": [2, 11],
                "risk-p78": [15],
                "risk-p79": [0],
                "risk-p80": [0],
                "fable-p95": [2],
            },
            before,
        )
        fable = self.cases["fable-p95"]["tables"][0]
        self.assertEqual(0, fable["text_slots_after"]["count"])


if __name__ == "__main__":
    unittest.main()
