"""Mutation tester (D6): inject synthetic defects into a copy of the HEAD
sections, run the verifier, and measure per-class recall — turning "calibrated
on history" into a number.

    uv run --with pymupdf python pipeline/verifier/mutate.py [--per-class 8] [--seed 5]

Detection rule: a mutation is detected iff the run produces a flag of the
class's intended invariant that was NOT in the unmutated baseline (matched on
the complete flag fingerprint). Severity and release behavior are measured
separately: ``intended_major`` asks whether that new intended finding is major,
``major_blocked`` asks whether an unsuppressed major remains after exact
acceptances, and ``gate_blocked`` records any nonzero production exit (including
an acceptance-configuration error). Keeping those signals separate prevents a
stale acceptance from masquerading as verifier recall.
"""

import argparse
import atexit
import hashlib
import json
import random
import re
import select
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import calibrate  # noqa: E402

SECTIONS = calibrate.CARD / "sections"
RE_LINK = re.compile(r"\[([^\]^][^\]]*)\]\((https?://[^)]+)\)")
RE_INTERNAL_LINK = re.compile(r"\[([^\]^][^\]]*)\]\(#([^)]+)\)")
RE_CHIP = re.compile(r":chip\[([^\]]+)\]")
RE_SENT = re.compile(r"(?<=[.!?] )([A-Z][^.!?\n]{40,180}[.!?]) ")
RE_PROSE_LINE = re.compile(
    r"^(?!\s*(?:[#>*|!:\-]|\[\^|<|\d+[.)]\s))"
    r"(?P<body>[A-Za-z\"“‘][^\n]{99,})$",
    re.M,
)
RE_SOURCE_IMG = re.compile(
    r"^!\[(?P<alt>[^\]]*)\]\("
    r"(?P<path>assets/figures/(?P<filename>p\d{3,}-[1-9]\d*\.png))"
    r"\)\s*$",
    re.M | re.I,
)
RE_FNDEF = re.compile(r"^\[\^\d+\]:.*$", re.M)
RE_MARKER = re.compile(r"<!-- p\.\d+ -->")
RE_BOLDLEAD = re.compile(r"\*\*([A-Z][^*]{6,60})\*\*")
RE_WORDPAIR = re.compile(r"(?<= )([a-z]{4,12}) ([a-z]{4,12})(?= )")
RE_CRITICAL_NUMBER = re.compile(
    r"(?<![\w])\d+(?:[.,:/-]\d+)*(?:[%‰])?(?![\w])")
RE_NEGATION = re.compile(
    r"\b(?:not|no|none|never|neither|nor|without|cannot|nothing|nobody|nowhere)\b",
    re.I,
)
RE_QUANTIFIED_UNIT = re.compile(
    r"\b(?P<number>\d[\d.,]*)(?P<gap>\s+)"
    r"(?:(?P<scale>thousand|million|billion|trillion)(?P<scale_gap>\s+))?"
    r"(?P<unit>tokens?|parameters?|requests?|queries|samples?|"
    r"milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b",
    re.I,
)
RE_CURRENCY_VALUE = re.compile(r"(?P<currency>[$€£¥₹₩₽])(?=\d)")
RE_CURRENCY_CODE_VALUE = re.compile(
    r"\b(?P<currency_code>USD|EUR|GBP|JPY|CNY|CAD|AUD|CHF|INR)(?=\s*\d)",
    re.I,
)
RE_COMPARATOR = re.compile(
    r"\b(?:at\s+(?:least|most)|up\s+to|no\s+(?:less|more)\s+than|"
    r"(?:less|greater|more|fewer)\s+than|under|over|below|above)\b|<=|>=|<|>",
    re.I,
)
RE_MONTH = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\b(?=(?:,\s*|\s+)\d{1,4}\b)",
    re.I,
)
RE_COMMENT_BLOCK = re.compile(r"<!--.*?-->", re.S)
RE_FNDEF_BLOCK = re.compile(
    r"^(?P<prefix>\[\^(?P<number>\d+)\]:[ \t]*)(?P<body>.*(?:\n(?: {4}|\t).*)*)",
    re.M,
)
RE_FNREF_SYNTAX = re.compile(r"\[\^(?P<number>\d+)\]")
RE_ORDERED_MARKER = re.compile(r"^(?: {0,3})(?P<number>\d+)(?=[.)][ \t]+)", re.M)
RE_LINK_DEST = re.compile(r"\]\(([^)\n]*)\)")
RE_HTML_TAG = re.compile(r"</?[A-Za-z][^>\n]*>")


def _visible_matches(pattern: re.Pattern, text: str) -> list[re.Match]:
    """Candidate matches that contribute visible canonical body text.

    Comments, footnote definitions, link/image destinations, and HTML tags are
    projection syntax. Mutating them would measure a different invariant while
    pretending to exercise T1 critical-token severity.
    """
    excluded: list[tuple[int, int]] = []
    for regex in (RE_COMMENT_BLOCK, RE_FNDEF_BLOCK, RE_HTML_TAG):
        excluded.extend(match.span() for match in regex.finditer(text))
    excluded.extend(match.span(1) for match in RE_LINK_DEST.finditer(text))
    excluded.extend(match.span("number") for match in RE_FNREF_SYNTAX.finditer(text))
    excluded.extend(match.span("number") for match in RE_ORDERED_MARKER.finditer(text))
    return [
        match for match in pattern.finditer(text)
        if not any(start <= match.start() < end for start, end in excluded)
    ]


