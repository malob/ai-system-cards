"""Classes added with the seventh card (D75, claude-fable-5-2): docling's
absorbed table footnotes, literal asterisks and a typed leading hyphen in
Markdown, in-box deliberate returns, and the projection of those escapes.
Each test pairs the new behaviour with the control that must not change."""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "generate"))

import assemble  # noqa: E402
import mdproj  # noqa: E402
import serialize  # noqa: E402
import tables  # noqa: E402

HEAD = "<!-- source: source.pdf pages 001-001 -->\n\n<!-- p.1 -->\n\n"


def _tokens(body: str) -> list[str]:
    return [t for t, _ in mdproj.project("x.md", HEAD + body + "\n").tokens]


class DoclingExtrasTests(unittest.TestCase):
    def test_table_footnotes_after_the_table_are_dropped(self):
        html = ("<table><tr><td>79.5*<sup>10</sup></td></tr></table>"
                '<div class="footnote">10 We ran GPT-6 Astra …</div>')
        self.assertEqual("<table><tr><td>79.5*<sup>10</sup></td></tr></table>",
                         tables._strip_docling_extras(html))

    def test_caption_strip_and_plain_table_are_unchanged(self):
        plain = "<table><tr><td>a</td></tr></table>"
        self.assertEqual(plain, tables._strip_docling_extras(plain))
        self.assertEqual(plain, tables._strip_docling_extras(
            "<table><caption>Table 1</caption><tr><td>a</td></tr></table>"))


class LiteralAsteriskTests(unittest.TestCase):
    def test_two_flanking_asterisks_are_escaped(self):
        out = serialize._apply_marks("Bash(python3:*) and Bash(source:*)", [])
        self.assertEqual(r"Bash(python3:\*) and Bash(source:\*)", out)
        self.assertIn("Bash(python3:*)", _tokens(out))

    def test_a_lone_or_spaced_asterisk_stays_bare(self):
        for text in ("(*GPT-5.5: run by the vendor)", "10% * 0.5 * 0.2 = 1%"):
            self.assertEqual(text, serialize._apply_marks(text, []))


class TypedHyphenTests(unittest.TestCase):
    def test_leading_typed_hyphen_in_transcript_text_is_literal(self):
        out = serialize._apply_marks("- I’d like your answer", [], escape_literals=True)
        self.assertEqual(r"\- I’d like your answer", out)
        self.assertEqual(["-", "I’d", "like", "your", "answer"], _tokens(out))

    def test_mid_text_hyphen_and_prose_are_untouched(self):
        self.assertEqual("a - b", serialize._apply_marks("a - b", [], escape_literals=True))
        self.assertEqual("- prose", serialize._apply_marks("- prose", []))


def _line(text, x0, x1, y0, mono=False):
    span = {"text": text, "bbox": [x0, y0, x1, y0 + 12]}
    return {"bbox": [x0, y0, x1, y0 + 12], "segs": [(0, len(text), span)], "mono": mono}


class BoxFitBreakTests(unittest.TestCase):
    BOX = (72.0, 100.0, 540.0, 300.0)

    def _block(self, *lines, kind="turn"):
        return {"type": kind, "box": self.BOX, "lines": list(lines)}

    def test_short_line_whose_successor_word_fits_is_a_return(self):
        a = _line("- nothing else", 82, 300, 138)
        b = _line("- I’d like you to choose red", 82, 460, 152)
        self.assertTrue(assemble._box_fit_break(self._block(a, b), a, b))

    def test_full_line_wrap_and_mono_and_prose_are_not(self):
        a = _line("your overall score is how close the total frequency", 82, 521, 180)
        b = _line("across the 100 rollouts", 82, 261, 194)
        self.assertFalse(assemble._box_fit_break(self._block(a, b), a, b))
        m1, m2 = _line("curl -s x", 82, 200, 138, True), _line("[While", 82, 140, 152, True)
        self.assertFalse(assemble._box_fit_break(self._block(m1, m2), m1, m2))
        p1, p2 = _line("short", 82, 120, 138), _line("next", 82, 110, 152)
        self.assertFalse(assemble._box_fit_break(self._block(p1, p2, kind="prose"), p1, p2))

    def test_break_mark_serializes_and_projects_as_whitespace(self):
        out = serialize._apply_marks("nothing else - I’d", [("br", 12, 13, None)],
                                     escape_literals=True)
        self.assertEqual("nothing else<br>- I’d", out)
        self.assertEqual(["nothing", "else", "-", "I’d"], _tokens(out))


if __name__ == "__main__":
    unittest.main()
