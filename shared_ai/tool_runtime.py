from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
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

    def spec(self, name: str) -> ToolSpec | None:
        item = self._tools.get(name)
        return item[0] if item else None

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

    def execute_with_fallback(
        self,
        name: str,
        payload: dict[str, Any],
        fallbacks: tuple[str, ...] = tuple(),
    ) -> dict[str, Any]:
        candidates = (name,) + tuple(fallbacks)
        attempts = []
        for candidate in candidates:
            result = self.execute(candidate, payload)
            attempts.append(f"{candidate}:{result['reason']}")
            if result["state"] == "PASS":
                return {**result, "attempts": tuple(attempts)}
            if result["reason"] == "human_threshold_required":
                return {**result, "attempts": tuple(attempts)}
        return {**result, "attempts": tuple(attempts)}

    def execute_plan(
        self,
        steps: tuple[dict[str, Any], ...],
        *,
        parallel: bool = False,
    ) -> dict[str, Any]:
        if not steps:
            return {"state": "PASS", "reason": "no_tools", "results": tuple()}

        if parallel:
            specs = [self.spec(str(step.get("name", ""))) for step in steps]
            if any(spec is None for spec in specs):
                return {
                    "state": "HOLD",
                    "reason": "tool_not_registered",
                    "results": tuple(),
                }
            if any(spec.consequential or not spec.read_only for spec in specs if spec):
                return {
                    "state": "HOLD",
                    "reason": "parallel_side_effect_forbidden",
                    "results": tuple(),
                }
            with ThreadPoolExecutor(max_workers=len(steps)) as pool:
                futures = [
                    pool.submit(
                        self.execute_with_fallback,
                        str(step["name"]),
                        dict(step.get("payload", {})),
                        tuple(str(x) for x in step.get("fallbacks", [])),
                    )
                    for step in steps
                ]
                results = tuple(f.result() for f in futures)
        else:
            results_list = []
            for step in steps:
                result = self.execute_with_fallback(
                    str(step["name"]),
                    dict(step.get("payload", {})),
                    tuple(str(x) for x in step.get("fallbacks", [])),
                )
                results_list.append(result)
                if result["state"] != "PASS":
                    return {
                        "state": "HOLD",
                        "reason": result["reason"],
                        "results": tuple(results_list),
                    }
            results = tuple(results_list)

        if any(result["state"] != "PASS" for result in results):
            first = next(result for result in results if result["state"] != "PASS")
            return {
                "state": "HOLD",
                "reason": first["reason"],
                "results": results,
            }
        return {"state": "PASS", "reason": "tool_plan_executed", "results": results}
