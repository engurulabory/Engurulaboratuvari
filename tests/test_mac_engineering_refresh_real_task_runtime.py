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
