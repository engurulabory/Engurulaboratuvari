#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WORKLIST = ROOT / "governance/mac-engineer/V11_100_POINT_CANONICAL_WORKLIST_V1.md"
ACCEPTANCE = ROOT / "governance/mac-engineer/V11_100_POINT_CANONICAL_WORKLIST_ACCEPTANCE_V1.json"
ROADMAP = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
SESSION = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"

AESTHETIC = ROOT / "governance/mac-engineer/V13_AESTHETIC_MOTOR_CANONICAL_NECESSARY_DIFFERENCE_CONTRACT_V1.md"
JEV = ROOT / "governance/mac-engineer/V11_JEV_CANONICAL_NECESSARY_DIFFERENCE_CONTRACT_V1_2.md"

EXPECTED_IDS = [f"{i:03d}" for i in range(1, 101)]


def main() -> int:
    issues: list[str] = []

    for path, name in (
        (WORKLIST, "WORKLIST"),
        (ACCEPTANCE, "ACCEPTANCE"),
        (ROADMAP, "ROADMAP"),
        (SESSION, "SESSION"),
        (AESTHETIC, "AESTHETIC"),
        (JEV, "JEV"),
    ):
        if not path.is_file():
            issues.append(f"MISSING:{name}")

    if issues:
        print(json.dumps({"state": "HOLD", "issues": issues}, indent=2))
        return 2

    text = WORKLIST.read_text(encoding="utf-8")

    ids = re.findall(
        r"^- \[ \] \*\*(\d{3})\.",
        text,
        flags=re.MULTILINE,
    )

    if ids != EXPECTED_IDS:
        issues.append("WORKLIST_POINT_IDS_NOT_EXACT_001_100")

    required_text = (
        "PREPARED / QUEUED — NOT YET ACTIVE",
        "UNSUPPORTED_CANONICAL_CLAIM = 0",
        "CRITICAL_FALSE_PASS = 0",
        "COMPLETED = 0 / 100",
        "REMAINING = 100 / 100",
        "V1_1_GROUNDED_ENGINEERING_RELIABILITY_VERIFIED_LOCKED",
    )

    for marker in required_text:
        if marker not in text:
            issues.append(f"WORKLIST_MARKER_MISSING:{marker}")

    acceptance = json.loads(
        ACCEPTANCE.read_text(encoding="utf-8")
    )

    if acceptance.get("state") != "PREPARED_QUEUED":
        issues.append("ACCEPTANCE_STATE_NOT_PREPARED_QUEUED")

    if acceptance.get("executionActive") is not False:
        issues.append("V11_EXECUTION_MUST_REMAIN_INACTIVE")

    if acceptance.get("totalPoints") != 100:
        issues.append("TOTAL_POINTS_NOT_100")

    if acceptance.get("completedPoints") != 0:
        issues.append("PREPARED_WORKLIST_MUST_START_AT_0")

    if acceptance.get("remainingPoints") != 100:
        issues.append("REMAINING_POINTS_NOT_100")

    if acceptance.get("totalGates") != 12:
        issues.append("TOTAL_GATES_NOT_12")

    roadmap = json.loads(
        ROADMAP.read_text(encoding="utf-8")
    )

    if roadmap.get("finalTarget", {}).get("version") != "v1.3":
        issues.append("FINAL_TARGET_NOT_V13")

    versions = {
        item.get("version"): item
        for item in roadmap.get("versions", [])
    }

    v11 = versions.get("v1.1", {})
    worklist = v11.get("canonicalWorklist", {})

    if worklist.get("path") != (
        "governance/mac-engineer/"
        "V11_100_POINT_CANONICAL_WORKLIST_V1.md"
    ):
        issues.append("ROADMAP_V11_WORKLIST_REFERENCE_MISSING")

    if worklist.get("state") != "PREPARED_QUEUED":
        issues.append("ROADMAP_V11_WORKLIST_STATE_MISMATCH")

    if worklist.get("completedPoints") != 0:
        issues.append("ROADMAP_V11_COMPLETED_POINTS_NOT_ZERO")

    session = json.loads(
        SESSION.read_text(encoding="utf-8")
    )

    v08 = session.get("currentV08", {})

    active_gate = v08.get("closureContract", {}).get("activeGate")
    gate11 = v08.get("gate11", {})
    gate12 = v08.get("gate12", {})

    if active_gate == 11:
        if gate11.get("executionStarted") is not False:
            issues.append("CURRENT_GATE11_EXECUTION_CHANGED")
    elif active_gate == 12:
        if (
            gate11.get("state") != "VERIFIED_LOCKED"
            or gate11.get("executionStarted") is not True
            or gate12.get("state") != "ACTIVE"
            or gate12.get("executionStarted") is not False
        ):
            issues.append("GATE11_CLOSURE_GATE12_TRANSITION_INVALID")
    else:
        issues.append("CURRENT_V08_ACTIVE_GATE_NOT_11_OR_12")

    prepared = session.get(
        "preparedFutureWorklists",
        {},
    ).get("v1.1", {})

    if prepared.get("state") != "PREPARED_QUEUED":
        issues.append("SESSION_V11_PREPARATION_REFERENCE_MISSING")

    if prepared.get("executionActive") is not False:
        issues.append("SESSION_V11_EXECUTION_MUST_REMAIN_FALSE")

    state = "PASS" if not issues else "HOLD"

    payload = {
        "state": state,
        "claim": (
            "V11_100_POINT_CANONICAL_WORKLIST_PREPARED"
            if state == "PASS"
            else "V11_100_POINT_CANONICAL_WORKLIST_HOLD"
        ),
        "pointCount": len(ids),
        "completedPoints": acceptance.get("completedPoints"),
        "remainingPoints": acceptance.get("remainingPoints"),
        "executionActive": acceptance.get("executionActive"),
        "issues": issues,
    }

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if state == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
