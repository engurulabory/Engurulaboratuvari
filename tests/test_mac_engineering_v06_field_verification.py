from __future__ import annotations

import unittest

import tools.mac_engineering_verify_real_task as real_task
import tools.mac_engineering_restart_continuity as restart
import tools.mac_engineering_verify_continuity as continuity
import tools.mac_engineering_build_commissioning_bundle as bundle


class MacEngineeringV06FieldVerificationTests(unittest.TestCase):
    def test_real_task_identity_is_stable(self):
        self.assertEqual(real_task.TASK_ID, "ENGURU-V06-FIELD-001")
        self.assertEqual(real_task.CHECKPOINT_ID, "v06-field-cp-001")

    def test_restart_uses_same_identity(self):
        self.assertEqual(restart.TASK_ID, real_task.TASK_ID)
        self.assertEqual(restart.CHECKPOINT_ID, real_task.CHECKPOINT_ID)

    def test_continuity_uses_same_identity(self):
        self.assertEqual(continuity.TASK_ID, real_task.TASK_ID)
        self.assertEqual(continuity.CHECKPOINT_ID, real_task.CHECKPOINT_ID)

    def test_pass_value_accepts_canonical_pass(self):
        self.assertTrue(real_task.test_state_pass("PASS"))
        self.assertTrue(continuity.pass_value("PASS"))
        self.assertFalse(continuity.pass_value("HOLD"))

    def test_ollama_qwen_detection(self):
        self.assertTrue(
            bundle.ollama_has_qwen(
                {"models": [{"name": "qwen3:14b"}]}
            )
        )
        self.assertFalse(
            bundle.ollama_has_qwen(
                {"models": [{"name": "other:latest"}]}
            )
        )

    def test_final_bundle_path_is_v06_evidence(self):
        self.assertTrue(
            bundle.BUNDLE.is_relative_to(bundle.EVIDENCE_ROOT)
        )


if __name__ == "__main__":
    unittest.main()
