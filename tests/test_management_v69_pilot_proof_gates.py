import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.management_v69_pilot_proof_gates import verify_source,owner_gate

class PilotGates(unittest.TestCase):
 def test_source_exact(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"source.txt";f.write_bytes(b"ENGURU")
   h=hashlib.sha256(b"ENGURU").hexdigest()
   self.assertEqual(verify_source(d,"source.txt",h)["state"],"PASS_SOURCE_SHA256")
   f.write_bytes(b"ENGURU_CHANGED")
   self.assertEqual(verify_source(d,"source.txt",h)["reason"],"SOURCE_SHA_DRIFT")
 def test_escape_and_link(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"file";f.write_bytes(b"ok")
   h=hashlib.sha256(b"ok").hexdigest()
   self.assertEqual(verify_source(d,"../file",h)["state"],"HOLD_GUVENLI_DUR")
   (Path(d)/"link").symlink_to(f)
   self.assertEqual(verify_source(d,"link",h)["reason"],"SOURCE_SCOPE")
 def test_invalid_pin(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/"file").write_bytes(b"ok")
   self.assertEqual(verify_source(d,"file","pass")["reason"],"INVALID_SHA_PIN")
 def test_owner_requires_real_receipt(self):
  proof={"state":"PASS_SOURCE_SHA256"}
  self.assertEqual(owner_gate(proof,"foreign")["reason"],"OWNER_SCOPE")
  self.assertEqual(owner_gate(proof,"engurulabory")["reason"],"AUTHENTIC_OWNER_AUTHORITY_REQUIRED")
  self.assertEqual(owner_gate(proof,"engurulabory",True,True,True,True)["reason"],"CANONICAL_VERIFIER_RECEIPT_REQUIRED")
 def test_false_source(self):
  self.assertEqual(owner_gate({"state":"HOLD_GUVENLI_DUR"},"engurulabory")["reason"],"SOURCE_EVIDENCE_REQUIRED")
if __name__=="__main__": unittest.main()
