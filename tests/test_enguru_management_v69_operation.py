import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/"tools/enguru_management_v69_operation.py"
s=importlib.util.spec_from_file_location("enguru_operation",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def item():
 return {"schema":"enguru.management-v69.operational-observation/v1","task_id":"LABORY_SAFE_REPAIR",
 "source_commit":"a"*40,"receipt_comment_id":100,"producer_run_id":1,
 "worker_job_id":2,"worker_job_conclusion":"success","receipt_state":"PASS",
 "receipt_verification":"PASS","receipt_full_sha256":"b"*64,"public_receipt_sha256":"c"*64,
 "donecheck_state":"HOLD_EXTERNAL_DONECHECK_V1_2","official_finish":"HOLD_DONECHECK_HUMAN_GATE",
 "task_owner_acceptance":"HOLD"}
class TestOperationalObservation(unittest.TestCase):
 def test_canonical(self):
  r=m.evaluate(item(),{"LABORY_SAFE_REPAIR"})
  self.assertEqual(r["state"],"PASS_RECORDED_OPERATION_PROVENANCE_OFFICIAL_HOLD")
  self.assertEqual(r["official_finish"],"HOLD")
 def test_foreign_task(self):
  self.assertEqual(m.evaluate(item(),{"OTHER"})["reason"],"TASK_ID_UNBOUND")
 def test_tampered_hash(self):
  r=item();r["receipt_full_sha256"]="x"
  self.assertEqual(m.evaluate(r,{"LABORY_SAFE_REPAIR"})["reason"],"INVALID_RECEIPT_DIGEST")
 def test_failed_worker(self):
  r=item();r["worker_job_conclusion"]="failure"
  self.assertEqual(m.evaluate(r,{"LABORY_SAFE_REPAIR"})["reason"],"OBSERVED_EXECUTION_UNPROVEN")
 def test_fake_owner_pass(self):
  r=item();r["task_owner_acceptance"]="PASS"
  self.assertEqual(m.evaluate(r,{"LABORY_SAFE_REPAIR"})["reason"],"FALSE_FINAL_ACCEPTANCE")
 def test_fake_donecheck_pass(self):
  r=item();r["donecheck_state"]="PASS"
  self.assertEqual(m.evaluate(r,{"LABORY_SAFE_REPAIR"})["reason"],"FALSE_FINAL_ACCEPTANCE")

 def live_fixture(self):
  import hashlib,json
  r=item();src=b"ENGURU_CYCLE_PILOT=VERIFIED\n"
  task={"id":"LABORY_SAFE_REPAIR","action":"propose_exact_repair","path":m.SOURCE,
   "expected_sha256":"0"*64,"desired_sha256":m.sha(src),"replace_from":"PENDING",
   "replace_to":"VERIFIED","dependencies":[],"target_repo":m.REPO,
   "acceptance_version":"v3.1","existing_pr_number":196}
  values={k:task.get(k) for k in m.FIELDS}
  values["observed_source_sha256"]=m.sha(src);values["source_commit"]=r["source_commit"]
  fp=m.sha(m.canonical(values).encode())
  pub={"schema":"enguru.controller.public_receipt.v1",
       "task_id":r["task_id"],"fingerprint":fp,"source_commit":r["source_commit"],
       "producer_run_id":str(r["producer_run_id"]),"producer_workflow":m.WORKFLOW,
       "full_receipt_sha256":r["receipt_full_sha256"],"official_verified_finish":"HOLD_DONECHECK_HUMAN_GATE",
       "donecheck_producer_candidate":{"doneCheckResult":"HOLD_EXTERNAL_DONECHECK_V1_2","humanThresholdRequired":True,"finalState":"HOLD"},
       "verification":{"state":"PASS"},"engineering":{"state":"PASS"}}
  r["public_receipt_sha256"]=m.sha(m.canonical(pub).encode())
  body=(f"<!-- ENGURU_CONTROLLER_V3:PASS:{r['task_id']}:{fp}:{r['producer_run_id']}:{r['source_commit']} -->\n"
        f"PUBLIC_RECEIPT_SHA256={r['public_receipt_sha256']}\n"
        + "```json\n"+m.canonical(pub)+"\n```")
  comment={"id":r["receipt_comment_id"],"user":{"login":m.BOT_LOGIN,"id":m.BOT_ID},
           "issue_url":"https://api.github.com/repos/"+m.REPO+"/issues/192","body":body}
  run={"id":r["producer_run_id"],"head_sha":r["source_commit"],"status":"completed","conclusion":"success",
       "path":m.WORKFLOW,"repository":{"full_name":m.REPO}}
  jobs={"jobs":[{"id":r["worker_job_id"],"name":"worker","run_id":r["producer_run_id"],
                  "status":"completed","conclusion":"success"}]}
  return r,comment,run,jobs,{"tasks":[task]},src,r["source_commit"]
 def test_live_valid_receipt_not_owner_pass(self):
  data=self.live_fixture()
  state=m.verify_live(*data)
  self.assertEqual(state["state"],"PASS_GITHUB_PROVENANCE_OFFICIAL_HOLD")
  self.assertEqual(state["official_finish"],"HOLD")
 def test_live_fake_bot_hold(self):
  data=list(self.live_fixture());data[1]["user"]["id"]=8
  self.assertEqual(m.verify_live(*data)["reason"],"GITHUB_BOT_AUTHOR_MISMATCH")
 def test_live_modified_source_hold(self):
  data=list(self.live_fixture());data[5]=b"tampered"
  self.assertEqual(m.verify_live(*data)["reason"],"OBSERVED_SOURCE_MISMATCH")
 def test_live_modified_receipt_hold(self):
  data=list(self.live_fixture());data[1]["body"]=data[1]["body"].replace("PUBLIC_RECEIPT_SHA256=","PUBLIC_RECEIPT_SHA256=0")
  self.assertEqual(m.verify_live(*data)["reason"],"RECEIPT_FORMAT")
 def test_live_wrong_run_hold(self):
  data=list(self.live_fixture());data[2]["head_sha"]="f"*40
  self.assertEqual(m.verify_live(*data)["reason"],"WORKFLOW_RUN_PROVENANCE")
 def test_live_wrong_job_hold(self):
  data=list(self.live_fixture());data[3]["jobs"][0]["conclusion"]="failure"
  self.assertEqual(m.verify_live(*data)["reason"],"WORKER_JOB_PROVENANCE")
 def test_evidence_write_once(self):
  import json,tempfile
  with tempfile.TemporaryDirectory() as root:
   dest=Path(root)/"evidence.json"
   expected={"state":"PASS_GITHUB_PROVENANCE_OFFICIAL_HOLD","official_finish":"HOLD"}
   m.write_once(dest,expected)
   self.assertEqual(json.loads(dest.read_text(encoding="utf-8")),expected)
   with self.assertRaises(FileExistsError):
    m.write_once(dest,{"official_finish":"PASS"})
   self.assertEqual(json.loads(dest.read_text(encoding="utf-8")),expected)
 def test_evidence_symlink_rejected(self):
  import tempfile
  with tempfile.TemporaryDirectory() as root:
   original=Path(root)/"canonical.txt"
   original.write_text("unchanged",encoding="utf-8")
   link=Path(root)/"evidence.json"
   link.symlink_to(original)
   with self.assertRaises((FileExistsError,OSError)):
    m.write_once(link,{"state":"PASS"})
   self.assertEqual(original.read_text(encoding="utf-8"),"unchanged")
if __name__=="__main__":unittest.main()
