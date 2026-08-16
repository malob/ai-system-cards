import hashlib
import unittest
from types import SimpleNamespace

import acceptance
import invariants
import mdproj
import norm


def source_page(text):
    return {
        "spans": [{
            "zone": "body",
            "line": 0,
            "text": text,
            "bbox": [0, 0, 100, 10],
            "font": "Times",
        }]
    }


class ProductionNormalizationTests(unittest.TestCase):
    def test_quote_style_drift_is_not_a_production_allowance(self):
        pages = [{}, source_page("The model said “no”.")]
        markdown = [(token, 2) for token in norm.tokens('The model said "no".', False)]

        flags = invariants.t1_text(markdown, pages, range(2, 3), set())

        self.assertTrue(flags)
        self.assertTrue(all(flag["invariant"] == "T1" for flag in flags))
        rendered = " ".join(
            flag["detail"]["missing_from_md"] + " "
            + flag["detail"]["extra_in_md"]
            for flag in flags
        )
        self.assertIn("“no”.", rendered)
        self.assertIn('"no".', rendered)

    def test_nonbreaking_hyphen_drift_is_not_a_production_allowance(self):
        pages = [{}, source_page("safety‑critical")]
        markdown = [("safety-critical", 2)]

        flags = invariants.t1_text(markdown, pages, range(2, 3), set())

        self.assertEqual(1, len(flags))
        self.assertEqual("safety‑critical", flags[0]["detail"]["missing_from_md"])
        self.assertEqual("safety-critical", flags[0]["detail"]["extra_in_md"])

    def test_nbsp_is_explicitly_ordinary_a2_whitespace(self):
        pages = [{}, source_page("high\u00a0stakes")]
        markdown = [("high", 2), ("stakes", 2)]

        flags = invariants.t1_text(markdown, pages, range(2, 3), set())

        self.assertEqual([], flags)

    def test_long_t1_acceptance_binds_text_beyond_display_sample(self):
        prefix = [f"longtoken{index:02d}" for index in range(40)]
        first = [(token, 2) for token in prefix]
        changed = list(prefix)
        changed[35] = "differenttoken35"
        second = [(token, 2) for token in changed]
        pages = [{}, source_page("")]

        first_flag = invariants.t1_text(first, pages, range(2, 3), set())[0]
        second_flag = invariants.t1_text(second, pages, range(2, 3), set())[0]

        self.assertEqual(
            first_flag["detail"]["extra_in_md"],
            second_flag["detail"]["extra_in_md"],
        )
        self.assertNotEqual(
            first_flag["detail"]["extra_sha256"],
            second_flag["detail"]["extra_sha256"],
        )
        self.assertNotEqual(
            acceptance.flag_fingerprint(first_flag),
            acceptance.flag_fingerprint(second_flag),
        )

    def test_displacement_pairing_uses_full_text_not_truncated_sample(self):
        sample = "shared " * 24
        insert = {
            "invariant": "T1", "page": 2, "severity": "major",
            "detail": {
                "op": "insert", "extra_in_md": sample[:160],
                "extra_sha256": hashlib.sha256(b"first full tail").hexdigest(),
                "extra_n_tokens": 40,
            },
        }
        delete = {
            "invariant": "T1", "page": 2, "severity": "major",
            "detail": {
                "op": "delete", "missing_from_md": sample[:160],
                "missing_sha256": hashlib.sha256(b"different full tail").hexdigest(),
                "missing_n_tokens": 40,
            },
        }

        flags = invariants.pair_displacements([insert, delete])

        self.assertEqual(2, len(flags))
        self.assertTrue(all(flag["severity"] == "major" for flag in flags))
        self.assertNotIn("displaced", {flag["detail"]["op"] for flag in flags})

    def _footnote_flags(self, source: str, markdown: str):
        pages = [{}, {
            "spans": [{"zone": "fnref", "text": "1"}],
            "footnotes": {1: source},
        }]
        section = SimpleNamespace(
            name="section.md", fn_refs=[(1, 2)], fn_defs={1: markdown})
        return invariants.fn1_footnotes(
            [section], pages, range(2, 3), set())

    def test_footnote_quote_and_hyphen_drift_is_visible_in_production(self):
        flags = self._footnote_flags(
            "A safety‑critical model said “no”.",
            'A safety-critical model said "no".',
        )

        self.assertEqual(1, len(flags))
        self.assertEqual("body-text-mismatch", flags[0]["detail"]["kind"])
        self.assertNotEqual(
            flags[0]["detail"]["oracle_sha256"],
            flags[0]["detail"]["md_sha256"],
        )

    def test_critical_footnote_number_and_negation_changes_are_major(self):
        for source, markdown, expected in (
            ("The score is 70.4%.", "The score is 99.9%.", "number"),
            ("The model does not comply.", "The model does comply.", "negation"),
        ):
            with self.subTest(source=source):
                flags = self._footnote_flags(source, markdown)
                self.assertEqual(1, len(flags))
                self.assertEqual("major", flags[0]["severity"])
                self.assertIn(
                    expected, flags[0]["detail"]["critical_classes"])

    def test_multpage_table_footnote_refs_follow_page_sentinels(self):
        markdown = (
            "<!-- source: source.pdf pages 002-003 -->\n\n"
            "<!-- p.2 -->\n<table><tr><td>A<sup>[^1]</sup></td></tr>\n"
            "<!-- p.3 -->\n<tr><td>B<sup>[^2]</sup></td></tr></table>\n"
            "[^1]: first\n\n[^2]: second\n"
        )

        section = mdproj.project("table.md", markdown)

        self.assertEqual([(1, 2), (2, 3)], section.fn_refs)


if __name__ == "__main__":
    unittest.main()
