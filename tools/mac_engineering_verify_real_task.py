#!/usr/bin/env python3
"""Verify the first real Mac Engineering commissioning task and durable checkpoint."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


HOME = Path.home()
FIXTURE = HOME / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture"
RUNTIME_ROOT = HOME / "Enguru" / "Runtime" / "MacEngineer"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
PREFLIGHT = EVIDENCE_ROOT / "package6-real-task-preflight.json"
RESULT = FIXTURE / "ENGURU_FIELD_RESULT.json"
OUTPUT = EVIDENCE_ROOT / "package6-real-task-evidence.json"

TASK_ID = "ENGURU-V06-FIELD-001"
CHECKPOINT_ID = "v06-field-cp-001"


class VerifyError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise VerifyError(f"JSON_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VerifyError(f"JSON_INVALID:{path}") from exc


def json_contains(value: Any, needle: str) -> bool:
    if isinstance(value, dict):
        return any(json_contains(v, needle) for v in value.values())
    if isinstance(value, list):
        return any(json_contains(v, needle) for v in value)
    return str(value) == needle


def find_durable_records() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not RUNTIME_ROOT.exists():
        return out
    for path in RUNTIME_ROOT.rglob("*.json"):
        try:
            if path.stat().st_size > 2_000_000:
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            json_contains(payload, TASK_ID)
            and json_contains(payload, CHECKPOINT_ID)
        ):
            out.append(
                {
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "mtime_ns": path.stat().st_mtime_ns,
                }
            )
    return out


def test_state_pass(value: Any) -> bool:
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
        preflight = load_json(PREFLIGHT)
        if preflight.get("state") != "PASS":
            raise VerifyError("REAL_TASK_PREFLIGHT_PASS_REQUIRED")
        if preflight.get("task_id") != TASK_ID:
            raise VerifyError("REAL_TASK_ID_PREFLIGHT_MISMATCH")
        if preflight.get("checkpoint_id") != CHECKPOINT_ID:
            raise VerifyError("CHECKPOINT_PREFLIGHT_MISMATCH")

        result = load_json(RESULT)
        if result.get("task_id") != TASK_ID:
            raise VerifyError("REAL_TASK_ID_RESULT_MISMATCH")
        if result.get("checkpoint_id") != CHECKPOINT_ID:
            raise VerifyError("CHECKPOINT_RESULT_MISMATCH")
        if result.get("baseline_head") != preflight.get("baseline_head"):
            raise VerifyError("REAL_TASK_BASELINE_HEAD_MISMATCH")
        if not test_state_pass(result.get("test_state")):
            raise VerifyError("REAL_TASK_RESULT_TEST_PASS_REQUIRED")

        tests = run(
            ["python3", "-m", "unittest", "discover", "-v"],
            cwd=FIXTURE,
        )
        if not tests["pass"]:
            raise VerifyError("REAL_TASK_TEST_REVERIFY_FAILED")

        status = run(["git", "status", "--porcelain"], cwd=FIXTURE)
        diff = run(["git", "diff", "--", "calculator.py"], cwd=FIXTURE)
        if not status["pass"] or not diff["pass"]:
            raise VerifyError("REAL_TASK_GIT_EVIDENCE_REQUIRED")
        if "calculator.py" not in str(status["stdout"]):
            raise VerifyError("REAL_TASK_ENGINEERING_CHANGE_REQUIRED")
        if not str(diff["stdout"]).strip():
            raise VerifyError("REAL_TASK_DIFF_REQUIRED")

        records = find_durable_records()
        if not records:
            raise VerifyError("DURABLE_TASK_CHECKPOINT_RECORD_REQUIRED")

        payload = {
            "schema": "enguru.mac-engineering.real-task-evidence/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "task_id": TASK_ID,
            "checkpoint_id": CHECKPOINT_ID,
            "fixture": str(FIXTURE),
            "baseline_head": preflight.get("baseline_head"),
            "result_file": str(RESULT),
            "result": result,
            "tests": tests,
            "git_status": status["stdout"],
            "git_diff": diff["stdout"],
            "artifact_refs": [
                str(FIXTURE / "calculator.py"),
                str(RESULT),
            ],
            "test_refs": [
                "python3 -m unittest discover -v",
            ],
            "durable_records": records,
            "truth_boundary": (
                "PASS proves the bounded real Git task was changed and re-tested, "
                "and the exact durable task/checkpoint identity exists in Mac "
                "Engineering runtime JSON state. Restart/resume is a separate gate."
            ),
            "next_action": (
                "Perform a real Mac Engineering app/runtime restart while preserving "
                "this task/checkpoint, then resume the exact task."
            ),
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (VerifyError, OSError) as exc:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "enguru.mac-engineering.real-task-evidence/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. No PASS without task, diff, tests and durable checkpoint state.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
