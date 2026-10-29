"""Zülfikar V1.4.1 / E00: bounded experience-to-task adapter.

This is a local disposable proof adapter for the EXISTING Döngü Onarım Motoru.
An incident description never becomes evidence, an official PASS, a commit, or
an authorization. Only caller-provided scoped, independently verified tests
may produce a technical candidate for a separate owner review.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

DOM_DIR = Path(__file__).resolve().parents[1] / "zulfikar-v12" / "v141" / "dom"
if str(DOM_DIR) not in sys.path:
    sys.path.insert(0, str(DOM_DIR))

from engine import Contract, LocalJournal, actual_source_digest, execute

SCHEMA = "enguru.zulfikar.v141.e00.experience/v1"
SCOPE = "LOCAL_DISPOSABLE_PROOF"
NEEDS = frozenset({
    "SIMPLICITY", "CAPABILITY", "RELIABILITY", "PERFORMANCE",
    "RECOVERY", "RIGHTS", "SAFETY", "USER_COMFORT"
})
KINDS = frozenset({
    "FAILURE", "INTERRUPTION", "REGRESSION", "SOURCE_DRIFT",
    "WRONG_EVIDENCE", "USER_FEEDBACK", "SUCCESS"
})
SHA = re.compile(r"^[a-f0-9]{64}$")
EXPECTED = frozenset({
    "schema", "eventId", "goalId", "userValue", "sourceSha256",
    "scope", "kind", "need", "criteria", "observedCriteria", "lesson"
})


def _valid_str(value, limit=360):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def experience_plan(event, source_file: Path):
    """Validate a recorded observation; NEVER elevate reported criteria to PASS."""
    issues = []
    if type(event) is not dict or set(event) != EXPECTED:
        return {"state": "HOLD_INVALID_EVENT_SCHEMA", "issues": ["SCHEMA_FIELDS"], "officialPassIssued": False}
    for name in ("eventId", "goalId", "userValue", "lesson"):
        if not _valid_str(event.get(name)):
            issues.append("INVALID_" + name)
    if event.get("schema") != SCHEMA or event.get("scope") != SCOPE:
        issues.append("SCHEMA_OR_SCOPE")
    if event.get("kind") not in KINDS or event.get("need") not in NEEDS:
        issues.append("INVALID_KIND_OR_NEED")
    pin = event.get("sourceSha256")
    if not isinstance(pin, str) or not SHA.fullmatch(pin):
        issues.append("SOURCE_PIN_INVALID")
    criteria = event.get("criteria")
    seen = event.get("observedCriteria")
    if (type(criteria) is not list or not 1 <= len(criteria) <= 20 or
        any(not _valid_str(x, 70) for x in criteria) or
        len(set(criteria)) != len(criteria) or
        type(seen) is not dict or set(seen) != set(criteria) or
        any(type(v) is not bool for v in seen.values())):
        issues.append("OBSERVATION_CRITERIA_INVALID")
    try:
        if not issues and actual_source_digest(Path(source_file)) != pin:
            issues.append("SOURCE_BYTES_DIFFER")
    except (ValueError, OSError, TypeError):
        issues.append("SOURCE_NOT_VERIFIED")
    if issues:
        return {"state": "HOLD_INVALID_EXPERIENCE", "issues": sorted(set(issues)),
                "officialPassIssued": False}
    missing = [key for key in criteria if seen[key] is False]
    return {
        "state": "E00_REPAIR_TASK_CANDIDATE" if missing else "E00_NO_CHANGE_REPORTED",
        "eventId": event["eventId"], "goalId": event["goalId"],
        "kind": event["kind"], "need": event["need"],
        "lesson": event["lesson"], "sourceSha256": pin,
        "reportedMissingCriteria": missing,
        "reportedBeforeDiagnostic": 100 * (len(criteria) - len(missing)) // len(criteria),
        "requiresExistingAuthorizedExecutor": bool(missing),
        "observationIndependentlyVerified": False,
        "officialPassIssued": False, "productVerifiedFinish": "NOT_ISSUED",
    }


def run_isolated_learning(event, source_file: Path, journal_folder: Path, *,
                          start_state, simulator, evaluator, repairer, real_tester,
                          independent_verifier, source_probe, max_rounds=3):
    """Run the existing DÖM only in a bounded disposable scope; return a candidate.

    No GitHub writes, Mac job dispatch, source-code self-modification, automatic
    human approvals, or real product completion claims are performed here.
    """
    plan = experience_plan(event, source_file)
    if plan["state"] != "E00_REPAIR_TASK_CANDIDATE":
        return {"state": plan["state"], "plan": plan,
                "officialPassIssued": False, "productVerifiedFinish": "NOT_ISSUED"}
    if type(max_rounds) is not int or not 1 <= max_rounds <= 3:
        return {"state": "HOLD_UNBOUNDED_REPAIR", "plan": plan,
                "officialPassIssued": False, "productVerifiedFinish": "NOT_ISSUED"}
    try:
        contract = Contract(event["goalId"], event["userValue"], "T01",
                            tuple(event["criteria"]), event["sourceSha256"])
        journal = LocalJournal(journal_folder)
        result = execute(contract=contract, start_state=start_state, journal=journal,
                         simulator=simulator, evaluator=evaluator, repairer=repairer,
                         real_tester=real_tester, independent_verifier=independent_verifier,
                         source_probe=source_probe, max_rounds=max_rounds,
                         source_file=source_file)
    except (ValueError, OSError, TypeError) as exc:
        return {"state": "HOLD_DÖM_INPUT_" + type(exc).__name__, "plan": plan,
                "officialPassIssued": False, "productVerifiedFinish": "NOT_ISSUED"}
    candidate = result.get("state") == "STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED"
    return {
        "state": "E00_ISOLATED_TEST_CANDIDATE" if candidate else "E00_REPAIR_HOLD",
        "plan": plan, "domState": result.get("state"),
        "domReason": result.get("reason"),
        "diagnostic": result.get("diagnostic"),
        "journalHeadSha256": result.get("journalHeadSha256"),
        "rounds": result.get("rounds", []),
        "realTestObserved": bool(candidate and result.get("rounds") and
                                 all(r.get("realTestVerified") for r in result["rounds"])),
        "officialPassIssued": False, "productVerifiedFinish": "NOT_ISSUED",
        "nextAction": "EXISTING_OWNER_DONECHECK_REVIEW" if candidate else "REPAIR_WITHIN_AUTHORIZED_SCOPE",
    }
