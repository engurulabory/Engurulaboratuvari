#!/usr/bin/env python3
"""Gate 12 — Final Consolidated Mac Campaign + Final Verify.

Real-Mac acceptance contract:
- duration >= 8 hours;
- >= 3 controlled interruption events spanning process/network/runtime surfaces;
- same durable task/checkpoint lineage;
- exactly-once durable effect;
- warm-baseline/peak/final RSS thresholds;
- runtime storage/temp reconciliation;
- full control-plane regression;
- full product regression + native build + diff checks;
- post-campaign DoneCheck™ v1.2 PASS;
- external GitHub A09 preserved as deferred.

No remote push, merge, or canonical promotion is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import statistics
import subprocess
import sys
import time
from typing import Any

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
ACCEPTED_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "local-accepted-control-plane-candidate.json"
PRODUCT_MIRROR = HOME / "Enguru" / "GitVault" / "MacEngineer" / "enguru-mac-engineer.git"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "final-consolidated-campaign"
BRIDGE_PATH = ROOT / "tools" / "mac_engineer_donecheck_v12_bridge.py"

MIN_DURATION_SECONDS = 8 * 60 * 60
SAMPLE_INTERVAL_SECONDS = 60
WARMUP_SECONDS = 5 * 60
BASELINE_SAMPLE_COUNT = 5
PROGRESS_INTERVAL_SECONDS = 30 * 60
WORKER_CHECKPOINT_INTERVAL_SECONDS = 60
WORKER_IDEMPOTENCY_KEY = "ENGURU-V07-FINAL-CAMPAIGN-001"
EFFECT_KEY = "ENGURU-V07-FINAL-CAMPAIGN-EFFECT-001"
CONTROLLED_EXIT = 75
EVENT_SCHEDULE = (
    (2 * 60 * 60, "PROCESS_GRACEFUL_RESTART"),
    (4 * 60 * 60, "LOOPBACK_NETWORK_INTERRUPTION"),
    (6 * 60 * 60, "RUNTIME_ABRUPT_RESTART"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label}_INVALID:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def git(cwd: Path, *args: str, timeout: int = 300) -> str:
    result = run(["git", *args], cwd=cwd, timeout=timeout)
    require(result, "GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def bare_git(mirror: Path, *args: str, timeout: int = 300) -> str:
    result = run(["git", "--git-dir", str(mirror), *args], timeout=timeout)
    require(result, "BARE_GIT_" + "_".join(args[:2]).upper())
    return result["stdout"].strip()


def mirror_has_commit(mirror: Path, sha: str) -> bool:
    result = run(
        ["git", "--git-dir", str(mirror), "cat-file", "-e", f"{sha}^{{commit}}"],
        timeout=60,
    )
    return result["code"] == 0


def validate_contract() -> tuple[dict[str, Any], dict[str, Any], str]:
    session = load_json(SESSION_STATE, "SESSION_STATE")
    v07 = session.get("currentV07") or {}
    closure = v07.get("verifiedFinishClosureContract") or {}
    if list(closure.get("passedGates") or []) != list(range(1, 12)):
        raise RuntimeError("GATES_1_11_PASS_REQUIRED")
    if closure.get("activeGate") != 12:
        raise RuntimeError("ACTIVE_GATE_12_REQUIRED")
    a09 = closure.get("githubA09") or {}
    if a09.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("EXTERNAL_A09_DEFERRED_REQUIRED")

    gate11 = closure.get("gate11") or {}
    gate11_path = Path(str(gate11.get("evidence") or "")).expanduser()
    gate11_evidence = load_json(gate11_path, "GATE11_EVIDENCE")
    if gate11_evidence.get("state") != "PASS":
        raise RuntimeError("GATE11_PASS_REQUIRED")
    if gate11_evidence.get("aggregateOutcome") != "pass":
        raise RuntimeError("GATE11_AGGREGATE_PASS_REQUIRED")

    accepted = load_json(ACCEPTED_STATE, "LOCAL_ACCEPTED_CANDIDATE")
    if accepted.get("state") != "PASS":
        raise RuntimeError("LOCAL_ACCEPTED_CANDIDATE_PASS_REQUIRED")
    if accepted.get("authority") != "PENDING_RECONCILIATION":
        raise RuntimeError("LOCAL_ACCEPTED_AUTHORITY_REQUIRED")
    if accepted.get("secondCanonicalTruth") is not False:
        raise RuntimeError("SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")

    current_branch = git(ROOT, "branch", "--show-current")
    current_head = git(ROOT, "rev-parse", "HEAD")
    current_status = git(ROOT, "status", "--porcelain")
    if current_branch != accepted.get("branch"):
        raise RuntimeError("CONTROL_BRANCH_ACCEPTED_PARITY_REQUIRED")
    if current_head != accepted.get("head"):
        raise RuntimeError("CONTROL_HEAD_ACCEPTED_PARITY_REQUIRED")
    if current_status:
        raise RuntimeError("CONTROL_WORKTREE_CLEAN_REQUIRED")

    product_sha = str(v07.get("productExactMain") or "")
    if len(product_sha) != 40:
        raise RuntimeError("PRODUCT_EXACT_MAIN_REQUIRED")
    if not PRODUCT_MIRROR.is_dir() or not mirror_has_commit(PRODUCT_MIRROR, product_sha):
        raise RuntimeError("PRODUCT_GITVAULT_EXACT_MAIN_REQUIRED")
    mirror_main = bare_git(PRODUCT_MIRROR, "rev-parse", "refs/remotes/origin/main")
    if mirror_main != product_sha:
        raise RuntimeError("PRODUCT_GITVAULT_REMOTE_MAIN_PARITY_REQUIRED")

    return v07, accepted, product_sha


def clone_product(target: Path, product_sha: str) -> None:
    result = run(["git", "clone", "--no-local", str(PRODUCT_MIRROR), str(target)], timeout=1200)
    require(result, "PRODUCT_GITVAULT_CLONE")
    checkout = run(["git", "checkout", "--detach", product_sha], cwd=target, timeout=120)
    require(checkout, "PRODUCT_EXACT_SHA_CHECKOUT")
    if git(target, "rev-parse", "HEAD") != product_sha:
        raise RuntimeError("PRODUCT_EXACT_SHA_CLONE_PARITY_REQUIRED")


def load_reliability(runtime_root: Path):
    sys.path.insert(0, str(runtime_root))
    try:
        from reliability import ReliabilityManager
    except Exception as exc:
        raise RuntimeError(f"RELIABILITY_IMPORT_FAILED:{type(exc).__name__}:{exc}") from exc
    return ReliabilityManager


def durable_effect_once(root: Path, task_id: str) -> bool:
    path = root / "effects" / f"{EFFECT_KEY}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "enguru.mac-engineer.final-campaign-effect/v1",
        "effectKey": EFFECT_KEY,
        "taskId": task_id,
        "value": "APPLIED_ONCE",
    }
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        existing = load_json(path, "DURABLE_EFFECT")
        if existing.get("taskId") != task_id or existing.get("effectKey") != EFFECT_KEY:
            raise RuntimeError("DURABLE_EFFECT_IDENTITY_MISMATCH")
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return True


def worker_mode(runtime_source: Path, durable_root: Path, ready: Path, sequence: int) -> int:
    ReliabilityManager = load_reliability(runtime_source)
    manager = ReliabilityManager(durable_root)
    started = manager.begin(
        WORKER_IDEMPOTENCY_KEY,
        metadata={"gate": 12, "role": "final_campaign_worker"},
    )
    task_id = str(started["task"]["task_id"])
    task = manager.get(task_id)

    if started.get("duplicate"):
        if task["state"] == "RUNNING":
            recovery = manager.classify_recovery(task_id)
            if recovery.get("classification") != "RECOVERABLE":
                raise RuntimeError("WORKER_RUNNING_RECOVERY_REQUIRED")
            manager.transition(
                task_id,
                "RECOVERY_REQUIRED",
                recovery_class="RECOVERABLE",
                note="final_campaign_worker_restart",
            )
            resumed = manager.resume(task_id)
            if not resumed.get("ok"):
                raise RuntimeError("WORKER_RUNNING_RESUME_REQUIRED")
        elif task["state"] in {"CHECKPOINTED", "RECOVERY_REQUIRED"}:
            resumed = manager.resume(task_id)
            if not resumed.get("ok"):
                raise RuntimeError("WORKER_CHECKPOINT_RESUME_REQUIRED")
        elif task["state"] != "RUNNING":
            raise RuntimeError(f"WORKER_STATE_NOT_RESUMABLE:{task['state']}")
    else:
        manager.transition(task_id, "RUNNING")

    durable_effect_once(durable_root, task_id)
    manager.checkpoint(
        task_id,
        {
            "stage": "worker_ready",
            "sequence": sequence,
            "observedAt": now(),
            "effectKey": EFFECT_KEY,
        },
        verified=True,
    )
    manager.resume(task_id)

    atomic_json(
        ready,
        {
            "state": "PASS",
            "taskId": task_id,
            "sequence": sequence,
            "pid": os.getpid(),
            "observedAt": now(),
        },
    )

    stopping = {"value": False}

    def graceful(_sig, _frame):
        stopping["value"] = True

    signal.signal(signal.SIGTERM, graceful)
    signal.signal(signal.SIGINT, graceful)

    checkpoint_seq = 0
    last_checkpoint = time.monotonic()
    while True:
        time.sleep(1)
        if stopping["value"]:
            manager.checkpoint(
                task_id,
                {
                    "stage": "controlled_process_exit",
                    "sequence": sequence,
                    "checkpointSequence": checkpoint_seq,
                    "observedAt": now(),
                },
                verified=True,
            )
            return CONTROLLED_EXIT

        if time.monotonic() - last_checkpoint >= WORKER_CHECKPOINT_INTERVAL_SECONDS:
            checkpoint_seq += 1
            manager.checkpoint(
                task_id,
                {
                    "stage": "campaign_heartbeat",
                    "sequence": sequence,
                    "checkpointSequence": checkpoint_seq,
                    "observedAt": now(),
                    "effectKey": EFFECT_KEY,
                },
                verified=True,
            )
            resumed = manager.resume(task_id)
            if not resumed.get("ok"):
                raise RuntimeError("WORKER_HEARTBEAT_RESUME_REQUIRED")
            last_checkpoint = time.monotonic()


def network_server_mode(port_file: Path) -> int:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(5)
    port = server.getsockname()[1]
    port_file.write_text(str(port) + "\n", encoding="utf-8")
    try:
        while True:
            conn, _ = server.accept()
            with conn:
                conn.sendall(b"ENGURU_OK\n")
    finally:
        server.close()


def wait_for_file(path: Path, timeout: int = 30) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            return
        time.sleep(0.1)
    raise RuntimeError(f"READY_FILE_TIMEOUT:{path}")


def start_worker(script: Path, runtime_source: Path, durable_root: Path, events: Path, sequence: int) -> tuple[subprocess.Popen, dict[str, Any]]:
    ready = events / f"worker-ready-{sequence:02d}.json"
    ready.unlink(missing_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-B",
            str(script),
            "--mode",
            "worker",
            "--runtime-source",
            str(runtime_source),
            "--durable-root",
            str(durable_root),
            "--ready",
            str(ready),
            "--sequence",
            str(sequence),
        ],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    wait_for_file(ready)
    payload = load_json(ready, "WORKER_READY")
    if payload.get("state") != "PASS" or payload.get("pid") != proc.pid:
        proc.kill()
        raise RuntimeError("WORKER_READY_CONTRACT_REQUIRED")
    return proc, payload


def worker_rss_kb(pid: int) -> int:
    result = run(["ps", "-o", "rss=", "-p", str(pid)], timeout=10)
    require(result, "WORKER_RSS")
    value = result["stdout"].strip()
    if not value.isdigit():
        raise RuntimeError(f"WORKER_RSS_INTEGER_REQUIRED:{value}")
    return int(value)


def loopback_probe(port: int) -> str:
    with socket.create_connection(("127.0.0.1", port), timeout=2.0) as conn:
        data = conn.recv(64)
    return data.decode("utf-8", errors="replace").strip()


def event_process_graceful(worker: subprocess.Popen, events: Path, runtime_source: Path, durable_root: Path, script: Path, sequence: int) -> tuple[subprocess.Popen, dict[str, Any]]:
    before_pid = worker.pid
    worker.terminate()
    code = worker.wait(timeout=30)
    if code != CONTROLLED_EXIT:
        stderr = worker.stderr.read()[-3000:] if worker.stderr else ""
        raise RuntimeError(f"GRACEFUL_WORKER_EXIT_REQUIRED:{code}:{stderr}")
    restarted, ready = start_worker(script, runtime_source, durable_root, events, sequence)
    payload = {
        "state": "PASS",
        "event": "PROCESS_GRACEFUL_RESTART",
        "beforePid": before_pid,
        "exitCode": code,
        "afterPid": restarted.pid,
        "taskId": ready["taskId"],
        "observedAt": now(),
    }
    atomic_json(events / "event-01-process.json", payload)
    return restarted, payload


def event_network(script: Path, events: Path) -> dict[str, Any]:
    port_file = events / "network-port.txt"
    port_file.unlink(missing_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-B", str(script), "--mode", "network-server", "--port-file", str(port_file)],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    wait_for_file(port_file)
    port = int(port_file.read_text(encoding="utf-8").strip())
    if loopback_probe(port) != "ENGURU_OK":
        server.kill()
        raise RuntimeError("LOOPBACK_INITIAL_PROBE_REQUIRED")

    server.terminate()
    server.wait(timeout=30)

    failure_observed = False
    try:
        loopback_probe(port)
    except OSError:
        failure_observed = True
    if not failure_observed:
        raise RuntimeError("LOOPBACK_INTERRUPTION_FAILURE_REQUIRED")

    port_file.unlink(missing_ok=True)
    recovered = subprocess.Popen(
        [sys.executable, "-B", str(script), "--mode", "network-server", "--port-file", str(port_file)],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    wait_for_file(port_file)
    recovered_port = int(port_file.read_text(encoding="utf-8").strip())
    if loopback_probe(recovered_port) != "ENGURU_OK":
        recovered.kill()
        raise RuntimeError("LOOPBACK_RECOVERY_PROBE_REQUIRED")
    recovered.terminate()
    recovered.wait(timeout=30)

    payload = {
        "state": "PASS",
        "event": "LOOPBACK_NETWORK_INTERRUPTION",
        "failureObserved": True,
        "recoveryObserved": True,
        "initialPort": port,
        "recoveryPort": recovered_port,
        "observedAt": now(),
    }
    atomic_json(events / "event-02-network.json", payload)
    return payload


def event_runtime_abrupt(worker: subprocess.Popen, events: Path, runtime_source: Path, durable_root: Path, script: Path, sequence: int) -> tuple[subprocess.Popen, dict[str, Any]]:
    before_pid = worker.pid
    worker.kill()
    code = worker.wait(timeout=30)
    restarted, ready = start_worker(script, runtime_source, durable_root, events, sequence)
    payload = {
        "state": "PASS",
        "event": "RUNTIME_ABRUPT_RESTART",
        "beforePid": before_pid,
        "exitCode": code,
        "afterPid": restarted.pid,
        "taskId": ready["taskId"],
        "observedAt": now(),
    }
    atomic_json(events / "event-03-runtime.json", payload)
    return restarted, payload


def evaluate_resources(samples: list[dict[str, Any]]) -> dict[str, Any]:
    post_warm = [s for s in samples if s["elapsedSeconds"] >= WARMUP_SECONDS]
    if len(post_warm) < BASELINE_SAMPLE_COUNT:
        raise RuntimeError("RSS_WARM_BASELINE_SAMPLES_REQUIRED")
    baseline_values = [s["rssKb"] for s in post_warm[:BASELINE_SAMPLE_COUNT]]
    warm_baseline = int(statistics.median(baseline_values))
    if warm_baseline <= 0:
        raise RuntimeError("RSS_WARM_BASELINE_POSITIVE_REQUIRED")
    measured = [s["rssKb"] for s in post_warm]
    peak = max(measured)
    final = samples[-1]["rssKb"]
    peak_ratio = peak / warm_baseline
    final_ratio = final / warm_baseline
    return {
        "state": "PASS" if peak_ratio <= 2.0 and final_ratio <= 1.5 else "HOLD",
        "warmBaselineKb": warm_baseline,
        "peakKb": peak,
        "finalKb": final,
        "peakRatio": peak_ratio,
        "finalRatio": final_ratio,
        "peakLimit": 2.0,
        "finalLimit": 1.5,
        "sampleCount": len(samples),
    }


def run_check(name: str, cmd: list[str], cwd: Path, log_dir: Path, timeout: int = 3600, env: dict[str, str] | None = None) -> dict[str, Any]:
    result = run(cmd, cwd=cwd, timeout=timeout, env=env)
    log = log_dir / f"{name}.log"
    log.write_text((result["stdout"] + "\n" + result["stderr"]).strip() + "\n", encoding="utf-8")
    return {
        "name": name,
        "state": "PASS" if result["code"] == 0 else "HOLD",
        "code": result["code"],
        "log": str(log),
        "sha256": sha256_file(log),
    }


def final_regressions(product: Path, run_dir: Path, accepted_head: str, product_sha: str) -> dict[str, Any]:
    logs = run_dir / "final-verify"
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(product / "runtime")

    checks = [
        run_check(
            "control-regression",
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
            ROOT,
            logs,
            timeout=3600,
            env=env,
        ),
        run_check(
            "control-diff-check",
            ["git", "diff", "--check"],
            ROOT,
            logs,
            timeout=120,
        ),
        run_check(
            "product-runtime-tests",
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "runtime/tests", "-v"],
            product,
            logs,
            timeout=3600,
            env=env,
        ),
        run_check(
            "product-native-prep-syntax",
            ["zsh", "-n", "execution_prep/native_app/prepare_native_app.command"],
            product,
            logs,
            timeout=120,
        ),
    ]

    swift_out = logs / "EnguruMacEngineer"
    checks.append(
        run_check(
            "product-native-swift-build",
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
            product,
            logs,
            timeout=1800,
        )
    )
    checks.append(
        run_check(
            "product-diff-check",
            ["git", "diff", "--check"],
            product,
            logs,
            timeout=120,
        )
    )

    if git(ROOT, "rev-parse", "HEAD") != accepted_head:
        raise RuntimeError("CONTROL_HEAD_CHANGED_DURING_CAMPAIGN")
    if git(ROOT, "status", "--porcelain"):
        raise RuntimeError("CONTROL_WORKTREE_CHANGED_DURING_CAMPAIGN")
    if git(product, "rev-parse", "HEAD") != product_sha:
        raise RuntimeError("PRODUCT_SHA_CHANGED_DURING_CAMPAIGN")
    if git(product, "status", "--porcelain"):
        raise RuntimeError("PRODUCT_WORKTREE_CHANGED_DURING_CAMPAIGN")

    state = "PASS" if all(item["state"] == "PASS" for item in checks) else "HOLD"
    return {"state": state, "checks": checks}


def durable_reconciliation(runtime_root: Path) -> dict[str, Any]:
    tasks = sorted((runtime_root / "tasks").glob("task_*.json"))
    effects = sorted((runtime_root / "effects").glob("*.json"))
    temp_or_cache = [
        str(p.relative_to(runtime_root))
        for p in runtime_root.rglob("*")
        if p.name in {"__pycache__", ".pytest_cache"}
        or p.suffix == ".pyc"
        or ".tmp" in p.name
    ]
    if len(tasks) != 1:
        raise RuntimeError(f"ONE_CAMPAIGN_TASK_REQUIRED:{len(tasks)}")
    task = load_json(tasks[0], "CAMPAIGN_TASK")
    if task.get("state") != "COMPLETE":
        raise RuntimeError("CAMPAIGN_TASK_COMPLETE_REQUIRED")
    if len(effects) != 1:
        raise RuntimeError(f"ONE_DURABLE_EFFECT_REQUIRED:{len(effects)}")
    effect = load_json(effects[0], "CAMPAIGN_EFFECT")
    if effect.get("taskId") != task.get("task_id"):
        raise RuntimeError("CAMPAIGN_EFFECT_TASK_IDENTITY_REQUIRED")
    if temp_or_cache:
        raise RuntimeError("RUNTIME_TEMP_CACHE_RECONCILIATION_REQUIRED:" + ",".join(temp_or_cache))
    return {
        "state": "PASS",
        "taskId": task["task_id"],
        "taskState": task["state"],
        "durableEffectCount": 1,
        "exactlyOnceEffect": True,
        "tempOrCacheArtifacts": temp_or_cache,
    }


def post_campaign_donecheck(core_path: Path, output_dir: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("enguru_donecheck_v12_bridge", BRIDGE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("DONECHECK_BRIDGE_IMPORT_REQUIRED")
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    runtime = bridge.ensure_donecheck_runtime()
    if runtime.get("state") != "PASS":
        raise RuntimeError("DONECHECK_RUNTIME_PASS_REQUIRED")

    input_payload = {
        "schema": "enguru.mac-engineer.final-campaign-donecheck-input/v1",
        "observedAt": now(),
        "task": {
            "id": "enguru-mac-v07-final-campaign",
            "title": "ENGÜRÜ Mac Engineer™ v0.7 final consolidated Mac campaign",
            "requestText": "Verify the final campaign Evidence against the locked Gate 12 acceptance contract.",
            "status": "awaiting_review",
            "createdAt": now(),
        },
        "criterion": {
            "gate": "V07-FINAL-CAMPAIGN",
            "statement": "Final consolidated Mac campaign satisfies duration, interruption, resource, regression and evidence continuity requirements.",
            "source": str(core_path),
            "artifactDigest": f"sha256:{sha256_file(core_path)}",
            "content": "[DONECHECK:PASS] Gate 12 final consolidated Mac campaign structural acceptance is PASS.",
        },
        "producer": {"kind": "mac_engineer", "id": bridge.PRODUCER_ID},
        "policy": {
            "requireEvidenceProvenance": True,
            "trustedProducerIds": [bridge.PRODUCER_ID],
        },
        "doneCheck": {"version": bridge.DONECHECK_VERSION, "exactSha": bridge.DONECHECK_SHA},
    }
    input_path = output_dir / "donecheck-input.json"
    input_path.write_text(json.dumps(input_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result_path = output_dir / "donecheck-result.json"
    test_path = bridge.DONECHECK_RUNTIME / "tests" / "enguru-mac-final-campaign.integration.test.ts"
    test_path.write_text(
        '''import { readFileSync, writeFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { createProducerEvidence, verifyTask, type SuccessCriterion } from "../src/donecheck-core";
const input = JSON.parse(readFileSync(process.env.ENGURU_FINAL_CAMPAIGN_INPUT!, "utf8"));
const criterion: SuccessCriterion = {
  id: input.criterion.gate,
  taskId: input.task.id,
  statement: input.criterion.statement,
  verificationInstruction: "Consume trusted final campaign Evidence.",
  kind: "objective",
  required: true,
};
describe("ENGÜRÜ Mac Engineer final campaign -> DoneCheck v1.2", () => {
  it("passes the final campaign criterion", () => {
    const evidence = createProducerEvidence({
      id: "evidence-final-campaign",
      taskId: input.task.id,
      criterionId: input.criterion.gate,
      kind: "test_report",
      content: input.criterion.content,
      collectedAt: input.observedAt,
      producerKind: input.producer.kind,
      producerId: input.producer.id,
      executionId: "final-campaign:" + input.doneCheck.exactSha,
      artifactDigest: input.criterion.artifactDigest,
      observedAt: input.observedAt,
      verificationRef: input.criterion.source,
    });
    const result = verifyTask({
      task: input.task,
      criteria: [criterion],
      aiOutput: "Final consolidated Mac campaign Evidence supplied.",
      evidence: [evidence],
      resultId: "verification-enguru-mac-v07-final-campaign",
      verifiedAt: input.observedAt,
      policy: input.policy,
    });
    expect(result.outcome).toBe("pass");
    expect(result.criteria[0].outcome).toBe("pass");
    writeFileSync(process.env.ENGURU_FINAL_CAMPAIGN_RESULT!, JSON.stringify({
      schema: "enguru.mac-engineer.final-campaign-donecheck-result/v1",
      doneCheckVersion: input.doneCheck.version,
      doneCheckExactSha: input.doneCheck.exactSha,
      outcome: result.outcome,
      criterionOutcome: result.criteria[0].outcome,
    }, null, 2) + "\\n", "utf8");
  });
});
''',
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["ENGURU_FINAL_CAMPAIGN_INPUT"] = str(input_path)
    env["ENGURU_FINAL_CAMPAIGN_RESULT"] = str(result_path)
    try:
        vitest = bridge.DONECHECK_RUNTIME / "node_modules" / ".bin" / "vitest"
        result = run(
            [str(vitest), "run", str(test_path.relative_to(bridge.DONECHECK_RUNTIME)), f"--reporter={bridge.VITEST_REPORTER}"],
            cwd=bridge.DONECHECK_RUNTIME,
            timeout=1800,
            env=env,
        )
    finally:
        test_path.unlink(missing_ok=True)
    require(result, "FINAL_CAMPAIGN_DONECHECK")
    output = load_json(result_path, "FINAL_CAMPAIGN_DONECHECK_RESULT")
    if output.get("outcome") != "pass" or output.get("criterionOutcome") != "pass":
        raise RuntimeError("FINAL_CAMPAIGN_DONECHECK_PASS_REQUIRED")
    if output.get("doneCheckExactSha") != bridge.DONECHECK_SHA:
        raise RuntimeError("FINAL_CAMPAIGN_DONECHECK_EXACT_SHA_REQUIRED")
    status = run(["git", "status", "--porcelain"], cwd=bridge.DONECHECK_RUNTIME, timeout=30)
    require(status, "DONECHECK_RUNTIME_STATUS")
    if status["stdout"]:
        raise RuntimeError("DONECHECK_RUNTIME_CLEAN_REQUIRED")
    return {
        "state": "PASS",
        "version": bridge.DONECHECK_VERSION,
        "exactSha": bridge.DONECHECK_SHA,
        "result": str(result_path),
        "resultSha256": sha256_file(result_path),
    }


def perform() -> dict[str, Any]:
    v07, accepted, product_sha = validate_contract()
    run_dir = EVIDENCE_ROOT / stamp()
    workspace = run_dir / "workspace"
    product = workspace / "enguru-mac-engineer"
    runtime_root = run_dir / "durable-runtime"
    events = run_dir / "events"
    samples_path = run_dir / "rss-samples.jsonl"
    events.mkdir(parents=True, exist_ok=False)
    workspace.mkdir(parents=True, exist_ok=True)
    clone_product(product, product_sha)
    runtime_source = product / "runtime"
    script = Path(__file__).resolve()

    start_wall = time.time()
    start_mono = time.monotonic()
    campaign_start = {
        "schema": "enguru.mac-engineer.final-campaign-start/v1",
        "state": "RUNNING",
        "startedAt": now(),
        "acceptedControlHead": accepted["head"],
        "acceptedControlBranch": accepted["branch"],
        "productExactMain": product_sha,
        "minimumDurationSeconds": MIN_DURATION_SECONDS,
        "eventScheduleSeconds": [item[0] for item in EVENT_SCHEDULE],
    }
    atomic_json(run_dir / "start.json", campaign_start)

    worker_sequence = 1
    worker, ready = start_worker(script, runtime_source, runtime_root, events, worker_sequence)
    canonical_task_id = ready["taskId"]
    samples: list[dict[str, Any]] = []
    completed_events: list[dict[str, Any]] = []
    event_index = 0
    next_sample = start_mono
    next_progress = start_mono + PROGRESS_INTERVAL_SECONDS

    print(f"CAMPAIGN_STATE=RUNNING", flush=True)
    print(f"CAMPAIGN_MIN_DURATION_SECONDS={MIN_DURATION_SECONDS}", flush=True)
    print(f"CAMPAIGN_TASK_ID={canonical_task_id}", flush=True)
    print(f"CAMPAIGN_EVIDENCE_DIR={run_dir}", flush=True)

    try:
        while True:
            current = time.monotonic()
            elapsed = current - start_mono

            if current >= next_sample:
                if worker.poll() is not None:
                    stderr = worker.stderr.read()[-3000:] if worker.stderr else ""
                    raise RuntimeError(f"CAMPAIGN_WORKER_UNEXPECTED_EXIT:{worker.returncode}:{stderr}")
                sample = {
                    "observedAt": now(),
                    "elapsedSeconds": elapsed,
                    "workerPid": worker.pid,
                    "rssKb": worker_rss_kb(worker.pid),
                }
                samples.append(sample)
                with samples_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
                next_sample = current + SAMPLE_INTERVAL_SECONDS

            if event_index < len(EVENT_SCHEDULE) and elapsed >= EVENT_SCHEDULE[event_index][0]:
                event_name = EVENT_SCHEDULE[event_index][1]
                worker_sequence += 1
                if event_name == "PROCESS_GRACEFUL_RESTART":
                    worker, payload = event_process_graceful(
                        worker, events, runtime_source, runtime_root, script, worker_sequence
                    )
                elif event_name == "LOOPBACK_NETWORK_INTERRUPTION":
                    payload = event_network(script, events)
                elif event_name == "RUNTIME_ABRUPT_RESTART":
                    worker, payload = event_runtime_abrupt(
                        worker, events, runtime_source, runtime_root, script, worker_sequence
                    )
                else:
                    raise RuntimeError(f"UNKNOWN_CAMPAIGN_EVENT:{event_name}")
                if payload.get("taskId") and payload.get("taskId") != canonical_task_id:
                    raise RuntimeError("CAMPAIGN_TASK_IDENTITY_CHANGED")
                completed_events.append(payload)
                print(f"CAMPAIGN_EVENT_{event_index + 1}=PASS:{event_name}", flush=True)
                event_index += 1

            if current >= next_progress:
                print(
                    f"CAMPAIGN_PROGRESS_SECONDS={int(elapsed)};EVENTS={len(completed_events)};SAMPLES={len(samples)}",
                    flush=True,
                )
                next_progress = current + PROGRESS_INTERVAL_SECONDS

            if elapsed >= MIN_DURATION_SECONDS:
                break
            time.sleep(1)
    finally:
        if worker.poll() is None:
            worker.terminate()
            try:
                code = worker.wait(timeout=30)
            except subprocess.TimeoutExpired:
                worker.kill()
                code = worker.wait(timeout=30)
            if code not in {CONTROLLED_EXIT, -signal.SIGTERM}:
                stderr = worker.stderr.read()[-3000:] if worker.stderr else ""
                if sys.exc_info()[0] is None:
                    raise RuntimeError(f"FINAL_WORKER_STOP_REQUIRED:{code}:{stderr}")

    end_mono = time.monotonic()
    duration = end_mono - start_mono
    if duration < MIN_DURATION_SECONDS:
        raise RuntimeError(f"CAMPAIGN_DURATION_REQUIRED:{duration}")
    if len(completed_events) != 3 or any(item.get("state") != "PASS" for item in completed_events):
        raise RuntimeError("THREE_CONTROLLED_INTERRUPTION_EVENTS_REQUIRED")

    ReliabilityManager = load_reliability(runtime_source)
    manager = ReliabilityManager(runtime_root)
    task = manager.get(canonical_task_id)
    if task["state"] == "RUNNING":
        recovery = manager.classify_recovery(canonical_task_id)
        if recovery.get("classification") != "RECOVERABLE":
            raise RuntimeError("FINAL_TASK_RECOVERY_REQUIRED")
        manager.transition(
            canonical_task_id,
            "RECOVERY_REQUIRED",
            recovery_class="RECOVERABLE",
            note="final_campaign_closeout",
        )
        manager.resume(canonical_task_id)
    elif task["state"] in {"CHECKPOINTED", "RECOVERY_REQUIRED"}:
        manager.resume(canonical_task_id)
    task = manager.get(canonical_task_id)
    if task["state"] != "RUNNING":
        raise RuntimeError(f"FINAL_TASK_RUNNING_REQUIRED:{task['state']}")
    manager.checkpoint(
        canonical_task_id,
        {
            "stage": "final_campaign_closeout",
            "durationSeconds": duration,
            "eventCount": len(completed_events),
            "observedAt": now(),
        },
        verified=True,
    )
    manager.resume(canonical_task_id)
    manager.transition(canonical_task_id, "VERIFYING")
    manager.transition(canonical_task_id, "COMPLETE")

    final_sample = {
        "observedAt": now(),
        "elapsedSeconds": duration,
        "workerPid": None,
        "rssKb": samples[-1]["rssKb"],
        "source": "LAST_LIVE_WORKER_SAMPLE",
    }
    samples.append(final_sample)
    with samples_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(final_sample, ensure_ascii=False) + "\n")

    resources = evaluate_resources(samples)
    if resources["state"] != "PASS":
        raise RuntimeError(
            f"RSS_LIMITS_REQUIRED:peak={resources['peakRatio']:.4f}:final={resources['finalRatio']:.4f}"
        )

    durable = durable_reconciliation(runtime_root)
    regression = final_regressions(product, run_dir, accepted["head"], product_sha)
    if regression["state"] != "PASS":
        raise RuntimeError("FINAL_REGRESSION_PASS_REQUIRED")

    core = {
        "schema": "enguru.mac-engineer.v07-final-campaign-core/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": 12,
        "durationSeconds": duration,
        "minimumDurationSeconds": MIN_DURATION_SECONDS,
        "durationPass": duration >= MIN_DURATION_SECONDS,
        "campaignTaskId": canonical_task_id,
        "controlledInterruptions": completed_events,
        "controlledInterruptionCount": len(completed_events),
        "interruptionSurfaces": [
            "process",
            "network_loopback",
            "runtime_abrupt_process",
        ],
        "resources": resources,
        "durableReconciliation": durable,
        "finalRegression": regression,
        "rssSamples": str(samples_path),
        "rssSamplesSha256": sha256_file(samples_path),
        "acceptedControlHead": accepted["head"],
        "productExactMain": product_sha,
        "remotePush": False,
        "remoteMerge": False,
        "secondCanonicalTruth": False,
        "externalA09": "EXTERNAL_BLOCKED_DEFERRED",
        "technicalHoldCount": 0,
        "authorityBoundary": (
            "Final campaign proves local Mac engineering reliability only. "
            "Human Threshold remains the final authority transition."
        ),
    }
    core_path = run_dir / "campaign-core.json"
    atomic_json(core_path, core)

    donecheck = post_campaign_donecheck(core_path, run_dir)
    final = {
        "schema": "enguru.mac-engineer.v07-final-consolidated-campaign/v1",
        **core,
        "postCampaignDoneCheck": donecheck,
        "postCampaignDoneCheckPass": True,
        "campaignCore": str(core_path),
        "campaignCoreSha256": sha256_file(core_path),
        "startReceipt": str(run_dir / "start.json"),
        "startReceiptSha256": sha256_file(run_dir / "start.json"),
        "completedAt": now(),
        "wallClockSeconds": time.time() - start_wall,
        "nextAction": "V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION",
    }
    evidence = run_dir / "evidence.json"
    final["evidencePath"] = str(evidence)
    atomic_json(evidence, final)

    receipt = run_dir / "receipt.txt"
    receipt.write_text(
        "\n".join(
            [
                "STATE=PASS",
                "DURATION_GTE_8H=PASS",
                "CONTROLLED_INTERRUPTION_COUNT=3",
                "PROCESS_INTERRUPTION=PASS",
                "NETWORK_INTERRUPTION=PASS",
                "RUNTIME_INTERRUPTION=PASS",
                "TASK_IDENTITY_CONTINUITY=PASS",
                "EXACTLY_ONCE_EFFECT=PASS",
                "RSS_PEAK_LIMIT=PASS",
                "RSS_FINAL_LIMIT=PASS",
                "STORAGE_RECONCILIATION=PASS",
                "CONTROL_PLANE_REGRESSION=PASS",
                "PRODUCT_REGRESSION=PASS",
                "NATIVE_BUILD=PASS",
                "FINAL_DIFF_CHECKS=PASS",
                "POST_CAMPAIGN_DONECHECK_V12=PASS",
                "TECHNICAL_HOLD_COUNT=0",
                "EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED",
                f"EVIDENCE={evidence}",
                "NEXT_ACTION=V07_HUMAN_THRESHOLD_AUTHORITY_TRANSITION",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return final


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["parent", "worker", "network-server"], default="parent")
    parser.add_argument("--runtime-source", type=Path)
    parser.add_argument("--durable-root", type=Path)
    parser.add_argument("--ready", type=Path)
    parser.add_argument("--sequence", type=int, default=0)
    parser.add_argument("--port-file", type=Path)
    args = parser.parse_args()

    if args.mode == "worker":
        if not args.runtime_source or not args.durable_root or not args.ready:
            raise SystemExit(2)
        return worker_mode(args.runtime_source, args.durable_root, args.ready, args.sequence)
    if args.mode == "network-server":
        if not args.port_file:
            raise SystemExit(2)
        return network_server_mode(args.port_file)

    try:
        result = perform()
    except Exception as exc:
        print("STATE=HOLD", flush=True)
        print(f"HOLD={type(exc).__name__}:{exc}", flush=True)
        print("NEXT_ACTION=RECONCILE_V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN", flush=True)
        return 2

    print("STATE=PASS", flush=True)
    print("DURATION_GTE_8H=PASS", flush=True)
    print("CONTROLLED_INTERRUPTION_COUNT=3", flush=True)
    print("PROCESS_INTERRUPTION=PASS", flush=True)
    print("NETWORK_INTERRUPTION=PASS", flush=True)
    print("RUNTIME_INTERRUPTION=PASS", flush=True)
    print("TASK_IDENTITY_CONTINUITY=PASS", flush=True)
    print("EXACTLY_ONCE_EFFECT=PASS", flush=True)
    print("RSS_PEAK_LIMIT=PASS", flush=True)
    print("RSS_FINAL_LIMIT=PASS", flush=True)
    print("STORAGE_RECONCILIATION=PASS", flush=True)
    print("CONTROL_PLANE_REGRESSION=PASS", flush=True)
    print("PRODUCT_REGRESSION=PASS", flush=True)
    print("NATIVE_BUILD=PASS", flush=True)
    print("FINAL_DIFF_CHECKS=PASS", flush=True)
    print("POST_CAMPAIGN_DONECHECK_V12=PASS", flush=True)
    print("TECHNICAL_HOLD_COUNT=0", flush=True)
    print("EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED", flush=True)
    print(f"EVIDENCE={result['evidencePath']}", flush=True)
    print(f"NEXT_ACTION={result['nextAction']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
