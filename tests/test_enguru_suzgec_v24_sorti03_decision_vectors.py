"""Four non-authorizing decision parity vectors matching Mac SORTI03 v1."""
import unittest
import hashlib
import json
def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
from tools.enguru_suzgec_v24_goal_acceptance_loop import decide

def vectors():
    c={"criterion_id":"C01","evidence_requirement":"verified receipt","pass_threshold":"PASS","verifier":"existing OSi verifier","authority_requirement":"existing native authority","result":"PASS","evidence_verified":True}
    b={"goal_id":"SORTI03_PARITY","goal_statement":"Verify bounded decision parity","scope_version":"v1","owner":"human","criteria":[c],"acceptance_locked":True,"source_verified":True,"value_preserved":True,"negative_simulation_verified":True,"existing_finish_gates":{"T01":"PASS","T02":"PASS","T03":"PASS","T04":"PASS"},"authenticated_human_threshold":False,"native_verified_finish":False,"field_provenance_verified":False,"retry_count":0,"retry_limit":1}
    return {"VALID_GOAL_NO_NATIVE_AUTHORITY":b,"EMPTY_GOAL":{**b,"goal_statement":""},"MISSING_EVIDENCE":{**b,"criteria":[{**c,"evidence_verified":False}]},"MISSING_GATE":{**b,"existing_finish_gates":{**b["existing_finish_gates"],"T04":"HOLD"}}}

EXPECTED={"VALID_GOAL_NO_NATIVE_AUTHORITY":"NATIVE_FINISH_AUTHORITY_HOLD","EMPTY_GOAL":"GOAL_LOCK_INCOMPLETE","MISSING_EVIDENCE":"CRITERION_NOT_VERIFIED","MISSING_GATE":"EXISTING_GATES_HOLD"}
class Sorti03DecisionVectors(unittest.TestCase):
    def test_exact_inputs_match_mac_receipt(self):
        self.assertEqual(canonical_sha(vectors()),"90809ed4de0d10a2b3b196159b3dedd00b240b9fdebb79d44dae87b609becf07")
    def test_full_outputs_match_mac_receipt(self):
        results={name:decide(v) for name,v in vectors().items()}
        self.assertEqual(canonical_sha(results),"a189a196a9d97137a568d66efcfee5ae09d7750cd5a9477e93f1303417828c5f")
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
