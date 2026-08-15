import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATE = ROOT / "pipeline" / "generate"
sys.path.insert(0, str(GENERATE))

SPEC = importlib.util.spec_from_file_location("generate_run", GENERATE / "run.py")
generate_run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_run)


class GenerateHandoffTests(unittest.TestCase):
    def test_full_generation_handoff_preserves_card_and_runs_full_gate(self):
        command = generate_run.verifier_command(full=True, section_prefixes=["00", "01"])
        self.assertIn(f"CARD={generate_run.cardcfg.CARD_ID}", command)
        self.assertTrue(command.endswith("calibrate.py WORKTREE"))
        self.assertNotIn("--sections", command)

    def test_partial_generation_handoff_keeps_section_scope(self):
        command = generate_run.verifier_command(full=False, section_prefixes=["02a", "02b"])
        self.assertIn(str(generate_run.OUT), command)
        self.assertIn("--sections 02a 02b", command)


if __name__ == "__main__":
    unittest.main()
