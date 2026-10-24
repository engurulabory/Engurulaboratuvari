"""Concrete behavioral control cases; distinct assertions, no fabricated CI run."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.management_v69_pilot_dual_acceptance import assess, THEORY_KEYS, FIELD_KEYS
from tools.management_v69_pilot_proof_gates import verify_source, owner_gate
from tools.management_v69_triple100_gate import evaluate

class ConcretePilotControls(unittest.TestCase):
    def test_design_001_theory_field_separation(self):
        x=assess(dict.fromkeys(THEORY_KEYS,True),dict.fromkeys(FIELD_KEYS,True))
        self.assertEqual(x["field_state"],"FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED")
    def test_design_002_owner_boolean_is_not_signature(self):
        x=owner_gate({"state":"PASS_SOURCE_SHA256"},"engurulabory",True,True,True,True)
        self.assertEqual(x["reason"],"CANONICAL_VERIFIER_RECEIPT_REQUIRED")
    def test_design_003_owner_scope(self):
        x=owner_gate({"state":"PASS_SOURCE_SHA256"},"other")
        self.assertEqual(x["reason"],"OWNER_SCOPE")
    def test_design_004_no_osi_mutation(self):
        self.assertEqual(assess({}, {})["osi_mutation"],0)
    def test_theory_001_missing_input_holds(self):
        self.assertEqual(assess({}, {})["theory_state"],"THEORY_HOLD")
    def test_theory_002_false_ci_holds(self):
        t=dict.fromkeys(THEORY_KEYS,True);t["github_ci"]=False
        self.assertEqual(assess(t,{})["theory_state"],"THEORY_HOLD")
    def test_theory_003_strings_are_not_pass(self):
        self.assertEqual(assess(dict.fromkeys(THEORY_KEYS,"PASS"),{})["theory_state"],"THEORY_HOLD")
    def test_theory_004_source_before_authority(self):
        self.assertEqual(owner_gate({"state":"HOLD_GUVENLI_DUR"},"engurulabory")["reason"],"SOURCE_EVIDENCE_REQUIRED")
    def test_simulation_001_valid_real_source_sha(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source";p.write_bytes(b"source")
            self.assertEqual(verify_source(d,"source",hashlib.sha256(b"source").hexdigest())["state"],"PASS_SOURCE_SHA256")
    def test_simulation_002_changed_source_holds(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source";p.write_bytes(b"changed")
            self.assertEqual(verify_source(d,"source",hashlib.sha256(b"source").hexdigest())["reason"],"SOURCE_SHA_DRIFT")
    def test_simulation_003_escape_holds(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(verify_source(d,"../secret","a"*64)["reason"],"PATH_SCOPE")
    def test_simulation_004_missing_triple_control_holds(self):
        good={a:{f"{a}_{n:03d}":True for n in range(1,101)} for a in ("DESIGN","THEORY","SIMULATION")}
        good["SIMULATION"]["SIMULATION_004"]=False
        self.assertFalse(evaluate(good)["triple_theoretical_candidate"])

if __name__=="__main__":
    unittest.main()
