from __future__ import annotations

from pathlib import Path
import unittest

import tools.mac_engineering_refresh_real_task_runtime as refresh


class MacEngineeringRefreshRealTaskRuntimeTests(unittest.TestCase):
    def test_fixture_identity_is_canonical(self):
        self.assertEqual(
            refresh.FIXTURE,
            Path.home() / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture",
        )

    def test_status_is_local_only(self):
        self.assertEqual(
            refresh.STATUS_URL,
            "http://127.0.0.1:8765/api/status",
        )

    def test_unicode_normalization_is_stable(self):
        composed = "ENGÜRÜ"
        decomposed = "ENGU\u0308RU\u0308"
        self.assertEqual(refresh.norm(composed), refresh.norm(decomposed))

    def test_refresh_evidence_is_v06_scoped(self):
        self.assertEqual(
            refresh.OUTPUT.name,
            "package6-real-task-runtime-refresh.json",
        )


if __name__ == "__main__":
    unittest.main()


# v0.6 regression: repository inventory acceptance is identity-based.
import importlib.util as _importlib_util
import unittest as _unittest
from pathlib import Path as _Path


class MacEngineeringFixtureIdentityRefreshTests(
    _unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        tool_path = (
            _Path(__file__).resolve().parents[1]
            / "tools"
            / "mac_engineering_refresh_real_task_runtime.py"
        )

        spec = _importlib_util.spec_from_file_location(
            "fixture_identity_refresh_tool",
            tool_path,
        )

        cls.mod = _importlib_util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_fixture_identity_accepts_stable_repo_count(self):
        rows = [
            {
                "name": "other-repository",
                "path": "/tmp/other-repository",
            },
            {
                "name": "mac-engineering-v06-field-fixture",
                "path": str(self.mod.FIXTURE),
            },
        ]

        observed = self.mod.fixture_from_rows(rows)

        self.assertIsNotNone(observed)
        self.assertEqual(
            observed["name"],
            "mac-engineering-v06-field-fixture",
        )

    def test_unrelated_inventory_does_not_manufacture_pass(self):
        rows = [
            {
                "name": "other-repository",
                "path": "/tmp/other-repository",
            },
        ]

        self.assertIsNone(
            self.mod.fixture_from_rows(rows)
        )

    def test_refresh_gate_has_no_fixed_repo_count(self):
        source = (
            _Path(
                self.mod.__file__
            ).read_text(encoding="utf-8")
        )

        self.assertNotIn(
            "after_count >= 9",
            source,
        )
