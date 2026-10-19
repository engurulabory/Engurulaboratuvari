import tempfile
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_transitive_closure import assess

class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        (self.root/"tools").mkdir()
    def write(self,p,s):
        q=self.root/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
    def test_transitive_missing_hold(self):
        self.write("tools/a.py","from tools.b import value")
        self.assertEqual(assess(self.root,["tools/a.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_transitive_cycle_bounded(self):
        self.write("tools/a.py","from tools.b import value")
        self.write("tools/b.py","from tools.a import value")
        r=assess(self.root,["tools/a.py"])
        self.assertEqual(r["state"],"PASS_BOUNDED_STATIC_CLOSURE_ONLY")
        self.assertEqual(len(r["checked"]),2)
        self.assertEqual(r["verifiedFinish"],"HOLD")
    def test_third_party_hold(self):
        self.write("tools/a.py","import thirdparty_untrusted")
        self.assertEqual(assess(self.root,["tools/a.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_dynamic_import_hold(self):
        self.write("tools/a.py","__import__('dangerous')")
        self.assertEqual(assess(self.root,["tools/a.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_bad_syntax_hold(self):
        self.write("tools/a.py","def ???")
        self.assertEqual(assess(self.root,["tools/a.py"])["state"],"HOLD_GUVENLI_DUR")
    def test_non_python_missing_hold(self):
        self.assertEqual(assess(self.root,["missing.json"])["state"],"HOLD_GUVENLI_DUR")
if __name__=="__main__":unittest.main()
