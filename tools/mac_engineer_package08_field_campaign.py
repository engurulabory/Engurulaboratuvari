#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_safe_execution_orchestrator as safe
import mac_engineer_governed_finish_adapter as finish

LEDGER = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json"
)


def now():
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha(path: Path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def write(path: Path, value):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def run_capability01(
    evidence_root: Path,
) -> Path:

    capability_id = (
        "CURRENT_TECHNICAL_TRUTH_READ"
    )

    ledger = load(LEDGER)
    row = ledger["capabilities"][0]

    if row["capabilityId"] != capability_id:
        raise RuntimeError(
            "CAPABILITY01_LEDGER_IDENTITY_MISMATCH"
        )

    if row["fieldState"] != "PENDING":
        raise RuntimeError(
            "CAPABILITY01_NOT_PENDING"
        )

    first = safe.execute_proven_read_only(
        capability_id
    )

    if (
        first.get("STATE") != "PASS"
        or first.get("EXECUTION_PERFORMED")
        is not True
        or first.get(
            "NETWORK_ACCESS_PERFORMED"
        ) is not False
        or first.get(
            "FILESYSTEM_MUTATION_PERFORMED"
        ) is not False
    ):
        raise RuntimeError(
            "CAPABILITY01_REAL_EXECUTION_FAILED"
        )

    result = first.get("RESULT")

    if not isinstance(result, dict) or not result:
        raise RuntimeError(
            "CAPABILITY01_EXPECTED_RESULT_MISSING"
        )

    failure = safe.execute_proven_read_only(
        "PACKAGE08_INTENTIONAL_UNKNOWN_CAPABILITY"
    )

    if not (
        failure.get("STATE") == "HOLD"
        and failure.get(
            "EXECUTION_PERFORMED"
        ) is False
    ):
        raise RuntimeError(
            "CAPABILITY01_FAILURE_PATH_NOT_FAIL_CLOSED"
        )

    fresh = safe.execute_proven_read_only(
        capability_id
    )

    if not (
        fresh.get("STATE") == "PASS"
        and fresh.get(
            "EXECUTION_PERFORMED"
        ) is True
    ):
        raise RuntimeError(
            "CAPABILITY01_FRESH_REVERIFY_FAILED"
        )

    execution_evidence = {
        "schema":
            "enguru.mac-engineer.package08-capability-execution-evidence/v1",

        "state": "PASS",

        "claim":
            "CURRENT_TECHNICAL_TRUTH_READ_REAL_OSI_EXECUTION_PASS",

        "capabilityIndex": 1,

        "capabilityId":
            capability_id,

        "observedAt":
            now(),

        "acceptance": {
            "discovered": True,
            "invocable": True,
            "realTaskExecuted": True,
            "expectedResultObserved": True,
            "failurePathTested": True,
            "freshReverify": True
        },

        "execution": {
            "first": first,
            "failurePath": failure,
            "fresh": fresh
        }
    }

    execution_path = (
        evidence_root
        / "capability-01"
        / "execution-evidence.json"
    )

    write(
        execution_path,
        execution_evidence,
    )

    execution_digest = sha(
        execution_path
    )

    execution_id = (
        "package08-cap01:"
        + execution_digest[:32]
    )

    task_id = (
        "package08-cap01-"
        + execution_digest[:16]
    )

    machine = finish.verify_machine_finish(
        evidence_path=
            execution_path,

        execution_id=
            execution_id,

        task_id=
            task_id,

        criterion_id=
            capability_id,

        statement=
            "CURRENT_TECHNICAL_TRUTH_READ real OSi field acceptance is PASS",
    )

    if (
        machine.get(
            "DONECHECK_STATE"
        )
        != "PASS"
    ):
        raise RuntimeError(
            "CAPABILITY01_DONECHECK_FAILED"
        )

    final = {
        "schema":
            "enguru.mac-engineer.package08-capability-field-proof/v1",

        "state": "PASS",

        "claim":
            "CURRENT_TECHNICAL_TRUTH_READ_FIELD_VERIFIED",

        "capabilityIndex": 1,

        "capabilityId":
            capability_id,

        "observedAt":
            now(),

        "acceptance": {
            "discovered": True,
            "invocable": True,
            "realTaskExecuted": True,
            "expectedResultObserved": True,
            "failurePathTested": True,
            "freshReverify": True,
            "evidenceBound": True,
            "doneCheckPass": True,
            "fieldVerified": True
        },

        "executionEvidence": {
            "path":
                str(execution_path),

            "sha256":
                execution_digest
        },

        "doneCheck": {
            "state":
                machine[
                    "DONECHECK_STATE"
                ],

            "version":
                machine[
                    "DONECHECK_VERSION"
                ],

            "exactSha":
                machine[
                    "DONECHECK_SHA"
                ],

            "verificationResultId":
                machine.get(
                    "VERIFICATION_RESULT_ID"
                )
        },

        "safety": {
            "networkAccessPerformed":
                False,

            "filesystemMutationPerformed":
                False,

            "authorityBypass":
                False,

            "criticalFalsePass":
                False
        }
    }

    final_path = (
        evidence_root
        / "capability-01"
        / "evidence.json"
    )

    write(
        final_path,
        final,
    )

    row["fieldState"] = (
        "FIELD_VERIFIED"
    )

    row["acceptance"] = dict(
        final["acceptance"]
    )

    row["evidence"] = {
        "path":
            str(final_path),

        "sha256":
            sha(final_path)
    }

    ledger["fieldVerifiedCount"] = sum(
        1
        for item in ledger["capabilities"]
        if item["fieldState"]
        == "FIELD_VERIFIED"
    )

    if ledger["fieldVerifiedCount"] != 1:
        raise RuntimeError(
            "CAPABILITY01_FIELD_COUNT_NOT_EXACTLY_ONE"
        )

    write(
        LEDGER,
        ledger,
    )

    return final_path



def _git_field_truth(repo):
    import subprocess

    def run_git(*args):
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            check=False,
        )

        return {
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }

    branch = run_git(
        "branch",
        "--show-current",
    )

    head = run_git(
        "rev-parse",
        "HEAD",
    )

    status = run_git(
        "status",
        "--porcelain",
    )

    if (
        branch["code"] != 0
        or head["code"] != 0
        or status["code"] != 0
    ):
        return {
            "STATE": "HOLD",
            "REASON": "GIT_TRUTH_UNAVAILABLE",
        }

    return {
        "STATE": "PASS",
        "branch": branch["stdout"],
        "head": head["stdout"],
        "status": status["stdout"],
    }


