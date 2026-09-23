#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ — Mac-native authority migration field proof.

Proves one bounded multi-repository engineering task entirely from local
Repository Fabric mirrors. No network, push, merge, or canonical remote
mutation is performed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

HOME = Path.home()
FABRIC_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "repository-fabric.json"
ACCEPTED_CONTROL_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "local-accepted-control-plane-candidate.json"
MIRROR_ROOT = HOME / "Enguru" / "GitVault" / "MacEngineer"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "mac-native-authority-migration"
TASK_ID = "ENGURU-V07-MAC-NATIVE-MIGRATION-001"
BRANCH = "enguru-mac-native-migration-proof"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 1800,
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
        tail = (str(result.get("stdout") or "") + "\n" + str(result.get("stderr") or ""))[-5000:]
        raise RuntimeError(f"{label}_FAILED:{tail}")


def git(cwd: Path, *args: str, timeout: int = 300) -> str:
    result = run(["git", *args], cwd=cwd, timeout=timeout)
    require(result, "GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def mirror_main(mirror: Path) -> str:
    result = run(["git", "--git-dir", str(mirror), "rev-parse", "refs/heads/main"], timeout=60)
    require(result, "MIRROR_MAIN")
    return result["stdout"].strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_fabric() -> dict[str, Any]:
    if not FABRIC_STATE.is_file():
        raise RuntimeError("REPOSITORY_FABRIC_STATE_REQUIRED")
    data = json.loads(FABRIC_STATE.read_text(encoding="utf-8"))
    if data.get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_PASS_REQUIRED")
    if data.get("repositoryCount") != 12 or data.get("mirrorPassCount") != 12:
        raise RuntimeError("REPOSITORY_FABRIC_12_OF_12_REQUIRED")
    if (data.get("offlineQueueProof") or {}).get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_OFFLINE_QUEUE_PASS_REQUIRED")
    return data


def load_accepted_control_candidate() -> dict[str, Any]:
    if not ACCEPTED_CONTROL_STATE.is_file():
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_CANDIDATE_REQUIRED")
    data = json.loads(ACCEPTED_CONTROL_STATE.read_text(encoding="utf-8"))
    acceptance = data.get("acceptance") or {}
    required = {
        "targetedTests": "PASS",
        "fullRegression": "PASS",
        "diffCheck": "PASS",
        "remoteBranchParity": "PASS",
        "mainAncestor": "PASS",
        "canonicalContext": "PASS",
        "sessionStart": "PASS",
    }
    if data.get("state") != "PASS":
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_CANDIDATE_PASS_REQUIRED")
    if data.get("authority") != "PENDING_RECONCILIATION":
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_AUTHORITY_REQUIRED")
    if data.get("canonicalRemoteAuthority") != "GITHUB_REMOTE_MAIN":
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_REMOTE_AUTHORITY_REQUIRED")
    if data.get("secondCanonicalTruth") is not False:
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_SECOND_TRUTH_FALSE_REQUIRED")
    if not data.get("head") or not data.get("originMain") or not data.get("branch"):
        raise RuntimeError("LOCAL_ACCEPTED_CONTROL_IDENTITY_REQUIRED")
    for key, expected in required.items():
        if acceptance.get(key) != expected:
            raise RuntimeError(f"LOCAL_ACCEPTED_CONTROL_{key.upper()}_{expected}_REQUIRED")
    return data


def repo_record(fabric: dict[str, Any], full_name: str) -> dict[str, Any]:
    for item in fabric.get("mirrors") or []:
        if item.get("repository") == full_name:
            return item
    raise RuntimeError(f"FABRIC_REPOSITORY_REQUIRED:{full_name}")


def mirror_has_commit(mirror: Path, sha: str) -> bool:
    result = run(
        ["git", "--git-dir", str(mirror), "cat-file", "-e", f"{sha}^{commit}"],
        timeout=60,
    )
    return result["code"] == 0


def clone_from_mirror(mirror: Path, target: Path, expected_sha: str) -> None:
    if not mirror.is_dir():
        raise RuntimeError(f"LOCAL_MIRROR_REQUIRED:{mirror}")
    if not mirror_has_commit(mirror, expected_sha):
        raise RuntimeError(f"LOCAL_MIRROR_EXACT_SHA_REQUIRED:{mirror.name}:{expected_sha}")
    result = run(
        ["git", "clone", "--no-local", str(mirror), str(target)],
        timeout=1200,
    )
    require(result, "LOCAL_MIRROR_CLONE")
    checkout = run(["git", "checkout", "--detach", expected_sha], cwd=target, timeout=120)
    require(checkout, "LOCAL_MIRROR_EXACT_SHA_CHECKOUT")
    head = git(target, "rev-parse", "HEAD")
    if head != expected_sha:
        raise RuntimeError(f"CLONE_EXACT_SHA_REQUIRED:{target.name}:{head}:{expected_sha}")


def write_manifest(
    repo_path: Path,
    *,
    repository: str,
    peer: str,
    base_sha: str,
) -> Path:
    path = repo_path / ".enguru" / "mac-native-authority-proof.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "enguru.mac-engineer.mac-native-authority-proof/v1",
        "taskId": TASK_ID,
        "repository": repository,
        "peerRepository": peer,
        "baseSha": base_sha,
        "executionAuthority": "MAC_NATIVE_LOCAL_FIELD_PROOF",
        "source": "LOCAL_GITVAULT_MIRROR_WITH_REPOSITORY_FABRIC_IDENTITY",
        "remoteMutation": False,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def commit_probe(repo_path: Path, repository: str, peer: str, base_sha: str) -> tuple[str, Path]:
    git(repo_path, "switch", "-c", BRANCH)
    git(repo_path, "config", "user.name", "ENGURU Mac Engineer Field Proof")
    git(repo_path, "config", "user.email", "mac-native-proof@invalid.local")
    manifest = write_manifest(repo_path, repository=repository, peer=peer, base_sha=base_sha)
    git(repo_path, "add", ".enguru/mac-native-authority-proof.json")
    git(repo_path, "commit", "-m", "test: mac-native authority migration proof")
    commit = git(repo_path, "rev-parse", "HEAD")
    if commit == base_sha:
        raise RuntimeError(f"LOCAL_COMMIT_REQUIRED:{repository}")
    ahead = git(repo_path, "rev-list", "--count", f"{base_sha}..HEAD")
    if ahead != "1":
        raise RuntimeError(f"ONE_LOCAL_COMMIT_REQUIRED:{repository}:{ahead}")
    return commit, manifest


def write_log(run_dir: Path, name: str, result: dict[str, Any]) -> Path:
    path = run_dir / f"{name}.log"
    path.write_text(
        (str(result.get("stdout") or "") + "\n" + str(result.get("stderr") or "")).strip() + "\n",
        encoding="utf-8",
    )
    return path


def control_plane_verify(repo_path: Path, run_dir: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=repo_path,
        timeout=3600,
        env=env,
    )
    log = write_log(run_dir, "control-plane-full-regression", result)
    require(result, "CONTROL_PLANE_FULL_REGRESSION")
    diff = run(["git", "diff", "--check", "main...HEAD"], cwd=repo_path, timeout=120)
    require(diff, "CONTROL_PLANE_DIFF_CHECK")
    return {"regression": "PASS", "diffCheck": "PASS", "log": str(log), "logSha256": sha256(log)}


def product_verify(repo_path: Path, run_dir: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(repo_path / "runtime")
    tests = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "runtime/tests", "-v"],
        cwd=repo_path,
        timeout=3600,
        env=env,
    )
    test_log = write_log(run_dir, "product-runtime-regression", tests)
    require(tests, "PRODUCT_RUNTIME_REGRESSION")

    syntax = run(
        ["zsh", "-n", "execution_prep/native_app/prepare_native_app.command"],
        cwd=repo_path,
        timeout=120,
        env=env,
    )
    syntax_log = write_log(run_dir, "product-native-prep-syntax", syntax)
    require(syntax, "PRODUCT_NATIVE_PREP_SYNTAX")

    binary = run_dir / "EnguruMacEngineer"
    swift = run(
        [
            "xcrun", "swiftc", "-parse-as-library",
            "execution_prep/native_app/EnguruMacEngineerApp.swift",
            "-o", str(binary),
            "-framework", "SwiftUI",
            "-framework", "WebKit",
            "-framework", "AppKit",
        ],
        cwd=repo_path,
        timeout=1800,
        env=env,
    )
    swift_log = write_log(run_dir, "product-native-swift-build", swift)
    require(swift, "PRODUCT_NATIVE_SWIFT_BUILD")

    diff = run(["git", "diff", "--check", "main...HEAD"], cwd=repo_path, timeout=120)
    require(diff, "PRODUCT_DIFF_CHECK")
    return {
        "runtimeRegression": "PASS",
        "nativePrepSyntax": "PASS",
        "nativeSwiftBuild": "PASS",
        "diffCheck": "PASS",
        "runtimeLog": str(test_log),
        "runtimeLogSha256": sha256(test_log),
        "swiftLog": str(swift_log),
        "swiftLogSha256": sha256(swift_log),
        "syntaxLog": str(syntax_log),
        "syntaxLogSha256": sha256(syntax_log),
    }


