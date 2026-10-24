import unittest
from tools.management_v69_triple100_evidence_registry import evaluate_registry
class RegistryTests(unittest.TestCase):
 def test_zero_claims(self):
  r=evaluate_registry({})
  for a in ("DESIGN","THEORY","SIMULATION"):
   self.assertEqual(r[a]["structured_candidates"],0)
   self.assertEqual(len(r[a]["missing"]),100)
 def test_one_structured_claim_is_only_candidate(self):
  row=dict(description="source-bound invariant",source_path="tools/example.py",source_sha256="a"*64,assertion_id="ASSERT_1",test_run_id=42,independent_review="machine")
  r=evaluate_registry({"DESIGN_001":row})
  self.assertEqual(r["DESIGN"]["structured_candidates"],1)
  self.assertEqual(r["three_dimensions_verified"],"HOLD")
 def test_fake_run_rejected(self):
  row=dict(description="test",source_path="tools/file.py",source_sha256="a"*64,assertion_id="A",test_run_id=True,independent_review="machine")
  self.assertEqual(evaluate_registry({"THEORY_001":row})["THEORY"]["structured_candidates"],0)
if __name__=="__main__":unittest.main()
