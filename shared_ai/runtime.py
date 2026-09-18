from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from shared_ai.behavior import BehaviorEngine


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

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RequestEnvelope":
        return cls(
            request_id=str(payload["request_id"]),
            task_type=str(payload["task_type"]),
            data_class=str(payload["data_class"]).upper(),
            required_capabilities=frozenset(str(x) for x in payload.get("required_capabilities", ["text"])),
            cost_ceiling=float(payload.get("cost_ceiling", 0)),
            input=str(payload.get("input", "")),
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
        }


class SharedAIRuntime:
    def __init__(self, providers: list[ProviderRecord] | None = None, behavior: BehaviorEngine | None = None) -> None:
        self.providers = providers or []
        self.behavior = behavior or BehaviorEngine()

    def register(self, provider: ProviderRecord) -> None:
        self.providers.append(provider)

    @staticmethod
    def _eligible(request: RequestEnvelope, provider: ProviderRecord) -> tuple[bool, str]:
        if provider.circuit_open or provider.health not in {"HEALTHY", "DEGRADED"}:
            return False, "health"
        if not provider.production_approved:
            return False, "authority"
        if not (provider.privacy_verified and provider.commercial_use_verified and provider.cost_verified):
            return False, "critical_metadata"
        if request.data_class == "SECRET" and not provider.local:
            return False, "secret_local_only"
        if provider.estimated_cost > request.cost_ceiling:
            return False, "cost"
        if not request.required_capabilities.issubset(provider.capabilities):
            return False, "capability"
        return True, "PASS"

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
                behavior_evidence=self.behavior.evidence(preflight),
            )

        for provider in self.providers:
            allowed, reason = self._eligible(request, provider)
            if not allowed:
                path.append(f"{provider.name}:SKIP:{reason}")
                continue

            try:
                attempts += 1
                response = provider.adapter.invoke(request)
                provider.failures = 0
                output = response.get("output")
                verification = self.behavior.verify(request, output)
                if verification.state != "PASS":
                    return RuntimeResult(
                        state=verification.state,
                        output=None,
                        provider=provider.name,
                        model=provider.model,
                        attempts=attempts,
                        path=tuple(path + [f"{provider.name}:PASS"]),
                        reason=verification.reason,
                        estimated_cost=provider.estimated_cost,
                        behavior_evidence=self.behavior.evidence(preflight, verification),
                    )
                return RuntimeResult(
                    state="PASS",
                    output=output,
                    provider=provider.name,
                    model=provider.model,
                    attempts=attempts,
                    path=tuple(path + [f"{provider.name}:PASS"]),
                    reason="verified_execution",
                    estimated_cost=provider.estimated_cost,
                    behavior_evidence=self.behavior.evidence(preflight, verification),
                )
            except Exception as exc:
                provider.failures += 1
                path.append(f"{provider.name}:ERROR:{type(exc).__name__}")
                if provider.failures >= 3:
                    provider.circuit_open = True
                continue

        return RuntimeResult(
            state="HOLD",
            output=None,
            provider=None,
            model=None,
            attempts=attempts,
            path=tuple(path),
            reason="no_safe_provider",
            estimated_cost=None,
            behavior_evidence=self.behavior.evidence(preflight),
        )
