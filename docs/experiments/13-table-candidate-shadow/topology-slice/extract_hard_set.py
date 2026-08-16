"""Fresh offline Docling + PyMuPDF replay for the topology hard set."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
import tempfile
import unicodedata
from bisect import bisect_right
from collections.abc import Sequence
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(HERE.parent / "clean-model"), str(HERE)]

import table_candidate as model
from topology_reconcile import RuleEvidence, reconcile_missing_header_rules

CASES = (
    ("opus-p52", "cards/anthropic/claude-opus-5/source.pdf", 52),
    ("opus-p56", "cards/anthropic/claude-opus-5/source.pdf", 56),
    ("risk-p78", "cards/anthropic/risk-report-2026-08/source.pdf", 78),
    ("risk-p79", "cards/anthropic/risk-report-2026-08/source.pdf", 79),
    ("risk-p80", "cards/anthropic/risk-report-2026-08/source.pdf", 80),
    ("fable-p95", "cards/anthropic/claude-fable-5/source.pdf", 95),
)
IMPLEMENTATION_FILES = (
    "docs/experiments/13-table-candidate-shadow/clean-model/table_candidate.py",
    "docs/experiments/13-table-candidate-shadow/topology-slice/topology_reconcile.py",
    "docs/experiments/13-table-candidate-shadow/topology-slice/extract_hard_set.py",
)


def _json(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value)).hexdigest()


def _file_digest(path: Path) -> str:
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
    return _file_digest(output)


def _scalar(value: Any) -> str:
    return str(value.value if hasattr(value, "value") else value)


def _cluster(values: list[float], tolerance: float = 1.5) -> tuple[float, ...]:
    clusters: list[list[float]] = []
    for value in sorted(values):
        if (
            not clusters
            or abs(value - sum(clusters[-1]) / len(clusters[-1])) > tolerance
        ):
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return tuple(round(sum(items) / len(items), 6) for items in clusters)


def _top_left_bbox(provenance: Any, height: float) -> tuple[float, float, float, float]:
    bbox = provenance.bbox
    if _scalar(bbox.coord_origin).upper() == "BOTTOMLEFT":
        return bbox.l, height - bbox.t, bbox.r, height - bbox.b
    return bbox.l, bbox.t, bbox.r, bbox.b


def _evidence(
    source: Path,
    source_sha256: str,
    page_number: int,
    provenance: Any,
    rows: int,
    columns: int,
) -> RuleEvidence:
    import pymupdf

    document = pymupdf.open(source)
    page = document[page_number - 1]
    left, top, right, bottom = _top_left_bbox(provenance, page.rect.height)
    width, height = right - left, bottom - top
    vertical: list[float] = []
    horizontal: list[tuple[float, float, float]] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "l":
                continue
            start, end = item[1], item[2]
            x0, x1 = sorted((float(start.x), float(end.x)))
            y0, y1 = sorted((float(start.y), float(end.y)))
            if (
                abs(start.y - end.y) <= 0.5
                and x1 - x0 >= width * 0.40
                and top - 3 <= y0 <= bottom + 3
                and x1 >= left - 3
                and x0 <= right + 3
            ):
                horizontal.append((round(x0, 6), round((y0 + y1) / 2, 6), round(x1, 6)))
            elif (
                abs(start.x - end.x) <= 0.5
                and y1 - y0 >= height * 0.18
                and left - 3 <= x0 <= right + 3
                and y1 >= top - 3
                and y0 <= bottom + 3
            ):
                vertical.append((x0 + x1) / 2)
    x_edges = _cluster(vertical)
    y_edges = _cluster([item[1] for item in horizontal])
    if len(x_edges) != columns + 1 or len(y_edges) != rows + 1:
        raise ValueError(f"ruling edge mismatch on source page {page_number}")
    words = []
    for x0, y0, x1, y1, text, *_ in page.get_text("words", sort=True):
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        if x_edges[0] < center_x < x_edges[-1] and y_edges[0] < center_y < y_edges[-1]:
            words.append((text, round(center_x, 6), round(center_y, 6)))
    document.close()
    return RuleEvidence(
        source_sha256,
        page_number,
        x_edges,
        y_edges,
        tuple(horizontal),
        tuple(words),
        f"PyMuPDF {importlib.metadata.version('pymupdf')}:get_drawings+get_text(words)",
    )


def _source(
    page_number: int, relative: str, source_hash: str, table_index: int, prov: Any
) -> model.SourceProvenance:
    bbox = prov.bbox
    return model.SourceProvenance(
        document_id=relative,
        source_sha256=source_hash,
        table_key=f"p{page_number}:table-{table_index}",
        regions=(
            model.SourceRegion(
                page_number,
                model.BBox(bbox.l, bbox.t, bbox.r, bbox.b, _scalar(bbox.coord_origin)),
                prov.charspan[0],
                prov.charspan[1],
            ),
        ),
    )


def _normalized(value: str) -> str:
    value = "".join(c for c in value if unicodedata.category(c) != "Cf")
    return " ".join(value.split())


def _text_mismatches(
    candidate: model.TableCandidate, evidence: RuleEvidence
) -> dict[str, Any]:
    grid = candidate.grid_cell_ids()
    assigned: dict[str, list[str]] = {cell.cell_id: [] for cell in candidate.cells}
    for word, center_x, center_y in evidence.words:
        column = bisect_right(evidence.x_edges, center_x) - 1
        row = bisect_right(evidence.y_edges, center_y) - 1
        assigned[grid[row][column]].append(word)
    mismatches = []
    for cell in candidate.cells:
        pdf_text = " ".join(assigned[cell.cell_id])
        if _normalized(pdf_text) != _normalized(cell.text):
            mismatches.append(
                {
                    "range": [
                        cell.row_start,
                        cell.row_end,
                        cell.column_start,
                        cell.column_end,
                    ],
                    "typed": cell.text,
                    "pdf": pdf_text,
                }
            )
    return {"count": len(mismatches), "examples": mismatches[:3]}


def _cell(cell: model.TableCell) -> dict[str, Any]:
    return {
        "range": [cell.row_start, cell.row_end, cell.column_start, cell.column_end],
        "text": cell.text,
        "roles": list(cell.header_roles),
        "adapter_generated": cell.adapter_generated,
    }


def _extract(case: tuple[str, str, int]) -> dict[str, Any]:
    from docling.document_converter import DocumentConverter

    case_id, relative, page_number = case
    source_path, source_hash = ROOT / relative, _file_digest(ROOT / relative)
    with tempfile.TemporaryDirectory(prefix=f"topology-{case_id}-") as tmp:
        mini = Path(tmp) / "page.pdf"
        mini_hash = _mini_pdf(source_path, page_number, mini)
        document = DocumentConverter().convert(mini).document
    tool = model.ToolProvenance(
        "docling",
        importlib.metadata.version("docling"),
        importlib.metadata.version("docling-core"),
        (),
        {"offline": True, "mini_pdf": "insert_pdf-reproducible-no_new_id"},
    )
    tables = []
    for index, table in enumerate(document.tables):
        if len(table.prov) != 1:
            raise ValueError(
                "hard-set table unexpectedly has multiple provenance regions"
            )
        candidate = model.adapt_docling_table_data(
            table.data,
            source=_source(page_number, relative, source_hash, index, table.prov[0]),
            tool=tool,
        )
        evidence = _evidence(
            source_path,
            source_hash,
            page_number,
            table.prov[0],
            candidate.num_rows,
            candidate.num_columns,
        )
        result = reconcile_missing_header_rules(candidate, evidence)
        before = {cell.cell_id: cell for cell in candidate.cells}
        after = {cell.cell_id: cell for cell in result.candidate.cells}
        decisions = []
        for decision in result.decisions:
            snapshot = decision.to_dict()
            upper = before[decision.upper_cell_id]
            snapshot.update(
                {
                    "upper_before": _cell(upper),
                    "lower_before": [
                        _cell(before[item]) for item in decision.lower_cell_ids
                    ],
                    "upper_after": _cell(after[decision.output_cell_id])
                    if decision.output_cell_id
                    else None,
                    "boundary_rule_mask": [
                        evidence.has_rule(decision.boundary_row, column)
                        for column in range(candidate.num_columns)
                    ],
                }
            )
            decisions.append(snapshot)
        tables.append(
            {
                "table_index": index,
                "shape": [candidate.num_rows, candidate.num_columns],
                "input_cell_count": len(candidate.cells),
                "output_cell_count": len(result.candidate.cells),
                "input_candidate_sha256": result.input_sha256,
                "evidence_sha256": result.evidence_sha256,
                "output_candidate_sha256": result.output_sha256,
                "rule_masks": [
                    [
                        evidence.has_rule(row, column)
                        for column in range(candidate.num_columns)
                    ]
                    for row in range(1, candidate.num_rows)
                ],
                "text_slots_before": _text_mismatches(candidate, evidence),
                "text_slots_after": _text_mismatches(result.candidate, evidence),
                "decisions": decisions,
                "invariants": result.provenance_dict()["invariants"],
            }
        )
    return {
        "case_id": case_id,
        "source": {"path": relative, "page": page_number, "sha256": source_hash},
        "mini_pdf_sha256": mini_hash,
        "tables": tables,
    }


def run(runs: int) -> dict[str, Any]:
    if runs < 2:
        raise ValueError("determinism replay needs at least two runs")
    cases = []
    for case in CASES:
        variants = [_extract(case) for _ in range(runs)]
        hashes = [_digest(item) for item in variants]
        cases.append(
            {
                **variants[0],
                "run_sha256": hashes,
                "deterministic": len(set(hashes)) == 1,
            }
        )
    return {
        "schema": "ai-system-cards/typed-topology-hard-set-summary/v2",
        "implementation_sha256": {
            path: _file_digest(ROOT / path) for path in IMPLEMENTATION_FILES
        },
        "offline": {
            "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
            "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
        },
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("docling", "docling-core", "pymupdf")
        },
        "deterministic": all(case["deterministic"] for case in cases),
        "cases": cases,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument(
        "--output", type=Path, default=HERE / "artifacts" / "hard-set.json"
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    artifact = run(args.runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_json(artifact) + b"\n")
    decisions = [
        item
        for case in artifact["cases"]
        for table in case["tables"]
        for item in table["decisions"]
    ]
    print(
        f"wrote {args.output}: deterministic={artifact['deterministic']}, "
        f"merged={sum(item['status'] == 'merged' for item in decisions)}, "
        f"blocked={sum(item['status'] == 'blocked' for item in decisions)}"
    )
    return 0 if artifact["deterministic"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
