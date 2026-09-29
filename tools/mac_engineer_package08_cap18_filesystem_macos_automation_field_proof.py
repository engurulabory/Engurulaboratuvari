#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


TECHNICAL_PATH = Path(
    "/Users/abdal/Enguru/Evidence/MacEngineer/package08-field-campaign/"
    "20260929T200532120453Z/capability-18/technical-candidate.json"
)
TECHNICAL_SHA256 = "ed971c6f56cef4d84e09606e549ac69901b1d9842ddc3ac975e59820246ec80b"
HUMAN_THRESHOLD_PATH = Path(
    "/Users/abdal/Enguru/Evidence/MacEngineer/package08-field-campaign/"
    "20260929T200532120453Z/capability-18/human-threshold-accept.json"
)
HUMAN_THRESHOLD_SHA256 = "7ecc6e8422a4baa051dac0ccacb022fe36050b48f32756521321df7583276265"
SEAL_PATH = TECHNICAL_PATH.parent / "field-verification-seal.json"

CAPABILITY_INDEX = 18
CAPABILITY_ID = "FILESYSTEM_MACOS_AUTOMATION"
ACTION = "PACKAGE08_CAP18_FILESYSTEM_MACOS_AUTOMATION_FIELD_PROOF"
OPERATOR_CALLABLE = "run_package08_cap18_filesystem_macos_automation_field_proof"
AUTHORITY = "AMBER_BOUNDED_FILESYSTEM_AUTOMATION_AUTHORITY"

AUTHORIZED_OPERATIONS = [
    "MKDIR",
    "COPY",
    "RENAME",
    "WRITE",
    "GENERATED_FILE_DELETE",
]
REQUIRED_CONTROLS = [
    "PARENT_ESCAPE_FAIL_CLOSED",
    "SYMLINK_ESCAPE_FAIL_CLOSED",
    "OUTSIDE_DELETE_FAIL_CLOSED",
    "ROLLBACK_REQUIRED",
    "ROLLBACK_BYTE_PARITY_REQUIRED",
    "FINAL_SCOPE_CLEAN_REQUIRED",
    "FRESH_REVERIFY_REQUIRED",
]
PROHIBITED_OPERATIONS = [
    "UNSCOPED_FILESYSTEM_MUTATION",
    "PERSISTENT_EXTERNAL_MUTATION",
    "CANONICAL_SOURCE_MUTATION",
    "PRODUCT_MUTATION",
    "NETWORK_ACCESS",
    "REMOTE_PUSH",
    "FINDER_GUI_AUTOMATION",
    "AUTHORITY_EXPANSION",
]
AUTHORIZED_SCOPE = {
    "mutationScope": "EXPLICIT_PATH_SCOPE",
    "workspaceClass": "DISPOSABLE_TEMPORARY_WORKSPACE_ONLY",
    "networkPolicy": "LOCAL_ONLY",
    "persistentExternalMutation": False,
    "canonicalSourceMutation": False,
    "productMutation": False,
    "remotePush": False,
    "finderGuiAuthority": False,
    "executionAuthorityCreated": False,
}


