import copy
import json
from pathlib import Path
import unittest

from shared_ai.aggregate_closeout import TARGETS, assess_v06_aggregate


SCORECARD = Path(__file__).resolve().parents[1] / "evidence" / "mac-engineer" / "V06_PACKAGE5_AGGREGATE_SCORECARD.json"


class Package5AggregateCloseoutTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SCORECARD.read_text(encoding="utf-8"))

    def test_canonical_scorecard_meets_every_locked_target(self):
        result = assess_v06_aggregate(self.payload)
        self.assertEqual(result.state, "PASS", result.issues)
        for domain, target in TARGETS.items():
            self.assertGreaterEqual(self.payload["domains"][domain]["score"], target)
        self.assertEqual(self.payload["criticalFailures"]["unresolved"], 0)

    def test_operating_character_score_is_bound_to_locked_12_dimension_mean(self):
        dims = self.payload["operatingCharacterDimensions"]
        self.assertEqual(len(dims), 12)
        mean = round(sum(item["score"] for item in dims) / len(dims), 1)
        self.assertEqual(mean, self.payload["domains"]["operating_character"]["score"])
        broken = copy.deepcopy(self.payload)
        broken["domains"]["operating_character"]["score"] = 99.9
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("OPERATING_CHARACTER_MEAN_MISMATCH", result.issues)

    def test_score_below_locked_target_holds(self):
        broken = copy.deepcopy(self.payload)
        broken["domains"]["engineering_foundations"]["score"] = 97.9
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("TARGET_NOT_MET:engineering_foundations", result.issues)

    def test_target_drift_holds(self):
        broken = copy.deepcopy(self.payload)
        broken["domains"]["persistent_working_memory"]["target"] = 90
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("TARGET_DRIFT:persistent_working_memory", result.issues)

    def test_missing_evidence_cannot_support_score(self):
        broken = copy.deepcopy(self.payload)
        broken["domains"]["finished_ability"]["evidenceRefs"] = []
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("DOMAIN_EVIDENCE_MISSING:finished_ability", result.issues)

    def test_open_package_blocks_v06_closeout(self):
        broken = copy.deepcopy(self.payload)
        broken["packages"]["package_4"]["state"] = "HOLD"
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertTrue(any(x.startswith("PACKAGE_NOT_CLOSED:package_4") for x in result.issues))

    def test_any_unresolved_critical_failure_blocks_closeout(self):
        broken = copy.deepcopy(self.payload)
        broken["criticalFailures"]["unresolved"] = 1
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("CRITICAL_FAILURES_NONZERO", result.issues)

    def test_donecheck_must_be_evidence_backed_pass(self):
        broken = copy.deepcopy(self.payload)
        broken["mandatoryDoneCheck"][0]["state"] = "HOLD"
        broken["mandatoryDoneCheck"][1]["evidenceRefs"] = []
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("DONECHECK_NOT_PASS:all_v06_packages_reconciled", result.issues)
        self.assertIn(
            "DONECHECK_EVIDENCE_MISSING:real_implementation_and_field_evidence_present",
            result.issues,
        )

    def test_unresolved_hold_ledger_must_be_empty(self):
        broken = copy.deepcopy(self.payload)
        broken["unresolvedHolds"] = ["missing-field-proof"]
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("UNRESOLVED_HOLDS_PRESENT", result.issues)

    def test_package5_cannot_claim_product_final_before_mac_commissioning(self):
        broken = copy.deepcopy(self.payload)
        broken["productFinalState"] = "VERIFIED_FINAL_LOCKED"
        result = assess_v06_aggregate(broken)
        self.assertEqual(result.state, "HOLD")
        self.assertIn("PREMATURE_PRODUCT_FINAL_CLAIM", result.issues)

    def test_mac_local_final_commissioning_is_explicit_next_gate(self):
        self.assertEqual(
            self.payload["nextRequiredGate"],
            "PACKAGE6_MAC_LOCAL_FINAL_COMMISSIONING",
        )
        self.assertEqual(
            self.payload["productFinalState"],
            "HOLD_MAC_LOCAL_COMMISSIONING_REQUIRED",
        )


if __name__ == "__main__":
    unittest.main()
