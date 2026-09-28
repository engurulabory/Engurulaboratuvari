#!/usr/bin/env python3
"""Strict, deterministic Gate12 PRE-005 candidate bundle validation."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
from typing import Any

try:
    from mac_engineer_v08_gate12_reviewer_authority import (
        TERMINAL_CANDIDATE_ID,
        strict_json_loads,
        terminal_candidate_id,
    )
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_reviewer_authority import (
        TERMINAL_CANDIDATE_ID,
        strict_json_loads,
        terminal_candidate_id,
    )


SCHEMA = "enguru.mac-engineer.v08-gate12-pre005-candidate-bundle/v1"
MACHINE_SCHEMA = "enguru.mac-engineer.v08-gate12-machine-result-binding/v1"
LEDGER_SCHEMA = "enguru.mac-engineer.v08-gate12-unresolved-deferred-ledger/v1"
DONECHECK_VERSION = "1.2.0"
DONECHECK_SHA = "8b90a8fc93453dd8a84994195d28d14b15e261cb"
TARGET = "v0.8"
EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
CONTROL_REPOSITORY = "engurulabory/Engurulaboratuvari"
CONTROL_BRANCH = "feat/mac-engineer-v08-product-engineering-operator"
PRODUCT_REPOSITORY = "engurulabory/enguru-mac-engineer"
PRODUCT_BRANCH = "feat/v08-native-productization-provenance"
PRODUCT_PUBLICATION = "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY"
SECURITY_CUSTODY = (
    Path.home() / "Library" / "Application Support" / "Enguru" / "Security"
).resolve()
SHA = re.compile(r"^sha256:[a-f0-9]{64}$")
GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
ARTIFACT_KEYS = (
    "machineResult",
    "evidenceManifest",
    "unresolvedDeferredLedger",
    "canonicalSnapshot",
    "acceptanceContract",
    "verifiedFinishReceipt",
    "auditLedger",
)
TOP_KEYS = {
    "schema", "bundleVersion", "control", "product", "doneCheck",
    "authority", "chain", "target", "artifacts", "terminalCandidateId",
}
CONTROL_KEYS = {
    "repository", "branch", "head", "base", "remoteFeatureHead",
    "remoteFeatureParity", "worktreeClean",
}
PRODUCT_KEYS = {
    "repository", "branch", "head", "base", "worktreeClean",
    "publicationState",
}
CHAIN_KEYS = {
    "machineResultDigest", "evidenceManifestDigest",
    "unresolvedDeferredLedgerDigest", "canonicalSnapshotDigest",
    "acceptanceContractDigest", "verifiedFinishReceiptDigest", "auditHead",
}


class CandidateHold(RuntimeError):
    """Candidate input is incomplete, stale, ambiguous, or unsafe."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CandidateHold(reason)


def assert_safe_artifact_path(path: Path) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    try:
        resolved.relative_to(SECURITY_CUSTODY)
    except ValueError:
        return resolved
    raise CandidateHold("PRIVATE_KEY_CUSTODY_PATH_FORBIDDEN")


def file_digest(path: Path) -> str:
    safe = assert_safe_artifact_path(path)
    h = hashlib.sha256()
    with safe.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _strict_object(path: Path, label: str) -> dict[str, Any]:
    safe = assert_safe_artifact_path(path)
    value, errors = strict_json_loads(safe.read_text(encoding="utf-8"))
    if errors or not isinstance(value, dict):
        raise CandidateHold(f"{label}_STRICT_JSON_OBJECT_REQUIRED")
    return value


def _validate_unresolved_ledger(path: Path) -> None:
    ledger = _strict_object(path, "UNRESOLVED_LEDGER")
    _require(set(ledger) == {"schema", "items"}, "UNRESOLVED_LEDGER_CLOSED_FIELDS_REQUIRED")
    _require(ledger["schema"] == LEDGER_SCHEMA, "UNRESOLVED_LEDGER_SCHEMA_MISMATCH")
    _require(isinstance(ledger["items"], list), "UNRESOLVED_LEDGER_ITEMS_REQUIRED")
    for item in ledger["items"]:
        _require(
            isinstance(item, dict)
            and set(item) == {"id", "classification", "severity", "state"},
            "UNRESOLVED_LEDGER_ITEM_INVALID",
        )
        _require(
            item["classification"] in {"EXTERNAL", "DEFERRED", "RESOLVED"},
            "UNRESOLVED_LEDGER_UNCLASSIFIED_ITEM",
        )
        _require(item["severity"] in {"NON_CRITICAL", "CRITICAL"}, "UNRESOLVED_LEDGER_SEVERITY_INVALID")
        _require(item["state"] in {"OPEN", "RESOLVED"}, "UNRESOLVED_LEDGER_STATE_INVALID")
        if item["severity"] == "CRITICAL" and item["state"] != "RESOLVED":
            raise CandidateHold("UNRESOLVED_CRITICAL_ITEM")


