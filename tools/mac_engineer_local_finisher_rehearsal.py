#!/usr/bin/env python3
"""Pre-A11 local finisher mechanics rehearsal for ENGÜRÜ Mac Engineering™.

This is a bounded local rehearsal only. It cannot manufacture V07-A09,
V07-A11, Human Threshold, or v0.7 version-lock authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

HOME = Path.home()
DEFAULT_EVIDENCE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "local-finisher-rehearsal"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(cmd: list[str], *, cwd: Path, timeout: int = 120) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def require_pass(result: dict[str, Any], label: str) -> None:
    if result["code"] != 0:
        raise RuntimeError(
            f"{label}_FAILED:"
            + (str(result.get("stdout") or "") + "\n" + str(result.get("stderr") or ""))[-2500:]
        )


def calculator_source(operator: str) -> str:
    return (
        "def add(a: int, b: int) -> int:\n"
        "    # ENGURU_RECOVERY_FAULT_START\n"
        f"    return a {operator} b\n"
        "    # ENGURU_RECOVERY_FAULT_END\n"
    )


def perform(evidence_root: Path = DEFAULT_EVIDENCE_ROOT) -> dict[str, Any]:
    run_dir = evidence_root / stamp()
    fixture = run_dir / "fixture"
    fixture.mkdir(parents=True, exist_ok=False)

    calc = fixture / "calculator.py"
    tests = fixture / "tests"
    tests.mkdir()
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
    calc.write_text(calculator_source("+"), encoding="utf-8")
    (fixture / "TASK.md").write_text(
        "# LOCAL FINISHER REHEARSAL\n\n"
        "Bounded recovery mechanics fixture. Local rehearsal authority only.\n",
        encoding="utf-8",
    )

    for cmd in (
        ["git", "init", "-b", "main"],
        ["git", "config", "user.name", "ENGURU Local Rehearsal"],
        ["git", "config", "user.email", "local-rehearsal@invalid.local"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "test: local finisher rehearsal baseline"],
    ):
        require_pass(run(cmd, cwd=fixture), "FIXTURE_GIT")

    baseline = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=fixture,
    )
    require_pass(baseline, "BASELINE_REGRESSION")
    baseline_hash = sha256(calc)

    calc.write_text(calculator_source("-"), encoding="utf-8")
    fault = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=fixture,
    )
    if fault["code"] == 0:
        raise RuntimeError("CONTROLLED_FAULT_MUST_FAIL")

    fault_status = run(["git", "status", "--porcelain"], cwd=fixture)
    require_pass(fault_status, "FAULT_STATUS")
    if "calculator.py" not in fault_status["stdout"]:
        raise RuntimeError("CONTROLLED_FAULT_SCOPE_REQUIRED")

    calc.write_text(calculator_source("+"), encoding="utf-8")
    regression = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=fixture,
    )
    require_pass(regression, "RECOVERY_REGRESSION")

    first_repair_hash = sha256(calc)
    calc.write_text(calculator_source("+"), encoding="utf-8")
    second_repair_hash = sha256(calc)
    idempotent = first_repair_hash == second_repair_hash == baseline_hash
    if not idempotent:
        raise RuntimeError("RECOVERY_IDEMPOTENCY_REQUIRED")

    verify = run(
        ["python3", "-B", "-c", "from calculator import add; print(add(2, 3))"],
        cwd=fixture,
    )
    require_pass(verify, "USER_VERIFY")
    if verify["stdout"] != "5":
        raise RuntimeError("USER_VERIFY_EXPECTED_5")

    diff_check = run(["git", "diff", "--check"], cwd=fixture)
    require_pass(diff_check, "DIFF_CHECK")
    final_status = run(["git", "status", "--porcelain"], cwd=fixture)
    require_pass(final_status, "FINAL_STATUS")
    if final_status["stdout"]:
        raise RuntimeError(f"FINAL_FIXTURE_CLEAN_REQUIRED:{final_status['stdout']}")

    payload = {
        "schema": "enguru.mac-engineer.local-finisher-rehearsal/v1",
        "observedAt": now(),
        "state": "PASS",
        "scope": "PRE_A11_LOCAL_FINISHER_REHEARSAL",
        "authority": "LOCAL_REHEARSAL_ONLY_NO_A09_NO_A11_NO_VERSION_LOCK",
        "fixture": str(fixture),
        "stages": {
            "UNDERSTAND": "PASS",
            "DISCOVER": "PASS",
            "ARCHITECT": "PASS_SMALLEST_MARKER_SCOPED_RECOVERY",
            "EXECUTE": "PASS_CONTROLLED_FAULT_INJECTED",
            "TEST": "PASS_FAILURE_OBSERVED",
            "RECOVER": "PASS_MINIMAL_REPAIR",
            "USER_VERIFY": "PASS",
            "FINISH": "PASS_REGRESSION_DIFF_CLEAN_EVIDENCE",
        },
        "baseline": {
            "tests": "PASS",
            "calculatorSha256": baseline_hash,
        },
        "controlledFault": {
            "observed": True,
            "testReturnCode": fault["code"],
            "scope": "calculator.py",
        },
        "recovery": {
            "regression": "PASS",
            "idempotent": True,
            "restoredBaselineHash": first_repair_hash == baseline_hash,
            "diffCheck": "PASS",
            "finalWorktree": "CLEAN",
            "userVerify": "add(2,3)=5",
        },
        "a09Boundary": "HOLD_EXTERNAL_CONFIRMATION_REQUIRED",
        "a11Boundary": "FORMAL_A11_REQUIRES_GITHUB_ENGINEERING_CANDIDATE_EXACT_MAIN_ACCEPTANCE",
        "nextAction": "V07_A09_EXTERNAL_CONFIRMATION_OR_A11_WHEN_ELIGIBLE",
    }
    evidence = run_dir / "evidence.json"
    payload["evidencePath"] = str(evidence)
    evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "receipt.txt").write_text(
        "\n".join(
            [
                "STATE=PASS",
                "SCOPE=PRE_A11_LOCAL_FINISHER_REHEARSAL",
                "FAULT_OBSERVED=PASS",
                "RECOVERY=PASS",
                "REGRESSION=PASS",
                "IDEMPOTENCY=PASS",
                "FINAL_WORKTREE=CLEAN",
                f"EVIDENCE={evidence}",
                "NEXT_ACTION=V07_A09_EXTERNAL_CONFIRMATION_OR_A11_WHEN_ELIGIBLE",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    try:
        payload = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_LOCAL_FINISHER_REHEARSAL")
        return 2

    print("STATE=PASS")
    print(f"SCOPE={payload['scope']}")
    print("FAULT_OBSERVED=PASS")
    print("RECOVERY=PASS")
    print("REGRESSION=PASS")
    print("IDEMPOTENCY=PASS")
    print("FINAL_WORKTREE=CLEAN")
    print(f"EVIDENCE={payload['evidencePath']}")
    print(f"NEXT_ACTION={payload['nextAction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
