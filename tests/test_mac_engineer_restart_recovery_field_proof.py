from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_restart_recovery_field_proof.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_restart_recovery_field_proof",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class RestartRecoveryFieldProofTests(unittest.TestCase):
    def test_contract_identity_is_stable(self):
        self.assertEqual(
            proof.IDEMPOTENCY_KEY,
            "ENGURU-V07-MAC-NATIVE-RESTART-001",
        )
        self.assertEqual(
            proof.EFFECT_KEY,
            "ENGURU-V07-DURABLE-EFFECT-001",
        )
        self.assertEqual(proof.CONTROLLED_INTERRUPTION_EXIT, 75)

    def test_durable_effect_is_created_exactly_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            created_1, first = proof.apply_effect_once(root, "task_1")
            created_2, second = proof.apply_effect_once(root, "task_1")

            self.assertTrue(created_1)
            self.assertFalse(created_2)
            self.assertEqual(first, second)
            effects = list((root / "effects").glob("*.json"))
            self.assertEqual(len(effects), 1)

    def test_mirror_commit_contract_uses_literal_commit_rev_spec(self):
        with mock.patch.object(
            proof,
            "run",
            return_value={"code": 0, "stdout": "", "stderr": ""},
        ) as runner:
            self.assertTrue(proof.mirror_has_commit("b" * 40))

        runner.assert_called_once_with(
            [
                "git",
                "--git-dir",
                str(proof.PRODUCT_MIRROR),
                "cat-file",
                "-e",
                ("b" * 40) + "^{commit}",
            ],
            timeout=60,
        )

    def test_product_exact_main_requires_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            state.write_text(
                json.dumps({"currentV07": {"productExactMain": "short"}}),
                encoding="utf-8",
            )
            with mock.patch.object(proof, "SESSION_STATE", state):
                with self.assertRaisesRegex(RuntimeError, "PRODUCT_EXACT_MAIN_REQUIRED"):
                    proof.product_exact_main()


if __name__ == "__main__":
    unittest.main()
