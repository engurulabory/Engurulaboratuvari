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
        "    return a + b\n",
        encoding="utf-8",
    )

    tests = FIXTURE / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "__init__.py").write_text("", encoding="utf-8")
    (tests / "test_calculator.py").write_text(
        "import unittest\n\n"
        "from calculator import add\n\n\n"
        "class CalculatorTests(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        self.assertEqual(add(2, 3), 5)\n\n\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )

    (FIXTURE / "CURRENT_STATE.md").write_text(
        "# CURRENT STATE\n\n"
        "## VERIFIED EXECUTABLE BASELINE\n\n"
        "This disposable field fixture intentionally lacks the current "
        "ENGÜRÜ field revalidation block.\n",
        encoding="utf-8",
    )

    (FIXTURE / "README.md").write_text(
        "# ENGÜRÜ Mac Engineering™ v0.6 Field Fixture\n\n"
        "Disposable commissioning repository for the already-verified "
        "controlled canonical-state repair path. Tests begin PASS. "
        "CURRENT_STATE.md begins stale by design. The commissioned "
        "engineer must run the real test contract, reconcile canonical "
        "CURRENT_STATE truth with the smallest reversible change, inspect "
        "the diff, run regression, preserve Evidence, and leave the same "
        "task resumable for restart verification.\n",
        encoding="utf-8",
    )

    MARKER.write_text(
        json.dumps(
            {
                "schema": "enguru.mac-engineering.field-fixture/v2",
                "task_id": TASK_ID,
                "checkpoint_id": CHECKPOINT_ID,
                "created_at": now(),
                "scope": "V0_6_CONTROLLED_CANONICAL_STATE_REPAIR",
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
        ["git", "commit", "-m", "test: v0.6 controlled repair field baseline"],
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
            for generated in (
                FIXTURE / "__pycache__",
                FIXTURE / "tests" / "__pycache__",
                FIXTURE / ".pytest_cache",
            ):
                if generated.is_dir():
                    shutil.rmtree(generated)
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

        baseline = run(
            [
                "python3",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            cwd=FIXTURE,
        )
        if not baseline["pass"]:
            raise FieldTaskError("BASELINE_TEST_PASS_REQUIRED")

        current_state = (FIXTURE / "CURRENT_STATE.md").read_text(
            encoding="utf-8"
        )
        if "ENGURU_CURRENT_REVALIDATION_START" in current_state:
            raise FieldTaskError("STALE_CURRENT_STATE_REQUIRED")

        prompt = f"""ENGÜRÜ Mac Engineering™ v0.6 FIELD COMMISSIONING

Use durable task ID: {TASK_ID}
Use checkpoint ID: {CHECKPOINT_ID}

Work only inside this repository:
{FIXTURE}

Objective:
1. Inspect the repository and verify its canonical git identity.
2. Run the repository's real local test contract.
3. Confirm tests PASS before repair.
4. Reconcile CURRENT_STATE.md canonical state truth using the existing controlled safe-repair path.
5. Apply only the smallest reversible difference.
6. Inspect git status and the exact diff.
7. Re-run regression and require PASS.
8. Produce Evidence for baseline tests, changed file, diff, regression and final verdict.
9. Preserve Human Threshold and stay inside this fixture. No network, no push, no commit, no other repository.
10. Persist task identity {TASK_ID} and checkpoint {CHECKPOINT_ID} after repair/test Evidence is attached.
11. Leave the task resumable for post-restart verification; do not finalize v0.6 from this first pass.

Use STATE → CLAIM → EVIDENCE → JUDGMENT/NEXT ACTION.
Return task ID, checkpoint ID, changed file, regression result, Evidence reference and PASS / HOLD / BLOCKED.
"""
        resume_prompt = f"""ENGÜRÜ Mac Engineering™ v0.6 CONTINUITY VERIFICATION

Resume the same durable task:
task_id: {TASK_ID}
checkpoint_id: {CHECKPOINT_ID}

Repository:
{FIXTURE}

Requirements:
1. Re-read repository/runtime/task state after restart.
2. Resume the exact same task identity and checkpoint.
3. Re-read git status and CURRENT_STATE.md diff; do not rely on stale conversation state.
4. Re-run the repository's real local test contract.
5. Verify the controlled canonical-state repair remains correct.
6. Reconcile any drift before proceeding.
7. Produce post-restart Evidence with the same task/checkpoint identity.
8. Only after those checks, mark this field task Verified Finish / PASS.

Return exact task/checkpoint identity, changed file and post-restart regression result.
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
            "baseline_tests": {
                "state": "PASS",
                "command": baseline["cmd"],
                "returncode": baseline["returncode"],
                "stdout": baseline["stdout"],
                "stderr": baseline["stderr"],
            },
            "repair_contract": {
                "target": "CURRENT_STATE.md",
                "stale_by_design": True,
                "expected_path": "controlled_canonical_state_reconciliation",
            },
            "prompt_file": str(PROMPT_FILE),
            "resume_prompt_file": str(RESUME_PROMPT_FILE),
            "truth_boundary": (
                "This prepares a real disposable Git repository with passing tests "
                "and one intentionally stale canonical-state document. It does not "
                "claim that ENGÜRÜ Mac Engineering has executed the repair yet."
            ),
            "next_action": (
                "Refresh the installed app/runtime repo inventory, then submit the "
                "exact prompt from package6-real-task-prompt.txt."
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