def _footnote_body_matches(pattern: re.Pattern, text: str) -> list[tuple[int, int, str]]:
    """Return absolute visible-text matches inside canonical footnote bodies."""
    matches: list[tuple[int, int, str]] = []
    for definition in RE_FNDEF_BLOCK.finditer(text):
        body = definition.group("body")
        offset = definition.start("body")
        excluded: list[tuple[int, int]] = []
        for regex in (RE_COMMENT_BLOCK, RE_HTML_TAG):
            excluded.extend(match.span() for match in regex.finditer(body))
        excluded.extend(match.span(1) for match in RE_LINK_DEST.finditer(body))
        for match in pattern.finditer(body):
            if any(start <= match.start() < end for start, end in excluded):
                continue
            matches.append((offset + match.start(), offset + match.end(), match.group(0)))
    return matches


_AMBIGUOUS_COMPARATORS = {"under", "over", "below", "above", "<", ">", "<=", ">="}


def _quantified_comparator_context(
    text: str, match: re.Match, *, symbol: bool
) -> bool:
    before = text[max(0, match.start() - 16):match.start()]
    after = text[match.end():min(len(text), match.end() + 16)]
    currency = r"[$€£¥₹₩₽]?"
    if re.match(rf"\s*{currency}\d", after):
        return True
    return symbol and bool(re.search(r"\d\s*$", before))


def _comparator_matches(text: str) -> list[re.Match]:
    """Return comparator claims, excluding Markdown and vague prose uses.

    ``over time`` and a line-leading blockquote ``>`` are not threshold claims.
    Ambiguous one-word/symbol forms therefore need a nearby numeral; explicit
    phrases such as ``at least`` remain eligible on their own.
    """
    out = []
    for match in _visible_matches(RE_COMPARATOR, text):
        value = " ".join(match.group(0).casefold().split())
        if value == ">":
            line_start = text.rfind("\n", 0, match.start()) + 1
            if not text[line_start:match.start()].strip():
                continue
        if value in _AMBIGUOUS_COMPARATORS:
            if not _quantified_comparator_context(
                text, match, symbol=value in {"<", ">", "<=", ">="}
            ):
                continue
        out.append(match)
    return out


def class_rng(seed: int, kind: str) -> random.Random:
    """A deterministic stream whose samples do not depend on class order.

    A single shared RNG made adding one mutation class silently resample every
    class after it, turning unrelated baseline movement into apparent detector
    movement.  The explicit digest is stable across processes and Python hash
    randomization.
    """
    material = f"mutation-v1\0{seed}\0{kind}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(material).digest()[:16], "big"))


class SourceProjectionError(RuntimeError):
    """The rendered-DOM authority could not produce trustworthy evidence."""


class SourceProjectionWorker:
    """Persistent bridge to the production JS transform/render/audit lane."""

    def __init__(self, card_id: str, *, node_executable: str = "node",
                 response_timeout: float = 60.0, worker_script: Path | None = None):
        script = (worker_script
                  or calibrate.REPO / "site/scripts/mutation-source-projection-worker.mjs")
        self._stderr = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
        self._request_id = 0
        self._closed = False
        self._response_timeout = response_timeout
        self.last_result = None
        try:
            self._process = subprocess.Popen(
                [node_executable, str(script), "--card", card_id],
                cwd=calibrate.REPO,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self._stderr,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            self._stderr.close()
            raise SourceProjectionError(
                f"cannot start rendered-DOM authority: {exc}"
            ) from exc

    def _stderr_text(self) -> str:
        self._stderr.flush()
        self._stderr.seek(0)
        return self._stderr.read().strip()

    def _force_stop(self) -> None:
        if self._process.poll() is not None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=5)

    def audit(self, sections: dict[str, str]) -> dict:
        """Render only the exact supplied section values, never WORKTREE."""
        if self._closed:
            raise SourceProjectionError("rendered-DOM authority is already closed")
        if not sections or any(
            not isinstance(name, str) or not isinstance(text, str)
            for name, text in sections.items()
        ):
            raise SourceProjectionError("sections must be a non-empty string mapping")
        self._request_id += 1
        request = {
            "id": self._request_id,
            "sections": [
                {"name": name, "text": sections[name]}
                for name in sorted(sections)
            ],
        }
        try:
            assert self._process.stdin is not None
            self._process.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
            self._process.stdin.flush()
            assert self._process.stdout is not None
            ready, _, _ = select.select(
                [self._process.stdout], [], [], self._response_timeout)
            if not ready:
                self._force_stop()
                detail = self._stderr_text()
                suffix = f": {detail}" if detail else ""
                raise SourceProjectionError(
                    "rendered-DOM authority exceeded "
                    f"{self._response_timeout:g}s response timeout{suffix}"
                )
            line = self._process.stdout.readline()
        except (BrokenPipeError, OSError) as exc:
            self._process.wait(timeout=5)
            detail = self._stderr_text() or str(exc)
            raise SourceProjectionError(
                f"rendered-DOM authority terminated: {detail}"
            ) from exc
        if not line:
            self._process.wait(timeout=5)
            detail = self._stderr_text() or f"exit {self._process.returncode}"
            raise SourceProjectionError(
                f"rendered-DOM authority returned no result: {detail}"
            )
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SourceProjectionError(
                "rendered-DOM authority returned malformed JSON"
            ) from exc
        if response.get("id") != self._request_id:
            raise SourceProjectionError("rendered-DOM authority response id disagrees")
        if response.get("error"):
            raise SourceProjectionError(
                f"rendered-DOM authority rejected supplied sections: {response['error']}"
            )
        if not isinstance(response.get("findings"), list):
            raise SourceProjectionError("rendered-DOM authority omitted findings")
        if not isinstance(response.get("stats"), dict):
            raise SourceProjectionError("rendered-DOM authority omitted stats")
        self.last_result = response
        return response

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._process.stdin is not None:
            try:
                self._process.stdin.close()
            except BrokenPipeError:
                pass
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._force_stop()
        if self._process.stdout is not None:
            self._process.stdout.close()
        self._stderr.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.close()


