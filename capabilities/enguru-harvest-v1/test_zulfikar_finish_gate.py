"""Regression tests for Zulfikar 100-point design and authority boundaries."""
import copy
import json
import unittest
from pathlib import Path
from zulfikar_finish_gate import validate_contract, simulations
ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/"ZULFIKAR_V131_100_GATE_CONTRACT.json").read_text(encoding="utf-8"))

class FinishGateTests(unittest.TestCase):
    def test_exact_100_design_separate_official(self):
        r=validate_contract(C)
        self.assertEqual(r["state"],"PASS_DEFINITION_ONLY")
        self.assertEqual(r["scopes"]["github"]["definition_score"],100)
        self.assertEqual(r["scopes"]["osi"]["definition_score"],100)
        self.assertEqual(r["scopes"]["github"]["official_acceptance"],"HOLD")
    def test_three_real_logic_suites_10_each(self):
        sims=simulations(C)
        self.assertEqual([x["passed"] for x in sims.values()],[10,10,10])
        self.assertTrue(all(x["total"]==10 and x["state"]=="PASS_LOGICAL_ONLY" for x in sims.values()))
    def test_forged_evidence_fails(self):
        for scope in ("github","osi"):
            c=copy.deepcopy(C)
            c[scope]["controls"][0]["proof_sha256"]="a"*64
            self.assertEqual(validate_contract(c)["state"],"HOLD_FORGED_ACCEPTANCE")
    def test_issuer_owner_and_merge(self):
        for field,value in (("owner","other"),("issuer","NEW_ISSUER"),("main_merge",True),("osi_execution",True),
                            ("peer_review_required_for_github_technical",True)):
            c={**C,field:value}
            self.assertEqual(validate_contract(c)["state"],"HOLD_AUTHORITY")
    def test_only_existing_control_ids(self):
        c=copy.deepcopy(C)
        c["github"]["controls"][0]["id"]="G11"
        self.assertEqual(validate_contract(c)["state"],"HOLD_ID_OR_POINTS")
    def test_100_cannot_be_replaced_by_overscoring(self):
        c=copy.deepcopy(C)
        c["osi"]["controls"][1]["points"]=20
        self.assertEqual(validate_contract(c)["state"],"HOLD_ID_OR_POINTS")

if __name__=="__main__":
    unittest.main()
