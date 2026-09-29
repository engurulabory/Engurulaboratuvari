"""Gate 12 publication stays below the canonical lock boundary."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import mac_engineer_v08_gate12_finalizer as finalizer


class FinalizerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.paths = {
            name: self.root / (name + ".json")
            for name in ("handoff", "bundle", "envelope", "session", "roadmap", "registry")
        }
        self.bundle = {
            "terminalCandidateId": "candidate-1",
            "control": {"head": "control-1"},
            "product": {"head": "product-1"},
            "doneCheck": {"version": "1.2.0"},
            "chain": {"auditHead": "audit-1"},
        }
        self.values = {
            "handoff": {
                "bundlePath": str(self.paths["bundle"]),
                "thresholdEnvelopePath": str(self.paths["envelope"]),
            },
            "bundle": self.bundle,
            "envelope": {"payload": {
                "decision": "ACCEPT", "decisionId": "decision-1",
                "decidedAt": "2026-09-28T19:34:31Z",
                "controlHead": "control-1", "productHead": "product-1",
            }},
            "session": {"currentObjective": finalizer.GATE12,
                        "currentV08": {"gate12": {
                            "state": "ACTIVE", "executionStarted": False,
                        }, "currentProductSource": {
                            "publicationState": "LOCAL_VERIFIED_NOT_REMOTE_PARITY",
                        }},
                        "observedV07A09LocalFallback": {"canonicalA09State": "HOLD"}},
            "roadmap": {"current": {"activeObjective": finalizer.GATE12,
                                   "activeGate": 12}},
            "registry": {"actions": {finalizer.GATE12: {
                "batch3Boundary": "FINAL_ACCEPTANCE_RECEIPT_AND_CANONICAL_LOCK",
                "finalAcceptanceReceipt": False, "canonicalLock": False,
            }}},
        }
        for name, value in self.values.items():
            self.paths[name].write_text(json.dumps(value), encoding="utf-8")
        for key, path in (("SESSION_PATH", self.paths["session"]),
                          ("ROADMAP_PATH", self.paths["roadmap"]),
                          ("REGISTRY_PATH", self.paths["registry"]),
                          ("EVIDENCE_ROOT", self.root / "evidence")):
            mocker = patch.object(finalizer, key, path)
            mocker.start()
            self.addCleanup(mocker.stop)
        mocker = patch.object(finalizer, "load_candidate_bundle",
                              return_value=self.bundle)
        mocker.start()
        self.addCleanup(mocker.stop)

    def _prelock(self, result):
        mocker = patch.object(finalizer, "execute_from_runtime_handoff",
                              return_value=result)
        mocker.start()
        self.addCleanup(mocker.stop)

    def test_stale_prelock_never_publishes_receipt_or_lock(self):
        self._prelock({"state": "HOLD", "reason": "LOCAL_CANDIDATE_ACCEPTANCE_STALE"})
        with self.assertRaisesRegex(finalizer.FinalizationHold,
                                    "LOCAL_CANDIDATE_ACCEPTANCE_STALE"):
            finalizer.finalize(handoff_path=self.paths["handoff"])
        self.assertFalse((self.root / "evidence").exists())

    def test_signed_head_mismatch_never_publishes(self):
        self._prelock({"state": "PASS", "batch2PreLock": "PASS"})
        value = self.values["envelope"]
        value["payload"]["controlHead"] = "other-head"
        self.paths["envelope"].write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationHold,
                                    "SIGNED_DECISION_HEAD_MISMATCH"):
            finalizer.finalize(handoff_path=self.paths["handoff"])
        self.assertFalse((self.root / "evidence").exists())

    def test_reconciled_state_prevents_republication(self):
        self._prelock({"state": "PASS", "batch2PreLock": "PASS"})
        value = self.values["session"]
        value["currentV08"]["gate12"]["state"] = "VERIFIED_LOCKED"
        self.paths["session"].write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationHold,
                                    "CANONICAL_PREEXECUTION_STATE_MISMATCH"):
            finalizer.finalize(handoff_path=self.paths["handoff"])
        self.assertFalse((self.root / "evidence").exists())

    def test_receipt_idempotent_and_never_claims_canonical_pass(self):
        self._prelock({"state": "PASS", "batch2PreLock": "PASS"})
        first = finalizer.finalize(handoff_path=self.paths["handoff"])
        second = finalizer.finalize(handoff_path=self.paths["handoff"])
        self.assertEqual(first["state"], "HOLD")
        self.assertEqual(first["reason"], "GATE12_CANONICAL_RECONCILIATION_REQUIRED")
        self.assertEqual(first["fieldReceiptDigest"], second["fieldReceiptDigest"])
        self.assertTrue(second["receiptIdempotent"])
        self.assertFalse(first["canonicalLockCreated"])
        receipt = json.loads(Path(first["fieldReceipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["state"],
                         "FIELD_ACCEPTED_PENDING_CANONICAL_RECONCILIATION")
        self.assertEqual(receipt["externalA09State"], "HOLD")
        self.assertFalse(receipt["canonicalLockCreated"])
        self.assertFalse(list((self.root / "evidence").rglob("canonical-lock.json")))
        self.assertEqual(json.loads(self.paths["session"].read_text()), self.values["session"])

    def test_changed_signed_decision_cannot_replace_published_receipt(self):
        self._prelock({"state": "PASS", "batch2PreLock": "PASS"})
        first = finalizer.finalize(handoff_path=self.paths["handoff"])
        value = self.values["envelope"]
        value["payload"]["decisionId"] = "decision-2"
        self.paths["envelope"].write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "PUBLICATION_DESTINATION_CONFLICT"):
            finalizer.finalize(handoff_path=self.paths["handoff"])
        receipt = json.loads(Path(first["fieldReceipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["humanDecisionId"], "decision-1")


class LockEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.root = root
        self.receipt_path = root / "evidence" / "candidate" / "field-acceptance-receipt.json"
        self.bundle_path = root / "bundle.json"
        self.envelope_path = root / "envelope.json"
        self.finish_path = root / "finish.json"
        self.ledger_path = root / "ledger.json"
        self.authority_path = root / "authority.json"
        self.replay_path = root / "replay.json"
        self.handoff_path = root / "handoff.json"
        self.session_path = root / "session.json"
        self.roadmap_path = root / "roadmap.json"
        self.registry_path = root / "registry.json"
        self.accepted = "a" * 40
        self.current = "b" * 40
        self.product = {
            "repository": "product", "branch": "feature", "head": "product-1",
            "base": "base", "worktreeClean": True,
            "publicationState": "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY",
        }
        self.bundle = {
            "terminalCandidateId": "candidate-1",
            "control": {"head": self.accepted},
            "product": self.product,
            "doneCheck": {"version": "1.2.0", "exactSha": "donecheck-sha"},
            "chain": {"auditHead": "audit-1", "verifiedFinishReceiptDigest": ""},
            "target": {"targetVersion": "v0.8", "intendedExit": finalizer.EXIT},
            "artifacts": {"unresolvedDeferredLedger": {"path": str(self.ledger_path)}},
        }
        for path in (self.bundle_path, self.envelope_path, self.finish_path, self.authority_path):
            path.write_text("{}", encoding="utf-8")
        self.envelope_path.write_text('{"payload": {"decision": "ACCEPT"}}', encoding="utf-8")
        self.bundle["chain"]["verifiedFinishReceiptDigest"] = finalizer.file_digest(self.finish_path)
        self.ledger_path.write_text(json.dumps({"items": [
            {"id": "V07_A09_EXTERNAL_CI_CONFIRMATION", "classification": "EXTERNAL",
             "severity": "NON_CRITICAL", "state": "OPEN"},
            {"id": "V08_PRODUCT_REMOTE_PUBLICATION", "classification": "DEFERRED",
             "severity": "NON_CRITICAL", "state": "OPEN"},
        ]}), encoding="utf-8")
        self.receipt = {
            "schema": "enguru.mac-engineer.v08-gate12-field-acceptance/v1",
            "state": "FIELD_ACCEPTED_PENDING_CANONICAL_RECONCILIATION",
            "humanDecision": "ACCEPT", "humanDecisionId": "decision-1",
            "prelock": "PASS", "canonicalLockCreated": False,
            "terminalCandidateId": "candidate-1", "control": self.bundle["control"],
            "product": self.product, "doneCheck": self.bundle["doneCheck"],
            "chain": self.bundle["chain"], "bundlePath": str(self.bundle_path),
            "bundleDigest": finalizer.file_digest(self.bundle_path),
            "thresholdEnvelopePath": str(self.envelope_path),
            "thresholdEnvelopeDigest": finalizer.file_digest(self.envelope_path),
            "externalA09State": "HOLD",
            "productPublicationState": self.product["publicationState"],
        }
        publication = finalizer.CrashDurablePublisher().publish_json(
            self.receipt_path, self.receipt
        )
        self.session = {
            "currentObjective": finalizer.GATE12,
            "currentV08": {
                "gate12": {
                    "state": "FIELD_ACCEPTED_PENDING_CANONICAL_LOCK",
                    "executionStarted": True, "canonicalLockCreated": False,
                    "fieldAcceptanceReceipt": str(self.receipt_path),
                    "fieldAcceptanceReceiptDigest": publication.digest,
                    "terminalCandidateId": "candidate-1",
                    "acceptedControlHead": self.accepted,
                },
                "currentProductSource": {"publicationState": self.product["publicationState"]},
            },
            "observedV07A09LocalFallback": {"canonicalA09State": "HOLD"},
        }
        self.roadmap = {"current": {
            "activeObjective": finalizer.GATE12, "activeGate": 12,
            "gate12FieldAcceptance": {"digest": publication.digest},
        }}
        self.registry = {"actions": {finalizer.GATE12: {"canonicalLock": False}}}
        self.handoff = {
            "bundlePath": str(self.bundle_path),
            "thresholdEnvelopePath": str(self.envelope_path),
            "humanReviewPath": str(root / "review.json"),
            "attestationPath": str(root / "attestation.json"),
            "verifiedFinishPath": str(self.finish_path),
            "auditPath": str(root / "audit.json"),
        }
        self._write_state()
        for key, path in (
            ("SESSION_PATH", self.session_path), ("ROADMAP_PATH", self.roadmap_path),
            ("REGISTRY_PATH", self.registry_path), ("HANDOFF_PATH", self.handoff_path),
            ("EVIDENCE_ROOT", root / "evidence"),
        ):
            mocker = patch.object(finalizer, key, path)
            mocker.start()
            self.addCleanup(mocker.stop)
        for key, value in (
            ("derive_live_truth", ({"head": self.current}, self.product)),
            ("_git", self.accepted),
            ("load_candidate_bundle", self.bundle),
            ("load_authority", {}),
            ("verify_authority", {"state": "PASS"}),
            ("verify_human_review_and_verified_finish", {"state": "PASS", "auditHead": "audit-1"}),
            ("verify_threshold_envelope_json", {
                "state": "PASS", "decisionId": "decision-1", "terminalCandidateId": "candidate-1",
            }),
        ):
            mocker = patch.object(finalizer, key, return_value=value)
            mocker.start()
            self.addCleanup(mocker.stop)

    def _write_state(self):
        for path, value in (
            (self.session_path, self.session), (self.roadmap_path, self.roadmap),
            (self.registry_path, self.registry), (self.handoff_path, self.handoff),
        ):
            path.write_text(json.dumps(value), encoding="utf-8")

    def _run(self):
        return finalizer.publish_lock_evidence(
            authority_path=self.authority_path, replay_path=self.replay_path
        )

    def test_valid_chain_publishes_idempotent_pending_evidence(self):
        first = self._run()
        second = self._run()
        self.assertEqual(first["state"], "HOLD")
        self.assertEqual(first["reason"], "GATE12_LOCK_EVIDENCE_PENDING_CANONICAL_COMMIT")
        self.assertEqual(first["lockEvidenceDigest"], second["lockEvidenceDigest"])
        self.assertTrue(second["idempotent"])
        self.assertFalse(first["canonicalLockCreated"])
        evidence = json.loads(Path(first["lockEvidence"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["acceptedControlHead"], self.accepted)
        self.assertEqual(evidence["reconciliationControlHead"], self.current)
        self.assertFalse(evidence["canonicalLockCreated"])
        self.assertFalse((self.receipt_path.parent / "canonical-lock.json").exists())

    def test_tampered_field_receipt_holds_before_publication(self):
        self.receipt_path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationHold, "FIELD_RECEIPT_PUBLICATION_MISMATCH"):
            self._run()
        self.assertFalse((self.receipt_path.parent / "canonical-lock-evidence.json").exists())

    def test_remote_unavailable_holds_before_publication(self):
        with patch.object(finalizer, "derive_live_truth", side_effect=RuntimeError("REMOTE_UNAVAILABLE")):
            with self.assertRaisesRegex(RuntimeError, "REMOTE_UNAVAILABLE"):
                self._run()
        self.assertFalse((self.receipt_path.parent / "canonical-lock-evidence.json").exists())

    def test_control_ancestry_drift_holds_before_publication(self):
        with patch.object(finalizer, "_git", return_value="unrelated-head"):
            with self.assertRaisesRegex(finalizer.FinalizationHold, "ACCEPTED_CONTROL_NOT_ANCESTOR"):
                self._run()
        self.assertFalse((self.receipt_path.parent / "canonical-lock-evidence.json").exists())

    def test_reviewer_authority_expiry_holds_before_publication(self):
        with patch.object(finalizer, "verify_authority", return_value={"state": "HOLD"}):
            with self.assertRaisesRegex(finalizer.FinalizationHold, "REVIEWER_AUTHORITY_HOLD"):
                self._run()
        self.assertFalse((self.receipt_path.parent / "canonical-lock-evidence.json").exists())

    def test_deferred_ledger_drift_holds_before_publication(self):
        self.ledger_path.write_text('{"items": []}', encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationHold, "DEFERRED_LEDGER_MISMATCH"):
            self._run()

    def test_signed_threshold_hold_prevents_publication(self):
        with patch.object(finalizer, "verify_threshold_envelope_json", return_value={"state": "HOLD"}):
            with self.assertRaisesRegex(finalizer.FinalizationHold, "HUMAN_THRESHOLD_BINDING_MISMATCH"):
                self._run()


if __name__ == "__main__":
    unittest.main()
