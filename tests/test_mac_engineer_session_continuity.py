from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.mac_engineer_session_continuity import (
    ROOT,
    STATE_FILE,
    CURRENT_STATUS,
    WORKLIST,
    active_objective,
    normalize_objective,
    authorized_product_working_branch,
    porcelain_paths,
)


class MacEngineerSessionContinuityTests(unittest.TestCase):
    def test_post_lock_objective_alignment_contract(self) -> None:
        import json

        root = Path(__file__).resolve().parents[1]
        session = json.loads(
            (root / "governance/mac-engineer/SESSION_STATE_V1.json").read_text(
                encoding="utf-8"
            )
        )
        roadmap = json.loads(
            (root / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json").read_text(
                encoding="utf-8"
            )
        )
        worklist = (root / "WORKLIST.md").read_text(encoding="utf-8")

        expected = "V0_7_VERIFIED_LOCKED_AWAIT_NEXT_OBJECTIVE"
        self.assertEqual(session["currentObjective"], expected)
        self.assertEqual(roadmap["current"]["activeObjective"], expected)
        self.assertIn(
            f"**Current single objective:** **{expected}**.",
            worklist,
        )

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

    def test_current_status_is_canonical_bootstrap_surface(self):
        self.assertTrue(CURRENT_STATUS.is_file())
        text = CURRENT_STATUS.read_text(encoding="utf-8")
        self.assertIn("CURRENT ENGINEERING TRUTH", text)
        self.assertIn("REMAINING v0.6 CLOSEOUT", text)
        self.assertIn("NEXT ACTION", text)
        self.assertIn("CONTINUITY_PATCH_REPEATABILITY", text)

    def test_current_status_update_is_mandatory_after_each_material_result(self):
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        rule = state["currentStatusUpdateRule"]
        self.assertEqual(rule["state"], "MANDATORY")
        self.assertEqual(rule["timing"], "BEFORE_NEXT_ACTION")
        self.assertIn("LATEST_EVIDENCE", rule["requiredFields"])
        self.assertIn("NEXT_ACTION", rule["requiredFields"])

        contract = (
            ROOT
            / "governance"
            / "mac-engineer"
            / "SESSION_CONTINUITY_CONTRACT_V1.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Current Status mandatory update invariant", contract)
        self.assertIn(
            "after every material engineering package",
            contract.lower(),
        )

        status = CURRENT_STATUS.read_text(encoding="utf-8")
        self.assertIn("MAINTENANCE RULE", status)
        self.assertIn("before the next action", status)

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

    def test_porcelain_paths_preserves_first_modified_path_after_strip(self):
        status = (
            "M runtime/app.py\n"
            " M runtime/field_reliability.py\n"
            "?? runtime/tests/test_field_continuity_binding.py"
        )
        self.assertEqual(
            porcelain_paths(status),
            [
                "runtime/app.py",
                "runtime/field_reliability.py",
                "runtime/tests/test_field_continuity_binding.py",
            ],
        )

    def test_continuity_patch_allows_exact_bounded_dirty_set(self):
        state = {
            "currentObjective": "CONTINUITY_PATCH_REPEATABILITY",
            "observedContinuityPatch": {
                "branch": "fix/v06-durable-continuity-binding",
                "head": "6f424c0",
                "baseMain": "6f424c0",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_continuity_binding.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-durable-continuity-binding",
            "head": "6f424c0",
            "origin_main": "6f424c0",
            "exact_origin_main": True,
            "clean": False,
            "status": (
                " M runtime/app.py\n"
                " M runtime/field_reliability.py\n"
                "?? runtime/tests/test_field_continuity_binding.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(state, product)
        self.assertTrue(authorized)
        self.assertEqual(policy["mode"], "IN_FLIGHT_PATCH")
        self.assertEqual(
            policy["observed_dirty_paths"],
            sorted(state["observedContinuityPatch"]["expectedDirtyPaths"]),
        )

    def test_product_patch_github_engineering_keeps_exact_inflight_patch_authorized(self):
        state = {
            "currentObjective": "PRODUCT_PATCH_GITHUB_ENGINEERING",
            "observedContinuityPatch": {
                "branch": "fix/v06-durable-continuity-binding",
                "head": "6f424c0",
                "baseMain": "6f424c0",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_continuity_binding.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-durable-continuity-binding",
            "head": "6f424c0",
            "origin_main": "6f424c0",
            "exact_origin_main": True,
            "clean": False,
            "status": (
                " M runtime/app.py\n"
                " M runtime/field_reliability.py\n"
                "?? runtime/tests/test_field_continuity_binding.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(state, product)
        self.assertTrue(authorized)
        self.assertEqual(policy["mode"], "IN_FLIGHT_PATCH")

    def test_product_patch_github_engineering_allows_exact_clean_single_commit(self):
        state = {
            "currentObjective": "PRODUCT_PATCH_GITHUB_ENGINEERING",
            "observedContinuityPatch": {
                "branch": "fix/v06-durable-continuity-binding",
                "head": "6f424c0",
                "baseMain": "6f424c0",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_continuity_binding.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-durable-continuity-binding",
            "head": "abc1234",
            "origin_main": "6f424c0",
            "exact_origin_main": False,
            "clean": True,
            "status": "",
            "merge_base_origin_main": "6f424c0",
            "ahead_origin_main": "1",
            "diff_names_origin_main": (
                "runtime/app.py\n"
                "runtime/field_reliability.py\n"
                "runtime/tests/test_field_continuity_binding.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(state, product)
        self.assertTrue(authorized)
        self.assertEqual(
            policy["mode"],
            "COMMITTED_PATCH_AWAITING_PR",
        )

    def test_product_patch_github_engineering_rejects_extra_committed_path(self):
        state = {
            "currentObjective": "PRODUCT_PATCH_GITHUB_ENGINEERING",
            "observedContinuityPatch": {
                "branch": "fix/v06-durable-continuity-binding",
                "head": "6f424c0",
                "baseMain": "6f424c0",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_continuity_binding.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-durable-continuity-binding",
            "head": "abc1234",
            "origin_main": "6f424c0",
            "exact_origin_main": False,
            "clean": True,
            "status": "",
            "merge_base_origin_main": "6f424c0",
            "ahead_origin_main": "1",
            "diff_names_origin_main": (
                "runtime/app.py\n"
                "runtime/field_reliability.py\n"
                "runtime/tests/test_field_continuity_binding.py\n"
                "runtime/unexpected.py"
            ),
        }
        authorized, _ = authorized_product_working_branch(state, product)
        self.assertFalse(authorized)

    def test_continuity_patch_rejects_unexpected_dirty_path(self):
        state = {
            "currentObjective": "CONTINUITY_PATCH_REPEATABILITY",
            "observedContinuityPatch": {
                "branch": "fix/v06-durable-continuity-binding",
                "head": "6f424c0",
                "baseMain": "6f424c0",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_continuity_binding.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-durable-continuity-binding",
            "head": "6f424c0",
            "origin_main": "6f424c0",
            "exact_origin_main": True,
            "clean": False,
            "status": (
                " M runtime/app.py\n"
                " M runtime/field_reliability.py\n"
                "?? runtime/tests/test_field_continuity_binding.py\n"
                "?? runtime/unexpected.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(state, product)
        self.assertFalse(authorized)
        self.assertIn("runtime/unexpected.py", policy["observed_dirty_paths"])

    def test_context_durability_patch_allows_exact_dirty_set(self):
        state = {
            "currentObjective": "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            "observedContextDurabilityPatch": {
                "branch": "fix/v06-context-durability-resume-routing",
                "head": "6d2fcd9",
                "baseMain": "6d2fcd9",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/cockpit_store.py",
                    "runtime/field_reliability.py",
                    "runtime/static/index.html",
                    "runtime/tests/test_context_durability.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-context-durability-resume-routing",
            "head": "6d2fcd9",
            "origin_main": "6d2fcd9",
            "exact_origin_main": True,
            "clean": False,
            "status": (
                " M runtime/app.py\n"
                " M runtime/cockpit_store.py\n"
                " M runtime/field_reliability.py\n"
                " M runtime/static/index.html\n"
                "?? runtime/tests/test_context_durability.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertEqual(policy["mode"], "IN_FLIGHT_PATCH")

    def test_context_durability_patch_allows_exact_clean_single_commit(self):
        state = {
            "currentObjective": "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            "observedContextDurabilityPatch": {
                "branch": "fix/v06-context-durability-resume-routing",
                "head": "6d2fcd9",
                "baseMain": "6d2fcd9",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/cockpit_store.py",
                    "runtime/field_reliability.py",
                    "runtime/static/index.html",
                    "runtime/tests/test_context_durability.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-context-durability-resume-routing",
            "head": "abc1234",
            "origin_main": "6d2fcd9",
            "exact_origin_main": False,
            "clean": True,
            "status": "",
            "merge_base_origin_main": "6d2fcd9",
            "ahead_origin_main": "1",
            "diff_names_origin_main": (
                "runtime/app.py\n"
                "runtime/cockpit_store.py\n"
                "runtime/field_reliability.py\n"
                "runtime/static/index.html\n"
                "runtime/tests/test_context_durability.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertEqual(
            policy["mode"],
            "COMMITTED_PATCH_AWAITING_PR",
        )

    def test_context_durability_patch_rejects_extra_path(self):
        state = {
            "currentObjective": "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            "observedContextDurabilityPatch": {
                "branch": "fix/v06-context-durability-resume-routing",
                "head": "6d2fcd9",
                "baseMain": "6d2fcd9",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/cockpit_store.py",
                    "runtime/field_reliability.py",
                    "runtime/static/index.html",
                    "runtime/tests/test_context_durability.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06/context-other",
            "head": "6d2fcd9",
            "origin_main": "6d2fcd9",
            "exact_origin_main": True,
            "clean": False,
            "status": "?? runtime/unexpected.py",
        }
        authorized, _ = authorized_product_working_branch(
            state,
            product,
        )
        self.assertFalse(authorized)

    def test_fresh_resume_patch_allows_exact_dirty_set(self):
        state = {
            "currentObjective": "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            "observedFreshResumeVerificationPatch": {
                "branch": "fix/v06-fresh-resume-verification",
                "head": "125be3a",
                "baseMain": "125be3a",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_resume_verification.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-fresh-resume-verification",
            "head": "125be3a",
            "origin_main": "125be3a",
            "exact_origin_main": True,
            "clean": False,
            "status": (
                " M runtime/app.py\n"
                " M runtime/field_reliability.py\n"
                "?? runtime/tests/test_field_resume_verification.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertEqual(policy["mode"], "IN_FLIGHT_PATCH")

    def test_fresh_resume_patch_allows_exact_clean_single_commit(self):
        state = {
            "currentObjective": "CHECKPOINT_RESTART_RESUME_FIELD_PROOF",
            "observedFreshResumeVerificationPatch": {
                "branch": "fix/v06-fresh-resume-verification",
                "head": "125be3a",
                "baseMain": "125be3a",
                "expectedDirtyPaths": [
                    "runtime/app.py",
                    "runtime/field_reliability.py",
                    "runtime/tests/test_field_resume_verification.py",
                ],
            },
        }
        product = {
            "branch": "fix/v06-fresh-resume-verification",
            "head": "abc1234",
            "origin_main": "125be3a",
            "exact_origin_main": False,
            "clean": True,
            "status": "",
            "merge_base_origin_main": "125be3a",
            "ahead_origin_main": "1",
            "diff_names_origin_main": (
                "runtime/app.py\n"
                "runtime/field_reliability.py\n"
                "runtime/tests/test_field_resume_verification.py"
            ),
        }
        authorized, policy = authorized_product_working_branch(
            state,
            product,
        )
        self.assertTrue(authorized)
        self.assertEqual(
            policy["mode"],
            "COMMITTED_PATCH_AWAITING_PR",
        )

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
