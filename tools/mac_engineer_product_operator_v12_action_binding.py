#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"

BINDING_DOC = GOV / "PRODUCT_OPERATOR_V12_ACTION_BINDING_V1.json"
ACTION_REGISTRY = GOV / "OPERATOR_ACTION_REGISTRY_V1.json"
CAPABILITY_REGISTRY = GOV / "CAPABILITY_REGISTRY_V1.json"

EXPECTED_OBJECTIVE = "ENGURU_PRODUCT_OPERATOR_V12"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate() -> dict[str, Any]:
    binding = load(BINDING_DOC)
    actions = load(ACTION_REGISTRY).get("actions") or {}
    capabilities_doc = load(CAPABILITY_REGISTRY)

    raw_capabilities = (
        capabilities_doc.get("capabilities")
        or capabilities_doc.get("registry")
        or capabilities_doc
    )

    if isinstance(raw_capabilities, list):
        capabilities = {
            str(item.get("CAPABILITY_ID") or item.get("capabilityId") or item.get("id")): item
            for item in raw_capabilities
            if isinstance(item, dict)
            and (item.get("CAPABILITY_ID") or item.get("capabilityId") or item.get("id"))
        }
    elif isinstance(raw_capabilities, dict):
        capabilities = raw_capabilities
    else:
        capabilities = {}

    checks: dict[str, bool] = {
        "objectiveIdentity": binding.get("objectiveId") == EXPECTED_OBJECTIVE,
        "deterministicSelection": (binding.get("policy") or {}).get("selection")
        == "DETERMINISTIC_EXACT_CLASS",
        "unboundHolds": (binding.get("policy") or {}).get("unbound") == "HOLD",
        "arbitraryActionBlocked": (binding.get("policy") or {}).get("arbitraryActionAllowed")
        is False,
        "authorityExpansionBlocked": (binding.get("policy") or {}).get("authorityExpansionAllowed")
        is False,
        "reusesExistingActions": (binding.get("policy") or {}).get("reuseExistingMacEngineerActions")
        is True,
    }

    resolved = {}
    for key, spec in (binding.get("bindings") or {}).items():
        cap = spec.get("capabilityId")
        action = spec.get("action")
        action_spec = actions.get(action)

        cap_exists = isinstance(capabilities, dict) and cap in capabilities
        action_exists = isinstance(action_spec, dict)
        handler_exists = bool(action_spec.get("handler")) if action_exists else False
        fail_closed = action_spec.get("failClosed") is True if action_exists else False
        remote_push_safe = action_spec.get("remotePush") is False if action_exists else False

        checks[f"{key}.capabilityExists"] = cap_exists
        checks[f"{key}.actionExists"] = action_exists
        checks[f"{key}.handlerExists"] = handler_exists
        checks[f"{key}.failClosed"] = fail_closed
        checks[f"{key}.remotePushFalse"] = remote_push_safe

        resolved[key] = {
            "capabilityId": cap,
            "action": action,
            "handler": action_spec.get("handler") if action_exists else None,
            "authority": action_spec.get("authority") if action_exists else None,
            "humanThresholdRequired": action_spec.get("humanThresholdRequired")
            if action_exists
            else None,
            "networkRequired": action_spec.get("networkRequired")
            if action_exists
            else None,
            "mutationScope": action_spec.get("mutationScope")
            if action_exists
            else None,
        }

    failed = [name for name, passed in checks.items() if not passed]

    if failed:
        return {
            "STATE": "HOLD",
            "HOLD_REASON": "PRODUCT_OPERATOR_V12_ACTION_BINDING_MISMATCH",
            "FAILED_CHECKS": failed,
            "CHECKS": checks,
            "RESOLVED": resolved,
        }

    return {
        "STATE": "PASS",
        "CLAIM": "PRODUCT_OPERATOR_V12_REGISTERED_ACTION_BINDING_VERIFIED",
        "OBJECTIVE_ID": EXPECTED_OBJECTIVE,
        "BINDING_COUNT": len(resolved),
        "CHECKS": checks,
        "RESOLVED": resolved,
        "NEXT_ACTION": "PRODUCT_OPERATOR_V12_G2_ACCEPTANCE_PROMOTION",
    }


def resolve(work_class: str) -> dict[str, Any]:
    result = evaluate()
    if result.get("STATE") != "PASS":
        return {
            "state": "HOLD",
            "reason": result.get("HOLD_REASON"),
        }

    resolved = result["RESOLVED"].get(work_class)
    if not resolved:
        return {
            "state": "HOLD",
            "reason": "UNBOUND_PRODUCT_OPERATOR_WORK_CLASS",
            "workClass": work_class,
        }

    return {
        "state": "PASS",
        "workClass": work_class,
        **resolved,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
