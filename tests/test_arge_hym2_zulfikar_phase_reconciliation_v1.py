"""HYM2 Zulfikar stall diagnosis: independent source and fake-PASS challenges."""
import copy
import unittest
from tools.arge_hym2_zulfikar_phase_reconciliation_v1 import (
    BLOCKS,TASKS,ROOT,score,checks,simulations,snapshot,run,
    EXPECTED_GH_STATES,
)


class PhaseBoundaryEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One actual pinned upstream read for all tests; the backend also
        # checks source blob identity before loading the original Zulfikar.
        cls.orig=snapshot()

    def test_original_goal_40_tasks_six_blocks_and_provenance(self):
        self.assertEqual(len(TASKS),40)
        self.assertEqual([len(v) for v in BLOCKS],[9,9,7,7,4,4])
        self.assertEqual(self.orig["cases"]["baseline"]["rows"],234)
        self.assertEqual(self.orig["matrix"]["official_pass"],"0/9")

    def test_goal_design_theory_three_independent_full_denominators(self):
        grades=score(self.orig)["grades"]
        self.assertEqual(set(grades),{"GOAL","DESIGN","THEORY"})
        self.assertTrue(all(v["score"]==100 and v["passed"]==v["total"]==10
                            and not v["failedIds"] for v in grades.values()))

    def test_three_distinct_simulation_families_catch_nine_tamper_cases(self):
        v=simulations(self.orig)
        self.assertEqual(v["state"],"PASS_THREE_DISTINCT_SIMULATION_FAMILIES")
        self.assertEqual(v["passed"],v["total"])
        self.assertEqual(v["total"],9)
        self.assertEqual(v["families"],{"SIM1_SOURCE":3,"SIM2_AUTHORITY":3,
                                         "SIM3_METAMORPHIC":3})
        self.assertTrue(all(x["detectedFailedIds"] and
                            x["result"]=="PASS_EXPECTED_HOLD"
                            for x in v["observations"].values()))

    def test_no_original_legacy_50_promotion(self):
        g=self.orig["gate"]
        self.assertEqual(g["score_accounting"]["github_preparation_last_authoritative_record"],"50/100")
        self.assertEqual([x["management_state"] for x in
                          g["proposed_readiness_trace_gates"]],list(EXPECTED_GH_STATES))
        self.assertEqual(self.orig["provenance"]["acceptance"],"HOLD")

    def test_forced_release_or_imaginary_extra_human_fails_design(self):
        for prop,replacement in (
            ("owner_authority","TWO_UNSUPPORTED_OWNERS"),
            ("public_review_contract","UPLOAD_PRIVATE_FACTORY_SOURCES"),
        ):
            with self.subTest(prop=prop):
                d=copy.deepcopy({k:v for k,v in self.orig.items() if k!="zulfi_mod"})
                d["provenance"]["a04_canonical_scope_boundary"][prop]=replacement
                self.assertLess(score(d)["grades"]["DESIGN"]["score"],100)

    def test_fake_gh06_grant_cannot_be_accepted_as_preparation(self):
        d=copy.deepcopy({k:v for k,v in self.orig.items() if k!="zulfi_mod"})
        d["gate"]["proposed_readiness_trace_gates"][5]["management_state"]="GITHUB_SOURCE_OBSERVED"
        v=score(d)["grades"]
        self.assertLess(v["DESIGN"]["score"],100)
        self.assertLess(v["THEORY"]["score"],100)

    def test_zulfikar_official_signer_is_still_false(self):
        mod=self.orig["zulfi_mod"]
        verdict=mod.assess({})
        self.assertEqual(verdict["official_verdict"],"NOT_EVALUATED")
        self.assertFalse(verdict["eligible_for_automatic_signature"])
        self.assertEqual(self.orig["zulfi"]["scope"],"DESIGN_ONLY / LOCAL_OFFLINE_VALIDATOR")

    def test_user_reported_scores_cannot_influence_evaluator(self):
        d=copy.deepcopy({k:v for k,v in self.orig.items() if k!="zulfi_mod"})
        base=score(d)
        d["claimed_scores"]={"GOAL":999,"DESIGN":999,"THEORY":999,"GITHUB":999}
        self.assertEqual(score(d),base)

    def test_real_pinned_oracles_issue_scoped_ready_not_official_pass(self):
        x=run()
        self.assertEqual(x["state"],"PASS_SCOPED_GOAL_DESIGN_THEORY_EVIDENCE_ONLY")
        self.assertEqual(x["legacy_github_preparation"],"50/100_HOLD")
        self.assertEqual(x["official_progress"],"0/40")
        self.assertEqual(x["field"],"0/100")
        self.assertEqual(x["verified_finish"],"HOLD")
        self.assertEqual(x["github_actual_ci"],"REQUIRES_EXACT_HEAD_HOST_CONFIRMATION")


if __name__=="__main__":
    unittest.main()
