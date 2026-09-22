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
CURRENT_STATUS = ROOT / "governance" / "mac-engineer" / "CURRENT_STATUS.md"
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
        "merge_base_origin_main": [
            "git",
            "merge-base",
            "HEAD",
            "origin/main",
        ],
        "ahead_origin_main": [
            "git",
            "rev-list",
            "--count",
            "origin/main..HEAD",
        ],
        "diff_names_origin_main": [
            "git",
            "diff",
            "--name-only",
            "origin/main...HEAD",
        ],
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


def porcelain_paths(status: str) -> list[str]:
    paths: list[str] = []
    for line in status.splitlines():
        if not line:
            continue

        # subprocess output is globally stripped before it reaches this parser.
        # That can remove the leading space from the first porcelain line:
        # " M runtime/app.py" -> "M runtime/app.py".
        # Preserve exact path identity for both normalized shapes.
        if len(line) >= 3 and line[2] == " ":
            path = line[3:]
        elif len(line) >= 2 and line[1] == " ":
            path = line[2:]
        else:
            continue

        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return sorted(paths)


def authorized_product_working_branch(
    state: dict[str, Any],
    product: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    objective = str(state.get("currentObjective", ""))

    if objective in {
        "CONTINUITY_PATCH_REPEATABILITY",
        "PRODUCT_PATCH_GITHUB_ENGINEERING",
        "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
    }:
        patch = (
            state.get("observedContextDurabilityPatch", {})
            if objective == "CHECKPOINT_RESTART_RESUME_FIELD_PROOF"
            else state.get("observedContinuityPatch", {})
        )
        expected_branch = str(patch.get("branch", ""))
        expected_head = str(patch.get("head", ""))
        expected_base = str(patch.get("baseMain", ""))
        expected_dirty = sorted(patch.get("expectedDirtyPaths", []))
        observed_dirty = porcelain_paths(str(product.get("status", "")))
        committed_diff = sorted(
            path
            for path in str(
                product.get("diff_names_origin_main", "")
            ).splitlines()
            if path
        )

        dirty_patch_authorized = bool(
            expected_branch
            and expected_head
            and expected_base
            and expected_dirty
            and product.get("branch") == expected_branch
            and product.get("head") == expected_head
            and product.get("origin_main") == expected_base
            and product.get("exact_origin_main") is True
            and observed_dirty == expected_dirty
        )

        committed_patch_authorized = bool(
            objective in {
                "PRODUCT_PATCH_GITHUB_ENGINEERING",
                "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            }
            and expected_branch
            and expected_head
            and expected_base
            and expected_dirty
            and product.get("branch") == expected_branch
            and product.get("origin_main") == expected_base
            and product.get("clean") is True
            and product.get("head") != expected_head
            and product.get("merge_base_origin_main")
            == expected_base
            and str(product.get("ahead_origin_main"))
            == "1"
            and committed_diff == expected_dirty
        )

        authorized = (
            dirty_patch_authorized
            or committed_patch_authorized
        )
        mode = (
            "IN_FLIGHT_PATCH"
            if dirty_patch_authorized
            else (
                "COMMITTED_PATCH_AWAITING_PR"
                if committed_patch_authorized
                else "IN_FLIGHT_PATCH"
            )
        )
        return authorized, {
            "mode": mode,
            "expected_branch": expected_branch,
            "expected_head": expected_head,
            "expected_base_main": expected_base,
            "expected_dirty_paths": expected_dirty,
            "observed_dirty_paths": observed_dirty,
            "committed_diff_paths": committed_diff,
            "ahead_origin_main": product.get(
                "ahead_origin_main"
            ),
            "merge_base_origin_main": product.get(
                "merge_base_origin_main"
            ),
            "authorized": authorized,
        }

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
        "mode": "CLEAN_WORKING_BRANCH",
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

        if product.get("clean") is not True and not working_branch_authorized:
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
        "current_status": {
            "path": str(CURRENT_STATUS.relative_to(ROOT)),
            "exists": CURRENT_STATUS.is_file(),
        },
        "locked_method": state.get("lockedMethod"),
        "current_status_update_rule": state.get("currentStatusUpdateRule"),
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
            "authorizes its exact publication state: either the bounded dirty patch "
            "or a clean one-commit-ahead branch with the exact expected diff; "
            "chat memory is advisory."
        ),
        "new_session_instruction": (
            "Read governance/mac-engineer/SESSION_CONTINUITY_CONTRACT_V1.md, "
            "governance/mac-engineer/ACTIVE_WORKING_PATH.md, "
            "governance/mac-engineer/CURRENT_STATUS.md, "
            "governance/mac-engineer/SESSION_STATE_V1.json, "
            "governance/mac-engineer/PRODUCT_ROADMAP_V1.json and WORKLIST.md. "
            "Confirm this snapshot, continue only the active objective, "
            "and reconcile CURRENT_STATUS after every material PASS/HOLD/BLOCKED result "
            "before the next action, using STATE → CLAIM → EVIDENCE → JUDGMENT/NEXT ACTION."
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
