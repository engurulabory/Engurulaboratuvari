import unittest
import tempfile
import sys
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from enguru_five_minute_controller import cycle,management_select

class ControllerTests(unittest.TestCase):
    def test_safe_management_engineer_management(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"safe.txt").write_text("PASS")
            task=dict(id="a",state="READY",priority=1,dependencies=[],action="verify_file_digest",path="safe.txt",expected_sha256=sha256(b"PASS").hexdigest())
            r=cycle(root,{"tasks":[task]},{"state":"HOLD"},pilot=True)
            self.assertEqual(r["state"],"PASS")
            self.assertEqual(r["executed_count"],1)
            self.assertEqual(r["human_authority"],"OWNER_RESERVED")
    def test_unvalidated_receipt_holds(self):
        r=cycle(Path("."),{"tasks":[]},{"state":"PASS","donecheck_verified_finish_receipt":"invented"})
        self.assertEqual(r["reason"],"CANONICAL_RECEIPT_VERIFIER_BINDING_REQUIRED")
    def test_pending_b1_holds(self):
        r=cycle(Path("."),{"tasks":[]},{"state":"HOLD"})
        self.assertEqual(r["reason"],"B1_SIGNED_DONECHECK_FINISH_REQUIRED")
    def test_scope_holds(self):
        t=dict(id="a",state="READY",action="verify_file_digest",path="../secret",expected_sha256="0"*64)
        with tempfile.TemporaryDirectory() as d:
            r=cycle(Path(d),{"tasks":[t]},{},pilot=True)
            self.assertEqual(r["state"],"HOLD_GUVENLI_DUR")
    def test_no_ungranted_shell(self):
        t=dict(id="a",state="READY",action="shell")
        with tempfile.TemporaryDirectory() as d:
            r=cycle(Path(d),{"tasks":[t]},{},pilot=True)
            self.assertEqual(r["engineer"]["reason"],"EXPLICIT_ACTION_GRANT_REQUIRED")
    def test_priority_dependencies(self):
        t,e=management_select({"verified_task_ids":[],"tasks":[{"id":"a","state":"READY","priority":1,"dependencies":["b"]},{"id":"b","state":"READY","priority":2}]})
        self.assertEqual(t["id"],"b")
    def test_duplicate_hold(self):
        t,e=management_select({"tasks":[{"id":"a"},{"id":"a"}]})
        self.assertEqual(e,"DUPLICATE_TASK_IDS")

if __name__=="__main__":unittest.main()
