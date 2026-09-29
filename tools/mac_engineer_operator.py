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
DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION = ROOT / "governance" / "mac-engineer" / "V07_DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION.command"
FINAL_CONSOLIDATED_MAC_CAMPAIGN = ROOT / "governance" / "mac-engineer" / "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN.command"
HUMAN_THRESHOLD_AUTHORITY_TRANSITION = ROOT / "governance" / "mac-engineer" / "V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION.command"
V08_SELF_ENGINEERING_BASELINE = ROOT / "governance" / "mac-engineer" / "V08_SELF_ENGINEERING_BASELINE_AUDIT.command"
V08_PRODUCT_REALITY_RECONCILIATION = ROOT / "governance" / "mac-engineer" / "V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION.command"
V08_UX_AESTHETIC_PRODUCT_CONTRACT = ROOT / "governance" / "mac-engineer" / "V08_UX_AESTHETIC_PRODUCT_CONTRACT.command"
V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING = ROOT / "governance" / "mac-engineer" / "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING.command"
V08_NATIVE_APP_PRODUCTIZATION = ROOT / "governance" / "mac-engineer" / "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE.command"
V08_EXISTING_PRODUCT_CHANGE = ROOT / "governance" / "mac-engineer" / "V08_EXISTING_PRODUCT_CHANGE_SCENARIO.command"
V08_FINISHED_PRODUCT_DELIVERY = ROOT / "governance" / "mac-engineer" / "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO.command"

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

    declared_version = str(session.get("currentVersion") or "").strip()
    roadmap_version = str(roadmap.get("current", {}).get("version") or "").strip()
    if declared_version:
        current_version = declared_version
    elif session.get("currentV07"):
        current_version = "v0.7"
    else:
        current_version = roadmap_version or "v0.7"
    version_key = "currentV" + current_version.removeprefix("v").replace(".", "")
    current_version_state = session.get(version_key) or {}
    roadmap_version_state = next(
        (
            item
            for item in roadmap.get("versions", [])
            if item.get("version") == current_version
        ),
        {},
    )

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
        "current_version": current_version,
        "current_state": (
            current_version_state.get("state")
            or roadmap.get("current", {}).get("state")
            or roadmap_version_state.get("state")
        ),
        "active_objective": roadmap.get("current", {}).get("activeObjective"),
        "version_state": current_version_state,
        "next_action": (
            current_version_state.get("nextAction")
            or roadmap_version_state.get("nextAction")
            or roadmap.get("current", {}).get("activeObjective")
        ),
        "local_continuity_next_action": current_version_state.get("localContinuityNextAction"),
        "local_continuity_state": current_version_state.get("localContinuityState"),
        "v07_state": current_v07.get("state") or v07_roadmap.get("state"),
        "a09_state": current_v07.get("a09State") or (v07_roadmap.get("a09") or {}).get("state"),
        "a09_candidate_sha": current_v07.get("a09LatestCandidateHead") or (v07_roadmap.get("a09") or {}).get("currentCandidateSha"),
        "local_fallback": current_v07.get("localFallback") or {},
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


def run_donecheck_v12_local_authority_verification() -> dict[str, Any]:
    if not DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION.is_file():
        return {
            "state": "HOLD",
            "reason": "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION)],
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


def run_final_consolidated_mac_campaign() -> dict[str, Any]:
    if not FINAL_CONSOLIDATED_MAC_CAMPAIGN.is_file():
        return {
            "state": "HOLD",
            "reason": "FINAL_CONSOLIDATED_MAC_CAMPAIGN_COMMAND_MISSING",
            "evidence": None,
        }

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.Popen(
        ["zsh", str(FINAL_CONSOLIDATED_MAC_CAMPAIGN)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        print(line, flush=True)
        lines.append(line)
        if len(lines) > 4000:
            lines = lines[-4000:]

    code = proc.wait()
    fields: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    return {
        "state": "PASS" if code == 0 else "HOLD",
        "code": code,
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": "\n".join(lines[-200:]),
        "stderr_tail": "",
    }


def run_human_threshold_review() -> dict[str, Any]:
    if not HUMAN_THRESHOLD_AUTHORITY_TRANSITION.is_file():
        return {
            "state": "HOLD",
            "reason": "HUMAN_THRESHOLD_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(HUMAN_THRESHOLD_AUTHORITY_TRANSITION), "REVIEW"],
        cwd=ROOT,
        timeout=1800,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    review_ready = (
        fields.get("HUMAN_THRESHOLD_REVIEW_READY") == "PASS"
        and fields.get("HUMAN_DECISION_OPTIONS") == "ACCEPT|HOLD"
        and fields.get("HOLD") == "HUMAN_DECISION_REQUIRED"
    )
    return {
        "state": "PASS" if review_ready else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-6000:],
        "stderr_tail": result.get("stderr", "")[-6000:],
    }


def run_v08_self_engineering_baseline() -> dict[str, Any]:
    if not V08_SELF_ENGINEERING_BASELINE.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_SELF_ENGINEERING_BASELINE_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(V08_SELF_ENGINEERING_BASELINE)],
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

    passed = (
        result["code"] == 0
        and fields.get("STATE") == "PASS"
        and fields.get("V08_GATE_01") == "PASS"
        and fields.get("PRODUCT_RUNTIME_REGRESSION") == "PASS"
        and fields.get("NATIVE_SWIFT_BUILD") == "PASS"
    )
    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-8000:],
        "stderr_tail": result.get("stderr", "")[-8000:],
    }


def run_v08_product_reality_reconciliation() -> dict[str, Any]:
    if not V08_PRODUCT_REALITY_RECONCILIATION.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_PRODUCT_REALITY_RECONCILIATION_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(V08_PRODUCT_REALITY_RECONCILIATION)],
        cwd=ROOT,
        timeout=1800,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    passed = (
        result["code"] == 0
        and fields.get("STATE") == "PASS"
        and fields.get("V08_GATE_02") == "PASS"
        and fields.get("PRODUCT_REALITY_RECONCILED") == "PASS"
        and fields.get("UNNECESSARY_NEW_CORE_COUNT") == "0"
    )
    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-8000:],
        "stderr_tail": result.get("stderr", "")[-8000:],
    }


def run_v08_ux_aesthetic_product_contract() -> dict[str, Any]:
    if not V08_UX_AESTHETIC_PRODUCT_CONTRACT.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_UX_AESTHETIC_PRODUCT_CONTRACT_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(V08_UX_AESTHETIC_PRODUCT_CONTRACT)],
        cwd=ROOT,
        timeout=1800,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    passed = (
        result["code"] == 0
        and fields.get("STATE") == "PASS"
        and fields.get("V08_GATE_03") == "PASS"
        and fields.get("UX_PRODUCT_CONTRACT") == "PASS"
        and fields.get("AESTHETIC_MOTOR_REUSE") == "PASS"
        and fields.get("UNNECESSARY_NEW_CORE_COUNT") == "0"
    )
    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-8000:],
        "stderr_tail": result.get("stderr", "")[-8000:],
    }


