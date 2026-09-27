from pathlib import Path
import ast
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

OPERATOR = ROOT / "tools" / "mac_engineer_operator.py"

SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_operator_p10_receipt_test",
    OPERATOR,
)
assert SPEC and SPEC.loader
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)

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

    def test_command_continue_records_p10_completion_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            runtime_receipts = evidence / "runtime"

            truth = {
                "current_version": "v0.8",
                "next_action":
                    "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING",
                "local_continuity_next_action":
                    "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING",
                "local_fallback": {},
            }

            commissioning = {
                "state": "PASS",
                "fields": {
                    "STATE": "PASS",
                    "P10_ACCEPTANCE": "10_OF_10_PASS",
                    "P09_PASS": "PASS",
                    "CHECKPOINT_CONTINUITY_PASS": "PASS",
                    "CONTROLLED_INTERRUPTION_PASS": "PASS",
                    "RESTART_RECOVERY_PASS": "PASS",
                    "SAME_TASK_RESUME_PASS": "PASS",
                    "IDEMPOTENCY_PASS": "PASS",
                    "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE":
                        "PASS",
                    "SINGLE_WRITER_DISCIPLINE_PASS": "PASS",
                    "BOUNDED_RETRY_PASS": "PASS",
                    "RECOVERY_EVIDENCE_PASS": "PASS",
                    "NEXT_ACTION":
                        "P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE",
                },
                "evidence": "/tmp/p10-final-acceptance.json",
            }

            with (
                mock.patch.object(operator, "EVIDENCE", evidence),
                mock.patch.object(
                    operator,
                    "RUNTIME_RECEIPTS",
                    runtime_receipts,
                ),
                mock.patch.object(
                    operator,
                    "canonical_boot",
                    return_value={"state": "PASS"},
                ),
                mock.patch.object(
                    operator,
                    "current_truth",
                    return_value=truth,
                ),
                mock.patch.object(
                    operator,
                    "sync_mirrors",
                    return_value={},
                ),
                mock.patch.object(
                    operator,
                    "runner_status",
                    return_value={"state": "UNCOMMISSIONED"},
                ),
                mock.patch.object(
                    operator,
                    "run_v08_gate11_consolidated_mac_commissioning",
                    return_value=commissioning,
                ),
                mock.patch.object(
                    operator,
                    "offline_manifest",
                    return_value={},
                ),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = operator.command_continue()

            receipt = json.loads(
                (evidence / "latest-receipt.json")
                .read_text(encoding="utf-8")
            )

        self.assertEqual(code, 0)
        self.assertEqual(receipt["state"], "PASS")
        self.assertEqual(
            receipt["next_action"],
            "P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE",
        )

        for marker in (
            "P10_P09_PASS",
            "P10_CHECKPOINT_CONTINUITY_PASS",
            "P10_CONTROLLED_INTERRUPTION_PASS",
            "P10_RESTART_RECOVERY_PASS",
            "P10_SAME_TASK_RESUME_PASS",
            "P10_IDEMPOTENCY_PASS",
            "P10_EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS",
            "P10_SINGLE_WRITER_DISCIPLINE_PASS",
            "P10_BOUNDED_RETRY_PASS",
            "P10_RECOVERY_EVIDENCE_PASS",
        ):
            self.assertIn(marker, receipt["completed"])

        self.assertNotIn(
            "P07_REAL_ENGINEERING_OBJECTIVE_COMPLETE",
            receipt["completed"],
        )


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
