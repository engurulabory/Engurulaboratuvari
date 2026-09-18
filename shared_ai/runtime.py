from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Protocol

from shared_ai.behavior import BehaviorEngine
from shared_ai.context_state import compact_context
from shared_ai.tool_runtime import ToolRegistry


class ProviderAdapter(Protocol):
    def invoke(self, request: "RequestEnvelope") -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class RequestEnvelope:
    request_id: str
    task_type: str
    data_class: str
    required_capabilities: frozenset[str]
    cost_ceiling: float
    input: str
    consequence_level: str = "LOW"
    uncertainty: float = 0.0
    verification_profile: str = "BASIC"
    provenance: tuple[str, ...] = tuple()
    context_id: str | None = None
    resume_from: str | None = None
    context_messages: tuple[str, ...] = tuple()
    steering_instruction: str = ""
    requested_tool: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    known_truths: tuple[str, ...] = tuple()
    tool_evidence: tuple[str, ...] = tuple()
    behavior_instruction: str = ""
    context_compacted: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RequestEnvelope":
        return cls(
            request_id=str(payload["request_id"]),
            task_type=str(payload["task_type"]),
            data_class=str(payload["data_class"]).upper(),
            required_capabilities=frozenset(
                str(x).lower()
                for x in payload.get("required_capabilities", ["text"])
            ),
            cost_ceiling=float(payload.get("cost_ceiling", 0)),
            input=str(payload.get("input", "")),
            consequence_level=str(payload.get("consequence_level", "LOW")).upper(),
            uncertainty=float(payload.get("uncertainty", 0.0)),
            verification_profile=str(
                payload.get("verification_profile", "BASIC")
            ).upper(),
            provenance=tuple(str(x) for x in payload.get("provenance", [])),
            context_id=(
                str(payload["context_id"]) if payload.get("context_id") else None
            ),
            resume_from=(
                str(payload["resume_from"]) if payload.get("resume_from") else None
            ),
            context_messages=tuple(
                str(x) for x in payload.get("context_messages", [])
            ),
            steering_instruction=str(payload.get("steering_instruction", "")),
            requested_tool=(
                str(payload["requested_tool"]) if payload.get("requested_tool") else None
            ),
            tool_input=(
                dict(payload.get("tool_input", {}))
                if isinstance(payload.get("tool_input", {}), dict)
                else {}
            ),
            # Internal authority/evidence fields are never accepted from callers.
            known_truths=tuple(),
            tool_evidence=tuple(),
            behavior_instruction="",
            context_compacted=False,
        )


@dataclass
class ProviderRecord:
    name: str
    model: str
    adapter: ProviderAdapter
    local: bool = False
    production_approved: bool = False
    privacy_verified: bool = False
    commercial_use_verified: bool = False
    cost_verified: bool = False
    estimated_cost: float = 0.0
    capabilities: set[str] = field(default_factory=lambda: {"text"})
    health: str = "HEALTHY"
    failures: int = 0
    circuit_open: bool = False


@dataclass(frozen=True)
class RuntimeResult:
    state: str
    output: Any
    provider: str | None
    model: str | None
    attempts: int
    path: tuple[str, ...]
    reason: str
    estimated_cost: float | None
    behavior_evidence: dict[str, Any] = field(default_factory=dict)
    citations: tuple[dict[str, Any], ...] = tuple()
    tool_evidence: tuple[str, ...] = tuple()

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "output": self.output,
            "route_evidence": {
                "provider": self.provider,
                "model": self.model,
                "attempts": self.attempts,
                "fallback_path": list(self.path),
                "reason": self.reason,
                "estimated_cost": self.estimated_cost,
            },
            "behavior_evidence": self.behavior_evidence,
            "citations": list(self.citations),
            "tool_evidence": list(self.tool_evidence),
        }