_P2_FINDINGS = {
    "noncanonical-pagemark",
    "out-of-range-page-marker",
    "excluded-page-marker",
    "missing-page-marker",
    "duplicate-page-marker",
    "page-marker-order",
}
_F3_FINDINGS = {
    "noncanonical-figure-link",
    "noncanonical-figure-skip",
    "noncanonical-rendered-figure",
    "extra-rendered-figure",
    "figure-page-context-mismatch",
    "missing-rendered-figure",
    "duplicate-rendered-figure",
    "missing-figure-skip-sentinel",
    "duplicate-figure-skip-sentinel",
    "rendered-figure-order",
}
_WHOLE_ARTICLE_FINDINGS = {
    "article-root-count",
    "active-or-non-html-article-content",
    "render-rejected",
}
_V1_FINDINGS = {"browser-hidden-authored-content"}


def _event_invariants(finding: dict) -> set[str]:
    event_kinds = {
        event.get("kind")
        for event in (finding.get("expectedEvent"), finding.get("actualEvent"))
        if isinstance(event, dict)
    }
    invariants = set()
    if "page" in event_kinds:
        invariants.add("P2")
    if event_kinds & {"figure", "accepted-skip"}:
        invariants.add("F3")
    return invariants or {"P2", "F3"}


def _finding_page(finding: dict) -> int:
    for key in ("page", "expectedPage", "precedingPage", "claimedPage"):
        value = finding.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    for event_key in ("expectedEvent", "actualEvent"):
        event = finding.get(event_key)
        if isinstance(event, dict) and isinstance(event.get("page"), int):
            return event["page"]
        filename = event.get("filename") if isinstance(event, dict) else None
        match = re.match(r"p(\d+)-", filename or "", re.I)
        if match:
            return int(match.group(1))
    match = re.match(r"p(\d+)-", finding.get("filename") or "", re.I)
    return int(match.group(1)) if match else 0


