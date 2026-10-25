"""Real executable, isolated tests of 12 local kernel operations."""
import json
import hashlib
import unittest
from pathlib import Path
from skill_kernel import execute, OPERATIONS

HERE=Path(__file__).resolve().parent
REGISTRY=json.loads((HERE/"source_candidates.json").read_text(encoding="utf-8"))

class SkillKernelTests(unittest.TestCase):
    def test_01_fingerprint(self):
        value=execute("fingerprint",{"utf8_text":"ENGURU"})
        self.assertEqual(value["sha256"],hashlib.sha256(b"ENGURU").hexdigest())
        self.assertEqual(execute("fingerprint",{"utf8_text":[]})["state"],"HOLD")
    def test_02_source_url(self):
        self.assertEqual(execute("source-url",{"url":"https://github.com/openai/codex"})["state"],"CHECKED")
        self.assertEqual(execute("source-url",{"url":"http://example.com"})["state"],"HOLD")
    def test_03_source_candidate(self):
        r={"id":"A","library":"skills","source_url":"https://example.org/a",
           "source_sha256":"a"*64,"license":"MIT","security_review":"PASS","mandatory_paid_api":0,
           "independent_review":"PASS","human_authority":"PASS"}
        self.assertEqual(execute("source-candidate",{"record":r})["state"],"CANDIDATE")
    def test_04_catalog(self):
        self.assertEqual(execute("catalog-check",REGISTRY)["state"],"CATALOG_FORMAT_PASS")
        bad=json.loads(json.dumps(REGISTRY))
        bad["candidates"][1]["repository"]=bad["candidates"][0]["repository"]
        self.assertEqual(execute("catalog-check",bad)["state"],"HOLD")
    def test_05_duplicates(self):
        self.assertEqual(execute("duplicate-check",{"identifiers":["a","b","a"]})["state"],"HOLD")
        self.assertEqual(execute("duplicate-check",{"identifiers":["a","b"]})["state"],"UNIQUE")
    def test_06_license(self):
        self.assertEqual(execute("license-triage",{"license_status":"UNVERIFIED"})["state"],"HOLD")
        self.assertEqual(execute("license-triage",{"license_status":"VERIFIED_WITH_PIN_AND_REVIEW","review_receipt_verified":True})["state"],"REVIEW_CANDIDATE")
    def test_07_cost(self):
        self.assertEqual(execute("cost-bound",{"mandatory_paid_api":0,"compute_budget_recorded":True})["state"],"BUDGET_CONTRACT_PASS")
        self.assertEqual(execute("cost-bound",{"mandatory_paid_api":0,"compute_budget_recorded":False})["state"],"HOLD")
    def test_08_prompt(self):
        p={"state":"CANDIDATE","claim":"test","evidence":"source","next_action":"verify"}
        self.assertEqual(execute("prompt-audit",{"prompt":p})["state"],"STRUCTURE_PASS")
        self.assertEqual(execute("prompt-audit",{"prompt":{"claim":"foo"}})["state"],"HOLD")
    def test_09_readme_drift(self):
        a="a"*40
        self.assertEqual(execute("readme-drift",{"recorded_git_blob_sha1":a,"observed_git_blob_sha1":a})["state"],"MATCH_RECORDED_README")
        self.assertEqual(execute("readme-drift",{"recorded_git_blob_sha1":a,"observed_git_blob_sha1":"b"*40})["state"],"HOLD")
    def test_10_evidence_bytes(self):
        self.assertEqual(execute("evidence-bytes",{"manifest":{},"assets":{}})["state"],"HOLD")
        self.assertEqual(execute("evidence-bytes",{"manifest":{},"assets":{"a":"GG"}})["state"],"HOLD")
    def test_11_paired_gain(self):
        run={"task_id":"one","baseline_success":True,"candidate_success":True,"baseline_seconds":10,
             "candidate_seconds":9,"baseline_quality":90,"candidate_quality":90}
        self.assertEqual(execute("paired-gain",{"paired_runs":[run]*5})["state"],"MEASURED_GAIN_CANDIDATE")
        self.assertEqual(execute("paired-gain",{"paired_runs":[run]*4})["state"],"HOLD")
        self.assertEqual(execute("paired-gain",{"paired_runs":[{**run,"candidate_quality":88}]*5})["state"],"HOLD")
    def test_12_osi_handoff(self):
        self.assertEqual(execute("osi-handoff",{"osi_executed":False})["state"],"HANDOFF_PREPARATION_ONLY")
        self.assertEqual(execute("osi-handoff",{"osi_executed":True})["state"],"HOLD")
    def test_operation_count_and_missing(self):
        self.assertEqual(len(OPERATIONS),12)
        self.assertEqual(execute("unexpected",{})["state"],"HOLD")
    def test_catalog_unverified(self):
        self.assertTrue(all(x["license"]=="UNVERIFIED" for x in REGISTRY["candidates"]))
        self.assertTrue(all(x["source_commit_sha"] is None for x in REGISTRY["candidates"]))
        self.assertEqual(REGISTRY["record_count"],30)

if __name__=="__main__":
    unittest.main()
