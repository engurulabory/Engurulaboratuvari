#!/usr/bin/env python3
"""Fail-closed Product Operator v1.2 identity and G1 foundation verifier."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"
PRODUCT = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"
OBJECTIVE = "ENGURU_PRODUCT_OPERATOR_V12"
ACTION = "PRODUCT_OPERATOR_V12_OBJECTIVE_ACTIVATION"
CALLABLE = "run_product_operator_v12_objective_activation"


def load(name: str) -> dict[str, Any]:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def git_value(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=PRODUCT, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def evaluate() -> dict[str, Any]:
    try:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        product = load("PRODUCT_OPERATOR_ROADMAP_V1.json")
        contract = load("PRODUCT_OPERATOR_V12_ACCEPTANCE_CONTRACT_V1.json")
        binding_doc = load("PRODUCT_OPERATOR_V12_EXECUTION_BINDING_V1.json")
        action_registry = load("OPERATOR_ACTION_REGISTRY_V1.json")
    except (OSError, ValueError, TypeError) as exc:
        return {"STATE": "HOLD", "HOLD_REASON": f"FOUNDATION_READ_FAILED:{type(exc).__name__}"}

    bindings = binding_doc.get("bindings") or []
    binding = bindings[0] if len(bindings) == 1 and isinstance(bindings[0], dict) else {}
    action = (action_registry.get("actions") or {}).get(ACTION) or {}
    gates = contract.get("gates") or []
    mac_v12 = next(
        (item for item in roadmap.get("versions", []) if item.get("version") == "v1.2"),
        {},
    )
    actual_head = git_value("rev-parse", "HEAD")
    product_clean = git_value("status", "--porcelain") == ""
    roadmap_head = str(
        product.get("sourceContinuity", {}).get("currentVerifiedHead") or ""
    )
    session_head = str(
        session.get("productOperatorV12", {})
        .get("sourceContinuity", {})
        .get("currentVerifiedHead")
        or ""
    )

    checks = {
        "productIdentity": product.get("product", {}).get("id") == "ENGURU_PRODUCT_OPERATOR",
        "distinctNamespace": product.get("stateNamespace") == "productOperatorV12",
        "objectiveActive": session.get("currentObjective") == OBJECTIVE,
        "objectiveStateBound": session.get("productOperatorV12", {}).get("state") == "ACTIVE",
        "macEngineerV12Preserved": mac_v12.get("name") == "Local Mac Astra Verified Final",
        "package08Preserved": session.get("postV08Objective", {}).get("state") == "VERIFIED_CLOSED",
        "fieldVerifiedCountPreserved": session.get("postV08Objective", {}).get("fieldVerifiedCount") == 19,
        "v08Preserved": session.get("currentV08", {}).get("state") == "VERIFIED_LOCKED",
        "gate12Preserved": session.get("currentV08", {}).get("gate12", {}).get("state") == "VERIFIED_LOCKED",
        "g1ThroughG7PassG8Pending": (
            len(gates) == 8
            and all(g.get("state") == "PASS" for g in gates[:7])
            and gates[7].get("id") == "HUMAN_FIELD_ACCEPTANCE"
            and gates[7].get("state") == "PENDING"
        ),
        "bindingRegistered": binding.get("action") == ACTION and binding.get("operatorCallable") == CALLABLE,
        "bindingFailClosed": binding.get("failClosed") is True,
        "actionRegistered": action.get("handler") == ACTION,
        "actionFailClosed": action.get("failClosed") is True,
        "noNetwork": action.get("networkRequired") is False,
        "noRemotePush": action.get("remotePush") is False,
        "canonicalSourceHead": bool(roadmap_head) and roadmap_head == session_head,
        "historicalSourcePreserved": "0ca33cc7b70fee915d02de72946bbd4bb0e40065" in product.get("sourceContinuity", {}).get("historicalVerifiedHeads", []),
        "actualSourceHead": actual_head == roadmap_head,
        "actualSourceClean": product_clean,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        return {
            "STATE": "HOLD",
            "HOLD_REASON": "FOUNDATION_CONTRACT_MISMATCH",
            "FAILED_CHECKS": failed,
            "CHECKS": checks,
        }
    return {
        "STATE": "PASS",
        "CLAIM": "PRODUCT_OPERATOR_V12_CANONICAL_FOUNDATION_READY",
        "OBJECTIVE_ID": OBJECTIVE,
        "ACTION": ACTION,
        "OPERATOR_CALLABLE": CALLABLE,
        "G1_STATE": "PASS",
        "CANONICAL_PRODUCT_SOURCE_HEAD": roadmap_head,
        "CHECKS": checks,
        "NEXT_ACTION": ACTION,
    }


def main() -> int:
    result = evaluate()
    for key in ("STATE", "CLAIM", "OBJECTIVE_ID", "ACTION", "OPERATOR_CALLABLE", "G1_STATE", "CANONICAL_PRODUCT_SOURCE_HEAD", "HOLD_REASON", "NEXT_ACTION"):
        if result.get(key) is not None:
            print(f"{key}={result[key]}")
    if result.get("FAILED_CHECKS"):
        print("FAILED_CHECKS=" + ",".join(result["FAILED_CHECKS"]))
    return 0 if result.get("STATE") == "PASS" else 20


if __name__ == "__main__":
    raise SystemExit(main())
