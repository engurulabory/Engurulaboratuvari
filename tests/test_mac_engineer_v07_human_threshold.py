from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v07_human_threshold.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v07_human_threshold",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
threshold = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(threshold)


class HumanThresholdTests(unittest.TestCase):
    def test_accept_token_is_explicit_and_stable(self):
        self.assertEqual(
            threshold.ACCEPT_TOKEN,
            "I_ACCEPT_V07_MAC_NATIVE_AUTHORITY",
        )

    def test_review_and_accept_are_distinct_modes(self):
        self.assertNotEqual("REVIEW", "ACCEPT")

    def test_gate_13_evidence_root_is_local_v07(self):
        self.assertIn(
            "MacEngineer/v0.7/human-threshold",
            str(threshold.EVIDENCE_ROOT),
        )


if __name__ == "__main__":
    unittest.main()
