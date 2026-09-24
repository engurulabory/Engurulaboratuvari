from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_donecheck_v12_local_authority_verification.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_donecheck_v12_local_authority_verification",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
verification = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verification)


class DoneCheckV12LocalAuthorityVerificationTests(unittest.TestCase):
    def test_donecheck_exact_contract_is_preserved(self):
        self.assertEqual(verification.DONECHECK_VERSION, "1.2.0")
        self.assertEqual(
            verification.DONECHECK_SHA,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )
        self.assertEqual(
            set(verification.CRITERIA),
            {"MAC-NATIVE-GATE-08", "MAC-NATIVE-GATE-09", "MAC-NATIVE-GATE-10"},
        )

    def test_gate9_structural_validator_requires_exactly_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gate9.json"
            path.write_text(
                json.dumps({
                    "state": "PASS",
                    "gate": 9,
                    "processRestart": "PASS",
                    "taskIdentityContinuity": "PASS",
                    "checkpointResume": "PASS",
                    "exactlyOnceDurableEffect": "PASS",
                    "durableEffectCount": 2,
                    "finalTaskState": "COMPLETE",
                    "gitVaultMirrorUnchanged": True,
                    "remotePush": False,
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                RuntimeError,
                "GATE9_STRUCTURAL_CHECK_FAILED:durableEffectCount",
            ):
                verification.validate_gate9(path)

    def test_gate10_validator_rejects_second_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gate10.json"
            path.write_text(
                json.dumps({
                    "state": "PASS",
                    "gate": 10,
                    "remotePush": False,
                    "remoteMerge": False,
                    "canonicalRemoteIdentityPreserved": True,
                    "secondCanonicalTruthCreated": True,
                    "offlineQueue": {
                        "authority": "PENDING_RECONCILIATION_NOT_CANONICAL",
                        "remoteMutation": False,
                        "secondCanonicalTruth": False,
                        "bundleVerify": "PASS",
                    },
                    "gitVault": {
                        "refsUnchanged": True,
                        "fsckBefore": "PASS",
                        "fsckAfter": "PASS",
                    },
                    "reconciliationReadiness": {
                        "state": "PASS",
                        "patchApplyCheck": "PASS",
                    },
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                RuntimeError,
                "secondCanonicalTruthCreated",
            ):
                verification.validate_gate10(path)

    def test_prepare_input_requires_gate_11_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "session.json"
            state.write_text(
                json.dumps({
                    "currentV07": {
                        "verifiedFinishClosureContract": {
                            "passedGates": list(range(1, 11)),
                            "activeGate": 10,
                            "githubA09": {
                                "state": "EXTERNAL_BLOCKED_DEFERRED",
                                "blockingLocalEngineering": False,
                            },
                        }
                    }
                }),
                encoding="utf-8",
            )
            with (
                mock.patch.object(verification, "SESSION_STATE", state),
                mock.patch.object(
                    verification.bridge,
                    "require_current_fabric",
                    return_value={"state": "PASS"},
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "ACTIVE_GATE_11_REQUIRED"):
                    verification.prepare_input(Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
