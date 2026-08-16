from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import extract_grid_discovery_evidence as evidence

HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "source-pages.json"
REVIEW_PATH = HERE / "review-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


class GridDiscoveryEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = json.loads(SOURCE_PATH.read_text())
        cls.review = json.loads(REVIEW_PATH.read_text())
        cls.documents = {item["source_path"]: item for item in cls.source["documents"]}

    def test_frozen_artifacts_are_exactly_reproducible(self) -> None:
        rebuilt_source = evidence.build_source()
        source_bytes = canonical(rebuilt_source)
        self.assertEqual(source_bytes, SOURCE_PATH.read_bytes())
        rebuilt_review = evidence.build_review(
            rebuilt_source, hashlib.sha256(source_bytes).hexdigest()
        )
        self.assertEqual(canonical(rebuilt_review), REVIEW_PATH.read_bytes())

    def test_hashes_bind_extractor_source_plane_and_three_archived_pdfs(self) -> None:
        self.assertEqual(
            self.source["implementation"]["sha256"], sha256(Path(evidence.__file__))
        )
        self.assertEqual(self.review["source_plane"]["sha256"], sha256(SOURCE_PATH))
        self.assertEqual(len(self.documents), 3)
        for relative_path, record in self.documents.items():
            self.assertEqual(
                record["source_sha256"], sha256(evidence.ROOT / relative_path)
            )
            self.assertEqual(record["source_id"], f"pdf-{record['source_sha256'][:16]}")

    def test_source_only_census_is_complete_and_one_to_one(self) -> None:
        expected = {
            "cards/anthropic/claude-opus-5/source.pdf": (193, 27, 17, 2_253),
            "cards/anthropic/claude-fable-5/source.pdf": (317, 40, 54, 5_617),
            "cards/anthropic/risk-report-2026-08/source.pdf": (186, 31, 6, 5_737),
        }
        for path, (pages, multi, single, words) in expected.items():
            record = self.documents[path]
            census = record["census"]
            self.assertEqual(record["page_count"], pages)
            self.assertEqual(census["raw_multi_cell_components"], multi)
            self.assertEqual(census["raw_single_cell_components"], single)
            self.assertEqual(census["pymupdf_ruled_regions"], multi)
            self.assertEqual(census["ruled_region_bbox_overlap_words"], words)

        raw_multi = [
            item
            for item in self.source["raw_enveloped_components"]
            if item["atomic_slots"] > 1
        ]
        regions = self.source["ruled_regions"]
        self.assertEqual((len(raw_multi), len(regions)), (98, 98))
        self.assertEqual(
            {item["component_id"] for item in raw_multi},
            {item["raw_stroke_crosscheck"]["component_id"] for item in regions},
        )
        self.assertTrue(
            all(
                item["raw_stroke_crosscheck"]["shape_equal"]
                and item["raw_stroke_crosscheck"]["iou"] >= 0.80
                for item in regions
            )
        )
        self.assertEqual(
            sum(item["word_ownership"]["bbox_overlap_words"] for item in regions),
            13_607,
        )
        self.assertEqual(
            sum(item["word_ownership"]["assigned_once"] for item in regions),
            13_607,
        )
        self.assertTrue(
            all(
                item["word_ownership"]["ambiguous"] == 0
                and item["word_ownership"]["outside"] == 0
                for item in regions
            )
        )

    def test_boundary_coverage_is_exhaustive_and_supports_guard(self) -> None:
        multi = [
            item
            for item in self.source["raw_enveloped_components"]
            if item["atomic_slots"] > 1
        ]
        outer = [
            boundary
            for component in multi
            for boundary in component["boundary_coverage"]["outer_boundary_slots"]
        ]
        internal = [
            boundary
            for component in multi
            for boundary in component["boundary_coverage"][
                "present_internal_boundary_slots"
            ]
        ]
        self.assertEqual(len(outer), 1_774)
        self.assertEqual(len(internal), 3_326)
        self.assertEqual(min(item["coverage_ratio"] for item in outer), 0.980769219675)
        self.assertEqual(max(item["missing_points"] for item in outer), 0.5)
        self.assertEqual(
            min(item["coverage_ratio"] for item in internal), 0.979166666667
        )
        self.assertEqual(max(item["missing_points"] for item in internal), 0.5)
        self.assertTrue(
            all(
                item["coverage_ratio"] >= 0.95 and item["missing_points"] <= 0.75
                for item in outer + internal
            )
        )

    def test_spans_and_low_axis_support_are_preserved(self) -> None:
        multi = [
            item
            for item in self.source["raw_enveloped_components"]
            if item["atomic_slots"] > 1
        ]
        self.assertEqual(sum(not item["span_bearing"] for item in multi), 73)
        self.assertEqual(sum(item["span_bearing"] for item in multi), 25)
        self.assertEqual(sum(item["present_rule_separations"] for item in multi), 3_326)
        self.assertEqual(sum(item["absent_rule_merges"] for item in multi), 143)
        self.assertEqual(
            min(item["minimum_internal_axis_support"] for item in multi),
            0.117647058824,
        )

    def test_live_observer_hashes_file_bytes_and_exposes_exact_finder_call(
        self,
    ) -> None:
        import pymupdf

        relative = "cards/anthropic/claude-opus-5/source.pdf"
        path = evidence.ROOT / relative
        with pymupdf.open(path) as document:
            bundle = evidence.observe_page(document, 16)
        record = self.documents[relative]
        self.assertEqual(bundle["source_sha256"], record["source_sha256"])
        self.assertEqual(bundle["source_id"], record["source_id"])
        self.assertEqual(bundle["source_path"], str(path.resolve()))
        self.assertEqual(
            bundle["observer"]["ruled_region_call"],
            {
                "strategy": "lines_strict",
                "use_layout": False,
                "all_other_arguments": "PyMuPDF 1.28.2 defaults",
            },
        )
        self.assertEqual(
            set(bundle["page"]),
            {"source_id", "page_1based", "width", "height", "segments", "words"},
        )
        self.assertEqual(len(bundle["finder_regions"]), 1)
        self.assertGreater(len(bundle["finder_regions"][0]["cells"]), 1)

    def test_page_payloads_are_label_free_and_segments_are_raw_l_items(self) -> None:
        forbidden = {
            "card_id",
            "case_id",
            "candidate",
            "review_label",
            "accepted_markdown",
            "legacy_html",
            "docling_bbox",
        }
        for page in self.source["pages"]:
            self.assertFalse(forbidden.intersection(page))
            segment_ids = [item["segment_id"] for item in page["segments"]]
            self.assertEqual(len(segment_ids), len(set(segment_ids)))
            self.assertTrue(all(item["item_kind"] == "l" for item in page["segments"]))
            self.assertTrue(
                all(
                    item["orientation"] in {"horizontal", "vertical"}
                    and all(
                        math.isfinite(item[key])
                        for key in ("fixed", "start", "end", "stroke_width")
                    )
                    and item["end"] > item["start"]
                    for item in page["segments"]
                )
            )
        policy = self.source["observer"]["raw_stroke_policy"]
        self.assertFalse(policy["rectangle_items_decomposed"])

    def test_natural_controls_and_semantic_claims_stay_in_review_plane(self) -> None:
        region_pages = {
            (item["source_id"], item["page_1based"])
            for item in self.source["ruled_regions"]
        }
        controls = {
            "cards/anthropic/claude-fable-5/source.pdf": (39, 40, 41, 42, 43),
            "cards/anthropic/claude-opus-5/source.pdf": (43, 85, 86, 93, 104),
            "cards/anthropic/risk-report-2026-08/source.pdf": (
                32,
                35,
                37,
                72,
                84,
                85,
                86,
                172,
            ),
        }
        for path, pages in controls.items():
            source_id = self.documents[path]["source_id"]
            self.assertTrue(
                all((source_id, page) not in region_pages for page in pages)
            )

        claims = self.review["caption_claim_controls"]
        self.assertEqual(
            sorted(item["publisher_caption_claim"] for item in claims),
            ["figure", "figure", "table"],
        )
        self.assertEqual(len(self.review["structure_tag_challenges"]), 10)
        self.assertFalse(self.review["natural_absent_rule_keep_separate"]["found"])
        self.assertFalse(
            self.review["corpus_census"]["caption_census_proves_semantic_recall"]
        )

    def test_single_separator_deletions_expose_mutation_cliffs(self) -> None:
        source_id = self.documents["cards/anthropic/claude-opus-5/source.pdf"][
            "source_id"
        ]
        page = next(
            item
            for item in self.source["pages"]
            if item["source_id"] == source_id and item["page_1based"] == 56
        )
        horizontal_deleted = [
            item
            for item in page["segments"]
            if not (
                item["orientation"] == "horizontal"
                and abs(item["fixed"] - 529.5) <= evidence.AXIS_TOLERANCE
            )
        ]
        vertical_deleted = [
            item
            for item in page["segments"]
            if not (
                item["orientation"] == "vertical"
                and abs(item["fixed"] - 360.5) <= evidence.AXIS_TOLERANCE
            )
        ]
        horizontal = evidence._raw_enveloped_components(
            source_id, 56, horizontal_deleted
        )
        vertical = evidence._raw_enveloped_components(source_id, 56, vertical_deleted)
        self.assertIn(
            (6, 3, 17),
            [(x["rows"], x["columns"], x["derived_cells"]) for x in horizontal],
        )
        self.assertIn(
            (7, 2, 13),
            [(x["rows"], x["columns"], x["derived_cells"]) for x in vertical],
        )


if __name__ == "__main__":
    unittest.main()
