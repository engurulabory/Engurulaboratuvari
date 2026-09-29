#!/usr/bin/env python3
"""Publish final acceptance from the reconciled Gate 12 evidence."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

try:
    from mac_engineer_v08_gate12_finalizer import (
        ROOT, SESSION_PATH, ROADMAP_PATH, REGISTRY_PATH, HANDOFF_PATH,
        EVIDENCE_ROOT, GATE12, EXIT, FinalizationHold, _git, _load,
        _verified_publication,
    )
    from mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle
    from mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from mac_engineer_v08_gate12_pre005_executor import derive_live_truth, REPLAY_PATH
    from mac_engineer_v08_gate12_pre005_replay import PersistentReplayAuthority
    from mac_engineer_v08_gate12_reviewer_authority import (
        EXPECTED_AUTHORITY_ARTIFACT, load_authority, verify_authority,
        verify_threshold_envelope_json,
    )
    from mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_finalizer import (
        ROOT, SESSION_PATH, ROADMAP_PATH, REGISTRY_PATH, HANDOFF_PATH,
        EVIDENCE_ROOT, GATE12, EXIT, FinalizationHold, _git, _load,
        _verified_publication,
    )
    from tools.mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle
    from tools.mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from tools.mac_engineer_v08_gate12_pre005_executor import derive_live_truth, REPLAY_PATH
    from tools.mac_engineer_v08_gate12_pre005_replay import PersistentReplayAuthority
    from tools.mac_engineer_v08_gate12_reviewer_authority import (
        EXPECTED_AUTHORITY_ARTIFACT, load_authority, verify_authority,
        verify_threshold_envelope_json,
    )
    from tools.mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish


def publish_final_acceptance_receipt(*, authority_path: Path = EXPECTED_AUTHORITY_ARTIFACT,
                                     replay_path: Path = REPLAY_PATH) -> dict[str, Any]:
    """Produce a machine receipt, then HOLD until its digest is canonically locked."""
    session, roadmap, registry = _load(SESSION_PATH), _load(ROADMAP_PATH), _load(REGISTRY_PATH)
    v08 = session.get("currentV08") or {}
    gate, closure = v08.get("gate12") or {}, v08.get("closureContract") or {}
    current = roadmap.get("current") or {}
    version = next((v for v in roadmap.get("versions", []) if v.get("version") == "v0.8"), {})
    finish = version.get("verifiedFinishContract") or {}
    if (
        session.get("currentObjective") != GATE12
        or v08.get("state") != "ACTIVE"
        or gate.get("state") != "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"
        or gate.get("canonicalLockCreated") is not False
        or gate.get("executionStarted") is not True
        or gate.get("humanDecision") != "ACCEPT"
        or gate.get("machineResult") != "PASS_11_OF_11"
        or closure.get("passedGates") != list(range(1, 12))
        or closure.get("activeGate") != 12
        or closure.get("remainingGates") != [12]
        or current.get("completed", [])[-1:] != ["V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING_PASS"]
        or current.get("remaining") != [GATE12]
        or current.get("activeGate") != 12
        or version.get("state") != "ACTIVE"
        or finish.get("state") != "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"
        or finish.get("passed") != list(range(1, 12))
        or finish.get("remaining") != [12]
        or (registry.get("actions") or {}).get(GATE12, {}).get("canonicalLock") is not False
    ):
        raise FinalizationHold("CANONICAL_LOCK_RECONCILIATION_MISMATCH")

    final_path = ROOT / "governance/mac-engineer/V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json"
    final = _load(final_path)
    if (
        gate.get("finalAcceptanceCandidate") != final_path.relative_to(ROOT).as_posix()
        or final.get("schema") != "enguru.mac-engineer.v08-gate12-final-acceptance/v1"
        or final.get("state") != "CANDIDATE_PENDING_FRESH_REMOTE_READBACK"
        or final.get("objective") != GATE12
        or final.get("exit") != EXIT
        or final.get("postCommitVerificationRequired") is not True
        or final.get("humanDecision") != "ACCEPT"
        or (final.get("doneCheck") or {}).get("criteria") != "PASS_11_OF_11"
    ):
        raise FinalizationHold("FINAL_ACCEPTANCE_CANDIDATE_MISMATCH")

    lock_path = Path(str(gate.get("lockEvidence") or ""))
    lock_digest = gate.get("lockEvidenceDigest")
    if not isinstance(lock_digest, str) or not lock_digest.startswith("sha256:"):
        raise FinalizationHold("LOCK_EVIDENCE_DIGEST_REQUIRED")
    lock = _verified_publication(lock_path, lock_digest)
    receipt_path = Path(str(gate.get("fieldAcceptanceReceipt") or ""))
    field_digest = gate.get("fieldAcceptanceReceiptDigest")
    if not isinstance(field_digest, str) or not field_digest.startswith("sha256:"):
        raise FinalizationHold("FIELD_RECEIPT_DIGEST_REQUIRED")
    receipt = _verified_publication(receipt_path, field_digest)
    if (
        lock.get("schema") != "enguru.mac-engineer.v08-gate12-lock-evidence/v1"
        or lock.get("state") != "LOCK_EVIDENCE_PENDING_CANONICAL_COMMIT"
        or lock.get("canonicalLockCreated") is not False
        or lock.get("fieldReceipt") != str(receipt_path)
        or lock.get("fieldReceiptDigest") != field_digest
        or lock.get("terminalCandidateId") != gate.get("terminalCandidateId")
        or lock.get("humanDecisionId") != receipt.get("humanDecisionId")
        or lock.get("acceptedControlHead") != gate.get("acceptedControlHead")
        or lock.get("reconciliationControlHead") != gate.get("reconciliationControlHead")
        or lock.get("productHead") != receipt.get("product", {}).get("head")
        or lock.get("doneCheck") != receipt.get("doneCheck")
        or lock.get("externalA09State") != "HOLD"
        or receipt.get("externalA09State") != "HOLD"
        or lock.get("productPublicationState") != "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY"
        or receipt.get("productPublicationState") != lock.get("productPublicationState")
        or receipt.get("humanDecision") != "ACCEPT"
        or receipt.get("prelock") != "PASS"
        or receipt.get("canonicalLockCreated") is not False
        or ((session.get("observedV07A09LocalFallback") or {}).get("canonicalA09State")) != "HOLD"
        or (v08.get("currentProductSource") or {}).get("publicationState") != lock.get("productPublicationState")
        or final.get("fieldReceipt") != str(receipt_path)
        or final.get("fieldReceiptDigest") != field_digest
        or final.get("lockEvidence") != str(lock_path)
        or final.get("lockEvidenceDigest") != lock_digest
        or final.get("terminalCandidateId") != lock.get("terminalCandidateId")
        or final.get("humanDecisionId") != lock.get("humanDecisionId")
        or final.get("acceptedControlHead") != lock.get("acceptedControlHead")
        or final.get("reconciliationControlHead") != lock.get("reconciliationControlHead")
        or final.get("externalA09State") != lock.get("externalA09State")
        or final.get("productPublicationState") != lock.get("productPublicationState")
        or final.get("doneCheck", {}).get("version") != lock.get("doneCheck", {}).get("version")
        or final.get("doneCheck", {}).get("exactSha") != lock.get("doneCheck", {}).get("exactSha")
    ):
        raise FinalizationHold("LOCK_FIELD_BINDING_MISMATCH")

    control, product = derive_live_truth()
    if (
        _git("merge-base", lock["reconciliationControlHead"], control["head"])
        != lock["reconciliationControlHead"]
        or _git("merge-base", lock["acceptedControlHead"], control["head"])
        != lock["acceptedControlHead"]
        or receipt.get("product") != product
    ):
        raise FinalizationHold("LOCK_FRESH_TRUTH_MISMATCH")

    bundle_path = Path(str(receipt.get("bundlePath") or ""))
    if file_digest(bundle_path) != receipt.get("bundleDigest"):
        raise FinalizationHold("LOCK_BUNDLE_DIGEST_MISMATCH")
    bundle = load_candidate_bundle(bundle_path)
    if any(receipt.get(k) != bundle.get(k) for k in
           ("terminalCandidateId", "control", "product", "doneCheck", "chain")):
        raise FinalizationHold("LOCK_BUNDLE_BINDING_MISMATCH")
    ledger = _load(Path(bundle["artifacts"]["unresolvedDeferredLedger"]["path"]))
    if ledger.get("items") != [
        {"id": "V07_A09_EXTERNAL_CI_CONFIRMATION", "classification": "EXTERNAL",
         "severity": "NON_CRITICAL", "state": "OPEN"},
        {"id": "V08_PRODUCT_REMOTE_PUBLICATION", "classification": "DEFERRED",
         "severity": "NON_CRITICAL", "state": "OPEN"},
    ]:
        raise FinalizationHold("LOCK_DEFERRED_LEDGER_MISMATCH")

    observed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    authority = load_authority(authority_path)
    authority_result = verify_authority(authority, observed_at=observed, production_use=True,
                                        artifact_path=authority_path)
    if authority_result.get("state") != "PASS":
        raise FinalizationHold("LOCK_REVIEWER_AUTHORITY_HOLD")
    handoff = _load(HANDOFF_PATH)
    if (
        Path(str(handoff.get("bundlePath") or "")).resolve() != bundle_path.resolve()
        or Path(str(handoff.get("thresholdEnvelopePath") or "")).resolve()
           != Path(str(receipt.get("thresholdEnvelopePath") or "")).resolve()
    ):
        raise FinalizationHold("LOCK_HANDOFF_MISMATCH")
    review = verify_human_review_and_verified_finish(
        review_path=Path(handoff["humanReviewPath"]),
        attestation_path=Path(handoff["attestationPath"]),
        receipt_path=Path(handoff["verifiedFinishPath"]),
        audit_path=Path(handoff["auditPath"]), authority=authority,
    )
    if (
        review.get("state") != "PASS"
        or review.get("auditHead") != bundle["chain"]["auditHead"]
        or file_digest(Path(handoff["verifiedFinishPath"]))
           != bundle["chain"]["verifiedFinishReceiptDigest"]
    ):
        raise FinalizationHold("LOCK_DONECHECK_FINISH_MISMATCH")
    envelope_path = Path(receipt["thresholdEnvelopePath"])
    if file_digest(envelope_path) != receipt.get("thresholdEnvelopeDigest"):
        raise FinalizationHold("LOCK_THRESHOLD_DIGEST_MISMATCH")
    envelope = _load(envelope_path)
    if (envelope.get("payload") or {}).get("decision") != "ACCEPT":
        raise FinalizationHold("LOCK_SIGNED_ACCEPT_REQUIRED")
    threshold = verify_threshold_envelope_json(
        authority_path.read_text(encoding="utf-8"),
        envelope_path.read_text(encoding="utf-8"),
        expected={
            "controlHead": bundle["control"]["head"],
            "productHead": bundle["product"]["head"],
            "doneCheckVersion": bundle["doneCheck"]["version"],
            "doneCheckSha": bundle["doneCheck"]["exactSha"],
            **bundle["chain"],
            "targetVersion": bundle["target"]["targetVersion"],
            "intendedExit": bundle["target"]["intendedExit"],
        },
        observed_at=observed, production_use=True, artifact_path=authority_path,
        replay_backend=PersistentReplayAuthority(replay_path),
    )
    if (
        threshold.get("state") != "PASS"
        or threshold.get("decisionId") != receipt.get("humanDecisionId")
        or threshold.get("terminalCandidateId") != bundle["terminalCandidateId"]
    ):
        raise FinalizationHold("LOCK_SIGNED_THRESHOLD_MISMATCH")
    final_receipt_path = lock_path.parent / "final-acceptance-receipt.json"
    final_receipt = {
        "schema": "enguru.mac-engineer.v08-gate12-final-acceptance-receipt/v1",
        "state": "FINAL_ACCEPTANCE_PASS_PENDING_CANONICAL_LOCK",
        "claim": "GATE12_FINAL_ACCEPTANCE_VERIFIED",
        "controlHead": control["head"], "productHead": product["head"],
        "fieldReceipt": str(receipt_path), "fieldReceiptDigest": field_digest,
        "lockEvidence": str(lock_path), "lockEvidenceDigest": lock_digest,
        "finalAcceptanceCandidate": str(final_path),
        "finalAcceptanceCandidateDigest": file_digest(final_path),
        "terminalCandidateId": bundle["terminalCandidateId"],
        "machineResult": "PASS_11_OF_11",
        "humanDecision": "ACCEPT", "humanDecisionId": threshold["decisionId"],
        "authorityDigest": authority_result["authorityDigest"],
        "externalA09State": "HOLD",
        "productPublicationState": product["publicationState"],
        "canonicalLockCreated": False,
    }
    published = CrashDurablePublisher().publish_json(final_receipt_path, final_receipt)
    _verified_publication(final_receipt_path, published.digest)
    return {
        "state": "HOLD", "reason": "GATE12_FINAL_RECEIPT_PENDING_CANONICAL_LOCK",
        "finalAcceptanceCandidate": str(final_path),
        "lockEvidence": str(lock_path), "lockEvidenceDigest": lock_digest,
        "fieldReceipt": str(receipt_path), "fieldReceiptDigest": field_digest,
        "finalAcceptanceReceipt": str(final_receipt_path),
        "finalAcceptanceReceiptDigest": published.digest,
        "controlHead": control["head"], "productHead": product["head"],
        "externalA09State": "HOLD",
        "productPublicationState": product["publicationState"],
        "canonicalLockCreated": False, "nextAction": GATE12,
    }


if __name__ == "__main__":
    try:
        result = publish_final_acceptance_receipt()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    except (FinalizationHold, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
