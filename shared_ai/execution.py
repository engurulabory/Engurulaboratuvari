from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionEnvelope:
    state: str
    output: Any
    source_type: str
    source_name: str | None
    model: str | None = None
    tools: tuple[str, ...] = tuple()
    route: tuple[str, ...] = tuple()
    attempts: int = 0
    latency_class: str = "STANDARD"
    estimated_cost: float | None = None
    evidence_refs: tuple[str, ...] = tuple()
    observations: tuple[str, ...] = tuple()
    side_effect_state: str = "NONE"
    completion_evidence: tuple[str, ...] = tuple()

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "output_present": self.output is not None,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "model": self.model,
            "tools": list(self.tools),
            "route": list(self.route),
            "attempts": self.attempts,
            "latency_class": self.latency_class,
            "estimated_cost": self.estimated_cost,
            "evidence_refs": list(self.evidence_refs),
            "observations": list(self.observations),
            "side_effect_state": self.side_effect_state,
            "completion_evidence": list(self.completion_evidence),
        }


def normalize_provider_response(
    response: Any,
    *,
    provider: str,
    model: str,
    attempts: int,
    latency_class: str,
    estimated_cost: float,
    evidence_refs: tuple[str, ...] = tuple(),
) -> ExecutionEnvelope:
    observations = []
    if not isinstance(response, dict):
        return ExecutionEnvelope(
            state="HOLD",
            output=None,
            source_type="provider",
            source_name=provider,
            model=model,
            attempts=attempts,
            latency_class=latency_class,
            estimated_cost=estimated_cost,
            evidence_refs=evidence_refs,
            observations=("malformed_provider_response",),
        )
    if "output" not in response:
        observations.append("missing_output_field")
    output = response.get("output")
    if response.get("partial") is True:
        observations.append("partial_output")
    return ExecutionEnvelope(
        state="PASS" if output is not None else "HOLD",
        output=output,
        source_type="provider",
        source_name=provider,
        model=model,
        attempts=attempts,
        latency_class=latency_class,
        estimated_cost=estimated_cost,
        evidence_refs=evidence_refs,
        observations=tuple(observations),
    )


def normalize_tool_plan(
    result: dict[str, Any] | None,
    *,
    latency_class: str,
) -> ExecutionEnvelope:
    if result is None:
        return ExecutionEnvelope(
            state="PASS",
            output=None,
            source_type="tool",
            source_name=None,
            latency_class=latency_class,
        )
    items = tuple(result.get("results", ()))
    tools = tuple(
        str(item.get("tool"))
        for item in items
        if isinstance(item, dict) and item.get("tool")
    )
    completion = tuple(
        str(ref)
        for item in items
        if isinstance(item, dict)
        for ref in item.get("completion_evidence", ())
    )
    side_effect = (
        "COMPLETED"
        if any(isinstance(item, dict) and item.get("side_effect") for item in items)
        else "NONE"
    )
    observations = tuple(
        str(item.get("reason"))
        for item in items
        if isinstance(item, dict) and item.get("state") != "PASS"
    )
    return ExecutionEnvelope(
        state=str(result.get("state", "HOLD")),
        output=items,
        source_type="tool",
        source_name=None,
        tools=tools,
        latency_class=latency_class,
        observations=observations,
        side_effect_state=side_effect,
        completion_evidence=completion,
    )
