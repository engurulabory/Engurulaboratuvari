#!/usr/bin/env python3
"""ENGÜRÜ Capability & Agent Authority Gate™ — fail-closed evaluator."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LEVEL = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
CRITICAL_BLAST = {"production", "financial", "public", "legal"}
SCHEMA = Path(__file__).resolve().parents[1] / "governance/ip-model-trust/CAPABILITY_AGENT_AUTHORITY.schema.json"


def verdict(state: str, reason: str, next_action: str, **extra) -> dict:
    return {"state": state, "reason": reason, "nextAction": next_action,
            "decisionScope": "DECLARED_CONTRACT_POLICY",
            "officialVerifiedFinish": "HOLD_CANONICAL_DONECHECK_HUMAN_THRESHOLD", **extra}


def schema_error(value, rule, path="$"):
    """Validate the keyword subset used by the existing canonical v0.1 schema."""
    types = {"object": dict, "array": list, "string": str, "boolean": bool,
             "integer": int, "null": type(None)}
    expected = rule.get("type")
    if expected is not None:
        expected = expected if isinstance(expected, list) else [expected]
        if not any(type(value) is types.get(name) for name in expected):
            return path
    if "const" in rule and (type(value) is not type(rule["const"]) or value != rule["const"]):
        return path
    if "enum" in rule and value not in rule["enum"]:
        return path
    if type(value) is dict:
        properties = rule.get("properties", {})
        if any(key not in value for key in rule.get("required", [])):
            return path
        if rule.get("additionalProperties") is False and set(value) - properties.keys():
            return path
        for key, child in value.items():
            if key in properties:
                error = schema_error(child, properties[key], path + "." + key)
                if error:
                    return error
    if type(value) is list:
        if len(value) < rule.get("minItems", 0):
            return path
        for index, child in enumerate(value):
            error = schema_error(child, rule.get("items", {}), f"{path}[{index}]")
            if error:
                return error
        if rule.get("uniqueItems") and any(child in value[:i] for i, child in enumerate(value)):
            return path
    if type(value) is str and len(value) < rule.get("minLength", 0):
        return path
    if type(value) is int and "minimum" in rule and value < rule["minimum"]:
        return path
    return None


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate contract field")
    return result


def evaluate(contract: dict) -> dict:
    if type(contract) is not dict:
        return verdict("BLOCKED", "INVALID_CONTRACT_SHAPE", "Provide a JSON contract object.")
    required = {
        "schemaVersion","actor","task","capabilities","authority","delegation",
        "credentials","risk","verification","humanThreshold","finalState"
    }
    missing = sorted(required - contract.keys())
    if missing:
        return verdict("BLOCKED","CONTRACT_MISSING_FIELDS","Complete the machine-readable contract.",missing=missing)
    if contract.get("schemaVersion") != "0.1":
        return verdict("BLOCKED","UNKNOWN_CONTRACT_VERSION","Use schemaVersion 0.1.")

    # Preserve the existing explicit policy-violation reason codes. All other
    # schema/type checks precede semantic evaluation and truth-value decisions.
    for section, field, reason in (
        ("delegation", "transferableAuthority", "TRANSITIVE_AUTHORITY_ATTEMPT"),
        ("credentials", "inheritance", "CREDENTIAL_INHERITANCE_ATTEMPT"),
    ):
        if type(contract[section]) is dict and contract[section].get(field) is True:
            return verdict("BLOCKED", reason, "Use independent minimum-scope authority and credentials.")
    try:
        error = schema_error(contract, json.loads(SCHEMA.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, RecursionError):
        return verdict("BLOCKED", "CANONICAL_SCHEMA_UNAVAILABLE", "Restore the canonical contract schema.")
    if error:
        return verdict("BLOCKED", "CONTRACT_SCHEMA_VIOLATION", "Provide the canonical field types and scope.", field=error)

    actor = contract["actor"]
    authority = contract["authority"]
    capabilities = contract["capabilities"]
    delegation = contract["delegation"]
    credentials = contract["credentials"]
    risk = contract["risk"]
    verification = contract["verification"]
    human = contract["humanThreshold"]
    autonomy = contract.get("autonomyWindow")
    self_mod = contract.get("selfModification", {"requested": False, "touchesGovernance": False})

    try:
        actor_level = LEVEL[actor["authorityLevel"]]
        requested_level = LEVEL[authority["requestedLevel"]]
        policy_ceiling = LEVEL[authority["policyCeiling"]]
    except (KeyError, TypeError):
        return verdict("BLOCKED","INVALID_AUTHORITY_LEVEL","Use L0-L5 authority levels.")

    if requested_level > policy_ceiling:
        return verdict("BLOCKED","AUTHORITY_SCOPE_VIOLATION","Reduce requested authority to the policy ceiling.")

    detected = set(capabilities["detected"])
    forbidden = detected.intersection(authority["forbiddenActions"])
    if forbidden:
        return verdict("BLOCKED", "AUTHORITY_SCOPE_VIOLATION", "Use actions within the explicit grant scope.",
                       forbiddenActions=sorted(forbidden))

    if requested_level > actor_level and not authority.get("explicitGrant", False):
        return verdict("HOLD","CAPABILITY_ESCALATION_UNAPPROVED","Obtain an explicit authority grant before escalation.")

    unapproved = sorted(set(capabilities.get("detected", [])) - set(capabilities.get("approved", [])))
    if unapproved:
        return verdict("HOLD","CAPABILITY_ESCALATION_UNAPPROVED","Classify and explicitly approve or deny the new capability.",unapprovedCapabilities=unapproved)

    outside_scope = detected - set(authority["allowedActions"])
    if outside_scope:
        return verdict("BLOCKED", "AUTHORITY_SCOPE_VIOLATION", "Use actions within the explicit grant scope.",
                       outsideAllowedActions=sorted(outside_scope))

    if delegation.get("transferableAuthority", False):
        return verdict("BLOCKED","TRANSITIVE_AUTHORITY_ATTEMPT","Delegated actors require independent least-authority grants.")

    depth = delegation.get("depth", 0)
    max_depth = delegation.get("maxDepth", 0)
    if depth > max_depth:
        return verdict("BLOCKED","DELEGATION_DEPTH_EXCEEDED","Reduce delegation depth to the declared maximum.")
    if depth > 0 and not delegation.get("allowed", False):
        return verdict("BLOCKED","UNAPPROVED_DELEGATION","Obtain explicit delegation authority.")

    if credentials.get("inheritance", False):
        return verdict("BLOCKED","CREDENTIAL_INHERITANCE_ATTEMPT","Issue only minimum-scope, explicit credentials to the delegated actor.")

    if self_mod.get("requested", False) and self_mod.get("touchesGovernance", False):
        return verdict("BLOCKED","GOVERNANCE_BYPASS_ATTEMPT","Route governance mutation to external Human Threshold authority.")

    if autonomy is not None:
        if not autonomy.get("active", False) or autonomy.get("remainingActions", 0) <= 0:
            return verdict("BLOCKED","AUTONOMY_WINDOW_EXPIRED","Stop execution and request a new bounded autonomy window.")

    critical = (
        risk.get("blastRadius") in CRITICAL_BLAST
        or not risk.get("reversible", True)
        or risk.get("financial", False)
        or risk.get("legal", False)
    )
    if critical and not human.get("required", False):
        return verdict("HOLD","HUMAN_THRESHOLD_REQUIRED","Declare and satisfy Human Threshold for critical or irreversible action.")
    if human.get("required", False) and not human.get("approved", False):
        return verdict("HOLD","IRREVERSIBLE_ACTION_UNAPPROVED","Obtain explicit Human Threshold approval.")

    if verification.get("independentVerifierRequired", False) and verification.get("actorIsFinalVerifier", False):
        return verdict("HOLD","EVIDENCE_BYPASS_ATTEMPT","Use an independent verifier before Verified Finish.")
    if not verification["evidenceRefs"] or any(not ref.strip() for ref in verification["evidenceRefs"]):
        return verdict("HOLD","EVIDENCE_REQUIRED","Attach verifiable evidence before PASS.")

    return verdict(
        "PASS",
        "WITHIN_AUTHORITY_AND_POLICY",
        "Proceed within the declared scope; retain the decision envelope as evidence."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="ENGÜRÜ Capability & Agent Authority Gate™")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        result = evaluate(contract)
    except (OSError, UnicodeError, ValueError, RecursionError):
        result = verdict("BLOCKED", "CONTRACT_INPUT_UNREADABLE", "Provide a readable UTF-8 JSON contract.")
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        except OSError:
            result = verdict("BLOCKED", "EVIDENCE_OUTPUT_UNWRITABLE", "Provide a writable evidence output path.")
            rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    return {"PASS": 0, "HOLD": 2, "BLOCKED": 3}[result["state"]]


if __name__ == "__main__":
    sys.exit(main())