def run_v08_full_product_engineering_chain_binding() -> dict[str, Any]:
    if not V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING.is_file():
        return {"state":"HOLD","reason":"V08_FULL_CHAIN_BINDING_COMMAND_MISSING","evidence":None}
    result = run(
        ["zsh", str(V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING)],
        cwd=ROOT,
        timeout=1800,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE":"1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout","").splitlines():
        if "=" in line:
            key,value=line.split("=",1)
            if key and value:
                fields[key.strip()]=value.strip()
    passed = (
        result["code"] == 0
        and fields.get("STATE") == "PASS"
        and fields.get("V08_GATE_04") == "PASS"
        and fields.get("FULL_PRODUCT_ENGINEERING_CHAIN_BOUND") == "PASS"
        and fields.get("MISSING_BINDING_COUNT") == "0"
        and fields.get("UNNECESSARY_NEW_CORE_COUNT") == "0"
    )
    return {
        "state":"PASS" if passed else "HOLD",
        "code":result["code"],
        "fields":fields,
        "evidence":fields.get("EVIDENCE"),
        "stdout_tail":result.get("stdout","")[-8000:],
        "stderr_tail":result.get("stderr","")[-8000:],
    }


def run_v08_native_app_productization() -> dict[str, Any]:
    if not V08_NATIVE_APP_PRODUCTIZATION.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_NATIVE_APP_PRODUCTIZATION_COMMAND_MISSING",
            "evidence": None,
        }
    result = run(
        ["zsh", str(V08_NATIVE_APP_PRODUCTIZATION)],
        cwd=ROOT,
        timeout=3600,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    fields: dict[str, str] = {}
    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    passed = (
        result["code"] == 0
        and fields.get("STATE") == "PASS"
        and fields.get("V08_GATE_05") == "PASS"
        and fields.get("NATIVE_APP_PRODUCTIZATION") == "PASS"
        and fields.get("PRODUCT_REMOTE_PUSH") == "false"
        and fields.get("PRODUCT_MUTATION_PATHS") == "3"
        and fields.get("SOURCE_BUNDLE_VERSION") == "0.8"
        and fields.get("INSTALLED_BUNDLE_VERSION") == "0.8"
        and fields.get("SOURCE_INSTALLED_RUNTIME_PARITY") == "PASS"
        and fields.get("RELEASE_PROVENANCE") == "PASS"
        and fields.get("CODESIGN") == "PASS"
        and fields.get("FRESH_APP_RUNTIME_READINESS") == "PASS"
    )
    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-10000:],
        "stderr_tail": result.get("stderr", "")[-10000:],
    }



def run_v08_existing_product_change() -> dict[str, Any]:
    if not V08_EXISTING_PRODUCT_CHANGE.is_file():
        return {
            "state": "HOLD",
            "implementation_state": "HOLD",
            "reason": "V08_EXISTING_PRODUCT_CHANGE_COMMAND_MISSING",
            "evidence": None,
        }

    result = run(
        ["zsh", str(V08_EXISTING_PRODUCT_CHANGE)],
        cwd=ROOT,
        timeout=3600,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key and value:
                fields[key.strip()] = value.strip()

    implementation_pass = (
        result["code"] == 2
        and fields.get("STATE") == "HOLD"
        and fields.get("V08_GATE_06") == "HOLD"
        and fields.get("V08_GATE_06_IMPLEMENTATION") == "PASS"
        and fields.get("EXISTING_PRODUCT_CHANGE_IMPLEMENTATION") == "PASS"
        and fields.get("PRODUCT_REMOTE_PUSH") == "false"
        and fields.get("PRODUCT_MUTATION_PATHS") == "2"
        and fields.get("SOURCE_CONTRACT") == "PASS"
        and fields.get("FULL_RUNTIME_REGRESSION") == "PASS"
        and fields.get("SOURCE_INSTALLED_RUNTIME_PARITY") == "PASS"
        and fields.get("RELEASE_PROVENANCE") == "PASS"
        and fields.get("CODESIGN") == "PASS"
        and fields.get("FRESH_APP_RUNTIME_READINESS") == "PASS"
        and fields.get("HUMAN_ARTISTIC_AUTHORITY") == "REQUIRED"
        and fields.get("HOLD") == "HUMAN_ARTISTIC_AUTHORITY_REQUIRED"
        and fields.get("NEXT_ACTION") == "HUMAN_ARTISTIC_AUTHORITY_REVIEW"
    )

    return {
        "state": "HOLD",
        "implementation_state": (
            "PASS" if implementation_pass else "HOLD"
        ),
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-10000:],
        "stderr_tail": result.get("stderr", "")[-10000:],
    }



def run_v08_finished_product_delivery() -> dict[str, Any]:
    if not V08_FINISHED_PRODUCT_DELIVERY.is_file():
        return {
            "state": "HOLD",
            "technical_state": "HOLD",
            "reason": "V08_FINISHED_PRODUCT_DELIVERY_COMMAND_MISSING",
            "evidence": None,
        }

    result = run(
        ["zsh", str(V08_FINISHED_PRODUCT_DELIVERY)],
        cwd=ROOT,
        timeout=3600,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)

            if key and value:
                fields[key.strip()] = value.strip()

    technical_pass = (
        result["code"] == 2
        and fields.get("STATE") == "HOLD"
        and fields.get("V08_GATE_10") == "HOLD"
        and fields.get("V08_GATE_10_TECHNICAL") == "PASS"
        and fields.get("HUMAN_THRESHOLD_REVIEW_READY") == "PASS"
        and fields.get("HUMAN_DECISION_OPTIONS") == "ACCEPT|HOLD"
        and fields.get("HOLD") == "HUMAN_DECISION_REQUIRED"
        and fields.get("NEXT_ACTION")
            == "GATE10_HUMAN_DELIVERY_ACCEPTANCE"
    )

    return {
        "state": "HOLD",
        "technical_state":
            "PASS" if technical_pass else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("EVIDENCE"),
        "stdout_tail":
            result.get("stdout", "")[-12000:],
        "stderr_tail":
            result.get("stderr", "")[-6000:],
    }