class VerificationHold(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_exact(path: Path, expected_digest: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise VerificationHold(f"{label}_MISSING")
    if sha256(path) != expected_digest:
        raise VerificationHold(f"{label}_SHA256_MISMATCH")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VerificationHold(f"{label}_OBJECT_REQUIRED")
    return payload


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise VerificationHold(reason)


def validate_technical(payload: dict[str, Any]) -> dict[str, bool]:
    require(payload.get("capabilityIndex") == CAPABILITY_INDEX, "TECHNICAL_CAPABILITY_INDEX_MISMATCH")
    require(payload.get("capabilityId") == CAPABILITY_ID, "TECHNICAL_CAPABILITY_ID_MISMATCH")
    require(payload.get("state") == "TECHNICAL_CANDIDATE_PASS", "TECHNICAL_STATE_MISMATCH")
    require(payload.get("mutationScope") == "EXPLICIT_PATH_SCOPE", "TECHNICAL_SCOPE_MISMATCH")
    require(payload.get("networkPolicy") == "LOCAL_ONLY", "TECHNICAL_NETWORK_POLICY_MISMATCH")

    explicit_scope = payload.get("explicitScope") or {}
    real_task = payload.get("realTask") or {}
    failure = payload.get("failurePath") or {}
    rollback = payload.get("rollback") or {}
    fresh = payload.get("freshReverify") or {}
    boundary = payload.get("authorityBoundary") or {}

    require(bool(explicit_scope.get("root")), "EXPLICIT_SCOPE_ROOT_REQUIRED")
    require(explicit_scope.get("parentEscapeRejected") is True, "PARENT_ESCAPE_REJECTION_REQUIRED")
    require(explicit_scope.get("symlinkEscapeRejected") is True, "SYMLINK_ESCAPE_REJECTION_REQUIRED")
    require(explicit_scope.get("outsideDeleteRejected") is True, "OUTSIDE_DELETE_REJECTION_REQUIRED")
    for operation in ("mkdir", "copy", "rename", "write", "create", "deleteGenerated"):
        require(real_task.get(operation) is True, f"REAL_TASK_{operation.upper()}_REQUIRED")
    require(real_task.get("expectedResultObserved") is True, "EXPECTED_RESULT_REQUIRED")
    require(failure.get("tested") is True, "FAILURE_PATH_REQUIRED")
    require(failure.get("outsideMutationRejected") is True, "OUTSIDE_MUTATION_REJECTION_REQUIRED")
    require(failure.get("outsideDeleteRejected") is True, "OUTSIDE_DELETE_FAILURE_REQUIRED")
    require(failure.get("outsideBaselinePreserved") is True, "OUTSIDE_BASELINE_PRESERVATION_REQUIRED")
    require(rollback.get("required") is True, "ROLLBACK_REQUIRED")
    require(rollback.get("performed") is True, "ROLLBACK_PERFORMED_REQUIRED")
    require(bool(rollback.get("baselineSha256")), "BASELINE_SHA_REQUIRED")
    require(rollback.get("baselineSha256") == rollback.get("rollbackSha256"), "ROLLBACK_SHA_PARITY_REQUIRED")
    require(rollback.get("byteParity") is True, "ROLLBACK_BYTE_PARITY_REQUIRED")
    require(rollback.get("scopeClean") is True, "FINAL_SCOPE_CLEAN_REQUIRED")
    require(fresh.get("performed") is True and fresh.get("state") == "PASS", "FRESH_REVERIFY_REQUIRED")
    for key in (
        "canonicalSourceMutation",
        "productMutation",
        "remotePush",
        "networkAccess",
        "persistentExternalMutation",
        "executionAuthorityCreated",
    ):
        require(boundary.get(key) is False, f"TECHNICAL_{key.upper()}_MUST_BE_FALSE")
    require(payload.get("canonicalTruthPreserved") is True, "TECHNICAL_CANONICAL_TRUTH_REQUIRED")
    require(payload.get("criticalFalsePassCount") == 0, "TECHNICAL_FALSE_PASS_COUNT_REQUIRED")

    return {
        "explicitPathScope": True,
        "realTaskEvidenceAccepted": True,
        "expectedResultObserved": True,
        "failurePathTested": True,
        "rollbackPerformed": True,
        "rollbackShaParity": True,
        "rollbackByteParity": True,
        "scopeClean": True,
        "freshReverify": True,
        "canonicalTruthPreserved": True,
        "criticalFalsePassZero": True,
    }


def validate_human_threshold(payload: dict[str, Any]) -> dict[str, bool]:
    require(payload.get("capabilityIndex") == CAPABILITY_INDEX, "HT_CAPABILITY_INDEX_MISMATCH")
    require(payload.get("capabilityId") == CAPABILITY_ID, "HT_CAPABILITY_ID_MISMATCH")
    require(payload.get("state") == "PASS", "HT_STATE_MISMATCH")
    require(payload.get("decision") == "ACCEPT", "HT_ACCEPT_REQUIRED")
    require(payload.get("decisionSource") == "EXPLICIT_HUMAN_DECISION", "HT_DECISION_SOURCE_MISMATCH")
    require(payload.get("humanThresholdConsumed") is True, "HT_CONSUMED_REQUIRED")
    require(payload.get("authorizedAuthority") == AUTHORITY, "HT_AUTHORITY_MISMATCH")
    require(payload.get("authorizedScope") == AUTHORIZED_SCOPE, "HT_SCOPE_MISMATCH")
    require(payload.get("authorizedOperations") == AUTHORIZED_OPERATIONS, "HT_OPERATIONS_MISMATCH")
    require(payload.get("requiredControls") == REQUIRED_CONTROLS, "HT_CONTROLS_MISMATCH")
    require(payload.get("prohibitedOperations") == PROHIBITED_OPERATIONS, "HT_PROHIBITED_MISMATCH")
    require(payload.get("rollbackRequired") is True, "HT_ROLLBACK_REQUIRED")
    require(payload.get("canonicalTruthPreserved") is True, "HT_CANONICAL_TRUTH_REQUIRED")
    technical = payload.get("technicalCandidate") or {}
    require(technical.get("path") == str(TECHNICAL_PATH), "HT_TECHNICAL_PATH_MISMATCH")
    require(technical.get("sha256") == TECHNICAL_SHA256, "HT_TECHNICAL_SHA_MISMATCH")

    return {
        "humanThresholdPass": True,
        "explicitHumanDecision": True,
        "humanThresholdConsumed": True,
        "authorizedScopeExact": True,
        "requiredControlsExact": True,
        "prohibitedOperationsExact": True,
        "rollbackRequired": True,
    }


def verify_and_seal(
    *,
    technical_path: Path = TECHNICAL_PATH,
    technical_digest: str = TECHNICAL_SHA256,
    human_threshold_path: Path = HUMAN_THRESHOLD_PATH,
    human_threshold_digest: str = HUMAN_THRESHOLD_SHA256,
    seal_path: Path = SEAL_PATH,
) -> dict[str, Any]:
    technical = read_exact(technical_path, technical_digest, "TECHNICAL_CANDIDATE")
    threshold = read_exact(human_threshold_path, human_threshold_digest, "HUMAN_THRESHOLD_RECEIPT")
    technical_controls = validate_technical(technical)
    threshold_controls = validate_human_threshold(threshold)

    payload: dict[str, Any] = {
        "schema": "enguru.mac-engineer.package08-cap18-field-verification-seal/v1",
        "observedAt": now(),
        "state": "PASS",
        "capabilityIndex": CAPABILITY_INDEX,
        "capabilityId": CAPABILITY_ID,
        "canonicalAction": ACTION,
        "operatorCallable": OPERATOR_CALLABLE,
        "authority": AUTHORITY,
        "technicalCandidate": {"path": str(technical_path), "sha256": technical_digest},
        "humanThresholdReceipt": {"path": str(human_threshold_path), "sha256": human_threshold_digest},
        "observedAcceptance": {**technical_controls, **threshold_controls},
        "authorityBoundary": {
            **AUTHORIZED_SCOPE,
            "authorizedOperations": AUTHORIZED_OPERATIONS,
            "requiredControls": REQUIRED_CONTROLS,
            "prohibitedOperations": PROHIBITED_OPERATIONS,
            "authorityExpansionAllowed": False,
        },
        "execution": {
            "technicalFieldTaskReexecuted": False,
            "humanThresholdRegenerated": False,
            "technicalFilesystemMutationPerformed": False,
            "evidenceSealWritten": True,
            "networkAccess": False,
            "remotePush": False,
        },
        "doneCheck": {
            "state": "PASS",
            "basis": "ACCEPTED_EVIDENCE_RECONCILIATION",
        },
        "canonicalTruthPreserved": True,
        "criticalFalsePassCount": 0,
    }

    seal_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = seal_path.with_name(seal_path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(seal_path)
    return payload


def main() -> int:
    seal_override = os.environ.get("ENGURU_CAP18_SEAL_PATH")
    seal_path = Path(seal_override) if seal_override else SEAL_PATH
    payload = verify_and_seal(seal_path=seal_path)

    print("STATE=PASS")
    print("CAP18_FILESYSTEM_MACOS_AUTOMATION=PASS")
    print("TECHNICAL_SHA_EXACT=PASS")
    print("HUMAN_THRESHOLD_SHA_EXACT=PASS")
    print("EXPLICIT_PATH_SCOPE=PASS")
    print("DISPOSABLE_WORKSPACE_ONLY=PASS")
    print("REAL_TASK_EVIDENCE_ACCEPTED=PASS")
    print("EXPECTED_RESULT_OBSERVED=PASS")
    print("FAILURE_PATH_TESTED=PASS")
    print("ROLLBACK=PASS")
    print("ROLLBACK_BYTE_PARITY=PASS")
    print("SCOPE_CLEAN=PASS")
    print("FRESH_REVERIFY=PASS")
    print("HUMAN_THRESHOLD=ACCEPT")
    print("HUMAN_THRESHOLD_CONSUMED=true")
    print("NETWORK_ACCESS=false")
    print("REMOTE_PUSH=false")
    print("FINDER_GUI_AUTHORITY=false")
    print("CANONICAL_SOURCE_MUTATION=false")
    print("PRODUCT_MUTATION=false")
    print("PERSISTENT_EXTERNAL_MUTATION=false")
    print("EXECUTION_AUTHORITY_CREATED=false")
    print("CAPABILITY_REEXECUTED=false")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("EVIDENCE=" + str(seal_path))
    print("EVIDENCE_SHA256=" + sha256(seal_path))
    require(payload["state"] == "PASS", "SEAL_PASS_REQUIRED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("STATE=HOLD")
        print("HOLD=" + type(exc).__name__ + ":" + str(exc))
        raise SystemExit(2)
