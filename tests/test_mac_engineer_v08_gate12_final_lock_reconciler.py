"""Gate 12 final canonical lock reconciliation is fail-closed and two-phase."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from unittest.mock import patch

from tools import mac_engineer_v08_gate12_final_lock_reconciler as final_lock


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class FinalLockReconcilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.root = root
        self.gov = root / "governance" / "mac-engineer"
        self.gov.mkdir(parents=True)
        self.evidence = root / "evidence"
        self.evidence.mkdir()
        self.receipt = self.evidence / "final-acceptance-receipt.json"
        self.field = self.evidence / "field.json"
        self.lock = self.evidence / "lock.json"

        self.session_path = self.gov / "SESSION_STATE_V1.json"
        self.roadmap_path = self.gov / "PRODUCT_ROADMAP_V1.json"
        self.registry_path = self.gov / "OPERATOR_ACTION_REGISTRY_V1.json"
        self.candidate_path = self.gov / "V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json"
        self.status_path = self.gov / "CURRENT_STATUS.md"
        self.working_path = self.gov / "ACTIVE_WORKING_PATH.md"
        self.worklist_path = root / "WORKLIST.md"
        self.acceptance_path = root / "acceptance.json"

        self.field.write_text("{}", encoding="utf-8")
        self.lock.write_text("{}", encoding="utf-8")

        self.session = {
            "currentVersion": "v0.8",
            "currentObjective": final_lock.GATE12,
            "currentV08": {
                "state": "ACTIVE",
                "nextAction": final_lock.GATE12,
                "localContinuityNextAction": final_lock.GATE12,
                "localContinuityState": "ACTIVE",
                "controlPlaneLocalContinuity": {
                    "state": "ACTIVE_VERSION_ENGINEERING",
                    "branch": final_lock.EXPECTED_BRANCH,
                    "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
                    "localAuthority": "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY_VERIFIED",
                    "secondCanonicalTruth": False,
                    "externalMergeGate": "HOLD_GITHUB_ACTIONS_EXECUTION",
                    "currentTechnicalTarget": final_lock.GATE12,
                    "nextAfterPass": final_lock.GATE12,
                },
                "currentProductSource": {
                    "localVerifiedHead": "product-1",
                    "publicationState": final_lock.EXPECTED_PRODUCT_PUBLICATION,
                },
                "closureContract": {
                    "passedGates": list(range(1, 12)),
                    "activeGate": 12,
                    "remainingGates": [12],
                },
                "gate12": {
                    "state": "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT",
                    "canonicalLockCreated": False,
                    "machineResult": "PASS_11_OF_11",
                    "humanDecision": "ACCEPT",
                    "fieldAcceptanceReceipt": str(self.field),
                    "fieldAcceptanceReceiptDigest": "sha256:" + "f" * 64,
                    "lockEvidence": str(self.lock),
                    "lockEvidenceDigest": "sha256:" + "a" * 64,
                    "terminalCandidateId": "candidate-1",
                },
            },
        }
        self.roadmap = {
            "current": {
                "state": "ACTIVE_PRODUCT_ENGINEERING_OPERATOR",
                "activeObjective": final_lock.GATE12,
                "completed": ["V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING_PASS"],
                "remaining": [final_lock.GATE12],
                "activeGate": 12,
                "gate12FieldAcceptance": {},
            },
            "versions": [{
                "version": "v0.8",
                "state": "ACTIVE",
                "nextAction": final_lock.GATE12,
                "verifiedFinishContract": {
                    "state": "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT",
                    "passed": list(range(1, 12)),
                    "active": 12,
                    "remaining": [12],
                },
            }],
        }
        self.registry = {"actions": {final_lock.GATE12: {
            "handler": "V08_GATE12_FINAL_ACCEPTANCE_READBACK",
            "finalAcceptanceReceipt": False,
            "canonicalLock": False,
            "finalAcceptanceReceiptCandidate": True,
        }}}
        self.candidate = {
            "schema": "enguru.mac-engineer.v08-gate12-final-acceptance/v1",
            "state": "CANDIDATE_PENDING_FRESH_REMOTE_READBACK",
            "objective": final_lock.GATE12,
            "exit": final_lock.EXIT,
            "postCommitVerificationRequired": True,
            "fieldReceiptDigest": "sha256:" + "f" * 64,
            "lockEvidenceDigest": "sha256:" + "a" * 64,
            "humanDecision": "ACCEPT",
            "doneCheck": {"criteria": "PASS_11_OF_11"},
        }

        for path, value in (
            (self.session_path, self.session),
            (self.roadmap_path, self.roadmap),
            (self.registry_path, self.registry),
            (self.candidate_path, self.candidate),
        ):
            path.write_text(json.dumps(value), encoding="utf-8")

        self.status_path.write_text(
            "# status\n## Gate 12 lock evidence reconciliation — final receipt pending\nold\n"
            "## PROGRAMMER AGENT AUTHORING DISCIPLINE\nkeep\n",
            encoding="utf-8",
        )
        self.working_path.write_text(
            "# path\n## CURRENT GATE 12 AUTHORITY\nold\n"
            "Bu dosya ENGÜRÜ Mac Engineer™ geliştirme çalışması sürerken x\n",
            encoding="utf-8",
        )
        self.worklist_path.write_text(
            "prefix\n<!-- ENGURU_GATE12_PREEXECUTION_CURRENT_AUTHORITY_V1 -->\nold\n",
            encoding="utf-8",
        )

        self.receipt_payload = {
            "schema": "enguru.mac-engineer.v08-gate12-final-acceptance-receipt/v1",
            "state": "FINAL_ACCEPTANCE_PASS_PENDING_CANONICAL_LOCK",
            "claim": "GATE12_FINAL_ACCEPTANCE_VERIFIED",
            "canonicalLockCreated": False,
            "machineResult": "PASS_11_OF_11",
            "humanDecision": "ACCEPT",
            "externalA09State": "HOLD",
            "productPublicationState": final_lock.EXPECTED_PRODUCT_PUBLICATION,
            "controlHead": "control-1",
            "productHead": "product-1",
            "fieldReceipt": str(self.field),
            "fieldReceiptDigest": "sha256:" + "f" * 64,
            "lockEvidence": str(self.lock),
            "lockEvidenceDigest": "sha256:" + "a" * 64,
            "terminalCandidateId": "candidate-1",
            "finalAcceptanceCandidate": str(self.candidate_path),
        }
        self.receipt_payload["finalAcceptanceCandidateDigest"] = digest(self.candidate_path)
        self.receipt.write_text(json.dumps(self.receipt_payload), encoding="utf-8")
        marker = self.receipt.with_name(self.receipt.name + ".enguru-publication.json")
        marker.write_text(json.dumps({
            "schema": "enguru.mac-engineer.publication/v1",
            "digest": digest(self.receipt),
            "byteLength": len(self.receipt.read_bytes()),
        }), encoding="utf-8")

        patches = {
            "ROOT": root,
            "GOV": self.gov,
            "SESSION_PATH": self.session_path,
            "ROADMAP_PATH": self.roadmap_path,
            "REGISTRY_PATH": self.registry_path,
            "CANDIDATE_PATH": self.candidate_path,
            "STATUS_PATH": self.status_path,
            "WORKING_PATH": self.working_path,
            "WORKLIST_PATH": self.worklist_path,
            "ACCEPTANCE_STATE": self.acceptance_path,
            "EVIDENCE_ROOT": self.evidence,
        }
        for name, value in patches.items():
            p = patch.object(final_lock, name, value)
            p.start()
            self.addCleanup(p.stop)

    def git_value(self, *args):
        values = {
            ("branch", "--show-current"): final_lock.EXPECTED_BRANCH,
            ("rev-parse", "HEAD"): "control-1",
            ("status", "--porcelain"): "",
            ("merge-base", "control-1", "control-1"): "control-1",
        }
        return values.get(tuple(args), "")

    def test_prepare_reconciles_exact_final_state_and_holds_for_commit(self):
        with patch.object(final_lock, "_git", side_effect=self.git_value),              patch.object(final_lock, "_run") as run:
            run.return_value.returncode = 0
            run.return_value.stderr = ""
            run.return_value.stdout = ""
            expected_paths = {
                "WORKLIST.md",
                "governance/mac-engineer/ACTIVE_WORKING_PATH.md",
                "governance/mac-engineer/CURRENT_STATUS.md",
                "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json",
                "governance/mac-engineer/PRODUCT_ROADMAP_V1.json",
                "governance/mac-engineer/SESSION_STATE_V1.json",
                "governance/mac-engineer/V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json",
            }
            with patch.object(final_lock, "EXPECTED_MUTATION_PATHS", expected_paths), \
                 patch.object(final_lock, "_changed_paths", return_value=expected_paths), \
                 patch.object(final_lock, "_git", side_effect=[
                     final_lock.EXPECTED_BRANCH, "control-1", "", "control-1",
                 ]):
                result = final_lock.prepare_final_lock_reconciliation()

        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "GATE12_FINAL_LOCK_RECONCILIATION_COMMIT_REQUIRED")
        session = json.loads(self.session_path.read_text())
        roadmap = json.loads(self.roadmap_path.read_text())
        registry = json.loads(self.registry_path.read_text())
        candidate = json.loads(self.candidate_path.read_text())
        self.assertEqual(session["currentV08"]["gate12"]["state"], "VERIFIED_LOCKED")
        self.assertTrue(session["currentV08"]["gate12"]["canonicalLockCreated"])
        self.assertEqual(session["currentV08"]["closureContract"]["passedGates"], list(range(1, 13)))
        self.assertIsNone(session["currentV08"]["closureContract"]["activeGate"])
        self.assertEqual(roadmap["current"]["remaining"], [])
        self.assertTrue(registry["actions"][final_lock.GATE12]["canonicalLock"])
        self.assertEqual(candidate["state"], "VERIFIED_LOCKED")
        self.assertIn("Final acceptance receipt digest", self.worklist_path.read_text())

    def test_changed_paths_uses_name_only_and_preserves_first_character(self):
        outputs = [
            "WORKLIST.md\ngovernance/mac-engineer/CURRENT_STATUS.md\n",
            "",
            "",
        ]

        def fake_run(*args, **kwargs):
            result = mock.Mock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = outputs.pop(0)
            return result

        with patch.object(final_lock, "_run", side_effect=fake_run):
            observed = final_lock._changed_paths()

        self.assertIn("WORKLIST.md", observed)
        self.assertIn(
            "governance/mac-engineer/CURRENT_STATUS.md",
            observed,
        )
        self.assertNotIn("ORKLIST.md", observed)

    def test_readback_requires_exact_local_acceptance(self):
        self.session["currentV08"]["state"] = "VERIFIED_LOCKED"
        self.session["currentV08"]["gate12"].update({
            "state": "VERIFIED_LOCKED",
            "canonicalLockCreated": True,
            "finalAcceptanceReceipt": str(self.receipt),
            "finalAcceptanceReceiptDigest": digest(self.receipt),
        })
        self.session["currentV08"]["closureContract"] = {
            "passedGates": list(range(1, 13)), "activeGate": None, "remainingGates": []
        }
        self.session_path.write_text(json.dumps(self.session))
        self.roadmap["current"].update({
            "state": "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED",
            "remaining": [], "activeGate": None,
        })
        self.roadmap["versions"][0].update({"state": "VERIFIED_LOCKED"})
        self.roadmap["versions"][0]["verifiedFinishContract"].update({
            "state": "VERIFIED_LOCKED",
            "passed": list(range(1, 13)),
            "remaining": [],
        })
        self.roadmap_path.write_text(json.dumps(self.roadmap))
        self.registry["actions"][final_lock.GATE12].update({
            "finalAcceptanceReceipt": True, "canonicalLock": True,
        })
        self.registry_path.write_text(json.dumps(self.registry))
        self.candidate.update({
            "state": "VERIFIED_LOCKED",
            "canonicalLockCreated": True,
            "finalAcceptanceReceiptDigest": digest(self.receipt),
        })
        self.candidate_path.write_text(json.dumps(self.candidate))
        self.acceptance_path.write_text(json.dumps({"state": "HOLD"}))

        with patch.object(final_lock, "_run") as run,              patch.object(final_lock, "_git", side_effect=lambda *args, **kwargs: {
                 ("branch", "--show-current"): final_lock.EXPECTED_BRANCH,
                 ("rev-parse", "HEAD"): "lock-commit",
                 ("rev-parse", f"origin/{final_lock.EXPECTED_BRANCH}"): "lock-commit",
                 ("status", "--porcelain"): "",
                 ("merge-base", "control-1", "lock-commit"): "control-1",
             }.get(tuple(args), "")):
            run.return_value.returncode = 0
            run.return_value.stderr = ""
            with self.assertRaisesRegex(final_lock.FinalLockHold, "FINAL_LOCK_LOCAL_ACCEPTANCE_REQUIRED"):
                final_lock.verify_final_lock_readback()


if __name__ == "__main__":
    unittest.main()
