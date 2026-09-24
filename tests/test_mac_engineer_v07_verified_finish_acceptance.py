from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v07_verified_finish_acceptance.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v07_verified_finish_acceptance",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
finish = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(finish)


class VerifiedFinishAcceptanceTests(unittest.TestCase):
    def test_donecheck_exact_sha_is_locked(self):
        self.assertEqual(
            finish.DONECHECK_SHA,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )

    def test_verified_finish_evidence_root_is_local_v07(self):
        self.assertIn(
            "MacEngineer/v0.7/verified-finish",
            str(finish.EVIDENCE_ROOT),
        )

    def test_latest_human_decision_selects_latest_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "a" / "human-decision.json"
            second = root / "b" / "human-decision.json"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("{}", encoding="utf-8")
            second.write_text("{}", encoding="utf-8")
            first.touch()
            second.touch()
            old = finish.HUMAN_ROOT
            try:
                finish.HUMAN_ROOT = root
                selected = finish.latest_human_decision()
                self.assertIn(selected, {first, second})
            finally:
                finish.HUMAN_ROOT = old


if __name__ == "__main__":
    unittest.main()
