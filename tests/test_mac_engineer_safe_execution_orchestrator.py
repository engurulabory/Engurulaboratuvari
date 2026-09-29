#!/usr/bin/env python3

from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_intent_plan_router as router
import mac_engineer_safe_execution_orchestrator as orch


checks: list[tuple[str, bool]] = []


def check(name: str, value: bool) -> None:
    checks.append((name, value))
    print(name + "=" + ("PASS" if value else "HOLD"))


existing_plan = router.route("mevcut ürünü güncelle")
existing_before = copy.deepcopy(existing_plan)
existing = orch.dry_run(existing_plan)

check(
    "SOURCE_CHANGE_BUILD_BOUND_REMAINING_PLAN_HOLD",
    existing["STATE"] == "HOLD"
    and existing["STEP_COUNT"] == 4
    and existing["EXECUTABLE_STEP_COUNT"] == 2
    and existing["HOLD_STEP_COUNT"] == 2
    and existing["STEPS"][0]["CAPABILITY_ID"]
        == "SOURCE_PRODUCT_CHANGE"
    and existing["STEPS"][0]["BINDING_TYPE"]
        == "REGISTERED_ACTION"
    and existing["STEPS"][0]["DRY_RUN_EXECUTABLE"]
        is True
    and existing["STEPS"][1]["CAPABILITY_ID"]
        == "BUILD"
    and existing["STEPS"][1]["BINDING_TYPE"]
        == "REGISTERED_ACTION"
    and existing["STEPS"][1]["DRY_RUN_EXECUTABLE"]
        is True
    and all(
        step["DRY_RUN_EXECUTABLE"] is False
        for step in existing["STEPS"][2:]
    ),
)

check(
    "NO_EXECUTION_SIDE_EFFECTS",
    existing["EXECUTION_PERFORMED"] is False
    and existing["NETWORK_ACCESS_PERFORMED"] is False
    and existing["FILESYSTEM_MUTATION_PERFORMED"] is False
    and existing["REGISTERED_HANDLER_INVOKED"] is False,
)

check(
    "PLAN_IMMUTABLE",
    existing_plan == existing_before,
)

check(
    "STEP_EVIDENCE_PRESENT",
    all(
        isinstance(step.get("EVIDENCE"), dict)
        and step["EVIDENCE"].get("DRY_RUN_ONLY") is True
        and step["EVIDENCE"].get("EXECUTION_PERFORMED") is False
        for step in existing["STEPS"]
    ),
)

truth_plan = router.route("mevcut teknik hakikati oku")
truth = orch.dry_run(truth_plan)

check(
    "CURRENT_TRUTH_PLAN_FAILS_CLOSED_ON_UNBOUND_BOOT",
    truth["STATE"] == "HOLD"
    and truth["STEP_COUNT"] == 3
    and truth["EXECUTABLE_STEP_COUNT"] == 2
    and truth["HOLD_STEP_COUNT"] == 1
    and truth["EXECUTION_PERFORMED"] is False
    and truth["STEPS"][0]["CAPABILITY_ID"]
        == "CURRENT_TECHNICAL_TRUTH_READ"
    and truth["STEPS"][0]["DRY_RUN_EXECUTABLE"] is True
    and truth["STEPS"][1]["CAPABILITY_ID"]
        == "CANONICAL_BOOT"
    and truth["STEPS"][1]["DRY_RUN_EXECUTABLE"] is False
    and truth["STEPS"][2]["CAPABILITY_ID"]
        == "LOCAL_DOCTOR"
    and truth["STEPS"][2]["DRY_RUN_EXECUTABLE"] is True,
)

release_plan = router.route("ürünü yayınla")
release = orch.dry_run(release_plan)

ht_steps = [
    step
    for step in release.get("STEPS", [])
    if step.get("REQUIRES_HUMAN_THRESHOLD") is True
]

check(
    "HT_REQUIRED_FAIL_CLOSED",
    release["STATE"] == "HOLD"
    and len(ht_steps) >= 1
    and all(
        step["DRY_RUN_EXECUTABLE"] is False
        and step["HOLD_REASON"]
            == "HUMAN_THRESHOLD_REQUIRED"
        for step in ht_steps
    ),
)

