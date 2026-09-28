from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import tools.mac_engineer_v08_gate12_pre005_candidate as candidate
import tools.mac_engineer_donecheck_v12_bridge as bridge


def write_json(path: Path, value: object) -> dict[str, str]:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": str(path), "digest": candidate.file_digest(path)}


def verification_manifest(root: Path, task_id: str = "task-g12", verified_at: str = "2026-09-28T08:00:00Z") -> dict:
    task = {"id": task_id, "title": "Gate12", "requestText": "Verify Gates 1–11", "status": "awaiting_review", "createdAt": verified_at}
    criteria, evidence, files = [], [], []
    for index in range(1, 12):
        gate = f"gate{index}"
        evidence_id = f"evidence-{gate}"
        content = f"[DONECHECK:PASS] {gate} criterion evidence verified\n"
        path = root / f"{gate}.log"
        path.write_text(content, encoding="utf-8")
        digest = candidate.file_digest(path)
        criteria.append({"id": gate, "taskId": task_id, "statement": f"{gate} passes", "verificationInstruction": "Check criterion-scoped system evidence", "kind": "objective", "required": True})
        evidence.append({"id": evidence_id, "taskId": task_id, "criterionId": gate, "kind": "test_report", "source": "system", "content": content, "collectedAt": verified_at, "provenance": {"schema": "donecheck.evidence-provenance/v1", "producerKind": "mac_engineer", "producerId": "enguru.mac-engineer", "executionId": f"test-{gate}", "artifactDigest": digest, "observedAt": verified_at}})
        files.append({"evidenceId": evidence_id, "path": str(path), "digest": digest})
    return {"verificationInput": {"task": task, "criteria": criteria, "aiOutput": "Gate evidence reviewed", "evidence": evidence, "resultId": "verification-g12", "verifiedAt": verified_at, "policy": {"requireEvidenceProvenance": True, "trustedProducerIds": ["enguru.mac-engineer"]}}, "evidenceFiles": files}


def fixture(root: Path) -> tuple[dict, Path]:
    manifest = verification_manifest(root, task_id="gate12", verified_at="2026-09-28T16:00:00Z")
    evidence = write_json(root / "evidence.json", manifest)
    unresolved = write_json(root / "unresolved.json", {"schema": candidate.LEDGER_SCHEMA, "items": []})
    snapshot = write_json(root / "snapshot.json", {"gate11": "VERIFIED_LOCKED", "gate12": "ACTIVE"})
    contract = write_json(root / "contract.json", {"exit": candidate.EXIT})
    receipt = write_json(root / "receipt.json", {"placeholder": True})
    audit = write_json(root / "audit.jsonl", {"placeholder": True})
    control = {"repository": candidate.CONTROL_REPOSITORY, "branch": candidate.CONTROL_BRANCH, "head": "a" * 40, "base": "b" * 40, "remoteFeatureHead": "a" * 40, "remoteFeatureParity": True, "worktreeClean": True}
    product = {"repository": candidate.PRODUCT_REPOSITORY, "branch": candidate.PRODUCT_BRANCH, "head": "c" * 40, "base": "d" * 40, "worktreeClean": True, "publicationState": candidate.PRODUCT_PUBLICATION}
    chain = {"machineResultDigest": "sha256:" + "0" * 64, "evidenceManifestDigest": evidence["digest"], "unresolvedDeferredLedgerDigest": unresolved["digest"], "canonicalSnapshotDigest": snapshot["digest"], "acceptanceContractDigest": contract["digest"], "verifiedFinishReceiptDigest": receipt["digest"], "auditHead": "sha256:" + "e" * 64}
    machine_value = {"schema": candidate.MACHINE_SCHEMA, "bindings": {"controlHead": control["head"], "productHead": product["head"], "doneCheckVersion": candidate.DONECHECK_VERSION, "doneCheckSha": candidate.DONECHECK_SHA, "evidenceManifestDigest": chain["evidenceManifestDigest"], "unresolvedDeferredLedgerDigest": chain["unresolvedDeferredLedgerDigest"], "canonicalSnapshotDigest": chain["canonicalSnapshotDigest"], "acceptanceContractDigest": chain["acceptanceContractDigest"]}, "verificationResult": bridge.reproduce_verification_result(manifest["verificationInput"])}
    machine = write_json(root / "machine.json", machine_value)
    chain["machineResultDigest"] = machine["digest"]
    artifacts = {"machineResult": machine, "evidenceManifest": evidence, "unresolvedDeferredLedger": unresolved, "canonicalSnapshot": snapshot, "acceptanceContract": contract, "verifiedFinishReceipt": receipt, "auditLedger": audit}
    bundle = candidate.build_candidate_bundle(control=control, product=product, done_check={"version": candidate.DONECHECK_VERSION, "exactSha": candidate.DONECHECK_SHA}, authority={"reviewerId": "reviewer", "keyId": "key", "authorityDigest": "sha256:" + "f" * 64}, chain=chain, target={"targetVersion": candidate.TARGET, "intendedExit": candidate.EXIT}, artifacts=artifacts)
    path = root / "bundle.json"
    path.write_text(json.dumps(bundle) + "\n", encoding="utf-8")
    return bundle, path


