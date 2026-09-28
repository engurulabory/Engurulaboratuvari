from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import tools.mac_engineer_v08_gate12_pre005_candidate as candidate
import tools.mac_engineer_v08_gate12_pre005_executor as executor
import tools.mac_engineer_v08_gate12_reviewer_authority as authority
import tools.mac_engineer_donecheck_v12_bridge as bridge
from tests.test_mac_engineer_v08_gate12_reviewer_authority import run_key_helper
from tests.test_mac_engineer_v08_gate12_pre005_candidate import verification_manifest


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def make_authority(keys: dict) -> dict:
    value = {
        "schema": authority.AUTHORITY_SCHEMA_ID, "authorityVersion": 1,
        "status": "ACTIVE", "validFrom": "2026-09-28T00:00:00Z",
        "expiresAt": "2026-10-28T00:00:00Z", "revokedAt": None,
        "revocationReason": None, "humanThresholdOwner": "TEST_ONLY_OWNER",
        "reviewer": {"reviewerId": "TEST_ONLY_REVIEWER", "keyId": "TEST_ONLY_KEY", "algorithm": "ed25519", "publicKeyPem": keys["publicKeyPem"], "publicKeyFingerprint": keys["fingerprint"]},
        "scope": {"objective": authority.OBJECTIVE, "gate": 12, "version": "v0.8", "exit": authority.EXIT, "doneCheckHumanReview": True, "gate12HumanThreshold": True},
        "doneCheckAuthority": {"allowedDecisions": ["accepted", "revise", "rejected"]},
        "humanThresholdAuthority": {"allowedDecisions": ["ACCEPT", "HOLD"]},
        "payloadDigest": "",
    }
    value["payloadDigest"] = authority.authority_digest(value)
    return value


DONECHECK_FIXTURE = r'''
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const input = JSON.parse(readFileSync(0, "utf8"));
const runtime = await import(pathToFileURL(input.runtime).href);
const review = input.review;
const attestation = runtime.signHumanReviewAttestation(review, {reviewerId: review.reviewerId, keyId: input.keyId, privateKeyPem: input.privateKeyPem, signedAt: input.signedAt});
const ledger = new runtime.JsonlAuditLedger(input.auditPath);
const receipt = await runtime.recordVerifiedFinish({verificationResult: input.result, review, attestation, authority: {reviewerId: review.reviewerId, keyId: input.keyId, publicKeyPem: input.publicKeyPem, allowedDecisions: ["accepted"]}, ledger, finishId: "finish-g12"});
writeFileSync(input.reviewPath, JSON.stringify(review));
writeFileSync(input.attestationPath, JSON.stringify(attestation));
writeFileSync(input.receiptPath, JSON.stringify(receipt));
process.stdout.write(JSON.stringify(receipt));
'''

SIGN_REVIEW = r'''
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const input = JSON.parse(readFileSync(0, "utf8"));
const runtime = await import(pathToFileURL(input.runtime).href);
const attestation = runtime.signHumanReviewAttestation(input.review, {reviewerId: input.review.reviewerId, keyId: input.keyId, privateKeyPem: input.privateKeyPem, signedAt: input.signedAt});
writeFileSync(input.attestationPath, JSON.stringify(attestation));
'''