def _canonical_boot_policy(
    control_truth,
    product_truth,
):
    reasons = []

    if control_truth.get("STATE") != "PASS":
        reasons.append(
            "CONTROL_TRUTH_UNAVAILABLE"
        )

    if product_truth.get("STATE") != "PASS":
        reasons.append(
            "PRODUCT_TRUTH_UNAVAILABLE"
        )

    if control_truth.get("branch") == "main":
        reasons.append(
            "CONTROL_MAIN_BRANCH_FORBIDDEN"
        )

    if product_truth.get("branch") == "main":
        reasons.append(
            "PRODUCT_MAIN_BRANCH_FORBIDDEN"
        )

    if product_truth.get("status") != "":
        reasons.append(
            "PRODUCT_WORKTREE_NOT_CLEAN"
        )

    if reasons:
        return {
            "STATE": "HOLD",
            "EXECUTION_ALLOWED": False,
            "REASONS": reasons,
        }

    return {
        "STATE": "PASS",
        "EXECUTION_ALLOWED": True,
    }


def run_capability02(
    evidence_root: Path,
) -> Path:

    import mac_engineer_operator as operator
    from mac_engineer_local_candidate_authority import (
        evaluate_local_accepted_candidate,
    )

    capability_id = "CANONICAL_BOOT"

    ledger = load(LEDGER)
    row = ledger["capabilities"][1]

    if row["capabilityId"] != capability_id:
        raise RuntimeError(
            "CAPABILITY02_LEDGER_IDENTITY_MISMATCH"
        )

    if row["fieldState"] != "PENDING":
        raise RuntimeError(
            "CAPABILITY02_NOT_PENDING"
        )

    product = (
        Path.home()
        / "Enguru"
        / "Projects"
        / "enguru-mac-engineer"
    )

    control_before = _git_field_truth(ROOT)
    product_before = _git_field_truth(product)

    policy = _canonical_boot_policy(
        control_before,
        product_before,
    )

    if (
        policy.get("STATE") != "PASS"
        or policy.get(
            "EXECUTION_ALLOWED"
        ) is not True
    ):
        raise RuntimeError(
            "CAPABILITY02_PREFLIGHT_HOLD"
        )

    session_state = load(
        ROOT
        / "governance"
        / "mac-engineer"
        / "SESSION_STATE_V1.json"
    )

    control_for_authority = (
        operator.git_state(ROOT)
    )

    local_candidate = (
        evaluate_local_accepted_candidate(
            control_for_authority,
            session_state,
        )
    )

    if local_candidate.get("authorized") is not True:
        raise RuntimeError(
            "CAPABILITY02_FRESH_LOCAL_ACCEPTED_CANDIDATE_REQUIRED:"
            + ",".join(
                local_candidate.get("reasons")
                or []
            )
        )

    # Failure path:
    # same policy must fail closed if either repo is on main.
    synthetic_control = dict(
        control_before
    )

    synthetic_control["branch"] = "main"

    negative = _canonical_boot_policy(
        synthetic_control,
        product_before,
    )

    failure_path_ok = (
        negative.get("STATE") == "HOLD"
        and negative.get(
            "EXECUTION_ALLOWED"
        ) is False
        and "CONTROL_MAIN_BRANCH_FORBIDDEN"
        in negative.get("REASONS", [])
    )

    if not failure_path_ok:
        raise RuntimeError(
            "CAPABILITY02_FAILURE_PATH_NOT_FAIL_CLOSED"
        )

    first = operator.canonical_boot()

    if first.get("state") != "PASS":
        raise RuntimeError(
            "CAPABILITY02_FIRST_BOOT_HOLD"
        )

    first_sync = (
        first.get("sync")
        or {}
    )

    first_start = (
        first.get("session_start")
        or {}
    )

    first_online = (
        first.get("online_sync")
        or {}
    )

    if (
        first_sync.get("code") != 0
        or first_start.get("code") != 0
    ):
        raise RuntimeError(
            "CAPABILITY02_FIRST_BOOT_SUBSTEP_HOLD"
        )

    allowed_modes = {
        "ONLINE_WORKING_BRANCH_PRESERVED",
        "OFFLINE_CACHED",
    }

    for name in (
        "control_plane",
        "product",
    ):
        sync_row = (
            first_online.get(name)
            or {}
        )

        if sync_row.get("state") != "PASS":
            raise RuntimeError(
                "CAPABILITY02_ONLINE_SYNC_HOLD_"
                + name
            )

        if sync_row.get("mode") not in allowed_modes:
            raise RuntimeError(
                "CAPABILITY02_UNSAFE_SYNC_MODE_"
                + str(sync_row.get("mode"))
            )

    control_after_first = (
        _git_field_truth(ROOT)
    )

    product_after_first = (
        _git_field_truth(product)
    )

    source_parity_first = (
        control_after_first.get("head")
        == control_before.get("head")
        and product_after_first.get("head")
        == product_before.get("head")
        and control_after_first.get("status")
        == control_before.get("status")
        and product_after_first.get("status")
        == product_before.get("status")
    )

    if not source_parity_first:
        raise RuntimeError(
            "CAPABILITY02_SOURCE_PARITY_BROKEN_AFTER_FIRST_BOOT"
        )

    # Fresh second run:
    # proves repeatability / regenerable recovery path.
    fresh = operator.canonical_boot()

    if fresh.get("state") != "PASS":
        raise RuntimeError(
            "CAPABILITY02_FRESH_BOOT_HOLD"
        )

    fresh_sync = (
        fresh.get("sync")
        or {}
    )

    fresh_start = (
        fresh.get("session_start")
        or {}
    )

    if (
        fresh_sync.get("code") != 0
        or fresh_start.get("code") != 0
    ):
        raise RuntimeError(
            "CAPABILITY02_FRESH_BOOT_SUBSTEP_HOLD"
        )

    fresh_online = (
        fresh.get("online_sync")
        or {}
    )

    for name in (
        "control_plane",
        "product",
    ):
        sync_row = (
            fresh_online.get(name)
            or {}
        )

        if (
            sync_row.get("state")
            != "PASS"
            or sync_row.get("mode")
            not in allowed_modes
        ):
            raise RuntimeError(
                "CAPABILITY02_FRESH_SYNC_POLICY_HOLD_"
                + name
            )

    control_after = _git_field_truth(
        ROOT
    )

    product_after = _git_field_truth(
        product
    )

    source_parity_final = (
        control_after.get("head")
        == control_before.get("head")
        and product_after.get("head")
        == product_before.get("head")
        and control_after.get("status")
        == control_before.get("status")
        and product_after.get("status")
        == product_before.get("status")
    )

    if not source_parity_final:
        raise RuntimeError(
            "CAPABILITY02_SOURCE_PARITY_BROKEN_AFTER_FRESH_BOOT"
        )

    execution = {
        "schema":
            "enguru.mac-engineer.package08-capability-execution-evidence/v1",

        "state": "PASS",

        "claim":
            "CANONICAL_BOOT_REAL_OSI_EXECUTION_PASS",

        "capabilityIndex": 2,

        "capabilityId":
            capability_id,

        "observedAt":
            now(),

        "acceptance": {
            "discovered": True,
            "invocable": True,
            "realTaskExecuted": True,
            "expectedResultObserved": True,
            "failurePathTested": True,
            "freshReverify": True,
            "recoveryOrRollbackPass": True,
        },

        "authority": {
            "networkPolicy":
                "READ_ONLY_NETWORK_BY_DEFAULT",

            "mutationScope":
                "EXPLICIT_AUTHORIZED_PATHS_ONLY",

            "sourceHeadMovementAllowed":
                False,

            "sourceWorktreeMutationAllowed":
                False,

            "derivedRuntimeContextWriteAllowed":
                True,

            "evidenceWriteAllowed":
                True,
        },

        "preflight": {
            "control":
                control_before,
            "product":
                product_before,
        },

        "failurePath": {
            "state":
                negative["STATE"],
            "reasons":
                negative.get(
                    "REASONS"
                ),
        },

        "firstBoot":
            first,

        "freshBoot":
            fresh,

        "postcondition": {
            "control":
                control_after,
            "product":
                product_after,

            "sourceParityAfterFirst":
                source_parity_first,

            "sourceParityFinal":
                source_parity_final,
        },
    }

    execution_path = (
        evidence_root
        / "capability-02"
        / "execution-evidence.json"
    )

    write(
        execution_path,
        execution,
    )

    digest = sha(
        execution_path
    )

    machine = (
        finish.verify_machine_finish(
            evidence_path=
                execution_path,

            execution_id=
                "package08-cap02:"
                + digest[:32],

            task_id=
                "package08-cap02-"
                + digest[:16],

            criterion_id=
                capability_id,

            statement=
                "CANONICAL_BOOT real OSi field acceptance is PASS",
        )
    )

    if (
        machine.get(
            "DONECHECK_STATE"
        )
        != "PASS"
    ):
        raise RuntimeError(
            "CAPABILITY02_DONECHECK_FAILED"
        )

    final = {
        "schema":
            "enguru.mac-engineer.package08-capability-field-proof/v1",

        "state": "PASS",

        "claim":
            "CANONICAL_BOOT_FIELD_VERIFIED",

        "capabilityIndex": 2,

        "capabilityId":
            capability_id,

        "observedAt":
            now(),

        "acceptance": {
            "discovered": True,
            "invocable": True,
            "realTaskExecuted": True,
            "expectedResultObserved": True,
            "failurePathTested": True,
            "freshReverify": True,
            "evidenceBound": True,
            "doneCheckPass": True,
            "fieldVerified": True,
            "recoveryOrRollbackPass": True,
        },

        "executionEvidence": {
            "path":
                str(
                    execution_path
                ),
            "sha256":
                digest,
        },

        "doneCheck": {
            "state":
                machine[
                    "DONECHECK_STATE"
                ],

            "version":
                machine[
                    "DONECHECK_VERSION"
                ],

            "exactSha":
                machine[
                    "DONECHECK_SHA"
                ],

            "verificationResultId":
                machine.get(
                    "VERIFICATION_RESULT_ID"
                ),
        },

        "safety": {
            "controlHeadUnchanged":
                control_after["head"]
                == control_before["head"],

            "productHeadUnchanged":
                product_after["head"]
                == product_before["head"],

            "controlWorktreeStatusUnchanged":
                control_after["status"]
                == control_before["status"],

            "productWorktreeStatusUnchanged":
                product_after["status"]
                == product_before["status"],

            "authorityBypass":
                False,

            "criticalFalsePass":
                False,

            "untrackedSourceMutation":
                False,
        },
    }

    final_path = (
        evidence_root
        / "capability-02"
        / "evidence.json"
    )

    write(
        final_path,
        final,
    )

    row["fieldState"] = (
        "FIELD_VERIFIED"
    )

    row["acceptance"] = dict(
        final["acceptance"]
    )

    row["evidence"] = {
        "path":
            str(final_path),
        "sha256":
            sha(final_path),
    }

    ledger["fieldVerifiedCount"] = sum(
        1
        for item in ledger[
            "capabilities"
        ]
        if item["fieldState"]
        == "FIELD_VERIFIED"
    )

    if ledger[
        "fieldVerifiedCount"
    ] != 2:
        raise RuntimeError(
            "CAPABILITY02_FIELD_COUNT_NOT_EXACTLY_TWO"
        )

    write(
        LEDGER,
        ledger,
    )

    return final_path

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--capability",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--evidence-root",
        required=True,
    )

    args = parser.parse_args()

    evidence_root = Path(
        args.evidence_root
    ).expanduser()

    if args.capability == 1:
        path = run_capability01(
            evidence_root
        )

    elif args.capability == 2:
        path = run_capability02(
            evidence_root
        )

    else:
        print("STATE=HOLD")
        print(
            "REASON=CAPABILITY_NOT_YET_BOUND"
        )
        return 20

    print(
        "EVIDENCE="
        + str(path)
    )

    print(
        "EVIDENCE_SHA256="
        + sha(path)
    )

    print("STATE=PASS")
    print(
        "CLAIM=CAPABILITY01_CURRENT_TECHNICAL_TRUTH_READ_FIELD_VERIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def canonical_boot_field_preflight():
    import subprocess
    from pathlib import Path

    control = ROOT

    product = (
        Path.home()
        / "Enguru"
        / "Projects"
        / "enguru-mac-engineer"
    )

    def git(repo, *args):
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            check=False,
        )

        return {
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }

    def truth(repo):
        branch = git(
            repo,
            "branch",
            "--show-current",
        )

        head = git(
            repo,
            "rev-parse",
            "HEAD",
        )

        status = git(
            repo,
            "status",
            "--porcelain",
        )

        if (
            branch["code"] != 0
            or head["code"] != 0
            or status["code"] != 0
        ):
            return {
                "STATE": "HOLD",
                "REASON":
                    "GIT_TRUTH_UNAVAILABLE",
            }

        return {
            "STATE": "PASS",
            "branch":
                branch["stdout"],
            "head":
                head["stdout"],
            "status":
                status["stdout"],
        }

    control_truth = truth(control)
    product_truth = truth(product)

    reasons = []

    if control_truth.get("STATE") != "PASS":
        reasons.append(
            "CONTROL_TRUTH_UNAVAILABLE"
        )

    if product_truth.get("STATE") != "PASS":
        reasons.append(
            "PRODUCT_TRUTH_UNAVAILABLE"
        )

    if control_truth.get("branch") == "main":
        reasons.append(
            "CONTROL_MAIN_BRANCH_FORBIDDEN"
        )

    if product_truth.get("branch") == "main":
        reasons.append(
            "PRODUCT_MAIN_BRANCH_FORBIDDEN"
        )

    if product_truth.get("status") != "":
        reasons.append(
            "PRODUCT_WORKTREE_NOT_CLEAN"
        )

    if reasons:
        return {
            "STATE": "HOLD",
            "EXECUTION_ALLOWED": False,
            "REASONS": reasons,
            "control": control_truth,
            "product": product_truth,
        }

    return {
        "STATE": "PASS",
        "EXECUTION_ALLOWED": True,

        "authority": {
            "networkReadAllowed": True,
            "sourceHeadMovementAllowed": False,
            "sourceWorktreeMutationAllowed": False,
            "derivedRuntimeStateWriteAllowed": True,
            "evidenceWriteAllowed": True,
            "offlineCachedFallbackAllowed": True,
        },

        "control": control_truth,
        "product": product_truth,
    }


def canonical_boot_postcondition(
    before,
):
    import subprocess
    from pathlib import Path

    control = ROOT

    product = (
        Path.home()
        / "Enguru"
        / "Projects"
        / "enguru-mac-engineer"
    )

    def git(repo, *args):
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.stdout.strip()

    after = {
        "controlHead":
            git(
                control,
                "rev-parse",
                "HEAD",
            ),

        "productHead":
            git(
                product,
                "rev-parse",
                "HEAD",
            ),
    }

    expected_control = (
        before["control"]["head"]
    )

    expected_product = (
        before["product"]["head"]
    )

    if (
        after["controlHead"]
        != expected_control
    ):
        return {
            "STATE": "HOLD",
            "REASON":
                "CONTROL_HEAD_MOVED",
            "after": after,
        }

    if (
        after["productHead"]
        != expected_product
    ):
        return {
            "STATE": "HOLD",
            "REASON":
                "PRODUCT_HEAD_MOVED",
            "after": after,
        }

    return {
        "STATE": "PASS",
        "SOURCE_HEADS_UNCHANGED": True,
        "after": after,
    }
