"""Adversarial 100-only acceptance policy checks. Real field cannot self-pass."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import unittest

import zulfikar_v131_universal_100_gate as policy
import zulfikar_v131_operational_bridge as bridge

HERE=Path(__file__).resolve().parent


class UmbrellaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p,_=bridge.source_read(bridge.ROOT,policy.POLICY_PATH)
        cls.s,_=bridge.source_read(bridge.ROOT,policy.SCORECARD_PATH)
        cls.goal,_=bridge.source_read(bridge.ROOT,policy.GOAL_PATH)
        cls.agents=bridge.read_no_symlink(bridge.ROOT,"AGENTS.md",100000).decode("utf-8")

    def decide(self,stage,value,evidence="EXACT_HEAD_CI"):
        return policy.classify(stage,value,evidence)

    def test_policy_source_is_all_ten_controls(self):
        c=policy.controls(self.p,self.s,self.agents,self.goal)
        self.assertEqual(len(c),10,c)
        self.assertTrue(all(c.values()),c)

    def test_every_score_1_through_99_is_diagnostic_only(self):
        for n in range(1,100):
            with self.subTest(n=n):
                result=self.decide("PREPARATION",n)
                self.assertEqual(result["decision"],"CONTINUE_IMPROVEMENT")
                self.assertIsNone(result["acceptedScore"])

    def test_zero_does_not_pass(self):
        self.assertEqual(self.decide("PREPARATION",0)["decision"],"CONTINUE_IMPROVEMENT")

    def test_91_no_longer_claimed_as_final_hold_score(self):
        self.assertEqual(self.s["historicalDiagnosticBeforeCurrentPolicy"]["score"],91)
        self.assertEqual(self.s["overallOperationalVerdict"],"CONTINUE_REAL_EVIDENCE_NOT_ACCEPTED")
        self.assertIsNone(self.s["acceptedOperationalScore"])

    def test_100_without_evidence_is_not_pass(self):
        self.assertIsNone(self.decide("PREPARATION",100,"NONE")["acceptedScore"])

    def test_100_simulation_is_not_real_finish(self):
        for stage in policy.PHASE_IDS:
            self.assertEqual(self.decide(stage,100,"SIMULATION")["decision"],"AWAIT_VERIFIED_EVIDENCE")

    def test_100_self_reported_is_not_authority(self):
        self.assertEqual(self.decide("PRODUCT_FINISH",100,"SELF_REPORTED")["decision"],"AWAIT_VERIFIED_EVIDENCE")

    def test_100_source_ci_never_unlocks_real_execution(self):
        self.assertEqual(self.decide("REAL_EXECUTION",100)["decision"],"AWAIT_AUTHORIZED_FIELD_AND_DONECHECK")
        self.assertIsNone(self.decide("REAL_EXECUTION",100)["acceptedScore"])

    def test_100_source_ci_never_unlocks_product_verified_finish(self):
        self.assertEqual(self.decide("PRODUCT_FINISH",100)["decision"],"AWAIT_AUTHORIZED_FIELD_AND_DONECHECK")
        self.assertIsNone(self.decide("PRODUCT_FINISH",100)["acceptedScore"])

    def test_100_preparation_is_candidate_until_external_ci(self):
        self.assertEqual(self.decide("PREPARATION",100)["decision"],"STAGE_100_CANDIDATE_EXACT_HEAD_CHECK_REQUIRED")
        self.assertIsNone(self.decide("PREPARATION",100)["acceptedScore"])

    def test_100_goal_architecture_is_scoped_candidate(self):
        self.assertEqual(self.decide("GOAL_ARCHITECTURE",100)["decision"],"STAGE_100_CANDIDATE_EXACT_HEAD_CHECK_REQUIRED")

    def test_boolean_true_is_not_score_1_or_100(self):
        self.assertEqual(self.decide("PREPARATION",True)["decision"],"INVALID_DIAGNOSTIC")

    def test_string100_is_not_verified(self):
        self.assertEqual(self.decide("PREPARATION","100")["decision"],"INVALID_DIAGNOSTIC")

    def test_101_and_negative_rejected(self):
        for n in (-100,-1,101,1000):
            self.assertEqual(self.decide("PREPARATION",n)["decision"],"INVALID_DIAGNOSTIC")

    def test_unknown_stage_rejected(self):
        self.assertEqual(self.decide("NOT_A_STAGE",100)["decision"],"INVALID_STAGE")

    def test_false_threshold_rejected(self):
        p=copy.deepcopy(self.p)
        p["acceptanceUniverse"]["passThreshold"]=91
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U04_ONLY_100_ACCEPTED"])

    def test_fake_diagnostic_authority_rejected(self):
        p=copy.deepcopy(self.p)
        p["acceptanceUniverse"]["diagnosticRange"]["authority"]="FINAL_PASS"
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U05_1_TO_99_DIAGNOSTIC_ONLY"])

    def test_six_stages_no_extra_stages(self):
        p=copy.deepcopy(self.p)
        p["eightStages"].append("NEW_STAGE")
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U02_EIGHT_STAGES_UNCHANGED"])

    def test_loop_cannot_drop_repair(self):
        p=copy.deepcopy(self.p)
        p["loop"].remove("REPAIR")
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U03_ITERATIVE_LOOP_LOCKED"])

    def test_self_reported_pass_rule_cannot_expand(self):
        p=copy.deepcopy(self.p)
        p["stageRoles"]["PRODUCT_FINISH"]["auth"]="SELF_REPORTED"
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U09_OWNER_DONECHECK_PRESERVED"])

    def test_historical91_is_never_auto_promoted_to100(self):
        s=copy.deepcopy(self.s)
        s["acceptedOperationalScore"]=100
        self.assertFalse(policy.controls(self.p,s,self.agents,self.goal)["U08_CANONICAL_91_IS_HISTORY"])

    def test_historical_status_cannot_be_called_current_pass(self):
        s=copy.deepcopy(self.s)
        s["overallOperationalVerdict"]="PASS"
        self.assertFalse(policy.controls(self.p,s,self.agents,self.goal)["U08_CANONICAL_91_IS_HISTORY"])

    def test_scope_must_include_global_agents(self):
        self.assertFalse(policy.controls(self.p,self.s,"SOURCE WITHOUT POLICY",self.goal)["U10_GLOBAL_START_AND_SAFE_END"])

    def test_premature_product_stop_rejected(self):
        p=copy.deepcopy(self.p)
        p["completionSequence"][-1]="PASS_FROM_PREPARATION"
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U10_GLOBAL_START_AND_SAFE_END"])

    def test_existing_goal_pointer_is_required(self):
        g=copy.deepcopy(self.goal)
        g["universalUmbrella"]["policyRef"]="NOT_CANONICAL"
        self.assertFalse(policy.controls(self.p,self.s,self.agents,g)["U01_USER_GOAL_LOCKED"])

    def test_working_loop_must_stop_at_verified_100(self):
        p=copy.deepcopy(self.p)
        p["loopArchitecture"]["stopAtVerified100"]=False
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U03_ITERATIVE_LOOP_LOCKED"])

    def test_working_loop_cannot_skip_real_test(self):
        p=copy.deepcopy(self.p)
        p["loopArchitecture"]["orderedPhases"].remove("REAL_TEST")
        self.assertFalse(policy.controls(p,self.s,self.agents,self.goal)["U03_ITERATIVE_LOOP_LOCKED"])

    def test_full_policy_cli_source_bound(self):
        proc=subprocess.run([sys.executable,"-B",str(HERE/"zulfikar_v131_universal_100_gate.py")],
                             capture_output=True,text=True,cwd=HERE,timeout=30)
        self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout[-800:])
        payload=json.loads(proc.stdout)
        self.assertEqual(payload["codePolicyDiagnostic"],100)
        self.assertEqual(payload["policyDecision"],"GITHUB_POLICY_100_CANDIDATE_EXACT_HEAD_CI_REQUIRED")
        self.assertIsNone(payload["operationalAcceptedScore"])
        self.assertEqual(payload["legacy91"],"HISTORICAL_DIAGNOSTIC_ONLY")
        self.assertEqual(payload["productVerifiedFinish"],"AWAIT_AUTHORIZED_EVIDENCE")


if __name__=="__main__":
    unittest.main(verbosity=2)
