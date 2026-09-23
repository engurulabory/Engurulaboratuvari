#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ — Gate 10 Offline / GitVault reconciliation proof.

Proves that engineering can continue from accepted local truth without GitHub
execution, while preserving remote identity and avoiding a second canonical
truth.

Flow:
  accepted local candidate + Repository Fabric PASS
  -> clone exact accepted HEAD from operator GitVault
  -> create one local pending-reconciliation commit
  -> seal patch + git bundle as durable queue artifacts
  -> verify patch applicability from the exact accepted base
  -> verify bundle integrity and exact queued commit
  -> verify GitVault refs are unchanged
  -> emit machine-readable Evidence

No network, push, merge, or remote mutation is performed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_STATE = (
    HOME
    / "Enguru"
    / "Runtime"
    / "MacEngineer"
    / "state"
    / "local-accepted-control-plane-candidate.json"
)
FABRIC_STATE = (
    HOME
    / "Enguru"
    / "Runtime"
    / "MacEngineer"
    / "state"
    / "repository-fabric.json"
)
CONTROL_MIRROR = (
    HOME
    / "Enguru"
    / "GitVault"
    / "MacEngineer"
    / "Engurulaboratuvari.git"
)
EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.7"
    / "offline-gitvault-reconciliation"
)

QUEUE_BRANCH = "enguru-offline-reconciliation-proof"
QUEUE_FILE = ".enguru/offline-reconciliation-proof.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 1200,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
            env=env,
        )
        return {
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"code": 124, "stdout": "", "stderr": "TIMEOUT"}


def require(result: dict[str, Any], label: str) -> None:
    if result["code"] != 0:
        tail = (
            str(result.get("stdout") or "")
            + "\n"
            + str(result.get("stderr") or "")
        )[-5000:]
        raise RuntimeError(f"{label}_FAILED:{tail}")


