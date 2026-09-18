#!/usr/bin/env python3
"""ENGÜRÜ Shared AI Infrastructure™ static foundation gate.

This gate validates architecture contracts only.
It MUST NOT claim runtime/provider Verified Finish.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path.cwd()

REQUIRED = [
    "governance/shared-ai/ARCHITECTURE.md",
    "governance/shared-ai/SERVICE_CONTRACT.yaml",
    "governance/shared-ai/POLICY.rego",
    "governance/shared-ai/PROVIDERS.yaml",
    "governance/shared-ai/CAPABILITIES.yaml",
    "governance/shared-ai/ROUTING.yaml",
    "governance/shared-ai/EVIDENCE.schema.json",
    "governance/shared-ai/ACCEPTANCE.yaml",
]

REQUIRED_ARCH_TOKENS = [
    "The system may optimize itself; it may not expand its own authority.",
    "Zero-Cost Guard",
    "Local fallback",
    "Result Verifier",
    "Evidence Ledger",
    "Model Intelligence",
]

REQUIRED_POLICY_TOKENS = [
    "default allow := false",
    'default verdict := "BLOCKED"',
    "secret_local_only",
    "cost_allowed",
    "capabilities_allowed",
    "authority_allowed",
]

REQUIRED_ROUTING_TOKENS = [
    "hard_constraints_first: true",
    "zero_cost_default: true",
    "local_final_fallback: true",
    "automatic_authority_expansion: false",
    "re_evaluate_policy: true",
]

REQUIRED_ACCEPTANCE_TOKENS = [
    "single_interface",
    "policy_fail_closed",
    "zero_cost_guard",
    "secret_boundary",
    "learning_boundary",
    "human_threshold",
    "offline_testability",
    "optional_openai",
]

def fail(findings):
    print(json.dumps({
        "gate": "ENGURU_SHARED_AI_FOUNDATION_GATE_V0_1",
        "state": "BLOCKED",
        "findings": findings,
        "runtimeVerifiedFinish": "HOLD",
    }, ensure_ascii=False, indent=2))
    return 3

def main() -> int:
    findings = []

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            findings.append({"code": "MISSING_REQUIRED_PATH", "path": path})
    if findings:
        return fail(findings)

    arch = (ROOT / REQUIRED[0]).read_text(encoding="utf-8")
    policy = (ROOT / REQUIRED[2]).read_text(encoding="utf-8")
    providers = (ROOT / REQUIRED[3]).read_text(encoding="utf-8")
    capabilities = (ROOT / REQUIRED[4]).read_text(encoding="utf-8")
    routing = (ROOT / REQUIRED[5]).read_text(encoding="utf-8")
    acceptance = (ROOT / REQUIRED[7]).read_text(encoding="utf-8")

    for token in REQUIRED_ARCH_TOKENS:
        if token not in arch:
            findings.append({"code": "ARCHITECTURE_INVARIANT_MISSING", "token": token})
    for token in REQUIRED_POLICY_TOKENS:
        if token not in policy:
            findings.append({"code": "POLICY_FAIL_CLOSED_INVARIANT_MISSING", "token": token})
    for token in REQUIRED_ROUTING_TOKENS:
        if token not in routing:
            findings.append({"code": "ROUTING_INVARIANT_MISSING", "token": token})
    for token in REQUIRED_ACCEPTANCE_TOKENS:
        if token not in acceptance:
            findings.append({"code": "ACCEPTANCE_GATE_MISSING", "token": token})

    for token in [
        "openai:",
        "role: OPTIONAL",
        "OpenAI API is not required",
        "paid_without_explicit_authority: BLOCKED",
        "secret_external_egress: BLOCKED",
    ]:
        if token not in providers:
            findings.append({"code": "PROVIDER_BOUNDARY_MISSING", "token": token})

    for token in [
        "promotion_rule:",
        "No model enters APPROVED/ACTIVE from automated discovery alone.",
        "human_threshold_required:",
    ]:
        if token not in capabilities:
            findings.append({"code": "MODEL_LIFECYCLE_BOUNDARY_MISSING", "token": token})

    evidence = json.loads((ROOT / REQUIRED[6]).read_text(encoding="utf-8"))
    required_evidence = set(evidence.get("required", []))
    expected_evidence = {
        "requestId", "timestamp", "taskType", "dataClass", "policyVerdict",
        "provider", "model", "attempts", "estimatedCost",
        "verificationState", "finalState",
    }
    if required_evidence != expected_evidence:
        findings.append({
            "code": "EVIDENCE_REQUIRED_SET_DRIFT",
            "expected": sorted(expected_evidence),
            "actual": sorted(required_evidence),
        })
    if evidence.get("properties", {}).get("secretMaterialStored", {}).get("const") is not False:
        findings.append({"code": "SECRET_EVIDENCE_BOUNDARY_MISSING"})

    product_map = json.loads((ROOT / "governance/ENGURU_PRODUCT_CORE_MAP_V2.json").read_text(encoding="utf-8"))
    truth = json.loads((ROOT / "governance/ENGURU_SYSTEM_TRUTH_V1.json").read_text(encoding="utf-8"))

    shared_map = {x.get("asset"): x for x in product_map.get("sharedInfrastructure", [])}
    shared_truth = {x.get("asset"): x for x in truth.get("sharedInfrastructure", [])}
    name = "ENGÜRÜ Shared AI Infrastructure™"
    if name not in shared_map:
        findings.append({"code": "PRODUCT_CORE_MAP_REGISTRATION_MISSING"})
    if name not in shared_truth:
        findings.append({"code": "SYSTEM_TRUTH_REGISTRATION_MISSING"})
    if name not in product_map.get("currentTopology", {}).get("sharedOperatingArchitecture", []):
        findings.append({"code": "TOPOLOGY_REGISTRATION_MISSING_MAP"})
    if name not in truth.get("currentTopology", {}).get("sharedOperatingArchitecture", []):
        findings.append({"code": "TOPOLOGY_REGISTRATION_MISSING_TRUTH"})

    if findings:
        return fail(findings)

    print(json.dumps({
        "gate": "ENGURU_SHARED_AI_FOUNDATION_GATE_V0_1",
        "state": "PASS",
        "architectureTarget": 100,
        "staticContracts": len(REQUIRED),
        "providerIndependence": "PASS",
        "openAIRequirement": "OPTIONAL",
        "zeroCostGuard": "PASS",
        "privacyFailClosed": "PASS",
        "controlledSelfOptimization": "PASS",
        "evidenceContract": "PASS",
        "laboryRegistration": "PASS",
        "runtimeVerifiedFinish": "HOLD"
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
