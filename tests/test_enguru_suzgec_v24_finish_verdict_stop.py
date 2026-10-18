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


class NestedStopBoundaryTests(unittest.TestCase):
    """Contract-only tests; authentic producer and OSi runtime remain HOLD."""

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(PATH.read_text(encoding="utf-8"))
        cls.n = cls.c["finishVerdictStop"]["nestedAcceptanceStop"]

    def test_inner_work_finishes_at_its_authorized_acceptance(self):
        self.assertIn("ITEM_FINISHED_STOP_ONLY", self.n["itemRule"])
        self.assertIn("PACKAGE_POLICY", self.n["itemRule"])

    def test_package_finishes_at_existing_donecheck(self):
        self.assertIn("ALL_REGISTERED_ITEMS_AUTHORIZED_ACCEPTED", self.n["packageRule"])
        self.assertIn("PACKAGE_DONECHECK_PASS", self.n["packageRule"])

    def test_project_finishes_only_after_all_original_requirements(self):
        p = self.n["projectRule"]
        for term in ("12_OF_12", "4_OF_4", "SEVEN_EXISTING_GATES", "HUMAN_THRESHOLD", "VERIFIED_FINISH"):
            self.assertIn(term, p)

    def test_derived_finish_does_not_add_a_gate(self):
        self.assertEqual(self.c["existingFinishGates"], ["T01", "T02", "T03", "T04"])
        self.assertTrue(self.c["finishVerdictStop"]["noNinthStage"])
        self.assertIn("NO_NEW_GATE", self.n["finalGate"])

    def test_stop_is_terminal_for_accepted_scope(self):
        self.assertIn("STOP_AT_ACCEPTED_SCOPE", self.n["stopEnforcement"])
        self.assertIn("NEW_HUMAN_APPROVED_WORK_OR_VERSION", self.n["stopEnforcement"])

    def test_missing_evidence_keeps_hold_without_fake_percent(self):
        self.assertIn("HOLD_GUVENLI_DUR", self.n["holdEnforcement"])
        self.assertIn("KEEP_LAST_NATIVE_VERIFIED_PERCENT", self.n["holdEnforcement"])
        self.assertIn("COUNTED_PASS", self.n["measureOfficial"])
        self.assertIn("NOT_PROJECT_PERCENT", self.n["measureGateClosure"])

    def test_self_approval_and_raw_pass_are_forbidden(self):
        self.assertTrue(self.n["noSelfApproval"])
        self.assertTrue(self.n["rawPassTextDoesNotGrantAuthority"])
        self.assertTrue(self.n["preserveP01P06AndHumanThreshold"])

    def test_candidate_does_not_claim_runtime_pass(self):
        self.assertIn("OSi_RUNTIME_BINDING_HOLD", self.n["state"])
        self.assertIn("HOLD_UNTIL_NATIVE_VERIFIED_BINDING", self.n["officialRuntimeEnforcement"])
        self.assertEqual(self.c["canonicalInstalledVersion"], "2.3")
        self.assertEqual(self.c["verifiedFinish"], "HOLD")


class NextExecutablePackageRuleTests(unittest.TestCase):
    """Candidate-only v2.4 wording and bounded next-action contract."""

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(PATH.read_text(encoding="utf-8"))
        cls.r = cls.c["finishVerdictStop"]["nextExecutableUnifiedPackage"]

    def test_preferred_integrated_next_package_phrase(self):
        self.assertEqual(self.r["preferredExpression"], "Bir sonraki yapılabilir adımları içeren birleşik ve bütünleşik paket.")

    def test_current_truth_and_evidence_are_required(self):
        self.assertIn("CURRENT_TRUTH", self.r["planningRule"])
        self.assertIn("NATIVE_EVIDENCE_AND_PROGRESS", self.r["planningRule"])
        self.assertIn("CONCRETE_EXECUTABLE_NEXT_ACTIONS_IN_DEPENDENCY_ORDER", self.r["acceptancePerPackage"])

    def test_positive_language_avoids_retired_phrase(self):
        self.assertIn("POSITIVE_PRESERVATION_AND_ACTION_LANGUAGE", self.r["wordingRule"])
        self.assertIn("AVOID_LEGACY_AZ_PAKET_SLOGAN", self.r["wordingRule"])

    def test_preapproved_next_flows_but_project_stops(self):
        self.assertIn("PREAPPROVED_NEXT_ITEM_FLOWS", self.r["transitionRule"])
        self.assertIn("BITTI_DUR", self.r["transitionRule"])

    def test_existing_eight_stage_and_no_new_gate(self):
        self.assertEqual(len(self.c["eightStages"]), 8)
        self.assertTrue(self.r["noNewCore"] and self.r["noNinthStage"] and self.r["noNewGate"])
        self.assertIn("PENDING_OSi_NATIVE", self.r["canonicalBinding"])


if __name__ == "__main__":
    unittest.main()
