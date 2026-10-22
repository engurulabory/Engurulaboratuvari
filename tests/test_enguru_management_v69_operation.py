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
if __name__=="__main__":unittest.main()
