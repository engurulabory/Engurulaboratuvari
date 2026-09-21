from __future__ import annotations

from pathlib import Path
import unittest

import tools.mac_engineering_prepare_real_task as prep


class MacEngineeringPrepareRealTaskTests(unittest.TestCase):
    def test_fixture_is_bounded_under_enguru_projects(self):
        self.assertTrue(
            prep.FIXTURE.is_relative_to(
                Path.home() / "Enguru" / "Projects"
            )
        )

    def test_fixture_identity_is_stable(self):
        self.assertEqual(
            prep.TASK_ID,
            "ENGURU-V06-FIELD-001",
        )
        self.assertEqual(
            prep.CHECKPOINT_ID,
            "v06-field-cp-001",
        )

    def test_prompts_are_evidence_side_not_product_source(self):
        self.assertTrue(
            prep.PROMPT_FILE.is_relative_to(prep.EVIDENCE_ROOT)
        )
        self.assertTrue(
            prep.RESUME_PROMPT_FILE.is_relative_to(prep.EVIDENCE_ROOT)
        )

    def test_fixture_marker_is_inside_fixture(self):
        self.assertEqual(
            prep.MARKER.parent,
            prep.FIXTURE,
        )

    def test_v06_fixture_uses_existing_safe_repair_contract(self):
        source = Path(prep.__file__).read_text(encoding="utf-8")
        self.assertIn("CURRENT_STATE.md", source)
        self.assertIn("VERIFIED EXECUTABLE BASELINE", source)
        self.assertIn('"tests"', source)
        self.assertNotIn("intentional bounded defect", source)


if __name__ == "__main__":
    unittest.main()
