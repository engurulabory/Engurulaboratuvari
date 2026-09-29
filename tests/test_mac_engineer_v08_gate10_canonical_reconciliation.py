import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SESSION = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"

G10_EXIT = "V08_FINISHED_PRODUCT_DELIVERY_ACCEPTED"
G11 = "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING"
G11_EXIT = "V08_CONSOLIDATED_MAC_COMMISSIONING_PASS"

ROADMAP_G10 = "V08_GATE_10_FINISHED_PRODUCT_DELIVERY"
ROADMAP_G10_PASS = "V08_GATE_10_FINISHED_PRODUCT_DELIVERY_PASS"
ROADMAP_G11 = "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING"
ROADMAP_G12 = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
PACKAGE08 = "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN"
PACKAGE08_NEXT = "RETURN_RAW_OUTPUT_TO_ZEKU_FOR_CAP18_FINAL_SECOND_LOOK"


class Gate10CanonicalReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = json.loads(SESSION.read_text(encoding="utf-8"))
        cls.roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))

    def test_gate10_is_verified_locked(self):
        closure = self.session["currentV08"]["gate10Closure"]

        self.assertEqual(closure["state"], "VERIFIED_LOCKED")
        self.assertEqual(closure["exit"], G10_EXIT)
        self.assertEqual(closure["humanDecision"], "ACCEPT")
        self.assertTrue(closure["historicalContractPreserved"])

    def test_gate11_to_gate12_authority_is_canonical(self):
        v08 = self.session["currentV08"]
        closure = v08["closureContract"]

        if closure["activeGate"] == 11:
            self.assertEqual(
                self.session["currentObjective"],
                G11,
            )
            self.assertEqual(
                closure["passedGates"],
                list(range(1, 11)),
            )
            self.assertEqual(
                closure["remainingGates"],
                [11, 12],
            )
            self.assertEqual(
                v08["gate11"]["state"],
                "ACTIVE",
            )
            self.assertFalse(
                v08["gate11"]["executionStarted"]
            )
        elif closure["activeGate"] == 12:
            self.assertEqual(
                self.session["currentObjective"],
                ROADMAP_G12,
            )
            self.assertEqual(
                closure["passedGates"],
                list(range(1, 12)),
            )
            self.assertEqual(
                closure["remainingGates"],
                [12],
            )
            self.assertEqual(
                v08["gate11"]["state"],
                "VERIFIED_LOCKED",
            )
            self.assertEqual(
                v08["gate11"]["exit"],
                G11_EXIT,
            )
            self.assertIn(
                v08["gate12"]["state"],
                {"FIELD_ACCEPTED_PENDING_CANONICAL_LOCK",
                 "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"},
            )
            self.assertTrue(
                v08["gate12"]["executionStarted"]
            )
            self.assertFalse(v08["gate12"]["canonicalLockCreated"])
        elif closure["activeGate"] is None:
            self.assertEqual(
                self.session["currentObjective"],
                PACKAGE08,
            )
            self.assertEqual(
                closure["passedGates"],
                list(range(1, 13)),
            )
            self.assertEqual(
                closure["remainingGates"],
                [],
            )
            self.assertEqual(
                v08["gate12"]["state"],
                "VERIFIED_LOCKED",
            )
            self.assertTrue(
                v08["gate12"]["canonicalLockCreated"]
            )
            self.assertEqual(v08["nextAction"], "AWAIT_NEXT_OBJECTIVE")
            self.assertEqual(
                self.session["postV08Objective"]["nextAction"],
                PACKAGE08_NEXT,
            )
        else:
            self.fail(
                "ACTIVE_GATE_MUST_BE_11_12_OR_FINAL"
            )

    def test_roadmap_reconciles_gate10_through_gate12(self):
        current = self.roadmap["current"]

        self.assertIn(
            ROADMAP_G10_PASS,
            current["completed"],
        )
        self.assertNotIn(
            ROADMAP_G10,
            current["remaining"],
        )

        if current["activeGate"] == 11:
            self.assertEqual(
                current["activeObjective"],
                G11,
            )
            self.assertIn(
                ROADMAP_G11,
                current["remaining"],
            )
            self.assertIn(
                ROADMAP_G12,
                current["remaining"],
            )
        elif current["activeGate"] == 12:
            self.assertEqual(
                current["activeObjective"],
                ROADMAP_G12,
            )
            self.assertNotIn(
                ROADMAP_G11,
                current["remaining"],
            )
            self.assertEqual(
                current["remaining"],
                [ROADMAP_G12],
            )
        elif current["activeGate"] is None:
            self.assertEqual(
                current["activeObjective"],
                PACKAGE08,
            )
            self.assertEqual(
                current["remaining"],
                [],
            )
            self.assertEqual(
                current["state"],
                "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED",
            )
            v08 = next(
                item for item in self.roadmap["versions"]
                if item["version"] == "v0.8"
            )
            self.assertEqual(v08["nextAction"], "AWAIT_NEXT_OBJECTIVE")
            self.assertEqual(
                current["postV08Objective"]["nextAction"],
                PACKAGE08_NEXT,
            )
        else:
            self.fail(
                "ROADMAP_ACTIVE_GATE_MUST_BE_11_12_OR_FINAL"
            )


if __name__ == "__main__":
    unittest.main()
