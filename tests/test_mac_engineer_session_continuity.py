from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.mac_engineer_session_continuity import (
    ROOT,
    STATE_FILE,
    WORKLIST,
    active_objective,
    normalize_objective,
    authorized_product_working_branch,
)


class MacEngineerSessionContinuityTests(unittest.TestCase):
    def test_objective_normalization_tolerates_formatting_only(self):
        self.assertEqual(
            normalize_objective("PRODUCT_CI_EXACT_MAIN_VERIFICATION"),
            normalize_objective("Product CI Exact-Main Verification"),
        )

    def test_worklist_and_session_state_have_one_matching_objective(self):
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        declared = normalize_objective(state["currentObjective"])
        objective = normalize_objective(active_objective())
        self.assertTrue(
            declared in objective or objective in declared,
            (declared, objective),
        )

    def test_continuity_contract_exists(self):
        contract = (
            ROOT
            / "governance"
            / "mac-engineer"
            / "SESSION_CONTINUITY_CONTRACT_V1.md"
        )
        self.assertTrue(contract.is_file())
        text = contract.read_text(encoding="utf-8")
        self.assertIn("SESSION START", text)
        self.assertIn("SESSION HANDOFF", text)
        self.assertIn("One active objective", text)

    def test_authorized_publication_branch_passes_exact_contract(self):
        state = {
            "currentObjective": "PRODUCT_SOURCE_V0_6_ALIGNMENT_PUBLICATION",
            "observedV06AlignmentPreparation": {
                "branch": "feature/v06-version-branding-alignment",
                "commit": "02b7cc3",
                "baseMain": "3ac09bd",
            },
        }
        product = {
            "branch": "feature/v06-version-branding-alignment",
            "head": "02b7cc3",
            "origin_main": "3ac09bd",
            "clean": True,
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertTrue(policy["authorized"])

    def test_authorized_branch_remains_valid_for_merge_objective(self):
        state = {
            "currentObjective": "PRODUCT_PR_EXACT_HEAD_CI_MERGE",
            "observedV06AlignmentPreparation": {
                "branch": "feature/v06-version-branding-alignment",
                "commit": "02b7cc3",
                "baseMain": "3ac09bd",
            },
        }
        product = {
            "branch": "feature/v06-version-branding-alignment",
            "head": "02b7cc3",
            "origin_main": "3ac09bd",
            "clean": True,
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertTrue(policy["authorized"])

    def test_unrecorded_product_branch_is_not_authorized(self):
        state = {
            "currentObjective": "PRODUCT_SOURCE_V0_6_ALIGNMENT_PUBLICATION",
            "observedV06AlignmentPreparation": {
                "branch": "feature/v06-version-branding-alignment",
                "commit": "02b7cc3",
                "baseMain": "3ac09bd",
            },
        }
        product = {
            "branch": "feature/other",
            "head": "02b7cc3",
            "origin_main": "3ac09bd",
            "clean": True,
        }
        authorized, _ = authorized_product_working_branch(
            state,
            product,
        )
        self.assertFalse(authorized)

    def test_worklist_is_canonical_source(self):
        self.assertTrue(WORKLIST.is_file())
        self.assertIn(
            "**Current single objective:**",
            WORKLIST.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