def detect_v08_gate11_active_package() -> str:
    p08_root = (
        HOME
        / "Enguru"
        / "Evidence"
        / "MacEngineer"
        / "v0.8"
        / "gate11-p08-stale-runtime-recovery"
    )

    p09_root = (
        HOME
        / "Enguru"
        / "Evidence"
        / "MacEngineer"
        / "v0.8"
        / "gate11-p09-lifecycle"
    )

    p10_root = (
        HOME
        / "Enguru"
        / "Evidence"
        / "MacEngineer"
        / "v0.8"
        / "gate11-p10-reliability"
    )

    p11_root = (
        HOME
        / "Enguru"
        / "Evidence"
        / "MacEngineer"
        / "v0.8"
        / "gate11-p11-independent-verification"
    )

    p11_receipts = sorted(
        p11_root.glob("*/p11-final-acceptance.json")
    )

    p11_required = (
        "P10_PASS",
        "TARGETED_REGRESSION_PASS",
        "FULL_CONTROL_PLANE_REGRESSION_PASS",
        "PRODUCT_REGRESSION_PASS",
        "DIFF_CHECK_PASS",
        "SCOPE_CHECK_PASS",
        "PROVENANCE_CHECK_PASS",
        "RECOVERY_CHECK_PASS",
        "EVIDENCE_COMPLETENESS_PASS",
        "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
        "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
        "UNTRACKED_MANUAL_STEP_COUNT_0",
        "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0",
        "CRITICAL_FALSE_PASS_0",
    )

    for receipt in reversed(p11_receipts):
        try:
            data = json.loads(
                receipt.read_text(encoding="utf-8")
            )
        except Exception:
            continue

        acceptance = data.get("acceptance") or {}

        if (
            data.get("state") == "PASS"
            and data.get("package") == "P11"
            and data.get("nextTransition") == "P12"
            and all(
                acceptance.get(key) == "PASS"
                for key in p11_required
            )
            and data.get(
                "currentUnresolvedCriticalFalsePassCount"
            ) == 0
            and data.get("sourceMutation") is False
            and data.get("remoteMutation") is False
            and data.get("newCore") is False
        ):
            return "P12"

    p10_receipts = sorted(
        p10_root.glob("*/p10-final-acceptance.json")
    )

    p10_required = (
        "P09_PASS",
        "CHECKPOINT_CONTINUITY_PASS",
        "CONTROLLED_INTERRUPTION_PASS",
        "RESTART_RECOVERY_PASS",
        "SAME_TASK_RESUME_PASS",
        "IDEMPOTENCY_PASS",
        "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE",
        "SINGLE_WRITER_DISCIPLINE_PASS",
        "BOUNDED_RETRY_PASS",
        "RECOVERY_EVIDENCE_PASS",
    )

    for receipt in reversed(p10_receipts):
        try:
            data = json.loads(
                receipt.read_text(encoding="utf-8")
            )
        except Exception:
            continue

        acceptance = data.get("acceptance") or {}

        if (
            data.get("state") == "PASS"
            and data.get("package") == "P10"
            and data.get("nextTransition") == "P11"
            and all(
                acceptance.get(key) == "PASS"
                for key in p10_required
            )
            and data.get("sourceMutation") is False
            and data.get("remoteMutation") is False
            and data.get("newCore") is False
        ):
            return "P11"

    p09_receipts = sorted(
        p09_root.glob("*/p09-final-acceptance.json")
    )

    for receipt in reversed(p09_receipts):
        try:
            data = json.loads(
                receipt.read_text(encoding="utf-8")
            )
        except Exception:
            continue

        if (
            data.get("state") == "PASS"
            and data.get("package") == "P09"
            and data.get("nextTransition") == "P10"
        ):
            return "P10"

    p08_receipts = sorted(
        p08_root.glob("*/p08-final-acceptance.json")
    )

    for receipt in reversed(p08_receipts):
        try:
            data = json.loads(
                receipt.read_text(encoding="utf-8")
            )
        except Exception:
            continue

        if (
            data.get("state") == "PASS"
            and data.get("package") == "P08"
            and data.get("nextTransition") == "P09"
        ):
            return "P09"

    return "P07"


def run_v08_gate11_p09_lifecycle_controlled_replacement_rollback() -> dict[str, Any]:
    command = (
        ROOT
        / "governance"
        / "mac-engineer"
        / "V08_GATE11_P09_LIFECYCLE_CONTROLLED_REPLACEMENT_ROLLBACK.command"
    )

    if not command.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_GATE11_P09_COMMAND_MISSING",
            "fields": {},
            "evidence": None,
        }

    result = run(
        ["zsh", str(command)],
        cwd=ROOT,
        timeout=7200,
        env=dict(os.environ),
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key:
            fields[key.strip()] = value.strip()

    required = [
        "CONTROLLED_REPLACEMENT_PASS",
        "STOP_PASS",
        "RESTART_PASS",
        "KNOWN_GOOD_ROLLBACK_PASS",
        "ROLLBACK_REVERIFY_PASS",
        "LIFECYCLE_PROVENANCE_PASS",
        "EVIDENCE_CONTINUITY_PASS",
    ]

    passed = all([
        result["code"] == 0,
        fields.get("STATE") == "PASS",
        fields.get("P09_ACCEPTANCE") == "8_OF_8_PASS",
        all(fields.get(key) == "PASS" for key in required),
        fields.get("FINAL_KNOWN_GOOD") == "P08_VERIFIED",
        fields.get("SOURCE_MUTATION") == "0",
        fields.get("REMOTE_MUTATION") == "0",
        fields.get("NEXT_ACTION")
            == "P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY",
    ])

    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "stdout_tail": result.get("stdout", "")[-24000:],
        "stderr_tail": result.get("stderr", "")[-12000:],
    }


def run_v08_gate11_p10_interruption_recovery_resume_reliability() -> dict[str, Any]:
    command = (
        ROOT
        / "governance"
        / "mac-engineer"
        / "V08_GATE11_P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY.command"
    )

    if not command.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_GATE11_P10_COMMAND_MISSING",
            "fields": {},
            "evidence": None,
        }

    result = run(
        ["zsh", str(command)],
        cwd=ROOT,
        timeout=7200,
        env=dict(os.environ),
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key:
            fields[key.strip()] = value.strip()

    required = [
        "P09_PASS",
        "CHECKPOINT_CONTINUITY_PASS",
        "CONTROLLED_INTERRUPTION_PASS",
        "RESTART_RECOVERY_PASS",
        "SAME_TASK_RESUME_PASS",
        "IDEMPOTENCY_PASS",
        "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE",
        "SINGLE_WRITER_DISCIPLINE_PASS",
        "BOUNDED_RETRY_PASS",
        "RECOVERY_EVIDENCE_PASS",
    ]

    passed = all([
        result["code"] == 0,
        fields.get("STATE") == "PASS",
        fields.get("P10_ACCEPTANCE") == "10_OF_10_PASS",
        all(fields.get(key) == "PASS" for key in required),
        fields.get("SOURCE_MUTATION") == "0",
        fields.get("REMOTE_MUTATION") == "0",
        fields.get("NEW_CORE") == "false",
        fields.get("NEXT_ACTION")
            == "P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE",
    ])

    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("P10_ACCEPTANCE_EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-24000:],
        "stderr_tail": result.get("stderr", "")[-12000:],
    }


def run_v08_gate11_p11_independent_verification_second_look_evidence_bundle() -> dict[str, Any]:
    command = (
        ROOT
        / "governance"
        / "mac-engineer"
        / "V08_GATE11_P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE.command"
    )

    if not command.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_GATE11_P11_COMMAND_MISSING",
            "fields": {},
            "evidence": None,
        }

    result = run(
        ["zsh", str(command)],
        cwd=ROOT,
        timeout=7200,
        env=dict(os.environ),
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key:
            fields[key.strip()] = value.strip()

    required = [
        "P10_PASS",
        "TARGETED_REGRESSION_PASS",
        "FULL_CONTROL_PLANE_REGRESSION_PASS",
        "PRODUCT_REGRESSION_PASS",
        "DIFF_CHECK_PASS",
        "SCOPE_CHECK_PASS",
        "PROVENANCE_CHECK_PASS",
        "RECOVERY_CHECK_PASS",
        "EVIDENCE_COMPLETENESS_PASS",
        "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
        "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
        "UNTRACKED_MANUAL_STEP_COUNT_0",
        "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0",
        "CRITICAL_FALSE_PASS_0",
    ]

    passed = all([
        result["code"] == 0,
        fields.get("STATE") == "PASS",
        fields.get("P11_ACCEPTANCE") == "14_OF_14_PASS",
        all(fields.get(key) == "PASS" for key in required),
        fields.get("CURRENT_UNRESOLVED_CRITICAL_FALSE_PASS_COUNT")
            == "0",
        fields.get("SOURCE_MUTATION") == "0",
        fields.get("REMOTE_MUTATION") == "0",
        fields.get("NEW_CORE") == "false",
        fields.get("NEXT_ACTION")
            == "P12_DONECHECK_CANONICAL_GATE11_CLOSURE",
    ])

    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence": fields.get("P11_ACCEPTANCE_EVIDENCE"),
        "stdout_tail": result.get("stdout", "")[-30000:],
        "stderr_tail": result.get("stderr", "")[-12000:],
    }