def _machine_bindings(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "controlHead": bundle["control"]["head"],
        "productHead": bundle["product"]["head"],
        "doneCheckVersion": bundle["doneCheck"]["version"],
        "doneCheckSha": bundle["doneCheck"]["exactSha"],
        "evidenceManifestDigest": bundle["chain"]["evidenceManifestDigest"],
        "unresolvedDeferredLedgerDigest": bundle["chain"]["unresolvedDeferredLedgerDigest"],
        "canonicalSnapshotDigest": bundle["chain"]["canonicalSnapshotDigest"],
        "acceptanceContractDigest": bundle["chain"]["acceptanceContractDigest"],
    }


def validate_machine_result(machine: dict[str, Any], bundle: dict[str, Any]) -> None:
    if set(machine) != {"schema", "bindings", "verificationResult"}:
        raise CandidateHold("MACHINE_RESULT_BINDING_CONTRACT_INSUFFICIENT")
    if machine.get("schema") != MACHINE_SCHEMA or machine.get("bindings") != _machine_bindings(bundle):
        raise CandidateHold("MACHINE_RESULT_BINDING_CONTRACT_INSUFFICIENT")
    result = machine.get("verificationResult")
    required = {"id", "taskId", "outcome", "reason", "criteria", "verifiedAt"}
    if not isinstance(result, dict) or set(result) != required:
        raise CandidateHold("MACHINE_RESULT_BINDING_CONTRACT_INSUFFICIENT")
    if result.get("outcome") != "pass" or not isinstance(result.get("criteria"), list) or not result["criteria"]:
        raise CandidateHold("MACHINE_RESULT_NOT_PASS")
    for criterion in result["criteria"]:
        if not isinstance(criterion, dict) or criterion.get("outcome") != "pass":
            raise CandidateHold("MACHINE_RESULT_NOT_PASS")

    manifest = _strict_object(Path(bundle["artifacts"]["evidenceManifest"]["path"]), "EVIDENCE_MANIFEST")
    _require(set(manifest) == {"verificationInput", "evidenceFiles"}, "DONECHECK_INPUT_MANIFEST_INVALID")
    inputs = manifest["verificationInput"]
    _require(isinstance(inputs, dict) and set(inputs) == {"task", "criteria", "aiOutput", "evidence", "resultId", "verifiedAt", "policy"}, "DONECHECK_INPUT_MANIFEST_INVALID")
    criteria, evidence, files = inputs["criteria"], inputs["evidence"], manifest["evidenceFiles"]
    _require(isinstance(criteria, list) and isinstance(evidence, list) and isinstance(files, list), "DONECHECK_INPUT_MANIFEST_INVALID")
    required_gates = {f"gate{i}" for i in range(1, 12)}
    _require(all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in criteria), "DONECHECK_GATE_CRITERIA_INCOMPLETE")
    _require({item.get("id") for item in criteria if isinstance(item, dict)} == required_gates and len(criteria) == 11 and all(item.get("required") is True and item.get("kind") == "objective" for item in criteria), "DONECHECK_GATE_CRITERIA_INCOMPLETE")
    _require(isinstance(inputs["policy"], dict) and inputs["policy"].get("requireEvidenceProvenance") is True and inputs["policy"].get("trustedProducerIds") == ["enguru.mac-engineer"], "DONECHECK_PROVENANCE_POLICY_REQUIRED")
    _require(len(evidence) == len(files) == 11, "DONECHECK_EVIDENCE_FILES_INCOMPLETE")
    _require(all(isinstance(item, dict) and isinstance(item.get("evidenceId"), str) for item in files), "DONECHECK_EVIDENCE_FILE_INVALID")
    file_by_id = {item.get("evidenceId"): item for item in files if isinstance(item, dict)}
    _require(len(file_by_id) == 11, "DONECHECK_EVIDENCE_FILES_INCOMPLETE")
    for item in evidence:
        _require(isinstance(item, dict) and isinstance(item.get("id"), str) and isinstance(item.get("criterionId"), str) and item.get("criterionId") in required_gates and item.get("source") == "system" and item.get("kind") in {"log", "test_report"}, "DONECHECK_EVIDENCE_SCOPE_INVALID")
        record = file_by_id.get(item.get("id"))
        basic = {"evidenceId", "path", "digest"}
        sourced = basic | {"sourceGate", "sourceStateKey", "sourcePath", "sourceDigest"}
        _require(isinstance(record, dict) and set(record) in (basic, sourced) and isinstance(record["path"], str) and bool(SHA.fullmatch(str(record["digest"]))), "DONECHECK_EVIDENCE_FILE_INVALID")
        path = assert_safe_artifact_path(Path(record["path"]))
        _require(path.is_file() and file_digest(path) == record["digest"], "DONECHECK_EVIDENCE_FILE_DIGEST_MISMATCH")
        _require(path.read_text(encoding="utf-8") == item.get("content"), "DONECHECK_EVIDENCE_CONTENT_MISMATCH")
        provenance = item.get("provenance")
        _require(isinstance(provenance, dict) and provenance.get("artifactDigest") == record["digest"] and provenance.get("producerKind") == "mac_engineer" and provenance.get("producerId") == "enguru.mac-engineer", "DONECHECK_EVIDENCE_PROVENANCE_MISMATCH")
    _require({item["criterionId"] for item in evidence} == required_gates, "DONECHECK_EVIDENCE_SCOPE_INVALID")
    try:
        try:
            from mac_engineer_donecheck_v12_bridge import reproduce_verification_result
        except ModuleNotFoundError:
            from tools.mac_engineer_donecheck_v12_bridge import reproduce_verification_result
        reproduced = reproduce_verification_result(inputs)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise CandidateHold(f"DONECHECK_VERIFY_TASK_UNAVAILABLE:{type(exc).__name__}") from exc
    _require(reproduced == result, "MACHINE_RESULT_NOT_REPRODUCED_BY_DONECHECK")


