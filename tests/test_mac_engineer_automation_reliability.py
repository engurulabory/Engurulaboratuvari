#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_automation_reliability_guard as guard


checks = []


def check(name, condition):
    checks.append(bool(condition))
    print(
        name
        + "="
        + ("PASS" if condition else "HOLD")
    )


x1 = guard.execution_id(
    "plan-1",
    "truth-1",
    1,
    "CURRENT_TECHNICAL_TRUTH_READ",
)

x2 = guard.execution_id(
    "plan-1",
    "truth-1",
    1,
    "CURRENT_TECHNICAL_TRUTH_READ",
)

x3 = guard.execution_id(
    "plan-1",
    "truth-2",
    1,
    "CURRENT_TECHNICAL_TRUTH_READ",
)

check(
    "IDENTITY_STABLE",
    x1 == x2,
)

check(
    "IDENTITY_TRUTH_SENSITIVE",
    x1 != x3,
)

check(
    "RETRY_MAX1_PARITY",
    guard.retry_limit_from_max_attempts(1)
    == 0,
)

check(
    "RETRY_MAX2_PARITY",
    guard.retry_limit_from_max_attempts(2)
    == 1,
)

try:
    guard.retry_limit_from_max_attempts(3)
    rejected = False
except ValueError:
    rejected = True

check(
    "RETRY_MAX3_REJECTED",
    rejected,
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
    "CLAIM=PACKAGE06_RELIABILITY_ADAPTER_NATIVE_TEST_PASS"
)

print("\n=== RUNTIME RELIABILITY ACCEPTANCE ===")

import tempfile
import mac_engineer_automation_reliability_adapter as adapter


class RetryableProbe(Exception):
    pass


# Bounded retry: Package06 maxAttempts=2 must mean
# exactly 2 total attempts, never 3.
with tempfile.TemporaryDirectory(
    prefix="enguru-p06-native-retry-"
) as root:

    manager = adapter.ReliabilityManager(root)

    started = manager.begin(
        "P06-NATIVE-RETRY"
    )

    task_id = started["task"]["task_id"]

    manager.transition(
        task_id,
        "RUNNING",
    )

    attempts = []

    def operation(attempt):
        attempts.append(attempt)
        raise RetryableProbe("CONTROLLED")

    retry_limit = (
        adapter.retry_limit_from_max_attempts(2)
    )

    result = manager.bounded_retry(
        task_id,
        operation,
        failure_kind="P06_NATIVE_RETRY",
        retry_exceptions=RetryableProbe,
        retry_limit=retry_limit,
    )

    check(
        "BOUNDED_RETRY_EXACT_TWO_ATTEMPTS",
        attempts == [1, 2]
        and result.get("max_attempts") == 2
        and result.get("reason") == "retry_exhausted",
    )


# Deterministic terminal HOLD persistence.
with tempfile.TemporaryDirectory(
    prefix="enguru-p06-native-terminal-"
) as root:

    manager = adapter.ReliabilityManager(root)

    started = manager.begin(
        "P06-NATIVE-HOLD"
    )

    task_id = started["task"]["task_id"]

    manager.transition(
        task_id,
        "RUNNING",
    )

    hold = manager.transition(
        task_id,
        "HOLD",
        note="CONTROLLED_NATIVE_HOLD",
    )

    check(
        "TERMINAL_HOLD_PERSISTED",
        hold["state"] == "HOLD"
        and manager.get(task_id)["state"] == "HOLD",
    )


# Verified LKG supplies recovery basis.
with tempfile.TemporaryDirectory(
    prefix="enguru-p06-native-lkg-"
) as root:

    manager = adapter.ReliabilityManager(root)

    started = manager.begin(
        "P06-NATIVE-LKG"
    )

    task_id = started["task"]["task_id"]

    manager.transition(
        task_id,
        "RUNNING",
    )

    checkpoint = manager.checkpoint(
        task_id,
        {
            "phase": "KNOWN_GOOD",
            "value": "KNOWN_GOOD",
        },
        verified=True,
    )

    manager.resume(task_id)

    manager.transition(
        task_id,
        "ROLLBACK_REQUIRED",
        recovery_class="ROLLBACK_REQUIRED",
        note="CONTROLLED_NATIVE_FAILURE",
    )

    rollback = manager.rollback_to_lkg(
        task_id
    )

    check(
        "VERIFIED_LKG_RECOVERY_BASIS",
        checkpoint.get("verified") is True
        and rollback.get("ok") is True,
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
    "CLAIM=PACKAGE06_AUTOMATION_RELIABILITY_NATIVE_REGRESSION_PASS"
)
