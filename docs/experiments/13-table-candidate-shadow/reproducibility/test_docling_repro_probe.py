"""Dependency-free unit tests for the reproducibility envelope."""

from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name("docling_repro_probe.py")
SPEC = importlib.util.spec_from_file_location("docling_repro_probe", MODULE_PATH)
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CanonicalJsonTests(unittest.TestCase):
    def test_object_order_does_not_change_bytes_or_digest(self) -> None:
        left = {"z": [3, 2, 1], "a": "café"}
        right = {"a": "café", "z": [3, 2, 1]}
        self.assertEqual(
            probe.canonical_json_bytes(left), probe.canonical_json_bytes(right)
        )
        self.assertEqual(probe.canonical_sha256(left), probe.canonical_sha256(right))
        self.assertIn("café".encode(), probe.canonical_json_bytes(left))

    def test_list_order_is_significant(self) -> None:
        self.assertNotEqual(
            probe.canonical_sha256([1, 2]), probe.canonical_sha256([2, 1])
        )

    def test_non_finite_numbers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            probe.canonical_json_bytes({"bad": math.nan})

    def test_written_file_has_only_one_unhashed_trailing_newline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "value.json"
            value = {"b": 2, "a": 1}
            probe.write_canonical_json(output, value)
            self.assertEqual(
                output.read_bytes(), probe.canonical_json_bytes(value) + b"\n"
            )


class ArtifactManifestTests(unittest.TestCase):
    def test_manifest_is_content_bound_and_path_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "z.bin").write_bytes(b"z")
            (root / "nested").mkdir()
            (root / "nested" / "a.bin").write_bytes(b"a")
            first = probe.artifact_manifest(root)
            self.assertEqual(
                ["nested/a.bin", "z.bin"], [f["path"] for f in first["files"]]
            )
            self.assertEqual(2, first["file_count"])
            (root / "z.bin").write_bytes(b"changed")
            second = probe.artifact_manifest(root)
            self.assertNotEqual(first["manifest_sha256"], second["manifest_sha256"])


class ArtifactPathBindingTests(unittest.TestCase):
    def settings(self, artifacts_path: Path | None, cache_dir: Path) -> SimpleNamespace:
        return SimpleNamespace(
            artifacts_path=artifacts_path,
            cache_dir=cache_dir,
            perf={"page_batch_size": 4},
            inference={"compile_torch_models": True},
        )

    def test_global_artifacts_path_is_recorded_and_recomputed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            pipeline = SimpleNamespace(
                pipeline_options=SimpleNamespace(artifacts_path=None),
                artifacts_path=root,
            )
            result = probe.effective_artifact_settings(
                pipeline,
                global_settings=self.settings(root, root / "cache"),
                environment={"DOCLING_ARTIFACTS_PATH": str(root)},
            )
            self.assertEqual("global_settings", result["resolution_source"])
            self.assertEqual(str(root), result["initialized_artifacts_path"])
            self.assertEqual(str(root), result["environment_DOCLING_ARTIFACTS_PATH"])

    def test_default_to_custom_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            stale_pipeline = SimpleNamespace(
                pipeline_options=SimpleNamespace(artifacts_path=None),
                artifacts_path=None,
            )
            with self.assertRaises(probe.ProvenanceError):
                probe.effective_artifact_settings(
                    stale_pipeline,
                    global_settings=self.settings(root, root / "cache"),
                    environment={"DOCLING_ARTIFACTS_PATH": str(root)},
                )

    def test_environment_change_after_settings_import_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            default_pipeline = SimpleNamespace(
                pipeline_options=SimpleNamespace(artifacts_path=None),
                artifacts_path=None,
            )
            with self.assertRaises(probe.ProvenanceError):
                probe.effective_artifact_settings(
                    default_pipeline,
                    global_settings=self.settings(None, root / "cache"),
                    environment={"DOCLING_ARTIFACTS_PATH": str(root)},
                )

    def test_pipeline_option_overrides_global_setting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            option_root = root / "option"
            global_root = root / "global"
            option_root.mkdir()
            global_root.mkdir()
            pipeline = SimpleNamespace(
                pipeline_options=SimpleNamespace(artifacts_path=option_root),
                artifacts_path=option_root,
            )
            result = probe.effective_artifact_settings(
                pipeline,
                global_settings=self.settings(global_root, root / "cache"),
                environment={"DOCLING_ARTIFACTS_PATH": str(global_root)},
            )
            self.assertEqual("pipeline_options", result["resolution_source"])
            self.assertEqual(str(option_root), result["initialized_artifacts_path"])

    def test_custom_repo_scoped_model_path_is_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            actual = root / "owner--model" / "weights"
            actual.mkdir(parents=True)
            (actual / "model.bin").write_bytes(b"model")
            binding = probe.bind_hf_artifact_directory(
                purpose="test",
                actual_path=actual,
                repo_id="owner/model",
                artifact_subpath=Path("weights"),
                configured_artifacts_path=root,
            )
            self.assertEqual(
                "docling_artifacts_path", binding["storage_identity"]["kind"]
            )
            self.assertEqual(1, binding["artifact_manifest"]["file_count"])

    def test_wrong_default_hf_repository_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            actual = Path(tmp) / "models--wrong--model" / "snapshots" / "abc"
            actual.mkdir(parents=True)
            (actual / "model.bin").write_bytes(b"model")
            with self.assertRaises(probe.ProvenanceError):
                probe.bind_hf_artifact_directory(
                    purpose="test",
                    actual_path=actual,
                    repo_id="owner/model",
                    configured_artifacts_path=None,
                )


