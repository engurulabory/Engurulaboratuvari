#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

sys.path.insert(
    0,
    str(ROOT / "tools"),
)

import mac_engineer_offline_gitvault_reconciliation_field_proof as offline

from mac_engineer_local_candidate_authority import (
    evaluate_local_accepted_candidate,
)

SESSION_STATE = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "SESSION_STATE_V1.json"
)

RESTART_COMMAND = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V07_MAC_NATIVE_RESTART_RECOVERY_PROOF.command"
)

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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def atomic_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = path.with_name(
        "." + path.name + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    os.replace(
        tmp,
        path,
    )


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 7200,
) -> dict[str, Any]:

    p = subprocess.run(
        cmd,
        cwd=str(
            cwd
            or ROOT
        ),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE":
                "1",
        },
    )

    return {
        "code":
            p.returncode,

        "stdout":
            p.stdout,

        "stderr":
            p.stderr,
    }


def git(
    *args: str,
) -> str:

    p = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=True,
    )

    return p.stdout.strip()


def load_json(
    path: Path,
) -> dict[str, Any]:

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            "JSON_OBJECT_REQUIRED"
        )

    return value


def postlock_accepted_candidate() -> dict[str, Any]:

    session = load_json(
        SESSION_STATE
    )

    control = {
        "branch":
            git(
                "branch",
                "--show-current",
            ),

        "head":
            git(
                "rev-parse",
                "HEAD",
            ),

        "origin_main":
            git(
                "rev-parse",
                "origin/main",
            ),

        "clean":
            git(
                "status",
                "--porcelain",
            )
            == "",
    }

    result = (
        evaluate_local_accepted_candidate(
            control,
            session,
        )
    )

    if (
        result.get(
            "authorized"
        )
        is not True
    ):
        raise RuntimeError(
            "POSTLOCK_ACCEPTED_CANDIDATE_REQUIRED:"
            + ",".join(
                result.get(
                    "reasons"
                )
                or []
            )
        )

    if (
        result.get(
            "policy_phase"
        )
        not in {
            "POST_LOCK_VERIFIED_FINISH",
            "ACTIVE_VERSION_ENGINEERING",
        }
    ):
        raise RuntimeError(
            "POSTLOCK_POLICY_PHASE_REQUIRED"
        )

    accepted = (
        result.get(
            "acceptance"
        )
        or {}
    )

    if (
        accepted.get(
            "authority"
        )
        !=
        "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY_VERIFIED"
    ):
        raise RuntimeError(
            "VERIFIED_LOCAL_AUTHORITY_REQUIRED"
        )

    if (
        accepted.get(
            "canonicalRemoteAuthority"
        )
        !=
        "GITHUB_REMOTE_MAIN"
    ):
        raise RuntimeError(
            "GITHUB_REMOTE_MAIN_REQUIRED"
        )

    if (
        accepted.get(
            "secondCanonicalTruth"
        )
        is not False
    ):
        raise RuntimeError(
            "SECOND_CANONICAL_TRUTH_FALSE_REQUIRED"
        )

    return accepted


def postlock_clone_exact(
    mirror: Path,
    target: Path,
    sha: str,
) -> None:

    if not mirror.is_dir():
        raise RuntimeError(
            "CONTROL_GITVAULT_MIRROR_REQUIRED"
        )

    if not offline.mirror_has_commit(
        mirror,
        sha,
    ):
        raise RuntimeError(
            "ACCEPTED_HEAD_NOT_PRESENT_IN_GITVAULT"
        )

    clone = offline.run(
        [
            "git",
            "clone",
            "--no-local",
            str(mirror),
            str(target),
        ],
        timeout=1200,
    )

    offline.require(
        clone,
        "LOCAL_GITVAULT_CLONE",
    )

    exact = offline.run(
        [
            "git",
            "fetch",
            "--no-tags",
            str(mirror),
            sha,
        ],
        cwd=target,
        timeout=1200,
    )

    offline.require(
        exact,
        "LOCAL_GITVAULT_EXACT_SHA_FETCH",
    )

    checkout = offline.run(
        [
            "git",
            "checkout",
            "--detach",
            sha,
        ],
        cwd=target,
        timeout=120,
    )

    offline.require(
        checkout,
        "ACCEPTED_HEAD_CHECKOUT",
    )

    if (
        offline.git(
            target,
            "rev-parse",
            "HEAD",
        )
        != sha
    ):
        raise RuntimeError(
            "ACCEPTED_HEAD_CLONE_PARITY_REQUIRED"
        )


