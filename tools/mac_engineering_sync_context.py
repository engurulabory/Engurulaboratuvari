#!/usr/bin/env python3
"""Sync canonical ENGÜRÜ Mac Engineering™ context into Mac runtime state."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
ROADMAP = ROOT / "governance" / "mac-engineer" / "PRODUCT_ROADMAP_V1.json"
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
WORKLIST = ROOT / "WORKLIST.md"
RUNTIME_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state"
OUTPUT = RUNTIME_STATE / "canonical-context.json"
EVIDENCE = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "canonical-context-sync.json"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git_truth(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False}
    out: dict[str, Any] = {"available": True}
    for key, cmd in {
        "head": ["git", "rev-parse", "HEAD"],
        "branch": ["git", "branch", "--show-current"],
        "origin_main": ["git", "rev-parse", "origin/main"],
        "status": ["git", "status", "--porcelain"],
    }.items():
        rc, stdout, stderr = run(cmd, path)
        out[key] = stdout if rc == 0 else None
        if rc != 0:
            out[f"{key}_error"] = stderr
    out["clean"] = out.get("status") == ""
    out["exact_origin_main"] = bool(
        out.get("head")
        and out.get("origin_main")
        and out["head"] == out["origin_main"]
    )
    return out


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def active_objective() -> str:
    text = WORKLIST.read_text(encoding="utf-8")
    matches = re.findall(
        r"\*\*Current single objective:\*\*\s+\*\*(.+?)\*\*\.",
        text,
    )
    if not matches:
        return "UNRESOLVED"
    # Mac Engineering section is canonical for this product; use the final match.
    return matches[-1]


def main() -> int:
    roadmap = load_json(ROADMAP)
    session = load_json(SESSION_STATE)
    control = git_truth(ROOT)

    issues: list[str] = []
    if control.get("branch") != "main":
        issues.append("CONTROL_PLANE_MAIN_REQUIRED")
    if control.get("clean") is not True:
        issues.append("CONTROL_PLANE_CLEAN_REQUIRED")
    if control.get("exact_origin_main") is not True:
        issues.append("CONTROL_PLANE_EXACT_MAIN_REQUIRED")

    if session.get("product") != "ENGÜRÜ Mac Engineering™":
        issues.append("CANONICAL_PRODUCT_NAME_MISMATCH")
    if roadmap.get("product", {}).get("canonicalName") != "ENGÜRÜ Mac Engineering™":
        issues.append("ROADMAP_PRODUCT_NAME_MISMATCH")

    objective = active_objective()
    if "Runtime/App Provenance Closure" not in objective:
        issues.append("WORKLIST_ACTIVE_OBJECTIVE_RECONCILIATION_REQUIRED")

    payload = {
        "schema": "enguru.mac-engineering.canonical-context/v1",
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "product": roadmap.get("product"),
        "current": roadmap.get("current"),
        "finalTarget": roadmap.get("finalTarget"),
        "versions": roadmap.get("versions"),
        "method": roadmap.get("method"),
        "activeObjective": objective,
        "sessionStateObjective": session.get("currentObjective"),
        "canonicalNextLine": session.get("canonicalNextLine"),
        "controlPlane": control,
        "sourceFiles": {
            "roadmap": str(ROADMAP.relative_to(ROOT)),
            "sessionState": str(SESSION_STATE.relative_to(ROOT)),
            "worklist": str(WORKLIST.relative_to(ROOT)),
        },
        "truthBoundary": (
            "This is a local runtime context snapshot derived from canonical GitHub-controlled files. "
            "It does not override GitHub WORKLIST/governance and cannot manufacture PASS."
        ),
    }

    RUNTIME_STATE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(text, encoding="utf-8")
    EVIDENCE.write_text(text, encoding="utf-8")

    print(
        json.dumps(
            {
                "state": payload["state"],
                "issues": issues,
                "product": payload["product"],
                "current": payload["current"],
                "finalTarget": payload["finalTarget"],
                "activeObjective": objective,
                "runtimeContext": str(OUTPUT),
                "evidence": str(EVIDENCE),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
