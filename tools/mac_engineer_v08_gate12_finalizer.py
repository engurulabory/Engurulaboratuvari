#!/usr/bin/env python3
"""Gate 12 field receipt; canonical reconciliation and lock are separate gates."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from tools.mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from tools.mac_engineer_v08_gate12_pre005_candidate import file_digest, load_candidate_bundle

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


if __name__ == "__main__":
    try:
        result = finalize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["state"] == "PASS" else 2)
    except (FinalizationHold, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
