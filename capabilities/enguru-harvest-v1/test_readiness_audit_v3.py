"""V1→V3 evidence-scored improvement, separate design and field proof."""
import json
import unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
S=json.loads((BASE/"READINESS_AUDIT_V3.json").read_text(encoding="utf-8"))
class AuditV3Tests(unittest.TestCase):
    def test_github_only_65(self):
        a=S["github"]
        self.assertEqual((a["baseline"],a["current"],a["target"]),(63,65,100))
        self.assertEqual(sum(x[1] for x in a["weights"]),65)
        self.assertEqual(sum(x[2] for x in a["weights"]),100)
        self.assertEqual(a["actual_acceptance"],"HOLD")
    def test_osi_60_bounded(self):
        a=S["osi"]
        self.assertEqual((a["baseline"],a["current"],a["target"]),(55,60,100))
        self.assertEqual(sum(x[1] for x in a["weights"]),60)
        self.assertEqual(sum(x[2] for x in a["weights"]),100)
        self.assertEqual(a["field_execution"],0)
        self.assertEqual(a["stage"],"GITHUB_ONLY_PRE_FIELD")
    def test_definition_is_not_real_finish(self):
        self.assertEqual(S["design_coverage"]["github"],100)
        self.assertEqual(S["design_coverage"]["osi"],100)
        self.assertEqual(S["design_coverage"]["real_verified_finish"],"HOLD")
        self.assertIs(S["proofs"]["mac_executed"],False)
        self.assertEqual(S["proofs"]["official_skill_adoptions"],0)
    def test_security_and_authority_boundaries(self):
        self.assertEqual(S["proofs"]["source_legal_approval"],"HOLD")
        self.assertEqual(S["proofs"]["user_benefit"],"HOLD")
        self.assertEqual(S["proofs"]["owner_decision"],"HOLD")
        self.assertEqual(S["proofs"]["source_commit_readme_pairs"],30)
if __name__=="__main__":
    unittest.main()
