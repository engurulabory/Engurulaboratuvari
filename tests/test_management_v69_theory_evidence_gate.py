import unittest
from tools.management_v69_theory_evidence_gate import assess
from tools.management_v69_formal70 import IDS
def proof():
 return {"state":"PASS","source_path":"tools/source.py","source_sha256":"a"*64,"test_run_id":123,"reviewer":"independent-machine"}
class EvidenceGate(unittest.TestCase):
 def test_empty(self):
  r=assess({})
  self.assertEqual(r["accepted_candidate_controls"],0)
  self.assertEqual(len(r["missing_controls"]),70)
 def test_claimed_70_are_never_final(self):
  r=assess({k:proof() for k in IDS})
  self.assertEqual(r["accepted_candidate_controls"],70)
  self.assertEqual(r["theory_final"],"HOLD")
 def test_bad_sha_and_fake_run(self):
  a=proof();a["source_sha256"]="NO";b=proof();b["test_run_id"]=True
  self.assertEqual(assess({IDS[0]:a,IDS[1]:b})["accepted_candidate_controls"],0)
 def test_path_escape(self):
  a=proof();a["source_path"]="../secrets"
  self.assertEqual(assess({IDS[0]:a})["accepted_candidate_controls"],0)
if __name__=="__main__": unittest.main()
