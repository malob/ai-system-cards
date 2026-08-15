"""Shared normalization for text comparison (verification contract §Normalization).

Two allowlists:
- PRODUCTION: what v2 output is allowed to differ from the source by (A1-A5).
- CALIBRATION adds v1's known, accepted divergences (quote folding) so that
  calibrating against v1 markdown doesn't drown in them. v2 generation must NOT
  rely on the calibration extras.
"""

import re
import unicodedata

LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st"}
INVISIBLES = re.compile("[­​‌‍⁠﻿]")  # soft hyphen, zero-widths
# A hyphenated compound that wraps after its hyphen extracts as 'X- y'
# ('introspection- based', 'Self- knowledge'); the faithful render joins it to
# 'X-y'. Fold both forms to 'X-y' so the comparison is wrap-insensitive (an A2
# sibling — text-form-only, never affects output). Whitespace-run tolerant:
# page_body_text puts two spaces at a wrap.
WRAP_HYPHEN = re.compile(r"(\w)-\s+(?=[a-z])")

# v1 stored straight quotes (renderer smart-quoted them); fold for calibration only.
CALIBRATION_FOLDS = {
    "“": '"', "”": '"',          # curly double quotes
    "‘": "'", "’": "'",          # curly single quotes
    "‑": "-",                          # non-breaking hyphen
    " ": " ",                          # nbsp
}


def normalize(text: str, calibration: bool = False) -> str:
    text = unicodedata.normalize("NFC", text)
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    text = INVISIBLES.sub("", text)
    text = WRAP_HYPHEN.sub(r"\1-", text)
    if calibration:
        for k, v in CALIBRATION_FOLDS.items():
            text = text.replace(k, v)
    return text


BULLET_GLYPHS = "●•◦▪‣○"

# End-of-line hyphenation join (A1), the OUTPUT-side transform shared by the
# serializer and the oracle's body-text projection so T1 sees both sides
# identically. 'informa- tion' → 'information'; suspended compounds keep
# their hyphen via the and/or/to lookahead ('single- and multi-'); and a
# wrap INSIDE a suspended-compound family keeps the hyphen too — 'Opus- and
# Sonnet- class models' must join to 'Sonnet-class', not 'Sonnetclass'
# (risk-report p.181).
A1_HYPHEN = re.compile(r"(\w)- (?!(?:and|or|to)\b)(?=[a-z])")


def join_wrap_hyphens(text: str) -> str:
    def _sub(m):
        if re.search(r"\w- (?:and|or|to)\b", text[max(0, m.start() - 40):m.start()]):
            return m.group(1) + "-"
        return m.group(1)
    return A1_HYPHEN.sub(_sub, text)


# MIRROR of A1 — the line wraps BEFORE the hyphen, so the continuation opens
# with it ('national-security' | '-relevant'). Unlike A1 this is NOT safe as
# a text rule: 'sed -i' and 'well-resourced and -staffed' are identical in
# text and must keep their space. It is therefore applied only where the
# LINE BOUNDARY is known — the join sites in oracle.page_body_text and
# assemble.block_text_and_marks, via this predicate.
LEAD_HYPHEN = re.compile(r"^-[a-z]", re.I)


def wrap_joins_tight(prev_line: str, next_line: str) -> bool:
    """True when a line join must NOT insert a space: the continuation opens
    with a hyphen that belongs to the word the previous line ended on."""
    return bool(prev_line and prev_line.rstrip()[-1:].isalnum()
                and LEAD_HYPHEN.match(next_line.lstrip()))

# Google Docs exports mark list markers with a zero-width space after the
# glyph/number ("●​Text", "1.​Text") — the shared mechanical signature used by
# both the generator (assemble) and the ST structural invariant.
import re as _re
LIST_MARKER = _re.compile(r"^([●•◦▪‣○]|\d{1,2}[.)]|[a-z][.)])​")  # incl. lettered sub-lists (a. b. c.)


def squash(text: str, calibration: bool = True) -> str:
    """Space-free token-normalized key — immune to span-join glue, wrapping,
    and bullet glyphs. The comparison form for S1/FN1-style text matching."""
    return "".join(tokens(text, calibration))


def tokens(text: str, calibration: bool = False) -> list[str]:
    """Whitespace-insensitive token stream (A2). Bullet glyphs are layout
    artifacts (list structure is checked by ST invariants), dropped (A5) —
    including when glued to the following word."""
    out = []
    for t in normalize(text, calibration).split():
        t = t.lstrip(BULLET_GLYPHS)
        if t:
            out.append(t)
    return out
