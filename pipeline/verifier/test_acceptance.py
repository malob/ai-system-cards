import copy
import unittest

import acceptance


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
