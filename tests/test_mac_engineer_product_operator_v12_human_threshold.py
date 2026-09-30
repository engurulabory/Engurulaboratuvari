import unittest

from tools.mac_engineer_product_operator_v12_human_threshold import (
    evaluate,
    evaluate_work_class,
)


class ProductOperatorV12HumanThresholdTests(unittest.TestCase):
    def test_non_ht_action_continues(self):
        result = evaluate_work_class("BUILD")
        self.assertEqual(result["state"], "CONTINUE")
        self.assertFalse(result["humanThresholdRequired"])
        self.assertFalse(result["executionAuthorityCreated"])

    def test_ht_action_stops_for_human(self):
        result = evaluate_work_class("FILESYSTEM_MACOS_AUTOMATION")
        self.assertEqual(result["state"], "NEEDS_HUMAN")
        self.assertEqual(result["reason"], "HUMAN_THRESHOLD_REQUIRED")
        self.assertTrue(result["humanThresholdRequired"])
        self.assertFalse(result["executionAuthorityCreated"])

    def test_accept_preserves_same_bounded_action(self):
        before = evaluate_work_class("FILESYSTEM_MACOS_AUTOMATION")
        after = evaluate_work_class(
            "FILESYSTEM_MACOS_AUTOMATION",
            human_decision="ACCEPT",
        )

        self.assertEqual(after["state"], "READY_AFTER_HUMAN_THRESHOLD")
        self.assertEqual(after["action"], before["action"])
        self.assertEqual(after["authority"], before["authority"])
        self.assertFalse(after["executionAuthorityCreated"])

    def test_reject_holds(self):
        result = evaluate_work_class(
            "FILESYSTEM_MACOS_AUTOMATION",
            human_decision="REJECT",
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "HUMAN_THRESHOLD_REJECTED")

    def test_invalid_decision_holds(self):
        result = evaluate_work_class(
            "FILESYSTEM_MACOS_AUTOMATION",
            human_decision="YES",
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "INVALID_HUMAN_THRESHOLD_DECISION",
        )

    def test_unbound_action_holds(self):
        result = evaluate_work_class("ARBITRARY_UNKNOWN_ACTION")
        self.assertEqual(result["state"], "HOLD")

    def test_g3_contract(self):
        result = evaluate()
        self.assertEqual(result["STATE"], "PASS")
        self.assertTrue(all(result["CHECKS"].values()))


if __name__ == "__main__":
    unittest.main()