def run_v08_gate11_p12_donecheck_canonical_gate11_closure() -> dict[str, Any]:
    command = (
        ROOT
        / "governance"
        / "mac-engineer"
        / "V08_GATE11_P12_DONECHECK_CANONICAL_GATE11_CLOSURE.command"
    )

    if not command.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_GATE11_P12_COMMAND_MISSING",
            "fields": {},
            "evidence": None,
        }

    result = run(
        ["zsh", str(command)],
        cwd=ROOT,
        timeout=7200,
        env=dict(os.environ),
    )

    fields: dict[str, str] = {}

    for line in result.get("stdout", "").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key:
            fields[key.strip()] = value.strip()

    required = [
        "P01_THROUGH_P11_PASS",
        "DONECHECK_V1_2_PASS",
        "CANONICAL_RECONCILIATION_PASS",
        "GATE11_EVIDENCE_BUNDLE_COMPLETE",
        "GATE11_ENGINEERING_EXECUTION_PASS",
        "ARCHITECTURE_STATE_PRESERVED",
        "NEW_CORE_FALSE",
        "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
        "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
        "UNTRACKED_MANUAL_STEP_COUNT_0",
        "GATE11_VERIFIED_LOCKED",
        "GATE11_EXIT_V08_CONSOLIDATED_MAC_COMMISSIONING_PASS",
        "ACTIVE_GATE_12",
        "GATE12_EXECUTION_0",
        "STOP_TRUE",
    ]

    passed = all([
        result["code"] == 0,
        fields.get("STATE") == "PASS",
        fields.get("P12_ACCEPTANCE")
            == "15_OF_15_PASS",
        all(
            fields.get(key) == "PASS"
            for key in required
        ),
        fields.get("CANONICAL_MUTATION_FILE_COUNT")
            == "4",
        fields.get("REMOTE_MUTATION") == "0",
        fields.get("PRODUCT_SOURCE_MUTATION") == "0",
        fields.get("NEW_CORE") == "false",
        fields.get("NEXT_ACTION")
            == "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP",
    ])

    return {
        "state": "PASS" if passed else "HOLD",
        "code": result["code"],
        "fields": fields,
        "evidence":
            fields.get("P12_ACCEPTANCE_EVIDENCE"),
        "stdout_tail":
            result.get("stdout", "")[-30000:],
        "stderr_tail":
            result.get("stderr", "")[-12000:],
    }


def run_v08_gate11_consolidated_mac_commissioning() -> dict[str, Any]:
    active_package = detect_v08_gate11_active_package()

    if active_package == "P12":
        return (
            run_v08_gate11_p12_donecheck_canonical_gate11_closure()
        )

    if active_package == "P11":
        return (
            run_v08_gate11_p11_independent_verification_second_look_evidence_bundle()
        )

    if active_package == "P09":
        return (
            run_v08_gate11_p09_lifecycle_controlled_replacement_rollback()
        )

    if active_package == "P10":
        return run_v08_gate11_p10_interruption_recovery_resume_reliability()

    command = (
        ROOT
        / "governance"
        / "mac-engineer"
        / "V08_GATE11_CONSOLIDATED_MAC_COMMISSIONING.command"
    )

    if not command.is_file():
        return {
            "state": "HOLD",
            "reason": "V08_GATE11_CONSOLIDATED_MAC_COMMISSIONING_COMMAND_MISSING",
            "fields": {},
            "evidence": None,
        }

    result = run(
        ["zsh", str(command)],
        cwd=ROOT,
        timeout=7200,
        env=dict(os.environ),
    )

    fields: dict[str, str] = {}

    for line in result.get(
        "stdout",
        "",
    ).splitlines():
        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1,
        )

        if key:
            fields[
                key.strip()
            ] = value.strip()

    passed = all([
        result["code"] == 0,
        fields.get("STATE")
            == "PASS",
        fields.get(
            "REAL_ENGINEERING_OBJECTIVE_COMPLETE"
        ) == "PASS",
        fields.get(
            "EXPECTED_SCOPE_MATCH_PASS"
        ) == "PASS",
        fields.get(
            "TARGETED_TEST_PASS"
        ) == "PASS",
        fields.get(
            "FULL_RUNTIME_REGRESSION"
        ) == "PASS",
        fields.get(
            "PRODUCT_REMOTE_MUTATION"
        ) == "false",
        fields.get(
            "NEXT_ACTION"
        ) == "P08",
    ])

    return {
        "state":
            "PASS"
            if passed
            else "HOLD",
        "code":
            result["code"],
        "fields":
            fields,
        "stdout_tail":
            result.get(
                "stdout",
                "",
            )[-20000:],
        "stderr_tail":
            result.get(
                "stderr",
                "",
            )[-12000:],
    }


