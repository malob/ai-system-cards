"""Focused independence checks for the legacy evidence replay."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("inspect_legacy_passes.py")
SPEC = importlib.util.spec_from_file_location("inspect_legacy_passes", MODULE_PATH)
assert SPEC and SPEC.loader
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)


class ProductionComparisonTests(unittest.TestCase):
    def test_fixture_replay_does_not_touch_production_cache_when_disabled(self):
        def forbidden_loader(*_args, **_kwargs):
            raise AssertionError("production cache loader must not be called")

        self.assertEqual(
            {},
            inspector.production_comparison(
                "<table></table>",
                1,
                0,
                {},
                enabled=False,
                loader=forbidden_loader,
            ),
        )

    def test_enabled_comparison_uses_supplied_loader(self):
        expected = "<table><tr><td>x</td></tr></table>"

        def loader(page_no, oracle_page):
            self.assertEqual(page_no, 4)
            self.assertEqual(oracle_page, {"page": 4})
            return [{"html": expected}]

        self.assertEqual(
            {
                "production_sha256": inspector.digest(expected),
                "matches_production": True,
            },
            inspector.production_comparison(
                expected,
                4,
                0,
                {"page": 4},
                enabled=True,
                loader=loader,
            ),
        )


if __name__ == "__main__":
    unittest.main()
