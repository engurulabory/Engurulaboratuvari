#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
PRODUCT = HOME / "Enguru/Projects/enguru-mac-engineer"

GATE6_TOOL = (
    CONTROL
    / "tools/mac_engineer_v08_existing_product_change.py"
)

BASELINE = "8bd62a2bd8c288b07d51f78ab2164444962bf7c4"

EVIDENCE_ROOT = (
    HOME
    / "Enguru/Evidence/MacEngineer"
    / "package08-field-campaign"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 3600,
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


def git(repo: Path, *args: str) -> str:
    result = run(
        ["git", *args],
        cwd=repo,
        timeout=300,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GIT_FAILED:"
            + " ".join(args)
            + ":"
            + (
                result["stderr"]
                or result["stdout"]
            )[-1600:]
        )

    return result["stdout"]


def sha_file(path: Path) -> str | None:
    if not path.exists():
        return None

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


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


def load_gate6():
    spec = importlib.util.spec_from_file_location(
        "package08_cap06_gate6",
        GATE6_TOOL,
    )

    if not spec or not spec.loader:
        raise RuntimeError(
            "GATE6_MODULE_LOAD_REQUIRED"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


def main() -> int:
    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-06"
    )

    evidence = (
        run_dir
        / "registered-action-result.json"
    )

    control_head_before = git(
        CONTROL,
        "rev-parse",
        "HEAD",
    )

    control_status_before = git(
        CONTROL,
        "status",
        "--porcelain",
    )

    product_head_before = git(
        PRODUCT,
        "rev-parse",
        "HEAD",
    )

    product_status_before = git(
        PRODUCT,
        "status",
        "--porcelain",
    )

    if product_status_before:
        raise RuntimeError(
            "CANONICAL_PRODUCT_WORKTREE_NOT_CLEAN"
        )

    gate6 = load_gate6()

    authorized = tuple(
        gate6.AUTHORIZED_PATHS
    )

    expected_authorized = (
        "runtime/static/index.html",
        "runtime/tests/test_v08_existing_product_change.py",
    )

    if authorized != expected_authorized:
        raise RuntimeError(
            "AUTHORIZED_PATH_CONTRACT_DRIFT"
        )

    payload: dict[str, Any] = {
        "schema":
            "enguru.mac-engineer.package08-cap06-registered-field-proof/v1",

        "observedAt":
            utc_now(),

        "state":
            "HOLD",

        "claim":
            "SOURCE_PRODUCT_CHANGE_FIELD_PROOF_INCOMPLETE",

        "capabilityId":
            "SOURCE_PRODUCT_CHANGE",

        "authority":
            "AMBER",

        "fieldModel":
            "DISPOSABLE_EXACT_BASELINE_BOUNDED_SOURCE_MUTATION",

        "authorizedMutationPaths":
            list(authorized),

        "authorizedMutationPathCount":
            len(authorized),

        "networkRequired":
            False,

        "remotePush":
            False,

        "canonicalControlHeadBefore":
            control_head_before,

        "canonicalProductHeadBefore":
            product_head_before,
    }

    try:
        with tempfile.TemporaryDirectory(
            prefix="enguru-cap06-"
        ) as td:
            fixture = Path(td) / "product"

            clone = run(
                [
                    "git",
                    "clone",
                    "--no-hardlinks",
                    "--no-checkout",
                    str(PRODUCT),
                    str(fixture),
                ],
                cwd=Path(td),
            )

            if clone["code"] != 0:
                raise RuntimeError(
                    "FIXTURE_CLONE_FAILED:"
                    + (
                        clone["stderr"]
                        or clone["stdout"]
                    )[-1600:]
                )

            checkout = run(
                [
                    "git",
                    "checkout",
                    "--detach",
                    BASELINE,
                ],
                cwd=fixture,
            )

            if checkout["code"] != 0:
                raise RuntimeError(
                    "FIXTURE_CHECKOUT_FAILED:"
                    + (
                        checkout["stderr"]
                        or checkout["stdout"]
                    )[-1600:]
                )

            if git(
                fixture,
                "rev-parse",
                "HEAD",
            ) != BASELINE:
                raise RuntimeError(
                    "FIXTURE_BASELINE_MISMATCH"
                )

            if git(
                fixture,
                "status",
                "--porcelain",
            ):
                raise RuntimeError(
                    "FIXTURE_NOT_CLEAN"
                )

            def fixture_git(
                *args: str,
            ) -> str:
                return git(
                    fixture,
                    *args,
                )

            gate6.PRODUCT = fixture
            gate6.git = fixture_git

            preimage: dict[str, Any] = {}

            for rel in authorized:
                path = fixture / rel

                preimage[rel] = {
                    "exists":
                        path.exists(),

                    "sha256":
                        sha_file(path),
                }

            if (
                preimage[
                    authorized[0]
                ]["exists"]
                is not True
            ):
                raise RuntimeError(
                    "INDEX_PREIMAGE_REQUIRED"
                )

            if (
                preimage[
                    authorized[1]
                ]["exists"]
                is not False
            ):
                raise RuntimeError(
                    "GENERATED_TEST_MUST_BE_ABSENT"
                )

            backups = gate6.backup_sources(
                run_dir
            )

            if authorized[0] not in backups:
                raise RuntimeError(
                    "INDEX_BACKUP_REQUIRED"
                )

            if authorized[1] in backups:
                raise RuntimeError(
                    "ABSENT_TEST_BACKUP_FORBIDDEN"
                )

            mutation_started = False

            try:
                gate6.apply_product_change()
                mutation_started = True

                scope = (
                    gate6.verify_worktree_scope()
                )

                if scope != sorted(authorized):
                    raise RuntimeError(
                        "SOURCE_MUTATION_SCOPE_MISMATCH"
                    )

                postimage: dict[str, Any] = {}

                for rel in authorized:
                    path = fixture / rel

                    postimage[rel] = {
                        "exists":
                            path.exists(),

                        "sha256":
                            sha_file(path),
                    }

                if (
                    postimage[
                        authorized[0]
                    ]["sha256"]
                    ==
                    preimage[
                        authorized[0]
                    ]["sha256"]
                ):
                    raise RuntimeError(
                        "INDEX_MUTATION_NOT_OBSERVED"
                    )

                if (
                    postimage[
                        authorized[1]
                    ]["exists"]
                    is not True
                ):
                    raise RuntimeError(
                        "GENERATED_TEST_NOT_CREATED"
                    )

                source_contract = (
                    gate6.verify_source_contract()
                )

                if (
                    source_contract.get("state")
                    != "PASS"
                ):
                    raise RuntimeError(
                        "SOURCE_CONTRACT_HOLD"
                    )

                regression = (
                    gate6.run_regression(
                        run_dir
                    )
                )

                if (
                    regression.get("state")
                    != "PASS"
                ):
                    raise RuntimeError(
                        "REGRESSION_HOLD"
                    )

                required_checks = {
                    "targeted-v08-existing-product-change",
                    "full-runtime-regression",
                    "native-prep-syntax",
                    "native-swift-build",
                    "diff-check",
                }

                observed_checks = {
                    item.get("name")
                    for item
                    in regression.get(
                        "checks",
                        [],
                    )
                }

                if (
                    observed_checks
                    != required_checks
                ):
                    raise RuntimeError(
                        "REGRESSION_CHECK_SET_MISMATCH"
                    )

                gate6.restore_precommit_sources(
                    backups
                )

                mutation_started = False

                rollback: dict[str, Any] = {}

                for rel in authorized:
                    path = fixture / rel

                    rollback[rel] = {
                        "exists":
                            path.exists(),

                        "sha256":
                            sha_file(path),
                    }

                if (
                    rollback[
                        authorized[0]
                    ]["sha256"]
                    !=
                    preimage[
                        authorized[0]
                    ]["sha256"]
                ):
                    raise RuntimeError(
                        "ROLLBACK_BYTE_PARITY_FAILED"
                    )

                if (
                    rollback[
                        authorized[1]
                    ]["exists"]
                    is not False
                ):
                    raise RuntimeError(
                        "ROLLBACK_NEW_FILE_REMOVE_FAILED"
                    )

                if git(
                    fixture,
                    "rev-parse",
                    "HEAD",
                ) != BASELINE:
                    raise RuntimeError(
                        "ROLLBACK_HEAD_CHANGED"
                    )

                if git(
                    fixture,
                    "status",
                    "--porcelain",
                ):
                    raise RuntimeError(
                        "ROLLBACK_WORKTREE_NOT_CLEAN"
                    )

                unauthorized = (
                    fixture
                    / "CAP06_UNAUTHORIZED_PROBE.txt"
                )

                unauthorized.write_text(
                    "fail closed\n",
                    encoding="utf-8",
                )

                failure_reason = None
                failure_observed = False

                try:
                    gate6.verify_worktree_scope()
                except RuntimeError as exc:
                    failure_reason = str(exc)

                    failure_observed = (
                        "GATE6_PRODUCT_MUTATION_SCOPE_MISMATCH"
                        in failure_reason
                    )
                finally:
                    unauthorized.unlink(
                        missing_ok=True
                    )

                if not failure_observed:
                    raise RuntimeError(
                        "UNAUTHORIZED_PATH_FAIL_CLOSED_MISSING"
                    )

                if git(
                    fixture,
                    "status",
                    "--porcelain",
                ):
                    raise RuntimeError(
                        "NEGATIVE_CONTROL_CLEANUP_FAILED"
                    )

                payload.update({
                    "state":
                        "PASS",

                    "claim":
                        "SOURCE_PRODUCT_CHANGE_REAL_BOUNDED_MUTATION_REGRESSION_ROLLBACK_AND_FAILURE_PATH_PASS",

                    "fixture": {
                        "baselineHead":
                            BASELINE,

                        "headAfterRollback":
                            git(
                                fixture,
                                "rev-parse",
                                "HEAD",
                            ),

                        "cleanAfterRollback":
                            True,
                    },

                    "preimage":
                        preimage,

                    "postimage":
                        postimage,

                    "rollback":
                        rollback,

                    "sourceContract":
                        source_contract,

                    "regression":
                        regression,

                    "failurePath": {
                        "unauthorizedPathInjected":
                            True,

                        "failClosedObserved":
                            True,

                        "reason":
                            failure_reason,
                    },

                    "rollbackProof": {
                        "required":
                            True,

                        "performed":
                            True,

                        "existingFileByteParity":
                            True,

                        "newFileRemoved":
                            True,

                        "headUnchanged":
                            True,

                        "worktreeClean":
                            True,
                    },

                    "mutationTruth": {
                        "fixtureMutationPerformed":
                            True,

                        "canonicalProductMutationPerformed":
                            False,

                        "canonicalControlMutationPerformed":
                            False,

                        "localCommitPerformed":
                            False,

                        "remotePushPerformed":
                            False,

                        "packageInstallPerformed":
                            False,
                    },
                })

            finally:
                if mutation_started:
                    try:
                        gate6.restore_precommit_sources(
                            backups
                        )
                    except Exception:
                        pass

        control_head_after = git(
            CONTROL,
            "rev-parse",
            "HEAD",
        )

        control_status_after = git(
            CONTROL,
            "status",
            "--porcelain",
        )

        product_head_after = git(
            PRODUCT,
            "rev-parse",
            "HEAD",
        )

        product_status_after = git(
            PRODUCT,
            "status",
            "--porcelain",
        )

        control_unchanged = (
            control_head_after
            == control_head_before
            and control_status_after
            == control_status_before
        )

        product_unchanged = (
            product_head_after
            == product_head_before
            and product_status_after
            == product_status_before
        )

        payload[
            "canonicalControlUnchanged"
        ] = control_unchanged

        payload[
            "canonicalProductUnchanged"
        ] = product_unchanged

        if not control_unchanged:
            raise RuntimeError(
                "CANONICAL_CONTROL_CHANGED"
            )

        if not product_unchanged:
            raise RuntimeError(
                "CANONICAL_PRODUCT_CHANGED"
            )

        write(
            evidence,
            payload,
        )

        print("STATE=PASS")
        print("CAP06_SOURCE_CHANGE=PASS")
        print("AUTHORIZED_PATH_COUNT=2")
        print("SOURCE_CONTRACT=PASS")
        print("REGRESSION=PASS")
        print("ROLLBACK=PASS")
        print("ROLLBACK_BYTE_PARITY=PASS")
        print("ROLLBACK_WORKTREE_CLEAN=PASS")
        print("FAILURE_PATH=PASS")
        print("CANONICAL_CONTROL_UNCHANGED=PASS")
        print("CANONICAL_PRODUCT_UNCHANGED=PASS")
        print("REMOTE_PUSH=false")
        print("NETWORK_REQUIRED=false")
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
        print("REMOTE_PUSH=false")
        print("NETWORK_REQUIRED=false")
        print("EXECUTION_AUTHORITY_CREATED=false")
        print("EVIDENCE=" + str(evidence))
        return 20


if __name__ == "__main__":
    raise SystemExit(main())
