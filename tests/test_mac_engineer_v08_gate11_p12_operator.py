from pathlib import Path
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

ADAPTER_PATH = (
    ROOT
    / "tools"
    / "mac_engineer_v08_gate11_p12_closeout.py"
)

OPERATOR_PATH = (
    ROOT
    / "tools"
    / "mac_engineer_operator.py"
)

COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_GATE11_P12_DONECHECK_CANONICAL_GATE11_CLOSURE.command"
)

SPEC = importlib.util.spec_from_file_location(
    "p12_adapter",
    ADAPTER_PATH,
)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)

OP_SPEC = importlib.util.spec_from_file_location(
    "p12_operator",
    OPERATOR_PATH,
)
assert OP_SPEC and OP_SPEC.loader
operator = importlib.util.module_from_spec(OP_SPEC)
OP_SPEC.loader.exec_module(operator)


class Gate11P12OperatorTests(unittest.TestCase):

    def test_p12_command_and_adapter_exist(self):
        self.assertTrue(COMMAND.is_file())
        self.assertTrue(ADAPTER_PATH.is_file())

    def test_p12_acceptance_contract_is_exact(self):
        self.assertEqual(
            len(adapter.P12_ACCEPTANCE),
            15,
        )

        self.assertEqual(
            set(adapter.P12_ACCEPTANCE),
            {
                "P01_THROUGH_P11_PASS",
                "DONECHECK_V1_2_PASS",
                "CANONICAL_RECONCILIATION_PASS",
                "GATE11_EVIDENCE_BUNDLE_COMPLETE",
                "GATE11_ENGINEERING_EXECUTION_PASS",
                "ARCHITECTURE_STATE_PRESERVED",
                "NEW_CORE_FALSE",
                "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
                "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
                "UNTRACKED_MANUAL_STEP_COUNT_0",
                "GATE11_VERIFIED_LOCKED",
                "GATE11_EXIT_V08_CONSOLIDATED_MAC_COMMISSIONING_PASS",
                "ACTIVE_GATE_12",
                "GATE12_EXECUTION_0",
                "STOP_TRUE",
            },
        )

    def test_reconcile_documents_activates_gate12_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            session = root / "session.json"
            roadmap = root / "roadmap.json"
            status = root / "status.md"
            matrix = root / "matrix.md"

            session.write_text(
                json.dumps({
                    "currentObjective": adapter.G11,
                    "currentV08": {
                        "nextAction": adapter.G11,
                        "localContinuityNextAction": adapter.G11,
                        "controlPlaneLocalContinuity": {
                            "currentTechnicalTarget":
                                adapter.G11,
                            "nextAfterPass":
                                adapter.G11,
                        },
                        "closureContract": {
                            "passedGates":
                                list(range(1, 11)),
                            "activeGate": 11,
                            "remainingGates":
                                [11, 12],
                        },
                        "gate11": {
                            "state": "ACTIVE",
                            "name": adapter.G11,
                            "exit": adapter.G11_EXIT,
                            "executionStarted": False,
                        },
                    },
                    "preparedGate11Method": {
                        "state": "PREPARED_QUEUED",
                        "executionActive": False,
                        "currentPackage": None,
                    },
                }),
                encoding="utf-8",
            )

            roadmap.write_text(
                json.dumps({
                    "current": {
                        "activeObjective":
                            adapter.G11,
                        "activeGate": 11,
                        "completed": [],
                        "remaining": [
                            adapter.G11,
                            adapter.G12,
                        ],
                        "nextAction":
                            adapter.G11,
                    }
                }),
                encoding="utf-8",
            )

            status.write_text(
                "**Updated:** old\n"
                "**Current objective:** old\n",
                encoding="utf-8",
            )

            matrix.write_text(
                "### Gate 11\n"
                + adapter.G11_EXIT
                + "\n"
                "### Gate 12 — DoneCheck™ v1.2 + Human Threshold™ + Version Lock\n"
                + adapter.G12_EXIT
                + "\n",
                encoding="utf-8",
            )

            adapter.reconcile_documents(
                session,
                roadmap,
                status,
                matrix,
                closure_evidence="/tmp/p12.json",
                donecheck_evidence="/tmp/donecheck.json",
                observed_at="2026-09-27T20:55:00+00:00",
            )

            s = json.loads(
                session.read_text(encoding="utf-8")
            )
            r = json.loads(
                roadmap.read_text(encoding="utf-8")
            )

            closure = (
                s["currentV08"]["closureContract"]
            )

            self.assertEqual(
                s["currentObjective"],
                adapter.G12,
            )
            self.assertEqual(
                closure["passedGates"],
                list(range(1, 12)),
            )
            self.assertEqual(
                closure["activeGate"],
                12,
            )
            self.assertEqual(
                closure["remainingGates"],
                [12],
            )
            self.assertEqual(
                s["currentV08"]["gate11"]["state"],
                "VERIFIED_LOCKED",
            )
            self.assertEqual(
                s["currentV08"]["gate12"]["state"],
                "ACTIVE",
            )
            self.assertFalse(
                s["currentV08"]["gate12"][
                    "executionStarted"
                ]
            )
            self.assertEqual(
                r["current"]["activeGate"],
                12,
            )
            self.assertEqual(
                r["current"]["remaining"],
                [adapter.G12],
            )

    def test_p12_dispatch_is_mocked_not_executed(self):
        sentinel = {
            "state": "PASS",
            "fields": {
                "P12_ACCEPTANCE":
                    "15_OF_15_PASS",
            },
            "evidence": "/tmp/p12.json",
        }

        with (
            mock.patch.object(
                operator,
                "detect_v08_gate11_active_package",
                return_value="P12",
            ),
            mock.patch.object(
                operator,
                "run_v08_gate11_p12_donecheck_canonical_gate11_closure",
                return_value=sentinel,
            ) as handler,
        ):
            result = (
                operator
                .run_v08_gate11_consolidated_mac_commissioning()
            )

        handler.assert_called_once_with()
        self.assertEqual(result, sentinel)

    def test_command_continue_records_p12_completion_markers(self):
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
            "P12_ACCEPTANCE": "15_OF_15_PASS",
            "NEXT_ACTION":
                "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP",
        }

        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)

            with (
                mock.patch.object(
                    operator,
                    "EVIDENCE",
                    evidence,
                ),
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
                    return_value={
                        "state": "UNCOMMISSIONED"
                    },
                ),
                mock.patch.object(
                    operator,
                    "run_v08_gate11_consolidated_mac_commissioning",
                    return_value={
                        "state": "PASS",
                        "fields": fields,
                        "evidence": "/tmp/p12.json",
                    },
                ),
                mock.patch.object(
                    operator,
                    "offline_manifest",
                    return_value={},
                ),
            ):
                with contextlib.redirect_stdout(
                    io.StringIO()
                ):
                    code = operator.command_continue()

            receipt = json.loads(
                (
                    evidence
                    / "latest-receipt.json"
                ).read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(code, 0)

        self.assertEqual(
            receipt["next_action"],
            "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP",
        )

        self.assertIn(
            "P12_GATE11_VERIFIED_LOCKED",
            receipt["completed"],
        )

        self.assertIn(
            "P12_ACTIVE_GATE_12",
            receipt["completed"],
        )

        self.assertIn(
            "P12_STOP_TRUE",
            receipt["completed"],
        )

        self.assertNotIn(
            "P11_P10_PASS",
            receipt["completed"],
        )


if __name__ == "__main__":
    unittest.main()
