"""Süzgeç v2.4 final eight-stage semantic sequence contract tests. Candidate only."""
import json
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_goal_acceptance_loop import decide

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json"
EXPECTED=["HEDEF","KABUL_SINIRLARI","MEVCUT_SEKIZ_ASAMA","GERCEK_KANIT","YETKILI_VERIFIED_FINISH","BITTI_DUR"]
class FinalSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(PATH.read_text(encoding="utf-8"))
        cls.r=cls.c["eightStageGoalAcceptanceLoop"]
    def test_exact_final_sequence(self):
        self.assertEqual(self.r["finalSequence"],EXPECTED)
    def test_stages_unchanged(self):
        self.assertEqual(self.c["eightStages"],["Hakikati gör","Değeri koru","Eksikleri ve ihtiyaçları tespit et","Gerekli farkı üret","Eksikleri tamamla, ihtiyaçları karşıla","Kanıtla","Bir sonraki ihtiyaçları belirle","İlerlet"])
    def test_existing_finish_gates(self):
        self.assertEqual(self.c["existingFinishGates"],["T01","T02","T03","T04"])
    def test_no_extra_authority_or_core(self):
        self.assertTrue(self.r["noNinthStage"] and self.r["noNewCore"] and self.r["noNewGate"])
        self.assertEqual(self.r["canonicalActivation"],"PENDING_OWNER_APPROVED_OSi_FIELD_BINDING")
    def test_not_self_certified(self):
        self.assertEqual(self.c["verifiedFinish"],"HOLD")
        self.assertIn("NO_SELF_DECLARED_PASS",self.r["finishThreshold"])
    def test_declared_pass_never_issues_finish(self):
        self.assertNotEqual(decide({"goal_id":"G","goal_statement":"Goal","scope_version":"v1","owner":"human","criteria":[]})["state"],"BITTI_DUR")
if __name__=="__main__":unittest.main()