def _projection(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "controlHead": bundle["control"]["head"],
        "productHead": bundle["product"]["head"],
        "doneCheckVersion": bundle["doneCheck"]["version"],
        "doneCheckSha": bundle["doneCheck"]["exactSha"],
        **bundle["chain"],
        "targetVersion": TARGET,
        "intendedExit": EXIT,
    }


def validate_candidate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    _require(set(bundle) == TOP_KEYS, "BUNDLE_CLOSED_FIELDS_REQUIRED")
    _require(bundle["schema"] == SCHEMA and bundle["bundleVersion"] == 1, "BUNDLE_SCHEMA_MISMATCH")
    control = bundle.get("control")
    _require(isinstance(control, dict) and set(control) == CONTROL_KEYS, "CONTROL_CLOSED_FIELDS_REQUIRED")
    _require(control["repository"] == CONTROL_REPOSITORY, "CONTROL_REPOSITORY_MISMATCH")
    _require(control["branch"] == CONTROL_BRANCH, "CONTROL_BRANCH_MISMATCH")
    _require(all(GIT_SHA.fullmatch(str(control[k]) or "") for k in ("head", "base", "remoteFeatureHead")), "CONTROL_SHA_INVALID")
    _require(control["remoteFeatureParity"] is True and control["remoteFeatureHead"] == control["head"], "CONTROL_REMOTE_PARITY_MISMATCH")
    _require(control["worktreeClean"] is True, "CONTROL_NOT_CLEAN")
    product = bundle.get("product")
    _require(isinstance(product, dict) and set(product) == PRODUCT_KEYS, "PRODUCT_CLOSED_FIELDS_REQUIRED")
    _require(product["repository"] == PRODUCT_REPOSITORY, "PRODUCT_REPOSITORY_MISMATCH")
    _require(product["branch"] == PRODUCT_BRANCH, "PRODUCT_BRANCH_MISMATCH")
    _require(all(GIT_SHA.fullmatch(str(product[k]) or "") for k in ("head", "base")), "PRODUCT_SHA_INVALID")
    _require(product["worktreeClean"] is True, "PRODUCT_NOT_CLEAN")
    _require(product["publicationState"] == PRODUCT_PUBLICATION, "PRODUCT_PUBLICATION_STATE_MISMATCH")
    _require(bundle.get("doneCheck") == {"version": DONECHECK_VERSION, "exactSha": DONECHECK_SHA}, "DONECHECK_EXACT_REQUIRED")
    authority = bundle.get("authority")
    _require(isinstance(authority, dict) and set(authority) == {"reviewerId", "keyId", "authorityDigest"}, "AUTHORITY_CLOSED_FIELDS_REQUIRED")
    _require(all(isinstance(authority[k], str) and authority[k] for k in ("reviewerId", "keyId")), "AUTHORITY_IDENTITY_REQUIRED")
    _require(bool(SHA.fullmatch(str(authority["authorityDigest"]))), "AUTHORITY_DIGEST_INVALID")
    chain = bundle.get("chain")
    _require(isinstance(chain, dict) and set(chain) == CHAIN_KEYS, "CHAIN_CLOSED_FIELDS_REQUIRED")
    _require(all(SHA.fullmatch(str(chain[k]) or "") for k in CHAIN_KEYS), "CHAIN_DIGEST_INVALID")
    _require(bundle.get("target") == {"targetVersion": TARGET, "intendedExit": EXIT}, "TARGET_EXIT_MISMATCH")
    artifacts = bundle.get("artifacts")
    _require(isinstance(artifacts, dict) and set(artifacts) == set(ARTIFACT_KEYS), "ARTIFACT_SET_MISMATCH")
    for name, item in artifacts.items():
        _require(isinstance(item, dict) and set(item) == {"path", "digest"}, f"ARTIFACT_DESCRIPTOR_INVALID:{name}")
        _require(bool(SHA.fullmatch(str(item["digest"]))), f"ARTIFACT_DIGEST_FORMAT_INVALID:{name}")
        path = assert_safe_artifact_path(Path(item["path"]))
        _require(path.is_file(), f"ARTIFACT_MISSING:{name}")
        _require(file_digest(path) == item["digest"], f"ARTIFACT_DIGEST_MISMATCH:{name}")
    digest_bindings = {
        "machineResult": "machineResultDigest",
        "evidenceManifest": "evidenceManifestDigest",
        "unresolvedDeferredLedger": "unresolvedDeferredLedgerDigest",
        "canonicalSnapshot": "canonicalSnapshotDigest",
        "acceptanceContract": "acceptanceContractDigest",
        "verifiedFinishReceipt": "verifiedFinishReceiptDigest",
    }
    for artifact_name, chain_name in digest_bindings.items():
        _require(artifacts[artifact_name]["digest"] == chain[chain_name], f"CHAIN_ARTIFACT_DIGEST_MISMATCH:{artifact_name}")
    # auditHead is the verified DoneCheck record hash; auditLedger.digest is file bytes.
    _validate_unresolved_ledger(Path(artifacts["unresolvedDeferredLedger"]["path"]))
    machine = _strict_object(Path(artifacts["machineResult"]["path"]), "MACHINE_RESULT")
    validate_machine_result(machine, bundle)
    computed = terminal_candidate_id(_projection(bundle))
    _require(bool(TERMINAL_CANDIDATE_ID.fullmatch(str(bundle["terminalCandidateId"]))), "TERMINAL_CANDIDATE_ID_INVALID")
    _require(bundle["terminalCandidateId"] == computed, "TERMINAL_CANDIDATE_ID_MISMATCH")
    return bundle


def build_candidate_bundle(*, control: dict[str, Any], product: dict[str, Any], done_check: dict[str, Any], authority: dict[str, Any], chain: dict[str, Any], target: dict[str, Any], artifacts: dict[str, dict[str, str]]) -> dict[str, Any]:
    bundle = {
        "schema": SCHEMA,
        "bundleVersion": 1,
        "control": control,
        "product": product,
        "doneCheck": done_check,
        "authority": authority,
        "chain": chain,
        "target": target,
        "artifacts": artifacts,
        "terminalCandidateId": "",
    }
    bundle["terminalCandidateId"] = terminal_candidate_id(_projection(bundle))
    return validate_candidate_bundle(bundle)


def load_candidate_bundle(path: Path) -> dict[str, Any]:
    value = _strict_object(path, "BUNDLE")
    return validate_candidate_bundle(value)


__all__ = [
    "CandidateHold", "MACHINE_SCHEMA", "LEDGER_SCHEMA", "build_candidate_bundle",
    "load_candidate_bundle", "validate_candidate_bundle", "validate_machine_result",
    "assert_safe_artifact_path", "file_digest",
]
