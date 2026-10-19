import tempfile
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_dependency_inventory import inventory

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/"tests").mkdir();(self.root/"tools").mkdir()
    def test_missing_test_is_hold(self):
        self.assertEqual(inventory(self.root,["missing.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_local_import_missing_is_hold(self):
        (self.root/"tests"/"test_one.py").write_text("from tools.not_here import value")
        self.assertEqual(inventory(self.root,["test_one.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_existing_direct_import_is_pass_bounded(self):
        (self.root/"tools"/"existing.py").write_text("value=1")
        (self.root/"tests"/"test_one.py").write_text("from tools.existing import value")
        r=inventory(self.root,["test_one.py"])
        self.assertEqual(r["state"],"PASS_DIRECT_IMPORTS_RESOLVED")
        self.assertEqual(r["verifiedFinish"],"HOLD")
        self.assertEqual(r["transitiveRuntimeDependencies"],"HOLD_NOT_ANALYZED")
    def test_bad_syntax_is_hold(self):
        (self.root/"tests"/"broken.py").write_text("def ???")
        self.assertEqual(inventory(self.root,["broken.py"])["state"],"HOLD_GUVENLI_DUR")
if __name__=="__main__":unittest.main()
