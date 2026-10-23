"""Adversarial review-only tests for A03 design gate."""
import unittest
from tools.arge_a03_preflight_v419 import assess_a03, GATES

def fixture():
    x = {"task_id":"A03","source_commit":"1"*40,"artifact_sha256":"a"*64,"producer_id":"producer","reviewer_id":"reviewer"}
    for k in GATES:
        x[k] = True
        x[k+"_evidence_ref"] = "evidence://" + k
    return x

class A03PreflightTests(unittest.TestCase):
    def test_reference_complete_is_advisory_only(self):
        r=assess_a03(fixture())
        self.assertEqual(r["state"],"EVIDENCE_REFERENCES_READY_FOR_INDEPENDENT_VERIFICATION")
        self.assertFalse(r["official_acceptance"])
        self.assertFalse(r["verified_finish"])

    def test_each_missing_gate_holds(self):
        for g in GATES:
            with self.subTest(gate=g):
                x=fixture(); x[g]=False
                self.assertEqual(assess_a03(x)["state"],"HOLD")

    def test_each_missing_provenance_holds(self):
        for g in GATES:
            with self.subTest(gate=g):
                x=fixture(); x[g+"_evidence_ref"]=""
                self.assertEqual(assess_a03(x)["state"],"HOLD")

    def test_fake_source_format_holds(self):
        x=fixture();x["source_commit"]="invalid"
        self.assertEqual(assess_a03(x)["state"],"HOLD")

    def test_duplicate_reviewer_holds(self):
        x=fixture();x["reviewer_id"]=x["producer_id"]
        self.assertEqual(assess_a03(x)["state"],"HOLD")

    def test_scope_mismatch_holds(self):
        x=fixture();x["task_id"]="P06"
        self.assertEqual(assess_a03(x)["state"],"HOLD")

if __name__=="__main__":
    unittest.main()
