#!/usr/bin/env python3
"""Verify exact task/checkpoint resume after a real Mac Engineering restart."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Any


HOME = Path.home()
FIXTURE = HOME / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
REAL_TASK = EVIDENCE_ROOT / "package6-real-task-evidence.json"
RESTART = EVIDENCE_ROOT / "package6-continuity-restart.json"
RESULT = FIXTURE / "ENGURU_FIELD_RESULT.json"
OUTPUT = EVIDENCE_ROOT / "package6-continuity-evidence.json"

TASK_ID = "ENGURU-V06-FIELD-001"
CHECKPOINT_ID = "v06-field-cp-001"


class ContinuityError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ContinuityError(f"JSON_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContinuityError(f"JSON_INVALID:{path}") from exc


def run(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout[-12000:],
        "stderr": p.stderr[-12000:],
    }


def pass_value(value: Any) -> bool:
    if value is True:
        return True
    return str(value).strip().upper() in {
        "PASS",
        "PASSED",
        "SUCCESS",
        "OK",
    }


def main() -> int:
    try:
        real_task = load_json(REAL_TASK)
        restart = load_json(RESTART)
        result = load_json(RESULT)

        if real_task.get("state") != "PASS":
            raise ContinuityError("REAL_TASK_PASS_REQUIRED")
        if restart.get("state") != "PASS":
            raise ContinuityError("RESTART_PASS_REQUIRED")
        if restart.get("restart_observed") is not True:
            raise ContinuityError("REAL_RESTART_REQUIRED")

        if result.get("task_id") != TASK_ID:
            raise ContinuityError("TASK_ID_BEFORE_MISMATCH")
        if result.get("checkpoint_id") != CHECKPOINT_ID:
            raise ContinuityError("CHECKPOINT_ID_BEFORE_MISMATCH")
        if result.get("resumed_after_restart") is not True:
            raise ContinuityError("RESUMED_AFTER_RESTART_REQUIRED")
        if result.get("resumed_task_id") != TASK_ID:
            raise ContinuityError("TASK_IDENTITY_DRIFT")
        if result.get("resumed_checkpoint_id") != CHECKPOINT_ID:
            raise ContinuityError("CHECKPOINT_IDENTITY_DRIFT")
        if not pass_value(result.get("post_restart_test_state")):
            raise ContinuityError("POST_RESTART_TEST_PASS_REQUIRED")

        tests = run(
            ["python3", "-m", "unittest", "discover", "-v"],
            cwd=FIXTURE,
        )
        if not tests["pass"]:
            raise ContinuityError("POST_RESTART_TEST_REVERIFY_FAILED")

        records = real_task.get("durable_records", [])
        if not isinstance(records, list) or not records:
            raise ContinuityError("DURABLE_RECORD_REQUIRED")
        record_path = Path(str(records[0].get("path", "")))
        if not record_path.is_file():
            raise ContinuityError("DURABLE_RECORD_LOST")

        before_mtime = int(
            restart.get("record_before", {}).get("mtime_ns") or 0
        )
        after_mtime = record_path.stat().st_mtime_ns
        if after_mtime < before_mtime:
            raise ContinuityError("DURABLE_RECORD_TIME_REGRESSION")

        payload = {
            "schema": "enguru.mac-engineering.continuity-evidence/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "task_id_before": TASK_ID,
            "task_id_after": result.get("resumed_task_id"),
            "checkpoint_id": CHECKPOINT_ID,
            "restart_observed": True,
            "durable_record": str(record_path),
            "record_mtime_before_restart": before_mtime,
            "record_mtime_after_resume": after_mtime,
            "post_restart_tests": tests,
            "result_file": str(RESULT),
            "truth_boundary": (
                "PASS proves the same task/checkpoint identity survived a real "
                "runtime restart, was explicitly resumed, and the engineering "
                "result was re-read and re-tested after restart."
            ),
            "next_action": "Reconcile recovery field proof and build the final local commissioning bundle.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (ContinuityError, OSError) as exc:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "enguru.mac-engineering.continuity-evidence/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. Restart evidence without exact task resume is insufficient.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
