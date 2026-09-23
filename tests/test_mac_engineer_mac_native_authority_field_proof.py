from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_mac_native_authority_field_proof.py"
SPEC = importlib.util.spec_from_file_location("mac_engineer_mac_native_authority_field_proof", MODULE_PATH)
assert SPEC and SPEC.loader
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class MacNativeAuthorityFieldProofTests(unittest.TestCase):
    def test_contract_identity_is_stable_and_local_only(self):
        self.assertEqual(proof.TASK_ID, "ENGURU-V07-MAC-NATIVE-MIGRATION-001")
        self.assertEqual(proof.BRANCH, "enguru-mac-native-migration-proof")

    def test_manifest_preserves_peer_identity_without_remote_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = proof.write_manifest(
                repo,
                repository="engurulabory/a",
                peer="engurulabory/b",
                base_sha="a" * 40,
            )
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["taskId"], proof.TASK_ID)
        self.assertEqual(payload["peerRepository"], "engurulabory/b")
        self.assertFalse(payload["remoteMutation"])
        self.assertEqual(payload["source"], "LOCAL_GITVAULT_MIRROR_WITH_REPOSITORY_FABRIC_IDENTITY")

    def test_mirror_remote_main_reads_remote_tracking_truth(self):
        with mock.patch.object(
            proof,
            "run",
            return_value={"code": 0, "stdout": "a" * 40, "stderr": ""},
        ) as runner:
            observed = proof.mirror_remote_main(Path("/tmp/example.git"))

        self.assertEqual(observed, "a" * 40)
        runner.assert_called_once_with(
            [
                "git",
                "--git-dir",
                "/tmp/example.git",
                "rev-parse",
                "refs/remotes/origin/main",
            ],
            timeout=60,
        )

    def test_control_plane_source_requires_fresh_local_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "accepted.json"
            state.write_text(
                json.dumps({
                    "state": "PASS",
                    "branch": "feat/test",
                    "head": "b" * 40,
                    "originMain": "a" * 40,
                    "authority": "PENDING_RECONCILIATION",
                    "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
                    "secondCanonicalTruth": False,
                    "evidence": "/tmp/evidence.json",
                    "acceptance": {
                        "targetedTests": "PASS",
                        "fullRegression": "PASS",
                        "diffCheck": "PASS",
                        "remoteBranchParity": "PASS",
                        "mainAncestor": "PASS",
                        "canonicalContext": "PASS",
                        "sessionStart": "PASS",
                    },
                }),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "ACCEPTED_CONTROL_STATE", state):
                accepted = proof.load_accepted_control_candidate()

        self.assertEqual(accepted["head"], "b" * 40)
        self.assertEqual(accepted["originMain"], "a" * 40)

    def test_control_plane_acceptance_rejects_stale_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "accepted.json"
            state.write_text(
                json.dumps({
                    "state": "PASS",
                    "branch": "feat/test",
                    "head": "b" * 40,
                    "originMain": "a" * 40,
                    "authority": "PENDING_RECONCILIATION",
                    "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
                    "secondCanonicalTruth": False,
                    "acceptance": {
                        "targetedTests": "PASS",
                        "fullRegression": "HOLD",
                        "diffCheck": "PASS",
                        "remoteBranchParity": "PASS",
                        "mainAncestor": "PASS",
                        "canonicalContext": "PASS",
                        "sessionStart": "PASS",
                    },
                }),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "ACCEPTED_CONTROL_STATE", state):
                with self.assertRaisesRegex(RuntimeError, "FULLREGRESSION_PASS_REQUIRED"):
                    proof.load_accepted_control_candidate()

    def test_fabric_gate_requires_12_of_12_and_offline_queue_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "fabric.json"
            state.write_text(
                json.dumps({
                    "state": "PASS",
                    "repositoryCount": 12,
                    "mirrorPassCount": 11,
                    "offlineQueueProof": {"state": "PASS"},
                }),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "FABRIC_STATE", state):
                with self.assertRaisesRegex(RuntimeError, "12_OF_12"):
                    proof.load_fabric()


if __name__ == "__main__":
    unittest.main()