tampered = copy.deepcopy(existing_plan)
tampered["EXECUTION_AUTHORIZED"] = True

check(
    "PACKAGE04_AUTHORITY_VIOLATION_HOLD",
    orch.dry_run(tampered)["HOLD_REASON"]
        == "PACKAGE04_EXECUTION_AUTHORITY_VIOLATION",
)

unknown = copy.deepcopy(existing_plan)
unknown["CAPABILITY_PLAN"] = ["INVENTED_CAPABILITY"]

check(
    "UNKNOWN_CAPABILITY_HOLD",
    orch.dry_run(unknown)["HOLD_REASON"]
        == "UNKNOWN_CAPABILITY",
)

again = orch.dry_run(existing_plan)

check(
    "DRY_RUN_DETERMINISTIC",
    again["DRY_RUN_DIGEST"]
        == existing["DRY_RUN_DIGEST"],
)


plan_bound = orch.execute_plan_step(
    truth_plan,
    1,
)

check(
    "PLAN_BOUND_STEP1_PASS",
    plan_bound["STATE"] == "PASS"
    and plan_bound["CAPABILITY_ID"]
        == "CURRENT_TECHNICAL_TRUTH_READ"
    and plan_bound["PLAN_ID"]
        == truth_plan["PLAN_ID"]
    and plan_bound["TRUTH_FINGERPRINT"]
        == truth_plan["TRUTH_FINGERPRINT"]
    and plan_bound["STEP_INDEX"] == 1
    and plan_bound["PLAN_IMMUTABLE"] is True
    and plan_bound["EXECUTION_PERFORMED"] is True
    and plan_bound["NETWORK_ACCESS_PERFORMED"] is False
    and plan_bound[
        "FILESYSTEM_MUTATION_PERFORMED"
    ] is False
    and bool(
        plan_bound.get("STEP_EVIDENCE_DIGEST")
    ),
)

plan_bound_step2 = orch.execute_plan_step(
    truth_plan,
    2,
)

check(
    "PLAN_BOUND_UNPROVEN_STEP_HOLD",
    plan_bound_step2["STATE"] == "HOLD"
    and plan_bound_step2[
        "EXECUTION_PERFORMED"
    ] is False,
)

import mac_engineer_operator as operator

_real_product_doctor = operator.product_doctor

operator.product_doctor = lambda: {
    "verdict": "PASS",
    "checks": [
        {
            "name": "synthetic_local",
            "scope": "LOCAL",
            "status": "PASS",
            "evidence": "PACKAGE05_TEST",
        }
    ],
    "online_capabilities": "HOLD",
}

try:
    doctor_bound = orch.execute_plan_step(
        truth_plan,
        3,
    )
finally:
    operator.product_doctor = _real_product_doctor

check(
    "PLAN_BOUND_LOCAL_DOCTOR_PASS",
    doctor_bound["STATE"] == "PASS"
    and doctor_bound["CAPABILITY_ID"] == "LOCAL_DOCTOR"
    and doctor_bound["PLAN_ID"]
        == truth_plan["PLAN_ID"]
    and doctor_bound["TRUTH_FINGERPRINT"]
        == truth_plan["TRUTH_FINGERPRINT"]
    and doctor_bound["STEP_INDEX"] == 3
    and doctor_bound["PLAN_IMMUTABLE"] is True
    and doctor_bound["EXECUTION_PERFORMED"] is True
    and doctor_bound["NETWORK_ACCESS_ALLOWED"] is True
    and doctor_bound["NETWORK_ACCESS_PERFORMED"] is True
    and doctor_bound[
        "FILESYSTEM_MUTATION_PERFORMED"
    ] is False
    and bool(
        doctor_bound.get("STEP_EVIDENCE_DIGEST")
    ),
)

