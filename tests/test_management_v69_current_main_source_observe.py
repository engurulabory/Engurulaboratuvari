import hashlib
import unittest
from tools.management_v69_current_main_source_observe import observe
class TestSourceObservation(unittest.TestCase):
 def test_exact_source(self):
  raw=b"ENGURU source"
  r=observe("a"*40,raw,hashlib.sha256(raw).hexdigest())
  self.assertEqual(r["state"],"PASS_CURRENT_MAIN_SOURCE_OBSERVED")
  self.assertEqual(r["owner_signature"],"HOLD_REAL_OWNER_SIGNER")
  self.assertFalse(r["historical_receipt_reusable"])
 def test_tamper(self):
  r=observe("a"*40,b"changed",hashlib.sha256(b"original").hexdigest())
  self.assertEqual(r["reason"],"SOURCE_DIGEST_MISMATCH")
 def test_commit(self):
  self.assertEqual(observe("wrong",b"",hashlib.sha256(b"").hexdigest())["reason"],"MAIN_SHA_REQUIRED")
if __name__=="__main__":unittest.main()
