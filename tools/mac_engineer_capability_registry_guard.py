#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED = [
    ("CURRENT_TECHNICAL_TRUTH_READ", "CURRENT TECHNICAL TRUTH READ"),
    ("CANONICAL_BOOT", "CANONICAL BOOT"),
    ("LOCAL_DOCTOR", "LOCAL DOCTOR"),
    ("OPERATOR_CONTINUE_DISPATCH", "OPERATOR CONTINUE / NEXT ACTION DISPATCH"),
    ("FAIL_CLOSED_ENGINEERING", "FAIL-CLOSED ENGINEERING"),
    ("SOURCE_PRODUCT_CHANGE", "SOURCE / PRODUCT CHANGE"),
    ("BUILD", "BUILD"),
    ("TEST_REGRESSION", "TEST / REGRESSION"),
    ("ROOT_CAUSE_REPAIR", "ROOT-CAUSE REPAIR"),
    ("MIGRATION_CANONICAL_RECONCILIATION", "MIGRATION / CANONICAL RECONCILIATION"),
    ("ADVANCED_CODE_ENGINEERING", "ADVANCED CODE ENGINEERING"),
    ("NEW_PRODUCT_FROM_BRIEF", "NEW PRODUCT FROM BRIEF"),
    ("RELEASE_LIFECYCLE", "RELEASE LIFECYCLE"),
    ("FINISHED_PRODUCT_DELIVERY_ACCEPTANCE", "FINISHED PRODUCT DELIVERY ACCEPTANCE"),
    ("EVIDENCE_DONECHECK", "EVIDENCE / DONECHECK™"),
    ("RECOVERY_OFFLINE_CONTINUITY", "RECOVERY / OFFLINE CONTINUITY"),
    ("TERMINAL_EXECUTION", "TERMINAL / SHELL EXECUTION"),
    ("FILESYSTEM_MACOS_AUTOMATION", "FILESYSTEM / FINDER / MACOS AUTOMATION"),
    ("INTERNET_RESEARCH_HARVEST_ASTRA", "INTERNET RESEARCH / HARVEST / LOCAL ASTRA"),
]

REQUIRED_FIELDS = {
    "CAPABILITY_ID", "STATE", "INPUTS", "OUTPUTS", "PRECONDITIONS",
    "AUTHORITY", "RISK_CLASS", "MUTATION_SCOPE", "NETWORK_POLICY",
    "REQUIRES_HUMAN_THRESHOLD", "RETRY_POLICY", "ROLLBACK_POLICY",
    "EVIDENCE_REQUIREMENTS", "NEXT_COMPATIBLE_CAPABILITIES", "FAIL_CLOSED",
}

