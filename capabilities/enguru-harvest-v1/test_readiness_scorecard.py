"""Validate analyst readiness rubrics while keeping authority states separate."""
import json
import unittest
from pathlib import Path
R=json.loads((Path(__file__).resolve().parent/"READINESS_SCORECARD_V1.json").read_text(encoding="utf-8"))
class ScoreTests(unittest.TestCase):
    def test_github_score(self):
        a=R["github"]["criteria"]
        self.assertEqual(sum(row[1] for row in a),63)
        self.assertEqual(sum(row[2] for row in a),100)
        self.assertEqual(R["github"]["readiness_score"],63)
        self.assertEqual(R["github"]["state"],"VERIFIED_FINISH_HOLD")
    def test_osi_score(self):
        a=R["osi"]["criteria"]
        self.assertEqual(sum(row[1] for row in a),55)
        self.assertEqual(sum(row[2] for row in a),100)
        self.assertEqual(R["osi"]["preflight_readiness_score"],55)
        self.assertEqual(R["osi"]["state"],"PRE_FIELD_PREPARATION_ONLY")
    def test_scores_are_not_official_acceptance(self):
        self.assertIs(R["github"]["actual_official_finish"],False)
        self.assertIs(R["osi"]["field_executed"],False)
        self.assertEqual(R["external_official_proven"],"0/12")
        self.assertEqual(R["human_threshold"],"HOLD")
        self.assertEqual(R["osi_execution"],0)
        self.assertEqual(R["merge"],0)
    def test_all_remaining_groups_present(self):
        self.assertEqual([x["id"] for x in R["remaining_packages"]],["K01","K02","K03","K04","K05"])
    def test_positive_weights_in_range(self):
        for rubric in (R["github"],R["osi"]):
            for label,earned,total in rubric["criteria"]:
                self.assertTrue(label)
                self.assertTrue(0<=earned<=total)
if __name__=="__main__":
    unittest.main()
