import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_terminal_twin_parity import fingerprint,compare,SCHEMA

class TwinParityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/"a.py").write_bytes(b"same")
    def test_equal_snapshot_bounded_not_native(self):
        a=fingerprint(self.root,["a.py"])
        b=dict(a)
        r=compare(a,b)
        self.assertEqual(r["state"],"PASS_BOUNDED_FINGERPRINT_PARITY_ONLY")
        self.assertEqual(r["verifiedFinish"],"HOLD")
    def test_modified_source_holds(self):
        a=fingerprint(self.root,["a.py"])
        (self.root/"a.py").write_bytes(b"changed")
        self.assertEqual(compare(a,fingerprint(self.root,["a.py"]))["state"],"HOLD_GUVENLI_DUR")
    def test_environment_difference_holds(self):
        a=fingerprint(self.root,["a.py"]);b=dict(a,architecture="other")
        self.assertEqual(compare(a,b)["state"],"HOLD_GUVENLI_DUR")
    def test_missing_schema_holds(self):
        self.assertEqual(compare({},{} )["state"],"HOLD_GUVENLI_DUR")
    def test_forged_finish_holds(self):
        a=fingerprint(self.root,["a.py"]);b=dict(a,verifiedFinish="PASS")
        self.assertEqual(compare(a,b)["state"],"HOLD_GUVENLI_DUR")
    def test_symlink_escape_rejected(self):
        (self.root/"alias.py").symlink_to(self.root/"a.py")
        with self.assertRaises(ValueError): fingerprint(self.root,["alias.py"])
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): fingerprint(self.root,["../secret"])
    def test_duplicate_scope_rejected(self):
        with self.assertRaises(ValueError): fingerprint(self.root,["a.py","a.py"])
if __name__=="__main__": unittest.main()
