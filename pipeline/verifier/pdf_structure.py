"""Source-only observation of tagged-PDF list structure.

This experimental observer deliberately knows nothing about the generator,
oracle, Markdown projection, or current card output.  It asks pinned PyMuPDF to
walk the PDF structure tree while producing ``rawdict`` text.  PyMuPDF exposes
each structure element as a type-2 block with its raw and standard roles, its
index in the parent structure element, a page-space bounding box, and nested
blocks.  The complete role/index path is therefore a stable source locator even
though this API does not expose the underlying MCID.

The result is an observation of claims made by the PDF's tags, not semantic
truth. The observer records tag ancestry, exact owned text, the first raw ZWSP
split, and the associated glyph boxes. It deliberately does not decide whether
the split represents a marker or whether any tag claim is semantically valid.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pymupdf as fitz

SCHEMA_VERSION = 1
PINNED_PYMUPDF_VERSION = "1.28.2"
PYMUPDF_VERSION = str(getattr(fitz, "__version__", "unknown"))
EXTRACTION_FLAGS = fitz.TEXTFLAGS_RAWDICT | fitz.TEXT_COLLECT_STRUCTURE


@dataclass(frozen=True)
class StructureStep:
    raw: str
    std: str
    index: int


@dataclass(frozen=True)
class PageEvidence:
    """One page slice of a logical tagged structure element."""

    occurrence_id: str
    page: int
    bbox: tuple[float, float, float, float]
    text: str
    text_sha256: str
    owned_text: str
    owned_text_sha256: str
    separator_prefix: str | None
    separator_suffix: str | None
    prefix_first_glyph_bbox: tuple[float, float, float, float] | None
    prefix_last_glyph_bbox: tuple[float, float, float, float] | None
    suffix_first_nonspace_glyph_bbox: tuple[float, float, float, float] | None


@dataclass(frozen=True)
class ListItemObservation:
    occurrence_id: str
    structure_path: tuple[StructureStep, ...]
    parent_list_id: str
    ancestor_roles: tuple[str, ...]
    pages: tuple[int, ...]
    evidence: tuple[PageEvidence, ...]


@dataclass(frozen=True)
class ListObservation:
    occurrence_id: str
    structure_path: tuple[StructureStep, ...]
    parent_list_id: str | None
    parent_item_id: str | None
    ancestor_roles: tuple[str, ...]
    direct_item_ids: tuple[str, ...]
    pages: tuple[int, ...]
    evidence: tuple[PageEvidence, ...]


@dataclass(frozen=True)
class StructureIssue:
    code: str
    severity: str
    occurrence_id: str | None
    pages: tuple[int, ...]
    detail: str


@dataclass(frozen=True)
class PDFStructureObservation:
    schema_version: int
    source_pdf: str
    source_sha256: str
    pymupdf_version: str
    extraction_flags: int
    status: str
    capabilities: dict[str, Any]
    stats: dict[str, int]
    lists: tuple[ListObservation, ...]
    list_items: tuple[ListItemObservation, ...]
    issues: tuple[StructureIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, ensure_ascii=False, sort_keys=True)


def _path_id(path: tuple[StructureStep, ...]) -> str:
    # Raw and standard roles are retained because RoleMap may make them differ.
    return "/".join(
        f"{step.raw}>{step.std}[{step.index}]" for step in path
    )


def _path_sort_key(path: tuple[StructureStep, ...]) -> tuple[tuple[int, str, str], ...]:
    """Sort by numeric structure indices, never lexicographic occurrence IDs."""
    return tuple((step.index, step.raw, step.std) for step in path)


def _separator_split(text: str) -> tuple[str | None, str | None]:
    """Record the first raw ZWSP split without assigning it semantics."""
    prefix, separator, suffix = text.partition("\u200b")
    return (prefix, suffix) if separator else (None, None)


def _bbox(value: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    try:
        box = tuple(float(item) for item in value)
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(item) for item in box):
        return None
    if box[2] < box[0] or box[3] < box[1]:
        return None
    return box


class _ValidatedCharacterReader:
    """Validate each text leaf once, then serve all textual observations."""

    def __init__(self, *, page: int, issues: list[StructureIssue]) -> None:
        self.page = page
        self.issues = issues
        self.leaves: dict[int, tuple[dict[str, Any], ...] | None] = {}

    def validate_blocks(self, blocks: list[Any]) -> None:
        for index, block in enumerate(blocks):
            if isinstance(block, dict):
                self._validate_tree(block, f"blocks[{index}]")

    def _malformed(self, detail: str) -> None:
        self.issues.append(
            StructureIssue(
                "text-character-stream-malformed",
                "blocking",
                None,
                (self.page,),
                detail,
            )
        )

    def _validate_tree(self, block: dict[str, Any], path: str) -> None:
        block_type = block.get("type")
        if block_type == 0:
            self._validate_leaf(block, path)
            return
        if block_type != 2:
            return
        children = block.get("blocks")
        if not isinstance(children, list):
            return
        for index, child in enumerate(children):
            if isinstance(child, dict):
                self._validate_tree(child, f"{path}.blocks[{index}]")

    def _validate_leaf(self, block: dict[str, Any], path: str) -> None:
        cache_key = id(block)
        if cache_key in self.leaves:
            return

        lines = block.get("lines")
        if not isinstance(lines, list):
            self.leaves[cache_key] = None
            self._malformed(f"{path}.lines is {type(lines).__name__}, expected list")
            return

        result: list[dict[str, Any]] = []
        for line_index, line in enumerate(lines):
            line_path = f"{path}.lines[{line_index}]"
            if not isinstance(line, dict):
                self.leaves[cache_key] = None
                self._malformed(
                    f"{line_path} is {type(line).__name__}, expected object"
                )
                return
            spans = line.get("spans")
            if not isinstance(spans, list):
                self.leaves[cache_key] = None
                self._malformed(
                    f"{line_path}.spans is {type(spans).__name__}, expected list"
                )
                return
            for span_index, span in enumerate(spans):
                span_path = f"{line_path}.spans[{span_index}]"
                if not isinstance(span, dict):
                    self.leaves[cache_key] = None
                    self._malformed(
                        f"{span_path} is {type(span).__name__}, expected object"
                    )
                    return
                chars = span.get("chars")
                if not isinstance(chars, list):
                    self.leaves[cache_key] = None
                    self._malformed(
                        f"{span_path}.chars is {type(chars).__name__}, expected list"
                    )
                    return
                for char_index, char in enumerate(chars):
                    char_path = f"{span_path}.chars[{char_index}]"
                    if not isinstance(char, dict):
                        self.leaves[cache_key] = None
                        self._malformed(
                            f"{char_path} is {type(char).__name__}, expected object"
                        )
                        return
                    value = char.get("c")
                    if not isinstance(value, str):
                        self.leaves[cache_key] = None
                        self._malformed(
                            f"{char_path}.c is {type(value).__name__}, "
                            "expected one-character string"
                        )
                        return
                    if len(value) != 1:
                        self.leaves[cache_key] = None
                        self._malformed(
                            f"{char_path}.c has length {len(value)}, "
                            "expected one-character string"
                        )
                        return
                    result.append(char)
        self.leaves[cache_key] = tuple(result)

    def read(
        self,
        block: Any,
        *,
        exclude_descendant_lists: bool,
        root: bool = True,
    ) -> tuple[dict[str, Any], ...] | None:
        if not isinstance(block, dict):
            return None
        block_type = block.get("type")
        if block_type == 2:
            if exclude_descendant_lists and not root and block.get("std") == "L":
                return ()
            children = block.get("blocks")
            if not isinstance(children, list):
                return None
            result: list[dict[str, Any]] = []
            for child in children:
                child_stream = self.read(
                    child,
                    exclude_descendant_lists=exclude_descendant_lists,
                    root=False,
                )
                if child_stream is None:
                    return None
                result.extend(child_stream)
            return tuple(result)
        if block_type != 0:
            return ()
        return self.leaves.get(id(block))


def _observe_separator_geometry(
    chars: tuple[dict[str, Any], ...] | None,
    *,
    owned_text: str,
    separator_prefix: str | None,
) -> tuple[
    tuple[float, float, float, float] | None,
    tuple[float, float, float, float] | None,
    tuple[float, float, float, float] | None,
]:
    """Observe glyph boxes adjacent to the first raw ZWSP separator."""
    if separator_prefix is None:
        return None, None, None
    if chars is None or "".join(char["c"] for char in chars) != owned_text:
        return None, None, None

    separator_index = len(separator_prefix)
    if (
        separator_index >= len(chars)
        or chars[separator_index]["c"] != "\u200b"
    ):
        return None, None, None
    prefix_chars = [
        char for char in chars[:separator_index] if not char["c"].isspace()
    ]
    suffix_char = next(
        (
            char
            for char in chars[separator_index + 1 :]
            if not char["c"].isspace()
        ),
        None,
    )
    return (
        None if not prefix_chars else _bbox(prefix_chars[0].get("bbox")),
        None if not prefix_chars else _bbox(prefix_chars[-1].get("bbox")),
        None if suffix_char is None else _bbox(suffix_char.get("bbox")),
    )


class _NodeAggregate:
    def __init__(
        self,
        path: tuple[StructureStep, ...],
        parent_list_id: str | None,
        parent_item_id: str | None,
        ancestors: tuple[str, ...],
    ) -> None:
        self.path = path
        self.parent_list_id = parent_list_id
        self.parent_item_id = parent_item_id
        self.ancestors = ancestors
        self.evidence: dict[int, PageEvidence] = {}
        self.direct_items: set[str] = set()


def _build_observation(
    *,
    source_pdf: str,
    source_sha256: str,
    page_dicts: Iterable[tuple[int, dict[str, Any]]],
    source_pages: int,
    structure_tree_present: bool,
    pymupdf_version: str,
) -> PDFStructureObservation:
    """Build an observation from isolated structure-aware rawdict pages.

    Keeping this stage pure makes malformed-tree behavior unit-testable without
    manufacturing binary PDF object trees, and leaves a clean seam for a future
    MCID-aware or second-producer observer.
    """
    lists: dict[str, _NodeAggregate] = {}
    items: dict[str, _NodeAggregate] = {}
    issues: list[StructureIssue] = []
    tagged_pages: set[int] = set()
    list_pages: set[int] = set()
    slot_roles: dict[tuple[tuple[StructureStep, ...], int], tuple[str, str]] = {}
    page_slots: set[tuple[int, tuple[StructureStep, ...], int]] = set()

    if pymupdf_version != PINNED_PYMUPDF_VERSION:
        issues.append(
            StructureIssue(
                "observer-version-mismatch",
                "blocking",
                None,
                (),
                f"expected PyMuPDF {PINNED_PYMUPDF_VERSION}, got {pymupdf_version}",
            )
        )
    if not structure_tree_present:
        issues.append(
            StructureIssue(
                "structure-tree-missing",
                "blocking",
                None,
                (),
                "PDF catalog has no /StructTreeRoot",
            )
        )

    def add_evidence(
        aggregate: _NodeAggregate,
        occurrence_id: str,
        page: int,
        block: dict[str, Any],
        reader: _ValidatedCharacterReader,
        *,
        is_list_item: bool,
    ) -> None:
        box = _bbox(block.get("bbox"))
        if box is None:
            issues.append(
                StructureIssue(
                    "structure-bbox-malformed",
                    "blocking",
                    occurrence_id,
                    (page,),
                    f"invalid bbox {block.get('bbox')!r}",
                )
            )
            box = (0.0, 0.0, 0.0, 0.0)
        full_chars = reader.read(block, exclude_descendant_lists=False)
        text = "" if full_chars is None else "".join(char["c"] for char in full_chars)
        owned_chars = (
            reader.read(block, exclude_descendant_lists=True)
            if is_list_item
            else full_chars
        )
        owned_text = (
            "" if owned_chars is None else "".join(char["c"] for char in owned_chars)
        )
        separator_prefix, separator_suffix = _separator_split(owned_text)
        separator_geometry = _observe_separator_geometry(
            owned_chars,
            owned_text=owned_text,
            separator_prefix=separator_prefix,
        )
        evidence = PageEvidence(
            occurrence_id=f"{occurrence_id}@p{page:04d}",
            page=page,
            bbox=box,
            text=text,
            text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            owned_text=owned_text,
            owned_text_sha256=hashlib.sha256(owned_text.encode("utf-8")).hexdigest(),
            separator_prefix=separator_prefix,
            separator_suffix=separator_suffix,
            prefix_first_glyph_bbox=separator_geometry[0],
            prefix_last_glyph_bbox=separator_geometry[1],
            suffix_first_nonspace_glyph_bbox=separator_geometry[2],
        )
        prior = aggregate.evidence.get(page)
        if prior is not None and prior != evidence:
            issues.append(
                StructureIssue(
                    "structure-occurrence-ambiguous",
                    "blocking",
                    occurrence_id,
                    (page,),
                    "same role/index path produced different page evidence",
                )
            )
        aggregate.evidence[page] = evidence

    def walk(
        block: Any,
        *,
        page: int,
        path: tuple[StructureStep, ...],
        ancestors: tuple[str, ...],
        nearest_list_id: str | None,
        nearest_item_id: str | None,
        parent_std: str | None,
        reader: _ValidatedCharacterReader,
    ) -> None:
        if not isinstance(block, dict):
            issues.append(
                StructureIssue(
                    "structure-block-malformed",
                    "blocking",
                    None,
                    (page,),
                    f"structure block is {type(block).__name__}",
                )
            )
            return
        if block.get("type") != 2:
            return
        raw, std, index = block.get("raw"), block.get("std"), block.get("index")
        if not isinstance(raw, str) or not isinstance(std, str):
            issues.append(
                StructureIssue(
                    "structure-role-malformed",
                    "blocking",
                    None,
                    (page,),
                    f"raw/std roles are {raw!r}/{std!r}",
                )
            )
            return
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            issues.append(
                StructureIssue(
                    "structure-index-malformed",
                    "blocking",
                    None,
                    (page,),
                    f"role {std!r} has index {index!r}",
                )
            )
            return

        step = StructureStep(raw=raw, std=std, index=index)
        node_path = path + (step,)
        occurrence_id = _path_id(node_path)
        page_slot = (page, path, index)
        if page_slot in page_slots:
            parent_id = _path_id(path) or "<root>"
            issues.append(
                StructureIssue(
                    "structure-index-duplicate",
                    "blocking",
                    occurrence_id,
                    (page,),
                    f"duplicate child index {index} under {parent_id} on page {page}",
                )
            )
            return
        page_slots.add(page_slot)

        slot = (path, index)
        role_pair = (raw, std)
        prior_role = slot_roles.setdefault(slot, role_pair)
        if prior_role != role_pair:
            issues.append(
                StructureIssue(
                    "structure-index-ambiguous",
                    "blocking",
                    None,
                    (page,),
                    f"slot {slot!r} maps to both {prior_role!r} and {role_pair!r}",
                )
            )

        tagged_pages.add(page)

        children = block.get("blocks")
        if not isinstance(children, list):
            issues.append(
                StructureIssue(
                    "structure-children-malformed",
                    "blocking",
                    occurrence_id,
                    (page,),
                    f"blocks is {type(children).__name__}",
                )
            )
            children = []
        malformed_child_indices = [
            child_index
            for child_index, child in enumerate(children)
            if not isinstance(child, dict)
        ]
        if malformed_child_indices:
            issues.append(
                StructureIssue(
                    "structure-block-malformed",
                    "blocking",
                    occurrence_id,
                    (page,),
                    "non-dict child blocks at indices "
                    f"{malformed_child_indices!r}",
                )
            )
        valid_children = [child for child in children if isinstance(child, dict)]

        child_list_id = nearest_list_id
        child_item_id = nearest_item_id
        if std == "L":
            aggregate = lists.setdefault(
                occurrence_id,
                _NodeAggregate(
                    node_path, nearest_list_id, nearest_item_id, ancestors
                ),
            )
            if (
                aggregate.path != node_path
                or aggregate.parent_list_id != nearest_list_id
                or aggregate.parent_item_id != nearest_item_id
                or aggregate.ancestors != ancestors
            ):
                issues.append(
                    StructureIssue(
                        "list-identity-ambiguous",
                        "blocking",
                        occurrence_id,
                        (page,),
                        "same list identity has inconsistent ancestry",
                    )
                )
            add_evidence(
                aggregate,
                occurrence_id,
                page,
                block,
                reader,
                is_list_item=False,
            )
            list_pages.add(page)
            child_list_id = occurrence_id
            child_item_id = None
        elif std == "LI":
            if parent_std != "L" or nearest_list_id is None:
                issues.append(
                    StructureIssue(
                        "list-item-without-list-parent",
                        "blocking",
                        occurrence_id,
                        (page,),
                        f"direct parent is {parent_std!r}",
                    )
                )
            else:
                aggregate = items.setdefault(
                    occurrence_id,
                    _NodeAggregate(node_path, nearest_list_id, None, ancestors),
                )
                add_evidence(
                    aggregate,
                    occurrence_id,
                    page,
                    block,
                    reader,
                    is_list_item=True,
                )
                lists[nearest_list_id].direct_items.add(occurrence_id)
                child_item_id = occurrence_id

        structure_children = [
            child for child in valid_children if child.get("type") == 2
        ]
        if std == "L":
            wrong = [child.get("std") for child in structure_children if child.get("std") != "LI"]
            direct_content = any(child.get("type") != 2 for child in valid_children)
            if wrong or direct_content:
                issues.append(
                    StructureIssue(
                        "list-children-malformed",
                        "blocking",
                        occurrence_id,
                        (page,),
                        f"non-LI structure roles={wrong!r}, direct_content={direct_content}",
                    )
                )

        for child in structure_children:
            walk(
                child,
                page=page,
                path=node_path,
                ancestors=ancestors + (std,),
                nearest_list_id=child_list_id,
                nearest_item_id=child_item_id,
                parent_std=std,
                reader=reader,
            )

    for page, rawdict in page_dicts:
        if not isinstance(rawdict, dict):
            issues.append(
                StructureIssue(
                    "page-rawdict-malformed",
                    "blocking",
                    None,
                    (page,),
                    f"rawdict is {type(rawdict).__name__}",
                )
            )
            continue
        blocks = rawdict.get("blocks")
        if not isinstance(blocks, list):
            issues.append(
                StructureIssue(
                    "page-blocks-malformed",
                    "blocking",
                    None,
                    (page,),
                    "rawdict blocks is not a list",
                )
            )
            continue
        reader = _ValidatedCharacterReader(page=page, issues=issues)
        reader.validate_blocks(blocks)
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                issues.append(
                    StructureIssue(
                        "page-block-malformed",
                        "blocking",
                        None,
                        (page,),
                        f"non-dict top-level block at index {block_index}",
                    )
                )
                continue
            if block.get("type") == 2:
                walk(
                    block,
                    page=page,
                    path=(),
                    ancestors=(),
                    nearest_list_id=None,
                    nearest_item_id=None,
                    parent_std=None,
                    reader=reader,
                )

    if structure_tree_present and not tagged_pages:
        issues.append(
            StructureIssue(
                "structure-extraction-empty",
                "blocking",
                None,
                (),
                "/StructTreeRoot exists but TEXT_COLLECT_STRUCTURE emitted no structure",
            )
        )
    if structure_tree_present and tagged_pages and not lists:
        issues.append(
            StructureIssue(
                "list-tags-empty",
                "advisory",
                None,
                (),
                "tag tree contains no standard /L elements",
            )
        )

    list_rows: list[ListObservation] = []
    for occurrence_id, aggregate in sorted(
        lists.items(), key=lambda row: _path_sort_key(row[1].path)
    ):
        pages = tuple(sorted(aggregate.evidence))
        direct_items = tuple(
            sorted(
                aggregate.direct_items,
                key=lambda item_id: _path_sort_key(items[item_id].path),
            )
        )
        if not direct_items:
            issues.append(
                StructureIssue(
                    "list-without-items",
                    "blocking",
                    occurrence_id,
                    pages,
                    "/L has no direct /LI children",
                )
            )
        list_rows.append(
            ListObservation(
                occurrence_id=occurrence_id,
                structure_path=aggregate.path,
                parent_list_id=aggregate.parent_list_id,
                parent_item_id=aggregate.parent_item_id,
                ancestor_roles=aggregate.ancestors,
                direct_item_ids=direct_items,
                pages=pages,
                evidence=tuple(aggregate.evidence[p] for p in pages),
            )
        )

    item_rows = [
        ListItemObservation(
            occurrence_id=occurrence_id,
            structure_path=aggregate.path,
            parent_list_id=aggregate.parent_list_id or "",
            ancestor_roles=aggregate.ancestors,
            pages=tuple(sorted(aggregate.evidence)),
            evidence=tuple(
                aggregate.evidence[p] for p in sorted(aggregate.evidence)
            ),
        )
        for occurrence_id, aggregate in sorted(
            items.items(), key=lambda row: _path_sort_key(row[1].path)
        )
    ]
    issues.sort(key=lambda issue: (issue.code, issue.occurrence_id or "", issue.pages))
    blocking = sum(issue.severity == "blocking" for issue in issues)
    advisory = sum(issue.severity == "advisory" for issue in issues)
    status = "blocked" if blocking else "advisory" if advisory else "ok"
    return PDFStructureObservation(
        schema_version=SCHEMA_VERSION,
        source_pdf=source_pdf,
        source_sha256=source_sha256,
        pymupdf_version=pymupdf_version,
        extraction_flags=EXTRACTION_FLAGS,
        status=status,
        capabilities={
            "hierarchy": "TEXT_COLLECT_STRUCTURE standard-role/index path",
            "source_locator": "global structure path plus 1-based page",
            "visible_text": True,
            "page_bbox": True,
            "raw_zwsp_separator": True,
            "raw_character_boxes": True,
            "mcid": False,
            "complete_visible_list_detection": False,
            "claim_scope": "observed PDF tags only; no semantic interpretation",
        },
        stats={
            "source_pages": source_pages,
            "tagged_pages": len(tagged_pages),
            "pages_with_lists": len(list_pages),
            "lists": len(list_rows),
            "list_items": len(item_rows),
            "list_page_occurrences": sum(len(row.pages) for row in list_rows),
            "list_item_page_occurrences": sum(len(row.pages) for row in item_rows),
            "blocking_issues": blocking,
            "advisory_issues": advisory,
        },
        lists=tuple(list_rows),
        list_items=tuple(item_rows),
        issues=tuple(issues),
    )


def observe_pdf(source_pdf: str | Path) -> PDFStructureObservation:
    """Observe list claims directly from a PDF using pinned PyMuPDF 1.28.2."""
    source_path = Path(source_pdf)
    source_bytes = source_path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    with fitz.open(stream=source_bytes, filetype="pdf") as document:
        catalog = document.pdf_catalog()
        struct_kind, _ = document.xref_get_key(catalog, "StructTreeRoot")
        structure_tree_present = struct_kind == "xref"
        pages = [
            (page_index, page.get_text("rawdict", flags=EXTRACTION_FLAGS))
            for page_index, page in enumerate(document, 1)
        ]
        return _build_observation(
            source_pdf=str(source_path),
            source_sha256=source_sha256,
            page_dicts=pages,
            source_pages=len(document),
            structure_tree_present=structure_tree_present,
            pymupdf_version=PYMUPDF_VERSION,
        )
