#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.7 — Verified Finish final acceptance.

Read-only final seal verification. Requires:
- fresh local accepted candidate on the exact current branch head;
- canonical SESSION_STATE / ROADMAP / WORKLIST already reconciled to 13/13;
- latest explicit Human Threshold ACCEPT receipt;
- Gate 12 final campaign PASS with post-campaign DoneCheck™ v1.2;
- external GitHub A09 preserved as deferred;
- clean worktree and diff hygiene.

Writes only local Evidence under ~/Enguru/Evidence/MacEngineer/v0.7/verified-finish.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance" / "mac-engineer" / "PRODUCT_ROADMAP_V1.json"
WORKLIST = ROOT / "WORKLIST.md"
CURRENT_STATUS = ROOT / "governance" / "mac-engineer" / "CURRENT_STATUS.md"
ACCEPTED_STATE = (
    HOME / "Enguru" / "Runtime" / "MacEngineer" / "state"
    / "local-accepted-control-plane-candidate.json"
)
HUMAN_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "human-threshold"
)
EVIDENCE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "verified-finish"
)
DONECHECK_SHA = "8b90a8fc93453dd8a84994195d28d14b15e261cb"


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


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 300) -> dict[str, Any]:
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


def latest_human_decision() -> Path:
    if not HUMAN_ROOT.is_dir():
        raise RuntimeError("HUMAN_THRESHOLD_EVIDENCE_ROOT_REQUIRED")
    candidates = sorted(
        HUMAN_ROOT.glob("*/human-decision.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("HUMAN_THRESHOLD_ACCEPT_RECEIPT_REQUIRED")
    return candidates[0]


def resolve(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def validate() -> dict[str, Any]:
    session = load_json(SESSION_STATE, "SESSION_STATE")
    v07 = session.get("currentV07") or {}
    closure = v07.get("verifiedFinishClosureContract") or {}

    if v07.get("state") != "VERIFIED_LOCKED":
        raise RuntimeError("SESSION_V07_VERIFIED_LOCKED_REQUIRED")
    if v07.get("humanThreshold") != "ACCEPTED":
        raise RuntimeError("SESSION_HUMAN_THRESHOLD_ACCEPTED_REQUIRED")
    if v07.get("engineeringMode") != "MAC_NATIVE_PRIMARY_AUTHORITY":
        raise RuntimeError("MAC_NATIVE_PRIMARY_AUTHORITY_REQUIRED")
    if list(closure.get("passedGates") or []) != list(range(1, 14)):
        raise RuntimeError("SESSION_13_OF_13_PASS_REQUIRED")
    if closure.get("activeGate") is not None:
        raise RuntimeError("SESSION_ACTIVE_GATE_CLEAR_REQUIRED")
    if list(closure.get("remainingGates") or []) != []:
        raise RuntimeError("SESSION_REMAINING_GATES_EMPTY_REQUIRED")
    if closure.get("state") != "VERIFIED_LOCKED_LOCAL_AUTHORITY":
        raise RuntimeError("SESSION_VERIFIED_LOCKED_STATE_REQUIRED")
    if closure.get("finalState") != "V0_7_LONG_RUN_RELIABILITY_VERIFIED_LOCKED":
        raise RuntimeError("SESSION_FINAL_STATE_REQUIRED")

    a09 = closure.get("githubA09") or {}
    if a09.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("EXTERNAL_A09_DEFERRED_REQUIRED")
    if a09.get("externalReconciliationRequiredWhenAvailable") is not True:
        raise RuntimeError("EXTERNAL_A09_RECONCILIATION_REQUIRED")
    if a09.get("blockingLocalVerifiedFinish") is not False:
        raise RuntimeError("EXTERNAL_A09_LOCAL_FINISH_NONBLOCKING_REQUIRED")

    gate12 = closure.get("gate12") or {}
    if gate12.get("state") != "PASS":
        raise RuntimeError("GATE12_PASS_REQUIRED")
    gate12_path = resolve(str(gate12.get("evidence") or ""))
    gate12_evidence = load_json(gate12_path, "GATE12_EVIDENCE")
    if gate12_evidence.get("state") != "PASS":
        raise RuntimeError("GATE12_EVIDENCE_PASS_REQUIRED")
    if gate12_evidence.get("technicalHoldCount") != 0:
        raise RuntimeError("GATE12_TECHNICAL_HOLD_ZERO_REQUIRED")
    if gate12_evidence.get("postCampaignDoneCheckPass") is not True:
        raise RuntimeError("GATE12_POST_CAMPAIGN_DONECHECK_REQUIRED")
    post_donecheck = gate12_evidence.get("postCampaignDoneCheck") or {}
    if post_donecheck.get("state") != "PASS":
        raise RuntimeError("DONECHECK_V12_PASS_REQUIRED")
    if post_donecheck.get("version") != "1.2.0":
        raise RuntimeError("DONECHECK_VERSION_1_2_REQUIRED")
    if post_donecheck.get("exactSha") != DONECHECK_SHA:
        raise RuntimeError("DONECHECK_EXACT_SHA_REQUIRED")

    human_path = latest_human_decision()
    human = load_json(human_path, "HUMAN_THRESHOLD_DECISION")
    if human.get("state") != "PASS":
        raise RuntimeError("HUMAN_DECISION_PASS_REQUIRED")
    if human.get("decision") != "ACCEPT":
        raise RuntimeError("HUMAN_DECISION_ACCEPT_REQUIRED")
    if human.get("humanThreshold") != "ACCEPTED":
        raise RuntimeError("HUMAN_THRESHOLD_ACCEPTED_REQUIRED")
    if human.get("authorityTransitionAccepted") is not True:
        raise RuntimeError("AUTHORITY_TRANSITION_ACCEPTED_REQUIRED")
    human_a09 = human.get("externalA09") or {}
    if human_a09.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("HUMAN_RECEIPT_A09_DEFERRED_REQUIRED")
    if human_a09.get("promoted") is not False:
        raise RuntimeError("HUMAN_RECEIPT_A09_NOT_PROMOTED_REQUIRED")

    roadmap = load_json(ROADMAP, "PRODUCT_ROADMAP")
    current = roadmap.get("current") or {}
    if current.get("version") != "v0.7":
        raise RuntimeError("ROADMAP_CURRENT_V07_REQUIRED")
    if current.get("state") != "LONG_RUN_RELIABILITY_VERIFIED_LOCKED":
        raise RuntimeError("ROADMAP_CURRENT_VERIFIED_LOCKED_REQUIRED")
    rv07 = next(
        (item for item in roadmap.get("versions", []) if item.get("version") == "v0.7"),
        None,
    )
    if not isinstance(rv07, dict) or rv07.get("state") != "VERIFIED_LOCKED":
        raise RuntimeError("ROADMAP_V07_VERIFIED_LOCKED_REQUIRED")
    contract = rv07.get("verifiedFinishContract") or {}
    if list(contract.get("passed") or []) != list(range(1, 14)):
        raise RuntimeError("ROADMAP_13_OF_13_PASS_REQUIRED")
    if contract.get("active") is not None or list(contract.get("remaining") or []) != []:
        raise RuntimeError("ROADMAP_GATE_CLOSURE_REQUIRED")

    worklist = WORKLIST.read_text(encoding="utf-8")
    if "13. [x] **Human Threshold™ + Authority Transition**" not in worklist:
        raise RuntimeError("WORKLIST_GATE13_PASS_REQUIRED")
    if "Closure state: 13/13 PASS." not in worklist:
        raise RuntimeError("WORKLIST_13_OF_13_REQUIRED")

    status_text = CURRENT_STATUS.read_text(encoding="utf-8")
    if "13/13 PASS / LONG-RUN RELIABILITY VERIFIED / LOCKED" not in status_text:
        raise RuntimeError("CURRENT_STATUS_VERIFIED_LOCKED_REQUIRED")

    accepted = load_json(ACCEPTED_STATE, "LOCAL_ACCEPTED_CANDIDATE")
    if accepted.get("state") != "PASS":
        raise RuntimeError("FRESH_LOCAL_ACCEPTED_CANDIDATE_REQUIRED")
    acceptance = accepted.get("acceptance") or {}
    required_acceptance = (
        "targetedTests",
        "fullRegression",
        "diffCheck",
        "remoteBranchParity",
        "mainAncestor",
        "canonicalContext",
        "sessionStart",
    )
    for key in required_acceptance:
        if acceptance.get(key) != "PASS":
            raise RuntimeError(f"FRESH_ACCEPTANCE_{key.upper()}_PASS_REQUIRED")

    branch = require(run(["git", "branch", "--show-current"], cwd=ROOT), "CONTROL_BRANCH")
    head = require(run(["git", "rev-parse", "HEAD"], cwd=ROOT), "CONTROL_HEAD")
    status = require(run(["git", "status", "--porcelain"], cwd=ROOT), "CONTROL_STATUS")
    diff_check = run(["git", "diff", "--check"], cwd=ROOT, timeout=120)
    require(diff_check, "CONTROL_DIFF_CHECK")

    if status:
        raise RuntimeError("CONTROL_WORKTREE_CLEAN_REQUIRED")
    if branch != accepted.get("branch"):
        raise RuntimeError("FRESH_ACCEPTANCE_BRANCH_PARITY_REQUIRED")
    if head != accepted.get("head"):
        raise RuntimeError("FRESH_ACCEPTANCE_HEAD_PARITY_REQUIRED")

    return {
        "session": session,
        "v07": v07,
        "closure": closure,
        "roadmap": roadmap,
        "accepted": accepted,
        "control": {"branch": branch, "head": head, "clean": True},
        "gate12Path": gate12_path,
        "gate12Digest": f"sha256:{sha256(gate12_path)}",
        "humanPath": human_path,
        "humanDigest": f"sha256:{sha256(human_path)}",
        "human": human,
        "doneCheck": {
            "version": post_donecheck.get("version"),
            "exactSha": post_donecheck.get("exactSha"),
            "state": post_donecheck.get("state"),
        },
        "externalA09": a09,
    }


def main() -> int:
    try:
        truth = validate()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_V07_VERIFIED_FINISH")
        return 2

    run_dir = EVIDENCE_ROOT / stamp()
    run_dir.mkdir(parents=True, exist_ok=False)
    evidence = {
        "schema": "enguru.mac-engineer.v07-verified-finish/v1",
        "observedAt": now(),
        "state": "PASS",
        "version": "v0.7",
        "verdict": "LONG_RUN_RELIABILITY_VERIFIED_LOCKED",
        "gates": "13_OF_13_PASS",
        "finalAuthority": "HUMAN_THRESHOLD_ACCEPTED",
        "engineeringAuthority": (
            "ENGÜRÜ Mac-Native Engineering Authority™ — "
            "Mac-local Build, Repair, Recovery & Verification Authority"
        ),
        "control": truth["control"],
        "freshLocalAcceptanceEvidence": truth["accepted"].get("evidence"),
        "gate12Evidence": str(truth["gate12Path"]),
        "gate12Digest": truth["gate12Digest"],
        "humanDecisionEvidence": str(truth["humanPath"]),
        "humanDecisionDigest": truth["humanDigest"],
        "doneCheck": truth["doneCheck"],
        "technicalHoldCount": 0,
        "externalA09": {
            "state": truth["externalA09"].get("state"),
            "promoted": False,
            "externalReconciliationRequiredWhenAvailable": True,
        },
        "secondCanonicalTruth": False,
        "remoteExternalPassManufactured": False,
        "nextAction": "AWAIT_NEXT_OBJECTIVE",
    }
    path = run_dir / "evidence.json"
    evidence["evidencePath"] = str(path)
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("STATE=PASS")
    print("VERIFIED_FINISH=PASS")
    print("VERSION=v0.7")
    print("GATES=13_OF_13_PASS")
    print("HUMAN_THRESHOLD=ACCEPTED")
    print("DONECHECK_V12=PASS")
    print("TECHNICAL_HOLD_COUNT=0")
    print("MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY=VERIFIED")
    print("EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED")
    print("EXTERNAL_A09_PROMOTED=false")
    print("SECOND_CANONICAL_TRUTH=false")
    print("VERDICT=LONG_RUN_RELIABILITY_VERIFIED_LOCKED")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=AWAIT_NEXT_OBJECTIVE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
