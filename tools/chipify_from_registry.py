"""Promote bold spans that are known smart-chip labels into :chip[…] directives.

For cards transcribed before the chip convention existed, smart chips survive as
plain bold (e.g. `**Fabrication**`). This reads the `chips:` registry from the
card's meta.yaml and rewrites each exact bold span `**Label**` whose text is a
registered label into `:chip[Label]`. Labels are matched longest-first and only
as whole bold spans, so multi-word labels and substrings don't collide.

Going forward, transcription agents should emit `:chip[Label]` directly; this
tool is the one-time migration for already-transcribed cards.

Usage: python3 tools/chipify_from_registry.py <card-dir> [--apply]
"""
import re
import sys
from pathlib import Path

import importlib.util

def load_yaml_chips(meta_path):
    # avoid a yaml dependency: parse the simple `chips:` block ourselves
    chips = {}
    in_block = False
    for line in meta_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^chips:\s*$", line):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^\s+(.+?):\s*(\S+)\s*$", line)
            if m and (line.startswith(" ") or line.startswith("\t")):
                key = m.group(1).strip().strip('"').strip("'")
                chips[key] = m.group(2).strip()
            elif line and not line[0].isspace():
                break
    return chips


def process(card_dir, apply):
    chips = load_yaml_chips(card_dir / "meta.yaml")
    if not chips:
        print("no chips registry in meta.yaml")
        return
    labels = sorted(chips, key=len, reverse=True)
    total = 0
    for f in sorted((card_dir / "sections").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        n = 0
        for label in labels:
            pat = re.compile(r"\*\*" + re.escape(label) + r"\*\*")
            text, k = pat.subn(f":chip[{label}]", text)
            n += k
        if n:
            print(f"  {f.name}: {n} chips")
            total += n
            if apply:
                f.write_text(text, encoding="utf-8")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {total} bold spans promoted to chips")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    process(Path(args[0]), "--apply" in sys.argv)
