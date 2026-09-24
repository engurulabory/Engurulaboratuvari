#!/usr/bin/env python3
"""Fresh local acceptance for the current control-plane candidate branch."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from tools.mac_engineer_local_candidate_authority import (
        local_candidate_policy_phase,
    )
except ModuleNotFoundError:
    from mac_engineer_local_candidate_authority import (
        local_candidate_policy_phase,
    )


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
RUNTIME_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state"
ACCEPTANCE_STATE = RUNTIME_STATE / "local-accepted-control-plane-candidate.json"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "canonical-boot"


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(cmd: list[str], *, timeout: int = 7200) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def git_value(*args: str) -> str:
    result = run(["git", *args], timeout=120)
    return result["stdout"].strip() if result["code"] == 0 else ""


def write_state(payload: dict[str, Any]) -> None:
    RUNTIME_STATE.mkdir(parents=True, exist_ok=True)
    ACCEPTANCE_STATE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fail(reason: str, details: dict[str, Any] | None = None) -> int:
    payload = {
        "schema": "enguru.mac-engineer.local-accepted-control-plane-candidate/v1",
        "state": "HOLD",
        "observedAt": now(),
        "reason": reason,
        "details": details or {},
    }
    write_state(payload)
    print("STATE=HOLD")
    print(f"HOLD={reason}")
    print(f"EVIDENCE={ACCEPTANCE_STATE}")
    print("NEXT_ACTION=RECONCILE_LOCAL_CANDIDATE")
    return 2


def main() -> int:
    session = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
    policy = ((session.get("currentV07") or {}).get("controlPlaneLocalContinuity") or {})

    expected_branch = str(policy.get("branch") or "")
    external_hold = str(policy.get("externalMergeGate") or "")
    acceptance_authority = str(policy.get("localAuthority") or "")
    policy_phase = local_candidate_policy_phase(policy)
    if (
        policy_phase is None
        or not expected_branch
        or policy.get("canonicalRemoteAuthority") != "GITHUB_REMOTE_MAIN"
        or policy.get("secondCanonicalTruth") is not False
        or not external_hold.startswith("HOLD_")
    ):
        return fail(
            "LOCAL_CANDIDATE_POLICY_INVALID",
            {
                "policyState": policy.get("state"),
                "localAuthority": acceptance_authority,
                "policyPhase": policy_phase,
            },
        )

    fetch = run(["git", "fetch", "--prune", "origin"], timeout=300)
    if fetch["code"] != 0:
        return fail(
            "REMOTE_REFRESH_REQUIRED",
            {"stderr_tail": fetch["stderr"][-2000:]},
        )

    branch = git_value("branch", "--show-current")
    head = git_value("rev-parse", "HEAD")
    origin_main = git_value("rev-parse", "origin/main")
    origin_branch = git_value("rev-parse", f"origin/{expected_branch}")
    status = git_value("status", "--porcelain")
    merge_base = git_value("merge-base", "HEAD", "origin/main")
    ahead = git_value("rev-list", "--count", "origin/main..HEAD")

    preflight = {
        "branch": branch,
        "head": head,
        "originMain": origin_main,
        "originBranch": origin_branch,
        "mergeBase": merge_base,
        "ahead": ahead,
        "clean": status == "",
    }

    if branch != expected_branch:
        return fail("EXPECTED_CANDIDATE_BRANCH_REQUIRED", preflight)
    if not head or head != origin_branch:
        return fail("REMOTE_BRANCH_PARITY_REQUIRED", preflight)
    if not origin_main or merge_base != origin_main:
        return fail("ORIGIN_MAIN_ANCESTOR_REQUIRED", preflight)
    if status:
        return fail("CONTROL_PLANE_CLEAN_REQUIRED", preflight)
    if not ahead.isdigit() or int(ahead) < 1:
        return fail("LOCAL_CANDIDATE_AHEAD_OF_MAIN_REQUIRED", preflight)

    targeted_commands = [
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_mac_engineer_local_candidate_authority.py",
            "-v",
        ],
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_mac_engineer_operator.py",
            "-v",
        ],
    ]
    targeted_results = [run(cmd) for cmd in targeted_commands]
    if any(item["code"] != 0 for item in targeted_results):
        return fail(
            "TARGETED_CANONICAL_BOOT_TESTS_FAILED",
            {
                "preflight": preflight,
                "results": [
                    {
                        "code": item["code"],
                        "stdout_tail": item["stdout"][-3000:],
                        "stderr_tail": item["stderr"][-3000:],
                    }
                    for item in targeted_results
                ],
            },
        )

    full = run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        timeout=7200,
    )
    if full["code"] != 0:
        return fail(
            "FULL_CONTROL_PLANE_REGRESSION_FAILED",
            {
                "preflight": preflight,
                "stdout_tail": full["stdout"][-5000:],
                "stderr_tail": full["stderr"][-5000:],
            },
        )

    diff_check = run(["git", "diff", "--check", "origin/main...HEAD"], timeout=120)
    post_status = git_value("status", "--porcelain")
    post_head = git_value("rev-parse", "HEAD")
    post_origin_main = git_value("rev-parse", "origin/main")
    post_origin_branch = git_value("rev-parse", f"origin/{expected_branch}")

    if diff_check["code"] != 0:
        return fail("DIFF_CHECK_FAILED", {"stderr_tail": diff_check["stderr"][-2000:]})
    if post_status:
        return fail("TESTS_CHANGED_WORKTREE", {"status": post_status})
    if post_head != head or post_origin_main != origin_main or post_origin_branch != origin_branch:
        return fail("GIT_TRUTH_CHANGED_DURING_ACCEPTANCE")

    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    evidence_path = EVIDENCE_ROOT / f"{stamp()}-local-accepted-candidate.json"
    evidence_payload = {
        "schema": "enguru.mac-engineer.local-accepted-control-plane-candidate-evidence/v1",
        "state": "PASS",
        "observedAt": now(),
        "branch": branch,
        "head": head,
        "originMain": origin_main,
        "originBranch": origin_branch,
        "mergeBase": merge_base,
        "aheadOfMain": int(ahead),
        "clean": True,
        "authority": acceptance_authority,
        "policyPhase": policy_phase,
        "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
        "secondCanonicalTruth": False,
        "externalMergeGate": external_hold,
        "tests": {
            "targetedCanonicalBoot": "PASS",
            "operatorTargeted": "PASS",
            "fullControlPlaneRegression": "PASS",
            "diffCheck": "PASS",
        },
    }
    evidence_path.write_text(
        json.dumps(evidence_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    acceptance = {
        "schema": "enguru.mac-engineer.local-accepted-control-plane-candidate/v1",
        "state": "PASS",
        "observedAt": now(),
        "branch": branch,
        "head": head,
        "originMain": origin_main,
        "originBranch": origin_branch,
        "clean": True,
        "authority": acceptance_authority,
        "policyPhase": policy_phase,
        "canonicalRemoteAuthority": "GITHUB_REMOTE_MAIN",
        "secondCanonicalTruth": False,
        "externalMergeGate": external_hold,
        "evidence": str(evidence_path),
        "acceptance": {
            "targetedTests": "PASS",
            "fullRegression": "PASS",
            "diffCheck": "PASS",
            "remoteBranchParity": "PASS",
            "mainAncestor": "PASS",
            "canonicalContext": "PENDING",
            "sessionStart": "PENDING",
        },
    }
    write_state(acceptance)

    sync = run([sys.executable, "-B", "tools/mac_engineering_sync_context.py"], timeout=300)
    start = run([sys.executable, "-B", "tools/mac_engineer_session_continuity.py", "start"], timeout=300)

    if sync["code"] != 0 or start["code"] != 0:
        acceptance["state"] = "HOLD"
        acceptance["reason"] = "CANONICAL_BOOT_VALIDATION_FAILED"
        acceptance["bootValidation"] = {
            "canonicalContext": {
                "code": sync["code"],
                "stdout_tail": sync["stdout"][-3000:],
                "stderr_tail": sync["stderr"][-3000:],
            },
            "sessionStart": {
                "code": start["code"],
                "stdout_tail": start["stdout"][-3000:],
                "stderr_tail": start["stderr"][-3000:],
            },
        }
        write_state(acceptance)
        print("STATE=HOLD")
        print("HOLD=CANONICAL_BOOT_VALIDATION_FAILED")
        print(f"EVIDENCE={evidence_path}")
        print("NEXT_ACTION=RECONCILE_CANONICAL_BOOT")
        return 2

    acceptance["acceptance"]["canonicalContext"] = "PASS"
    acceptance["acceptance"]["sessionStart"] = "PASS"
    acceptance["bootValidation"] = {
        "canonicalContext": "PASS",
        "sessionStart": "PASS",
    }
    write_state(acceptance)

    print("STATE=PASS")
    print("MODE=LOCAL_ACCEPTED_CANDIDATE")
    print(f"BRANCH={branch}")
    print(f"HEAD={head}")
    print(f"ORIGIN_MAIN={origin_main}")
    print("TARGETED=PASS")
    print("FULL_REGRESSION=PASS")
    print("CANONICAL_CONTEXT=PASS")
    print("SESSION_START=PASS")
    print(f"AUTHORITY={acceptance_authority}")
    print(f"POLICY_PHASE={policy_phase}")
    print(f"EVIDENCE={evidence_path}")
    print("NEXT_ACTION=enguru-mac doctor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
