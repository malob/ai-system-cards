import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATE = ROOT / "pipeline" / "generate"
sys.path.insert(0, str(GENERATE))

SPEC = importlib.util.spec_from_file_location("generate_run", GENERATE / "run.py")
generate_run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_run)


class GenerateHandoffTests(unittest.TestCase):
    def test_full_generation_handoff_preserves_card_and_runs_full_gate(self):
        command = generate_run.verifier_command(full=True, section_prefixes=["00", "01"])
        self.assertIn(f"CARD={generate_run.cardcfg.CARD_ID}", command)
        self.assertTrue(command.endswith("calibrate.py WORKTREE"))
        self.assertNotIn("--sections", command)

    def test_partial_generation_handoff_keeps_section_scope(self):
        command = generate_run.verifier_command(full=False, section_prefixes=["02a", "02b"])
        self.assertIn(str(generate_run.OUT), command)
        self.assertIn("--sections 02a 02b", command)


class DestinationResolutionTests(unittest.TestCase):
    @staticmethod
    def resolve(md, *, anchor="heading-from-geometry", text_resolution=None):
        return generate_run.resolve_destination_placeholders(
            md,
            anchor_for=lambda _page, _y: anchor,
            text_resolution=text_resolution or (lambda _text: None),
            pooled={},
        )

    def test_broken_page_zero_destination_becomes_prose_not_empty_fragment(self):
        self.assertEqual(
            self.resolve("Read [the discussion](DEST:0:-1) next."),
            "Read the discussion next.",
        )
        self.assertEqual(
            self.resolve('<a href="DEST:0:-1"><em>See discussion</em></a>'),
            "<em>See discussion</em>",
        )

    def test_page_zero_unique_numeric_heading_is_recovered(self):
        def unique_heading(text):
            return "6-5-4-3-stealthiness" if text.strip() == "6.5.4.3" else None

        self.assertEqual(
            self.resolve("[6.5.4.3](DEST:0:-1)", text_resolution=unique_heading),
            "[6.5.4.3](#6-5-4-3-stealthiness)",
        )

    def test_nested_markdown_placeholder_fails_closed(self):
        with self.assertRaisesRegex(
                generate_run.DestinationResolutionError,
                "unresolved destination placeholder"):
            self.resolve("[outer [inner]](DEST:0:-1)")

    def test_unrecognized_raw_html_placeholder_fails_closed(self):
        with self.assertRaisesRegex(
                generate_run.DestinationResolutionError,
                "unresolved destination placeholder"):
            self.resolve('<a class="xref" href="DEST:0:-1">discussion</a>')

    def test_nonzero_destination_without_any_heading_fails_closed(self):
        with self.assertRaisesRegex(
                generate_run.DestinationResolutionError,
                "page 42 has no heading anchor"):
            self.resolve("[target](DEST:42:100)", anchor="")

    def test_ordinary_markdown_and_table_html_resolution_is_unchanged(self):
        source = (
            "[ordinary link](DEST:42:100)\n"
            '<a href="DEST:42:100"><em>table link</em></a>'
        )
        self.assertEqual(
            self.resolve(source),
            "[ordinary link](#heading-from-geometry)\n"
            '<a href="#heading-from-geometry"><em>table link</em></a>',
        )


if __name__ == "__main__":
    unittest.main()
