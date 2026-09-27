import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

OPERATOR = (
    ROOT
    / "tools"
    / "mac_engineer_operator.py"
)

COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_GATE11_CONSOLIDATED_MAC_COMMISSIONING.command"
)


class Gate11HandlerTests(unittest.TestCase):
    def test_handler_function_and_branch_exist(self):
        source = OPERATOR.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

        functions = {
            node.name
            for node in tree.body
            if isinstance(
                node,
                ast.FunctionDef,
            )
        }

        self.assertIn(
            "run_v08_gate11_consolidated_mac_commissioning",
            functions,
        )

        self.assertIn(
            'local_action == "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING"',
            source,
        )

        self.assertIn(
            "P07_REAL_ENGINEERING_OBJECTIVE_COMPLETE",
            source,
        )

        self.assertIn(
            "P07_TARGETED_TEST_PASS",
            source,
        )

    def test_command_contract_is_bounded(self):
        self.assertTrue(
            COMMAND.is_file()
        )

        source = COMMAND.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "runtime/tests/test_python_test_replacement_policy.py",
            source,
        )

        self.assertIn(
            "REAL_ENGINEERING_OBJECTIVE_COMPLETE=PASS",
            source,
        )

        self.assertIn(
            "TARGETED_TEST_PASS=PASS",
            source,
        )

        self.assertIn(
            "PRODUCT_REMOTE_MUTATION=false",
            source,
        )


if __name__ == "__main__":
    unittest.main()
