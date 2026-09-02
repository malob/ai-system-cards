from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from typing import ClassVar

import pymupdf as fitz

HERE = Path(__file__).parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import source_inventory


def _png(color: int) -> bytes:
    pixmap = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 20, 20), False)
    pixmap.clear_with(color)
    return pixmap.tobytes("png")


def make_source(path: Path, *, duplicate_draw=True) -> dict[str, bytes]:
    """Five pages: cover, linked front matter, and two content pages."""
    document = fitz.open()
    for _ in range(5):
        document.new_page(width=612, height=792)
    document[0].insert_text((72, 100), "Synthetic system card")
    document[1].insert_text((72, 50), "Dense linked substantive page one")
    document[2].insert_text((72, 50), "Dense linked substantive page two")
    document[3].insert_text((72, 50), "First content page")
    document[4].insert_text((72, 50), "Second content page")

    for page_index in (1, 2):
        page = document[page_index]
        for ordinal in range(12):
            y = 70 + ordinal * 14
            page.insert_link(
                {
                    "kind": fitz.LINK_GOTO,
                    "from": fitz.Rect(72, y, 250, y + 11),
                    "page": 3 + ordinal % 2,
                    "to": fitz.Point(72, 50),
                }
            )

    first = _png(0x336699)
    second = first if duplicate_draw else _png(0x993366)
    page = document[3]
    first_xref = page.insert_image(fitz.Rect(72, 200, 172, 300), stream=first)
    if duplicate_draw:
        page.insert_image(fitz.Rect(74, 202, 174, 302), xref=first_xref)
    else:
        page.insert_image(fitz.Rect(220, 200, 320, 300), stream=second)
    document.save(path)
    document.close()
    return {"p004-1.png": first, "p004-2.png": second}


def write_assets(directory: Path, assets: dict[str, bytes]) -> None:
    directory.mkdir()
    for name, data in assets.items():
        (directory / name).write_bytes(data)


def inventory_for(
    source_pdf: Path,
    *,
    page_kinds: dict[int, str] | None = None,
    duplicates: dict[str, str] | None = None,
    allowed_skips: dict[str, str] | None = None,
) -> dict:
    source = source_inventory.observe_source(source_pdf)
    pages = {item.page: item for item in source.pages}
    figures = {item.filename: item for item in source.raw_figures}
    page_entries = []
    for page, kind in sorted((page_kinds or {}).items()):
        page_entries.append(
            {
                "page": page,
                "kind": kind,
                "reason": f"reviewed {kind} exclusion",
                "observation": asdict(pages[page]),
            }
        )
    figure_entries = []
    for name, duplicate_of in sorted((duplicates or {}).items()):
        observation = asdict(figures[name])
        observation["bbox"] = list(observation["bbox"])
        figure_entries.append(
            {
                "filename": name,
                "kind": "duplicate-draw",
                "duplicate_of": duplicate_of,
                "reason": "reviewed coincident duplicate draw",
                "observation": observation,
            }
        )
    for name, reason in sorted((allowed_skips or {}).items()):
        observation = asdict(figures[name])
        observation["bbox"] = list(observation["bbox"])
        figure_entries.append(
            {
                "filename": name,
                "kind": "allow-skip",
                "reason": reason,
                "observation": observation,
            }
        )
    return {
        "schema_version": source_inventory.INVENTORY_SCHEMA_VERSION,
        "observer_schema_version": source_inventory.OBSERVER_SCHEMA_VERSION,
        "pymupdf_version": source_inventory.PYMUPDF_VERSION,
        "source_sha256": source.source_sha256,
        "page_exclusions": page_entries,
        "figure_exclusions": figure_entries,
    }


def base_inventory(source_pdf: Path, *, allow_skip=None) -> dict:
    return inventory_for(
        source_pdf,
        page_kinds={1: "cover", 2: "toc", 3: "toc"},
        duplicates={"p004-2.png": "p004-1.png"},
        allowed_skips=allow_skip,
    )


def kinds(report) -> list[str]:
    return [flag["detail"]["kind"] for flag in report.flags]


class SourceInventorySyntheticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / "source.pdf"
        assets = make_source(self.pdf)
        self.figures = self.root / "figures"
        write_assets(self.figures, assets)
        self.inventory = base_inventory(self.pdf)
        self.figure_map = {"4": ["p004-1.png", "p004-2.png"]}

    def tearDown(self):
        self.temp.cleanup()

    def verify(self, **overrides):
        arguments = {
            "inventory": self.inventory,
            "claimed_toc_pages": {2, 3},
            "claimed_figure_map": self.figure_map,
            "figure_dir": self.figures,
        }
        arguments.update(overrides)
        return source_inventory.verify(self.pdf, **arguments)

    def test_clean_source_uses_exact_overlay_authority(self):
        report = self.verify()
        self.assertEqual(report.flags, [])
        self.assertEqual(
            report.stats,
            {
                "source_pages": 5,
                "cover_pages": 1,
                "toc_pages": 2,
                "content_pages": 2,
                "blank_pages": 0,
                "raw_source_figures": 2,
                "visual_source_figures": 1,
                "projectable_source_figures": 1,
                "required_output_figures": 1,
                "duplicate_draw_exclusions": 1,
            },
        )

    def test_missing_inventory_fails_closed(self):
        report = self.verify(inventory=None)
        self.assertTrue(
            all(item["kind"] == "content" for item in report.page_dispositions)
        )
        self.assertEqual(kinds(report).count("source-inventory-missing"), 2)

    def test_stale_source_or_observer_binding_fails_closed(self):
        for field, value in (
            ("source_sha256", "0" * 64),
            ("observer_schema_version", 999),
            ("pymupdf_version", "0.0.0"),
        ):
            with self.subTest(field=field):
                overlay = json.loads(json.dumps(self.inventory))
                overlay[field] = value
                report = self.verify(inventory=overlay)
                self.assertEqual(kinds(report).count("source-inventory-stale"), 2)
                self.assertTrue(
                    all(item["kind"] == "content" for item in report.page_dispositions)
                )

    def test_inventory_json_path_is_supported_and_malformed_json_fails_closed(self):
        path = self.root / "source-inventory.json"
        path.write_text(json.dumps(self.inventory))
        self.assertEqual(self.verify(inventory=path).flags, [])
        path.write_text("{")
        report = self.verify(inventory=path)
        self.assertEqual(kinds(report).count("source-inventory-malformed"), 2)
        self.assertTrue(
            all(item["kind"] == "content" for item in report.page_dispositions)
        )

    def test_stale_entry_does_not_exclude_affected_page(self):
        overlay = json.loads(json.dumps(self.inventory))
        overlay["page_exclusions"][0]["observation"]["word_count"] += 1
        report = self.verify(inventory=overlay)
        self.assertIn("page-exclusion-stale", kinds(report))
        page_one = next(item for item in report.page_dispositions if item["page"] == 1)
        self.assertEqual(page_one["kind"], "content")

    def test_stale_figure_entry_leaves_occurrence_projectable(self):
        overlay = json.loads(json.dumps(self.inventory))
        overlay["figure_exclusions"][0]["observation"]["digest"] = "0" * 32
        report = self.verify(inventory=overlay)
        self.assertIn("figure-exclusion-stale", kinds(report))
        second = next(
            item for item in report.figures if item["filename"] == "p004-2.png"
        )
        self.assertEqual(second["disposition"], "required-output")

    def test_exact_authorized_skip_is_part_of_source_projection_contract(self):
        reason = "decorative raster reviewed against source"
        overlay = base_inventory(self.pdf, allow_skip={"p004-1.png": reason})
        report = self.verify(inventory=overlay)
        self.assertEqual(report.flags, [])
        first = next(
            item for item in report.figures if item["filename"] == "p004-1.png"
        )
        self.assertEqual(first["disposition"], "accepted-skip")
        self.assertEqual(report.stats["required_output_figures"], 0)

    def test_skip_authority_cannot_target_an_excluded_page(self):
        overlay = inventory_for(
            self.pdf,
            page_kinds={1: "cover", 2: "toc", 3: "toc", 4: "toc"},
            allowed_skips={"p004-1.png": "not a projectable source occurrence"},
        )
        report = self.verify(inventory=overlay, claimed_toc_pages={2, 3, 4})
        self.assertIn("figure-exclusion-stale", kinds(report))

    def test_malformed_overlay_scalars_fail_closed_without_crashing(self):
        cases = (
            ("page_exclusions", 0, "kind", []),
            ("figure_exclusions", 0, "filename", []),
            ("figure_exclusions", 0, "duplicate_of", []),
        )
        for collection, index, field, value in cases:
            with self.subTest(field=field):
                overlay = json.loads(json.dumps(self.inventory))
                overlay[collection][index][field] = value
                report = self.verify(inventory=overlay)
                self.assertTrue(
                    {"page-exclusion-stale", "figure-exclusion-stale"}
                    & set(kinds(report))
                )

    def test_duplicate_exclusions_must_point_to_an_earlier_occurrence(self):
        overlay = json.loads(json.dumps(self.inventory))
        source = source_inventory.observe_source(self.pdf)
        first = next(
            item for item in source.raw_figures if item.filename == "p004-1.png"
        )
        observation = asdict(first)
        observation["bbox"] = list(observation["bbox"])
        overlay["figure_exclusions"].append(
            {
                "filename": "p004-1.png",
                "kind": "duplicate-draw",
                "duplicate_of": "p004-2.png",
                "reason": "invalid reciprocal cycle",
                "observation": observation,
            }
        )
        report = self.verify(inventory=overlay)
        self.assertIn("figure-exclusion-stale", kinds(report))

    def test_arbitrary_png_named_bytes_do_not_satisfy_asset(self):
        (self.figures / "p004-1.png").write_bytes(b"arbitrary bytes")
        report = self.verify()
        self.assertIn("source-figure-asset-invalid", kinds(report))

    def test_wrong_png_pixels_do_not_satisfy_asset(self):
        (self.figures / "p004-1.png").write_bytes(_png(0xFFFFFF))
        report = self.verify()
        self.assertIn("source-figure-asset-mismatch", kinds(report))

    def test_omitted_substantive_page_one_is_required_without_authorization(self):
        overlay = inventory_for(
            self.pdf,
            page_kinds={2: "toc", 3: "toc"},
            duplicates={"p004-2.png": "p004-1.png"},
        )
        report = self.verify(inventory=overlay)
        page_one = next(item for item in report.page_dispositions if item["page"] == 1)
        self.assertEqual(page_one["kind"], "content")

    def test_dense_linked_pages_are_content_without_exact_authorization(self):
        overlay = inventory_for(
            self.pdf,
            page_kinds={1: "cover"},
            duplicates={"p004-2.png": "p004-1.png"},
        )
        report = self.verify(inventory=overlay)
        self.assertEqual(
            {
                item["page"]
                for item in report.page_dispositions
                if item["kind"] == "toc"
            },
            set(),
        )

    def test_map_is_checked_against_duplicate_raw_occurrence(self):
        report = self.verify(claimed_figure_map={"4": ["p004-1.png"]})
        self.assertIn("figure-map-source-mismatch", kinds(report))


