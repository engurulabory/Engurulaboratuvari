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

COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_GATE11_P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE.command"
)

SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_operator_p11_test",
    OPERATOR,
)
assert SPEC and SPEC.loader
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


class Gate11P11OperatorTests(unittest.TestCase):

    def test_operator_python_syntax(self):
        ast.parse(
            OPERATOR.read_text(encoding="utf-8"),
            filename=str(OPERATOR),
        )

    def test_p11_command_exists(self):
        self.assertTrue(COMMAND.is_file())

    def test_p11_command_contains_exact_acceptance(self):
        source = COMMAND.read_text(encoding="utf-8")

        for token in (
            "P10_PASS=PASS",
            "TARGETED_REGRESSION_PASS=PASS",
            "FULL_CONTROL_PLANE_REGRESSION_PASS=PASS",
            "PRODUCT_REGRESSION_PASS=PASS",
            "DIFF_CHECK_PASS=PASS",
            "SCOPE_CHECK_PASS=PASS",
            "PROVENANCE_CHECK_PASS=PASS",
            "RECOVERY_CHECK_PASS=PASS",
            "EVIDENCE_COMPLETENESS_PASS=PASS",
            "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0=PASS",
            "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0=PASS",
            "UNTRACKED_MANUAL_STEP_COUNT_0=PASS",
            "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0=PASS",
            "CRITICAL_FALSE_PASS_0=PASS",
            "P11_ACCEPTANCE=14_OF_14_PASS",
            "CURRENT_UNRESOLVED_CRITICAL_FALSE_PASS_COUNT=0",
            "HISTORICAL_REJECTED_FALSE_PASS_CLAIM_COUNT=1",
            "NEXT_ACTION=P12_DONECHECK_CANONICAL_GATE11_CLOSURE",
        ):
            self.assertIn(token, source)

    def test_p11_command_preserves_authority_boundary(self):
        source = COMMAND.read_text(encoding="utf-8")

        self.assertNotIn("git" + " push", source)
        self.assertNotIn("git commit", source)
        self.assertNotIn("git merge", source)
        self.assertIn("NEW_CORE=false", source)
        self.assertIn("SOURCE_MUTATION=0", source)
        self.assertIn("REMOTE_MUTATION=0", source)

    def test_operator_has_p11_handler(self):
        source = OPERATOR.read_text(encoding="utf-8")

        for token in (
            "run_v08_gate11_p11_independent_verification_second_look_evidence_bundle",
            'active_package == "P11"',
            'active_package == "P12"',
            "V08_GATE11_P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE.command",
            'fields.get("P11_ACCEPTANCE") == "14_OF_14_PASS"',
            "P12_DONECHECK_CANONICAL_GATE11_CLOSURE",
        ):
            self.assertIn(token, source)

    def test_verified_p11_receipt_promotes_router_to_p12(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)

            receipt = (
                home
                / "Enguru"
                / "Evidence"
                / "MacEngineer"
                / "v0.8"
                / "gate11-p11-independent-verification"
                / "20260927T210000Z"
                / "p11-final-acceptance.json"
            )
            receipt.parent.mkdir(parents=True)

            required = (
                "P10_PASS",
                "TARGETED_REGRESSION_PASS",
                "FULL_CONTROL_PLANE_REGRESSION_PASS",
                "PRODUCT_REGRESSION_PASS",
                "DIFF_CHECK_PASS",
                "SCOPE_CHECK_PASS",
                "PROVENANCE_CHECK_PASS",
                "RECOVERY_CHECK_PASS",
                "EVIDENCE_COMPLETENESS_PASS",
                "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
                "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
                "UNTRACKED_MANUAL_STEP_COUNT_0",
                "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0",
                "CRITICAL_FALSE_PASS_0",
            )

            receipt.write_text(
                json.dumps(
                    {
                        "state": "PASS",
                        "package": "P11",
                        "acceptance": {
                            key: "PASS"
                            for key in required
                        },
                        "currentUnresolvedCriticalFalsePassCount": 0,
                        "sourceMutation": False,
                        "remoteMutation": False,
                        "newCore": False,
                        "nextTransition": "P12",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(operator, "HOME", home):
                active = operator.detect_v08_gate11_active_package()

        self.assertEqual(active, "P12")

    def test_incomplete_p11_receipt_does_not_promote_to_p12(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)

            receipt = (
                home
                / "Enguru"
                / "Evidence"
                / "MacEngineer"
                / "v0.8"
                / "gate11-p11-independent-verification"
                / "20260927T210000Z"
                / "p11-final-acceptance.json"
            )
            receipt.parent.mkdir(parents=True)

            receipt.write_text(
                json.dumps(
                    {
                        "state": "PASS",
                        "package": "P11",
                        "acceptance": {
                            "P10_PASS": "PASS",
                        },
                        "currentUnresolvedCriticalFalsePassCount": 0,
                        "sourceMutation": False,
                        "remoteMutation": False,
                        "newCore": False,
                        "nextTransition": "P12",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(operator, "HOME", home):
                active = operator.detect_v08_gate11_active_package()

        self.assertNotEqual(active, "P12")

    def test_p12_is_fail_closed_until_handler_is_bound(self):
        with mock.patch.object(
            operator,
            "detect_v08_gate11_active_package",
            return_value="P12",
        ):
            result = (
                operator.run_v08_gate11_consolidated_mac_commissioning()
            )

        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "V08_GATE11_P12_HANDLER_NOT_YET_BOUND",
        )

    def test_command_continue_records_p11_completion_markers(self):
        truth = {
            "current_version": "v0.8",
            "next_action":
                "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING",
            "local_continuity_next_action":
                "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING",
            "local_fallback": {},
        }

        fields = {
            "STATE": "PASS",
            "P11_ACCEPTANCE": "14_OF_14_PASS",
            "CURRENT_UNRESOLVED_CRITICAL_FALSE_PASS_COUNT": "0",
            "NEXT_ACTION":
                "P12_DONECHECK_CANONICAL_GATE11_CLOSURE",
        }

        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)

            with (
                mock.patch.object(operator, "EVIDENCE", evidence),
                mock.patch.object(
                    operator,
                    "RUNTIME_RECEIPTS",
                    evidence / "runtime",
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
                    return_value={
                        "state": "PASS",
                        "fields": fields,
                        "evidence": "/tmp/p11.json",
                    },
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
        self.assertEqual(
            receipt["next_action"],
            "P12_DONECHECK_CANONICAL_GATE11_CLOSURE",
        )
        self.assertIn(
            "P11_CRITICAL_FALSE_PASS_0",
            receipt["completed"],
        )
        self.assertNotIn(
            "P07_REAL_ENGINEERING_OBJECTIVE_COMPLETE",
            receipt["completed"],
        )


if __name__ == "__main__":
    unittest.main()
