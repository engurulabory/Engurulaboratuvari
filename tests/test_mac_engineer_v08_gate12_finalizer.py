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


if __name__ == "__main__":
    unittest.main()
