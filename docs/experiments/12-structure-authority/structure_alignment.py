"""Advisory alignment of live PDF tag claims with production DOM list items.

This experiment is not a release gate and writes no authority artifact. Its
public run path always reopens the card's ``source.pdf``. The PDF observer
provides raw tag/text/geometry facts; provisional marker interpretation lives
here so it can be calibrated or replaced without changing the base observer.

Run after installing the locked ``site`` dependencies::

    uv run --python 3.12 --with 'pymupdf==1.28.2' \
      python docs/experiments/12-structure-authority/structure_alignment.py \
      anthropic/claude-opus-5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
VERIFIER = REPO / "pipeline" / "verifier"
sys.path.insert(0, str(VERIFIER))

import pdf_structure

SITE = REPO / "site"
REPORTER = SITE / "scripts" / "list-structure-report.mjs"
SCHEMA_VERSION = 1
MATCH_CONTRACT = "exact-visible-own-tokens.v1"
DOM_SCHEMA_VERSION = 2
DOM_TOKEN_DIGEST_METHOD = "visible-list-tokens.sha256-json.v1"
SOURCE_STATUSES = frozenset({"ok", "advisory", "blocked"})

# Provisional policy, deliberately colocated with this experiment rather than
# the raw PDF observer. These values are hypotheses to test against more PDFs.
MARKER_PATTERN = re.compile(
    r"[ \t]*(?:"
    r"[•◦●○▪▫■‣⁃o-]"
    r"|\d{1,3}[.)]"
    r"|[A-Za-z][.)]"
    r"|[ivxlcdmIVXLCDM]{1,8}[.)]"
    r"|\((?:\d{1,3}|[A-Za-z]|[ivxlcdmIVXLCDM]{1,8})\)"
    r")"
)
MIN_FIRST_GLYPH_GAP_SCALE = 0.6
MIN_TRAILING_GAP_SCALE = 0.2
MIN_VERTICAL_OVERLAP = 0.5

LIGATURES = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi",
    "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
}
INVISIBLES = re.compile("[\u00ad\u200b\u200c\u200d\u2060\ufeff]")
WRAPPED_HYPHEN = re.compile(r"(\w)-\s+(?=[a-z])")


@dataclass(frozen=True)
class MatchRow:
    """Observer-neutral occurrence consumed by the exact-match core."""

    occurrence: int
    pages: tuple[int, ...]
    tokens: tuple[str, ...]


def normalize_source_text(text: str) -> str:
    """Apply narrow extraction normalization without folding punctuation."""
    text = unicodedata.normalize("NFC", text)
    for source, replacement in LIGATURES.items():
        text = text.replace(source, replacement)
    text = INVISIBLES.sub("", text)
    text = WRAPPED_HYPHEN.sub(r"\1-", text)
    return " ".join(text.split())


def _is_word_character(char: str) -> bool:
    return unicodedata.category(char)[:1] in {"L", "M", "N"}


def visible_tokens(text: str) -> tuple[str, ...]:
    """Python mirror of the DOM observer's punctuation-retaining tokenizer."""
    result: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if _is_word_character(char):
            start = index
            index += 1
            while index < len(text) and _is_word_character(text[index]):
                index += 1
            while (
                index + 1 < len(text)
                and text[index] in {"'", "’"}
                and _is_word_character(text[index + 1])
            ):
                index += 2
                while index < len(text) and _is_word_character(text[index]):
                    index += 1
            result.append(text[start:index])
        elif char.isspace():
            index += 1
        else:
            result.append(char)
            index += 1
    return tuple(result)


