import unittest
from unittest.mock import patch

from tools.mac_engineer_product_operator_v12_material_execution import (
    execute_material_work_class,
)


def pass_execution(capability_id):
    return {
        "STATE": "PASS",
        "CAPABILITY_ID": capability_id,
        "BINDING_TYPE": "REGISTERED_ACTION",
        "REGISTERED_HANDLER_INVOKED": True,
        "EXECUTION_PERFORMED": True,
        "NETWORK_ACCESS_PERFORMED": False,
        "REMOTE_PUSH_PERFORMED": False,
    }


class ProductOperatorV12MaterialExecutionTests(unittest.TestCase):
    @patch(
        "tools.mac_engineer_product_operator_v12_material_execution."
        "safe_orchestrator.execute_proven_registered_action"
    )
    def test_build_executes_registered_action(self, execute):
        execute.side_effect = pass_execution
        result = execute_material_work_class("BUILD")

        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["capabilityId"], "BUILD")
        self.assertTrue(result["materialExecutionPerformed"])
        execute.assert_called_once_with("BUILD")

    @patch(
        "tools.mac_engineer_product_operator_v12_material_execution."
        "safe_orchestrator.execute_proven_registered_action"
    )
    def test_test_regression_executes_registered_action(self, execute):
        execute.side_effect = pass_execution
        result = execute_material_work_class("TEST_REGRESSION")

        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["capabilityId"], "TEST_REGRESSION")
        self.assertTrue(result["materialExecutionPerformed"])
        execute.assert_called_once_with("TEST_REGRESSION")

    @patch(
        "tools.mac_engineer_product_operator_v12_material_execution."
        "safe_orchestrator.execute_proven_registered_action"
    )
    def test_ht_required_stops_before_execution(self, execute):
        result = execute_material_work_class(
            "FILESYSTEM_MACOS_AUTOMATION"
        )

        self.assertEqual(result["state"], "NEEDS_HUMAN")
        self.assertFalse(result["materialExecutionPerformed"])
        execute.assert_not_called()

    @patch(
        "tools.mac_engineer_product_operator_v12_material_execution."
        "safe_orchestrator.execute_proven_registered_action"
    )
    def test_unknown_action_holds_before_execution(self, execute):
        result = execute_material_work_class(
            "ARBITRARY_UNKNOWN_ACTION"
        )

        self.assertEqual(result["state"], "HOLD")
        self.assertFalse(result["materialExecutionPerformed"])
        execute.assert_not_called()

    @patch(
        "tools.mac_engineer_product_operator_v12_material_execution."
        "safe_orchestrator.execute_proven_registered_action"
    )
    def test_downstream_hold_is_preserved(self, execute):
        execute.return_value = {
            "STATE": "HOLD",
            "HOLD_REASON": "REGISTERED_ACTION_RESULT_CONTRACT_HOLD",
            "CAPABILITY_ID": "BUILD",
            "EXECUTION_PERFORMED": True,
        }

        result = execute_material_work_class("BUILD")

        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "REGISTERED_ACTION_RESULT_CONTRACT_HOLD",
        )


if __name__ == "__main__":
    unittest.main()
