import unittest
from tools.management_v69_historical_ci_classify import classify
A="1"*40
B="2"*40
class Historical(unittest.TestCase):
 def test_history_drifts_but_classification_passes(self):
  r=classify({"source_commit":A},{"main_sha":B})
  self.assertEqual(r["state"],"PASS_HISTORICAL_DRIFT_CLASSIFIED")
  self.assertFalse(r["current_main_accepted"])
  self.assertEqual(r["official_finish"],"HOLD")
 def test_equal_pin_cannot_approve(self):
  self.assertEqual(classify({"source_commit":A},{"main_sha":A})["reason"],"AUTHENTIC_CURRENT_MAIN_RECEIPT_REQUIRED")
 def test_invalid_pin(self):
  self.assertEqual(classify({"source_commit":"fake"},{"main_sha":B})["state"],"HOLD_GUVENLI_DUR")
if __name__=="__main__":unittest.main()
