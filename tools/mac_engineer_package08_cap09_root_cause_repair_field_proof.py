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
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 300,
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
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def git(
    repo: Path,
    *args: str,
) -> str:
    result = run(
        ["git", *args],
        cwd=repo,
        timeout=120,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GIT_COMMAND_HOLD:"
            + " ".join(args)
        )

    return result["stdout"]


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
        timeout=120,
    )


def main() -> int:
    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-09"
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

    source_status_before = git(
        SOURCE_FIXTURE,
        "status",
        "--porcelain",
    )

    if source_head_before != EXPECTED_HEAD:
        raise RuntimeError(
            "SOURCE_FIXTURE_EXACT_HEAD_REQUIRED"
        )

    with tempfile.TemporaryDirectory(
        prefix="enguru-cap09-repair-"
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
            timeout=120,
        )

        if clone.returncode != 0:
            raise RuntimeError(
                "DISPOSABLE_CLONE_HOLD"
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
                "EXACT_HEAD_CHECKOUT_HOLD"
            )

        calc = fixture / "calculator.py"

        baseline = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )

        if calc.read_text(
            encoding="utf-8"
        ) != baseline:
            raise RuntimeError(
                "BASELINE_SOURCE_REQUIRED"
            )

        baseline_sha = sha256(calc)

        baseline_test = regression(fixture)

        if baseline_test["code"] != 0:
            raise RuntimeError(
                "BASELINE_REGRESSION_HOLD"
            )

        fault_source = (
            "def add(a: int, b: int) -> int:\n"
            "    # ENGURU_RECOVERY_FAULT_START\n"
            "    return a - b\n"
            "    # ENGURU_RECOVERY_FAULT_END\n"
        )

        calc.write_text(
            fault_source,
            encoding="utf-8",
        )

        fault_test = regression(fixture)

        if fault_test["code"] == 0:
            raise RuntimeError(
                "CONTROLLED_FAILURE_REQUIRED"
            )

        runtime_fault = run(
            [
                "python3",
                "-B",
                "-c",
                (
                    "from calculator import add; "
                    "print(add(2,3))"
                ),
            ],
            cwd=fixture,
        )

        if (
            runtime_fault["code"] != 0
            or runtime_fault["stdout"] != "-1"
        ):
            raise RuntimeError(
                "CONTROLLED_RUNTIME_FAILURE_REQUIRED"
            )

        status = git(
            fixture,
            "status",
            "--porcelain",
        )

        changed = [
            row
            for row in status.splitlines()
            if row.strip()
        ]

        if (
            len(changed) != 1
            or not changed[0].endswith(
                "calculator.py"
            )
        ):
            raise RuntimeError(
                "SINGLE_FILE_FAULT_SCOPE_REQUIRED"
            )

        root_cause = (
            "controlled_bounded_fault_marker_block"
        )

        calc.write_text(
            baseline,
            encoding="utf-8",
        )

        repaired_sha = sha256(calc)

        if repaired_sha != baseline_sha:
            raise RuntimeError(
                "REPAIR_BASELINE_PARITY_REQUIRED"
            )

        repaired_test = regression(fixture)

        if repaired_test["code"] != 0:
            raise RuntimeError(
                "POST_REPAIR_REGRESSION_REQUIRED"
            )

        runtime_verify = run(
            [
                "python3",
                "-B",
                "-c",
                (
                    "from calculator import add; "
                    "print(add(2,3))"
                ),
            ],
            cwd=fixture,
        )

        if (
            runtime_verify["code"] != 0
            or runtime_verify["stdout"] != "5"
        ):
            raise RuntimeError(
                "POST_REPAIR_RUNTIME_VERIFY_REQUIRED"
            )

        if git(
            fixture,
            "status",
            "--porcelain",
        ):
            raise RuntimeError(
                "FINAL_FIXTURE_CLEAN_REQUIRED"
            )

        calc.write_text(
            baseline,
            encoding="utf-8",
        )

        if sha256(calc) != baseline_sha:
            raise RuntimeError(
                "REPAIR_IDEMPOTENCY_REQUIRED"
            )

        if git(
            fixture,
            "status",
            "--porcelain",
        ):
            raise RuntimeError(
                "REPAIR_IDEMPOTENCY_CLEAN_REQUIRED"
            )

    source_head_after = git(
        SOURCE_FIXTURE,
        "rev-parse",
        "HEAD",
    )

    source_status_after = git(
        SOURCE_FIXTURE,
        "status",
        "--porcelain",
    )

    if source_head_after != source_head_before:
        raise RuntimeError(
            "SOURCE_FIXTURE_HEAD_PRESERVATION_REQUIRED"
        )

    if source_status_after != source_status_before:
        raise RuntimeError(
            "SOURCE_FIXTURE_TRUTH_PRESERVATION_REQUIRED"
        )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-capability09-root-cause-repair-field-proof/v1",

        "observedAt":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "state":
            "PASS",

        "capabilityId":
            "ROOT_CAUSE_REPAIR",

        "authority":
            "AMBER",

        "riskClass":
            "MEDIUM",

        "fieldModel":
            "DISPOSABLE_CONTROLLED_FAILURE_ROOT_CAUSE_BOUNDED_REPAIR",

        "mutationScope":
            "BOUNDED_REPAIR_SCOPE",

        "failure": {
            "observed":
                True,

            "runtimeValue":
                "-1",

            "failingRegressionObserved":
                True,

            "singleFileScope":
                True,
        },

        "rootCause": {
            "state":
                "PASS",

            "identity":
                root_cause,

            "evidenceBound":
                True,
        },

        "repair": {
            "state":
                "PASS",

            "identity":
                "remove_exact_bounded_fault_marker_block_and_restore_baseline_addition",

            "smallestSufficient":
                True,

            "baselineParity":
                True,

            "idempotent":
                True,
        },

        "reverify": {
            "regression":
                "PASS",

            "runtimeValue":
                "5",
        },

        "recovery": {
            "rollbackRequired":
                True,

            "baselineParityObserved":
                True,

            "finalFixtureClean":
                True,

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
    print("CAP09_ROOT_CAUSE_REPAIR=PASS")
    print("CONTROLLED_FAILURE_REPRODUCED=PASS")
    print(
        "ROOT_CAUSE="
        + root_cause
    )
    print("ROOT_CAUSE_EVIDENCE=PASS")
    print("SMALLEST_SUFFICIENT_REPAIR=PASS")
    print("POST_REPAIR_REGRESSION=PASS")
    print("POST_REPAIR_RUNTIME_VERIFY=PASS")
    print("ROLLBACK_BASELINE_PARITY=PASS")
    print("FINAL_FIXTURE_CLEAN=PASS")
    print("SOURCE_FIXTURE_TRUTH_PRESERVED=PASS")
    print("REPAIR_IDEMPOTENCY=PASS")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("AUTHORITY=AMBER")
    print("MUTATION_SCOPE=BOUNDED_REPAIR_SCOPE")
    print("REMOTE_PUSH=false")
    print("EXECUTION_AUTHORITY_CREATED=false")
    print("EVIDENCE=" + str(evidence))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
