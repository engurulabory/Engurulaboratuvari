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

    def test_pass_receipt_rechecks_source_sha(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"source.txt").write_bytes(b"PASS")
            task=t()
            old=key(task,root,"a"*40)
            (root/"source.txt").write_bytes(b"DRIFT")
            self.assertNotEqual(old,key(task,root,"a"*40))
            self.assertNotEqual(old,key(task,root,"b"*40))
    def test_retry_budget_governed(self):
        task=t()
        r=cycle(Path("."),{"tasks":[task]},G,failed={task["id"]:2})
        self.assertEqual(r["reason"],"RETRY_BUDGET_REQUIRES_MANAGEMENT_REVIEW")
    def test_current_source_verified_finish_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            r=cycle(root,{"tasks":[t()]},G,commit="a"*40)
            self.assertEqual(r["official_verified_finish"],"HOLD_DONECHECK_HUMAN_GATE")

    def test_repair_candidate_second_verification_and_owner_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sub=root/"governance/controller/work";sub.mkdir(parents=True)
            (sub/"fix.txt").write_bytes(b"old\n")
            item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
                   expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
                   replace_from="old",replace_to="new")
            result=cycle(root,{"tasks":[item]},G,commit="a"*40)
            self.assertEqual(result["state"],"PR_PENDING")
            self.assertEqual(result["verification"]["proof"],"REPAIR_INDEPENDENT_RECOMPUTE")
            self.assertFalse(result["authorized_merge"])
            self.assertEqual((sub/"fix.txt").read_bytes(),b"old\n")
            (sub/"fix.txt").write_bytes(b"new\n")
            self.assertEqual(cycle(root,{"tasks":[item]},G,commit="a"*40)["state"],"PASS")
    def test_repair_wrong_digest_holds(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sub=root/"governance/controller/work";sub.mkdir(parents=True)
            (sub/"fix.txt").write_bytes(b"old\n")
            item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
                   expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256="0"*64,
                   replace_from="old",replace_to="new")
            self.assertEqual(cycle(root,{"tasks":[item]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_repair_scope_is_explicit(self):
        self.assertEqual(cycle(Path("."),{"tasks":[t(action="propose_exact_repair")]},G)["reason"],"REPAIR_PATH_GRANT")
    def test_pending_blocks_repeat_without_unlocking_dependencies(self):
        item=t()
        root=Path(".")
        self.assertEqual(select({"tasks":[item]},set(),{item["id"]})[1],"NO_READY_TASK")
        child=t(id="LABORY_SECOND",dependencies=[item["id"]])
        self.assertEqual(select({"tasks":[item,child]},set(),{item["id"]})[1],"NO_READY_TASK")
    def test_repair_contract_alters_fingerprint(self):
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256="1"*64,desired_sha256="2"*64,replace_from="old",replace_to="new")
        self.assertNotEqual(key(item),key({**item,"replace_to":"different"}))
if __name__=="__main__":unittest.main()
