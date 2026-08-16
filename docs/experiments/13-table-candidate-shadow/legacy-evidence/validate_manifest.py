#!/usr/bin/env python3
"""Validate the legacy table evidence manifest and replayable cache slices."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
MANIFEST = HERE / "manifest.json"
INSPECTOR = HERE / "inspect_legacy_passes.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def raw_entry_sha256(entry: dict) -> str:
    data = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(data)


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def table_locator(path: Path, index: int) -> dict:
    text = path.read_text()
    tables = list(re.finditer(r"<table>.*?</table>", text, re.DOTALL))
    if not 0 <= index < len(tables):
        raise AssertionError(
            f"{path}: table_index {index} outside 0..{len(tables) - 1}"
        )
    match = tables[index]
    line_start = text.count("\n", 0, match.start()) + 1
    line_end = text.count("\n", 0, match.end()) + 1
    prior_markers = list(re.finditer(r"<!-- p\.(\d+) -->", text[: match.start()]))
    pages = [int(prior_markers[-1].group(1))] if prior_markers else []
    pages.extend(map(int, re.findall(r"<!-- p\.(\d+) -->", match.group(0))))
    caption_match = re.search(
        r"\*\*\[Table ([^\]]+)\][^\n]*", text[match.end() : match.end() + 1500]
    )
    return {
        "line_start": line_start,
        "line_end": line_end,
        "source_pages": pages,
        "caption": caption_match.group(1) if caption_match else None,
        "table_sha256": sha256_bytes(match.group(0).encode()),
    }


def run_inspector(
    card: str,
    fixture: Path,
    pages: list[int],
    logical: bool = False,
    compare_production: bool = False,
):
    env = dict(os.environ)
    env["CARD"] = card
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(INSPECTOR), "--fixture", str(fixture)]
    if logical:
        cmd.append("--logical")
    if compare_production:
        cmd.append("--compare-production")
    cmd.extend(map(str, pages))
    proc = subprocess.run(
        cmd, cwd=REPO, env=env, check=True, text=True, capture_output=True
    )
    return json.loads(proc.stdout)


def check_equal(errors: list[str], label: str, actual, expected) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    errors: list[str] = []
    warnings: list[str] = []

    capture_files = {
        "tables_py_sha256": REPO / "pipeline/generate/tables.py",
        "run_py_sha256": REPO / "pipeline/generate/run.py",
    }
    for field, path in capture_files.items():
        check_equal(errors, str(path), sha256_file(path), manifest["capture"][field])

    fixtures: dict[str, dict] = {}
    fixture_cards: dict[str, str] = {}
    production_cache_available: dict[str, bool] = {}
    for card, source in manifest["sources"].items():
        pdf = REPO / source["source_pdf"]
        fixture_path = REPO / source["fixture"]
        check_equal(errors, str(pdf), sha256_file(pdf), source["source_pdf_sha256"])
        check_equal(
            errors,
            str(fixture_path),
            sha256_file(fixture_path),
            source["fixture_sha256"],
        )
        fixture = json.loads(fixture_path.read_text())
        fixtures[source["fixture"]] = fixture
        fixture_cards[source["fixture"]] = card
        check_equal(errors, f"{fixture_path}:card", fixture["card"], card)
        check_equal(
            errors,
            f"{fixture_path}:source_pdf_sha256",
            fixture["source_pdf_sha256"],
            source["source_pdf_sha256"],
        )
        check_equal(
            errors,
            f"{fixture_path}:source_cache_sha256",
            fixture["source_cache_sha256"],
            source["source_cache_sha256"],
        )
        source_cache = REPO / source["source_cache"]
        production_cache_available[card] = source_cache.exists()
        if source_cache.exists():
            check_equal(
                errors,
                str(source_cache),
                sha256_file(source_cache),
                source["source_cache_sha256"],
            )
            full_cache = json.loads(source_cache.read_text())
            for page, entries in fixture["pages"].items():
                check_equal(
                    errors,
                    f"{fixture_path}:page-{page}-source-subset",
                    entries,
                    full_cache.get(page),
                )
        else:
            warnings.append(
                f"source cache absent; fixture remains replayable: {source_cache}"
            )
        oracle = REPO / "pipeline/.cache" / card.replace("/", "-") / "oracle.json"
        if oracle.exists():
            check_equal(
                errors, str(oracle), sha256_file(oracle), source["oracle_cache_sha256"]
            )
        else:
            warnings.append(
                f"oracle cache absent; postprocessing replay skipped: {oracle}"
            )

    candidate_records = [
        item
        for item in walk(manifest)
        if isinstance(item, dict)
        and {"page", "table_index", "raw_entry_sha256", "fixture"} <= item.keys()
    ]
    for candidate in candidate_records:
        fixture = fixtures[candidate["fixture"]]
        page_entries = fixture["pages"].get(str(candidate["page"]), [])
        index = candidate["table_index"]
        if not 0 <= index < len(page_entries):
            errors.append(
                f"{candidate['fixture']} page {candidate['page']}: table_index {index} missing"
            )
            continue
        entry = page_entries[index]
        prefix = f"{candidate['fixture']}:{candidate['page']}:{index}"
        check_equal(errors, f"{prefix}:bbox", entry["bbox"], candidate["bbox"])
        check_equal(
            errors,
            f"{prefix}:raw_entry_sha256",
            raw_entry_sha256(entry),
            candidate["raw_entry_sha256"],
        )
        check_equal(
            errors,
            f"{prefix}:raw_html_sha256",
            sha256_bytes(entry["html"].encode()),
            candidate["raw_html_sha256"],
        )

    accepted_records = [
        item
        for item in walk(manifest)
        if isinstance(item, dict)
        and {"file", "table_index", "caption", "table_sha256"} <= item.keys()
    ]
    for accepted in accepted_records:
        path = REPO / accepted["file"]
        actual = table_locator(path, accepted["table_index"])
        for field in (
            "line_start",
            "line_end",
            "source_pages",
            "caption",
            "table_sha256",
        ):
            check_equal(errors, f"{path}:{field}", actual[field], accepted[field])

    # Replay every selected per-page candidate against the matching oracle.
    by_fixture: dict[str, list[dict]] = {}
    for candidate in candidate_records:
        by_fixture.setdefault(candidate["fixture"], []).append(candidate)
    for fixture_rel, candidates in by_fixture.items():
        card = fixture_cards[fixture_rel]
        oracle = REPO / "pipeline/.cache" / card.replace("/", "-") / "oracle.json"
        if not oracle.exists():
            continue
        pages = sorted({candidate["page"] for candidate in candidates})
        compare_production = production_cache_available[card]
        reports = run_inspector(
            card,
            REPO / fixture_rel,
            pages,
            compare_production=compare_production,
        )
        report_by_key = {(r["page"], r["table_index"]): r for r in reports}
        for candidate in candidates:
            key = (candidate["page"], candidate["table_index"])
            report = report_by_key[key]
            fields = {
                "raw_entry_sha256": "raw_entry_sha256",
                "raw_sha256": "raw_html_sha256",
                "final_sha256": "postprocess_sha256",
                "raw": "raw_shape",
                "final": "postprocess_shape",
                "drawing_evidence": "drawing_evidence",
            }
            for report_field, manifest_field in fields.items():
                check_equal(
                    errors,
                    f"replay {card}:{key}:{manifest_field}",
                    report[report_field],
                    candidate[manifest_field],
                )
            if compare_production:
                check_equal(
                    errors,
                    f"replay {card}:{key}:mirrors_current_get_tables",
                    report["matches_production"],
                    candidate["mirrors_current_get_tables"],
                )
            check_equal(
                errors,
                f"replay {card}:{key}:changed_passes",
                [change["pass"] for change in report["changed_passes"]],
                candidate["changed_passes"],
            )

    # Replay every logical multi-page shadow recorded in the manifest.
    logical_records = [
        item
        for item in walk(manifest)
        if isinstance(item, dict)
        and "logical_shadow" in item
        and isinstance(item.get("candidates"), list)
        and item["candidates"]
    ]
    seen_logical = set()
    for item in logical_records:
        candidates = item["candidates"]
        fixture_rel = candidates[0]["fixture"]
        card = fixture_cards[fixture_rel]
        pages = sorted({candidate["page"] for candidate in candidates})
        key = (card, tuple(pages))
        if key in seen_logical:
            continue
        seen_logical.add(key)
        oracle = REPO / "pipeline/.cache" / card.replace("/", "-") / "oracle.json"
        if not oracle.exists():
            continue
        report = run_inspector(card, REPO / fixture_rel, pages, logical=True)
        expected = item["logical_shadow"]
        for field in (
            "postprocess_sha256",
            "bytes",
            "rows",
            "ul_count",
            "li_count",
            "cell_lists_changed",
        ):
            if field in expected:
                check_equal(
                    errors,
                    f"logical replay {card}:{pages}:{field}",
                    report[field],
                    expected[field],
                )
        seam_values = [
            s["continuation_row_merge_changed"]
            for s in report["seam_row_merge_changes"]
        ]
        if "page_seams" in expected:
            check_equal(
                errors,
                f"logical replay {card}:{pages}:page_seams",
                len(seam_values),
                expected["page_seams"],
            )
        if "continuation_row_merge_changed_all_seams" in expected:
            check_equal(
                errors,
                f"logical replay {card}:{pages}:all_seams",
                bool(seam_values) and all(seam_values),
                expected["continuation_row_merge_changed_all_seams"],
            )
        if "continuation_row_merge_changed" in expected:
            check_equal(
                errors,
                f"logical replay {card}:{pages}:seams",
                bool(seam_values)
                and all(v == seam_values[0] for v in seam_values)
                and seam_values[0],
                expected["continuation_row_merge_changed"],
            )

    # The two historical-only passes were checked over all 98 current cache candidates.
    dead = manifest["observed_dead_or_historical_only_passes"]
    for card, expected_count in dead["corpus_wide_candidates_checked"].items():
        source = manifest["sources"][card]
        cache_path = REPO / source["source_cache"]
        oracle_path = REPO / "pipeline/.cache" / card.replace("/", "-") / "oracle.json"
        if not cache_path.exists() or not oracle_path.exists():
            warnings.append(f"corpus-wide dead-pass check skipped for {card}")
            continue
        cache = json.loads(cache_path.read_text())
        pages = sorted(map(int, cache))
        reports = run_inspector(card, cache_path, pages)
        check_equal(errors, f"{card}:candidate_count", len(reports), expected_count)
        for report in reports:
            changed = [change["pass"] for change in report["changed_passes"]]
            for name in dead["current_snapshot_no_change"]:
                if any(
                    pass_name == name or pass_name.startswith(name + ":")
                    for pass_name in changed
                ):
                    errors.append(
                        f"{card}:{report['page']}:{report['table_index']} unexpectedly fires {name}"
                    )

    if errors:
        print("legacy evidence validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(
        "legacy evidence validation passed: "
        f"{len(candidate_records)} locators, {len(accepted_records)} canonical tables, "
        f"{len(seen_logical)} logical shadows"
    )
    for warning in warnings:
        print(f"warning: {warning}")


if __name__ == "__main__":
    main()
