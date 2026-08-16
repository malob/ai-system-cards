import copy
import json
import tempfile
import unittest
from pathlib import Path

import acceptance
import calibrate


def _flag():
    return {
        "invariant": "T1",
        "page": 37,
        "severity": "major",
        "detail": {
            "op": "replace",
            "missing_from_md": "Fabrication",
            "extra_in_md": "Skipped cheap verification",
            "n_tokens": 3,
        },
    }


def _config(*entries):
    return acceptance.parse_acceptances({"accepted": list(entries)})


def _entry_without_helper(flag):
    """Construct a wire-format entry so forbidden-entry parsing is testable."""
    payload = acceptance.canonical_flag(flag)
    return {**payload, "fingerprint": acceptance.flag_fingerprint(payload)}


class AcceptanceTests(unittest.TestCase):
    def test_fingerprint_is_stable_canonical_sha256(self):
        flag = _flag()
        reordered = {
            "detail": dict(reversed(list(flag["detail"].items()))),
            "severity": flag["severity"],
            "page": flag["page"],
            "invariant": flag["invariant"],
        }
        expected = "e94d8a4e508ae032e33cbb969be34c4ca585b19bc2bce82d66e664fd5f6cb117"
        self.assertEqual(acceptance.flag_fingerprint(flag), expected)
        self.assertEqual(acceptance.flag_fingerprint(reordered), expected)

    def test_exact_flag_is_suppressed(self):
        flag = _flag()
        result = acceptance.apply_acceptances(
            [flag], _config(acceptance.acceptance_entry(flag)))
        self.assertEqual(result.flags, [])
        self.assertEqual(result.matched, (acceptance.flag_fingerprint(flag),))
        self.assertEqual(result.stale, ())

    def test_same_invariant_and_page_with_different_detail_is_not_suppressed(self):
        accepted = _flag()
        new_flag = copy.deepcopy(accepted)
        new_flag["detail"]["missing_from_md"] = "new regression"
        result = acceptance.apply_acceptances(
            [new_flag], _config(acceptance.acceptance_entry(accepted)))
        self.assertEqual(result.flags, [new_flag])
        self.assertEqual(result.matched, ())
        self.assertEqual(result.stale, (acceptance.flag_fingerprint(accepted),))

    def test_stale_acceptance_is_rejected_when_required(self):
        flag = _flag()
        result = acceptance.apply_acceptances(
            [], _config(acceptance.acceptance_entry(flag)))
        with self.assertRaisesRegex(acceptance.AcceptanceConfigError,
                                    "stale acceptance fingerprint"):
            acceptance.reject_stale(result)

    def test_duplicate_acceptance_is_rejected(self):
        entry = acceptance.acceptance_entry(_flag())
        with self.assertRaisesRegex(acceptance.AcceptanceConfigError,
                                    "duplicate acceptance fingerprint"):
            _config(entry, dict(entry))

    def test_invalid_fingerprint_is_rejected(self):
        entry = acceptance.acceptance_entry(_flag())
        entry["fingerprint"] = "0" * 64
        with self.assertRaisesRegex(acceptance.AcceptanceConfigError,
                                    "does not match its exact flag payload"):
            _config(entry)

    def test_source_authority_entry_builders_reject_generic_acceptance(self):
        guidance = {
            "P2": "use source-inventory.json",
            "F3": "use source-inventory.json",
            "RF1": "use source-footnote-dispositions.json",
            "L2": "no generic exception is permitted",
            "V1": "no generic exception is permitted",
        }
        for invariant, message in guidance.items():
            with self.subTest(invariant=invariant):
                flag = {**_flag(), "invariant": invariant}
                with self.assertRaisesRegex(
                    acceptance.AcceptanceConfigError,
                    message,
                ):
                    acceptance.acceptance_entry(flag)

    def test_all_rf1_finding_kinds_are_rejected_before_matching(self):
        kinds = (
            "invalid-disposition-document",
            "invalid-disposition-schema",
            "stale-disposition-source",
            "duplicate-disposition-observation",
            "definition-text-mismatch",
        )
        for kind in kinds:
            with self.subTest(kind=kind):
                flag = {
                    "invariant": "RF1",
                    "page": 37,
                    "severity": "major",
                    "detail": {"kind": kind},
                }
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "accepted.json"
                    path.write_text(json.dumps({
                        "accepted": [_entry_without_helper(flag)],
                    }))
                    remaining, matched, error = calibrate._apply_accepted(
                        [flag], path, require_all=True
                    )

                self.assertEqual(remaining, [flag])
                self.assertEqual(matched, 0)
                self.assertIn("cannot accept RF1 findings", error)
                self.assertEqual(
                    acceptance.gate_exit_code(
                        remaining, config_error=error is not None
                    ),
                    2,
                )

    def test_calibrate_still_suppresses_exact_t1_acceptance(self):
        flag = _flag()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "accepted.json"
            path.write_text(json.dumps({
                "accepted": [acceptance.acceptance_entry(flag)],
            }))
            remaining, matched, error = calibrate._apply_accepted(
                [flag], path, require_all=True
            )

        self.assertEqual(remaining, [])
        self.assertEqual(matched, 1)
        self.assertIsNone(error)
        self.assertEqual(
            acceptance.gate_exit_code(
                remaining, config_error=error is not None
            ),
            0,
        )

    def test_rf1_config_error_is_transactional_before_t1_matching(self):
        t1_flag = _flag()
        rf1_flag = {
            "invariant": "RF1",
            "page": 37,
            "severity": "major",
            "detail": {"kind": "definition-text-mismatch"},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "accepted.json"
            path.write_text(json.dumps({
                "accepted": [
                    acceptance.acceptance_entry(t1_flag),
                    _entry_without_helper(rf1_flag),
                ],
            }))
            remaining, matched, error = calibrate._apply_accepted(
                [t1_flag, rf1_flag], path, require_all=True
            )

        self.assertEqual(remaining, [t1_flag, rf1_flag])
        self.assertEqual(matched, 0)
        self.assertIn("cannot accept RF1 findings", error)
        self.assertEqual(
            acceptance.gate_exit_code(
                remaining, config_error=error is not None
            ),
            2,
        )

    def test_p2_and_f3_config_errors_are_transactional_before_matching(self):
        authority_flags = (
            {
                "invariant": "P2",
                "page": 37,
                "severity": "major",
                "detail": {"kind": "missing-page-marker"},
            },
            {
                "invariant": "F3",
                "page": 37,
                "severity": "major",
                "detail": {
                    "kind": "missing-rendered-figure",
                    "filename": "p037-1.png",
                },
            },
        )
        for authority_flag in authority_flags:
            with self.subTest(invariant=authority_flag["invariant"]):
                t1_flag = _flag()
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "accepted.json"
                    path.write_text(json.dumps({
                        "accepted": [
                            acceptance.acceptance_entry(t1_flag),
                            _entry_without_helper(authority_flag),
                        ],
                    }))
                    remaining, matched, error = calibrate._apply_accepted(
                        [t1_flag, authority_flag], path, require_all=True
                    )

                self.assertEqual(remaining, [t1_flag, authority_flag])
                self.assertEqual(matched, 0)
                self.assertIn(
                    f"cannot accept {authority_flag['invariant']} findings",
                    error,
                )
                self.assertIn("use source-inventory.json", error)
                self.assertEqual(
                    acceptance.gate_exit_code(
                        remaining, config_error=error is not None
                    ),
                    2,
                )

    def test_l2_and_v1_wire_entries_have_no_generic_exception(self):
        for invariant, authority in (
            ("L2", "source/link projection authority"),
            ("V1", "final-rendered-DOM visibility authority"),
        ):
            with self.subTest(invariant=invariant):
                flag = {
                    "invariant": invariant,
                    "page": 37,
                    "severity": "major",
                    "detail": {"kind": "authority-regression"},
                }
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "accepted.json"
                    path.write_text(json.dumps({
                        "accepted": [_entry_without_helper(flag)],
                    }))
                    remaining, matched, error = calibrate._apply_accepted(
                        [flag], path, require_all=True
                    )

                self.assertEqual(remaining, [flag])
                self.assertEqual(matched, 0)
                self.assertIn("no generic exception is permitted", error)
                self.assertIn(authority, error)
                self.assertEqual(
                    acceptance.gate_exit_code(
                        remaining, config_error=error is not None
                    ),
                    2,
                )

    def test_exit_codes(self):
        major = _flag()
        minor = {**major, "severity": "minor"}
        self.assertEqual(acceptance.gate_exit_code([major]), 1)
        self.assertEqual(acceptance.gate_exit_code([major], report_only=True), 0)
        self.assertEqual(acceptance.gate_exit_code([minor]), 0)
        self.assertEqual(
            acceptance.gate_exit_code([], report_only=True, config_error=True), 2)


if __name__ == "__main__":
    unittest.main()
