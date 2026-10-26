import unittest
from tools.management_v69_pilot_dual_acceptance import assess,THEORY_KEYS,FIELD_KEYS
class GateTests(unittest.TestCase):
 def test_all_missing(self):
  r=assess({},{})
  self.assertEqual(r["theory_state"],"THEORY_HOLD")
  self.assertEqual(r["next_target"],"01")
  self.assertEqual(len(r["theory_missing"]),len(THEORY_KEYS))
 def test_theory_pass_never_field(self):
  r=assess(dict.fromkeys(THEORY_KEYS,True),{})
  self.assertEqual(r["theory_state"],"THEORY_CANDIDATE_PASS")
  self.assertEqual(r["field_state"],"FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED")
  self.assertEqual(r["verified_finish"],"HOLD")
  self.assertEqual(r["next_target"],"02")
 def test_all_claimed_field_never_authorized(self):
  r=assess(dict.fromkeys(THEORY_KEYS,True),dict.fromkeys(FIELD_KEYS,True))
  self.assertEqual(r["field_state"],"FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED")
  self.assertEqual(r["osi_mutation"],0)
 def test_truth_is_not_string(self):
  r=assess(dict.fromkeys(THEORY_KEYS,"PASS"),{})
  self.assertEqual(r["theory_state"],"THEORY_HOLD")
 def test_single_missing_theory(self):
  x=dict.fromkeys(THEORY_KEYS,True);x["source_sha256"]=False
  r=assess(x,{})
  self.assertEqual(r["theory_missing"],["source_sha256"])
 def test_no_side_effect(self):
  a=dict.fromkeys(THEORY_KEYS,True);b={}
  assess(a,b)
  self.assertEqual(a,dict.fromkeys(THEORY_KEYS,True))
  self.assertEqual(b,{})
if __name__=="__main__":unittest.main()
