"""ENGURU HIKMET CORE v0.1 fail-closed gate evaluator.

This module does not make religious, legal, or moral authority claims.
It evaluates declared gate states under ENGURU governance rules.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

GATES = (
    "intent",
    "reality",
    "perseverance",
    "mizan",
    "responsibility",
    "consequence",
    "learning",
)

VERDICTS = {"PASS", "HOLD", "BLOCKED"}
REQUIRED_GATE_FIELDS = {"state", "claim", "evidence", "next_action", "verdict"}


class HikmetContractError(ValueError):
    """Raised when a Hikmet Gate record violates the machine contract."""


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_record(record: Dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise HikmetContractError("record must be an object")

    required_top = set(GATES) | {"human_threshold_required", "overall_verdict"}
    missing = required_top - set(record)
    if missing:
        raise HikmetContractError(f"missing top-level fields: {sorted(missing)}")

    if not isinstance(record["human_threshold_required"], bool):
        raise HikmetContractError("human_threshold_required must be boolean")

    if record["overall_verdict"] not in VERDICTS:
        raise HikmetContractError("invalid overall_verdict")

    for gate_name in GATES:
        gate = record[gate_name]
        if not isinstance(gate, dict):
            raise HikmetContractError(f"{gate_name} must be an object")
        missing_fields = REQUIRED_GATE_FIELDS - set(gate)
        if missing_fields:
            raise HikmetContractError(
                f"{gate_name} missing fields: {sorted(missing_fields)}"
            )
        if not _nonempty(gate["state"]):
            raise HikmetContractError(f"{gate_name}.state must be non-empty")
        if not _nonempty(gate["claim"]):
            raise HikmetContractError(f"{gate_name}.claim must be non-empty")
        if not isinstance(gate["evidence"], list) or not all(
            _nonempty(item) for item in gate["evidence"]
        ):
            raise HikmetContractError(
                f"{gate_name}.evidence must be an array of non-empty strings"
            )
        if not isinstance(gate["next_action"], str):
            raise HikmetContractError(f"{gate_name}.next_action must be a string")
        if gate["verdict"] not in VERDICTS:
            raise HikmetContractError(f"{gate_name}.verdict is invalid")


def derive_overall_verdict(record: Dict[str, Any]) -> str:
    """Derive the only governance-safe overall verdict.

    BLOCKED dominates. Human Threshold always prevents automatic PASS.
    Any HOLD prevents PASS. PASS is possible only when every gate is PASS.
    """
    validate_record(record)
    gate_verdicts: Iterable[str] = (record[name]["verdict"] for name in GATES)
    verdicts = list(gate_verdicts)

    if "BLOCKED" in verdicts:
        return "BLOCKED"
    if record["human_threshold_required"]:
        return "HOLD"
    if "HOLD" in verdicts:
        return "HOLD"
    return "PASS"


def donecheck(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a DoneCheck-compatible evidence envelope for the Hikmet gate."""
    validate_record(record)
    derived = derive_overall_verdict(record)
    declared = record["overall_verdict"]
    aligned = declared == derived

    return {
        "state": "PASS" if aligned else "HOLD",
        "claim": "declared overall verdict matches fail-closed derivation",
        "evidence": {
            "declared_overall_verdict": declared,
            "derived_overall_verdict": derived,
            "human_threshold_required": record["human_threshold_required"],
            "gate_verdicts": {name: record[name]["verdict"] for name in GATES},
        },
        "next_action": "none" if aligned else "align overall_verdict with derived verdict",
        "verdict": "PASS" if aligned else "HOLD",
    }