ALLOWED_STATES = {"VERIFIED", "VERIFIED_BOUNDED", "PARTIAL", "FIELD_TEST_REQUIRED"}
ALLOWED_AUTHORITY = {"GREEN", "AMBER", "RED"}
ALLOWED_RISK = {"LOW", "MEDIUM", "HIGH"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(registry: Path, schema: Path, inventory: Path) -> list[str]:
    errors: list[str] = []
    r = load(registry)
    s = load(schema)
    inv = inventory.read_text(encoding="utf-8")

    if r.get("schema") != "enguru.mac-engineer.capability-registry/v1":
        errors.append("REGISTRY_SCHEMA_ID_MISMATCH")
    if r.get("product") != "ENGÜRÜ Mac Engineer™":
        errors.append("REGISTRY_PRODUCT_MISMATCH")

    caps = r.get("capabilities")
    if not isinstance(caps, list):
        return errors + ["CAPABILITIES_NOT_LIST"]

    ids = [x.get("CAPABILITY_ID") for x in caps if isinstance(x, dict)]
    expected_ids = [x[0] for x in EXPECTED]

    if len(caps) != 19:
        errors.append(f"CAPABILITY_COUNT_{len(caps)}")
    if len(set(ids)) != len(ids):
        errors.append("DUPLICATE_CAPABILITY_ID")
    if ids != expected_ids:
        errors.append("CAPABILITY_ID_ORDER_OR_COVERAGE_MISMATCH")

    for idx, cap in enumerate(caps, start=1):
        if not isinstance(cap, dict):
            errors.append(f"C{idx:02d}_NOT_OBJECT")
            continue
        missing = REQUIRED_FIELDS - set(cap)
        if missing:
            errors.append(f"C{idx:02d}_MISSING_FIELDS:{','.join(sorted(missing))}")
        if cap.get("STATE") not in ALLOWED_STATES:
            errors.append(f"C{idx:02d}_UNKNOWN_STATE")
        if cap.get("AUTHORITY") not in ALLOWED_AUTHORITY:
            errors.append(f"C{idx:02d}_UNKNOWN_AUTHORITY")
        if cap.get("RISK_CLASS") not in ALLOWED_RISK:
            errors.append(f"C{idx:02d}_UNKNOWN_RISK")
        if cap.get("FAIL_CLOSED") is not True:
            errors.append(f"C{idx:02d}_FAIL_CLOSED_FALSE")
        retry = cap.get("RETRY_POLICY")
        if not isinstance(retry, dict):
            errors.append(f"C{idx:02d}_RETRY_POLICY_INVALID")
        else:
            if retry.get("maxAttempts", 999) > 2:
                errors.append(f"C{idx:02d}_RETRY_LIMIT_EXCEEDED")
            if retry.get("overLimit") != "HOLD":
                errors.append(f"C{idx:02d}_OVER_LIMIT_NOT_HOLD")
        if cap.get("NEXT_COMPATIBLE_CAPABILITIES") != []:
            errors.append(f"C{idx:02d}_PACKAGE03_GRAPH_PREAUTHORIZED")
        if cap.get("AUTHORITY") in {"AMBER", "RED"} and cap.get("ROLLBACK_POLICY") != "REQUIRED":
            errors.append(f"C{idx:02d}_ROLLBACK_REQUIRED")

    headings = re.findall(r"^##\s+(\d+)\.\s+(.+)$", inv, re.M)
    expected_headings = [(str(i), title) for i, (_, title) in enumerate(EXPECTED, start=1)]
    if headings != expected_headings:
        errors.append("INVENTORY_REGISTRY_PARITY_MISMATCH")

    required_top = {"schema", "product", "rule", "defaults", "capabilities"}
    if set(s.get("required", [])) != required_top:
        errors.append("SCHEMA_TOP_REQUIRED_MISMATCH")

    item_schema = (
        s.get("properties", {})
         .get("capabilities", {})
         .get("items", {})
    )
    if set(item_schema.get("required", [])) != REQUIRED_FIELDS:
        errors.append("SCHEMA_CAPABILITY_REQUIRED_MISMATCH")
    if item_schema.get("additionalProperties") is not False:
        errors.append("SCHEMA_CAPABILITY_ADDITIONAL_PROPERTIES_NOT_FALSE")

    schema_caps = s.get("properties", {}).get("capabilities", {})
    if schema_caps.get("minItems") != 19 or schema_caps.get("maxItems") != 19:
        errors.append("SCHEMA_CAPABILITY_COUNT_NOT_EXACT_19")

    props = item_schema.get("properties", {})
    if set(props.get("STATE", {}).get("enum", [])) != ALLOWED_STATES:
        errors.append("SCHEMA_STATE_ENUM_MISMATCH")
    if set(props.get("AUTHORITY", {}).get("enum", [])) != ALLOWED_AUTHORITY:
        errors.append("SCHEMA_AUTHORITY_ENUM_MISMATCH")
    if props.get("FAIL_CLOSED", {}).get("const") is not True:
        errors.append("SCHEMA_FAIL_CLOSED_NOT_CONST_TRUE")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=root / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.json")
    ap.add_argument("--schema", type=Path, default=root / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.schema.json")
    ap.add_argument("--inventory", type=Path, default=root / "governance/mac-engineer/CURRENT_PROVEN_CAPABILITY_INVENTORY_V1.md")
    args = ap.parse_args()

    try:
        errors = validate(args.registry, args.schema, args.inventory)
    except Exception as exc:
        print("STATE=HOLD")
        print(f"REASON=REGISTRY_GUARD_EXCEPTION:{type(exc).__name__}:{exc}")
        return 30

    if errors:
        print("STATE=HOLD")
        print("CLAIM=CAPABILITY_REGISTRY_GUARD_REJECTED")
        for error in errors:
            print(f"ERROR={error}")
        return 20

    print("STATE=PASS")
    print("CLAIM=CAPABILITY_REGISTRY_NATIVE_GUARD_PASS")
    print("CAPABILITY_COUNT=19")
    print("INVENTORY_PARITY=19_OF_19")
    print("DUPLICATE_COUNT=0")
    print("UNKNOWN_STATE_COUNT=0")
    print("UNKNOWN_AUTHORITY_COUNT=0")
    print("FAIL_CLOSED_FALSE_COUNT=0")
    print("RETRY_LIMIT_VIOLATION_COUNT=0")
    print("PACKAGE03_GRAPH_PREAUTHORIZATION=0")
    print("SCHEMA_CONTRACT_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
