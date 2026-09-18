from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_DATA_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "SECRET"}
VALID_REASONING_EFFORTS = {"MINIMAL", "STANDARD", "DEEP"}


@dataclass(frozen=True)
class BehaviorVerdict:
    state: str
    reason: str
    reasoning_effort: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "reason": self.reason,
            "reasoning_effort": self.reasoning_effort,
        }


class BehaviorEngine:
    version = "0.1"

    @staticmethod
    def reasoning_effort(request: Any) -> str:
        task = str(getattr(request, "task_type", "")).lower()
        data_class = str(getattr(request, "data_class", "")).upper()
        capabilities = set(getattr(request, "required_capabilities", frozenset()))

        if data_class == "SECRET" or "reasoning" in capabilities or task in {
            "audit",
            "verification",
            "research",
            "reasoning",
        }:
            return "DEEP"
        if task in {"echo", "format", "rewrite", "classification"}:
            return "MINIMAL"
        return "STANDARD"

    def preflight(self, request: Any) -> BehaviorVerdict:
        effort = self.reasoning_effort(request)

        if not str(getattr(request, "input", "")).strip():
            return BehaviorVerdict("HOLD", "missing_input", effort)
        if str(getattr(request, "data_class", "")).upper() not in VALID_DATA_CLASSES:
            return BehaviorVerdict("HOLD", "invalid_data_class", effort)
        if float(getattr(request, "cost_ceiling", 0)) < 0:
            return BehaviorVerdict("HOLD", "invalid_cost_ceiling", effort)
        if not set(getattr(request, "required_capabilities", frozenset())):
            return BehaviorVerdict("HOLD", "missing_capabilities", effort)
        return BehaviorVerdict("PASS", "preflight_pass", effort)

    def verify(self, request: Any, output: Any) -> BehaviorVerdict:
        effort = self.reasoning_effort(request)
        if output is None:
            return BehaviorVerdict("HOLD", "empty_output", effort)
        if isinstance(output, str) and not output.strip():
            return BehaviorVerdict("HOLD", "empty_output", effort)
        return BehaviorVerdict("PASS", "verification_pass", effort)

    def evidence(
        self,
        preflight: BehaviorVerdict,
        verification: BehaviorVerdict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "behavior_version": self.version,
            "preflight": preflight.state,
            "preflight_reason": preflight.reason,
            "reasoning_effort": preflight.reasoning_effort,
            "private_chain_of_thought_stored": False,
        }
        if verification is not None:
            payload["verification"] = verification.state
            payload["verification_reason"] = verification.reason
        return payload
