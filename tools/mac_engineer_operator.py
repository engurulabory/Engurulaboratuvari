#!/usr/bin/env python3
"""Minimal operator surface for ENGÜRÜ Mac Engineer™ on OSi."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
ENGURU = HOME / "Enguru"
PRODUCT = ENGURU / "Projects" / "enguru-mac-engineer"
RUNTIME = ENGURU / "Runtime" / "MacEngineer"
EVIDENCE = ENGURU / "Evidence" / "MacEngineer" / "operator"
RUNTIME_RECEIPTS = RUNTIME / "state" / "operator"
GITVAULT = ENGURU / "GitVault" / "MacEngineer"
RUNNER_HOME = Path(
    os.environ.get(
        "ENGURU_GITHUB_RUNNER_HOME",
        str(ENGURU / "Runtime" / "GitHubRunner" / "enguru-mac-engineer"),
    )
).expanduser()

SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance" / "mac-engineer" / "PRODUCT_ROADMAP_V1.json"
ACTION_REGISTRY = ROOT / "governance" / "mac-engineer" / "OPERATOR_ACTION_REGISTRY_V1.json"
CONTROL = ROOT / "tools" / "mac_engineer_control.py"
A10_ACCEPTANCE = ROOT / "governance" / "mac-engineer" / "V07_A10_DONECHECK_V12_ACCEPTANCE.command"
LOCAL_FINISHER_REHEARSAL = ROOT / "governance" / "mac-engineer" / "V07_LOCAL_FINISHER_REHEARSAL.command"
MAC_NATIVE_AUTHORITY_FIELD_PROOF = ROOT / "governance" / "mac-engineer" / "V07_MAC_NATIVE_AUTHORITY_FIELD_PROOF.command"
MAC_NATIVE_RESTART_RECOVERY_PROOF = ROOT / "governance" / "mac-engineer" / "V07_MAC_NATIVE_RESTART_RECOVERY_PROOF.command"
MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF = ROOT / "governance" / "mac-engineer" / "V07_MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF.command"

TERMINAL_STATES = {"COMPLETE", "HOLD", "FAILED", "BLOCKED"}
RECOVERABLE_STATES = {"RUNNING", "CHECKPOINTED", "RECOVERY_REQUIRED", "VERIFYING"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
            env=env,
        )
        return {
            "code": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "code": 124,
            "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
            "stderr": "TIMEOUT",
        }
    except Exception as exc:
        return {
            "code": 125,
            "stdout": "",
            "stderr": f"{type(exc).__name__}:{exc}",
        }


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def git_state(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False, "path": str(path)}
    commands = {
        "head": ["git", "rev-parse", "HEAD"],
        "branch": ["git", "branch", "--show-current"],
        "origin_main": ["git", "rev-parse", "origin/main"],
        "status": ["git", "status", "--porcelain"],
        "ahead_origin_main": ["git", "rev-list", "--count", "origin/main..HEAD"],
    }
    out: dict[str, Any] = {"available": True, "path": str(path)}
    for key, cmd in commands.items():
        result = run(cmd, cwd=path, timeout=30)
        out[key] = result["stdout"] if result["code"] == 0 else None
    out["clean"] = out.get("status") == ""
    out["exact_origin_main"] = bool(
        out.get("head")
        and out.get("origin_main")
        and out["head"] == out["origin_main"]
    )
    return out


def sync_repo_online(path: Path) -> dict[str, Any]:
    state = git_state(path)
    if not state.get("available"):
        return {"state": "HOLD", "mode": "LOCAL_MISSING", "path": str(path)}
    fetch = run(["git", "fetch", "origin", "main", "--prune"], cwd=path, timeout=120)
    if fetch["code"] != 0:
        return {
            "state": "PASS",
            "mode": "OFFLINE_CACHED",
            "path": str(path),
            "fetch_error": fetch["stderr"],
        }
    refreshed = git_state(path)
    if refreshed.get("branch") == "main" and refreshed.get("clean") is True:
        ff = run(["git", "merge", "--ff-only", "origin/main"], cwd=path, timeout=60)
        return {
            "state": "PASS" if ff["code"] == 0 else "HOLD",
            "mode": "ONLINE_FF_ONLY",
            "path": str(path),
            "fast_forward_code": ff["code"],
            "fast_forward_error": ff["stderr"] if ff["code"] else None,
        }
    return {
        "state": "PASS",
        "mode": "ONLINE_WORKING_BRANCH_PRESERVED",
        "path": str(path),
        "branch": refreshed.get("branch"),
        "clean": refreshed.get("clean"),
    }


def current_truth() -> dict[str, Any]:
    session = load_json(SESSION_STATE, {}) or {}
    roadmap = load_json(ROADMAP, {}) or {}
    current_v07 = session.get("currentV07") or {}
    v07_roadmap = next(
        (
            item
            for item in roadmap.get("versions", [])
            if item.get("version") == "v0.7"
        ),
        {},
    )
    return {
        "product": session.get("product") or roadmap.get("product", {}).get("canonicalName"),
        "current_version": roadmap.get("current", {}).get("version"),
        "current_state": roadmap.get("current", {}).get("state"),
        "active_objective": roadmap.get("current", {}).get("activeObjective"),
        "v07_state": current_v07.get("state") or v07_roadmap.get("state"),
        "next_action": current_v07.get("nextAction") or v07_roadmap.get("nextAction"),
        "a09_state": current_v07.get("a09State") or (v07_roadmap.get("a09") or {}).get("state"),
        "a09_candidate_sha": current_v07.get("a09LatestCandidateHead") or (v07_roadmap.get("a09") or {}).get("currentCandidateSha"),
        "local_fallback": current_v07.get("localFallback") or {},
        "local_continuity_next_action": current_v07.get("localContinuityNextAction"),
        "local_continuity_state": current_v07.get("localContinuityState"),
        "final_target": roadmap.get("finalTarget") or {},
    }


def runner_status() -> dict[str, Any]:
    configured = (RUNNER_HOME / ".runner").is_file()
    run_script = (RUNNER_HOME / "run.sh").is_file()
    service_script = (RUNNER_HOME / "svc.sh").is_file()
    ps = run(["ps", "-axo", "pid=,command="], timeout=10)
    listeners = []
    if ps["code"] == 0:
        for line in ps["stdout"].splitlines():
            low = line.lower()
            if "runner.listener" in low or (
                str(RUNNER_HOME).lower() in low and "runsvc" in low
            ):
                listeners.append(line.strip())
    state = "PASS" if configured and run_script and listeners else (
        "READY_TO_START" if configured and run_script else "UNCOMMISSIONED"
    )
    return {
        "state": state,
        "home": str(RUNNER_HOME),
        "configured": configured,
        "run_script": run_script,
        "service_script": service_script,
        "listener_count": len(listeners),
        "labels": ["self-hosted", "macOS", "ARM64", "enguru-mac"],
    }


def mirror_path(name: str) -> Path:
    return GITVAULT / f"{name}.git"


def _mirror_one(source: Path, name: str) -> dict[str, Any]:
    target = mirror_path(name)
    GITVAULT.mkdir(parents=True, exist_ok=True)
    if not (source / ".git").exists():
        return {"state": "HOLD", "reason": "SOURCE_GIT_REQUIRED", "path": str(target)}
    if not target.exists():
        result = run(
            ["git", "clone", "--mirror", str(source), str(target)],
            timeout=180,
        )
        action = "CREATED"
    else:
        result = run(
            [
                "git",
                "--git-dir",
                str(target),
                "fetch",
                "--prune",
                str(source),
                "+refs/*:refs/*",
            ],
            timeout=180,
        )
        action = "UPDATED"
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "action": action,
        "path": str(target),
        "authority": "RECOVERY_MIRROR_NOT_CANONICAL",
        "error": result["stderr"] if result["code"] else None,
    }


def sync_mirrors() -> dict[str, Any]:
    return {
        "control_plane": _mirror_one(ROOT, "Engurulaboratuvari"),
        "product": _mirror_one(PRODUCT, "enguru-mac-engineer"),
    }


def pending_reconciliation(path: Path) -> dict[str, Any]:
    state = git_state(path)
    if not state.get("available"):
        return {"state": "HOLD", "path": str(path), "commits": []}
    result = run(
        ["git", "rev-list", "--reverse", "origin/main..HEAD"],
        cwd=path,
        timeout=30,
    )
    commits = result["stdout"].splitlines() if result["code"] == 0 and result["stdout"] else []
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "path": str(path),
        "branch": state.get("branch"),
        "head": state.get("head"),
        "origin_main": state.get("origin_main"),
        "ahead": len(commits),
        "commits": commits,
        "authority": "PENDING_RECONCILIATION_NOT_CANONICAL",
    }


def offline_manifest() -> dict[str, Any]:
    return {
        "schema": "enguru.mac-engineer.offline-reconciliation/v1",
        "observed_at": now(),
        "control_plane": pending_reconciliation(ROOT),
        "product": pending_reconciliation(PRODUCT),
        "rule": (
            "Local commits preserve engineering continuity. GitHub canonical authority "
            "is restored by explicit reconciliation; local mirrors do not create a second truth."
        ),
    }


def latest_matching_fallback(candidate_sha: str | None) -> dict[str, Any] | None:
    if not candidate_sha:
        return None
    root = ENGURU / "Evidence" / "MacEngineer" / "v0.7"
    if not root.is_dir():
        return None
    candidates = sorted(
        root.glob("astra-fallback-*/evidence.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        payload = load_json(path)
        if (
            isinstance(payload, dict)
            and payload.get("state") == "LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING"
            and payload.get("candidate_sha") == candidate_sha
        ):
            return {**payload, "_path": str(path)}
    return None


def run_a09_local_rehearsal() -> dict[str, Any]:
    command = ROOT / "governance" / "mac-engineer" / "V07_ASTRA_LOCAL_FALLBACK.command"
    if not command.is_file():
        return {"state": "HOLD", "reason": "A09_LOCAL_REHEARSAL_COMMAND_MISSING"}
    result = run(["zsh", str(command)], cwd=ROOT, timeout=3600)
    evidence_path = None
    for line in result.get("stdout", "").splitlines():
        if line.startswith("EVIDENCE="):
            evidence_path = line.split("=", 1)[1].strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "evidence": evidence_path,
        "stdout_tail": result.get("stdout", "")[-4000:],
        "stderr_tail": result.get("stderr", "")[-4000:],
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_receipt(
    *,
    command: str,
    state: str,
    completed: list[str],
    evidence: list[str],
    hold: str,
    next_action: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "schema": "enguru.mac-engineer.operator-receipt/v1",
        "observed_at": now(),
        "command": command,
        "state": state,
        "completed": completed,
        "evidence": evidence,
        "hold": hold,
        "next_action": next_action,
        "authority": {
            "github": "CANONICAL_WHEN_AVAILABLE",
            "local_execution": "OSi_LOCAL_EXECUTION_RUNTIME",
            "local_mirror": "RECOVERY_ONLY",
            "final": "DONECHECK_V1_2_THEN_HUMAN_THRESHOLD",
        },
        "details": details or {},
    }
    json_path = EVIDENCE / f"{stamp}-{command}.json"
    txt_path = EVIDENCE / f"{stamp}-{command}.txt"
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    json_path.write_text(json_text, encoding="utf-8")
    lines = [
        f"STATE={state}",
        f"COMMAND={command}",
        "COMPLETED=" + ("; ".join(completed) if completed else "NONE"),
        "EVIDENCE=" + ("; ".join(evidence) if evidence else str(json_path)),
        f"HOLD={hold or 'NONE'}",
        f"NEXT_ACTION={next_action or 'NONE'}",
        f"RECEIPT={json_path}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EVIDENCE / "latest-receipt.json").write_text(json_text, encoding="utf-8")
    (EVIDENCE / "latest-receipt.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    RUNTIME_RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RUNTIME_RECEIPTS / "latest-receipt.json").write_text(
        json_text,
        encoding="utf-8",
    )
    (RUNTIME_RECEIPTS / "latest-receipt.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    payload["receipt"] = str(json_path)
    payload["compact_receipt"] = str(txt_path)
    return payload


def print_receipt(payload: dict[str, Any]) -> None:
    print(f"STATE={payload['state']}")
    print(f"COMMAND={payload['command']}")
    print("COMPLETED=" + ("; ".join(payload["completed"]) if payload["completed"] else "NONE"))
    print("EVIDENCE=" + ("; ".join(payload["evidence"]) if payload["evidence"] else payload["receipt"]))
    print(f"HOLD={payload['hold'] or 'NONE'}")
    print(f"NEXT_ACTION={payload['next_action'] or 'NONE'}")
    print(f"RECEIPT={payload['receipt']}")


def canonical_boot() -> dict[str, Any]:
    online_sync = {
        "control_plane": sync_repo_online(ROOT),
        "product": sync_repo_online(PRODUCT),
    }
    sync = run([sys.executable, "-B", str(CONTROL), "sync-context"], cwd=ROOT, timeout=120)
    start = run([sys.executable, "-B", str(CONTROL), "session-start"], cwd=ROOT, timeout=120)
    return {
        "state": "PASS" if sync["code"] == 0 and start["code"] == 0 else "HOLD",
        "online_sync": online_sync,
        "sync": sync,
        "session_start": start,
    }


def product_doctor() -> dict[str, Any]:
    doctor_path = PRODUCT / "runtime" / "doctor.py"
    if not doctor_path.is_file():
        return {"verdict": "HOLD", "reason": "PRODUCT_DOCTOR_MISSING"}
    spec = importlib.util.spec_from_file_location("enguru_product_doctor", doctor_path)
    if not spec or not spec.loader:
        return {"verdict": "HOLD", "reason": "PRODUCT_DOCTOR_IMPORT_FAILED"}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run(ENGURU)


def verify_product() -> tuple[str, dict[str, Any], list[str]]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = EVIDENCE / f"verify-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    def checked(name: str, cmd: list[str], timeout: int = 900, env: dict[str, str] | None = None) -> None:
        result = run(cmd, cwd=PRODUCT, timeout=timeout, env=env)
        log = run_dir / f"{name}.log"
        log.write_text(
            (result["stdout"] + "\n" + result["stderr"]).strip() + "\n",
            encoding="utf-8",
        )
        checks.append({
            "name": name,
            "state": "PASS" if result["code"] == 0 else "HOLD",
            "code": result["code"],
            "log": str(log),
            "sha256": sha256_file(log),
        })

    env = dict(os.environ)
    env["PYTHONPATH"] = str(PRODUCT / "runtime")
    checked("runtime-compile", ["python3", "-B", "-m", "compileall", "-q", "runtime"])
    checked(
        "runtime-tests",
        ["python3", "-B", "-m", "unittest", "discover", "-s", "runtime/tests", "-v"],
        timeout=1800,
        env=env,
    )
    checked("native-prep-syntax", ["zsh", "-n", "execution_prep/native_app/prepare_native_app.command"])
    swift_out = run_dir / "EnguruMacEngineer"
    checked(
        "native-swift-build",
        [
            "xcrun",
            "swiftc",
            "-parse-as-library",
            "execution_prep/native_app/EnguruMacEngineerApp.swift",
            "-o",
            str(swift_out),
            "-framework",
            "SwiftUI",
            "-framework",
            "WebKit",
            "-framework",
            "AppKit",
        ],
        timeout=900,
    )
    checked("diff-check", ["git", "diff", "--check"], timeout=60)
    product_state = git_state(PRODUCT)
    local_donecheck = (
        all(item["state"] == "PASS" for item in checks)
        and product_state.get("clean") is True
    )
    summary = {
        "schema": "enguru.mac-engineer.operator-verification/v1",
        "observed_at": now(),
        "product": product_state,
        "checks": checks,
        "local_donecheck": "PASS" if local_donecheck else "HOLD",
        "authority_boundary": (
            "LOCAL_ENGINEERING_VERIFICATION_ONLY; canonical version closure still requires "
            "the active acceptance matrix, DoneCheck v1.2 and Human Threshold."
        ),
    }
    evidence_path = run_dir / "evidence.json"
    evidence_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return (
        "PASS" if local_donecheck else "HOLD",
        summary,
        [str(evidence_path)],
    )


def latest_task() -> dict[str, Any] | None:
    tasks = RUNTIME / "tasks"
    if not tasks.is_dir():
        return None
    candidates = sorted(
        tasks.glob("task_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        data = load_json(path)
        if isinstance(data, dict):
            data = dict(data)
            data["_path"] = str(path)
            return data
    return None


def recover_latest_task() -> dict[str, Any]:
    task = latest_task()
    if not task:
        return {"state": "PASS", "action": "NO_ACTIVE_TASK", "task": None}
    task_id = task.get("task_id")
    task_state = task.get("state")
    if task_state in TERMINAL_STATES:
        return {"state": "PASS", "action": "TERMINAL_TASK_PRESERVED", "task": task}

    runtime_path = PRODUCT / "runtime"
    if str(runtime_path) not in sys.path:
        sys.path.insert(0, str(runtime_path))
    from reliability import ReliabilityManager  # type: ignore

    manager = ReliabilityManager(RUNTIME)
    current = manager.get(task_id)
    if not current:
        return {"state": "HOLD", "action": "TASK_MISSING", "task": task}

    if current["state"] == "RUNNING":
        classification = manager.classify_recovery(task_id)
        if classification.get("classification") == "RECOVERABLE":
            manager.transition(
                task_id,
                "RECOVERY_REQUIRED",
                recovery_class="RECOVERABLE",
                note="operator_recover_after_interruption",
            )
        elif classification.get("classification") == "ROLLBACK_REQUIRED":
            rolled = manager.rollback_to_lkg(task_id)
            return {
                "state": "PASS" if rolled.get("ok") else "HOLD",
                "action": "ROLLBACK_TO_LKG",
                "result": rolled,
            }
        else:
            return {"state": "HOLD", "action": "RECOVERY_BASIS_REQUIRED", "result": classification}

    current = manager.get(task_id)
    if current["state"] == "VERIFYING":
        manager.transition(
            task_id,
            "RUNNING",
            recovery_class="RECOVERABLE",
            note="operator_recover_from_verifying",
        )
        return {"state": "PASS", "action": "VERIFYING_TO_RUNNING", "task": manager.get(task_id)}

    if current["state"] in {"CHECKPOINTED", "RECOVERY_REQUIRED"}:
        resumed = manager.resume(task_id)
        return {
            "state": "PASS" if resumed.get("ok") else "HOLD",
            "action": "RESUME_FROM_CHECKPOINT",
            "result": resumed,
        }

    return {
        "state": "HOLD",
        "action": "UNHANDLED_TASK_STATE",
        "task": current,
    }


def command_status() -> int:
    truth = current_truth()
    control = git_state(ROOT)
    product = git_state(PRODUCT)
    runner = runner_status()
    manifest = offline_manifest()
    local_ok = (
        control.get("available")
        and product.get("available")
        and PRODUCT.exists()
        and RUNTIME.exists()
    )
    state = "PASS" if local_ok else "HOLD"
    canonical_hold = truth.get("a09_state") if truth.get("v07_state") == "HOLD" else ""
    payload = write_receipt(
        command="status",
        state=state,
        completed=["CANONICAL_STATE_READ", "LOCAL_GIT_STATE_READ", "RUNNER_STATE_READ"],
        evidence=[str(SESSION_STATE), str(ROADMAP)],
        hold=str(canonical_hold or ""),
        next_action=str(truth.get("next_action") or "UNRESOLVED"),
        details={
            "truth": truth,
            "control_plane": control,
            "product": product,
            "runner": runner,
            "offline_manifest": manifest,
        },
    )
    print_receipt(payload)
    return 0 if state == "PASS" else 2


def command_doctor() -> int:
    doctor = product_doctor()
    runner = runner_status()
    mirrors = sync_mirrors()
    manifest = offline_manifest()
    state = "PASS" if (
        doctor.get("verdict") == "PASS"
        and all(item.get("state") == "PASS" for item in mirrors.values())
    ) else "HOLD"
    hold_parts = []
    if doctor.get("verdict") != "PASS":
        hold_parts.append("LOCAL_DOCTOR")
    if any(item.get("state") != "PASS" for item in mirrors.values()):
        hold_parts.append("GITVAULT_SYNC")
    payload = write_receipt(
        command="doctor",
        state=state,
        completed=["LOCAL_DOCTOR", "GITVAULT_SYNC", "OFFLINE_QUEUE_RECONCILIATION"],
        evidence=[str(mirror_path("Engurulaboratuvari")), str(mirror_path("enguru-mac-engineer"))],
        hold="+".join(hold_parts),
        next_action="enguru-mac continue" if doctor.get("verdict") == "PASS" else "RECONCILE_DOCTOR_HOLD",
        details={
            "doctor": doctor,
            "runner": runner,
            "mirrors": mirrors,
            "offline_manifest": manifest,
        },
    )
    print_receipt(payload)
    return 0 if state == "PASS" else 2


def command_verify() -> int:
    boot = canonical_boot()
    if boot.get("state") != "PASS":
        truth = current_truth()
        payload = write_receipt(
            command="verify",
            state="HOLD",
            completed=["CANONICAL_BOOT_HOLD"],
            evidence=[str(SESSION_STATE)],
            hold="CANONICAL_BOOT",
            next_action="enguru-mac doctor",
            details={"boot": boot, "truth": truth},
        )
        print_receipt(payload)
        return 2

    state, verification, evidence = verify_product()
    mirrors = sync_mirrors()
    truth = current_truth()
    hold = "" if state == "PASS" else "LOCAL_VERIFICATION"
    payload = write_receipt(
        command="verify",
        state=state,
        completed=[
            "RUNTIME_COMPILE",
            "FULL_RUNTIME_REGRESSION",
            "NATIVE_SYNTAX",
            "NATIVE_SWIFT_BUILD",
            "DIFF_CHECK",
            "LOCAL_DONECHECK",
            "GITVAULT_SYNC",
        ],
        evidence=evidence,
        hold=hold,
        next_action=str(truth.get("next_action") or "UNRESOLVED"),
        details={"verification": verification, "mirrors": mirrors, "truth": truth},
    )
    print_receipt(payload)
    return 0 if state == "PASS" else 2


def command_recover() -> int:
    boot = canonical_boot()
    truth = current_truth()
    if boot.get("state") != "PASS":
        mirrors = sync_mirrors()
        payload = write_receipt(
            command="recover",
            state="HOLD",
            completed=["CANONICAL_BOOT_HOLD", "GITVAULT_SYNC"],
            evidence=[str(SESSION_STATE)],
            hold="CANONICAL_BOOT",
            next_action="enguru-mac doctor",
            details={"boot": boot, "mirrors": mirrors, "truth": truth},
        )
        print_receipt(payload)
        return 2

    recovery = recover_latest_task()
    mirrors = sync_mirrors()
    state = "PASS" if recovery.get("state") == "PASS" else "HOLD"
    hold = "" if state == "PASS" else str(recovery.get("action") or "RECOVERY_HOLD")
    payload = write_receipt(
        command="recover",
        state=state,
        completed=["CANONICAL_BOOT", "TASK_RECOVERY_CLASSIFICATION", "GITVAULT_SYNC"],
        evidence=[],
        hold=hold,
        next_action=str(truth.get("next_action") or "enguru-mac doctor"),
        details={"boot": boot, "recovery": recovery, "mirrors": mirrors},
    )
    print_receipt(payload)
    return 0 if state == "PASS" else 2


def run_a10_donecheck_acceptance() -> dict[str, Any]:
    if not A10_ACCEPTANCE.is_file():
        return {
            "state": "HOLD",
            "reason": "A10_ACCEPTANCE_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(["zsh", str(A10_ACCEPTANCE)], cwd=ROOT, timeout=7200)
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-5000:],
        "stderr_tail": result.get("stderr", "")[-5000:],
    }


def run_local_finisher_rehearsal() -> dict[str, Any]:
    if not LOCAL_FINISHER_REHEARSAL.is_file():
        return {
            "state": "HOLD",
            "reason": "LOCAL_FINISHER_REHEARSAL_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(["zsh", str(LOCAL_FINISHER_REHEARSAL)], cwd=ROOT, timeout=1800)
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-5000:],
        "stderr_tail": result.get("stderr", "")[-5000:],
    }


def run_mac_native_authority_field_proof() -> dict[str, Any]:
    if not MAC_NATIVE_AUTHORITY_FIELD_PROOF.is_file():
        return {
            "state": "HOLD",
            "reason": "MAC_NATIVE_AUTHORITY_FIELD_PROOF_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(MAC_NATIVE_AUTHORITY_FIELD_PROOF)],
        cwd=ROOT,
        timeout=7200,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-6000:],
        "stderr_tail": result.get("stderr", "")[-6000:],
    }


def run_mac_native_restart_recovery_proof() -> dict[str, Any]:
    if not MAC_NATIVE_RESTART_RECOVERY_PROOF.is_file():
        return {
            "state": "HOLD",
            "reason": "MAC_NATIVE_RESTART_RECOVERY_PROOF_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(MAC_NATIVE_RESTART_RECOVERY_PROOF)],
        cwd=ROOT,
        timeout=7200,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-6000:],
        "stderr_tail": result.get("stderr", "")[-6000:],
    }


def run_mac_native_offline_gitvault_reconciliation_proof() -> dict[str, Any]:
    if not MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF.is_file():
        return {
            "state": "HOLD",
            "reason": "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF)],
        cwd=ROOT,
        timeout=7200,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()
    return {
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-6000:],
        "stderr_tail": result.get("stderr", "")[-6000:],
    }


def command_continue() -> int:
    boot = canonical_boot()
    truth = current_truth()
    mirrors = sync_mirrors()
    runner = runner_status()
    action = str(truth.get("next_action") or "UNRESOLVED")
    local_action = str(truth.get("local_continuity_next_action") or "")
    fallback = truth.get("local_fallback") or {}

    if boot.get("state") != "PASS":
        state = "HOLD"
        hold = "CANONICAL_BOOT"
        next_action = "enguru-mac doctor"
        completed = ["CANONICAL_BOOT_HOLD", "GITVAULT_SYNC"]
    elif local_action == "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        offline_proof = run_mac_native_offline_gitvault_reconciliation_proof()
        if offline_proof.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(offline_proof.get("evidence") or ""),
                    ] if item
                ],
                hold="MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "offline_proof": offline_proof,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF_PASS",
            "OFFLINE_LOCAL_COMMIT_QUEUE_PASS",
            "DURABLE_PATCH_PASS",
            "DURABLE_GIT_BUNDLE_PASS",
            "RECONCILIATION_APPLY_CHECK_PASS",
            "GITVAULT_REFS_UNCHANGED_PASS",
            "SECOND_CANONICAL_TRUTH_FALSE",
        ])
        state = "HOLD"
        hold = "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION_REQUIRED"
        next_action = (
            (offline_proof.get("fields") or {}).get("NEXT_ACTION")
            or "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION"
        )
    elif local_action == "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        restart_proof = run_mac_native_restart_recovery_proof()
        if restart_proof.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(restart_proof.get("evidence") or ""),
                    ] if item
                ],
                hold="MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "restart_proof": restart_proof,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF_PASS",
            "PROCESS_RESTART_PASS",
            "TASK_IDENTITY_CONTINUITY_PASS",
            "CHECKPOINT_RESUME_PASS",
            "EXACTLY_ONCE_EFFECT_PASS",
            "FINAL_STATE_COMPLETE",
        ])
        state = "HOLD"
        hold = "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF_REQUIRED"
        next_action = (
            (restart_proof.get("fields") or {}).get("NEXT_ACTION")
            or "MAC_NATIVE_OFFLINE_GITVAULT_RECONCILIATION_PROOF"
        )
    elif local_action == "MAC_NATIVE_AUTHORITY_MIGRATION_FIELD_PROOF":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        migration_proof = run_mac_native_authority_field_proof()
        if migration_proof.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(migration_proof.get("evidence") or ""),
                    ] if item
                ],
                hold="MAC_NATIVE_AUTHORITY_MIGRATION_FIELD_PROOF",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "migration_proof": migration_proof,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "MAC_NATIVE_AUTHORITY_MIGRATION_FIELD_PROOF_PASS",
            "MULTI_REPO_LOCAL_ENGINEERING_PASS",
            "REMOTE_PUSH_FALSE",
            "SECOND_CANONICAL_TRUTH_FALSE",
        ])
        state = "HOLD"
        hold = "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF_REQUIRED"
        next_action = (
            (migration_proof.get("fields") or {}).get("NEXT_ACTION")
            or "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF"
        )
    elif local_action == "V07_LOCAL_FINISHER_REHEARSAL":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        local_finisher = run_local_finisher_rehearsal()
        if local_finisher.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(local_finisher.get("evidence") or ""),
                    ] if item
                ],
                hold="LOCAL_FINISHER_REHEARSAL",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "local_finisher": local_finisher,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "LOCAL_FINISHER_REHEARSAL_PASS",
            "A10_DONECHECK_V1_2_INTEGRATION_PASS_PRESERVED",
            "A09_DONECHECK_INCONCLUSIVE_PRESERVED",
        ])
        state = "HOLD"
        hold = "A09_EXTERNAL_CONFIRMATION_PENDING"
        next_action = (
            (local_finisher.get("fields") or {}).get("NEXT_ACTION")
            or "V07_A09_EXTERNAL_CONFIRMATION_OR_A11_WHEN_ELIGIBLE"
        )
    elif local_action == "V07_A10_DONECHECK_V1_2_INTEGRATION":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        a10 = run_a10_donecheck_acceptance()
        if a10.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(a10.get("evidence") or ""),
                    ] if item
                ],
                hold="A10_DONECHECK_V1_2_INTEGRATION",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "a10": a10,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "A10_DONECHECK_V1_2_INTEGRATION_PASS",
            "A01_A08_DONECHECK_PASS",
            "A09_DONECHECK_INCONCLUSIVE_PRESERVED",
        ])
        state = "HOLD"
        hold = "A09_EXTERNAL_CONFIRMATION_PENDING"
        next_action = (
            (a10.get("fields") or {}).get("NEXT_ACTION")
            or "LOCAL_FINISHER_REHEARSAL_OR_A09_EXTERNAL_CONFIRMATION"
        )
    elif action == "V07_A09_CLEAR_GITHUB_PRIVATE_REPO_HOSTED_ACTIONS_EXECUTION_GATE":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        candidate_sha = str(truth.get("a09_candidate_sha") or "")
        local_evidence = latest_matching_fallback(candidate_sha)
        rehearsal = None

        if local_evidence:
            completed.append("A09_LOCAL_REHEARSAL_ALREADY_PASS")
        else:
            rehearsal = run_a09_local_rehearsal()
            if rehearsal.get("state") != "PASS":
                payload = write_receipt(
                    command="continue",
                    state="HOLD",
                    completed=completed,
                    evidence=[
                        item for item in [
                            str(SESSION_STATE),
                            str(rehearsal.get("evidence") or ""),
                        ] if item
                    ],
                    hold="A09_LOCAL_REHEARSAL",
                    next_action="enguru-mac verify",
                    details={
                        "truth": truth,
                        "boot": boot,
                        "runner": runner,
                        "mirrors": mirrors,
                        "rehearsal": rehearsal,
                    },
                )
                print_receipt(payload)
                return 2
            completed.append("A09_LOCAL_REHEARSAL_PASS")
            local_evidence = {
                "candidate_sha": candidate_sha,
                "_path": rehearsal.get("evidence"),
            }

        if runner.get("state") == "PASS":
            state = "HOLD"
            hold = "GITHUB_EXTERNAL_CONFIRMATION_PENDING"
            next_action = "A09_SELF_HOSTED_GITHUB_CHECK_CONFIRMATION"
            completed.append("SELF_HOSTED_RUNNER_READY")
        else:
            state = "HOLD"
            hold = "SELF_HOSTED_RUNNER_COMMISSIONING_OR_GITHUB_EXTERNAL_CONFIRMATION"
            next_action = "COMMISSION_OSI_SELF_HOSTED_RUNNER"
    else:
        registry = load_json(ACTION_REGISTRY, {}) or {}
        handler = (registry.get("actions") or {}).get(action)
        state = "HOLD"
        hold = "REGISTERED_NEXT_ACTION_REQUIRED" if handler else "ACTION_HANDLER_NOT_REGISTERED"
        next_action = action
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]

    payload = write_receipt(
        command="continue",
        state=state,
        completed=completed,
        evidence=[
            item
            for item in [
                str(SESSION_STATE),
                str((fallback or {}).get("evidence") or ""),
                str((locals().get("migration_proof") or {}).get("evidence") or ""),
                str((locals().get("restart_proof") or {}).get("evidence") or ""),
                str((locals().get("offline_proof") or {}).get("evidence") or ""),
            ]
            if item
        ],
        hold=hold,
        next_action=next_action,
        details={
            "truth": truth,
            "boot": boot,
            "runner": runner,
            "mirrors": mirrors,
            "local_a09_evidence": locals().get("local_evidence"),
            "local_a09_rehearsal": locals().get("rehearsal"),
            "a10": locals().get("a10"),
            "local_finisher": locals().get("local_finisher"),
            "migration_proof": locals().get("migration_proof"),
            "restart_proof": locals().get("restart_proof"),
            "offline_proof": locals().get("offline_proof"),
            "offline_manifest": offline_manifest(),
        },
    )
    print_receipt(payload)
    return 0 if state == "PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser(prog="enguru-mac")
    parser.add_argument(
        "command",
        choices=["status", "continue", "verify", "recover", "doctor"],
    )
    args = parser.parse_args()
    return {
        "status": command_status,
        "continue": command_continue,
        "verify": command_verify,
        "recover": command_recover,
        "doctor": command_doctor,
    }[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
