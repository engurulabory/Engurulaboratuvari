#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ORCHESTRATOR_CONTRACT = (
    ROOT
    / "governance/mac-engineer/SAFE_EXECUTION_ORCHESTRATOR_V1.json"
)

CAPABILITY_REGISTRY = (
    ROOT
    / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.json"
)

BINDING_REGISTRY = (
    ROOT
    / "governance/mac-engineer/CAPABILITY_EXECUTION_BINDING_V1.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(payload: Any) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def hold(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "STATE": "HOLD",
        "MODE": "DRY_RUN",
        "EXECUTION_PERFORMED": False,
        "HOLD_REASON": reason,
        **extra,
    }


def dry_run(plan: dict[str, Any]) -> dict[str, Any]:
    contract = load_json(ORCHESTRATOR_CONTRACT)
    registry = load_json(CAPABILITY_REGISTRY)
    binding_doc = load_json(BINDING_REGISTRY)

    if plan.get("STATE") != "PLAN_READY":
        return hold("PLAN_NOT_READY")

    if not plan.get("PLAN_ID"):
        return hold("PLAN_ID_MISSING")

    if not plan.get("TRUTH_FINGERPRINT"):
        return hold("PLAN_TRUTH_FINGERPRINT_MISSING")

    if plan.get("EXECUTION_AUTHORIZED") is not False:
        return hold("PACKAGE04_EXECUTION_AUTHORITY_VIOLATION")

    capability_plan = plan.get("CAPABILITY_PLAN")

    if not isinstance(capability_plan, list) or not capability_plan:
        return hold("CAPABILITY_PLAN_MISSING")

    caps = {
        row["CAPABILITY_ID"]: row
        for row in registry["capabilities"]
    }

    bindings = {
        row["CAPABILITY_ID"]: row
        for row in binding_doc["bindings"]
    }

    unknown = [
        cid
        for cid in capability_plan
        if cid not in caps
    ]

    if unknown:
        return hold(
            "UNKNOWN_CAPABILITY",
            UNKNOWN_CAPABILITIES=unknown,
        )

    missing_binding = [
        cid
        for cid in capability_plan
        if cid not in bindings
    ]

    if missing_binding:
        return hold(
            "CAPABILITY_BINDING_MISSING",
            MISSING_BINDINGS=missing_binding,
        )

    steps: list[dict[str, Any]] = []

    executable_count = 0
    hold_count = 0
    ht_required_count = 0

    for index, cid in enumerate(capability_plan, start=1):
        cap = caps[cid]
        binding = bindings[cid]

        binding_type = binding["BINDING_TYPE"]

        requires_ht = (
            cap.get("REQUIRES_HUMAN_THRESHOLD") is True
        )

        if requires_ht:
            ht_required_count += 1

        binding_hold_reason = (
            binding.get("REASON")
            if binding_type == "HOLD_UNBOUND"
            else None
        )

        if requires_ht:
            step_state = "HOLD"
            executable = False
            reason = "HUMAN_THRESHOLD_REQUIRED"
            hold_count += 1

        elif binding_type == "HOLD_UNBOUND":
            step_state = "HOLD"
            executable = False
            reason = (
                binding_hold_reason
                or "UNBOUND_CAPABILITY"
            )
            hold_count += 1

        elif binding_type in {
            "DIRECT_RUNTIME",
            "REGISTERED_ACTION",
        }:
            step_state = "DRY_RUN_READY"
            executable = True
            reason = None
            executable_count += 1

        else:
            return hold(
                "UNKNOWN_BINDING_TYPE",
                CAPABILITY_ID=cid,
                BINDING_TYPE=binding_type,
            )

        steps.append(
            {
                "STEP_INDEX": index,
                "CAPABILITY_ID": cid,
                "CAPABILITY_STATE": cap.get("STATE"),
                "AUTHORITY": cap.get("AUTHORITY"),
                "RISK_CLASS": cap.get("RISK_CLASS"),
                "MUTATION_SCOPE": cap.get(
                    "MUTATION_SCOPE"
                ),
                "NETWORK_POLICY": cap.get(
                    "NETWORK_POLICY"
                ),
                "REQUIRES_HUMAN_THRESHOLD":
                    requires_ht,
                "RETRY_POLICY": cap.get(
                    "RETRY_POLICY"
                ),
                "ROLLBACK_POLICY": cap.get(
                    "ROLLBACK_POLICY"
                ),
                "BINDING_TYPE": binding_type,
                "BINDING_HOLD_REASON": binding_hold_reason,
                "DRY_RUN_EXECUTABLE": executable,
                "STEP_STATE": step_state,
                "HOLD_REASON": reason,
                "EXECUTION_PERFORMED": False,
                "EVIDENCE": {
                    "PLAN_ID": plan["PLAN_ID"],
                    "STEP_INDEX": index,
                    "CAPABILITY_ID": cid,
                    "BINDING_TYPE": binding_type,
                    "DRY_RUN_ONLY": True,
                    "EXECUTION_PERFORMED": False,
                },
            }
        )

    final_state = (
        "HOLD"
        if hold_count
        else "DRY_RUN_READY"
    )

    result = {
        "STATE": final_state,
        "MODE": "DRY_RUN",
        "PLAN_ID": plan["PLAN_ID"],
        "TRUTH_FINGERPRINT":
            plan["TRUTH_FINGERPRINT"],
        "PLAN_IMMUTABLE": True,
        "PLAN_MUTATION_PERFORMED": False,
        "EXECUTION_PERFORMED": False,
        "NETWORK_ACCESS_PERFORMED": False,
        "FILESYSTEM_MUTATION_PERFORMED": False,
        "REGISTERED_HANDLER_INVOKED": False,
        "STEP_COUNT": len(steps),
        "EXECUTABLE_STEP_COUNT": executable_count,
        "HOLD_STEP_COUNT": hold_count,
        "HT_REQUIRED_STEP_COUNT":
            ht_required_count,
        "STEPS": steps,
        "EVIDENCE": {
            "orchestratorContract":
                str(
                    ORCHESTRATOR_CONTRACT.relative_to(
                        ROOT
                    )
                ),
            "capabilityRegistry":
                str(
                    CAPABILITY_REGISTRY.relative_to(
                        ROOT
                    )
                ),
            "bindingRegistry":
                str(
                    BINDING_REGISTRY.relative_to(
                        ROOT
                    )
                ),
            "dryRunOnly": True,
        },
    }

    result["DRY_RUN_DIGEST"] = canonical_digest(
        result
    )

    return result



