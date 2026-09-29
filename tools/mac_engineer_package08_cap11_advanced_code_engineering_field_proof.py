#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()

SOURCE_FIXTURE = (
    HOME
    / "Enguru/Projects/mac-engineering-v06-field-fixture"
)

EXPECTED_HEAD = (
    "f563a779f6d01a46e037e4330383c3adb032d426"
)

EVIDENCE_ROOT = (
    HOME
    / "Enguru/Evidence/MacEngineer"
    / "package08-field-campaign"
)


def stamp() -> str:
    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )


def run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 180,
) -> dict[str, Any]:
    p = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )

    return {
        "code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def git_raw(
    repo: Path,
    *args: str,
) -> str:
    result = run(
        ["git", *args],
        cwd=repo,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GIT_COMMAND_HOLD:"
            + " ".join(args)
        )

    return result["stdout"]


def git(
    repo: Path,
    *args: str,
) -> str:
    return git_raw(
        repo,
        *args,
    ).strip()


def changed_paths(repo: Path) -> list[str]:
    tracked = [
        row
        for row in git_raw(
            repo,
            "diff",
            "--name-only",
        ).splitlines()
        if row
    ]

    untracked = [
        row
        for row in git_raw(
            repo,
            "ls-files",
            "--others",
            "--exclude-standard",
        ).splitlines()
        if row
    ]

    return sorted(
        set(tracked + untracked)
    )


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def regression(repo: Path) -> dict[str, Any]:
    return run(
        [
            "python3",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        cwd=repo,
    )


def main() -> int:
    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-11"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    evidence = (
        run_dir
        / "registered-action-result.json"
    )

    source_head_before = git(
        SOURCE_FIXTURE,
        "rev-parse",
        "HEAD",
    )

    source_status_before = git_raw(
        SOURCE_FIXTURE,
        "status",
        "--porcelain",
    )

    if source_head_before != EXPECTED_HEAD:
        raise RuntimeError(
            "SOURCE_FIXTURE_EXACT_HEAD_REQUIRED"
        )

    with tempfile.TemporaryDirectory(
        prefix="enguru-cap11-engineering-"
    ) as td:

        fixture = Path(td) / "fixture"

        clone = subprocess.run(
            [
                "git",
                "clone",
                "--no-hardlinks",
                "--no-checkout",
                str(SOURCE_FIXTURE),
                str(fixture),
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )

        if clone.returncode != 0:
            raise RuntimeError(
                "DISPOSABLE_CLONE_REQUIRED"
            )

        checkout = run(
            [
                "git",
                "checkout",
                "--detach",
                EXPECTED_HEAD,
            ],
            cwd=fixture,
        )

        if checkout["code"] != 0:
            raise RuntimeError(
                "EXACT_HEAD_CHECKOUT_REQUIRED"
            )

        if git_raw(
            fixture,
            "status",
            "--porcelain",
        ):
            raise RuntimeError(
                "BASELINE_CLEAN_REQUIRED"
            )

        calc = fixture / "calculator.py"
        ops = fixture / "operations.py"

        baseline = calc.read_text(
            encoding="utf-8"
        )

        baseline_sha = sha(calc)

        baseline_regression = regression(
            fixture
        )

        if (
            baseline_regression["code"]
            != 0
        ):
            raise RuntimeError(
                "BASELINE_REGRESSION_REQUIRED"
            )

        engineered_calc = (
            "from operations import apply_addition\n\n"
            "def add(a: int, b: int) -> int:\n"
            "    return apply_addition(a, b)\n"
        )

        calc.write_text(
            engineered_calc,
            encoding="utf-8",
        )

        incomplete = regression(
            fixture
        )

        if incomplete["code"] == 0:
            raise RuntimeError(
                "INCOMPLETE_CHANGE_MUST_FAIL"
            )

        if changed_paths(
            fixture
        ) != [
            "calculator.py",
        ]:
            raise RuntimeError(
                "INCOMPLETE_SCOPE_REQUIRED"
            )

        operations_source = (
            "def apply_addition(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )

        ops.write_text(
            operations_source,
            encoding="utf-8",
        )

        if changed_paths(
            fixture
        ) != [
            "calculator.py",
            "operations.py",
        ]:
            raise RuntimeError(
                "EXACT_ENGINEERING_SCOPE_REQUIRED"
            )

        targeted = run(
            [
                "python3",
                "-B",
                "-m",
                "unittest",
                "-v",
                "tests.test_calculator",
            ],
            cwd=fixture,
        )

        if targeted["code"] != 0:
            raise RuntimeError(
                "TARGETED_REGRESSION_REQUIRED"
            )

        full = regression(
            fixture
        )

        if full["code"] != 0:
            raise RuntimeError(
                "FULL_REGRESSION_REQUIRED"
            )

        public = run(
            [
                "python3",
                "-B",
                "-c",
                "from calculator import add; print(add(2,3))",
            ],
            cwd=fixture,
        )

        if (
            public["code"] != 0
            or public["stdout"].strip()
            != "5"
        ):
            raise RuntimeError(
                "PUBLIC_CONTRACT_REQUIRED"
            )

        internal = run(
            [
                "python3",
                "-B",
                "-c",
                (
                    "from operations import apply_addition;"
                    "print(apply_addition(7,8))"
                ),
            ],
            cwd=fixture,
        )

        if (
            internal["code"] != 0
            or internal["stdout"].strip()
            != "15"
        ):
            raise RuntimeError(
                "INTERNAL_ABSTRACTION_REQUIRED"
            )

        calc_engineered_sha = sha(
            calc
        )

        ops_engineered_sha = sha(
            ops
        )

        calc.write_text(
            engineered_calc,
            encoding="utf-8",
        )

        ops.write_text(
            operations_source,
            encoding="utf-8",
        )

        if (
            sha(calc)
            != calc_engineered_sha
            or sha(ops)
            != ops_engineered_sha
        ):
            raise RuntimeError(
                "IDEMPOTENCY_REQUIRED"
            )

        calc.write_text(
            baseline,
            encoding="utf-8",
        )

        ops.unlink()

        if sha(calc) != baseline_sha:
            raise RuntimeError(
                "ROLLBACK_BYTE_PARITY_REQUIRED"
            )

        if changed_paths(fixture):
            raise RuntimeError(
                "ROLLBACK_SCOPE_CLEAN_REQUIRED"
            )

        if git_raw(
            fixture,
            "status",
            "--porcelain",
        ):
            raise RuntimeError(
                "ROLLBACK_WORKTREE_CLEAN_REQUIRED"
            )

        rollback_regression = regression(
            fixture
        )

        if (
            rollback_regression["code"]
            != 0
        ):
            raise RuntimeError(
                "ROLLBACK_REGRESSION_REQUIRED"
            )

    source_head_after = git(
        SOURCE_FIXTURE,
        "rev-parse",
        "HEAD",
    )

    source_status_after = git_raw(
        SOURCE_FIXTURE,
        "status",
        "--porcelain",
    )

    if (
        source_head_after
        != source_head_before
    ):
        raise RuntimeError(
            "SOURCE_FIXTURE_HEAD_PRESERVATION_REQUIRED"
        )

    if (
        source_status_after
        != source_status_before
    ):
        raise RuntimeError(
            "SOURCE_FIXTURE_TRUTH_PRESERVATION_REQUIRED"
        )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-capability11-registered-action/v1",

        "state":
            "PASS",

        "capabilityId":
            "ADVANCED_CODE_ENGINEERING",

        "authority":
            "AMBER",

        "riskClass":
            "MEDIUM",

        "fieldModel":
            "DISPOSABLE_MULTI_FILE_ENGINEERING_WITH_REGRESSION_AND_ROLLBACK",

        "mutationScope":
            "EXPLICIT_ENGINEERING_SCOPE",

        "negativeControl": {
            "incompleteChangeFailed":
                True,

            "singleFilePrecompleteScope":
                True,
        },

        "engineeringChange": {
            "changedFileCount":
                2,

            "changedFiles": [
                "calculator.py",
                "operations.py",
            ],

            "targetedRegression":
                "PASS",

            "fullRegression":
                "PASS",

            "publicBehaviorPreserved":
                True,

            "internalAbstractionVerified":
                True,

            "idempotent":
                True,
        },

        "rollbackRecovery": {
            "required":
                True,

            "byteParity":
                True,

            "worktreeClean":
                True,

            "regression":
                "PASS",

            "sourceFixtureTruthPreserved":
                True,
        },

        "criticalFalsePassCount":
            0,

        "canonicalTruthPreserved":
            True,
    }

    evidence.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("STATE=PASS")
    print(
        "CAP11_ADVANCED_CODE_ENGINEERING=PASS"
    )
    print(
        "INCOMPLETE_MULTI_FILE_CHANGE_FAILURE=PASS"
    )
    print(
        "MULTI_FILE_SCOPE=PASS"
    )
    print(
        "CHANGED_FILE_COUNT=2"
    )
    print(
        "TARGETED_REGRESSION=PASS"
    )
    print(
        "FULL_REGRESSION=PASS"
    )
    print(
        "PUBLIC_ADD_BEHAVIOR_PRESERVED=PASS"
    )
    print(
        "INTERNAL_OPERATION_ABSTRACTION=PASS"
    )
    print(
        "ENGINEERING_IDEMPOTENCY=PASS"
    )
    print(
        "ROLLBACK_BYTE_PARITY=PASS"
    )
    print(
        "ROLLBACK_WORKTREE_CLEAN=PASS"
    )
    print(
        "ROLLBACK_REGRESSION=PASS"
    )
    print(
        "SOURCE_FIXTURE_TRUTH_PRESERVED=PASS"
    )
    print(
        "CRITICAL_FALSE_PASS_COUNT=0"
    )
    print(
        "CANONICAL_TRUTH_PRESERVED=PASS"
    )
    print("AUTHORITY=AMBER")
    print(
        "MUTATION_SCOPE=EXPLICIT_ENGINEERING_SCOPE"
    )
    print("REMOTE_PUSH=false")
    print(
        "EXECUTION_AUTHORITY_CREATED=false"
    )
    print(
        "EVIDENCE="
        + str(evidence)
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("STATE=HOLD")
        print(
            "HOLD="
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        raise SystemExit(2)
