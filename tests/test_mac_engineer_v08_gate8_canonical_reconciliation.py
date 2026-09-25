import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SESSION = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "SESSION_STATE_V1.json"
)

ROADMAP = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "PRODUCT_ROADMAP_V1.json"
)

CURRENT_STATUS = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "CURRENT_STATUS.md"
)

ACTIVE_PATH = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "ACTIVE_WORKING_PATH.md"
)

G10 = "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO"


class Gate8CanonicalReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )

        self.roadmap = json.loads(
            ROADMAP.read_text(encoding="utf-8")
        )

        self.v08 = self.state["currentV08"]

    def test_gate8_historical_closure_is_preserved(self):
        closure = self.v08["gate8Closure"]

        self.assertEqual(
            closure["state"],
            "VERIFIED_PASS",
        )

        self.assertEqual(
            closure["exit"],
            "V08_NEW_PRODUCT_FROM_BRIEF_VERIFIED",
        )

    def test_gate8_contract_remains_present(self):
        gate8 = self.v08["gate8"]

        self.assertEqual(
            gate8["name"],
            "V08_NEW_PRODUCT_FROM_BRIEF_SCENARIO",
        )

        self.assertEqual(
            gate8["humanBriefLock"]["state"],
            "LOCKED",
        )

    def test_gate10_is_current_structured_truth(self):
        self.assertEqual(
            self.state["currentObjective"],
            G10,
        )

        self.assertEqual(
            self.v08["closureContract"]["activeGate"],
            10,
        )

        self.assertEqual(
            self.roadmap["current"]["activeObjective"],
            G10,
        )

    def test_current_status_points_to_gate10(self):
        text = CURRENT_STATUS.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            f"**Current objective:** {G10}",
            text[:3000],
        )

    def test_active_path_records_gate10(self):
        text = ACTIVE_PATH.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "ENGURU_V08_GATE9_CANONICAL_RECONCILIATION_V1",
            text,
        )

        self.assertIn(
            G10,
            text,
        )


if __name__ == "__main__":
    unittest.main()
