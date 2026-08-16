"""Extract the fixed source-bound word-alignment cases."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(HERE.parent / "clean-model"), str(HERE)]

import table_candidate as model
from word_alignment import (
    WORD_SELECTION,
    GridEvidence,
    SourceWord,
    align_words,
    reassign_cell_text,
)

CASES = (
    ("opus-p52-t0", "cards/anthropic/claude-opus-5/source.pdf", 52, 0),
    ("opus-p53-t0", "cards/anthropic/claude-opus-5/source.pdf", 53, 0),
    ("opus-p56-t0", "cards/anthropic/claude-opus-5/source.pdf", 56, 0),
    ("opus-p56-t1", "cards/anthropic/claude-opus-5/source.pdf", 56, 1),
    ("risk-p78-t0", "cards/anthropic/risk-report-2026-08/source.pdf", 78, 0),
    ("risk-p79-t0", "cards/anthropic/risk-report-2026-08/source.pdf", 79, 0),
    ("risk-p80-t0", "cards/anthropic/risk-report-2026-08/source.pdf", 80, 0),
    ("fable-p20-t0", "cards/anthropic/claude-fable-5/source.pdf", 20, 0),
    ("fable-p94-t0", "cards/anthropic/claude-fable-5/source.pdf", 94, 0),
    ("fable-p95-t0", "cards/anthropic/claude-fable-5/source.pdf", 95, 0),
)
SOURCE_EVIDENCE = HERE / "evidence" / "source-word-evidence.json"
IMPLEMENTATION_FILES = (
    "docs/experiments/13-table-candidate-shadow/clean-model/table_candidate.py",
    "docs/experiments/13-table-candidate-shadow/word-alignment/word_alignment.py",
    "docs/experiments/13-table-candidate-shadow/word-alignment/extract_alignment_cases.py",
)


def _json(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mini_pdf(source: Path, page_number: int, output: Path) -> str:
    import pymupdf

    document = pymupdf.open(source)
    mini = pymupdf.open()
    mini.insert_pdf(document, from_page=page_number - 1, to_page=page_number - 1)
    mini.save(output, reproducible=True, no_new_id=True)
    mini.close()
    document.close()
    return _file_hash(output)


def _scalar(value: Any) -> str:
    return str(value.value if hasattr(value, "value") else value)


def _reviewed_cases() -> tuple[str, dict[str, Any]]:
    raw = SOURCE_EVIDENCE.read_bytes()
    artifact = json.loads(raw)
    if artifact["schema"] != "ai-system-cards/source-word-alignment-evidence/v1":
        raise ValueError("unexpected source-word evidence schema")
    return hashlib.sha256(raw).hexdigest(), {
        case["case_id"]: case for case in artifact["cases"]
    }


def load_reviewed_evidence(
    case: dict[str, Any], candidate: model.TableCandidate
) -> tuple[GridEvidence, tuple[tuple[float, ...], ...]]:
    source = case["source"]
    context = case["candidate_context"]
    if source["sha256"] != candidate.source.source_sha256:
        raise ValueError("reviewed evidence source hash differs from candidate")
    if source["page_number"] not in {
        region.page_number for region in candidate.source.regions
    }:
        raise ValueError("reviewed evidence page differs from candidate")
    if context["table_key"] != candidate.source.table_key:
        raise ValueError("reviewed evidence table key differs from candidate")
    if context["shape"] != [candidate.num_rows, candidate.num_columns]:
        raise ValueError("reviewed evidence shape differs from candidate")
    words = tuple(
        SourceWord(
            item["word_id"],
            item["ordinal"],
            item["text"],
            tuple(item["bbox"]),
            item["block"],
            item["line"],
            item["word"],
        )
        for item in case["words"]
    )
    geometry = case["geometry"]
    evidence = GridEvidence(
        source["document_id"],
        source["sha256"],
        source["page_number"],
        context["table_key"],
        tuple(geometry["x_edges"]),
        tuple(geometry["y_edges"]),
        words,
        "PyMuPDF 1.28.2:get_drawings+get_text(words,sort=True)",
        json.dumps(
            {
                "word_selection": WORD_SELECTION,
                "source_evidence_selection_policy": case["selection_policy"],
            }
        ),
    )
    return evidence, tuple(tuple(item) for item in geometry["horizontal_rules"])


def _source(
    document_id: str, source_hash: str, page_number: int, index: int, provenance: Any
) -> model.SourceProvenance:
    bbox = provenance.bbox
    return model.SourceProvenance(
        document_id,
        source_hash,
        f"p{page_number}:table-{index}",
        (
            model.SourceRegion(
                page_number,
                model.BBox(bbox.l, bbox.t, bbox.r, bbox.b, _scalar(bbox.coord_origin)),
                provenance.charspan[0],
                provenance.charspan[1],
            ),
        ),
    )


def _fixture(candidate: model.TableCandidate) -> dict[str, Any]:
    return {
        "source": candidate.source.to_dict(),
        "tool": candidate.tool.to_dict(),
        "docling_payload": candidate.diagnostic_docling_payload(),
        "candidate_sha256": hashlib.sha256(candidate.to_json_bytes()).hexdigest(),
    }


def load_candidate(raw: dict[str, Any]) -> model.TableCandidate:
    """Replay an artifact candidate without Docling installed."""

    source_raw = raw["source"]
    regions = []
    for region in source_raw["regions"]:
        bbox_raw = region["bbox"]
        bbox = (
            None
            if bbox_raw is None
            else model.BBox(
                bbox_raw["l"],
                bbox_raw["t"],
                bbox_raw["r"],
                bbox_raw["b"],
                bbox_raw["coord_origin"],
                json.dumps(bbox_raw["tool_fields"]),
            )
        )
        char_range = region["char_range"]
        regions.append(
            model.SourceRegion(
                region["page_number"],
                bbox,
                None if char_range is None else char_range[0],
                None if char_range is None else char_range[1],
            )
        )
    source = model.SourceProvenance(
        source_raw["document_id"],
        source_raw["source_sha256"],
        source_raw["table_key"],
        tuple(regions),
    )
    tool_raw = raw["tool"]
    tool = model.ToolProvenance(
        tool_raw["extractor_name"],
        tool_raw["extractor_version"],
        tool_raw["data_model_version"],
        tuple(tool_raw["model_artifacts"]),
        json.dumps(tool_raw["settings"]),
    )
    candidate = model.adapt_docling_table_data(
        raw["docling_payload"], source=source, tool=tool
    )
    if hashlib.sha256(candidate.to_json_bytes()).hexdigest() != raw["candidate_sha256"]:
        raise ValueError("fixture candidate hash mismatch")
    return candidate


def _table_result(
    case_id: str,
    table_index: int,
    table: Any,
    reviewed: dict[str, Any],
) -> dict[str, Any]:
    source = reviewed["source"]
    tool = model.ToolProvenance(
        "docling",
        importlib.metadata.version("docling"),
        importlib.metadata.version("docling-core"),
        (),
        json.dumps({"offline": True, "mini_pdf": "insert_pdf-reproducible-no_new_id"}),
    )
    candidate = model.adapt_docling_table_data(
        table.data,
        source=_source(
            source["document_id"],
            source["sha256"],
            source["page_number"],
            table_index,
            table.prov[0],
        ),
        tool=tool,
    )
    evidence, _ = load_reviewed_evidence(reviewed, candidate)
    alignment = align_words(candidate, evidence)
    result = reassign_cell_text(candidate, evidence)
    replay = reassign_cell_text(result.candidate, evidence)
    counts = {
        status: sum(item.status == status for item in alignment.assignments)
        for status in ("assigned", "adapter_gap", "ambiguous", "outside_grid")
    }
    return {
        "case_id": case_id,
        "classification": reviewed["classification"],
        "table_index": table_index,
        "candidate": _fixture(candidate),
        "source_evidence_case_id": case_id,
        "result": result.provenance_dict(),
        "assignment_counts": counts,
        "change_count": len(result.changes),
        "surface_only_count": len(result.surface_only_cell_ids),
        "idempotent": replay.status in {"noop", "blocked"}
        and replay.output_candidate_sha256 == result.output_candidate_sha256,
    }


def _extract_once(
    reviewed_cases: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    from docling.document_converter import DocumentConverter

    grouped: dict[tuple[str, int], list[tuple[str, int]]] = {}
    for case_id, relative, page, table_index in CASES:
        grouped.setdefault((relative, page), []).append((case_id, table_index))
    results = []
    mini_hashes = {}
    for (relative, page_number), selections in grouped.items():
        with tempfile.TemporaryDirectory(prefix=f"word-align-p{page_number}-") as tmp:
            mini = Path(tmp) / "page.pdf"
            mini_hashes[f"{relative}#page={page_number}"] = _mini_pdf(
                ROOT / relative, page_number, mini
            )
            document = DocumentConverter().convert(mini).document
        for case_id, table_index in selections:
            table = document.tables[table_index]
            if len(table.prov) != 1:
                raise ValueError("target table must have exactly one provenance region")
            results.append(
                _table_result(
                    case_id,
                    table_index,
                    table,
                    reviewed_cases[case_id],
                )
            )
    return results, mini_hashes


def run(runs: int) -> dict[str, Any]:
    if runs < 2:
        raise ValueError("live extraction determinism requires at least two runs")
    evidence_hash, reviewed_cases = _reviewed_cases()
    expected_ids = {case[0] for case in CASES}
    if set(reviewed_cases) != expected_ids:
        raise ValueError("CASES must exactly cover the independent evidence cases")
    paths = {relative: _file_hash(ROOT / relative) for _, relative, _, _ in CASES}
    for case_id, relative, _, _ in CASES:
        if paths[relative] != reviewed_cases[case_id]["source"]["sha256"]:
            raise ValueError(f"source hash drift for {case_id}")
    variants = [_extract_once(reviewed_cases) for _ in range(runs)]
    results = []
    for index, first in enumerate(variants[0][0]):
        hashes = [hashlib.sha256(_json(run[0][index])).hexdigest() for run in variants]
        results.append(
            {
                **first,
                "extraction_run_sha256": hashes,
                "extraction_deterministic": len(set(hashes)) == 1,
            }
        )
    mini_hashes = variants[0][1]
    if any(item[1] != mini_hashes for item in variants[1:]):
        raise AssertionError("reproducible mini-PDF hashes changed between runs")
    return {
        "schema": "ai-system-cards/word-alignment-cases/v1",
        "implementation_sha256": {
            path: _file_hash(ROOT / path) for path in IMPLEMENTATION_FILES
        },
        "source_sha256": paths,
        "source_word_evidence_sha256": evidence_hash,
        "mini_pdf_sha256": mini_hashes,
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("docling", "docling-core", "pymupdf")
        },
        "offline": {
            "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
            "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
        },
        "deterministic": all(case["extraction_deterministic"] for case in results),
        "cases": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=HERE / "artifacts" / "alignment-cases.json"
    )
    parser.add_argument("--runs", type=int, default=2)
    args = parser.parse_args()
    artifact = run(args.runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_json(artifact) + b"\n")
    print(
        f"wrote {args.output}: "
        f"{sum(case['change_count'] for case in artifact['cases'])} changes"
    )
    return 0 if artifact["deterministic"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
