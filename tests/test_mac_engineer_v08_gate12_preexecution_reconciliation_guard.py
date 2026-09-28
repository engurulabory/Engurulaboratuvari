from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import tools.mac_engineer_v08_gate12_preexecution_reconciliation_guard as guard


class Gate12PreexecutionReconciliationGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = guard.load_json(guard.SESSION)
        cls.roadmap = guard.load_json(guard.ROADMAP)
        cls.status = guard.STATUS.read_text(encoding="utf-8")
        cls.working_path = guard.WORKING_PATH.read_text(encoding="utf-8")
        cls.worklist = guard.WORKLIST.read_text(encoding="utf-8")
        cls.acceptance = guard.ACCEPTANCE.read_text(encoding="utf-8")
        cls.product_truth = guard.current_product_truth()

    def evaluate(self, **overrides):
        values = {
            "session": deepcopy(self.session),
            "roadmap": deepcopy(self.roadmap),
            "status": self.status,
            "working_path": self.working_path,
            "worklist": self.worklist,
            "acceptance": self.acceptance,
            "product_truth": deepcopy(self.product_truth),
        }
        values.update(overrides)
        return guard.evaluate(**values)

    def test_current_repository_is_gate12_preexecution_reconciled(self):
        result = self.evaluate()
        self.assertEqual(result["state"], "PASS", result["failed"])
        self.assertEqual(result["gate12ExecutionStarted"], 0)
        self.assertEqual(result["productSourceMutationCount"], 0)
        self.assertFalse(result["newCore"])

    def test_gate12_started_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["gate12"]["executionStarted"] = True
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("SESSION_GATE12_ACTIVE_NOT_STARTED", result["failed"])

    def test_gate11_not_locked_with_gate12_active_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["gate11"]["state"] = "ACTIVE"
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("SESSION_GATE11_VERIFIED_LOCKED", result["failed"])

    def test_product_head_mismatch_fails_closed(self):
        product_truth = deepcopy(self.product_truth)
        product_truth["head"] = "incorrect-product-head"
        result = self.evaluate(product_truth=product_truth)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("PRODUCT_REPOSITORY_UNCHANGED", result["failed"])

    def test_final_target_not_v13_fails_closed(self):
        roadmap = deepcopy(self.roadmap)
        roadmap["finalTarget"]["version"] = "v1.2"
        result = self.evaluate(roadmap=roadmap)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("ROADMAP_FINAL_TARGET_V13", result["failed"])

    def test_worklist_objective_mismatch_with_marker_retained_fails_closed(self):
        worklist = self.worklist.replace(
            "**Active objective:** "
            "`V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK`",
            "**Active objective:** `V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING`",
            1,
        ).replace(
            "**Current single objective:** "
            "**V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK**.",
            "**Current single objective:** "
            "**V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING**.",
            1,
        )
        self.assertIn(guard.CURRENT_OBJECTIVE_MARKER, worklist)
        result = self.evaluate(worklist=worklist)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("WORKLIST_EXACT_CURRENT_OBJECTIVE", result["failed"])

    def test_worklist_authoritative_current_objective_missing_fails_closed(self):
        worklist = self.worklist.replace(
            "**Active objective:** "
            "`V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK`\n",
            "",
            1,
        ).replace(
            "**Current single objective:** "
            "**V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK**.\n",
            "",
            1,
        )
        self.assertIn(guard.CURRENT_OBJECTIVE_MARKER, worklist)
        result = self.evaluate(worklist=worklist)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("WORKLIST_EXACT_CURRENT_OBJECTIVE", result["failed"])

    def test_conflicting_worklist_current_projection_fails_closed(self):
        worklist = self.worklist.replace(
            guard.CURRENT_OBJECTIVE_MARKER,
            guard.CURRENT_OBJECTIVE_MARKER
            + "\n`CURRENT_OBJECTIVE=V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING`",
            1,
        )
        result = self.evaluate(worklist=worklist)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("WORKLIST_EXACT_CURRENT_OBJECTIVE", result["failed"])

    def test_gate6_historical_evidence_missing_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["gate6"].pop("evidence")
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn(
            "SESSION_GATE6_HISTORICAL_EVIDENCE_PRESERVED",
            result["failed"],
        )

    def test_gate10_historical_evidence_missing_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["gate10Closure"].pop("evidence")
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn(
            "SESSION_GATE10_HISTORICAL_EVIDENCE_PRESERVED",
            result["failed"],
        )

    def test_gate11_historical_evidence_identity_change_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["gate11"]["closureEvidence"] = "changed-evidence"
        session["currentV08"]["gate11Closure"]["evidence"] = "changed-evidence"
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn(
            "SESSION_GATE11_HISTORICAL_EVIDENCE_PRESERVED",
            result["failed"],
        )

    def test_exact_worklist_and_gate6_11_evidence_pass(self):
        result = self.evaluate()
        self.assertTrue(result["checks"]["WORKLIST_EXACT_CURRENT_OBJECTIVE"])
        for gate in range(6, 12):
            self.assertTrue(
                result["checks"][
                    f"SESSION_GATE{gate}_HISTORICAL_EVIDENCE_PRESERVED"
                ]
            )

    def test_product_remote_parity_claim_fails_closed(self):
        session = deepcopy(self.session)
        session["currentV08"]["currentProductSource"]["remoteParity"] = True
        result = self.evaluate(session=session)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("SESSION_PRODUCT_SOURCE_CURRENT", result["failed"])

    def test_gate12_acceptance_semantic_loss_fails_closed(self):
        acceptance = self.acceptance.replace(
            "- Human Threshold™ explicitly accepts;",
            "",
        )
        result = self.evaluate(acceptance=acceptance)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("GATE12_ACCEPTANCE_SEMANTICS_PRESERVED", result["failed"])

    def test_v12_milestone_loss_fails_closed(self):
        roadmap = deepcopy(self.roadmap)
        roadmap["versions"] = [
            item for item in roadmap["versions"] if item["version"] != "v1.2"
        ]
        result = self.evaluate(roadmap=roadmap)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("V12_VERSION_PATH_MILESTONE_PRESERVED", result["failed"])

    def test_guard_has_no_evidence_writer(self):
        source = Path(guard.__file__).read_text(encoding="utf-8")
        self.assertNotIn("write_text(", source)
        self.assertNotIn("mkdir(", source)


if __name__ == "__main__":
    unittest.main()
