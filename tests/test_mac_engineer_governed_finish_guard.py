#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_governed_finish_guard as guard


checks = []


def check(name, condition):
    checks.append(bool(condition))
    print(
        name
        + "="
        + ("PASS" if condition else "HOLD")
    )


verified = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="PASS",
    ht_required=False,
    human_decision=None,
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=True,
)

check(
    "GREEN_VERIFIED_FINISH",
    verified["STATE"] == "VERIFIED",
)

missing_evidence = guard.evaluate_finish(
    material_evidence_present=False,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="PASS",
    ht_required=False,
    human_decision=None,
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=True,
)

check(
    "MISSING_EVIDENCE_HOLD",
    missing_evidence["STATE"] == "HOLD",
)

stale = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=False,
    cached_pass_used=True,
    donecheck_state="PASS",
    ht_required=False,
    human_decision=None,
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=True,
)

check(
    "STALE_CACHED_PASS_HOLD",
    stale["STATE"] == "HOLD",
)

donecheck_fail = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="HOLD",
    ht_required=False,
    human_decision=None,
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=True,
)

check(
    "DONECHECK_NONPASS_HOLD",
    donecheck_fail["STATE"] == "HOLD",
)

ht_missing = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="PASS",
    ht_required=True,
    human_decision=None,
    execution_identity_bound=False,
    donecheck_identity_bound=False,
    supported_final_claim=True,
)

check(
    "HT_REQUIRED_MISSING_HOLD",
    ht_missing["STATE"] == "HOLD",
)

ht_accept = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="PASS",
    ht_required=True,
    human_decision="ACCEPT",
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=True,
)

check(
    "HT_ACCEPT_BOUND_VERIFIED",
    ht_accept["STATE"] == "VERIFIED",
)

unsupported = guard.evaluate_finish(
    material_evidence_present=True,
    fresh_verification=True,
    cached_pass_used=False,
    donecheck_state="PASS",
    ht_required=False,
    human_decision=None,
    execution_identity_bound=True,
    donecheck_identity_bound=True,
    supported_final_claim=False,
)

check(
    "UNSUPPORTED_FINAL_CLAIM_HOLD",
    unsupported["STATE"] == "HOLD",
)

passed = sum(checks)

print(
    "TESTS="
    + str(passed)
    + "_OF_"
    + str(len(checks))
    + "_PASS"
)

if passed != len(checks):
    raise SystemExit(20)

print("STATE=PASS")
print(
    "CLAIM=PACKAGE07_GOVERNED_FINISH_NATIVE_REGRESSION_PASS"
)
