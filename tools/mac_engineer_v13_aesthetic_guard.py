#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACCEPTANCE = (
    ROOT
    / "governance/mac-engineer/"
      "V13_AESTHETIC_MOTOR_ACCEPTANCE_V1.json"
)

CONTRACT = (
    ROOT
    / "governance/mac-engineer/"
      "V13_AESTHETIC_MOTOR_CANONICAL_NECESSARY_DIFFERENCE_CONTRACT_V1.md"
)

ROADMAP = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"

REQUIRED = {
    "VISUAL_PROVIDER_RUNTIME_COMMISSIONED",
    "REAL_LOCAL_VISUAL_GENERATION",
    "REAL_IMAGE_EDITING",
    "REFERENCE_IMAGE_EXECUTION",
    "LOCAL_MODEL_QUALIFICATION",
    "LOCAL_PROVENANCE_PERSISTENCE_RESOURCE_EVIDENCE",
    "LOCAL_EXTERNAL_API_ZERO_COST_EVIDENCE",
    "COST_AWARE_CREATIVE_SEARCH",
    "QUALITY_ESCALATION_ROUTER",
    "AESTHETIC_STUDIO_MAC_ENGINEER_BINDING",
    "WORLD_CLASS_BLIND_BENCHMARK",
    "HUMAN_ARTISTIC_AUTHORITY",
}

def main() -> int:
    issues = []

    for path in (
        ACCEPTANCE,
        CONTRACT,
        ROADMAP,
    ):
        if not path.is_file():
            issues.append(
                "MISSING:"
                + str(path.relative_to(ROOT))
            )

    if issues:
        print(json.dumps({
            "state": "HOLD",
            "claim": "V13_AESTHETIC_MOTOR_PASS_GUARD",
            "issues": issues,
        }, ensure_ascii=False, indent=2))
        return 2

    acceptance = json.loads(
        ACCEPTANCE.read_text(encoding="utf-8")
    )

    roadmap = json.loads(
        ROADMAP.read_text(encoding="utf-8")
    )

    if acceptance.get("requiredVerdict") != (
        "V13_AESTHETIC_MOTOR_VERIFIED_FINISH"
    ):
        issues.append("REQUIRED_VERDICT_MISMATCH")

    criteria = acceptance.get("criteria", {})

    if set(criteria) != REQUIRED:
        issues.append("REQUIRED_CRITERIA_SET_MISMATCH")

    for name in sorted(REQUIRED):
        item = criteria.get(name, {})

        if item.get("state") != "PASS":
            issues.append(
                "CRITERION_NOT_PASS:" + name
            )

        evidence = item.get("evidence")

        if (
            not isinstance(evidence, list)
            or not evidence
        ):
            issues.append(
                "EVIDENCE_REQUIRED:" + name
            )

    final_target = roadmap.get("finalTarget", {})

    if final_target.get("version") != "v1.3":
        issues.append("FINAL_TARGET_NOT_V13")

    if "V13_AESTHETIC_MOTOR_VERIFIED_FINISH" not in (
        final_target.get("requiredPreconditions", [])
    ):
        issues.append(
            "V13_PRECONDITION_NOT_BOUND_TO_FINAL_TARGET"
        )

    v13 = next(
        (
            item
            for item in roadmap.get("versions", [])
            if item.get("version") == "v1.3"
        ),
        None,
    )

    if not v13:
        issues.append("V13_ROADMAP_ENTRY_MISSING")

    elif "V13_AESTHETIC_MOTOR_VERIFIED_FINISH" not in (
        v13.get("exit", [])
    ):
        issues.append("V13_AESTHETIC_EXIT_MISSING")

    state = "HOLD" if issues else "PASS"

    claim = (
        "V13_AESTHETIC_MOTOR_PASS_GUARD_HOLD"
        if issues
        else "V13_AESTHETIC_MOTOR_VERIFIED_FINISH"
    )

    print(json.dumps({
        "state": state,
        "claim": claim,
        "criteriaCount": len(REQUIRED),
        "issues": issues,
    }, ensure_ascii=False, indent=2))

    return 2 if issues else 0

if __name__ == "__main__":
    raise SystemExit(main())
