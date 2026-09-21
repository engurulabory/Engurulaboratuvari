from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


TARGETS = {
    "operating_character": 98.0,
    "architecture_foundations": 97.0,
    "engineering_foundations": 98.0,
    "intellectual_depth": 97.0,
    "finished_ability": 98.0,
    "human_centered_conversation": 97.0,
    "persistent_working_memory": 97.0,
}

REQUIRED_PACKAGES = (
    "package_1",
    "package_2a",
    "package_2a1",
    "package_2b",
    "package_2c",
    "package_3",
    "package_4",
)

CLOSED_PACKAGE_STATES = {
    "VERIFIED_PASS",
    "VERIFIED_AUDIT_COMPLETE",
    "REAL_GAP_REVIEW_COMPLETE",
    "VERIFIED_FINAL_LOCKED",
    "COMPLETED_USER_LOCKED",
}


@dataclass(frozen=True)
class AggregateCloseoutResult:
    state: str
    reason: str
    issues: tuple[str, ...]
    evidence: tuple[str, ...]


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def assess_v06_aggregate(payload: Mapping[str, Any]) -> AggregateCloseoutResult:
    issues: list[str] = []
    evidence: list[str] = []

    if payload.get("schemaVersion") != "1.0":
        issues.append("UNKNOWN_SCORECARD_SCHEMA")

    score_type = str(payload.get("scoreType", ""))
    if score_type != "V0.6_INTERNAL_FIELD_APPLIED_CLOSURE":
        issues.append("INVALID_SCORE_TYPE")

    packages = payload.get("packages")
    if not isinstance(packages, Mapping):
        issues.append("PACKAGE_EVIDENCE_REQUIRED")
        packages = {}

    for package_id in REQUIRED_PACKAGES:
        item = packages.get(package_id)
        if not isinstance(item, Mapping):
            issues.append(f"PACKAGE_REQUIRED:{package_id}")
            continue
        state = str(item.get("state", ""))
        refs = item.get("evidenceRefs", [])
        if state not in CLOSED_PACKAGE_STATES:
            issues.append(f"PACKAGE_NOT_CLOSED:{package_id}:{state or 'UNKNOWN'}")
        if not isinstance(refs, list) or not refs:
            issues.append(f"PACKAGE_EVIDENCE_MISSING:{package_id}")
        else:
            evidence.extend(f"{package_id}:{ref}" for ref in refs)

    domains = payload.get("domains")
    if not isinstance(domains, Mapping):
        issues.append("DOMAIN_SCORECARD_REQUIRED")
        domains = {}

    for domain, target in TARGETS.items():
        item = domains.get(domain)
        if not isinstance(item, Mapping):
            issues.append(f"DOMAIN_REQUIRED:{domain}")
            continue
        score = _number(item.get("score"))
        declared_target = _number(item.get("target"))
        refs = item.get("evidenceRefs", [])
        basis = str(item.get("basis", "")).strip()
        if declared_target is None or abs(declared_target - target) > 1e-9:
            issues.append(f"TARGET_DRIFT:{domain}")
        if score is None or score < target or score > 100:
            issues.append(f"TARGET_NOT_MET:{domain}")
        if not isinstance(refs, list) or not refs:
            issues.append(f"DOMAIN_EVIDENCE_MISSING:{domain}")
        else:
            evidence.extend(f"{domain}:{ref}" for ref in refs)
        if not basis:
            issues.append(f"DOMAIN_BASIS_MISSING:{domain}")

    critical = payload.get("criticalFailures")
    if not isinstance(critical, Mapping):
        issues.append("CRITICAL_FAILURE_LEDGER_REQUIRED")
    else:
        unresolved = critical.get("unresolved")
        refs = critical.get("evidenceRefs", [])
        if unresolved != 0:
            issues.append("CRITICAL_FAILURES_NONZERO")
        if not isinstance(refs, list) or not refs:
            issues.append("CRITICAL_FAILURE_EVIDENCE_MISSING")
        else:
            evidence.extend(f"critical:{ref}" for ref in refs)

    donecheck = payload.get("mandatoryDoneCheck")
    if not isinstance(donecheck, list) or not donecheck:
        issues.append("MANDATORY_DONECHECK_REQUIRED")
    else:
        for item in donecheck:
            if not isinstance(item, Mapping):
                issues.append("INVALID_DONECHECK_ITEM")
                continue
            name = str(item.get("check", "")).strip()
            state = str(item.get("state", "")).upper()
            refs = item.get("evidenceRefs", [])
            if not name:
                issues.append("DONECHECK_NAME_REQUIRED")
            if state != "PASS":
                issues.append(f"DONECHECK_NOT_PASS:{name or 'UNKNOWN'}")
            if not isinstance(refs, list) or not refs:
                issues.append(f"DONECHECK_EVIDENCE_MISSING:{name or 'UNKNOWN'}")
            else:
                evidence.extend(f"donecheck:{name}:{ref}" for ref in refs)

    unresolved_holds = payload.get("unresolvedHolds")
    if unresolved_holds not in ([], tuple()):
        issues.append("UNRESOLVED_HOLDS_PRESENT")

    return AggregateCloseoutResult(
        state="HOLD" if issues else "PASS",
        reason="aggregate_closeout_hold" if issues else "v06_aggregate_evidence_pass",
        issues=tuple(issues),
        evidence=tuple(dict.fromkeys(evidence)),
    )
