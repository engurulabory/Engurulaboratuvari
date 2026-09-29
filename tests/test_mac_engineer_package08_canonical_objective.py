from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"
OBJECTIVE = "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN"
NEXT_ACTION = "RETURN_RAW_OUTPUT_TO_ZEKU_FOR_CAP18_FINAL_SECOND_LOOK"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


class Package08CanonicalObjectiveTests(unittest.TestCase):
    def test_package08_post_v08_objective_is_canonically_bound(self) -> None:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        status = (GOV / "CURRENT_STATUS.md").read_text(encoding="utf-8")
        worklist = (ROOT / "WORKLIST.md").read_text(encoding="utf-8")

        self.assertEqual(session["currentObjective"], OBJECTIVE)
        self.assertEqual(session["nextAction"], NEXT_ACTION)
        self.assertEqual(roadmap["current"]["activeObjective"], OBJECTIVE)
        self.assertEqual(roadmap["current"]["nextAction"], NEXT_ACTION)
        self.assertIn(f"**Active objective:** `{OBJECTIVE}`", worklist)
        self.assertIn(f"**Current single objective:** **{OBJECTIVE}**.", worklist)
        self.assertIn(f"`CURRENT_OBJECTIVE={OBJECTIVE}`", status)
        self.assertIn(f"`{NEXT_ACTION}`", status)

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
            roadmap["current"]["state"],
            "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED",
        )
        self.assertIsNone(roadmap["current"]["activeGate"])
        self.assertEqual(v08["state"], "VERIFIED_LOCKED")
        self.assertEqual(v08["nextAction"], "AWAIT_NEXT_OBJECTIVE")

    def test_campaign_truth_preserves_capability_states_and_count(self) -> None:
        session = load("SESSION_STATE_V1.json")
        roadmap = load("PRODUCT_ROADMAP_V1.json")
        ledger = load("CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json")
        campaign = session["postV08Objective"]
        roadmap_campaign = roadmap["current"]["postV08Objective"]
        capabilities = {item["index"]: item for item in ledger["capabilities"]}

        self.assertEqual(ledger["fieldVerifiedCount"], 18)
        self.assertEqual(capabilities[17]["fieldState"], "FIELD_VERIFIED")
        self.assertEqual(
            capabilities[18]["capabilityId"], "FILESYSTEM_MACOS_AUTOMATION"
        )
        self.assertEqual(capabilities[18]["fieldState"], "FIELD_VERIFIED")
        self.assertEqual(capabilities[19]["fieldState"], "PENDING")
        self.assertEqual(campaign, roadmap_campaign)
        self.assertEqual(campaign["fieldVerifiedCount"], 18)
        self.assertIsNone(campaign["activeCapabilityIndex"])
        self.assertIsNone(campaign["activeCapabilityState"])
        self.assertEqual(campaign["lastFieldVerifiedCapabilityIndex"], 18)
        self.assertEqual(campaign["nextCapabilityIndex"], 19)
        self.assertEqual(campaign["nextCapabilityState"], "PENDING")
        self.assertFalse(campaign["v08Reopened"])
        self.assertFalse(campaign["gate12Reactivated"])
        self.assertTrue(campaign["capabilityExecutionPerformed"])
        self.assertFalse(campaign["technicalFieldTaskReexecuted"])
        self.assertFalse(campaign["humanThresholdRegenerated"])


if __name__ == "__main__":
    unittest.main()
