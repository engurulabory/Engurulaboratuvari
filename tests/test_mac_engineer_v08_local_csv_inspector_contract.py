from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "governance/mac-engineer/"
      "V08_GATE8_LOCAL_CSV_INSPECTOR_TASK_CONTRACT_V1.json"
)

SESSION = (
    ROOT
    / "governance/mac-engineer/SESSION_STATE_V1.json"
)

STATUS = (
    ROOT
    / "governance/mac-engineer/CURRENT_STATUS.md"
)

ACTIVE = (
    ROOT
    / "governance/mac-engineer/ACTIVE_WORKING_PATH.md"
)


class LocalCsvInspectorTaskContractTests(unittest.TestCase):
    def test_human_brief_is_locked(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["state"],
            "HUMAN_BRIEF_LOCKED",
        )
        self.assertEqual(
            data["brief"]["productName"],
            "LOCAL CSV INSPECTOR",
        )
        self.assertEqual(
            data["brief"]["humanBriefLock"],
            "LOCKED",
        )

    def test_brief_hash_is_deterministic(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        payload = json.dumps(
            data["brief"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        observed = hashlib.sha256(payload).hexdigest()

        self.assertEqual(
            observed,
            data["briefHash"],
        )

    def test_technology_is_not_preselected(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["brief"]["technologyStack"],
            "UNLOCKED_ENGINEERING_DECISION",
        )

    def test_field_product_source_has_not_started(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["fieldProductSourceGenerationState"],
            "NOT_STARTED",
        )
        self.assertFalse(
            data["workspaceContract"]
                ["fieldProductSourcePrecreated"]
        )

    def test_gate8_acceptance_requires_real_product_truth(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        required = set(
            data["acceptanceContract"]["finalProduct"]
        )

        for item in {
            "REAL_FILE_SELECTION",
            "REAL_PARSING",
            "TARGETED_TEST_PASS",
            "FULL_REGRESSION_PASS",
            "PACKAGE_PROVENANCE_PASS",
            "FRESH_LAUNCH_PASS",
            "HUMAN_USE_PASS",
            "EVIDENCE_COMPLETE",
            "DONECHECK_V1_2_PASS",
        }:
            self.assertIn(item, required)

    def test_manual_source_targets_remain_zero(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        acceptance = data["acceptanceContract"]

        self.assertEqual(
            acceptance["humanManualSourceEditCountTarget"],
            0,
        )
        self.assertEqual(
            acceptance[
                "chatgptDirectFieldProductPatchCountTarget"
            ],
            0,
        )
        self.assertEqual(
            acceptance["untrackedManualStepCountTarget"],
            0,
        )

    def test_capability_truth_preserves_field_proof_boundary(self):
        data = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        preflight = data["capabilityPreflight"]

        self.assertEqual(
            preflight["researchCapability"]["state"],
            "MEVCUT",
        )
        self.assertIn(
            "PENDING",
            preflight["researchCapability"]["fieldProof"],
        )

        for key in (
            "build",
            "test",
            "repair",
            "package",
            "runtimeExecution",
            "evidenceProduction",
            "doneCheckBinding",
        ):
            self.assertEqual(
                preflight[key]["state"],
                "SAHADA_DOGRULANMIS",
            )

    def test_session_state_consumes_same_contract(self):
        state = json.loads(
            SESSION.read_text(encoding="utf-8")
        )
        contract = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        gate8 = state["currentV08"]["gate8"]

        self.assertEqual(
            gate8["humanBriefLock"]["state"],
            "LOCKED",
        )
        self.assertEqual(
            gate8["humanBriefLock"]["briefHash"],
            contract["briefHash"],
        )
        self.assertEqual(
            gate8["taskContract"]["taskId"],
            contract["taskId"],
        )
        self.assertEqual(
            gate8["nextAction"],
            "GATE8_RESEARCH_HARVEST_ARCHITECTURE_VERTICAL_SLICE",
        )

    def test_human_surfaces_show_locked_brief(self):
        status = STATUS.read_text(encoding="utf-8")
        active = ACTIVE.read_text(encoding="utf-8")

        self.assertIn(
            "LOCAL CSV INSPECTOR — LOCKED",
            status,
        )
        self.assertIn(
            "LOCAL CSV INSPECTOR — LOCKED",
            active,
        )


if __name__ == "__main__":
    unittest.main()
