"""Adversarial stage order, 3+2 meaningful retries and independent final oracles."""
import copy
import unittest

from tools.enguru_method_three_phase_gate_v1 import review, PHASES, FINAL_FAMILIES


def digest(num):
    return f"{num:064x}"


def plan(rounds=3):
    controls = {p: [p+"1", p+"2", p+"3"] for p in PHASES+FINAL_FAMILIES}
    registry = {"controls": controls, "rounds": {}, "finalFamilies": {}}
    for pi, phase in enumerate(PHASES):
        registry["rounds"][phase] = [
            {"caseId": f"{phase}-r{i+1}", "source": digest(100+pi*20+i),
             "proof": digest(300+pi*20+i), "passed": controls[phase][:
                    (1 if i == 0 else 2 if i == 1 else 3)],
             "oracle": f"primary-{phase}" if i != 2 else f"independent-{phase}"}
            for i in range(rounds)
        ]
    for i, family in enumerate(FINAL_FAMILIES):
        registry["finalFamilies"][family] = {
            "caseId": family, "source": registry["rounds"]["GITHUB"][-1]["source"],
            "proof": digest(900+i), "passed": controls[family],
            "oracle": f"distinct-final-{family}"}
    return registry


def verifier(phase, entry):
    # This is a synthetic test-only source verifier. Actual projects wire their
    # existing real source/CI evaluators, never a self-reported numeric score.
    return {
        "passedIds": entry["passed"],
        "sourceSha256": entry["source"],
        "evidenceSha256": entry["proof"],
        "oracleId": entry["oracle"],
    }


