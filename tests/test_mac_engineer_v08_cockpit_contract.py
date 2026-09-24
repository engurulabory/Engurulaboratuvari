from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_UX_AESTHETIC_PRODUCT_CONTRACT_V1.md"
)


class V08CockpitContractTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = CONTRACT.read_text(encoding="utf-8")

    def test_single_persistent_work_surface(self):
        self.assertIn(
            "Cockpit is the single persistent primary work surface.",
            self.text,
        )

    def test_five_states_are_one_surface(self):
        self.assertIn(
            "READY → INSPECTING → WORKING → NEEDS_HUMAN → VERIFIED",
            self.text,
        )
        self.assertIn(
            "states of one persistent working surface",
            self.text,
        )

    def test_mac_local_terminal_execution_is_bound(self):
        self.assertIn(
            "Mac-local shell / terminal execution",
            self.text,
        )

    def test_inspection_only_preserves_source_state(self):
        self.assertIn(
            "Inspection-only work preserves project source state",
            self.text,
        )

    def test_repair_chain_is_explicit(self):
        self.assertIn(
            "read → root cause → smallest sufficient change → test → regression → runtime verification → Evidence → DoneCheck™ → result",
            self.text,
        )

    def test_projects_is_secondary_surface(self):
        self.assertIn(
            "Projects is a secondary visibility and control surface.",
            self.text,
        )
        self.assertIn(
            "Cockpit’te Aç",
            self.text,
        )

    def test_project_lifecycle_is_explicit(self):
        for item in (
            "Archive",
            "Restore",
            "Unpublish",
            "Delete",
            "Human Threshold™",
            "recovery / backup truth",
        ):
            self.assertIn(item, self.text)

    def test_primary_activity_is_compressed(self):
        self.assertIn(
            "Active Project → Status → Attention → Now → concise live activity → result",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
