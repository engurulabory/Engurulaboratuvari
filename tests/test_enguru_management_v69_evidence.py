"""Management V6.9: the source receipt is not independent CI authentication."""
import importlib.util
import unittest
from pathlib import Path

module_file = Path(__file__).resolve().parents[1] / "tools" / "enguru_management_v69_evidence.py"
spec = importlib.util.spec_from_file_location("management_evidence", module_file)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample():
    digests = {"governance/controller/TASKS.json": "a"*64,
               "governance/controller/ACTIVATION.json": "b"*64}
    tasks = {"tasks": [{"id": "TASK_A", "state": "PAUSED_AUDITED"}]}
    activation = {"human_final_authority": "OWNER"}
    ledger = {"schema": "enguru.management-v69.evidence-crosswalk/v1",
              "source_sha256": digests,
              "management_ci": {"workflow": "ENGURU Management V6.9 Review",
                                "conclusion": "success", "run_id": 17, "head_sha": "c"*40},
              "records": [{"task_id": "TASK_A", "observed_controller_state": "PAUSED_AUDITED",
                           "evidence_level": "B_CI_SOURCE_READ",
                           "task_execution_proven": False,
                           "independent_verifier": "HOLD",
                           "authority_acceptance": "HOLD"}]}
    return ledger, tasks, activation, digests


class EvidenceTests(unittest.TestCase):
    def test_ci_claim_never_counts_as_independently_verified(self):
        result = mod.validate(*sample())
        self.assertEqual(result["state"], "PASS_CROSSWALK_STRUCTURE_OFFICIAL_HOLD")
        self.assertTrue(result["ci_claim_recorded"])
        self.assertFalse(result["ci_read_verified"])
        self.assertEqual(result["official_finish"], "HOLD")
        self.assertEqual(result["authority_accepted"], 0)

    def test_forged_success_record_still_unverified(self):
        ledger, tasks, gate, digests = sample()
        ledger["management_ci"]["run_id"] = 999999999
        result = mod.validate(ledger, tasks, gate, digests)
        self.assertFalse(result["ci_read_verified"])
        self.assertEqual(result["ci_verification_reason"], "EXTERNAL_GITHUB_RUN_ATTESTATION_REQUIRED")

    def test_boolean_run_id_invalid(self):
        ledger, tasks, gate, digests = sample()
        ledger["management_ci"]["run_id"] = True
        result = mod.validate(ledger, tasks, gate, digests)
        self.assertEqual(result["reason"], "CI_RUN_ID")

    def test_source_drift_fails_closed(self):
        ledger, tasks, gate, digests = sample()
        ledger["source_sha256"] = dict(ledger["source_sha256"])
        ledger["source_sha256"]["governance/controller/TASKS.json"] = "0"*64
        result = mod.validate(ledger, tasks, gate, digests)
        self.assertEqual(result["reason"], "SOURCE_DRIFT")

    def test_fabricated_authority_fails_closed(self):
        ledger, tasks, gate, digests = sample()
        ledger["records"][0]["authority_acceptance"] = "PASS"
        result = mod.validate(ledger, tasks, gate, digests)
        self.assertEqual(result["reason"], "FALSE_ACCEPTANCE_CLAIM")


if __name__ == "__main__":
    unittest.main()
