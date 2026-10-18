"""PLive contract-change counter and finish-law structural tests.
These tests are static; they never issue producer grants or accept live P02 work.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "governance/plive/ENGURU_PLIVE_PROGRESS_FINISH_CONTRACT_V1.json"
METHOD = ROOT / "governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json"

class PLiveProgressFinishContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(POLICY.read_text(encoding="utf-8"))
        cls.m = json.loads(METHOD.read_text(encoding="utf-8"))

    def test_single_native_progress_authority(self):
        self.assertEqual(self.p["visibility"]["officialNumerator"], "EXISTING_NATIVE_PROGRESS_CORE_COUNTED_PASS")
        self.assertTrue(self.p["limits"]["noNewCounter"] and self.p["limits"]["noNewCore"])

    def test_every_contract_mutation_triggers_check(self):
        self.assertEqual(set(self.p["register"]["trigger"]), {"CREATE", "MODIFY", "RENAME", "DELETE"})
        self.assertIn("ALL_WORK_CONTRACTS", self.p["register"]["scope"])

    def test_registration_validation_preserves_current_work_contract(self):
        checks = self.p["register"]["validate"]
        self.assertIn("COUNTER_POLICY_AUTO_FROM_WORK_CONTRACT", checks)
        self.assertIn("VALID_REGISTERED_BINDING", checks)
        self.assertIn("NO_PROJECT_NAME_COLLISION", checks)

    def test_before_and_after_existing_native_counter(self):
        self.assertIn("NATIVE_VERIFIED_PROGRESS", self.p["register"]["before"])
        self.assertIn("NATIVE_VERIFY", self.p["register"]["after"])

    def test_all_required_visibility_dimensions(self):
        fields = set(self.p["visibility"]["required"])
        self.assertTrue({"DECLARED_PASS","EVIDENCED_PASS","COUNTED_PASS","UNVERIFIED_PASS","ITEMS_REMAINING","OFFICIAL_REMAINING_PERCENT","PACKAGE_DONECHECK_COUNT","BLOCKERS_AND_OWNER"} <= fields)

    def test_engineering_activity_not_promoted_to_pass(self):
        self.assertIn("NEVER_AUTOMATIC_COUNTED_PASS", self.p["visibility"]["engineeringEvidence"])
        self.assertTrue(self.p["limits"]["noUnverifiedPassPromotion"])

    def test_item_done_does_not_block_preapproved_next(self):
        self.assertIn("AUTHORIZED_PREAPPROVED_NEXT_ITEM_MAY_CONTINUE", self.p["finish"]["onAcceptedItem"])
        self.assertTrue(self.p["finish"]["noRepeatedApprovalWithinCurrentGrant"])

    def test_package_done_does_not_block_preapproved_next(self):
        self.assertIn("AUTHORIZED_PREAPPROVED_NEXT_PACKAGE_MAY_CONTINUE", self.p["finish"]["onAcceptedPackage"])

    def test_finished_project_stops(self):
        self.assertIn("BITTI_DUR", self.p["finish"]["onVerifiedProjectFinish"])
        self.assertIn("NEW_HUMAN_APPROVED", self.p["finish"]["nextOutsideScope"])

    def test_protected_authorities_held(self):
        self.assertEqual(self.p["limits"]["p01"], "SUSPENDED_PRESERVED")
        self.assertEqual(self.p["limits"]["p06"], "SEPARATE_SECURITY_AUTHORITY")
        self.assertTrue(self.p["limits"]["noAutoGrant"])
        self.assertEqual(self.p["limits"]["verifiedFinish"], "HOLD")

    def test_suzgec_v24_rule_matches_plive_policy(self):
        n = self.m["finishVerdictStop"]["passNextFlow"]
        g = self.m["workProgressClosure"]["pliveCounterActivationRule"]
        self.assertTrue(n["noRepeatedHumanCommandWithinValidApprovedScope"])
        self.assertIn("EVERY_NEW_CHANGED", g["trigger"])
        self.assertEqual(g["progressAuthority"], "ONLY_NATIVE_COUNTED_PASS_DIVIDED_BY_WORKLIST_TOTAL")

    def test_static_contract_never_claims_field_acceptance(self):
        self.assertIn("HOLD", self.p["state"])
        self.assertIn("PENDING_OSi_FIELD", self.p["limits"]["runtimeEnforcement"])
        self.assertEqual(self.m["canonicalInstalledVersion"], "2.3")
        self.assertEqual(self.m["verifiedFinish"], "HOLD")

if __name__ == "__main__":
    unittest.main()