class TableDataSerializationTests(unittest.TestCase):
    class FakeTableData:
        def __init__(self, include_grid: bool = False) -> None:
            self.include_grid = include_grid
            self.kwargs = None

        def model_dump(self, **kwargs):
            self.kwargs = kwargs
            value = {"num_rows": 1, "num_cols": 1, "table_cells": []}
            if self.include_grid:
                value["grid"] = []
            return value

    def test_computed_fields_are_explicitly_excluded(self) -> None:
        value = self.FakeTableData()
        serialized = probe.serialize_table_data(value)
        self.assertNotIn("grid", serialized)
        self.assertIs(value.kwargs["exclude_computed_fields"], True)

    def test_grid_leak_fails_closed(self) -> None:
        with self.assertRaises(probe.ProvenanceError):
            probe.serialize_table_data(self.FakeTableData(include_grid=True))


class SummaryBindingTests(unittest.TestCase):
    def test_summary_is_bound_to_full_report_hash(self) -> None:
        report = {
            "schema_name": "report",
            "schema_version": 2,
            "artifact": {
                "source": {"filename": "source.pdf"},
                "candidate": {"tables": []},
                "candidate_sha256": "candidate",
                "extractor": {
                    "packages": {},
                    "models": [],
                    "execution": {"artifact_settings": {}},
                },
            },
            "runs": [{"artifact_sha256": "artifact"}],
            "comparison": {"all_equal": True},
        }
        summary = probe.summarize_report(report)
        self.assertEqual(
            probe.canonical_sha256(report),
            summary["derived_from"]["report_sha256"],
        )

    def test_checked_summary_is_mechanically_derived(self) -> None:
        directory = MODULE_PATH.parent
        report_path = directory / "probe-result-p20.json"
        summary_path = directory / "probe-result-summary.json"
        self.assertTrue(report_path.is_file())
        self.assertTrue(summary_path.is_file())
        report = json.loads(report_path.read_text())
        summary = json.loads(summary_path.read_text())
        self.assertEqual(probe.summarize_report(report), summary)
        self.assertEqual(
            probe.probe_implementation_binding(),
            report["artifact"]["extractor"]["probe_implementation"],
        )


class RunComparisonTests(unittest.TestCase):
    def record(
        self, candidate: str = "c", mini: str = "m", artifact: str = "a"
    ) -> dict:
        return {
            "mini_pdf_sha256": mini,
            "candidate_sha256": candidate,
            "artifact_sha256": artifact,
        }

    def test_equal_runs_pass(self) -> None:
        result = probe.compare_run_records([self.record(), self.record()])
        self.assertEqual(
            {
                "mini_pdf_sha256": True,
                "candidate_sha256": True,
                "artifact_sha256": True,
                "all_equal": True,
            },
            result,
        )

    def test_each_replay_boundary_can_fail_independently(self) -> None:
        for field in ("candidate", "mini", "artifact"):
            kwargs = {field: "different"}
            result = probe.compare_run_records([self.record(), self.record(**kwargs)])
            self.assertFalse(result["all_equal"])


if __name__ == "__main__":
    unittest.main()
