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
    "UNBOUND_EXISTING_PRODUCT_HOLD",
    existing["STATE"] == "HOLD"
    and existing["HOLD_STEP_COUNT"] == 4
    and existing["EXECUTABLE_STEP_COUNT"] == 0,
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
    "SEVENTEEN_UNBOUND_FAIL_CLOSED",
    len(hold_bindings) == 17,
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