class CandidateTests(unittest.TestCase):
    def test_fabricated_pass_with_matching_digest_cannot_replace_donecheck_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle, _ = fixture(root)
            machine = json.loads((root / "machine.json").read_text(encoding="utf-8"))
            machine["verificationResult"]["reason"] = "manually asserted pass"
            write_json(root / "machine.json", machine)
            bundle["artifacts"]["machineResult"]["digest"] = candidate.file_digest(root / "machine.json")
            bundle["chain"]["machineResultDigest"] = bundle["artifacts"]["machineResult"]["digest"]
            with self.assertRaisesRegex(candidate.CandidateHold, "MACHINE_RESULT_NOT_REPRODUCED_BY_DONECHECK"):
                candidate.validate_candidate_bundle(bundle)

    def test_missing_criterion_evidence_holds_even_with_pass_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle, _ = fixture(root)
            manifest = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
            manifest["verificationInput"]["evidence"].pop()
            manifest["evidenceFiles"].pop()
            write_json(root / "evidence.json", manifest)
            bundle["artifacts"]["evidenceManifest"]["digest"] = candidate.file_digest(root / "evidence.json")
            bundle["chain"]["evidenceManifestDigest"] = bundle["artifacts"]["evidenceManifest"]["digest"]
            machine = json.loads((root / "machine.json").read_text(encoding="utf-8"))
            machine["bindings"]["evidenceManifestDigest"] = bundle["chain"]["evidenceManifestDigest"]
            write_json(root / "machine.json", machine)
            bundle["artifacts"]["machineResult"]["digest"] = candidate.file_digest(root / "machine.json")
            bundle["chain"]["machineResultDigest"] = bundle["artifacts"]["machineResult"]["digest"]
            with self.assertRaisesRegex(candidate.CandidateHold, "DONECHECK_EVIDENCE_FILES_INCOMPLETE"):
                candidate.validate_candidate_bundle(bundle)

    def test_schema_and_terminal_identity_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle, path = fixture(Path(directory))
            self.assertEqual(candidate.load_candidate_bundle(path), bundle)
            bundle["terminalCandidateId"] = "g12-candidate-sha256:" + "0" * 64
            path.write_text(json.dumps(bundle), encoding="utf-8")
            with self.assertRaisesRegex(candidate.CandidateHold, "TERMINAL_CANDIDATE_ID_MISMATCH"):
                candidate.load_candidate_bundle(path)

    def test_audit_file_digest_is_distinct_from_audit_head(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle, _ = fixture(Path(directory))
            self.assertNotEqual(bundle["artifacts"]["auditLedger"]["digest"], bundle["chain"]["auditHead"])

    def test_unresolved_critical_item_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle, path = fixture(root)
            ledger = {"schema": candidate.LEDGER_SCHEMA, "items": [{"id": "critical-1", "classification": "DEFERRED", "severity": "CRITICAL", "state": "OPEN"}]}
            bundle["artifacts"]["unresolvedDeferredLedger"] = write_json(root / "unresolved.json", ledger)
            bundle["chain"]["unresolvedDeferredLedgerDigest"] = bundle["artifacts"]["unresolvedDeferredLedger"]["digest"]
            path.write_text(json.dumps(bundle), encoding="utf-8")
            with self.assertRaisesRegex(candidate.CandidateHold, "UNRESOLVED_CRITICAL_ITEM"):
                candidate.load_candidate_bundle(path)

    def test_machine_result_without_bindings_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle, path = fixture(root)
            bundle["artifacts"]["machineResult"] = write_json(root / "machine.json", {"state": "PASS", "outcome": "PASS"})
            bundle["chain"]["machineResultDigest"] = bundle["artifacts"]["machineResult"]["digest"]
            path.write_text(json.dumps(bundle), encoding="utf-8")
            with self.assertRaisesRegex(candidate.CandidateHold, "MACHINE_RESULT_BINDING_CONTRACT_INSUFFICIENT"):
                candidate.load_candidate_bundle(path)

    def test_private_key_custody_path_holds_before_read(self):
        forbidden = candidate.SECURITY_CUSTODY / "synthetic-do-not-read.json"
        with self.assertRaisesRegex(candidate.CandidateHold, "PRIVATE_KEY_CUSTODY_PATH_FORBIDDEN"):
            candidate.assert_safe_artifact_path(forbidden)


if __name__ == "__main__":
    unittest.main()
