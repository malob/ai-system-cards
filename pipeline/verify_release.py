"""Run the complete fast release gate from one local command.

Invoke this under the repository's pinned verifier environment, after installing
the site lockfile:

    uv run --python 3.12 --with 'pymupdf==1.28.2' \
      python pipeline/verify_release.py

The slower seeded mutation floor remains a separate scheduled/review gate.  This
orchestrator mirrors the Pages dependency graph: shared card discovery, Python
unit tests, every card's source/canonical gates and tracked artifacts, seams,
then the browser-normalized site tests and production build.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"


@dataclass(frozen=True)
class CommandFailure(RuntimeError):
    label: str
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def __str__(self) -> str:
        return f"{self.label} exited {self.returncode}"


def _run(
    label: str,
    argv: list[str],
    *,
    cwd: Path = REPO,
    env: dict[str, str] | None = None,
) -> str:
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise CommandFailure(
            label,
            tuple(argv),
            result.returncode,
            result.stdout,
            result.stderr,
        )
    return result.stdout + result.stderr


def _require_executable(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"required executable is unavailable: {name}")


def _discover_cards() -> list[str]:
    output = _run(
        "card discovery",
        ["node", "site/scripts/card-matrix.mjs"],
    )
    try:
        cards = json.loads(output)
    except json.JSONDecodeError as error:
        raise RuntimeError("card discovery did not emit JSON") from error
    if (
        not isinstance(cards, list)
        or not cards
        or not all(isinstance(card, str) and card.count("/") == 1 for card in cards)
    ):
        raise RuntimeError("card discovery emitted an invalid or empty inventory")
    return cards


def _assert_same(actual: Path, expected: Path, label: str) -> None:
    try:
        same = actual.read_bytes() == expected.read_bytes()
    except OSError as error:
        raise RuntimeError(f"{label} could not be compared: {error}") from error
    if not same:
        raise RuntimeError(
            f"{label} is stale; regenerate and review {expected.relative_to(REPO)}"
        )


def _gate_card(card_id: str, temp_root: Path) -> str:
    safe_name = card_id.replace("/", "-")
    l2_path = temp_root / f"{safe_name}-l2-links.json"
    projection_path = temp_root / f"{safe_name}-source-projection.json"
    env = {**os.environ, "CARD": card_id}
    output = _run(
        f"gate {card_id}",
        [
            sys.executable,
            "pipeline/verifier/calibrate.py",
            "WORKTREE",
            "--l2-json",
            str(l2_path),
            "--source-projection-json",
            str(projection_path),
        ],
        env=env,
    )
    card_root = REPO / "cards" / card_id
    _assert_same(l2_path, card_root / "l2-links.json", f"{card_id} L2 artifact")
    _assert_same(
        projection_path,
        card_root / "source-projection.json",
        f"{card_id} source projection",
    )
    output += _run(
        f"table seams {card_id}",
        [sys.executable, "pipeline/audit_table_seams.py"],
        env=env,
    )
    return output


def _print_failure(error: Exception) -> None:
    print(f"\nFAILED: {error}", file=sys.stderr)
    if isinstance(error, CommandFailure):
        if error.stdout:
            print(error.stdout.rstrip(), file=sys.stderr)
        if error.stderr:
            print(error.stderr.rstrip(), file=sys.stderr)
        print(f"argv: {list(error.argv)!r}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jobs",
        type=int,
        default=3,
        help="parallel card gates (default: 3)",
    )
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs must be positive")

    try:
        _require_executable("node")
        _require_executable("pnpm")
        print("== shared card inventory ==", flush=True)
        inventory_test = _run(
            "card inventory test",
            ["node", "--test", "site/scripts/card-inventory.test.mjs"],
        )
        print(inventory_test.rstrip())
        cards = _discover_cards()
        print(f"discovered {len(cards)} card(s): {', '.join(cards)}")

        print("\n== verifier unit tests ==", flush=True)
        unit_output = _run(
            "verifier unit tests",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "pipeline/verifier",
                "-p",
                "test_*.py",
            ],
        )
        print(unit_output.rstrip())

        print("\n== all card gates + exact artifacts + seams ==", flush=True)
        failures: list[Exception] = []
        with tempfile.TemporaryDirectory(prefix="ai-system-cards-release-") as name:
            temp_root = Path(name)
            with ThreadPoolExecutor(max_workers=min(args.jobs, len(cards))) as pool:
                futures = {
                    pool.submit(_gate_card, card, temp_root): card for card in cards
                }
                outputs: dict[str, str] = {}
                for future in as_completed(futures):
                    card = futures[future]
                    try:
                        outputs[card] = future.result()
                    # A worker may surface an unexpected parser/filesystem
                    # exception. Collect every card failure before returning;
                    # never let one failed future hide its siblings' evidence.
                    except Exception as error:  # noqa: BLE001
                        failures.append(error)
                for card in cards:
                    if card in outputs:
                        print(f"\n--- {card} ---\n{outputs[card].rstrip()}")
        if failures:
            for error in failures:
                _print_failure(error)
            return 1

        print("\n== site unit/projection tests ==", flush=True)
        print(_run("site tests", ["pnpm", "test"], cwd=SITE).rstrip())
        print("\n== clean production build + final-DOM audits ==", flush=True)
        print(_run("site build", ["pnpm", "build"], cwd=SITE).rstrip())
    except (CommandFailure, RuntimeError) as error:
        _print_failure(error)
        return 1

    print("\nFAST RELEASE GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
