"""Probe whether a rich Docling table candidate is replayable.

This is experiment-only code.  It deliberately does not import the production
generator or read its legacy ``{bbox, html}`` cache.

The probe extracts one source page twice with fresh ``DocumentConverter``
instances, serializes the public Docling ``TableData`` model without flattening
it to HTML, and compares canonical hashes.  Its envelope binds the result to the
source PDF, extraction recipe, package versions, effective pipeline options,
Docling schema, and immutable model snapshots/artifact bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "ai-system-cards/docling-repro-probe"
REPORT_SCHEMA_VERSION = 2
CANDIDATE_SCHEMA = "ai-system-cards/raw-docling-table-candidate"
CANDIDATE_SCHEMA_VERSION = 2
CANONICAL_JSON_VERSION = "json-sort-keys-utf8-no-nan-v1"

PACKAGE_DISTRIBUTIONS = (
    "docling",
    "docling-core",
    "docling-ibm-models",
    "docling-parse",
    "pymupdf",
    "pydantic",
    "torch",
    "transformers",
    "safetensors",
    "huggingface-hub",
    "numpy",
    "pillow",
    "rapidocr",
)


class ProvenanceError(RuntimeError):
    """The initialized runtime cannot be bound to identifiable artifact bytes."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Return the byte representation used for every compared digest.

    JSON object keys are sorted, list order is significant, Unicode is encoded
    directly as UTF-8, insignificant whitespace is absent, and NaN/Infinity are
    rejected.  A trailing newline is a file convention and is not hashed.
    """

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _relative_files(root: Path) -> Iterable[Path]:
    """Yield regular files in lexical path order, following snapshot symlinks."""

    return sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def artifact_manifest(root: Path) -> dict[str, Any]:
    """Hash an inference artifact tree without recording machine-local paths."""

    if not root.is_dir():
        raise FileNotFoundError(f"artifact directory does not exist: {root}")
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in _relative_files(root)
    ]
    manifest = {"files": files}
    return {
        **manifest,
        "file_count": len(files),
        "total_size": sum(item["size"] for item in files),
        "manifest_sha256": canonical_sha256(manifest),
    }


def package_versions(
    distributions: Sequence[str] = PACKAGE_DISTRIBUTIONS,
) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in distributions:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def probe_implementation_binding() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {"filename": path.name, "sha256": sha256_file(path)}


def _qualified_name(value: object) -> str:
    cls = value if isinstance(value, type) else type(value)
    return f"{cls.__module__}.{cls.__qualname__}"


def effective_pdf_pipeline() -> dict[str, Any]:
    """Serialize defaults plus the effective model choices hidden by defaults."""

    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter
    from docling.utils.accelerator_utils import decide_device

    converter = DocumentConverter()
    format_option = converter.format_to_options[InputFormat.PDF]
    options = format_option.pipeline_options
    table_options = options.table_structure_options
    layout_options = options.layout_options
    layout_model_spec = layout_options.model_spec

    value = options.model_dump(mode="json")
    # Some Docling option types encode their discriminator and effective defaults
    # as ClassVars/custom serializers, so ``model_dump`` alone is insufficient
    # provenance.  Record those choices explicitly.
    value["effective"] = {
        "format_option_class": _qualified_name(format_option),
        "pipeline_class": _qualified_name(format_option.pipeline_cls),
        "resolved_accelerator_device": decide_device(
            options.accelerator_options.device
        ),
        "layout": {
            "options_class": _qualified_name(layout_options),
            "kind": getattr(layout_options, "kind", None),
            "model": {
                "name": layout_model_spec.name,
                "repo_id": layout_model_spec.repo_id,
                "revision": layout_model_spec.revision,
            },
            "keep_empty_clusters": layout_options.keep_empty_clusters,
            "skip_cell_assignment": layout_options.skip_cell_assignment,
            "create_orphan_clusters": layout_options.create_orphan_clusters,
        },
        "table_structure": {
            "options_class": _qualified_name(table_options),
            "kind": getattr(table_options, "kind", None),
            "do_cell_matching": table_options.do_cell_matching,
            "mode": table_options.mode.value,
        },
        "ocr_options_class": _qualified_name(options.ocr_options),
    }
    return value


def table_schema_binding() -> dict[str, Any]:
    from docling_core.types.doc import DoclingDocument, TableData

    schema = TableData.model_json_schema()
    return {
        "docling_document_schema_name": DoclingDocument.model_fields[
            "schema_name"
        ].default,
        "docling_document_schema_version": DoclingDocument.model_fields[
            "version"
        ].default,
        "table_data_class": _qualified_name(TableData),
        "table_data_json_schema_sha256": canonical_sha256(schema),
        "table_data_json_schema": schema,
    }


def _path(value: object | None) -> Path | None:
    if value is None:
        return None
    return Path(value).expanduser()


def _resolved_path(value: object | None) -> Path | None:
    path = _path(value)
    return None if path is None else path.resolve()


def _path_text(value: object | None) -> str | None:
    path = _resolved_path(value)
    return None if path is None else str(path)


def effective_artifact_settings(
    pipeline: object,
    *,
    global_settings: object | None = None,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Bind Docling's two-level artifact-path resolution and relevant globals.

    ``BasePipeline`` gives the per-pipeline option priority over the process-wide
    ``DOCLING_ARTIFACTS_PATH`` setting.  Recompute that choice and reject a
    pipeline whose initialized path disagrees; merely recording the environment
    variable would miss option overrides and stale imported settings.
    """

    if global_settings is None:
        from docling.datamodel.settings import settings as global_settings

    if environment is None:
        environment = os.environ

    pipeline_options = getattr(pipeline, "pipeline_options", None)
    if pipeline_options is None:
        raise ProvenanceError("initialized pipeline has no pipeline_options")
    option_path = _resolved_path(getattr(pipeline_options, "artifacts_path", None))
    global_path = _resolved_path(getattr(global_settings, "artifacts_path", None))
    initialized_path = _resolved_path(getattr(pipeline, "artifacts_path", None))
    environment_value = environment.get("DOCLING_ARTIFACTS_PATH")
    environment_path = (
        None if environment_value is None else _resolved_path(environment_value)
    )
    if environment_value is not None and environment_path != global_path:
        raise ProvenanceError(
            "DOCLING_ARTIFACTS_PATH does not match the imported global setting: "
            f"environment={environment_path}, global_settings={global_path}"
        )
    expected_path = option_path if option_path is not None else global_path
    if initialized_path != expected_path:
        raise ProvenanceError(
            "initialized pipeline artifact path does not match effective settings: "
            f"initialized={initialized_path}, expected={expected_path}"
        )

    def dump_setting(name: str) -> Any:
        value = getattr(global_settings, name, None)
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        return value

    return {
        "pipeline_options_artifacts_path": _path_text(option_path),
        "global_settings_artifacts_path": _path_text(global_path),
        "initialized_artifacts_path": _path_text(initialized_path),
        "resolution_source": (
            "pipeline_options"
            if option_path is not None
            else "global_settings"
            if global_path is not None
            else "library_defaults"
        ),
        "environment_DOCLING_ARTIFACTS_PATH": environment_value,
        "global_cache_dir": _path_text(getattr(global_settings, "cache_dir", None)),
        "global_perf": dump_setting("perf"),
        "global_inference": dump_setting("inference"),
    }


