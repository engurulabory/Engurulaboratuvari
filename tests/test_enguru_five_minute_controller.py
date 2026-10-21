import sys,unittest,tempfile
from pathlib import Path
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from enguru_five_minute_controller import cycle,select,verifier,key,REPO
G={"state":"ENABLED_READONLY","repository":REPO,"max_tasks_per_cycle":1,"max_additional_spend_usd":0,"paid_providers":False,"human_final_authority":"OWNER"}
def t(**kwargs):
    x={"id":"LABORY_PILOT","state":"READY","target_repo":REPO,"action":"verify_file_digest","path":"source.txt","expected_sha256":sha256(b"PASS").hexdigest(),"dependencies":[]}
    x.update(kwargs);return x
class ControllerTests(unittest.TestCase):
    def test_proof(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            r=cycle(root,{"tasks":[t()]},G)
            self.assertEqual(r["state"],"PASS");self.assertEqual(r["verification"]["state"],"PASS")
            self.assertFalse(r["authorized_merge"]);self.assertEqual(r["additional_spend_usd"],0)
    def test_idle(self):self.assertEqual(cycle(Path("."),{"tasks":[t()]},G,{"LABORY_PILOT"})["state"],"PASS_IDLE")
    def test_paid_provider(self):self.assertEqual(cycle(Path("."),{"tasks":[]},{**G,"paid_providers":True})["reason"],"AUTHORITY_OR_ZERO_COST_GATE")
    def test_cost(self):self.assertEqual(cycle(Path("."),{"tasks":[]},{**G,"max_additional_spend_usd":1})["state"],"HOLD_GUVENLI_DUR")
    def test_private(self):self.assertEqual(cycle(Path("."),{"tasks":[t(target_repo="private")]},G)["reason"],"PRIVATE_REPO_GRANT_REQUIRED")
    def test_shell(self):self.assertEqual(cycle(Path("."),{"tasks":[t(action="shell")]},G)["reason"],"ACTION_GRANT_REQUIRED")
    def test_duplicate(self):self.assertEqual(select({"tasks":[t(),t()]},set())[1],"DUPLICATE_TASK_IDS")
    def test_missing_dependency(self):self.assertEqual(select({"tasks":[t(dependencies=["MISSING"])]},set())[1],"DEPENDENCY_AUTHORITY")
    def test_priority(self):
        nexttask=t(id="LABORY_SECOND",dependencies=["LABORY_PILOT"])
        self.assertEqual(select({"tasks":[nexttask,t()]},set())[0]["id"],"LABORY_PILOT")
        self.assertEqual(select({"tasks":[nexttask,t()]},{"LABORY_PILOT"})[0]["id"],"LABORY_SECOND")
    def test_escape(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(cycle(Path(d),{"tasks":[t(path="../secret")]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"FAIL")
            self.assertEqual(cycle(root,{"tasks":[t()]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            self.assertEqual(verifier(t(),{"state":"PASS","evidence":{"sha256":"0"*64,"size":4}},root)["state"],"HOLD_GUVENLI_DUR")
    def test_unknown_recipe(self):self.assertEqual(cycle(Path("."),{"tasks":[t(action="run_unit_test",path="other.py")]},G)["reason"],"TEST_RECIPE_SCOPE")
    def test_fingerprint(self):self.assertNotEqual(key(t()),key(t(path="change.txt")))
if __name__=="__main__":unittest.main()