def source_projection_flags(findings: list[dict]) -> list[dict]:
    """Normalize final-DOM findings into stable blocking P2/F3 records."""
    flags = []
    for finding in findings:
        if not isinstance(finding, dict) or not isinstance(finding.get("kind"), str):
            raise SourceProjectionError("rendered-DOM finding has an invalid shape")
        kind = finding["kind"]
        if kind in _P2_FINDINGS:
            invariants = {"P2"}
        elif kind in _F3_FINDINGS:
            invariants = {"F3"}
        elif kind in _WHOLE_ARTICLE_FINDINGS:
            invariants = {"P2", "F3"}
        elif kind in _V1_FINDINGS:
            invariants = {"V1"}
        elif kind == "source-projection-event-stream":
            invariants = _event_invariants(finding)
        else:
            # New audit vocabulary must be deliberately classified. Ignoring it
            # would make mutation recall silently narrower than production.
            raise SourceProjectionError(
                f"unclassified rendered-DOM finding kind: {kind}"
            )
        exact_finding = {key: value for key, value in finding.items() if key != "offset"}
        digest = hashlib.sha256(json.dumps(
            exact_finding, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()
        for invariant in sorted(invariants):
            flags.append({
                "invariant": invariant,
                "page": _finding_page(finding),
                "severity": "major",
                "detail": {
                    "kind": kind,
                    "finding_sha256": digest,
                    "authority": "final-rendered-dom",
                },
            })
    return flags


def collect_composite_flags(ref: str, section_texts: dict[str, str],
                            worker: SourceProjectionWorker, *,
                            prevalidated_source_inventory_flags=None) -> list[dict]:
    """Combine legacy/source checks with independently rendered DOM facts."""
    legacy = calibrate.collect_flags(
        ref,
        prevalidated_source_inventory_flags=(
            prevalidated_source_inventory_flags
        ),
    )
    rendered = worker.audit(section_texts)
    return legacy + source_projection_flags(rendered["findings"])


def mutations(kind: str, text: str, rng: random.Random):
    """Return (mutated_text, note) or None if no eligible site in this file."""
    def pick(matches):
        return rng.choice(matches) if matches else None

    if kind == "split-item":
        # break a long list item at a word boundary mid-way: continuation
        # becomes a separate paragraph (the wrapped-bullet defect class)
        cands = [m for m in re.finditer(r"^- .{120,300}$", text, re.M)]
        m = pick(cands)
        if not m:
            return None
        s = m.group(0)
        cut = s.rfind(" ", 80, 160)
        return (text[: m.start()] + s[:cut] + "\n\n" + s[cut + 1:] + text[m.end():], s[:40]) if cut > 0 else None
    if kind == "item-to-paragraph":
        m = pick(list(re.finditer(r"^- (.{40,})$", text, re.M)))
        return (text[: m.start()] + m.group(1) + text[m.end():], m.group(1)[:40]) if m else None
    if kind == "split-heading":
        m = pick([h for h in re.finditer(r"^(#{2,5}) (.{30,90})$", text, re.M)])
        if not m:
            return None
        s = m.group(2)
        cut = s.rfind(" ", 15, 45)
        if cut <= 0:
            return None
        return (text[: m.start()] + f"{m.group(1)} {s[:cut]}\n\n{s[cut+1:]}" + text[m.end():], s[:40])
    if kind == "drop-link":
        m = pick(list(RE_LINK.finditer(text)))
        return (text[: m.start()] + m.group(1) + text[m.end():], m.group(2)) if m else None
    if kind == "repoint-link":
        # Keep the link present and point it at a DIFFERENT, already-existing
        # target from the same section. An existence-only link audit passes
        # this mutation; L2 must bind the occurrence to its PDF destination.
        links = list(RE_INTERNAL_LINK.finditer(text))
        candidates = [m for m in links if any(n.group(2) != m.group(2) for n in links)]
        m = pick(candidates)
        if not m:
            return None
        alternatives = sorted({n.group(2) for n in links if n.group(2) != m.group(2)})
        wrong = rng.choice(alternatives)
        replacement = f"[{m.group(1)}](#{wrong})"
        note = f"{m.group(2)} -> {wrong}"
        return text[: m.start()] + replacement + text[m.end():], note
    if kind == "flatten-chip":
        m = pick(list(RE_CHIP.finditer(text)))
        return (text[: m.start()] + f"**{m.group(1)}**" + text[m.end():], m.group(1)) if m else None
    if kind == "delete-sentence":
        m = pick(list(RE_SENT.finditer(text)))
        return (text[: m.start(1)] + text[m.end():], m.group(1)[:40]) if m else None
    if kind == "hide-prose":
        m = pick(list(RE_PROSE_LINE.finditer(text)))
        if not m:
            return None
        body = m.group("body")
        replacement = f"<span hidden>{body}</span>"
        return text[:m.start()] + replacement + text[m.end():], body[:40]
    if kind == "duplicate-paragraph":
        paras = [p for p in text.split("\n\n") if len(p) > 200 and not p.startswith(("<", "!", ":", "#", "|"))]
        p = pick(paras)
        return (text.replace(p, p + "\n\n" + p, 1), p[:40]) if p else None
    if kind == "swap-words":
        m = pick(list(RE_WORDPAIR.finditer(text)))
        return (text[: m.start()] + f"{m.group(2)} {m.group(1)}" + text[m.end():], m.group(0)) if m else None
    if kind == "change-number":
        m = pick(_visible_matches(RE_CRITICAL_NUMBER, text))
        if not m:
            return None
        value = m.group(0)
        digit = next(
            (index for index in range(len(value) - 1, -1, -1)
             if value[index].isdigit()),
            None,
        )
        if digit is None:
            return None
        replacement_digit = str((int(value[digit]) + 1) % 10)
        replacement = value[:digit] + replacement_digit + value[digit + 1:]
        return (
            text[:m.start()] + replacement + text[m.end():],
            f"{value} -> {replacement}",
        )
    if kind == "drop-negation":
        m = pick(_visible_matches(RE_NEGATION, text))
        if not m:
            return None
        # Remove one neighboring space so the mutation stays grammatical enough
        # to isolate the semantic token rather than manufacture layout noise.
        start, end = m.span()
        if end < len(text) and text[end:end + 1] == " ":
            end += 1
        elif start and text[start - 1:start] == " ":
            start -= 1
        return text[:start] + text[end:], m.group(0)
    if kind == "change-unit":
        unit_matches = _visible_matches(RE_QUANTIFIED_UNIT, text)
        currency_matches = _visible_matches(RE_CURRENCY_VALUE, text)
        currency_code_matches = _visible_matches(RE_CURRENCY_CODE_VALUE, text)
        candidates = [("unit", match) for match in unit_matches]
        candidates += [("currency", match) for match in currency_matches]
        candidates += [("currency-code", match) for match in currency_code_matches]
        chosen = pick(candidates)
        if not chosen:
            return None
        shape, m = chosen
        if shape == "currency":
            value = m.group("currency")
            replacement = "€" if value != "€" else "$"
            start, end = m.span("currency")
        elif shape == "currency-code":
            value = m.group("currency_code")
            replacement = "EUR" if value.casefold() != "eur" else "USD"
            start, end = m.span("currency_code")
        else:
            value = m.group("unit")
            singular = not value.casefold().endswith("s")
            family = value.casefold().rstrip("s")
            replacements = {
                "token": "parameter", "parameter": "token",
                "request": "query", "query": "request", "querie": "request",
                "sample": "token", "millisecond": "second", "second": "minute",
                "minute": "hour", "hour": "day", "day": "hour",
                "week": "month", "month": "year", "year": "month",
            }
            replacement = replacements.get(family, "tokens")
            if not singular:
                replacement += "s"
            start, end = m.span("unit")
        return (
            text[:start] + replacement + text[end:],
            f"{value} -> {replacement}",
        )
    if kind == "change-comparator":
        m = pick(_comparator_matches(text))
        if not m:
            return None
        value = " ".join(m.group(0).casefold().split())
        replacements = {
            "at least": "at most", "at most": "at least",
            "up to": "over", "no less than": "less than",
            "no more than": "more than", "less than": "greater than",
            "greater than": "less than", "more than": "less than",
            "fewer than": "more than", "under": "over", "over": "under",
            "below": "above", "above": "below", "<=": ">", ">=": "<",
            "<": ">=", ">": "<=",
        }
        replacement = replacements[value]
        return text[:m.start()] + replacement + text[m.end():], f"{value} -> {replacement}"
    if kind == "change-date":
        m = pick(_visible_matches(RE_MONTH, text))
        if not m:
            return None
        months = [
            "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December",
        ]
        index = [month.casefold() for month in months].index(m.group(0).casefold())
        replacement = months[(index + 1) % len(months)]
        return (
            text[:m.start()] + replacement + text[m.end():],
            f"{m.group(0)} -> {replacement}",
        )
    if kind == "change-fn-value":
        chosen = pick(_footnote_body_matches(RE_CRITICAL_NUMBER, text))
        if not chosen:
            return None
        start, end, value = chosen
        digit = next(
            (index for index in range(len(value) - 1, -1, -1)
             if value[index].isdigit()),
            None,
        )
        if digit is None:
            return None
        replacement_digit = str((int(value[digit]) + 1) % 10)
        replacement = value[:digit] + replacement_digit + value[digit + 1:]
        return (
            text[:start] + replacement + text[end:],
            f"footnote {value} -> {replacement}",
        )
    if kind == "drop-fn-negation":
        chosen = pick(_footnote_body_matches(RE_NEGATION, text))
        if not chosen:
            return None
        start, end, value = chosen
        if end < len(text) and text[end:end + 1] == " ":
            end += 1
        elif start and text[start - 1:start] == " ":
            start -= 1
        return text[:start] + text[end:], f"footnote {value}"
    if kind == "drop-image":
        m = pick(list(RE_SOURCE_IMG.finditer(text)))
        return (text[: m.start()] + text[m.end():], m.group(0)[:40]) if m else None
    if kind == "wrong-image-path":
        m = pick(list(RE_SOURCE_IMG.finditer(text)))
        if not m:
            return None
        wrong = m.group("path").replace("assets/figures/", "assets/wrong-figures/", 1)
        replacement = f"![{m.group('alt')}]({wrong})"
        return (
            text[:m.start()] + replacement + text[m.end():],
            f"{m.group('path')} -> {wrong}",
        )
    if kind == "hide-image":
        m = pick(list(RE_SOURCE_IMG.finditer(text)))
        if not m:
            return None
        # Raw HTML is passed through the production renderer. The image still
        # names the exact canonical published asset, but a hidden ancestor means
        # it cannot satisfy visible final-DOM projection authority.
        src = (
            f"/ai-system-cards/cards/{calibrate.cardcfg.CARD_ID}/figures/"
            f"{m.group('filename')}"
        )
        replacement = f'<span hidden><img src="{src}" alt=""></span>'
        return (
            text[:m.start()] + replacement + text[m.end():],
            f"hide {m.group('filename')}",
        )
    if kind == "reorder-images":
        matches = list(RE_SOURCE_IMG.finditer(text))
        if len(matches) < 2:
            return None
        left, right = sorted(rng.sample(matches, 2), key=lambda match: match.start())
        return (
            text[:left.start()] + right.group(0)
            + text[left.end():right.start()] + left.group(0)
            + text[right.end():],
            f"{left.group('filename')} <-> {right.group('filename')}",
        )
    if kind == "drop-fndef":
        m = pick(list(RE_FNDEF.finditer(text)))
        return (text[: m.start()] + text[m.end():], m.group(0)[:30]) if m else None
    if kind == "dup-marker":
        m = pick(list(RE_MARKER.finditer(text)))
        return (text + f"\n\n{m.group(0)}\n", m.group(0)) if m else None
    if kind == "drop-marker":
        m = pick(list(RE_MARKER.finditer(text)))
        return (text[:m.start()] + text[m.end():], m.group(0)) if m else None
    if kind == "drop-bold":
        # realistic sites only: body bolds. S1 deliberately excludes footnote
        # defs, table interiors (TB1's layer), and turn labels — picking those
        # measures the exclusions, not the gate.
        cands = []
        for m in RE_BOLDLEAD.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            line = text[ls:ls + 12]
            in_table = text.rfind("<table", 0, m.start()) > text.rfind("</table>", 0, m.start())
            if not line.startswith(("[^", ":::", "|")) and not in_table:
                cands.append(m)
        m = pick(cands)
        return (text[: m.start()] + m.group(1) + text[m.end():], m.group(1)[:40]) if m else None
    return None


CLASSES = {
    "split-item": "ST2",
    "item-to-paragraph": "ST1",
    "split-heading": "ST3",
    "drop-link": "L1",
    "repoint-link": "L2",
    "flatten-chip": "S2",
    "delete-sentence": "T1",
    "hide-prose": "V1",
    "duplicate-paragraph": "T1",
    "swap-words": "T1",
    "change-number": "T1",
    "drop-negation": "T1",
    "change-unit": "T1",
    "change-comparator": "T1",
    "change-date": "T1",
    "change-fn-value": "FN1",
    "drop-fn-negation": "FN1",
    "drop-image": "F3",
    "wrong-image-path": "F3",
    "hide-image": "F3",
    "reorder-images": "F3",
    "drop-fndef": "FN1",
    "dup-marker": "P2",
    "drop-marker": "P2",
    "drop-bold": "S1",
}


def flag_keys(flags):
    """Full finding multiset, including page, severity, and exact digests."""
    return Counter(
        calibrate.acceptance.flag_fingerprint(flag) for flag in flags
    )


class MutationBaselineError(RuntimeError):
    """The unmutated card is not a clean base for release-blocking recall."""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self.exit_code = exit_code


MUTATION_SCHEMA_VERSION = 2
_RESULT_KEYS = {
    "caught",
    "detected",
    "details",
    "gate_blocked",
    "intended_major",
    "invariant",
    "major_blocked",
    "tried",
}
_DETAIL_KEYS = {
    "caught",
    "detected",
    "file",
    "gate_blocked",
    "gate_exit",
    "gate_reason",
    "intended_major",
    "intended_new_flags",
    "major_blocked",
    "site",
}


def _natural_int(value, label: str) -> int:
    if type(value) is not int or value < 0:
        raise MutationBaselineError(f"{label} must be a non-negative integer", 2)
    return value


def _positive_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if count < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return count


def validate_mutation_envelope(document, *, card_id: str, seed: int,
                               per_class: int) -> dict:
    """Validate the strict, run-bound mutation artifact schema."""
    if type(per_class) is not int or per_class < 1:
        raise MutationBaselineError("requested per_class must be a positive integer", 2)
    if not isinstance(document, dict) or set(document) != {
        "card_id", "per_class", "results", "schema_version", "seed"
    }:
        raise MutationBaselineError(
            "mutation baseline must be a schema-v2 envelope with exactly "
            "card_id, per_class, results, schema_version, and seed",
            2,
        )
    if document["schema_version"] != MUTATION_SCHEMA_VERSION:
        raise MutationBaselineError(
            f"mutation baseline schema_version must be {MUTATION_SCHEMA_VERSION}", 2)
    if document["card_id"] != card_id:
        raise MutationBaselineError(
            f"mutation baseline card_id {document['card_id']!r} != {card_id!r}", 2)
    if type(document["seed"]) is not int or document["seed"] != seed:
        raise MutationBaselineError(
            f"mutation baseline seed {document['seed']!r} != {seed}", 2)
    if type(document["per_class"]) is not int or document["per_class"] != per_class:
        raise MutationBaselineError(
            "mutation baseline per_class "
            f"{document['per_class']!r} != {per_class}",
            2,
        )
    results = document["results"]
    if not isinstance(results, dict) or not results:
        raise MutationBaselineError("mutation baseline results must be non-empty", 2)
    for kind, result in results.items():
        label = f"mutation baseline results.{kind}"
        if kind not in CLASSES:
            raise MutationBaselineError(f"{label} is not a known mutation class", 2)
        if not isinstance(result, dict) or set(result) != _RESULT_KEYS:
            raise MutationBaselineError(
                f"{label} keys must be exactly {', '.join(sorted(_RESULT_KEYS))}", 2)
        if result["invariant"] != CLASSES[kind]:
            raise MutationBaselineError(
                f"{label}.invariant {result['invariant']!r} != {CLASSES[kind]!r}", 2)
        tried = _natural_int(result["tried"], f"{label}.tried")
        if tried != per_class:
            raise MutationBaselineError(
                f"{label}.tried {tried} != envelope per_class {per_class}", 2)
        counts = {}
        for key in (
            "caught", "detected", "intended_major", "major_blocked", "gate_blocked"
        ):
            counts[key] = _natural_int(result[key], f"{label}.{key}")
            if counts[key] > tried:
                raise MutationBaselineError(f"{label}.{key} exceeds tried", 2)
        if counts["caught"] != counts["detected"]:
            raise MutationBaselineError(f"{label}.caught must equal detected", 2)
        if counts["intended_major"] > counts["detected"]:
            raise MutationBaselineError(
                f"{label}.intended_major cannot exceed detected", 2)
        details = result["details"]
        if not isinstance(details, list) or len(details) != tried:
            raise MutationBaselineError(
                f"{label}.details length must equal tried", 2)
        aggregate = Counter()
        for index, detail in enumerate(details):
            detail_label = f"{label}.details[{index}]"
            if not isinstance(detail, dict) or set(detail) != _DETAIL_KEYS:
                raise MutationBaselineError(
                    f"{detail_label} keys must be exactly "
                    f"{', '.join(sorted(_DETAIL_KEYS))}",
                    2,
                )
            for key in ("file", "site", "gate_reason"):
                if not isinstance(detail[key], str):
                    raise MutationBaselineError(f"{detail_label}.{key} must be a string", 2)
            for key in (
                "caught", "detected", "intended_major", "major_blocked", "gate_blocked"
            ):
                if type(detail[key]) is not bool:
                    raise MutationBaselineError(f"{detail_label}.{key} must be boolean", 2)
                aggregate[key] += int(detail[key])
            intended_new_flags = _natural_int(
                detail["intended_new_flags"],
                f"{detail_label}.intended_new_flags",
            )
            _natural_int(detail["gate_exit"], f"{detail_label}.gate_exit")
            if detail["caught"] != detail["detected"]:
                raise MutationBaselineError(
                    f"{detail_label}.caught must equal detected", 2)
            if detail["intended_major"] and not detail["detected"]:
                raise MutationBaselineError(
                    f"{detail_label}.intended_major requires detected", 2)
            if detail["detected"] != (intended_new_flags > 0):
                raise MutationBaselineError(
                    f"{detail_label}.detected disagrees with intended_new_flags", 2)
            if detail["major_blocked"] and not detail["gate_blocked"]:
                raise MutationBaselineError(
                    f"{detail_label}.major_blocked requires gate_blocked", 2)
            if detail["gate_blocked"] != (detail["gate_exit"] != 0):
                raise MutationBaselineError(
                    f"{detail_label}.gate_blocked disagrees with gate_exit", 2)
            if detail["gate_reason"] not in {"none", "major", "acceptance-config"}:
                raise MutationBaselineError(
                    f"{detail_label}.gate_reason is unknown", 2)
            expected_gate_exit = {
                "none": 0,
                "major": 1,
                "acceptance-config": 2,
            }[detail["gate_reason"]]
            if detail["gate_exit"] != expected_gate_exit:
                raise MutationBaselineError(
                    f"{detail_label}.gate_reason disagrees with gate_exit", 2)
            if detail["gate_reason"] == "major" and not detail["major_blocked"]:
                raise MutationBaselineError(
                    f"{detail_label}.major gate lacks major_blocked evidence", 2)
        for key, count in counts.items():
            if aggregate[key] != count:
                raise MutationBaselineError(
                    f"{label}.{key} disagrees with detail evidence", 2)
    return results


def mutation_envelope(results: dict, *, card_id: str, seed: int,
                      per_class: int) -> dict:
    document = {
        "schema_version": MUTATION_SCHEMA_VERSION,
        "card_id": card_id,
        "seed": seed,
        "per_class": per_class,
        "results": results,
    }
    validate_mutation_envelope(
        document, card_id=card_id, seed=seed, per_class=per_class)
    return document


def load_mutation_baseline(path: Path, output_path: Path, *, card_id: str,
                           seed: int, per_class: int) -> dict:
    """Load and validate baseline authority before any mutation or output write."""
    try:
        same_file = path.resolve() == output_path.resolve()
        if path.exists() and output_path.exists():
            same_file = same_file or path.samefile(output_path)
    except OSError as exc:
        raise MutationBaselineError(
            f"cannot resolve mutation baseline/output identity: {exc}", 2
        ) from exc
    if same_file:
        raise MutationBaselineError(
            "--json output must not resolve to the --baseline file", 2)
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MutationBaselineError(f"cannot read mutation baseline {path}: {exc}", 2) from exc
    return validate_mutation_envelope(
        document, card_id=card_id, seed=seed, per_class=per_class)


def write_mutation_results(path: Path, results: dict, *, card_id: str,
                           seed: int, per_class: int) -> None:
    document = mutation_envelope(
        results, card_id=card_id, seed=seed, per_class=per_class)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=1) + "\n")


