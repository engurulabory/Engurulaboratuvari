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

    def test_hold_requires_unlock_condition_or_next_action(self):
        result = MODULE.lint(
            "STATE=HOLD\n"
            "CLAIM: Current evidence is incomplete.\n"
            "EVIDENCE: repository truth was inspected.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L14" for f in result["findings"])
        )

    def test_hold_with_unlock_condition_passes(self):
        result = MODULE.lint(
            "PACKAGE_STATE=HOLD\n"
            "CLAIM: Current evidence is incomplete.\n"
            "EVIDENCE: repository truth was inspected.\n"
            "UNLOCK_CONDITION: Focused runtime evidence completes the package gate.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")

    def test_verified_adjective_in_natural_state_is_not_closure(self):
        result = MODULE.lint(
            "STATE — Production remains blocked by verified external authority.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")
        self.assertFalse(
            any(f["rule"] == "L04" for f in result["findings"])
        )

    def test_verified_closure_still_requires_evidence(self):
        result = MODULE.lint(
            "STATE=VERIFIED\n"
            "CLAIM: Package closure is asserted.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L04" for f in result["findings"])
        )


    def test_blocked_requires_removal_path(self):
        result = MODULE.lint(
            "PACKAGE_STATE=BLOCKED\n"
            "CLAIM: Production deployment requires unavailable authority.\n"
            "EVIDENCE: authority check confirms access is unavailable.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L16" for f in result["findings"])
        )

    def test_blocked_with_next_action_passes(self):
        result = MODULE.lint(
            "PACKAGE_STATE=BLOCKED\n"
            "CLAIM: Production deployment requires unavailable authority.\n"
            "EVIDENCE: authority check confirms access is unavailable.\n"
            "NEXT_ACTION: Resume deployment when authorized access becomes available.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")

    def test_blocked_with_unblock_condition_passes(self):
        result = MODULE.lint(
            "PACKAGE_STATE=BLOCKED\n"
            "CLAIM: Production deployment requires unavailable authority.\n"
            "EVIDENCE: authority check confirms access is unavailable.\n"
            "UNBLOCK_CONDITION: Authorized production access becomes available.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")


    def test_verified_finish_requires_closure_contract(self):
        result = MODULE.lint(
            "PACKAGE_STATE=PASS\n"
            "CLAIM: Verified Finish is complete.\n"
            "EVIDENCE: implementation tests passed and receipt exists.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L17" for f in result["findings"])
        )

    def test_verified_finish_with_closure_contract_passes(self):
        result = MODULE.lint(
            "VERIFIED_FINISH_STATE=PASS\n"
            "CLAIM: Verified Finish is complete.\n"
            "EVIDENCE: DoneCheck PASS; required field acceptance PASS.\n"
            "CLOSURE_CONTRACT: Active task closure criteria are resolved and satisfied.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")

    def test_verified_finish_with_closure_criteria_passes(self):
        result = MODULE.lint(
            "PACKAGE_STATE=PASS\n"
            "CLAIM: Verified Finish is ready.\n"
            "EVIDENCE: required acceptance evidence is present.\n"
            "CLOSURE_CRITERIA: Required task criteria are resolved and satisfied.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")

    def test_scoped_task_pass_does_not_require_global_verified_finish(self):
        result = MODULE.lint(
            "TASK_ACCEPTANCE_STATE=PASS\n"
            "CLAIM: Runtime acceptance is complete.\n"
            "EVIDENCE: runtime receipt is present.\n"
            "CANONICAL_RECORD_STATE=HOLD\n"
            "NEXT_ACTION: Complete bounded canonical record.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")
        self.assertFalse(
            any(f["rule"] == "L17" for f in result["findings"])
        )

    def test_verified_finish_discussion_is_not_closure_assertion(self):
        result = MODULE.lint(
            "STATE — Verified Finish requirements are documented in the active contract.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")
        self.assertFalse(
            any(f["rule"] == "L17" for f in result["findings"])
        )


    def test_multiple_bare_judgments_require_scope(self):
        result = MODULE.lint(
            "STATE=PASS\n"
            "CLAIM: Decision separation is complete.\n"
            "EVIDENCE: canonical contract test receipt is present.\n"
            "STATE=HOLD\n"
            "NEXT_ACTION: Complete package evidence.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(f["rule"] == "L15" for f in result["findings"])
        )

    def test_scoped_judgments_pass(self):
        result = MODULE.lint(
            "DECISION_STATE=PASS\n"
            "CLAIM: Package separation is established.\n"
            "EVIDENCE: canonical decision receipt is present.\n"
            "PACKAGE_STATE=HOLD\n"
            "NEXT_ACTION: Complete package evidence.\n",
            strict=True,
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


    def test_l18_ordered_sequence_passes(self):
        result = MODULE.lint(
            "SUZGEC_SEQUENCE=ENFORCED\n"
            "PRESERVED_VALUE: canonical authority\n"
            "NECESSARY_DIFFERENCE: bounded binding\n"
            "REUSE_EXECUTION: existing package guard\n"
            "EVIDENCE: focused test receipt is present.\n"
            "CLOSURE: active criteria satisfied\n"
            "PACKAGE_STATE=PASS\n"
            "CLAIM: Runtime binding is verified by tests.\n"
            "NEXT_ACTION: Advance canonical execution.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "PASS")
        self.assertFalse(any(
            f["rule"] == "L18"
            for f in result["findings"]
        ))

    def test_l18_missing_field_holds(self):
        result = MODULE.lint(
            "SUZGEC_SEQUENCE=ENFORCED\n"
            "PRESERVED_VALUE: canonical authority\n"
            "NECESSARY_DIFFERENCE: bounded binding\n"
            "EVIDENCE: focused test receipt is present.\n"
            "CLOSURE: criteria pending\n"
            "PACKAGE_STATE=HOLD\n"
            "CLAIM: Sequence requires completion.\n"
            "NEXT_ACTION: Restore reuse execution field.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(
            f["rule"] == "L18"
            for f in result["findings"]
        ))

    def test_l18_wrong_order_holds(self):
        result = MODULE.lint(
            "SUZGEC_SEQUENCE=ENFORCED\n"
            "NECESSARY_DIFFERENCE: bounded binding\n"
            "PRESERVED_VALUE: canonical authority\n"
            "REUSE_EXECUTION: existing package guard\n"
            "EVIDENCE: focused test receipt is present.\n"
            "CLOSURE: criteria pending\n"
            "PACKAGE_STATE=HOLD\n"
            "CLAIM: Sequence order requires reconciliation.\n"
            "NEXT_ACTION: Restore canonical ordering.\n",
            strict=True,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(any(
            f["rule"] == "L18"
            for f in result["findings"]
        ))


if __name__ == "__main__":
    unittest.main()
