#!/usr/bin/env python3
"""Fail-closed authority evaluation for a locally accepted control-plane candidate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_ACCEPTANCE_STATE = (
    Path.home()
    / "Enguru"
    / "Runtime"
    / "MacEngineer"
    / "state"
    / "local-accepted-control-plane-candidate.json"
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _candidate_policy(session: dict[str, Any]) -> dict[str, Any]:
    current = session.get("currentV07") or {}
    policy = current.get("controlPlaneLocalContinuity") or {}
    return policy if isinstance(policy, dict) else {}


def evaluate_local_accepted_candidate(
    control: dict[str, Any],
    session: dict[str, Any],
    *,
    acceptance_path: Path | None = None,
) -> dict[str, Any]:
    """Return whether current control-plane truth is an accepted local candidate.

    Exact-main remains the canonical remote authority. This function only grants
    local engineering continuity when a machine-readable local acceptance state
    and its Evidence exactly match the current branch/HEAD/origin-main truth.
    """

    policy = _candidate_policy(session)
    configured_path = str(policy.get("acceptanceStatePath") or "").strip()
    state_path = (
        Path(configured_path).expanduser()
        if configured_path
        else (acceptance_path or DEFAULT_ACCEPTANCE_STATE)
    )

    reasons: list[str] = []

    expected_branch = str(policy.get("branch") or "")
    expected_external_hold = str(policy.get("externalMergeGate") or "")

    if policy.get("state") != "PENDING_RECONCILIATION":
        reasons.append("POLICY_PENDING_RECONCILIATION_REQUIRED")
    if not expected_branch:
        reasons.append("POLICY_BRANCH_REQUIRED")
    if policy.get("canonicalRemoteAuthority") != "GITHUB_REMOTE_MAIN":
        reasons.append("POLICY_GITHUB_REMOTE_MAIN_AUTHORITY_REQUIRED")
    if policy.get("localAuthority") != "PENDING_RECONCILIATION":
        reasons.append("POLICY_LOCAL_PENDING_RECONCILIATION_REQUIRED")
    if policy.get("secondCanonicalTruth") is not False:
        reasons.append("POLICY_SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")
    if not expected_external_hold.startswith("HOLD_"):
        reasons.append("POLICY_EXTERNAL_MERGE_HOLD_REQUIRED")

    artifact = _load_json(state_path)
    if artifact is None:
        reasons.append("LOCAL_ACCEPTANCE_STATE_REQUIRED")
        return {
            "authorized": False,
            "mode": "LOCAL_ACCEPTED_CANDIDATE",
            "reasons": reasons,
            "policy": policy,
            "acceptance_state_path": str(state_path),
            "acceptance": None,
            "evidence": None,
        }

    if artifact.get("schema") != "enguru.mac-engineer.local-accepted-control-plane-candidate/v1":
        reasons.append("LOCAL_ACCEPTANCE_SCHEMA_MISMATCH")
    if artifact.get("state") != "PASS":
        reasons.append("LOCAL_ACCEPTANCE_PASS_REQUIRED")
    if artifact.get("authority") != "PENDING_RECONCILIATION":
        reasons.append("LOCAL_ACCEPTANCE_AUTHORITY_MISMATCH")
    if artifact.get("canonicalRemoteAuthority") != "GITHUB_REMOTE_MAIN":
        reasons.append("LOCAL_ACCEPTANCE_REMOTE_AUTHORITY_MISMATCH")
    if artifact.get("secondCanonicalTruth") is not False:
        reasons.append("LOCAL_ACCEPTANCE_SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")
    if artifact.get("externalMergeGate") != expected_external_hold:
        reasons.append("LOCAL_ACCEPTANCE_EXTERNAL_HOLD_MISMATCH")

    comparisons = {
        "branch": (control.get("branch"), expected_branch, artifact.get("branch")),
        "head": (control.get("head"), artifact.get("head"), artifact.get("head")),
        "originMain": (
            control.get("origin_main"),
            artifact.get("originMain"),
            artifact.get("originMain"),
        ),
    }
    if control.get("branch") != expected_branch or artifact.get("branch") != expected_branch:
        reasons.append("LOCAL_ACCEPTANCE_BRANCH_MISMATCH")
    if not control.get("head") or control.get("head") != artifact.get("head"):
        reasons.append("LOCAL_ACCEPTANCE_HEAD_MISMATCH")
    if not control.get("origin_main") or control.get("origin_main") != artifact.get("originMain"):
        reasons.append("LOCAL_ACCEPTANCE_ORIGIN_MAIN_MISMATCH")
    if control.get("clean") is not True or artifact.get("clean") is not True:
        reasons.append("LOCAL_ACCEPTANCE_CLEAN_REQUIRED")
    if control.get("branch") == "main":
        reasons.append("LOCAL_ACCEPTANCE_NON_MAIN_BRANCH_REQUIRED")
    if control.get("head") == control.get("origin_main"):
        reasons.append("LOCAL_ACCEPTANCE_DISTINCT_CANDIDATE_REQUIRED")

    acceptance = artifact.get("acceptance") or {}
    required_acceptance = {
        "targetedTests": "PASS",
        "fullRegression": "PASS",
        "diffCheck": "PASS",
        "remoteBranchParity": "PASS",
        "mainAncestor": "PASS",
        "canonicalContext": "PASS",
        "sessionStart": "PASS",
    }
    for key, expected in required_acceptance.items():
        if acceptance.get(key) != expected:
            reasons.append(f"LOCAL_ACCEPTANCE_{key.upper()}_{expected}_REQUIRED")

    evidence_value = str(artifact.get("evidence") or "").strip()
    evidence_path = Path(evidence_value).expanduser() if evidence_value else None
    evidence = _load_json(evidence_path) if evidence_path else None
    if evidence is None:
        reasons.append("LOCAL_ACCEPTANCE_EVIDENCE_REQUIRED")
    else:
        if evidence.get("schema") != "enguru.mac-engineer.local-accepted-control-plane-candidate-evidence/v1":
            reasons.append("LOCAL_ACCEPTANCE_EVIDENCE_SCHEMA_MISMATCH")
        if evidence.get("state") != "PASS":
            reasons.append("LOCAL_ACCEPTANCE_EVIDENCE_PASS_REQUIRED")
        for key, observed in {
            "branch": artifact.get("branch"),
            "head": artifact.get("head"),
            "originMain": artifact.get("originMain"),
            "authority": artifact.get("authority"),
            "canonicalRemoteAuthority": artifact.get("canonicalRemoteAuthority"),
            "externalMergeGate": artifact.get("externalMergeGate"),
        }.items():
            if evidence.get(key) != observed:
                reasons.append(f"LOCAL_ACCEPTANCE_EVIDENCE_{key.upper()}_MISMATCH")
        if evidence.get("secondCanonicalTruth") is not False:
            reasons.append("LOCAL_ACCEPTANCE_EVIDENCE_SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")

    return {
        "authorized": not reasons,
        "mode": "LOCAL_ACCEPTED_CANDIDATE",
        "reasons": reasons,
        "policy": policy,
        "acceptance_state_path": str(state_path),
        "acceptance": artifact,
        "evidence": evidence,
        "comparisons": comparisons,
    }
