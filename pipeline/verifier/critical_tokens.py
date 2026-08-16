"""Semantic-critical atoms for T1 severity.

Token count is a poor proxy for consequence: changing one benchmark number or
deleting one negation can be more serious than moving a paragraph.  This module
compares a small local window around each T1 opcode and identifies ordered,
meaning-bearing atoms whose source and output values differ.

The comparison is deliberately formatting-aware but not content-normalizing.
Markdown/HTML wrappers and whitespace around numeric punctuation do not create a
new value; numbers, dates, units, negations, and comparators do.  The window is
local so equal document-wide counts cannot hide values swapped between claims.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

import norm


CLASS_ORDER = ("number", "date", "unit", "negation", "comparator")

_HTML_WRAPPER = re.compile(r"</?[A-Za-z][^>]*>")
_NUMERIC_PUNCT_SPACE = re.compile(r"(?<=\d)\s*([.,:/-])\s*(?=\d)")
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,;:%‰)\]])")
_SPACE_AFTER_OPEN = re.compile(r"([(\[])\s+")
_NUMBER = re.compile(r"(?<![\w.])[+-]?\d+(?:[.,:/-]\d+)*(?:[%‰])?")
_DATE = re.compile(r"\d{4}-\d{1,2}-\d{1,2}")
_WORD = re.compile(r"[A-Za-zµμ°%]+(?:[’'][A-Za-z]+)?")
_SYMBOL_COMPARATOR = re.compile(r"<=|>=|!=|==|<|>|=")
_PHRASE_COMPARATOR = re.compile(
    r"\b(?:at\s+(?:least|most)|up\s+to|no\s+(?:less|more)\s+than|"
    r"(?:less|greater|more|fewer)\s+than|under|over|below|above)\b",
    re.I,
)
_AMBIGUOUS_COMPARATORS = {"under", "over", "below", "above"}
_CURRENCY = re.compile(r"[$€£¥₹₩₽]")

_NEGATIONS = {
    "not", "no", "none", "never", "neither", "nor", "without",
    "cannot", "nothing", "nobody", "nowhere",
}

# Full words and low-ambiguity abbreviations are always units.  The one-letter
# symbols below count only next to a numeral in the local window.
_UNITS = {
    "%", "percent", "percentage", "percentages",
    "ms", "millisecond", "milliseconds",
    "second", "seconds", "sec", "secs",
    "minute", "minutes", "min", "mins",
    "hour", "hours", "hr", "hrs",
    "day", "days", "week", "weeks", "month", "months", "year", "years",
    "ns", "nanosecond", "nanoseconds", "us", "µs", "μs",
    "microsecond", "microseconds",
    "kg", "kilogram", "kilograms", "mg", "milligram", "milligrams",
    "µg", "μg", "microgram", "micrograms", "gram", "grams",
    "km", "kilometer", "kilometers", "kilometre", "kilometres",
    "cm", "centimeter", "centimeters", "centimetre", "centimetres",
    "mm", "millimeter", "millimeters", "millimetre", "millimetres",
    "meter", "meters", "metre", "metres", "mile", "miles",
    "foot", "feet", "inch", "inches",
    "l", "liter", "liters", "litre", "litres", "ml", "milliliter",
    "milliliters", "millilitre", "millilitres",
    "celsius", "fahrenheit", "kelvin", "°c", "°f",
    "hz", "khz", "mhz", "ghz", "hertz",
    "kb", "mb", "gb", "tb", "byte", "bytes", "kilobyte", "kilobytes",
    "megabyte", "megabytes", "gigabyte", "gigabytes", "terabyte", "terabytes",
    # Quantified AI/safety-report domains and magnitude words. A one-token
    # change from "tokens" to "parameters" or million to billion changes the
    # reported quantity even when its adjacent numeral is untouched.
    "token", "tokens", "parameter", "parameters", "request", "requests",
    "query", "queries", "sample", "samples", "point", "points",
    "thousand", "million", "billion", "trillion",
    "usd", "eur", "gbp", "jpy", "cny", "cad", "aud", "chf", "inr",
}
_AMBIGUOUS_UNITS = {"g", "m", "s", "h"}
_MONTHS = {
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
    "oct", "nov", "dec",
}


def canonical_text(tokens: Sequence[str]) -> str:
    """Remove projection wrappers while preserving semantic characters."""
    text = " ".join(tokens)
    text = norm.normalize(text, calibration=False)
    text = _HTML_WRAPPER.sub("", text)
    # Asterisks/backticks are unambiguous Markdown wrappers in the projected
    # fragments. Underscores are not: ``1_000`` and identifier names can carry
    # real code meaning, so leave them visible to the atom comparison.
    text = text.replace("`", "").replace("*", "")
    text = text.replace("\\", "")
    text = text.replace("≤", "<=").replace("≥", ">=").replace("≠", "!=")
    text = _NUMERIC_PUNCT_SPACE.sub(r"\1", text)
    text = _SPACE_BEFORE_PUNCT.sub(r"\1", text)
    text = _SPACE_AFTER_OPEN.sub(r"\1", text)
    return " ".join(text.split())


def _number_atoms(text: str) -> tuple[list[str], list[str]]:
    numbers: list[str] = []
    dates: list[str] = []
    for match in _NUMBER.finditer(text):
        value = match.group(0)
        if _DATE.fullmatch(value):
            dates.append(value)
        else:
            numbers.append(value)
    return numbers, dates


def _is_numeric_neighbor(text: str, start: int, end: int) -> bool:
    before = text[:start].rstrip()
    after = text[end:].lstrip()
    return bool(
        re.search(r"\d(?:[.,:/-]\d+)*\s*$", before)
        or re.match(r"^(?:,\s*)?\d", after)
    )


def _quantified_comparator_context(
    text: str, start: int, end: int, *, symbol: bool
) -> bool:
    before = text[max(0, start - 16):start]
    after = text[end:min(len(text), end + 16)]
    currency = r"[$€£¥₹₩₽]?"
    if re.match(rf"\s*{currency}\d", after):
        return True
    return symbol and bool(re.search(r"\d\s*$", before))


def atoms(tokens: Sequence[str]) -> dict[str, list[str]]:
    """Return ordered critical atoms in one formatting-normalized window."""
    text = canonical_text(tokens)
    numbers, dates = _number_atoms(text)
    result: dict[str, list[str]] = {
        "number": numbers,
        "date": dates,
        "unit": [],
        "negation": [],
        "comparator": [],
    }

    for match in _WORD.finditer(text):
        value = match.group(0).casefold().replace("’", "'")
        if value in _NEGATIONS or value.endswith("n't"):
            result["negation"].append(value)
        if value in _MONTHS and _is_numeric_neighbor(text, match.start(), match.end()):
            result["date"].append(value)
        if value in _UNITS or (
            value in _AMBIGUOUS_UNITS
            and _is_numeric_neighbor(text, match.start(), match.end())
        ):
            result["unit"].append(value)

    result["unit"].extend(match.group(0) for match in _CURRENCY.finditer(text))

    phrase_spans: list[tuple[int, int]] = []
    for match in _PHRASE_COMPARATOR.finditer(text):
        value = " ".join(match.group(0).casefold().split())
        if value in _AMBIGUOUS_COMPARATORS:
            if not _quantified_comparator_context(
                text, match.start(), match.end(), symbol=False
            ):
                continue
        result["comparator"].append("-".join(value.split()))
        phrase_spans.append(match.span())
    for match in _SYMBOL_COMPARATOR.finditer(text):
        # HTML wrappers were already removed; symbols that remain are content.
        if (not any(start <= match.start() < end for start, end in phrase_spans)
                and _quantified_comparator_context(
                    text, match.start(), match.end(), symbol=True)):
            result["comparator"].append(match.group(0))
    return result


def changed_classes(
    source_tokens: Sequence[str],
    output_tokens: Sequence[str],
) -> list[str]:
    """Return deterministic critical classes whose ordered local atoms differ."""
    source = atoms(source_tokens)
    output = atoms(output_tokens)
    return [name for name in CLASS_ORDER if source[name] != output[name]]


def opcode_classes(
    source_tokens: Sequence[str],
    output_tokens: Sequence[str],
    source_start: int,
    source_end: int,
    output_start: int,
    output_end: int,
    *,
    context: int = 2,
) -> list[str]:
    """Classify one opcode with enough equal context for units/phrases."""
    source_window = source_tokens[
        max(0, source_start - context):min(len(source_tokens), source_end + context)
    ]
    output_window = output_tokens[
        max(0, output_start - context):min(len(output_tokens), output_end + context)
    ]
    return changed_classes(source_window, output_window)


__all__ = ["CLASS_ORDER", "atoms", "canonical_text", "changed_classes", "opcode_classes"]
