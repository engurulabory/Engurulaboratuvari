#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ACCEPTANCE = (
    ROOT
    / "governance/mac-engineer/"
      "V11_JEV_PROVIDER_QUALIFICATION_ACCEPTANCE_V1.json"
)

REQUIRED_CRITERIA = (
    "PROVIDER_TRUTH_VERIFIED",
    "LIVE_TRANSPORT_VERIFIED",
    "SCHEMA_PROVENANCE_BOUND",
    "LIVE_100_STATE_BENCHMARK",
    "CALIBRATION_EVIDENCE",
    "LATENCY_EVIDENCE",
    "COST_EVIDENCE",
    "TRANSPORT_RESILIENCE",
    "AUTHORITY_REGRESSION",
    "DETERMINISTIC_CONTINUITY",
)


def evaluate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))

    issues: list[str] = []

    if data.get("accessExpected") is not True:
        issues.append("JEV_ACCESS_EXPECTED_REQUIRED")

    if data.get("integrationDirection") != "FORWARD":
        issues.append("JEV_INTEGRATION_DIRECTION_FORWARD_REQUIRED")

    if data.get("role") != "OPTIONAL_BOUNDED_ASSESSOR":
        issues.append("JEV_ROLE_MISMATCH")

    if data.get("assessorOnly") is not True:
        issues.append("JEV_ASSESSOR_ONLY_REQUIRED")

    if data.get("deterministicContinuityRequired") is not True:
        issues.append("DETERMINISTIC_CONTINUITY_REQUIRED")

    if data.get("v13MandatoryDependency") is not False:
        issues.append("V13_MANDATORY_DEPENDENCY_MUST_BE_FALSE")

    if data.get("vercelCanonical") is not False:
        issues.append("VERCEL_MUST_REMAIN_NON_CANONICAL")

    if data.get("newCore") is not False:
        issues.append("NEW_CORE_MUST_REMAIN_FALSE")

    benchmark = data.get("benchmark", {})

    if benchmark.get("expectedCases") != 100:
        issues.append("BENCHMARK_EXPECTED_CASES_MUST_BE_100")

    if benchmark.get("fixtureDigestRequired") is not True:
        issues.append("BENCHMARK_FIXTURE_DIGEST_REQUIRED")

    thresholds = data.get("thresholds", {})

    if thresholds.get("canonicalAgreementMin") != 0.95:
        issues.append("CANONICAL_AGREEMENT_THRESHOLD_MISMATCH")

    if thresholds.get("criticalFalsePassMax") != 0:
        issues.append("CRITICAL_FALSE_PASS_THRESHOLD_MISMATCH")

    if thresholds.get("humanThresholdMissMax") != 0:
        issues.append("HUMAN_THRESHOLD_MISS_THRESHOLD_MISMATCH")

    if thresholds.get("latencyImprovementFactorTarget") != 0.75:
        issues.append("LATENCY_TARGET_MISMATCH")

    if thresholds.get("costImprovementFactorTarget") != 0.75:
        issues.append("COST_TARGET_MISMATCH")

    retry_max = thresholds.get("maxRetryAttempts")

    if not isinstance(retry_max, int) or retry_max > 2:
        issues.append("RETRY_BUDGET_EXCEEDS_CONTRACT")

    if thresholds.get("calibrationMethodDeclaredRequired") is not True:
        issues.append("CALIBRATION_METHOD_REQUIRED")

    if thresholds.get("calibrationEvidenceRequired") is not True:
        issues.append("CALIBRATION_EVIDENCE_REQUIRED")

    criteria = data.get("criteria", {})

    for name in REQUIRED_CRITERIA:
        criterion = criteria.get(name)

        if not isinstance(criterion, dict):
            issues.append(f"CRITERION_MISSING:{name}")
            continue

        if criterion.get("state") != "PASS":
            issues.append(f"CRITERION_NOT_PASS:{name}")
            continue

        evidence = criterion.get("evidence")

        if not isinstance(evidence, str) or not evidence.strip():
            issues.append(f"EVIDENCE_REQUIRED:{name}")

    state = "PASS" if not issues else "HOLD"

    return {
        "state": state,
        "claim": (
            "JEV_PROVIDER_QUALIFICATION_PASS"
            if state == "PASS"
            else "JEV_PROVIDER_QUALIFICATION_EVIDENCE_PENDING"
        ),
        "accessExpected": data.get("accessExpected"),
        "integrationDirection": data.get("integrationDirection"),
        "currentProviderEvidenceState":
            data.get("currentProviderEvidenceState"),
        "criteriaCount": len(REQUIRED_CRITERIA),
        "v13MandatoryDependency":
            data.get("v13MandatoryDependency"),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--acceptance",
        default=str(DEFAULT_ACCEPTANCE),
    )
    args = parser.parse_args()

    result = evaluate(Path(args.acceptance))

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if result["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
