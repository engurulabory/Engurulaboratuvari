from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_local_finisher_rehearsal.py"
SPEC = importlib.util.spec_from_file_location("mac_engineer_local_finisher_rehearsal", MODULE_PATH)
assert SPEC and SPEC.loader
rehearsal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rehearsal)


class LocalFinisherRehearsalTests(unittest.TestCase):
    def test_rehearsal_observes_fault_recovers_and_finishes_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = rehearsal.perform(Path(tmp))

        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(payload["scope"], "PRE_A11_LOCAL_FINISHER_REHEARSAL")
        self.assertTrue(payload["controlledFault"]["observed"])
        self.assertEqual(payload["recovery"]["regression"], "PASS")
        self.assertTrue(payload["recovery"]["idempotent"])
        self.assertTrue(payload["recovery"]["restoredBaselineHash"])
        self.assertEqual(payload["recovery"]["finalWorktree"], "CLEAN")
        self.assertIn("NO_A09_NO_A11", payload["authority"])


if __name__ == "__main__":
    unittest.main()
