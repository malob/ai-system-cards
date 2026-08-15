import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

# mutate imports the full verifier stack.  Keeping the import explicit makes the
# test runnable both as discovery and as a single file under uv + PyMuPDF.
SPEC = importlib.util.spec_from_file_location("mutate", HERE / "mutate.py")
mutate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mutate)


def result(caught=7, tried=8, invariant="T1"):
    return {"invariant": invariant, "caught": caught, "tried": tried, "details": []}


class MutationBaselineTests(unittest.TestCase):
    def test_equal_result_holds(self):
        self.assertEqual([], mutate.baseline_regressions({"drop": result()}, {"drop": result()}))

    def test_improvement_holds(self):
        self.assertEqual(
            [], mutate.baseline_regressions({"drop": result(caught=8)}, {"drop": result(caught=7)})
        )

    def test_recall_drop_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(caught=6)}, {"drop": result(caught=7)}
        )
        self.assertIn("recall regressed", problems[0])

    def test_sample_count_change_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(tried=10)}, {"drop": result(tried=8)}
        )
        self.assertIn("sample count changed", problems[0])

    def test_class_set_changes_fail(self):
        problems = mutate.baseline_regressions(
            {"new": result()}, {"removed": result()}
        )
        self.assertEqual(2, len(problems))
        self.assertTrue(any("missing" in p for p in problems))
        self.assertTrue(any("no committed baseline" in p for p in problems))

    def test_invariant_change_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(invariant="L1")}, {"drop": result(invariant="T1")}
        )
        self.assertIn("invariant changed", problems[0])


if __name__ == "__main__":
    unittest.main()
