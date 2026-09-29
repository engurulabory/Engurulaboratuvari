#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "EVIDENCE_DONECHECK_HUMAN_THRESHOLD_BINDING_V1.json"
)

REGISTRY = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "CAPABILITY_REGISTRY_V1.json"
)


def load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def evaluate_finish(
    *,
    material_evidence_present: bool,
    fresh_verification: bool,
    cached_pass_used: bool,
    donecheck_state: str,
    ht_required: bool,
    human_decision: str | None,
    execution_identity_bound: bool,
    donecheck_identity_bound: bool,
    supported_final_claim: bool,
) -> dict[str, Any]:

    reasons = []

    if not material_evidence_present:
        reasons.append("MATERIAL_EVIDENCE_REQUIRED")

    if not fresh_verification:
        reasons.append("FRESH_VERIFICATION_REQUIRED")

    if cached_pass_used:
        reasons.append(
            "CACHED_PASS_CANNOT_AUTHORIZE_FINAL_FINISH"
        )

    if donecheck_state != "PASS":
        reasons.append("DONECHECK_PASS_REQUIRED")

    if ht_required:
        if human_decision != "ACCEPT":
            reasons.append(
                "HUMAN_THRESHOLD_ACCEPT_REQUIRED"
            )

        if not execution_identity_bound:
            reasons.append(
                "HUMAN_DECISION_EXECUTION_BINDING_REQUIRED"
            )

        if not donecheck_identity_bound:
            reasons.append(
                "HUMAN_DECISION_DONECHECK_BINDING_REQUIRED"
            )

    if not supported_final_claim:
        reasons.append(
            "UNSUPPORTED_FINAL_CLAIM"
        )

    if reasons:
        return {
            "STATE": "HOLD",
            "VERIFIED": False,
            "REASONS": reasons,
        }

    return {
        "STATE": "VERIFIED",
        "VERIFIED": True,
        "REASONS": [],
    }


def main() -> int:
    contract = load(CONTRACT)
    registry = load(REGISTRY)

    capabilities = registry["capabilities"]

    ht_rows = [
        row
        for row in capabilities
        if row.get(
            "REQUIRES_HUMAN_THRESHOLD"
        ) is True
    ]

    red_rows = [
        row
        for row in capabilities
        if row.get("AUTHORITY") == "RED"
    ]

    checks = {
        "NO_NEW_CORE":
            contract["newCoreIntroduced"] is False,

        "MATERIAL_EVIDENCE_REQUIRED":
            contract["evidence"][
                "materialStepEvidenceRequired"
            ] is True,

        "FRESH_FINISH_REQUIRED":
            contract["freshVerification"][
                "requiredForFinalFinish"
            ] is True,

        "CACHED_PASS_DISABLED":
            contract["freshVerification"][
                "cachedPassMayAuthorizeFinalFinish"
            ] is False,

        "STALE_EVIDENCE_DISABLED":
            contract["freshVerification"][
                "staleEvidenceMayAuthorizeFinalFinish"
            ] is False,

        "DONECHECK_VERSION_EXACT":
            contract["doneCheck"]["version"]
            == "1.2.0",

        "DONECHECK_SHA_EXACT":
            contract["doneCheck"]["exactSha"]
            == "8b90a8fc93453dd8a84994195d28d14b15e261cb",

        "DONECHECK_PASS_REQUIRED":
            contract["doneCheck"][
                "passRequiredForFinalFinish"
            ] is True,

        "HT_METADATA_AUTHORITATIVE":
            contract["humanThreshold"][
                "metadataAuthoritative"
            ] is True,

        "HT_BYPASS_DISABLED":
            contract["humanThreshold"][
                "bypassAllowed"
            ] is False,

        "ALL_RED_REQUIRE_HT":
            all(
                row.get(
                    "REQUIRES_HUMAN_THRESHOLD"
                ) is True
                for row in red_rows
            ),

        "HT_CAPABILITY_SET_NONEMPTY":
            len(ht_rows) > 0,

        "PLAN_SELECTION_DISABLED":
            contract["packageBoundaries"][
                "planSelectionAllowed"
            ] is False,

        "EXECUTION_AUTHORITY_NOT_EXPANDED":
            contract["packageBoundaries"][
                "executionAuthorityExpansionAllowed"
            ] is False,
    }

    for name, ok in checks.items():
        print(
            name
            + "="
            + ("PASS" if ok else "HOLD")
        )

    print(
        "HT_CAPABILITY_COUNT="
        + str(len(ht_rows))
    )

    print(
        "RED_CAPABILITY_COUNT="
        + str(len(red_rows))
    )

    passed = sum(
        1 for ok in checks.values()
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
        "CLAIM=PACKAGE07_GOVERNED_FINISH_CONTRACT_GUARD_PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