registered_plan = {
    "STATE": "PLAN_READY",
    "PLAN_ID": "package05-cap04-registered-action-test",
    "TRUTH_FINGERPRINT": "package05-cap04-test-truth",
    "EXECUTION_AUTHORIZED": False,
    "CAPABILITY_PLAN": [
        "OPERATOR_CONTINUE_DISPATCH",
    ],
}

_real_restart = (
    operator
    .run_mac_native_restart_recovery_proof
)

operator.run_mac_native_restart_recovery_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE": "PASS",
        "PROCESS_RESTART": "PASS",
        "TASK_IDENTITY": "PASS",
        "CHECKPOINT_RESUME": "PASS",
        "EXACTLY_ONCE_EFFECT": "PASS",
        "FINAL_STATE": "COMPLETE",
        "GITVAULT_MIRROR_UNCHANGED": "PASS",
        "REMOTE_PUSH": "false",
    },
    "evidence": "/tmp/package05-cap04-recovery-evidence.json",
}

try:
    registered_bound = orch.execute_plan_step(
        registered_plan,
        1,
    )
finally:
    operator.run_mac_native_restart_recovery_proof = (
        _real_restart
    )

check(
    "PLAN_BOUND_REGISTERED_ACTION_PASS",
    registered_bound["STATE"] == "PASS"
    and registered_bound["CAPABILITY_ID"]
        == "OPERATOR_CONTINUE_DISPATCH"
    and registered_bound["BINDING_TYPE"]
        == "REGISTERED_ACTION"
    and registered_bound["ACTION"]
        == "MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF"
    and registered_bound["REGISTERED_HANDLER_INVOKED"]
        is True
    and registered_bound["EXECUTION_PERFORMED"]
        is True
    and registered_bound[
        "RECOVERY_PROOF_OBSERVED"
    ] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["processRestartPass"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["taskIdentityPass"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["checkpointResumePass"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["exactlyOnceEffectPass"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["finalStateComplete"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["gitVaultMirrorUnchanged"] is True
    and registered_bound[
        "OBSERVED_RESULT"
    ]["remotePushFalse"] is True
    and registered_bound[
        "MUTATION_SCOPE"
    ]["filesystemMutationExpected"] is True
    and registered_bound[
        "MUTATION_SCOPE"
    ]["canonicalSourceMutationAllowed"] is False
    and bool(
        registered_bound.get(
            "STEP_EVIDENCE_DIGEST"
        )
    ),
)


cap06_plan = {
    "STATE":
        "PLAN_READY",

    "PLAN_ID":
        "package05-cap06-registered-action-test",

    "TRUTH_FINGERPRINT":
        "package05-cap06-test-truth",

    "EXECUTION_AUTHORIZED":
        False,

    "CAPABILITY_PLAN": [
        "SOURCE_PRODUCT_CHANGE",
    ],
}

_real_cap06 = (
    operator
    .run_package08_cap06_disposable_source_change_field_proof
)

operator.run_package08_cap06_disposable_source_change_field_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE": "PASS",
        "CAP06_SOURCE_CHANGE": "PASS",
        "AUTHORIZED_PATH_COUNT": "2",
        "SOURCE_CONTRACT": "PASS",
        "REGRESSION": "PASS",
        "ROLLBACK": "PASS",
        "ROLLBACK_BYTE_PARITY": "PASS",
        "ROLLBACK_WORKTREE_CLEAN": "PASS",
        "FAILURE_PATH": "PASS",
        "CANONICAL_CONTROL_UNCHANGED": "PASS",
        "CANONICAL_PRODUCT_UNCHANGED": "PASS",
        "REMOTE_PUSH": "false",
        "NETWORK_REQUIRED": "false",
        "EXECUTION_AUTHORITY_CREATED": "false",
    },
    "evidence":
        "/tmp/package05-cap06-source-change-evidence.json",
}

try:
    cap06_registered = (
        orch.execute_plan_step(
            cap06_plan,
            1,
        )
    )
finally:
    operator.run_package08_cap06_disposable_source_change_field_proof = (
        _real_cap06
    )

check(
    "PLAN_BOUND_CAP06_REGISTERED_ACTION_PASS",

    cap06_registered["STATE"]
    == "PASS"

    and cap06_registered[
        "CAPABILITY_ID"
    ]
    == "SOURCE_PRODUCT_CHANGE"

    and cap06_registered[
        "BINDING_TYPE"
    ]
    == "REGISTERED_ACTION"

    and cap06_registered[
        "REGISTERED_HANDLER_INVOKED"
    ]
    is True

    and cap06_registered[
        "EXECUTION_PERFORMED"
    ]
    is True

    and cap06_registered[
        "RECOVERY_PROOF_OBSERVED"
    ]
    is True

    and cap06_registered[
        "OBSERVED_RESULT"
    ]["authorizedPathCountTwo"]
    is True

    and cap06_registered[
        "OBSERVED_RESULT"
    ]["regressionPass"]
    is True

    and cap06_registered[
        "OBSERVED_RESULT"
    ]["rollbackPass"]
    is True

    and cap06_registered[
        "OBSERVED_RESULT"
    ]["failurePathPass"]
    is True

    and cap06_registered[
        "OBSERVED_RESULT"
    ]["canonicalProductUnchanged"]
    is True

    and cap06_registered[
        "MUTATION_SCOPE"
    ]["authorizedPathCount"]
    == 2

    and cap06_registered[
        "MUTATION_SCOPE"
    ]["canonicalSourceMutationAllowed"]
    is False
)

operator.run_package08_cap06_disposable_source_change_field_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE": "PASS",
        "CAP06_SOURCE_CHANGE": "PASS",
        "AUTHORIZED_PATH_COUNT": "2",
        "SOURCE_CONTRACT": "PASS",
        "REGRESSION": "PASS",
        "ROLLBACK": "HOLD",
        "ROLLBACK_BYTE_PARITY": "HOLD",
        "ROLLBACK_WORKTREE_CLEAN": "HOLD",
        "FAILURE_PATH": "PASS",
        "CANONICAL_CONTROL_UNCHANGED": "PASS",
        "CANONICAL_PRODUCT_UNCHANGED": "PASS",
        "REMOTE_PUSH": "false",
        "NETWORK_REQUIRED": "false",
        "EXECUTION_AUTHORITY_CREATED": "false",
    },
    "evidence":
        "/tmp/package05-cap06-incomplete-rollback.json",
}

try:
    cap06_incomplete_rollback = (
        orch.execute_plan_step(
            cap06_plan,
            1,
        )
    )
finally:
    operator.run_package08_cap06_disposable_source_change_field_proof = (
        _real_cap06
    )

check(
    "CAP06_REGISTERED_ACTION_INCOMPLETE_ROLLBACK_HOLD",

    cap06_incomplete_rollback[
        "STATE"
    ]
    == "HOLD"

    and cap06_incomplete_rollback[
        "HOLD_REASON"
    ]
    == "REGISTERED_ACTION_RESULT_CONTRACT_HOLD"

    and cap06_incomplete_rollback[
        "RECOVERY_PROOF_OBSERVED"
    ]
    is False
)


_binding_path = orch.BINDING_REGISTRY
_original_binding_doc = orch.load_json(
    _binding_path
)

_tampered_binding_doc = (
    __import__("copy").deepcopy(
        _original_binding_doc
    )
)

_cap04_binding = next(
    row
    for row in _tampered_binding_doc["bindings"]
    if row["CAPABILITY_ID"]
    == "OPERATOR_CONTINUE_DISPATCH"
)

_cap04_binding["ACTION"] = (
    "UNREGISTERED_SYNTHETIC_ACTION"
)

_real_load_json = orch.load_json

def _tampered_load_json(path):
    if path == orch.BINDING_REGISTRY:
        return _tampered_binding_doc
    return _real_load_json(path)

orch.load_json = _tampered_load_json

try:
    tampered_registered = (
        orch.execute_plan_step(
            registered_plan,
            1,
        )
    )
finally:
    orch.load_json = _real_load_json

check(
    "REGISTERED_ACTION_TAMPER_FAIL_CLOSED",
    tampered_registered["STATE"] == "HOLD"
    and tampered_registered[
        "EXECUTION_PERFORMED"
    ] is False,
)

_real_restart = (
    operator
    .run_mac_native_restart_recovery_proof
)

operator.run_mac_native_restart_recovery_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE": "PASS",
        "PROCESS_RESTART": "PASS",
        "TASK_IDENTITY": "PASS",
        "CHECKPOINT_RESUME": "PASS",
        "EXACTLY_ONCE_EFFECT": "HOLD",
        "FINAL_STATE": "COMPLETE",
        "GITVAULT_MIRROR_UNCHANGED": "PASS",
        "REMOTE_PUSH": "false",
    },
    "evidence": "/tmp/package05-invalid-recovery-evidence.json",
}