def gate12_registry_contract(registry: dict[str, Any]) -> dict[str, Any]:
    action = (registry.get("actions") or {}).get(
        "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
    )
    expected = {
        "handler": "V08_GATE12_PRE005_BOUNDED_PRELOCK",
        "authority": "HUMAN_THRESHOLD_AND_DURABLE_REPLAY",
        "doneCheckVersion": "1.2.0",
        "doneCheckExactSha": "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        "finalAcceptanceReceipt": False,
        "canonicalLock": False,
        "batch3Boundary": "FINAL_ACCEPTANCE_RECEIPT_AND_CANONICAL_LOCK",
        "failClosed": True,
    }
    if not isinstance(action, dict) or any(action.get(k) != v for k, v in expected.items()):
        return {"state": "HOLD", "reason": "GATE12_REGISTRY_CONTRACT_MISMATCH"}
    required = {
        "GATE11_VERIFIED_LOCKED", "GATE12_ACTIVE_NOT_STARTED",
        "FRESH_CANDIDATE_BUNDLE", "DONECHECK_V1_2_EXACT", "MACHINE_PASS",
        "HUMAN_REVIEW_PASS", "VERIFIED_FINISH_PASS", "SIGNED_THRESHOLD",
        "DURABLE_REPLAY", "SINGLE_WRITER_LOCK",
    }
    if set(action.get("requires") or []) != required:
        return {"state": "HOLD", "reason": "GATE12_REGISTRY_REQUIREMENTS_MISMATCH"}
    return {"state": "PASS", "action": action}


def gate12_final_readback_due(
    truth: dict[str, Any],
    gate12_snapshot: dict[str, Any],
) -> bool:
    return bool(
        truth.get("current_version") == "v0.8"
        and truth.get("current_state") == "VERIFIED_LOCKED"
        and truth.get("next_action") == "AWAIT_NEXT_OBJECTIVE"
        and truth.get("local_continuity_next_action") == "AWAIT_NEXT_OBJECTIVE"
        and gate12_snapshot.get("state") == "VERIFIED_LOCKED"
        and gate12_snapshot.get("canonicalLockCreated") is True
        and gate12_snapshot.get("finalLockReadback") == "PENDING_POST_COMMIT"
    )



