"""Exact, fail-closed handling for adjudicated verifier findings.

An acceptance identifies one complete flag by a canonical SHA-256 fingerprint.
The helper is deliberately independent of card selection and filesystem state so
its matching and validation semantics can be tested in isolation.

Source- and final-projection findings are deliberately outside this generic
authority. Their exception mechanisms must preserve the stronger provenance of
the authority that issued them; ``accepted.json`` cannot act as a parallel,
less-bound escape hatch.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

_ENTRY_KEYS = frozenset({"fingerprint", "invariant", "page", "severity", "detail"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_NON_GENERIC_ACCEPTANCE_GUIDANCE = {
    "P2": "use source-inventory.json",
    "F3": "use source-inventory.json",
    "RF1": "use source-footnote-dispositions.json",
    "L2": "no generic exception is permitted for source/link projection authority",
    "V1": "no generic exception is permitted for final-rendered-DOM visibility authority",
}


class AcceptanceConfigError(ValueError):
    """The acceptance document is malformed, contradictory, or stale."""


@dataclass(frozen=True)
class AcceptanceConfig:
    by_fingerprint: Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True)
class AcceptanceResult:
    flags: list[dict]
    matched: tuple[str, ...]
    stale: tuple[str, ...]


def canonical_flag(flag: Mapping[str, Any]) -> dict[str, Any]:
    """Return and validate the exact flag payload covered by a fingerprint."""
    if not isinstance(flag, Mapping):
        raise AcceptanceConfigError("flag must be an object")

    invariant = flag.get("invariant")
    page = flag.get("page")
    severity = flag.get("severity")
    detail = flag.get("detail")
    if not isinstance(invariant, str) or not invariant:
        raise AcceptanceConfigError("flag invariant must be a non-empty string")
    if isinstance(page, bool) or not isinstance(page, int) or page < 0:
        raise AcceptanceConfigError("flag page must be a non-negative integer")
    if severity not in ("major", "minor"):
        raise AcceptanceConfigError("flag severity must be 'major' or 'minor'")
    if not isinstance(detail, dict):
        raise AcceptanceConfigError("flag detail must be an object")

    payload = {
        "invariant": invariant,
        "page": page,
        "severity": severity,
        "detail": detail,
    }
    try:
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AcceptanceConfigError(f"flag is not canonical-JSON serializable: {exc}") from exc
    return payload


def flag_fingerprint(flag: Mapping[str, Any]) -> str:
    """Stable SHA-256 of invariant+page+severity+detail canonical JSON."""
    encoded = json.dumps(
        canonical_flag(flag),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _reject_non_generic_acceptance(
    payload: Mapping[str, Any], where: str
) -> None:
    invariant = payload.get("invariant")
    guidance = _NON_GENERIC_ACCEPTANCE_GUIDANCE.get(invariant)
    if guidance is not None:
        raise AcceptanceConfigError(
            f"{where} cannot accept {invariant} findings; {guidance}"
        )


def acceptance_entry(flag: Mapping[str, Any]) -> dict[str, Any]:
    """Build the strict accepted.json entry for an observed major flag."""
    payload = canonical_flag(flag)
    if payload["severity"] != "major":
        raise AcceptanceConfigError("only major flags may be accepted")
    _reject_non_generic_acceptance(payload, "accepted.json")
    return {**payload, "fingerprint": flag_fingerprint(payload)}


def parse_acceptances(document: Any) -> AcceptanceConfig:
    """Validate an accepted.json-compatible object transactionally."""
    if not isinstance(document, dict):
        raise AcceptanceConfigError("acceptance document must be an object")
    raw = document.get("accepted")
    if not isinstance(raw, list):
        raise AcceptanceConfigError("acceptance document must contain an 'accepted' list")

    by_fingerprint: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(raw):
        where = f"accepted[{index}]"
        if not isinstance(entry, dict):
            raise AcceptanceConfigError(f"{where} must be an object")
        missing = _ENTRY_KEYS - entry.keys()
        extra = entry.keys() - _ENTRY_KEYS
        if missing:
            raise AcceptanceConfigError(f"{where} missing field(s): {', '.join(sorted(missing))}")
        if extra:
            raise AcceptanceConfigError(f"{where} has unknown field(s): {', '.join(sorted(extra))}")

        fingerprint = entry["fingerprint"]
        if not isinstance(fingerprint, str) or not _SHA256.fullmatch(fingerprint):
            raise AcceptanceConfigError(f"{where}.fingerprint must be 64 lowercase hex characters")
        payload = canonical_flag(entry)
        if payload["severity"] != "major":
            raise AcceptanceConfigError(f"{where} accepts a non-major flag")
        _reject_non_generic_acceptance(payload, where)
        expected = flag_fingerprint(payload)
        if fingerprint != expected:
            raise AcceptanceConfigError(
                f"{where}.fingerprint does not match its exact flag payload; expected {expected}"
            )
        if fingerprint in by_fingerprint:
            raise AcceptanceConfigError(f"duplicate acceptance fingerprint: {fingerprint}")
        by_fingerprint[fingerprint] = payload
    return AcceptanceConfig(by_fingerprint=by_fingerprint)


def apply_acceptances(flags: Sequence[dict], config: AcceptanceConfig) -> AcceptanceResult:
    """Suppress at most one exact major flag per configured fingerprint."""
    # AcceptanceConfig is normally created by parse_acceptances. Keep this
    # boundary fail-closed even if an in-process caller constructs it directly.
    for payload in config.by_fingerprint.values():
        _reject_non_generic_acceptance(payload, "acceptance config")

    unmatched = set(config.by_fingerprint)
    matched: list[str] = []
    remaining: list[dict] = []
    for flag in flags:
        fingerprint = flag_fingerprint(flag)
        if flag.get("severity") == "major" and fingerprint in unmatched:
            unmatched.remove(fingerprint)
            matched.append(fingerprint)
        else:
            remaining.append(flag)
    return AcceptanceResult(
        flags=remaining,
        matched=tuple(matched),
        stale=tuple(sorted(unmatched)),
    )


def reject_stale(result: AcceptanceResult) -> None:
    """Fail a full current-card gate when configured acceptances did not match."""
    if result.stale:
        raise AcceptanceConfigError(
            "stale acceptance fingerprint(s): " + ", ".join(result.stale)
        )


def gate_exit_code(flags: Sequence[Mapping[str, Any]], *, report_only: bool = False,
                   config_error: bool = False) -> int:
    """Return 2 for config errors, else 1 for majors unless report-only."""
    if config_error:
        return 2
    if not report_only and any(flag.get("severity") == "major" for flag in flags):
        return 1
    return 0