try:
    incomplete_recovery = (
        orch.execute_plan_step(
            registered_plan,
            1,
        )
    )
finally:
    operator.run_mac_native_restart_recovery_proof = (
        _real_restart
    )

check(
    "REGISTERED_ACTION_INCOMPLETE_RECOVERY_HOLD",
    incomplete_recovery["STATE"] == "HOLD"
    and incomplete_recovery["HOLD_REASON"]
        == "REGISTERED_ACTION_RESULT_CONTRACT_HOLD"
    and incomplete_recovery[
        "RECOVERY_PROOF_OBSERVED"
    ] is False,
)



build_plan = {
    "STATE":
        "PLAN_READY",

    "PLAN_ID":
        "package05-cap07-build-test",

    "TRUTH_FINGERPRINT":
        "package05-cap07-build-truth",

    "EXECUTION_AUTHORIZED":
        False,

    "CAPABILITY_PLAN": [
        "BUILD",
    ],
}

_real_build = (
    operator
    .run_package08_cap07_build_field_proof
)

operator.run_package08_cap07_build_field_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE":
            "PASS",

        "CAP07_BUILD":
            "PASS",

        "BUILD_ARTIFACT_EXECUTABLE":
            "PASS",

        "BUILD_ARTIFACT_SHA256":
            "a" * 64,

        "CONTROLLED_COMPILER_REJECTION":
            "PASS",

        "FAILED_ARTIFACT_CLEANUP":
            "PASS",

        "CANONICAL_TRUTH_PRESERVED":
            "PASS",

        "AUTHORITY":
            "GREEN",

        "NETWORK_POLICY":
            "LOCAL_ONLY",

        "MUTATION_SCOPE":
            "BUILD_ARTIFACTS_ONLY",

        "REMOTE_PUSH":
            "false",

        "EXECUTION_AUTHORITY_CREATED":
            "false",
    },
    "evidence":
        "/tmp/package05-cap07-build-evidence.json",
}

