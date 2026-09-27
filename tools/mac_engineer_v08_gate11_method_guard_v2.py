#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACCEPTANCE = ROOT / (
    "governance/mac-engineer/"
    "V08_GATE11_METHOD_ACCEPTANCE_V2.json"
)

MATRIX = ROOT / (
    "governance/mac-engineer/"
    "V08_GATE11_12_PACKAGE_ACCEPTANCE_MATRIX_V2.md"
)

ROLE = ROOT / (
    "governance/mac-engineer/"
    "V08_GATE11_STRENGTHENED_ROLE_CONTRACT_V2.md"
)

ROADMAP = ROOT / (
    "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
)

SESSION = ROOT / (
    "governance/mac-engineer/SESSION_STATE_V1.json"
)

GATE8_TASK = ROOT / (
    "governance/mac-engineer/"
    "V08_GATE8_LOCAL_CSV_INSPECTOR_TASK_CONTRACT_V1.json"
)

EXPECTED_IDS = [
    f"P{i:02d}"
    for i in range(1, 13)
]


def main() -> int:
    issues: list[str] = []

    for path, name in (
        (ACCEPTANCE, "ACCEPTANCE"),
        (MATRIX, "MATRIX"),
        (ROLE, "ROLE"),
        (ROADMAP, "ROADMAP"),
        (SESSION, "SESSION"),
        (GATE8_TASK, "GATE8_TASK"),
    ):
        if not path.is_file():
            issues.append(f"MISSING:{name}")

    if issues:
        print(json.dumps(
            {
                "state": "HOLD",
                "issues": issues,
            },
            indent=2,
        ))
        return 2

    data = json.loads(
        ACCEPTANCE.read_text(
            encoding="utf-8"
        )
    )

    if data.get("state") != "PREPARED_QUEUED":
        issues.append(
            "METHOD_STATE_NOT_PREPARED_QUEUED"
        )

    if data.get("executionActive") is not False:
        issues.append(
            "GATE11_EXECUTION_PREMATURELY_ACTIVE"
        )

    packages = data.get("packages", [])

    if [
        p.get("id")
        for p in packages
    ] != EXPECTED_IDS:
        issues.append(
            "PACKAGE_IDS_NOT_EXACT_P01_P12"
        )

    harvest = (
        data
        .get("historicalCapabilities", {})
        .get("researchHarvest", {})
    )

    if harvest.get("originGate") != 8:
        issues.append(
            "HARVEST_ORIGIN_GATE_NOT_8"
        )

    if harvest.get("state") != (
        "HISTORICAL_VERIFIED"
    ):
        issues.append(
            "HARVEST_HISTORY_NOT_VERIFIED"
        )

    if harvest.get(
        "gate11Action"
    ) != (
        "FRESH_RECONCILE_AND_REUSE_CLASSIFY_IN_P03"
    ):
        issues.append(
            "HARVEST_NOT_BOUND_TO_P03"
        )

    if harvest.get(
        "duplicateCapabilityCreationAllowed"
    ) is not False:
        issues.append(
            "DUPLICATE_HARVEST_CREATION_NOT_BLOCKED"
        )

    allowed = harvest.get(
        "allowedGate11Dispositions",
        [],
    )

    expected_allowed = [
        "VERIFIED_REUSABLE",
        "VERIFIED_CONTEXT_SPECIFIC",
        "FRESH_BINDING_REQUIRED",
    ]

    if allowed != expected_allowed:
        issues.append(
            "HARVEST_ALLOWED_DISPOSITIONS_CHANGED"
        )

    p03 = next(
        (
            p for p in packages
            if p.get("id") == "P03"
        ),
        {},
    )

    required_p03 = {
        "GATE8_RESEARCH_HARVEST_HISTORY_RECONCILED_PASS",
        "GATE8_VERIFIED_HARVEST_TRUTH_PRESERVED",
        "HARVEST_CAPABILITY_DISPOSITION_VALID",
        "HARVEST_CAPABILITY_REINVENTED_FALSE",
    }

    if not required_p03.issubset(
        set(p03.get("pass", []))
    ):
        issues.append(
            "P03_HARVEST_BINDING_INCOMPLETE"
        )

    p04 = next(
        (
            p for p in packages
            if p.get("id") == "P04"
        ),
        {},
    )

    if (
        "RESEARCH_HARVEST_CAPABILITY_DISPOSITION_DECLARED"
        not in p04.get("pass", [])
    ):
        issues.append(
            "P04_HARVEST_DISPOSITION_NOT_REQUIRED"
        )

    invariants = set(
        data.get(
            "globalInvariants",
            []
        )
    )

    for marker in (
        "GATE8_VERIFIED_HARVEST_TRUTH_PRESERVED=true",
        "DUPLICATE_HARVEST_CAPABILITY_CREATED=false",
        "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION=0",
    ):
        if marker not in invariants:
            issues.append(
                f"INVARIANT_MISSING:{marker}"
            )

    zeku = (
        data.get("roles", {})
        .get("zeku", {})
    )

    if zeku.get(
        "defaultCodeMode"
    ) is not False:
        issues.append(
            "ZEKU_CODE_MODE_NOT_DEFAULT_FALSE"
        )

    matrix_text = MATRIX.read_text(
        encoding="utf-8"
    )

    role_text = ROLE.read_text(
        encoding="utf-8"
    )

    for marker in (
        "Gate 11 does not reinvent Harvest.",
        "DUPLICATE_HARVEST_CAPABILITY_CREATED=false",
    ):
        if marker not in matrix_text:
            issues.append(
                f"MATRIX_MARKER_MISSING:{marker}"
            )

    for marker in (
        "Gate 8 proved the Research / Verified Harvest capability.",
        "A Terminal result does not automatically authorize a Zekü patch.",
        "RESEARCH_HARVEST_SPECIALIST_QUALIFICATION",
    ):
        if marker not in role_text:
            issues.append(
                f"ROLE_MARKER_MISSING:{marker}"
            )

    roadmap = json.loads(
        ROADMAP.read_text(
            encoding="utf-8"
        )
    )

    if roadmap.get(
        "finalTarget", {}
    ).get("version") != "v1.3":
        issues.append(
            "FINAL_TARGET_NOT_V13"
        )

    versions = {
        item.get("version"): item
        for item in roadmap.get(
            "versions", []
        )
    }

    method = (
        versions.get("v0.8", {})
        .get(
            "gate11CommissioningMethod",
            {}
        )
    )

    if method.get(
        "state"
    ) != "PREPARED_QUEUED":
        issues.append(
            "ROADMAP_METHOD_REFERENCE_MISSING"
        )

    if method.get(
        "executionActive"
    ) is not False:
        issues.append(
            "ROADMAP_GATE11_EXECUTION_ACTIVE"
        )

    if method.get(
        "harvestPreservation"
    ) is not True:
        issues.append(
            "ROADMAP_HARVEST_PRESERVATION_MISSING"
        )

    session = json.loads(
        SESSION.read_text(
            encoding="utf-8"
        )
    )

    v08 = session.get(
        "currentV08", {}
    )

    if (
        v08
        .get("closureContract", {})
        .get("activeGate")
        != 11
    ):
        issues.append(
            "CURRENT_ACTIVE_GATE_CHANGED"
        )

    if (
        v08
        .get("gate11", {})
        .get("executionStarted")
        is not False
    ):
        issues.append(
            "CURRENT_GATE11_EXECUTION_CHANGED"
        )

    prepared = session.get(
        "preparedGate11Method",
        {}
    )

    if prepared.get(
        "harvestHistoricalTruthPreserved"
    ) is not True:
        issues.append(
            "SESSION_HARVEST_PRESERVATION_MISSING"
        )

    state = (
        "PASS"
        if not issues
        else "HOLD"
    )

    print(json.dumps(
        {
            "state": state,
            "claim": (
                "V08_GATE11_METHOD_V2_PREPARED"
                if state == "PASS"
                else "V08_GATE11_METHOD_V2_HOLD"
            ),
            "packageCount":
                len(packages),
            "gate11ExecutionActive":
                data.get(
                    "executionActive"
                ),
            "harvestOriginGate":
                harvest.get(
                    "originGate"
                ),
            "harvestHistoricalState":
                harvest.get(
                    "state"
                ),
            "harvestGate11Action":
                harvest.get(
                    "gate11Action"
                ),
            "duplicateHarvestCreationAllowed":
                harvest.get(
                    "duplicateCapabilityCreationAllowed"
                ),
            "issues": issues,
        },
        ensure_ascii=False,
        indent=2,
    ))

    return (
        0
        if state == "PASS"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
