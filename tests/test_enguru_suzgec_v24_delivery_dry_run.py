import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_delivery_dry_run import assess

class DryRunTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);(self.root/"tools").mkdir()
  self.inventory=self.root/"inventory.json"
  self.name="tools/example.py"
  self.digest=hashlib.sha256(b"example").hexdigest()
 def check(self):
  self.inventory.write_text(json.dumps({"schema":"enguru.suzgec.v24.github-delivery-inventory/v1","state":"PASS_BOUNDED_GITHUB_SOURCE_INVENTORY_ONLY","files":{self.name:self.digest}}))
  return assess(self.root,self.inventory)
 def test_missing_file_holds(self):
  self.assertEqual(self.check()["items"][0]["status"],"MISSING_NEEDS_EXPLICIT_DELIVERY")
 def test_existing_difference_holds(self):
  (self.root/self.name).write_bytes(b"different")
  self.assertEqual(self.check()["items"][0]["status"],"HOLD_EXISTING_SOURCE_DIFFERS")
 def test_identical_file_still_not_native_pass(self):
  (self.root/self.name).write_bytes(b"example")
  r=self.check();self.assertEqual(r["state"],"PASS_READ_ONLY_IDENTICAL_SOURCES_ONLY")
  self.assertEqual(r["verifiedFinish"],"HOLD");self.assertEqual(r["writes"],0)
 def test_symlink_holds(self):
  (self.root/self.name).symlink_to(self.inventory)
  self.assertEqual(self.check()["items"][0]["status"],"HOLD_SYMLINK")
 def test_traversal_holds(self):
  self.name="../unsafe.py";self.assertEqual(self.check()["state"],"HOLD_GUVENLI_DUR")
 def test_unverified_manifest_holds(self):
  self.inventory.write_text('{"files":{"tools/example.py":"123"}}')
  self.assertEqual(assess(self.root,self.inventory)["state"],"HOLD_GUVENLI_DUR")
if __name__=="__main__":unittest.main()