try:
    cap07_build = (
        orch.execute_plan_step(
            build_plan,
            1,
        )
    )
finally:
    operator.run_package08_cap07_build_field_proof = (
        _real_build
    )

check(
    "PLAN_BOUND_CAP07_BUILD_REGISTERED_ACTION_PASS",

    cap07_build["STATE"]
    == "PASS"

    and cap07_build[
        "CAPABILITY_ID"
    ]
    == "BUILD"

    and cap07_build[
        "BINDING_TYPE"
    ]
    == "REGISTERED_ACTION"

    and cap07_build[
        "REGISTERED_HANDLER_INVOKED"
    ]
    is True

    and cap07_build[
        "EXECUTION_PERFORMED"
    ]
    is True

    and cap07_build[
        "RECOVERY_PROOF_REQUIRED"
    ]
    is False

    and cap07_build[
        "OBSERVED_RESULT"
    ]["buildPass"]
    is True

    and cap07_build[
        "OBSERVED_RESULT"
    ]["artifactExecutable"]
    is True

    and cap07_build[
        "OBSERVED_RESULT"
    ]["artifactIdentityPresent"]
    is True

    and cap07_build[
        "OBSERVED_RESULT"
    ]["controlledCompilerRejection"]
    is True

    and cap07_build[
        "OBSERVED_RESULT"
    ]["canonicalTruthPreserved"]
    is True

    and cap07_build[
        "MUTATION_SCOPE"
    ]["scope"]
    == "BUILD_ARTIFACTS_ONLY"
)

