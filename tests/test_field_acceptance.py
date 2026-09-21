import json
from pathlib import Path
import unittest

from shared_ai.field_acceptance import (
    FINISHED_ABILITY_STAGES,
    FieldStageEvidence,
    FinishedAbilityGate,
    GovernedToolGapProposal,
    HumanInterventionReconciliationGate,
    SpecialistSpawnGuard,
)


FIXTURE = Path(__file__).resolve().parents[1] / "evidence" / "mac-engineer" / "PACKAGE4_REAL_FIELD_SCENARIO_PACKAGE3.json"


class SpecialistSpawnGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = SpecialistSpawnGuard()

    def assess(self, **overrides):
        data = dict(
            reason="CAPABILITY_GAP",
            need_evidence=("capability:vision=UNSUPPORTED",),
            scope=("render-review",),
            max_steps=4,
            parent_capabilities=("files", "vision", "tests"),
            specialist_capabilities=("vision", "files"),
            parent_human_thresholds=("merge", "publish"),
            specialist_human_thresholds=("merge", "publish"),
        )
        data.update(overrides)
        return self.guard.assess(**data)

    def test_verified_bounded_specialist_passes_without_authority_growth(self):
        result = self.assess()
        self.assertEqual(result.state, "PASS")
        self.assertIn("authority:inherited_without_expansion", result.evidence)

    def test_unverified_specialist_need_holds(self):
        result = self.assess(reason="CONVENIENCE")
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "specialist_need_not_verified")

    def test_step_budget_is_bounded(self):
        self.assertEqual(self.assess(max_steps=13).state, "HOLD")

    def test_extra_specialist_capability_is_privilege_escalation(self):
        result = self.assess(specialist_capabilities=("vision", "shell"))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "specialist_privilege_escalation")

    def test_specialist_cannot_change_human_thresholds(self):
        result = self.assess(specialist_human_thresholds=("merge",))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "specialist_human_threshold_drift")


class GovernedToolGapProposalTests(unittest.TestCase):
    def setUp(self):
        self.guard = GovernedToolGapProposal()

    def assess(self, **overrides):
        data = dict(
            tool_gap_evidence=("gap:browser-video-capture",),
            proposal="Evaluate one zero-cost browser capture adapter.",
            authority_review="PASS",
            security_review="PASS",
            cost_review="PASS",
            bounded_test_evidence=("sandbox:test-1",),
            decision="ACCEPT",
            autonomous_install_requested=False,
        )
        data.update(overrides)
        return self.guard.assess(**data)

    def test_accept_is_proposal_only_and_does_not_grant_install_authority(self):
        result = self.assess()
        self.assertEqual(result.state, "PASS")
        self.assertIn("installation_authority:NOT_GRANTED", result.evidence)

    def test_missing_review_holds(self):
        result = self.assess(security_review="HOLD")
        self.assertEqual(result.state, "HOLD")
        self.assertIn("security", result.reason)

    def test_bounded_test_is_required(self):
        result = self.assess(bounded_test_evidence=tuple())
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "tool_gap_bounded_test_required")

    def test_tool_gap_never_self_grants_install_authority(self):
        result = self.assess(autonomous_install_requested=True)
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "tool_gap_does_not_grant_install_authority")

    def test_reject_is_a_valid_reviewed_outcome(self):
        result = self.assess(decision="REJECT")
        self.assertEqual(result.state, "PASS")
        self.assertIn("decision:REJECT", result.evidence)


class HumanInterventionReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.gate = HumanInterventionReconciliationGate()

    def assess(self, **overrides):
        data = dict(
            human_intervention_occurred=True,
            checkpoint_revision=4,
            current_revision=5,
            reread_evidence={
                "repo": "sha:new",
                "runtime": "runtime:healthy",
                "artifact": "artifact:digest",
                "state": "task:revision-5",
            },
            differences=("repo_sha_changed",),
            reconciled=True,
            new_verified_state="REVISION_5_RECONCILED",
            reconciliation_evidence=("reconcile:diff-reviewed",),
        )
        data.update(overrides)
        return self.gate.assess(**data)

    def test_human_intervention_establishes_new_verified_state_before_resume(self):
        result = self.assess()
        self.assertEqual(result.state, "PASS")
        self.assertTrue(any(item.startswith("NEW_VERIFIED_STATE:") for item in result.evidence))

    def test_stale_revision_holds_after_human_intervention(self):
        result = self.assess(current_revision=4)
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "post_human_revision_not_advanced")

    def test_all_real_surfaces_are_reread(self):
        evidence = {
            "repo": "sha:new",
            "runtime": "runtime:healthy",
            "artifact": "",
            "state": "task:revision-5",
        }
        result = self.assess(reread_evidence=evidence)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("artifact", result.reason)

    def test_detected_difference_must_be_reconciled(self):
        result = self.assess(reconciled=False)
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "post_human_differences_unreconciled")

    def test_no_intervention_needs_no_reconciliation(self):
        result = self.assess(human_intervention_occurred=False)
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.reason, "human_reconciliation_not_required")


class FinishedAbilityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = FinishedAbilityGate()
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.payload = payload
        self.stages = tuple(
            FieldStageEvidence(
                stage=item["stage"],
                state=item["state"],
                evidence=tuple(item["evidence"]),
                real_field=bool(item["real_field"]),
            )
            for item in payload["stages"]
        )

    def test_real_package3_repository_scenario_passes_all_eight_stages(self):
        result = self.gate.assess(
            self.stages,
            recovery_exercised=self.payload["recoveryExercised"],
            donecheck_pass=self.payload["donecheckPass"],
            final_evidence=tuple(self.payload["finalEvidence"]),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.completed_stages, FINISHED_ABILITY_STAGES)
        self.assertEqual(result.reason, "finished_ability_real_field_pass")

    def test_missing_stage_holds(self):
        result = self.gate.assess(
            self.stages[:-1],
            recovery_exercised=True,
            donecheck_pass=True,
            final_evidence=("finish:evidence",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "finished_ability_stage_set_incomplete")

    def test_synthetic_stage_cannot_manufacture_field_pass(self):
        synthetic = list(self.stages)
        target = synthetic[0]
        synthetic[0] = FieldStageEvidence(
            target.stage,
            target.state,
            target.evidence,
            real_field=False,
        )
        result = self.gate.assess(
            synthetic,
            recovery_exercised=True,
            donecheck_pass=True,
            final_evidence=("finish:evidence",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "synthetic_field_evidence:UNDERSTAND")

    def test_recovery_must_be_exercised_in_real_field(self):
        result = self.gate.assess(
            self.stages,
            recovery_exercised=False,
            donecheck_pass=True,
            final_evidence=("finish:evidence",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "recovery_field_proof_required")

    def test_mandatory_donecheck_is_required(self):
        result = self.gate.assess(
            self.stages,
            recovery_exercised=True,
            donecheck_pass=False,
            final_evidence=("finish:evidence",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "mandatory_donecheck_required")

    def test_critical_field_failure_cannot_be_averaged_away(self):
        result = self.gate.assess(
            self.stages,
            recovery_exercised=True,
            donecheck_pass=True,
            final_evidence=("finish:evidence",),
            critical_failures=("irreversible_action_without_authority",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "critical_field_failure")


if __name__ == "__main__":
    unittest.main()
