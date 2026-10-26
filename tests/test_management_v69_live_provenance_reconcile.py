import unittest
from tools.management_v69_live_provenance_reconcile import reconcile_historical
A="1"*40
B="2"*40
class ReconcileTests(unittest.TestCase):
 def test_drift(self):
  r=reconcile_historical(A,B,True,{})
  self.assertEqual(r["reason"],"HISTORICAL_RECORD_CURRENT_MAIN_DRIFT")
 def test_missing_source(self):
  self.assertEqual(reconcile_historical(A,A,False,{})["reason"],"SOURCE_PROVENANCE_REQUIRED")
 def test_source_needs_canonical(self):
  self.assertEqual(reconcile_historical(A,A,True,{})["reason"],"CANONICAL_OWNER_RECEIPT_REQUIRED")
 def test_wrong_commit(self):
  self.assertEqual(reconcile_historical("invalid",A,True,{})["reason"],"COMMIT_PIN_REQUIRED")
if __name__=="__main__":unittest.main()
