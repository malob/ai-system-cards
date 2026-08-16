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
    str(HERE.parent / "word-alignment"),
    str(HERE),
]

from build_replay import (
    ALIGNMENT,
    ORIGIN_EVIDENCE,
    SOURCE_WORDS,
    build_artifact,
    load_planes,
)
from origin_projection import (
    ClaimCell,
    ClaimPlane,
    GridRange,
    RuleSegment,
    SourcePlane,
    SourceWord,
    classify_bounded_slot,
    resolve_overlay,
)

ARTIFACT = HERE / "artifacts" / "origin-projection-replay.json"
SOURCE_HASH = "a" * 64
EVIDENCE_HASH = "b" * 64


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rules(rows: int, columns: int) -> tuple[RuleSegment, ...]:
    result = []
    for row in range(rows + 1):
        result.append(RuleSegment("horizontal", row * 10, 0, columns * 10))
    for column in range(columns + 1):
        result.append(RuleSegment("vertical", column * 10, 0, rows * 10))
    return tuple(result)


def _source(
    words: tuple[SourceWord, ...],
    rows: int = 1,
    columns: int = 2,
    rules: tuple[RuleSegment, ...] | None = None,
) -> SourcePlane:
    return SourcePlane(
        "synthetic",
        "synthetic",
        SOURCE_HASH,
        1,
        "p1:table-0",
        rows,
        columns,
        tuple(i * 10 for i in range(columns + 1)),
        tuple(i * 10 for i in range(rows + 1)),
        words,
        _rules(rows, columns) if rules is None else rules,
        EVIDENCE_HASH,
        EVIDENCE_HASH,
    )


def _claims(
    cells: tuple[ClaimCell, ...], rows: int = 1, columns: int = 2
) -> ClaimPlane:
    return ClaimPlane(
        "synthetic",
        "synthetic",
        SOURCE_HASH,
        1,
        "p1:table-0",
        rows,
        columns,
        "c" * 64,
        "{}",
        cells,
    )


def _word(
    word_id: str,
    ordinal: int,
    text: str,
    bbox: tuple[float, float, float, float],
    styled: bool = False,
) -> SourceWord:
    return SourceWord(
        word_id,
        ordinal,
        text,
        bbox,
        json.dumps({"numeric_superscript_candidate": styled, "style_spans": []}),
    )


def _claim(
    claim_id: str, value: GridRange, text: str, origin: str = "observed"
) -> ClaimCell:
    return ClaimCell(
        claim_id,
        value,
        text,
        origin,
        json.dumps(
            {
                "cell_id": claim_id,
                "row_range": [value.row_start, value.row_end],
                "column_range": [value.column_start, value.column_end],
                "text": text,
                "adapter_generated": origin == "adapter_gap",
                "retained": claim_id,
            }
        ),
    )


