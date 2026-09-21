#!/usr/bin/env python3
"""Perform the real runtime/app restart for v0.6 continuity verification."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import tools.mac_engineer_exact_sha_rebuild_install as install


HOME = Path.home()
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
REAL_TASK = EVIDENCE_ROOT / "package6-real-task-evidence.json"
RESUME_PROMPT = EVIDENCE_ROOT / "package6-real-task-resume-prompt.txt"
OUTPUT = EVIDENCE_ROOT / "package6-continuity-restart.json"

TASK_ID = "ENGURU-V06-FIELD-001"
CHECKPOINT_ID = "v06-field-cp-001"


class RestartError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RestartError(f"EVIDENCE_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RestartError(f"EVIDENCE_INVALID:{path}") from exc


def runtime_pids(rows: list[dict[str, str]]) -> set[str]:
    return {
        row["pid"]
        for row in rows
        if install.command_contains_path(
            row.get("command", ""),
            install.RUNTIME_PY,
        )
    }


def app_pids(rows: list[dict[str, str]]) -> set[str]:
    return {
        row["pid"]
        for row in rows
        if install.command_contains_path(
            row.get("command", ""),
            install.INSTALLED_APP,
        )
    }


def main() -> int:
    try:
        task = load_json(REAL_TASK)
        if task.get("state") != "PASS":
            raise RestartError("REAL_TASK_PASS_REQUIRED")
        if task.get("task_id") != TASK_ID:
            raise RestartError("TASK_ID_MISMATCH")
        if task.get("checkpoint_id") != CHECKPOINT_ID:
            raise RestartError("CHECKPOINT_ID_MISMATCH")

        records = task.get("durable_records", [])
        if not isinstance(records, list) or not records:
            raise RestartError("DURABLE_RECORD_REQUIRED")

        record_path = Path(str(records[0].get("path", "")))
        if not record_path.is_file():
            raise RestartError("DURABLE_RECORD_FILE_REQUIRED")

        record_before = {
            "path": str(record_path),
            "sha256": sha256_file(record_path),
            "mtime_ns": record_path.stat().st_mtime_ns,
        }

        before = install.process_rows()
        before_runtime = runtime_pids(before)
        if not before_runtime:
            raise RestartError("RUNNING_RUNTIME_REQUIRED_BEFORE_RESTART")

        stopped = install.stop_existing_processes()

        launch = install.run(
            ["open", str(install.INSTALLED_APP)],
            timeout=20,
        )
        if not launch["pass"]:
            raise RestartError(
                f"APP_RELAUNCH_FAILED:{launch['stderr']}"
            )

        live = install.live_status()
        if not live["pass"]:
            raise RestartError("LIVE_STATUS_REQUIRED_AFTER_RESTART")

        process_check = install.wait_for_processes()
        if not process_check["pass"]:
            raise RestartError("APP_RUNTIME_PROCESS_READY_REQUIRED")

        after = process_check["rows"]
        after_runtime = runtime_pids(after)
        if not after_runtime:
            raise RestartError("RUNTIME_REQUIRED_AFTER_RESTART")
        if before_runtime & after_runtime:
            raise RestartError("RUNTIME_PID_RESTART_REQUIRED")

        if not record_path.is_file():
            raise RestartError("DURABLE_RECORD_LOST_AFTER_RESTART")

        record_after = {
            "path": str(record_path),
            "sha256": sha256_file(record_path),
            "mtime_ns": record_path.stat().st_mtime_ns,
        }

        payload = {
            "schema": "enguru.mac-engineering.continuity-restart/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "task_id": TASK_ID,
            "checkpoint_id": CHECKPOINT_ID,
            "record_before": record_before,
            "record_after_restart": record_after,
            "before_processes": before,
            "stopped_processes": stopped,
            "after_processes": after,
            "runtime_pids_before": sorted(before_runtime),
            "runtime_pids_after": sorted(after_runtime),
            "app_pids_before": sorted(app_pids(before)),
            "app_pids_after": sorted(app_pids(after)),
            "restart_observed": True,
            "live_status": live,
            "resume_prompt": str(RESUME_PROMPT),
            "truth_boundary": (
                "PASS proves a real runtime process restart occurred and the exact "
                "durable task record survived it. Task resume/continued execution "
                "must still be proven through the installed Mac Engineering path."
            ),
            "next_action": (
                "Submit the exact resume prompt to the installed app, then run the "
                "continuity verifier."
            ),
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (RestartError, OSError, subprocess.TimeoutExpired) as exc:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "enguru.mac-engineering.continuity-restart/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. Restart alone cannot manufacture resume PASS.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
