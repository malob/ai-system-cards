from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import extract_origin_projection_evidence as evidence

HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / "origin-projection-evidence.json"


class OriginProjectionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = ARTIFACT.read_bytes()
        cls.artifact = json.loads(cls.raw)
        cls.typed = {case["case_id"]: case for case in cls.artifact["typed_cases"]}

    def test_artifact_is_canonical_and_reproducible_from_live_sources(self) -> None:
        self.assertEqual(self.raw, evidence._canonical(self.artifact) + b"\n")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence.json"
            output.write_bytes(evidence._canonical(evidence.build()) + b"\n")
            self.assertEqual(output.read_bytes(), self.raw)

    def test_input_hashes_and_case_locators_are_exact(self) -> None:
        self.assertEqual(
            self.artifact["schema"],
            "ai-system-cards/origin-projection-source-evidence/v1",
        )
        for item in self.artifact["inputs"].values():
            path = evidence.ROOT / item["path"]
            self.assertEqual(evidence._sha256(path), item["sha256"])
        self.assertEqual(
            set(self.typed),
            {
                "opus-p56-t0:adapter-empty-source-supported-span",
                "opus-p56-t1:observed-source-empty-misprojected-payload",
                "opus-p56-t1:observed-populated-keep-separate",
                "opus-p56-t1:adapter-empty-with-source-words",
                "fable-p94-t0:styled-superscript-word-trap",
                "fable-p95-t0:observed-plus-adapter-source-supported-span",
            },
        )
        self.assertFalse(self.artifact["authority_boundary"]["accepted_markdown_used"])

    def test_origin_is_not_inferred_from_source_occupancy(self) -> None:
        adapter_span = self.typed["opus-p56-t0:adapter-empty-source-supported-span"]
        observed_empty = self.typed[
            "opus-p56-t1:observed-source-empty-misprojected-payload"
        ]
        self.assertEqual(adapter_span["source_occupancy"], "empty")
        self.assertEqual(observed_empty["source_occupancy"], "empty")
        self.assertTrue(
            adapter_span["extractor_claim"]["cells"][0]["adapter_generated"]
        )
        self.assertEqual(adapter_span["extractor_claim"]["cells"][0]["text"], "")
        self.assertFalse(
            observed_empty["extractor_claim"]["cells"][0]["adapter_generated"]
        )
        self.assertEqual(observed_empty["extractor_claim"]["cells"][0]["text"], "API,")
        self.assertFalse(observed_empty["boundary"]["source_rule_present"])

    def test_populated_control_and_words_in_adapter_gap_are_distinct(self) -> None:
        populated = self.typed["opus-p56-t1:observed-populated-keep-separate"]
        adapter_words = self.typed["opus-p56-t1:adapter-empty-with-source-words"]
        self.assertTrue(populated["boundary"]["source_rule_present"])
        self.assertEqual(
            " ".join(word["text"] for word in populated["source_word_refs"]),
            "API, without a system prompt",
        )
        self.assertEqual(
            populated["extractor_claim"]["cells"][0]["text"], "without a system prompt"
        )
        self.assertTrue(
            adapter_words["extractor_claim"]["cells"][0]["adapter_generated"]
        )
        self.assertEqual(adapter_words["extractor_claim"]["cells"][0]["text"], "")
        self.assertEqual(
            " ".join(word["text"] for word in adapter_words["source_word_refs"]),
            "88% (± 5%)",
        )

    def test_style_span_and_occurrence_identity_traps_are_preserved(self) -> None:
        trap = self.typed["fable-p94-t0:styled-superscript-word-trap"]
        styled = next(
            word
            for word in trap["source_word_refs"]
            if word["word_id"] == "p94:b11:l2:w0"
        )
        self.assertEqual(styled["text"], "4.610")
        spans = styled["source_features"]["style_spans"]
        self.assertEqual([span["text"] for span in spans], ["4.6", "10", " "])
        self.assertEqual([span["superscript"] for span in spans], [False, True, False])
        repeated = self.artifact["repeated_token_occurrence_control"]
        self.assertEqual(repeated["text"], "88%")
        self.assertEqual(len(set(repeated["word_ids"])), 2)
        self.assertEqual(len(set(repeated["ordinals"])), 2)

    def test_p95_span_keeps_observed_and_adapter_origins(self) -> None:
        case = self.typed["fable-p95-t0:observed-plus-adapter-source-supported-span"]
        cells = case["extractor_claim"]["cells"]
        self.assertEqual([cell["adapter_generated"] for cell in cells], [False, True])
        self.assertEqual([cell["text"] for cell in cells], ["Claude Opus 4.8", ""])
        self.assertEqual(
            [word["word_id"] for word in case["source_word_refs"]],
            ["p95:b9:l0:w0", "p95:b9:l1:w0", "p95:b9:l1:w1"],
        )
        self.assertFalse(case["boundary"]["source_rule_present"])

    def test_true_blank_is_source_only_and_fully_bounded(self) -> None:
        controls = self.artifact["source_only_controls"]
        self.assertEqual(len(controls), 1)
        control = controls[0]
        self.assertEqual(control["source_occupancy"], "empty")
        self.assertEqual(control["source_word_overlap_count"], 0)
        self.assertFalse(control["executable_typed_candidate"])
        self.assertEqual(len(control["required_horizontal_segments"]), 2)
        self.assertEqual(len(control["required_vertical_segments"]), 2)
        fixture = evidence.ROOT / control["legacy_locator"]["fixture_path"]
        self.assertEqual(
            evidence._sha256(fixture), control["legacy_locator"]["fixture_sha256"]
        )

    def test_raw_rules_derive_all_ranges_and_assign_all_words(self) -> None:
        cases = self.artifact["rule_topology_cases"]
        self.assertEqual(len(cases), 10)
        self.assertEqual(
            sum(len(case["mechanically_derived_rectangular_ranges"]) for case in cases),
            274,
        )
        self.assertEqual(
            sum(case["full_bbox_assignment"]["assigned"] for case in cases),
            790,
        )
        for case in cases:
            self.assertTrue(case["derived_matches_reviewed_range_set"])
            self.assertTrue(
                case["full_bbox_assignment"]["matches_reviewed_word_ranges"]
            )
            self.assertEqual(case["full_bbox_assignment"]["ambiguous"], 0)
            self.assertEqual(case["full_bbox_assignment"]["outside"], 0)
            self.assertTrue(case["ruled_eligibility"]["eligible"])
            self.assertTrue(
                all(case["ruled_eligibility"]["complete_outer_envelope"].values())
            )
            self.assertEqual(
                case["ruled_eligibility"][
                    "wholly_missing_internal_horizontal_boundaries"
                ],
                [],
            )
            self.assertEqual(
                case["ruled_eligibility"][
                    "wholly_missing_internal_vertical_boundaries"
                ],
                [],
            )

    def test_ruled_eligibility_fails_on_whole_boundary_and_outer_mutations(
        self,
    ) -> None:
        case = self.artifact["rule_topology_cases"][0]
        grid = case["candidate_conditioned_grid"]
        x_edges, y_edges = grid["x_edges"], grid["y_edges"]
        horizontal = case["raw_horizontal_segments"]
        vertical = case["raw_vertical_segments"]

        boundary_y = y_edges[1]
        missing_internal_h = [
            item for item in horizontal if abs(item[1] - boundary_y) > 1.25
        ]
        with self.assertRaisesRegex(
            ValueError, "wholly missing internal ruled boundary"
        ):
            evidence._ruled_masks(
                "mutated-h", x_edges, y_edges, missing_internal_h, vertical
            )

        boundary_x = x_edges[1]
        missing_internal_v = [
            item for item in vertical if abs(item[0] - boundary_x) > 1.25
        ]
        with self.assertRaisesRegex(
            ValueError, "wholly missing internal ruled boundary"
        ):
            evidence._ruled_masks(
                "mutated-v", x_edges, y_edges, horizontal, missing_internal_v
            )

        top_y = y_edges[0]
        missing_outer = [item for item in horizontal if abs(item[1] - top_y) > 1.25]
        with self.assertRaisesRegex(ValueError, "incomplete outer ruled envelope"):
            evidence._ruled_masks(
                "mutated-outer", x_edges, y_edges, missing_outer, vertical
            )

    def test_no_absent_rule_keep_separate_negative_is_claimed(self) -> None:
        self.assertFalse(self.artifact["natural_absent_rule_keep_separate_negative"])
        self.assertIn(
            "Do not generalize",
            self.artifact["natural_absent_rule_keep_separate_note"],
        )


if __name__ == "__main__":
    unittest.main()