def _bbox(value: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    if any(
        not isinstance(coordinate, (int, float))
        or isinstance(coordinate, bool)
        or not math.isfinite(coordinate)
        for coordinate in value
    ):
        return None
    box = tuple(float(coordinate) for coordinate in value)
    if box[2] < box[0] or box[3] < box[1]:
        return None
    return box


def _marker_body(evidence: pdf_structure.PageEvidence) -> str | None:
    """Return the provisional body only when lexical and geometry tests agree."""
    prefix = evidence.separator_prefix
    suffix = evidence.separator_suffix
    if (
        prefix is None
        or suffix is None
        or evidence.owned_text != f"{prefix}\u200b{suffix}"
        or MARKER_PATTERN.fullmatch(prefix) is None
        or not suffix.strip()
    ):
        return None

    first = _bbox(evidence.prefix_first_glyph_bbox)
    last = _bbox(evidence.prefix_last_glyph_bbox)
    body = _bbox(evidence.suffix_first_nonspace_glyph_bbox)
    if first is None or last is None or body is None:
        return None
    first_height = first[3] - first[1]
    last_height = last[3] - last[1]
    body_height = body[3] - body[1]
    if min(first_height, last_height, body_height) <= 0:
        return None
    first_overlap = min(first[3], body[3]) - max(first[1], body[1])
    last_overlap = min(last[3], body[3]) - max(last[1], body[1])
    if (
        first_overlap < MIN_VERTICAL_OVERLAP * min(first_height, body_height)
        or last_overlap < MIN_VERTICAL_OVERLAP * min(last_height, body_height)
    ):
        return None
    if (
        body[0] - first[2]
        < MIN_FIRST_GLYPH_GAP_SCALE * max(first_height, body_height)
        or body[0] - last[2]
        < MIN_TRAILING_GAP_SCALE * max(last_height, body_height)
    ):
        return None
    return suffix


def _source_rows(source: pdf_structure.PDFStructureObservation) -> list[MatchRow]:
    """Adapt one live PDF observer to neutral rows; retain every tag-item claim."""
    rows = []
    for occurrence, item in enumerate(source.list_items):
        parts = []
        for evidence in item.evidence:
            body = _marker_body(evidence)
            parts.append(evidence.owned_text if body is None else body)
        text = normalize_source_text(" ".join(parts))
        rows.append(MatchRow(occurrence, item.pages, visible_tokens(text)))
    return rows


def _token_digest(tokens: list[str] | tuple[str, ...]) -> str:
    encoded = json.dumps(
        list(tokens), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _page_from_marker(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"p-(\d+)", value)
    page = int(match.group(1)) if match else 0
    return page if page > 0 else None


def _validate_dom(dom: Any) -> None:
    """Validate the actual JSON/subprocess boundary strictly."""
    if not isinstance(dom, dict):
        raise TypeError("DOM list observation is not an object")
    if dom.get("schemaVersion") != DOM_SCHEMA_VERSION:
        raise ValueError("unsupported DOM list observation schema")
    if dom.get("tokenDigestMethod") != DOM_TOKEN_DIGEST_METHOD:
        raise ValueError("unsupported DOM token digest method")
    if not isinstance(dom.get("events"), list):
        raise TypeError("DOM list observation has no event collection")
    if not isinstance(dom.get("excludedSubtrees"), list):
        raise TypeError("DOM observation has no excluded-subtree collection")

    occurrences: dict[str, set[int]] = defaultdict(set)
    for event in dom["events"]:
        if not isinstance(event, dict) or event.get("kind") not in {"list", "item"}:
            raise ValueError("DOM observation has a malformed event")
        kind = event["kind"]
        occurrence = event.get("occurrence")
        if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 0:
            raise ValueError("DOM event has an invalid occurrence")
        if occurrence in occurrences[kind]:
            raise ValueError("DOM event occurrences are not unique within kind")
        occurrences[kind].add(occurrence)
        if kind != "item":
            continue
        tokens = event.get("ownTokens")
        text = event.get("ownText")
        if not isinstance(tokens, list) or any(not isinstance(token, str) for token in tokens):
            raise TypeError("DOM item has invalid own tokens")
        if not isinstance(text, str):
            raise TypeError("DOM item has invalid own text")
        if tuple(tokens) != visible_tokens(text):
            raise ValueError("DOM item tokens disagree with its visible text")
        if event.get("ownTokenCount") != len(tokens):
            raise ValueError("DOM item token count is invalid")
        if event.get("ownTokenSha256") != _token_digest(tokens):
            raise ValueError("DOM item token digest is invalid")
        nearest = event.get("nearestPageMarkerId")
        if nearest is not None and _page_from_marker(nearest) is None:
            raise ValueError("DOM item has an invalid nearest page marker")
        own_markers = event.get("ownPageMarkers")
        if not isinstance(own_markers, list):
            raise TypeError("DOM item has invalid owned page markers")
        for marker in own_markers:
            if not isinstance(marker, dict) or _page_from_marker(marker.get("id")) is None:
                raise ValueError("DOM item has a malformed owned page marker")
            offset = marker.get("tokenOffset")
            if (
                not isinstance(offset, int)
                or isinstance(offset, bool)
                or not 0 <= offset <= len(tokens)
            ):
                raise ValueError("DOM item has an invalid page-marker token offset")

    for subtree in dom["excludedSubtrees"]:
        if not isinstance(subtree, dict) or not isinstance(subtree.get("kind"), str):
            raise TypeError("DOM observation has a malformed excluded subtree")
        if subtree["kind"] == "renderer-footnotes":
            count = subtree.get("itemCount")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValueError("renderer-footnote exclusion has an invalid item count")


def _dom_rows(dom: dict[str, Any]) -> list[MatchRow]:
    rows = []
    for event in dom["events"]:
        if event["kind"] != "item":
            continue
        pages = {_page_from_marker(event.get("nearestPageMarkerId"))}
        pages.update(
            _page_from_marker(marker["id"])
            for marker in event["ownPageMarkers"]
        )
        rows.append(MatchRow(
            event["occurrence"],
            tuple(sorted(page for page in pages if page is not None)),
            tuple(event["ownTokens"]),
        ))
    return rows


def _group(rows: Iterable[MatchRow]) -> dict[tuple[str, ...], list[MatchRow]]:
    grouped: dict[tuple[str, ...], list[MatchRow]] = defaultdict(list)
    for row in rows:
        if row.tokens:
            grouped[row.tokens].append(row)
    return grouped


def _resolved_by_page(source_group: list[MatchRow], dom_group: list[MatchRow]) -> int:
    resolved: set[tuple[int, int]] = set()
    for source in source_group:
        candidates = [dom for dom in dom_group if set(dom.pages) & set(source.pages)]
        if len(candidates) != 1:
            continue
        candidate = candidates[0]
        contenders = [row for row in source_group if set(row.pages) & set(candidate.pages)]
        if len(contenders) == 1:
            resolved.add((source.occurrence, candidate.occurrence))
    return len(resolved)


def match_rows(source_rows: list[MatchRow], dom_rows: list[MatchRow]) -> dict[str, int]:
    """Partition neutral rows into unique, page-resolved, unresolved, unmatched."""
    source_groups = _group(source_rows)
    dom_groups = _group(dom_rows)
    unique = page_resolved = unresolved = 0
    for tokens in source_groups.keys() & dom_groups.keys():
        source_group = source_groups[tokens]
        dom_group = dom_groups[tokens]
        if len(source_group) == 1 and len(dom_group) == 1:
            unique += 1
            continue
        capacity = min(len(source_group), len(dom_group))
        resolved = min(_resolved_by_page(source_group, dom_group), capacity)
        page_resolved += resolved
        unresolved += capacity - resolved
    paired = unique + page_resolved + unresolved
    return {
        "source_exact_unique": unique,
        "source_exact_page_resolved": page_resolved,
        "source_exact_ambiguous_unresolved": unresolved,
        "source_exact_unmatched": len(source_rows) - paired,
        "dom_exact_unique": unique,
        "dom_exact_page_resolved": page_resolved,
        "dom_exact_ambiguous_unresolved": unresolved,
        "dom_exact_unmatched": len(dom_rows) - paired,
    }


def _align_live_observation(
    card_id: str,
    source: pdf_structure.PDFStructureObservation,
    dom: dict[str, Any],
) -> dict[str, Any]:
    if source.schema_version != pdf_structure.SCHEMA_VERSION:
        raise ValueError("unsupported live source-observation schema")
    if source.status not in SOURCE_STATUSES:
        raise ValueError("unsupported live source-observation status")
    if (
        source.pymupdf_version != pdf_structure.PINNED_PYMUPDF_VERSION
        and source.status != "blocked"
    ):
        raise ValueError("unpinned source observer did not block its observation")
    _validate_dom(dom)

    source_rows = _source_rows(source)
    dom_rows = _dom_rows(dom)
    renderer_footnotes = [
        subtree for subtree in dom["excludedSubtrees"]
        if subtree["kind"] == "renderer-footnotes"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment": "source-to-dom-list-alignment",
        "status": "blocked" if source.status == "blocked" else "advisory",
        "card": card_id,
        "match_contract": MATCH_CONTRACT,
        "policy": {
            "release_gate": False,
            "fuzzy_matches_accepted": False,
            "page_context_use": "disambiguate identical exact matches only",
            "marker_interpretation": "provisional lexical and glyph-gap policy in experiment",
            "source_authority_artifact": False,
        },
        "source": {
            "sha256": source.source_sha256,
            "observer": "pymupdf-tag-tree",
            "observer_version": source.pymupdf_version,
            "observer_status": source.status,
            "lists_tag_claims_included": len(source.lists),
            "items_total": len(source.list_items),
            "items_tag_claims_included": len(source_rows),
            "blocking_issue_codes": sorted({
                issue.code for issue in source.issues
                if issue.severity == "blocking"
            }),
        },
        "dom": {
            "schema_version": dom["schemaVersion"],
            "token_digest_method": dom["tokenDigestMethod"],
            "items_total": len(dom_rows),
            "renderer_footnote_subtrees_excluded": len(renderer_footnotes),
            "renderer_footnote_items_excluded": sum(
                subtree["itemCount"] for subtree in renderer_footnotes
            ),
        },
        "matches": match_rows(source_rows, dom_rows),
    }


def resolve_card(value: str) -> tuple[str, Path]:
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        root = candidate.resolve()
        try:
            relative = root.relative_to((REPO / "cards").resolve())
        except ValueError as error:
            raise ValueError("card path must be below the repository cards directory") from error
        parts = relative.parts
    else:
        text = value.removeprefix("cards/").strip("/")
        parts = tuple(part for part in text.split("/") if part)
        root = REPO / "cards" / Path(*parts)
    if len(parts) != 2 or any(
        not re.fullmatch(r"[a-z0-9][a-z0-9-]*", part) for part in parts
    ):
        raise ValueError("card must be a vendor/slug id or its card directory")
    if not root.is_dir() or not (root / "source.pdf").is_file():
        raise ValueError(f"unknown or incomplete card: {'/'.join(parts)}")
    return "/".join(parts), root


def render_dom_observation(card_id: str) -> dict[str, Any]:
    result = subprocess.run(
        ["node", str(REPORTER), card_id],
        cwd=SITE,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"production list reporter failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("production list reporter emitted invalid JSON") from error


def run(card: str) -> dict[str, Any]:
    """Reopen the card source and run the advisory experiment."""
    card_id, card_root = resolve_card(card)
    source = pdf_structure.observe_pdf(card_root / "source.pdf")
    dom = render_dom_observation(card_id)
    return _align_live_observation(card_id, source, dom)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", help="vendor/slug id or path below cards/")
    args = parser.parse_args(argv)
    try:
        report = run(args.card)
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
        parser.exit(2, f"structure alignment failed: {error}\n")
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 3 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
