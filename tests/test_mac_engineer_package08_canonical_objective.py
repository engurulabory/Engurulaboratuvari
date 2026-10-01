from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"
OBJECTIVE = "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN"
NEXT_ACTION = "AWAIT_NEXT_OBJECTIVE"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


class Package08CanonicalObjectiveTests(unittest.TestCase):
    def test_package08_post_v08_objective_is_canonically_bound(self) -> None:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        status = (GOV / "CURRENT_STATUS.md").read_text(encoding="utf-8")
        worklist = (ROOT / "WORKLIST.md").read_text(encoding="utf-8")

        session_campaign = session["postV08Objective"]
        roadmap_campaign = roadmap["current"]["postV08Objective"]

        self.assertEqual(session_campaign, roadmap_campaign)
        self.assertEqual(session_campaign["objective"], OBJECTIVE)
        self.assertEqual(session_campaign["state"], "VERIFIED_CLOSED")
        self.assertEqual(session_campaign["nextAction"], NEXT_ACTION)
        self.assertIn("Predecessor objective:", status)
        self.assertIn(OBJECTIVE, status)
        self.assertIn("VERIFIED_CLOSED", status)

    def test_v08_lock_is_preserved_and_gate12_is_not_reactivated(self) -> None:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        v08 = next(
            item for item in roadmap["versions"] if item["version"] == "v0.8"
        )

        self.assertEqual(session["currentV08"]["state"], "VERIFIED_LOCKED")
        self.assertEqual(session["currentV08"]["nextAction"], "AWAIT_NEXT_OBJECTIVE")
        self.assertEqual(session["currentV08"]["gate12"]["state"], "VERIFIED_LOCKED")
        self.assertIsNone(session["currentV08"]["closureContract"]["activeGate"])
        self.assertEqual(
            roadmap["current"]["postV08Objective"]["state"],
            "VERIFIED_CLOSED",
        )
        self.assertEqual(
            roadmap["current"]["postV08Objective"]["objective"],
            OBJECTIVE,
        )
        self.assertNotEqual(roadmap["current"].get("activeGate"), 12)
        self.assertEqual(v08["state"], "VERIFIED_LOCKED")
        self.assertEqual(v08["nextAction"], "AWAIT_NEXT_OBJECTIVE")

    def test_campaign_truth_preserves_capability_states_and_count(self) -> None:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        ledger = load("CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json")
        campaign = session["postV08Objective"]
        roadmap_campaign = roadmap["current"]["postV08Objective"]
        capabilities = {item["index"]: item for item in ledger["capabilities"]}

        self.assertEqual(ledger["fieldVerifiedCount"], 19)
        self.assertEqual(capabilities[17]["fieldState"], "FIELD_VERIFIED")
        self.assertEqual(
            capabilities[18]["capabilityId"], "FILESYSTEM_MACOS_AUTOMATION"
        )
        self.assertEqual(capabilities[18]["fieldState"], "FIELD_VERIFIED")
        self.assertEqual(capabilities[19]["fieldState"], "FIELD_VERIFIED")
        self.assertTrue(all(capabilities[19]["acceptance"].values()))
        self.assertEqual(campaign, roadmap_campaign)
        self.assertEqual(campaign["state"], "VERIFIED_CLOSED")
        self.assertEqual(campaign["fieldVerifiedCount"], 19)
        self.assertEqual(campaign["activeCapabilityIndex"], 19)
        self.assertEqual(campaign["activeCapabilityState"], "FIELD_VERIFIED")
        self.assertEqual(campaign["lastFieldVerifiedCapabilityIndex"], 19)
        self.assertIsNone(campaign["nextCapabilityIndex"])
        self.assertEqual(campaign["nextCapabilityState"], "CAMPAIGN_CLOSED")
        self.assertEqual(campaign["cap19AttemptCount"], 2)
        self.assertTrue(campaign["cap19RetryBudgetExhausted"])
        self.assertTrue(campaign["cap19DoneCheckPass"])
        self.assertTrue(campaign["cap19FieldSealProduced"])
        self.assertTrue(campaign["campaignDoneCheckPass"])
        self.assertFalse(campaign["v08Reopened"])
        self.assertFalse(campaign["gate12Reactivated"])
        self.assertTrue(campaign["capabilityExecutionPerformed"])
        self.assertFalse(campaign["technicalFieldTaskReexecuted"])
        self.assertFalse(campaign["humanThresholdRegenerated"])


if __name__ == "__main__":
    unittest.main()
