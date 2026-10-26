import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/"upstream_execution_coverage.json").read_text(encoding="utf-8"))
class CoverageTests(unittest.TestCase):
    def test_all_ids_unique(self):
        self.assertEqual([x["id"] for x in DATA["records"]],[f"P{i:02d}" for i in range(1,13)])
    def test_real_observed_count(self):
        self.assertEqual(sum(x["technical_state"]=="REAL_TECHNICAL_UNREVIEWED" for x in DATA["records"]),9)
        self.assertEqual(DATA["technical_executed_count"],9)
    def test_structure_is_separate(self):
        self.assertEqual(sum(x["technical_state"]=="STRUCTURE_ONLY_REUSE_HOLD" for x in DATA["records"]),1)
        self.assertEqual(DATA["structure_only_count"],1)
    def test_no_official_proven(self):
        self.assertEqual(DATA["independently_proven_count"],0)
        self.assertTrue(all(x["official_proven"] is False and x["independent_review"]=="HOLD" for x in DATA["records"]))
        self.assertEqual(DATA["github_verified_finish"],"HOLD")
    def test_unexecuted_models_and_osi(self):
        self.assertEqual(DATA["actual_codex_or_claude_authorized_runs"],0)
        self.assertEqual(DATA["real_user_gain_benchmarks"],0)
        self.assertEqual(DATA["osi_execution_count"],0)
        self.assertTrue(all(x["osi_execution"]==0 for x in DATA["records"]))
    def test_real_evidence_links_only(self):
        for entry in DATA["records"]:
            u=entry["github_ci_evidence"]
            if entry["technical_state"].startswith("HOLD_"):
                self.assertIsNone(u)
            else:
                self.assertTrue(u.startswith("https://github.com/engurulabory/Engurulaboratuvari/actions/runs/"))

if __name__=="__main__":
    unittest.main()
