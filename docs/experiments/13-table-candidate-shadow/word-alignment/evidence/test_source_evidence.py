from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ARTIFACT = HERE / "source-word-evidence.json"
EXTRACTOR = HERE / "extract_source_evidence.py"

SPEC = importlib.util.spec_from_file_location("source_evidence_extractor", EXTRACTOR)
assert SPEC and SPEC.loader
EXTRACTOR_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXTRACTOR_MODULE
SPEC.loader.exec_module(EXTRACTOR_MODULE)


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


class SourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload: dict[str, Any] = json.loads(ARTIFACT.read_text())

    def test_artifact_is_bound_to_extractor_and_sources(self) -> None:
        self.assertEqual(self.payload["implementation_sha256"], _sha256(EXTRACTOR))
        for case in self.payload["cases"]:
            source = ROOT / case["source"]["path"]
            self.assertEqual(case["source"]["sha256"], _sha256(source))

    def test_no_bbox_overlapping_source_word_is_omitted(self) -> None:
        import pymupdf

        for case in self.payload["cases"]:
            with self.subTest(case=case["case_id"]):
                document = pymupdf.open(ROOT / case["source"]["path"])
                page = document[case["source"]["page_number"] - 1]
                x_edges = case["geometry"]["x_edges"]
                y_edges = case["geometry"]["y_edges"]
                envelope = [x_edges[0], y_edges[0], x_edges[-1], y_edges[-1]]
                observed = []
                for ordinal, raw in enumerate(page.get_text("words", sort=True)):
                    x0, y0, x1, y1, text, block, line, word = raw
                    bbox = [
                        round(x0, 6),
                        round(y0, 6),
                        round(x1, 6),
                        round(y1, 6),
                    ]
                    if _overlaps(bbox, envelope):
                        observed.append(
                            {
                                "word_id": f"p{case['source']['page_number']}:b{block}:l{line}:w{word}",
                                "ordinal": ordinal,
                                "text": text,
                                "bbox": bbox,
                            }
                        )
                artifact_words = [
                    {key: item[key] for key in ("word_id", "ordinal", "text", "bbox")}
                    for item in case["words"]
                ]
                self.assertEqual(artifact_words, observed)
                self.assertEqual(case["word_census"]["included"], len(observed))
                self.assertEqual(
                    case["word_census"]["bbox_overlapping_grid"], len(observed)
                )
                self.assertEqual(case["word_census"]["omitted_bbox_overlaps"], 0)
                document.close()

    def test_assignment_and_source_features_are_total(self) -> None:
        saw_link = False
        saw_superscript = False
        saw_punctuation = False
        for case in self.payload["cases"]:
            inside = {
                item["word_id"]
                for item in case["words"]
                if item["selection_status"] == "inside-by-center"
            }
            assigned = [
                word_id
                for cell in case["expected_cells"]
                for word_id in cell["word_ids"]
            ]
            controls = {item["word_id"] for item in case["overlap_controls"]}
            self.assertEqual(inside, set(assigned))
            self.assertEqual(len(assigned), len(set(assigned)))
            self.assertFalse(inside & controls)
            self.assertEqual(
                controls,
                {
                    item["word_id"]
                    for item in case["words"]
                    if item["selection_status"] != "inside-by-center"
                },
            )
            for word in case["words"]:
                features = word["source_features"]
                self.assertEqual(
                    features["superscript"],
                    any(span["superscript"] for span in features["style_spans"]),
                )
                self.assertEqual(
                    features["numeric_superscript_candidate"],
                    features["superscript"]
                    and any(character.isdigit() for character in word["text"]),
                )
                saw_link |= bool(features["links"])
                saw_superscript |= features["superscript"]
                saw_punctuation |= bool(features["punctuation"])
        self.assertTrue(saw_link)
        self.assertTrue(saw_superscript)
        self.assertTrue(saw_punctuation)

    def test_exact_boundary_center_is_explicitly_ambiguous(self) -> None:
        status = EXTRACTOR_MODULE._selection_status(
            10.0,
            5.0,
            (0.0, 10.0, 20.0),
            (0.0, 10.0),
        )
        self.assertEqual(status, "center-on-grid-boundary")

    def test_controls_do_not_claim_a_missing_rule_negative(self) -> None:
        self.assertIsNone(self.payload["natural_missing-rule_negative"])
        controls = [
            control
            for case in self.payload["cases"]
            for control in case["topology_boundary_controls"]
        ]
        self.assertTrue(any(control["verdict"] == "span" for control in controls))
        self.assertTrue(
            any(control["verdict"] == "keep-separate" for control in controls)
        )
        for control in controls:
            if control["verdict"] == "span":
                self.assertFalse(any(control["source_rule_mask"]))
            elif control["verdict"] == "keep-separate":
                self.assertTrue(all(control["source_rule_mask"]))


if __name__ == "__main__":
    unittest.main()