operator.run_package08_cap07_build_field_proof = lambda: {
    "state": "PASS",
    "code": 0,
    "fields": {
        "STATE":
            "PASS",

        "CAP07_BUILD":
            "PASS",

        "BUILD_ARTIFACT_EXECUTABLE":
            "PASS",

        "BUILD_ARTIFACT_SHA256":
            "a" * 64,

        "CONTROLLED_COMPILER_REJECTION":
            "HOLD",

        "FAILED_ARTIFACT_CLEANUP":
            "PASS",

        "CANONICAL_TRUTH_PRESERVED":
            "PASS",

        "AUTHORITY":
            "GREEN",

        "NETWORK_POLICY":
            "LOCAL_ONLY",

        "MUTATION_SCOPE":
            "BUILD_ARTIFACTS_ONLY",

        "REMOTE_PUSH":
            "false",

        "EXECUTION_AUTHORITY_CREATED":
            "false",
    },
    "evidence":
        "/tmp/package05-cap07-build-negative.json",
}

try:
    cap07_failure_path_hold = (
        orch.execute_plan_step(
            build_plan,
            1,
        )
    )
finally:
    operator.run_package08_cap07_build_field_proof = (
        _real_build
    )

check(
    "CAP07_BUILD_FAILURE_PATH_REQUIRED_HOLD",

    cap07_failure_path_hold[
        "STATE"
    ]
    == "HOLD"

    and cap07_failure_path_hold[
        "HOLD_REASON"
    ]
    == "REGISTERED_ACTION_RESULT_CONTRACT_HOLD"
)


invalid_step = orch.execute_plan_step(
    truth_plan,
    99,
)

check(
    "INVALID_PLAN_STEP_HOLD",
    invalid_step["STATE"] == "HOLD"
    and invalid_step["HOLD_REASON"]
        == "PLAN_STEP_INDEX_INVALID",
)

binding_doc = orch.load_json(
    orch.BINDING_REGISTRY
)

direct_bindings = [
    row
    for row in binding_doc["bindings"]
    if row["BINDING_TYPE"] == "DIRECT_RUNTIME"
]

hold_bindings = [
    row
    for row in binding_doc["bindings"]
    if row["BINDING_TYPE"] == "HOLD_UNBOUND"
]

registered_bindings = [
    row
    for row in binding_doc["bindings"]
    if row["BINDING_TYPE"] == "REGISTERED_ACTION"
]

direct_ids = {
    row["CAPABILITY_ID"]
    for row in direct_bindings
}

check(
    "TWO_PROVEN_DIRECT_BINDINGS",
    len(direct_bindings) == 2
    and direct_ids == {
        "CURRENT_TECHNICAL_TRUTH_READ",
        "LOCAL_DOCTOR",
    }
    and all(
        row["READ_ONLY_CONFIRMED"] is True
        for row in direct_bindings
    ),
)

check(
    "THREE_PROVEN_REGISTERED_ACTION_BINDINGS",
    len(registered_bindings) == 3
    and {
        row["CAPABILITY_ID"]
        for row in registered_bindings
    }
    == {
        "OPERATOR_CONTINUE_DISPATCH",
        "SOURCE_PRODUCT_CHANGE",
        "BUILD",
    },
)

check(
    "FOURTEEN_UNBOUND_FAIL_CLOSED",
    len(hold_bindings) == 14,
)


passed = sum(1 for _, ok in checks if ok)

print(
    "TESTS="
    + str(passed)
    + "_OF_"
    + str(len(checks))
    + "_PASS"
)

if passed != len(checks):
    print("STATE=HOLD")
    print("CLAIM=PACKAGE05_DRY_RUN_REGRESSION_FAILED")
    raise SystemExit(20)

print("STATE=PASS")
print("CLAIM=PACKAGE05_DRY_RUN_REGRESSION_PASS")