def resolve_operator_continue_dispatch(
    action: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:

    normalized = str(
        action
        or "UNRESOLVED"
    )

    if registry is None:
        registry = (
            load_json(
                ACTION_REGISTRY,
                {},
            )
            or {}
        )

    actions = (
        registry.get("actions")
        or {}
    )

    contract = actions.get(
        normalized
    )

    if not isinstance(
        contract,
        dict,
    ):
        return {
            "STATE": "HOLD",
            "ACTION": normalized,
            "REGISTERED": False,
            "HANDLER": None,
            "AUTHORITY": None,
            "HOLD_REASON":
                "ACTION_HANDLER_NOT_REGISTERED",
            "NEXT_ACTION": normalized,
            "DISPATCH_EXECUTED": False,
            "DOWNSTREAM_ACTION_EXECUTED": False,
            "SOURCE_MUTATION_PERFORMED": False,
            "NETWORK_ACCESS_PERFORMED": False,
        }

    return {
        "STATE": "HOLD",
        "ACTION": normalized,
        "REGISTERED": True,
        "HANDLER":
            contract.get("handler"),
        "AUTHORITY":
            contract.get("authority"),
        "HOLD_REASON":
            "REGISTERED_NEXT_ACTION_REQUIRED",
        "NEXT_ACTION": normalized,
        "DISPATCH_EXECUTED": True,
        "DOWNSTREAM_ACTION_EXECUTED": False,
        "SOURCE_MUTATION_PERFORMED": False,
        "NETWORK_ACCESS_PERFORMED": False,
        "CONTRACT": contract,
    }

def command_continue() -> int:
    boot = canonical_boot()
    truth = current_truth()
    mirrors = sync_mirrors()
    runner = runner_status()
    action = str(truth.get("next_action") or "UNRESOLVED")
    local_action = str(truth.get("local_continuity_next_action") or "")
    fallback = truth.get("local_fallback") or {}
    session_snapshot = load_json(SESSION_STATE, {}) or {}
    v08_snapshot = session_snapshot.get("currentV08") or {}
    gate12_snapshot = v08_snapshot.get("gate12") or {}
    gate12_state = str(gate12_snapshot.get("state") or "")


    if boot.get("state") != "PASS":
        state = "HOLD"
        hold = "CANONICAL_BOOT"
        next_action = "enguru-mac doctor"
        completed = ["CANONICAL_BOOT_HOLD", "GITVAULT_SYNC"]
    elif gate12_final_readback_due(truth, gate12_snapshot):
        try:
            try:
                from mac_engineer_v08_gate12_final_lock_reconciler import (
                    verify_final_lock_readback,
                )
            except ModuleNotFoundError:
                from tools.mac_engineer_v08_gate12_final_lock_reconciler import (
                    verify_final_lock_readback,
                )
            gate12_final_lock = verify_final_lock_readback()
        except Exception as exc:
            gate12_final_lock = {
                "state": "HOLD",
                "reason": f"GATE12_FINAL_LOCK_READBACK:{type(exc).__name__}:{exc}",
            }
        state = "PASS" if gate12_final_lock.get("state") == "PASS" else "HOLD"
        hold = None if state == "PASS" else str(
            gate12_final_lock.get("reason") or "GATE12_FINAL_LOCK_READBACK_REQUIRED"
        )
        next_action = str(gate12_final_lock.get("nextAction") or "AWAIT_NEXT_OBJECTIVE")
        completed = [
            "CANONICAL_BOOT",
            "GITVAULT_SYNC",
            "V08_GATE12_FINAL_CANONICAL_LOCK_READBACK_" + state,
        ]
    elif (
        local_action == "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
        and gate12_state == "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"
    ):
        lock_path = Path(str(gate12_snapshot.get("lockEvidence") or ""))
        final_receipt_path = lock_path.parent / "final-acceptance-receipt.json"
        if final_receipt_path.is_file():
            try:
                try:
                    from mac_engineer_v08_gate12_final_lock_reconciler import (
                        prepare_final_lock_reconciliation,
                    )
                except ModuleNotFoundError:
                    from tools.mac_engineer_v08_gate12_final_lock_reconciler import (
                        prepare_final_lock_reconciliation,
                    )
                gate12_final_lock = prepare_final_lock_reconciliation()
            except Exception as exc:
                gate12_final_lock = {
                    "state": "HOLD",
                    "reason": f"GATE12_FINAL_LOCK_RECONCILIATION:{type(exc).__name__}:{exc}",
                }
            state = "HOLD"
            hold = str(
                gate12_final_lock.get("reason")
                or "GATE12_FINAL_LOCK_RECONCILIATION_REQUIRED"
            )
            next_action = str(
                gate12_final_lock.get("nextAction")
                or "COMMIT_PUSH_ACCEPT_AND_FRESH_READBACK"
            )
            completed = [
                "CANONICAL_BOOT",
                "GITVAULT_SYNC",
                "V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_PRESENT",
                "V08_GATE12_FINAL_LOCK_RECONCILIATION_" + (
                    "PREPARED"
                    if gate12_final_lock.get("canonicalLockCreated") is True
                    else "HOLD"
                ),
            ]
        else:
            try:
                if str(ROOT) not in sys.path:
                    sys.path.insert(0, str(ROOT))
                from tools.mac_engineer_v08_gate12_canonical_lock import (
                    publish_final_acceptance_receipt,
                )
                lock_readback = publish_final_acceptance_receipt()
            except Exception as exc:
                lock_readback = {
                    "state": "HOLD",
                    "reason": f"GATE12_LOCK_READBACK:{type(exc).__name__}:{exc}",
                }
            state = "HOLD"
            hold = str(
                lock_readback.get("reason")
                or "GATE12_FINAL_ACCEPTANCE_RECEIPT_REQUIRED"
            )
            next_action = str(
                lock_readback.get("nextAction")
                or "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
            )
            completed = [
                "CANONICAL_BOOT",
                "GITVAULT_SYNC",
                "V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_" + (
                    "PUBLISHED" if lock_readback.get("finalAcceptanceReceipt") else "HOLD"
                ),
            ]
    elif (
        local_action == "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
        and ((load_json(SESSION_STATE, {}) or {}).get("currentV08") or {})
        .get("gate12", {}).get("state") == "FIELD_ACCEPTED_PENDING_CANONICAL_LOCK"
    ):
        try:
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from tools.mac_engineer_v08_gate12_finalizer import publish_lock_evidence
            lock_evidence = publish_lock_evidence()
        except Exception as exc:
            lock_evidence = {
                "state": "HOLD", "reason": f"GATE12_LOCK_EVIDENCE:{type(exc).__name__}:{exc}"
            }
        state = "HOLD"
        hold = str(lock_evidence.get("reason") or "GATE12_CANONICAL_LOCK_PENDING")
        next_action = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
        completed = [
            "CANONICAL_BOOT", "GITVAULT_SYNC",
            "V08_GATE12_FIELD_ACCEPTANCE_RECORDED",
            "V08_GATE12_LOCK_EVIDENCE_" + (
                "PUBLISHED" if lock_evidence.get("lockEvidence") else "HOLD"
            ),
        ]
    elif local_action == "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        registry_contract = gate12_registry_contract(load_json(ACTION_REGISTRY, {}) or {})
        if registry_contract.get("state") != "PASS":
            prelock = registry_contract
        else:
            try:
                try:
                    from mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
                except ModuleNotFoundError:
                    from tools.mac_engineer_v08_gate12_pre005_executor import execute_from_runtime_handoff
                prelock = execute_from_runtime_handoff()
            except Exception as exc:
                prelock = {"state": "HOLD", "reason": f"PRE005_HANDLER:{type(exc).__name__}:{exc}"}
        completed.append("V08_GATE12_PRE005_BOUNDED_PRELOCK_" + str(prelock.get("state") or "HOLD"))
        if prelock.get("state") == "PASS":
            try:
                try:
                    from mac_engineer_v08_gate12_finalizer import finalize
                except ModuleNotFoundError:
                    from tools.mac_engineer_v08_gate12_finalizer import finalize
                finalization = finalize()
            except Exception as exc:
                finalization = {"state": "HOLD", "reason": f"BATCH3_FINALIZER:{type(exc).__name__}:{exc}"}
            state = "PASS" if finalization.get("state") == "PASS" else "HOLD"
            hold = None if state == "PASS" else str(finalization.get("reason") or "BATCH3_FINALIZATION_REQUIRED")
            next_action = str(finalization.get("nextAction") or "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK")
            completed.append("V08_GATE12_BATCH3_FINALIZATION_" + state)
        else:
            state = "HOLD"
            hold = str(prelock.get("reason") or "PRE005_BOUNDED_PRELOCK")
            next_action = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
    elif local_action == "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING":
        completed = [
            "CANONICAL_BOOT",
            "GITVAULT_SYNC",
        ]

        commissioning = (
            run_v08_gate11_consolidated_mac_commissioning()
        )

        passed = (
            commissioning.get("state")
            == "PASS"
        )

        fields = (
            commissioning.get("fields")
            or {}
        )

        if passed:
            if (
                fields.get("P12_ACCEPTANCE")
                == "15_OF_15_PASS"
            ):
                completed.extend([
                    "P12_P01_THROUGH_P11_PASS",
                    "P12_DONECHECK_V1_2_PASS",
                    "P12_CANONICAL_RECONCILIATION_PASS",
                    "P12_GATE11_EVIDENCE_BUNDLE_COMPLETE",
                    "P12_GATE11_ENGINEERING_EXECUTION_PASS",
                    "P12_ARCHITECTURE_STATE_PRESERVED",
                    "P12_NEW_CORE_FALSE",
                    "P12_HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
                    "P12_CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
                    "P12_UNTRACKED_MANUAL_STEP_COUNT_0",
                    "P12_GATE11_VERIFIED_LOCKED",
                    "P12_GATE11_EXIT_PASS",
                    "P12_ACTIVE_GATE_12",
                    "P12_GATE12_EXECUTION_0",
                    "P12_STOP_TRUE",
                ])
            elif (
                fields.get("P11_ACCEPTANCE")
                == "14_OF_14_PASS"
            ):
                completed.extend([
                    "P11_P10_PASS",
                    "P11_TARGETED_REGRESSION_PASS",
                    "P11_FULL_CONTROL_PLANE_REGRESSION_PASS",
                    "P11_PRODUCT_REGRESSION_PASS",
                    "P11_DIFF_CHECK_PASS",
                    "P11_SCOPE_CHECK_PASS",
                    "P11_PROVENANCE_CHECK_PASS",
                    "P11_RECOVERY_CHECK_PASS",
                    "P11_EVIDENCE_COMPLETENESS_PASS",
                    "P11_HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
                    "P11_CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
                    "P11_UNTRACKED_MANUAL_STEP_COUNT_0",
                    "P11_ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0",
                    "P11_CRITICAL_FALSE_PASS_0",
                ])
            elif (
                fields.get("P10_ACCEPTANCE")
                == "10_OF_10_PASS"
            ):
                completed.extend([
                    "P10_P09_PASS",
                    "P10_CHECKPOINT_CONTINUITY_PASS",
                    "P10_CONTROLLED_INTERRUPTION_PASS",
                    "P10_RESTART_RECOVERY_PASS",
                    "P10_SAME_TASK_RESUME_PASS",
                    "P10_IDEMPOTENCY_PASS",
                    "P10_EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS",
                    "P10_SINGLE_WRITER_DISCIPLINE_PASS",
                    "P10_BOUNDED_RETRY_PASS",
                    "P10_RECOVERY_EVIDENCE_PASS",
                ])
            elif (
                fields.get("P09_ACCEPTANCE")
                == "8_OF_8_PASS"
            ):
                completed.extend([
                    "P09_CONTROLLED_REPLACEMENT_PASS",
                    "P09_STOP_PASS",
                    "P09_RESTART_PASS",
                    "P09_KNOWN_GOOD_ROLLBACK_PASS",
                    "P09_ROLLBACK_REVERIFY_PASS",
                    "P09_LIFECYCLE_PROVENANCE_PASS",
                    "P09_EVIDENCE_CONTINUITY_PASS",
                ])
            else:
                completed.extend([
                    "P07_REAL_ENGINEERING_OBJECTIVE_COMPLETE",
                    "P07_EXPECTED_SCOPE_MATCH_PASS",
                    "P07_TARGETED_TEST_PASS",
                ])

        payload = write_receipt(
            command="continue",
            state=(
                "PASS"
                if passed
                else "HOLD"
            ),
            completed=completed,
            evidence=[
                str(SESSION_STATE),
            ],
            hold=(
                ""
                if passed
                else "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING"
            ),
            next_action=(
                fields.get(
                    "NEXT_ACTION"
                )
                or (
                    "P08"
                    if passed
                    else "enguru-mac doctor"
                )
            ),
            details={
                "truth":
                    truth,
                "boot":
                    boot,
                "runner":
                    runner,
                "mirrors":
                    mirrors,
                "gate11Commissioning":
                    commissioning,
            },
        )

        print_receipt(payload)

        return (
            0
            if passed
            else 2
        )

    elif local_action == "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO":
        completed = [
            "CANONICAL_BOOT",
            "GITVAULT_SYNC",
        ]

        gate10_delivery = run_v08_finished_product_delivery()

        if gate10_delivery.get("technical_state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item
                    for item in [
                        str(SESSION_STATE),
                        str(gate10_delivery.get("evidence") or ""),
                    ]
                    if item
                ],
                hold="V08_FINISHED_PRODUCT_DELIVERY_SCENARIO",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_finished_product_delivery":
                        gate10_delivery,
                },
            )

            print_receipt(payload)
            return 2

        completed.extend([
            "V08_FINISHED_PRODUCT_DELIVERY_TECHNICAL_PASS",
            "USER_FACING_DELIVERY_TECHNICAL_PASS",
            "OPERATIONAL_USAGE_PATH_TECHNICAL_PASS",
            "OPERATIONAL_STATUS_TECHNICAL_PASS",
            "FINISHED_RESULT_DELIVERY_TECHNICAL_PASS",
            "DELIVERY_EVIDENCE_BUNDLE_TECHNICAL_PASS",
            "FIELD_PRODUCT_MUTATION_FALSE",
            "UNNECESSARY_NEW_CORE_ZERO",
            "HUMAN_THRESHOLD_REVIEW_READY_PASS",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])

        state = "HOLD"
        hold = "HUMAN_DECISION_REQUIRED"
        next_action = (
            (gate10_delivery.get("fields") or {})
            .get("NEXT_ACTION")
            or "GATE10_HUMAN_DELIVERY_ACCEPTANCE"
        )

    elif local_action == "V08_EXISTING_PRODUCT_CHANGE_SCENARIO":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        v08_existing_change = run_v08_existing_product_change()

        if v08_existing_change.get("implementation_state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(v08_existing_change.get("evidence") or ""),
                    ] if item
                ],
                hold="V08_EXISTING_PRODUCT_CHANGE_SCENARIO",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_existing_change": v08_existing_change,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_EXISTING_PRODUCT_CHANGE_IMPLEMENTATION_PASS",
            "BOUNDED_PRODUCT_MUTATION_TWO_PATHS_PASS",
            "PRIMARY_STATE_SURFACE_PASS",
            "CONDITIONAL_ATTENTION_PASS",
            "VISIBLE_NEXT_ACTION_PASS",
            "NATURAL_LANGUAGE_COMPOSER_PRESERVED",
            "FULL_RUNTIME_REGRESSION_PASS",
            "SOURCE_INSTALLED_RUNTIME_PARITY_PASS",
            "RELEASE_PROVENANCE_PASS",
            "NATIVE_CODESIGN_PASS",
            "FRESH_APP_RUNTIME_READINESS_PASS",
            "PRODUCT_REMOTE_PUSH_FALSE",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])

        state = "HOLD"
        hold = "HUMAN_ARTISTIC_AUTHORITY_REQUIRED"
        next_action = (
            (v08_existing_change.get("fields") or {}).get("NEXT_ACTION")
            or "HUMAN_ARTISTIC_AUTHORITY_REVIEW"
        )
    elif local_action == "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        productization = run_v08_native_app_productization()
        if productization.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(productization.get("evidence") or ""),
                    ] if item
                ],
                hold="V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_native_app_productization": productization,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE_PASS",
            "PRODUCT_LOCAL_COMMIT_BOUND",
            "BUNDLE_VERSION_V08_PASS",
            "SOURCE_INSTALLED_RUNTIME_PARITY_PASS",
            "RELEASE_PROVENANCE_PASS",
            "NATIVE_CODESIGN_PASS",
            "FRESH_APP_RUNTIME_READINESS_PASS",
            "PRODUCT_REMOTE_PUSH_FALSE",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])
        state = "HOLD"
        hold = "V08_EXISTING_PRODUCT_CHANGE_SCENARIO_REQUIRED"
        next_action = (
            (productization.get("fields") or {}).get("NEXT_ACTION")
            or "V08_EXISTING_PRODUCT_CHANGE_SCENARIO"
        )
    elif local_action == "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        binding = run_v08_full_product_engineering_chain_binding()
        if binding.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[item for item in [str(SESSION_STATE), str(binding.get("evidence") or "")] if item],
                hold="V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING",
                next_action="enguru-mac doctor",
                details={
                    "truth":truth,
                    "boot":boot,
                    "runner":runner,
                    "mirrors":mirrors,
                    "v08_full_chain_binding":binding,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING_PASS",
            "PRODUCT_ENGINEERING_CHAIN_14_STAGE_BOUND",
            "EXISTING_MECHANISMS_REUSED",
            "DEPLOY_ADAPTER_BOUNDARY_DEFINED",
            "LATER_EXECUTION_PROOF_GATES_PRESERVED",
            "UNNECESSARY_NEW_CORE_ZERO",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])
        state = "HOLD"
        hold = "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE_REQUIRED"
        next_action = (
            (binding.get("fields") or {}).get("NEXT_ACTION")
            or "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE"
        )
    elif local_action == "V08_UX_AESTHETIC_PRODUCT_CONTRACT":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        ux_contract = run_v08_ux_aesthetic_product_contract()
        if ux_contract.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(ux_contract.get("evidence") or ""),
                    ] if item
                ],
                hold="V08_UX_AESTHETIC_PRODUCT_CONTRACT",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_ux_aesthetic_product_contract": ux_contract,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_UX_AESTHETIC_PRODUCT_CONTRACT_PASS",
            "PRIMARY_USER_QUESTIONS_THREE_PASS",
            "MAIN_SURFACE_SIMPLIFICATION_CONTRACT_PASS",
            "AESTHETIC_MOTOR_REUSE_PASS",
            "OVERFLOW_ORIGINALITY_ACCESSIBILITY_GATES_DEFINED",
            "HUMAN_ARTISTIC_AUTHORITY_GATE_DEFINED",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])
        state = "HOLD"
        hold = "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING_REQUIRED"
        next_action = (
            (ux_contract.get("fields") or {}).get("NEXT_ACTION")
            or "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING"
        )
    elif local_action == "V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        reconciliation = run_v08_product_reality_reconciliation()
        if reconciliation.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(reconciliation.get("evidence") or ""),
                    ] if item
                ],
                hold="V08_PRODUCT_REALITY_RECONCILIATION",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_product_reality_reconciliation": reconciliation,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_PRODUCT_REALITY_RECONCILIATION_PASS",
            "SOURCE_RUNTIME_INSTALLED_TRUTH_RECONCILED",
            "NATIVE_SHELL_WEB_RUNTIME_BOUNDARY_RECONCILED",
            "BOUNDED_REQUIRED_DIFFERENCE_DEFINED",
            "UNNECESSARY_NEW_CORE_ZERO",
            "DONECHECK_V1_2_AUTHORITY_PRESERVED",
        ])
        state = "HOLD"
        hold = "V08_UX_AESTHETIC_PRODUCT_CONTRACT_REQUIRED"
        next_action = (
            (reconciliation.get("fields") or {}).get("NEXT_ACTION")
            or "V08_UX_AESTHETIC_PRODUCT_CONTRACT"
        )
    elif local_action == "V08_SELF_ENGINEERING_BASELINE_AUDIT":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        v08_baseline = run_v08_self_engineering_baseline()
        if v08_baseline.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(v08_baseline.get("evidence") or ""),
                    ] if item
                ],
                hold="V08_SELF_ENGINEERING_BASELINE_AUDIT",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "v08_baseline": v08_baseline,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V08_SELF_ENGINEERING_BASELINE_AUDIT_PASS",
            "PRODUCT_RUNTIME_REGRESSION_PASS",
            "NATIVE_SWIFT_BUILD_PASS",
            "CURRENT_PRODUCT_REALITY_MEASURED",
            "DONECHECK_V1_2_AUTHORITY_BOUND",
        ])
        state = "HOLD"
        hold = "V08_PRODUCT_REALITY_RECONCILIATION_REQUIRED"
        next_action = (
            (v08_baseline.get("fields") or {}).get("NEXT_ACTION")
            or "V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION"
        )
    elif local_action == "V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        human_review = run_human_threshold_review()
        if human_review.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(human_review.get("evidence") or ""),
                    ] if item
                ],
                hold="HUMAN_THRESHOLD_REVIEW_PRECONDITION",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "human_review": human_review,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "HUMAN_THRESHOLD_REVIEW_READY_PASS",
            "ENGINEERING_GATES_12_OF_12_PASS",
            "DONECHECK_V12_PASS",
            "TECHNICAL_HOLD_ZERO",
            "EXTERNAL_A09_DEFERRED_PRESERVED",
        ])
        state = "HOLD"
        hold = "HUMAN_DECISION_REQUIRED"
        next_action = "EXPLICIT_HUMAN_ACCEPT_OR_HOLD"
    elif local_action == "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        final_campaign = run_final_consolidated_mac_campaign()
        if final_campaign.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(final_campaign.get("evidence") or ""),
                    ] if item
                ],
                hold="V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "final_campaign": final_campaign,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_PASS",
            "DURATION_GTE_8H_PASS",
            "THREE_CONTROLLED_INTERRUPTION_EVENTS_PASS",
            "TASK_IDENTITY_CONTINUITY_PASS",
            "EXACTLY_ONCE_EFFECT_PASS",
            "RSS_LIMITS_PASS",
            "STORAGE_RECONCILIATION_PASS",
            "FINAL_REGRESSIONS_PASS",
            "NATIVE_BUILD_PASS",
            "POST_CAMPAIGN_DONECHECK_V12_PASS",
            "TECHNICAL_HOLD_ZERO",
            "EXTERNAL_A09_DEFERRED_PRESERVED",
        ])
        state = "HOLD"
        hold = "V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION_REQUIRED"
        next_action = (
            (final_campaign.get("fields") or {}).get("NEXT_ACTION")
            or "V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION"
        )
    elif local_action == "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION":
        completed = ["CANONICAL_BOOT", "GITVAULT_SYNC"]
        local_authority_verification = run_donecheck_v12_local_authority_verification()
        if local_authority_verification.get("state") != "PASS":
            payload = write_receipt(
                command="continue",
                state="HOLD",
                completed=completed,
                evidence=[
                    item for item in [
                        str(SESSION_STATE),
                        str(local_authority_verification.get("evidence") or ""),
                    ] if item
                ],
                hold="DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION",
                next_action="enguru-mac doctor",
                details={
                    "truth": truth,
                    "boot": boot,
                    "runner": runner,
                    "mirrors": mirrors,
                    "local_authority_verification": local_authority_verification,
                },
            )
            print_receipt(payload)
            return 2

        completed.extend([
            "DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION_PASS",
            "GATE8_DONECHECK_PASS",
            "GATE9_DONECHECK_PASS",
            "GATE10_DONECHECK_PASS",
            "LOCAL_AUTHORITY_MIGRATION_MACHINE_VERIFICATION_PASS",
            "EXTERNAL_A09_DEFERRED_PRESERVED",
        ])
        state = "HOLD"
        hold = "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY_REQUIRED"
        next_action = (
            (local_authority_verification.get("fields") or {}).get("NEXT_ACTION")
            or "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY"
        )
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

        dispatch = resolve_operator_continue_dispatch(
            action,
            registry,
        )

        state = dispatch["STATE"]
        hold = dispatch["HOLD_REASON"]
        next_action = dispatch["NEXT_ACTION"]

        completed = [
            "CANONICAL_BOOT",
            "GITVAULT_SYNC",
        ]

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
                str((locals().get("local_authority_verification") or {}).get("evidence") or ""),
                str((locals().get("final_campaign") or {}).get("evidence") or ""),
                str((locals().get("human_review") or {}).get("evidence") or ""),
                str((locals().get("v08_baseline") or {}).get("evidence") or ""),
                str((locals().get("v08_existing_change") or {}).get("evidence") or ""),
                str((locals().get("finalization") or {}).get("fieldReceipt") or ""),
                str((locals().get("lock_evidence") or {}).get("lockEvidence") or ""),
                str((locals().get("lock_readback") or {}).get("lockEvidence") or ""),
                str((locals().get("lock_readback") or {}).get("finalAcceptanceReceipt") or ""),
                str((locals().get("gate12_final_lock") or {}).get("finalAcceptanceReceipt") or ""),
                str((locals().get("gate12_final_lock") or {}).get("finalLockEvidence") or ""),
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
            "local_authority_verification": locals().get("local_authority_verification"),
            "final_campaign": locals().get("final_campaign"),
            "human_review": locals().get("human_review"),
            "v08_baseline": locals().get("v08_baseline"),
            "v08_existing_change": locals().get("v08_existing_change"),
            "gate12_prelock": locals().get("prelock"),
            "gate12_finalization": locals().get("finalization"),
            "gate12_lock_evidence": locals().get("lock_evidence"),
            "gate12_lock_readback": locals().get("lock_readback"),
            "gate12_final_lock": locals().get("gate12_final_lock"),
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