def _relative_to(path: Path, root: Path) -> Path | None:
    try:
        return path.relative_to(root)
    except ValueError:
        return None


def bind_hf_artifact_directory(
    *,
    purpose: str,
    actual_path: Path,
    repo_id: str,
    artifact_subpath: Path = Path(),
    configured_artifacts_path: Path | None,
    allow_deprecated_unscoped_custom_path: bool = False,
) -> dict[str, Any]:
    """Match and hash the directory an initialized HF-backed stage used.

    For the library-managed flow, identity must be visible in the canonical
    Hugging Face ``models--ORG--REPO/snapshots/COMMIT`` path.  For an explicit
    Docling artifacts root, identity must match Docling's repo-scoped layout.
    This intentionally does not call ``snapshot_download`` or infer which
    branch *ought* to have been used.
    """

    actual = actual_path.expanduser().resolve()
    if not actual.is_dir():
        raise ProvenanceError(
            f"{purpose} initialized artifact is not a directory: {actual}"
        )
    if not repo_id or "/" not in repo_id:
        raise ProvenanceError(f"{purpose} has invalid repository identity: {repo_id!r}")

    repo_folder = repo_id.replace("/", "--")
    subpath = Path(artifact_subpath)
    if configured_artifacts_path is not None:
        configured = configured_artifacts_path.expanduser().resolve()
        candidates = [("repo_scoped", configured / repo_folder / subpath)]
        if allow_deprecated_unscoped_custom_path:
            candidates.append(("deprecated_unscoped", configured / subpath))
        matches = [
            (layout, candidate.resolve())
            for layout, candidate in candidates
            if candidate.resolve() == actual
        ]
        if len(matches) != 1:
            expected = ", ".join(str(candidate) for _, candidate in candidates)
            raise ProvenanceError(
                f"{purpose} initialized path {actual} does not match configured "
                f"artifact identity for {repo_id}; expected one of: {expected}"
            )
        custom_layout, _ = matches[0]
        storage = {
            "kind": "docling_artifacts_path",
            "layout": custom_layout,
            "configured_root": str(configured),
            "repo_folder": repo_folder,
            "resolved_revision": None,
        }
    else:
        repo_cache_folder = f"models--{repo_folder}"
        parts = actual.parts
        positions = [i for i, part in enumerate(parts) if part == repo_cache_folder]
        matches = []
        for index in positions:
            tail = parts[index:]
            if len(tail) < 3 or tail[1] != "snapshots" or not tail[2]:
                continue
            expected_tail = (repo_cache_folder, "snapshots", tail[2], *subpath.parts)
            if tuple(tail) == expected_tail:
                matches.append(tail[2])
        if len(matches) != 1:
            raise ProvenanceError(
                f"{purpose} initialized path {actual} cannot be matched to exactly "
                f"one {repo_id} Hugging Face snapshot with subpath {subpath.as_posix()!r}"
            )
        storage = {
            "kind": "huggingface_snapshot",
            "repo_cache_folder": repo_cache_folder,
            "resolved_revision": matches[0],
        }

    return {
        "purpose": purpose,
        "repo_id": repo_id,
        "artifact_subpath": subpath.as_posix() if subpath.parts else ".",
        "storage_identity": storage,
        "artifact_manifest": artifact_manifest(actual),
    }


