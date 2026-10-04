from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "enguru_language_pre_send_linter.py"
SPEC = importlib.util.spec_from_file_location("enguru_language_pre_send_linter", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EnguruLanguagePreSendLinterTests(unittest.TestCase):
    def test_positive_valid_state_instruction_passes(self):
        text = (
            "STATE — Current canonical repository truth is authoritative.\n"
            "CLAIM — The required difference is bounded.\n"
            "EVIDENCE — current SHA abc123 and test receipt are present.\n"
            "NEXT ACTION — Apply the bounded change and rerun regression.\n"
        )
        result = MODULE.lint(text, strict=True)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["finding_count"], 0)

    def test_prohibition_first_instruction_holds(self):
        result = MODULE.lint("Do not use stale context.\n")
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(f["rule"] == "L01" for f in result["findings"]))

    def test_turkish_negative_instruction_holds(self):
        result = MODULE.lint("Eski konuşma özetlerinden teknik gerçeklik varsayılmayacak.\n")
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(f["rule"] == "L01" for f in result["findings"]))

    def test_verified_negative_state_is_allowed(self):
        result = MODULE.lint("STATE — CI is not available because the external runner gate is blocked.\n")
        self.assertEqual(result["state"], "PASS")

    def test_governed_block_requires_claim_and_evidence(self):
        result = MODULE.lint("STATE: HOLD\nNEXT_ACTION: Verify current repository truth.\n")
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(f["rule"] == "L03" for f in result["findings"]))

    def test_placeholder_evidence_is_critical(self):
        result = MODULE.lint("EVIDENCE — TODO_EVIDENCE\n")
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(f["rule"] == "L11" and f["severity"] == "CRITICAL" for f in result["findings"]))

    def test_strict_pass_needs_evidence(self):
        result = MODULE.lint("STATE=PASS\nCLAIM: Everything is complete.\nEVIDENCE:\n", strict=True)
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(f["rule"] == "L04" for f in result["findings"]))


    def test_fail_is_canonical_state(self):
        result = MODULE.lint(
            "STATE=FAIL\n"
            "CLAIM: Runtime acceptance failed.\n"
            "EVIDENCE: test receipt rc=1 is present.\n"
            "NEXT_ACTION: Repair the observed runtime difference.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")

    def test_bozmadan_holds(self):
        result = MODULE.lint(
            "Mevcut sistemi bozmadan gerekli değişikliği uygula.\n"
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L13" for f in result["findings"])
        )

    def test_koruyarak_passes(self):
        result = MODULE.lint(
            "Mevcut sistemi koruyarak gerekli farkı uygula.\n"
        )
        self.assertEqual(result["state"], "PASS")

    def test_unknown_verdict_holds(self):
        result = MODULE.lint(
            "STATE=COMPLETE\n"
            "CLAIM: Work is complete.\n"
            "EVIDENCE: current test receipt is present.\n"
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L06" for f in result["findings"])
        )


if __name__ == "__main__":
    unittest.main()
