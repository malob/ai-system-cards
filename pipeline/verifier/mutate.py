"""Mutation tester (D6): inject synthetic defects into a copy of the HEAD
sections, run the verifier, and measure per-class recall — turning "calibrated
on history" into a number.

    uv run --with pymupdf python pipeline/verifier/mutate.py [--per-class 8] [--seed 5]

Detection rule: a mutation is caught iff the run produces a flag of the class's
invariant that was NOT in the unmutated baseline (matched on invariant+detail).
"""

import argparse
import json
import random
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import calibrate  # noqa: E402

SECTIONS = calibrate.CARD / "sections"
RE_LINK = re.compile(r"\[([^\]^][^\]]*)\]\((https?://[^)]+)\)")
RE_CHIP = re.compile(r":chip\[([^\]]+)\]")
RE_SENT = re.compile(r"(?<=[.!?] )([A-Z][^.!?\n]{40,180}[.!?]) ")
RE_IMG = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$", re.M)
RE_FNDEF = re.compile(r"^\[\^\d+\]:.*$", re.M)
RE_MARKER = re.compile(r"<!-- p\.\d+ -->")
RE_BOLDLEAD = re.compile(r"\*\*([A-Z][^*]{6,60})\*\*")
RE_WORDPAIR = re.compile(r"(?<= )([a-z]{4,12}) ([a-z]{4,12})(?= )")


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
    if kind == "flatten-chip":
        m = pick(list(RE_CHIP.finditer(text)))
        return (text[: m.start()] + f"**{m.group(1)}**" + text[m.end():], m.group(1)) if m else None
    if kind == "delete-sentence":
        m = pick(list(RE_SENT.finditer(text)))
        return (text[: m.start(1)] + text[m.end():], m.group(1)[:40]) if m else None
    if kind == "duplicate-paragraph":
        paras = [p for p in text.split("\n\n") if len(p) > 200 and not p.startswith(("<", "!", ":", "#", "|"))]
        p = pick(paras)
        return (text.replace(p, p + "\n\n" + p, 1), p[:40]) if p else None
    if kind == "swap-words":
        m = pick(list(RE_WORDPAIR.finditer(text)))
        return (text[: m.start()] + f"{m.group(2)} {m.group(1)}" + text[m.end():], m.group(0)) if m else None
    if kind == "drop-image":
        m = pick(list(RE_IMG.finditer(text)))
        return (text[: m.start()] + text[m.end():], m.group(0)[:40]) if m else None
    if kind == "drop-fndef":
        m = pick(list(RE_FNDEF.finditer(text)))
        return (text[: m.start()] + text[m.end():], m.group(0)[:30]) if m else None
    if kind == "dup-marker":
        m = pick(list(RE_MARKER.finditer(text)))
        return (text + f"\n\n{m.group(0)}\n", m.group(0)) if m else None
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
    "flatten-chip": "S2",
    "delete-sentence": "T1",
    "duplicate-paragraph": "T1",
    "swap-words": "T1",
    "drop-image": "F1",
    "drop-fndef": "FN1",
    "dup-marker": "P1",
    "drop-bold": "S1",
}


def flag_keys(flags):
    return {(f["invariant"], json.dumps(f["detail"], sort_keys=True)) for f in flags}


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
        if got.get("invariant") != want.get("invariant"):
            problems.append(
                f"{kind}: invariant changed {want.get('invariant')} -> {got.get('invariant')}"
            )
        if got.get("tried") != want.get("tried"):
            problems.append(
                f"{kind}: sample count changed {want.get('tried')} -> {got.get('tried')}"
            )
        elif got.get("caught", 0) < want.get("caught", 0):
            problems.append(
                f"{kind}: recall regressed {want.get('caught')}/{want.get('tried')}"
                f" -> {got.get('caught')}/{got.get('tried')}"
            )
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=8)
    ap.add_argument("--seed", type=int, default=5)
    # Per-card default. The legacy plain results.json remains the original
    # fable-5 calibration record and must never be clobbered by a current run.
    ap.add_argument("--json", type=Path,
                    default=Path("docs/experiments/05-mutation-testing/"
                                 f"results-{calibrate.cardcfg.CARD_ID.replace('/', '-')}.json"))
    ap.add_argument("--classes", nargs="*", help="limit to these mutation kinds")
    ap.add_argument(
        "--baseline",
        type=Path,
        help="committed results JSON; fail if class coverage/sample count changes or recall drops",
    )
    args = ap.parse_args()
    rng = random.Random(args.seed)

    files = {p.name: p.read_text() for p in sorted(SECTIONS.glob("*.md"))}
    baseline = flag_keys(calibrate.collect_flags("WORKTREE"))
    print(f"baseline flags: {len(baseline)}")

    results = {}
    for kind, inv in CLASSES.items():
        if args.classes and kind not in args.classes:
            continue
        caught = tried = 0
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
            tmp = Path(tempfile.mkdtemp(prefix=f"mut-{kind}-"))
            for n, t in files.items():
                (tmp / n).write_text(mut[0] if n == name else t)
            new = [
                f for f in calibrate.collect_flags(str(tmp))
                if f["invariant"] == inv
                and (f["invariant"], json.dumps(f["detail"], sort_keys=True)) not in baseline
            ]
            hit = bool(new)
            caught += hit
            details.append({"file": name, "site": mut[1], "caught": hit})
            shutil.rmtree(tmp)
            print(f"{kind:>20} [{i+1}/{args.per_class}] {'HIT ' if hit else 'MISS'} {name}: {mut[1][:40]}")
        results[kind] = {"invariant": inv, "caught": caught, "tried": tried, "details": details}

    print("\n=== per-class recall ===")
    for kind, r in results.items():
        pct = 100 * r["caught"] / r["tried"] if r["tried"] else 0
        print(f"{kind:>20} ({r['invariant']}): {r['caught']}/{r['tried']}  {pct:.0f}%")

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(results, indent=1))
    print(f"wrote {args.json}")

    if args.baseline:
        expected = json.loads(args.baseline.read_text())
        regressions = baseline_regressions(results, expected)
        if regressions:
            print("\n=== MUTATION BASELINE FAILED ===")
            for problem in regressions:
                print(f"- {problem}")
            raise SystemExit(1)
        print(f"mutation baseline held: {args.baseline}")


if __name__ == "__main__":
    main()
