from pathlib import Path
import ast
import unittest


ROOT = Path(__file__).resolve().parents[1]

OPERATOR = ROOT / "tools/mac_engineer_operator.py"

COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_GATE11_P09_LIFECYCLE_CONTROLLED_REPLACEMENT_ROLLBACK.command"
)


class Gate11P09OperatorTests(unittest.TestCase):
    def test_operator_python_syntax(self):
        ast.parse(
            OPERATOR.read_text(encoding="utf-8"),
            filename=str(OPERATOR),
        )

    def test_p09_command_exists(self):
        self.assertTrue(COMMAND.is_file())

    def test_p09_command_contains_real_lifecycle_chain(self):
        source = COMMAND.read_text(encoding="utf-8")

        for token in (
            "prepare_native_app.command",
            "osascript",
            "open -n",
            "previous_app_backup",
            ".runtime-previous.",
            "CONTROLLED_REPLACEMENT_PASS=PASS",
            "STOP_PASS=PASS",
            "RESTART_PASS=PASS",
            "KNOWN_GOOD_ROLLBACK_PASS=PASS",
            "ROLLBACK_REVERIFY_PASS=PASS",
            "LIFECYCLE_PROVENANCE_PASS=PASS",
            "EVIDENCE_CONTINUITY_PASS=PASS",
            "FINAL_KNOWN_GOOD=P08_VERIFIED",
            "P09_ACCEPTANCE=8_OF_8_PASS",
            "NEXT_ACTION=P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY",
        ):
            self.assertIn(token, source)

    def test_operator_has_package_router_and_p09_handler(self):
        source = OPERATOR.read_text(encoding="utf-8")

        for token in (
            "detect_v08_gate11_active_package",
            "run_v08_gate11_p09_lifecycle_controlled_replacement_rollback",
            'active_package == "P09"',
            'active_package == "P10"',
            "P09_CONTROLLED_REPLACEMENT_PASS",
            "P09_EVIDENCE_CONTINUITY_PASS",
        ):
            self.assertIn(token, source)

    def test_p07_handler_is_preserved(self):
        source = OPERATOR.read_text(encoding="utf-8")

        self.assertIn(
            "run_v08_gate11_consolidated_mac_commissioning",
            source,
        )
        self.assertIn(
            "P07_REAL_ENGINEERING_OBJECTIVE_COMPLETE",
            source,
        )


if __name__ == "__main__":
    unittest.main()
