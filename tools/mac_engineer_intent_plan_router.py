#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def evidence_path(path: Path) -> str:
    """Return repo-relative path when possible, otherwise stable absolute path."""
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)
CONTRACT = ROOT / "governance/mac-engineer/INTENT_EXECUTION_PLAN_ROUTER_V1.json"
REGISTRY = ROOT / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.json"
GRAPH = ROOT / "governance/mac-engineer/CAPABILITY_DEPENDENCY_GRAPH_V1.json"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def normalize_intent(raw: str) -> str:
    return " ".join(raw.casefold().split())

def truth_fingerprint(contract: dict, registry: dict, graph: dict) -> str:
    payload = {
        "contract": contract,
        "registry": registry,
        "graph": graph,
    }
    return sha256_bytes(canonical_bytes(payload))

def authority_rank(name: str) -> int:
    return {"GREEN": 1, "AMBER": 2, "RED": 3}.get(name, 99)

def validate_plan(plan: list[str], registry: dict, graph: dict) -> tuple[bool, str]:
    caps = {c["CAPABILITY_ID"]: c for c in registry["capabilities"]}
    forward = {(e["FROM"], e["TO"]) for e in graph["forwardEdges"]}
    controlled = set()
    for loop in graph["controlledLoops"]:
        path = loop["PATH"]
        for a, b in zip(path, path[1:]):
            controlled.add((a, b))

    unknown = [c for c in plan if c not in caps]
    if unknown:
        return False, "UNKNOWN_CAPABILITY"

    for a, b in zip(plan, plan[1:]):
        if (a, b) not in forward and (a, b) not in controlled:
            return False, "GRAPH_INCOMPATIBLE_PLAN"

    return True, "PASS"

def classify(normalized: str, contract: dict) -> list[dict]:
    matches = []
    for route in contract["intentClasses"]:
        patterns = [" ".join(p.casefold().split()) for p in route["MATCH_ANY"]]
        if any(p in normalized for p in patterns):
            matches.append(route)
    return matches

def route(intent: str) -> dict:
    contract = load(CONTRACT)
    registry = load(REGISTRY)
    graph = load(GRAPH)

    normalized = normalize_intent(intent)
    fingerprint = truth_fingerprint(contract, registry, graph)

    base = {
        "ORIGINAL_INTENT": intent,
        "NORMALIZED_INTENT": normalized,
        "TRUTH_FINGERPRINT": fingerprint,
        "EXECUTION_AUTHORIZED": False,
    }

    if not normalized:
        return {
            **base,
            "STATE": "HOLD",
            "HOLD_REASON": "EMPTY_INTENT",
            "INTENT_CLASS": None,
            "PLAN_ID": None,
            "CAPABILITY_PLAN": [],
            "MAX_AUTHORITY": None,
            "REQUIRES_HUMAN_THRESHOLD": False,
            "EVIDENCE": {
                "routerContract": evidence_path(CONTRACT),
                "registry": evidence_path(REGISTRY),
                "graph": evidence_path(GRAPH),
                "classificationCount": 0,
                "planValidated": False,
            },
        }

    matches = classify(normalized, contract)

    if len(matches) == 0:
        return {
            **base,
            "STATE": "HOLD",
            "HOLD_REASON": "UNSUPPORTED_INTENT",
            "INTENT_CLASS": None,
            "PLAN_ID": None,
            "CAPABILITY_PLAN": [],
            "MAX_AUTHORITY": None,
            "REQUIRES_HUMAN_THRESHOLD": False,
            "EVIDENCE": {
                "routerContract": evidence_path(CONTRACT),
                "registry": evidence_path(REGISTRY),
                "graph": evidence_path(GRAPH),
                "classificationCount": 0,
                "planValidated": False,
            },
        }

    if len(matches) != 1:
        return {
            **base,
            "STATE": "HOLD",
            "HOLD_REASON": "AMBIGUOUS_INTENT_CLASS",
            "INTENT_CLASS": None,
            "MATCHED_INTENT_CLASSES": sorted(x["INTENT_CLASS"] for x in matches),
            "PLAN_ID": None,
            "CAPABILITY_PLAN": [],
            "MAX_AUTHORITY": None,
            "REQUIRES_HUMAN_THRESHOLD": False,
            "EVIDENCE": {
                "routerContract": evidence_path(CONTRACT),
                "registry": evidence_path(REGISTRY),
                "graph": evidence_path(GRAPH),
                "classificationCount": len(matches),
                "planValidated": False,
            },
        }

    selected = matches[0]
    plan = list(selected["PLAN"])
    valid, reason = validate_plan(plan, registry, graph)
    if not valid:
        return {
            **base,
            "STATE": "HOLD",
            "HOLD_REASON": reason,
            "INTENT_CLASS": selected["INTENT_CLASS"],
            "PLAN_ID": None,
            "CAPABILITY_PLAN": plan,
            "MAX_AUTHORITY": None,
            "REQUIRES_HUMAN_THRESHOLD": False,
            "EVIDENCE": {
                "routerContract": evidence_path(CONTRACT),
                "registry": evidence_path(REGISTRY),
                "graph": evidence_path(GRAPH),
                "classificationCount": 1,
                "planValidated": False,
            },
        }

    caps = {c["CAPABILITY_ID"]: c for c in registry["capabilities"]}
    max_authority = max((caps[c]["AUTHORITY"] for c in plan), key=authority_rank)
    requires_ht = any(caps[c]["AUTHORITY"] == "RED" for c in plan)

    if requires_ht and selected.get("REQUIRES_HUMAN_THRESHOLD") is not True:
        return {
            **base,
            "STATE": "HOLD",
            "HOLD_REASON": "RED_CAPABILITY_WITHOUT_HUMAN_THRESHOLD",
            "INTENT_CLASS": selected["INTENT_CLASS"],
            "PLAN_ID": None,
            "CAPABILITY_PLAN": plan,
            "MAX_AUTHORITY": max_authority,
            "REQUIRES_HUMAN_THRESHOLD": True,
            "EVIDENCE": {
                "routerContract": evidence_path(CONTRACT),
                "registry": evidence_path(REGISTRY),
                "graph": evidence_path(GRAPH),
                "classificationCount": 1,
                "planValidated": True,
                "authorityResolved": False,
            },
        }

    plan_basis = {
        "normalizedIntent": normalized,
        "intentClass": selected["INTENT_CLASS"],
        "truthFingerprint": fingerprint,
        "capabilityPlan": plan,
        "requiresHumanThreshold": requires_ht,
    }
    plan_id = "plan-" + sha256_bytes(canonical_bytes(plan_basis))[:24]

    return {
        **base,
        "STATE": "PLAN_READY",
        "HOLD_REASON": None,
        "INTENT_CLASS": selected["INTENT_CLASS"],
        "PLAN_ID": plan_id,
        "CAPABILITY_PLAN": plan,
        "MAX_AUTHORITY": max_authority,
        "REQUIRES_HUMAN_THRESHOLD": requires_ht,
        "EVIDENCE": {
            "routerContract": evidence_path(CONTRACT),
            "registry": evidence_path(REGISTRY),
            "graph": evidence_path(GRAPH),
            "classificationCount": 1,
            "planValidated": True,
            "authorityResolved": True,
            "executionAuthorized": False,
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("human_intent", nargs="?")
    parser.add_argument("--intent", dest="intent_option")
    args = parser.parse_args()
    intent = args.intent_option if args.intent_option is not None else (args.human_intent or "")
    result = route(intent)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["STATE"] == "PLAN_READY" else 20

if __name__ == "__main__":
    raise SystemExit(main())
