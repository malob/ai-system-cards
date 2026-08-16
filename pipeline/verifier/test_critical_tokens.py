import sys
import unittest
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import critical_tokens  # noqa: E402
import invariants  # noqa: E402
import norm  # noqa: E402


def source_page(text):
    return {
        "spans": [{
            "zone": "body",
            "line": 0,
            "text": text,
            "bbox": [0, 0, 300, 10],
            "font": "Times",
        }]
    }


class CriticalTokenTests(unittest.TestCase):
    def assert_classes(self, source, output, expected):
        self.assertEqual(
            expected,
            critical_tokens.changed_classes(source.split(), output.split()),
        )

    def test_numbers_dates_model_versions_and_percentages_are_critical(self):
        self.assert_classes("70.4%", "99.9%", ["number"])
        self.assert_classes("-5", "5", ["number"])
        self.assert_classes("2026-08-15", "2027-08-15", ["date"])
        self.assert_classes("June 2026", "July 2026", ["date"])
        self.assert_classes("May, 2026", "June, 2026", ["date"])
        self.assert_classes("May be enabled", "June be enabled", [])
        self.assert_classes("GPT-5.5", "GPT-5.6", ["number"])

    def test_negation_is_critical_at_one_token(self):
        self.assert_classes("does not comply", "does comply", ["negation"])
        self.assert_classes("none", "", ["negation"])

    def test_units_are_critical_with_numeric_context(self):
        self.assert_classes("70 mg", "70 g", ["unit"])
        self.assert_classes("48 hours", "48 days", ["unit"])
        self.assert_classes("5 million tokens", "5 million parameters", ["unit"])
        self.assert_classes("cost $5", "cost €5", ["unit"])
        self.assert_classes("cost USD 5", "cost EUR 5", ["unit"])

    def test_comparators_are_critical_and_glyph_synonyms_are_equal(self):
        self.assert_classes("at least", "at most", ["comparator"])
        self.assert_classes("under 5%", "over 5%", ["comparator"])
        self.assert_classes("x <= 5", "x > 5", ["comparator"])
        self.assert_classes("x ≤ 5", "x <= 5", [])

    def test_ambiguous_comparator_words_need_threshold_context(self):
        self.assert_classes("averaged over time", "averaged under time", [])
        self.assert_classes(
            "Model 5 averaged over all environments",
            "Model 5 averaged under all environments",
            [],
        )
        self.assert_classes("over 5 failures", "under 5 failures", ["comparator"])

    def test_projection_wrappers_and_numeric_spacing_are_not_semantic(self):
        self.assert_classes("<score>0.82</score>", "0.82", [])
        self.assert_classes("GPT-5. 5", "GPT-5.5", [])
        self.assert_classes("4.5.8.2.2.", "*4.5.8.2.2**.*", [])

    def test_same_numbers_with_card_notation_hyphen_change_are_not_critical(self):
        self.assert_classes(
            "J♦ 5♦ 4♣ CELLearly 4♣",
            "J♦ 5♦ 4♣ CELL-early 4♣",
            [],
        )

    def test_numeric_code_separator_is_not_mistaken_for_emphasis(self):
        self.assert_classes("limit 1_000", "limit 1000", ["number"])

    def test_ordinary_word_substitution_remains_noncritical(self):
        self.assert_classes("blue model", "green model", [])

    def test_ordered_local_atoms_do_not_cancel_a_swap(self):
        self.assert_classes("70 before 99", "99 before 70", ["number"])

    def test_context_recovers_split_comparator_phrase(self):
        source = "limit is at least five".split()
        output = "limit is at most five".split()
        self.assertEqual(
            ["comparator"],
            critical_tokens.opcode_classes(source, output, 3, 4, 3, 4),
        )

    def test_t1_integration_promotes_one_token_number_change(self):
        pages = [{}, source_page("The score was 70.4% today.")]
        markdown = [
            (token, 2)
            for token in norm.tokens("The score was 99.9% today.", False)
        ]

        flags = invariants.t1_text(markdown, pages, range(2, 3), set())

        self.assertEqual(1, len(flags))
        self.assertEqual("major", flags[0]["severity"])
        self.assertEqual(["number"], flags[0]["detail"]["critical_classes"])

    def test_t1_integration_promotes_deleted_negation_even_in_table_zone(self):
        pages = [{}, source_page("The model does not comply.")]
        markdown = [
            (token, 2)
            for token in norm.tokens("The model does comply.", False)
        ]

        flags = invariants.t1_text(
            markdown, pages, range(2, 3), set(), table_pages={2})

        self.assertEqual(1, len(flags))
        self.assertEqual("major", flags[0]["severity"])
        self.assertEqual(["negation"], flags[0]["detail"]["critical_classes"])
        self.assertEqual("table", flags[0]["detail"]["zone"])

    def test_t1_integration_blocks_each_supported_critical_class(self):
        cases = [
            ("The limit is under 5%.", "The limit is over 5%.", "comparator"),
            ("The run used 5 million tokens.",
             "The run used 5 million parameters.", "unit"),
            ("Published June 2026.", "Published July 2026.", "date"),
            ("The cost is $5.", "The cost is €5.", "unit"),
            ("The value is -5.", "The value is 5.", "number"),
            ("Published May, 2026.", "Published June, 2026.", "date"),
            ("The cost is USD 5.", "The cost is EUR 5.", "unit"),
        ]
        for source, output, expected in cases:
            with self.subTest(source=source, output=output):
                pages = [{}, source_page(source)]
                markdown = [
                    (token, 2) for token in norm.tokens(output, False)
                ]
                flags = invariants.t1_text(
                    markdown, pages, range(2, 3), set())
                self.assertTrue(flags)
                self.assertTrue(all(f["severity"] == "major" for f in flags))
                classes = {
                    cls for flag in flags
                    for cls in flag["detail"].get("critical_classes", [])
                }
                self.assertIn(expected, classes)


if __name__ == "__main__":
    unittest.main()
