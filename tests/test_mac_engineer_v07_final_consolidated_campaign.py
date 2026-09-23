from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v07_final_consolidated_campaign.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v07_final_consolidated_campaign",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
campaign = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(campaign)


class FinalConsolidatedCampaignTests(unittest.TestCase):
    def test_locked_duration_and_event_contract(self):
        self.assertEqual(campaign.MIN_DURATION_SECONDS, 8 * 60 * 60)
        self.assertEqual(len(campaign.EVENT_SCHEDULE), 3)
        self.assertEqual(
            [name for _, name in campaign.EVENT_SCHEDULE],
            [
                "PROCESS_GRACEFUL_RESTART",
                "LOOPBACK_NETWORK_INTERRUPTION",
                "RUNTIME_ABRUPT_RESTART",
            ],
        )

    def test_resource_contract_passes_at_limits(self):
        samples = []
        for index in range(10):
            samples.append({
                "elapsedSeconds": campaign.WARMUP_SECONDS + index * 60,
                "rssKb": 100 if index < 5 else 150,
            })
        result = campaign.evaluate_resources(samples)
        self.assertEqual(result["state"], "PASS")
        self.assertLessEqual(result["peakRatio"], 2.0)
        self.assertLessEqual(result["finalRatio"], 1.5)

    def test_resource_contract_holds_above_peak_limit(self):
        samples = []
        for index in range(6):
            samples.append({
                "elapsedSeconds": campaign.WARMUP_SECONDS + index * 60,
                "rssKb": 100,
            })
        samples.append({
            "elapsedSeconds": campaign.WARMUP_SECONDS + 7 * 60,
            "rssKb": 201,
        })
        result = campaign.evaluate_resources(samples)
        self.assertEqual(result["state"], "HOLD")
        self.assertGreater(result["peakRatio"], 2.0)

    def test_resource_contract_holds_above_final_limit(self):
        samples = []
        for index in range(5):
            samples.append({
                "elapsedSeconds": campaign.WARMUP_SECONDS + index * 60,
                "rssKb": 100,
            })
        samples.append({
            "elapsedSeconds": campaign.WARMUP_SECONDS + 6 * 60,
            "rssKb": 151,
        })
        result = campaign.evaluate_resources(samples)
        self.assertEqual(result["state"], "HOLD")
        self.assertGreater(result["finalRatio"], 1.5)

    def test_campaign_idempotency_contract_is_stable(self):
        self.assertEqual(
            campaign.WORKER_IDEMPOTENCY_KEY,
            "ENGURU-V07-FINAL-CAMPAIGN-001",
        )
        self.assertEqual(
            campaign.EFFECT_KEY,
            "ENGURU-V07-FINAL-CAMPAIGN-EFFECT-001",
        )


if __name__ == "__main__":
    unittest.main()