def export_patch(repo_path: Path, base_sha: str, target: Path) -> None:
    result = run(["git", "format-patch", "--stdout", f"{base_sha}..HEAD"], cwd=repo_path, timeout=120)
    require(result, "FORMAT_PATCH")
    target.write_text(result["stdout"] + "\n", encoding="utf-8")


def clean(repo_path: Path) -> bool:
    return git(repo_path, "status", "--porcelain") == ""


def perform() -> dict[str, Any]:
    fabric = load_fabric()
    accepted_control = load_accepted_control_candidate()
    run_dir = EVIDENCE_ROOT / stamp()
    workspace = run_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)

    control_name = "engurulabory/Engurulaboratuvari"
    product_name = "engurulabory/enguru-mac-engineer"
    control_record = repo_record(fabric, control_name)
    product_record = repo_record(fabric, product_name)

    control_mirror = MIRROR_ROOT / "Engurulaboratuvari.git"
    product_mirror = MIRROR_ROOT / "enguru-mac-engineer.git"
    control_mirror_main = mirror_main(control_mirror)
    product_base = mirror_main(product_mirror)
    control_base = str(accepted_control["head"])

    if control_mirror_main != control_record.get("observedMain"):
        raise RuntimeError("CONTROL_MIRROR_FABRIC_MAIN_PARITY_REQUIRED")
    if product_base != product_record.get("observedMain"):
        raise RuntimeError("PRODUCT_MIRROR_FABRIC_PARITY_REQUIRED")
    if str(accepted_control["originMain"]) != control_mirror_main:
        raise RuntimeError("ACCEPTED_CONTROL_ORIGIN_MAIN_FABRIC_PARITY_REQUIRED")
    if not mirror_has_commit(control_mirror, control_base):
        raise RuntimeError("ACCEPTED_CONTROL_HEAD_NOT_PRESENT_IN_LOCAL_MIRROR")

    control_mirror_before = control_mirror_main
    product_mirror_before = product_base

    control = workspace / "Engurulaboratuvari"
    product = workspace / "enguru-mac-engineer"
    clone_from_mirror(control_mirror, control, control_base)
    clone_from_mirror(product_mirror, product, product_base)

    control_commit, control_manifest = commit_probe(
        control, control_name, product_name, control_base
    )
    product_commit, product_manifest = commit_probe(
        product, product_name, control_name, product_base
    )

    control_contract = json.loads(control_manifest.read_text(encoding="utf-8"))
    product_contract = json.loads(product_manifest.read_text(encoding="utf-8"))
    if control_contract["taskId"] != product_contract["taskId"] or control_contract["taskId"] != TASK_ID:
        raise RuntimeError("CROSS_REPO_TASK_ID_PARITY_REQUIRED")
    if control_contract["peerRepository"] != product_name:
        raise RuntimeError("CONTROL_PEER_IDENTITY_REQUIRED")
    if product_contract["peerRepository"] != control_name:
        raise RuntimeError("PRODUCT_PEER_IDENTITY_REQUIRED")

    control_verify = control_plane_verify(control, run_dir)
    product_verify_result = product_verify(product, run_dir)

    if not clean(control) or not clean(product):
        raise RuntimeError("FIELD_PROOF_WORKTREES_CLEAN_REQUIRED")

    control_patch = run_dir / "Engurulaboratuvari.patch"
    product_patch = run_dir / "enguru-mac-engineer.patch"
    export_patch(control, control_base, control_patch)
    export_patch(product, product_base, product_patch)

    control_mirror_after = mirror_main(control_mirror)
    product_mirror_after = mirror_main(product_mirror)
    mirrors_unchanged = (
        control_mirror_after == control_mirror_before
        and product_mirror_after == product_mirror_before
    )
    if not mirrors_unchanged:
        raise RuntimeError("RECOVERY_MIRRORS_MUST_REMAIN_UNCHANGED")

    shutil.rmtree(workspace)

    payload = {
        "schema": "enguru.mac-engineer.mac-native-authority-migration-field-proof/v1",
        "observedAt": now(),
        "state": "PASS",
        "taskId": TASK_ID,
        "scope": "MULTI_REPOSITORY_LOCAL_END_TO_END_FIELD_PROOF",
        "networkRequired": False,
        "remotePush": False,
        "remoteMerge": False,
        "secondCanonicalTruthCreated": False,
        "repositories": {
            control_name: {
                "baseSha": control_base,
                "acceptedCandidateBranch": accepted_control["branch"],
                "acceptedCandidateOriginMain": accepted_control["originMain"],
                "acceptedCandidateEvidence": accepted_control.get("evidence"),
                "sourceAuthority": "LOCAL_ACCEPTED_CANDIDATE_PENDING_RECONCILIATION",
                "localProofCommit": control_commit,
                "patch": str(control_patch),
                "patchSha256": sha256(control_patch),
                "verification": control_verify,
            },
            product_name: {
                "baseSha": product_base,
                "localProofCommit": product_commit,
                "patch": str(product_patch),
                "patchSha256": sha256(product_patch),
                "verification": product_verify_result,
            },
        },
        "crossRepositoryTaskIdentity": "PASS",
        "repositoryFabric": "12_OF_12_PASS",
        "executionSource": "FRESH_OPERATOR_GITVAULT_MIRRORS",
        "gitVaultMirrorsUnchanged": mirrors_unchanged,
        "localCommitQueue": "2_LOCAL_COMMITS_NOT_PUSHED",
        "evidenceContinuity": "PASS",
        "authority": (
            "FIELD_PROOF_ONLY. Local commits were executed from verified local mirrors, "
            "captured as patches/Evidence, and discarded after verification. Canonical "
            "remote refs and recovery mirrors remain unchanged."
        ),
        "nextAction": "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF",
    }
    evidence = run_dir / "evidence.json"
    payload["evidencePath"] = str(evidence)
    evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "receipt.txt").write_text(
        "\n".join([
            "STATE=PASS",
            f"TASK_ID={TASK_ID}",
            "MULTI_REPO=PASS",
            "CONTROL_PLANE_REGRESSION=PASS",
            "PRODUCT_REGRESSION=PASS",
            "NATIVE_BUILD=PASS",
            "GITVAULT_MIRRORS_UNCHANGED=PASS",
            "REMOTE_PUSH=false",
            "SECOND_CANONICAL_TRUTH=false",
            f"EVIDENCE={evidence}",
            "NEXT_ACTION=MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF",
        ]) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    try:
        payload = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_MAC_NATIVE_AUTHORITY_FIELD_PROOF")
        return 2

    print("STATE=PASS")
    print(f"TASK_ID={payload['taskId']}")
    print("MULTI_REPO=PASS")
    print("CONTROL_PLANE_REGRESSION=PASS")
    print("PRODUCT_REGRESSION=PASS")
    print("NATIVE_BUILD=PASS")
    print("GITVAULT_MIRRORS_UNCHANGED=PASS")
    print("REMOTE_PUSH=false")
    print("SECOND_CANONICAL_TRUTH=false")
    print(f"EVIDENCE={payload['evidencePath']}")
    print(f"NEXT_ACTION={payload['nextAction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