def parse_fields(
    text: str,
) -> dict[str, str]:

    fields: dict[str, str] = {}

    for line in text.splitlines():
        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1,
        )

        fields[
            key.strip()
        ] = value.strip()

    return fields


def main() -> int:

    if not RESTART_COMMAND.is_file():
        raise RuntimeError(
            "RESTART_COMMAND_REQUIRED"
        )

    restart = run(
        [
            "zsh",
            str(
                RESTART_COMMAND
            ),
        ]
    )

    restart_fields = parse_fields(
        restart["stdout"]
    )

    if (
        restart["code"] != 0
        or restart_fields.get(
            "STATE"
        )
        != "PASS"
        or restart_fields.get(
            "PROCESS_RESTART"
        )
        != "PASS"
        or restart_fields.get(
            "TASK_IDENTITY"
        )
        != "PASS"
        or restart_fields.get(
            "CHECKPOINT_RESUME"
        )
        != "PASS"
        or restart_fields.get(
            "EXACTLY_ONCE_EFFECT"
        )
        != "PASS"
        or restart_fields.get(
            "FINAL_STATE"
        )
        != "COMPLETE"
        or restart_fields.get(
            "GITVAULT_MIRROR_UNCHANGED"
        )
        != "PASS"
        or restart_fields.get(
            "REMOTE_PUSH"
        )
        != "false"
    ):
        raise RuntimeError(
            "RESTART_RECOVERY_FIELD_PROOF_REQUIRED"
        )

    restart_evidence = Path(
        restart_fields.get(
            "EVIDENCE"
        )
        or ""
    )

    if (
        not restart_evidence.is_file()
    ):
        raise RuntimeError(
            "RESTART_EVIDENCE_REQUIRED"
        )

    restart_sha = sha256_file(
        restart_evidence
    )

    if (
        len(restart_sha) != 64
        or any(
            c not in "0123456789abcdef"
            for c in restart_sha
        )
    ):
        raise RuntimeError(
            "RESTART_EVIDENCE_SHA256_INVALID"
        )

    restart_payload = load_json(
        restart_evidence
    )

    if (
        restart_payload.get("state")
        != "PASS"
    ):
        raise RuntimeError(
            "RESTART_EVIDENCE_PASS_REQUIRED"
        )

    original_loader = (
        offline
        .load_accepted_candidate
    )

    original_clone = (
        offline
        .clone_exact
    )

    offline.load_accepted_candidate = (
        postlock_accepted_candidate
    )

    offline.clone_exact = (
        postlock_clone_exact
    )

    try:
        offline_payload = (
            offline.perform()
        )
    finally:
        offline.load_accepted_candidate = (
            original_loader
        )

        offline.clone_exact = (
            original_clone
        )

    if (
        offline_payload.get(
            "state"
        )
        != "PASS"
    ):
        raise RuntimeError(
            "OFFLINE_FIELD_PROOF_REQUIRED"
        )

    real = (
        offline_payload.get(
            "realCheckoutPendingReconciliation"
        )
        or {}
    )

    queue = (
        offline_payload.get(
            "offlineQueue"
        )
        or {}
    )

    reconciliation = (
        offline_payload.get(
            "reconciliationReadiness"
        )
        or {}
    )

    vault = (
        offline_payload.get(
            "gitVault"
        )
        or {}
    )

    accepted = (
        offline_payload.get(
            "acceptedCandidate"
        )
        or {}
    )

    offline_evidence = Path(
        offline_payload.get(
            "evidencePath"
        )
        or ""
    )

    if (
        not offline_evidence.is_file()
    ):
        raise RuntimeError(
            "OFFLINE_EVIDENCE_REQUIRED"
        )

    checks = {
        "realAuthority":
            real.get(
                "authority"
            )
            ==
            "PENDING_RECONCILIATION_NOT_CANONICAL",

        "queueAuthority":
            queue.get(
                "authority"
            )
            ==
            "PENDING_RECONCILIATION_NOT_CANONICAL",

        "queueOneAhead":
            queue.get(
                "aheadAcceptedHead"
            )
            == 1,

        "queueRemoteMutationFalse":
            queue.get(
                "remoteMutation"
            )
            is False,

        "queueSecondTruthFalse":
            queue.get(
                "secondCanonicalTruth"
            )
            is False,

        "reconciliationPass":
            reconciliation.get(
                "state"
            )
            == "PASS",

        "patchApplyCheck":
            reconciliation.get(
                "patchApplyCheck"
            )
            == "PASS",

        "refsUnchanged":
            vault.get(
                "refsUnchanged"
            )
            is True,

        "remoteIdentity":
            offline_payload.get(
                "canonicalRemoteIdentityPreserved"
            )
            is True,

        "networkFalse":
            offline_payload.get(
                "networkRequired"
            )
            is False,

        "remotePushFalse":
            offline_payload.get(
                "remotePush"
            )
            is False,

        "remoteMergeFalse":
            offline_payload.get(
                "remoteMerge"
            )
            is False,

        "secondTruthCreatedFalse":
            offline_payload.get(
                "secondCanonicalTruthCreated"
            )
            is False,

        "acceptedHeadFresh":
            accepted.get(
                "head"
            )
            == git(
                "rev-parse",
                "HEAD",
            ),
    }

    if not all(
        checks.values()
    ):
        raise RuntimeError(
            "OFFLINE_CONTINUITY_CHECK_FAILED:"
            + ",".join(
                key
                for key, ok
                in checks.items()
                if not ok
            )
        )

    run_dir = (
        EVIDENCE_ROOT
        / stamp()
        / "capability-16"
    )

    evidence = (
        run_dir
        / "field-proof.json"
    )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-cap16-field-proof/v1",

        "observedAt":
            now(),

        "state":
            "PASS",

        "capabilityId":
            "RECOVERY_OFFLINE_CONTINUITY",

        "authority":
            "AMBER",

        "mutationScope":
            "RECOVERY_AND_ROLLBACK_SCOPE",

        "restartRecovery": {
            "state":
                "PASS",

            "evidence":
                str(
                    restart_evidence
                ),

            "sha256":
                sha256_file(
                    restart_evidence
                ),
        },

        "offlineContinuity": {
            "state":
                "PASS",

            "evidence":
                str(
                    offline_evidence
                ),

            "sha256":
                sha256_file(
                    offline_evidence
                ),
        },

        "remotePush":
            False,

        "networkRequired":
            False,

        "humanThresholdRequired":
            False,

        "secondCanonicalTruth":
            False,

        "canonicalTruthPreserved":
            True,

        "recoveryProofObserved":
            True,

        "nextAction":
            "DONECHECK_V12_CAP16_AND_FIELD_VERIFICATION_SEAL",
    }

    atomic_json(
        evidence,
        payload,
    )

    print("STATE=PASS")
    print(
        "CAP16_RECOVERY_OFFLINE_CONTINUITY=PASS"
    )
    print("RESTART_RECOVERY=PASS")
    print("CHECKPOINT_RESUME=PASS")
    print("EXACTLY_ONCE_EFFECT=PASS")
    print("OFFLINE_CONTINUITY=PASS")
    print("OFFLINE_QUEUE=PASS")
    print("DURABLE_PATCH=PASS")
    print("DURABLE_GIT_BUNDLE=PASS")
    print(
        "RECONCILIATION_APPLY_CHECK=PASS"
    )
    print(
        "GITVAULT_REFS_UNCHANGED=PASS"
    )
    print(
        "REMOTE_IDENTITY_PRESERVED=PASS"
    )
    print("AUTHORITY=AMBER")
    print(
        "MUTATION_SCOPE=RECOVERY_AND_ROLLBACK_SCOPE"
    )
    print(
        "HUMAN_THRESHOLD_REQUIRED=false"
    )
    print("NETWORK_REQUIRED=false")
    print("REMOTE_PUSH=false")
    print(
        "SECOND_CANONICAL_TRUTH=false"
    )
    print(
        "CANONICAL_TRUTH_PRESERVED=PASS"
    )
    print(
        "RESTART_EVIDENCE_SHA256="
        + restart_sha
    )
    print(
        "OFFLINE_EVIDENCE_SHA256="
        + sha256_file(
            offline_evidence
        )
    )
    print(
        "EVIDENCE="
        + str(
            evidence
        )
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
