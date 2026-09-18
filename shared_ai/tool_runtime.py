from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    capabilities: frozenset[str]
    read_only: bool = True
    consequential: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, Callable[[dict[str, Any]], Any]]] = {}

    def register(
        self,
        spec: ToolSpec,
        handler: Callable[[dict[str, Any]], Any],
    ) -> None:
        self._tools[spec.name] = (spec, handler)

    def discover(self, required_capabilities: set[str]) -> list[ToolSpec]:
        matches = []
        for spec, _ in self._tools.values():
            if required_capabilities.issubset(set(spec.capabilities)):
                matches.append(spec)
        return sorted(matches, key=lambda item: item.name)

    def execute(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if name not in self._tools:
            return {"state": "HOLD", "reason": "tool_not_registered", "tool": name}
        spec, handler = self._tools[name]
        if spec.consequential:
            return {
                "state": "HOLD",
                "reason": "human_threshold_required",
                "tool": name,
            }
        try:
            output = handler(payload)
            return {
                "state": "PASS",
                "reason": "tool_executed",
                "tool": name,
                "output": output,
                "read_only": spec.read_only,
            }
        except Exception as exc:
            return {
                "state": "HOLD",
                "reason": f"tool_error:{type(exc).__name__}",
                "tool": name,
            }
