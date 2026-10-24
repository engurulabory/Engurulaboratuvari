import importlib.util
import json
import pathlib
import unittest

p=pathlib.Path(__file__).resolve().parents[1]/"tools"/"enguru_management_v69_source_adapter.py"
s=importlib.util.spec_from_file_location("v69_adapter",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
COMMIT="a"*40
def valid():
    t={"tasks":[{"id":"TASK_A","state":"PAUSED_AUDITED","action":"verify_file_digest",
                 "target_repo":m.EXPECTED_REPO,"path":"governance/controller/PILOT_SOURCE.txt",
                 "dependencies":[]}]}
    g={"repository":m.EXPECTED_REPO,"state":"ENABLED_BOUNDED_PR"}
    return json.dumps(t).encode(),json.dumps(g).encode()

class AdapterTests(unittest.TestCase):
    def test_source_bound_inventory(self):
        t,g=valid();r=m.reconcile(t,g,"main",COMMIT)
        self.assertEqual(r["state"],"PASS_SOURCE_BOUND_MANAGEMENT_INVENTORY")
        self.assertEqual(r["task_count"],1)
        self.assertEqual(r["independently_accepted"],0)
        self.assertEqual(r["tasks"][0]["management_state"],"OBSERVED_ONLY")
    def test_no_source_commit_hold(self):
        t,g=valid()
        self.assertEqual(m.reconcile(t,g,"main","HEAD")["reason"],"COMMIT_PIN_REQUIRED")
    def test_wrong_repo_hold(self):
        t,g=valid();g=json.dumps({"repository":"other/repo"}).encode()
        self.assertEqual(m.reconcile(t,g,"main",COMMIT)["reason"],"CONTROLLER_CONTRACT_MISMATCH")
    def test_duplicate_id_hold(self):
        t,g=valid();x=json.loads(t);x["tasks"].append(x["tasks"][0])
        self.assertEqual(m.reconcile(json.dumps(x).encode(),g,"main",COMMIT)["reason"],"TASK_AUTHORITY_INVALID")
    def test_unknown_dependency_hold(self):
        t,g=valid();x=json.loads(t);x["tasks"][0]["dependencies"]=["UNKNOWN"]
        self.assertEqual(m.reconcile(json.dumps(x).encode(),g,"main",COMMIT)["reason"],"DEPENDENCY_CONTRACT_INVALID")
    def test_invalid_json_hold(self):
        _,g=valid()
        self.assertEqual(m.reconcile(b"invalid",g,"main",COMMIT)["reason"],"SOURCE_JSON_INVALID")
    def test_no_fake_operational_acceptance(self):
        t,g=valid();x=json.loads(t);x["tasks"][0]["state"]="READY"
        r=m.reconcile(json.dumps(x).encode(),g,"main",COMMIT)
        self.assertEqual(r["operational_acceptance"],"HOLD_INDEPENDENT_OPERATION_ACCEPTANCE")
        self.assertEqual(r["github_writes"],0)
if __name__=="__main__":unittest.main()
