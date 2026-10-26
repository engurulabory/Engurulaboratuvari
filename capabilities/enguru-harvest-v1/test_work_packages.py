"""K01–K05 Zulfikar scope, DAG, authority and safe finish gates."""
import json
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/"WORK_PACKAGES_ZULFIKAR_V13.json").read_text(encoding="utf-8"))

class WorkPackageTests(unittest.TestCase):
    def test_exact_ids(self):
        self.assertEqual([p["id"] for p in PLAN["packs"]],["K01","K02","K03","K04","K05"])
    def test_real_dag(self):
        seen=set()
        for pack in PLAN["packs"]:
            self.assertTrue(set(pack["dependencies"]).issubset(seen))
            seen.add(pack["id"])
    def test_one_owner(self):
        owner=PLAN["authority"]
        self.assertEqual(owner["owner"],"engurulabory")
        self.assertIs(owner["peer_review_required_for_github_technical"],False)
        self.assertEqual(owner["owner_decision"],"HUMAN_THRESHOLD_HOLD_NOT_SELF_GRANTED")
        self.assertIs(owner["new_issuer"],False)
    def test_github_field_boundaries(self):
        self.assertEqual(PLAN["completion_policy"]["osiExecution"],0)
        self.assertEqual(PLAN["completion_policy"]["mainMerge"],0)
        self.assertIn("official",PLAN["completion_policy"]["githubVerifiedFinish"])
    def test_packages_hold_actual_adoption(self):
        self.assertIn("HOLD",PLAN["packs"][1]["state"])
        self.assertIn("HOLD",PLAN["packs"][2]["state"])
        self.assertIn("HOLD",PLAN["packs"][4]["state"])
        self.assertEqual(PLAN["authority"]["external_skill_official_proven"],0)
    def test_source_is_one_product(self):
        self.assertEqual(PLAN["baseline_head"],"5177b7840c34df20894cbf8fdc6a11ddfbfb2cde")
        self.assertEqual(PLAN["authority"]["scope"],"GITHUB_TECHNICAL_ACCEPTANCE_ONLY")

if __name__=="__main__":
    unittest.main()
