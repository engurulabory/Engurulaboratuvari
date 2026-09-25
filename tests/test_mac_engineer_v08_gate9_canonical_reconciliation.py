import json
import re
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

WORKLIST = ROOT / "WORKLIST.md"

MATRIX = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_PRODUCT_ENGINEERING_OPERATOR_ACCEPTANCE_MATRIX_V1.md"
)

G9 = "V08_RELEASE_LIFECYCLE_SCENARIO"
G9_EXIT = "V08_RELEASE_LIFECYCLE_VERIFIED"
G10 = "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO"


class Gate9CanonicalReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )

        self.roadmap = json.loads(
            ROADMAP.read_text(encoding="utf-8")
        )

        self.v08 = self.state["currentV08"]

    def test_gate9_contract_is_preserved(self):
        self.assertEqual(
            self.v08["gate9"]["name"],
            G9,
        )

        self.assertEqual(
            self.v08["gate9"]["exit"],
            G9_EXIT,
        )

    def test_gate9_closure_is_verified_locked(self):
        closure = self.v08["gate9Closure"]

        self.assertEqual(
            closure["state"],
            "VERIFIED_LOCKED",
        )

        self.assertEqual(
            closure["exit"],
            G9_EXIT,
        )

        self.assertEqual(
            closure["doneCheck"],
            "PASS",
        )

        self.assertEqual(
            closure["verifiedFinish"],
            "PASS",
        )

        self.assertEqual(
            closure["humanThreshold"],
            "CLEAR",
        )

    def test_gate10_is_current_authority(self):
        closure = self.v08["closureContract"]

        self.assertEqual(
            closure["passedGates"],
            list(range(1, 10)),
        )

        self.assertEqual(
            closure["activeGate"],
            10,
        )

        self.assertEqual(
            closure["remainingGates"],
            [10, 11, 12],
        )

        self.assertEqual(
            self.state["currentObjective"],
            G10,
        )

        self.assertEqual(
            self.v08["gate10"]["state"],
            "ACTIVE",
        )

    def test_roadmap_current_is_gate10(self):
        current = self.roadmap["current"]

        self.assertEqual(
            current["activeObjective"],
            G10,
        )

        self.assertIn(
            "V08_GATE_09_RELEASE_LIFECYCLE_PASS",
            current["completed"],
        )

    def test_worklist_current_objectives_are_gate10(self):
        text = WORKLIST.read_text(
            encoding="utf-8"
        )

        active = re.findall(
            r"\*\*Active objective:\*\*\s*`([^`]+)`",
            text,
        )

        single = re.findall(
            (
                r"\*\*Current single objective:\*\*"
                r"\s+\*\*(.+?)\*\*\."
            ),
            text,
        )

        self.assertTrue(active)
        self.assertTrue(single)

        self.assertEqual(
            active[-1],
            G10,
        )

        self.assertEqual(
            single[-1],
            G10,
        )

    def test_acceptance_matrix_records_gate9_closure(self):
        text = MATRIX.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "GATE9_CANONICAL_CLOSURE_2026_09_25",
            text,
        )

        self.assertIn(
            G9_EXIT,
            text,
        )


if __name__ == "__main__":
    unittest.main()
