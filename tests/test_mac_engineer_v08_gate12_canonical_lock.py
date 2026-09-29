"""The committed lock cannot PASS from repository claims alone."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import mac_engineer_v08_gate12_canonical_lock as lock


class CanonicalLockTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = {k: self.root / (k + ".json") for k in (
            "session", "roadmap", "registry", "lock", "receipt", "bundle",
            "ledger", "authority", "handoff", "threshold", "finish",
        )}
        self.path["lock"].parent.mkdir(parents=True, exist_ok=True)
        for key in ("bundle", "authority", "finish"):
            self.path[key].write_text("{}", encoding="utf-8")
        self.path["threshold"].write_text('{"payload": {"decision": "ACCEPT"}}', encoding="utf-8")
        self.product = {
            "head": "product-1", "publicationState":
            "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY",
        }
        self.bundle = {
            "terminalCandidateId": "candidate-1", "control": {"head": "accepted"},
            "product": self.product, "doneCheck": {"version": "1.2.0", "exactSha": "donecheck"},
            "chain": {"auditHead": "audit", "verifiedFinishReceiptDigest": lock.file_digest(self.path["finish"])},
            "target": {"targetVersion": "v0.8", "intendedExit": lock.EXIT},
            "artifacts": {"unresolvedDeferredLedger": {"path": str(self.path["ledger"])}},
        }
        self.path["ledger"].write_text(json.dumps({"items": [
            {"id": "V07_A09_EXTERNAL_CI_CONFIRMATION", "classification": "EXTERNAL",
             "severity": "NON_CRITICAL", "state": "OPEN"},
            {"id": "V08_PRODUCT_REMOTE_PUBLICATION", "classification": "DEFERRED",
             "severity": "NON_CRITICAL", "state": "OPEN"},
        ]}), encoding="utf-8")
        self.receipt = {
            "humanDecision": "ACCEPT", "humanDecisionId": "decision-1", "prelock": "PASS",
            "canonicalLockCreated": False, "product": self.product,
            "externalA09State": "HOLD", "productPublicationState": self.product["publicationState"],
            "bundlePath": str(self.path["bundle"]), "bundleDigest": lock.file_digest(self.path["bundle"]),
            "thresholdEnvelopePath": str(self.path["threshold"]),
            "thresholdEnvelopeDigest": lock.file_digest(self.path["threshold"]),
            **{key: self.bundle[key] for key in
               ("terminalCandidateId", "control", "doneCheck", "chain")},
        }
        self.evidence = {
            "schema": "enguru.mac-engineer.v08-gate12-lock-evidence/v1",
            "state": "LOCK_EVIDENCE_PENDING_CANONICAL_COMMIT",
            "canonicalLockCreated": False,
            "fieldReceipt": str(self.path["receipt"]), "fieldReceiptDigest": "sha256:" + "f" * 64,
            "terminalCandidateId": "candidate-1", "humanDecisionId": "decision-1",
            "acceptedControlHead": "accepted", "reconciliationControlHead": "reconciliation",
            "productHead": "product-1", "doneCheck": self.bundle["doneCheck"],
            "externalA09State": "HOLD", "productPublicationState": self.product["publicationState"],
        }
        self.session = {
            "currentObjective": lock.GATE12, "currentV08": {
                "state": "ACTIVE",
                "gate12": {
                    "state": "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT", "executionStarted": True,
                    "canonicalLockCreated": False, "humanDecision": "ACCEPT",
                    "machineResult": "PASS_11_OF_11", "lockEvidence": str(self.path["lock"]),
                    "lockEvidenceDigest": "sha256:" + "a" * 64, "fieldAcceptanceReceipt": str(self.path["receipt"]),
                    "fieldAcceptanceReceiptDigest": "sha256:" + "f" * 64,
                    "terminalCandidateId": "candidate-1", "acceptedControlHead": "accepted",
                    "reconciliationControlHead": "reconciliation",
                    "finalAcceptanceCandidate": "governance/mac-engineer/V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json",
                },
                "closureContract": {"passedGates": list(range(1, 12)),
                                    "activeGate": 12, "remainingGates": [12]},
                "currentProductSource": {"publicationState": self.product["publicationState"]},
            },
            "observedV07A09LocalFallback": {"canonicalA09State": "HOLD"},
        }
        self.roadmap = {
            "current": {"completed": ["V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING_PASS"], "remaining": [lock.GATE12],
                        "activeGate": 12, "state": "ACTIVE_PRODUCT_ENGINEERING_OPERATOR"},
            "versions": [{"version": "v0.8", "state": "ACTIVE",
                          "verifiedFinishContract": {"state": "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT",
                             "passed": list(range(1, 12)), "remaining": [12]}}],
        }
        self.registry = {"actions": {lock.GATE12: {"canonicalLock": False}}}
        self.final = {
            "schema": "enguru.mac-engineer.v08-gate12-final-acceptance/v1",
            "state": "CANDIDATE_PENDING_FRESH_REMOTE_READBACK",
            "objective": lock.GATE12, "exit": lock.EXIT,
            "postCommitVerificationRequired": True,
            "humanDecision": "ACCEPT", "doneCheck": {"version": "1.2.0", "exactSha": "donecheck", "criteria": "PASS_11_OF_11"},
            "fieldReceipt": str(self.path["receipt"]), "fieldReceiptDigest": "sha256:" + "f" * 64,
            "lockEvidence": str(self.path["lock"]), "lockEvidenceDigest": "sha256:" + "a" * 64,
            "terminalCandidateId": "candidate-1", "humanDecisionId": "decision-1",
            "acceptedControlHead": "accepted", "reconciliationControlHead": "reconciliation",
            "externalA09State": "HOLD", "productPublicationState": self.product["publicationState"],
        }
        (self.root / "governance/mac-engineer").mkdir(parents=True)
        for path, value in (
            (self.path["session"], self.session), (self.path["roadmap"], self.roadmap),
            (self.path["registry"], self.registry),
            (self.root / self.session["currentV08"]["gate12"]["finalAcceptanceCandidate"], self.final),
            (self.path["handoff"], {
                "bundlePath": str(self.path["bundle"]),
                "thresholdEnvelopePath": str(self.path["threshold"]),
                "humanReviewPath": str(self.root / "human.json"),
                "attestationPath": str(self.root / "attestation.json"),
                "verifiedFinishPath": str(self.path["finish"]),
                "auditPath": str(self.root / "audit.json"),
            }),
        ):
            path.write_text(json.dumps(value), encoding="utf-8")
        for name, value in (
            ("ROOT", self.root), ("SESSION_PATH", self.path["session"]),
            ("ROADMAP_PATH", self.path["roadmap"]), ("REGISTRY_PATH", self.path["registry"]),
            ("HANDOFF_PATH", self.path["handoff"]),
        ):
            mocker = patch.object(lock, name, value)
            mocker.start(); self.addCleanup(mocker.stop)
        for name, value in (
            ("_verified_publication", None), ("derive_live_truth", ({"head": "closure"}, self.product)),
            ("_git", None), ("load_candidate_bundle", self.bundle),
            ("load_authority", {}), ("verify_authority", {"state": "PASS", "authorityDigest": "authority"}),
            ("verify_human_review_and_verified_finish", {"state": "PASS", "auditHead": "audit"}),
            ("verify_threshold_envelope_json", {"state": "PASS", "decisionId": "decision-1",
                                                "terminalCandidateId": "candidate-1"}),
        ):
            mocker = patch.object(lock, name)
            m = mocker.start(); self.addCleanup(mocker.stop)
            if name == "_verified_publication":
                m.side_effect = lambda p, d: (
                    self.evidence if p == self.path["lock"] else
                    self.receipt if p == self.path["receipt"] else
                    json.loads(p.read_text(encoding="utf-8"))
                )
            elif name == "_git":
                m.side_effect = lambda _op, head, _current: head
            else:
                m.return_value = value

    def run_lock(self):
        return lock.publish_final_acceptance_receipt(
            authority_path=self.path["authority"], replay_path=self.root / "replay.json"
        )

    def test_signed_chain_and_remote_readback_publishes_pending_receipt(self):
        result = self.run_lock()
        retry = self.run_lock()
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["finalAcceptanceReceiptDigest"], retry["finalAcceptanceReceiptDigest"])
        self.assertFalse(result["canonicalLockCreated"])
        self.assertEqual(result["nextAction"], lock.GATE12)
        self.assertTrue(Path(result["finalAcceptanceReceipt"]).is_file())
        self.assertEqual(result["finalAcceptanceReceiptDigest"],
                         lock.file_digest(Path(result["finalAcceptanceReceipt"])))

    def test_missing_remote_truth_holds(self):
        with patch.object(lock, "derive_live_truth", side_effect=RuntimeError("REMOTE_UNAVAILABLE")):
            with self.assertRaisesRegex(RuntimeError, "REMOTE_UNAVAILABLE"):
                self.run_lock()

    def test_unrelated_reconciliation_head_holds(self):
        with patch.object(lock, "_git", return_value="unrelated"):
            with self.assertRaisesRegex(lock.FinalizationHold, "LOCK_FRESH_TRUTH_MISMATCH"):
                self.run_lock()

    def test_changed_deferred_classification_holds(self):
        self.evidence["externalA09State"] = "PASS"
        with self.assertRaisesRegex(lock.FinalizationHold, "LOCK_FIELD_BINDING_MISMATCH"):
            self.run_lock()

    def test_signed_threshold_hold_never_claims_lock(self):
        with patch.object(lock, "verify_threshold_envelope_json", return_value={"state": "HOLD"}):
            with self.assertRaisesRegex(lock.FinalizationHold, "LOCK_SIGNED_THRESHOLD_MISMATCH"):
                self.run_lock()

    def test_changed_lock_digest_holds(self):
        self.session["currentV08"]["gate12"]["lockEvidenceDigest"] = None
        self.path["session"].write_text(json.dumps(self.session), encoding="utf-8")
        with self.assertRaisesRegex(lock.FinalizationHold, "LOCK_EVIDENCE_DIGEST_REQUIRED"):
            self.run_lock()


class RepositoryLockCandidateTests(unittest.TestCase):
    def test_exact_repository_candidate_preserves_open_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        gov = root / "governance/mac-engineer"
        session = json.loads((gov / "SESSION_STATE_V1.json").read_text(encoding="utf-8"))
        roadmap = json.loads((gov / "PRODUCT_ROADMAP_V1.json").read_text(encoding="utf-8"))
        registry = json.loads((gov / "OPERATOR_ACTION_REGISTRY_V1.json").read_text(encoding="utf-8"))
        candidate = json.loads((gov / "V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json").read_text(encoding="utf-8"))
        gate = session["currentV08"]["gate12"]
        current = roadmap["current"]
        self.assertEqual(gate["lockEvidenceDigest"], current["gate12FieldAcceptance"]["lockEvidenceDigest"])
        self.assertEqual(gate["lockEvidenceDigest"], candidate["lockEvidenceDigest"])
        self.assertEqual(gate["fieldAcceptanceReceiptDigest"], candidate["fieldReceiptDigest"])
        self.assertTrue(candidate["postCommitVerificationRequired"])
        self.assertEqual(candidate["reconciliationControlHead"], gate["reconciliationControlHead"])
        self.assertEqual(candidate["externalA09State"], "HOLD")
        self.assertEqual(session["observedV07A09LocalFallback"]["canonicalA09State"], "HOLD")
        self.assertEqual(candidate["productPublicationState"],
                         session["currentV08"]["currentProductSource"]["publicationState"])

        if gate["state"] == "VERIFIED_LOCKED":
            self.assertTrue(gate["canonicalLockCreated"])
            self.assertEqual(candidate["state"], "VERIFIED_LOCKED")
            self.assertTrue(candidate["canonicalLockCreated"])
            self.assertTrue(registry["actions"][lock.GATE12]["finalAcceptanceReceipt"])
            self.assertTrue(registry["actions"][lock.GATE12]["canonicalLock"])
            self.assertIsNone(current["activeGate"])
            self.assertEqual(current["remaining"], [])
            self.assertEqual(current["state"],
                             "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED")
        else:
            self.assertEqual(
                gate["state"],
                "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT",
            )
            self.assertFalse(gate["canonicalLockCreated"])
            self.assertEqual(candidate["state"], "CANDIDATE_PENDING_FRESH_REMOTE_READBACK")
            self.assertFalse(registry["actions"][lock.GATE12]["finalAcceptanceReceipt"])
            self.assertFalse(registry["actions"][lock.GATE12]["canonicalLock"])
            self.assertEqual(current["activeGate"], 12)
            self.assertEqual(current["remaining"], [lock.GATE12])


if __name__ == "__main__":
    unittest.main()
