from __future__ import annotations

import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import structure_alignment as alignment

pdf = alignment.pdf_structure


def evidence(
    text: str,
    prefix: str | None = "●",
    *,
    separated_geometry: bool = True,
    occurrence_id: str = "evidence",
    page: int = 1,
) -> pdf.PageEvidence:
    owned_text = text if prefix is None else f"{prefix}\u200b{text}"
    if prefix is None:
        prefix_first = prefix_last = suffix_first = None
        suffix = None
    else:
        prefix_first = prefix_last = (0.0, 0.0, 1.0, 10.0)
        suffix_first = None if not text.strip() else (
            (10.0, 0.0, 20.0, 10.0)
            if separated_geometry
            else (1.5, 0.0, 11.5, 10.0)
        )
        suffix = text
    digest = alignment.hashlib.sha256(owned_text.encode()).hexdigest()
    return pdf.PageEvidence(
        occurrence_id=occurrence_id,
        page=page,
        bbox=(0.0, 0.0, 20.0, 10.0),
        text=owned_text,
        text_sha256=digest,
        owned_text=owned_text,
        owned_text_sha256=digest,
        separator_prefix=prefix,
        separator_suffix=suffix,
        prefix_first_glyph_bbox=prefix_first,
        prefix_last_glyph_bbox=prefix_last,
        suffix_first_nonspace_glyph_bbox=suffix_first,
    )


def list_item(
    occurrence_id: str,
    parent_list_id: str,
    page: int,
    item_evidence: pdf.PageEvidence,
) -> pdf.ListItemObservation:
    return pdf.ListItemObservation(
        occurrence_id=occurrence_id,
        structure_path=(),
        parent_list_id=parent_list_id,
        ancestor_roles=("L",),
        pages=(page,),
        evidence=(replace(
            item_evidence,
            occurrence_id=f"{occurrence_id}@p{page:04d}",
            page=page,
        ),),
    )


def source_fixture() -> pdf.PDFStructureObservation:
    items = (
        list_item("I0", "L0", 1, evidence("Same")),
        list_item("I1", "L0", 2, evidence("Same")),
        list_item("I2", "L0", 3, evidence("user's text", "1.")),
        list_item("I3", "L1", 4, evidence("Ignored")),
    )
    lists = (
        pdf.ListObservation(
            occurrence_id="L0",
            structure_path=(),
            parent_list_id=None,
            parent_item_id=None,
            ancestor_roles=(),
            direct_item_ids=("I0", "I1", "I2"),
            pages=(1, 2, 3),
            evidence=(),
        ),
        pdf.ListObservation(
            occurrence_id="L1",
            structure_path=(),
            parent_list_id=None,
            parent_item_id=None,
            ancestor_roles=(),
            direct_item_ids=("I3",),
            pages=(4,),
            evidence=(),
        ),
    )
    return pdf.PDFStructureObservation(
        schema_version=pdf.SCHEMA_VERSION,
        source_pdf="synthetic.pdf",
        source_sha256="a" * 64,
        pymupdf_version=pdf.PINNED_PYMUPDF_VERSION,
        extraction_flags=pdf.EXTRACTION_FLAGS,
        status="ok",
        capabilities={},
        stats={},
        lists=lists,
        list_items=items,
        issues=(),
    )


def item(
    occurrence: int,
    page: int,
    text: str,
    tokens: list[str],
    own_pages: tuple[int, ...] = (),
) -> dict:
    return {
        "kind": "item",
        "occurrence": occurrence,
        "nearestPageMarkerId": f"p-{page}",
        "ownText": text,
        "ownTokens": tokens,
        "ownTokenCount": len(tokens),
        "ownTokenSha256": alignment._token_digest(tokens),
        "ownPageMarkers": [
            {"id": f"p-{own_page}", "tokenOffset": 0}
            for own_page in own_pages
        ],
    }


