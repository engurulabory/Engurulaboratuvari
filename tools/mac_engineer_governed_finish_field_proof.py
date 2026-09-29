#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_governed_finish_adapter as adapter


P06 = (
    Path.home()
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "package06-automation-reliability"
    / "final-20260929T112642Z"
    / "evidence.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


if not P06.is_file():
    raise SystemExit(
        "PACKAGE06_EVIDENCE_MISSING"
    )

execution_id = (
    "package07:"
    + sha(P06)[:32]
)

task_id = (
    "enguru-package07-"
    + sha(P06)[:16]
)

machine = (
    adapter.verify_machine_finish(
        evidence_path=P06,
        execution_id=execution_id,
        task_id=task_id,
        criterion_id="PACKAGE06_RELIABILITY",
        statement=
            "Package 06 Automation Reliability acceptance is PASS",
    )
)

print(
    "DONECHECK_STATE="
    + machine["DONECHECK_STATE"]
)

print(
    "DONECHECK_VERSION="
    + machine["DONECHECK_VERSION"]
)

print(
    "DONECHECK_SHA="
    + machine["DONECHECK_SHA"]
)

criteria = (
    machine["RAW_RESULT"].get(
        "criteria"
    )
    or []
)

print(
    "CRITERION_OUTCOME="
    + str(
        criteria[0].get("outcome")
        if criteria
        else None
    )
)

print(
    "AGGREGATE_OUTCOME="
    + str(
        machine["RAW_RESULT"].get(
            "aggregateOutcome"
        )
        or machine["RAW_RESULT"].get(
            "outcome"
        )
    )
)

green = (
    adapter.evaluate_green_finish(
        machine
    )
)

print(
    "GREEN_FINAL_STATE="
    + green["STATE"]
)

ht_missing = (
    adapter.evaluate_ht_missing(
        machine
    )
)

print(
    "HT_MISSING_STATE="
    + ht_missing["STATE"]
)

checks = {
    "REAL_DONECHECK_PASS":
        machine["DONECHECK_STATE"]
        == "PASS",

    "PINNED_DONECHECK_VERSION":
        machine["DONECHECK_VERSION"]
        == "1.2.0",

    "PINNED_DONECHECK_SHA":
        machine["DONECHECK_SHA"]
        == "8b90a8fc93453dd8a84994195d28d14b15e261cb",

    "GREEN_FINISH_VERIFIED":
        green["STATE"]
        == "VERIFIED",

    "HT_REQUIRED_WITHOUT_DECISION_HOLD":
        ht_missing["STATE"]
        == "HOLD",
}

for name, ok in checks.items():
    print(
        name
        + "="
        + ("PASS" if ok else "HOLD")
    )

passed = sum(
    1
    for ok in checks.values()
    if ok
)

print(
    "CHECKS="
    + str(passed)
    + "_OF_"
    + str(len(checks))
    + "_PASS"
)

if passed != len(checks):
    print(
        json.dumps(
            machine["RAW_RESULT"],
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(20)

print("STATE=PASS")
print(
    "CLAIM=PACKAGE07_REAL_DONECHECK_GREEN_AND_HT_HOLD_FIELD_PROOF_PASS"
)
