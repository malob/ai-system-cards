"""Rerunnable harness for the F18 correlated semantic-zoning failure.

This is deliberately a verifier fixture, not a production transformation.  It
models the measured failure mode: change a contiguous run of genuine body spans
to ``fnbody`` and make the corresponding canonical prose a footnote definition
without adding a reference.  The source and Markdown body projections then agree
on the same wrong omission, which demonstrates why a separate structural blocker
is required.
"""

from copy import deepcopy


def build_baseline(fixture: dict) -> tuple[dict, str]:
    """Build compact source facts and Markdown from an immutable F18 fixture."""
    page_number = int(fixture["page"])
    texts = fixture["retained_spans"] + fixture["relocated_spans"]
    spans = []
    for line, text in enumerate(texts, 1):
        y0 = 72.0 + line * 14.0
        spans.append({
            "text": text,
            "zone": "body",
            "line": line,
            "bbox": [72.0, y0, 528.0, y0 + 11.0],
            "font": "Arial",
        })
    page = {"spans": spans, "footnotes": {}}
    body = " ".join(text.strip() for text in texts)
    markdown = (
        f"<!-- source: source.pdf pages {page_number:03d}-{page_number:03d} -->\n\n"
        f"<!-- p.{page_number} -->\n\n{body}\n"
    )
    return page, markdown


def rezone_as_dangling_definition(
    page: dict,
    markdown: str,
    relocated_span_texts: list[str],
    footnote_number: int,
) -> tuple[dict, str]:
    """Move one exact contiguous body-span run into an unreferenced definition."""
    mutated_page = deepcopy(page)
    texts = [span["text"] for span in mutated_page["spans"]]
    width = len(relocated_span_texts)
    starts = [
        index for index in range(len(texts) - width + 1)
        if texts[index:index + width] == relocated_span_texts
    ]
    if len(starts) != 1:
        raise ValueError(f"expected one exact relocated span run, found {len(starts)}")
    if footnote_number in mutated_page.get("footnotes", {}):
        raise ValueError(f"footnote {footnote_number} already exists")

    start = starts[0]
    selected = mutated_page["spans"][start:start + width]
    if any(span.get("zone") != "body" for span in selected):
        raise ValueError("relocated span run must begin entirely in the body zone")
    for span in selected:
        span["zone"] = "fnbody"
        span["fn"] = footnote_number

    prose = " ".join(text.strip() for text in relocated_span_texts)
    if markdown.count(prose) != 1:
        raise ValueError("relocated prose must occur exactly once in canonical Markdown")
    mutated_page.setdefault("footnotes", {})[footnote_number] = prose
    definition = f"\n\n[^{footnote_number}]: {prose}"
    mutated_markdown = markdown.replace(prose, definition, 1)
    return mutated_page, mutated_markdown