def execute_proven_read_only(
    capability_id: str,
) -> dict[str, Any]:

    registry = load_json(CAPABILITY_REGISTRY)
    binding_doc = load_json(BINDING_REGISTRY)

    caps = {
        row["CAPABILITY_ID"]: row
        for row in registry["capabilities"]
    }

    bindings = {
        row["CAPABILITY_ID"]: row
        for row in binding_doc["bindings"]
    }

    if capability_id not in caps:
        return hold(
            "UNKNOWN_CAPABILITY",
            CAPABILITY_ID=capability_id,
        )

    binding = bindings.get(capability_id)

    if not binding:
        return hold(
            "CAPABILITY_BINDING_MISSING",
            CAPABILITY_ID=capability_id,
        )

    if binding.get("BINDING_TYPE") != "DIRECT_RUNTIME":
        return hold(
            "CAPABILITY_NOT_DIRECT_RUNTIME",
            CAPABILITY_ID=capability_id,
        )

    if binding.get("READ_ONLY_CONFIRMED") is not True:
        return hold(
            "READ_ONLY_NOT_CONFIRMED",
            CAPABILITY_ID=capability_id,
        )

    if (
        binding.get("FILESYSTEM_MUTATION_ALLOWED")
        is not False
    ):
        return hold(
            "READ_ONLY_MUTATION_POLICY_VIOLATION",
            CAPABILITY_ID=capability_id,
        )

    module_name = binding.get("MODULE")
    callable_name = binding.get("CALLABLE")

    allowlist = {
        "CURRENT_TECHNICAL_TRUTH_READ": {
            "MODULE": "mac_engineer_operator",
            "CALLABLE": "current_truth",
            "NETWORK_ALLOWED": False,
        },
        "LOCAL_DOCTOR": {
            "MODULE": "mac_engineer_operator",
            "CALLABLE": "product_doctor",
            "NETWORK_ALLOWED": True,
        },
    }

    policy = allowlist.get(capability_id)

    if policy is None:
        return hold(
            "DIRECT_RUNTIME_ALLOWLIST_MISS",
            CAPABILITY_ID=capability_id,
        )

    if (
        module_name != policy["MODULE"]
        or callable_name != policy["CALLABLE"]
    ):
        return hold(
            "DIRECT_RUNTIME_ALLOWLIST_MISS",
            CAPABILITY_ID=capability_id,
        )

    if (
        binding.get("NETWORK_ALLOWED")
        is not policy["NETWORK_ALLOWED"]
    ):
        return hold(
            "READ_ONLY_NETWORK_POLICY_VIOLATION",
            CAPABILITY_ID=capability_id,
        )

    import mac_engineer_operator as operator

    if capability_id == "CURRENT_TECHNICAL_TRUTH_READ":
        result = operator.current_truth()
        execution_state = "PASS"
        network_access_performed = False

    elif capability_id == "LOCAL_DOCTOR":
        result = operator.product_doctor()

        execution_state = (
            "PASS"
            if result.get("verdict") == "PASS"
            else "HOLD"
        )

        # Conservative accounting:
        # this callable contains authorized ONLINE observation
        # surfaces, even when the environment ultimately uses
        # only local/cache-backed state.
        network_access_performed = True

    else:
        return hold(
            "DIRECT_RUNTIME_ALLOWLIST_MISS",
            CAPABILITY_ID=capability_id,
        )

    payload = {
        "STATE": execution_state,
        "MODE": "EXECUTE_PROVEN_READ_ONLY",
        "CAPABILITY_ID": capability_id,
        "BINDING_TYPE": "DIRECT_RUNTIME",
        "MODULE": module_name,
        "CALLABLE": callable_name,
        "NETWORK_ACCESS_ALLOWED":
            policy["NETWORK_ALLOWED"],
        "NETWORK_ACCESS_PERFORMED":
            network_access_performed,
        "FILESYSTEM_MUTATION_PERFORMED": False,
        "REGISTERED_HANDLER_INVOKED": False,
        "EXECUTION_PERFORMED": True,
        "RESULT": result,
        "EVIDENCE": {
            "bindingRegistry":
                str(BINDING_REGISTRY.relative_to(ROOT)),
            "capabilityRegistry":
                str(CAPABILITY_REGISTRY.relative_to(ROOT)),
            "readOnlyConfirmed": True,
            "allowlistedCallable": True,
            "networkPolicyMatched": True,
        },
    }

    if execution_state != "PASS":
        payload["HOLD_REASON"] = (
            "LOCAL_DOCTOR_HOLD"
            if capability_id == "LOCAL_DOCTOR"
            else "DIRECT_RUNTIME_RESULT_HOLD"
        )

    return payload



