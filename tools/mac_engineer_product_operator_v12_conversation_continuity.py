#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"

SESSION = GOV / "SESSION_STATE_V1.json"
ROADMAP = GOV / "PRODUCT_OPERATOR_ROADMAP_V1.json"
CONTRACT = GOV / "PRODUCT_OPERATOR_V12_ACCEPTANCE_CONTRACT_V1.json"

EXPECTED_OBJECTIVE = "ENGURU_PRODUCT_OPERATOR_V12"
EXPECTED_GATE = "G5_CONVERSATION_CONTINUITY"
EXPECTED_NEXT = "PRODUCT_OPERATOR_V12_CONVERSATION_CONTINUITY"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_projection() -> dict[str, Any]:
    session = load(SESSION)
    roadmap = load(ROADMAP)
    contract = load(CONTRACT)

    po = session.get("productOperatorV12") or {}

    gates = {
        str(g.get("id")): g.get("state")
        for g in contract.get("gates", [])
    }

    return {
        "objective": session.get("currentObjective"),
        "state": po.get("state"),
        "activeGate": po.get("activeGate"),
        "nextAction": po.get("nextAction"),
        "roadmapActiveGate":
            (roadmap.get("objective") or {}).get("activeGate"),
        "roadmapNextAction":
            (roadmap.get("objective") or {}).get("nextAction"),
        "gates": gates,
        "sourceContinuity": po.get("sourceContinuity") or {},
        "g1": po.get("g1ObjectiveActivation") or {},
        "g2": po.get("g2RegisteredActionBinding") or {},
        "g3": po.get("g3HumanThreshold") or {},
        "g4": po.get("g4MaterialExecution") or {},
    }


def evaluate() -> dict[str, Any]:
    p = canonical_projection()

    checks = {
        "objectiveIdentity":
            p["objective"] == EXPECTED_OBJECTIVE,

        "productOperatorActive":
            p["state"] == "ACTIVE",

        "activeGateG5":
            p["activeGate"] == EXPECTED_GATE
            and p["roadmapActiveGate"] == EXPECTED_GATE,

        "nextActionAligned":
            p["nextAction"] == EXPECTED_NEXT
            and p["roadmapNextAction"] == EXPECTED_NEXT,

        "g1Pass":
            p["gates"].get("OBJECTIVE_ACTIVATION") == "PASS"
            and p["g1"].get("state") == "PASS",

        "g2Pass":
            p["gates"].get("REGISTERED_ACTION_BINDING") == "PASS"
            and p["g2"].get("state") == "PASS",

        "g3Pass":
            p["gates"].get("HUMAN_THRESHOLD") == "PASS"
            and p["g3"].get("state") == "PASS",

        "g4Pass":
            p["gates"].get("MATERIAL_EXECUTION") == "PASS"
            and p["g4"].get("state") == "PASS",

        "g5Pending":
            p["gates"].get("CONVERSATION_CONTINUITY") == "PENDING",

        "sourceContinuityPreserved":
            p["sourceContinuity"].get("provenancePreserved") is True
            and p["sourceContinuity"].get("worktree") == "CLEAN",
    }

    failed = [k for k, v in checks.items() if not v]

    if failed:
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "PRODUCT_OPERATOR_V12_CONVERSATION_CONTINUITY_CANONICAL_MISMATCH",
            "FAILED_CHECKS": failed,
            "CHECKS": checks,
            "PROJECTION": p,
        }

    return {
        "STATE": "PASS",
        "CLAIM":
            "PRODUCT_OPERATOR_V12_CONVERSATION_CONTINUITY_CANONICAL_BINDING_VERIFIED",
        "CHECKS": checks,
        "PROJECTION": p,
        "AUTHORITY":
            "CONVERSATION_STATE_NON_AUTHORITATIVE_CANONICAL_STATE_PRESERVED",
        "NEXT_ACTION":
            "PRODUCT_OPERATOR_V12_G5_ACCEPTANCE_PROMOTION",
    }


if __name__ == "__main__":
    print(json.dumps(
        evaluate(),
        ensure_ascii=False,
        indent=2,
    ))
