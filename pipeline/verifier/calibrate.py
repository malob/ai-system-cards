"""Verifier v0 calibration driver.

Run the gate invariants over v1's markdown at a given git ref, against the PDF
oracle. Usage (from repo root):

    uv run --with pymupdf python pipeline/verifier/calibrate.py WORKTREE
    uv run --with pymupdf python pipeline/verifier/calibrate.py f60899a
    ... [--sections 02a 06f] [--json out.json] [--samples 12]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import invariants
import mdproj
import oracle

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "cards/anthropic/claude-fable-5"
TOC_PAGES = set(range(4, 11))
EXPECTED_PAGES = [p for p in range(2, 320) if p not in TOC_PAGES]  # 1 = cover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref", help="git ref for the markdown side, or WORKTREE")
    ap.add_argument("--sections", nargs="*", help="prefixes to limit to (e.g. 02a)")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--samples", type=int, default=10)
    args = ap.parse_args()

    pages = oracle.extract(CARD / "source.pdf", cache=REPO / "pipeline/.cache/oracle.json")
    figures_map = json.loads((CARD / "extracted/figures-map.json").read_text())

    sections = []
    for name, text in mdproj.sections_at_ref(REPO, args.ref):
        if args.sections and not any(name.startswith(p) for p in args.sections):
            continue
        sections.append(mdproj.project(name, text))

    # global streams — sections share boundary pages, so compare the whole doc.
    # Title pages 1-2 are declared exclusions (cover art + title typography;
    # trivially eyeballable, no body text).
    md_tokens = [tp for sec in sections for tp in sec.tokens if tp[1] > 2]
    md_links = [l for sec in sections for l in sec.links]
    table_pages = set().union(*(sec.table_pages for sec in sections))
    table_pages |= {p + 1 for p in table_pages} | {p - 1 for p in table_pages}  # spill
    if args.sections:
        page_range = range(max(3, sections[0].page_start), sections[-1].page_end + 1)
    else:
        page_range = range(3, 320)

    flags = []
    flags += invariants.t1_text(md_tokens, pages, page_range, TOC_PAGES, table_pages)
    flags += invariants.l1_links(md_links, pages, page_range, TOC_PAGES, table_pages)
    flags += invariants.fn1_footnotes(sections, pages, page_range, TOC_PAGES)
    if not args.sections:
        flags += invariants.p1_markers(sections, EXPECTED_PAGES)
        flags += invariants.f1_figures(sections, figures_map)
    flags = invariants.pair_displacements(flags)

    by_inv = Counter((f["invariant"], f["severity"]) for f in flags)
    print(f"\n=== verifier v0 @ {args.ref} — {len(sections)} sections ===")
    for (inv, sev), n in sorted(by_inv.items()):
        print(f"{inv:>4} {sev:<6} {n}")

    for inv in ("T1", "L1", "P1", "F1", "FN1"):
        sample = [f for f in flags if f["invariant"] == inv and f["severity"] == "major"][: args.samples]
        if sample:
            print(f"\n--- {inv} major samples ---")
            for f in sample:
                print(f"p.{f['page']:<4} {json.dumps(f['detail'], ensure_ascii=False)[:220]}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(flags, indent=1, ensure_ascii=False))
        print(f"\nwrote {args.json} ({len(flags)} flags)")


if __name__ == "__main__":
    main()
