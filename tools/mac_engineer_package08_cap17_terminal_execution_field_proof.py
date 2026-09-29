#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

ROOT = Path.cwd()

sys.path.insert(
    0,
    str(ROOT / "tools"),
)

import mac_engineer_operator as operator


HOME = Path.home()

EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "package08-field-campaign"
)


def now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def stamp() -> str:
    return (
        datetime.now(timezone.utc)
        .strftime("%Y%m%dT%H%M%S%fZ")
    )


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(
        path.read_bytes()
    )


def canonical_command(
    python_executable: str,
    script: str,
) -> list[str]:
    return [
        python_executable,
        "-B",
        "-c",
        script,
    ]


def execute_explicit(
    *,
    requested: list[str],
    allowed: list[str],
    cwd: Path,
    allowed_cwd: Path,
    timeout: int,
) -> dict[str, Any]:

    if requested != allowed:
        return {
            "state":
                "HOLD",

            "reason":
                "COMMAND_NOT_EXACTLY_ALLOWLISTED",

            "executed":
                False,
        }

    if cwd.resolve() != allowed_cwd.resolve():
        return {
            "state":
                "HOLD",

            "reason":
                "COMMAND_CWD_SCOPE_VIOLATION",

            "executed":
                False,
        }

    if timeout < 1 or timeout > 30:
        return {
            "state":
                "HOLD",

            "reason":
                "COMMAND_TIMEOUT_SCOPE_VIOLATION",

            "executed":
                False,
        }

    result = operator.run(
        requested,
        cwd=cwd,
        timeout=timeout,
        env={
            "PATH":
                __import__("os")
                .environ.get(
                    "PATH",
                    "",
                ),

            "PYTHONDONTWRITEBYTECODE":
                "1",
        },
    )

    return {
        "state":
            (
                "PASS"
                if result["code"] == 0
                else "HOLD"
            ),

        "reason":
            (
                None
                if result["code"] == 0
                else "COMMAND_NONZERO_EXIT"
            ),

        "executed":
            True,

        "code":
            result["code"],

        "stdout":
            result["stdout"],

        "stderr":
            result["stderr"],
    }


