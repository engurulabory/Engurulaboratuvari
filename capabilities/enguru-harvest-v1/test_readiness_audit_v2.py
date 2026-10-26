"""Enforce exact-source-only readiness score increases."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
R=json.loads((ROOT/"READINESS_AUDIT_V2.json").read_text(encoding="utf-8"))
class ReadinessAuditTests(unittest.TestCase):
    def test_score_exact(self):
        self.assertEqual(R["baseline_github"],63)
        self.assertEqual(sum(x[1] for x in R["discrete_rubric"]["github"]),65)
        self.assertEqual(sum(x[2] for x in R["discrete_rubric"]["github"]),100)
        self.assertEqual(R["github_verified_readiness"],65)
    def test_osi_stage_unmodified(self):
        self.assertEqual(R["osi_current"],55)
        self.assertEqual(R["osi_baseline"],55)
    def test_no_false_finish(self):
        self.assertEqual(R["github_official"],"HOLD")
        self.assertEqual(R["owner_verified_finish_decision"],"HOLD")
        self.assertEqual(R["external_official_proven"],0)
        self.assertEqual(R["real_user_task_benchmark_accepted"],0)
        self.assertEqual(R["mac_execution"],0)
        self.assertEqual(R["legal_reuse_approved"],0)
    def test_pins_count(self):
        self.assertEqual(R["confirmed_real_source_pin_count"],30)
    def test_no_overclaim(self):
        self.assertEqual(R["status"],"EVIDENCE_ASSESSED_ONLY")
if __name__=="__main__":
    unittest.main()