def release_gate_outcome(flags: list[dict], accepted_path: Path) -> dict:
    """Apply production acceptance semantics and summarize the gate outcome.

    Mutation runs use a temporary absolute directory, but they still represent
    a full-card release gate. Therefore every committed acceptance must match,
    just as it must for WORKTREE; otherwise stale accepted majors would be
    silently ignored by calibrate's ordinary historical/partial-ref behavior.
    """
    remaining, accepted, config_error = calibrate._apply_accepted(
        flags, accepted_path, require_all=True)
    unsuppressed_majors = sum(
        flag.get("severity") == "major" for flag in remaining)
    exit_code = calibrate.acceptance.gate_exit_code(
        remaining, config_error=config_error is not None)
    reason = ("acceptance-config" if config_error
              else "major" if unsuppressed_majors
              else "none")
    return {
        "exit_code": exit_code,
        "gate_blocked": exit_code != 0,
        # This is the recall-bearing release signal. An acceptance-config
        # error also stops CI, but it is not evidence that the intended defect
        # reached a blocking verifier invariant.
        "major_blocked": unsuppressed_majors > 0,
        "gate_reason": reason,
        "accepted_majors": accepted,
        "unsuppressed_majors": unsuppressed_majors,
        "acceptance_error": config_error,
    }


