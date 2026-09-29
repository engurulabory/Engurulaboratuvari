#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
PRODUCT = HOME / "Enguru/Projects/enguru-mac-engineer"

EVIDENCE_ROOT = (
    HOME
    / "Enguru/Evidence/MacEngineer"
    / "package08-field-campaign"
)


def stamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )


def digest_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 3600,
) -> dict[str, Any]:
    p = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        timeout=timeout,
    )

    return {
        "code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def git(*args: str) -> str:
    result = run(
        ["git", *args],
        cwd=PRODUCT,
        timeout=120,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GIT_COMMAND_HOLD:"
            + " ".join(args)
        )

    return result["stdout"].strip()


def main() -> int:
    evidence_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-08"
    )

    evidence_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    evidence = (
        evidence_dir
        / "registered-action-result.json"
    )

    head_before = git(
        "rev-parse",
        "HEAD",
    )

    status_before = git(
        "status",
        "--porcelain",
    )

    if status_before:
        raise RuntimeError(
            "PRODUCT_WORKTREE_CLEAN_REQUIRED"
        )

    env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(
            PRODUCT / "runtime"
        ),
    }

    targeted = run(
        [
            "python3",
            "-m",
            "unittest",
            "-v",
            "runtime.tests.test_v08_existing_product_change",
        ],
        cwd=PRODUCT,
        env=env,
    )

    if targeted["code"] != 0:
        raise RuntimeError(
            "TARGETED_REGRESSION_HOLD"
        )

    full = run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "runtime/tests",
            "-v",
        ],
        cwd=PRODUCT,
        env=env,
    )

    if full["code"] != 0:
        raise RuntimeError(
            "FULL_RUNTIME_REGRESSION_HOLD"
        )

    with tempfile.TemporaryDirectory(
        prefix="enguru-cap08-"
    ) as td:
        root = Path(td)

        failing_test = (
            root
            / "test_controlled_failure.py"
        )

        failing_test.write_text(
            (
                "import unittest\n\n"
                "class ControlledFailure(unittest.TestCase):\n"
                "    def test_detection(self):\n"
                "        self.assertEqual(1, 2)\n"
            ),
            encoding="utf-8",
        )

        negative = run(
            [
                "python3",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(root),
                "-p",
                "test_*.py",
                "-v",
            ],
            cwd=root,
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            timeout=120,
        )

        failure_detected = (
            negative["code"] != 0
        )

        if not failure_detected:
            raise RuntimeError(
                "CONTROLLED_FAILURE_DETECTION_REQUIRED"
            )

    head_after = git(
        "rev-parse",
        "HEAD",
    )

    status_after = git(
        "status",
        "--porcelain",
    )

    if (
        head_after != head_before
        or status_after != status_before
    ):
        raise RuntimeError(
            "CANONICAL_TRUTH_PARITY_REQUIRED"
        )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-capability08-test-regression-field-proof/v1",

        "observedAt":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "state":
            "PASS",

        "claim":
            "TEST_REGRESSION_GREEN_LOCAL_FIELD_VERIFIED_CANDIDATE",

        "capabilityId":
            "TEST_REGRESSION",

        "authority":
            "GREEN",

        "riskClass":
            "LOW",

        "fieldModel":
            "LOCAL_TARGETED_FULL_REGRESSION_WITH_CONTROLLED_FAILURE",

        "mutationScope":
            "TEST_ARTIFACTS_ONLY",

        "networkPolicy":
            "LOCAL_ONLY",

        "targetedRegression": {
            "state":
                "PASS",

            "stdoutSha256":
                digest_text(
                    targeted["stdout"]
                ),

            "stderrSha256":
                digest_text(
                    targeted["stderr"]
                ),
        },

        "fullRegression": {
            "state":
                "PASS",

            "stdoutSha256":
                digest_text(
                    full["stdout"]
                ),

            "stderrSha256":
                digest_text(
                    full["stderr"]
                ),
        },

        "failurePath": {
            "state":
                "PASS",

            "controlledFailingTest":
                True,

            "failureDetected":
                True,

            "criticalFalsePassCount":
                0,
        },

        "governanceTruth": {
            "canonicalTruthPreserved":
                True,

            "authority":
                "GREEN",

            "networkPolicy":
                "LOCAL_ONLY",

            "mutationScope":
                "TEST_ARTIFACTS_ONLY",
        },
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
    print("CAP08_TEST_REGRESSION=PASS")
    print("TARGETED_REGRESSION=PASS")
    print("FULL_RUNTIME_REGRESSION=PASS")
    print("CONTROLLED_TEST_FAILURE_DETECTED=PASS")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("AUTHORITY=GREEN")
    print("NETWORK_POLICY=LOCAL_ONLY")
    print("MUTATION_SCOPE=TEST_ARTIFACTS_ONLY")
    print("REMOTE_PUSH=false")
    print("EXECUTION_AUTHORITY_CREATED=false")
    print("EVIDENCE=" + str(evidence))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
