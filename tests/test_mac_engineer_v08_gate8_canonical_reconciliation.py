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


    def test_gate8_progression_remains_monotonic_after_later_gates(self):
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

        roadmap = json.loads(
            (
                root
                / "governance"
                / "mac-engineer"
                / "PRODUCT_ROADMAP_V1.json"
            ).read_text(
                encoding="utf-8"
            )
        )

        closure = (
            session["currentV08"]
            ["closureContract"]
        )

        self.assertIn(
            8,
            closure["passedGates"],
        )

        active_gate = closure["activeGate"]
        if active_gate is None:
            self.assertEqual(
                session["currentV08"]["state"],
                "VERIFIED_LOCKED",
            )
            self.assertEqual(
                closure["passedGates"],
                list(range(1, 13)),
            )
            self.assertEqual(
                closure["remainingGates"],
                [],
            )
        else:
            self.assertGreater(
                active_gate,
                8,
            )

        self.assertNotIn(
            8,
            closure["remainingGates"],
        )

        self.assertIn(
            "V08_GATE_08_NEW_PRODUCT_FROM_BRIEF_PASS",
            roadmap["current"].get("completed") or [],
        )

    def test_current_status_preserves_gate8_historical_closure(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]

        text = (
            root
            / "governance"
            / "mac-engineer"
            / "CURRENT_STATUS.md"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Gate 8",
            text,
        )

    def test_active_path_preserves_gate8_historical_record(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]

        text = (
            root
            / "governance"
            / "mac-engineer"
            / "ACTIVE_WORKING_PATH.md"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Gate 8",
            text,
        )

if __name__ == "__main__":
    unittest.main()
