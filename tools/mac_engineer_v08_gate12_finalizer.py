#!/usr/bin/env python3
"""Gate 12 field receipt; canonical reconciliation and lock are separate gates."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle
    from mac_engineer_v08_gate12_pre005_executor import derive_live_truth, REPLAY_PATH
    from mac_engineer_v08_gate12_pre005_replay import PersistentReplayAuthority
    from mac_engineer_v08_gate12_reviewer_authority import EXPECTED_AUTHORITY_ARTIFACT, load_authority, verify_authority, verify_threshold_envelope_json
    from mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from tools.mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from tools.mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle
    from tools.mac_engineer_v08_gate12_pre005_executor import derive_live_truth, REPLAY_PATH
    from tools.mac_engineer_v08_gate12_pre005_replay import PersistentReplayAuthority
    from tools.mac_engineer_v08_gate12_reviewer_authority import EXPECTED_AUTHORITY_ARTIFACT, load_authority, verify_authority, verify_threshold_envelope_json
    from tools.mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish

ROOT = Path(__file__).resolve().parents[1]
SESSION_PATH = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
ROADMAP_PATH = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
REGISTRY_PATH = ROOT / "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json"
HANDOFF_PATH = Path.home() / "Enguru/Runtime/MacEngineer/gate12/pre005/handoff.json"
EVIDENCE_ROOT = Path.home() / "Enguru/Evidence/MacEngineer/v0.8/gate12-final"
EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
GATE12 = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"


class FinalizationHold(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizationHold(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def finalize(*, handoff_path: Path = HANDOFF_PATH) -> dict[str, Any]:
    """Publish a bound field receipt, then HOLD until repository reconciliation."""
    if not handoff_path.is_file():
        raise FinalizationHold("PRE005_HANDOFF_MISSING")
    prelock = execute_from_runtime_handoff(handoff_path)
    if prelock.get("state") != "PASS" or prelock.get("batch2PreLock") != "PASS":
        raise FinalizationHold("PRE005_NOT_PASS:" + str(prelock.get("reason", "UNKNOWN")))

    handoff = _load(handoff_path)
    bundle_path = Path(handoff["bundlePath"])
    bundle = load_candidate_bundle(bundle_path)
    session, roadmap, registry = _load(SESSION_PATH), _load(ROADMAP_PATH), _load(REGISTRY_PATH)
    gate = (session.get("currentV08") or {}).get("gate12") or {}
    current = roadmap.get("current") or {}
    action = (registry.get("actions") or {}).get(GATE12) or {}
    if (
        session.get("currentObjective") != GATE12
        or gate.get("state") != "ACTIVE"
        or gate.get("executionStarted") is not False
        or current.get("activeObjective") != GATE12
        or current.get("activeGate") != 12
        or action.get("batch3Boundary") != "FINAL_ACCEPTANCE_RECEIPT_AND_CANONICAL_LOCK"
        or action.get("finalAcceptanceReceipt") is not False
        or action.get("canonicalLock") is not False
    ):
        raise FinalizationHold("CANONICAL_PREEXECUTION_STATE_MISMATCH")

    envelope_path = Path(handoff["thresholdEnvelopePath"])
    envelope = _load(envelope_path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict) or payload.get("decision") != "ACCEPT":
        raise FinalizationHold("SIGNED_ACCEPT_DECISION_REQUIRED")
    if (
        payload.get("controlHead") != bundle["control"]["head"]
        or payload.get("productHead") != bundle["product"]["head"]
    ):
        raise FinalizationHold("SIGNED_DECISION_HEAD_MISMATCH")
    decision_id, decided_at = payload.get("decisionId"), payload.get("decidedAt")
    if not isinstance(decision_id, str) or not decision_id:
        raise FinalizationHold("SIGNED_DECISION_ID_REQUIRED")
    if not isinstance(decided_at, str) or not decided_at:
        raise FinalizationHold("SIGNED_DECISION_TIME_REQUIRED")

    # The signed time is stable across retries. Prelock checks authority expiry
    # using the executing Mac's fresh UTC clock, never this signed timestamp.
    run_id = hashlib.sha256(bundle["terminalCandidateId"].encode("utf-8")).hexdigest()[:24]
    receipt_path = EVIDENCE_ROOT / run_id / "field-acceptance-receipt.json"
    receipt = {
        "schema": "enguru.mac-engineer.v08-gate12-field-acceptance/v1",
        "state": "FIELD_ACCEPTED_PENDING_CANONICAL_RECONCILIATION",
        "gate": 12, "intendedExit": EXIT,
        "humanDecision": "ACCEPT", "humanDecisionId": decision_id,
        "humanDecidedAt": decided_at,
        "terminalCandidateId": bundle["terminalCandidateId"],
        "doneCheck": bundle["doneCheck"], "control": bundle["control"],
        "product": bundle["product"], "chain": bundle["chain"],
        "bundlePath": str(bundle_path), "bundleDigest": file_digest(bundle_path),
        "thresholdEnvelopePath": str(envelope_path),
        "thresholdEnvelopeDigest": file_digest(envelope_path),
        "prelock": "PASS",
        "externalA09State": (session.get("observedV07A09LocalFallback") or {}).get("canonicalA09State"),
        "productPublicationState": ((session.get("currentV08") or {}).get("currentProductSource") or {}).get("publicationState"),
        "canonicalLockCreated": False,
    }
    result = CrashDurablePublisher().publish_json(receipt_path, receipt)
    return {
        "state": "HOLD", "reason": "GATE12_CANONICAL_RECONCILIATION_REQUIRED",
        "fieldReceipt": str(receipt_path), "fieldReceiptDigest": result.digest,
        "receiptIdempotent": result.idempotent, "executionStarted": True,
        "canonicalLockCreated": False, "nextAction": GATE12,
    }


def _verified_publication(path: Path, expected_digest: str) -> dict[str, Any]:
    if not path.resolve().is_relative_to(EVIDENCE_ROOT.resolve()):
        raise FinalizationHold("FIELD_RECEIPT_OUTSIDE_EVIDENCE_ROOT")
    marker = CrashDurablePublisher.marker_path(path)
    if CrashDurablePublisher.staging_paths(path):
        raise FinalizationHold("FIELD_RECEIPT_STAGING_AMBIGUOUS")
    data = path.read_bytes()
    metadata = _load(marker)
    if (
        file_digest(path) != expected_digest
        or metadata.get("schema") != "enguru.mac-engineer.publication/v1"
        or metadata.get("digest") != expected_digest
        or metadata.get("byteLength") != len(data)
    ):
        raise FinalizationHold("FIELD_RECEIPT_PUBLICATION_MISMATCH")
    return _load(path)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        check=False, timeout=30,
    )
    if result.returncode:
        raise FinalizationHold("CONTROL_ANCESTRY_UNAVAILABLE")
    return result.stdout.strip()


def publish_lock_evidence(*, authority_path: Path = EXPECTED_AUTHORITY_ARTIFACT,
                          replay_path: Path = REPLAY_PATH) -> dict[str, Any]:
    """Verify field acceptance against fresh control truth and publish lock evidence.

    A later repository commit must reconcile the lock digest before final PASS.
    """
    session, roadmap, registry = _load(SESSION_PATH), _load(ROADMAP_PATH), _load(REGISTRY_PATH)
    gate = (session.get("currentV08") or {}).get("gate12") or {}
    current = roadmap.get("current") or {}
    if (
        session.get("currentObjective") != GATE12
        or gate.get("state") != "FIELD_ACCEPTED_PENDING_CANONICAL_LOCK"
        or gate.get("executionStarted") is not True
        or gate.get("canonicalLockCreated") is not False
        or current.get("activeObjective") != GATE12
        or current.get("activeGate") != 12
        or (current.get("gate12FieldAcceptance") or {}).get("digest")
           != gate.get("fieldAcceptanceReceiptDigest")
        or (registry.get("actions") or {}).get(GATE12, {}).get("canonicalLock") is not False
    ):
        raise FinalizationHold("FIELD_ACCEPTANCE_RECONCILIATION_MISMATCH")
    expected_digest = gate.get("fieldAcceptanceReceiptDigest")
    receipt_path = Path(str(gate.get("fieldAcceptanceReceipt") or ""))
    if not isinstance(expected_digest, str) or not expected_digest.startswith("sha256:"):
        raise FinalizationHold("FIELD_RECEIPT_DIGEST_REQUIRED")
    receipt = _verified_publication(receipt_path, expected_digest)
    if (
        receipt.get("schema") != "enguru.mac-engineer.v08-gate12-field-acceptance/v1"
        or receipt.get("state") != "FIELD_ACCEPTED_PENDING_CANONICAL_RECONCILIATION"
        or receipt.get("humanDecision") != "ACCEPT"
        or receipt.get("prelock") != "PASS"
        or receipt.get("canonicalLockCreated") is not False
        or receipt.get("terminalCandidateId") != gate.get("terminalCandidateId")
        or (receipt.get("control") or {}).get("head") != gate.get("acceptedControlHead")
        or receipt.get("externalA09State") != "HOLD"
        or receipt.get("productPublicationState")
           != "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY"
    ):
        raise FinalizationHold("FIELD_RECEIPT_SEMANTICS_MISMATCH")
    control, product = derive_live_truth()
    accepted_head = gate["acceptedControlHead"]
    if _git("merge-base", accepted_head, control["head"]) != accepted_head:
        raise FinalizationHold("ACCEPTED_CONTROL_NOT_ANCESTOR")
    if receipt.get("product") != product:
        raise FinalizationHold("PRODUCT_FIELD_TRUTH_MISMATCH")
    if (
        (session.get("observedV07A09LocalFallback") or {}).get("canonicalA09State") != "HOLD"
        or ((session.get("currentV08") or {}).get("currentProductSource") or {}).get("publicationState")
           != receipt["productPublicationState"]
    ):
        raise FinalizationHold("DEFERRED_CLASSIFICATION_DRIFT")

    bundle_path = Path(str(receipt.get("bundlePath") or ""))
    if file_digest(bundle_path) != receipt.get("bundleDigest"):
        raise FinalizationHold("ACCEPTED_BUNDLE_DIGEST_MISMATCH")
    bundle = load_candidate_bundle(bundle_path)
    if any(receipt.get(name) != bundle.get(name) for name in
           ("terminalCandidateId", "control", "product", "doneCheck", "chain")):
        raise FinalizationHold("ACCEPTED_BUNDLE_BINDING_MISMATCH")
    ledger = _load(Path(bundle["artifacts"]["unresolvedDeferredLedger"]["path"]))
    expected_items = [
        {"id": "V07_A09_EXTERNAL_CI_CONFIRMATION", "classification": "EXTERNAL",
         "severity": "NON_CRITICAL", "state": "OPEN"},
        {"id": "V08_PRODUCT_REMOTE_PUBLICATION", "classification": "DEFERRED",
         "severity": "NON_CRITICAL", "state": "OPEN"},
    ]
    if ledger.get("items") != expected_items:
        raise FinalizationHold("DEFERRED_LEDGER_MISMATCH")

    authority = load_authority(authority_path)
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    checked_authority = verify_authority(
        authority, observed_at=observed_at, production_use=True,
        artifact_path=authority_path,
    )
    if checked_authority.get("state") != "PASS":
        raise FinalizationHold("REVIEWER_AUTHORITY_HOLD")
    handoff = _load(HANDOFF_PATH)
    if Path(str(handoff.get("bundlePath") or "")).resolve() != bundle_path.resolve():
        raise FinalizationHold("HANDOFF_BUNDLE_MISMATCH")
    if Path(str(handoff.get("thresholdEnvelopePath") or "")).resolve() != Path(receipt["thresholdEnvelopePath"]).resolve():
        raise FinalizationHold("HANDOFF_THRESHOLD_MISMATCH")
    review = verify_human_review_and_verified_finish(
        review_path=Path(handoff["humanReviewPath"]),
        attestation_path=Path(handoff["attestationPath"]),
        receipt_path=Path(handoff["verifiedFinishPath"]),
        audit_path=Path(handoff["auditPath"]),
        authority=authority,
    )
    if (
        review.get("state") != "PASS"
        or review.get("auditHead") != bundle["chain"]["auditHead"]
        or file_digest(Path(handoff["verifiedFinishPath"]))
           != bundle["chain"]["verifiedFinishReceiptDigest"]
    ):
        raise FinalizationHold("DONECHECK_FINISH_BINDING_MISMATCH")
    envelope_path = Path(receipt["thresholdEnvelopePath"])
    if file_digest(envelope_path) != receipt.get("thresholdEnvelopeDigest"):
        raise FinalizationHold("THRESHOLD_ENVELOPE_DIGEST_MISMATCH")
    envelope = _load(envelope_path)
    if (envelope.get("payload") or {}).get("decision") != "ACCEPT":
        raise FinalizationHold("SIGNED_ACCEPT_DECISION_REQUIRED")
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
        observed_at=observed_at, production_use=True,
        artifact_path=authority_path,
        replay_backend=PersistentReplayAuthority(replay_path),
    )
    if (
        threshold.get("state") != "PASS"
        or threshold.get("decisionId") != receipt.get("humanDecisionId")
        or threshold.get("terminalCandidateId") != bundle["terminalCandidateId"]
    ):
        raise FinalizationHold("HUMAN_THRESHOLD_BINDING_MISMATCH")

    lock_path = receipt_path.parent / "canonical-lock-evidence.json"
    evidence = {
        "schema": "enguru.mac-engineer.v08-gate12-lock-evidence/v1",
        "state": "LOCK_EVIDENCE_PENDING_CANONICAL_COMMIT",
        "version": "v0.8", "gate": 12, "intendedExit": EXIT,
        "fieldReceipt": str(receipt_path), "fieldReceiptDigest": expected_digest,
        "terminalCandidateId": bundle["terminalCandidateId"],
        "humanDecisionId": threshold["decisionId"],
        "acceptedControlHead": accepted_head,
        "reconciliationControlHead": control["head"],
        "productHead": product["head"],
        "doneCheck": bundle["doneCheck"],
        "externalA09State": "HOLD",
        "productPublicationState": product["publicationState"],
        "canonicalLockCreated": False,
    }
    published = CrashDurablePublisher().publish_json(lock_path, evidence)
    return {
        "state": "HOLD", "reason": "GATE12_LOCK_EVIDENCE_PENDING_CANONICAL_COMMIT",
        "lockEvidence": str(lock_path), "lockEvidenceDigest": published.digest,
        "idempotent": published.idempotent, "canonicalLockCreated": False,
        "nextAction": GATE12,
    }


if __name__ == "__main__":
    try:
        result = finalize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["state"] == "PASS" else 2)
    except (FinalizationHold, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
