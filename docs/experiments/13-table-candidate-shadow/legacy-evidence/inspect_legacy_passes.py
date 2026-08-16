#!/usr/bin/env python3
"""Report which legacy table passes change cached Docling HTML.

This is an archaeology aid, not a production replay harness.  It mirrors the
per-page pass order in ``pipeline/generate/tables.py::get_tables`` and prints a
JSON report; it never writes the cache or canonical Markdown.

Run from the repository root, for example:

    env CARD=anthropic/claude-fable-5 python3 \
      docs/experiments/13-table-candidate-shadow/legacy-evidence/inspect_legacy_passes.py \
      72 95
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "pipeline"))
sys.path.insert(0, str(REPO / "pipeline/generate"))

import cardcfg
import tables


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def shape(html: str) -> dict[str, int]:
    return {
        "bytes": len(html.encode()),
        "rows": len(re.findall(r"<tr", html)),
        "cells": len(re.findall(r"<t[hd]", html)),
        "rowspans": len(re.findall(r"rowspan=", html)),
        "colspans": len(re.findall(r"colspan=", html)),
        "links": len(re.findall(r"<a ", html)),
        "fnrefs": len(re.findall(r"<sup", html)),
        "lists": len(re.findall(r"<ul", html)),
    }


def entry_digest(entry: dict) -> str:
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return digest(canonical)


def drawing_evidence(bbox: list, oracle_page: dict) -> dict[str, int | float]:
    """Count source drawing evidence intersecting the Docling table bbox.

    Horizontal rules have zero height, so ordinary rectangle intersection
    would miss them.  Full-page white backgrounds are not table fills.
    """

    rules = [
        rule
        for rule in oracle_page.get("rules", [])
        if min(bbox[2], rule["bbox"][2]) - max(bbox[0], rule["bbox"][0]) > 1
        and bbox[1] - 1 <= rule["bbox"][1] <= bbox[3] + 1
    ]
    fills = []
    for box in oracle_page.get("boxes", []):
        bb = box["bbox"]
        if box.get("color") == "#ffffff":
            continue
        if (
            min(bbox[2], bb[2]) - max(bbox[0], bb[0]) > 1
            and min(bbox[3], bb[3]) - max(bbox[1], bb[1]) > 1
        ):
            fills.append(box)
    return {
        "horizontal_rules": len(rules),
        "horizontal_rule_ink_pt": round(
            sum(rule["bbox"][2] - rule["bbox"][0] for rule in rules), 3
        ),
        "nonwhite_filled_rectangles": len(fills),
    }


def trace(raw: str, bbox: list, oracle_page: dict) -> tuple[str, list[dict]]:
    html = raw
    changes: list[dict] = []

    def apply(name, fn):
        nonlocal html
        before = html
        html = fn(html)
        if html != before:
            changes.append(
                {
                    "pass": name,
                    "before_sha256": digest(before),
                    "after_sha256": digest(html),
                    "before": shape(before),
                    "after": shape(html),
                }
            )

    apply("demote_data_th:pre", tables._demote_data_th)
    apply("promote_split_rowspan", tables._promote_split_rowspan)
    apply("normalize_rowspan_subrows:pre", tables._normalize_rowspan_subrows)
    apply("dedup_cascaded_cells:pre", tables._dedup_cascaded_cells)
    apply(
        "strip_caption",
        lambda h: re.sub(r"<caption>.*?</caption>", "", h, flags=re.DOTALL),
    )
    apply(
        "merge_fragment_rows",
        lambda h: tables._merge_fragment_rows(h, bbox, oracle_page),
    )
    apply(
        "split_glued_cells", lambda h: tables._split_glued_cells(h, bbox, oracle_page)
    )
    apply(
        "resplit_misjoined_cells",
        lambda h: tables._resplit_misjoined_cells(h, bbox, oracle_page),
    )
    apply(
        "extend_truncated_cells",
        lambda h: tables._extend_truncated_cells(h, bbox, oracle_page),
    )
    apply("dedup_cascaded_cells:post_extension", tables._dedup_cascaded_cells)
    apply(
        "fix_wrapped_header_cells",
        lambda h: tables._fix_wrapped_header_cells(h, bbox, oracle_page),
    )
    apply("repair_rotation", lambda h: tables._repair_rotation(h, bbox, oracle_page))
    apply(
        "merge_overflow_cells",
        lambda h: tables._merge_overflow_cells(h, bbox, oracle_page),
    )
    apply("restyle_cells", lambda h: tables._restyle_cells(h, bbox, oracle_page))
    apply(
        "restore_cell_glyphs",
        lambda h: tables._restore_cell_glyphs(h, bbox, oracle_page),
    )
    apply("bold_cell_leads", lambda h: tables._bold_cell_leads(h, bbox, oracle_page))
    apply("bold_label_cells", lambda h: tables._bold_label_cells(h, bbox, oracle_page))
    apply(
        "split_cell_paragraphs",
        lambda h: tables._split_cell_paragraphs(h, bbox, oracle_page),
    )
    apply("inject_fnrefs", lambda h: tables._inject_fnrefs(h, bbox, oracle_page))
    apply("inject_links", lambda h: tables._inject_links(h, bbox, oracle_page))
    apply("normalize_rowspan_subrows:post", tables._normalize_rowspan_subrows)
    apply("cell_blank_lines", lambda h: tables._cell_blank_lines(h, bbox, oracle_page))
    apply("bullet_breaks", tables._bullet_breaks)
    apply("demote_data_th:post", tables._demote_data_th)
    apply(
        "promote_white_text_headers",
        lambda h: tables._promote_white_text_headers(h, bbox, oracle_page),
    )
    apply(
        "demote_black_text_th",
        lambda h: tables._demote_black_text_th(h, bbox, oracle_page),
    )
    apply("debold_th", tables._debold_th)
    apply(
        "join_hyphen_wraps",
        lambda h: re.sub(
            r"(\w+-\w+) (-[a-z])",
            r"\1\2",
            re.sub(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])", r"\1-", h),
        ),
    )
    apply(
        "close_link_punctuation",
        lambda h: re.sub(r"(</a>(?:</[a-z]+>)*)\s+([,.;:)])", r"\1\2", h),
    )
    apply(
        "lift_regular_sups", lambda h: tables._lift_regular_sups(h, bbox, oracle_page)
    )
    return html, changes


def load_merge_tables():
    """Load only run.py's table-merge helpers without importing its pipeline."""

    source = (REPO / "pipeline/generate/run.py").read_text()
    tree = ast.parse(source)
    wanted = {"_tbl_rows", "_row_squash", "_merge_tables"}
    nodes = []
    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name in wanted
            or isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "TR"
                for target in node.targets
            )
        ):
            nodes.append(node)
    namespace = {"re": re}
    exec(  # noqa: S102 - execute only the allowlisted local AST nodes above
        compile(ast.Module(body=nodes, type_ignores=[]), "run.py", "exec"), namespace
    )
    return namespace["_merge_tables"]


