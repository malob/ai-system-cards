"""Build the compact origin/projection replay from checked-in source artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [
    str(HERE.parent / "clean-model"),
    str(HERE.parent / "word-alignment"),
    str(HERE),
]

from extract_alignment_cases import load_candidate
from origin_projection import (
    ClaimCell,
    ClaimPlane,
    GridRange,
    RuleSegment,
    SourcePlane,
    SourceWord,
    classify_bounded_slot,
    resolve_overlay,
)

SOURCE_WORDS = HERE.parent / "word-alignment" / "evidence" / "source-word-evidence.json"
ALIGNMENT = HERE.parent / "word-alignment" / "artifacts" / "alignment-cases.json"
ORIGIN_EVIDENCE = HERE / "evidence" / "origin-projection-evidence.json"
IMPLEMENTATION = (HERE / "origin_projection.py", HERE / "build_replay.py")


def _bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()


def _inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    words, alignment, origin = (
        json.loads(path.read_bytes())
        for path in (SOURCE_WORDS, ALIGNMENT, ORIGIN_EVIDENCE)
    )
    declared = origin["inputs"]
    if _hash(SOURCE_WORDS) != declared["source_word_evidence"]["sha256"]:
        raise ValueError("origin evidence does not bind current source-word evidence")
    if _hash(ALIGNMENT) != declared["word_alignment_artifact"]["sha256"]:
        raise ValueError("origin evidence does not bind current alignment artifact")
    if words["schema"] != "ai-system-cards/source-word-alignment-evidence/v1":
        raise ValueError("unexpected source-word schema")
    if alignment["schema"] != "ai-system-cards/word-alignment-cases/v1":
        raise ValueError("unexpected alignment schema")
    if origin["schema"] != "ai-system-cards/origin-projection-source-evidence/v1":
        raise ValueError("unexpected origin evidence schema")
    return words, alignment, origin


def load_planes() -> dict[str, tuple[SourcePlane, ClaimPlane]]:
    words_artifact, alignment_artifact, origin_artifact = _inputs()
    evidence_hash = _hash(ORIGIN_EVIDENCE)
    word_hash = _hash(SOURCE_WORDS)
    words_by_id = {case["case_id"]: case for case in words_artifact["cases"]}
    claims_by_id = {case["case_id"]: case for case in alignment_artifact["cases"]}
    rules_by_id = {
        case["case_id"]: case for case in origin_artifact["rule_topology_cases"]
    }
    if set(words_by_id) != set(claims_by_id) or set(words_by_id) != set(rules_by_id):
        raise ValueError("the three inputs must cover the same cases")
    result = {}
    for case_id in sorted(words_by_id):
        words_raw, claim_raw, rule_raw = (
            words_by_id[case_id],
            claims_by_id[case_id],
            rules_by_id[case_id],
        )
        candidate = load_candidate(claim_raw["candidate"])
        source = words_raw["source"]
        context = rule_raw["candidate_conditioned_grid"]
        if context["table_key"] != candidate.source.table_key or context["shape"] != [
            candidate.num_rows,
            candidate.num_columns,
        ]:
            raise ValueError(f"grid/candidate mismatch for {case_id}")
        if source["sha256"] != candidate.source.source_sha256 or source[
            "page_number"
        ] not in {region.page_number for region in candidate.source.regions}:
            raise ValueError(f"source/candidate mismatch for {case_id}")
        candidate_sha256 = hashlib.sha256(candidate.to_json_bytes()).hexdigest()
        if candidate_sha256 != claim_raw["candidate"]["candidate_sha256"]:
            raise ValueError(f"candidate bytes/hash mismatch for {case_id}")
        rules = tuple(
            [
                RuleSegment("horizontal", y, start, end)
                for start, y, end in rule_raw["raw_horizontal_segments"]
            ]
            + [
                RuleSegment("vertical", x, start, end)
                for x, start, end in rule_raw["raw_vertical_segments"]
            ]
        )
        source_plane = SourcePlane(
            case_id,
            source["document_id"],
            source["sha256"],
            source["page_number"],
            context["table_key"],
            context["shape"][0],
            context["shape"][1],
            tuple(context["x_edges"]),
            tuple(context["y_edges"]),
            tuple(
                SourceWord(
                    item["word_id"],
                    item["ordinal"],
                    item["text"],
                    tuple(item["bbox"]),
                    json.dumps(item["source_features"]),
                )
                for item in words_raw["words"]
            ),
            rules,
            word_hash,
            evidence_hash,
            rule_raw["rule_tolerance_points"],
            rule_raw["full_bbox_assignment"]["containment_tolerance_points"],
        )
        claim_plane = ClaimPlane(
            case_id,
            candidate.source.document_id,
            candidate.source.source_sha256,
            source["page_number"],
            candidate.source.table_key,
            candidate.num_rows,
            candidate.num_columns,
            candidate_sha256,
            json.dumps(candidate.tool.to_dict()),
            tuple(
                ClaimCell(
                    cell.cell_id,
                    GridRange(
                        cell.row_start, cell.row_end, cell.column_start, cell.column_end
                    ),
                    cell.text,
                    "adapter_gap" if cell.adapter_generated else "observed",
                    json.dumps(cell.to_dict()),
                )
                for cell in candidate.cells
            ),
        )
        result[case_id] = (source_plane, claim_plane)
    return result


def build_artifact() -> dict[str, Any]:
    _, _, origin_artifact = _inputs()
    cases = []
    for case_id, (source, claims) in load_planes().items():
        result = resolve_overlay(source, claims)
        ranges = [item.range.to_list() for item in result.components]
        assignments = [item.to_dict() for item in result.associations]
        cases.append(
            {
                "case_id": case_id,
                "status": result.status,
                "reason": result.reason,
                "source_plane_sha256": result.source_plane_sha256,
                "claim_plane_sha256": result.claim_plane_sha256,
                "candidate_sha256": result.input_candidate_sha256,
                "candidate_unchanged": result.input_candidate_sha256
                == result.output_candidate_sha256,
                "component_count": len(result.components),
                "component_ranges_sha256": _digest(ranges),
                "association_count": len(assignments),
                "association_sha256": _digest(assignments),
                "conflict_counts": {
                    kind: sum(item.kind == kind for item in result.conflicts)
                    for kind in sorted({item.kind for item in result.conflicts})
                },
                "result_sha256": result.sha256,
            }
        )
    source_only = []
    for control in origin_artifact["source_only_controls"]:
        horizontal = control["required_horizontal_segments"]
        vertical = control["required_vertical_segments"]
        classification = classify_bounded_slot(
            control["source_word_overlap_count"],
            (
                bool(horizontal[0]),
                bool(horizontal[1]),
                bool(vertical[0]),
                bool(vertical[1]),
            ),
        )
        source_only.append(
            {
                "case_id": control["case_id"],
                "classification": classification,
                "extractor_origin": "unknown-no-typed-candidate",
                "source_sha256": control["source"]["sha256"],
            }
        )
    return {
        "schema": "ai-system-cards/origin-projection-replay/v1",
        "implementation_sha256": {
            str(path.relative_to(ROOT)): _hash(path) for path in IMPLEMENTATION
        },
        "input_sha256": {
            str(path.relative_to(ROOT)): _hash(path)
            for path in (SOURCE_WORDS, ALIGNMENT, ORIGIN_EVIDENCE)
        },
        "cases": cases,
        "source_only_controls": source_only,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "artifacts" / "origin-projection-replay.json",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_bytes(artifact) + b"\n")
    print(f"wrote {args.output}: {len(artifact['cases'])} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
