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


    def test_gate9_historical_transition_remains_monotonic(self):
        import json
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]

        session = json.loads(
            (
                root
                / "governance"
                / "mac-engineer"
                / "SESSION_STATE_V1.json"
            ).read_text(
                encoding="utf-8"
            )
        )

        closure = session["currentV08"]["closureContract"]

        self.assertIn(
            9,
            closure["passedGates"],
        )

        self.assertGreater(
            closure["activeGate"],
            9,
        )

        self.assertNotIn(
            9,
            closure["remainingGates"],
        )

    def test_roadmap_preserves_gate9_completion_without_claiming_current_authority(self):
        current = self.roadmap["current"]

        self.assertIn(
            "V08_GATE_09_RELEASE_LIFECYCLE_PASS",
            current.get("completed") or [],
        )

        self.assertNotIn(
            "V08_GATE_09_RELEASE_LIFECYCLE",
            current.get("remaining") or [],
        )

    def test_worklist_preserves_gate10_historical_transition_record(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]

        text = (
            root
            / "WORKLIST.md"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO",
            text,
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
