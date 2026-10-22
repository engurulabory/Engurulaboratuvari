"""Fail-closed and coverage tests for V2 structural pre-send gate."""
import copy
import unittest

from tools.enguru_batch_evidence_gate_v2 import EvidenceError, evaluate


def make_ledger():
    checks = [{"id": f"B{i:02d}-{j:02d}", "name": f"original-{i}-{j}",
               "state": "HOLD", "evidence": None}
              for i in range(1, 11) for j in range(1, 11)]
    for row in checks[:27]:
        row["state"] = "PASS_EVIDENCE"
        row["evidence"] = "receipt"
    return {"total_units": 100, "verified_units": 27, "remaining_units": 73,
            "checks": checks}


def item(cid="B03-08", owner_required=True):
    return {"id": cid, "original_condition": "original-3-8",
            "claim": "PASS_CANDIDATE", "real_execution": "isolated real field result",
            "source_head": "a" * 40, "evidence_sha256": "b" * 64,
            "positive_test": {"state": "PASS", "receipt_sha256": "c" * 64},
            "negative_test": {"state": "PASS", "receipt_sha256": "d" * 64},
            "owner": {"required": owner_required,
                      "state": "APPROVED" if owner_required else "NOT_REQUIRED",
                      "receipt_sha256": "e" * 64 if owner_required else None}}


def packet(items=None):
    return {"schema": "enguru.batch.evidence/v2", "baseline": 27,
            "items": [item()] if items is None else items}


class BatchEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.ledger = make_ledger()

    def test_ready_is_only_candidate_not_acceptance(self):
        result = evaluate(self.ledger, packet())
        self.assertEqual(result["structurally_ready"], 1)
        self.assertEqual(result["official_pass_added"], 0)
        self.assertEqual(result["baseline"], 27)
        self.assertEqual(result["state"], "PRE_SEND_STRUCTURAL_CHECK_ONLY_NOT_AUTHORITY")

    def test_three_ready_of_eight_is_partial_and_preserves_counter(self):
        ids = [f"B04-{i:02d}" for i in range(1, 9)]
        records = []
        for cid in ids:
            x = item(cid)
            x["original_condition"] = next(z["name"] for z in self.ledger["checks"] if z["id"] == cid)
            records.append(x)
        for x in records[3:]:
            x["positive_test"]["state"] = "HOLD"
        result = evaluate(self.ledger, packet(records))
        self.assertEqual(result["candidates"], 8)
        self.assertEqual(result["structurally_ready"], 3)
        self.assertEqual(result["needs_completion"], 5)
        self.assertEqual(result["structural_coverage_percent"], 37.5)
        self.assertEqual(result["official_pass_added"], 0)

    def test_missing_negative_test_is_hold(self):
        p = packet()
        p["items"][0].pop("negative_test")
        result = evaluate(self.ledger, p)
        self.assertIn("NEGATIVE_TEST_RECEIPT", result["items"][0]["missing"])

    def test_unapproved_owner_is_hold(self):
        p = packet()
        p["items"][0]["owner"]["state"] = "HOLD"
        result = evaluate(self.ledger, p)
        self.assertIn("OWNER_APPROVED_SCOPE_RECEIPT", result["items"][0]["missing"])

    def test_false_not_required_owner_fails_classification(self):
        p = packet()
        p["items"][0]["owner"]["required"] = False
        self.assertIn("OWNER_NOT_REQUIRED_SCOPE", evaluate(self.ledger, p)["items"][0]["missing"])

    def test_no_owner_required_classifies_when_explicit(self):
        p = packet([item(owner_required=False)])
        self.assertEqual(evaluate(self.ledger, p)["structurally_ready"], 1)

    def test_malformed_sha_holds(self):
        p = packet()
        p["items"][0]["source_head"] = "not-a-commit"
        self.assertEqual(evaluate(self.ledger, p)["structurally_ready"], 0)

    def test_missing_real_execution_holds(self):
        p = packet()
        p["items"][0]["real_execution"] = ""
        self.assertIn("REAL_EXECUTION", evaluate(self.ledger, p)["items"][0]["missing"])

    def test_stale_baseline_rejected(self):
        p = packet()
        p["baseline"] = 26
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_accepted_id_rejected(self):
        p = packet()
        p["items"][0]["id"] = "B01-01"
        p["items"][0]["original_condition"] = "original-1-1"
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_wrong_original_condition_rejected(self):
        p = packet()
        p["items"][0]["original_condition"] = "replacement-condition"
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_duplicate_id_rejected(self):
        p = packet([item(), item()])
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_more_than_ten_rejected(self):
        p = packet()
        p["items"] = [item() for _ in range(11)]
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_fake_final_acceptance_rejected(self):
        p = packet()
        p["items"][0]["claim"] = "PASS_EVIDENCE"
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)
        p["items"][0]["claim"] = "PASS_CANDIDATE"
        p["verified_finish"] = True
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_counter_tampering_rejected(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["verified_units"] = 100
        with self.assertRaises(EvidenceError):
            evaluate(ledger, packet())

    def test_bool_baseline_rejected(self):
        p = packet()
        p["baseline"] = True
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, p)

    def test_zero_candidates_rejected(self):
        with self.assertRaises(EvidenceError):
            evaluate(self.ledger, packet([]))


if __name__ == "__main__":
    unittest.main()
