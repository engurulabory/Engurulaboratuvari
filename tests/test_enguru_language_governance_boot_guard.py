from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "enguru_language_governance_boot_guard.py"
)

SPEC = importlib.util.spec_from_file_location(
    "enguru_language_governance_boot_guard",
    MODULE_PATH,
)

MODULE = importlib.util.module_from_spec(SPEC)

assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EnguruSuzgeciBootGuardTests(unittest.TestCase):
    def test_guard_passes(self):
        result = MODULE.validate()

        self.assertEqual(
            result["state"],
            "PASS",
        )

        self.assertEqual(
            result["authority_state"],
            "PASS",
        )

        self.assertEqual(
            result["artifact_count"],
            7,
        )

    def test_all_authorities_have_sha256(self):
        result = MODULE.validate()

        for artifact in result["artifacts"]:
            self.assertEqual(
                len(artifact["sha256"]),
                64,
            )

            int(
                artifact["sha256"],
                16,
            )

    def test_contract_is_authority(self):
        paths = {
            artifact["path"]
            for artifact in MODULE.validate()["artifacts"]
        }

        self.assertIn(
            "governance/chatgpt/"
            "ENGURU_LANGUAGE_GOVERNANCE_CONTRACT_V1.json",
            paths,
        )

    def test_precedence_is_authority(self):
        paths = {
            artifact["path"]
            for artifact in MODULE.validate()["artifacts"]
        }

        self.assertIn(
            "governance/chatgpt/"
            "ENGURU_LANGUAGE_GOVERNANCE_AUTHORITY_PRECEDENCE_V1.json",
            paths,
        )


if __name__ == "__main__":
    unittest.main()
