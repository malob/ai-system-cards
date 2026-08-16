import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import calibrate
import l2_links
import mdproj


def annotation(source_id, anchor, rect, *, dest_page=2, dest_y=90,
               page=10, line_start_x=None, unresolvable=False, name=""):
    if line_start_x is None:
        line_start_x = rect[0]
    return l2_links.SourceAnnotation(
        source_id, page, anchor, rect, line_start_x, dest_page, dest_y,
        None, 72.0, name, unresolvable, 1,
    )


def heading(identity, title, slug, bbox, *, page=2, ordinal=0):
    return l2_links.Heading(
        identity, f"md:{identity}", "00.md", ordinal, 2, title, page, slug,
        ordinal, (ordinal,), bbox,
    )


def source_link(anchor="Section 2.1", *, dest_page=2, dest_y=90,
                unresolvable=False, name=""):
    return l2_links.SourceLink(
        "source", 10, anchor, ("annotation",), dest_page, dest_y, name,
        unresolvable, ((10, 10, 30, 20),),
    )


def output_link(target="#21-target", text="Section 2.1"):
    return l2_links.OutputLink(
        "00.md:l0", "00.md", 0, 10, text, target, ("00.md:l0",),
        (text,), (0,), False,
    )


def model():
    return l2_links.SourceModel("/source.pdf", "a" * 64, (), (), (), ())


