"""ENGURU Süzgeç v2.4: finiş hükmü / DUR kararının statik karşıt sözleşme testi.

Bu testler gerçek OSi runtime, issuer grant veya Human Threshold üretmez.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json"
STAGES = ["Hakikati gör", "Değeri koru", "Eksikleri ve ihtiyaçları tespit et",
          "Gerekli farkı üret", "Eksikleri tamamla, ihtiyaçları karşıla",
          "Kanıtla", "Bir sonraki ihtiyaçları belirle", "İlerlet"]

class FinishVerdictStopContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(PATH.read_text(encoding="utf-8"))
        cls.rule = cls.contract["finishVerdictStop"]

    def test_eight_stages_locked(self):
        self.assertEqual(self.contract["eightStages"], STAGES)

    def test_existing_four_gates_preserved(self):
        self.assertEqual(self.contract["existingFinishGates"], ["T01","T02","T03","T04"])
        self.assertFalse(self.rule["noNinthStage"] is False)
        self.assertTrue(self.rule["noNewCore"])
        self.assertTrue(self.rule["noNewFinishGate"])

    def test_stage_binding_is_existing_only(self):
        self.assertEqual(set(self.rule["appliedWithinExistingStages"]), {"03","04","06","07","08"})

    def test_before_work_has_fixed_scope_and_stop(self):
        required = set(self.rule["requiredBeforeExecution"])
        self.assertTrue({"fixed_goal_and_scope_id","work_items_and_gate_ids",
                         "final_acceptance_thresholds","human_threshold_and_stop_boundary"} <= required)

    def test_all_seven_finish_predicates_required(self):
        required = self.rule["allRequiredForBittiDur"]
        self.assertEqual(len(required), 7)
        self.assertEqual(len(set(required)), len(required))
        self.assertIn("native_progress_verified_finish", required)
        self.assertIn("authenticated_human_threshold_accepted", required)

    def test_missing_proof_mandates_safe_stop(self):
        self.assertTrue(self.rule["outcomes"]["missingEvidenceOrAuthority"].startswith("HOLD_GUVENLI_DUR"))
        self.assertIn("BLOCKER", self.rule["outcomes"]["missingEvidenceOrAuthority"])

    def test_only_all_verified_can_finish(self):
        self.assertTrue(self.rule["outcomes"]["allRealEvidenceAndAuthorityVerified"].startswith("BITTI_DUR"))

    def test_scope_expansion_human_and_versioned(self):
        self.assertEqual(self.rule["scopeChange"], "ONLY_EXPLICIT_HUMAN_APPROVED_VERSIONED_CHANGE")
        self.assertIn("SONRAKI_IS_VEYA_SURUM", self.rule["outcomes"]["newNeedOutsideScope"])

    def test_simulation_does_not_grant_authority(self):
        self.assertTrue(self.rule["simulatedTestsNotOfficialPass"])
        self.assertTrue(self.rule["documentsNotIssuerGrant"])

    def test_protected_project_status_stays_hold(self):
        self.assertEqual(self.contract["canonicalInstalledVersion"], "2.3")
        self.assertEqual(self.contract["verifiedFinish"], "HOLD")
        self.assertEqual(self.contract["p01"], "SUSPENDED")
        self.assertEqual(self.rule["verifiedFinish"], "HOLD")

    def test_p06_and_human_separate(self):
        protected = self.rule["preserveExistingAuthorities"]
        self.assertIn("P06_SEPARATE_SECURITY_AUTHORITY", protected)
        self.assertIn("HUMAN_THRESHOLD_HUMAN_ONLY", protected)

    def test_existing_runtime_bindings_reused(self):
        self.assertIn("EXISTING_PRE_SEND_POSTCHECK_DONECHECK_AND_PROGRESS",self.rule["enforcement"])
        self.assertIn("FIELD_BINDING_PENDING",self.rule["enforcement"])

if __name__ == "__main__":
    unittest.main()
