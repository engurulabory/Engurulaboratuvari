from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Protocol

from shared_ai.behavior import BehaviorEngine
from shared_ai.capabilities import normalize_capabilities
from shared_ai.context_state import compact_context
from shared_ai.execution import ExecutionEnvelope, normalize_provider_response, normalize_tool_plan
from shared_ai.output import GovernedFormatter
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
    intent: str = ""
    success_criteria: tuple[str, ...] = tuple()
    critical_context_complete: bool = True
    grounding_status: str = "CURRENT"
    freshness_required: bool = False
    authoritative_provenance: tuple[str, ...] = tuple()
    reversibility: str = "REVERSIBLE"
    human_approval: bool = False
    tool_plan: tuple[dict[str, Any], ...] = tuple()
    parallel_tools: bool = False
    replan_count: int = 0
    latency_class: str = "STANDARD"
    response_language: str = "AUTO"
    response_length: str = "AUTO"
    response_structure: str = "PLAIN"
    include_technical_evidence: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RequestEnvelope":
        return cls(
            request_id=str(payload["request_id"]),
            task_type=str(payload["task_type"]),
            data_class=str(payload["data_class"]).upper(),
            required_capabilities=normalize_capabilities(
                payload.get("required_capabilities", ["text"])
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
            intent=str(payload.get("intent", "")),
            success_criteria=tuple(str(x) for x in payload.get("success_criteria", [])),
            critical_context_complete=bool(payload.get("critical_context_complete", True)),
            grounding_status=str(payload.get("grounding_status", "CURRENT")).upper(),
            freshness_required=bool(payload.get("freshness_required", False)),
            authoritative_provenance=tuple(
                str(x) for x in payload.get("authoritative_provenance", [])
            ),
            reversibility=str(payload.get("reversibility", "REVERSIBLE")).upper(),
            human_approval=False,
            tool_plan=tuple(
                dict(step) for step in payload.get("tool_plan", [])
                if isinstance(step, dict)
            ),
            parallel_tools=bool(payload.get("parallel_tools", False)),
            replan_count=0,
            latency_class=str(payload.get("latency_class", "STANDARD")).upper(),
            response_language=str(payload.get("response_language", "AUTO")).upper(),
            response_length=str(payload.get("response_length", "AUTO")).upper(),
            response_structure=str(payload.get("response_structure", "PLAIN")).upper(),
            include_technical_evidence=bool(payload.get("include_technical_evidence", False)),
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
    execution_evidence: dict[str, Any] = field(default_factory=dict)

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
            "execution_evidence": self.execution_evidence,
        }


class SharedAIRuntime:
    def __init__(
        self,
        providers: list[ProviderRecord] | None = None,
        behavior: BehaviorEngine | None = None,
        tools: ToolRegistry | None = None,
        formatter: GovernedFormatter | None = None,
    ) -> None:
        self.providers = providers or []
        self.behavior = behavior or BehaviorEngine()
        self.tools = tools or ToolRegistry()
        self.formatter = formatter or GovernedFormatter()

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
            behavior_instruction="\n".join(parts),
            context_compacted=bool(compacted),
        )

    def _run_tools(
        self, request: RequestEnvelope
    ) -> tuple[RequestEnvelope, dict[str, Any] | None]:
        steps = request.tool_plan
        if not steps and request.requested_tool:
            steps = ({
                "name": request.requested_tool,
                "payload": request.tool_input,
                "fallbacks": [],
            },)
        if not steps:
            return request, None

        result = self.tools.execute_plan(
            steps,
            parallel=request.parallel_tools,
            human_approved=request.human_approval,
        )
        if result["state"] != "PASS":
            return request, result

        evidence = tuple(
            f"{item['tool']}:PASS"
            for item in result.get("results", ())
            if item.get("state") == "PASS"
        )
        contexts = [
            f"TOOL_RESULT[{item['tool']}]:{item.get('output')}"
            for item in result.get("results", ())
            if item.get("state") == "PASS"
        ]
        instruction = "\n".join(
            part
            for part in [
                request.behavior_instruction,
                *contexts,
                "REPLAN_AFTER_TOOL_EVIDENCE",
            ]
            if part
        )

        return (
            replace(
                request,
                tool_evidence=evidence,
                behavior_instruction=instruction,
                replan_count=min(request.replan_count + 1, 1),
            ),
            result,
        )

    @staticmethod
    def _combine_execution(
        *,
        provider_execution: ExecutionEnvelope | None,
        tool_execution: ExecutionEnvelope,
        path: tuple[str, ...],
        citations: tuple[dict[str, Any], ...],
        tool_evidence: tuple[str, ...],
        state: str,
        reason: str,
        latency_class: str,
    ) -> dict[str, Any]:
        observations = list(tool_execution.observations)
        if provider_execution is not None:
            observations.extend(provider_execution.observations)
        if reason not in {"verified_execution", "no_safe_provider"}:
            observations.append(reason)
        refs = list(tool_evidence)
        refs.extend(str(item.get("ref")) for item in citations if item.get("ref"))
        envelope = ExecutionEnvelope(
            state=state,
            output=provider_execution.output if provider_execution is not None else None,
            source_type="combined",
            source_name=provider_execution.source_name if provider_execution is not None else None,
            model=provider_execution.model if provider_execution is not None else None,
            tools=tool_execution.tools,
            route=path,
            attempts=provider_execution.attempts if provider_execution is not None else 0,
            latency_class=latency_class,
            estimated_cost=(
                provider_execution.estimated_cost if provider_execution is not None else None
            ),
            evidence_refs=tuple(refs),
            observations=tuple(observations),
            side_effect_state=tool_execution.side_effect_state,
            completion_evidence=tool_execution.completion_evidence,
        )
        return envelope.as_dict()

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
        active_request, tool_result = self._run_tools(active_request)
        tool_execution = normalize_tool_plan(
            tool_result,
            latency_class=active_request.latency_class,
        )

        if tool_result is not None and tool_result["state"] != "PASS":
            return RuntimeResult(
                state="HOLD",
                output=None,
                provider=None,
                model=None,
                attempts=0,
                path=(f"tool-plan:{tool_result['reason']}",),
                reason=tool_result["reason"],
                estimated_cost=None,
                behavior_evidence=self.behavior.evidence(active_request, preflight),
                tool_evidence=tuple(),
                execution_evidence=self._combine_execution(
                    provider_execution=None,
                    tool_execution=tool_execution,
                    path=(f"tool-plan:{tool_result['reason']}",),
                    citations=tuple(),
                    tool_evidence=tuple(),
                    state="HOLD",
                    reason=tool_result["reason"],
                    latency_class=active_request.latency_class,
                ),
            )

        for provider in self.providers:
            allowed, reason = self._eligible(active_request, provider)
            if not allowed:
                path.append(f"{provider.name}:SKIP:{reason}")
                continue

            correction_attempts = 0
            replan_attempts = 0
            provider_request = active_request

            while True:
                try:
                    attempts += 1
                    response = provider.adapter.invoke(provider_request)
                    provider.failures = 0
                    provider_execution = normalize_provider_response(
                        response,
                        provider=provider.name,
                        model=provider.model,
                        attempts=attempts,
                        latency_class=active_request.latency_class,
                        estimated_cost=provider.estimated_cost,
                        evidence_refs=active_request.tool_evidence,
                    )
                    if (
                        provider_execution.state != "PASS"
                        or "partial_output" in provider_execution.observations
                    ):
                        observation = (
                            provider_execution.observations[0]
                            if provider_execution.observations
                            else "malformed_provider_response"
                        )
                        path.append(f"{provider.name}:OBSERVE:{observation}")
                        break
                    output = provider_execution.output
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
                            execution_evidence=self._combine_execution(
                                provider_execution=provider_execution,
                                tool_execution=tool_execution,
                                path=tuple(path + [label]),
                                citations=tuple(
                                    self.behavior.render_citations(verification)
                                ),
                                tool_evidence=active_request.tool_evidence,
                                state="PASS",
                                reason="verified_execution",
                                latency_class=active_request.latency_class,
                            ),
                        )

                    path.append(
                        f"{provider.name}:VERIFY_HOLD:{verification.reason}"
                    )

                    if (
                        verification.reason in {"contradiction_detected", "unsupported_claim"}
                        and replan_attempts < 1
                    ):
                        replan_attempts += 1
                        provider_request = replace(
                            active_request,
                            behavior_instruction="\n".join(
                                part
                                for part in [
                                    active_request.behavior_instruction,
                                    (
                                        "Governed verification found "
                                        f"{verification.reason}. Re-plan once using current "
                                        "evidence and remove the contradiction/unsupported claim."
                                    ),
                                ]
                                if part
                            ),
                            replan_count=min(active_request.replan_count + 1, 1),
                        )
                        continue

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
                        execution_evidence=self._combine_execution(
                            provider_execution=provider_execution,
                            tool_execution=tool_execution,
                            path=tuple(path),
                            citations=tuple(
                                self.behavior.render_citations(verification)
                            ),
                            tool_evidence=active_request.tool_evidence,
                            state=verification.state,
                            reason=verification.reason,
                            latency_class=active_request.latency_class,
                        ),
                    )

                except TimeoutError:
                    provider.failures += 1
                    path.append(f"{provider.name}:TIMEOUT")
                    if provider.failures >= 3:
                        provider.circuit_open = True
                    break
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
            execution_evidence=self._combine_execution(
                provider_execution=None,
                tool_execution=tool_execution,
                path=tuple(path),
                citations=tuple(),
                tool_evidence=active_request.tool_evidence,
                state="HOLD",
                reason="no_safe_provider",
                latency_class=active_request.latency_class,
            ),
        )
