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

    try:
        import mac_engineer_operator as operator
    except ModuleNotFoundError:
        from tools import mac_engineer_operator as operator

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

    expected_by_capability = {
        "OPERATOR_CONTINUE_DISPATCH": {
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
        },

        "SOURCE_PRODUCT_CHANGE": {
            "ACTION":
                "PACKAGE08_CAP06_DISPOSABLE_SOURCE_CHANGE_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP06_DISPOSABLE_SOURCE_CHANGE_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap06_disposable_source_change_field_proof",

            "AUTHORITY":
                "REAL_DISPOSABLE_EXACT_BASELINE_SOURCE_MUTATION_EVIDENCE",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "AUTHORIZED_PATH_COUNT":
                2,

            "CANONICAL_SOURCE_MUTATION_ALLOWED":
                False,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },
        "BUILD": {
            "ACTION":
                "PACKAGE08_CAP07_BUILD_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP07_BUILD_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap07_build_field_proof",

            "AUTHORITY":
                "GREEN_LOCAL_BUILD_ARTIFACT_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "MUTATION_SCOPE":
                "BUILD_ARTIFACTS_ONLY",

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "TEST_REGRESSION": {
            "ACTION":
                "PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap08_test_regression_field_proof",

            "AUTHORITY":
                "GREEN_LOCAL_TEST_REGRESSION_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "MUTATION_SCOPE":
                "TEST_ARTIFACTS_ONLY",

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "ROOT_CAUSE_REPAIR": {
            "ACTION":
                "PACKAGE08_CAP09_ROOT_CAUSE_REPAIR_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP09_ROOT_CAUSE_REPAIR_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap09_root_cause_repair_field_proof",

            "AUTHORITY":
                "AMBER_LOCAL_BOUNDED_REPAIR_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "MUTATION_SCOPE":
                "BOUNDED_REPAIR_SCOPE",

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "MIGRATION_CANONICAL_RECONCILIATION": {
            "ACTION":
                "PACKAGE08_CAP10_MIGRATION_CANONICAL_RECONCILIATION_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP10_MIGRATION_CANONICAL_RECONCILIATION_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap10_migration_canonical_reconciliation_field_proof",

            "AUTHORITY":
                "AMBER_HT_ACCEPTED_EXPLICIT_RECONCILIATION_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                True,

            "HUMAN_THRESHOLD_DECISION":
                "ACCEPT",

            "HUMAN_THRESHOLD_RECEIPT_SHA256":
                "b48f594ffb7e66bac4209e1882c6c8394789c4b78da38be47cfe2ea96f0703c4",

            "POST_HUMAN_EVIDENCE_SHA256":
                "2e8c2ad9b2141e6d5de82741cfbddc62cde00ce22392f87dc8e0034279e8592e",

            "MUTATION_SCOPE":
                "EXPLICIT_RECONCILIATION_SCOPE",

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "ADVANCED_CODE_ENGINEERING": {
            "ACTION":
                "PACKAGE08_CAP11_ADVANCED_CODE_ENGINEERING_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP11_ADVANCED_CODE_ENGINEERING_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap11_advanced_code_engineering_field_proof",

            "AUTHORITY":
                "AMBER_LOCAL_EXPLICIT_ENGINEERING_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "MUTATION_SCOPE":
                "EXPLICIT_ENGINEERING_SCOPE",

            "MINIMUM_CHANGED_FILE_COUNT":
                2,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "NEW_PRODUCT_FROM_BRIEF": {
            "ACTION":
                "PACKAGE08_CAP12_NEW_PRODUCT_FROM_BRIEF_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP12_NEW_PRODUCT_FROM_BRIEF_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap12_new_product_from_brief_field_proof",

            "AUTHORITY":
                "AMBER_LOCAL_AUTHORIZED_WORKSPACE_PRODUCT_CREATION_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "MUTATION_SCOPE":
                "AUTHORIZED_WORKSPACE_ONLY",

            "PRODUCT_CREATION_REQUIRED":
                True,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "RELEASE_LIFECYCLE": {
            "ACTION":
                "PACKAGE08_CAP13_RELEASE_LIFECYCLE_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP13_RELEASE_LIFECYCLE_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap13_release_lifecycle_field_proof",

            "AUTHORITY":
                "RED_HT_ACCEPTED_LOCAL_RELEASE_LIFECYCLE_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                True,

            "HUMAN_THRESHOLD_DECISION":
                "ACCEPT",

            "HUMAN_THRESHOLD_RECEIPT_SHA256":
                "5f0d34425a05472a8376544fa2b9604b96cd9f3f1a1945f0f200ed4d80a3ce96",

            "POST_HUMAN_EVIDENCE_SHA256":
                "46f81b7dd6d5291c1116e027c51808963f453a09af5aef0e2276f257a7d4889f",

            "P09_ACCEPTANCE_SHA256":
                "638bd13a48f3070125571e22c38fe3735c30b0157da604513125c35c27b232f2",

            "MUTATION_SCOPE":
                "CONTROLLED_RELEASE_SCOPE",

            "ACTIVE_LIFECYCLE_REEXECUTION_ALLOWED":
                False,

            "CLOUD_PRODUCTION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE": {
            "ACTION":
                "PACKAGE08_CAP14_FINISHED_PRODUCT_DELIVERY_ACCEPTANCE_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP14_FINISHED_PRODUCT_DELIVERY_ACCEPTANCE_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap14_finished_product_delivery_acceptance_field_proof",

            "AUTHORITY":
                "RED_HT_ACCEPTED_FINISHED_PRODUCT_DELIVERY_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                True,

            "HUMAN_THRESHOLD_DECISION":
                "ACCEPT",

            "DELIVERY_PACKAGE_SHA256":
                "c92cafc7da9763acdacc1b267a168d62b6cf7c92c30354838127c740516c6c13",

            "HUMAN_THRESHOLD_RECEIPT_SHA256":
                "744c8919f84ffb222f363ccfd5b5e85ac493d6297a2a46e4eb3c5aceffa72bb0",

            "POST_HUMAN_EVIDENCE_SHA256":
                "b34e072246ea77655a521a0198ba130a3bf8bc7cc08cfb8e82447aed69aa5b64",

            "MUTATION_SCOPE":
                "EVIDENCE_AND_ACCEPTANCE_ONLY",

            "PRODUCT_MUTATION_ALLOWED":
                False,

            "RELEASE_MUTATION_ALLOWED":
                False,

            "ACCEPTANCE_REEXECUTION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "EVIDENCE_DONECHECK": {
            "ACTION":
                "PACKAGE08_CAP15_EVIDENCE_DONECHECK_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP15_EVIDENCE_DONECHECK_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap15_evidence_donecheck_field_proof",

            "AUTHORITY":
                "GREEN_PINNED_DONECHECK_V1_2_EVIDENCE_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                False,

            "HUMAN_THRESHOLD_REQUIRED":
                False,

            "SOURCE_EVIDENCE_SHA256":
                "8bfc00df230bd5f42b87d9e418e349ab6a205ff81ff2fe81be7d8991cb137740",

            "PRIOR_FIELD_EVIDENCE_SHA256":
                "04b868f33dbff0863874925bdf9bb7553fa8fd998f7daada15bbb7b5525056af",

            "DONECHECK_VERSION":
                "1.2.0",

            "DONECHECK_EXACT_SHA":
                "8b90a8fc93453dd8a84994195d28d14b15e261cb",

            "MUTATION_SCOPE":
                "EVIDENCE_ONLY",

            "SOURCE_MUTATION_ALLOWED":
                False,

            "PRODUCT_MUTATION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },


        "RECOVERY_OFFLINE_CONTINUITY": {
            "ACTION":
                "PACKAGE08_CAP16_RECOVERY_OFFLINE_CONTINUITY_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP16_RECOVERY_OFFLINE_CONTINUITY_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap16_recovery_offline_continuity_field_proof",

            "AUTHORITY":
                "AMBER_RECOVERY_OFFLINE_CONTINUITY_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                False,

            "MUTATION_SCOPE":
                "RECOVERY_AND_ROLLBACK_SCOPE",

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "SECOND_CANONICAL_TRUTH":
                False,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "TERMINAL_EXECUTION": {
            "ACTION":
                "PACKAGE08_CAP17_TERMINAL_EXECUTION_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP17_TERMINAL_EXECUTION_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap17_terminal_execution_field_proof",

            "AUTHORITY":
                "AMBER_EXPLICIT_TERMINAL_COMMAND_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "ROLLBACK_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                False,

            "MUTATION_SCOPE":
                "COMMAND_SCOPE_EXPLICIT",

            "SHELL_INTERPOLATION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "FILESYSTEM_MACOS_AUTOMATION": {
            "ACTION":
                "PACKAGE08_CAP18_FILESYSTEM_MACOS_AUTOMATION_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP18_FILESYSTEM_MACOS_AUTOMATION_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap18_filesystem_macos_automation_field_proof",

            "AUTHORITY":
                "AMBER_BOUNDED_FILESYSTEM_AUTOMATION_AUTHORITY",

            "NETWORK_ALLOWED":
                False,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                True,

            "ROLLBACK_REQUIRED":
                True,

            "HUMAN_THRESHOLD_REQUIRED":
                True,

            "HUMAN_THRESHOLD_DECISION":
                "ACCEPT",

            "MUTATION_SCOPE":
                "EXPLICIT_PATH_SCOPE",

            "WORKSPACE_CLASS":
                "DISPOSABLE_TEMPORARY_WORKSPACE_ONLY",

            "FINDER_GUI_AUTHORITY":
                False,

            "CANONICAL_SOURCE_MUTATION_ALLOWED":
                False,

            "PRODUCT_MUTATION_ALLOWED":
                False,

            "PERSISTENT_EXTERNAL_MUTATION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },

        "INTERNET_RESEARCH_HARVEST_ASTRA": {
            "ACTION":
                "PACKAGE08_CAP19_INTERNET_RESEARCH_HARVEST_ASTRA_FIELD_PROOF",

            "REGISTERED_HANDLER":
                "PACKAGE08_CAP19_INTERNET_RESEARCH_HARVEST_ASTRA_FIELD_PROOF",

            "OPERATOR_CALLABLE":
                "run_package08_cap19_internet_research_harvest_astra_field_proof",

            "AUTHORITY":
                "GREEN_BOUNDED_READ_ONLY_RESEARCH_AUTHORITY",

            "NETWORK_ALLOWED":
                True,

            "READ_ONLY_NETWORK":
                True,

            "REMOTE_PUSH_ALLOWED":
                False,

            "RECOVERY_PROOF_REQUIRED":
                False,

            "HUMAN_THRESHOLD_REQUIRED":
                False,

            "MUTATION_SCOPE":
                "RESEARCH_ARTIFACTS_ONLY",

            "GENERAL_BROWSER_AUTHORITY":
                False,

            "CREDENTIAL_REQUIRED":
                False,

            "CANONICAL_SOURCE_MUTATION_ALLOWED":
                False,

            "PRODUCT_MUTATION_ALLOWED":
                False,

            "PERSISTENT_EXTERNAL_MUTATION_ALLOWED":
                False,

            "CANONICAL_TRUTH_PRESERVED":
                True,

            "EXECUTION_AUTHORITY_CREATED":
                False,
        },


    }

    expected = (
        expected_by_capability.get(
            capability_id
        )
    )

    if expected is None:
        return hold(
            "REGISTERED_ACTION_ALLOWLIST_MISS",
            CAPABILITY_ID=capability_id,
        )

    for key, value in expected.items():
        if binding.get(key) != value:
            return hold(
                "REGISTERED_ACTION_BINDING_MISMATCH",
                CAPABILITY_ID=capability_id,
                FIELD=key,
            )

    try:
        import mac_engineer_operator as operator
    except ModuleNotFoundError:
        from tools import mac_engineer_operator as operator

    action_registry = (
        operator.load_json(
            operator.ACTION_REGISTRY,
            {},
        )
        or {}
    )

    action = binding["ACTION"]

    contract = (
        action_registry.get(
            "actions"
        )
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

    expected_network_required = (
        capability_id
        == "INTERNET_RESEARCH_HARVEST_ASTRA"
    )

    if (
        contract.get("networkRequired")
        is not expected_network_required
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

    if capability_id == "FILESYSTEM_MACOS_AUTOMATION":
        cap18_contract = {
            "humanThresholdRequired": True,
            "humanThresholdDecision": "ACCEPT",
            "rollbackRequired": True,
            "mutationScope": "EXPLICIT_PATH_SCOPE",
            "workspaceClass": "DISPOSABLE_TEMPORARY_WORKSPACE_ONLY",
            "finderGuiAuthority": False,
            "canonicalSourceMutationAllowed": False,
            "productMutationAllowed": False,
            "persistentExternalMutationAllowed": False,
            "authorityExpansionAllowed": False,
            "canonicalTruthPreserved": True,
            "technicalCandidateSha256": "ed971c6f56cef4d84e09606e549ac69901b1d9842ddc3ac975e59820246ec80b",
            "humanThresholdReceiptSha256": "7ecc6e8422a4baa051dac0ccacb022fe36050b48f32756521321df7583276265",
        }
        for key, value in cap18_contract.items():
            if contract.get(key) != value:
                return hold(
                    "REGISTERED_ACTION_CAP18_CONTRACT_MISMATCH",
                    CAPABILITY_ID=capability_id,
                    ACTION=action,
                    FIELD=key,
                )

    if capability_id == "INTERNET_RESEARCH_HARVEST_ASTRA":
        cap19_contract = {
            "readOnlyNetwork": True,
            "allowedHosts": ["rfc-editor.org", "www.iana.org", "www.rfc-editor.org"],
            "maxAttempts": 2,
            "credentialRequired": False,
            "humanThresholdRequired": False,
            "mutationScope": "RESEARCH_ARTIFACTS_ONLY",
            "generalBrowserAuthority": False,
            "canonicalSourceMutationAllowed": False,
            "productMutationAllowed": False,
            "persistentExternalMutationAllowed": False,
            "authorityExpansionAllowed": False,
            "canonicalTruthPreserved": True,
        }
        for key, value in cap19_contract.items():
            if contract.get(key) != value:
                return hold(
                    "REGISTERED_ACTION_CAP19_CONTRACT_MISMATCH",
                    CAPABILITY_ID=capability_id,
                    ACTION=action,
                    FIELD=key,
                )

    if capability_id == "SOURCE_PRODUCT_CHANGE":
        if (
            contract.get(
                "authorizedPathCount"
            )
            != 2
        ):
            return hold(
                "REGISTERED_ACTION_AUTHORIZED_PATH_COUNT_MISMATCH",
                CAPABILITY_ID=capability_id,
                ACTION=action,
            )

        if (
            contract.get(
                "canonicalSourceMutation"
            )
            is not False
        ):
            return hold(
                "REGISTERED_ACTION_CANONICAL_MUTATION_POLICY_VIOLATION",
                CAPABILITY_ID=capability_id,
                ACTION=action,
            )

    if (
        capability_id
        == "OPERATOR_CONTINUE_DISPATCH"
    ):
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
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
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
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "DISPOSABLE_WORKSPACE_DURABLE_RUNTIME_AND_EVIDENCE",

            "canonicalSourceMutationAllowed":
                False,

            "remoteMutationAllowed":
                False,
        }

    elif capability_id == "SOURCE_PRODUCT_CHANGE":
        result = (
            operator
            .run_package08_cap06_disposable_source_change_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "sourceChangePass":
                fields.get(
                    "CAP06_SOURCE_CHANGE"
                )
                == "PASS",

            "authorizedPathCountTwo":
                fields.get(
                    "AUTHORIZED_PATH_COUNT"
                )
                == "2",

            "sourceContractPass":
                fields.get(
                    "SOURCE_CONTRACT"
                )
                == "PASS",

            "regressionPass":
                fields.get(
                    "REGRESSION"
                )
                == "PASS",

            "rollbackPass":
                fields.get(
                    "ROLLBACK"
                )
                == "PASS",

            "rollbackByteParityPass":
                fields.get(
                    "ROLLBACK_BYTE_PARITY"
                )
                == "PASS",

            "rollbackWorktreeClean":
                fields.get(
                    "ROLLBACK_WORKTREE_CLEAN"
                )
                == "PASS",

            "failurePathPass":
                fields.get(
                    "FAILURE_PATH"
                )
                == "PASS",

            "canonicalControlUnchanged":
                fields.get(
                    "CANONICAL_CONTROL_UNCHANGED"
                )
                == "PASS",

            "canonicalProductUnchanged":
                fields.get(
                    "CANONICAL_PRODUCT_UNCHANGED"
                )
                == "PASS",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "networkRequiredFalse":
                fields.get(
                    "NETWORK_REQUIRED"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "rollbackPass"
            ]
            and observed[
                "rollbackByteParityPass"
            ]
            and observed[
                "rollbackWorktreeClean"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "DISPOSABLE_EXACT_BASELINE_BOUNDED_SOURCE_MUTATION",

            "authorizedPathCount":
                2,

            "canonicalSourceMutationAllowed":
                False,

            "remoteMutationAllowed":
                False,
        }

    elif capability_id == "BUILD":
        result = (
            operator
            .run_package08_cap07_build_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "buildPass":
                fields.get(
                    "CAP07_BUILD"
                )
                == "PASS",

            "artifactExecutable":
                fields.get(
                    "BUILD_ARTIFACT_EXECUTABLE"
                )
                == "PASS",

            "artifactIdentityPresent":
                bool(
                    fields.get(
                        "BUILD_ARTIFACT_SHA256"
                    )
                ),

            "controlledCompilerRejection":
                fields.get(
                    "CONTROLLED_COMPILER_REJECTION"
                )
                == "PASS",

            "failedArtifactCleanup":
                fields.get(
                    "FAILED_ARTIFACT_CLEANUP"
                )
                == "PASS",

            "canonicalTruthPreserved":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityGreen":
                fields.get(
                    "AUTHORITY"
                )
                == "GREEN",

            "localOnly":
                fields.get(
                    "NETWORK_POLICY"
                )
                == "LOCAL_ONLY",

            "buildArtifactsOnly":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "BUILD_ARTIFACTS_ONLY",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = False

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "BUILD_ARTIFACTS_ONLY",

            "canonicalTruthPreserved":
                True,

            "artifactIdentityRequired":
                True,
        }

    elif capability_id == "TEST_REGRESSION":
        result = (
            operator
            .run_package08_cap08_test_regression_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "regressionPass":
                fields.get(
                    "CAP08_TEST_REGRESSION"
                )
                == "PASS",

            "targetedPass":
                fields.get(
                    "TARGETED_REGRESSION"
                )
                == "PASS",

            "fullPass":
                fields.get(
                    "FULL_RUNTIME_REGRESSION"
                )
                == "PASS",

            "failureDetected":
                fields.get(
                    "CONTROLLED_TEST_FAILURE_DETECTED"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruthPreserved":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityGreen":
                fields.get(
                    "AUTHORITY"
                )
                == "GREEN",

            "localOnly":
                fields.get(
                    "NETWORK_POLICY"
                )
                == "LOCAL_ONLY",

            "testArtifactsOnly":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "TEST_ARTIFACTS_ONLY",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = False

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "TEST_ARTIFACTS_ONLY",

            "canonicalTruthPreserved":
                True,

            "testEvidenceRequired":
                True,
        }

    elif capability_id == "ROOT_CAUSE_REPAIR":
        result = (
            operator
            .run_package08_cap09_root_cause_repair_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "repairPass":
                fields.get(
                    "CAP09_ROOT_CAUSE_REPAIR"
                )
                == "PASS",

            "failureReproduced":
                fields.get(
                    "CONTROLLED_FAILURE_REPRODUCED"
                )
                == "PASS",

            "rootCauseEvidence":
                fields.get(
                    "ROOT_CAUSE_EVIDENCE"
                )
                == "PASS",

            "rootCauseIdentity":
                fields.get(
                    "ROOT_CAUSE"
                )
                == "controlled_bounded_fault_marker_block",

            "smallestRepair":
                fields.get(
                    "SMALLEST_SUFFICIENT_REPAIR"
                )
                == "PASS",

            "regressionPass":
                fields.get(
                    "POST_REPAIR_REGRESSION"
                )
                == "PASS",

            "runtimeVerifyPass":
                fields.get(
                    "POST_REPAIR_RUNTIME_VERIFY"
                )
                == "PASS",

            "rollbackBaselineParity":
                fields.get(
                    "ROLLBACK_BASELINE_PARITY"
                )
                == "PASS",

            "finalFixtureClean":
                fields.get(
                    "FINAL_FIXTURE_CLEAN"
                )
                == "PASS",

            "sourceFixtureTruthPreserved":
                fields.get(
                    "SOURCE_FIXTURE_TRUTH_PRESERVED"
                )
                == "PASS",

            "repairIdempotent":
                fields.get(
                    "REPAIR_IDEMPOTENCY"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruthPreserved":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityAmber":
                fields.get(
                    "AUTHORITY"
                )
                == "AMBER",

            "boundedRepairScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "BOUNDED_REPAIR_SCOPE",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "rollbackBaselineParity"
            ]
            and observed[
                "finalFixtureClean"
            ]
            and observed[
                "sourceFixtureTruthPreserved"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "BOUNDED_REPAIR_SCOPE",

            "canonicalTruthPreserved":
                True,

            "rootCauseEvidenceRequired":
                True,

            "smallestSufficientRepairRequired":
                True,
        }

    elif capability_id == "MIGRATION_CANONICAL_RECONCILIATION":
        result = (
            operator
            .run_package08_cap10_migration_canonical_reconciliation_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "reconciliationPass":
                fields.get(
                    "CAP10_MIGRATION_CANONICAL_RECONCILIATION"
                )
                == "PASS",

            "humanThresholdAccept":
                fields.get(
                    "HUMAN_THRESHOLD_ACCEPT"
                )
                == "PASS",

            "technicalRollbackParity":
                fields.get(
                    "TECHNICAL_ROLLBACK_PARITY"
                )
                == "PASS",

            "reconciliationIdempotency":
                fields.get(
                    "RECONCILIATION_IDEMPOTENCY"
                )
                == "PASS",

            "freshRepo":
                fields.get(
                    "FRESH_REPO_REREAD"
                )
                == "PASS",

            "freshRuntime":
                fields.get(
                    "FRESH_RUNTIME_REREAD"
                )
                == "PASS",

            "freshArtifact":
                fields.get(
                    "FRESH_ARTIFACT_REREAD"
                )
                == "PASS",

            "freshState":
                fields.get(
                    "FRESH_STATE_REREAD"
                )
                == "PASS",

            "newVerifiedState":
                fields.get(
                    "NEW_VERIFIED_STATE_ESTABLISHED"
                )
                == "PASS",

            "staleResumeRejected":
                fields.get(
                    "STALE_RESUME_REJECTED"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruthPreserved":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityAmber":
                fields.get(
                    "AUTHORITY"
                )
                == "AMBER",

            "explicitReconciliationScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "EXPLICIT_RECONCILIATION_SCOPE",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "humanThresholdReceiptDigest":
                fields.get(
                    "HUMAN_THRESHOLD_RECEIPT_SHA256"
                )
                == "b48f594ffb7e66bac4209e1882c6c8394789c4b78da38be47cfe2ea96f0703c4",

            "postHumanEvidenceDigest":
                fields.get(
                    "POST_HUMAN_EVIDENCE_SHA256"
                )
                == "2e8c2ad9b2141e6d5de82741cfbddc62cde00ce22392f87dc8e0034279e8592e",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "technicalRollbackParity"
            ]
            and observed[
                "reconciliationIdempotency"
            ]
            and observed[
                "staleResumeRejected"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "EXPLICIT_RECONCILIATION_SCOPE",

            "canonicalTruthPreserved":
                True,

            "humanThresholdRequired":
                True,

            "humanThresholdObserved":
                observed[
                    "humanThresholdAccept"
                ],

            "postHumanFreshReconciliationRequired":
                True,
        }

    elif capability_id == "ADVANCED_CODE_ENGINEERING":
        result = (
            operator
            .run_package08_cap11_advanced_code_engineering_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "engineeringPass":
                fields.get(
                    "CAP11_ADVANCED_CODE_ENGINEERING"
                )
                == "PASS",

            "negativeControl":
                fields.get(
                    "INCOMPLETE_MULTI_FILE_CHANGE_FAILURE"
                )
                == "PASS",

            "multiFileScope":
                fields.get(
                    "MULTI_FILE_SCOPE"
                )
                == "PASS",

            "changedFileCount":
                fields.get(
                    "CHANGED_FILE_COUNT"
                )
                == "2",

            "targetedRegression":
                fields.get(
                    "TARGETED_REGRESSION"
                )
                == "PASS",

            "fullRegression":
                fields.get(
                    "FULL_REGRESSION"
                )
                == "PASS",

            "publicBehavior":
                fields.get(
                    "PUBLIC_ADD_BEHAVIOR_PRESERVED"
                )
                == "PASS",

            "internalAbstraction":
                fields.get(
                    "INTERNAL_OPERATION_ABSTRACTION"
                )
                == "PASS",

            "idempotent":
                fields.get(
                    "ENGINEERING_IDEMPOTENCY"
                )
                == "PASS",

            "rollbackParity":
                fields.get(
                    "ROLLBACK_BYTE_PARITY"
                )
                == "PASS",

            "rollbackClean":
                fields.get(
                    "ROLLBACK_WORKTREE_CLEAN"
                )
                == "PASS",

            "rollbackRegression":
                fields.get(
                    "ROLLBACK_REGRESSION"
                )
                == "PASS",

            "sourceFixtureTruth":
                fields.get(
                    "SOURCE_FIXTURE_TRUTH_PRESERVED"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityAmber":
                fields.get(
                    "AUTHORITY"
                )
                == "AMBER",

            "engineeringScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "EXPLICIT_ENGINEERING_SCOPE",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "rollbackParity"
            ]
            and observed[
                "rollbackClean"
            ]
            and observed[
                "rollbackRegression"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "EXPLICIT_ENGINEERING_SCOPE",

            "minimumChangedFileCount":
                2,

            "canonicalTruthPreserved":
                True,

            "rollbackRequired":
                True,
        }

    elif capability_id == "NEW_PRODUCT_FROM_BRIEF":
        result = (
            operator
            .run_package08_cap12_new_product_from_brief_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "productFromBriefPass":
                fields.get(
                    "CAP12_NEW_PRODUCT_FROM_BRIEF"
                )
                == "PASS",

            "negativeControl":
                fields.get(
                    "INCOMPLETE_BRIEF_PRODUCT_REJECTED"
                )
                == "PASS",

            "requiredProductFiles":
                fields.get(
                    "REQUIRED_PRODUCT_FILES"
                )
                == "PASS",

            "productFileCountFour":
                fields.get(
                    "PRODUCT_FILE_COUNT"
                )
                == "4",

            "callableContract":
                fields.get(
                    "CALLABLE_CONTRACT"
                )
                == "PASS",

            "productTest":
                fields.get(
                    "PRODUCT_TEST"
                )
                == "PASS",

            "cliRuntime":
                fields.get(
                    "CLI_RUNTIME_VERIFY"
                )
                == "PASS",

            "cliFailurePath":
                fields.get(
                    "CLI_FAILURE_PATH"
                )
                == "PASS",

            "productManifest":
                fields.get(
                    "PRODUCT_MANIFEST"
                )
                == "PASS",

            "idempotent":
                fields.get(
                    "PRODUCT_IDEMPOTENCY"
                )
                == "PASS",

            "workspaceCleanup":
                fields.get(
                    "DISPOSABLE_WORKSPACE_CLEANUP"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityAmber":
                fields.get(
                    "AUTHORITY"
                )
                == "AMBER",

            "authorizedWorkspaceScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "AUTHORIZED_WORKSPACE_ONLY",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "runtimeEvidencePresent":
                bool(
                    result.get(
                        "evidence"
                    )
                ),
        }

        recovery_observed = bool(
            observed[
                "workspaceCleanup"
            ]
            and observed[
                "idempotent"
            ]
            and observed[
                "negativeControl"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "AUTHORIZED_WORKSPACE_ONLY",

            "productCreationRequired":
                True,

            "canonicalTruthPreserved":
                True,

            "rollbackRequired":
                True,
        }

    elif capability_id == "RELEASE_LIFECYCLE":
        result = (
            operator
            .run_package08_cap13_release_lifecycle_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "releaseLifecyclePass":
                fields.get(
                    "CAP13_RELEASE_LIFECYCLE"
                )
                == "PASS",

            "humanThresholdAccept":
                fields.get(
                    "HUMAN_THRESHOLD_ACCEPT"
                )
                == "PASS",

            "htConsumedOnce":
                fields.get(
                    "HT_EXECUTION_ALREADY_CONSUMED"
                )
                == "PASS",

            "activeLifecycle":
                fields.get(
                    "ACTIVE_LIFECYCLE_EXECUTED"
                )
                == "PASS",

            "controlledReplacement":
                fields.get(
                    "CONTROLLED_REPLACEMENT"
                )
                == "PASS",

            "knownGoodRollback":
                fields.get(
                    "KNOWN_GOOD_ROLLBACK"
                )
                == "PASS",

            "rollbackReverify":
                fields.get(
                    "ROLLBACK_REVERIFY"
                )
                == "PASS",

            "provenance":
                fields.get(
                    "LIFECYCLE_PROVENANCE"
                )
                == "PASS",

            "evidenceContinuity":
                fields.get(
                    "EVIDENCE_CONTINUITY"
                )
                == "PASS",

            "codesign":
                fields.get(
                    "FRESH_CODESIGN"
                )
                == "PASS",

            "runtime":
                fields.get(
                    "FRESH_RUNTIME_REVERIFY"
                )
                == "PASS",

            "sourceMutationFalse":
                fields.get(
                    "SOURCE_MUTATION"
                )
                == "false",

            "remoteMutationFalse":
                fields.get(
                    "REMOTE_MUTATION"
                )
                == "false",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "cloudProductionFalse":
                fields.get(
                    "CLOUD_PRODUCTION"
                )
                == "false",

            "dnsMutationFalse":
                fields.get(
                    "DNS_MUTATION"
                )
                == "false",

            "domainMutationFalse":
                fields.get(
                    "DOMAIN_MUTATION"
                )
                == "false",

            "verifiedLiveFalse":
                fields.get(
                    "VERIFIED_LIVE_GRANTED"
                )
                == "false",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityRed":
                fields.get(
                    "AUTHORITY"
                )
                == "RED",

            "controlledReleaseScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "CONTROLLED_RELEASE_SCOPE",

            "receiptDigest":
                fields.get(
                    "HUMAN_THRESHOLD_RECEIPT_SHA256"
                )
                == "5f0d34425a05472a8376544fa2b9604b96cd9f3f1a1945f0f200ed4d80a3ce96",

            "postHumanDigest":
                fields.get(
                    "POST_HUMAN_EVIDENCE_SHA256"
                )
                == "46f81b7dd6d5291c1116e027c51808963f453a09af5aef0e2276f257a7d4889f",

            "p09Digest":
                fields.get(
                    "P09_ACCEPTANCE_SHA256"
                )
                == "638bd13a48f3070125571e22c38fe3735c30b0157da604513125c35c27b232f2",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "knownGoodRollback"
            ]
            and observed[
                "rollbackReverify"
            ]
            and observed[
                "provenance"
            ]
            and observed[
                "evidenceContinuity"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                False,

            "historicalControlledMutationObserved":
                True,

            "scope":
                "CONTROLLED_RELEASE_SCOPE",

            "humanThresholdRequired":
                True,

            "humanThresholdConsumed":
                True,

            "activeLifecycleReexecutionAllowed":
                False,

            "cloudProductionAllowed":
                False,

            "canonicalTruthPreserved":
                True,
        }

    elif capability_id == "FILESYSTEM_MACOS_AUTOMATION":
        result = (
            operator
            .run_package08_cap18_filesystem_macos_automation_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(result.get("fields"), dict)
            else {}
        )

        observed = {
            "wrapperStatePass": result.get("state") == "PASS",
            "wrapperCodeZero": result.get("code") == 0,
            "capabilityPass": fields.get("CAP18_FILESYSTEM_MACOS_AUTOMATION") == "PASS",
            "technicalShaExact": fields.get("TECHNICAL_SHA_EXACT") == "PASS",
            "humanThresholdShaExact": fields.get("HUMAN_THRESHOLD_SHA_EXACT") == "PASS",
            "explicitScope": fields.get("EXPLICIT_PATH_SCOPE") == "PASS",
            "disposableWorkspace": fields.get("DISPOSABLE_WORKSPACE_ONLY") == "PASS",
            "realTaskEvidence": fields.get("REAL_TASK_EVIDENCE_ACCEPTED") == "PASS",
            "expectedResult": fields.get("EXPECTED_RESULT_OBSERVED") == "PASS",
            "failurePath": fields.get("FAILURE_PATH_TESTED") == "PASS",
            "rollback": fields.get("ROLLBACK") == "PASS",
            "rollbackParity": fields.get("ROLLBACK_BYTE_PARITY") == "PASS",
            "scopeClean": fields.get("SCOPE_CLEAN") == "PASS",
            "freshReverify": fields.get("FRESH_REVERIFY") == "PASS",
            "humanThresholdAccept": fields.get("HUMAN_THRESHOLD") == "ACCEPT",
            "humanThresholdConsumed": fields.get("HUMAN_THRESHOLD_CONSUMED") == "true",
            "networkFalse": fields.get("NETWORK_ACCESS") == "false",
            "remotePushFalse": fields.get("REMOTE_PUSH") == "false",
            "finderGuiFalse": fields.get("FINDER_GUI_AUTHORITY") == "false",
            "canonicalMutationFalse": fields.get("CANONICAL_SOURCE_MUTATION") == "false",
            "productMutationFalse": fields.get("PRODUCT_MUTATION") == "false",
            "persistentExternalMutationFalse": fields.get("PERSISTENT_EXTERNAL_MUTATION") == "false",
            "authorityCreatedFalse": fields.get("EXECUTION_AUTHORITY_CREATED") == "false",
            "notReexecuted": fields.get("CAPABILITY_REEXECUTED") == "false",
            "canonicalTruth": fields.get("CANONICAL_TRUTH_PRESERVED") == "PASS",
            "falsePassZero": fields.get("CRITICAL_FALSE_PASS_COUNT") == "0",
            "runtimeEvidencePresent": bool(result.get("evidence")),
        }

        recovery_observed = bool(
            observed["rollback"]
            and observed["rollbackParity"]
            and observed["scopeClean"]
        )

        mutation_scope = {
            "filesystemMutationExpected": True,
            "technicalFilesystemMutationExpected": False,
            "evidenceSealMutationExpected": True,
            "scope": "EXPLICIT_PATH_SCOPE",
            "workspaceClass": "DISPOSABLE_TEMPORARY_WORKSPACE_ONLY",
            "humanThresholdRequired": True,
            "humanThresholdDecision": "ACCEPT",
            "recoveryProofRequired": True,
            "rollbackRequired": True,
            "finderGuiAuthority": False,
            "canonicalSourceMutationAllowed": False,
            "productMutationAllowed": False,
            "persistentExternalMutationAllowed": False,
            "remoteMutationAllowed": False,
            "technicalFieldTaskReexecuted": False,
            "canonicalTruthPreserved": True,
        }

    elif capability_id == "INTERNET_RESEARCH_HARVEST_ASTRA":
        result = (
            operator
            .run_package08_cap19_internet_research_harvest_astra_field_proof()
        )

        fields = result.get("fields") if isinstance(result.get("fields"), dict) else {}
        observed = {
            "wrapperStatePass": result.get("state") == "PASS",
            "wrapperCodeZero": result.get("code") == 0,
            "capabilityPass": fields.get("CAP19_INTERNET_RESEARCH_HARVEST_ASTRA") == "PASS",
            "networkAccess": fields.get("NETWORK_ACCESS") == "true",
            "networkMutationFalse": fields.get("NETWORK_MUTATION") == "false",
            "sourceMutationFalse": fields.get("SOURCE_MUTATION") == "false",
            "productMutationFalse": fields.get("PRODUCT_MUTATION") == "false",
            "remotePushFalse": fields.get("REMOTE_PUSH") == "false",
            "credentialFalse": fields.get("CREDENTIAL_USED") == "false",
            "freshSources": fields.get("FRESH_SOURCES") == "2",
            "astraSynthesis": fields.get("ASTRA_SYNTHESIS") == "PASS",
            "expectedResult": fields.get("EXPECTED_RESULT_OBSERVED") == "PASS",
            "failurePath": fields.get("FAILURE_PATH_TESTED") == "PASS",
            "boundedRetry": fields.get("BOUNDED_RETRY") == "PASS",
            "freshReverify": fields.get("FRESH_REVERIFY") == "PASS",
            "doneCheck": fields.get("DONECHECK") == "PASS",
            "humanThresholdFalse": fields.get("HUMAN_THRESHOLD_REQUIRED") == "false",
            "generalBrowserFalse": fields.get("GENERAL_BROWSER_AUTHORITY") == "false",
            "canonicalTruth": fields.get("CANONICAL_TRUTH_PRESERVED") == "PASS",
            "falsePassZero": fields.get("CRITICAL_FALSE_PASS_COUNT") == "0",
            "runtimeEvidencePresent": bool(result.get("evidence")),
        }

        recovery_observed = False
        mutation_scope = {
            "filesystemMutationExpected": True,
            "scope": "RESEARCH_ARTIFACTS_ONLY",
            "networkAccessExpected": True,
            "networkMutationAllowed": False,
            "sourceMutationAllowed": False,
            "productMutationAllowed": False,
            "remoteMutationAllowed": False,
            "generalBrowserAuthority": False,
            "credentialRequired": False,
            "humanThresholdRequired": False,
            "canonicalTruthPreserved": True,
        }

    elif capability_id == "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE":
        result = (
            operator
            .run_package08_cap14_finished_product_delivery_acceptance_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "deliveryAcceptancePass":
                fields.get(
                    "CAP14_FINISHED_PRODUCT_DELIVERY_ACCEPTANCE"
                )
                == "PASS",

            "humanThresholdAccept":
                fields.get(
                    "HUMAN_THRESHOLD_ACCEPT"
                )
                == "PASS",

            "htConsumedOnce":
                fields.get(
                    "HT_ACCEPTANCE_ALREADY_CONSUMED"
                )
                == "PASS",

            "deliveryImmutable":
                fields.get(
                    "DELIVERY_PACKAGE_IMMUTABLE"
                )
                == "PASS",

            "exactProductIdentity":
                fields.get(
                    "EXACT_PRODUCT_IDENTITY_BOUND"
                )
                == "PASS",

            "finishedProductDelivered":
                fields.get(
                    "FINISHED_PRODUCT_DELIVERED"
                )
                == "PASS",

            "humanDeliveryAcceptance":
                fields.get(
                    "HUMAN_DELIVERY_ACCEPTANCE"
                )
                == "PASS",

            "codesign":
                fields.get(
                    "FRESH_CODESIGN"
                )
                == "PASS",

            "runtime":
                fields.get(
                    "FRESH_RUNTIME_REVERIFY"
                )
                == "PASS",

            "productMutationFalse":
                fields.get(
                    "PRODUCT_MUTATION"
                )
                == "false",

            "releaseMutationFalse":
                fields.get(
                    "RELEASE_MUTATION"
                )
                == "false",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "cloudPublicationFalse":
                fields.get(
                    "CLOUD_PUBLICATION"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityRed":
                fields.get(
                    "AUTHORITY"
                )
                == "RED",

            "acceptanceScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "EVIDENCE_AND_ACCEPTANCE_ONLY",

            "deliveryDigest":
                fields.get(
                    "DELIVERY_PACKAGE_SHA256"
                )
                == "c92cafc7da9763acdacc1b267a168d62b6cf7c92c30354838127c740516c6c13",

            "receiptDigest":
                fields.get(
                    "HUMAN_THRESHOLD_RECEIPT_SHA256"
                )
                == "744c8919f84ffb222f363ccfd5b5e85ac493d6297a2a46e4eb3c5aceffa72bb0",

            "postHumanDigest":
                fields.get(
                    "POST_HUMAN_EVIDENCE_SHA256"
                )
                == "b34e072246ea77655a521a0198ba130a3bf8bc7cc08cfb8e82447aed69aa5b64",

            "runtimeEvidencePresent":
                bool(
                    result.get("evidence")
                ),
        }

        recovery_observed = bool(
            observed[
                "deliveryImmutable"
            ]
            and observed[
                "exactProductIdentity"
            ]
            and observed[
                "productMutationFalse"
            ]
            and observed[
                "releaseMutationFalse"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                False,

            "historicalHumanAcceptanceObserved":
                True,

            "scope":
                "EVIDENCE_AND_ACCEPTANCE_ONLY",

            "humanThresholdRequired":
                True,

            "humanThresholdConsumed":
                True,

            "acceptanceReexecutionAllowed":
                False,

            "productMutationAllowed":
                False,

            "releaseMutationAllowed":
                False,

            "canonicalTruthPreserved":
                True,
        }

    elif capability_id == "EVIDENCE_DONECHECK":
        result = (
            operator
            .run_package08_cap15_evidence_donecheck_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "capabilityPass":
                fields.get(
                    "CAP15_EVIDENCE_DONECHECK"
                )
                == "PASS",

            "freshMaterialEvidence":
                fields.get(
                    "FRESH_MATERIAL_EVIDENCE"
                )
                == "PASS",

            "doneCheckPass":
                fields.get(
                    "DONECHECK_STATE"
                )
                == "PASS",

            "doneCheckVersion":
                fields.get(
                    "DONECHECK_VERSION"
                )
                == "1.2.0",

            "doneCheckSha":
                fields.get(
                    "DONECHECK_SHA"
                )
                == "8b90a8fc93453dd8a84994195d28d14b15e261cb",

            "verificationResultPresent":
                bool(
                    fields.get(
                        "VERIFICATION_RESULT_ID"
                    )
                ),

            "governedFinishVerified":
                fields.get(
                    "GOVERNED_FINISH"
                )
                == "VERIFIED",

            "nonPassRejected":
                fields.get(
                    "NONPASS_EVIDENCE_REJECTED"
                )
                == "PASS",

            "missingEvidenceHold":
                fields.get(
                    "MISSING_EVIDENCE_HOLD"
                )
                == "PASS",

            "staleCachedPassHold":
                fields.get(
                    "STALE_CACHED_PASS_HOLD"
                )
                == "PASS",

            "doneCheckNonPassHold":
                fields.get(
                    "DONECHECK_NONPASS_HOLD"
                )
                == "PASS",

            "unsupportedClaimHold":
                fields.get(
                    "UNSUPPORTED_FINAL_CLAIM_HOLD"
                )
                == "PASS",

            "humanThresholdFalse":
                fields.get(
                    "HUMAN_THRESHOLD_REQUIRED"
                )
                == "false",

            "sourceMutationFalse":
                fields.get(
                    "SOURCE_MUTATION"
                )
                == "false",

            "productMutationFalse":
                fields.get(
                    "PRODUCT_MUTATION"
                )
                == "false",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "networkMutationFalse":
                fields.get(
                    "NETWORK_MUTATION"
                )
                == "false",

            "executionAuthorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityGreen":
                fields.get(
                    "AUTHORITY"
                )
                == "GREEN",

            "evidenceOnly":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "EVIDENCE_ONLY",

            "sourceDigest":
                fields.get(
                    "SOURCE_EVIDENCE_SHA256"
                )
                == "8bfc00df230bd5f42b87d9e418e349ab6a205ff81ff2fe81be7d8991cb137740",

            "priorFieldDigest":
                fields.get(
                    "PRIOR_FIELD_EVIDENCE_SHA256"
                )
                == "04b868f33dbff0863874925bdf9bb7553fa8fd998f7daada15bbb7b5525056af",

            "runtimeEvidencePresent":
                bool(
                    result.get(
                        "evidence"
                    )
                ),
        }

        recovery_observed = False

        mutation_scope = {
            "filesystemMutationExpected":
                False,

            "scope":
                "EVIDENCE_ONLY",

            "humanThresholdRequired":
                False,

            "recoveryProofRequired":
                False,

            "sourceMutationAllowed":
                False,

            "productMutationAllowed":
                False,

            "remoteMutationAllowed":
                False,

            "canonicalTruthPreserved":
                True,
        }

    elif capability_id == "RECOVERY_OFFLINE_CONTINUITY":
        result = (
            operator
            .run_package08_cap16_recovery_offline_continuity_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "capabilityPass":
                fields.get(
                    "CAP16_RECOVERY_OFFLINE_CONTINUITY"
                )
                == "PASS",

            "restartRecovery":
                fields.get(
                    "RESTART_RECOVERY"
                )
                == "PASS",

            "checkpointResume":
                fields.get(
                    "CHECKPOINT_RESUME"
                )
                == "PASS",

            "exactlyOnce":
                fields.get(
                    "EXACTLY_ONCE_EFFECT"
                )
                == "PASS",

            "offlineContinuity":
                fields.get(
                    "OFFLINE_CONTINUITY"
                )
                == "PASS",

            "offlineQueue":
                fields.get(
                    "OFFLINE_QUEUE"
                )
                == "PASS",

            "durablePatch":
                fields.get(
                    "DURABLE_PATCH"
                )
                == "PASS",

            "durableBundle":
                fields.get(
                    "DURABLE_GIT_BUNDLE"
                )
                == "PASS",

            "reconciliation":
                fields.get(
                    "RECONCILIATION_APPLY_CHECK"
                )
                == "PASS",

            "refsUnchanged":
                fields.get(
                    "GITVAULT_REFS_UNCHANGED"
                )
                == "PASS",

            "remoteIdentity":
                fields.get(
                    "REMOTE_IDENTITY_PRESERVED"
                )
                == "PASS",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "networkFalse":
                fields.get(
                    "NETWORK_REQUIRED"
                )
                == "false",

            "secondTruthFalse":
                fields.get(
                    "SECOND_CANONICAL_TRUTH"
                )
                == "false",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "authorityAmber":
                fields.get(
                    "AUTHORITY"
                )
                == "AMBER",

            "mutationScope":
                fields.get(
                    "MUTATION_SCOPE"
                )
                == "RECOVERY_AND_ROLLBACK_SCOPE",

            "humanThresholdFalse":
                fields.get(
                    "HUMAN_THRESHOLD_REQUIRED"
                )
                == "false",

            "restartDigest":
                (
                    len(
                        fields.get(
                            "RESTART_EVIDENCE_SHA256",
                            "",
                        )
                    )
                    == 64
                    and all(
                        c
                        in "0123456789abcdef"
                        for c
                        in fields.get(
                            "RESTART_EVIDENCE_SHA256",
                            "",
                        )
                    )
                ),

            "offlineDigest":
                (
                    len(
                        fields.get(
                            "OFFLINE_EVIDENCE_SHA256",
                            "",
                        )
                    )
                    == 64
                    and all(
                        c
                        in "0123456789abcdef"
                        for c
                        in fields.get(
                            "OFFLINE_EVIDENCE_SHA256",
                            "",
                        )
                    )
                ),

            "runtimeEvidencePresent":
                bool(
                    result.get(
                        "evidence"
                    )
                ),
        }

        recovery_observed = bool(
            observed[
                "restartRecovery"
            ]
            and observed[
                "checkpointResume"
            ]
            and observed[
                "exactlyOnce"
            ]
            and observed[
                "offlineContinuity"
            ]
            and observed[
                "reconciliation"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "RECOVERY_AND_ROLLBACK_SCOPE",

            "humanThresholdRequired":
                False,

            "recoveryProofRequired":
                True,

            "canonicalSourceMutationAllowed":
                False,

            "remoteMutationAllowed":
                False,

            "secondCanonicalTruthAllowed":
                False,

            "canonicalTruthPreserved":
                True,
        }


    elif capability_id == "TERMINAL_EXECUTION":
        result = (
            operator
            .run_package08_cap17_terminal_execution_field_proof()
        )

        fields = (
            result.get("fields")
            if isinstance(
                result.get("fields"),
                dict,
            )
            else {}
        )

        observed = {
            "wrapperStatePass":
                result.get("state")
                == "PASS",

            "wrapperCodeZero":
                result.get("code")
                == 0,

            "capabilityPass":
                fields.get(
                    "CAP17_TERMINAL_EXECUTION"
                )
                == "PASS",

            "explicitScope":
                fields.get(
                    "COMMAND_SCOPE_EXPLICIT"
                )
                == "PASS",

            "argvAllowlist":
                fields.get(
                    "ARGV_ALLOWLIST"
                )
                == "PASS",

            "cwdScope":
                fields.get(
                    "CWD_SCOPE"
                )
                == "PASS",

            "realCommand":
                fields.get(
                    "REAL_COMMAND_EXECUTED"
                )
                == "PASS",

            "expectedResult":
                fields.get(
                    "EXPECTED_RESULT_OBSERVED"
                )
                == "PASS",

            "unallowlistedRejected":
                fields.get(
                    "UNALLOWLISTED_COMMAND_REJECTED"
                )
                == "PASS",

            "cwdEscapeRejected":
                fields.get(
                    "CWD_ESCAPE_REJECTED"
                )
                == "PASS",

            "nonzeroHeld":
                fields.get(
                    "NONZERO_EXIT_HELD"
                )
                == "PASS",

            "failurePath":
                fields.get(
                    "FAILURE_PATH_TESTED"
                )
                == "PASS",

            "rollback":
                fields.get(
                    "ROLLBACK"
                )
                == "PASS",

            "rollbackParity":
                fields.get(
                    "ROLLBACK_BYTE_PARITY"
                )
                == "PASS",

            "freshReverify":
                fields.get(
                    "FRESH_REVERIFY"
                )
                == "PASS",

            "finalRollback":
                fields.get(
                    "FINAL_ROLLBACK"
                )
                == "PASS",

            "networkFalse":
                fields.get(
                    "NETWORK_ACCESS"
                )
                == "false",

            "remotePushFalse":
                fields.get(
                    "REMOTE_PUSH"
                )
                == "false",

            "humanThresholdFalse":
                fields.get(
                    "HUMAN_THRESHOLD_REQUIRED"
                )
                == "false",

            "canonicalMutationFalse":
                fields.get(
                    "CANONICAL_SOURCE_MUTATION"
                )
                == "false",

            "productMutationFalse":
                fields.get(
                    "PRODUCT_MUTATION"
                )
                == "false",

            "authorityCreatedFalse":
                fields.get(
                    "EXECUTION_AUTHORITY_CREATED"
                )
                == "false",

            "canonicalTruth":
                fields.get(
                    "CANONICAL_TRUTH_PRESERVED"
                )
                == "PASS",

            "falsePassZero":
                fields.get(
                    "CRITICAL_FALSE_PASS_COUNT"
                )
                == "0",

            "runtimeEvidencePresent":
                bool(
                    result.get(
                        "evidence"
                    )
                ),
        }

        recovery_observed = bool(
            observed[
                "rollback"
            ]
            and observed[
                "rollbackParity"
            ]
            and observed[
                "finalRollback"
            ]
        )

        mutation_scope = {
            "filesystemMutationExpected":
                True,

            "scope":
                "COMMAND_SCOPE_EXPLICIT",

            "humanThresholdRequired":
                False,

            "recoveryProofRequired":
                True,

            "rollbackRequired":
                True,

            "shellInterpolationAllowed":
                False,

            "canonicalSourceMutationAllowed":
                False,

            "productMutationAllowed":
                False,

            "remoteMutationAllowed":
                False,

            "canonicalTruthPreserved":
                True,
        }


    execution_state = (
        "PASS"
        if all(observed.values())
        else "HOLD"
    )

    runtime_evidence = result.get(
        "evidence"
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
            binding[
                "REGISTERED_HANDLER"
            ],

        "AUTHORITY":
            binding["AUTHORITY"],

        "NETWORK_POLICY": {
            "allowed":
                expected_network_required,

            "contractNetworkRequired":
                contract.get(
                    "networkRequired"
                ),
        },

        "REMOTE_PUSH_POLICY": {
            "allowed":
                False,

            "observedRemotePushFalse":
                observed[
                    "remotePushFalse"
                ],
        },

        "MUTATION_SCOPE":
            mutation_scope,

        "REGISTERED_HANDLER_INVOKED":
            True,

        "EXECUTION_PERFORMED":
            True,

        "RECOVERY_PROOF_REQUIRED":
            bool(
                binding.get(
                    "RECOVERY_PROOF_REQUIRED",
                    False,
                )
            ),

        "RECOVERY_PROOF_OBSERVED":
            recovery_observed,

        "OBSERVED_RESULT":
            observed,

        "RESULT":
            result,

        "EVIDENCE": {
            "bindingRegistry":
                str(
                    BINDING_REGISTRY
                    .relative_to(ROOT)
                ),

            "capabilityRegistry":
                str(
                    CAPABILITY_REGISTRY
                    .relative_to(ROOT)
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
                is expected_network_required,

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
