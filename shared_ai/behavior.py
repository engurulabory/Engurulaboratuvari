from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_DATA_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "SECRET"}
VALID_REASONING_EFFORTS = {"MINIMAL", "STANDARD", "DEEP"}
VALID_CONSEQUENCE_LEVELS = {"LOW", "MEDIUM", "HIGH"}
VALID_VERIFICATION_PROFILES = {"BASIC", "GROUNDED", "STRUCTURED", "ACTION"}
VALID_CAPABILITIES = {
    "text",
    "vision",
    "audio",
    "tool_calling",
    "structured_output",
    "reasoning",
    "streaming",
    "long_context",
}
STEP_BUDGETS = {"MINIMAL": 2, "STANDARD": 6, "DEEP": 12}


@dataclass(frozen=True)
class BehaviorPlan:
    reasoning_effort: str
    step_budget: int
    verification_profile: str
    tool_required: bool
    context_state: str


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
    version = "0.2"
    max_corrections = 1

    @staticmethod
    def reasoning_effort(request: Any) -> str:
        task = str(getattr(request, "task_type", "")).lower()
        data_class = str(getattr(request, "data_class", "")).upper()
        capabilities = set(getattr(request, "required_capabilities", frozenset()))
        consequence = str(getattr(request, "consequence_level", "LOW")).upper()
        uncertainty = float(getattr(request, "uncertainty", 0.0))

        if (
            data_class == "SECRET"
            or consequence == "HIGH"
            or uncertainty >= 0.60
            or "reasoning" in capabilities
            or task in {"audit", "verification", "research", "reasoning"}
        ):
            return "DEEP"
        if (
            consequence == "LOW"
            and uncertainty <= 0.20
            and task in {"echo", "format", "rewrite", "classification"}
        ):
            return "MINIMAL"
        return "STANDARD"

    def plan(self, request: Any) -> BehaviorPlan:
        effort = self.reasoning_effort(request)
        profile = str(getattr(request, "verification_profile", "BASIC")).upper()
        context_state = "RESUMED" if getattr(request, "resume_from", None) else "NEW"
        tool_required = "tool_calling" in set(
            getattr(request, "required_capabilities", frozenset())
        )
        return BehaviorPlan(
            reasoning_effort=effort,
            step_budget=STEP_BUDGETS[effort],
            verification_profile=profile,
            tool_required=tool_required,
            context_state=context_state,
        )

    def preflight(self, request: Any) -> BehaviorVerdict:
        plan = self.plan(request)

        if not str(getattr(request, "input", "")).strip():
            return BehaviorVerdict("HOLD", "missing_input", plan.reasoning_effort)
        if str(getattr(request, "data_class", "")).upper() not in VALID_DATA_CLASSES:
            return BehaviorVerdict("HOLD", "invalid_data_class", plan.reasoning_effort)
        if float(getattr(request, "cost_ceiling", 0)) < 0:
            return BehaviorVerdict("HOLD", "invalid_cost_ceiling", plan.reasoning_effort)

        capabilities = set(getattr(request, "required_capabilities", frozenset()))
        if not capabilities:
            return BehaviorVerdict("HOLD", "missing_capabilities", plan.reasoning_effort)
        if capabilities - VALID_CAPABILITIES:
            return BehaviorVerdict("HOLD", "unknown_capability", plan.reasoning_effort)

        consequence = str(getattr(request, "consequence_level", "LOW")).upper()
        if consequence not in VALID_CONSEQUENCE_LEVELS:
            return BehaviorVerdict("HOLD", "invalid_consequence_level", plan.reasoning_effort)

        uncertainty = float(getattr(request, "uncertainty", 0.0))
        if uncertainty < 0 or uncertainty > 1:
            return BehaviorVerdict("HOLD", "invalid_uncertainty", plan.reasoning_effort)

        if plan.verification_profile not in VALID_VERIFICATION_PROFILES:
            return BehaviorVerdict("HOLD", "invalid_verification_profile", plan.reasoning_effort)

        if getattr(request, "resume_from", None) and not getattr(request, "context_id", None):
            return BehaviorVerdict("HOLD", "invalid_resume_state", plan.reasoning_effort)

        if plan.verification_profile == "GROUNDED" and not tuple(
            getattr(request, "provenance", tuple())
        ):
            return BehaviorVerdict("HOLD", "missing_provenance", plan.reasoning_effort)

        if plan.verification_profile == "ACTION" and not tuple(
            getattr(request, "tool_evidence", tuple())
        ):
            return BehaviorVerdict("HOLD", "missing_action_evidence", plan.reasoning_effort)

        return BehaviorVerdict("PASS", "preflight_pass", plan.reasoning_effort)

    def verify(self, request: Any, output: Any) -> BehaviorVerdict:
        plan = self.plan(request)
        if output is None:
            return BehaviorVerdict("HOLD", "empty_output", plan.reasoning_effort)
        if isinstance(output, str) and not output.strip():
            return BehaviorVerdict("HOLD", "empty_output", plan.reasoning_effort)

        if plan.verification_profile == "STRUCTURED" and not isinstance(output, (dict, list)):
            return BehaviorVerdict(
                "HOLD", "structured_output_required", plan.reasoning_effort
            )

        if plan.verification_profile == "GROUNDED" and not tuple(
            getattr(request, "provenance", tuple())
        ):
            return BehaviorVerdict("HOLD", "missing_provenance", plan.reasoning_effort)

        if plan.verification_profile == "ACTION" and not tuple(
            getattr(request, "tool_evidence", tuple())
        ):
            return BehaviorVerdict("HOLD", "missing_action_evidence", plan.reasoning_effort)

        return BehaviorVerdict("PASS", "verification_pass", plan.reasoning_effort)

    @staticmethod
    def correction_retryable(reason: str) -> bool:
        return reason in {"empty_output", "structured_output_required"}

    def evidence(
        self,
        request: Any,
        preflight: BehaviorVerdict,
        verification: BehaviorVerdict | None = None,
        correction_attempts: int = 0,
    ) -> dict[str, Any]:
        plan = self.plan(request)
        payload: dict[str, Any] = {
            "behavior_version": self.version,
            "preflight": preflight.state,
            "preflight_reason": preflight.reason,
            "reasoning_effort": plan.reasoning_effort,
            "step_budget": plan.step_budget,
            "verification_profile": plan.verification_profile,
            "provenance_count": len(tuple(getattr(request, "provenance", tuple()))),
            "context_state": plan.context_state,
            "tool_required": plan.tool_required,
            "correction_attempts": correction_attempts,
            "private_chain_of_thought_stored": False,
        }
        if verification is not None:
            payload["verification"] = verification.state
            payload["verification_reason"] = verification.reason
        return payload
