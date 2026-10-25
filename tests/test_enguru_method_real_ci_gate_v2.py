"""Six real-GitHub verification boundaries, repeatability and false-PASS probes."""
import copy
import json
import unittest
from tools.enguru_method_real_ci_gate_v2 import (
    AREAS, REPO, RUN_ID, RUN_SHA, WORKFLOW_PATH, WORKFLOW_ID, SPEC, canonical, evaluate, digest
)

SHA="c"*40
TREE="d"*40

def records():
    commit={"sha":SHA,"url":"https://api.github.com/repos/"+REPO+"/commits/"+SHA,"commit":{"tree":{"sha":TREE}}}
    run={"id":RUN_ID,"head_sha":RUN_SHA,"event":"push","status":"completed",
         "conclusion":"success","head_repository":{"full_name":REPO},
         "repository":{"full_name":REPO},"path":WORKFLOW_PATH,"workflow_id":WORKFLOW_ID}
    return commit,run

class SixDomainDeterministicEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(SPEC.read_text(encoding="utf-8"))

    def evaluate(self, commit=None, run=None, spec=None, sha=SHA):
        default_commit,default_run=records()
        return evaluate(self.spec if spec is None else spec,sha,
                        default_commit if commit is None else commit,
                        default_run if run is None else run)

    def test_six_areas_each_have_exactly_sixteen_canonical_controls(self):
        r=self.evaluate()
        self.assertEqual(r["verdict"],"PASS_SOURCE_METHOD_VERIFIED_PRODUCTS_HOLD")
        self.assertEqual([x["area"] for x in r["areas"]],list(AREAS))
        self.assertEqual(r["pass_count_real_source"],6)
        self.assertEqual(r["pass_count_real_products"],0)
        for d in r["areas"]:
            with self.subTest(area=d["area"]):
                self.assertEqual(d["fixed_denominator"],16)
                self.assertEqual(len(set(d["acceptance_controls"])),16)
                self.assertEqual(d["real_product_task_controls_completed"],0)
                self.assertEqual(d["product_verified_finish"],"HOLD_ORIGINAL_REAL_TASK_EVIDENCE")
                self.assertEqual(d["real_owner_or_independent_review"],"HOLD")
                self.assertEqual(d["mac_osi_field"],"HOLD_NOT_EXECUTED")
                self.assertEqual(d["official_donecheck"],"HOLD_NOT_EXECUTED")

    def test_six_areas_same_snapshot_repeatable(self):
        r=self.evaluate()
        for _ in range(4):
            self.assertEqual(canonical(r),canonical(self.evaluate()))
            self.assertEqual(r["receipt_sha256"],self.evaluate()["receipt_sha256"])
        self.assertEqual(r["receipt_sha256"],digest({k:v for k,v in r.items() if k!="receipt_sha256"}))

    def test_six_areas_wrong_source_commit_holds(self):
        c,r=records()
        c["sha"]="0"*40
        self.assertEqual(self.evaluate(commit=c)["verdict"],"HOLD_INSUFFICIENT_REAL_GITHUB_EVIDENCE")

    def test_six_areas_bad_source_tree_holds(self):
        c,r=records()
        c["commit"]["tree"]["sha"]="bad-tree"
        self.assertEqual(self.evaluate(commit=c)["pass_count_real_source"],0)

    def test_six_areas_mismatched_ci_run_holds(self):
        c,r=records()
        r["head_sha"]="f"*40
        self.assertEqual(self.evaluate(run=r)["pass_count_real_source"],0)

    def test_six_areas_failed_ci_holds(self):
        c,r=records()
        r["conclusion"]="failure"
        self.assertEqual(self.evaluate(run=r)["verdict"],"HOLD_INSUFFICIENT_REAL_GITHUB_EVIDENCE")

    def test_six_areas_wrong_issuer_repo_holds(self):
        c,r=records()
        r["head_repository"]["full_name"]="untrusted/forgery"
        self.assertEqual(self.evaluate(run=r)["pass_count_real_source"],0)

    def test_six_areas_running_ci_cannot_claim_pass(self):
        c,r=records()
        r["status"]="in_progress"
        self.assertEqual(self.evaluate(run=r)["verdict"],"HOLD_INSUFFICIENT_REAL_GITHUB_EVIDENCE")

    def test_six_areas_wrong_source_input_holds(self):
        self.assertEqual(self.evaluate(sha="HEAD")["verdict"],"HOLD_CANONICAL_OR_SHA_INPUT")

    def test_six_areas_changed_canonical_denominator_holds(self):
        spec=copy.deepcopy(self.spec)
        spec["shared_controls"].pop()
        self.assertEqual(self.evaluate(spec=spec)["verdict"],"HOLD_CANONICAL_OR_SHA_INPUT")

    def test_six_areas_duplicate_control_holds(self):
        spec=copy.deepcopy(self.spec)
        spec["domains"][1]["domain_controls"][2]["id"]=spec["domains"][1]["domain_controls"][0]["id"]
        self.assertEqual(self.evaluate(spec=spec)["verdict"],"HOLD_FIXED_SCOPE")

    def test_six_areas_marked_product_pass_cannot_affect_result(self):
        spec=copy.deepcopy(self.spec)
        spec["claimed_100_percent"]=True
        self.assertEqual(self.evaluate(spec=spec)["pass_count_real_products"],0)
        self.assertEqual(self.evaluate(spec=spec)["verdict"],"PASS_SOURCE_METHOD_VERIFIED_PRODUCTS_HOLD")

    def test_six_areas_untrusted_ci_check_is_not_real_product_pass(self):
        r=self.evaluate()
        for d in r["areas"]:
            self.assertNotEqual(d["product_verified_finish"],"PASS")
        self.assertEqual(r["safety"],"PRODUCT_PASS_REQUIRES_ITS_OWN_REAL_EVIDENCE_AND_AUTHORITY")

    def test_contract_semantics_mutations_hold_in_all_six_areas(self):
        # One unchanged denominator can still hide rewritten acceptance semantics.
        for index in range(36):
            for field in ("id", "key", "required", "negative"):
                spec=copy.deepcopy(self.spec)
                controls=spec["shared_controls"] if index<12 else spec["domains"][(index-12)//4]["domain_controls"]
                control=controls[index if index<12 else (index-12)%4]
                control[field]="FORGED_ACCEPTANCE"
                with self.subTest(index=index,field=field):
                    self.assertEqual(self.evaluate(spec=spec)["verdict"],"HOLD_FIXED_SCOPE")

    def test_wrong_workflow_and_repository_hold(self):
        for key,value in (("path","wrong.yml"),("workflow_id",0),
                          ("repository",{"full_name":"untrusted/forgery"})):
            c,r=records();r[key]=value
            with self.subTest(key=key):
                self.assertEqual(self.evaluate(run=r)["pass_count_real_source"],0)
        c,r=records();c["url"]="https://api.github.com/repos/untrusted/forgery/commits/"+SHA
        self.assertEqual(self.evaluate(commit=c)["pass_count_real_source"],0)

    def test_malformed_contracts_return_hold(self):
        for value in (None,False,17,"invalid",{},[] ,{"shared_controls":None},
                      {"shared_controls":[None]*12,"domains":[None]*6}):
            with self.subTest(value=value):
                c,r=records()
                self.assertTrue(evaluate(value,SHA,c,r)["verdict"].startswith("HOLD"))
        for field in ("shared_controls","domains"):
            spec=copy.deepcopy(self.spec);spec[field]=None
            self.assertTrue(self.evaluate(spec=spec)["verdict"].startswith("HOLD"))

    def test_malformed_api_snapshots_return_hold(self):
        for bad in (None,False,[],"bad",{"commit":None},{"commit":{"tree":None}}):
            c,r=records()
            self.assertEqual(evaluate(self.spec,SHA,bad,r)["pass_count_real_source"],0)
            self.assertEqual(evaluate(self.spec,SHA,c,bad)["pass_count_real_source"],0)

    def test_receipt_binds_snapshots_and_reserves_current_ci(self):
        c,r=records();first=self.evaluate(commit=c,run=r)
        c["commit"]["message"]="different observed evidence"
        second=self.evaluate(commit=c,run=r)
        self.assertNotEqual(first["receipt_sha256"],second["receipt_sha256"])
        self.assertTrue(first["current_commit_ci"].startswith("HOLD"))
        self.assertEqual(first["pass_count_real_products"],0)

if __name__=="__main__":
    unittest.main()
