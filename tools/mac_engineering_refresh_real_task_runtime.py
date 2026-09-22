#!/usr/bin/env python3
"""Refresh ENGÜRÜ Mac Engineering™ runtime after real-task fixture preparation."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import unicodedata
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from typing import Any


HOME = Path.home()
APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
RUNTIME_PY = HOME / "Enguru" / "Runtime" / "MacEngineer" / "runtime" / "app.py"
FIXTURE = HOME / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture"
PREP_EVIDENCE = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
    / "package6-real-task-preflight.json"
)
OUTPUT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
    / "package6-real-task-runtime-refresh.json"
)
STATUS_URL = "http://127.0.0.1:8765/api/status"


class RefreshError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], timeout: int = 30) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def norm(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def process_rows() -> list[dict[str, str]]:
    r = run(["ps", "-axo", "pid=,command="])
    if not r["pass"]:
        return []
    rows: list[dict[str, str]] = []
    app_path = norm(str(APP))
    runtime_path = norm(str(RUNTIME_PY))
    for line in r["stdout"].splitlines():
        stripped = line.strip()
        pid, _, command = stripped.partition(" ")
        n = norm(command)
        if app_path in n or runtime_path in n:
            rows.append({"pid": pid.strip(), "command": command.strip()})
    return rows


def stop_processes() -> list[dict[str, str]]:
    rows = process_rows()
    for row in rows:
        try:
            os.kill(int(row["pid"]), signal.SIGTERM)
        except (ProcessLookupError, ValueError):
            pass
    deadline = time.time() + 8
    while time.time() < deadline:
        if not process_rows():
            return rows
        time.sleep(0.25)
    for row in process_rows():
        try:
            os.kill(int(row["pid"]), signal.SIGKILL)
        except (ProcessLookupError, ValueError):
            pass
    time.sleep(0.5)
    if process_rows():
        raise RefreshError("RUNTIME_PROCESS_STOP_FAILED")
    return rows


def status() -> dict[str, Any]:
    try:
        with urlopen(STATUS_URL, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {"pass": True, "payload": data}
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"pass": False, "error": type(exc).__name__}


def wait_status(timeout_seconds: float = 20.0) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = status()
        if last.get("pass") and last.get("payload", {}).get("state") == "RUNNING":
            return last
        time.sleep(0.5)
    return last


def fixture_from_rows(
    rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    expected = FIXTURE.resolve()

    for row in rows:
        raw_path = row.get("path")

        if not raw_path:
            continue

        try:
            observed = Path(
                str(raw_path)
            ).expanduser().resolve()
        except OSError:
            continue

        if observed == expected:
            return row

    return None


def runtime_repository_inventory() -> dict[str, Any]:
    runtime_dir = RUNTIME_PY.parent

    code = """
import json
import sys
from pathlib import Path

runtime_dir = Path(sys.argv[1])
enguru_root = Path(sys.argv[2])

sys.path.insert(0, str(runtime_dir))

import repo_manager as rm

rows = rm.scan_enguru(enguru_root)

print(
    json.dumps(
        rows,
        ensure_ascii=False,
    )
)
"""

    result = run(
        [
            "python3",
            "-c",
            code,
            str(runtime_dir),
            str(HOME / "Enguru"),
        ],
        timeout=30,
    )

    if not result["pass"]:
        raise RefreshError(
            "RUNTIME_REPOSITORY_SCAN_FAILED:"
            + str(result["stderr"])
        )

    try:
        rows = json.loads(
            str(result["stdout"])
        )
    except json.JSONDecodeError as exc:
        raise RefreshError(
            "RUNTIME_REPOSITORY_SCAN_INVALID_JSON"
        ) from exc

    if not isinstance(rows, list):
        raise RefreshError(
            "RUNTIME_REPOSITORY_SCAN_LIST_REQUIRED"
        )

    fixture = fixture_from_rows(rows)

    return {
        "repo_count": len(rows),
        "fixture_discovered": fixture is not None,
        "fixture": fixture,
    }


def main() -> int:
    try:
        if not PREP_EVIDENCE.is_file():
            raise RefreshError("REAL_TASK_PREFLIGHT_EVIDENCE_REQUIRED")
        prep = json.loads(PREP_EVIDENCE.read_text(encoding="utf-8"))
        if prep.get("state") != "PASS":
            raise RefreshError("REAL_TASK_PREFLIGHT_PASS_REQUIRED")
        if Path(prep.get("fixture", "")).resolve() != FIXTURE.resolve():
            raise RefreshError("REAL_TASK_FIXTURE_IDENTITY_MISMATCH")
        if not (FIXTURE / ".git").is_dir():
            raise RefreshError("REAL_TASK_FIXTURE_GIT_REQUIRED")

        before = status()
        before_count = (
            before.get("payload", {}).get("repo_count")
            if before.get("pass")
            else None
        )

        stopped = stop_processes()
        opened = run(["open", str(APP)])
        if not opened["pass"]:
            raise RefreshError(f"APP_OPEN_FAILED:{opened['stderr']}")

        after = wait_status()
        if not after.get("pass"):
            raise RefreshError("RUNTIME_STATUS_NOT_READY_AFTER_REFRESH")

        after_payload = after.get("payload", {})
        after_count = after_payload.get("repo_count")
        if not isinstance(after_count, int):
            raise RefreshError("RUNTIME_REPO_COUNT_REQUIRED")

        runtime_inventory = (
            runtime_repository_inventory()
        )

        if not runtime_inventory.get(
            "fixture_discovered"
        ):
            raise RefreshError(
                "REAL_TASK_FIXTURE_NOT_DISCOVERED:"
                f"before={before_count}:"
                f"after={after_count}"
            )

        runtime_repo_count = (
            runtime_inventory.get("repo_count")
        )

        if runtime_repo_count != after_count:
            raise RefreshError(
                "RUNTIME_REPO_COUNT_MISMATCH:"
                f"status={after_count}:"
                f"scan={runtime_repo_count}"
            )

        inventory_refreshed = True

        rows = process_rows()
        app_present = any(norm(str(APP)) in norm(row["command"]) for row in rows)
        runtime_present = any(norm(str(RUNTIME_PY)) in norm(row["command"]) for row in rows)
        if not app_present:
            raise RefreshError("INSTALLED_APP_PROCESS_REQUIRED")
        if not runtime_present:
            raise RefreshError("RUNTIME_PROCESS_REQUIRED")

        payload = {
            "schema": "enguru.mac-engineering.real-task-runtime-refresh/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "task_id": prep.get("task_id"),
            "checkpoint_id": prep.get("checkpoint_id"),
            "fixture": str(FIXTURE),
            "before_repo_count": before_count,
            "after_repo_count": after_count,
            "inventory_refreshed": inventory_refreshed,
            "fixture_discovered": True,
            "runtime_repository_inventory": runtime_inventory,
            "stopped_processes": stopped,
            "processes_after": rows,
            "runtime_status": after_payload,
            "truth_boundary": (
                "This proves the installed app/runtime restarted and refreshed its "
                "repository inventory after fixture preparation. It does not claim "
                "the field repair task has executed yet."
            ),
            "next_action": "Submit the exact package6-real-task-prompt.txt in the installed app.",
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (RefreshError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        payload = {
            "schema": "enguru.mac-engineering.real-task-runtime-refresh/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. No field fixture source was changed.",
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
