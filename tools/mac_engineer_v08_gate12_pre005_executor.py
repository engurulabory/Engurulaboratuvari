#!/usr/bin/env python3
"""Fail-closed, single-writer Gate12 PRE-005 Batch-2 coordinator."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from mac_engineer_v08_gate12_pre005_candidate import (
        CandidateHold, assert_safe_artifact_path, file_digest,
        load_candidate_bundle, validate_machine_result,
    )
    from mac_engineer_v08_gate12_reviewer_authority import (
        EXPECTED_AUTHORITY_ARTIFACT, load_authority, strict_json_loads,
        verify_authority, verify_threshold_envelope_json,
    )
    from mac_engineer_v08_gate12_pre005_replay import (
        PersistentReplayAuthority, ReplayStoreHold,
    )
    from mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish
except ModuleNotFoundError:
    from tools.mac_engineer_v08_gate12_pre005_candidate import (
        CandidateHold, assert_safe_artifact_path, file_digest,
        load_candidate_bundle, validate_machine_result,
    )
    from tools.mac_engineer_v08_gate12_reviewer_authority import (
        EXPECTED_AUTHORITY_ARTIFACT, load_authority, strict_json_loads,
        verify_authority, verify_threshold_envelope_json,
    )
    from tools.mac_engineer_v08_gate12_pre005_replay import (
        PersistentReplayAuthority, ReplayStoreHold,
    )
    from tools.mac_engineer_donecheck_v12_bridge import verify_human_review_and_verified_finish


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME_ROOT = Path.home() / "Enguru" / "Runtime" / "MacEngineer" / "gate12" / "pre005"
LOCK_PATH = RUNTIME_ROOT / "execution.lock"
HANDOFF_PATH = RUNTIME_ROOT / "handoff.json"
REPLAY_PATH = RUNTIME_ROOT / "replay.json"
ACCEPTANCE_STATE = Path.home() / "Enguru" / "Runtime" / "MacEngineer" / "state" / "local-accepted-control-plane-candidate.json"
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
AUTHORITY_PATH = EXPECTED_AUTHORITY_ARTIFACT
HANDOFF_KEYS = {
    "schema", "bundlePath", "thresholdEnvelopePath", "humanReviewPath",
    "attestationPath", "verifiedFinishPath", "auditPath", "observedAt",
}


class ExecutionHold(RuntimeError):
    pass


@contextmanager
def exclusive_execution_lock(path: Path = LOCK_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ExecutionHold("PRE005_EXECUTION_LOCK_HELD") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _hold(reason: str) -> dict[str, Any]:
    return {
        "state": "HOLD",
        "batch2PreLock": "HOLD",
        "reason": reason,
        "executionStarted": False,
        "createsFinalReceipt": False,
        "createsCanonicalLock": False,
    }


def _strict_object(path: Path, label: str) -> dict[str, Any]:
    safe = assert_safe_artifact_path(path)
    value, errors = strict_json_loads(safe.read_text(encoding="utf-8"))
    if errors or not isinstance(value, dict):
        raise ExecutionHold(f"{label}_STRICT_JSON_REQUIRED")
    return value


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True,
        check=False, timeout=30,
    )
    if result.returncode != 0:
        raise ExecutionHold("LIVE_GIT_TRUTH_UNAVAILABLE")
    return result.stdout.strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fresh_control_remote(branch: str) -> tuple[str, str]:
    refs = ("refs/heads/main", f"refs/heads/{branch}")
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-remote", "--heads", "origin", *refs],
        text=True, capture_output=True, check=False, timeout=60,
    )
    if result.returncode != 0:
        raise ExecutionHold("FRESH_REMOTE_TRUTH_UNAVAILABLE")
    observed: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2 or parts[1] not in refs or parts[1] in observed:
            raise ExecutionHold("FRESH_REMOTE_TRUTH_AMBIGUOUS")
        observed[parts[1]] = parts[0]
    if set(observed) != set(refs):
        raise ExecutionHold("FRESH_REMOTE_TRUTH_UNAVAILABLE")
    return observed[refs[0]], observed[refs[1]]


def derive_live_truth() -> tuple[dict[str, Any], dict[str, Any]]:
    acceptance = _strict_object(ACCEPTANCE_STATE, "LOCAL_CANDIDATE_ACCEPTANCE")
    branch = _git(ROOT, "branch", "--show-current")
    head = _git(ROOT, "rev-parse", "HEAD")
    base, remote = _fresh_control_remote(branch)
    clean = _git(ROOT, "status", "--porcelain") == ""
    required_acceptance = (
        acceptance.get("state") == "PASS"
        and acceptance.get("branch") == branch
        and acceptance.get("head") == head
        and acceptance.get("originMain") == base
        and acceptance.get("originBranch") == remote
        and acceptance.get("clean") is True
        and all(
            (acceptance.get("acceptance") or {}).get(key) == "PASS"
            for key in (
                "targetedTests", "fullRegression", "diffCheck",
                "remoteBranchParity", "mainAncestor", "canonicalContext",
                "sessionStart",
            )
        )
    )
    if not required_acceptance:
        raise ExecutionHold("LOCAL_CANDIDATE_ACCEPTANCE_STALE")
    merge_base = _git(ROOT, "merge-base", "HEAD", base)
    if not clean or remote != head or merge_base != base:
        raise ExecutionHold("CONTROL_LIVE_TRUTH_MISMATCH")
    control = {
        "repository": "engurulabory/Engurulaboratuvari",
        "branch": branch,
        "head": head,
        "base": base,
        "remoteFeatureHead": remote,
        "remoteFeatureParity": True,
        "worktreeClean": True,
    }
    session = _strict_object(SESSION_STATE, "SESSION_STATE")
    current = (session.get("currentV08") or {}).get("currentProductSource") or {}
    product_branch = _git(PRODUCT_ROOT, "branch", "--show-current")
    product_head = _git(PRODUCT_ROOT, "rev-parse", "HEAD")
    product_base = _git(PRODUCT_ROOT, "rev-parse", "origin/main")
    product_clean = _git(PRODUCT_ROOT, "status", "--porcelain") == ""
    if (
        product_branch != current.get("branch")
        or product_head != current.get("localVerifiedHead")
        or product_base != current.get("baseOriginMain")
        or not product_clean
        or current.get("worktree") != "CLEAN"
    ):
        raise ExecutionHold("PRODUCT_LIVE_TRUTH_MISMATCH")
    product = {
        "repository": current.get("repository"),
        "branch": product_branch,
        "head": product_head,
        "base": product_base,
        "worktreeClean": True,
        "publicationState": current.get("publicationState"),
    }
    return control, product


def execute_prelock(
    *, bundle_path: Path, threshold_envelope_path: Path,
    human_review_path: Path, attestation_path: Path,
    verified_finish_path: Path, audit_path: Path,
    expected_control: dict[str, Any], expected_product: dict[str, Any],
    authority_path: Path = AUTHORITY_PATH, replay_path: Path = REPLAY_PATH,
    lock_path: Path = LOCK_PATH, observed_at: str,
    production_use: bool = True,
) -> dict[str, Any]:
    try:
        all_paths = (
            bundle_path, threshold_envelope_path, human_review_path,
            attestation_path, verified_finish_path, audit_path,
            authority_path, replay_path, lock_path,
        )
        for path in all_paths:
            assert_safe_artifact_path(path)
        with exclusive_execution_lock(lock_path):
            bundle = load_candidate_bundle(bundle_path)
            if bundle["control"] != expected_control:
                return _hold("CONTROL_TRUTH_MISMATCH")
            if bundle["product"] != expected_product:
                return _hold("PRODUCT_TRUTH_MISMATCH")
            receipt_artifact = Path(bundle["artifacts"]["verifiedFinishReceipt"]["path"]).resolve()
            audit_artifact = Path(bundle["artifacts"]["auditLedger"]["path"]).resolve()
            if receipt_artifact != verified_finish_path.resolve() or audit_artifact != audit_path.resolve():
                return _hold("HANDOFF_ARTIFACT_PATH_MISMATCH")
            authority_text = authority_path.read_text(encoding="utf-8")
            authority = load_authority(authority_path)
            authority_observed_at = _utc_now() if production_use else observed_at
            authority_result = verify_authority(
                authority, observed_at=authority_observed_at,
                production_use=production_use,
                artifact_path=authority_path if production_use else None,
            )
            if authority_result.get("state") != "PASS":
                return _hold("REVIEWER_AUTHORITY:" + ",".join(authority_result.get("errors", [])))
            if (
                bundle["authority"]
                != {
                    "reviewerId": authority["reviewer"]["reviewerId"],
                    "keyId": authority["reviewer"]["keyId"],
                    "authorityDigest": authority_result["authorityDigest"],
                }
            ):
                return _hold("CANDIDATE_AUTHORITY_MISMATCH")
            if production_use:
                try:
                    from mac_engineer_v08_gate12_pre005_evidence import verify_source_lineage, EvidenceHold
                except ModuleNotFoundError:
                    from tools.mac_engineer_v08_gate12_pre005_evidence import verify_source_lineage, EvidenceHold
                try:
                    manifest = _strict_object(Path(bundle["artifacts"]["evidenceManifest"]["path"]), "EVIDENCE_MANIFEST")
                    verify_source_lineage(manifest, _strict_object(SESSION_STATE, "SESSION_STATE"))
                except EvidenceHold as exc:
                    return _hold(str(exc))
            machine = _strict_object(Path(bundle["artifacts"]["machineResult"]["path"]), "MACHINE_RESULT")
            validate_machine_result(machine, bundle)
            review_value = _strict_object(human_review_path, "HUMAN_REVIEW")
            result_id = machine["verificationResult"]["id"]
            if review_value.get("verificationResultId") != result_id:
                return _hold("MACHINE_HUMAN_REVIEW_RESULT_MISMATCH")
            review = verify_human_review_and_verified_finish(
                review_path=human_review_path,
                attestation_path=attestation_path,
                receipt_path=verified_finish_path,
                audit_path=audit_path,
                authority=authority,
            )
            if review.get("state") != "PASS":
                return _hold("DONECHECK_HUMAN_REVIEW_OR_FINISH:" + ",".join(review.get("errors", [])))
            if (
                file_digest(verified_finish_path) != bundle["chain"]["verifiedFinishReceiptDigest"]
                or review.get("auditHead") != bundle["chain"]["auditHead"]
            ):
                return _hold("VERIFIED_FINISH_BINDING_MISMATCH")
            envelope = _strict_object(threshold_envelope_path, "HUMAN_THRESHOLD_ENVELOPE")
            payload = envelope.get("payload")
            if not isinstance(payload, dict) or payload.get("decision") not in {"ACCEPT", "HOLD"}:
                return _hold("HUMAN_THRESHOLD_DECISION_INVALID")
            decision = payload["decision"]
            replay = PersistentReplayAuthority(replay_path)
            expected = {
                "controlHead": bundle["control"]["head"],
                "productHead": bundle["product"]["head"],
                "doneCheckVersion": bundle["doneCheck"]["version"],
                "doneCheckSha": bundle["doneCheck"]["exactSha"],
                **bundle["chain"],
                "targetVersion": bundle["target"]["targetVersion"],
                "intendedExit": bundle["target"]["intendedExit"],
            }
            threshold = verify_threshold_envelope_json(
                authority_text,
                threshold_envelope_path.read_text(encoding="utf-8"),
                expected=expected,
                observed_at=authority_observed_at,
                production_use=production_use,
                artifact_path=authority_path if production_use else None,
                replay_backend=replay,
            )
            if threshold.get("state") != "PASS":
                return _hold("HUMAN_THRESHOLD:" + ",".join(threshold.get("errors", [])))
            if threshold.get("terminalCandidateId") != bundle["terminalCandidateId"]:
                return _hold("THRESHOLD_TERMINAL_CANDIDATE_MISMATCH")
            record = {
                "decisionId": threshold["decisionId"],
                "terminalCandidateId": threshold["terminalCandidateId"],
                "payloadDigest": threshold["payloadDigest"],
                "envelopeDigest": threshold["envelopeDigest"],
                "decision": decision,
            }
            replay_disposition = replay.remember(record)
            if decision == "HOLD":
                result = _hold("HUMAN_THRESHOLD_HOLD")
                result["replayDisposition"] = replay_disposition
                return result
            return {
                "state": "PASS",
                "batch2PreLock": "PASS",
                "replayDisposition": replay_disposition,
                "executionStarted": False,
                "createsFinalReceipt": False,
                "createsCanonicalLock": False,
            }
    except (CandidateHold, ExecutionHold, ReplayStoreHold, OSError, ValueError, KeyError) as exc:
        return _hold(str(exc))


def execute_from_runtime_handoff(
    manifest_path: Path = HANDOFF_PATH,
) -> dict[str, Any]:
    try:
        manifest = _strict_object(manifest_path, "PRE005_HANDOFF")
        if set(manifest) != HANDOFF_KEYS or manifest.get("schema") != "enguru.mac-engineer.v08-gate12-pre005-handoff/v1":
            raise ExecutionHold("PRE005_HANDOFF_INVALID")
        control, product = derive_live_truth()
        return execute_prelock(
            bundle_path=Path(manifest["bundlePath"]),
            threshold_envelope_path=Path(manifest["thresholdEnvelopePath"]),
            human_review_path=Path(manifest["humanReviewPath"]),
            attestation_path=Path(manifest["attestationPath"]),
            verified_finish_path=Path(manifest["verifiedFinishPath"]),
            audit_path=Path(manifest["auditPath"]),
            expected_control=control,
            expected_product=product,
            observed_at=manifest["observedAt"],
        )
    except (CandidateHold, ExecutionHold, OSError, ValueError, KeyError) as exc:
        return _hold(str(exc))


__all__ = [
    "ExecutionHold", "exclusive_execution_lock", "execute_prelock",
    "execute_from_runtime_handoff", "derive_live_truth", "HANDOFF_PATH",
]