def _loaded_transformers_model_path(engine: object) -> Path:
    model = getattr(engine, "_model", None)
    candidates: set[Path] = set()
    for target in (model, getattr(model, "_orig_mod", None)):
        if target is None:
            continue
        for value in (
            getattr(target, "name_or_path", None),
            getattr(getattr(target, "config", None), "_name_or_path", None),
        ):
            if value and Path(value).expanduser().is_dir():
                candidates.add(Path(value).expanduser().resolve())
    if len(candidates) != 1:
        raise ProvenanceError(
            "layout engine did not expose one unambiguous initialized model path: "
            f"{sorted(str(path) for path in candidates)}"
        )
    return next(iter(candidates))


def layout_model_binding(stage: object) -> dict[str, Any]:
    engine = getattr(stage, "engine", None)
    if engine is None or type(engine).__name__ != "TransformersObjectDetectionEngine":
        raise ProvenanceError(
            "unsupported initialized layout engine for byte provenance: "
            f"{_qualified_name(engine) if engine is not None else None}"
        )
    repo_id = getattr(engine, "_repo_id", None)
    model_config = getattr(engine, "_model_config", None)
    if not isinstance(repo_id, str) or model_config is None:
        raise ProvenanceError("layout engine lacks initialized repository metadata")
    binding = bind_hf_artifact_directory(
        purpose="layout_detection",
        actual_path=_loaded_transformers_model_path(engine),
        repo_id=repo_id,
        configured_artifacts_path=_path(getattr(engine, "_artifacts_path", None)),
    )
    binding["requested_revision"] = getattr(model_config, "revision", None) or "main"
    binding["engine_class"] = _qualified_name(engine)
    return binding


