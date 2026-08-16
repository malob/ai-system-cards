from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import ClassVar

HERE = Path(__file__).parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import pdf_structure


def _text_leaf(
    text: str,
    bbox=(10, 10, 100, 24),
    *,
    suffix_x: float | None = None,
    char_bboxes: bool = True,
) -> dict:
    x = float(bbox[0])
    top = float(bbox[1])
    bottom = float(bbox[3])
    after_separator = False
    chars = []
    for char in text:
        if after_separator and suffix_x is not None:
            x = suffix_x
            suffix_x = None
        width = 0.0 if char == "\u200b" else 4.0
        row = {"c": char}
        if char_bboxes:
            row["bbox"] = (x, top, x + width, bottom)
        chars.append(row)
        x += width
        if char == "\u200b":
            after_separator = True
    return {
        "type": 0,
        "bbox": bbox,
        "lines": [
            {
                "spans": [
                    {"chars": chars},
                ]
            }
        ],
    }


def _node(std: str, index: int, children: list[dict], bbox=(10, 10, 100, 24)) -> dict:
    return {
        "type": 2,
        "raw": std,
        "std": std,
        "index": index,
        "bbox": bbox,
        "blocks": children,
    }


def _fixture_observation(*pages: tuple[int, dict], tree=True):
    return pdf_structure._build_observation(
        source_pdf="fixture.pdf",
        source_sha256="a" * 64,
        page_dicts=pages,
        source_pages=len(pages),
        structure_tree_present=tree,
        pymupdf_version=pdf_structure.PINNED_PYMUPDF_VERSION,
    )
