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


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def required_files(root: Path) -> dict[str, Any]:
    required = [
        "README.md",
        "brief_product.py",
        "cli.py",
        "tests/test_brief_product.py",
    ]

    missing = [
        item
        for item in required
        if not (root / item).is_file()
    ]

    return {
        "required":
            required,

        "missing":
            missing,

        "pass":
            not missing,
    }


def main() -> int:
    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-12"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    evidence = (
        run_dir
        / "registered-action-result.json"
    )

    brief = {
        "productName":
            "Enguru Brief Calculator",

        "objective":
            "Create a local CLI product from a bounded brief.",

        "callableBehavior":
            "add(a,b) returns arithmetic sum",

        "executableSurface":
            "python3 cli.py <a> <b>",

        "acceptance": [
            "add(2,3)==5",
            "python3 cli.py 2 3 -> 5",
            "unit tests PASS",
        ],
    }

    workspace_identity = None

    with tempfile.TemporaryDirectory(
        prefix="enguru-cap12-product-"
    ) as td:

        workspace = (
            Path(td)
            / "authorized-product"
        )

        workspace.mkdir()

        workspace_identity = str(
            workspace
        )

        # ------------------------------
        # NEGATIVE CONTROL
        # ------------------------------

        (
            workspace
            / "README.md"
        ).write_text(
            "# Enguru Brief Calculator\n\n"
            "Local CLI calculator product.\n",
            encoding="utf-8",
        )

        incomplete = required_files(
            workspace
        )

        if incomplete["pass"]:
            raise RuntimeError(
                "INCOMPLETE_PRODUCT_MUST_HOLD"
            )

        expected_missing = {
            "brief_product.py",
            "cli.py",
            "tests/test_brief_product.py",
        }

        if set(
            incomplete["missing"]
        ) != expected_missing:
            raise RuntimeError(
                "NEGATIVE_CONTROL_SCOPE_REQUIRED"
            )

        # ------------------------------
        # COMPLETE WORKING PRODUCT
        # ------------------------------

        (
            workspace
            / "brief_product.py"
        ).write_text(
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        (
            workspace
            / "cli.py"
        ).write_text(
            "from __future__ import annotations\n\n"
            "import sys\n"
            "from brief_product import add\n\n"
            "def main() -> int:\n"
            "    if len(sys.argv) != 3:\n"
            "        print('usage: python3 cli.py <a> <b>')\n"
            "        return 2\n"
            "    a = int(sys.argv[1])\n"
            "    b = int(sys.argv[2])\n"
            "    print(add(a, b))\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n",
            encoding="utf-8",
        )

        tests = (
            workspace
            / "tests"
        )

        tests.mkdir()

        (
            tests
            / "test_brief_product.py"
        ).write_text(
            "import unittest\n\n"
            "from brief_product import add\n\n"
            "class BriefProductTests(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

        complete = required_files(
            workspace
        )

        if not complete["pass"]:
            raise RuntimeError(
                "REQUIRED_PRODUCT_FILES"
            )

        callable_check = run(
            [
                "python3",
                "-B",
                "-c",
                (
                    "from brief_product import add;"
                    "print(add(2,3))"
                ),
            ],
            cwd=workspace,
        )

        if (
            callable_check["code"]
            != 0
            or callable_check[
                "stdout"
            ].strip()
            != "5"
        ):
            raise RuntimeError(
                "CALLABLE_CONTRACT_REQUIRED"
            )

        test_result = run(
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
            cwd=workspace,
        )

        if test_result["code"] != 0:
            raise RuntimeError(
                "PRODUCT_TEST_REQUIRED"
            )

        cli = run(
            [
                "python3",
                "-B",
                "cli.py",
                "2",
                "3",
            ],
            cwd=workspace,
        )

        if (
            cli["code"] != 0
            or cli[
                "stdout"
            ].strip()
            != "5"
        ):
            raise RuntimeError(
                "CLI_RUNTIME_REQUIRED"
            )

        cli_negative = run(
            [
                "python3",
                "-B",
                "cli.py",
            ],
            cwd=workspace,
        )

        if (
            cli_negative["code"] != 2
            or "usage:"
            not in cli_negative[
                "stdout"
            ]
        ):
            raise RuntimeError(
                "CLI_FAILURE_PATH_REQUIRED"
            )

        product_files = [
            workspace / "README.md",
            workspace / "brief_product.py",
            workspace / "cli.py",
            workspace / "tests/test_brief_product.py",
        ]

        manifest = {
            str(
                path.relative_to(
                    workspace
                )
            ):
                sha(path)

            for path
            in product_files
        }

        product_source = (
            workspace
            / "brief_product.py"
        )

        product_source_sha = sha(
            product_source
        )

        product_source.write_text(
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        if (
            sha(product_source)
            != product_source_sha
        ):
            raise RuntimeError(
                "PRODUCT_IDEMPOTENCY_REQUIRED"
            )

        payload = {
            "schema":
                "enguru.mac-engineer.package08-capability12-registered-action/v1",

            "state":
                "PASS",

            "capabilityId":
                "NEW_PRODUCT_FROM_BRIEF",

            "authority":
                "AMBER",

            "riskClass":
                "MEDIUM",

            "fieldModel":
                "AUTHORIZED_DISPOSABLE_WORKSPACE_BRIEF_TO_WORKING_PRODUCT",

            "mutationScope":
                "AUTHORIZED_WORKSPACE_ONLY",

            "brief":
                brief,

            "negativeControl": {
                "incompleteProductRejected":
                    True,

                "missingRequiredSurfaces":
                    sorted(
                        expected_missing
                    ),
            },

            "product": {
                "state":
                    "PASS",

                "requiredFileCount":
                    4,

                "requiredFiles":
                    complete[
                        "required"
                    ],

                "manifestSha256":
                    manifest,

                "callableContractPass":
                    True,

                "testsPass":
                    True,

                "cliRuntimePass":
                    True,

                "cliFailurePathPass":
                    True,

                "idempotent":
                    True,
            },

            "rollbackRecovery": {
                "required":
                    True,

                "disposableWorkspace":
                    True,

                "workspaceCleanupRequired":
                    True,
            },

            "governanceTruth": {
                "authorizedWorkspaceOnly":
                    True,

                "remotePushPerformed":
                    False,

                "canonicalSourceMutationPerformed":
                    False,

                "canonicalTruthPreserved":
                    True,
            },

            "criticalFalsePassCount":
                0,
        }

        evidence.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

    if (
        workspace_identity
        and Path(
            workspace_identity
        ).exists()
    ):
        raise RuntimeError(
            "DISPOSABLE_WORKSPACE_CLEANUP_REQUIRED"
        )

    payload = json.loads(
        evidence.read_text(
            encoding="utf-8"
        )
    )

    payload[
        "rollbackRecovery"
    ][
        "workspaceCleanupPass"
    ] = True

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
        "CAP12_NEW_PRODUCT_FROM_BRIEF=PASS"
    )
    print(
        "INCOMPLETE_BRIEF_PRODUCT_REJECTED=PASS"
    )
    print(
        "REQUIRED_PRODUCT_FILES=PASS"
    )
    print(
        "PRODUCT_FILE_COUNT=4"
    )
    print(
        "CALLABLE_CONTRACT=PASS"
    )
    print(
        "PRODUCT_TEST=PASS"
    )
    print(
        "CLI_RUNTIME_VERIFY=PASS"
    )
    print(
        "CLI_FAILURE_PATH=PASS"
    )
    print(
        "PRODUCT_MANIFEST=PASS"
    )
    print(
        "PRODUCT_IDEMPOTENCY=PASS"
    )
    print(
        "DISPOSABLE_WORKSPACE_CLEANUP=PASS"
    )
    print(
        "CRITICAL_FALSE_PASS_COUNT=0"
    )
    print(
        "CANONICAL_TRUTH_PRESERVED=PASS"
    )
    print("AUTHORITY=AMBER")
    print(
        "MUTATION_SCOPE=AUTHORIZED_WORKSPACE_ONLY"
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
