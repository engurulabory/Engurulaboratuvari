import json
import unittest
from pathlib import Path

from shared_ai.jev_experiment import BenchmarkCase, JevPrediction, evaluate


FIXTURE = Path("evidence/jev/benchmark_states_v1.json")


class JevExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.rows = payload["cases"]

    def cases(self):
        return [
            BenchmarkCase(
                case_id=row["id"],
                canonical_verdict=row["canonical_verdict"],
                human_threshold_required=row["human_threshold_required"],
                critical_authority_case=row["critical_authority_case"],
            )
            for row in self.rows
        ]

    def perfect_predictions(self):
        return [
            JevPrediction(
                case_id=row["id"],
                verdict=row["canonical_verdict"],
                human_threshold_required=row["human_threshold_required"],
                confidence=0.99,
                latency_ms=100.0,
                cost_usd=0.00001,
            )
            for row in self.rows
        ]

    def test_fixture_has_exactly_100_cases(self):
        self.assertEqual(len(self.rows), 100)
        self.assertEqual(len({row["id"] for row in self.rows}), 100)

    def test_missing_live_metrics_stays_hold(self):
        result = evaluate(
            self.cases(),
            self.perfect_predictions(),
            calibration_acceptable=None,
            latency_improved=None,
            cost_improved=None,
            deterministic_fallback_pass=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.canonical_agreement, 1.0)

    def test_full_gate_can_pass_only_with_all_evidence(self):
        result = evaluate(
            self.cases(),
            self.perfect_predictions(),
            calibration_acceptable=True,
            latency_improved=True,
            cost_improved=True,
            deterministic_fallback_pass=True,
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.critical_false_pass, 0)
        self.assertEqual(result.human_threshold_miss, 0)

    def test_critical_false_pass_blocks(self):
        predictions = self.perfect_predictions()
        target = next(i for i, row in enumerate(self.rows) if row["critical_authority_case"] and row["canonical_verdict"] != "PASS")
        row = self.rows[target]
        predictions[target] = JevPrediction(row["id"], "PASS", row["human_threshold_required"], 0.99)
        result = evaluate(
            self.cases(), predictions,
            calibration_acceptable=True,
            latency_improved=True,
            cost_improved=True,
            deterministic_fallback_pass=True,
        )
        self.assertEqual(result.state, "BLOCKED")
        self.assertGreater(result.critical_false_pass, 0)

    def test_human_threshold_miss_blocks(self):
        predictions = self.perfect_predictions()
        target = next(i for i, row in enumerate(self.rows) if row["human_threshold_required"])
        row = self.rows[target]
        predictions[target] = JevPrediction(row["id"], row["canonical_verdict"], False, 0.99)
        result = evaluate(
            self.cases(), predictions,
            calibration_acceptable=True,
            latency_improved=True,
            cost_improved=True,
            deterministic_fallback_pass=True,
        )
        self.assertEqual(result.state, "BLOCKED")
        self.assertGreater(result.human_threshold_miss, 0)


if __name__ == "__main__":
    unittest.main()