def resign_review(f: dict, decision: str) -> None:
    review = json.loads(f["review_path"].read_text())
    review["decision"] = decision
    write_json(f["review_path"], review)
    result = subprocess.run(
        ["node", "--experimental-loader", bridge.NODE_EXTENSION_LOADER, "--input-type=module", "-e", SIGN_REVIEW],
        input=json.dumps({"runtime": str(authority.DONECHECK_RUNTIME / "dist/donecheck-runtime-node.js"), "review": review, "keyId": f["auth"]["reviewer"]["keyId"], "privateKeyPem": f["keys"]["privateKeyPem"], "signedAt": "2026-09-28T08:01:01Z", "attestationPath": str(f["attestation_path"])}),
        text=True, capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def fixture(root: Path, decision: str = "ACCEPT") -> dict:
    keys = run_key_helper({"operation": "generate"})
    auth = make_authority(keys)
    auth_path = root / "authority.json"; write_json(auth_path, auth)
    control = {"repository": candidate.CONTROL_REPOSITORY, "branch": candidate.CONTROL_BRANCH, "head": "a" * 40, "base": "b" * 40, "remoteFeatureHead": "a" * 40, "remoteFeatureParity": True, "worktreeClean": True}
    product = {"repository": candidate.PRODUCT_REPOSITORY, "branch": candidate.PRODUCT_BRANCH, "head": "c" * 40, "base": "d" * 40, "worktreeClean": True, "publicationState": candidate.PRODUCT_PUBLICATION}
    manifest = verification_manifest(root)
    evidence_path = root / "evidence.json"; write_json(evidence_path, manifest)
    unresolved_path = root / "unresolved.json"; write_json(unresolved_path, {"schema": candidate.LEDGER_SCHEMA, "items": []})
    snapshot_path = root / "snapshot.json"; write_json(snapshot_path, {"gate11": "VERIFIED_LOCKED", "gate12": "ACTIVE"})
    contract_path = root / "contract.json"; write_json(contract_path, {"exit": candidate.EXIT})
    paths = {"evidenceManifest": evidence_path, "unresolvedDeferredLedger": unresolved_path, "canonicalSnapshot": snapshot_path, "acceptanceContract": contract_path}
    bindings = {"controlHead": control["head"], "productHead": product["head"], "doneCheckVersion": candidate.DONECHECK_VERSION, "doneCheckSha": candidate.DONECHECK_SHA, **{k + "Digest": candidate.file_digest(v) for k, v in paths.items()}}
    result = bridge.reproduce_verification_result(manifest["verificationInput"])
    machine_path = root / "machine.json"; write_json(machine_path, {"schema": candidate.MACHINE_SCHEMA, "bindings": bindings, "verificationResult": result})
    review = {"id": "review-g12", "taskId": result["taskId"], "verificationResultId": result["id"], "decision": "accepted", "reason": "accepted evidence", "reviewerId": auth["reviewer"]["reviewerId"], "reviewedAt": "2026-09-28T08:01:00Z"}
    review_path, attestation_path, receipt_path, audit_path = (root / n for n in ("review.json", "attestation.json", "receipt.json", "audit.jsonl"))
    donecheck = subprocess.run(["node", "--experimental-loader", bridge.NODE_EXTENSION_LOADER, "--input-type=module", "-e", DONECHECK_FIXTURE], input=json.dumps({"runtime": str(authority.DONECHECK_RUNTIME / "dist/donecheck-runtime-node.js"), "review": review, "result": result, "keyId": auth["reviewer"]["keyId"], "privateKeyPem": keys["privateKeyPem"], "publicKeyPem": keys["publicKeyPem"], "signedAt": "2026-09-28T08:01:01Z", "auditPath": str(audit_path), "reviewPath": str(review_path), "attestationPath": str(attestation_path), "receiptPath": str(receipt_path)}), text=True, capture_output=True, check=False)
    if donecheck.returncode != 0: raise AssertionError(donecheck.stderr)
    receipt = json.loads(donecheck.stdout)
    artifacts = {"machineResult": {"path": str(machine_path), "digest": candidate.file_digest(machine_path)}, "evidenceManifest": {"path": str(evidence_path), "digest": candidate.file_digest(evidence_path)}, "unresolvedDeferredLedger": {"path": str(unresolved_path), "digest": candidate.file_digest(unresolved_path)}, "canonicalSnapshot": {"path": str(snapshot_path), "digest": candidate.file_digest(snapshot_path)}, "acceptanceContract": {"path": str(contract_path), "digest": candidate.file_digest(contract_path)}, "verifiedFinishReceipt": {"path": str(receipt_path), "digest": candidate.file_digest(receipt_path)}, "auditLedger": {"path": str(audit_path), "digest": candidate.file_digest(audit_path)}}
    chain = {"machineResultDigest": artifacts["machineResult"]["digest"], "evidenceManifestDigest": artifacts["evidenceManifest"]["digest"], "unresolvedDeferredLedgerDigest": artifacts["unresolvedDeferredLedger"]["digest"], "canonicalSnapshotDigest": artifacts["canonicalSnapshot"]["digest"], "acceptanceContractDigest": artifacts["acceptanceContract"]["digest"], "verifiedFinishReceiptDigest": artifacts["verifiedFinishReceipt"]["digest"], "auditHead": receipt["auditHeadHash"]}
    bundle = candidate.build_candidate_bundle(control=control, product=product, done_check={"version": candidate.DONECHECK_VERSION, "exactSha": candidate.DONECHECK_SHA}, authority={"reviewerId": auth["reviewer"]["reviewerId"], "keyId": auth["reviewer"]["keyId"], "authorityDigest": auth["payloadDigest"]}, chain=chain, target={"targetVersion": "v0.8", "intendedExit": candidate.EXIT}, artifacts=artifacts)
    bundle_path = root / "bundle.json"; write_json(bundle_path, bundle)
    payload = {"schema": authority.THRESHOLD_SCHEMA_ID, "decisionId": "", "authorityDigest": auth["payloadDigest"], "reviewerId": auth["reviewer"]["reviewerId"], "keyId": auth["reviewer"]["keyId"], "controlHead": control["head"], "productHead": product["head"], "doneCheckVersion": candidate.DONECHECK_VERSION, "doneCheckSha": candidate.DONECHECK_SHA, **chain, "targetVersion": "v0.8", "intendedExit": candidate.EXIT, "decision": decision, "decidedAt": "2026-09-28T08:02:00Z"}
    payload["decisionId"] = authority.decision_id(payload)
    envelope = {"payload": payload, "payloadDigest": authority.digest(payload), "attestation": {"scheme": "ed25519", "reviewerId": payload["reviewerId"], "keyId": payload["keyId"], "signedAt": payload["decidedAt"], "signatureBase64": ""}}
    envelope["attestation"]["signatureBase64"] = run_key_helper({"operation": "sign", "attestationSchema": authority.THRESHOLD_ATTESTATION_SCHEMA_ID, "signedAt": payload["decidedAt"], "payload": payload, "privateKeyPem": keys["privateKeyPem"]})["signatureBase64"]
    envelope_path = root / "threshold.json"; write_json(envelope_path, envelope)
    return locals()


def live_truth_fixture() -> tuple[dict, dict, object]:
    head, base = "a" * 40, "b" * 40
    acceptance = {
        "state": "PASS", "branch": candidate.CONTROL_BRANCH, "head": head,
        "originMain": base, "originBranch": head, "clean": True,
        "acceptance": {key: "PASS" for key in (
            "targetedTests", "fullRegression", "diffCheck", "remoteBranchParity",
            "mainAncestor", "canonicalContext", "sessionStart",
        )},
    }
    session = {"currentV08": {"currentProductSource": {
        "repository": candidate.PRODUCT_REPOSITORY,
        "branch": candidate.PRODUCT_BRANCH, "localVerifiedHead": "c" * 40,
        "baseOriginMain": "d" * 40, "worktree": "CLEAN",
        "publicationState": candidate.PRODUCT_PUBLICATION,
    }}}
    def git_value(repo: Path, *args: str) -> str:
        table = {
            (str(executor.ROOT), "branch", "--show-current"): candidate.CONTROL_BRANCH,
            (str(executor.ROOT), "rev-parse", "HEAD"): head,
            (str(executor.ROOT), "status", "--porcelain"): "",
            (str(executor.ROOT), "merge-base", "HEAD", base): base,
            (str(executor.PRODUCT_ROOT), "branch", "--show-current"): candidate.PRODUCT_BRANCH,
            (str(executor.PRODUCT_ROOT), "rev-parse", "HEAD"): "c" * 40,
            (str(executor.PRODUCT_ROOT), "rev-parse", "origin/main"): "d" * 40,
            (str(executor.PRODUCT_ROOT), "status", "--porcelain"): "",
        }
        return table[(str(repo), *args)]
    return acceptance, session, git_value


class ExecutorTests(unittest.TestCase):
    def run_fixture(self, f: dict, root: Path) -> dict:
        return executor.execute_prelock(bundle_path=f["bundle_path"], threshold_envelope_path=f["envelope_path"], human_review_path=f["review_path"], attestation_path=f["attestation_path"], verified_finish_path=f["receipt_path"], audit_path=f["audit_path"], expected_control=f["control"], expected_product=f["product"], authority_path=f["auth_path"], replay_path=root/"replay.json", lock_path=root/"lock", observed_at="2026-09-28T09:00:00Z", production_use=False)

    def test_positive_ephemeral_chain_and_exact_replay_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            result = self.run_fixture(f, root)
            self.assertEqual(result["state"], "PASS")
            records = json.loads((Path(directory)/"replay.json").read_text())["records"]
            self.assertEqual(set(records[0]), {"decisionId", "terminalCandidateId", "payloadDigest", "envelopeDigest", "decision"})

    def test_signed_hold_never_becomes_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root, decision="HOLD")
            result = self.run_fixture(f, root)
            self.assertEqual(result["state"], "HOLD")
            self.assertEqual(json.loads((Path(directory)/"replay.json").read_text())["records"][0]["decision"], "HOLD")

    def test_process_lock_rejects_concurrent_writer_and_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "lock"
            with executor.exclusive_execution_lock(lock):
                with self.assertRaises(executor.ExecutionHold):
                    with executor.exclusive_execution_lock(lock):
                        pass
            with executor.exclusive_execution_lock(lock):
                pass

    def test_missing_and_stale_handoff_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(executor.execute_from_runtime_handoff(Path(directory)/"missing.json")["state"], "HOLD")
            path = Path(directory)/"handoff.json"; write_json(path, {"schema": "enguru.mac-engineer.v08-gate12-pre005-handoff/v1", "bundlePath": "x", "thresholdEnvelopePath": "x", "humanReviewPath": "x", "attestationPath": "x", "verifiedFinishPath": "x", "auditPath": "x", "observedAt": "2026-09-28T09:00:00Z"})
            with mock.patch.object(executor, "derive_live_truth", side_effect=executor.ExecutionHold("LOCAL_CANDIDATE_ACCEPTANCE_STALE")):
                self.assertIn("STALE", executor.execute_from_runtime_handoff(path)["reason"])

    def test_rejected_review_and_fake_receipts_hold(self):
        for decision in ("rejected", "revise"):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); f = fixture(root); resign_review(f, decision)
                reviewed = bridge.verify_human_review_and_verified_finish(review_path=f["review_path"], attestation_path=f["attestation_path"], receipt_path=f["receipt_path"], audit_path=f["audit_path"], authority=f["auth"])
                self.assertEqual(reviewed["state"], "HOLD")
                self.assertIn("HUMAN_REVIEW_ACCEPTED_REQUIRED", reviewed["errors"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            receipt = json.loads(f["receipt_path"].read_text()); receipt["verificationResultId"] = "wrong"; write_json(f["receipt_path"], receipt)
            reviewed = bridge.verify_human_review_and_verified_finish(review_path=f["review_path"], attestation_path=f["attestation_path"], receipt_path=f["receipt_path"], audit_path=f["audit_path"], authority=f["auth"])
            self.assertEqual(reviewed["state"], "HOLD")
            self.assertIn("VERIFIED_FINISH_RESULT_MISMATCH", reviewed["errors"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            receipt = json.loads(f["receipt_path"].read_text()); receipt["auditHeadHash"] = "sha256:" + "0" * 64; write_json(f["receipt_path"], receipt)
            reviewed = bridge.verify_human_review_and_verified_finish(review_path=f["review_path"], attestation_path=f["attestation_path"], receipt_path=f["receipt_path"], audit_path=f["audit_path"], authority=f["auth"])
            self.assertEqual(reviewed["state"], "HOLD")
            self.assertIn("VERIFIED_FINISH_AUDIT_HEAD_MISMATCH", reviewed["errors"])

    def test_stale_machine_and_corrupt_or_conflicting_replay_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            machine = json.loads((root/"machine.json").read_text()); machine["bindings"]["controlHead"] = "9" * 40; write_json(root/"machine.json", machine)
            bundle = json.loads(f["bundle_path"].read_text())
            bundle["artifacts"]["machineResult"]["digest"] = candidate.file_digest(root/"machine.json")
            bundle["chain"]["machineResultDigest"] = bundle["artifacts"]["machineResult"]["digest"]
            bundle["terminalCandidateId"] = authority.terminal_candidate_id({"controlHead": bundle["control"]["head"], "productHead": bundle["product"]["head"], "doneCheckVersion": bundle["doneCheck"]["version"], "doneCheckSha": bundle["doneCheck"]["exactSha"], **bundle["chain"], "targetVersion": "v0.8", "intendedExit": candidate.EXIT})
            write_json(f["bundle_path"], bundle)
            self.assertEqual(self.run_fixture(f, root)["state"], "HOLD")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            write_json(root/"replay.json", {"schema": "enguru.mac-engineer.v08-gate12-replay/v1", "records": [{"wrong": True}]})
            self.assertEqual(self.run_fixture(f, root)["state"], "HOLD")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            self.assertEqual(self.run_fixture(f, root)["state"], "PASS")
            replay = json.loads((root/"replay.json").read_text()); replay["records"][0]["envelopeDigest"] = "sha256:" + "0" * 64; write_json(root/"replay.json", replay)
            self.assertEqual(self.run_fixture(f, root)["state"], "HOLD")

    def test_backdated_handoff_cannot_make_expired_authority_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); f = fixture(root)
            with mock.patch.object(executor, "_utc_now", return_value="2026-10-29T00:00:00Z"):
                result = executor.execute_prelock(bundle_path=f["bundle_path"], threshold_envelope_path=f["envelope_path"], human_review_path=f["review_path"], attestation_path=f["attestation_path"], verified_finish_path=f["receipt_path"], audit_path=f["audit_path"], expected_control=f["control"], expected_product=f["product"], authority_path=f["auth_path"], replay_path=root/"replay.json", lock_path=root/"lock", observed_at="2026-09-28T00:00:01Z", production_use=True)
            self.assertEqual(result["state"], "HOLD")
            self.assertIn("AUTHORITY_EXPIRED", result["reason"])

    def test_fresh_remote_feature_drift_holds(self):
        acceptance, session, git_value = live_truth_fixture()
        with mock.patch.object(executor, "_strict_object", side_effect=[acceptance, session]), mock.patch.object(executor, "_git", side_effect=git_value), mock.patch.object(executor, "_fresh_control_remote", return_value=("b" * 40, "e" * 40)):
            with self.assertRaisesRegex(executor.ExecutionHold, "LOCAL_CANDIDATE_ACCEPTANCE_STALE"):
                executor.derive_live_truth()

    def test_fresh_remote_main_drift_holds(self):
        acceptance, session, git_value = live_truth_fixture()
        with mock.patch.object(executor, "_strict_object", side_effect=[acceptance, session]), mock.patch.object(executor, "_git", side_effect=git_value), mock.patch.object(executor, "_fresh_control_remote", return_value=("e" * 40, "a" * 40)):
            with self.assertRaisesRegex(executor.ExecutionHold, "LOCAL_CANDIDATE_ACCEPTANCE_STALE"):
                executor.derive_live_truth()

    def test_fresh_remote_unavailable_holds(self):
        acceptance, _, git_value = live_truth_fixture()
        with mock.patch.object(executor, "_strict_object", return_value=acceptance), mock.patch.object(executor, "_git", side_effect=git_value), mock.patch.object(executor, "_fresh_control_remote", side_effect=executor.ExecutionHold("FRESH_REMOTE_TRUTH_UNAVAILABLE")):
            with self.assertRaisesRegex(executor.ExecutionHold, "FRESH_REMOTE_TRUTH_UNAVAILABLE"):
                executor.derive_live_truth()


if __name__ == "__main__":
    unittest.main()
