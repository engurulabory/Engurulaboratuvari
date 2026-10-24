import tempfile
import unittest
from pathlib import Path
from tools.management_v69_architecture_theory_independent import inspect,REQUIRED
class TestIndependentTheory(unittest.TestCase):
 def test_repo_sources(self):
  r=inspect(Path(__file__).resolve().parents[1])
  self.assertEqual(r["state"],"THEORY_SOURCE_REVIEW_PASS")
  self.assertEqual(len(r["evidence"]),len(REQUIRED))
  self.assertEqual(r["owner_authority"],"HOLD")
  self.assertEqual(r["official_verified_finish"],"HOLD")
 def test_absent_source_hold(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(inspect(d)["reason"],"MISSING_SOURCE")
 def test_all_claimed_is_not_final(self):
  r=inspect(Path(__file__).resolve().parents[1])
  self.assertEqual(r["design_100"],"HOLD_INDEPENDENT_FINAL")
  self.assertEqual(r["osi_mutation"],0)
if __name__=="__main__":unittest.main()
