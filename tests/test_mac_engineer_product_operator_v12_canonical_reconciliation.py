import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance" / "mac-engineer"
PRODUCT = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"

OBJECTIVE = "ENGURU_PRODUCT_OPERATOR_V12"
ACTIVE_GATE = None
NEXT_ACTION = "P1_QWEN38_QUALIFICATION"


def load(name):
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def git(*args):
    result = subprocess.run(
        ["git", "-C", str(PRODUCT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class ProductOperatorV12CanonicalReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = load("SESSION_STATE_V1.json")
        cls.roadmap = load("PRODUCT_ROADMAP_V1.json")
        cls.product_roadmap = load("PRODUCT_OPERATOR_ROADMAP_V1.json")
        cls.contract = load("PRODUCT_OPERATOR_V12_ACCEPTANCE_CONTRACT_V1.json")

    def test_one_active_objective_and_next_action(self):
        self.assertEqual(self.session["currentObjective"], OBJECTIVE)
        self.assertEqual(self.roadmap["current"]["activeObjective"], OBJECTIVE)
        self.assertEqual(self.product_roadmap["objective"]["id"], OBJECTIVE)
        self.assertEqual(self.contract["objectiveId"], OBJECTIVE)
        self.assertEqual(self.session["nextAction"], NEXT_ACTION)
        self.assertEqual(self.roadmap["current"]["nextAction"], NEXT_ACTION)
        self.assertEqual(self.product_roadmap["objective"]["nextAction"], NEXT_ACTION)
        self.assertEqual(self.contract["nextAction"], NEXT_ACTION)

    def test_g1_through_g8_pass_and_objective_is_closed(self):
        gates = self.contract["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["state"] == "PASS" for gate in gates))
        self.assertEqual(gates[7]["id"], "HUMAN_FIELD_ACCEPTANCE")
        self.assertEqual(gates[7]["state"], "PASS")
        self.assertEqual(
            self.session["productOperatorV12"]["activeGate"],
            ACTIVE_GATE,
        )
        self.assertEqual(
            self.roadmap["current"]["activeGate"],
            ACTIVE_GATE,
        )
        self.assertEqual(
            self.product_roadmap["objective"]["activeGate"],
            ACTIVE_GATE,
        )

    def test_source_continuity_matches_fresh_product_truth(self):
        actual_head = git("rev-parse", "HEAD")
        actual_branch = git("branch", "--show-current")
        self.assertEqual(git("status", "--porcelain"), "")

        sources = (
            self.session["productOperatorV12"]["sourceContinuity"],
            self.product_roadmap["sourceContinuity"],
        )
        for source in sources:
            self.assertEqual(source["currentVerifiedHead"], actual_head)
            self.assertEqual(source["branch"], actual_branch)
            self.assertEqual(source["worktree"], "CLEAN")

    def test_package08_is_closed_predecessor_not_active_objective(self):
        self.assertEqual(
            self.session["postV08Objective"]["state"],
            "VERIFIED_CLOSED",
        )
        self.assertNotEqual(
            self.session["currentObjective"],
            "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN",
        )
        self.assertNotEqual(
            self.roadmap["current"]["activeObjective"],
            "PACKAGE08_FIELD_CAPABILITY_CAMPAIGN",
        )

    def test_final_information_architecture_is_implemented_machine_verified_g8_pass(self):
        surface = self.contract["finalProductSurfaceContract"]
        self.assertEqual(
            surface["implementationState"],
            "IMPLEMENTED_MACHINE_VERIFIED_G8_PASS",
        )
        self.assertEqual(surface["topLevelSurfaces"], ["COCKPIT", "PROJELER"])
        self.assertEqual(
            surface["archivePolicy"],
            "PROJECTS_FILTER_NOT_TOP_LEVEL_SURFACE",
        )
        self.assertIn("PERMANENT_PROJECT_RAIL", surface["cockpit"]["forbidden"])
        self.assertIn("PERMANENT_STATUS_RAIL", surface["cockpit"]["forbidden"])
        self.assertEqual(surface["status"]["presentation"], "DEFAULT_CLOSED_DRAWER")
        self.assertEqual(
            surface["productStateVocabulary"],
            ["READY", "WORKING", "NEEDS_HUMAN", "VERIFIED"],
        )
        self.assertEqual(
            surface["stageVocabulary"],
            ["PLANLAMA", "URETIM", "DOGRULAMA", "YAYIN"],
        )
        self.assertFalse(surface["invariants"]["publishedIsState"])
        self.assertTrue(surface["invariants"]["stateDistinctFromStage"])
        self.assertEqual(surface["invariants"]["newCoreCount"], 0)
        self.assertEqual(surface["invariants"]["newGateCount"], 0)
        self.assertEqual(surface["invariants"]["newSecondCockpitCount"], 0)


if __name__ == "__main__":
    unittest.main()
