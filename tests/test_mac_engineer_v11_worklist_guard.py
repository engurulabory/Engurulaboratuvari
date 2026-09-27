from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WORKLIST = ROOT / "governance/mac-engineer/V11_100_POINT_CANONICAL_WORKLIST_V1.md"
ACCEPTANCE = ROOT / "governance/mac-engineer/V11_100_POINT_CANONICAL_WORKLIST_ACCEPTANCE_V1.json"
GUARD = ROOT / "tools/mac_engineer_v11_worklist_guard.py"


class V11WorklistGuardTests(unittest.TestCase):
    def test_worklist_has_exactly_100_explicit_points(self):
        text = WORKLIST.read_text(encoding="utf-8")

        ids = re.findall(
            r"^- \[ \] \*\*(\d{3})\.",
            text,
            flags=re.MULTILINE,
        )

        self.assertEqual(
            ids,
            [f"{i:03d}" for i in range(1, 101)],
        )

    def test_prepared_worklist_is_not_active(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["state"],
            "PREPARED_QUEUED",
        )
        self.assertFalse(data["executionActive"])
        self.assertEqual(data["completedPoints"], 0)
        self.assertEqual(data["remainingPoints"], 100)

    def test_critical_invariants_are_locked(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        inv = data["criticalInvariants"]

        self.assertEqual(
            inv["unsupportedCanonicalClaimMax"],
            0,
        )
        self.assertEqual(
            inv["criticalFalsePassMax"],
            0,
        )
        self.assertEqual(
            inv["humanThresholdMissMax"],
            0,
        )
        self.assertEqual(
            inv["criticalSourceProvenanceCoverage"],
            1.0,
        )

    def test_guard_passes_current_preparation(self):
        result = subprocess.run(
            [sys.executable, str(GUARD)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr,
        )

        payload = json.loads(result.stdout)

        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(payload["pointCount"], 100)
        self.assertFalse(payload["executionActive"])


if __name__ == "__main__":
    unittest.main()
