from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_offline_gitvault_reconciliation_field_proof.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_offline_gitvault_reconciliation_field_proof",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class OfflineGitVaultReconciliationFieldProofTests(unittest.TestCase):
    def test_contract_names_are_stable(self):
        self.assertEqual(
            proof.QUEUE_BRANCH,
            "enguru-offline-reconciliation-proof",
        )
        self.assertEqual(
            proof.QUEUE_FILE,
            ".enguru/offline-reconciliation-proof.json",
        )

    def test_accepted_candidate_requires_passed_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "accepted.json"
            state.write_text(
                json.dumps({
                    "state": "PASS",
                    "authority": "PENDING_RECONCILIATION",
                    "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
                    "secondCanonicalTruth": False,
                    "branch": "feat/test",
                    "head": "b" * 40,
                    "originMain": "a" * 40,
                    "acceptance": {
                        "targetedTests": "PASS",
                        "fullRegression": "PASS",
                        "diffCheck": "PASS",
                        "remoteBranchParity": "PASS",
                        "mainAncestor": "PASS",
                        "canonicalContext": "PASS",
                        "sessionStart": "HOLD",
                    },
                }),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "ACCEPTED_STATE", state):
                with self.assertRaisesRegex(RuntimeError, "SESSIONSTART_PASS_REQUIRED"):
                    proof.load_accepted_candidate()

    def test_fabric_requires_12_of_12_and_offline_queue_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "fabric.json"
            state.write_text(
                json.dumps({
                    "state": "PASS",
                    "repositoryCount": 12,
                    "mirrorPassCount": 12,
                    "offlineQueueProof": {"state": "HOLD"},
                }),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "FABRIC_STATE", state):
                with self.assertRaisesRegex(RuntimeError, "OFFLINE_QUEUE_PASS_REQUIRED"):
                    proof.load_fabric()

    def test_mirror_has_commit_uses_literal_commit_rev_spec(self):
        with mock.patch.object(
            proof,
            "run",
            return_value={"code": 0, "stdout": "", "stderr": ""},
        ) as runner:
            self.assertTrue(
                proof.mirror_has_commit(Path("/tmp/example.git"), "b" * 40)
            )

        runner.assert_called_once_with(
            [
                "git",
                "--git-dir",
                "/tmp/example.git",
                "cat-file",
                "-e",
                ("b" * 40) + "^{commit}",
            ],
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