class PureResolverTests(unittest.TestCase):
    def test_source_only_bounded_blank_is_narrow_and_fail_closed(self) -> None:
        self.assertEqual(
            "true_blank", classify_bounded_slot(0, (True, True, True, True))
        )
        self.assertEqual("occupied", classify_bounded_slot(1, (True, True, True, True)))
        self.assertEqual(
            "blocked_unbounded", classify_bounded_slot(0, (True, False, True, True))
        )

    def test_repeated_equal_occurrences_remain_distinct_and_permutation_invariant(
        self,
    ) -> None:
        words = (
            _word("w-left", 1, "same", (1, 1, 4, 4)),
            _word("w-right", 2, "same", (11, 1, 14, 4)),
        )
        source = _source(words)
        claims = _claims(
            (
                _claim("left", GridRange(0, 1, 0, 1), "same"),
                _claim("right", GridRange(0, 1, 1, 2), "same"),
            )
        )
        first = resolve_overlay(source, claims)
        second = resolve_overlay(
            replace(
                source,
                words=tuple(reversed(source.words)),
                rules=tuple(reversed(source.rules)),
            ),
            replace(claims, cells=tuple(reversed(claims.cells))),
        )
        self.assertEqual("noop", first.status)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(
            {"w-left", "w-right"}, {item.word_id for item in first.associations}
        )

    def test_valid_spanning_observed_claim_is_not_reported_empty(self) -> None:
        rules = tuple(
            rule
            for rule in _rules(2, 2)
            if not (rule.orientation == "vertical" and rule.fixed == 10)
        ) + (RuleSegment("vertical", 10, 10, 20),)
        source = _source((_word("w", 1, "X", (1, 1, 4, 4)),), 2, 2, rules)
        claims = _claims(
            (
                _claim("span", GridRange(0, 1, 0, 2), "X"),
                _claim("bottom-left", GridRange(1, 2, 0, 1), ""),
                _claim("bottom-right", GridRange(1, 2, 1, 2), ""),
            ),
            2,
            2,
        )
        result = resolve_overlay(source, claims)
        self.assertEqual("noop", result.status)
        self.assertFalse(
            any(
                item.kind == "observed-payload-over-source-empty-range"
                for item in result.conflicts
            )
        )

    def test_observed_empty_and_adapter_gap_origins_remain_immutable_conflicts(
        self,
    ) -> None:
        source = _source((_word("right-word", 1, "R", (11, 1, 14, 4)),))
        claims = _claims(
            (
                _claim("observed", GridRange(0, 1, 0, 1), "R"),
                _claim("gap", GridRange(0, 1, 1, 2), "", "adapter_gap"),
            )
        )
        before = claims.to_dict()
        result = resolve_overlay(source, claims)
        self.assertEqual("proposed", result.status)
        self.assertEqual(before, claims.to_dict())
        self.assertEqual(result.input_candidate_sha256, result.output_candidate_sha256)
        kinds = {item.kind for item in result.conflicts}
        self.assertIn("observed-payload-over-source-empty-range", kinds)
        self.assertIn("source-words-overlap-adapter-gap", kinds)
        self.assertEqual("observed", claims.cells[0].origin)
        self.assertEqual("adapter_gap", claims.cells[1].origin)

    def test_styled_word_associates_but_blocks_all_materialization(self) -> None:
        source = _source((_word("styled", 1, "4.610", (1, 1, 4, 4), styled=True),))
        claims = _claims(
            (
                _claim("left", GridRange(0, 1, 0, 1), "4.6 10"),
                _claim("right", GridRange(0, 1, 1, 2), ""),
            )
        )
        result = resolve_overlay(source, claims)
        self.assertEqual("blocked", result.status)
        self.assertEqual("assigned", result.associations[0].status)
        self.assertTrue(
            all(item.materialized_text is None for item in result.components)
        )

    def test_boundary_word_and_sparse_rules_fail_closed_without_candidate_change(
        self,
    ) -> None:
        crossing = _source((_word("crossing", 1, "X", (9, 1, 11, 4)),))
        claims = _claims(
            (
                _claim("left", GridRange(0, 1, 0, 1), "X"),
                _claim("right", GridRange(0, 1, 1, 2), ""),
            )
        )
        result = resolve_overlay(crossing, claims)
        self.assertEqual("blocked", result.status)
        self.assertEqual("outside", result.associations[0].status)
        self.assertEqual(result.input_candidate_sha256, result.output_candidate_sha256)
        sparse = replace(
            crossing,
            words=(),
            rules=tuple(
                rule
                for rule in crossing.rules
                if not (rule.orientation == "horizontal" and rule.fixed == 0)
            ),
        )
        result = resolve_overlay(sparse, claims)
        self.assertEqual("blocked", result.status)
        self.assertEqual((), result.components)

    def test_nonrectangular_rule_component_blocks(self) -> None:
        rules = tuple(
            rule
            for rule in _rules(2, 2)
            if not (
                (rule.orientation == "horizontal" and rule.fixed == 10)
                or (rule.orientation == "vertical" and rule.fixed == 10)
            )
        ) + (
            RuleSegment("horizontal", 10, 10, 20),
            RuleSegment("vertical", 10, 0, 10),
        )
        source = _source((), 2, 2, rules)
        claims = _claims(
            tuple(
                _claim(
                    f"c{row}{column}", GridRange(row, row + 1, column, column + 1), ""
                )
                for row in range(2)
                for column in range(2)
            ),
            2,
            2,
        )
        result = resolve_overlay(source, claims)
        self.assertEqual("blocked", result.status)
        self.assertIn("not rectangular", result.reason)


class ArtifactReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = json.loads(ARTIFACT.read_bytes())
        cls.planes = load_planes()
        cls.source_labels = {
            case["case_id"]: case
            for case in json.loads(SOURCE_WORDS.read_bytes())["cases"]
        }
        cls.origin = json.loads(ORIGIN_EVIDENCE.read_bytes())

    def test_artifact_is_canonical_current_and_exactly_input_bound(self) -> None:
        self.assertEqual(self.artifact, build_artifact())
        self.assertEqual(
            "37bdedacdaafdf77284c07ca39d88d350c40da89cb5cdec9b8a2634df1029a88",
            _hash(ORIGIN_EVIDENCE),
        )
        for path in (SOURCE_WORDS, ALIGNMENT, ORIGIN_EVIDENCE):
            self.assertEqual(
                _hash(path), self.artifact["input_sha256"][str(path.relative_to(ROOT))]
            )

    def test_raw_rules_reproduce_all_274_reviewed_ranges_without_runtime_labels(
        self,
    ) -> None:
        total = 0
        for case_id, (source, claims) in self.planes.items():
            result = resolve_overlay(source, claims)
            actual = {tuple(item.range.to_list()) for item in result.components}
            expected = {
                tuple(item["range"])
                for item in self.source_labels[case_id]["expected_cells"]
            }
            self.assertEqual(expected, actual, case_id)
            total += len(actual)
        self.assertEqual(274, total)

    def test_all_790_words_associate_once_with_features_retained(self) -> None:
        total = 0
        for case_id, (source, claims) in self.planes.items():
            result = resolve_overlay(source, claims)
            self.assertEqual(len(source.words), len(result.associations), case_id)
            self.assertTrue(
                all(item.status == "assigned" for item in result.associations), case_id
            )
            self.assertEqual(
                {word.word_id for word in source.words},
                {item.word_id for item in result.associations},
            )
            expected_features = {
                item["word_id"]: item["source_features"]
                for item in self.source_labels[case_id]["words"]
            }
            self.assertEqual(
                expected_features,
                {word.word_id: json.loads(word.features_json) for word in source.words},
            )
            total += len(source.words)
        self.assertEqual(790, total)

    def test_exact_natural_statuses_and_candidate_immutability(self) -> None:
        expected = {
            "fable-p20-t0": "noop",
            "fable-p94-t0": "blocked",
            "fable-p95-t0": "proposed",
            "opus-p52-t0": "proposed",
            "opus-p53-t0": "proposed",
            "opus-p56-t0": "proposed",
            "opus-p56-t1": "proposed",
            "risk-p78-t0": "proposed",
            "risk-p79-t0": "noop",
            "risk-p80-t0": "noop",
        }
        for case_id, (source, claims) in self.planes.items():
            result = resolve_overlay(source, claims)
            self.assertEqual(expected[case_id], result.status)
            self.assertEqual(
                result.input_candidate_sha256, result.output_candidate_sha256
            )
        self.assertEqual(
            [
                {
                    "case_id": "risk-p115-t0:true-blank-source-only-control",
                    "classification": "true_blank",
                    "extractor_origin": "unknown-no-typed-candidate",
                    "source_sha256": "d76815f8c0bd284a33c7017d642d0734ba903ae63f7c1e6ca7778b35b2c40fa4",
                }
            ],
            self.artifact["source_only_controls"],
        )

    def test_p56_joint_resolution_p94_boundary_and_repeated_occurrences(self) -> None:
        source, claims = self.planes["opus-p56-t1"]
        result = resolve_overlay(source, claims)
        projection = {tuple(item.range.to_list()): item for item in result.components}
        self.assertEqual("Model", projection[(0, 2, 0, 1)].materialized_text)
        self.assertEqual(
            "API, without a system prompt", projection[(1, 2, 1, 2)].materialized_text
        )
        claim_by_range = {tuple(cell.range.to_list()): cell for cell in claims.cells}
        self.assertEqual("observed", claim_by_range[(1, 2, 0, 1)].origin)
        self.assertEqual("adapter_gap", claim_by_range[(4, 5, 1, 2)].origin)
        kinds = {item.kind for item in result.conflicts}
        self.assertIn("observed-payload-over-source-empty-range", kinds)
        self.assertIn("source-words-overlap-adapter-gap", kinds)
        gap = next(
            item
            for item in result.conflicts
            if item.kind == "source-words-overlap-adapter-gap"
        )
        self.assertEqual(3, len(gap.word_ids))
        repeated = self.origin["repeated_token_occurrence_control"]["word_ids"]
        self.assertEqual(
            set(repeated),
            {item.word_id for item in result.associations if item.word_id in repeated},
        )
        p94 = resolve_overlay(*self.planes["fable-p94-t0"])
        self.assertEqual("blocked", p94.status)
        self.assertTrue(all(item.status == "assigned" for item in p94.associations))
        self.assertTrue(all(item.materialized_text is None for item in p94.components))


if __name__ == "__main__":
    unittest.main()
