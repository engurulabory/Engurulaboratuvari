#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "AUTOMATION_RELIABILITY_ADAPTER_V1.json"
)

REGISTRY = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "CAPABILITY_REGISTRY_V1.json"
)

ORCHESTRATOR = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "SAFE_EXECUTION_ORCHESTRATOR_V1.json"
)


def load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def execution_id(
    plan_id: str,
    truth_fingerprint: str,
    step_index: int,
    capability_id: str,
) -> str:

    raw = "|".join(
        [
            plan_id,
            truth_fingerprint,
            str(step_index),
            capability_id,
        ]
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def retry_limit_from_max_attempts(
    max_attempts: int,
) -> int:

    if not isinstance(max_attempts, int):
        raise ValueError("MAX_ATTEMPTS_NOT_INT")

    if max_attempts < 1:
        raise ValueError(
            "MAX_ATTEMPTS_BELOW_MINIMUM"
        )

    if max_attempts > 2:
        raise ValueError(
            "MAX_ATTEMPTS_EXCEEDS_CONTRACT"
        )

    return max_attempts - 1


def main() -> int:
    contract = load(CONTRACT)
    registry = load(REGISTRY)
    orchestrator = load(ORCHESTRATOR)

    checks = {}

    checks["NO_NEW_CORE"] = (
        contract["newCoreIntroduced"] is False
    )

    checks["REUSE_RELIABILITY_MANAGER"] = (
        contract["reuse"]["manager"]
        == "ReliabilityManager"
    )

    checks["IDENTITY_COMPONENTS_EXACT"] = (
        contract["executionIdentity"]["components"]
        == [
            "PLAN_ID",
            "TRUTH_FINGERPRINT",
            "STEP_INDEX",
            "CAPABILITY_ID",
        ]
    )

    a = execution_id(
        "plan-a",
        "truth-a",
        1,
        "CURRENT_TECHNICAL_TRUTH_READ",
    )

    b = execution_id(
        "plan-a",
        "truth-a",
        1,
        "CURRENT_TECHNICAL_TRUTH_READ",
    )

    c = execution_id(
        "plan-a",
        "truth-b",
        1,
        "CURRENT_TECHNICAL_TRUTH_READ",
    )

    checks["EXECUTION_ID_DETERMINISTIC"] = (
        a == b
    )

    checks["TRUTH_DRIFT_CHANGES_ID"] = (
        a != c
    )

    checks["STALE_RESUME_HOLD"] = (
        contract["staleState"][
            "staleCheckpointMayAuthorizeResume"
        ] is False
        and contract["staleState"][
            "mismatchPolicy"
        ] == "HOLD"
    )

    checks["RETRY_1_TO_0"] = (
        retry_limit_from_max_attempts(1)
        == 0
    )

    checks["RETRY_2_TO_1"] = (
        retry_limit_from_max_attempts(2)
        == 1
    )

    try:
        retry_limit_from_max_attempts(3)
        over_limit_rejected = False
    except ValueError:
        over_limit_rejected = True

    checks["RETRY_OVER_LIMIT_HOLD"] = (
        over_limit_rejected
    )

    checks["ORCHESTRATOR_MAX_ATTEMPTS_2"] = (
        orchestrator["retryPolicy"][
            "maximumAllowedAttempts"
        ] == 2
    )

    checks["REGISTRY_ALL_MAX_ATTEMPTS_2"] = (
        all(
            row["RETRY_POLICY"][
                "maxAttempts"
            ] == 2
            and row["RETRY_POLICY"][
                "overLimit"
            ] == "HOLD"
            for row in registry["capabilities"]
        )
    )

    checks["DUPLICATE_REPLAY_DISABLED"] = (
        contract["idempotency"][
            "duplicateEffectReplayAllowed"
        ] is False
    )

    checks["SINGLE_WRITER_REQUIRED"] = (
        contract["singleWriter"][
            "requiredForMaterialStateMutation"
        ] is True
    )

    checks["PLAN_SELECTION_DISABLED"] = (
        contract["package05Boundary"][
            "planSelectionAllowed"
        ] is False
    )

    checks["PLAN_MUTATION_DISABLED"] = (
        contract["package05Boundary"][
            "planMutationAllowed"
        ] is False
    )

    checks["AUTHORITY_EXPANSION_DISABLED"] = (
        contract["package05Boundary"][
            "executionAuthorityExpansionAllowed"
        ] is False
    )

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
        print("STATE=HOLD")
        return 20

    print("STATE=PASS")
    print(
        "CLAIM=PACKAGE06_RELIABILITY_ADAPTER_CONTRACT_GUARD_PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