def require_clean_release_baseline(flags: list[dict], accepted_path: Path) -> dict:
    """Reject a baseline whose normal release gate already fails.

    Without this precondition, every mutation would receive a false-positive
    release-blocking hit from a pre-existing major or malformed/stale
    acceptance configuration.
    """
    outcome = release_gate_outcome(flags, accepted_path)
    if outcome["exit_code"]:
        if outcome["acceptance_error"]:
            detail = outcome["acceptance_error"]
        else:
            detail = f"{outcome['unsuppressed_majors']} unsuppressed major(s)"
        raise MutationBaselineError(
            f"unmutated release gate exits {outcome['exit_code']}: {detail}",
            outcome["exit_code"],
        )
    return outcome


def mutation_evidence(flags: list[dict], intended_invariant: str,
                      baseline,
                      accepted_path: Path) -> dict:
    """Return independent detection, severity, and production-gate evidence."""
    remaining_baseline = Counter(baseline)
    intended_new = []
    for flag in flags:
        fingerprint = calibrate.acceptance.flag_fingerprint(flag)
        if remaining_baseline[fingerprint]:
            remaining_baseline[fingerprint] -= 1
        elif flag["invariant"] == intended_invariant:
            intended_new.append(flag)
    gate = release_gate_outcome(flags, accepted_path)
    return {
        "detected": bool(intended_new),
        "intended_new_flags": len(intended_new),
        "intended_major": any(
            flag.get("severity") == "major" for flag in intended_new),
        "major_blocked": gate["major_blocked"],
        "gate_blocked": gate["gate_blocked"],
        "gate_exit": gate["exit_code"],
        "gate_reason": gate["gate_reason"],
    }


