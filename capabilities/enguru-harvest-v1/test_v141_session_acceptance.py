"""V1.4.1 user session: evidence-ranked technical work vs official progression."""
import json
import unittest
from pathlib import Path

R=json.loads((Path(__file__).resolve().parent/"V141_SESSION_ACCEPTANCE_V1.json").read_text(encoding="utf-8"))
IDS=["T01","T02","A01","A02","A03","A04","A05","A06"]
class UniversalSessionV141Tests(unittest.TestCase):
    def test_exact_dependency_order(self):
        self.assertEqual([r["id"] for r in R["stages"]],IDS)
        self.assertEqual([r["order"] for r in R["stages"]],list(range(1,9)))
        self.assertEqual(R["official_current_gate"],"T01")
        self.assertIs(R["allow_auto_advance"],False)
    def test_real_github_source_pinned(self):
        self.assertEqual(R["source_v141_commit"],"8fbd40c8fde34e7f8d77d5079c4da86a1baa8dad")
        self.assertEqual(R["last_verified_exact_head"],"59e5b7043f55bf103d9dfa81354fce5d207f30fc")
        self.assertEqual((R["workflow_success"],R["harvest_job_success"]),(5,4))
        self.assertEqual((R["source_files_sha256_validated"],R["source_v141_real_test_executions"]),(18,378))
        self.assertEqual(R["harvest_real_regression_tests"],119)
    def test_full_contract_without_claiming_full_proof(self):
        self.assertEqual((R["github_acceptance_design_score"],R["osi_acceptance_design_score"]),(100,100))
        self.assertEqual((R["github_preparation_score"],R["osi_preparation_score"]),(65,60))
        self.assertEqual(R["official_verified_finish"],"HOLD")
        self.assertEqual(R["human_threshold"],"HOLD")
    def test_scope_and_authority(self):
        self.assertEqual((R["mac_osi_execution"],R["main_merge"]),(0,0))
        self.assertEqual((R["source_proven_external_skills"],R["source_external_skill_target"]),(0,12))
        self.assertEqual((R["repo"],R["pr"]),("engurulabory/Engurulaboratuvari",243))
        self.assertTrue(all(r["claimed_official_pass"] is False for r in R["stages"]))
        self.assertTrue(all(r["independent_evidence_score_100"] is False for r in R["stages"]))
    def test_human_provenance_dependencies(self):
        a={r["id"]:r for r in R["stages"]}
        self.assertIn("HOLD_ACTUAL_AUTHORIZED_TASKS",a["A05"]["blocking_evidence"])
        self.assertIn("HOLD_STAGE_PREDECESSOR_A05",a["A06"]["blocking_evidence"])
        self.assertIn("HOLD_OWNER_FIELD_PERMISSION",a["A06"]["blocking_evidence"])
    def test_no_empty_acceptance_or_unexplained_hold(self):
        for stage in R["stages"]:
            self.assertTrue(stage["acceptance"].strip())
            self.assertTrue(stage["blocking_evidence"])
            self.assertTrue(stage["technical_observation"].strip())
if __name__=="__main__":
    unittest.main()
