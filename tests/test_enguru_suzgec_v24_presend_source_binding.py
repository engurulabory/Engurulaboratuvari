import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.enguru_suzgec_v24_presend_source_binding import evaluate

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"a.py"
        self.source.write_text("stable")
        self.draft=self.root/"draft.txt"
        self.draft.write_text("Geçerli çalışma.")
        files={"a.py":hashlib.sha256(b"stable").hexdigest()}
        digest=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        self.manifest=self.root/"manifest.json"
        self.manifest.write_text(json.dumps({"goal_scope_id":"ENGURU_SUZGEC_V24","source_files":files,"prediction_source_sha256":digest}))

    def call(self):
        return evaluate(self.root,self.manifest,self.draft)

    def test_real_missing_linter_contract_stays_hold(self):
        self.assertEqual(self.call()["state"],"HOLD_GUVENLI_DUR")

    def test_source_change_skips_language(self):
        self.source.write_text("changed")
        with patch("tools.enguru_suzgec_v24_presend_source_binding.inspect") as mocked:
            r=self.call()
        mocked.assert_not_called()
        self.assertEqual(r["reason"],"SOURCE_PREFLIGHT_HOLD")

    def test_source_pass_language_hold(self):
        with patch("tools.enguru_suzgec_v24_presend_source_binding.inspect",return_value={"state":"HOLD"}):
            self.assertEqual(self.call()["reason"],"LANGUAGE_PRESEND_HOLD")

    def test_two_scoped_pass_still_never_verified_finish(self):
        with patch("tools.enguru_suzgec_v24_presend_source_binding.inspect",return_value={"state":"PASS_SCOPED_DRAFT_LANGUAGE_GATE"}):
            r=self.call()
        self.assertEqual(r["state"],"PASS_BOUNDED_PREPARATION_ONLY")
        self.assertEqual(r["verifiedFinish"],"HOLD")

    def test_missing_draft_holds(self):
        self.draft.unlink()
        self.assertEqual(self.call()["state"],"HOLD_GUVENLI_DUR")

    def test_draft_symlink_holds(self):
        self.draft.unlink()
        self.draft.symlink_to(self.source)
        self.assertEqual(self.call()["state"],"HOLD_GUVENLI_DUR")

    def test_corrupt_manifest_holds(self):
        self.manifest.write_text("{")
        self.assertEqual(self.call()["state"],"HOLD_GUVENLI_DUR")

if __name__=="__main__":
    unittest.main()