class IsolatedStructureTests(unittest.TestCase):
    def test_role_index_path_merges_page_slices_and_preserves_evidence(self):
        def page(text: str, bbox) -> dict:
            item = _node("LI", 0, [_text_leaf(text, bbox)], bbox)
            listing = _node("L", 7, [item], bbox)
            return {"blocks": [_node("Document", 0, [listing], bbox)]}

        observed = _fixture_observation(
            (1, page("first", (10, 10, 100, 24))),
            (2, page("second", (10, 30, 100, 44))),
        )
        self.assertEqual(observed.status, "ok")
        self.assertEqual(observed.stats["lists"], 1)
        self.assertEqual(observed.stats["list_items"], 1)
        self.assertEqual(observed.stats["list_page_occurrences"], 2)
        self.assertEqual(observed.list_items[0].pages, (1, 2))
        listing = observed.lists[0]
        self.assertEqual(listing.pages, (1, 2))
        self.assertEqual([row.text for row in listing.evidence], ["first", "second"])
        self.assertEqual(listing.evidence[1].bbox, (10.0, 30.0, 100.0, 44.0))
        self.assertIn("Document>Document[0]/L>L[7]", listing.occurrence_id)
        self.assertNotIn(
            "structure-index-duplicate",
            {issue.code for issue in observed.issues},
        )
        self.assertEqual(json.loads(observed.to_json())["source_sha256"], "a" * 64)

    def test_identical_same_page_sibling_slots_are_rejected(self):
        first = _node("LI", 0, [_text_leaf("same")])
        second = _node("LI", 0, [_text_leaf("same")])
        listing = _node("L", 1, [first, second])
        tree = _node("Document", 0, [listing])

        observed = _fixture_observation((1, {"blocks": [tree]}))

        self.assertEqual(observed.status, "blocked")
        self.assertEqual(observed.stats["list_items"], 1)
        duplicate = [
            issue
            for issue in observed.issues
            if issue.code == "structure-index-duplicate"
        ]
        self.assertEqual(len(duplicate), 1)
        self.assertEqual(
            duplicate[0].detail,
            "duplicate child index 0 under "
            "Document>Document[0]/L>L[1] on page 1",
        )

    def test_bool_structure_index_is_rejected(self):
        item = _node("LI", True, [_text_leaf("item")])
        listing = _node("L", 1, [item])
        tree = _node("Document", 0, [listing])

        observed = _fixture_observation((1, {"blocks": [tree]}))

        self.assertEqual(observed.status, "blocked")
        self.assertIn(
            "role 'LI' has index True",
            {issue.detail for issue in observed.issues},
        )

    def test_numeric_structure_path_order_survives_twelve_siblings(self):
        items = [
            _node("LI", index, [_text_leaf(f"item {index}")])
            for index in range(12)
        ]
        first_list = _node("L", 2, items)
        second_list = _node("L", 10, [_node("LI", 0, [_text_leaf("later")])])
        tree = _node("Document", 0, [first_list, second_list])
        observed = _fixture_observation((1, {"blocks": [tree]}))

        self.assertEqual(
            [row.structure_path[-1].index for row in observed.lists],
            [2, 10],
        )
        self.assertEqual(
            [
                next(
                    row.structure_path[-1].index
                    for row in observed.list_items
                    if row.occurrence_id == item_id
                )
                for item_id in observed.lists[0].direct_item_ids
            ],
            list(range(12)),
        )
        self.assertEqual(
            [row.structure_path[-1].index for row in observed.list_items[:12]],
            list(range(12)),
        )

    def test_nested_list_ownership_and_raw_separator_observations_are_explicit(self):
        inner_item = _node(
            "LI", 0, [_text_leaf("◦\u200b inner", suffix_x=30.0)]
        )
        inner_list = _node("L", 1, [inner_item])
        outer_body = _node(
            "LBody", 0, [_text_leaf("•\u200b outer", suffix_x=30.0)]
        )
        outer_item = _node("LI", 0, [outer_body, inner_list])
        outer_list = _node("L", 4, [outer_item])
        tree = _node("Document", 0, [outer_list])
        observed = _fixture_observation((1, {"blocks": [tree]}))

        outer, inner = observed.lists
        outer_item_row = next(
            row
            for row in observed.list_items
            if row.parent_list_id == outer.occurrence_id
        )
        inner_item_row = next(
            row
            for row in observed.list_items
            if row.parent_list_id == inner.occurrence_id
        )
        self.assertIsNone(outer.parent_item_id)
        self.assertEqual(inner.parent_list_id, outer.occurrence_id)
        self.assertEqual(inner.parent_item_id, outer_item_row.occurrence_id)
        self.assertEqual(outer.evidence[0].separator_prefix, "•")
        self.assertEqual(
            outer.evidence[0].separator_suffix,
            " outer◦\u200b inner",
        )

        outer_page = outer_item_row.evidence[0]
        self.assertEqual(outer_page.text, "•\u200b outer◦\u200b inner")
        self.assertEqual(outer_page.owned_text, "•\u200b outer")
        self.assertEqual(outer_page.separator_prefix, "•")
        self.assertEqual(outer_page.separator_suffix, " outer")
        self.assertIsNotNone(outer_page.prefix_first_glyph_bbox)
        self.assertIsNotNone(outer_page.prefix_last_glyph_bbox)
        self.assertIsNotNone(outer_page.suffix_first_nonspace_glyph_bbox)
        self.assertEqual(inner_item_row.evidence[0].owned_text, "◦\u200b inner")
        self.assertEqual(inner_item_row.evidence[0].separator_prefix, "◦")
        self.assertEqual(inner_item_row.evidence[0].separator_suffix, " inner")

    def test_raw_separator_and_glyph_boxes_are_observed_without_interpretation(self):
        item = _node("LI", 0, [_text_leaf("Alpha\u200bBeta")])
        listing = _node("L", 0, [item])
        tree = _node("Document", 0, [listing])

        observed = _fixture_observation((1, {"blocks": [tree]}))

        evidence = observed.list_items[0].evidence[0]
        self.assertEqual(evidence.owned_text, "Alpha\u200bBeta")
        self.assertEqual(evidence.separator_prefix, "Alpha")
        self.assertEqual(evidence.separator_suffix, "Beta")
        self.assertEqual(evidence.prefix_first_glyph_bbox, (10.0, 10.0, 14.0, 24.0))
        self.assertEqual(evidence.prefix_last_glyph_bbox, (26.0, 10.0, 30.0, 24.0))
        self.assertEqual(
            evidence.suffix_first_nonspace_glyph_bbox,
            (30.0, 10.0, 34.0, 24.0),
        )
        serialized = json.loads(observed.to_json())["list_items"][0]["evidence"][0]
        self.assertEqual(serialized["separator_prefix"], "Alpha")
        self.assertEqual(
            serialized["suffix_first_nonspace_glyph_bbox"],
            [30.0, 10.0, 34.0, 24.0],
        )

    def test_raw_separator_survives_when_character_boxes_are_unavailable(self):
        item = _node(
            "LI", 0, [_text_leaf("Alpha\u200bBeta", char_bboxes=False)]
        )
        tree = _node("Document", 0, [_node("L", 0, [item])])

        observed = _fixture_observation((1, {"blocks": [tree]}))
        evidence = observed.list_items[0].evidence[0]

        self.assertEqual(evidence.separator_prefix, "Alpha")
        self.assertEqual(evidence.separator_suffix, "Beta")
        self.assertIsNone(evidence.prefix_first_glyph_bbox)
        self.assertIsNone(evidence.prefix_last_glyph_bbox)
        self.assertIsNone(evidence.suffix_first_nonspace_glyph_bbox)

    def test_absent_and_whitespace_only_separator_parts_are_recorded_raw(self):
        cases = (
            ("AlphaBeta", None, None, False, False),
            ("Prefix\u200b ", "Prefix", " ", True, False),
        )
        for text, prefix, suffix, has_prefix_box, has_suffix_box in cases:
            with self.subTest(text=text):
                item = _node("LI", 0, [_text_leaf(text)])
                tree = _node("Document", 0, [_node("L", 0, [item])])

                observed = _fixture_observation((1, {"blocks": [tree]}))
                evidence = observed.list_items[0].evidence[0]

                self.assertEqual(evidence.separator_prefix, prefix)
                self.assertEqual(evidence.separator_suffix, suffix)
                self.assertEqual(
                    evidence.prefix_first_glyph_bbox is not None,
                    has_prefix_box,
                )
                self.assertEqual(
                    evidence.suffix_first_nonspace_glyph_bbox is not None,
                    has_suffix_box,
                )

    def test_malformed_nested_text_leaves_block_without_partial_text(self):
        leaf_path = "blocks[0].blocks[0].blocks[0].blocks[0]"
        cases = (
            ("lines", None, f"{leaf_path}.lines is NoneType, expected list"),
            (
                "spans",
                None,
                f"{leaf_path}.lines[0].spans is NoneType, expected list",
            ),
            (
                "chars",
                None,
                f"{leaf_path}.lines[0].spans[0].chars is NoneType, expected list",
            ),
            (
                "char-value",
                7,
                (
                    f"{leaf_path}.lines[0].spans[0].chars[0].c is int, "
                    "expected one-character string"
                ),
            ),
            (
                "char-value",
                "xy",
                (
                    f"{leaf_path}.lines[0].spans[0].chars[0].c has length 2, "
                    "expected one-character string"
                ),
            ),
        )
        for shape, value, expected_detail in cases:
            with self.subTest(shape=shape, value=value):
                leaf = _text_leaf("x")
                if shape == "lines":
                    leaf["lines"] = value
                elif shape == "spans":
                    leaf["lines"][0]["spans"] = value
                elif shape == "chars":
                    leaf["lines"][0]["spans"][0]["chars"] = value
                else:
                    leaf["lines"][0]["spans"][0]["chars"][0]["c"] = value
                item = _node("LI", 0, [leaf])
                listing = _node("L", 0, [item])
                tree = _node("Document", 0, [listing])

                observed = _fixture_observation((1, {"blocks": [tree]}))

                self.assertEqual(observed.status, "blocked")
                malformed = [
                    issue
                    for issue in observed.issues
                    if issue.code == "text-character-stream-malformed"
                ]
                self.assertEqual(
                    [(issue.pages, issue.detail) for issue in malformed],
                    [((1,), expected_detail)],
                )
                self.assertEqual(observed.lists[0].evidence[0].text, "")
                item_evidence = observed.list_items[0].evidence[0]
                self.assertEqual(item_evidence.text, "")
                self.assertEqual(item_evidence.owned_text, "")
                self.assertIsNone(item_evidence.separator_prefix)
                self.assertIsNone(item_evidence.separator_suffix)

    def test_missing_or_malformed_list_structure_fails_closed(self):
        missing = _fixture_observation((1, {"blocks": []}), tree=False)
        self.assertEqual(missing.status, "blocked")
        self.assertIn("structure-tree-missing", {issue.code for issue in missing.issues})

        malformed_list = _node("L", 1, [_node("P", 0, [_text_leaf("not LI")])])
        malformed = _fixture_observation(
            (1, {"blocks": [_node("Document", 0, [malformed_list])]}),
        )
        self.assertEqual(malformed.status, "blocked")
        self.assertEqual(malformed.stats["blocking_issues"], 2)
        self.assertEqual(
            {issue.code for issue in malformed.issues},
            {"list-children-malformed", "list-without-items"},
        )

    def test_malformed_bbox_fails_closed_without_crashing(self):
        item = _node("LI", 0, [_text_leaf("item")])
        listing = _node("L", 1, [item], bbox=(10, "bad", 100, 24))
        tree = _node("Document", 0, [listing])

        observed = _fixture_observation((1, {"blocks": [tree]}))

        self.assertEqual(observed.status, "blocked")
        self.assertEqual(observed.stats["blocking_issues"], 1)
        issue = observed.issues[0]
        self.assertEqual(issue.code, "structure-bbox-malformed")
        self.assertEqual(issue.severity, "blocking")
        self.assertEqual(observed.lists[0].evidence[0].bbox, (0.0, 0.0, 0.0, 0.0))

    def test_non_dict_page_and_child_blocks_fail_closed_without_crashing(self):
        valid_item = _node("LI", 0, [_text_leaf("item")])
        listing = _node("L", 1, [valid_item, None])
        tree = _node("Document", 0, [listing, "bad child"])

        observed = _fixture_observation(
            (1, {"blocks": ["bad top-level block", tree]}),
            (2, None),
        )

        self.assertEqual(observed.status, "blocked")
        self.assertEqual(observed.stats["lists"], 1)
        self.assertEqual(observed.stats["list_items"], 1)
        self.assertEqual(
            {issue.code for issue in observed.issues},
            {
                "page-block-malformed",
                "page-rawdict-malformed",
                "structure-block-malformed",
            },
        )
        self.assertEqual(observed.list_items[0].evidence[0].owned_text, "item")