def execute_proven_registered_action(
    capability_id: str,
) -> dict[str, Any]:

    registry = load_json(
        CAPABILITY_REGISTRY
    )

    binding_doc = load_json(
        BINDING_REGISTRY
    )

    caps = {
        row["CAPABILITY_ID"]: row
        for row in registry["capabilities"]
    }

    bindings = {
        row["CAPABILITY_ID"]: row
        for row in binding_doc["bindings"]
    }

    if capability_id not in caps:
        return hold(
            "UNKNOWN_CAPABILITY",
            CAPABILITY_ID=capability_id,
        )

    binding = bindings.get(
        capability_id
    )

    if not binding:
        return hold(
            "CAPABILITY_BINDING_MISSING",
            CAPABILITY_ID=capability_id,
        )

    if (
        binding.get("BINDING_TYPE")
        != "REGISTERED_ACTION"
    ):
        return hold(
            "CAPABILITY_NOT_REGISTERED_ACTION",
            CAPABILITY_ID=capability_id,
        )

    if (
        capability_id
        != "OPERATOR_CONTINUE_DISPATCH"
    ):
        return hold(
            "REGISTERED_ACTION_ALLOWLIST_MISS",
            CAPABILITY_ID=capability_id,
        )

    expected = {
        "ACTION":
            "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF",

        "REGISTERED_HANDLER":
            "MAC_NATIVE_RESTART_RECOVERY_FIELD_PROOF",

        "OPERATOR_CALLABLE":
            "run_mac_native_restart_recovery_proof",

        "AUTHORITY":
            "REAL_MAC_LOCAL_PROCESS_RESTART_EVIDENCE",

        "NETWORK_ALLOWED":
            False,

        "REMOTE_PUSH_ALLOWED":
            False,

        "RECOVERY_PROOF_REQUIRED":
            True,

        "EXECUTION_AUTHORITY_CREATED":
            False,
    }

    for key, value in expected.items():
        if binding.get(key) != value:
            return hold(
                "REGISTERED_ACTION_BINDING_MISMATCH",
                CAPABILITY_ID=capability_id,
                FIELD=key,
            )

    import mac_engineer_operator as operator

    action_registry = (
        operator.load_json(
            operator.ACTION_REGISTRY,
            {},
        )
        or {}
    )

    action = binding["ACTION"]

    contract = (
        action_registry.get("actions")
        or {}
    ).get(action)

    if not isinstance(
        contract,
        dict,
    ):
        return hold(
            "ACTION_HANDLER_NOT_REGISTERED",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    if (
        contract.get("handler")
        != binding["REGISTERED_HANDLER"]
    ):
        return hold(
            "REGISTERED_HANDLER_MISMATCH",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    if (
        contract.get("authority")
        != binding["AUTHORITY"]
    ):
        return hold(
            "REGISTERED_AUTHORITY_MISMATCH",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    if (
        contract.get("networkRequired")
        is not False
    ):
        return hold(
            "REGISTERED_ACTION_NETWORK_POLICY_VIOLATION",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    if (
        contract.get("remotePush")
        is not False
    ):
        return hold(
            "REGISTERED_ACTION_REMOTE_PUSH_POLICY_VIOLATION",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    if (
        contract.get("failClosed")
        is not True
    ):
        return hold(
            "REGISTERED_ACTION_FAIL_CLOSED_REQUIRED",
            CAPABILITY_ID=capability_id,
            ACTION=action,
        )

    result = (
        operator
        .run_mac_native_restart_recovery_proof()
    )

    fields = (
        result.get("fields")
        if isinstance(
            result.get("fields"),
            dict,
        )
        else {}
    )

    runtime_evidence = result.get(
        "evidence"
    )

    observed = {
        "wrapperStatePass":
            result.get("state")
            == "PASS",

        "wrapperCodeZero":
            result.get("code")
            == 0,

        "processRestartPass":
            fields.get(
                "PROCESS_RESTART"
            )
            == "PASS",

        "taskIdentityPass":
            fields.get(
                "TASK_IDENTITY"
            )
            == "PASS",

        "checkpointResumePass":
            fields.get(
                "CHECKPOINT_RESUME"
            )
            == "PASS",

        "exactlyOnceEffectPass":
            fields.get(
                "EXACTLY_ONCE_EFFECT"
            )
            == "PASS",

        "finalStateComplete":
            fields.get(
                "FINAL_STATE"
            )
            == "COMPLETE",

        "gitVaultMirrorUnchanged":
            fields.get(
                "GITVAULT_MIRROR_UNCHANGED"
            )
            == "PASS",

        "remotePushFalse":
            fields.get(
                "REMOTE_PUSH"
            )
            == "false",

        "runtimeEvidencePresent":
            bool(runtime_evidence),
    }

    execution_state = (
        "PASS"
        if all(observed.values())
        else "HOLD"
    )

    payload = {
        "STATE":
            execution_state,

        "MODE":
            "EXECUTE_PROVEN_REGISTERED_ACTION",

        "CAPABILITY_ID":
            capability_id,

        "BINDING_TYPE":
            "REGISTERED_ACTION",

        "ACTION":
            action,

        "REGISTERED_HANDLER":
            binding["REGISTERED_HANDLER"],

        "AUTHORITY":
            binding["AUTHORITY"],

        "NETWORK_POLICY":
            {
                "allowed":
                    False,

                "contractNetworkRequired":
                    contract.get(
                        "networkRequired"
                    ),
            },

        "REMOTE_PUSH_POLICY":
            {
                "allowed":
                    False,

                "observedRemotePushFalse":
                    observed[
                        "remotePushFalse"
                    ],
            },

        "MUTATION_SCOPE":
            {
                "filesystemMutationExpected":
                    True,

                "scope":
                    "DISPOSABLE_WORKSPACE_DURABLE_RUNTIME_AND_EVIDENCE",

                "canonicalSourceMutationAllowed":
                    False,

                "remoteMutationAllowed":
                    False,
            },

        "REGISTERED_HANDLER_INVOKED":
            True,

        "EXECUTION_PERFORMED":
            True,

        "RECOVERY_PROOF_REQUIRED":
            True,

        "RECOVERY_PROOF_OBSERVED":
            bool(
                observed[
                    "processRestartPass"
                ]
                and observed[
                    "taskIdentityPass"
                ]
                and observed[
                    "checkpointResumePass"
                ]
                and observed[
                    "exactlyOnceEffectPass"
                ]
                and observed[
                    "finalStateComplete"
                ]
            ),

        "OBSERVED_RESULT":
            observed,

        "RESULT":
            result,

        "EVIDENCE": {
            "bindingRegistry":
                str(
                    BINDING_REGISTRY.relative_to(
                        ROOT
                    )
                ),

            "capabilityRegistry":
                str(
                    CAPABILITY_REGISTRY.relative_to(
                        ROOT
                    )
                ),

            "registeredActionValidated":
                True,

            "registeredHandlerValidated":
                True,

            "authorityMatched":
                True,

            "networkPolicyMatched":
                contract.get(
                    "networkRequired"
                )
                is False,

            "remotePushPolicyMatched":
                observed[
                    "remotePushFalse"
                ],

            "runtimeEvidence":
                runtime_evidence,
        },
    }

    if execution_state != "PASS":
        payload["HOLD_REASON"] = (
            "REGISTERED_ACTION_RESULT_CONTRACT_HOLD"
        )

    return payload


def execute_plan_step(
    plan: dict[str, Any],
    step_index: int,
) -> dict[str, Any]:

    original_digest = canonical_digest(plan)

    if plan.get("STATE") != "PLAN_READY":
        return hold("PLAN_NOT_READY")

    if not plan.get("PLAN_ID"):
        return hold("PLAN_ID_MISSING")

    if not plan.get("TRUTH_FINGERPRINT"):
        return hold("PLAN_TRUTH_FINGERPRINT_MISSING")

    if plan.get("EXECUTION_AUTHORIZED") is not False:
        return hold(
            "PACKAGE04_EXECUTION_AUTHORITY_VIOLATION"
        )

    capability_plan = plan.get("CAPABILITY_PLAN")

    if not isinstance(capability_plan, list):
        return hold("CAPABILITY_PLAN_MISSING")

    if step_index < 1 or step_index > len(capability_plan):
        return hold(
            "PLAN_STEP_INDEX_INVALID",
            STEP_INDEX=step_index,
        )

    capability_id = capability_plan[step_index - 1]

    binding_doc = load_json(
        BINDING_REGISTRY
    )

    bindings = {
        row["CAPABILITY_ID"]: row
        for row in binding_doc["bindings"]
    }

    binding = bindings.get(
        capability_id
    )

    if not binding:
        result = hold(
            "CAPABILITY_BINDING_MISSING",
            CAPABILITY_ID=capability_id,
        )

    elif (
        binding.get("BINDING_TYPE")
        == "DIRECT_RUNTIME"
    ):
        result = execute_proven_read_only(
            capability_id
        )

    elif (
        binding.get("BINDING_TYPE")
        == "REGISTERED_ACTION"
    ):
        result = execute_proven_registered_action(
            capability_id
        )

    else:
        result = hold(
            "CAPABILITY_NOT_EXECUTABLE",
            CAPABILITY_ID=capability_id,
            BINDING_TYPE=binding.get(
                "BINDING_TYPE"
            ),
        )

    if canonical_digest(plan) != original_digest:
        return hold(
            "PLAN_MUTATION_DETECTED",
            PLAN_ID=plan["PLAN_ID"],
        )

    result["PLAN_ID"] = plan["PLAN_ID"]
    result["TRUTH_FINGERPRINT"] = (
        plan["TRUTH_FINGERPRINT"]
    )
    result["STEP_INDEX"] = step_index
    result["PLAN_IMMUTABLE"] = True
    result["PLAN_EXECUTION_AUTHORIZED_INPUT"] = False

    result["STEP_EVIDENCE_DIGEST"] = canonical_digest(
        {
            "PLAN_ID": result["PLAN_ID"],
            "TRUTH_FINGERPRINT":
                result["TRUTH_FINGERPRINT"],
            "STEP_INDEX": step_index,
            "CAPABILITY_ID": capability_id,
            "STATE": result.get("STATE"),
            "EXECUTION_PERFORMED":
                result.get("EXECUTION_PERFORMED"),
            "NETWORK_ACCESS_PERFORMED":
                result.get(
                    "NETWORK_ACCESS_PERFORMED"
                ),
            "FILESYSTEM_MUTATION_PERFORMED":
                result.get(
                    "FILESYSTEM_MUTATION_PERFORMED"
                ),
        }
    )

    return result


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--plan-json",
        required=True,
        help="Package 04 PLAN_READY JSON file",
    )

    args = parser.parse_args()

    plan_path = Path(args.plan_json).resolve()

    if not plan_path.is_file():
        print(
            json.dumps(
                hold("PLAN_FILE_MISSING"),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 20

    plan = load_json(plan_path)
    result = dry_run(plan)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )

    if result["STATE"] in {
        "DRY_RUN_READY",
        "HOLD",
    }:
        return 0

    return 20


if __name__ == "__main__":
    raise SystemExit(main())
