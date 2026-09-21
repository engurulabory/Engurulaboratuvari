#!/usr/bin/env python3
"""Canonical session start/handoff snapshot for ENGÜRÜ Mac Engineer™."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
PRODUCT_SOURCE = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME = HOME / "Enguru" / "Runtime" / "MacEngineer"
APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
STATE_FILE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
WORKLIST = ROOT / "WORKLIST.md"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git_state(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False, "path": str(path)}
    result: dict[str, Any] = {"available": True, "path": str(path)}
    commands = {
        "head": ["git", "rev-parse", "HEAD"],
        "branch": ["git", "branch", "--show-current"],
        "status": ["git", "status", "--porcelain"],
        "origin": ["git", "remote", "get-url", "origin"],
        "origin_main": ["git", "rev-parse", "origin/main"],
    }
    for key, cmd in commands.items():
        rc, out, err = run(cmd, cwd=path)
        result[key] = out if rc == 0 else None
        if rc != 0:
            result[f"{key}_error"] = err
    result["clean"] = not bool(result.get("status"))
    result["exact_origin_main"] = bool(
        result.get("head")
        and result.get("origin_main")
        and result["head"] == result["origin_main"]
    )
    return result


def load_state() -> dict[str, Any]:
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def normalize_objective(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def active_objective() -> str:
    text = WORKLIST.read_text(encoding="utf-8")
    match = re.search(
        r"\*\*Current single objective:\*\*\s+\*\*(.+?)\*\*\.",
        text,
    )
    return match.group(1) if match else "UNRESOLVED"


def authorized_product_working_branch(
    state: dict[str, Any],
    product: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    objective = str(state.get("currentObjective", ""))
    prepared = state.get("observedV06AlignmentPreparation", {})
    if objective not in {
        "PRODUCT_SOURCE_V0_6_ALIGNMENT_PUBLICATION",
        "PRODUCT_PR_EXACT_HEAD_CI_MERGE",
    }:
        return False, {}

    expected_branch = str(prepared.get("branch", ""))
    expected_head = str(prepared.get("commit", ""))
    expected_base = str(prepared.get("baseMain", ""))

    authorized = bool(
        expected_branch
        and expected_head
        and expected_base
        and product.get("branch") == expected_branch
        and product.get("head") == expected_head
        and product.get("origin_main") == expected_base
        and product.get("clean") is True
    )
    return authorized, {
        "expected_branch": expected_branch,
        "expected_head": expected_head,
        "expected_base_main": expected_base,
        "authorized": authorized,
    }


def process_state() -> list[dict[str, str]]:
    rc, out, _ = run(["ps", "-axo", "pid=,command="])
    if rc != 0:
        return []
    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        low = line.lower()
        if "engurumacengineer" in low or "/enguru/runtime/macengineer/" in low:
            pid, _, command = line.strip().partition(" ")
            rows.append({"pid": pid, "command": command})
    return rows


def snapshot(mode: str) -> dict[str, Any]:
    state = load_state()
    control = git_state(ROOT)
    product = git_state(PRODUCT_SOURCE)
    objective = active_objective()

    issues: list[str] = []
    if control.get("branch") != "main":
        issues.append("CONTROL_PLANE_MAIN_REQUIRED")
    if control.get("clean") is not True:
        issues.append("CONTROL_PLANE_CLEAN_REQUIRED")
    if control.get("exact_origin_main") is not True:
        issues.append("CONTROL_PLANE_EXACT_MAIN_REQUIRED")

    working_branch_authorized = False
    working_branch_policy: dict[str, Any] = {}
    if not product.get("available"):
        issues.append("PRODUCT_SOURCE_REQUIRED")
    else:
        (
            working_branch_authorized,
            working_branch_policy,
        ) = authorized_product_working_branch(state, product)

        if product.get("clean") is not True:
            issues.append("PRODUCT_SOURCE_CLEAN_REQUIRED")

        if not working_branch_authorized:
            if product.get("branch") != "main":
                issues.append("PRODUCT_SOURCE_MAIN_REQUIRED")
            if product.get("exact_origin_main") is not True:
                issues.append("PRODUCT_SOURCE_EXACT_MAIN_REQUIRED")

        expected = "engurulabory/enguru-mac-engineer"
        origin = product.get("origin") or ""
        if expected not in origin:
            issues.append("PRODUCT_SOURCE_ORIGIN_MISMATCH")

    declared = state.get("currentObjective", "")
    # WORKLIST is the higher authority; mismatch must be visible, not silently repaired.
    if declared:
        declared_norm = normalize_objective(declared)
        objective_norm = normalize_objective(objective)
        if declared_norm not in objective_norm and objective_norm not in declared_norm:
            issues.append("SESSION_STATE_WORKLIST_OBJECTIVE_RECONCILIATION_REQUIRED")

    payload = {
        "schema": "enguru.mac-engineer.session-snapshot/v1",
        "mode": mode,
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "continuity_contract": state.get("continuityContract"),
        "locked_method": state.get("lockedMethod"),
        "authority_order": state.get("authorityOrder"),
        "active_objective": objective,
        "declared_session_objective": declared,
        "canonical_next_line": state.get("canonicalNextLine", []),
        "closed_truth": state.get("closedTruth", {}),
        "canonical_surfaces": state.get("canonicalSurfaces", {}),
        "control_plane": control,
        "product_source": product,
        "product_working_branch_policy": {
            "authorized": working_branch_authorized,
            **working_branch_policy,
        },
        "runtime": {
            "root_exists": RUNTIME.exists(),
            "app_exists": APP.exists(),
            "processes": process_state(),
        },
        "session_rule": (
            "Continue only the canonical active objective. "
            "Treat GitHub WORKLIST/governance and exact-main as authority. "
            "A non-main product branch is accepted only when SESSION_STATE "
            "explicitly authorizes its exact branch/head/base for the active objective; "
            "chat memory is advisory."
        ),
        "new_session_instruction": (
            "Read governance/mac-engineer/SESSION_CONTINUITY_CONTRACT_V1.md, "
            "governance/mac-engineer/SESSION_STATE_V1.json and WORKLIST.md. "
            "Confirm this snapshot, then continue only the active objective "
            "using STATE → CLAIM → EVIDENCE → JUDGMENT/NEXT ACTION."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["start", "handoff"])
    args = parser.parse_args()

    payload = snapshot(args.mode)
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    name = (
        "session-start-latest.json"
        if args.mode == "start"
        else "session-handoff-latest.json"
    )
    path = EVIDENCE_ROOT / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    output = dict(payload)
    output["evidence"] = str(path)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
