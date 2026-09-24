#!/usr/bin/env python3
"""Gate 13 — Human Threshold™ review and explicit authority transition receipt.

REVIEW is read-only and fail-closed. It validates Gates 1-12, the final campaign
Evidence, fresh local candidate acceptance, DoneCheck™ v1.2 and the deferred
external GitHub A09 boundary.

ACCEPT requires an explicit human decision token. It writes a local Human
Threshold receipt only. Canonical source/version lock remains a separate
reconciliation step after that receipt is observed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance" / "mac-engineer" / "PRODUCT_ROADMAP_V1.json"
WORKLIST = ROOT / "WORKLIST.md"
ACCEPTED_STATE = (
    HOME
    / "Enguru"
    / "Runtime"
    / "MacEngineer"
    / "state"
    / "local-accepted-control-plane-candidate.json"
)
EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.7"
    / "human-threshold"
)
ACCEPT_TOKEN = "I_ACCEPT_V07_MAC_NATIVE_AUTHORITY"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label}_INVALID:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "code": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"code": 124, "stdout": "", "stderr": "TIMEOUT"}


def require(result: dict[str, Any], label: str) -> str:
    if result["code"] != 0:
        raise RuntimeError(
            f"{label}_FAILED:"
            + (str(result.get("stdout") or "") + "\n" + str(result.get("stderr") or ""))[-3000:]
        )
    return str(result.get("stdout") or "").strip()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def resolve_evidence(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def validate_current_truth() -> dict[str, Any]:
    session = load_json(SESSION_STATE, "SESSION_STATE")
    v07 = session.get("currentV07") or {}
    closure = v07.get("verifiedFinishClosureContract") or {}

    passed = list(closure.get("passedGates") or [])
    if passed != list(range(1, 13)):
        raise RuntimeError(f"GATES_1_12_PASS_REQUIRED:{passed}")
    if closure.get("activeGate") != 13:
        raise RuntimeError("ACTIVE_GATE_13_REQUIRED")
    if list(closure.get("remainingGates") or []) != [13]:
        raise RuntimeError("ONLY_GATE_13_REMAINING_REQUIRED")
    if closure.get("finalAuthority") != "HUMAN_THRESHOLD":
        raise RuntimeError("HUMAN_THRESHOLD_FINAL_AUTHORITY_REQUIRED")

    gate12 = closure.get("gate12") or {}
    if gate12.get("state") != "PASS":
        raise RuntimeError("GATE12_PASS_REQUIRED")
    gate12_path = resolve_evidence(str(gate12.get("evidence") or ""))
    evidence = load_json(gate12_path, "GATE12_EVIDENCE")

    structural = {
        "state": evidence.get("state") == "PASS",
        "gate": evidence.get("gate") == 12,
        "duration": evidence.get("durationPass") is True,
        "interruptions": evidence.get("controlledInterruptionCount") == 3,
        "resources": (evidence.get("resources") or {}).get("state") == "PASS",
        "durable": (evidence.get("durableReconciliation") or {}).get("state") == "PASS",
        "regression": (evidence.get("finalRegression") or {}).get("state") == "PASS",
        "donecheck": evidence.get("postCampaignDoneCheckPass") is True,
        "technicalHoldZero": evidence.get("technicalHoldCount") == 0,
        "remotePush": evidence.get("remotePush") is False,
        "remoteMerge": evidence.get("remoteMerge") is False,
        "secondTruth": evidence.get("secondCanonicalTruth") is False,
        "externalA09": evidence.get("externalA09") == "EXTERNAL_BLOCKED_DEFERRED",
    }
    failed = [key for key, ok in structural.items() if not ok]
    if failed:
        raise RuntimeError("GATE12_STRUCTURAL_CHECK_FAILED:" + ",".join(failed))

    donecheck = evidence.get("postCampaignDoneCheck") or {}
    if donecheck.get("state") != "PASS":
        raise RuntimeError("POST_CAMPAIGN_DONECHECK_PASS_REQUIRED")
    if donecheck.get("version") != "1.2.0":
        raise RuntimeError("DONECHECK_V1_2_REQUIRED")
    if donecheck.get("exactSha") != "8b90a8fc93453dd8a84994195d28d14b15e261cb":
        raise RuntimeError("DONECHECK_EXACT_SHA_REQUIRED")

    a09 = closure.get("githubA09") or {}
    if a09.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("EXTERNAL_A09_DEFERRED_BOUNDARY_REQUIRED")
    if a09.get("blockingLocalVerifiedFinish") is not False:
        raise RuntimeError("A09_LOCAL_VERIFIED_FINISH_NONBLOCKING_REQUIRED")
    if a09.get("externalReconciliationRequiredWhenAvailable") is not True:
        raise RuntimeError("A09_EXTERNAL_RECONCILIATION_REQUIRED")

    accepted = load_json(ACCEPTED_STATE, "LOCAL_ACCEPTED_CANDIDATE")
    if accepted.get("state") != "PASS":
        raise RuntimeError("LOCAL_ACCEPTED_CANDIDATE_PASS_REQUIRED")
    if accepted.get("authority") != "PENDING_RECONCILIATION":
        raise RuntimeError("LOCAL_ACCEPTED_AUTHORITY_REQUIRED")
    if accepted.get("secondCanonicalTruth") is not False:
        raise RuntimeError("LOCAL_ACCEPTED_SECOND_TRUTH_FALSE_REQUIRED")

    branch = require(run(["git", "branch", "--show-current"], cwd=ROOT), "CONTROL_BRANCH")
    head = require(run(["git", "rev-parse", "HEAD"], cwd=ROOT), "CONTROL_HEAD")
    status = require(run(["git", "status", "--porcelain"], cwd=ROOT), "CONTROL_STATUS")
    origin_main = require(run(["git", "rev-parse", "origin/main"], cwd=ROOT), "CONTROL_ORIGIN_MAIN")

    if status:
        raise RuntimeError("CONTROL_WORKTREE_CLEAN_REQUIRED")
    if branch != accepted.get("branch"):
        raise RuntimeError("CONTROL_BRANCH_ACCEPTED_PARITY_REQUIRED")
    if head != accepted.get("head"):
        raise RuntimeError("CONTROL_HEAD_ACCEPTED_PARITY_REQUIRED")
    if origin_main != accepted.get("originMain"):
        raise RuntimeError("CONTROL_ORIGIN_MAIN_ACCEPTED_PARITY_REQUIRED")

    roadmap = load_json(ROADMAP, "PRODUCT_ROADMAP")
    v07_roadmap = next(
        (item for item in roadmap.get("versions", []) if item.get("version") == "v0.7"),
        None,
    )
    if not isinstance(v07_roadmap, dict):
        raise RuntimeError("V07_ROADMAP_REQUIRED")
    contract = v07_roadmap.get("verifiedFinishContract") or {}
    if list(contract.get("passed") or []) != list(range(1, 13)):
        raise RuntimeError("ROADMAP_GATES_1_12_PASS_REQUIRED")
    if contract.get("active") != 13:
        raise RuntimeError("ROADMAP_ACTIVE_GATE_13_REQUIRED")

    if not WORKLIST.is_file():
        raise RuntimeError("WORKLIST_REQUIRED")
    worklist = WORKLIST.read_text(encoding="utf-8")
    if "12. [x] **Final Verify + Consolidated Mac Long-Run Commissioning**" not in worklist:
        raise RuntimeError("WORKLIST_GATE12_PASS_REQUIRED")
    if "13. [ ] **Human Threshold™ + Authority Transition — ACTIVE / HUMAN DECISION REQUIRED**" not in worklist:
        raise RuntimeError("WORKLIST_GATE13_ACTIVE_REQUIRED")

    return {
        "session": session,
        "v07": v07,
        "closure": closure,
        "gate12Evidence": gate12_path,
        "gate12Digest": f"sha256:{sha256(gate12_path)}",
        "accepted": accepted,
        "control": {
            "branch": branch,
            "head": head,
            "originMain": origin_main,
            "clean": True,
        },
        "doneCheck": {
            "version": donecheck["version"],
            "exactSha": donecheck["exactSha"],
            "state": donecheck["state"],
        },
        "externalA09": a09,
    }


def review() -> dict[str, Any]:
    truth = validate_current_truth()
    run_dir = EVIDENCE_ROOT / stamp()
    payload = {
        "schema": "enguru.mac-engineer.v07-human-threshold-review/v1",
        "observedAt": now(),
        "state": "HOLD",
        "hold": "HUMAN_DECISION_REQUIRED",
        "gate": 13,
        "engineeringGates": "12_OF_12_PASS",
        "technicalHoldCount": 0,
        "gate12Evidence": str(truth["gate12Evidence"]),
        "gate12Digest": truth["gate12Digest"],
        "doneCheck": truth["doneCheck"],
        "control": truth["control"],
        "externalA09": {
            "state": truth["externalA09"].get("state"),
            "preserved": True,
            "externalReconciliationRequiredWhenAvailable": True,
        },
        "authorityTransitionTarget": (
            "ENGÜRÜ Mac-Native Engineering Authority™ — "
            "Mac-local Build, Repair, Recovery & Verification Authority"
        ),
        "humanDecisionOptions": ["ACCEPT", "HOLD"],
        "acceptMeaning": (
            "Accept Mac-native primary local engineering authority for v0.7 "
            "with external GitHub A09 preserved as deferred external evidence."
        ),
        "holdMeaning": (
            "Keep Gate 13 open and preserve 12/13 PASS while additional human review continues."
        ),
        "canonicalLockCreated": False,
        "nextAction": "EXPLICIT_HUMAN_ACCEPT_OR_HOLD",
    }
    path = run_dir / "review.json"
    payload["evidencePath"] = str(path)
    atomic_json(path, payload)
    return payload


def accept() -> dict[str, Any]:
    supplied = os.environ.get("ENGURU_HUMAN_ACCEPTANCE", "")
    if supplied != ACCEPT_TOKEN:
        raise RuntimeError("EXPLICIT_HUMAN_ACCEPTANCE_TOKEN_REQUIRED")

    truth = validate_current_truth()
    run_dir = EVIDENCE_ROOT / stamp()
    payload = {
        "schema": "enguru.mac-engineer.v07-human-threshold-decision/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": 13,
        "decision": "ACCEPT",
        "humanThreshold": "ACCEPTED",
        "engineeringGates": "12_OF_12_PASS",
        "technicalHoldCount": 0,
        "gate12Evidence": str(truth["gate12Evidence"]),
        "gate12Digest": truth["gate12Digest"],
        "doneCheck": truth["doneCheck"],
        "control": truth["control"],
        "externalA09": {
            "state": truth["externalA09"].get("state"),
            "preserved": True,
            "promoted": False,
            "externalReconciliationRequiredWhenAvailable": True,
        },
        "authorityTransitionAccepted": True,
        "authorityTransitionTarget": (
            "ENGÜRÜ Mac-Native Engineering Authority™ — "
            "Mac-local Build, Repair, Recovery & Verification Authority"
        ),
        "canonicalLockCreated": False,
        "canonicalLockPending": True,
        "nextAction": "CANONICAL_V0_7_LOCK_RECONCILIATION",
    }
    path = run_dir / "human-decision.json"
    payload["evidencePath"] = str(path)
    atomic_json(path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", choices=["REVIEW", "ACCEPT"], default="REVIEW")
    args = parser.parse_args()

    try:
        result = review() if args.decision == "REVIEW" else accept()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_HUMAN_THRESHOLD_PRECONDITIONS")
        return 2

    if args.decision == "REVIEW":
        print("STATE=HOLD")
        print("HOLD=HUMAN_DECISION_REQUIRED")
        print("HUMAN_THRESHOLD_REVIEW_READY=PASS")
        print("ENGINEERING_GATES=12_OF_12_PASS")
        print("TECHNICAL_HOLD_COUNT=0")
        print("DONECHECK_V12=PASS")
        print("EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED")
        print("AUTHORITY_TRANSITION_TARGET=MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY")
        print("HUMAN_DECISION_OPTIONS=ACCEPT|HOLD")
        print(f"EVIDENCE={result['evidencePath']}")
        print("NEXT_ACTION=EXPLICIT_HUMAN_ACCEPT_OR_HOLD")
        return 2

    print("STATE=PASS")
    print("HUMAN_THRESHOLD=ACCEPTED")
    print("ENGINEERING_GATES=12_OF_12_PASS")
    print("TECHNICAL_HOLD_COUNT=0")
    print("DONECHECK_V12=PASS")
    print("EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED")
    print("EXTERNAL_A09_PROMOTED=false")
    print("AUTHORITY_TRANSITION_ACCEPTED=PASS")
    print("CANONICAL_LOCK_CREATED=false")
    print("CANONICAL_LOCK_PENDING=true")
    print(f"EVIDENCE={result['evidencePath']}")
    print("NEXT_ACTION=CANONICAL_V0_7_LOCK_RECONCILIATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
