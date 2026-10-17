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


class WorkProgressClosureTests(unittest.TestCase):
    """Static acceptance clauses only; field issuer/grant/runtime still HOLD."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(PATH.read_text(encoding="utf-8"))
        cls.c = cls.document["workProgressClosure"]

    def test_unchanged_eight_stages_and_finish_gates(self):
        self.assertEqual(self.document["eightStages"], STAGES)
        self.assertEqual(self.document["existingFinishGates"], ["T01", "T02", "T03", "T04"])
        self.assertTrue(all(self.c[k] for k in ("noNewCore", "noNinthStage", "noNewFinishGate")))

    def test_existing_stages_and_execution_reused(self):
        self.assertEqual(set(self.c["boundToExistingStages"]), {"03", "04", "05", "06", "07", "08"})
        self.assertEqual(self.c["reuseExistingAuthorities"]["execution"], "ENGURU_WORK_PROTOCOL_EXISTING")
        self.assertEqual(self.c["reuseExistingAuthorities"]["counter"], "ENGURU_PROGRESS_CORE_EXISTING_ONLY")
        self.assertEqual(self.c["reuseExistingAuthorities"]["projection"], "ENGURU_PLIVE_EXISTING_ONLY")

    def test_universal_scope_with_p02_first_real_field(self):
        self.assertEqual(self.c["scope"], "ALL_VALID_REGISTERED_OSi_WORK_CONTRACTS")
        self.assertEqual(self.c["firstField"], "plive-p02-user-screen")
        self.assertIn("TWO_DISTINCT_REAL_PROJECTS", self.c["requirementForUniversalFieldPass"])

    def test_evidence_scoped_grant_and_donecheck_required(self):
        conditions = set(self.c["acceptancePreconditions"])
        self.assertIn("authenticated_project_item_head_action_scoped_grant_verified", conditions)
        self.assertIn("existing_verifier_and_contract_required_DoneCheck_PASS", conditions)
        self.assertIn("actual_field_evidence_verified_for_exact_item_and_action", conditions)

    def test_atomic_writing_and_replay_prevention(self):
        self.assertIn("ATOMIC", self.c["canonicalCommitRule"])
        self.assertIn("IDEMPOTENT", self.c["canonicalCommitRule"])
        self.assertEqual(self.c["onDuplicateEvent"], "IDEMPOTENT_NO_DOUBLE_CREDIT")
        self.assertIn("ZERO_UNAUTHORIZED", self.c["onConflictingReplayOrDrift"])

    def test_only_native_verified_counted_pass_drives_live_ui(self):
        self.assertIn("EXISTING_WORK_CONTRACT", self.c["progressRule"])
        self.assertIn("EXISTING_NATIVE_PROGRESS_CORE_VERIFIED", self.c["screenRule"])
        self.assertIn("AFTER_RESTART", self.c["continuityRule"])

    def test_blocker_owner_and_pending_acceptance_separated(self):
        self.assertIn("BLOCKER_AND_OWNER", self.c["onBlocked"])
        self.assertIn("PENDING", self.c["onAuthorizedVerifiedChange"])

    def test_no_simulated_promotion_or_p06_bypass(self):
        self.assertTrue(self.c["noSyntheticPromotion"])
        self.assertIn("P06_SEPARATE_AUTHORITY", self.c["reuseExistingAuthorities"]["security"])
        self.assertEqual(self.c["officialAuthority"], "HOLD_UNTIL_REAL_ISSUER_GRANT_VERIFIER_WRITER_AND_FIELD_PROOF")

    def test_method_contract_is_candidate_not_runtime_pass(self):
        self.assertEqual(self.document["canonicalInstalledVersion"], "2.3")
        self.assertEqual(self.c["verifiedFinish"], "HOLD")
        self.assertIn("RUNTIME_BINDING_AND_FIELD_ACCEPTANCE_HOLD", self.c["state"])

if __name__ == "__main__":
    unittest.main()
