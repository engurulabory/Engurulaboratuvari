import unittest
from tools.management_v69_triple100_distinctness_audit import audit
class TestDistinctness(unittest.TestCase):
 def test_missing_all(self):
  r=audit({})
  self.assertEqual(len(r["missing_descriptions"]),300)
  self.assertEqual(r["described_controls"],0)
 def test_duplicate_does_not_become_unique(self):
  p={"description":"Check owner separation", "assertion_id":"test_owner", "source_path":"tools/pilot.py"}
  r=audit({"DESIGN_001":p,"DESIGN_002":dict(p)})
  self.assertEqual(set(r["duplicate_assertion_claims"]),{"DESIGN_001","DESIGN_002"})
  self.assertEqual(r["final"],"HOLD_INDEPENDENT_CI_AND_EVIDENCE")
 def test_placeholder_rejected(self):
  r=audit({"SIMULATION_001":{"description":"TODO","assertion_id":"test_a","source_path":"tools/a.py"}})
  self.assertEqual(r["placeholder_descriptions"],["SIMULATION_001"])
if __name__=="__main__":unittest.main()
