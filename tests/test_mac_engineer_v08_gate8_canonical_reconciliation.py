from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SESSION = (
    ROOT
    / "governance/mac-engineer/SESSION_STATE_V1.json"
)

ROADMAP = (
    ROOT
    / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
)

STATUS = (
    ROOT
    / "governance/mac-engineer/CURRENT_STATUS.md"
)

ACTIVE = (
    ROOT
    / "governance/mac-engineer/ACTIVE_WORKING_PATH.md"
)


class Gate8CanonicalReconciliationTests(unittest.TestCase):
    def test_session_state_gate9_is_current_truth(self):
        import json
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]

        state = json.loads(
            (
                root
                / "governance/mac-engineer/SESSION_STATE_V1.json"
            ).read_text(encoding="utf-8")
        )

        roadmap = json.loads(
            (
                root
                / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
            ).read_text(encoding="utf-8")
        )

        worklist = (
            root / "WORKLIST.md"
        ).read_text(encoding="utf-8")

        expected = "V08_RELEASE_LIFECYCLE_SCENARIO"

        self.assertEqual(
            state["currentObjective"],
            expected,
        )

        self.assertEqual(
            roadmap["current"]["activeObjective"],
            expected,
        )

        current_v08 = state["currentV08"]
        closure = current_v08["closureContract"]

        self.assertEqual(
            closure["passedGates"],
            [1, 2, 3, 4, 5, 6, 7, 8],
        )

        self.assertEqual(
            closure["activeGate"],
            9,
        )

        self.assertEqual(
            closure["remainingGates"],
            [9, 10, 11, 12],
        )

        gate8 = current_v08["gate8"]

        self.assertIn(
            "humanBriefLock",
            gate8,
        )

        self.assertEqual(
            gate8["nextAction"],
            "GATE8_RESEARCH_HARVEST_ARCHITECTURE_VERTICAL_SLICE",
        )

        gate8_closure = current_v08["gate8Closure"]

        self.assertEqual(
            gate8_closure["state"],
            "VERIFIED_PASS",
        )

        self.assertEqual(
            gate8_closure["exit"],
            "V08_NEW_PRODUCT_FROM_BRIEF_VERIFIED",
        )

        gate9 = current_v08["gate9"]

        self.assertEqual(
            gate9["state"],
            "ACTIVE",
        )

        self.assertEqual(
            gate9["previousGate"],
            "V08_NEW_PRODUCT_FROM_BRIEF_VERIFIED",
        )

        self.assertEqual(
            gate9["exit"],
            "V08_RELEASE_LIFECYCLE_VERIFIED",
        )

        self.assertIn(
            "**Active objective:** "
            "`V08_RELEASE_LIFECYCLE_SCENARIO`",
            worklist,
        )

        self.assertIn(
            "**Current single objective:** "
            "**V08_RELEASE_LIFECYCLE_SCENARIO**.",
            worklist,
        )

        self.assertIn(
            "8. [x] **Gate 8 — New Product from Brief "
            "Scenario — PASS / SEALED**",
            worklist,
        )

        self.assertIn(
            "9. [ ] **Gate 9 — Deploy / Live Verify / "
            "Rollback + Lifecycle — ACTIVE**",
            worklist,
        )


    def test_session_state_matches_product_roadmap_gate_truth(self):
        state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )
        roadmap = json.loads(
            ROADMAP.read_text(encoding="utf-8")
        )

        version = next(
            item
            for item in roadmap["versions"]
            if item["version"] == "v0.8"
        )

        contract = version["verifiedFinishContract"]
        closure = state["currentV08"]["closureContract"]

        self.assertEqual(
            roadmap["current"]["activeObjective"],
            state["currentObjective"],
        )
        self.assertEqual(
            contract["passed"],
            closure["passedGates"],
        )
        self.assertEqual(
            contract["active"],
            closure["activeGate"],
        )
        self.assertEqual(
            contract["remaining"],
            closure["remainingGates"],
        )

    def test_reconnaissance_truth_is_recorded(self):
        state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )

        recon = state["currentV08"]["gate8Reconnaissance"]

        self.assertEqual(recon["state"], "PASS")
        self.assertEqual(
            recon["researchTransportState"],
            "MEVCUT_NOT_YET_FIELD_VERIFIED",
        )
        self.assertEqual(
            recon["operatorRegistryGate8Handler"],
            "ABSENT_NOT_YET_PROVEN_REQUIRED",
        )
        self.assertFalse(
            recon["newCoreRequired"]
        )

    def test_active_working_path_boot_points_to_gate8(self):
        text = ACTIVE.read_text(encoding="utf-8")
        state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )

        boot_start = text.index(
            "## NEXT SESSION BOOT — V0.8"
        )
        boot_end = text.index(
            "## Mandatory Pre-Output ENGÜRÜ Filter",
            boot_start,
        )
        boot = text[boot_start:boot_end]

        self.assertIn(
            "`Gate 8 — New Product from Brief Scenario`",
            boot,
        )
        self.assertIn(
            "`V08_NEW_PRODUCT_FROM_BRIEF_SCENARIO`",
            boot,
        )
        self.assertIn(
            f"`{state['nextAction']}`",
            boot,
        )
        self.assertIn(
            "## Gate 8 Phase A Canonical Reconciliation",
            text,
        )

    def test_current_status_top_truth_points_to_gate8(self):
        text = STATUS.read_text(encoding="utf-8")
        top = text[:5000]

        self.assertIn(
            "Gate 8 — New Product from Brief Scenario",
            top,
        )
        self.assertIn(
            "Gates 1–7 are verified PASS",
            top,
        )
        self.assertIn(
            "`V08_NEW_PRODUCT_FROM_BRIEF_SCENARIO`",
            top,
        )


if __name__ == "__main__":
    unittest.main()