def _repo_id_from_folder(folder: object) -> str:
    if not isinstance(folder, str) or "--" not in folder:
        raise ProvenanceError(f"cannot derive repository identity from {folder!r}")
    owner, repository = folder.split("--", 1)
    if not owner or not repository:
        raise ProvenanceError(f"cannot derive repository identity from {folder!r}")
    return f"{owner}/{repository}"


def table_model_binding(stage: object, artifacts_path: Path | None) -> dict[str, Any]:
    if not getattr(stage, "enabled", False):
        return {"purpose": "table_structure", "enabled": False}
    config = getattr(stage, "tm_config", None)
    try:
        actual_path = Path(config["model"]["save_dir"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ProvenanceError(
            "initialized TableFormer stage lacks tm_config.model.save_dir"
        ) from exc
    repo_id = _repo_id_from_folder(getattr(stage, "_model_repo_folder", None))
    mode = getattr(stage, "mode", None)
    mode_value = mode.value if isinstance(mode, Enum) else str(mode)
    subpath = Path(getattr(stage, "_model_path", "")) / mode_value
    binding = bind_hf_artifact_directory(
        purpose="table_structure",
        actual_path=actual_path,
        repo_id=repo_id,
        artifact_subpath=subpath,
        configured_artifacts_path=artifacts_path,
        allow_deprecated_unscoped_custom_path=True,
    )
    binding.update(
        {
            "enabled": True,
            "mode": mode_value,
            "model_type": getattr(stage, "tm_model_type", None),
            "stage_class": _qualified_name(stage),
        }
    )
    return binding


def _file_manifest(path: Path) -> dict[str, Any]:
    actual = path.expanduser().resolve()
    if not actual.is_file():
        raise ProvenanceError(f"initialized artifact file does not exist: {actual}")
    return {
        "size": actual.stat().st_size,
        "sha256": sha256_file(actual),
    }


def _rapidocr_file_info(section: object) -> object:
    from rapidocr.inference_engine.base import FileInfo

    return FileInfo(
        engine_type=section.engine_type,
        ocr_version=section.ocr_version,
        task_type=section.task_type,
        lang_type=section.lang_type,
        model_type=section.model_type,
    )


def _rapidocr_model_path(component: object, section: object) -> tuple[Path, str]:
    configured = section.get("model_path", None)
    if configured is not None:
        return Path(configured), "explicit_or_docling_resolved"
    session = getattr(component, "session", None)
    if session is None or not hasattr(session, "get_model_url"):
        raise ProvenanceError("RapidOCR component has no initialized inference session")
    model_info = session.get_model_url(_rapidocr_file_info(section))
    model_url = model_info.get("model_dir") if isinstance(model_info, Mapping) else None
    model_root = section.get("model_root_dir", None)
    if not model_url or model_root is None:
        raise ProvenanceError("RapidOCR session cannot identify its loaded model file")
    return Path(model_root) / Path(model_url).name, "library_resolved"


def _assert_rapidocr_path_identity(
    *,
    path: Path,
    explicit_option: object | None,
    artifacts_path: Path | None,
    purpose: str,
) -> str:
    actual = path.expanduser().resolve()
    if explicit_option is not None:
        expected = Path(explicit_option).expanduser().resolve()
        if actual != expected:
            raise ProvenanceError(
                f"{purpose} path {actual} does not match explicit option {expected}"
            )
        return "explicit_option"
    if artifacts_path is not None:
        expected_root = (artifacts_path / "RapidOcr").expanduser().resolve()
        if _relative_to(actual, expected_root) is None:
            raise ProvenanceError(
                f"{purpose} path {actual} is outside configured RapidOCR root {expected_root}"
            )
        return "docling_artifacts_path"
    return "rapidocr_library_config"


def rapidocr_model_binding(
    stage: object, artifacts_path: Path | None
) -> dict[str, Any]:
    engine = getattr(stage, "_engine", None)
    if engine is None:
        engine = stage
    if type(engine).__name__ != "RapidOcrModel":
        raise ProvenanceError(
            "unsupported initialized OCR engine for byte provenance: "
            f"{_qualified_name(engine)}"
        )
    if not getattr(engine, "enabled", False):
        return {"purpose": "ocr", "enabled": False}
    reader = getattr(engine, "reader", None)
    cfg = getattr(reader, "cfg", None)
    if reader is None or cfg is None:
        raise ProvenanceError("RapidOCR engine lacks initialized reader configuration")

    options = getattr(engine, "options", None)
    components = (
        ("detection", "Det", "text_det", "det_model_path"),
        ("classification", "Cls", "text_cls", "cls_model_path"),
        ("recognition", "Rec", "text_rec", "rec_model_path"),
    )
    files = []
    for purpose, section_name, component_name, option_name in components:
        section = cfg[section_name]
        path, resolver = _rapidocr_model_path(getattr(reader, component_name), section)
        identity_source = _assert_rapidocr_path_identity(
            path=path,
            explicit_option=getattr(options, option_name, None),
            artifacts_path=artifacts_path,
            purpose=f"RapidOCR {purpose}",
        )
        files.append(
            {
                "purpose": purpose,
                "filename": path.name,
                "resolver": resolver,
                "identity_source": identity_source,
                "manifest": _file_manifest(path),
            }
        )

    recognition = reader.text_rec
    rec_section = cfg["Rec"]
    session = getattr(recognition, "session", None)
    if session is None:
        raise ProvenanceError("RapidOCR recognition component has no session")
    if session.have_key():
        dictionary = {
            "kind": "embedded_character_list",
            "character_list_sha256": canonical_sha256(session.get_character_list()),
        }
    else:
        dict_path = rec_section.get("rec_keys_path", None)
        resolver = "explicit_or_docling_resolved"
        if dict_path is None:
            from rapidocr.ch_ppocr_rec.main import DEFAULT_DICT_URL, DEFAULT_MODEL_PATH

            dict_url = session.get_dict_key_url(_rapidocr_file_info(rec_section))
            dict_url = dict_url if dict_url is not None else DEFAULT_DICT_URL
            dict_path = DEFAULT_MODEL_PATH / Path(dict_url).name
            resolver = "library_resolved"
        dict_path = Path(dict_path)
        dictionary = {
            "kind": "file",
            "filename": dict_path.name,
            "resolver": resolver,
            "identity_source": _assert_rapidocr_path_identity(
                path=dict_path,
                explicit_option=getattr(options, "rec_keys_path", None),
                artifacts_path=artifacts_path,
                purpose="RapidOCR recognition dictionary",
            ),
            "manifest": _file_manifest(dict_path),
        }

    backend = getattr(options, "backend", None)
    if isinstance(backend, Enum):
        backend = backend.value
    return {
        "purpose": "ocr",
        "enabled": True,
        "stage_class": _qualified_name(stage),
        "engine_class": _qualified_name(engine),
        "reader_class": _qualified_name(reader),
        "backend": backend,
        "model_root_dir": _path_text(cfg.Global.model_root_dir),
        "files": files,
        "recognition_dictionary": dictionary,
    }


def initialized_model_bindings(pipeline: object) -> list[dict[str, Any]]:
    artifacts_path = _path(getattr(pipeline, "artifacts_path", None))
    layout = getattr(pipeline, "layout_model", None)
    table = getattr(pipeline, "table_model", None)
    ocr = getattr(pipeline, "ocr_model", None)
    if layout is None or table is None or ocr is None:
        raise ProvenanceError(
            "initialized pipeline is missing layout, table, or OCR stage"
        )
    return [
        layout_model_binding(layout),
        table_model_binding(table, artifacts_path),
        rapidocr_model_binding(ocr, artifacts_path),
    ]


def build_single_page_pdf(
    source: Path, page_number: int, output: Path
) -> dict[str, Any]:
    """Reproduce production's one-page mini-PDF extraction recipe."""

    import pymupdf

    source_doc = pymupdf.open(source)
    if not 1 <= page_number <= source_doc.page_count:
        raise ValueError(
            f"page {page_number} outside source range 1..{source_doc.page_count}"
        )
    source_page = source_doc[page_number - 1]
    dimensions = [source_page.rect.width, source_page.rect.height]
    mini = pymupdf.open()
    mini.insert_pdf(source_doc, from_page=page_number - 1, to_page=page_number - 1)
    # Production currently calls ``save`` with defaults.  The first probe run
    # demonstrated that those bytes differ across identical runs because the
    # wrapper receives a fresh PDF ID.  PyMuPDF's reproducible mode removes that
    # irrelevant entropy while preserving the copied source page.
    mini.save(output, reproducible=True, no_new_id=True)
    mini.close()
    source_doc.close()
    return {
        "recipe": "pymupdf.insert_pdf-one-page-reproducible-no-new-id-save-v1",
        "source_page_number": page_number,
        "mini_pdf_page_number": 1,
        "page_dimensions_points": dimensions,
        "mini_pdf_sha256": sha256_file(output),
    }


def _model_dump(value: Any) -> Any:
    return value.model_dump(mode="json", by_alias=True)


def serialize_table_data(value: Any) -> dict[str, Any]:
    """Serialize declared TableData fields, never its computed ``grid`` view."""

    try:
        serialized = value.model_dump(
            mode="json",
            by_alias=True,
            exclude_computed_fields=True,
        )
    except TypeError as exc:
        raise ProvenanceError(
            "TableData serializer cannot exclude computed fields in this Docling schema"
        ) from exc
    if not isinstance(serialized, dict):
        raise ProvenanceError("TableData did not serialize to an object")
    if "grid" in serialized:
        raise ProvenanceError("computed TableData.grid leaked into raw candidate")
    return serialized


def _stage_binding(stage: object) -> dict[str, Any]:
    binding: dict[str, Any] = {"class": _qualified_name(stage)}
    for name in ("enabled", "scale", "do_cell_matching", "tm_model_type"):
        value = getattr(stage, name, None)
        if isinstance(value, (str, int, float, bool)) or value is None:
            binding[name] = value
    options = getattr(stage, "options", None)
    if options is not None and hasattr(options, "model_dump"):
        binding["options"] = options.model_dump(mode="json")
        binding["options_class"] = _qualified_name(options)
        binding["options_kind"] = getattr(options, "kind", None)
    engine = getattr(stage, "_engine", None)
    if engine is None:
        engine = getattr(stage, "engine", None)
    if engine is not None:
        binding["engine_class"] = _qualified_name(engine)
        engine_options = getattr(engine, "options", None)
        if engine_options is not None and hasattr(engine_options, "model_dump"):
            binding["engine_options"] = engine_options.model_dump(mode="json")
            binding["engine_options_class"] = _qualified_name(engine_options)
            binding["engine_options_kind"] = getattr(engine_options, "kind", None)
    return binding


def _initialized_pipeline(converter: object) -> object:
    pipelines = list(converter.initialized_pipelines.values())
    if len(pipelines) != 1:
        raise RuntimeError(f"expected one initialized pipeline, got {len(pipelines)}")
    return pipelines[0]


def _execution_binding(pipeline: object) -> dict[str, Any]:
    stage_names = (
        "preprocessing_model",
        "ocr_model",
        "layout_model",
        "layout_postprocessing_model",
        "table_model",
        "assemble_model",
        "reading_order_model",
        "heading_hierarchy_model",
    )
    return {
        "pipeline_class": _qualified_name(pipeline),
        "artifact_settings": effective_artifact_settings(pipeline),
        "stages": {
            name: _stage_binding(getattr(pipeline, name))
            for name in stage_names
            if getattr(pipeline, name, None) is not None
        },
    }


def extract_raw_candidate(
    source: Path, page_number: int
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
]:
    """Return (input binding, raw rich table candidate) for one fresh run."""

    from docling.document_converter import DocumentConverter

    with tempfile.TemporaryDirectory(prefix="docling-repro-") as tmp:
        mini_path = Path(tmp) / "source-page.pdf"
        input_binding = build_single_page_pdf(source, page_number, mini_path)
        converter = DocumentConverter()
        document = converter.convert(mini_path).document
        initialized_pipeline = _initialized_pipeline(converter)
        execution = _execution_binding(initialized_pipeline)
        models = initialized_model_bindings(initialized_pipeline)

    tables = []
    for index, table in enumerate(document.tables):
        tables.append(
            {
                "index": index,
                "self_ref": table.self_ref,
                "label": table.label.value,
                "provenance": [_model_dump(item) for item in table.prov],
                "data": serialize_table_data(table.data),
            }
        )
    candidate = {
        "schema_name": CANDIDATE_SCHEMA,
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "source_page_number": page_number,
        "docling_document": {
            "schema_name": document.schema_name,
            "schema_version": document.version,
        },
        "tables": tables,
    }
    return input_binding, candidate, execution, models


def compare_run_records(records: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    fields = ("mini_pdf_sha256", "candidate_sha256", "artifact_sha256")
    equality = {
        field: len({record[field] for record in records}) == 1 for field in fields
    }
    return {**equality, "all_equal": all(equality.values())}


def make_artifact(
    *,
    source: Path,
    source_sha256: str,
    input_binding: Mapping[str, Any],
    candidate: Mapping[str, Any],
    packages: Mapping[str, str],
    pipeline: Mapping[str, Any],
    execution: Mapping[str, Any],
    schema: Mapping[str, Any],
    models: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_name": REPORT_SCHEMA,
        "schema_version": REPORT_SCHEMA_VERSION,
        "canonical_json": CANONICAL_JSON_VERSION,
        "source": {
            # A repository-relative/card identity is metadata; replay authority
            # comes from content hash + page number, never an absolute path.
            "filename": source.name,
            "sha256": source_sha256,
            **input_binding,
        },
        "extractor": {
            "probe_implementation": probe_implementation_binding(),
            "packages": dict(packages),
            "pipeline": dict(pipeline),
            "pipeline_sha256": canonical_sha256(pipeline),
            "execution": dict(execution),
            "schema": dict(schema),
            "models": list(models),
        },
        "candidate": dict(candidate),
        "candidate_sha256": canonical_sha256(candidate),
    }


def run_probe(source: Path, page_number: int, runs: int = 2) -> dict[str, Any]:
    if runs < 2:
        raise ValueError("determinism probe requires at least two runs")
    if not source.is_file():
        raise FileNotFoundError(source)

    source_digest = sha256_file(source)
    packages = package_versions()
    pipeline = effective_pdf_pipeline()
    schema = table_schema_binding()
    artifacts = []
    records = []
    for run_index in range(runs):
        input_binding, candidate, execution, models = extract_raw_candidate(
            source, page_number
        )
        artifact = make_artifact(
            source=source,
            source_sha256=source_digest,
            input_binding=input_binding,
            candidate=candidate,
            packages=packages,
            pipeline=pipeline,
            execution=execution,
            schema=schema,
            models=models,
        )
        artifact_digest = canonical_sha256(artifact)
        artifacts.append(artifact)
        records.append(
            {
                "run": run_index + 1,
                "mini_pdf_sha256": input_binding["mini_pdf_sha256"],
                "candidate_sha256": artifact["candidate_sha256"],
                "artifact_sha256": artifact_digest,
            }
        )

    comparison = compare_run_records(records)
    report: dict[str, Any] = {
        "schema_name": f"{REPORT_SCHEMA}-determinism-report",
        "schema_version": REPORT_SCHEMA_VERSION,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "machine": platform.machine(),
            "python_hash_seed": os.environ.get("PYTHONHASHSEED", "UNSET"),
        },
        "artifact": artifacts[0],
        "runs": records,
        "comparison": comparison,
    }
    if not comparison["all_equal"]:
        # Preserve variants only on failure so a mismatch can be structurally
        # diffed without making successful reports needlessly repetitive.
        report["variant_artifacts"] = artifacts
    return report


def summarize_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the review-sized result from the canonical full report."""

    artifact = report["artifact"]
    candidate = artifact["candidate"]
    table_shapes = []
    for table in candidate["tables"]:
        data = table["data"]
        cells = data.get("table_cells", [])
        table_shapes.append(
            {
                "index": table["index"],
                "num_rows": data.get("num_rows"),
                "num_cols": data.get("num_cols"),
                "unique_cell_count": len(cells),
                "computed_grid_present": "grid" in data,
            }
        )

    model_summaries = []
    for binding in artifact["extractor"]["models"]:
        value = {
            key: binding[key]
            for key in (
                "purpose",
                "enabled",
                "repo_id",
                "requested_revision",
                "storage_identity",
                "backend",
            )
            if key in binding
        }
        manifest = binding.get("artifact_manifest")
        if manifest is not None:
            value["artifact_manifest_sha256"] = manifest["manifest_sha256"]
        if "files" in binding:
            value["files"] = [
                {
                    "purpose": item["purpose"],
                    "filename": item["filename"],
                    "sha256": item["manifest"]["sha256"],
                }
                for item in binding["files"]
            ]
        model_summaries.append(value)

    return {
        "schema_name": f"{REPORT_SCHEMA}-summary",
        "schema_version": REPORT_SCHEMA_VERSION,
        "derived_from": {
            "report_sha256": canonical_sha256(report),
            "report_schema_name": report["schema_name"],
            "report_schema_version": report["schema_version"],
        },
        "source": artifact["source"],
        "packages": artifact["extractor"]["packages"],
        "artifact_settings": artifact["extractor"]["execution"]["artifact_settings"],
        "models": model_summaries,
        "table_count": len(candidate["tables"]),
        "table_shapes": table_shapes,
        "candidate_sha256": artifact["candidate_sha256"],
        "artifact_sha256": report["runs"][0]["artifact_sha256"],
        "comparison": report["comparison"],
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("cards/anthropic/claude-fable-5/source.pdf"),
    )
    parser.add_argument("--page", type=int, default=20)
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="write a mechanically derived compact summary beside the full report",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = run_probe(args.source, args.page, args.runs)
    write_canonical_json(args.output, report)
    if args.summary_output is not None:
        write_canonical_json(args.summary_output, summarize_report(report))
    comparison = report["comparison"]
    print(
        f"wrote {args.output}: {len(report['artifact']['candidate']['tables'])} table(s); "
        f"candidate deterministic={comparison['candidate_sha256']}; "
        f"full artifact deterministic={comparison['artifact_sha256']}"
    )
    return 0 if comparison["all_equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
