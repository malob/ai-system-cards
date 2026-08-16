"""Source-bound page and raster-figure inventory verification.

Every PDF page and every raw ``Page.get_image_info`` occurrence is required by
default.  The *only* exclusion authority is a checked-in inventory overlay
passed to :func:`verify`.  That overlay is bound to the exact PDF SHA-256 and
observer schema, and every exclusion repeats the exact source observation it
was reviewed against.  Missing, malformed, or stale authority fails closed:
the checker emits a major and keeps the affected page / figure projectable.

The cover / TOC and duplicate-draw heuristics in this module are proposal
helpers only.  They are deliberately never consulted by the release gate.
Likewise, generator ``toc_pages`` and ``figures-map.json`` data are merely
claims checked against the source, never authority for omitting source data.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import pymupdf as fitz

SCHEMA_VERSION = 2
INVENTORY_SCHEMA_VERSION = 1
OBSERVER_SCHEMA_VERSION = 2
PROJECTION_SCHEMA_VERSION = 1
PROJECTION_DIGEST_METHOD = "l2.sections_sha256.v1"
PYMUPDF_VERSION = str(getattr(fitz, "__version__", "unknown"))
TOC_FRONTMATTER_LIMIT = 20
TOC_MIN_INTERNAL_LINKS = 12
DUPLICATE_DRAW_OVERLAP = 0.90

RE_FIGURE_NAME = re.compile(r"^p(?P<page>\d{3,})-(?P<ordinal>[1-9]\d*)\.png$")
RE_CARD_ID = re.compile(r"^[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*$")
RE_SHA256 = re.compile(r"^[0-9a-f]{64}$")

INVENTORY_KEYS = {
    "schema_version",
    "observer_schema_version",
    "pymupdf_version",
    "source_sha256",
    "page_exclusions",
    "figure_exclusions",
}
PAGE_EXCLUSION_KEYS = {"page", "kind", "reason", "observation"}
FIGURE_EXCLUSION_COMMON_KEYS = {"filename", "kind", "reason", "observation"}


@dataclass(frozen=True)
class FigureObservation:
    """One displayed raster occurrence, in source-page display order."""

    page: int
    ordinal: int
    xref: int
    digest: str
    width: int
    height: int
    bbox: tuple[float, float, float, float]
    asset_digest: str = ""
    has_smask: bool = False

    @property
    def filename(self) -> str:
        return f"p{self.page:03d}-{self.ordinal}.png"


@dataclass(frozen=True)
class PageObservation:
    page: int
    word_count: int
    text_chars: int
    internal_links: int
    uri_links: int
    drawing_count: int
    raster_count: int

    @property
    def visibly_blank(self) -> bool:
        return (
            self.text_chars == 0
            and self.internal_links == 0
            and self.uri_links == 0
            and self.drawing_count == 0
            and self.raster_count == 0
        )


@dataclass(frozen=True)
class SourceObservation:
    source_pdf: str
    source_sha256: str
    pages: tuple[PageObservation, ...]
    raw_figures: tuple[FigureObservation, ...]


@dataclass(frozen=True)
class InventoryAuthority:
    """Validated omission authority; invalid entries never reach this type."""

    page_exclusions: Mapping[int, tuple[str, str]]
    duplicate_draws: Mapping[str, tuple[str, str]]
    allowed_skips: Mapping[str, str]


@dataclass(frozen=True)
class PageDisposition:
    page: int
    kind: str
    evidence: dict


@dataclass
class SourceInventoryReport:
    schema_version: int
    source_pdf: str
    source_sha256: str
    stats: dict[str, int]
    page_dispositions: list[dict]
    figures: list[dict]
    flags: list[dict]
    exclusions: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "source_pdf": self.source_pdf,
            "source_sha256": self.source_sha256,
            "stats": self.stats,
            "page_dispositions": self.page_dispositions,
            "figures": self.figures,
            "flags": self.flags,
            "exclusions": self.exclusions,
        }


@dataclass(frozen=True)
class SourceProjectionArtifact:
    """Portable source authority consumed by the final-DOM verifier.

    The artifact contains no Markdown interpretation.  Its only canonical-side
    input is an opaque digest over the exact ordered section filenames/bytes,
    using the same framing method as L2.
    """

    document: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return self.document

    def to_json(self) -> str:
        return json.dumps(
            self.document, indent=2, ensure_ascii=False, sort_keys=True
        )


class ProjectionArtifactError(ValueError):
    """The portable projection authority could not be issued safely."""


def _flag(invariant: str, page: int, kind: str, **detail) -> dict:
    return {
        "invariant": invariant,
        "page": page,
        "severity": "major",
        "detail": {"kind": kind, **detail},
    }


def _flag_sort_key(flag: dict) -> tuple:
    return (
        flag["invariant"],
        flag["page"],
        flag["detail"]["kind"],
        json.dumps(flag["detail"], sort_keys=True),
    )


def _internal_link(link: dict) -> bool:
    """Recognize resolved /GoTo and named destinations across PyMuPDF APIs."""
    destination = link.get("page")
    return (
        isinstance(destination, int)
        and destination >= 0
        and link.get("kind") in {fitz.LINK_GOTO, fitz.LINK_NAMED}
    )


def _source_asset_identity(
    document: fitz.Document, xref: int, smask_xref: int
) -> tuple[str, str, bool]:
    """Return the exact decoded PNG sample digest expected from extraction.

    ``pdfimages`` emits an RGB base image and a separate soft mask.  The
    repository extraction step combines those as premultiplied RGBA, so do the
    same directly from PDF objects.  This retains the raw ``get_image_info``
    digest as a separate observation while making RGBA assets checkable too.
    """
    if xref <= 0:
        return "", "", False
    base = fitz.Pixmap(document, xref)
    if base.colorspace is None:
        raise RuntimeError(f"source image xref {xref} has no color space")
    if base.colorspace.n != fitz.csRGB.n:
        base = fitz.Pixmap(fitz.csRGB, base)
    if base.alpha:
        base = fitz.Pixmap(base, 0)
    base_digest = hashlib.md5(base.samples).hexdigest()
    if smask_xref <= 0:
        return base_digest, base_digest, False

    mask = fitz.Pixmap(document, smask_xref)
    if (mask.width, mask.height) != (base.width, base.height) or mask.n != 1:
        raise RuntimeError(
            f"source soft mask xref {smask_xref} has incompatible geometry"
        )
    combined = fitz.Pixmap(base, mask)
    return base_digest, hashlib.md5(combined.samples).hexdigest(), True


@lru_cache(maxsize=8)
def _observe_source_cached(source_path: str, expected_sha256: str) -> SourceObservation:
    """Parse an immutable PDF content identity once per verifier process."""
    source_pdf = Path(source_path)
    source_bytes = source_pdf.read_bytes()
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(f"source PDF changed while inventorying: {source_pdf}")
    page_observations: list[PageObservation] = []
    figures: list[FigureObservation] = []

    with fitz.open(stream=source_bytes, filetype="pdf") as document:
        for page_index, page in enumerate(document):
            page_number = page_index + 1
            links = page.get_links()
            image_info = page.get_image_info(hashes=True, xrefs=True)
            smask_by_xref = {
                int(item[0]): int(item[1] or 0) for item in page.get_images(full=True)
            }
            words = page.get_text("words")
            text = page.get_text("text")
            page_observations.append(
                PageObservation(
                    page=page_number,
                    word_count=len(words),
                    text_chars=len("".join(text.split())),
                    internal_links=sum(_internal_link(link) for link in links),
                    uri_links=sum(bool(link.get("uri")) for link in links),
                    drawing_count=len(page.get_cdrawings()),
                    raster_count=len(image_info),
                )
            )
            for ordinal, image in enumerate(image_info, 1):
                digest = image.get("digest", b"")
                if isinstance(digest, bytes):
                    digest = digest.hex()
                bbox = tuple(round(float(value), 4) for value in image["bbox"])
                xref = int(image.get("xref") or 0)
                base_digest, asset_digest, has_smask = _source_asset_identity(
                    document, xref, smask_by_xref.get(xref, 0)
                )
                if xref > 0 and base_digest != str(digest):
                    raise RuntimeError(
                        f"get_image_info digest disagrees with xref {xref} pixels"
                    )
                figures.append(
                    FigureObservation(
                        page=page_number,
                        ordinal=ordinal,
                        xref=xref,
                        digest=str(digest),
                        width=int(image.get("width") or 0),
                        height=int(image.get("height") or 0),
                        bbox=bbox,
                        asset_digest=asset_digest,
                        has_smask=has_smask,
                    )
                )

    return SourceObservation(
        source_pdf=str(source_pdf),
        source_sha256=actual_sha256,
        pages=tuple(page_observations),
        raw_figures=tuple(figures),
    )


def observe_source(source_pdf: str | Path) -> SourceObservation:
    """Read page and displayed-raster facts directly from ``source.pdf``.

    The file is hashed on every call so an in-process source change cannot hide
    behind the cache. Expensive page parsing is reused only for the same content
    digest, which keeps seeded mutation runs practical without weakening source
    identity.
    """
    source_pdf = Path(source_pdf).resolve()
    source_sha256 = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
    return _observe_source_cached(str(source_pdf), source_sha256)


def _contiguous_runs(pages: Iterable[int]) -> list[tuple[int, ...]]:
    runs: list[list[int]] = []
    for page in sorted(set(pages)):
        if not runs or page != runs[-1][-1] + 1:
            runs.append([page])
        else:
            runs[-1].append(page)
    return [tuple(run) for run in runs]


def classify_page_dispositions(
    source: SourceObservation,
) -> tuple[list[PageDisposition], list[dict], list[dict]]:
    """Propose cover / TOC candidates for human inventory review.

    This helper is not called by :func:`verify` and has no exclusion authority.
    Generator-declared TOC pages are intentionally not an input.  Ambiguous
    source evidence remains content even in this proposal.
    """
    if not source.pages:
        return [], [_flag("P2", 0, "empty-source-pdf")], []

    flags: list[dict] = []
    exclusions: list[dict] = []
    first = source.pages[0]
    if first.word_count > 150 or first.internal_links >= TOC_MIN_INTERNAL_LINKS:
        flags.append(
            _flag(
                "P2",
                1,
                "cover-page-atypical",
                word_count=first.word_count,
                internal_links=first.internal_links,
            )
        )

    candidates = [
        page.page
        for page in source.pages[1:TOC_FRONTMATTER_LIMIT]
        if page.internal_links >= TOC_MIN_INTERNAL_LINKS and page.uri_links == 0
    ]
    runs = _contiguous_runs(candidates)
    qualifying = [run for run in runs if len(run) >= 2]
    toc_pages: set[int] = set()
    if len(qualifying) == 1 and sum(len(run) for run in runs) == len(qualifying[0]):
        toc_pages.update(qualifying[0])
    elif candidates:
        flags.append(
            _flag(
                "P2",
                candidates[0],
                "toc-source-ambiguous",
                candidate_runs=[list(run) for run in runs],
                policy={
                    "frontmatter_limit": TOC_FRONTMATTER_LIMIT,
                    "minimum_internal_links": TOC_MIN_INTERNAL_LINKS,
                    "minimum_run": 2,
                },
            )
        )

    dispositions: list[PageDisposition] = []
    for observation in source.pages:
        if observation.page == 1:
            kind = "cover"
        elif observation.page in toc_pages:
            kind = "toc"
        elif observation.visibly_blank:
            kind = "blank"
            flags.append(
                _flag(
                    "P2",
                    observation.page,
                    "unadjudicated-blank-page",
                )
            )
        else:
            kind = "content"
        evidence = {
            "word_count": observation.word_count,
            "internal_links": observation.internal_links,
            "uri_links": observation.uri_links,
            "raster_count": observation.raster_count,
            "drawing_count": observation.drawing_count,
        }
        dispositions.append(PageDisposition(observation.page, kind, evidence))
        if kind in {"cover", "toc"}:
            exclusions.append(
                {
                    "kind": f"source-{kind}-page",
                    "page": observation.page,
                    "evidence": evidence,
                }
            )
    return dispositions, flags, exclusions


def _page_evidence(observation: PageObservation) -> dict[str, Any]:
    return asdict(observation)


def _figure_evidence(observation: FigureObservation) -> dict[str, Any]:
    # JSON has no tuple type.  Canonicalize bbox explicitly so an in-memory
    # test mapping and a parsed checked-in JSON document compare identically.
    return {
        "page": observation.page,
        "ordinal": observation.ordinal,
        "xref": observation.xref,
        "digest": observation.digest,
        "width": observation.width,
        "height": observation.height,
        "bbox": list(observation.bbox),
        "asset_digest": observation.asset_digest,
        "has_smask": observation.has_smask,
    }


def _authority_pair(kind: str, **detail: Any) -> list[dict]:
    """A broken global overlay invalidates both independent authority lanes."""
    return [
        _flag("P2", 0, kind, **detail),
        _flag("F3", 0, kind, **detail),
    ]


def _load_inventory_document(
    inventory: Mapping[str, Any] | str | Path | None,
) -> tuple[Mapping[str, Any] | None, list[dict]]:
    if inventory is None:
        return None, _authority_pair("source-inventory-missing")
    if isinstance(inventory, Mapping):
        return inventory, []
    if not isinstance(inventory, (str, Path)):
        return None, _authority_pair(
            "source-inventory-malformed", problem="not-a-mapping-or-path"
        )
    path = Path(inventory)
    try:
        parsed = json.loads(path.read_text())
    except FileNotFoundError:
        return None, _authority_pair(
            "source-inventory-missing", inventory_path=str(path)
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, _authority_pair(
            "source-inventory-malformed",
            inventory_path=str(path),
            problem=type(error).__name__,
        )
    if not isinstance(parsed, Mapping):
        return None, _authority_pair(
            "source-inventory-malformed",
            inventory_path=str(path),
            problem="top-level-value-is-not-an-object",
        )
    return parsed, []


def _validate_inventory(
    source: SourceObservation,
    inventory: Mapping[str, Any] | str | Path | None,
) -> tuple[InventoryAuthority, list[dict]]:
    """Validate the exclusion overlay without ever inferring an exclusion.

    Global identity/schema failures reject the whole overlay.  A malformed or
    stale individual entry rejects only that entry, leaving its source item
    required.  This is important: an inventory typo must produce too many
    required items, never silently hide one.
    """
    empty = InventoryAuthority({}, {}, {})
    document, flags = _load_inventory_document(inventory)
    if document is None:
        return empty, flags

    if set(document) != INVENTORY_KEYS:
        flags.extend(
            _authority_pair(
                "source-inventory-malformed",
                problem="unexpected-top-level-keys",
                expected=sorted(INVENTORY_KEYS),
                actual=sorted(str(key) for key in document),
            )
        )
        return empty, flags
    if document.get("schema_version") != INVENTORY_SCHEMA_VERSION:
        flags.extend(
            _authority_pair(
                "source-inventory-stale",
                problem="inventory-schema-version",
                expected=INVENTORY_SCHEMA_VERSION,
                actual=document.get("schema_version"),
            )
        )
        return empty, flags
    if document.get("observer_schema_version") != OBSERVER_SCHEMA_VERSION:
        flags.extend(
            _authority_pair(
                "source-inventory-stale",
                problem="observer-schema-version",
                expected=OBSERVER_SCHEMA_VERSION,
                actual=document.get("observer_schema_version"),
            )
        )
        return empty, flags
    if document.get("pymupdf_version") != PYMUPDF_VERSION:
        flags.extend(
            _authority_pair(
                "source-inventory-stale",
                problem="pymupdf-version",
                expected=PYMUPDF_VERSION,
                actual=document.get("pymupdf_version"),
            )
        )
        return empty, flags
    if document.get("source_sha256") != source.source_sha256:
        flags.extend(
            _authority_pair(
                "source-inventory-stale",
                problem="source-sha256",
                expected=source.source_sha256,
                actual=document.get("source_sha256"),
            )
        )
        return empty, flags
    raw_pages = document.get("page_exclusions")
    raw_figures = document.get("figure_exclusions")
    if not isinstance(raw_pages, list) or not isinstance(raw_figures, list):
        flags.extend(
            _authority_pair(
                "source-inventory-malformed",
                problem="exclusions-must-be-arrays",
            )
        )
        return empty, flags

    page_by_number = {item.page: item for item in source.pages}
    page_candidates: list[tuple[int, str, str]] = []
    for index, entry in enumerate(raw_pages):
        if not isinstance(entry, Mapping) or set(entry) != PAGE_EXCLUSION_KEYS:
            flags.append(
                _flag(
                    "P2",
                    0,
                    "page-exclusion-malformed",
                    index=index,
                    expected_keys=sorted(PAGE_EXCLUSION_KEYS),
                )
            )
            continue
        page = entry.get("page")
        kind = entry.get("kind")
        reason = entry.get("reason")
        observation = page_by_number.get(page) if type(page) is int else None
        problem = None
        if observation is None:
            problem = "unknown-page"
        elif not isinstance(kind, str) or kind not in {"cover", "toc", "blank"}:
            problem = "unknown-kind"
        elif not isinstance(reason, str) or not reason.strip():
            problem = "empty-reason"
        elif entry.get("observation") != _page_evidence(observation):
            problem = "observation-mismatch"
        elif kind == "cover" and page != 1:
            problem = "cover-must-be-page-one"
        elif kind == "blank" and not observation.visibly_blank:
            problem = "nonblank-page-declared-blank"
        if problem:
            flags.append(
                _flag(
                    "P2",
                    int(page) if type(page) is int else 0,
                    "page-exclusion-stale",
                    index=index,
                    problem=problem,
                )
            )
            continue
        page_candidates.append((page, str(kind), reason.strip()))

    duplicate_pages = {
        page
        for page, count in Counter(item[0] for item in page_candidates).items()
        if count > 1
    }
    for page in sorted(duplicate_pages):
        flags.append(_flag("P2", page, "duplicate-page-exclusion"))
    page_authority = {
        page: (kind, reason)
        for page, kind, reason in page_candidates
        if page not in duplicate_pages
    }

    figure_by_name = {item.filename: item for item in source.raw_figures}
    figure_candidates: list[tuple[str, str, str, str | None]] = []
    for index, entry in enumerate(raw_figures):
        if not isinstance(entry, Mapping):
            flags.append(_flag("F3", 0, "figure-exclusion-malformed", index=index))
            continue
        kind = entry.get("kind")
        expected_keys = (
            FIGURE_EXCLUSION_COMMON_KEYS | {"duplicate_of"}
            if kind == "duplicate-draw"
            else FIGURE_EXCLUSION_COMMON_KEYS
        )
        name = entry.get("filename")
        match = RE_FIGURE_NAME.fullmatch(name) if isinstance(name, str) else None
        page = int(match.group("page")) if match else 0
        if set(entry) != expected_keys:
            flags.append(
                _flag(
                    "F3",
                    page,
                    "figure-exclusion-malformed",
                    index=index,
                    expected_keys=sorted(expected_keys),
                )
            )
            continue
        figure = figure_by_name.get(name) if isinstance(name, str) else None
        reason = entry.get("reason")
        duplicate_of = entry.get("duplicate_of") if kind == "duplicate-draw" else None
        problem = None
        if not isinstance(kind, str) or kind not in {"duplicate-draw", "allow-skip"}:
            problem = "unknown-kind"
        elif not isinstance(name, str):
            problem = "invalid-filename"
        elif figure is None:
            problem = "unknown-source-occurrence"
        elif not isinstance(reason, str) or not reason.strip():
            problem = "empty-reason"
        elif entry.get("observation") != _figure_evidence(figure):
            problem = "observation-mismatch"
        elif kind == "allow-skip" and figure.page in page_authority:
            problem = "skip-occurrence-not-projectable"
        elif kind == "duplicate-draw":
            prior = (
                figure_by_name.get(duplicate_of)
                if isinstance(duplicate_of, str)
                else None
            )
            source_order = {
                item.filename: index for index, item in enumerate(source.raw_figures)
            }
            if not isinstance(duplicate_of, str) or prior is None or prior == figure:
                problem = "unknown-duplicate-target"
            elif source_order[duplicate_of] >= source_order[figure.filename]:
                problem = "duplicate-target-must-precede-occurrence"
            elif (
                prior.page != figure.page
                or prior.digest != figure.digest
                or (prior.width, prior.height) != (figure.width, figure.height)
                or _overlap_fraction(prior.bbox, figure.bbox) < DUPLICATE_DRAW_OVERLAP
            ):
                problem = "duplicate-claim-not-supported-by-observation"
        if problem:
            flags.append(
                _flag(
                    "F3",
                    figure.page if figure else page,
                    "figure-exclusion-stale",
                    index=index,
                    filename=name,
                    problem=problem,
                )
            )
            continue
        figure_candidates.append((name, str(kind), reason.strip(), duplicate_of))

    duplicate_names = {
        name
        for name, count in Counter(item[0] for item in figure_candidates).items()
        if count > 1
    }
    for name in sorted(duplicate_names):
        figure = figure_by_name[name]
        flags.append(
            _flag("F3", figure.page, "duplicate-figure-exclusion", filename=name)
        )
    duplicate_authority = {
        name: (str(duplicate_of), reason)
        for name, kind, reason, duplicate_of in figure_candidates
        if name not in duplicate_names and kind == "duplicate-draw"
    }
    skip_authority = {
        name: reason
        for name, kind, reason, _ in figure_candidates
        if name not in duplicate_names and kind == "allow-skip"
    }
    return (
        InventoryAuthority(page_authority, duplicate_authority, skip_authority),
        flags,
    )


def verify_page_disposition(
    source: SourceObservation,
    authority: InventoryAuthority,
    claimed_toc_pages: Iterable[int] | None = None,
) -> tuple[list[PageDisposition], list[dict], list[dict]]:
    """Validate exact source exclusions and the generator's TOC claim.

    Published page anchors are checked against the built DOM.  Keeping that
    projection check out of this module avoids reimplementing the repository's
    CommonMark, raw-HTML, and remark-directive grammar in Python.
    """
    flags: list[dict] = []
    exclusions: list[dict] = []
    dispositions: list[PageDisposition] = []
    for observation in source.pages:
        authorized = authority.page_exclusions.get(observation.page)
        kind, reason = authorized if authorized else ("content", None)
        evidence = _page_evidence(observation)
        dispositions.append(PageDisposition(observation.page, kind, evidence))
        if authorized:
            exclusions.append(
                {
                    "kind": f"source-{kind}-page",
                    "page": observation.page,
                    "reason": reason,
                    "observation": evidence,
                }
            )
    if claimed_toc_pages is not None:
        claimed = {int(page) for page in claimed_toc_pages}
        authorized_toc = {item.page for item in dispositions if item.kind == "toc"}
        for page in sorted(claimed - authorized_toc):
            flags.append(
                _flag(
                    "P2",
                    page,
                    "unsupported-toc-exclusion",
                    authorized_toc_pages=sorted(authorized_toc),
                )
            )
        for page in sorted(authorized_toc - claimed):
            flags.append(
                _flag(
                    "P2",
                    page,
                    "unclaimed-toc-page",
                    claimed_toc_pages=sorted(claimed),
                )
            )

    return dispositions, flags, exclusions


def _area(bbox: tuple[float, float, float, float]) -> float:
    return max(0.0, bbox[2] - bbox[0]) * max(0.0, bbox[3] - bbox[1])


def _overlap_fraction(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> float:
    intersection = max(0.0, min(left[2], right[2]) - max(left[0], right[0])) * max(
        0.0, min(left[3], right[3]) - max(left[1], right[1])
    )
    smaller = min(_area(left), _area(right))
    return intersection / smaller if smaller else 0.0


def collapse_duplicate_draws(
    figures: Sequence[FigureObservation],
) -> tuple[list[FigureObservation], list[dict]]:
    """Propose near-coincident duplicate draws for human inventory review.

    This helper is not called by :func:`verify` and has no exclusion authority.
    """
    kept: list[FigureObservation] = []
    exclusions: list[dict] = []
    kept_by_page: dict[int, list[FigureObservation]] = defaultdict(list)
    for figure in figures:
        duplicate_of = next(
            (
                prior
                for prior in kept_by_page[figure.page]
                if figure.digest
                and figure.digest == prior.digest
                and (figure.width, figure.height) == (prior.width, prior.height)
                and _overlap_fraction(figure.bbox, prior.bbox) >= DUPLICATE_DRAW_OVERLAP
            ),
            None,
        )
        if duplicate_of is None:
            kept.append(figure)
            kept_by_page[figure.page].append(figure)
        else:
            exclusions.append(
                {
                    "kind": "duplicate-image-draw",
                    "page": figure.page,
                    "filename": figure.filename,
                    "duplicate_of": duplicate_of.filename,
                    "digest": figure.digest,
                    "overlap_fraction": round(
                        _overlap_fraction(figure.bbox, duplicate_of.bbox), 4
                    ),
                }
            )
    return kept, exclusions


def _normalize_figure_map(
    claimed: Mapping[str | int, Sequence[str]],
) -> tuple[dict[int, list[str]], list[dict]]:
    normalized: dict[int, list[str]] = {}
    flags: list[dict] = []
    for raw_page, raw_names in claimed.items():
        try:
            page = int(raw_page)
        except (TypeError, ValueError):
            flags.append(_flag("F3", 0, "invalid-figure-map-page", value=str(raw_page)))
            continue
        if isinstance(raw_names, (str, bytes)) or not isinstance(raw_names, Sequence):
            flags.append(
                _flag("F3", page, "invalid-figure-map-entry", value=repr(raw_names))
            )
            continue
        if page in normalized:
            flags.append(
                _flag(
                    "F3",
                    page,
                    "duplicate-figure-map-page",
                    value=str(raw_page),
                )
            )
            continue
        normalized[page] = [str(name) for name in raw_names]
    return normalized, flags


@lru_cache(maxsize=1024)
def _decode_png_cached(
    asset_path: str, expected_file_sha256: str
) -> tuple[int, int, str, bool]:
    """Decode immutable PNG bytes once and return RGB pixel identity.

    PyMuPDF's source digest is over decoded base color samples.  The independent
    observation also records the exact decoded RGB/RGBA digest expected after
    combining a PDF soft mask, so alpha-bearing assets remain fully checkable.
    """
    data = Path(asset_path).read_bytes()
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_file_sha256:
        raise RuntimeError("asset changed while decoding")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("asset is not a PNG")
    pixmap = fitz.Pixmap(data)
    width, height = pixmap.width, pixmap.height
    had_alpha = bool(pixmap.alpha)
    if pixmap.colorspace is None:
        raise ValueError("PNG has no color space")
    if pixmap.colorspace.n != fitz.csRGB.n:
        pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
    return width, height, hashlib.md5(pixmap.samples).hexdigest(), had_alpha


def _decode_png(asset_path: Path) -> tuple[int, int, str, bool]:
    data = asset_path.read_bytes()
    return _decode_png_cached(
        str(asset_path.resolve()), hashlib.sha256(data).hexdigest()
    )


def verify_figures(
    source: SourceObservation,
    dispositions: Sequence[PageDisposition],
    authority: InventoryAuthority,
    claimed_figure_map: Mapping[str | int, Sequence[str]] | None = None,
    figure_dir: str | Path | None = None,
) -> tuple[list[dict], list[dict], list[dict], dict[str, int]]:
    """Bind the raw PDF raster inventory to map claims and local PNG bytes.

    Final rendered figure presence/order belongs to the built-DOM projection
    audit.  This lane establishes the independent source inventory that audit
    must satisfy.
    """
    source_by_name = {figure.filename: figure for figure in source.raw_figures}
    duplicate_names = set(authority.duplicate_draws)
    visual_figures = [
        figure
        for figure in source.raw_figures
        if figure.filename not in duplicate_names
    ]
    kind_by_page = {item.page: item.kind for item in dispositions}
    expected_projected = [
        figure
        for figure in visual_figures
        if kind_by_page.get(figure.page) == "content"
    ]
    exclusions: list[dict] = []
    for name, (duplicate_of, reason) in authority.duplicate_draws.items():
        figure = source_by_name[name]
        exclusions.append(
            {
                "kind": "duplicate-image-draw",
                "page": figure.page,
                "filename": name,
                "duplicate_of": duplicate_of,
                "reason": reason,
                "observation": _figure_evidence(figure),
            }
        )
    for figure in visual_figures:
        page_kind = kind_by_page.get(figure.page)
        if page_kind in {"cover", "toc", "blank"}:
            exclusions.append(
                {
                    "kind": f"figure-on-{page_kind}-page",
                    "page": figure.page,
                    "filename": figure.filename,
                    "digest": figure.digest,
                    "reason": authority.page_exclusions[figure.page][1],
                }
            )
    for name, reason in authority.allowed_skips.items():
        figure = source_by_name[name]
        exclusions.append(
            {
                "kind": "accepted-figure-skip",
                "page": figure.page,
                "filename": name,
                "reason": reason,
                "observation": _figure_evidence(figure),
            }
        )

    flags: list[dict] = []
    if claimed_figure_map is None:
        flags.append(_flag("F3", 0, "figure-map-missing"))
    else:
        claimed, claim_flags = _normalize_figure_map(claimed_figure_map)
        flags.extend(claim_flags)
        expected_map: dict[int, list[str]] = defaultdict(list)
        for figure in source.raw_figures:
            expected_map[figure.page].append(figure.filename)
        for page in sorted(set(expected_map) | set(claimed)):
            expected = expected_map.get(page, [])
            actual = claimed.get(page, [])
            if expected != actual:
                flags.append(
                    _flag(
                        "F3",
                        page,
                        "figure-map-source-mismatch",
                        expected=expected,
                        claimed=actual,
                    )
                )

    if figure_dir is None:
        flags.append(_flag("F3", 0, "figure-asset-directory-not-supplied"))
    else:
        figure_dir = Path(figure_dir)
        expected_assets = {figure.filename for figure in source.raw_figures}
        if not figure_dir.is_dir():
            flags.append(
                _flag(
                    "F3",
                    0,
                    "figure-asset-directory-missing",
                    directory=str(figure_dir),
                )
            )
        else:
            actual_assets = {path.name for path in figure_dir.glob("*.png")}
            for name in sorted(expected_assets - actual_assets):
                match = RE_FIGURE_NAME.fullmatch(name)
                flags.append(
                    _flag(
                        "F3",
                        int(match.group("page")),
                        "source-figure-asset-missing",
                        filename=name,
                    )
                )
            for name in sorted(actual_assets - expected_assets):
                match = RE_FIGURE_NAME.fullmatch(name)
                flags.append(
                    _flag(
                        "F3",
                        int(match.group("page")) if match else 0,
                        "unexplained-figure-asset",
                        filename=name,
                    )
                )
            for name in sorted(expected_assets & actual_assets):
                figure = source_by_name[name]
                asset_path = figure_dir / name
                try:
                    width, height, digest, had_alpha = _decode_png(asset_path)
                except (OSError, RuntimeError, ValueError, fitz.FileDataError) as error:
                    flags.append(
                        _flag(
                            "F3",
                            figure.page,
                            "source-figure-asset-invalid",
                            filename=name,
                            problem=str(error),
                        )
                    )
                    continue
                expected_asset_digest = figure.asset_digest or figure.digest
                if (width, height, digest, had_alpha) != (
                    figure.width,
                    figure.height,
                    expected_asset_digest,
                    figure.has_smask,
                ):
                    flags.append(
                        _flag(
                            "F3",
                            figure.page,
                            "source-figure-asset-mismatch",
                            filename=name,
                            expected={
                                "width": figure.width,
                                "height": figure.height,
                                "digest": expected_asset_digest,
                                "has_alpha": figure.has_smask,
                            },
                            actual={
                                "width": width,
                                "height": height,
                                "digest": digest,
                                "had_alpha": had_alpha,
                            },
                        )
                    )

    figures = []
    for figure in source.raw_figures:
        if figure.filename in duplicate_names:
            disposition = "duplicate-draw"
        elif figure.filename in authority.allowed_skips:
            disposition = "accepted-skip"
        elif kind_by_page.get(figure.page) == "content":
            disposition = "required-output"
        else:
            disposition = f"excluded-{kind_by_page.get(figure.page, 'unknown')}"
        figures.append(
            {**asdict(figure), "filename": figure.filename, "disposition": disposition}
        )

    stats = {
        "raw_source_figures": len(source.raw_figures),
        "visual_source_figures": len(visual_figures),
        "projectable_source_figures": len(expected_projected),
        "required_output_figures": sum(
            figure.filename not in authority.allowed_skips
            for figure in expected_projected
        ),
        "duplicate_draw_exclusions": len(duplicate_names),
    }
    return figures, flags, exclusions, stats


def verify(
    source_pdf: str | Path,
    *,
    inventory: Mapping[str, Any] | str | Path | None = None,
    claimed_toc_pages: Iterable[int] | None = None,
    claimed_figure_map: Mapping[str | int, Sequence[str]] | None = None,
    figure_dir: str | Path | None = None,
) -> SourceInventoryReport:
    """Validate source-bound page/figure authority and extraction claims."""
    source = observe_source(source_pdf)
    authority, inventory_flags = _validate_inventory(source, inventory)
    dispositions, page_flags, page_exclusions = verify_page_disposition(
        source, authority, claimed_toc_pages
    )
    figures, figure_flags, figure_exclusions, figure_stats = verify_figures(
        source,
        dispositions,
        authority,
        claimed_figure_map=claimed_figure_map,
        figure_dir=figure_dir,
    )
    disposition_counts = Counter(item.kind for item in dispositions)
    stats = {
        "source_pages": len(source.pages),
        "cover_pages": disposition_counts["cover"],
        "toc_pages": disposition_counts["toc"],
        "content_pages": disposition_counts["content"],
        "blank_pages": disposition_counts["blank"],
        **figure_stats,
    }
    return SourceInventoryReport(
        schema_version=SCHEMA_VERSION,
        source_pdf=source.source_pdf,
        source_sha256=source.source_sha256,
        stats=stats,
        page_dispositions=[asdict(item) for item in dispositions],
        figures=figures,
        flags=sorted(inventory_flags + page_flags + figure_flags, key=_flag_sort_key),
        exclusions=sorted(
            page_exclusions + figure_exclusions,
            key=lambda item: (
                int(item.get("page", 0)),
                item.get("kind", ""),
                item.get("filename", ""),
            ),
        ),
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _projection_reason_sha256(reason: str) -> str:
    return _sha256_bytes(reason.encode("utf-8"))


def build_projection_artifact(
    source_pdf: str | Path,
    *,
    card_id: str,
    inventory_path: str | Path,
    claimed_toc_pages: Iterable[int] | None,
    figure_map_path: str | Path,
    figure_dir: str | Path,
    canonical_sections_sha256: str,
) -> SourceProjectionArtifact:
    """Issue strict, portable source expectations for the built-DOM audit.

    Both JSON inputs are read once, hashed as exact bytes, parsed, and then
    passed through the source verifier.  No artifact is issued if that verifier
    has even one unresolved flag.  Canonical Markdown is not parsed here: its
    exact ordered byte-stream digest is accepted as an opaque binding from L2.
    """
    if not isinstance(card_id, str) or RE_CARD_ID.fullmatch(card_id) is None:
        raise ProjectionArtifactError(
            "card_id must be a canonical lowercase vendor/slug"
        )
    if (
        not isinstance(canonical_sections_sha256, str)
        or RE_SHA256.fullmatch(canonical_sections_sha256) is None
    ):
        raise ProjectionArtifactError(
            "canonical_sections_sha256 must be a lowercase SHA-256 digest"
        )

    inventory_path = Path(inventory_path)
    figure_map_path = Path(figure_map_path)
    figure_dir = Path(figure_dir)
    try:
        inventory_bytes = inventory_path.read_bytes()
        figure_map_bytes = figure_map_path.read_bytes()
        inventory_document = json.loads(inventory_bytes)
        figure_map_document = json.loads(figure_map_bytes)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProjectionArtifactError(
            f"projection input is unreadable or malformed: {type(error).__name__}"
        ) from error
    if not isinstance(inventory_document, Mapping):
        raise ProjectionArtifactError("source-inventory.json must be an object")
    if not isinstance(figure_map_document, Mapping):
        raise ProjectionArtifactError("figures-map.json must be an object")

    report = verify(
        source_pdf,
        inventory=inventory_document,
        claimed_toc_pages=claimed_toc_pages,
        claimed_figure_map=figure_map_document,
        figure_dir=figure_dir,
    )
    if report.flags:
        kinds = sorted(
            Counter(flag["detail"]["kind"] for flag in report.flags).items()
        )
        raise ProjectionArtifactError(
            "source projection has unresolved flags: "
            + ", ".join(f"{kind}={count}" for kind, count in kinds)
        )

    page_numbers = [item["page"] for item in report.page_dispositions]
    expected_pages = list(range(1, report.stats["source_pages"] + 1))
    if page_numbers != expected_pages:
        raise ProjectionArtifactError(
            "source page dispositions do not cover every PDF page exactly once"
        )

    page_reasons: dict[int, str] = {}
    duplicate_reasons: dict[str, tuple[str, str]] = {}
    skip_reasons: dict[str, str] = {}
    for exclusion in report.exclusions:
        kind = exclusion.get("kind")
        if isinstance(kind, str) and kind.startswith("source-") and kind.endswith(
            "-page"
        ):
            page_reasons[int(exclusion["page"])] = str(exclusion["reason"])
        elif kind == "duplicate-image-draw":
            duplicate_reasons[str(exclusion["filename"])] = (
                str(exclusion["duplicate_of"]),
                str(exclusion["reason"]),
            )
        elif kind == "accepted-figure-skip":
            skip_reasons[str(exclusion["filename"])] = str(exclusion["reason"])

    pages: list[dict[str, Any]] = []
    page_kind: dict[int, str] = {}
    for item in report.page_dispositions:
        page = int(item["page"])
        disposition = str(item["kind"])
        page_kind[page] = disposition
        reason = None if disposition == "content" else page_reasons.get(page)
        if disposition != "content" and not reason:
            raise ProjectionArtifactError(
                f"excluded source page {page} has no validated reason"
            )
        pages.append(
            {
                "pdf_page": page,
                "disposition": disposition,
                "reason_sha256": (
                    _projection_reason_sha256(reason) if reason is not None else None
                ),
                "source_observation": dict(item["evidence"]),
            }
        )

    figure_names = [str(item["filename"]) for item in report.figures]
    if len(figure_names) != len(set(figure_names)):
        raise ProjectionArtifactError("source raster filenames are not unique")
    source_order = [
        (int(item["page"]), int(item["ordinal"])) for item in report.figures
    ]
    if source_order != sorted(source_order):
        raise ProjectionArtifactError("source raster occurrences are not ordered")

    assets: list[dict[str, Any]] = []
    asset_by_name: dict[str, dict[str, Any]] = {}
    for figure in report.figures:
        filename = str(figure["filename"])
        asset_path = figure_dir / filename
        try:
            asset_bytes = asset_path.read_bytes()
            file_sha256 = _sha256_bytes(asset_bytes)
            width, height, decoded_digest, has_alpha = _decode_png_cached(
                str(asset_path.resolve()), file_sha256
            )
        except (OSError, RuntimeError, ValueError, fitz.FileDataError) as error:
            raise ProjectionArtifactError(
                f"could not revalidate projection asset {filename}: {error}"
            ) from error
        expected_digest = str(figure["asset_digest"] or figure["digest"])
        expected_identity = (
            int(figure["width"]),
            int(figure["height"]),
            expected_digest,
            bool(figure["has_smask"]),
        )
        if (width, height, decoded_digest, has_alpha) != expected_identity:
            raise ProjectionArtifactError(
                f"projection asset {filename} changed after source verification"
            )

        disposition = str(figure["disposition"])
        duplicate_of = None
        reason = None
        if disposition == "duplicate-draw":
            duplicate = duplicate_reasons.get(filename)
            if duplicate is None:
                raise ProjectionArtifactError(
                    f"duplicate raster {filename} has no validated authority"
                )
            duplicate_of, reason = duplicate
        elif disposition == "accepted-skip":
            reason = skip_reasons.get(filename)
            if not reason:
                raise ProjectionArtifactError(
                    f"accepted skip {filename} has no validated authority"
                )
            if page_kind[int(figure["page"])] != "content":
                raise ProjectionArtifactError(
                    f"accepted skip {filename} is not on a content page"
                )
        elif disposition.startswith("excluded-"):
            reason = page_reasons.get(int(figure["page"]))
            if not reason:
                raise ProjectionArtifactError(
                    f"excluded raster {filename} has no page authority"
                )
        elif disposition != "required-output":
            raise ProjectionArtifactError(
                f"raster {filename} has unknown disposition {disposition}"
            )

        asset = {
            "filename": filename,
            "logical_path": f"figures/{filename}",
            "file_sha256": file_sha256,
            "width": width,
            "height": height,
            "has_alpha": has_alpha,
            "disposition": disposition,
            "duplicate_of": duplicate_of,
            "reason_sha256": (
                _projection_reason_sha256(reason) if reason is not None else None
            ),
            "source": {
                "pdf_page": int(figure["page"]),
                "draw_index": int(figure["ordinal"]),
                "xref": int(figure["xref"]),
                "raw_sample_md5": str(figure["digest"]),
                "asset_sample_md5": expected_digest,
                "bbox": list(figure["bbox"]),
                "has_soft_mask": bool(figure["has_smask"]),
            },
        }
        assets.append(asset)
        asset_by_name[filename] = asset

    events: list[dict[str, Any]] = []
    assets_by_page: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for asset in assets:
        assets_by_page[int(asset["source"]["pdf_page"])].append(asset)
    for page in pages:
        pdf_page = int(page["pdf_page"])
        if page["disposition"] != "content":
            continue
        events.append({"kind": "page", "pdf_page": pdf_page, "anchor": f"p-{pdf_page}"})
        for asset in assets_by_page.get(pdf_page, []):
            source_identity = asset["source"]
            if asset["disposition"] == "required-output":
                events.append(
                    {
                        "kind": "figure",
                        "pdf_page": pdf_page,
                        "draw_index": source_identity["draw_index"],
                        "filename": asset["filename"],
                        "logical_src": asset["logical_path"],
                        "asset_sha256": asset["file_sha256"],
                    }
                )
            elif asset["disposition"] == "accepted-skip":
                events.append(
                    {
                        "kind": "accepted-skip",
                        "pdf_page": pdf_page,
                        "draw_index": source_identity["draw_index"],
                        "filename": asset["filename"],
                        "reason_sha256": asset["reason_sha256"],
                    }
                )

    # Assert the exact construction invariants before serializing.  These are
    # intentionally redundant with the loops above: a later refactor must not
    # be able to issue a partial or reordered authority artifact.
    if [page["pdf_page"] for page in pages] != expected_pages:
        raise ProjectionArtifactError("projection page coverage is incomplete")
    event_pages = [event["pdf_page"] for event in events if event["kind"] == "page"]
    expected_content_pages = [
        page["pdf_page"] for page in pages if page["disposition"] == "content"
    ]
    if event_pages != expected_content_pages:
        raise ProjectionArtifactError("projection page events are incomplete or reordered")
    event_figures = [
        event["filename"]
        for event in events
        if event["kind"] in {"figure", "accepted-skip"}
    ]
    expected_event_figures = [
        asset["filename"]
        for asset in assets
        if asset["disposition"] in {"required-output", "accepted-skip"}
    ]
    if event_figures != expected_event_figures:
        raise ProjectionArtifactError("projection figure events are incomplete or reordered")
    if set(asset_by_name) != set(figure_names):
        raise ProjectionArtifactError("projection assets do not cover every source raster")

    document = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "card_id": card_id,
        "observer_schema_version": OBSERVER_SCHEMA_VERSION,
        "pymupdf_version": PYMUPDF_VERSION,
        "source": {
            "file": Path(source_pdf).name,
            "sha256": report.source_sha256,
            "page_count": report.stats["source_pages"],
        },
        "inputs": {
            "inventory": {
                "file": "source-inventory.json",
                "sha256": _sha256_bytes(inventory_bytes),
            },
            "figures_map": {
                "file": "extracted/figures-map.json",
                "sha256": _sha256_bytes(figure_map_bytes),
            },
            "canonical_sections": {
                "digest_method": PROJECTION_DIGEST_METHOD,
                "sha256": canonical_sections_sha256,
            },
        },
        "source_flags": [],
        "pages": pages,
        "assets": assets,
        "events": events,
    }
    return SourceProjectionArtifact(document)


__all__ = [
    "DUPLICATE_DRAW_OVERLAP",
    "INVENTORY_SCHEMA_VERSION",
    "OBSERVER_SCHEMA_VERSION",
    "PROJECTION_DIGEST_METHOD",
    "PROJECTION_SCHEMA_VERSION",
    "PYMUPDF_VERSION",
    "FigureObservation",
    "InventoryAuthority",
    "PageDisposition",
    "PageObservation",
    "ProjectionArtifactError",
    "SourceInventoryReport",
    "SourceObservation",
    "SourceProjectionArtifact",
    "build_projection_artifact",
    "classify_page_dispositions",
    "collapse_duplicate_draws",
    "observe_source",
    "verify",
    "verify_figures",
    "verify_page_disposition",
]
