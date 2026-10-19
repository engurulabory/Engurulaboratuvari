"""Four non-authorizing decision parity vectors matching Mac SORTI03 v1."""
import unittest
from tools.enguru_suzgec_v24_goal_acceptance_loop import decide

def vectors():
    c={"criterion_id":"C01","evidence_requirement":"verified receipt","pass_threshold":"PASS","verifier":"existing OSi verifier","authority_requirement":"existing native authority","result":"PASS","evidence_verified":True}
    b={"goal_id":"SORTI03_PARITY","goal_statement":"Verify bounded decision parity","scope_version":"v1","owner":"human","criteria":[c],"acceptance_locked":True,"source_verified":True,"value_preserved":True,"negative_simulation_verified":True,"existing_finish_gates":{"T01":"PASS","T02":"PASS","T03":"PASS","T04":"PASS"},"authenticated_human_threshold":False,"native_verified_finish":False,"field_provenance_verified":False,"retry_count":0,"retry_limit":1}
    return {"VALID_GOAL_NO_NATIVE_AUTHORITY":b,"EMPTY_GOAL":{**b,"goal_statement":""},"MISSING_EVIDENCE":{**b,"criteria":[{**c,"evidence_verified":False}]},"MISSING_GATE":{**b,"existing_finish_gates":{**b["existing_finish_gates"],"T04":"HOLD"}}}

EXPECTED={"VALID_GOAL_NO_NATIVE_AUTHORITY":"NATIVE_FINISH_AUTHORITY_HOLD","EMPTY_GOAL":"GOAL_LOCK_INCOMPLETE","MISSING_EVIDENCE":"CRITERION_NOT_VERIFIED","MISSING_GATE":"EXISTING_GATES_HOLD"}
class Sorti03DecisionVectors(unittest.TestCase):
    def test_four_decisions(self):
        for name,work in vectors().items():
            with self.subTest(name=name):
                result=decide(work)
                self.assertEqual(result["state"],"HOLD_GUVENLI_DUR")
                self.assertEqual(result["blockers"],[EXPECTED[name]])
                self.assertEqual(result["verifiedFinish"],"HOLD")
    def test_no_fabricated_authority(self):
        self.assertTrue(all(decide(v)["authority"]=="NATIVE_OSi_ONLY" for v in vectors().values()))
if __name__=="__main__": unittest.main()
