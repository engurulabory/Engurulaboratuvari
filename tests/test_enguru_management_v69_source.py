"""Real-source read-only projection tests."""
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/"tools"/"enguru_management_v69_source.py"
s=importlib.util.spec_from_file_location("mgmt_source",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
commit="a"*40
activation={"repository":m.REPO,"human_final_authority":"OWNER","state":"ENABLED_BOUNDED_PR"}
def task(ident="A",state="READY",deps=None):
    return {"id":ident,"target_repo":m.REPO,"state":state,"dependencies":deps or []}
class TestSource(unittest.TestCase):
    def test_canonical_projection(self):
        r=m.reconcile({"tasks":[task()]},activation,commit,{"x":"z"})
        self.assertEqual(r["state"],"MANAGEMENT_SNAPSHOT_READ_ONLY")
        self.assertEqual(r["verified_acceptance"],0)
        self.assertEqual(r["ready_for_execution"],[])
        self.assertEqual(r["tasks"][0]["observed_controller_state"],"READY")
    def test_paused(self):
        r=m.reconcile({"tasks":[task(state="PAUSED_AUDITED")]},activation,commit,{})
        self.assertEqual(r["tasks"][0]["management_state"],"PAUSED")
    def test_commit_required(self):
        self.assertEqual(m.reconcile({"tasks":[]},activation,"main",{})["reason"],"SOURCE_COMMIT_REQUIRED")
    def test_owner_authority(self):
        a=dict(activation,human_final_authority="BOT")
        self.assertEqual(m.reconcile({"tasks":[]},a,commit,{})["reason"],"AUTHORITY_BOUNDARY")
    def test_duplicate_ids(self):
        self.assertEqual(m.reconcile({"tasks":[task(),task()]},activation,commit,{})["reason"],"TASK_ID")
    def test_dependency_unknown(self):
        self.assertEqual(m.reconcile({"tasks":[task(deps=["MISSING"])]},activation,commit,{})["reason"],"DEPENDENCY_MISSING")
    def test_cross_repo(self):
        a=task();a["target_repo"]="wrong"
        self.assertEqual(m.reconcile({"tasks":[a]},activation,commit,{})["reason"],"SCOPE_OR_DEPENDENCY")
    def test_symlink_rejection(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            x=Path(root);(x/"target").write_text("test")
            (x/"link").symlink_to(x/"target")
            with self.assertRaisesRegex(ValueError,"SYMLINK_SOURCE"):m.read(x,"link")
if __name__=="__main__":unittest.main()
