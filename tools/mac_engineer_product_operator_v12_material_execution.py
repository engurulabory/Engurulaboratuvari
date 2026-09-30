#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any

try:
    from mac_engineer_product_operator_v12_human_threshold import evaluate_work_class
    import mac_engineer_safe_execution_orchestrator as safe_orchestrator
except ModuleNotFoundError:
    from tools.mac_engineer_product_operator_v12_human_threshold import evaluate_work_class
    from tools import mac_engineer_safe_execution_orchestrator as safe_orchestrator


def execute_material_work_class(
    work_class: str,
    *,
    human_decision: str | None = None,
) -> dict[str, Any]:
    threshold = evaluate_work_class(
        work_class,
        human_decision=human_decision,
    )

    threshold_state = threshold.get("state")

    if threshold_state == "NEEDS_HUMAN":
        return {
            **threshold,
            "materialExecutionPerformed": False,
        }

    if threshold_state == "HOLD":
        return {
            **threshold,
            "materialExecutionPerformed": False,
        }

    if threshold_state not in {
        "CONTINUE",
        "READY_AFTER_HUMAN_THRESHOLD",
    }:
        return {
            "state": "HOLD",
            "reason": "HUMAN_THRESHOLD_STATE_NOT_EXECUTABLE",
            "workClass": work_class,
            "thresholdState": threshold_state,
            "materialExecutionPerformed": False,
        }

    capability_id = threshold.get("capabilityId")
    action = threshold.get("action")
    authority = threshold.get("authority")

    if not capability_id or not action or not authority:
        return {
            "state": "HOLD",
            "reason": "MATERIAL_EXECUTION_BINDING_INCOMPLETE",
            "workClass": work_class,
            "materialExecutionPerformed": False,
        }

    result = safe_orchestrator.execute_proven_registered_action(
        capability_id
    )

    if result.get("STATE") != "PASS":
        return {
            "state": "HOLD",
            "reason":
                result.get("HOLD_REASON")
                or "REGISTERED_ACTION_EXECUTION_HOLD",
            "workClass": work_class,
            "capabilityId": capability_id,
            "action": action,
            "authority": authority,
            "materialExecutionPerformed":
                result.get("EXECUTION_PERFORMED") is True,
            "executionResult": result,
        }

    if result.get("CAPABILITY_ID") != capability_id:
        return {
            "state": "HOLD",
            "reason": "EXECUTED_CAPABILITY_IDENTITY_MISMATCH",
            "workClass": work_class,
            "materialExecutionPerformed": True,
            "executionResult": result,
        }

    if result.get("BINDING_TYPE") != "REGISTERED_ACTION":
        return {
            "state": "HOLD",
            "reason": "EXECUTION_BINDING_TYPE_MISMATCH",
            "workClass": work_class,
            "materialExecutionPerformed": True,
            "executionResult": result,
        }

    if result.get("REGISTERED_HANDLER_INVOKED") is not True:
        return {
            "state": "HOLD",
            "reason": "REGISTERED_HANDLER_NOT_OBSERVED",
            "workClass": work_class,
            "materialExecutionPerformed": True,
            "executionResult": result,
        }

    if result.get("EXECUTION_PERFORMED") is not True:
        return {
            "state": "HOLD",
            "reason": "MATERIAL_EXECUTION_NOT_OBSERVED",
            "workClass": work_class,
            "materialExecutionPerformed": False,
            "executionResult": result,
        }

    return {
        "state": "PASS",
        "reason": "MATERIAL_EXECUTION_VERIFIED",
        "workClass": work_class,
        "capabilityId": capability_id,
        "action": action,
        "authority": authority,
        "humanThresholdState": threshold_state,
        "materialExecutionPerformed": True,
        "executionResult": result,
    }


if __name__ == "__main__":
    print(json.dumps(
        execute_material_work_class("BUILD"),
        ensure_ascii=False,
        indent=2,
    ))
