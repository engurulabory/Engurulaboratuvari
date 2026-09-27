from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROADMAP = (
    ROOT
    / "governance/mac-engineer/"
      "PRODUCT_ROADMAP_V1.json"
)

ACCEPTANCE = (
    ROOT
    / "governance/mac-engineer/"
      "V13_AESTHETIC_MOTOR_ACCEPTANCE_V1.json"
)

GUARD = ROOT / "tools/mac_engineer_v13_aesthetic_guard.py"


class V13AestheticGuardTests(unittest.TestCase):

    def test_v13_is_final_target(self):
        roadmap = json.loads(
            ROADMAP.read_text(encoding="utf-8")
        )

        self.assertEqual(
            roadmap["finalTarget"]["version"],
            "v1.3",
        )

        self.assertIn(
            "V13_AESTHETIC_MOTOR_VERIFIED_FINISH",
            roadmap["finalTarget"]["requiredPreconditions"],
        )

    def test_v13_exit_requires_aesthetic_finish(self):
        roadmap = json.loads(
            ROADMAP.read_text(encoding="utf-8")
        )

        v13 = next(
            item
            for item in roadmap["versions"]
            if item["version"] == "v1.3"
        )

        self.assertIn(
            "V13_AESTHETIC_MOTOR_VERIFIED_FINISH",
            v13["exit"],
        )

    def test_acceptance_contract_is_fail_closed(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["requiredVerdict"],
            "V13_AESTHETIC_MOTOR_VERIFIED_FINISH",
        )

        self.assertGreaterEqual(
            len(data["criteria"]),
            12,
        )

    def test_guard_matches_acceptance_state(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        complete = all(
            item.get("state") == "PASS"
            and bool(item.get("evidence"))
            for item in data["criteria"].values()
        )

        result = subprocess.run(
            [
                sys.executable,
                str(GUARD),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(
            result.returncode,
            0 if complete else 2,
        )


if __name__ == "__main__":
    unittest.main()
