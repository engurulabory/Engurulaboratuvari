#!/usr/bin/env python3
"""Read-only OSi binding over the canonical control-plane Steward."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = (
    ROOT
    / "governance"
    / "osi-runtime"
    / "ENGURU_OSI_STEWARD_BINDING_V1.json"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )


def node_executable() -> str:
    discovered = shutil.which("node")
    if discovered:
        return discovered
    for candidate in (Path("/opt/homebrew/bin/node"), Path("/usr/local/bin/node")):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError("NODE_RUNTIME_REQUIRED")


def require(command: list[str], *, cwd: Path, label: str) -> str:
    result = run(command, cwd=cwd)
    if result.returncode != 0:
        message = (result.stdout + "\n" + result.stderr)[-3000:]
        raise RuntimeError(f"{label}_FAILED:{message}")
    return result.stdout.strip()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def git_object(repo: Path, spec: str) -> str:
    return require(["git", "rev-parse", spec], cwd=repo, label="GIT_OBJECT")


def status_bytes(repo: Path) -> bytes:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repo,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError("GIT_STATUS_FAILED")
    return result.stdout


def validate_binding(binding: dict[str, Any]) -> None:
    if binding.get("schema") != "enguru.osi-runtime.steward-binding/v1":
        raise RuntimeError("STEWARD_BINDING_SCHEMA_MISMATCH")
    boundary = binding.get("authorityBoundary") or {}
    operator = binding.get("operator") or {}
    if boundary.get("canonicalStewardCount") != 1:
        raise RuntimeError("CANONICAL_STEWARD_COUNT_INVALID")
    if boundary.get("secondStewardAllowed") is not False:
        raise RuntimeError("SECOND_STEWARD_AUTHORITY_REJECTED")
    if operator.get("mode") != "READ_ONLY_INSPECT_AND_PLAN":
        raise RuntimeError("STEWARD_OPERATOR_MODE_INVALID")
    if operator.get("mutationAllowed") is not False:
        raise RuntimeError("STEWARD_MUTATION_AUTHORITY_REJECTED")
    if binding.get("builderLineage", {}).get("canonicalAuthority") is not False:
        raise RuntimeError("BUILDER_LINEAGE_AUTHORITY_REJECTED")


def inspect(*, repo: Path = ROOT, binding_path: Path = BINDING_PATH) -> dict[str, Any]:
    repo = repo.resolve()
    if repo != ROOT.resolve():
        raise RuntimeError("STEWARD_SCOPE_OUTSIDE_CANONICAL_REPOSITORY")
    binding = load_json(binding_path)
    validate_binding(binding)
    source = binding["canonicalSource"]
    before = status_bytes(repo)
    head = git_object(repo, "HEAD")
    local_tree = git_object(repo, f"HEAD:{source['path']}")
    main_tree = git_object(repo, f"{source['observedMainHead']}:{source['path']}")
    workflow_blob = git_object(repo, f"HEAD:{source['scheduledWorkflow']}")
    expected_tree = source["tree"]
    expected_workflow = source["scheduledWorkflowBlob"]

    parity_reasons = []
    if local_tree != expected_tree:
        parity_reasons.append("LOCAL_STEWARD_TREE_DRIFT")
    if main_tree != expected_tree:
        parity_reasons.append("RECORDED_MAIN_STEWARD_TREE_DRIFT")
    if workflow_blob != expected_workflow:
        parity_reasons.append("SCHEDULED_WORKFLOW_DRIFT")

    cycle_result = run(
        [node_executable(), "steward/run-scheduled-cycle.mjs"],
        cwd=repo,
    )
    if cycle_result.returncode not in {0, 3}:
        raise RuntimeError(
            "STEWARD_CYCLE_EXECUTION_FAILED:"
            + (cycle_result.stdout + "\n" + cycle_result.stderr)[-3000:]
        )
    cycle = json.loads(cycle_result.stdout)
    # Steward v1.2 emits an explicit, read-only authority/write boundary.
    # Validate the raw runtime receipt before projecting the legacy field.
    if (
        cycle.get("schemaVersion") != "1.2"
        or cycle.get("sourceCommit") != head
        or cycle.get("mode") != "READ_ONLY_SCHEDULED_CYCLE"
        or cycle.get("authority") != "INSPECT_AND_PLAN"
        or cycle.get("writeBoundary") != "PRESERVED"
        or cycle.get("scorecard", {}).get("repairsApplied") != 0
    ):
        raise RuntimeError("STEWARD_V12_READ_ONLY_CYCLE_CONTRACT_DRIFT")
    cycle = dict(cycle)
    # Compatibility projection; canonical upstream receipt is unchanged.
    # This describes allowed authority, not a fabricated field observation.
    cycle["destructiveActionsAllowed"] = False
    after = status_bytes(repo)
    worktree_preserved = before == after
    reasons = list(parity_reasons)
    if not worktree_preserved:
        reasons.append("WORKTREE_MUTATED_BY_STEWARD")
    if cycle.get("state") == "BLOCKED":
        reasons.append("STEWARD_CYCLE_BLOCKED")

    state = "PASS" if not reasons else "HOLD"
    return {
        "schema": "enguru.osi-runtime.steward-inspection/v1",
        "state": state,
        "observedAt": now(),
        "bindingId": binding["bindingId"],
        "mode": "READ_ONLY_INSPECT_AND_PLAN",
        "repository": source["repository"],
        "head": head,
        "canonicalSource": {
            "path": source["path"],
            "expectedTree": expected_tree,
            "localTree": local_tree,
            "recordedMainTree": main_tree,
            "treeParity": "PASS" if not parity_reasons else "HOLD",
            "scheduledWorkflowBlob": workflow_blob,
        },
        "builderLineage": {
            "repository": binding["builderLineage"]["repository"],
            "tree": binding["builderLineage"]["tree"],
            "role": binding["builderLineage"]["role"],
            "canonicalAuthority": False,
            "copiedIntoCanonical": False,
        },
        "cycle": cycle,
        "safeHygienePlan": {
            "mode": "PLAN_ONLY",
            "applied": False,
            "findings": cycle.get("findings", []),
            "humanThresholdRequired": bool(cycle.get("findings")),
        },
        "worktree": {
            "beforeDigest": digest_bytes(before),
            "afterDigest": digest_bytes(after),
            "preserved": worktree_preserved,
            "preExistingChangesPreserved": True,
        },
        "authority": {
            "canonicalStewardCount": 1,
            "secondStewardCreated": False,
            "mutationAllowed": False,
            "destructiveActionPerformed": False,
            "humanThresholdPreserved": True,
        },
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="enguru-steward")
    parser.add_argument("--inspect", action="store_true", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--binding", type=Path, default=BINDING_PATH, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        receipt = inspect(repo=args.repo, binding_path=args.binding)
    except (RuntimeError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"STATE=HOLD\nREASON={exc}", file=sys.stderr)
        return 20
    if args.output:
        atomic_json(args.output.expanduser().resolve(), receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["state"] == "PASS" else 20


if __name__ == "__main__":
    raise SystemExit(main())
