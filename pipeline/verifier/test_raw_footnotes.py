import copy
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
sys.path.insert(0, str(HERE.parent))

import dangling_footnotes  # noqa: E402
import f18_semantic_zoning  # noqa: E402
import invariants  # noqa: E402
import mdproj  # noqa: E402
import raw_footnotes  # noqa: E402


def section_texts(card: Path) -> list[tuple[str, str]]:
    return [(path.name, path.read_text()) for path in sorted((card / "sections").glob("*.md"))]


def synthetic_definition(number: int, page: int, text: str) -> raw_footnotes.RawDefinition:
    return raw_footnotes.RawDefinition(
        number=number,
        marker_page=page,
        marker_bbox=(72.0, 650.0, 75.0, 658.0),
        end_page=page,
        text=text,
        line_bboxes=((page, (72.0, 650.0, 500.0, 663.0)),),
    )


def synthetic_reference(number: int, page: int) -> raw_footnotes.RawReference:
    return raw_footnotes.RawReference(number, page, (200.0, 200.0, 204.0, 208.0))


class RawFootnoteAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fable = REPO / "cards/anthropic/claude-fable-5"
        cls.opus = REPO / "cards/anthropic/claude-opus-5"
        cls.risk = REPO / "cards/anthropic/risk-report-2026-08"

    def test_current_corpus_has_zero_unexplained_rf1_findings(self):
        risk_dispositions = json.loads(
            (self.risk / "source-footnote-dispositions.json").read_text()
        )
        cases = (
            (self.fable, None),
            (self.opus, None),
            (self.risk, risk_dispositions),
        )
        for card, dispositions in cases:
            with self.subTest(card=card.name):
                self.assertEqual(
                    [],
                    raw_footnotes.verify(
                        card / "source.pdf",
                        section_texts(card),
                        dispositions=dispositions,
                    ),
                )

    def test_unexplained_raw_reference_fails_closed_without_disposition(self):
        flags = raw_footnotes.verify(
            self.risk / "source.pdf",
            section_texts(self.risk),
        )
        kinds = [flag["detail"]["kind"] for flag in flags]
        self.assertIn("raw-reference-definition-ambiguous", kinds)
        self.assertIn("source-reference-without-canonical-occurrence", kinds)
        self.assertTrue(all(flag["severity"] == "major" for flag in flags))

    def test_stale_disposition_does_not_suppress_observation(self):
        disposition = json.loads(
            (self.risk / "source-footnote-dispositions.json").read_text()
        )
        disposition["source_sha256"] = "0" * 64
        flags = raw_footnotes.verify(
            self.risk / "source.pdf",
            section_texts(self.risk),
            dispositions=disposition,
        )
        kinds = [flag["detail"]["kind"] for flag in flags]
        self.assertIn("stale-disposition-source", kinds)
        self.assertIn("raw-reference-definition-ambiguous", kinds)

    def test_stale_observer_contract_does_not_suppress_observation(self):
        disposition = json.loads(
            (self.risk / "source-footnote-dispositions.json").read_text()
        )
        disposition["observer_schema_version"] += 1
        flags = raw_footnotes.verify(
            self.risk / "source.pdf",
            section_texts(self.risk),
            dispositions=disposition,
        )
        kinds = [flag["detail"]["kind"] for flag in flags]
        self.assertIn("stale-disposition-observer-schema", kinds)
        self.assertIn("raw-reference-definition-ambiguous", kinds)

    def test_non_string_disposition_id_is_a_blocking_finding_not_a_crash(self):
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="9" * 64,
            definitions=(synthetic_definition(1, 2, "one body"),),
            references=(synthetic_reference(1, 2),),
        )
        section = (
            "valid.md",
            "<!-- source: source.pdf pages 002-002 -->\n\n"
            "<!-- p.2 -->\n\nVisible.[^1]\n\n[^1]: one body\n",
        )
        for field in ("excluded_references", "excluded_definitions"):
            with self.subTest(field=field):
                dispositions = {
                    "schema_version": 1,
                    "observer_schema_version": raw_footnotes.OBSERVER_SCHEMA_VERSION,
                    "pymupdf_version": raw_footnotes.PYMUPDF_VERSION,
                    "source_sha256": observation.source_sha256,
                    "excluded_references": [],
                    "excluded_definitions": [],
                }
                dispositions[field] = [{"source_id": ["bad"], "reason": "x"}]
                flags = raw_footnotes.verify(
                    "unused.pdf",
                    [section],
                    observation=observation,
                    dispositions=dispositions,
                )
                self.assertEqual(
                    ["invalid-disposition-entry"],
                    [flag["detail"]["kind"] for flag in flags],
                )
                self.assertEqual("major", flags[0]["severity"])

    def test_non_mapping_disposition_document_is_a_blocking_finding(self):
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="8" * 64,
            definitions=(),
            references=(),
        )
        flags = raw_footnotes.verify(
            "unused.pdf", [], observation=observation, dispositions=[]
        )
        self.assertEqual(
            ["invalid-disposition-document"],
            [flag["detail"]["kind"] for flag in flags],
        )

    def test_observe_hashes_content_even_when_stat_identity_is_restored(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        path = Path(handle.name)
        try:
            handle.write(b"aaaa")
            handle.close()
            before = path.stat()

            def fake_observe(source_path, digest):
                return raw_footnotes.RawObservation(source_path, digest, (), ())

            with mock.patch.object(raw_footnotes, "_observe_cached", side_effect=fake_observe):
                first = raw_footnotes.observe(path)
                path.write_bytes(b"bbbb")
                os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                second = raw_footnotes.observe(path)
            self.assertNotEqual(first.source_sha256, second.source_sha256)
        finally:
            path.unlink(missing_ok=True)

    def test_unfamiliar_relative_typography_cannot_disappear_with_canonical_footnote(self):
        """A valid larger footnote family must not be outside observation.

        PyMuPDF's HTML layout emits the 11pt body's superscript at 9.13pt,
        while the definition uses an 8pt marker and 8pt body.  All three are
        larger than the old 7.6pt absolute cap.  Co-deleting the canonical
        reference and definition must therefore fail closed.
        """
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.pdf"
            document = raw_footnotes.fitz.open()
            page = document.new_page()
            page.insert_htmlbox(
                raw_footnotes.fitz.Rect(72, 72, 500, 160),
                '<p style="font-size:11pt">Body<sup>1</sup> tail</p>',
            )
            # Separate insertions exercise the visual-line coalescer rather
            # than handing the observer a pre-grouped synthetic line.
            page.insert_text((72, 700), "1", fontsize=8)
            page.insert_text((82, 700), "synthetic footnote body", fontsize=8)
            document.save(source)
            document.close()

            with raw_footnotes.fitz.open(source) as reopened:
                superscript_sizes = [
                    float(span["size"])
                    for block in reopened[0].get_text("dict")["blocks"]
                    if block.get("type") == 0
                    for line in block.get("lines", [])
                    for span in line.get("spans", [])
                    if span.get("flags", 0) & raw_footnotes.SUPER
                    and span.get("text", "").strip() == "1"
                ]
            self.assertEqual(1, len(superscript_sizes))
            self.assertGreater(superscript_sizes[0], 7.6)

            observation = raw_footnotes.observe(source)
            self.assertEqual([1], [ref.number for ref in observation.references])
            self.assertEqual([1], [definition.number for definition in observation.definitions])
            self.assertEqual(
                "synthetic footnote body", observation.definitions[0].text,
            )

            preserved = (
                "synthetic.md",
                "<!-- source: source.pdf pages 001-001 -->\n\n"
                "<!-- p.1 -->\n\nBody[^1] tail\n\n"
                "[^1]: synthetic footnote body\n",
            )
            self.assertEqual(
                [],
                raw_footnotes.verify(
                    source, [preserved], observation=observation,
                ),
            )

            co_deleted = (
                "synthetic.md",
                "<!-- source: source.pdf pages 001-001 -->\n\n"
                "<!-- p.1 -->\n\nBody tail\n",
            )
            flags = raw_footnotes.verify(
                source, [co_deleted], observation=observation,
            )
            kinds = [flag["detail"]["kind"] for flag in flags]
            self.assertIn("source-reference-without-canonical-occurrence", kinds)
            self.assertIn("source-definition-without-canonical-occurrence", kinds)

    def test_restarted_numbers_bind_to_distinct_source_occurrences(self):
        first = (
            "a.md",
            "<!-- source: source.pdf pages 002-003 -->\n\n"
            "<!-- p.2 -->\n\nAlpha.[^1]\n\n[^1]: first body\n",
        )
        second = (
            "b.md",
            "<!-- source: source.pdf pages 010-011 -->\n\n"
            "<!-- p.10 -->\n\nBeta.[^1]\n\n[^1]: second body\n",
        )
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="a" * 64,
            definitions=(
                synthetic_definition(1, 2, "first body"),
                synthetic_definition(1, 10, "second body"),
            ),
            references=(synthetic_reference(1, 2), synthetic_reference(1, 10)),
        )

        self.assertEqual(
            [],
            raw_footnotes.verify(
                "unused.pdf", [first, second], observation=observation,
            ),
        )

    def test_duplicate_definition_in_one_section_cannot_hide_in_a_dict(self):
        section = (
            "dup.md",
            "<!-- source: source.pdf pages 002-003 -->\n\n"
            "<!-- p.2 -->\n\nAlpha.[^1]\n\n"
            "[^1]: first body\n\n[^1]: replacement body\n",
        )
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="b" * 64,
            definitions=(synthetic_definition(1, 2, "first body"),),
            references=(synthetic_reference(1, 2),),
        )

        flags = raw_footnotes.verify(
            "unused.pdf", [section], observation=observation,
        )
        self.assertIn(
            "duplicate-canonical-definition",
            [flag["detail"]["kind"] for flag in flags],
        )

    def test_multiple_same_page_references_are_bound_by_occurrence_order(self):
        section = (
            "repeat.md",
            "<!-- source: source.pdf pages 002-003 -->\n\n"
            "<!-- p.2 -->\n\nAlpha.[^1] Beta.[^1]\n\n[^1]: one body\n",
        )
        first = synthetic_reference(1, 2)
        second = raw_footnotes.RawReference(1, 2, (300.0, 300.0, 304.0, 308.0))
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="c" * 64,
            definitions=(synthetic_definition(1, 2, "one body"),),
            references=(first, second),
        )
        self.assertEqual(
            [],
            raw_footnotes.verify("unused.pdf", [section], observation=observation),
        )

    def test_duplicate_raw_reference_identity_fails_before_occurrence_collapse(self):
        section = (
            "repeat.md",
            "<!-- source: source.pdf pages 002-002 -->\n\n"
            "<!-- p.2 -->\n\nAlpha.[^1]\n\n[^1]: one body\n",
        )
        reference = synthetic_reference(1, 2)
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="2" * 64,
            definitions=(synthetic_definition(1, 2, "one body"),),
            # These are two raw glyph occurrences, even though the observer's
            # rounded public identity cannot distinguish their geometry.
            references=(reference, reference),
        )
        dispositions = {
            "schema_version": 1,
            "observer_schema_version": raw_footnotes.OBSERVER_SCHEMA_VERSION,
            "pymupdf_version": raw_footnotes.PYMUPDF_VERSION,
            "source_sha256": observation.source_sha256,
            # A reviewed exclusion must not accidentally suppress both raw
            # occurrences just because their IDs collide.
            "excluded_references": [
                {"source_id": reference.source_id, "reason": "synthetic artifact"},
            ],
            "excluded_definitions": [],
        }

        for configured_dispositions in (None, dispositions):
            with self.subTest(dispositions=configured_dispositions is not None):
                flags = raw_footnotes.verify(
                    "unused.pdf",
                    [section],
                    observation=observation,
                    dispositions=configured_dispositions,
                )
                self.assertEqual(
                    ["duplicate-raw-source-id"],
                    [flag["detail"]["kind"] for flag in flags],
                )
                self.assertEqual("reference", flags[0]["detail"]["source_kind"])
                self.assertEqual(2, flags[0]["detail"]["count"])
                self.assertEqual("major", flags[0]["severity"])

    def test_duplicate_raw_definition_identity_fails_before_dict_collapse(self):
        section = (
            "repeat.md",
            "<!-- source: source.pdf pages 002-002 -->\n\n"
            "<!-- p.2 -->\n\nAlpha.[^1]\n\n[^1]: one body\n",
        )
        definition = synthetic_definition(1, 2, "one body")
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="3" * 64,
            definitions=(definition, definition),
            references=(synthetic_reference(1, 2),),
        )

        flags = raw_footnotes.verify(
            "unused.pdf", [section], observation=observation,
        )
        self.assertEqual(
            ["duplicate-raw-source-id"],
            [flag["detail"]["kind"] for flag in flags],
        )
        self.assertEqual("definition", flags[0]["detail"]["source_kind"])
        self.assertEqual(2, flags[0]["detail"]["count"])
        self.assertEqual("major", flags[0]["severity"])

    def test_page_sentinels_inside_multpage_table_drive_reference_identity(self):
        section = (
            "table.md",
            "<!-- source: source.pdf pages 002-003 -->\n\n"
            "<!-- p.2 -->\n<table><tr><td>A<sup>[^1]</sup></td></tr>\n"
            "<!-- p.3 -->\n<tr><td>B<sup>[^2]</sup></td></tr></table>\n\n"
            "[^1]: first body\n\n[^2]: second body\n",
        )
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="d" * 64,
            definitions=(
                synthetic_definition(1, 2, "first body"),
                synthetic_definition(2, 3, "second body"),
            ),
            references=(synthetic_reference(1, 2), synthetic_reference(2, 3)),
        )
        self.assertEqual(
            [],
            raw_footnotes.verify("unused.pdf", [section], observation=observation),
        )

    def test_unreferenced_raw_definition_is_still_required(self):
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="e" * 64,
            definitions=(synthetic_definition(7, 2, "unclaimed source body"),),
            references=(),
        )
        section = (
            "empty.md",
            "<!-- source: source.pdf pages 002-003 -->\n\n<!-- p.2 -->\n\nVisible.\n",
        )
        flags = raw_footnotes.verify(
            "unused.pdf", [section], observation=observation,
        )
        self.assertEqual(
            ["source-definition-without-canonical-occurrence"],
            [flag["detail"]["kind"] for flag in flags],
        )

    def test_literal_or_hidden_reference_syntax_cannot_replace_visible_ref(self):
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="f" * 64,
            definitions=(synthetic_definition(1, 2, "one body"),),
            references=(synthetic_reference(1, 2),),
        )
        forged_forms = (
            "<!-- [^1] -->",
            "<!-- [^1]",
            "`[^1]`",
            "```text\n[^1]\n```",
            "```text\n[^1]",
            "<code>[^1]</code>",
            "<code>[^1]",
            "<pre>[^1]</pre>",
            "    [^1]",
            "[label](https://example.test/[^1])",
            "![^1](assets/figure.png)",
            '<span data-note="[^1]">visible</span>',
            r"\[^1]",
            "<script>[^1]</script>",
        )
        for forged in forged_forms:
            with self.subTest(forged=forged):
                section = (
                    "forged-ref.md",
                    "<!-- source: source.pdf pages 002-003 -->\n\n"
                    f"<!-- p.2 -->\n\n{forged}\n\n[^1]: one body\n",
                )
                flags = raw_footnotes.verify(
                    "unused.pdf", [section], observation=observation,
                )
                kinds = [flag["detail"]["kind"] for flag in flags]
                self.assertIn("source-reference-without-canonical-occurrence", kinds)

    def test_literal_or_hidden_definition_syntax_cannot_satisfy_source_def(self):
        observation = raw_footnotes.RawObservation(
            source_pdf="synthetic.pdf",
            source_sha256="1" * 64,
            definitions=(synthetic_definition(1, 2, "one body"),),
            references=(synthetic_reference(1, 2),),
        )
        forged_forms = (
            "<!-- [^1]: one body -->",
            "<!-- [^1]: one body",
            "`[^1]: one body`",
            "```text\n[^1]: one body\n```",
            "```text\n[^1]: one body",
            "<code>[^1]: one body</code>",
            "<code>[^1]: one body",
            "<pre>[^1]: one body</pre>",
            "    [^1]: one body",
        )
        for forged in forged_forms:
            with self.subTest(forged=forged):
                section = (
                    "forged-def.md",
                    "<!-- source: source.pdf pages 002-003 -->\n\n"
                    f"<!-- p.2 -->\n\nVisible.[^1]\n\n{forged}\n",
                )
                flags = raw_footnotes.verify(
                    "unused.pdf", [section], observation=observation,
                )
                self.assertIn(
                    "source-definition-without-canonical-occurrence",
                    [flag["detail"]["kind"] for flag in flags],
                )

    def test_referenced_definition_f18_legacy_false_green_but_rf1_blocks(self):
        fixture = json.loads((HERE / "fixtures/f18-semantic-zoning.json").read_text())
        page_two, baseline_markdown = f18_semantic_zoning.build_baseline(fixture)
        raw_observation = raw_footnotes.observe(self.opus / "source.pdf")
        source_definition = next(
            definition for definition in raw_observation.definitions
            if definition.number == 1 and definition.marker_page == 36
        )
        baseline_markdown = baseline_markdown.replace(
            "pages 002-002", "pages 002-036"
        )
        baseline_markdown += (
            "\n<!-- p.36 -->\n\nExploitBench[^1]\n\n"
            f"[^1]: {source_definition.text}\n"
        )
        baseline_section = mdproj.project("f18-referenced.md", baseline_markdown)
        page_36 = {
            "spans": [{"text": "1", "zone": "fnref"}],
            "footnotes": {1: source_definition.text},
        }
        blank = {"spans": [], "footnotes": {}}
        baseline_pages = [copy.deepcopy(blank) for _ in range(36)]
        baseline_pages[1] = page_two
        baseline_pages[35] = page_36

        prose = " ".join(text.strip() for text in fixture["relocated_spans"])
        mutated_page_two = copy.deepcopy(page_two)
        selected = [
            span for span in mutated_page_two["spans"]
            if span["text"] in fixture["relocated_spans"]
        ]
        self.assertEqual(12, len(selected))
        for span in selected:
            span["zone"] = "fnbody"
            span["fn"] = 1
        mutated_page_36 = copy.deepcopy(page_36)
        mutated_page_36["footnotes"][1] += " " + prose
        mutated_markdown = baseline_markdown.replace(prose, "", 1).replace(
            f"[^1]: {source_definition.text}",
            f"[^1]: {source_definition.text} {prose}",
            1,
        )
        mutated_section = mdproj.project("f18-referenced.md", mutated_markdown)
        mutated_pages = [copy.deepcopy(blank) for _ in range(36)]
        mutated_pages[1] = mutated_page_two
        mutated_pages[35] = mutated_page_36

        def page_two_tokens(section):
            return [item for item in section.tokens if item[1] == 2]

        # The correlated interpretation remains a complete legacy false green:
        # source/body T1, source/output FN1, and dangling-definition closure all
        # accept the same wrong relocation into an already referenced footnote.
        self.assertEqual([], invariants.t1_text(
            page_two_tokens(baseline_section), baseline_pages, [2], set()))
        self.assertEqual([], invariants.t1_text(
            page_two_tokens(mutated_section), mutated_pages, [2], set()))
        self.assertEqual([], invariants.fn1_footnotes(
            [baseline_section], baseline_pages, [2, 36], set()))
        self.assertEqual([], invariants.fn1_footnotes(
            [mutated_section], mutated_pages, [2, 36], set()))
        self.assertEqual([], dangling_footnotes.check([mutated_section]))

        # Apply the same attack to the complete real Markdown. RF1 reopens the
        # unmodified PDF and compares the referenced definition with the exact
        # p.36 marker/body occurrence, so the appended p.2 prose cannot pass.
        real_sections = section_texts(self.opus)
        start = "those of Claude Fable 5’s, with one change:"
        end = "Multi-turn behavior was in line with Opus 4.8, with some qualitative differences: Opus 5’s"
        mutated_real = []
        relocated = None
        for name, text in real_sections:
            if name == "00-executive-summary.md":
                match = re.search(re.escape(start) + r".*?" + re.escape(end), text, re.S)
                self.assertIsNotNone(match)
                relocated = match.group(0)
                text = text[:match.start()] + text[match.end():]
            mutated_real.append((name, text))
        self.assertIsNotNone(relocated)
        mutated_real = [
            (
                name,
                re.sub(r"(?m)^(\[\^1\]:[^\n]*)$", r"\1 " + relocated, text, count=1)
                if name == "03-cyber.md" else text,
            )
            for name, text in mutated_real
        ]
        flags = raw_footnotes.verify(
            self.opus / "source.pdf",
            mutated_real,
            observation=raw_observation,
        )
        mismatches = [
            flag for flag in flags
            if flag["detail"]["kind"] == "definition-text-mismatch"
            and flag["detail"].get("number") == 1
        ]
        self.assertEqual(1, len(mismatches))
        self.assertEqual("major", mismatches[0]["severity"])
        self.assertEqual(64, len(mismatches[0]["detail"]["source"]["normalized_sha256"]))
        self.assertEqual(64, len(mismatches[0]["detail"]["canonical"]["normalized_sha256"]))


if __name__ == "__main__":
    unittest.main()
