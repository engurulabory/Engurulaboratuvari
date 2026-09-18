from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImpactRule:
    path_prefix: str
    routes: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseQualityResult:
    state: str
    reason: str
    affected_routes: tuple[str, ...]
    benchmark_regression_pct: float | None = None


class ReleaseQualityGate:
    """Evidence adapter for diff-aware browser QA, canary and benchmark proof."""

    @staticmethod
    def affected_routes(
        changed_paths: tuple[str, ...],
        rules: tuple[ImpactRule, ...],
    ) -> tuple[str, ...]:
        routes: set[str] = set()
        for path in changed_paths:
            clean = path.strip("/")
            for rule in rules:
                prefix = rule.path_prefix.strip("/")
                if clean == prefix or clean.startswith(prefix + "/"):
                    routes.update(rule.routes)
        return tuple(sorted(routes))

    def assess(
        self,
        *,
        changed_paths: tuple[str, ...],
        impact_rules: tuple[ImpactRule, ...],
        browser_evidence: dict[str, tuple[str, ...]],
        visual_or_route_change: bool,
        production_release: bool,
        canary_evidence: tuple[str, ...] = tuple(),
        benchmark_required: bool = False,
        benchmark_before: float | None = None,
        benchmark_after: float | None = None,
        regression_budget_pct: float = 10.0,
    ) -> ReleaseQualityResult:
        if not changed_paths:
            return ReleaseQualityResult("HOLD", "missing_diff_scope", tuple())

        affected = self.affected_routes(changed_paths, impact_rules)

        if visual_or_route_change and not affected:
            return ReleaseQualityResult("HOLD", "impact_mapping_required", tuple())

        for route in affected:
            if not browser_evidence.get(route):
                return ReleaseQualityResult(
                    "HOLD", "browser_evidence_missing", affected
                )

        if production_release and not canary_evidence:
            return ReleaseQualityResult("HOLD", "canary_evidence_required", affected)

        regression: float | None = None
        if benchmark_required:
            if benchmark_before is None or benchmark_after is None:
                return ReleaseQualityResult(
                    "HOLD", "benchmark_evidence_required", affected
                )
            if benchmark_before <= 0:
                return ReleaseQualityResult(
                    "HOLD", "invalid_benchmark_baseline", affected
                )
            regression = ((benchmark_after - benchmark_before) / benchmark_before) * 100.0
            if regression > regression_budget_pct:
                return ReleaseQualityResult(
                    "HOLD",
                    "benchmark_regression_exceeded",
                    affected,
                    benchmark_regression_pct=regression,
                )

        return ReleaseQualityResult(
            "PASS",
            "release_quality_pass",
            affected,
            benchmark_regression_pct=regression,
        )
