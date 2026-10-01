from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"

CAPABILITY_BINDING = GOV / "CAPABILITY_EXECUTION_BINDING_V1.json"
CAPABILITY_GRAPH = GOV / "CAPABILITY_DEPENDENCY_GRAPH_V1.json"
ACTION_REGISTRY = GOV / "OPERATOR_ACTION_REGISTRY_V1.json"
PILOT_FABRIC = GOV / "PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json"
PILOT_GOVERNANCE = GOV / "PRODUCT_OPERATOR_V12_PILOT_GOVERNANCE_CONTRACT_V1.json"


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object: {path}")
    return data


def _pilot(pilot_id: str) -> dict[str, Any] | None:
    fabric = _load(PILOT_FABRIC)
    profiles = fabric.get("profiles") or []

    for profile in profiles:
        if (
            isinstance(profile, dict)
            and profile.get("PILOT_ID") == pilot_id
        ):
            return profile

    return None


def _capability_graph_node(capability_id: str) -> dict[str, Any] | None:
    graph = _load(CAPABILITY_GRAPH)
    nodes = graph.get("nodes") or []

    for node in nodes:
        if (
            isinstance(node, dict)
            and node.get("CAPABILITY_ID") == capability_id
        ):
            return node

    return None


def resolve_pilot_execution(
    *,
    work_id: str,
    pilot_id: str,
    capability_id: str,
    producer_id: str,
    verifier_id: str,
    writer_owner: str | None = None,
) -> dict[str, Any]:

    if not work_id or not pilot_id or not capability_id:
        return {
            "state": "HOLD",
            "reason": "WORK_PILOT_CAPABILITY_REQUIRED",
        }

    pilot = _pilot(pilot_id)
    if pilot is None:
        return {
            "state": "HOLD",
            "reason": "UNKNOWN_PILOT",
            "pilot_id": pilot_id,
        }

    approved = pilot.get("CAPABILITY_IDS") or []
    if capability_id not in approved:
        return {
            "state": "HOLD",
            "reason": "PILOT_CAPABILITY_NOT_APPROVED",
            "pilot_id": pilot_id,
            "capability_id": capability_id,
        }

    binding_doc = _load(CAPABILITY_BINDING)
    bindings = binding_doc.get("bindings") or []

    binding = next(
        (
            item for item in bindings
            if isinstance(item, dict)
            and item.get("CAPABILITY_ID") == capability_id
        ),
        None,
    )

    if binding is None:
        return {
            "state": "HOLD",
            "reason": "CAPABILITY_BINDING_UNRESOLVED",
            "capability_id": capability_id,
        }

    binding_type = binding.get("BINDING_TYPE")

    if binding_type not in {"REGISTERED_ACTION", "DIRECT_RUNTIME"}:
        return {
            "state": "HOLD",
            "reason": "CAPABILITY_NOT_EXECUTABLE",
            "capability_id": capability_id,
            "binding_type": binding_type,
        }

    action = binding.get("ACTION")
    handler = None
    action_authority = None

    if binding_type == "REGISTERED_ACTION":
        actions = (_load(ACTION_REGISTRY).get("actions") or {})
        record = actions.get(action)

        if not isinstance(record, dict):
            return {
                "state": "HOLD",
                "reason": "ACTION_REGISTRY_UNRESOLVED",
                "action": action,
            }

        handler = record.get("handler")
        action_authority = record.get("authority")

        if not handler:
            return {
                "state": "HOLD",
                "reason": "ACTION_HANDLER_UNRESOLVED",
                "action": action,
            }

        if not action_authority:
            return {
                "state": "HOLD",
                "reason": "ACTION_AUTHORITY_UNRESOLVED",
                "action": action,
            }

        declared_binding_authority = binding.get("AUTHORITY")
        if (
            declared_binding_authority
            and declared_binding_authority != action_authority
        ):
            return {
                "state": "HOLD",
                "reason": "AUTHORITY_SOURCE_CONTRADICTION",
                "bindingAuthority": declared_binding_authority,
                "actionAuthority": action_authority,
            }

        authority = action_authority

    else:
        node = _capability_graph_node(capability_id)

        if not isinstance(node, dict):
            return {
                "state": "HOLD",
                "reason": "CAPABILITY_AUTHORITY_UNRESOLVED",
                "capability_id": capability_id,
            }

        authority = node.get("AUTHORITY")

        if not authority:
            return {
                "state": "HOLD",
                "reason": "CAPABILITY_AUTHORITY_UNRESOLVED",
                "capability_id": capability_id,
            }

    if not producer_id or not verifier_id:
        return {
            "state": "HOLD",
            "reason": "PRODUCER_AND_VERIFIER_REQUIRED",
        }

    if producer_id == verifier_id:
        return {
            "state": "HOLD",
            "reason": "PRODUCER_VERIFIER_COLLISION",
        }

    mutation_scope = binding.get("MUTATION_SCOPE")

    material_mutation = bool(
        mutation_scope
        and mutation_scope not in {
            "READ_ONLY",
            "TEST_ARTIFACTS_ONLY",
            "BUILD_ARTIFACTS_ONLY",
        }
    )

    if material_mutation:
        if not writer_owner:
            return {
                "state": "HOLD",
                "reason": "SINGLE_WRITER_OWNER_REQUIRED",
                "work_id": work_id,
            }

        if writer_owner != pilot_id:
            return {
                "state": "HOLD",
                "reason": "SINGLE_WRITER_OWNER_MISMATCH",
                "work_id": work_id,
                "pilot_id": pilot_id,
                "writer_owner": writer_owner,
            }

    envelope = {
        "WORK_ID": work_id,
        "PILOT_ID": pilot_id,
        "CAPABILITY_ID": capability_id,
        "AUTHORITY": authority,
        "BINDING_TYPE": binding_type,
        "ACTION": action,
        "HANDLER": handler,
        "MUTATION_SCOPE": mutation_scope,
        "HUMAN_THRESHOLD_REQUIRED": bool(
            binding.get("HUMAN_THRESHOLD_REQUIRED", False)
        ),
        "PRODUCER": producer_id,
        "VERIFIER": verifier_id,
        "SINGLE_WRITER_OWNER": (
            writer_owner if material_mutation else None
        ),
        "EXECUTION_AUTHORITY_CREATED": False,
    }

    return {
        "state": "PASS",
        "reason": "PILOT_RUNTIME_BINDING_RESOLVED",
        "execution": envelope,
        "handoff": {
            "WORK_ID": work_id,
            "PILOT": pilot_id,
            "CAPABILITY": capability_id,
            "AUTHORITY": authority,
            "PRODUCER": producer_id,
            "VERIFIER": verifier_id,
        },
    }