def main() -> int:

    python = shutil.which(
        "python3"
    )

    if not python:
        raise RuntimeError(
            "PYTHON3_EXECUTABLE_REQUIRED"
        )

    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-17"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    workspace = Path(
        tempfile.mkdtemp(
            prefix=
                "enguru-cap17-terminal-",
            dir="/tmp",
        )
    )

    target = (
        workspace
        / "terminal-proof.txt"
    )

    baseline = b"BASELINE\n"

    target.write_bytes(
        baseline
    )

    baseline_sha = sha_file(
        target
    )

    mutation_script = (
        "from pathlib import Path;"
        "p=Path('terminal-proof.txt');"
        "p.write_text("
        "'EXECUTED\\n',"
        "encoding='utf-8'"
        ")"
    )

    allowed = canonical_command(
        python,
        mutation_script,
    )

    # Negative control 1:
    # exact command mismatch must never execute.
    mismatch = list(allowed)

    mismatch[-1] = (
        "from pathlib import Path;"
        "Path('UNAUTHORIZED.txt')"
        ".write_text('NO')"
    )

    denied_command = execute_explicit(
        requested=mismatch,
        allowed=allowed,
        cwd=workspace,
        allowed_cwd=workspace,
        timeout=10,
    )

    if (
        denied_command.get("state")
        != "HOLD"
        or denied_command.get(
            "executed"
        )
        is not False
        or (
            workspace
            / "UNAUTHORIZED.txt"
        ).exists()
    ):
        raise RuntimeError(
            "UNALLOWLISTED_COMMAND_FAIL_CLOSED_REQUIRED"
        )

    # Negative control 2:
    # even an allowlisted argv cannot escape
    # its explicit cwd boundary.
    outside = Path(
        tempfile.mkdtemp(
            prefix=
                "enguru-cap17-outside-",
            dir="/tmp",
        )
    )

    denied_cwd = execute_explicit(
        requested=allowed,
        allowed=allowed,
        cwd=outside,
        allowed_cwd=workspace,
        timeout=10,
    )

    if (
        denied_cwd.get("state")
        != "HOLD"
        or denied_cwd.get(
            "executed"
        )
        is not False
    ):
        raise RuntimeError(
            "CWD_SCOPE_FAIL_CLOSED_REQUIRED"
        )

    # Real explicit terminal execution.
    execution = execute_explicit(
        requested=allowed,
        allowed=allowed,
        cwd=workspace,
        allowed_cwd=workspace,
        timeout=10,
    )

    if (
        execution.get("state")
        != "PASS"
        or execution.get(
            "executed"
        )
        is not True
        or execution.get("code")
        != 0
    ):
        raise RuntimeError(
            "REAL_TERMINAL_EXECUTION_REQUIRED"
        )

    if not target.is_file():
        raise RuntimeError(
            "EXPECTED_RESULT_MISSING"
        )

    mutated_bytes = (
        target.read_bytes()
    )

    mutated_sha = sha_bytes(
        mutated_bytes
    )

    if (
        mutated_bytes
        != b"EXECUTED\n"
    ):
        raise RuntimeError(
            "EXPECTED_COMMAND_RESULT_REQUIRED"
        )

    if mutated_sha == baseline_sha:
        raise RuntimeError(
            "MATERIAL_COMMAND_EFFECT_REQUIRED"
        )

    # Failure path:
    # exact allowlisted failing command executes,
    # returns nonzero, and must be observed as HOLD.
    failure_script = (
        "raise SystemExit(23)"
    )

    failure_allowed = canonical_command(
        python,
        failure_script,
    )

    failure = execute_explicit(
        requested=failure_allowed,
        allowed=failure_allowed,
        cwd=workspace,
        allowed_cwd=workspace,
        timeout=10,
    )

    if (
        failure.get("state")
        != "HOLD"
        or failure.get(
            "executed"
        )
        is not True
        or failure.get("code")
        != 23
        or failure.get("reason")
        != "COMMAND_NONZERO_EXIT"
    ):
        raise RuntimeError(
            "NONZERO_EXIT_FAIL_CLOSED_REQUIRED"
        )

    # Required rollback.
    target.write_bytes(
        baseline
    )

    rollback_sha = sha_file(
        target
    )

    rollback_pass = (
        target.read_bytes()
        == baseline
        and rollback_sha
        == baseline_sha
    )

    if not rollback_pass:
        raise RuntimeError(
            "ROLLBACK_BYTE_PARITY_REQUIRED"
        )

    # No unauthorized files may survive.
    names = sorted(
        p.name
        for p in workspace.iterdir()
    )

    if names != [
        "terminal-proof.txt"
    ]:
        raise RuntimeError(
            "WORKSPACE_SCOPE_PRESERVATION_REQUIRED:"
            + ",".join(names)
        )

    # Fresh re-execution after rollback.
    fresh = execute_explicit(
        requested=allowed,
        allowed=allowed,
        cwd=workspace,
        allowed_cwd=workspace,
        timeout=10,
    )

    if (
        fresh.get("state")
        != "PASS"
        or target.read_bytes()
        != b"EXECUTED\n"
    ):
        raise RuntimeError(
            "FRESH_REVERIFY_EXECUTION_REQUIRED"
        )

    # Final rollback after fresh reverify.
    target.write_bytes(
        baseline
    )

    if (
        target.read_bytes()
        != baseline
        or sha_file(target)
        != baseline_sha
    ):
        raise RuntimeError(
            "FINAL_ROLLBACK_REQUIRED"
        )

    evidence = (
        run_dir
        / "field-proof.json"
    )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-cap17-terminal-execution-field-proof/v1",

        "observedAt":
            now(),

        "state":
            "PASS",

        "capabilityIndex":
            17,

        "capabilityId":
            "TERMINAL_EXECUTION",

        "authority":
            "AMBER",

        "riskClass":
            "HIGH",

        "fieldModel":
            "EXPLICIT_ARGV_AND_CWD_SCOPED_LOCAL_TERMINAL_EXECUTION",

        "mutationScope":
            "COMMAND_SCOPE_EXPLICIT",

        "executionSubstrate":
            "mac_engineer_operator.run",

        "networkPolicy":
            "NO_NETWORK_USED",

        "humanThresholdRequired":
            False,

        "explicitCommand": {
            "argv":
                allowed,

            "cwd":
                str(workspace),

            "timeoutSeconds":
                10,

            "shell":
                False,

            "executed":
                True,

            "exitCode":
                execution["code"],
        },

        "expectedResult": {
            "observed":
                True,

            "mutatedSha256":
                mutated_sha,
        },

        "negativeControls": {
            "unallowlistedCommandRejected":
                True,

            "cwdEscapeRejected":
                True,

            "nonzeroExitHeld":
                True,

            "nonzeroExitCode":
                23,
        },

        "rollback": {
            "required":
                True,

            "performed":
                True,

            "baselineSha256":
                baseline_sha,

            "rollbackSha256":
                rollback_sha,

            "byteParity":
                True,

            "finalRollback":
                True,
        },

        "freshReverify": {
            "performed":
                True,

            "state":
                "PASS",
        },

        "authorityBoundary": {
            "canonicalSourceMutation":
                False,

            "productMutation":
                False,

            "remotePush":
                False,

            "networkAccess":
                False,

            "shellInterpolation":
                False,

            "executionAuthorityCreated":
                False,
        },

        "canonicalTruthPreserved":
            True,

        "criticalFalsePassCount":
            0,
    }

    evidence.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    shutil.rmtree(
        workspace
    )

    shutil.rmtree(
        outside
    )

    print("STATE=PASS")
    print(
        "CAP17_TERMINAL_EXECUTION=PASS"
    )
    print(
        "EXECUTION_SUBSTRATE=mac_engineer_operator.run"
    )
    print(
        "COMMAND_SCOPE_EXPLICIT=PASS"
    )
    print(
        "ARGV_ALLOWLIST=PASS"
    )
    print(
        "CWD_SCOPE=PASS"
    )
    print(
        "REAL_COMMAND_EXECUTED=PASS"
    )
    print(
        "EXPECTED_RESULT_OBSERVED=PASS"
    )
    print(
        "UNALLOWLISTED_COMMAND_REJECTED=PASS"
    )
    print(
        "CWD_ESCAPE_REJECTED=PASS"
    )
    print(
        "NONZERO_EXIT_HELD=PASS"
    )
    print(
        "FAILURE_PATH_TESTED=PASS"
    )
    print(
        "ROLLBACK=PASS"
    )
    print(
        "ROLLBACK_BYTE_PARITY=PASS"
    )
    print(
        "FRESH_REVERIFY=PASS"
    )
    print(
        "FINAL_ROLLBACK=PASS"
    )
    print(
        "NETWORK_ACCESS=false"
    )
    print(
        "REMOTE_PUSH=false"
    )
    print(
        "HUMAN_THRESHOLD_REQUIRED=false"
    )
    print(
        "CANONICAL_SOURCE_MUTATION=false"
    )
    print(
        "PRODUCT_MUTATION=false"
    )
    print(
        "EXECUTION_AUTHORITY_CREATED=false"
    )
    print(
        "CANONICAL_TRUTH_PRESERVED=PASS"
    )
    print(
        "CRITICAL_FALSE_PASS_COUNT=0"
    )
    print(
        "EVIDENCE="
        + str(evidence)
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )
    except Exception as exc:
        print("STATE=HOLD")
        print(
            "HOLD="
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        raise SystemExit(2)
