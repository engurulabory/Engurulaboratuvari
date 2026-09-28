#!/usr/bin/env python3
"""Gate 12 Batch 3 final acceptance and canonical lock transition."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from typing import Any

try:
    from mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from mac_engineer_v08_gate12_reviewer_authority import digest  # type: ignore
    from mac_engineer_v08_gate12_pre005_candidate import file_digest
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
    from tools.mac_engineer_v08_gate12_pre005_publisher import CrashDurablePublisher
    from tools.mac_engineer_v08_gate12_reviewer_authority import digest  # type: ignore
    from tools.mac_engineer_v08_gate12_pre005_candidate import file_digest


ROOT = Path(__file__).resolve().parents[1]
SESSION_PATH = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
ROADMAP_PATH = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
REGISTRY_PATH = ROOT / "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json"
HANDOFF_PATH = Path.home() / "Enguru/Runtime/MacEngineer/gate12/pre005/handoff.json"
EVIDENCE_ROOT = Path.home() / "Enguru/Evidence/MacEngineer/v0.8/gate12-final"
EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
NEXT = "V08_VERIFIED_LOCKED_AWAIT_NEXT_OBJECTIVE"


class FinalizationHold(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizationHold(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _append_once(values: list[Any], value: Any) -> list[Any]:
    return values if value in values else values + [value]


def _reconcile(session: dict[str, Any], roadmap: dict[str, Any], registry: dict[str, Any], receipt_path: Path, lock_path: Path, receipt_digest: str, lock_digest: str, bundle: dict[str, Any], observed_at: str) -> None:
    current = session.setdefault("currentV08", {})
    gate12 = current.setdefault("gate12", {})
    current.update({"state": "VERIFIED_LOCKED", "nextAction": NEXT, "localContinuityNextAction": NEXT, "localContinuityState": "VERIFIED_LOCKED"})
    current.setdefault("closureContract", {})["passedGates"] = list(range(1, 13))
    current["closureContract"].update({"activeGate": None, "remainingGates": []})
    current["controlPlaneLocalContinuity"].update({"currentTechnicalTarget": NEXT, "nextAfterPass": NEXT, "state": "VERIFIED_LOCKED"})
    gate12.update({"state": "VERIFIED_LOCKED", "executionStarted": True, "humanDecision": "ACCEPT", "doneCheckV12": "PASS", "finalAcceptanceReceipt": str(receipt_path), "finalAcceptanceReceiptDigest": receipt_digest, "canonicalLock": str(lock_path), "canonicalLockDigest": lock_digest, "verifiedFinish": "PASS", "observedAt": observed_at, "nextAction": NEXT})
    session.update({"currentObjective": NEXT, "nextAction": NEXT})

    roadmap["current"].update({"state": "VERIFIED_LOCKED", "activeObjective": NEXT, "activeGate": None, "remaining": [], "nextAction": NEXT})
    roadmap["current"]["completed"] = _append_once(roadmap["current"].get("completed", []), "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK_PASS")
    version = next(item for item in roadmap["versions"] if item.get("version") == "v0.8")
    version.update({"state": "VERIFIED_LOCKED", "nextAction": NEXT})
    finish = version.setdefault("verifiedFinishContract", {})
    finish.update({"state": "VERIFIED_LOCKED", "passed": list(range(1, 13)), "active": None, "remaining": [], "finalAuthority": "HUMAN_THRESHOLD_ACCEPTED", "finalState": EXIT, "finalAcceptanceReceipt": str(receipt_path), "finalAcceptanceReceiptDigest": receipt_digest, "canonicalLock": str(lock_path), "canonicalLockDigest": lock_digest})
    version["humanThreshold"] = {"state": "ACCEPTED", "decision": "ACCEPT", "evidence": str(receipt_path), "observedAt": observed_at}

    action = (registry.setdefault("actions", {})).setdefault("V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK", {})
    action.update({"finalAcceptanceReceipt": True, "canonicalLock": True, "batch3Boundary": "COMPLETED", "nextAfterPass": NEXT})


def finalize(*, handoff_path: Path = HANDOFF_PATH) -> dict[str, Any]:
    if not handoff_path.is_file():
        raise FinalizationHold("PRE005_HANDOFF_MISSING")
    prelock = execute_from_runtime_handoff(handoff_path)
    if prelock.get("state") != "PASS" or prelock.get("batch2PreLock") != "PASS":
        raise FinalizationHold("PRE005_NOT_PASS")
    handoff = _load(handoff_path)
    bundle_path = Path(handoff["bundlePath"])
    bundle = _load(bundle_path)
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run = EVIDENCE_ROOT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run.mkdir(parents=True, exist_ok=False)
    receipt = {
        "schema": "enguru.mac-engineer.v08-gate12-final-acceptance/v1",
        "state": "PASS", "gate": 12, "exit": EXIT, "observedAt": observed_at,
        "terminalCandidateId": bundle["terminalCandidateId"], "decision": "ACCEPT",
        "doneCheck": bundle["doneCheck"], "control": bundle["control"], "product": bundle["product"],
        "chain": bundle["chain"], "bundlePath": str(bundle_path), "prelock": "PASS",
        "executionStarted": True, "canonicalLockCreated": True,
    }
    publisher = CrashDurablePublisher()
    receipt_path = run / "final-acceptance-receipt.json"
    receipt_result = publisher.publish_json(receipt_path, receipt)
    lock = {
        "schema": "enguru.mac-engineer.v08-gate12-canonical-lock/v1",
        "state": "VERIFIED_LOCKED", "version": "v0.8", "gate": 12, "exit": EXIT,
        "observedAt": observed_at, "terminalCandidateId": bundle["terminalCandidateId"],
        "finalAcceptanceReceipt": str(receipt_path), "finalAcceptanceReceiptDigest": receipt_result.digest,
        "controlHead": bundle["control"]["head"], "productHead": bundle["product"]["head"],
        "doneCheck": bundle["doneCheck"], "humanThreshold": "ACCEPTED",
    }
    lock_path = run / "canonical-lock.json"
    lock_result = publisher.publish_json(lock_path, lock)
    session, roadmap, registry = _load(SESSION_PATH), _load(ROADMAP_PATH), _load(REGISTRY_PATH)
    _reconcile(session, roadmap, registry, receipt_path, lock_path, receipt_result.digest, lock_result.digest, bundle, observed_at)
    _atomic_json(SESSION_PATH, session); _atomic_json(ROADMAP_PATH, roadmap); _atomic_json(REGISTRY_PATH, registry)
    return {"state": "PASS", "finalAcceptanceReceipt": str(receipt_path), "canonicalLock": str(lock_path), "executionStarted": True, "nextAction": NEXT}


if __name__ == "__main__":
    try:
        print(json.dumps(finalize(), ensure_ascii=False, indent=2))
    except (FinalizationHold, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
