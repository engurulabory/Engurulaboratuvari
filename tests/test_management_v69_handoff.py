import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from management_v69_handoff_verify import validate,three_rounds
BASE={"schema":"enguru.management.handoff/v1","task_id":"ENGURU_MANAGEMENT_V69_PR_203","source_commit":"a"*40,"source_sha256":"b"*64,"required_evidence":["source","test"],"executor_scope":"GITHUB_REVIEW_ONLY","rollback_plan":"Restore SHA-verified prior files","reviewer":"independent","producer":"engineer","authority_ref":"HOLD_OWNER_GRANT","previous_state":"HOLD","acceptance":"HOLD","target_inventory_sha256":"c"*64}
class HandoffTests(unittest.TestCase):
 def test_valid_review_only(self):self.assertEqual(validate(BASE),"PASS_REVIEW_SCHEMA_ONLY")
 def test_reject_extra_field(self):
  x=dict(BASE,bypass=True);self.assertEqual(validate(x),"HOLD_SCHEMA")
 def test_reject_self_review(self):
  x=dict(BASE,reviewer="engineer");self.assertEqual(validate(x),"HOLD_REVIEW_INDEPENDENCE")
 def test_reject_authority_pass(self):
  x=dict(BASE,acceptance="PASS");self.assertEqual(validate(x),"HOLD_FALSE_ACCEPTANCE")
 def test_reject_osi_scope(self):
  x=dict(BASE,executor_scope="OSI_INSTALL");self.assertEqual(validate(x),"HOLD_SCOPE")
 def test_missing_inventory(self):
  x=dict(BASE,target_inventory_sha256="");self.assertEqual(validate(x),"HOLD_HASH")
 def test_missing_evidence(self):
  x=dict(BASE,required_evidence=[]);self.assertEqual(validate(x),"HOLD_EVIDENCE")
 def test_three_rounds_structure(self):
  r=[{"head":"a"*40,"run_id":str(i),"tests":10,"outcome":"PASS"} for i in range(3)]
  self.assertEqual(three_rounds(r),"PASS_THREE_RECEIPT_STRUCTURE_ONLY")
 def test_head_drift(self):
  r=[{"head":"a"*40,"run_id":str(i),"tests":10,"outcome":"PASS"} for i in range(3)]
  r[2]["head"]="b"*40
  self.assertEqual(three_rounds(r),"HOLD_EXACT_HEAD")
 def test_repeated_run(self):
  r=[{"head":"a"*40,"run_id":"same","tests":10,"outcome":"PASS"} for i in range(3)]
  self.assertEqual(three_rounds(r),"HOLD_RUN_ID")
 def test_failed_run(self):
  r=[{"head":"a"*40,"run_id":str(i),"tests":10,"outcome":"PASS"} for i in range(3)]
  r[1]["outcome"]="FAIL"
  self.assertEqual(three_rounds(r),"HOLD_TEST_EVIDENCE")
 def test_bool_test_count(self):
  r=[{"head":"a"*40,"run_id":str(i),"tests":True,"outcome":"PASS"} for i in range(3)]
  self.assertEqual(three_rounds(r),"HOLD_TEST_EVIDENCE")
if __name__=="__main__":unittest.main()
