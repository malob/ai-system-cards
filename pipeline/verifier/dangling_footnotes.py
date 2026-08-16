"""Output-side footnote reference closure.

The source/body verifier deliberately removes footnote definitions from its main
text stream.  That is correct for ordinary footnotes, but it creates a dangerous
correlated-authority failure: prose misclassified as a source footnote can be
removed from both source and output body streams while surviving in an orphaned
Markdown definition.  A definition with no reference is independently observable
in the canonical projection, so reject it without consulting semantic zones.
"""

import hashlib
from collections.abc import Iterable
from typing import Any


def check(sections: Iterable[Any]) -> list[dict]:
    """Return FN1 majors for definitions unused in their publishable section.

    Sections are also exported as standalone Markdown documents, so reference
    closure is intentionally section-local.  Matching is exact on the parsed
    footnote number; nearby numbers and references in another section cannot
    justify a definition.
    """
    flags = []
    for section in sections:
        referenced = {number for number, _page in section.fn_refs}
        pages = getattr(section, "fn_def_pages", {})
        for number in sorted(section.fn_defs):
            if number in referenced:
                continue
            page = pages.get(number, section.page_end or section.page_start or 0)
            text = section.fn_defs[number]
            flags.append({
                "invariant": "FN1",
                "page": page,
                "severity": "major",
                "detail": {
                    "kind": "definition-without-ref",
                    "n": number,
                    "section": section.name,
                    "text": text[:80],
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "text_n_chars": len(text),
                    "text_n_tokens": len(text.split()),
                },
            })
    return flags
