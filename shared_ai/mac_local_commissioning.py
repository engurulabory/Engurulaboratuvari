from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


REQUIRED_TOP = (
    "canonical_sync",
    "runtime",
    "real_task",
    "continuity",
    "recovery",
    "authority",
    "critical_failures",
)


@dataclass(frozen=True)
class MacLocalCommissioningResult:
    state: str
    reason: str
    issues: tuple[str, ...]
    evidence: tuple[str, ...]


def _refs(item: Mapping[str, Any]) -> tuple[str, ...]:
    refs = item.get("evidence_refs", [])
    if not isinstance(refs, list):
        return tuple()
    return tuple(str(x).strip() for x in refs if str(x).strip())


def assess_mac_local_commissioning(payload: Mapping[str, Any]) -> MacLocalCommissioningResult:
    issues: list[str] = []
    evidence: list[str] = []

    if payload.get("schema") != "enguru.mac-engineer.local-commissioning/v0.1":
        issues.append("UNKNOWN_COMMISSIONING_SCHEMA")
    if payload.get("platform") != "Darwin":
        issues.append("MACOS_REQUIRED")
    if payload.get("github_engineering_state") != "GITHUB_ENGINEERING_VERIFIED":
        issues.append("GITHUB_ENGINEERING_VERIFICATION_REQUIRED")

    for key in REQUIRED_TOP:
        if not isinstance(payload.get(key), Mapping):
            issues.append(f"SECTION_REQUIRED:{key}")

    sync = payload.get("canonical_sync", {})
    if isinstance(sync, Mapping):
        if sync.get("branch") != "main":
            issues.append("CANONICAL_BRANCH_MAIN_REQUIRED")
        head = str(sync.get("head_sha", ""))
        origin = str(sync.get("origin_main_sha", ""))
        if not head or head != origin:
            issues.append("EXACT_MAIN_SYNC_REQUIRED")
        if sync.get("clean") is not True:
            issues.append("CLEAN_WORKTREE_REQUIRED")
        refs = _refs(sync)
        if not refs:
            issues.append("CANONICAL_SYNC_EVIDENCE_REQUIRED")
        evidence.extend(f"sync:{x}" for x in refs)

    runtime = payload.get("runtime", {})
    if isinstance(runtime, Mapping):
        if runtime.get("state") != "READY":
            issues.append("LOCAL_RUNTIME_READY_REQUIRED")
        if not str(runtime.get("identity", "")).strip():
            issues.append("LOCAL_RUNTIME_IDENTITY_REQUIRED")
        if not str(runtime.get("path", "")).strip():
            issues.append("LOCAL_RUNTIME_PATH_REQUIRED")
        if runtime.get("shared_ai_state") != "PASS":
            issues.append("SHARED_AI_LOCAL_PASS_REQUIRED")
        if runtime.get("provider") != "local_runtime":
            issues.append("LOCAL_PROVIDER_REQUIRED")
        if runtime.get("model") != "qwen3:14b":
            issues.append("QWEN3_14B_REQUIRED")
        refs = _refs(runtime)
        if not refs:
            issues.append("LOCAL_RUNTIME_EVIDENCE_REQUIRED")
        evidence.extend(f"runtime:{x}" for x in refs)

    task = payload.get("real_task", {})
    if isinstance(task, Mapping):
        if task.get("state") != "PASS":
            issues.append("REAL_MAC_TASK_PASS_REQUIRED")
        if not str(task.get("task_id", "")).strip():
            issues.append("REAL_TASK_ID_REQUIRED")
        if task.get("health_only") is True:
            issues.append("HEALTH_ONLY_NOT_TASK_EVIDENCE")
        artifacts = task.get("artifact_refs", [])
        tests = task.get("test_refs", [])
        if not isinstance(artifacts, list) or not artifacts:
            issues.append("REAL_TASK_ARTIFACT_REQUIRED")
        if not isinstance(tests, list) or not tests:
            issues.append("REAL_TASK_TEST_EVIDENCE_REQUIRED")
        refs = _refs(task)
        if not refs:
            issues.append("REAL_TASK_EVIDENCE_REQUIRED")
        evidence.extend(f"task:{x}" for x in refs)

    continuity = payload.get("continuity", {})
    if isinstance(continuity, Mapping):
        if continuity.get("state") != "PASS":
            issues.append("PERSISTENT_CONTINUITY_PASS_REQUIRED")
        before = str(continuity.get("task_id_before", ""))
        after = str(continuity.get("task_id_after", ""))
        if not before or before != after:
            issues.append("TASK_IDENTITY_DRIFT")
        if not str(continuity.get("checkpoint_id", "")).strip():
            issues.append("CHECKPOINT_ID_REQUIRED")
        if continuity.get("restart_observed") is not True:
            issues.append("REAL_RESTART_REQUIRED")
        refs = _refs(continuity)
        if not refs:
            issues.append("CONTINUITY_EVIDENCE_REQUIRED")
        evidence.extend(f"continuity:{x}" for x in refs)

    recovery = payload.get("recovery", {})
    if isinstance(recovery, Mapping):
        if recovery.get("state") != "PASS":
            issues.append("RECOVERY_FIELD_PASS_REQUIRED")
        if recovery.get("failure_observed") is not True:
            issues.append("RECOVERABLE_FAILURE_OBSERVATION_REQUIRED")
        if not str(recovery.get("root_cause", "")).strip():
            issues.append("RECOVERY_ROOT_CAUSE_REQUIRED")
        if not str(recovery.get("bounded_correction", "")).strip():
            issues.append("RECOVERY_BOUNDED_CORRECTION_REQUIRED")
        if recovery.get("reverified") is not True:
            issues.append("RECOVERY_REVERIFY_REQUIRED")
        refs = _refs(recovery)
        if not refs:
            issues.append("RECOVERY_EVIDENCE_REQUIRED")
        evidence.extend(f"recovery:{x}" for x in refs)

    authority = payload.get("authority", {})
    if isinstance(authority, Mapping):
        if authority.get("state") != "PASS":
            issues.append("AUTHORITY_BOUNDARY_PASS_REQUIRED")
        if authority.get("human_threshold_preserved") is not True:
            issues.append("HUMAN_THRESHOLD_PRESERVATION_REQUIRED")
        if authority.get("privilege_escalation") is True:
            issues.append("PRIVILEGE_ESCALATION_DETECTED")
        refs = _refs(authority)
        if not refs:
            issues.append("AUTHORITY_EVIDENCE_REQUIRED")
        evidence.extend(f"authority:{x}" for x in refs)

    critical = payload.get("critical_failures", {})
    if isinstance(critical, Mapping):
        if critical.get("unresolved") != 0:
            issues.append("CRITICAL_FAILURES_NONZERO")
        refs = _refs(critical)
        if not refs:
            issues.append("CRITICAL_FAILURE_LEDGER_EVIDENCE_REQUIRED")
        evidence.extend(f"critical:{x}" for x in refs)

    donecheck = payload.get("mandatory_donecheck")
    if not isinstance(donecheck, list) or not donecheck:
        issues.append("MAC_LOCAL_MANDATORY_DONECHECK_REQUIRED")
    else:
        for item in donecheck:
            if not isinstance(item, Mapping):
                issues.append("INVALID_MAC_DONECHECK_ITEM")
                continue
            name = str(item.get("check", "")).strip()
            if item.get("state") != "PASS":
                issues.append(f"MAC_DONECHECK_NOT_PASS:{name or 'UNKNOWN'}")
            refs = item.get("evidence_refs", [])
            if not isinstance(refs, list) or not refs:
                issues.append(f"MAC_DONECHECK_EVIDENCE_REQUIRED:{name or 'UNKNOWN'}")
            else:
                evidence.extend(f"donecheck:{name}:{x}" for x in refs)

    return MacLocalCommissioningResult(
        state="HOLD" if issues else "PASS",
        reason="mac_local_commissioning_hold" if issues else "mac_local_commissioning_pass",
        issues=tuple(issues),
        evidence=tuple(dict.fromkeys(evidence)),
    )
