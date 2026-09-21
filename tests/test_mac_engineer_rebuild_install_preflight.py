from __future__ import annotations

import unittest

import tools.mac_engineer_rebuild_install_preflight as preflight


class MacEngineerRebuildInstallPreflightTests(unittest.TestCase):
    def test_target_version_is_v06(self):
        self.assertEqual(preflight.TARGET_VERSION, "0.6")

    def test_canonical_paths_are_separated(self):
        self.assertNotEqual(preflight.PRODUCT, preflight.RUNTIME)
        self.assertNotEqual(preflight.PRODUCT, preflight.INSTALLED_APP)
        self.assertNotEqual(preflight.RUNTIME, preflight.INSTALLED_APP)

    def test_product_runtime_is_source_surface(self):
        self.assertEqual(
            preflight.PRODUCT_RUNTIME,
            preflight.PRODUCT / "runtime",
        )

    def test_current_runtime_is_execution_surface(self):
        self.assertEqual(
            preflight.CURRENT_RUNTIME,
            preflight.RUNTIME / "runtime",
        )


if __name__ == "__main__":
    unittest.main()
