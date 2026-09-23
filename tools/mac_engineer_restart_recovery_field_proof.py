#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ — Gate 9 restart/recovery continuity field proof.

Proves one governed task across a real Python process boundary using the
canonical product ReliabilityManager sourced from the local GitVault mirror.

Parent flow:
  local GitVault exact-main clone
  -> process A: create task + one durable effect + verified checkpoint
  -> controlled process exit
  -> process B: reopen durable state + duplicate begin + resume same task
  -> suppress duplicate effect + verify + COMPLETE
  -> Evidence reconciliation

No network, push, merge, or canonical source mutation is performed.
"""
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

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
PRODUCT_MIRROR = HOME / "Enguru" / "GitVault" / "MacEngineer" / "enguru-mac-engineer.git"
EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.7"
    / "restart-recovery-continuity"
)

IDEMPOTENCY_KEY = "ENGURU-V07-MAC-NATIVE-RESTART-001"
EFFECT_KEY = "ENGURU-V07-DURABLE-EFFECT-001"
CONTROLLED_INTERRUPTION_EXIT = 75


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
        tail = (
            str(result.get("stdout") or "")
            + "\n"
            + str(result.get("stderr") or "")
        )[-5000:]
        raise RuntimeError(f"{label}_FAILED:{tail}")


def git_output(mirror_or_repo: Path, args: list[str], *, bare: bool = False) -> str:
    cmd = ["git"]
    if bare:
        cmd.extend(["--git-dir", str(mirror_or_repo)])
    cmd.extend(args)
    result = run(cmd, cwd=None if bare else mirror_or_repo, timeout=120)
    require(result, "GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_json(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def product_exact_main() -> str:
    data = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
    current = data.get("currentV07") or {}
    value = str(current.get("productExactMain") or "").strip()
    if len(value) != 40:
        raise RuntimeError("PRODUCT_EXACT_MAIN_REQUIRED")
    return value


def mirror_remote_main() -> str:
    return git_output(
        PRODUCT_MIRROR,
        ["rev-parse", "refs/remotes/origin/main"],
        bare=True,
    )


def mirror_has_commit(sha: str) -> bool:
    result = run(
        [
            "git",
            "--git-dir",
            str(PRODUCT_MIRROR),
            "cat-file",
            "-e",
            f"{sha}^{{commit}}",
        ],
        timeout=60,
    )
    return result["code"] == 0


def clone_exact_product(target: Path, expected_sha: str) -> None:
    if not PRODUCT_MIRROR.is_dir():
        raise RuntimeError("PRODUCT_GITVAULT_MIRROR_REQUIRED")
    if not mirror_has_commit(expected_sha):
        raise RuntimeError("PRODUCT_EXACT_MAIN_NOT_IN_GITVAULT")
    result = run(
        ["git", "clone", "--no-local", str(PRODUCT_MIRROR), str(target)],
        timeout=1200,
    )
    require(result, "PRODUCT_LOCAL_CLONE")
    checkout = run(
        ["git", "checkout", "--detach", expected_sha],
        cwd=target,
        timeout=120,
    )
    require(checkout, "PRODUCT_EXACT_SHA_CHECKOUT")
    observed = git_output(target, ["rev-parse", "HEAD"])
    if observed != expected_sha:
        raise RuntimeError("PRODUCT_EXACT_SHA_PARITY_REQUIRED")


def load_reliability(runtime_root: Path):
    sys.path.insert(0, str(runtime_root))
    try:
        from reliability import ReliabilityManager
    except Exception as exc:
        raise RuntimeError(
            f"CANONICAL_RELIABILITY_IMPORT_FAILED:{type(exc).__name__}:{exc}"
        ) from exc
    return ReliabilityManager


def effect_path(durable_root: Path) -> Path:
    return durable_root / "effects" / f"{EFFECT_KEY}.json"


def apply_effect_once(durable_root: Path, task_id: str) -> tuple[bool, dict[str, Any]]:
    path = effect_path(durable_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "enguru.mac-engineer.restart-recovery-effect/v1",
        "effectKey": EFFECT_KEY,
        "taskId": task_id,
        "value": "APPLIED_ONCE",
    }
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        return False, existing

    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return True, payload


def phase_start(
    *,
    runtime_root: Path,
    durable_root: Path,
    receipt_path: Path,
) -> int:
    ReliabilityManager = load_reliability(runtime_root)
    manager = ReliabilityManager(durable_root)

    created = manager.begin(
        IDEMPOTENCY_KEY,
        metadata={
            "gate": "GATE_9",
            "proof": "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY",
        },
    )
    if created.get("duplicate") is not False:
        raise RuntimeError("PHASE_START_NEW_TASK_REQUIRED")

    task_id = str(created["task"]["task_id"])
    manager.transition(task_id, "RUNNING")

    effect_created, effect = apply_effect_once(durable_root, task_id)
    if not effect_created:
        raise RuntimeError("PHASE_START_EFFECT_MUST_BE_NEW")

    effect_digest = digest_json(effect)
    checkpoint = manager.checkpoint(
        task_id,
        {
            "gate": "GATE_9",
            "phase": "BEFORE_RESTART",
            "effectKey": EFFECT_KEY,
            "effectDigest": effect_digest,
            "restartSequence": 0,
        },
        verified=True,
    )
    task = manager.get(task_id)
    if task.get("state") != "CHECKPOINTED":
        raise RuntimeError("PHASE_START_CHECKPOINTED_REQUIRED")

    receipt = {
        "schema": "enguru.mac-engineer.restart-recovery-phase/v1",
        "state": "CONTROLLED_INTERRUPTION",
        "phase": "START",
        "taskId": task_id,
        "idempotencyKey": IDEMPOTENCY_KEY,
        "effectKey": EFFECT_KEY,
        "effectCreated": True,
        "effectDigest": effect_digest,
        "checkpointDigest": checkpoint["payload_digest"],
        "checkpointVerified": checkpoint["verified"],
        "taskState": task["state"],
        "processId": os.getpid(),
        "next": "PROCESS_RESTART_AND_RESUME",
    }
    atomic_json(receipt_path, receipt)
    print(f"TASK_ID={task_id}")
    print("PHASE=START")
    print("CHECKPOINT=PASS")
    print("EFFECT_CREATED=true")
    print("CONTROLLED_INTERRUPTION=PASS")
    return CONTROLLED_INTERRUPTION_EXIT


def phase_resume(
    *,
    runtime_root: Path,
    durable_root: Path,
    receipt_path: Path,
    expected_task_id: str,
) -> int:
    ReliabilityManager = load_reliability(runtime_root)
    manager = ReliabilityManager(durable_root)

    replay = manager.begin(
        IDEMPOTENCY_KEY,
        metadata={"gate": "GATE_9_REPLAY"},
    )
    if replay.get("duplicate") is not True:
        raise RuntimeError("PHASE_RESUME_DUPLICATE_REQUIRED")

    task_id = str(replay["task"]["task_id"])
    if task_id != expected_task_id:
        raise RuntimeError("TASK_IDENTITY_CHANGED_AFTER_RESTART")

    checkpoint_before = manager.load_checkpoint(task_id)
    if not checkpoint_before.get("ok"):
        raise RuntimeError("VERIFIED_CHECKPOINT_REQUIRED_AFTER_RESTART")
    payload_before = checkpoint_before["checkpoint"]["payload"]
    if payload_before.get("phase") != "BEFORE_RESTART":
        raise RuntimeError("BEFORE_RESTART_CHECKPOINT_REQUIRED")

    effect_created, effect = apply_effect_once(durable_root, task_id)
    if effect_created:
        raise RuntimeError("DUPLICATE_DURABLE_EFFECT_CREATED")
    if effect.get("taskId") != task_id or effect.get("effectKey") != EFFECT_KEY:
        raise RuntimeError("DURABLE_EFFECT_IDENTITY_MISMATCH")
    effect_digest = digest_json(effect)
    if effect_digest != payload_before.get("effectDigest"):
        raise RuntimeError("DURABLE_EFFECT_DIGEST_MISMATCH")

    resumed = manager.resume(task_id)
    if not resumed.get("ok"):
        raise RuntimeError(
            "RESUME_REQUIRED:"
            + str(resumed.get("classification"))
            + ":"
            + str(resumed.get("reason"))
        )
    if resumed["task"]["task_id"] != task_id:
        raise RuntimeError("RESUMED_TASK_IDENTITY_MISMATCH")

    checkpoint_after = manager.checkpoint(
        task_id,
        {
            "gate": "GATE_9",
            "phase": "AFTER_RESTART",
            "effectKey": EFFECT_KEY,
            "effectDigest": effect_digest,
            "restartSequence": 1,
            "resumedFromDigest": checkpoint_before["checkpoint"]["payload_digest"],
        },
        verified=True,
    )
    manager.transition(task_id, "VERIFYING")
    final_task = manager.transition(task_id, "COMPLETE")

    if final_task.get("state") != "COMPLETE":
        raise RuntimeError("FINAL_COMPLETE_REQUIRED")

    receipt = {
        "schema": "enguru.mac-engineer.restart-recovery-phase/v1",
        "state": "PASS",
        "phase": "RESUME",
        "taskId": task_id,
        "sameTaskIdentity": True,
        "duplicateBegin": True,
        "effectKey": EFFECT_KEY,
        "effectCreated": False,
        "exactlyOnceEffect": True,
        "effectDigest": effect_digest,
        "checkpointBeforeDigest": checkpoint_before["checkpoint"]["payload_digest"],
        "checkpointAfterDigest": checkpoint_after["payload_digest"],
        "checkpointVerified": checkpoint_after["verified"],
        "restartSequence": 1,
        "finalState": final_task["state"],
        "processId": os.getpid(),
    }
    atomic_json(receipt_path, receipt)
    print(f"TASK_ID={task_id}")
    print("PHASE=RESUME")
    print("TASK_IDENTITY=PASS")
    print("CHECKPOINT_RESUME=PASS")
    print("EXACTLY_ONCE_EFFECT=PASS")
    print("FINAL_STATE=COMPLETE")
    return 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def reconcile_journal(durable_root: Path, task_id: str) -> dict[str, Any]:
    journal = durable_root / "logs" / "task-journal.jsonl"
    if not journal.is_file():
        raise RuntimeError("TASK_JOURNAL_REQUIRED")
    rows = [
        json.loads(line)
        for line in journal.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    task_rows = [row for row in rows if row.get("task_id") == task_id]
    create_commits = [
        row
        for row in task_rows
        if row.get("phase") == "COMMIT" and row.get("op") == "CREATE_TASK"
    ]
    checkpoint_commits = [
        row
        for row in task_rows
        if row.get("phase") == "COMMIT" and row.get("op") == "CHECKPOINT"
    ]
    complete_commits = [
        row
        for row in task_rows
        if (
            row.get("phase") == "COMMIT"
            and row.get("op") == "TRANSITION"
            and row.get("state") == "COMPLETE"
        )
    ]
    if len(create_commits) != 1:
        raise RuntimeError(f"ONE_TASK_CREATE_COMMIT_REQUIRED:{len(create_commits)}")
    if len(checkpoint_commits) != 2:
        raise RuntimeError(
            f"TWO_CHECKPOINT_COMMITS_REQUIRED:{len(checkpoint_commits)}"
        )
    if len(complete_commits) != 1:
        raise RuntimeError(f"ONE_COMPLETE_COMMIT_REQUIRED:{len(complete_commits)}")
    return {
        "taskRows": len(task_rows),
        "createCommits": len(create_commits),
        "checkpointCommits": len(checkpoint_commits),
        "completeCommits": len(complete_commits),
        "journal": str(journal),
        "journalSha256": sha256_file(journal),
    }


def perform() -> dict[str, Any]:
    expected_main = product_exact_main()
    if not PRODUCT_MIRROR.is_dir():
        raise RuntimeError("PRODUCT_GITVAULT_MIRROR_REQUIRED")

    mirror_before = mirror_remote_main()
    if mirror_before != expected_main:
        raise RuntimeError(
            f"PRODUCT_GITVAULT_REMOTE_MAIN_PARITY_REQUIRED:{mirror_before}:{expected_main}"
        )

    run_dir = EVIDENCE_ROOT / stamp()
    workspace = run_dir / "workspace"
    product = workspace / "enguru-mac-engineer"
    durable_root = run_dir / "durable-runtime"
    start_receipt = run_dir / "phase-start.json"
    resume_receipt = run_dir / "phase-resume.json"
    workspace.mkdir(parents=True, exist_ok=False)

    clone_exact_product(product, expected_main)
    runtime_root = product / "runtime"
    if not (runtime_root / "reliability.py").is_file():
        raise RuntimeError("CANONICAL_RELIABILITY_RUNTIME_REQUIRED")

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    script = str(Path(__file__).resolve())

    start = run(
        [
            sys.executable,
            "-B",
            script,
            "--phase",
            "start",
            "--runtime-root",
            str(runtime_root),
            "--durable-root",
            str(durable_root),
            "--receipt",
            str(start_receipt),
        ],
        cwd=ROOT,
        timeout=600,
        env=env,
    )
    if start["code"] != CONTROLLED_INTERRUPTION_EXIT:
        raise RuntimeError(
            "CONTROLLED_INTERRUPTION_EXIT_REQUIRED:"
            + str(start["code"])
            + ":"
            + (start["stdout"] + "\n" + start["stderr"])[-4000:]
        )
    first = load_json(start_receipt)
    task_id = str(first.get("taskId") or "")
    if not task_id or first.get("checkpointVerified") is not True:
        raise RuntimeError("PHASE_START_RECEIPT_INVALID")

    resume = run(
        [
            sys.executable,
            "-B",
            script,
            "--phase",
            "resume",
            "--runtime-root",
            str(runtime_root),
            "--durable-root",
            str(durable_root),
            "--receipt",
            str(resume_receipt),
            "--expected-task-id",
            task_id,
        ],
        cwd=ROOT,
        timeout=600,
        env=env,
    )
    require(resume, "RESTART_RESUME_PROCESS")
    second = load_json(resume_receipt)

    if second.get("taskId") != task_id or second.get("sameTaskIdentity") is not True:
        raise RuntimeError("TASK_IDENTITY_CONTINUITY_REQUIRED")
    if second.get("exactlyOnceEffect") is not True:
        raise RuntimeError("EXACTLY_ONCE_EFFECT_REQUIRED")
    if second.get("finalState") != "COMPLETE":
        raise RuntimeError("FINAL_COMPLETE_REQUIRED")

    effects = sorted((durable_root / "effects").glob("*.json"))
    if len(effects) != 1:
        raise RuntimeError(f"ONE_DURABLE_EFFECT_FILE_REQUIRED:{len(effects)}")
    effect = load_json(effects[0])
    if effect.get("taskId") != task_id or effect.get("effectKey") != EFFECT_KEY:
        raise RuntimeError("DURABLE_EFFECT_RECONCILIATION_FAILED")

    task_path = durable_root / "tasks" / f"{task_id}.json"
    task = load_json(task_path)
    if task.get("state") != "COMPLETE":
        raise RuntimeError("DURABLE_FINAL_TASK_COMPLETE_REQUIRED")

    checkpoint_path = durable_root / "checkpoints" / f"{task_id}.json"
    checkpoint = load_json(checkpoint_path)
    if (checkpoint.get("payload") or {}).get("phase") != "AFTER_RESTART":
        raise RuntimeError("AFTER_RESTART_CHECKPOINT_REQUIRED")

    journal = reconcile_journal(durable_root, task_id)

    product_status = git_output(product, ["status", "--porcelain"])
    if product_status:
        raise RuntimeError("DISPOSABLE_PRODUCT_SOURCE_CHANGED")

    mirror_after = mirror_remote_main()
    if mirror_after != mirror_before:
        raise RuntimeError("PRODUCT_GITVAULT_MIRROR_CHANGED")

    phase_processes_distinct = (
        isinstance(first.get("processId"), int)
        and isinstance(second.get("processId"), int)
        and first["processId"] != second["processId"]
    )
    if not phase_processes_distinct:
        raise RuntimeError("DISTINCT_PROCESS_RESTART_REQUIRED")

    shutil.rmtree(workspace)

    payload = {
        "schema": "enguru.mac-engineer.mac-native-restart-recovery-field-proof/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": 9,
        "taskId": task_id,
        "idempotencyKey": IDEMPOTENCY_KEY,
        "effectKey": EFFECT_KEY,
        "productSourceSha": expected_main,
        "productSource": "LOCAL_GITVAULT_EXACT_MAIN",
        "networkRequired": False,
        "remotePush": False,
        "processRestart": "PASS",
        "distinctProcessBoundary": True,
        "taskIdentityContinuity": "PASS",
        "checkpointResume": "PASS",
        "exactlyOnceDurableEffect": "PASS",
        "durableEffectCount": 1,
        "finalTaskState": "COMPLETE",
        "gitVaultMirrorUnchanged": True,
        "journalReconciliation": journal,
        "phaseStart": {
            "receipt": str(start_receipt),
            "sha256": sha256_file(start_receipt),
            "processId": first["processId"],
            "controlledExitCode": CONTROLLED_INTERRUPTION_EXIT,
        },
        "phaseResume": {
            "receipt": str(resume_receipt),
            "sha256": sha256_file(resume_receipt),
            "processId": second["processId"],
        },
        "durableState": {
            "root": str(durable_root),
            "task": str(task_path),
            "taskSha256": sha256_file(task_path),
            "checkpoint": str(checkpoint_path),
            "checkpointSha256": sha256_file(checkpoint_path),
            "effect": str(effects[0]),
            "effectSha256": sha256_file(effects[0]),
        },
        "authority": (
            "REAL_MAC_LOCAL_PROCESS_RESTART_FIELD_EVIDENCE. "
            "The canonical product ReliabilityManager was loaded from the exact "
            "GitVault product main source. No network or remote mutation occurred."
        ),
        "nextAction": "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF",
    }
    evidence = run_dir / "evidence.json"
    payload["evidencePath"] = str(evidence)
    atomic_json(evidence, payload)
    receipt = run_dir / "receipt.txt"
    receipt.write_text(
        "\n".join(
            [
                "STATE=PASS",
                f"TASK_ID={task_id}",
                "PROCESS_RESTART=PASS",
                "TASK_IDENTITY=PASS",
                "CHECKPOINT_RESUME=PASS",
                "EXACTLY_ONCE_EFFECT=PASS",
                "FINAL_STATE=COMPLETE",
                "GITVAULT_MIRROR_UNCHANGED=PASS",
                "REMOTE_PUSH=false",
                f"EVIDENCE={evidence}",
                "NEXT_ACTION=MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["parent", "start", "resume"], default="parent")
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--durable-root", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expected-task-id")
    args = parser.parse_args()

    try:
        if args.phase == "start":
            if not args.runtime_root or not args.durable_root or not args.receipt:
                raise RuntimeError("PHASE_START_ARGUMENTS_REQUIRED")
            return phase_start(
                runtime_root=args.runtime_root,
                durable_root=args.durable_root,
                receipt_path=args.receipt,
            )

        if args.phase == "resume":
            if (
                not args.runtime_root
                or not args.durable_root
                or not args.receipt
                or not args.expected_task_id
            ):
                raise RuntimeError("PHASE_RESUME_ARGUMENTS_REQUIRED")
            return phase_resume(
                runtime_root=args.runtime_root,
                durable_root=args.durable_root,
                receipt_path=args.receipt,
                expected_task_id=args.expected_task_id,
            )

        payload = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_MAC_NATIVE_RESTART_RECOVERY_PROOF")
        return 2

    print("STATE=PASS")
    print(f"TASK_ID={payload['taskId']}")
    print("PROCESS_RESTART=PASS")
    print("TASK_IDENTITY=PASS")
    print("CHECKPOINT_RESUME=PASS")
    print("EXACTLY_ONCE_EFFECT=PASS")
    print("FINAL_STATE=COMPLETE")
    print("GITVAULT_MIRROR_UNCHANGED=PASS")
    print("REMOTE_PUSH=false")
    print(f"EVIDENCE={payload['evidencePath']}")
    print(f"NEXT_ACTION={payload['nextAction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
