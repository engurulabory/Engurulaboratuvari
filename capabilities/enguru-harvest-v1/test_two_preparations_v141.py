"""Counter-evaluate both Zulfikar V1.4.1 PREPARATION scopes; never mint field PASS."""
import copy
import json
import unittest
from pathlib import Path
from verify_two_preparations_v141 import (
    assess,contract_guard,git_reader,V3,GATES,
)

HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE/"TWO_PREPARATION_100_V141.json").read_text(encoding="utf-8"))

class TwoPreparationTests(unittest.TestCase):
    def test_eight_gates_five_checks_each(self):
        self.assertIsNone(contract_guard(CONTRACT))
        for name in ("github","osi"):
            stages=CONTRACT["tracks"][name]["stages"]
            self.assertEqual([x["id"] for x in stages],list(GATES))
            self.assertEqual([len(x["required_evidence"]) for x in stages],[5]*8)
            self.assertEqual(len({x["check_id"] for s in stages for x in s["required_evidence"]}),40)
    def test_actual_git_head_preparation_100(self):
        r=assess(CONTRACT,git_reader)
        self.assertEqual(r["state"],"PASS_BOTH_PREPARATIONS_100_OF_100")
        self.assertEqual([r["tracks"][x]["score"] for x in ("github","osi")],[100,100])
        self.assertEqual([sum(s["checked"] for s in r["tracks"][x]["gates"]) for x in ("github","osi")],[40,40])
    def test_real_finish_remains_hold(self):
        r=assess(CONTRACT,git_reader)
        self.assertEqual(r["official_verified_finish"],"HOLD")
        self.assertEqual(r["owner_threshold"],"HOLD")
        self.assertEqual(r["source_reuse_authority"],"HOLD")
        self.assertEqual((r["mac_execution"],r["main_merge"]),(0,0))
    def test_historical_score_not_overwritten(self):
        self.assertEqual(CONTRACT["base_historic_score"],{"github_application_evidence":65,"osi_prefield_evidence":60})
    def test_mutated_owner_fails(self):
        c={**CONTRACT,"owner":"another-owner"}
        self.assertEqual(assess(c,git_reader)["reason"],"AUTHORITY")
    def test_mutated_field_execution_fails(self):
        for field,value in (("mac_execution",1),("main_merge",1),("mandatory_paid_api",1),
                            ("measured_official_proven_skills",12),("peer_reviewer_new_required",True)):
            c={**CONTRACT,field:value}
            self.assertEqual(assess(c,git_reader)["reason"],"AUTHORITY")
    def test_forged_verified_finish_fails(self):
        for field in ("official_verified_finish","source_rights_acceptance","real_user_acceptance"):
            c={**CONTRACT,field:"PASS"}
            self.assertEqual(assess(c,git_reader)["reason"],"AUTHORITY")
    def test_future_gate_cannot_skip_predecessor(self):
        c=copy.deepcopy(CONTRACT)
        c["tracks"]["github"]["stages"][2]["id"]="A05"
        self.assertEqual(assess(c,git_reader)["reason"],"GATE_ORDER")
    def test_missing_control_fails(self):
        c=copy.deepcopy(CONTRACT)
        c["tracks"]["osi"]["stages"][-1]["required_evidence"].pop()
        self.assertEqual(assess(c,git_reader)["reason"],"FIVE_CONTROLS")
    def test_duplicate_file_credit_fails(self):
        c=copy.deepcopy(CONTRACT)
        checks=c["tracks"]["github"]["stages"][0]["required_evidence"]
        checks[2]["source_path"]=checks[1]["source_path"]
        self.assertEqual(assess(c,git_reader)["reason"],"UNSAFE_EVIDENCE_PATH")
    def test_escape_path_fails(self):
        c=copy.deepcopy(CONTRACT)
        c["tracks"]["github"]["stages"][0]["required_evidence"][0]["source_path"]="../secret"
        self.assertEqual(assess(c,git_reader)["reason"],"UNSAFE_EVIDENCE_PATH")
    def test_nonexistent_source_fails(self):
        c=copy.deepcopy(CONTRACT)
        c["tracks"]["github"]["stages"][0]["required_evidence"][0]["source_path"]="capabilities/enguru-harvest-v1/does-not-exist-v141.txt"
        self.assertTrue(assess(c,git_reader)["reason"].startswith("EVIDENCE_MISSING:"))
    def test_canonical_drift_fails(self):
        def bad_reader(path):
            if path==V3:
                return b"wrong canonical"
            return git_reader(path)
        self.assertEqual(assess(CONTRACT,bad_reader)["reason"],"CANONICAL_SHA")
    def test_false_real_user_receipt_fails(self):
        def bad_reader(path):
            data=git_reader(path)
            if path.endswith("/PILOT_APPLICATION_PREP_V141.json"):
                val=json.loads(data)
                val["actual_user_receipts"]=5
                return json.dumps(val).encode()
            return data
        self.assertEqual(assess(CONTRACT,bad_reader)["reason"],"FIVE_PILOT_INPUT_AND_STOP")
    def test_license_auto_adoption_fails(self):
        def bad_reader(path):
            data=git_reader(path)
            if path.endswith("/root_license_observations.json"):
                val=json.loads(data)
                val["observations"][0]["redistribution_approval"]="PASS"
                return json.dumps(val).encode()
            return data
        self.assertEqual(assess(CONTRACT,bad_reader)["reason"],"LICENSE_USE_RIGHTS_HOLD")
    def test_simulated_real_product_finish_fails(self):
        def bad_reader(path):
            data=git_reader(path)
            if path.endswith("/ZULFIKAR_V131_100_GATE_CONTRACT.json"):
                val=json.loads(data)
                val["github"]["state"]="PASS"
                return json.dumps(val).encode()
            return data
        self.assertEqual(assess(CONTRACT,bad_reader)["reason"],"CANONICAL_PRODUCT_FINISH_HOLD")
    def test_v141_source_identity_fails(self):
        c={**CONTRACT,"source_commit":"f"*40}
        self.assertEqual(assess(c,git_reader)["reason"],"AUTHORITY")
    def test_narrow_stage_label_scope(self):
        c=copy.deepcopy(CONTRACT)
        c["tracks"]["osi"]["stages"][-1]["stage_pass_scope"]="FIELD_PASS"
        self.assertEqual(assess(c,git_reader)["reason"],"GATE_ORDER")

if __name__=="__main__":
    unittest.main()
