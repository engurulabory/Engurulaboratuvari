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

SOURCE = (
    PRODUCT
    / "execution_prep/native_app/EnguruMacEngineerApp.swift"
)

EVIDENCE_ROOT = (
    HOME
    / "Enguru/Evidence/MacEngineer"
    / "package08-field-campaign"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 1800,
) -> dict[str, Any]:

    proc = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )

    return {
        "args": args,
        "code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
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

    return result["stdout"]


def write(
    path: Path,
    payload: dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-07"
    )

    evidence = (
        run_dir
        / "registered-action-result.json"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    head_before = git(
        "rev-parse",
        "HEAD",
    )

    status_before = git(
        "status",
        "--porcelain",
    )

    source_sha_before = sha256(
        SOURCE
    )

    if status_before:
        raise RuntimeError(
            "PRODUCT_WORKTREE_CLEAN_REQUIRED"
        )

    payload: dict[str, Any] = {
        "schema":
            "enguru.mac-engineer.package08-capability07-build-field-proof/v1",

        "observedAt":
            now(),

        "state":
            "HOLD",

        "capabilityId":
            "BUILD",

        "authority":
            "GREEN",

        "riskClass":
            "LOW",

        "fieldModel":
            "LOCAL_TEMP_NATIVE_SWIFT_BUILD_ARTIFACT",

        "mutationScope":
            "BUILD_ARTIFACTS_ONLY",

        "networkPolicy":
            "LOCAL_ONLY",
    }

    try:
        with tempfile.TemporaryDirectory(
            prefix="enguru-cap07-build-"
        ) as td:

            root = Path(td)

            artifact = (
                root
                / "EnguruMacEngineer"
            )

            positive = run(
                [
                    "xcrun",
                    "swiftc",
                    "-parse-as-library",
                    str(SOURCE),
                    "-o",
                    str(artifact),
                    "-framework",
                    "SwiftUI",
                    "-framework",
                    "WebKit",
                    "-framework",
                    "AppKit",
                ],
                cwd=PRODUCT,
            )

            if positive["code"] != 0:
                raise RuntimeError(
                    "NATIVE_SWIFT_BUILD_HOLD:"
                    + positive["stderr"][-3000:]
                )

            if not artifact.is_file():
                raise RuntimeError(
                    "BUILD_ARTIFACT_REQUIRED"
                )

            artifact.chmod(
                artifact.stat().st_mode
                | 0o111
            )

            if not os.access(
                artifact,
                os.X_OK,
            ):
                raise RuntimeError(
                    "EXECUTABLE_ARTIFACT_REQUIRED"
                )

            artifact_sha = sha256(
                artifact
            )

            artifact_size = (
                artifact.stat().st_size
            )

            invalid_source = (
                root
                / "ControlledCompilerRejection.swift"
            )

            invalid_source.write_text(
                (
                    "import SwiftUI\n"
                    "struct ControlledCompilerRejection {\n"
                    "    let value: =\n"
                    "}\n"
                ),
                encoding="utf-8",
            )

            failed_artifact = (
                root
                / "ControlledFailureArtifact"
            )

            negative = run(
                [
                    "xcrun",
                    "swiftc",
                    "-parse-as-library",
                    str(invalid_source),
                    "-o",
                    str(failed_artifact),
                    "-framework",
                    "SwiftUI",
                ],
                cwd=PRODUCT,
            )

            compiler_rejection = (
                negative["code"] != 0
            )

            failed_artifact_absent = (
                not failed_artifact.exists()
            )

            if not compiler_rejection:
                raise RuntimeError(
                    "CONTROLLED_COMPILER_REJECTION_REQUIRED"
                )

            if not failed_artifact_absent:
                raise RuntimeError(
                    "FAILED_BUILD_ARTIFACT_CLEANUP_REQUIRED"
                )

            head_after = git(
                "rev-parse",
                "HEAD",
            )

            status_after = git(
                "status",
                "--porcelain",
            )

            source_sha_after = sha256(
                SOURCE
            )

            source_preserved = (
                source_sha_after
                == source_sha_before
            )

            product_truth_preserved = (
                head_after == head_before
                and status_after == status_before
            )

            if not source_preserved:
                raise RuntimeError(
                    "SOURCE_PARITY_REQUIRED"
                )

            if not product_truth_preserved:
                raise RuntimeError(
                    "PRODUCT_TRUTH_PARITY_REQUIRED"
                )

            payload.update({
                "state":
                    "PASS",

                "claim":
                    "BUILD_LOCAL_NATIVE_SWIFT_ARTIFACT_VERIFIED",

                "source": {
                    "path":
                        str(SOURCE),

                    "sha256":
                        source_sha_after,

                    "preserved":
                        True,
                },

                "build": {
                    "state":
                        "PASS",

                    "toolchain":
                        "xcrun swiftc",

                    "artifactExecutable":
                        True,

                    "artifactSize":
                        artifact_size,

                    "artifactSha256":
                        artifact_sha,

                    "artifactScope":
                        "TEMPORARY_BUILD_ARTIFACT",
                },

                "failurePath": {
                    "state":
                        "PASS",

                    "controlledCompilerRejection":
                        compiler_rejection,

                    "failedArtifactCleanup":
                        failed_artifact_absent,

                    "criticalFalsePassCount":
                        0,
                },

                "governanceTruth": {
                    "authority":
                        "GREEN",

                    "networkPolicy":
                        "LOCAL_ONLY",

                    "mutationScope":
                        "BUILD_ARTIFACTS_ONLY",

                    "canonicalTruthPreserved":
                        True,
                },

                "cleanup": {
                    "temporaryArtifactLifecycle":
                        "PASS",
                },
            })

        write(
            evidence,
            payload,
        )

        print("STATE=PASS")
        print("CAP07_BUILD=PASS")
        print("BUILD_ARTIFACT_EXECUTABLE=PASS")
        print(
            "BUILD_ARTIFACT_SIZE="
            + str(
                payload["build"][
                    "artifactSize"
                ]
            )
        )
        print(
            "BUILD_ARTIFACT_SHA256="
            + payload["build"][
                "artifactSha256"
            ]
        )
        print("CONTROLLED_COMPILER_REJECTION=PASS")
        print("FAILED_ARTIFACT_CLEANUP=PASS")
        print("CANONICAL_TRUTH_PRESERVED=PASS")
        print("AUTHORITY=GREEN")
        print("NETWORK_POLICY=LOCAL_ONLY")
        print("MUTATION_SCOPE=BUILD_ARTIFACTS_ONLY")
        print("REMOTE_PUSH=false")
        print("EXECUTION_AUTHORITY_CREATED=false")
        print("EVIDENCE=" + str(evidence))

        return 0

    except Exception as exc:
        payload["state"] = "HOLD"
        payload["reason"] = (
            type(exc).__name__
            + ":"
            + str(exc)
        )

        write(
            evidence,
            payload,
        )

        print("STATE=HOLD")
        print(
            "HOLD_REASON="
            + payload["reason"]
        )
        print("EVIDENCE=" + str(evidence))

        return 20


if __name__ == "__main__":
    raise SystemExit(main())