def logical_trace(page_nos: list[int], cache: dict, oracle: list[dict]) -> dict:
    """Replay the current cross-page merge/list tail over fixture candidates."""

    merge_tables = load_merge_tables()
    parts = []
    current = None
    seam_changes = []
    for page_no in page_nos:
        entries = cache.get(str(page_no), [])
        if len(entries) != 1:
            raise SystemExit(
                f"logical trace requires one candidate on page {page_no}; "
                f"found {len(entries)}"
            )
        entry = entries[0]
        processed, _ = trace(entry["html"], entry["bbox"], oracle[page_no - 1])
        parts.append((entry["bbox"], oracle[page_no - 1]))
        if current is None:
            current = processed
            continue
        merged = merge_tables(current, processed, page_no)
        if merged is None:
            raise SystemExit(f"legacy merge rejected page seam before {page_no}")
        row_merged = tables.merge_continuation_rows(merged)
        seam_changes.append(
            {
                "next_page": page_no,
                "continuation_row_merge_changed": row_merged != merged,
            }
        )
        current = tables._bullet_breaks(row_merged)
    assert current is not None
    before_lists = current
    current = tables._cell_lists(current, tables._cell_align_ctx(parts))
    return {
        "card": cardcfg.CARD_ID,
        "pages": page_nos,
        "postprocess_sha256": digest(current),
        "bytes": len(current.encode()),
        "rows": len(re.findall(r"<tr", current)),
        "ul_count": len(re.findall(r"<ul", current)),
        "li_count": len(re.findall(r"<li", current)),
        "cell_lists_changed": current != before_lists,
        "seam_row_merge_changes": seam_changes,
    }


def production_comparison(
    final: str,
    page_no: int,
    table_index: int,
    oracle_page: dict,
    *,
    enabled: bool,
    loader=None,
) -> dict[str, str | bool]:
    """Compare with production only when its complete cache is authoritative."""

    if not enabled:
        return {}
    loader = loader or tables.get_tables
    production = loader(page_no, oracle_page)[table_index]["html"]
    return {
        "production_sha256": digest(production),
        "matches_production": final == production,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--logical", action="store_true")
    parser.add_argument(
        "--compare-production",
        action="store_true",
        help="also compare fixture replay with get_tables(); requires the full cache",
    )
    parser.add_argument("pages", type=int, nargs="+")
    args = parser.parse_args()
    loaded = (
        json.loads(args.fixture.read_text())
        if args.fixture
        else json.loads(cardcfg.TABLES_CACHE.read_text())
    )
    cache = loaded.get("pages", loaded)
    oracle = json.loads(cardcfg.ORACLE_CACHE.read_text())
    if args.logical:
        print(json.dumps(logical_trace(args.pages, cache, oracle), indent=2))
        return
    reports = []
    for page_no in args.pages:
        for index, entry in enumerate(cache.get(str(page_no), [])):
            final, changes = trace(entry["html"], entry["bbox"], oracle[page_no - 1])
            report = {
                "card": cardcfg.CARD_ID,
                "page": page_no,
                "table_index": index,
                "bbox": entry["bbox"],
                "raw_entry_sha256": entry_digest(entry),
                "raw_sha256": digest(entry["html"]),
                "final_sha256": digest(final),
                "raw": shape(entry["html"]),
                "final": shape(final),
                "drawing_evidence": drawing_evidence(
                    entry["bbox"], oracle[page_no - 1]
                ),
                "changed_passes": changes,
            }
            report.update(
                production_comparison(
                    final,
                    page_no,
                    index,
                    oracle[page_no - 1],
                    enabled=args.compare_production,
                )
            )
            reports.append(report)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
