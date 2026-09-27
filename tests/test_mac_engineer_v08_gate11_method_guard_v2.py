from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACCEPTANCE = ROOT / (
    "governance/mac-engineer/"
    "V08_GATE11_METHOD_ACCEPTANCE_V2.json"
)

GUARD = ROOT / (
    "tools/"
    "mac_engineer_v08_gate11_method_guard_v2.py"
)


class Gate11MethodV2Tests(unittest.TestCase):

    def load(self):
        return json.loads(
            ACCEPTANCE.read_text(
                encoding="utf-8"
            )
        )

    def test_exact_p01_p12(self):
        data = self.load()

        self.assertEqual(
            [
                p["id"]
                for p in data["packages"]
            ],
            [
                f"P{i:02d}"
                for i in range(1, 13)
            ],
        )

    def test_gate11_execution_remains_zero_state(self):
        data = self.load()

        self.assertEqual(
            data["state"],
            "PREPARED_QUEUED",
        )

        self.assertFalse(
            data["executionActive"]
        )

    def test_gate8_harvest_is_historical_verified(self):
        data = self.load()

        harvest = (
            data[
                "historicalCapabilities"
            ][
                "researchHarvest"
            ]
        )

        self.assertEqual(
            harvest["originGate"],
            8,
        )

        self.assertEqual(
            harvest["state"],
            "HISTORICAL_VERIFIED",
        )

        self.assertFalse(
            harvest[
                "duplicateCapabilityCreationAllowed"
            ]
        )

    def test_p03_reconciles_harvest(self):
        data = self.load()

        p03 = next(
            p for p in data["packages"]
            if p["id"] == "P03"
        )

        required = {
            "GATE8_RESEARCH_HARVEST_HISTORY_RECONCILED_PASS",
            "GATE8_VERIFIED_HARVEST_TRUTH_PRESERVED",
            "HARVEST_CAPABILITY_DISPOSITION_VALID",
            "HARVEST_CAPABILITY_REINVENTED_FALSE",
        }

        self.assertTrue(
            required.issubset(
                set(p03["pass"])
            )
        )

    def test_p04_requires_harvest_disposition(self):
        data = self.load()

        p04 = next(
            p for p in data["packages"]
            if p["id"] == "P04"
        )

        self.assertIn(
            "RESEARCH_HARVEST_CAPABILITY_DISPOSITION_DECLARED",
            p04["pass"],
        )

    def test_zeku_code_mode_defaults_closed(self):
        data = self.load()

        self.assertFalse(
            data["roles"]["zeku"][
                "defaultCodeMode"
            ]
        )

    def test_guard_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(GUARD),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                result.stdout
                + result.stderr
            ),
        )

        payload = json.loads(
            result.stdout
        )

        self.assertEqual(
            payload["state"],
            "PASS",
        )

        self.assertEqual(
            payload["packageCount"],
            12,
        )

        self.assertFalse(
            payload[
                "gate11ExecutionActive"
            ]
        )


if __name__ == "__main__":
    unittest.main()
