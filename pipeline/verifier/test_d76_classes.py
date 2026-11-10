"""Tagged-table classes added with the eighth card (D76, gemini-4-carbon):
the page marker at a tagged cut row's exact seam, footnote-zone tag lines,
and docling rows split from two-line cells. Each test pairs the new
behaviour with the control that must not change."""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "generate"))

import tables  # noqa: E402


def _cell(text, y, i=0):
    return {"tag": "TD", "index": 0, "paras": [{"i": i, "lines": [[80, y, 300, y + 12, text]]}]}


def _tag_table(rows):
    return {"table": 7, "rows": [{"tr": k, "cells": cells} for k, cells in enumerate(rows)]}


class SeamMarkerTests(unittest.TestCase):
    HTML = ("<table><tbody><tr><td>Label</td><td>head of the</td></tr>"
            "<!-- p.16 --><tr><td></td><td>tail on the next page</td></tr>"
            "<tr><td>Next</td><td>row</td></tr></tbody></table>")

    def test_tagged_cut_row_takes_the_marker_at_its_seam(self):
        out = tables.merge_continuation_rows(self.HTML, forced=(1, [None, True]))
        self.assertIn("head of the<!-- p.16 --> tail on the next page", out)
        self.assertEqual(1, out.count("<!-- p.16 -->"))
        self.assertIn("<tr><td>Next</td>", out)

    def test_untagged_merge_keeps_the_marker_between_rows(self):
        out = tables.merge_continuation_rows(self.HTML)
        self.assertNotIn("the<!-- p.16 -->", out)
        self.assertEqual(1, out.count("<!-- p.16 -->"))


class FootnoteZoneTagTests(unittest.TestCase):
    def test_a_note_nested_in_a_cell_tag_tree_is_dropped(self):
        t = _tag_table([[_cell("Header", 100), _cell("Evidence", 100)]])
        t["rows"][0]["cells"][0]["paras"].append(
            {"i": 1, "lines": [[78, 651, 512, 664, "2 On Gram, the model recorded"]]})
        page = {"tags": [t], "spans": [{"zone": "fnbody", "bbox": [78, 651, 512, 664]}]}
        lines = tables._tag_table_lines(tables._page_tags(page)[0])
        self.assertEqual(["Header", "Evidence"], [l[4] for l in lines])

    def test_page_without_notes_keeps_every_line(self):
        t = _tag_table([[_cell("A", 100), _cell("B", 100)]])
        page = {"tags": [t], "spans": [{"zone": "body", "bbox": [72, 700, 200, 712]}]}
        self.assertEqual(t, tables._page_tags(page)[0])


class SplitRowTests(unittest.TestCase):
    TAGS = _tag_table([[_cell("Eval", 100), _cell("Score", 100)],
                       [_cell("HealthBench Pro (length-adjusted)", 120), _cell("72.8 (59.5)", 120)]])

    def test_docling_split_of_a_two_line_cell_yields_to_the_tags(self):
        html = ("<table><tr><td>Eval</td><td>Score</td></tr>"
                "<tr><td>HealthBench Pro</td><td>72.8</td></tr>"
                "<tr><td>(length-adjusted)</td><td>(59.5)</td></tr></table>")
        self.assertTrue(tables._docling_split_rows(html, self.TAGS))

    def test_extra_docling_text_is_untagged_content_not_a_split(self):
        html = ("<table><tr><td>Eval</td><td>Score</td></tr>"
                "<tr><td>HealthBench Pro</td><td>72.8</td></tr>"
                "<tr><td>(length-adjusted) continued</td><td>(59.5)</td></tr></table>")
        self.assertFalse(tables._docling_split_rows(html, self.TAGS))


if __name__ == "__main__":
    unittest.main()
