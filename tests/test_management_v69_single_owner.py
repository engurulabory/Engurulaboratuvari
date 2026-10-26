import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"governance/management-v69/handoff/SINGLE_OWNER_ZERO_ROUTINE_V1.md"
class PolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=P.read_text()
 def test_proposal_preserves_canonical(self):
  self.assertIn("CURRENT_CANONICAL_AUTHORITY=UNCHANGED",self.s)
  self.assertIn("PROPOSED_CANONICAL_AMENDMENT",self.s)
 def test_sole_owner_and_no_fake_review(self):
  for x in ("engurulabory","Makine doğrulaması bağımsız insan review olarak adlandırılmaz","sahte reviewer","HOLD"):
   with self.subTest(x=x):self.assertIn(x,self.s)
 def test_no_false_final(self):
  for x in ("G2_G6_OFFICIAL=HOLD","VERIFIED_FINISH=HOLD","OSI_MUTATION=0"):
   self.assertIn(x,self.s)
 def test_ci_distinction(self):self.assertIn("üç attempt'i = HOLD",self.s)
 def test_free_is_target(self):self.assertIn("Maliyet hedefi 0 ek ücret",self.s)
 def test_all_nine(self):
  for i in range(1,10):self.assertIn(f"{i:02d} ",self.s)
if __name__=="__main__":unittest.main()