class RealPDFStructureTests(unittest.TestCase):
    EXPECTED: ClassVar = {
        "claude-fable-5": {
            "source_pages": 317,
            "tagged_pages": 317,
            "pages_with_lists": 76,
            "lists": 126,
            "list_items": 364,
            "list_page_occurrences": 147,
            "list_item_page_occurrences": 372,
            "blocking_issues": 0,
            "advisory_issues": 0,
        },
        "claude-opus-5": {
            "source_pages": 193,
            "tagged_pages": 193,
            "pages_with_lists": 43,
            "lists": 56,
            "list_items": 195,
            "list_page_occurrences": 69,
            "list_item_page_occurrences": 199,
            "blocking_issues": 0,
            "advisory_issues": 0,
        },
        "risk-report-2026-08": {
            "source_pages": 186,
            "tagged_pages": 186,
            "pages_with_lists": 80,
            "lists": 83,
            "list_items": 300,
            "list_page_occurrences": 103,
            "list_item_page_occurrences": 302,
            "blocking_issues": 0,
            "advisory_issues": 0,
        },
    }

    def test_all_archived_pdfs_have_stable_source_only_counts(self):
        for slug, expected in self.EXPECTED.items():
            with self.subTest(slug=slug):
                source = REPO / "cards" / "anthropic" / slug / "source.pdf"
                observed = pdf_structure.observe_pdf(source)
                self.assertEqual(observed.pymupdf_version, "1.28.2")
                self.assertEqual(len(observed.source_sha256), 64)
                self.assertEqual(observed.stats, expected)
                self.assertFalse(
                    any(issue.severity == "blocking" for issue in observed.issues)
                )
                self.assertTrue(all(row.evidence for row in observed.lists))


if __name__ == "__main__":
    unittest.main()
