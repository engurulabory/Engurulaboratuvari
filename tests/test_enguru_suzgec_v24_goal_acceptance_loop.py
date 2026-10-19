import unittest
from tools.enguru_suzgec_v24_goal_acceptance_loop import decide
def candidate():
 return {"goal_id":"G1","goal_statement":"Deliver scoped result","scope_version":"v1","owner":"owner",
 "acceptance_locked":True,"criteria":[{"criterion_id":"A1","evidence_requirement":"native receipt","pass_threshold":"exact match","verifier":"existing authorized verifier","authority_requirement":"valid scoped grant","result":"PASS","evidence_verified":True}],
 "source_verified":True,"value_preserved":True,"negative_simulation_verified":True,
 "existing_finish_gates":{"T01":"PASS","T02":"PASS","T03":"PASS","T04":"PASS"},
 "authenticated_human_threshold":True,"native_verified_finish":True,"field_provenance_verified":True}
class ContractLoopTests(unittest.TestCase):
 def test_empty_goal_holds(self):
  x=candidate();x["goal_statement"]="";self.assertEqual(decide(x)["next_stage"],"01")
 def test_unlocked_acceptance_holds(self):
  x=candidate();x["acceptance_locked"]=False;self.assertEqual(decide(x)["next_stage"],"03")
 def test_missing_criterion_evidence_holds(self):
  x=candidate();x["criteria"][0]["evidence_verified"]=False;self.assertEqual(decide(x)["state"],"HOLD_GUVENLI_DUR")
 def test_duplicate_acceptance_holds(self):
  x=candidate();x["criteria"].append(dict(x["criteria"][0]));self.assertEqual(decide(x)["state"],"HOLD_GUVENLI_DUR")
 def test_missing_existing_gate_holds(self):
  x=candidate();x["existing_finish_gates"]["T04"]="HOLD";self.assertEqual(decide(x)["state"],"HOLD_GUVENLI_DUR")
 def test_false_human_threshold_holds(self):
  x=candidate();x["authenticated_human_threshold"]=False;self.assertEqual(decide(x)["state"],"HOLD_GUVENLI_DUR")
 def test_retry_limit_halts(self):
  x=candidate();x["criteria"][0]["result"]="HOLD";x["retry_count"]=3;x["retry_limit"]=3
  self.assertEqual(decide(x)["next_action"],"STOP_AND_ASSIGN_BLOCKER_OWNER")
 def test_bounded_retry_returns_to_existing_stage(self):
  x=candidate();x["criteria"][0]["result"]="HOLD";x["retry_count"]=1;x["retry_limit"]=3
  self.assertEqual(decide(x)["next_action"],"REENTER_EXISTING_STAGE_WITHIN_SAME_LOCKED_SCOPE")
 def test_declared_all_pass_never_self_grants_bitirdi(self):
  r=decide(candidate());self.assertEqual(r["state"],"PASS_STATIC_FINISH_PREDICATES_ONLY")
  self.assertEqual(r["verifiedFinish"],"HOLD")
  self.assertNotEqual(r["state"],"BITTI_DUR")
if __name__=="__main__":unittest.main()