class L2LinkTests(unittest.TestCase):
    def test_duplicate_github_slugs_preserve_heading_occurrence_identity(self):
        self.assertEqual(
            l2_links.github_slugs(["Scope", "Scope", "Scope-1", "Scope"]),
            ["scope", "scope-1", "scope-1-1", "scope-2"],
        )

    def test_raw_table_marker_attributes_later_page_link(self):
        text = """<!-- source: source.pdf pages 010-011 -->
<!-- p.10 -->
## 1 Start
<table><tr><td>first</td></tr><!-- p.11 --><tr><td><a href="#target">Later</a></td></tr></table>
"""
        parsed = l2_links.parse_markdown([("00.md", text)])
        self.assertEqual([(link.text, link.page) for link in parsed.links], [("Later", 11)])
        projected = mdproj.project("00.md", text)
        self.assertEqual(projected.links, [("Later", "#target", 11)])

    def test_split_annotations_group_only_for_real_wrap_geometry(self):
        wrapped = [
            annotation("a", "Section", (480, 100, 530, 114), line_start_x=100),
            annotation("b", "2.7", (100, 114, 125, 128), line_start_x=100),
        ]
        groups = l2_links.group_source_annotations(wrapped)
        self.assertEqual([group.anchor for group in groups], ["Section 2.7"])

        separate_items = [
            annotation("c", "Unfaithful thinking", (100, 200, 220, 214), line_start_x=100),
            annotation("d", "verbalized awareness", (390, 216, 520, 230), line_start_x=100),
        ]
        self.assertEqual(len(l2_links.group_source_annotations(separate_items)), 2)

    def test_multi_annotation_group_requires_the_complete_combined_label(self):
        grouped = l2_links.group_source_annotations([
            annotation("a", "Alpha", (10, 10, 50, 20)),
            annotation("b", "Beta", (55, 10, 90, 20)),
        ])
        partial = [output_link("#21-target", "Alpha")]
        pairs, _ = l2_links.pair_links(grouped, partial)
        self.assertEqual(pairs, {})
        report = l2_links.evaluate(
            model(), [heading("target", "2.1 Target", "21-target", (72, 100, 300, 120))],
            [], grouped, partial, [],
        )
        self.assertEqual(
            {flag["detail"]["kind"] for flag in report.flags},
            {"missing-output-link", "unexplained-output-link"},
        )

    def test_short_numeric_links_are_verified_and_repointing_fails(self):
        target = heading("target", "4.2 Target", "42-target", (72, 100, 300, 120))
        wrong = heading("wrong", "4.3 Wrong", "43-wrong", (72, 200, 300, 220), ordinal=1)
        source = source_link(anchor="4.2")
        correct = l2_links.evaluate(
            model(), [target, wrong], [], [source], [output_link("#42-target", "4.2")], [],
        )
        self.assertEqual(correct.flags, [])
        repointed = l2_links.evaluate(
            model(), [target, wrong], [], [source], [output_link("#43-wrong", "4.2")], [],
        )
        self.assertEqual(repointed.flags[0]["detail"]["kind"], "wrong-existing-target")

    def test_only_sub_three_point_blank_source_slivers_are_excluded(self):
        def blank(width):
            return l2_links.SourceLink(
                "blank", 184, "", ("annotation",), 185, 364.0, "", False,
                ((71.0, 100.0, 71.0 + width, 114.0),),
            )
        self.assertEqual(l2_links.blank_source_disposition(blank(2.89)),
                         "blank-anchor-sliver")
        self.assertEqual(l2_links.blank_source_disposition(blank(3.01)),
                         "source-anchor-unreadable")

    def test_wrapped_section_number_checks_both_authored_members(self):
        grouped_source = l2_links.group_source_annotations([
            annotation("a", "Section", (10, 10, 50, 20)),
            annotation("b", "3.6", (55, 10, 80, 20)),
        ])
        occurrences = [
            l2_links.OutputOccurrence("00.md:l0", "00.md", 0, "Section", "#36-target",
                                      10, 0, 10, False, ""),
            l2_links.OutputOccurrence("00.md:l1", "00.md", 1, "3.6", "#36-target",
                                      10, 11, 20, False, " "),
        ]
        grouped_output = l2_links.group_output_occurrences(occurrences)
        self.assertEqual(grouped_output[0].text, "Section 3.6")
        target = heading("target", "3.6 Target", "36-target", (72, 100, 300, 120))
        report = l2_links.evaluate(model(), [target], [], grouped_source, grouped_output, [])
        self.assertEqual(report.flags, [])
        self.assertEqual([entry["output_id"] for entry in report.expected_links],
                         ["00.md:l0", "00.md:l1"])

    def test_destination_gap_activates_next_full_heading_bbox(self):
        parent = heading("parent", "2 Parent", "2-parent", (72, 50, 300, 70))
        child = heading("child", "2.1 Child", "21-child", (72, 100, 300, 120), ordinal=1)
        resolved, reason = l2_links.resolve_destination(
            source_link(dest_y=88), [parent, child]
        )
        self.assertEqual((resolved.identity, reason), ("child", "geometry"))

    def test_deleted_child_plus_repointed_parent_cannot_shrink_source_inventory(self):
        source = l2_links.SourceModel(
            "/cards/test/vendor/source.pdf", "a" * 64, (300.0, 300.0),
            ((), (
                l2_links.SourceLine("2 Parent", (72, 50, 300, 70), 16, True),
                l2_links.SourceLine("2.1 Child", (72, 100, 300, 120), 14, True),
            )),
            (
                l2_links.OutlineItem(0, 1, (0,), "2 Parent", 2, 50),
                l2_links.OutlineItem(1, 2, (0, 1), "2.1 Child", 2, 100),
            ),
            (),
        )
        # The output under test deleted the child and repointed its link to the
        # still-real parent.  Source-first acceptance must retain the child.
        parsed = l2_links.ParsedMarkdown((
            l2_links.MarkdownHeading("00.md:h0", "00.md", 0, 2,
                                     "2 Parent", 2, "2-parent"),
        ), ())
        headings, heading_flags = l2_links.accept_headings(source, parsed)
        self.assertIn("target-heading-missing",
                      [flag["detail"]["kind"] for flag in heading_flags])
        report = l2_links.evaluate(
            source, headings, heading_flags,
            [source_link(anchor="child link", dest_y=88)],
            [output_link("#2-parent", "child link")], [],
        )
        kinds = [flag["detail"]["kind"] for flag in report.flags]
        self.assertIn("target-heading-missing-for-link", kinds)

    def test_unresolvable_destination_recovers_only_unique_printed_heading(self):
        target = heading("target", "2.1 Target", "21-target", (72, 100, 300, 120))
        recovered, reason = l2_links.resolve_destination(
            source_link(anchor="2.1", dest_page=0, dest_y=None, unresolvable=True,
                        name="missing"),
            [target],
        )
        self.assertEqual((recovered.identity, reason), ("target", "printed-heading-recovery"))
        unresolved, reason = l2_links.resolve_destination(
            source_link(anchor="descriptive prose", dest_page=0, dest_y=None,
                        unresolvable=True, name="missing"),
            [target],
        )
        self.assertIsNone(unresolved)
        self.assertEqual(reason, "source-unresolvable")

    def test_wrong_existing_and_dead_targets_are_l2_majors(self):
        expected = heading("expected", "2.1 Target", "21-target", (72, 100, 300, 120))
        wrong = heading("wrong", "2.2 Wrong", "22-wrong", (72, 200, 300, 220), ordinal=1)
        report = l2_links.evaluate(
            model(), [expected, wrong], [], [source_link()],
            [output_link("#22-wrong")], [],
        )
        self.assertEqual(report.flags[0]["detail"]["kind"], "wrong-existing-target")

        report = l2_links.evaluate(
            model(), [expected], [], [source_link()], [output_link("#missing")], [],
        )
        self.assertEqual(report.flags[0]["detail"]["kind"], "dead-target")

    def test_unrecoverable_source_is_plain_only_and_hash_target_fails(self):
        target = heading("target", "2.1 Target", "21-target", (72, 100, 300, 120))
        unresolved = source_link(anchor="descriptive prose", dest_page=0, dest_y=None,
                                 unresolvable=True, name="missing")
        report = l2_links.evaluate(model(), [target], [], [unresolved], [], [])
        self.assertEqual(report.flags, [])
        self.assertEqual(report.exclusions[0]["kind"], "source-unresolvable-plain-text")

        report = l2_links.evaluate(
            model(), [target], [], [unresolved], [output_link("#", "descriptive prose")], [],
        )
        self.assertEqual(report.flags[0]["detail"]["kind"], "empty-target")

        blank_output = output_link("#21-target", "")
        report = l2_links.evaluate(model(), [target], [], [], [blank_output], [])
        self.assertEqual(report.flags[0]["detail"]["kind"], "unexplained-output-link")

    def test_source_cache_key_uses_bytes_even_when_stat_metadata_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.pdf"
            path.write_bytes(b"first")
            stat = path.stat()
            with mock.patch.object(l2_links, "_load_source_cached",
                                   side_effect=lambda _, digest: digest) as loader:
                first = l2_links.load_source(path)
                path.write_bytes(b"other")  # same size
                os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                second = l2_links.load_source(path)
            self.assertNotEqual(first, second)
            self.assertEqual(loader.call_count, 2)

    def test_partial_calibration_never_enables_full_graph_l2(self):
        self.assertTrue(calibrate._full_l2_enabled())
        self.assertFalse(calibrate._full_l2_enabled(["02a"], None))
        self.assertFalse(calibrate._full_l2_enabled(None, [20, 21]))

    def test_known_wrong_destinations_replay_as_occurrence_tied_l2_majors(self):
        document = json.loads((HERE / "known_wrong_destinations.json").read_text())
        self.assertEqual(document["schema_version"], 1)
        fixtures = document["fixtures"]
        self.assertEqual(len(fixtures), 27)

        locators = {
            (fixture["card"], fixture["file"], fixture["source_page"],
             fixture["label"], fixture["rank"])
            for fixture in fixtures
        }
        self.assertEqual(len(locators), len(fixtures), "fixture locators must be unique")

        fixtures_by_card = {}
        for fixture in fixtures:
            fixtures_by_card.setdefault(fixture["card"], []).append(fixture)

        def locate(parsed, fixture):
            matches = [
                link for link in parsed.links
                if link.file == fixture["file"]
                and link.page == fixture["source_page"]
                and l2_links.text_key(link.text) == fixture["label"]
            ]
            rank = fixture["rank"]
            self.assertLess(
                rank, len(matches),
                f"fixture occurrence missing: {fixture}",
            )
            return matches[rank]

        for card_id, card_fixtures in sorted(fixtures_by_card.items()):
            with self.subTest(card=card_id):
                card = REPO / "cards" / card_id
                sections = [
                    (path.name, path.read_text())
                    for path in sorted((card / "sections").glob("*.md"))
                ]
                manifest = (card / "style-manifest.yaml").read_text()
                toc_match = re.search(r"^\s*toc_pages:\s*\[([^]]*)\]", manifest, re.M)
                toc_pages = ({int(value) for value in toc_match.group(1).split(",")
                              if value.strip()} if toc_match else set())

                # Hash and parse the immutable source exactly once per card. Each
                # replay still runs the public L2 entry point, but avoids re-reading
                # hundreds of PDF pages for fixtures that alter only one href.
                source = l2_links.load_source(card / "source.pdf")
                with mock.patch.object(l2_links, "load_source", return_value=source):
                    baseline = l2_links.verify(card / "source.pdf", sections, toc_pages)
                    self.assertEqual(baseline.flags, [], f"nonzero baseline for {card_id}")
                    parsed = l2_links.parse_markdown(sections)

                    for fixture in card_fixtures:
                        with self.subTest(commit=fixture["commit"], file=fixture["file"],
                                          page=fixture["source_page"],
                                          label=fixture["label"]):
                            occurrence = locate(parsed, fixture)
                            self.assertEqual(occurrence.target, fixture["correct_href"])

                            section_map = dict(sections)
                            text = section_map[fixture["file"]]
                            event = text[occurrence.start:occurrence.end]
                            self.assertEqual(event.count(fixture["correct_href"]), 1)
                            section_map[fixture["file"]] = (
                                text[:occurrence.start]
                                + event.replace(
                                    fixture["correct_href"], fixture["old_href"], 1)
                                + text[occurrence.end:]
                            )
                            mutated_sections = [
                                (name, section_map[name]) for name, _ in sections
                            ]
                            mutated_parsed = l2_links.parse_markdown(mutated_sections)
                            mutated_occurrence = locate(mutated_parsed, fixture)
                            self.assertEqual(mutated_occurrence.target, fixture["old_href"])

                            report = l2_links.verify(
                                card / "source.pdf", mutated_sections, toc_pages)
                            tied = [
                                flag for flag in report.flags
                                if flag["invariant"] == "L2"
                                and flag["severity"] == "major"
                                and mutated_occurrence.output_id in
                                flag["detail"].get("output_id", "").split("+")
                                and flag["detail"].get("target") == fixture["old_href"]
                                and (
                                    flag["detail"].get("kind") ==
                                    "unexplained-output-link"
                                    or flag["detail"].get("expected") ==
                                    fixture["correct_href"]
                                )
                            ]
                            self.assertTrue(
                                tied,
                                "historical wrong target did not produce an "
                                f"occurrence-tied L2 major: {fixture}; flags={report.flags}",
                            )


if __name__ == "__main__":
    unittest.main()