class SourceProjectionArtifactTests(unittest.TestCase):
    DIGEST = "a" * 64

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / "source.pdf"
        assets = make_source(self.pdf)
        self.figures = self.root / "figures"
        write_assets(self.figures, assets)
        self.inventory_path = self.root / "source-inventory.json"
        self.figure_map_path = self.root / "figures-map.json"
        self.inventory_path.write_text(json.dumps(base_inventory(self.pdf)))
        self.figure_map_path.write_text(
            json.dumps({"4": ["p004-1.png", "p004-2.png"]})
        )

    def tearDown(self):
        self.temp.cleanup()

    def artifact(self):
        return source_inventory.build_projection_artifact(
            self.pdf,
            card_id="example/synthetic-card",
            inventory_path=self.inventory_path,
            claimed_toc_pages={2, 3},
            figure_map_path=self.figure_map_path,
            figure_dir=self.figures,
            canonical_sections_sha256=self.DIGEST,
        )

    def test_artifact_is_deterministic_and_binds_every_exact_input(self):
        first = self.artifact()
        second = self.artifact()
        self.assertEqual(first.to_json(), second.to_json())
        document = first.as_dict()
        self.assertEqual(document["source_flags"], [])
        self.assertEqual(document["card_id"], "example/synthetic-card")
        self.assertEqual(
            document["source"]["sha256"],
            hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            document["inputs"]["inventory"]["sha256"],
            hashlib.sha256(self.inventory_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            document["inputs"]["figures_map"]["sha256"],
            hashlib.sha256(self.figure_map_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            document["inputs"]["canonical_sections"],
            {
                "digest_method": source_inventory.PROJECTION_DIGEST_METHOD,
                "sha256": self.DIGEST,
            },
        )

    def test_artifact_covers_pages_assets_and_exact_source_event_order(self):
        document = self.artifact().as_dict()
        self.assertEqual(
            [page["pdf_page"] for page in document["pages"]],
            [1, 2, 3, 4, 5],
        )
        self.assertEqual(
            [page["disposition"] for page in document["pages"]],
            ["cover", "toc", "toc", "content", "content"],
        )
        self.assertEqual(
            [asset["filename"] for asset in document["assets"]],
            ["p004-1.png", "p004-2.png"],
        )
        self.assertEqual(
            [asset["disposition"] for asset in document["assets"]],
            ["required-output", "duplicate-draw"],
        )
        for asset in document["assets"]:
            expected_bytes = (self.figures / asset["filename"]).read_bytes()
            self.assertEqual(
                asset["file_sha256"], hashlib.sha256(expected_bytes).hexdigest()
            )
            self.assertEqual((asset["width"], asset["height"]), (20, 20))
            self.assertEqual(
                (asset["source"]["pdf_page"], asset["source"]["draw_index"]),
                (4, 1 if asset["filename"] == "p004-1.png" else 2),
            )
        self.assertEqual(
            document["events"],
            [
                {"kind": "page", "pdf_page": 4, "anchor": "p-4"},
                {
                    "kind": "figure",
                    "pdf_page": 4,
                    "draw_index": 1,
                    "filename": "p004-1.png",
                    "logical_src": "figures/p004-1.png",
                    "asset_sha256": hashlib.sha256(
                        (self.figures / "p004-1.png").read_bytes()
                    ).hexdigest(),
                },
                {"kind": "page", "pdf_page": 5, "anchor": "p-5"},
            ],
        )

    def test_allow_skip_is_a_required_interleaved_event_with_trimmed_reason_hash(self):
        reason = "  reviewed decorative raster  "
        overlay = base_inventory(
            self.pdf, allow_skip={"p004-1.png": reason}
        )
        self.inventory_path.write_text(json.dumps(overlay))
        document = self.artifact().as_dict()
        expected_reason = hashlib.sha256(reason.strip().encode("utf-8")).hexdigest()
        self.assertEqual(
            document["events"],
            [
                {"kind": "page", "pdf_page": 4, "anchor": "p-4"},
                {
                    "kind": "accepted-skip",
                    "pdf_page": 4,
                    "draw_index": 1,
                    "filename": "p004-1.png",
                    "reason_sha256": expected_reason,
                },
                {"kind": "page", "pdf_page": 5, "anchor": "p-5"},
            ],
        )
        first_asset = document["assets"][0]
        self.assertEqual(first_asset["disposition"], "accepted-skip")
        self.assertEqual(first_asset["reason_sha256"], expected_reason)

    def test_raw_input_bytes_change_the_artifact_hash_without_semantic_drift(self):
        before = self.artifact().as_dict()["inputs"]["inventory"]["sha256"]
        self.inventory_path.write_text(self.inventory_path.read_text() + "\n")
        after = self.artifact().as_dict()["inputs"]["inventory"]["sha256"]
        self.assertNotEqual(before, after)
        self.assertEqual(
            after, hashlib.sha256(self.inventory_path.read_bytes()).hexdigest()
        )

    def test_artifact_refuses_unresolved_source_flags(self):
        self.figure_map_path.write_text(json.dumps({"4": ["p004-1.png"]}))
        with self.assertRaisesRegex(
            source_inventory.ProjectionArtifactError,
            "figure-map-source-mismatch",
        ):
            self.artifact()

    def test_artifact_refuses_an_unbound_canonical_digest(self):
        with self.assertRaisesRegex(
            source_inventory.ProjectionArtifactError,
            "canonical_sections_sha256",
        ):
            source_inventory.build_projection_artifact(
                self.pdf,
                card_id="example/synthetic-card",
                inventory_path=self.inventory_path,
                claimed_toc_pages={2, 3},
                figure_map_path=self.figure_map_path,
                figure_dir=self.figures,
                canonical_sections_sha256="not-a-digest",
            )


class SourceInventoryProposalTests(unittest.TestCase):
    @staticmethod
    def figure(ordinal, bbox, digest="same"):
        return source_inventory.FigureObservation(
            page=4,
            ordinal=ordinal,
            xref=10,
            digest=digest,
            width=20,
            height=20,
            bbox=bbox,
        )

    def test_duplicate_heuristic_is_only_a_proposal_helper(self):
        overlap = self.figure(2, (2, 2, 102, 102))
        kept, exclusions = source_inventory.collapse_duplicate_draws(
            [self.figure(1, (0, 0, 100, 100)), overlap]
        )
        self.assertEqual([item.filename for item in kept], ["p004-1.png"])
        self.assertEqual(exclusions[0]["filename"], "p004-2.png")

        separated = self.figure(2, (200, 200, 300, 300))
        kept, exclusions = source_inventory.collapse_duplicate_draws(
            [self.figure(1, (0, 0, 100, 100)), separated]
        )
        self.assertEqual(len(kept), 2)
        self.assertEqual(exclusions, [])


class CurrentCorpusInventoryTests(unittest.TestCase):
    EXPECTED: ClassVar = {
        "anthropic/claude-fable-5": (317, 7, 309, 153, 152, 151, 1, 151),
        "anthropic/claude-opus-5": (198, 5, 192, 101, 101, 100, 0, 100),
        "anthropic/risk-report-2026-08": (186, 5, 180, 15, 15, 14, 0, 14),
    }

    def test_all_current_cards_have_zero_source_inventory_findings(self):
        for card_id, expected in self.EXPECTED.items():
            with self.subTest(card=card_id):
                card = REPO / "cards" / card_id
                manifest = (card / "style-manifest.yaml").read_text()
                match = re.search(
                    r"^\s*toc_pages:\s*\[([^]]*)\]", manifest, re.MULTILINE
                )
                claimed_toc = {
                    int(value) for value in match.group(1).split(",") if value.strip()
                }
                claimed_map = json.loads(
                    (card / "extracted/figures-map.json").read_text()
                )
                report = source_inventory.verify(
                    card / "source.pdf",
                    inventory=card / "source-inventory.json",
                    claimed_toc_pages=claimed_toc,
                    claimed_figure_map=claimed_map,
                    figure_dir=card / "assets/figures",
                )
                self.assertEqual(report.flags, [], f"{card_id}: {report.flags}")
                (
                    source_pages,
                    toc_pages,
                    content_pages,
                    raw,
                    visual,
                    projectable,
                    duplicates,
                    output,
                ) = expected
                self.assertEqual(report.stats["source_pages"], source_pages)
                self.assertEqual(report.stats["cover_pages"], 1)
                self.assertEqual(report.stats["toc_pages"], toc_pages)
                self.assertEqual(report.stats["content_pages"], content_pages)
                self.assertEqual(report.stats["raw_source_figures"], raw)
                self.assertEqual(report.stats["visual_source_figures"], visual)
                self.assertEqual(
                    report.stats["projectable_source_figures"], projectable
                )
                self.assertEqual(report.stats["duplicate_draw_exclusions"], duplicates)
                self.assertEqual(report.stats["required_output_figures"], output)


if __name__ == "__main__":
    unittest.main()
