from pathlib import Path
import ast
import unittest


ROOT = Path(__file__).resolve().parents[1]

OPERATOR = ROOT / "tools" / "mac_engineer_operator.py"

COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_GATE11_P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY.command"
)


class Gate11P10OperatorTests(unittest.TestCase):
    def test_operator_python_syntax(self):
        ast.parse(
            OPERATOR.read_text(encoding="utf-8"),
            filename=str(OPERATOR),
        )

    def test_p10_command_exists(self):
        self.assertTrue(COMMAND.is_file())

    def test_p10_command_reuses_existing_reliability_capabilities(self):
        source = COMMAND.read_text(encoding="utf-8")

        for token in (
            "V07_MAC_NATIVE_RESTART_RECOVERY_PROOF.command",
            "CURRENT_RELIABILITY_DIFFERS_FROM_FIELD_PROOF_ENGINE",
            "test_single_writer",
            "test_v07_a05_bounded_retry_policy_and_watchdog_decision",
            "P09_PASS=PASS",
            "CHECKPOINT_CONTINUITY_PASS=PASS",
            "CONTROLLED_INTERRUPTION_PASS=PASS",
            "RESTART_RECOVERY_PASS=PASS",
            "SAME_TASK_RESUME_PASS=PASS",
            "IDEMPOTENCY_PASS=PASS",
            "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE=PASS",
            "SINGLE_WRITER_DISCIPLINE_PASS=PASS",
            "BOUNDED_RETRY_PASS=PASS",
            "RECOVERY_EVIDENCE_PASS=PASS",
            "P10_ACCEPTANCE=10_OF_10_PASS",
            "NEXT_ACTION=P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE",
        ):
            self.assertIn(token, source)

    def test_p10_command_preserves_authority_boundary(self):
        source = COMMAND.read_text(encoding="utf-8")

        self.assertNotIn("git" + " push", source)
        self.assertNotIn("git merge", source)
        self.assertNotIn("git commit", source)
        self.assertIn("NEW_CORE=false", source)
        self.assertIn("SOURCE_MUTATION=0", source)
        self.assertIn("REMOTE_MUTATION=0", source)

    def test_operator_has_p10_handler(self):
        source = OPERATOR.read_text(encoding="utf-8")

        for token in (
            "run_v08_gate11_p10_interruption_recovery_resume_reliability",
            'active_package == "P10"',
            "V08_GATE11_P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY.command",
            'fields.get("P10_ACCEPTANCE") == "10_OF_10_PASS"',
            "P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE",
        ):
            self.assertIn(token, source)

    def test_p09_router_is_preserved(self):
        source = OPERATOR.read_text(encoding="utf-8")

        self.assertIn(
            'active_package == "P09"',
            source,
        )
        self.assertIn(
            "run_v08_gate11_p09_lifecycle_controlled_replacement_rollback",
            source,
        )


if __name__ == "__main__":
    unittest.main()