def git(cwd: Path, *args: str, timeout: int = 300) -> str:
    result = run(["git", *args], cwd=cwd, timeout=timeout)
    require(result, "GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def bare_git(mirror: Path, *args: str, timeout: int = 300) -> str:
    result = run(["git", "--git-dir", str(mirror), *args], timeout=timeout)
    require(result, "BARE_GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label}_INVALID:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def load_accepted_candidate() -> dict[str, Any]:
    data = load_json(ACCEPTED_STATE, "LOCAL_ACCEPTED_CANDIDATE_STATE")
    acceptance = data.get("acceptance") or {}
    required = (
        "targetedTests",
        "fullRegression",
        "diffCheck",
        "remoteBranchParity",
        "mainAncestor",
        "canonicalContext",
        "sessionStart",
    )
    if data.get("state") != "PASS":
        raise RuntimeError("LOCAL_ACCEPTED_CANDIDATE_PASS_REQUIRED")
    if data.get("authority") != "PENDING_RECONCILIATION":
        raise RuntimeError("LOCAL_ACCEPTED_CANDIDATE_AUTHORITY_REQUIRED")
    if data.get("canonicalRemoteAuthority") != "GITHUB_REMOTE_MAIN":
        raise RuntimeError("GITHUB_REMOTE_MAIN_IDENTITY_REQUIRED")
    if data.get("secondCanonicalTruth") is not False:
        raise RuntimeError("SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")
    for key in required:
        if acceptance.get(key) != "PASS":
            raise RuntimeError(f"LOCAL_ACCEPTED_{key.upper()}_PASS_REQUIRED")
    for key in ("branch", "head", "originMain"):
        if not str(data.get(key) or "").strip():
            raise RuntimeError(f"LOCAL_ACCEPTED_{key.upper()}_REQUIRED")
    return data


def load_fabric() -> dict[str, Any]:
    data = load_json(FABRIC_STATE, "REPOSITORY_FABRIC_STATE")
    if data.get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_PASS_REQUIRED")
    if data.get("repositoryCount") != 12 or data.get("mirrorPassCount") != 12:
        raise RuntimeError("REPOSITORY_FABRIC_12_OF_12_REQUIRED")
    if (data.get("offlineQueueProof") or {}).get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_OFFLINE_QUEUE_PASS_REQUIRED")
    return data


def mirror_refs(mirror: Path) -> str:
    return bare_git(mirror, "show-ref")


def mirror_has_commit(mirror: Path, sha: str) -> bool:
    result = run(
        [
            "git",
            "--git-dir",
            str(mirror),
            "cat-file",
            "-e",
            f"{sha}^{{commit}}",
        ],
        timeout=60,
    )
    return result["code"] == 0


def validate_real_checkout(accepted: dict[str, Any]) -> dict[str, Any]:
    branch = git(ROOT, "branch", "--show-current")
    head = git(ROOT, "rev-parse", "HEAD")
    origin_main = git(ROOT, "rev-parse", "origin/main")
    status = git(ROOT, "status", "--porcelain")
    ahead = git(ROOT, "rev-list", "--count", "origin/main..HEAD")

    if branch != accepted["branch"]:
        raise RuntimeError("REAL_CHECKOUT_BRANCH_ACCEPTED_PARITY_REQUIRED")
    if head != accepted["head"]:
        raise RuntimeError("REAL_CHECKOUT_HEAD_ACCEPTED_PARITY_REQUIRED")
    if origin_main != accepted["originMain"]:
        raise RuntimeError("REAL_CHECKOUT_ORIGIN_MAIN_ACCEPTED_PARITY_REQUIRED")
    if status:
        raise RuntimeError("REAL_CHECKOUT_CLEAN_REQUIRED")
    if not ahead.isdigit() or int(ahead) < 1:
        raise RuntimeError("REAL_CHECKOUT_PENDING_RECONCILIATION_REQUIRED")

    return {
        "branch": branch,
        "head": head,
        "originMain": origin_main,
        "aheadOriginMain": int(ahead),
        "clean": True,
        "authority": "PENDING_RECONCILIATION_NOT_CANONICAL",
    }


def clone_exact(mirror: Path, target: Path, sha: str) -> None:
    if not mirror.is_dir():
        raise RuntimeError("CONTROL_GITVAULT_MIRROR_REQUIRED")
    if not mirror_has_commit(mirror, sha):
        raise RuntimeError("ACCEPTED_HEAD_NOT_PRESENT_IN_GITVAULT")
    result = run(
        ["git", "clone", "--no-local", str(mirror), str(target)],
        timeout=1200,
    )
    require(result, "LOCAL_GITVAULT_CLONE")
    checkout = run(
        ["git", "checkout", "--detach", sha],
        cwd=target,
        timeout=120,
    )
    require(checkout, "ACCEPTED_HEAD_CHECKOUT")
    if git(target, "rev-parse", "HEAD") != sha:
        raise RuntimeError("ACCEPTED_HEAD_CLONE_PARITY_REQUIRED")


def create_offline_commit(
    fixture: Path,
    *,
    accepted: dict[str, Any],
) -> tuple[str, Path]:
    git(fixture, "switch", "-c", QUEUE_BRANCH)
    git(fixture, "config", "user.name", "ENGURU Offline Reconciliation Proof")
    git(fixture, "config", "user.email", "offline-proof@invalid.local")

    queue_path = fixture / QUEUE_FILE
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "enguru.mac-engineer.offline-reconciliation-item/v1",
        "createdAt": now(),
        "authority": "PENDING_RECONCILIATION_NOT_CANONICAL",
        "baseAcceptedHead": accepted["head"],
        "remoteMainIdentity": accepted["originMain"],
        "sourceBranch": accepted["branch"],
        "networkRequired": False,
        "remoteMutation": False,
        "secondCanonicalTruth": False,
        "reconciliationMode": "EXPLICIT_WHEN_REMOTE_AUTHORITY_AVAILABLE",
    }
    atomic_json(queue_path, manifest)
    git(fixture, "add", QUEUE_FILE)
    git(fixture, "commit", "-m", "test: offline reconciliation queue proof")
    commit = git(fixture, "rev-parse", "HEAD")
    ahead_base = git(
        fixture,
        "rev-list",
        "--count",
        f"{accepted['head']}..HEAD",
    )
    if ahead_base != "1":
        raise RuntimeError(f"ONE_OFFLINE_COMMIT_REQUIRED:{ahead_base}")
    if git(fixture, "status", "--porcelain"):
        raise RuntimeError("OFFLINE_FIXTURE_CLEAN_REQUIRED")
    return commit, queue_path


def seal_queue(
    fixture: Path,
    *,
    accepted_head: str,
    offline_commit: str,
    run_dir: Path,
) -> dict[str, Any]:
    patch = run_dir / "pending-reconciliation.patch"
    patch_result = run(
        ["git", "format-patch", "--stdout", f"{accepted_head}..HEAD"],
        cwd=fixture,
        timeout=120,
    )
    require(patch_result, "OFFLINE_PATCH_EXPORT")
    patch.write_text(patch_result["stdout"] + "\n", encoding="utf-8")

    bundle = run_dir / "pending-reconciliation.bundle"
    bundle_result = run(
        ["git", "bundle", "create", str(bundle), QUEUE_BRANCH],
        cwd=fixture,
        timeout=300,
    )
    require(bundle_result, "OFFLINE_BUNDLE_CREATE")

    verify = run(
        ["git", "bundle", "verify", str(bundle)],
        cwd=fixture,
        timeout=300,
    )
    require(verify, "OFFLINE_BUNDLE_VERIFY")

    heads = run(
        ["git", "bundle", "list-heads", str(bundle)],
        cwd=fixture,
        timeout=120,
    )
    require(heads, "OFFLINE_BUNDLE_LIST_HEADS")
    if offline_commit not in heads["stdout"]:
        raise RuntimeError("OFFLINE_COMMIT_NOT_SEALED_IN_BUNDLE")

    return {
        "patch": str(patch),
        "patchSha256": sha256_file(patch),
        "bundle": str(bundle),
        "bundleSha256": sha256_file(bundle),
        "bundleVerify": "PASS",
        "bundleHeads": heads["stdout"].splitlines(),
    }


def verify_reconciliation_ready(
    mirror: Path,
    *,
    accepted_head: str,
    patch: Path,
    target: Path,
) -> dict[str, Any]:
    clone_exact(mirror, target, accepted_head)
    check = run(
        ["git", "apply", "--check", str(patch)],
        cwd=target,
        timeout=120,
    )
    require(check, "RECONCILIATION_PATCH_APPLY_CHECK")
    if git(target, "status", "--porcelain"):
        raise RuntimeError("RECONCILIATION_CHECKOUT_CHANGED_BY_APPLY_CHECK")
    return {
        "state": "PASS",
        "baseSha": accepted_head,
        "patchApplyCheck": "PASS",
        "worktreeCleanAfterCheck": True,
    }


def perform() -> dict[str, Any]:
    accepted = load_accepted_candidate()
    fabric = load_fabric()
    real_checkout = validate_real_checkout(accepted)

    if not CONTROL_MIRROR.is_dir():
        raise RuntimeError("CONTROL_GITVAULT_MIRROR_REQUIRED")

    mirror_remote_main = bare_git(
        CONTROL_MIRROR,
        "rev-parse",
        "refs/remotes/origin/main",
    )
    if mirror_remote_main != accepted["originMain"]:
        raise RuntimeError("GITVAULT_REMOTE_MAIN_IDENTITY_REQUIRED")
    if not mirror_has_commit(CONTROL_MIRROR, accepted["head"]):
        raise RuntimeError("GITVAULT_ACCEPTED_HEAD_REQUIRED")

    mirror_refs_before = mirror_refs(CONTROL_MIRROR)
    mirror_refs_before_digest = sha256_text(mirror_refs_before)

    fsck_before = run(
        ["git", "--git-dir", str(CONTROL_MIRROR), "fsck", "--full", "--no-dangling"],
        timeout=600,
    )
    require(fsck_before, "GITVAULT_FSCK_BEFORE")

    run_dir = EVIDENCE_ROOT / stamp()
    workspace = run_dir / "workspace"
    fixture = workspace / "offline-fixture"
    reconcile = workspace / "reconciliation-check"
    workspace.mkdir(parents=True, exist_ok=False)

    clone_exact(CONTROL_MIRROR, fixture, accepted["head"])
    offline_commit, queue_path = create_offline_commit(
        fixture,
        accepted=accepted,
    )

    queued_ahead_remote = git(
        fixture,
        "rev-list",
        "--count",
        f"{accepted['originMain']}..HEAD",
    )
    if not queued_ahead_remote.isdigit():
        raise RuntimeError("QUEUED_AHEAD_REMOTE_COUNT_REQUIRED")

    queue_artifacts = seal_queue(
        fixture,
        accepted_head=accepted["head"],
        offline_commit=offline_commit,
        run_dir=run_dir,
    )
    reconciliation = verify_reconciliation_ready(
        CONTROL_MIRROR,
        accepted_head=accepted["head"],
        patch=Path(queue_artifacts["patch"]),
        target=reconcile,
    )

    mirror_refs_after = mirror_refs(CONTROL_MIRROR)
    mirror_refs_after_digest = sha256_text(mirror_refs_after)
    if mirror_refs_after != mirror_refs_before:
        raise RuntimeError("GITVAULT_REFS_CHANGED_DURING_OFFLINE_PROOF")

    fsck_after = run(
        ["git", "--git-dir", str(CONTROL_MIRROR), "fsck", "--full", "--no-dangling"],
        timeout=600,
    )
    require(fsck_after, "GITVAULT_FSCK_AFTER")

    queue_manifest = load_json(queue_path, "OFFLINE_QUEUE_ITEM")
    if queue_manifest.get("authority") != "PENDING_RECONCILIATION_NOT_CANONICAL":
        raise RuntimeError("OFFLINE_QUEUE_AUTHORITY_REQUIRED")
    if queue_manifest.get("secondCanonicalTruth") is not False:
        raise RuntimeError("OFFLINE_QUEUE_SECOND_TRUTH_FALSE_REQUIRED")
    if queue_manifest.get("remoteMutation") is not False:
        raise RuntimeError("OFFLINE_QUEUE_REMOTE_MUTATION_FALSE_REQUIRED")

    shutil.rmtree(workspace)

    payload = {
        "schema": "enguru.mac-engineer.offline-gitvault-reconciliation-proof/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": 10,
        "acceptedCandidate": {
            "branch": accepted["branch"],
            "head": accepted["head"],
            "originMain": accepted["originMain"],
            "evidence": accepted.get("evidence"),
        },
        "realCheckoutPendingReconciliation": real_checkout,
        "repositoryFabric": {
            "state": fabric["state"],
            "repositoryCount": fabric["repositoryCount"],
            "mirrorPassCount": fabric["mirrorPassCount"],
            "offlineQueueProof": (fabric.get("offlineQueueProof") or {}).get("state"),
        },
        "gitVault": {
            "mirror": str(CONTROL_MIRROR),
            "remoteMain": mirror_remote_main,
            "refsBeforeSha256": mirror_refs_before_digest,
            "refsAfterSha256": mirror_refs_after_digest,
            "refsUnchanged": True,
            "fsckBefore": "PASS",
            "fsckAfter": "PASS",
        },
        "offlineQueue": {
            "authority": "PENDING_RECONCILIATION_NOT_CANONICAL",
            "baseAcceptedHead": accepted["head"],
            "offlineCommit": offline_commit,
            "aheadAcceptedHead": 1,
            "aheadRemoteMain": int(queued_ahead_remote),
            "remoteMutation": False,
            "secondCanonicalTruth": False,
            **queue_artifacts,
        },
        "reconciliationReadiness": reconciliation,
        "networkRequired": False,
        "githubActionsRequired": False,
        "remotePush": False,
        "remoteMerge": False,
        "canonicalRemoteIdentityPreserved": True,
        "secondCanonicalTruthCreated": False,
        "authority": (
            "REAL_MAC_OFFLINE_RECONCILIATION_FIELD_EVIDENCE. "
            "Queued engineering work is sealed as durable Evidence and remains "
            "PENDING_RECONCILIATION_NOT_CANONICAL until explicit remote reconciliation."
        ),
        "nextAction": "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION",
    }

    evidence = run_dir / "evidence.json"
    payload["evidencePath"] = str(evidence)
    atomic_json(evidence, payload)

    receipt = run_dir / "receipt.txt"
    receipt.write_text(
        "\n".join(
            [
                "STATE=PASS",
                "OFFLINE_LOCAL_COMMIT_QUEUE=PASS",
                "DURABLE_PATCH=PASS",
                "DURABLE_GIT_BUNDLE=PASS",
                "RECONCILIATION_APPLY_CHECK=PASS",
                "GITVAULT_REFS_UNCHANGED=PASS",
                "REMOTE_IDENTITY_PRESERVED=PASS",
                "REMOTE_PUSH=false",
                "SECOND_CANONICAL_TRUTH=false",
                f"EVIDENCE={evidence}",
                "NEXT_ACTION=DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return payload


def main() -> int:
    try:
        payload = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_OFFLINE_GITVAULT_PROOF")
        return 2

    print("STATE=PASS")
    print("OFFLINE_LOCAL_COMMIT_QUEUE=PASS")
    print("DURABLE_PATCH=PASS")
    print("DURABLE_GIT_BUNDLE=PASS")
    print("RECONCILIATION_APPLY_CHECK=PASS")
    print("GITVAULT_REFS_UNCHANGED=PASS")
    print("REMOTE_IDENTITY_PRESERVED=PASS")
    print("REMOTE_PUSH=false")
    print("SECOND_CANONICAL_TRUTH=false")
    print(f"EVIDENCE={payload['evidencePath']}")
    print(f"NEXT_ACTION={payload['nextAction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