class PolicyTests(unittest.TestCase):
    def test_design_then_theory_then_github_three_rounds(self):
        r = review(plan(), verifier)
        self.assertEqual(r["policyVerdict"], "PASS_THREE_PHASE_POLICY_REQUIRES_EXTERNAL_CI")
        self.assertEqual(r["phaseOrder"], list(PHASES))
        self.assertEqual(r["repairRounds"], dict.fromkeys(PHASES, 3))
        self.assertEqual(r["finalSimulationScores"], dict.fromkeys(FINAL_FAMILIES, 100))
        self.assertEqual(r["GITHUB_PREPARED"], "HOLD_PENDING_EXACT_SOURCE_AND_CI")
        self.assertEqual(r["OSI_FIELD_READY"], "HOLD")
        self.assertEqual(r["HUMAN_AUTHORIZED"], "HOLD")
        self.assertEqual(r["VERIFIED_FINISH"], "HOLD")

    def test_successful_fourth_round_after_observed_improvement(self):
        p = plan()
        p["rounds"]["DESIGN"][2]["passed"] = ["DESIGN1", "DESIGN2"]
        p["rounds"]["DESIGN"].append({
            "caseId": "DESIGN-r4", "source": digest(190), "proof": digest(390),
            "passed": p["controls"]["DESIGN"], "oracle": "independent-4"})
        self.assertEqual(review(p, verifier)["repairRounds"]["DESIGN"], 4)

    def test_successful_fifth_round(self):
        p = plan()
        p["rounds"]["THEORY"][1]["passed"] = ["THEORY1"]
        p["rounds"]["THEORY"][2]["passed"] = ["THEORY1"]
        p["rounds"]["THEORY"].extend([
            {"caseId":"THEORY-r4", "source":digest(190), "proof":digest(400),
             "passed":["THEORY1","THEORY2"], "oracle":"independent-4"},
            {"caseId":"THEORY-r5", "source":digest(191), "proof":digest(401),
             "passed":p["controls"]["THEORY"],"oracle":"independent-5"},
        ])
        self.assertEqual(review(p, verifier)["repairRounds"]["THEORY"], 5)

    def test_no_automatic_100_at_fifth_round(self):
        p = plan()
        p["rounds"]["GITHUB"][2]["passed"] = ["GITHUB1"]
        p["rounds"]["GITHUB"].extend([
            {"caseId":"GITHUB-r4", "source":digest(190), "proof":digest(400),
             "passed":["GITHUB1","GITHUB2"], "oracle":"independent-4"},
            {"caseId":"GITHUB-r5", "source":digest(191), "proof":digest(401),
             "passed":["GITHUB1","GITHUB2"], "oracle":"independent-5"},
        ])
        r = review(p, verifier)
        self.assertEqual(r["policyVerdict"], "HOLD")
        self.assertEqual(r["activePhase"], "GITHUB")
        self.assertEqual(r["GITHUB_PREPARED"], "HOLD")

    def test_forged_numeric_claim_cannot_raise_score(self):
        p = plan()
        p["rounds"]["DESIGN"][2]["passed"] = ["DESIGN1", "DESIGN2"]
        p["rounds"]["DESIGN"][2]["score"] = 100
        p["rounds"]["DESIGN"][2]["GITHUB_PREPARED"] = "PASS"
        self.assertEqual(review(p, verifier)["reason"], "HOLD_PHASE_HAS_OPEN_CONTROLS")

    def test_second_phase_cannot_start_before_first_pass(self):
        p = plan()
        p["rounds"]["DESIGN"][2]["passed"] = ["DESIGN1"]
        r = review(p, verifier)
        self.assertTrue(all(x["phase"] == "DESIGN" for x in r["history"]))
        self.assertEqual(r["activePhase"], "DESIGN")

    def test_missing_three_rounds_holds(self):
        p = plan()
        p["rounds"]["DESIGN"] = p["rounds"]["DESIGN"][:2]
        self.assertEqual(review(p, verifier)["reason"], "HOLD_ROUND_COUNT_3_TO_5")

    def test_sixth_round_rejected(self):
        p = plan()
        p["rounds"]["DESIGN"] *= 2
        self.assertEqual(review(p, verifier)["reason"], "HOLD_ROUND_COUNT_3_TO_5")

    def test_repeat_without_new_evidence_holds(self):
        p = plan()
        p["rounds"]["DESIGN"][1]["source"] = p["rounds"]["DESIGN"][0]["source"]
        p["rounds"]["DESIGN"][1]["proof"] = p["rounds"]["DESIGN"][0]["proof"]
        self.assertEqual(review(p, verifier)["reason"], "HOLD_REPEAT_WITHOUT_NEW_EVIDENCE")

    def test_extra_round_without_closed_gap_holds(self):
        p = plan()
        p["rounds"]["DESIGN"][2]["passed"] = ["DESIGN1", "DESIGN2"]
        p["rounds"]["DESIGN"].append({
            "caseId":"DESIGN-r4", "source":digest(190), "proof":digest(390),
            "passed":["DESIGN1","DESIGN2"], "oracle":"independent-4"})
        self.assertEqual(review(p, verifier)["reason"], "HOLD_EXTRA_ROUND_WITHOUT_CLOSED_GAP")

    def test_third_design_oracle_must_be_distinct(self):
        p = plan()
        p["rounds"]["DESIGN"][2]["oracle"] = p["rounds"]["DESIGN"][0]["oracle"]
        self.assertEqual(review(p, verifier)["reason"], "HOLD_THIRD_ROUND_ORACLE_NOT_DISTINCT")

    def test_final_simulation_3_does_not_inherit_design_theory_pass(self):
        p = plan()
        p["finalFamilies"]["SIM3"]["passed"] = ["SIM31", "SIM32"]
        r = review(p, verifier)
        self.assertEqual(r["reason"], "HOLD_FINAL_SIMULATION_GAPS")
        self.assertEqual(r["GITHUB_PREPARED"], "HOLD")

    def test_final_distinct_oracles_and_exact_source(self):
        p = plan()
        p["finalFamilies"]["SIM3"]["oracle"] = p["finalFamilies"]["SIM2"]["oracle"]
        self.assertEqual(review(p, verifier)["reason"], "HOLD_FINAL_ORACLES_NOT_DISTINCT")
        p = plan()
        p["finalFamilies"]["SIM3"]["source"] = digest(88)
        self.assertEqual(review(p, verifier)["reason"], "HOLD_FINAL_SOURCE_DRIFT")

    def test_invalid_controls_or_verifier_receipt_hold(self):
        p = plan()
        p["controls"]["THEORY"].append("THEORY1")
        self.assertIn("HOLD_FIXED_ACCEPTANCE_IDS", review(p, verifier)["reason"])
        p = plan()
        def broken(phase, entry):
            result = verifier(phase, entry)
            result["evidenceSha256"] = "bad"
            return result
        self.assertIn("HOLD_BAD_VERIFIER_PROOF", review(p, broken)["reason"])

    def test_field_authority_always_separate(self):
        p = plan()
        p["HUMAN_AUTHORIZED"] = "PASS"
        p["VERIFIED_FINISH"] = "PASS"
        r = review(p, verifier)
        self.assertEqual(r["HUMAN_AUTHORIZED"], "HOLD")
        self.assertEqual(r["VERIFIED_FINISH"], "HOLD")


if __name__ == "__main__":
    unittest.main()
