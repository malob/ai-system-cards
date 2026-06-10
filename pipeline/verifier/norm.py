"""Shared normalization for text comparison (verification contract §Normalization).

Two allowlists:
- PRODUCTION: what v2 output is allowed to differ from the source by (A1-A4).
- CALIBRATION adds v1's known, accepted divergences (quote folding) so that
  calibrating against v1 markdown doesn't drown in them. v2 generation must NOT
  rely on the calibration extras.
"""

import re
import unicodedata

LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st"}
INVISIBLES = re.compile("[­​‌‍⁠﻿]")  # soft hyphen, zero-widths

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
    if calibration:
        for k, v in CALIBRATION_FOLDS.items():
            text = text.replace(k, v)
    return text


BULLET_GLYPHS = "●•◦▪‣○"

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
    artifacts (list structure is checked at the schema level), dropped (A5) —
    including when glued to the following word."""
    out = []
    for t in normalize(text, calibration).split():
        t = t.lstrip(BULLET_GLYPHS)
        if t:
            out.append(t)
    return out
