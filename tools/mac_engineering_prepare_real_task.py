#!/usr/bin/env python3
"""Prepare the bounded real-repository commissioning task for v0.6 field closeout."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


HOME = Path.home()
FIXTURE = HOME / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture"
MARKER = FIXTURE / ".enguru-v06-field-fixture.json"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
OUTPUT = EVIDENCE_ROOT / "package6-real-task-preflight.json"
PROMPT_FILE = EVIDENCE_ROOT / "package6-real-task-prompt.txt"
RESUME_PROMPT_FILE = EVIDENCE_ROOT / "package6-real-task-resume-prompt.txt"

TASK_ID = "ENGURU-V06-FIELD-001"
CHECKPOINT_ID = "v06-field-cp-001"


class FieldTaskError(RuntimeError):
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


def write_fixture() -> None:
    FIXTURE.mkdir(parents=True, exist_ok=False)
    (FIXTURE / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    # Commissioning fixture: one intentional bounded defect.\n"
        "    return a - b\n",
        encoding="utf-8",
    )
    (FIXTURE / "test_calculator.py").write_text(
        "import unittest\n\n"
        "from calculator import add\n\n\n"
        "class CalculatorTests(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        self.assertEqual(add(2, 3), 5)\n\n\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )
    (FIXTURE / "README.md").write_text(
        "# ENGÜRÜ Mac Engineering™ v0.6 Field Fixture\n\n"
        "Disposable commissioning repository. One intentional defect exists in "
        "calculator.py. The commissioned engineer must discover it by running "
        "the test, make the smallest correction, re-run the test, preserve a "
        "diff, and attach Evidence to the durable task.\n",
        encoding="utf-8",
    )
    MARKER.write_text(
        json.dumps(
            {
                "schema": "enguru.mac-engineering.field-fixture/v1",
                "task_id": TASK_ID,
                "checkpoint_id": CHECKPOINT_ID,
                "created_at": now(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    steps = [
        ["git", "init", "-b", "main"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "test: v0.6 Mac Engineering commissioning baseline"],
    ]
    for cmd in steps:
        result = run(cmd, cwd=FIXTURE)
        if not result["pass"]:
            raise FieldTaskError(
                f"FIXTURE_GIT_INIT_FAILED:{' '.join(cmd)}:{result['stderr']}"
            )


def fixture_truth() -> dict[str, Any]:
    if not FIXTURE.is_dir():
        return {"available": False}
    head = run(["git", "rev-parse", "HEAD"], cwd=FIXTURE)
    status = run(["git", "status", "--porcelain"], cwd=FIXTURE)
    return {
        "available": True,
        "head": head["stdout"].strip() if head["pass"] else "",
        "clean": status["pass"] and not status["stdout"].strip(),
        "status": status["stdout"],
        "marker": MARKER.is_file(),
    }


def main() -> int:
    try:
        if FIXTURE.exists():
            if not MARKER.is_file():
                raise FieldTaskError("EXISTING_FIXTURE_PATH_NOT_OWNED")
            truth = fixture_truth()
            if not truth.get("clean"):
                raise FieldTaskError(
                    "EXISTING_FIELD_FIXTURE_HAS_UNRECONCILED_CHANGES"
                )
            shutil.rmtree(FIXTURE)

        write_fixture()
        truth = fixture_truth()
        if not truth.get("clean"):
            raise FieldTaskError("FIXTURE_BASELINE_NOT_CLEAN")

        failing = run(
            ["python3", "-m", "unittest", "discover", "-v"],
            cwd=FIXTURE,
        )
        if failing["pass"]:
            raise FieldTaskError("INTENTIONAL_BASELINE_FAILURE_REQUIRED")

        result_path = FIXTURE / "ENGURU_FIELD_RESULT.json"
        prompt = f"""ENGÜRÜ Mac Engineering™ v0.6 FIELD COMMISSIONING

Use durable task ID: {TASK_ID}
Use checkpoint ID: {CHECKPOINT_ID}

Work only inside this repository:
{FIXTURE}

Objective:
1. Inspect the repository.
2. Run: python3 -m unittest discover -v
3. Observe the real failing test.
4. Diagnose the root cause.
5. Make the smallest reversible engineering correction.
6. Re-run the same test command until PASS.
7. Show the exact git diff.
8. Write {result_path} containing:
   - task_id
   - checkpoint_id
   - baseline_head
   - changed_files
   - test_command
   - test_state
   - diff_summary
   - evidence_refs
9. Preserve Human Threshold and stay inside this fixture. No network, no push, no commit, no other repository.
10. Persist the task and create checkpoint {CHECKPOINT_ID} after the fix/test Evidence is attached.
11. Leave the task resumable for a post-restart verification pass. Do not close the durable task as final yet.

Return the task ID, checkpoint ID, changed file, test result and Evidence path.
"""
        resume_prompt = f"""ENGÜRÜ Mac Engineering™ v0.6 CONTINUITY VERIFICATION

Resume the existing durable task:
task_id: {TASK_ID}
checkpoint_id: {CHECKPOINT_ID}

Re-read repository/runtime/task state after restart:
{FIXTURE}

Requirements:
1. Resume the exact same task identity and checkpoint.
2. Re-read git status and diff; do not rely on stale conversation state.
3. Re-run: python3 -m unittest discover -v
4. Verify the bounded correction still passes.
5. Reconcile any drift before proceeding.
6. Update {result_path} with:
   - resumed_after_restart: true
   - resumed_task_id
   - resumed_checkpoint_id
   - post_restart_test_state
   - post_restart_evidence_refs
7. Only after those checks, mark the task Verified Finish / PASS with Evidence.

Return exact task/checkpoint identity and post-restart test result.
"""
        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        PROMPT_FILE.write_text(prompt, encoding="utf-8")
        RESUME_PROMPT_FILE.write_text(resume_prompt, encoding="utf-8")

        payload = {
            "schema": "enguru.mac-engineering.real-task-preflight/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "task_id": TASK_ID,
            "checkpoint_id": CHECKPOINT_ID,
            "fixture": str(FIXTURE),
            "baseline_head": truth.get("head"),
            "baseline_clean": truth.get("clean"),
            "intentional_failure": {
                "observed": True,
                "command": failing["cmd"],
                "returncode": failing["returncode"],
                "stdout": failing["stdout"],
                "stderr": failing["stderr"],
            },
            "prompt_file": str(PROMPT_FILE),
            "resume_prompt_file": str(RESUME_PROMPT_FILE),
            "truth_boundary": (
                "This prepares a real disposable Git repository with one observed "
                "failing test. It does not claim that ENGÜRÜ Mac Engineering has "
                "executed or fixed the task yet."
            ),
            "next_action": (
                "Open the installed ENGÜRÜ Mac Engineer app and submit the exact "
                "prompt from package6-real-task-prompt.txt."
            ),
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (FieldTaskError, OSError) as exc:
        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "enguru.mac-engineering.real-task-preflight/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. No product/runtime source was modified.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