class SharedAIRuntime:
    def __init__(
        self,
        providers: list[ProviderRecord] | None = None,
        behavior: BehaviorEngine | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.providers = providers or []
        self.behavior = behavior or BehaviorEngine()
        self.tools = tools or ToolRegistry()

    def register(self, provider: ProviderRecord) -> None:
        self.providers.append(provider)

    @staticmethod
    def _eligible(
        request: RequestEnvelope, provider: ProviderRecord
    ) -> tuple[bool, str]:
        if provider.circuit_open or provider.health not in {"HEALTHY", "DEGRADED"}:
            return False, "health"
        if not provider.production_approved:
            return False, "authority"
        if not (
            provider.privacy_verified
            and provider.commercial_use_verified
            and provider.cost_verified
        ):
            return False, "critical_metadata"
        if request.data_class == "SECRET" and not provider.local:
            return False, "secret_local_only"
        if provider.estimated_cost > request.cost_ceiling:
            return False, "cost"
        if not request.required_capabilities.issubset(provider.capabilities):
            return False, "capability"
        return True, "PASS"

    def _prepare_context(self, request: RequestEnvelope) -> RequestEnvelope:
        if not request.context_messages and not request.steering_instruction:
            return request

        compacted = compact_context(
            list(request.context_messages),
            verified_facts=request.known_truths,
        )
        parts = []
        if compacted:
            parts.append(f"CONTEXT:{compacted}")
        if request.steering_instruction.strip():
            parts.append(f"CURRENT_STEERING:{request.steering_instruction.strip()}")

        return replace(
            request,
            behavior_instruction="\\n".join(parts),
            context_compacted=bool(compacted),
        )

    def _run_tool(self, request: RequestEnvelope) -> tuple[RequestEnvelope, dict[str, Any] | None]:
        if not request.requested_tool:
            return request, None

        result = self.tools.execute(request.requested_tool, request.tool_input)
        if result["state"] != "PASS":
            return request, result

        evidence = (f"{request.requested_tool}:PASS",)
        tool_output = result.get("output")
        instruction = request.behavior_instruction
        tool_context = f"TOOL_RESULT[{request.requested_tool}]:{tool_output}"
        instruction == "\n".join(part for part in [instruction, tool_context] if part)

        return (
            replace(
                request,
                tool_evidence=evidence,
                behavior_instruction=instruction,
            ),
            result,
        )

    def execute(self, request: RequestEnvelope) -> RuntimeResult:
        attempts = 0
        path: list[str] = []

        preflight = self.behavior.preflight(request)
        if preflight.state != "PASS":
            return RuntimeResult(
                state=preflight.state,
                output=None,
                provider=None,
                model=None,
                attempts=0,
                path=tuple(),
                reason=preflight.reason,
                estimated_cost=None,
                behavior_evidence=self.behavior.evidence(request, preflight),
            )

        active_request = self._prepare_context(request)
        active_request, tool_result = self._run_tool(active_request)

        if tool_result is not None and tool_result["state"] != "PASS":
            return RuntimeResult(
                state="HOLD",
                output=None,
                provider=None,
                model=None,
                attempts=0,
                path=(f"tool:{tool_result['tool']}:{tool_result['reason']}",),
                reason=tool_result["reason"],
                estimated_cost=None,
                behavior_evidence=self.behavior.evidence(active_request, preflight),
                tool_evidence=tuple(),
            )

        for provider in self.providers:
            allowed, reason = self._eligible(active_request, provider)
            if not allowed:
                path.append(f"{provider.name}:SKIP:{reason}")
                continue

            correction_attempts = 0
            provider_request = active_request

            while True:
                try:
                    attempts += 1
                    response = provider.adapter.invoke(provider_request)
                    provider.failures = 0
                    output = response.get("output")
                    verification = self.behavior.verify(active_request, output)

                    if verification.state == "PASS":
                        label = (
                            f"{provider.name}:CORRECT:PASS"
                            if correction_attempts
                            else f"{provider.name}:PASS"
                        )
                        return RuntimeResult(
                            state="PASS",
                            output=output,
                            provider=provider.name,
                            model=provider.model,
                            attempts=attempts,
                            path=tuple(path + [label]),
                            reason="verified_execution",
                            estimated_cost=provider.estimated_cost,
                            behavior_evidence=self.behavior.evidence(
                                active_request,
                                preflight,
                                verification,
                                correction_attempts=correction_attempts,
                            ),
                            citations=tuple(
                                self.behavior.render_citations(verification)
                            ),
                            tool_evidence=active_request.tool_evidence,
                        )

                    path.append(
                        f"{provider.name}:VERIFY_HOLD:{verification.reason}"
                    )

                    if (
                        correction_attempts < self.behavior.max_corrections
                        and self.behavior.correction_retryable(verification.reason)
                    ):
                        correction_attempts += 1
                        provider_request = replace(
                            active_request,
                            behavior_instruction="\n".join(
                                part
                                for part in [
                                    active_request.behavior_instruction,
                                    (
                                        "Previous output failed governed verification "
                                        f"({verification.reason}). Return a corrected response "
                                        f"for verification profile {active_request.verification_profile}."
                                    ),
                                ]
                                if part
                            ),
                        )
                        continue

                    return RuntimeResult(
                        state=verification.state,
                        output=None,
                        provider=provider.name,
                        model=provider.model,
                        attempts=attempts,
                        path=tuple(path),
                        reason=verification.reason,
                        estimated_cost=provider.estimated_cost,
                        behavior_evidence=self.behavior.evidence(
                            active_request,
                            preflight,
                            verification,
                            correction_attempts=correction_attempts,
                        ),
                        citations=tuple(
                            self.behavior.render_citations(verification)
                        ),
                        tool_evidence=active_request.tool_evidence,
                    )

                except Exception as exc:
                    provider.failures += 1
                    path.append(f"{provider.name}:ERROR:{type(exc).__name__}")
                    if provider.failures >= 3:
                        provider.circuit_open = True
                    break

        return RuntimeResult(
            state="HOLD",
            output=None,
            provider=None,
            model=None,
            attempts=attempts,
            path=tuple(path),
            reason="no_safe_provider",
            estimated_cost=None,
            behavior_evidence=self.behavior.evidence(active_request, preflight),
            tool_evidence=active_request.tool_evidence,
        )
