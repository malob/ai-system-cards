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
    def test_class_rng_is_independent_of_other_class_sampling(self):
        first = mutate.class_rng(5, "repoint-link")
        expected = [first.random() for _ in range(3)]
        unrelated = mutate.class_rng(5, "drop-link")
        for _ in range(100):
            unrelated.random()
        second = mutate.class_rng(5, "repoint-link")
        actual = [second.random() for _ in range(3)]
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected[0], mutate.class_rng(5, "drop-link").random())

    def test_repoint_link_uses_a_different_existing_target(self):
        source = "[first](#one) and [second](#two)"
        changed, note = mutate.mutations("repoint-link", source, mutate.random.Random(5))
        self.assertNotEqual(source, changed)
        self.assertIn(" -> ", note)
        targets = [target for _, target in mutate.RE_INTERNAL_LINK.findall(changed)]
        self.assertTrue(set(targets).issubset({"one", "two"}))
        self.assertEqual(1, len(set(targets)))

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
