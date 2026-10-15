"""Verifier classes added for the first non-Anthropic template (D70/D71,
gemini-4-argon): a footer page number above the 42pt band, adjacent footnote
references in one superscript span, relocated footnote links with a repeated
label, literal '<' / '|' in the Markdown projection, and hyphen list markers.
Each test pairs the new behaviour with the control that must not change."""

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import l2_links  # noqa: E402
import mdproj  # noqa: E402
import oracle  # noqa: E402
import raw_footnotes  # noqa: E402


def _footnoted_pdf(path: Path, *, ref: str, defs: list[str], page_number_y: float) -> None:
    """One page: a body sentence carrying superscript ``ref``, footnote
    definitions at the bottom (6pt marker + 10pt body under a 144pt rule),
    and a bare page number at ``page_number_y`` (baseline)."""
    document = raw_footnotes.fitz.open()
    page = document.new_page(width=612, height=792)   # US Letter, as the corpus
    page.insert_htmlbox(
        raw_footnotes.fitz.Rect(72, 72, 500, 160),
        f'<p style="font-size:11pt">Bench<sup>{ref}</sup> tail of the body sentence</p>',
    )
    page.draw_line((72, 640), (216, 640), color=(0, 0, 0), width=0.5)
    y = 660.0
    for number in defs:
        page.insert_text((72, y), number, fontsize=6)
        page.insert_text((78, y), f"note body {number}", fontsize=10)
        y += 14
    page.insert_text((530, page_number_y), "5", fontsize=11)
    document.save(path)
    document.close()


