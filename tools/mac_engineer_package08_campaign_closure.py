#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"
DONECHECK_VERSION = "1.2.0"
DONECHECK_SHA = "8b90a8fc93453dd8a84994195d28d14b15e261cb"
OBJECTIVE = "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN"
FINAL_NEXT_ACTION = "AWAIT_NEXT_OBJECTIVE"
CAP19_ID = "INTERNET_RESEARCH_HARVEST_ASTRA"
CAP19_ACTION = "PACKAGE08_CAP19_INTERNET_RESEARCH_HARVEST_ASTRA_FIELD_PROOF"
CAP19_PROVIDER = "local_runtime"
CAP19_MODEL = "qwen3:14b"
REQUIRED_ZERO_TOLERANCE = {
    "AUTHORITY_BYPASS",
    "CRITICAL_FALSE_PASS",
    "EVIDENCE_MISSING",
    "HUMAN_THRESHOLD_MISS",
    "STALE_PASS_USED_AS_FINAL",
    "UNBOUNDED_RETRY",
    "UNTRACKED_MUTATION",
}


class ClosureHold(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ClosureHold(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_documents(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    gov = root / "governance" / "mac-engineer"
    return {
        "registry": load_json(gov / "CAPABILITY_REGISTRY_V1.json"),
        "bindings": load_json(gov / "CAPABILITY_EXECUTION_BINDING_V1.json"),
        "ledger": load_json(gov / "CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json"),
        "graph": load_json(gov / "CAPABILITY_DEPENDENCY_GRAPH_V1.json"),
        "actions": load_json(gov / "OPERATOR_ACTION_REGISTRY_V1.json"),
        "session": load_json(gov / "SESSION_STATE_V1.json"),
        "roadmap": load_json(gov / "PRODUCT_ROADMAP_V1.json"),
    }


def _capability_ids(rows: list[dict[str, Any]], key: str) -> list[str]:
    return [str(row.get(key) or "") for row in rows]


def evaluate(root: Path = ROOT) -> tuple[dict[str, bool], dict[str, Any]]:
    docs = load_documents(root)
    registry = docs["registry"]
    bindings = docs["bindings"]
    ledger = docs["ledger"]
    graph = docs["graph"]
    actions = docs["actions"]
    session = docs["session"]
    roadmap = docs["roadmap"]

    registry_rows = registry.get("capabilities") or []
    binding_rows = bindings.get("bindings") or []
    ledger_rows = ledger.get("capabilities") or []
    graph_nodes = graph.get("nodes") or []
    action_rows = actions.get("actions") or {}

    registry_ids = _capability_ids(registry_rows, "CAPABILITY_ID")
    binding_ids = _capability_ids(binding_rows, "CAPABILITY_ID")
    ledger_ids = _capability_ids(ledger_rows, "capabilityId")
    graph_ids = _capability_ids(graph_nodes, "CAPABILITY_ID")

    evidence_bindings: list[dict[str, Any]] = []
    evidence_valid = True
    cap01_18_valid = True
    for row in ledger_rows:
        evidence = row.get("evidence") or {}
        path = Path(str(evidence.get("path") or ""))
        expected = str(evidence.get("sha256") or "")
        actual = sha256(path) if path.is_file() else ""
        valid = bool(expected) and actual == expected
        evidence_valid = evidence_valid and valid
        if int(row.get("index") or 0) <= 18:
            cap01_18_valid = cap01_18_valid and valid
        evidence_bindings.append({
            "index": row.get("index"),
            "capabilityId": row.get("capabilityId"),
            "fieldState": row.get("fieldState"),
            "path": str(path),
            "sha256": expected,
            "digestValid": valid,
        })

    registered_bindings_valid = True
    for row in binding_rows:
        binding_type = row.get("BINDING_TYPE")
        if binding_type == "REGISTERED_ACTION":
            action = str(row.get("ACTION") or "")
            registered_bindings_valid = (
                registered_bindings_valid
                and bool(action)
                and action in action_rows
                and action_rows[action].get("handler") == row.get("REGISTERED_HANDLER")
            )
        elif binding_type not in {"DIRECT_RUNTIME", "HOLD_UNBOUND"}:
            registered_bindings_valid = False

    cap19_row = next(
        (row for row in ledger_rows if row.get("capabilityId") == CAP19_ID),
        {},
    )
    cap19_evidence = cap19_row.get("evidence") or {}
    cap19_seal_path = Path(str(cap19_evidence.get("path") or ""))
    cap19_seal = load_json(cap19_seal_path) if cap19_seal_path.is_file() else {}
    cap19_donecheck_ref = cap19_seal.get("mandatoryDoneCheck") or {}
    cap19_donecheck_path = Path(str(cap19_donecheck_ref.get("path") or ""))
    cap19_donecheck = (
        load_json(cap19_donecheck_path) if cap19_donecheck_path.is_file() else {}
    )
    cap19_criteria = cap19_donecheck.get("criteria") or {}
    cap19_source_bindings = cap19_seal.get("sourceBindings") or []

    post_session = session.get("postV08Objective") or {}
    post_roadmap = (roadmap.get("current") or {}).get("postV08Objective") or {}
    current_v08 = session.get("currentV08") or {}
    roadmap_current = roadmap.get("current") or {}
    roadmap_v08 = next(
        (
            row
            for row in (roadmap.get("versions") or [])
            if row.get("version") == "v0.8"
        ),
        {},
    )
    zero_tolerance = ledger.get("zeroTolerance") or {}
    authority_boundary = graph.get("authorityBoundary") or {}

    checks = {
        "registry_coverage_19": (
            len(registry_rows) == 19
            and len(set(registry_ids)) == 19
            and set(registry_ids) == set(ledger_ids)
            and all(row.get("STATE") in {"VERIFIED", "VERIFIED_BOUNDED"} for row in registry_rows)
        ),
        "execution_binding_coverage_19": (
            len(binding_rows) == 19
            and len(set(binding_ids)) == 19
            and set(binding_ids) == set(ledger_ids)
            and registered_bindings_valid
        ),
        "field_ledger_19_of_19": (
            ledger.get("fieldVerifiedCount") == 19
            and ledger.get("capabilityCount") == 19
            and len(ledger_rows) == 19
            and [row.get("index") for row in ledger_rows] == list(range(1, 20))
            and all(row.get("fieldState") == "FIELD_VERIFIED" for row in ledger_rows)
            and all((row.get("acceptance") or {}).get("fieldVerified") is True for row in ledger_rows)
        ),
        "all_field_evidence_digests_valid": evidence_valid,
        "cap01_18_evidence_chain_preserved": cap01_18_valid,
        "dependency_graph_coverage_and_authority": (
            len(graph_nodes) == 19
            and len(set(graph_ids)) == 19
            and set(graph_ids) == set(ledger_ids)
            and authority_boundary.get("newCoreIntroduced") is False
            and authority_boundary.get("unlistedTransitionPolicy") == "HOLD"
        ),
        "operator_registry_and_cap19_action_valid": (
            isinstance(action_rows, dict)
            and CAP19_ACTION in action_rows
            and action_rows[CAP19_ACTION].get("handler") == CAP19_ACTION
            and action_rows[CAP19_ACTION].get("readOnlyNetwork") is True
            and action_rows[CAP19_ACTION].get("remotePush") is False
            and action_rows[CAP19_ACTION].get("maxAttempts") == 2
        ),
        "cap19_field_seal_valid": (
            cap19_seal.get("state") == "PASS"
            and cap19_seal.get("capabilityIndex") == 19
            and cap19_seal.get("capabilityId") == CAP19_ID
            and cap19_seal.get("canonicalAction") == CAP19_ACTION
            and cap19_seal.get("provider") == CAP19_PROVIDER
            and cap19_seal.get("model") == CAP19_MODEL
            and len(cap19_source_bindings) == 2
            and all(item.get("url") and item.get("sha256") for item in cap19_source_bindings)
            and cap19_seal.get("canonicalTruthPreserved") is True
        ),
        "cap19_donecheck_21_of_21": (
            cap19_donecheck.get("state") == "PASS"
            and cap19_donecheck.get("criterionCount") == 21
            and len(cap19_criteria) == 21
            and all(
                item.get("state") == "PASS" and item.get("check") is True
                for item in cap19_criteria.values()
            )
            and cap19_donecheck_ref.get("sha256") == (
                sha256(cap19_donecheck_path) if cap19_donecheck_path.is_file() else ""
            )
        ),
        "zero_tolerance_all_zero": (
            set(zero_tolerance) == REQUIRED_ZERO_TOLERANCE
            and all(value == 0 for value in zero_tolerance.values())
        ),
        "v08_verified_locked_preserved": (
            current_v08.get("state") == "VERIFIED_LOCKED"
            and roadmap_current.get("state") == "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
            and roadmap_v08.get("state") == "VERIFIED_LOCKED"
            and post_session.get("v08Reopened") is False
            and post_roadmap.get("v08Reopened") is False
        ),
        "gate12_final_lock_preserved": (
            (current_v08.get("gate12") or {}).get("state") == "VERIFIED_LOCKED"
            and post_session.get("gate12Reactivated") is False
            and post_roadmap.get("gate12Reactivated") is False
        ),
        "campaign_canonical_surfaces_aligned": (
            post_session == post_roadmap
            and post_session.get("objective") == OBJECTIVE
            and post_roadmap.get("objective") == OBJECTIVE
            and post_session.get("fieldVerifiedCount") == 19
            and post_session.get("activeCapabilityState") == "FIELD_VERIFIED"
            and post_session.get("state") == "VERIFIED_CLOSED"
        ),
        "remote_push_authority_closed": (
            cap19_seal.get("execution", {}).get("remotePush") is False
            and action_rows[CAP19_ACTION].get("remotePush") is False
        ),
    }

    context = {
        "documents": docs,
        "evidenceBindings": evidence_bindings,
        "cap19Seal": {
            "path": str(cap19_seal_path),
            "sha256": sha256(cap19_seal_path) if cap19_seal_path.is_file() else "",
        },
        "cap19DoneCheck": {
            "path": str(cap19_donecheck_path),
            "sha256": sha256(cap19_donecheck_path) if cap19_donecheck_path.is_file() else "",
            "criterionCount": cap19_donecheck.get("criterionCount"),
        },
        "cap19SourceBindings": cap19_source_bindings,
        "zeroTolerance": zero_tolerance,
    }
    return checks, context


def create_closure_evidence(output_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    checks, context = evaluate(root)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ClosureHold("PACKAGE08_CAMPAIGN_CLOSURE_HOLD:" + ",".join(failed))

    output_dir.mkdir(parents=True, exist_ok=False)
    observed_at = now()
    criteria = {
        name: {"state": "PASS", "check": True}
        for name in checks
    }
    donecheck = {
        "schema": "enguru.mac-engineer.package08-campaign-donecheck/v1",
        "observedAt": observed_at,
        "state": "PASS",
        "claim": "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN_AGGREGATE_ACCEPTANCE_PASS",
        "doneCheck": {"version": DONECHECK_VERSION, "exactSha": DONECHECK_SHA},
        "criterionCount": len(criteria),
        "criteria": criteria,
        "fieldVerifiedCount": 19,
        "zeroTolerance": context["zeroTolerance"],
    }
    donecheck_path = output_dir / "campaign-donecheck.json"
    write_json(donecheck_path, donecheck)

    receipt = {
        "schema": "enguru.mac-engineer.package08-campaign-closure-receipt/v1",
        "observedAt": observed_at,
        "state": "PASS",
        "claim": "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN_VERIFIED_CLOSED",
        "objective": OBJECTIVE,
        "campaignState": "VERIFIED_CLOSED",
        "fieldVerifiedCount": 19,
        "capabilities": context["evidenceBindings"],
        "cap19FieldSeal": context["cap19Seal"],
        "cap19DoneCheck": context["cap19DoneCheck"],
        "cap19SourceBindings": context["cap19SourceBindings"],
        "campaignDoneCheck": {
            "path": str(donecheck_path),
            "sha256": sha256(donecheck_path),
            "criterionCount": len(criteria),
        },
        "zeroTolerance": context["zeroTolerance"],
        "preservation": {
            "cap01_19Preserved": True,
            "cap01_18EvidenceChainPreserved": True,
            "historicalEvidencePreserved": True,
            "authorityBoundariesPreserved": True,
            "providerModelNetworkContractsPreserved": True,
            "v08VerifiedLockedPreserved": True,
            "gate12FinalLockPreserved": True,
        },
        "execution": {
            "networkExecution": False,
            "providerExecution": False,
            "runtimeMutation": False,
            "remotePush": False,
            "commitCreated": False,
        },
        "canonicalPromotion": {
            "from": "ACTIVE",
            "to": "VERIFIED_CLOSED",
            "nextAction": FINAL_NEXT_ACTION,
        },
    }
    receipt_path = output_dir / "campaign-closure-receipt.json"
    write_json(receipt_path, receipt)
    return {
        "state": "PASS",
        "doneCheckPath": str(donecheck_path),
        "doneCheckSha256": sha256(donecheck_path),
        "receiptPath": str(receipt_path),
        "receiptSha256": sha256(receipt_path),
        "criterionCount": len(criteria),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(
            Path.home()
            / "Enguru/Evidence/MacEngineer/package08-field-campaign"
            / "campaign-closure"
            / stamp()
        ),
    )
    args = parser.parse_args()
    try:
        result = create_closure_evidence(args.output_dir)
    except ClosureHold as error:
        print("STATE=HOLD")
        print(f"REASON={error}")
        return 20
    print("STATE=PASS")
    print("CLAIM=PACKAGE08_FIELD_CAPABILITY_CAMPAIGN_AGGREGATE_ACCEPTANCE_PASS")
    print(f"CAMPAIGN_DONECHECK={result['doneCheckPath']}")
    print(f"CAMPAIGN_DONECHECK_SHA256={result['doneCheckSha256']}")
    print(f"CAMPAIGN_CLOSURE_RECEIPT={result['receiptPath']}")
    print(f"CAMPAIGN_CLOSURE_RECEIPT_SHA256={result['receiptSha256']}")
    print(f"DONECHECK_CRITERIA_PASS={result['criterionCount']}/{result['criterionCount']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
