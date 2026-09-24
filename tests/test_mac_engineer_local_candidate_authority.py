from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.mac_engineer_local_candidate_authority import (
    evaluate_local_accepted_candidate,
)


class LocalAcceptedCandidateAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.evidence = self.root / "evidence.json"
        self.state = self.root / "state.json"
        self.branch = "feat/mac-engineer-osi-operator-surface"
        self.head = "a" * 40
        self.origin_main = "b" * 40
        self.external_hold = "HOLD_GITHUB_ACTIONS_EXECUTION"

        evidence_payload = {
            "schema": "enguru.mac-engineer.local-accepted-control-plane-candidate-evidence/v1",
            "state": "PASS",
            "branch": self.branch,
            "head": self.head,
            "originMain": self.origin_main,
            "authority": "PENDING_RECONCILIATION",
            "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
            "secondCanonicalTruth": False,
            "externalMergeGate": self.external_hold,
        }
        self.evidence.write_text(json.dumps(evidence_payload), encoding="utf-8")

        state_payload = {
            "schema": "enguru.mac-engineer.local-accepted-control-plane-candidate/v1",
            "state": "PASS",
            "branch": self.branch,
            "head": self.head,
            "originMain": self.origin_main,
            "clean": True,
            "authority": "PENDING_RECONCILIATION",
            "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
            "secondCanonicalTruth": False,
            "externalMergeGate": self.external_hold,
            "evidence": str(self.evidence),
            "acceptance": {
                "targetedTests": "PASS",
                "fullRegression": "PASS",
                "diffCheck": "PASS",
                "remoteBranchParity": "PASS",
                "mainAncestor": "PASS",
                "canonicalContext": "PASS",
                "sessionStart": "PASS",
            },
        }
        self.state.write_text(json.dumps(state_payload), encoding="utf-8")

        self.control = {
            "branch": self.branch,
            "head": self.head,
            "origin_main": self.origin_main,
            "clean": True,
            "exact_origin_main": False,
        }
        self.session = {
            "currentV07": {
                "controlPlaneLocalContinuity": {
                    "state": "PENDING_RECONCILIATION",
                    "branch": self.branch,
                    "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
                    "localAuthority": "PENDING_RECONCILIATION",
                    "secondCanonicalTruth": False,
                    "externalMergeGate": self.external_hold,
                    "acceptanceStatePath": str(self.state),
                }
            }
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def evaluate(self):
        return evaluate_local_accepted_candidate(
            self.control,
            self.session,
            acceptance_path=self.state,
        )

    def test_exact_matching_candidate_is_authorized(self) -> None:
        result = self.evaluate()
        self.assertTrue(result["authorized"], result["reasons"])
        self.assertEqual(result["mode"], "LOCAL_ACCEPTED_CANDIDATE")

    def test_post_lock_verified_local_authority_is_authorized(self) -> None:
        policy = self.session["currentV07"]["controlPlaneLocalContinuity"]
        policy["state"] = "VERIFIED_LOCAL_AUTHORITY_PENDING_EXTERNAL_RECONCILIATION"
        policy["localAuthority"] = "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY_VERIFIED"

        state_payload = json.loads(self.state.read_text(encoding="utf-8"))
        state_payload["authority"] = "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY_VERIFIED"
        state_payload["policyPhase"] = "POST_LOCK_VERIFIED_FINISH"
        self.state.write_text(json.dumps(state_payload), encoding="utf-8")

        evidence_payload = json.loads(self.evidence.read_text(encoding="utf-8"))
        evidence_payload["authority"] = "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY_VERIFIED"
        evidence_payload["policyPhase"] = "POST_LOCK_VERIFIED_FINISH"
        self.evidence.write_text(json.dumps(evidence_payload), encoding="utf-8")

        result = self.evaluate()
        self.assertTrue(result["authorized"], result["reasons"])
        self.assertEqual(result["policy_phase"], "POST_LOCK_VERIFIED_FINISH")

    def test_mixed_policy_phase_fails_closed(self) -> None:
        policy = self.session["currentV07"]["controlPlaneLocalContinuity"]
        policy["state"] = "VERIFIED_LOCAL_AUTHORITY_PENDING_EXTERNAL_RECONCILIATION"
        policy["localAuthority"] = "PENDING_RECONCILIATION"

        result = self.evaluate()
        self.assertFalse(result["authorized"])
        self.assertIn("POLICY_LOCAL_CONTINUITY_PHASE_REQUIRED", result["reasons"])

    def test_head_drift_fails_closed(self) -> None:
        self.control["head"] = "c" * 40
        result = self.evaluate()
        self.assertFalse(result["authorized"])
        self.assertIn("LOCAL_ACCEPTANCE_HEAD_MISMATCH", result["reasons"])

    def test_dirty_worktree_fails_closed(self) -> None:
        self.control["clean"] = False
        result = self.evaluate()
        self.assertFalse(result["authorized"])
        self.assertIn("LOCAL_ACCEPTANCE_CLEAN_REQUIRED", result["reasons"])

    def test_evidence_sha_mismatch_fails_closed(self) -> None:
        payload = json.loads(self.evidence.read_text(encoding="utf-8"))
        payload["head"] = "d" * 40
        self.evidence.write_text(json.dumps(payload), encoding="utf-8")
        result = self.evaluate()
        self.assertFalse(result["authorized"])
        self.assertIn("LOCAL_ACCEPTANCE_EVIDENCE_HEAD_MISMATCH", result["reasons"])

    def test_missing_external_hold_fails_closed(self) -> None:
        self.session["currentV07"]["controlPlaneLocalContinuity"]["externalMergeGate"] = ""
        result = self.evaluate()
        self.assertFalse(result["authorized"])
        self.assertIn("POLICY_EXTERNAL_MERGE_HOLD_REQUIRED", result["reasons"])


if __name__ == "__main__":
    unittest.main()