class FooterAndAdjacentRefTests(unittest.TestCase):
    def test_page_number_above_the_band_is_footer_when_it_is_the_lowest_line(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.pdf"
            # baseline 740: bbox bottom ~743, above the 42pt band (750) but
            # inside the 1in margin — gemini-4-argon's footer geometry
            _footnoted_pdf(source, ref="1", defs=["1"], page_number_y=740)
            observation = raw_footnotes.observe(source)
            self.assertEqual([1], [d.number for d in observation.definitions])
            self.assertEqual("note body 1", observation.definitions[0].text)

    def test_adjacent_superscripts_split_only_when_both_halves_are_defined(self):
        with tempfile.TemporaryDirectory() as directory:
            split = Path(directory) / "split.pdf"
            _footnoted_pdf(split, ref="78", defs=["7", "8"], page_number_y=770)
            observation = raw_footnotes.observe(split)
            self.assertEqual([7, 8], [r.number for r in observation.references])

            whole = Path(directory) / "whole.pdf"
            _footnoted_pdf(whole, ref="78", defs=["78"], page_number_y=770)
            observation = raw_footnotes.observe(whole)
            self.assertEqual([78], [r.number for r in observation.references])


def _continued_note_pdf(path: Path, *, separator_on_page_2: bool) -> None:
    """Note 1 starts at the bottom of page 1 and its tail sits alone at the
    bottom of page 2 — under a 2in rule when ``separator_on_page_2``."""
    document = raw_footnotes.fitz.open()
    for number in (1, 2):
        page = document.new_page(width=612, height=792)
        page.insert_htmlbox(
            raw_footnotes.fitz.Rect(72, 72, 500, 160),
            '<p style="font-size:11pt">Body<sup>1</sup> sentence on the page</p>'
            if number == 1 else
            '<p style="font-size:11pt">Second page body sentence here</p>')
        if number == 1 or separator_on_page_2:
            page.draw_line((72, 640), (216, 640), color=(0, 0, 0), width=0.5)
        if number == 1:
            page.insert_text((72, 660), "1", fontsize=6)
            page.insert_text((78, 660), "first part of the note", fontsize=10)
        else:
            page.insert_text((72, 660), "tail of the note", fontsize=10)
        page.insert_text((530, 770), str(number), fontsize=11)
    document.save(path)
    document.close()


class SeparatorContinuationTests(unittest.TestCase):
    def test_tail_alone_under_the_separator_continues_the_previous_note(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.pdf"
            _continued_note_pdf(source, separator_on_page_2=True)
            (definition,) = raw_footnotes.observe(source).definitions
            self.assertEqual("first part of the note tail of the note", definition.text)
            self.assertEqual(2, definition.end_page)

    def test_without_a_separator_the_tail_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.pdf"
            _continued_note_pdf(source, separator_on_page_2=False)
            (definition,) = raw_footnotes.observe(source).definitions
            self.assertEqual("first part of the note", definition.text)


class RelocatedFootnoteLinkTests(unittest.TestCase):
    def test_repeated_label_pairs_through_each_footnote_reference_page(self):
        text = (
            "<!-- source: source.pdf pages 020-024 -->\n\n"
            "<!-- p.20 -->\n\nFirst claim.[^2]\n\n"
            "<!-- p.22 -->\n\nSecond claim.[^3]\n\n"
            "<!-- p.24 -->\n\nLast page.\n\n"
            "[^2]: See [Section 3.7](#37-checkpoints) for checkpoints.\n\n"
            "[^3]: See [Section 3.7](#37-checkpoints) again.\n"
        )
        parsed = l2_links.parse_markdown([("03a.md", text)])
        self.assertEqual([20, 22], [link.footnote_page for link in parsed.links])
        outputs = l2_links.group_output_occurrences(parsed.links)

        def source(page):
            return l2_links.SourceLink(
                f"src{page}", page, "Section 3.7", (f"a{page}",), 161, 80.0, "",
                False, ((72, 690, 130, 700),))

        pairs, notes = l2_links.pair_links([source(22), source(20)], outputs)
        # source 0 (p.22) ↔ output 1 (fn 3), source 1 (p.20) ↔ output 0 (fn 2)
        self.assertEqual({0: 1, 1: 0}, pairs)
        self.assertEqual({"relocated-footnote-reference-page"}, {n["kind"] for n in notes})

    def test_unique_label_keeps_the_original_relocation_rule(self):
        text = (
            "<!-- source: source.pdf pages 020-021 -->\n\n"
            "<!-- p.20 -->\n\nClaim.[^2]\n\n<!-- p.21 -->\n\nMore.\n\n"
            "[^2]: See [Section 3.7](#37-checkpoints).\n"
        )
        outputs = l2_links.group_output_occurrences(
            l2_links.parse_markdown([("03a.md", text)]).links)
        src = l2_links.SourceLink("s", 20, "Section 3.7", ("a",), 161, 80.0, "",
                                  False, ((72, 690, 130, 700),))
        pairs, notes = l2_links.pair_links([src], outputs)
        self.assertEqual({0: 0}, pairs)
        self.assertEqual(["relocated-footnote"], [n["kind"] for n in notes])


class ProjectionLiteralTests(unittest.TestCase):
    def test_literal_angle_brackets_and_pipes_survive_projection(self):
        text = (
            "<!-- source: source.pdf pages 001-001 -->\n\n<!-- p.1 -->\n\n"
            "its `<thought>` blocks and \\<answer> tags\n\n"
            "<table><tr><td>history -c 2&gt;/dev/null || true</td></tr></table>\n"
        )
        tokens = [t for t, _ in mdproj.project("x.md", text).tokens]
        self.assertIn("<thought>", tokens)
        self.assertIn("<answer>", tokens)
        self.assertIn("||", tokens)

    def test_real_inline_markup_still_strips(self):
        text = ("<!-- source: source.pdf pages 001-001 -->\n\n<!-- p.1 -->\n\n"
                "plain <b>bold</b> and <i>slant</i> text\n")
        tokens = [t for t, _ in mdproj.project("x.md", text).tokens]
        self.assertEqual(["plain", "bold", "and", "slant", "text"], tokens)


def _span(text, x0, x1, y0, line):
    return {"text": text, "zone": "body", "bbox": [x0, y0, x1, y0 + 12],
            "line": line, "font": "Sans", "size": 11.0}


class HyphenBulletTests(unittest.TestCase):
    def test_hyphen_marker_with_hanging_text_is_structure(self):
        page = {"spans": [_span("-​", 90, 97, 190, 1),
                          _span("Suicide & self-harm", 108, 220, 190, 2)]}
        text = oracle.page_body_text(page)
        self.assertNotIn("-\u200b", text)
        self.assertIn("Suicide", text)

    def test_table_dash_placeholder_stays_text(self):
        # fable-5 pp.251-252: '-' + ZWSP as an empty-value table cell, its
        # neighbour ~40pt away
        page = {"spans": [_span("-​", 285, 293, 470, 1),
                          _span("83.4", 332, 352, 470, 2)]}
        self.assertIn("-​", oracle.page_body_text(page))


if __name__ == "__main__":
    unittest.main()
