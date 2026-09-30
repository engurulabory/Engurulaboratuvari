#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any

try:
    from mac_engineer_product_operator_v12_action_binding import resolve
except ModuleNotFoundError:
    from tools.mac_engineer_product_operator_v12_action_binding import resolve


ALLOWED_DECISIONS = {"ACCEPT", "REJECT"}


def evaluate_work_class(
    work_class: str,
    *,
    human_decision: str | None = None,
) -> dict[str, Any]:
    binding = resolve(work_class)

    if binding.get("state") != "PASS":
        return {
            "state": "HOLD",
            "reason": binding.get("reason") or "ACTION_BINDING_UNAVAILABLE",
            "workClass": work_class,
            "executionAuthorityCreated": False,
        }

    requires_ht = binding.get("humanThresholdRequired") is True

    if not requires_ht:
        return {
            "state": "CONTINUE",
            "reason": "HUMAN_THRESHOLD_NOT_REQUIRED",
            "workClass": work_class,
            "capabilityId": binding.get("capabilityId"),
            "action": binding.get("action"),
            "handler": binding.get("handler"),
            "authority": binding.get("authority"),
            "humanThresholdRequired": False,
            "humanDecision": None,
            "executionAuthorityCreated": False,
        }

    if human_decision is None:
        return {
            "state": "NEEDS_HUMAN",
            "reason": "HUMAN_THRESHOLD_REQUIRED",
            "workClass": work_class,
            "capabilityId": binding.get("capabilityId"),
            "action": binding.get("action"),
            "handler": binding.get("handler"),
            "authority": binding.get("authority"),
            "humanThresholdRequired": True,
            "allowedDecisions": sorted(ALLOWED_DECISIONS),
            "executionAuthorityCreated": False,
        }

    decision = str(human_decision).strip().upper()

    if decision not in ALLOWED_DECISIONS:
        return {
            "state": "HOLD",
            "reason": "INVALID_HUMAN_THRESHOLD_DECISION",
            "workClass": work_class,
            "humanThresholdRequired": True,
            "humanDecision": decision,
            "executionAuthorityCreated": False,
        }

    if decision == "REJECT":
        return {
            "state": "HOLD",
            "reason": "HUMAN_THRESHOLD_REJECTED",
            "workClass": work_class,
            "capabilityId": binding.get("capabilityId"),
            "action": binding.get("action"),
            "authority": binding.get("authority"),
            "humanThresholdRequired": True,
            "humanDecision": "REJECT",
            "executionAuthorityCreated": False,
        }

    return {
        "state": "READY_AFTER_HUMAN_THRESHOLD",
        "reason": "HUMAN_THRESHOLD_ACCEPTED_FOR_BOUNDED_ACTION",
        "workClass": work_class,
        "capabilityId": binding.get("capabilityId"),
        "action": binding.get("action"),
        "handler": binding.get("handler"),
        "authority": binding.get("authority"),
        "humanThresholdRequired": True,
        "humanDecision": "ACCEPT",
        # G3 proves the decision boundary only.
        # G4 creates/consumes actual execution authority.
        "executionAuthorityCreated": False,
    }


def evaluate() -> dict[str, Any]:
    auto = evaluate_work_class("BUILD")
    needs_human = evaluate_work_class("FILESYSTEM_MACOS_AUTOMATION")
    accepted = evaluate_work_class(
        "FILESYSTEM_MACOS_AUTOMATION",
        human_decision="ACCEPT",
    )
    rejected = evaluate_work_class(
        "FILESYSTEM_MACOS_AUTOMATION",
        human_decision="REJECT",
    )
    invalid = evaluate_work_class(
        "FILESYSTEM_MACOS_AUTOMATION",
        human_decision="YES",
    )
    unbound = evaluate_work_class("ARBITRARY_UNKNOWN_ACTION")

    checks = {
        "nonHtContinues":
            auto.get("state") == "CONTINUE"
            and auto.get("humanThresholdRequired") is False,

        "htStopsForHuman":
            needs_human.get("state") == "NEEDS_HUMAN"
            and needs_human.get("reason") == "HUMAN_THRESHOLD_REQUIRED"
            and needs_human.get("executionAuthorityCreated") is False,

        "acceptedReturnsSameBoundedAction":
            accepted.get("state") == "READY_AFTER_HUMAN_THRESHOLD"
            and accepted.get("action") == needs_human.get("action")
            and accepted.get("authority") == needs_human.get("authority")
            and accepted.get("executionAuthorityCreated") is False,

        "rejectionHolds":
            rejected.get("state") == "HOLD"
            and rejected.get("reason") == "HUMAN_THRESHOLD_REJECTED",

        "invalidDecisionHolds":
            invalid.get("state") == "HOLD"
            and invalid.get("reason") == "INVALID_HUMAN_THRESHOLD_DECISION",

        "unboundHolds":
            unbound.get("state") == "HOLD",

        "noPrematureExecutionAuthority":
            all(
                r.get("executionAuthorityCreated") is False
                for r in (
                    auto,
                    needs_human,
                    accepted,
                    rejected,
                    invalid,
                    unbound,
                )
            ),
    }

    failed = [k for k, v in checks.items() if not v]

    if failed:
        return {
            "STATE": "HOLD",
            "HOLD_REASON": "PRODUCT_OPERATOR_V12_HUMAN_THRESHOLD_MISMATCH",
            "FAILED_CHECKS": failed,
            "CHECKS": checks,
        }

    return {
        "STATE": "PASS",
        "CLAIM": "PRODUCT_OPERATOR_V12_HUMAN_THRESHOLD_ADAPTER_VERIFIED",
        "CHECKS": checks,
        "NEXT_ACTION": "PRODUCT_OPERATOR_V12_G3_ACCEPTANCE_PROMOTION",
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
