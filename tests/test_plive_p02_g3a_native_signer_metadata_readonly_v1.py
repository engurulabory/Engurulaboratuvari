"""Offline G3-A metadata qualification adversarial tests. No signer execution."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from plive_p02_g3a_native_signer_metadata_readonly_v1 import (
    POLICY_REL, DECISION_REL, POLICY_SHA, DECISION_SHA, qualify,
)


class NativeSignerQualificationTests(unittest.TestCase):
    def test_empty_root_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), None)
            self.assertEqual(x["state"], "HOLD_G3A_NATIVE_AUTHORITY")
            self.assertEqual(x["checks"]["policy"], "HOLD_PIN_OR_FILE")
            self.assertFalse(x["issuerQualified"])

    def test_missing_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), Path(d) / "absent")
            self.assertFalse(x["grantIssued"])
            self.assertEqual(x["canonicalWrites"], 0)
            self.assertEqual(x["keychainOperations"], 0)

    def test_candidate_never_signs(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), Path(d) / "absent")
            self.assertEqual(x["signatureOperations"], 0)
            self.assertEqual(x["verifiedFinish"], "HOLD")

    def test_policy_pin_is_not_issuer(self):
        self.assertEqual(len(POLICY_SHA), 64)
        self.assertEqual(len(DECISION_SHA), 64)
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), None)
            self.assertFalse(x["issuerQualified"])

    def test_no_external_commands_on_invalid_policy(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("plive_p02_g3a_native_signer_metadata_readonly_v1.command",
                       side_effect=AssertionError("command unexpectedly called")):
                qualify(Path(d), Path(d) / "absent")

    def test_policy_paths_scoped(self):
        self.assertIn("plive-p02-user-screen/", POLICY_REL)
        self.assertIn("plive-p02-user-screen/", DECISION_REL)


if __name__ == "__main__":
    unittest.main()