def dom_fixture() -> dict:
    return {
        "schemaVersion": 2,
        "tokenDigestMethod": "visible-list-tokens.sha256-json.v1",
        "excludedSubtrees": [
            {"kind": "renderer-footnotes", "occurrence": 0, "listCount": 1, "itemCount": 9},
        ],
        "events": [
            item(0, 1, "Same", ["Same"]),
            item(1, 2, "Same", ["Same"]),
            item(2, 3, "user’s text", ["user’s", "text"]),
            item(3, 4, "Ignored", ["Ignored"]),
        ],
    }


class MatchingTests(unittest.TestCase):
    def test_tokenizer_retains_punctuation_after_narrow_source_normalization(self):
        text = alignment.normalize_source_text(" ﬁne\u200b  user’s  1. ")
        self.assertEqual(text, "fine user’s 1.")
        self.assertEqual(alignment.visible_tokens(text), ("fine", "user’s", "1", "."))

    def test_marker_policy_requires_lexical_shape_and_separated_geometry(self):
        self.assertEqual(alignment._marker_body(evidence("body", "1.")), "body")
        self.assertIsNone(alignment._marker_body(
            evidence("ordinary", "1.", separated_geometry=False)
        ))
        self.assertIsNone(alignment._marker_body(evidence("body", "Alpha")))
        self.assertIsNone(alignment._marker_body(evidence("", "-")))

    def test_exact_unique_and_page_resolved_counts_partition_both_sides(self):
        report = alignment._align_live_observation(
            "anthropic/example", source_fixture(), dom_fixture()
        )
        self.assertEqual(report["status"], "advisory")
        self.assertFalse(report["policy"]["release_gate"])
        self.assertEqual(report["source"]["items_tag_claims_included"], 4)
        self.assertEqual(report["matches"], {
            "source_exact_unique": 1,
            "source_exact_page_resolved": 2,
            "source_exact_ambiguous_unresolved": 0,
            "source_exact_unmatched": 1,
            "dom_exact_unique": 1,
            "dom_exact_page_resolved": 2,
            "dom_exact_ambiguous_unresolved": 0,
            "dom_exact_unmatched": 1,
        })
        self.assertEqual(report["dom"]["renderer_footnote_items_excluded"], 9)

    def test_neutral_match_core_reports_unresolved_and_cardinality_residuals(self):
        source = [
            alignment.MatchRow(0, (1,), ("Same",)),
            alignment.MatchRow(1, (2,), ("Same",)),
        ]
        dom = [alignment.MatchRow(0, (1, 2), ("Same",))]
        self.assertEqual(alignment.match_rows(source, dom), {
            "source_exact_unique": 0,
            "source_exact_page_resolved": 0,
            "source_exact_ambiguous_unresolved": 1,
            "source_exact_unmatched": 1,
            "dom_exact_unique": 0,
            "dom_exact_page_resolved": 0,
            "dom_exact_ambiguous_unresolved": 1,
            "dom_exact_unmatched": 0,
        })

    def test_empty_token_rows_never_match(self):
        source = [alignment.MatchRow(0, (1,), ())]
        dom = [alignment.MatchRow(0, (1,), ())]
        report = alignment.match_rows(source, dom)
        self.assertEqual(report["source_exact_unique"], 0)
        self.assertEqual(report["source_exact_unmatched"], 1)
        self.assertEqual(report["dom_exact_unmatched"], 1)

    def test_contiguous_marker_shaped_text_keeps_its_prefix(self):
        source = source_fixture()
        source = replace(source, list_items=(list_item(
            "I-ordinary-marker-shape",
            "L0",
            1,
            evidence("ordinary text", "1.", separated_geometry=False),
        ),))
        dom = dom_fixture()
        dom["events"] = [
            item(0, 1, "1. ordinary text", ["1", ".", "ordinary", "text"]),
        ]
        report = alignment._align_live_observation("anthropic/example", source, dom)
        self.assertEqual(report["matches"]["source_exact_unique"], 1)

    def test_dom_json_schema_text_and_digest_are_strict(self):
        dom = dom_fixture()
        dom["tokenDigestMethod"] = "unknown"
        with self.assertRaisesRegex(ValueError, "DOM token digest method"):
            alignment._align_live_observation("anthropic/example", source_fixture(), dom)

        dom = dom_fixture()
        dom["events"][0]["ownTokenSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "token digest"):
            alignment._align_live_observation("anthropic/example", source_fixture(), dom)

    def test_run_reopens_source_pdf_and_passes_live_observation(self):
        source = source_fixture()
        expected = {"status": "advisory"}
        card_root = Path("/synthetic/card")
        with (
            patch.object(
                alignment, "resolve_card",
                return_value=("anthropic/example", card_root),
            ),
            patch.object(alignment.pdf_structure, "observe_pdf", return_value=source) as observe,
            patch.object(alignment, "render_dom_observation", return_value=dom_fixture()),
            patch.object(alignment, "_align_live_observation", return_value=expected) as match,
        ):
            self.assertIs(alignment.run("anthropic/example"), expected)
        observe.assert_called_once_with(card_root / "source.pdf")
        self.assertIs(match.call_args.args[1], source)

    def test_blocked_source_produces_blocked_report_and_nonzero_cli_status(self):
        source = source_fixture()
        source = replace(
            source,
            status="blocked",
            issues=(pdf.StructureIssue(
                code="synthetic-source-break",
                severity="blocking",
                occurrence_id=None,
                pages=(),
                detail="synthetic",
            ),),
        )
        report = alignment._align_live_observation(
            "anthropic/example", source, dom_fixture()
        )
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(
            report["source"]["blocking_issue_codes"],
            ["synthetic-source-break"],
        )
        stdout = StringIO()
        with patch.object(alignment, "run", return_value=report), redirect_stdout(stdout):
            self.assertEqual(alignment.main(["anthropic/example"]), 3)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "blocked")

    def test_malformed_boundary_is_a_clean_cli_error(self):
        stderr = StringIO()
        with (
            patch.object(alignment, "run", side_effect=ValueError("bad observation")),
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            alignment.main(["anthropic/example"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("structure alignment failed: bad observation", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_card_id_and_card_directory_resolve_to_same_card(self):
        card_id, root = alignment.resolve_card("anthropic/claude-opus-5")
        self.assertEqual(card_id, "anthropic/claude-opus-5")
        self.assertEqual(alignment.resolve_card(str(root)), (card_id, root))


@unittest.skipUnless(
    os.environ.get("RUN_STRUCTURE_ALIGNMENT_CORPUS") == "1",
    "set RUN_STRUCTURE_ALIGNMENT_CORPUS=1 after installing site dependencies",
)
class ArchivedCorpusCensusTests(unittest.TestCase):
    EXPECTED: ClassVar = {
        "claude-fable-5": {
            "source": (364, 364),
            "dom": (368, 76),
            "matches": (297, 0, 0, 67, 297, 0, 0, 71),
        },
        "claude-opus-5": {
            "source": (195, 195),
            "dom": (224, 36),
            "matches": (181, 0, 0, 14, 181, 0, 0, 43),
        },
        "risk-report-2026-08": {
            "source": (300, 300),
            "dom": (305, 92),
            "matches": (259, 2, 0, 39, 259, 2, 0, 44),
        },
    }

    def test_current_three_card_advisory_census_is_stable(self):
        fields = (
            "source_exact_unique", "source_exact_page_resolved",
            "source_exact_ambiguous_unresolved", "source_exact_unmatched",
            "dom_exact_unique", "dom_exact_page_resolved",
            "dom_exact_ambiguous_unresolved", "dom_exact_unmatched",
        )
        for slug, expected in self.EXPECTED.items():
            with self.subTest(slug=slug):
                report = alignment.run(f"anthropic/{slug}")
                self.assertEqual(report["status"], "advisory")
                self.assertEqual(
                    (
                        report["source"]["items_total"],
                        report["source"]["items_tag_claims_included"],
                    ),
                    expected["source"],
                )
                self.assertEqual(
                    (
                        report["dom"]["items_total"],
                        report["dom"]["renderer_footnote_items_excluded"],
                    ),
                    expected["dom"],
                )
                self.assertEqual(
                    tuple(report["matches"][field] for field in fields),
                    expected["matches"],
                )


if __name__ == "__main__":
    unittest.main()
