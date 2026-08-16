import json
import hashlib
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import dangling_footnotes  # noqa: E402
import f18_semantic_zoning  # noqa: E402
import invariants  # noqa: E402
import mdproj  # noqa: E402
import oracle  # noqa: E402


def project(body: str, page: int = 7):
    text = (
        f"<!-- source: source.pdf pages {page:03d}-{page:03d} -->\n\n"
        f"<!-- p.{page} -->\n\n{body}\n"
    )
    return mdproj.project("fixture.md", text)


class DanglingFootnoteTests(unittest.TestCase):
    def test_definition_without_reference_is_a_blocking_fn1_finding(self):
        section = project("Visible body.\n\n[^42]: Hidden definition body.")

        self.assertEqual(
            [{
                "invariant": "FN1",
                "page": 7,
                "severity": "major",
                "detail": {
                    "kind": "definition-without-ref",
                    "n": 42,
                    "section": "fixture.md",
                    "text": "Hidden definition body.",
                    "text_sha256": hashlib.sha256(
                        b"Hidden definition body."
                    ).hexdigest(),
                    "text_n_chars": 23,
                    "text_n_tokens": 3,
                },
            }],
            dangling_footnotes.check([section]),
        )

    def test_matching_reference_is_the_nearest_non_finding(self):
        section = project("Visible body.[^42]\n\n[^42]: Referenced definition body.")

        self.assertEqual([], dangling_footnotes.check([section]))

    def test_nearby_number_does_not_authorize_the_definition(self):
        section = project("Visible body.[^41]\n\n[^42]: Wrong-number definition body.")

        flags = dangling_footnotes.check([section])
        self.assertEqual([42], [flag["detail"]["n"] for flag in flags])

    def test_long_common_prefix_definitions_have_distinct_authority_identity(self):
        prefix = "shared definition text " * 8
        first = project(f"Visible.\n\n[^42]: {prefix}first tail")
        second = project(f"Visible.\n\n[^42]: {prefix}second tail")

        first_detail = dangling_footnotes.check([first])[0]["detail"]
        second_detail = dangling_footnotes.check([second])[0]["detail"]

        self.assertEqual(first_detail["text"], second_detail["text"])
        self.assertNotEqual(first_detail["text_sha256"], second_detail["text_sha256"])

    def test_f18_rezones_twelve_real_body_spans_but_independent_check_fires(self):
        fixture = json.loads(
            (HERE / "fixtures" / "f18-semantic-zoning.json").read_text()
        )
        self.assertEqual(12, len(fixture["relocated_spans"]))
        baseline_page, baseline_markdown = f18_semantic_zoning.build_baseline(fixture)
        baseline_section = mdproj.project("f18.md", baseline_markdown)
        blank_page = {"spans": [], "footnotes": {}}
        self.assertEqual(
            [],
            invariants.t1_text(
                baseline_section.tokens,
                [blank_page, baseline_page],
                [fixture["page"]],
                set(),
            ),
        )

        mutated_page, mutated_markdown = (
            f18_semantic_zoning.rezone_as_dangling_definition(
                baseline_page,
                baseline_markdown,
                fixture["relocated_spans"],
                fixture["footnote_number"],
            )
        )
        mutated_section = mdproj.project("f18.md", mutated_markdown)

        # The measured correlated false green: both semantic projections omit
        # the same real prose from their body streams, while legacy FN1 sees
        # matching footnote bodies and zero refs on both sides.
        self.assertNotIn("Safeguards and harmlessness", oracle.page_body_text(mutated_page))
        self.assertIn(
            "Safeguards and harmlessness", mutated_section.fn_defs[fixture["footnote_number"]]
        )
        self.assertEqual([], mutated_section.fn_refs)
        self.assertEqual(
            [],
            invariants.t1_text(
                mutated_section.tokens,
                [blank_page, mutated_page],
                [fixture["page"]],
                set(),
            ),
        )
        self.assertEqual(
            [],
            invariants.fn1_footnotes(
                [mutated_section],
                [blank_page, mutated_page],
                [fixture["page"]],
                set(),
            ),
        )

        flags = dangling_footnotes.check([mutated_section])
        self.assertEqual(1, len(flags))
        self.assertEqual("major", flags[0]["severity"])
        self.assertEqual("definition-without-ref", flags[0]["detail"]["kind"])
        self.assertEqual(99, flags[0]["detail"]["n"])


if __name__ == "__main__":
    unittest.main()