def detection_count(result: dict) -> int:
    """Read the schema-v2 detection count."""
    return result["detected"]


def baseline_regressions(results: dict, expected: dict) -> list[str]:
    """Return human-readable reasons that mutation recall fell below baseline.

    The seeded sample count is part of the contract: silently comparing different
    sample sizes makes the raw caught count meaningless.  Improvements are allowed;
    removed or newly unbaselined classes require an intentional baseline update.
    Per-mutation site details are evidence, not the gate — source edits can move a
    seeded sample while preserving the measured class recall.
    """
    problems = []
    actual_classes = set(results)
    expected_classes = set(expected)
    for kind in sorted(expected_classes - actual_classes):
        problems.append(f"{kind}: baseline class is missing from this run")
    for kind in sorted(actual_classes - expected_classes):
        problems.append(f"{kind}: current class has no committed baseline")
    for kind in sorted(actual_classes & expected_classes):
        got, want = results[kind], expected[kind]
        for label, result in (("current", got), ("baseline", want)):
            if ("detected" in result and "caught" in result
                    and result["detected"] != result["caught"]):
                problems.append(
                    f"{kind}: {label} caught alias disagrees with detected"
                )
        if got.get("invariant") != want.get("invariant"):
            problems.append(
                f"{kind}: invariant changed {want.get('invariant')} -> {got.get('invariant')}"
            )
        same_sample_count = got.get("tried") == want.get("tried")
        if not same_sample_count:
            problems.append(
                f"{kind}: sample count changed {want.get('tried')} -> {got.get('tried')}"
            )
        elif detection_count(got) < detection_count(want):
            problems.append(
                f"{kind}: detection recall regressed "
                f"{detection_count(want)}/{want.get('tried')}"
                f" -> {detection_count(got)}/{got.get('tried')}"
            )
        if same_sample_count:
            for field, label in (
                ("intended_major", "intended-major"),
                ("major_blocked", "major-blocking"),
            ):
                if got[field] < want[field]:
                    problems.append(
                        f"{kind}: {label} recall regressed "
                        f"{want[field]}/{want.get('tried')}"
                        f" -> {got[field]}/{got.get('tried')}"
                    )
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=_positive_count, default=8)
    ap.add_argument("--seed", type=int, default=5)
    # A casual calibration writes only to the OS temp directory. Promotion to
    # tracked evidence is an explicit reviewed copy; the runner never defaults
    # to mutating a committed baseline.
    ap.add_argument("--json", type=Path,
                    default=(Path(tempfile.gettempdir())
                             / ("mutation-"
                                f"{calibrate.cardcfg.CARD_ID.replace('/', '-')}.json")))
    ap.add_argument("--classes", nargs="*", help="limit to these mutation kinds")
    ap.add_argument(
        "--baseline",
        type=Path,
        help="committed results JSON; fail if class coverage/sample count changes or recall drops",
    )
    args = ap.parse_args()
    expected = None
    if args.baseline:
        try:
            expected = load_mutation_baseline(
                args.baseline,
                args.json,
                card_id=calibrate.cardcfg.CARD_ID,
                seed=args.seed,
                per_class=args.per_class,
            )
        except MutationBaselineError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            raise SystemExit(exc.exit_code) from exc
    files = {p.name: p.read_text() for p in sorted(SECTIONS.glob("*.md"))}
    accepted_path = calibrate.CARD / "accepted.json"
    # Section-only mutations cannot change raw PDF/map/asset observations.
    # Validate that independent source authority once; production collect_flags
    # keeps its observe-on-every-call default.
    static_source_flags = tuple(calibrate._source_inventory_report().flags)
    projection_worker = SourceProjectionWorker(calibrate.cardcfg.CARD_ID)
    atexit.register(projection_worker.close)
    baseline_flags = collect_composite_flags(
        "WORKTREE", files, projection_worker,
        prevalidated_source_inventory_flags=static_source_flags)
    baseline = flag_keys(baseline_flags)
    try:
        baseline_gate = require_clean_release_baseline(
            baseline_flags, accepted_path)
    except MutationBaselineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc
    print(
        f"baseline flags: {len(baseline)} raw; "
        f"{len(projection_worker.last_result['findings'])} final-DOM finding(s); "
        f"{baseline_gate['accepted_majors']} accepted major(s); "
        f"{baseline_gate['unsuppressed_majors']} unsuppressed major(s)"
    )

    results = {}
    for kind, inv in CLASSES.items():
        if args.classes and kind not in args.classes:
            continue
        rng = class_rng(args.seed, kind)
        detected = intended_major = major_blocked = gate_blocked = tried = 0
        details = []
        eligible = [n for n, t in files.items() if mutations(kind, t, random.Random(0)) is not None]
        if not eligible:
            # class not present in this card (e.g. no chips) — n/a, not a miss
            print(f"{kind:>20} n/a (no eligible section)")
            continue
        for i in range(args.per_class):
            name = rng.choice(eligible)
            mut = mutations(kind, files[name], rng)
            if not mut:
                continue
            tried += 1
            mutated_files = dict(files)
            mutated_files[name] = mut[0]
            with tempfile.TemporaryDirectory(prefix=f"mut-{kind}-") as tmp_name:
                tmp = Path(tmp_name)
                for n, t in mutated_files.items():
                    (tmp / n).write_text(t)
                flags = collect_composite_flags(
                    str(tmp), mutated_files, projection_worker,
                    prevalidated_source_inventory_flags=static_source_flags)
            evidence = mutation_evidence(
                flags, inv, baseline, accepted_path)
            detected += evidence["detected"]
            intended_major += evidence["intended_major"]
            major_blocked += evidence["major_blocked"]
            gate_blocked += evidence["gate_blocked"]
            details.append({
                "file": name,
                "site": mut[1],
                # Legacy alias retained for existing artifact consumers.
                "caught": evidence["detected"],
                "detected": evidence["detected"],
                "intended_new_flags": evidence["intended_new_flags"],
                "intended_major": evidence["intended_major"],
                "major_blocked": evidence["major_blocked"],
                "gate_blocked": evidence["gate_blocked"],
                "gate_exit": evidence["gate_exit"],
                "gate_reason": evidence["gate_reason"],
            })
            detection_status = "HIT " if evidence["detected"] else "MISS"
            severity_status = "MAJOR" if evidence["intended_major"] else "ADVIS"
            gate_status = (
                "BLOCK" if evidence["major_blocked"]
                else "CONFIG" if evidence["gate_blocked"]
                else "PASS"
            )
            print(
                f"{kind:>20} [{i+1}/{args.per_class}] "
                f"{detection_status} {severity_status} {gate_status} "
                f"{name}: {mut[1][:40]}"
            )
        results[kind] = {
            "invariant": inv,
            # Legacy alias: caught has always meant intended detection.
            "caught": detected,
            "detected": detected,
            "intended_major": intended_major,
            "major_blocked": major_blocked,
            # Diagnostic only: includes acceptance-config exits and is not a
            # recall floor, because config churn is not detector evidence.
            "gate_blocked": gate_blocked,
            "tried": tried,
            "details": details,
        }

    projection_worker.close()
    atexit.unregister(projection_worker.close)

    print("\n=== per-class mutation evidence ===")
    for kind, r in results.items():
        detection_pct = 100 * r["detected"] / r["tried"] if r["tried"] else 0
        intended_major_pct = (
            100 * r["intended_major"] / r["tried"] if r["tried"] else 0)
        blocking_pct = (
            100 * r["major_blocked"] / r["tried"] if r["tried"] else 0)
        print(
            f"{kind:>20} ({r['invariant']}): "
            f"detected {r['detected']}/{r['tried']} {detection_pct:.0f}%; "
            f"intended-major {r['intended_major']}/{r['tried']} "
            f"{intended_major_pct:.0f}%; "
            f"major-blocked {r['major_blocked']}/{r['tried']} "
            f"{blocking_pct:.0f}%"
        )

    write_mutation_results(
        args.json,
        results,
        card_id=calibrate.cardcfg.CARD_ID,
        seed=args.seed,
        per_class=args.per_class,
    )
    print(f"wrote {args.json}")

    if expected is not None:
        regressions = baseline_regressions(results, expected)
        if regressions:
            print("\n=== MUTATION BASELINE FAILED ===")
            for problem in regressions:
                print(f"- {problem}")
            raise SystemExit(1)
        print(f"mutation baseline held: {args.baseline}")


if __name__ == "__main__":
    try:
        main()
    except (SourceProjectionError, MutationBaselineError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(getattr(exc, "exit_code", 2)) from exc
