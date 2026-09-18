import unittest

from shared_ai.release_quality import ImpactRule, ReleaseQualityGate


class ReleaseQualityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ReleaseQualityGate()
        self.rules = (
            ImpactRule("app/dashboard", ("/dashboard",)),
            ImpactRule("components/nav", ("/", "/dashboard")),
        )

    def test_diff_maps_to_affected_routes(self):
        routes = self.gate.affected_routes(
            ("components/nav/menu.tsx",),
            self.rules,
        )
        self.assertEqual(routes, ("/", "/dashboard"))

    def test_visual_change_without_mapping_holds(self):
        result = self.gate.assess(
            changed_paths=("components/unknown.tsx",),
            impact_rules=self.rules,
            browser_evidence={},
            visual_or_route_change=True,
            production_release=False,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "impact_mapping_required")

    def test_missing_browser_evidence_holds(self):
        result = self.gate.assess(
            changed_paths=("app/dashboard/page.tsx",),
            impact_rules=self.rules,
            browser_evidence={},
            visual_or_route_change=True,
            production_release=False,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "browser_evidence_missing")

    def test_browser_evidence_passes_for_preview(self):
        result = self.gate.assess(
            changed_paths=("app/dashboard/page.tsx",),
            impact_rules=self.rules,
            browser_evidence={"/dashboard": ("vx1:desktop", "vx1:mobile")},
            visual_or_route_change=True,
            production_release=False,
        )
        self.assertEqual(result.state, "PASS")

    def test_production_release_requires_canary(self):
        result = self.gate.assess(
            changed_paths=("app/dashboard/page.tsx",),
            impact_rules=self.rules,
            browser_evidence={"/dashboard": ("browser:pass",)},
            visual_or_route_change=True,
            production_release=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "canary_evidence_required")

    def test_benchmark_required_without_baseline_holds(self):
        result = self.gate.assess(
            changed_paths=("app/dashboard/page.tsx",),
            impact_rules=self.rules,
            browser_evidence={"/dashboard": ("browser:pass",)},
            visual_or_route_change=True,
            production_release=True,
            canary_evidence=("canary:pass",),
            benchmark_required=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "benchmark_evidence_required")

    def test_benchmark_regression_over_budget_holds(self):
        result = self.gate.assess(
            changed_paths=("app/dashboard/page.tsx",),
            impact_rules=self.rules,
            browser_evidence={"/dashboard": ("browser:pass",)},
            visual_or_route_change=True,
            production_release=True,
            canary_evidence=("canary:pass",),
            benchmark_required=True,
            benchmark_before=100.0,
            benchmark_after=125.0,
            regression_budget_pct=10.0,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "benchmark_regression_exceeded")
        self.assertAlmostEqual(result.benchmark_regression_pct, 25.0)

    def test_complete_release_evidence_passes(self):
        result = self.gate.assess(
            changed_paths=("components/nav/menu.tsx",),
            impact_rules=self.rules,
            browser_evidence={
                "/": ("browser:desktop",),
                "/dashboard": ("browser:desktop", "browser:mobile"),
            },
            visual_or_route_change=True,
            production_release=True,
            canary_evidence=("canary:http-200", "canary:no-console-errors"),
            benchmark_required=True,
            benchmark_before=100.0,
            benchmark_after=106.0,
            regression_budget_pct=10.0,
        )
        self.assertEqual(result.state, "PASS")
        self.assertAlmostEqual(result.benchmark_regression_pct, 6.0)


if __name__ == "__main__":
    unittest.main()
