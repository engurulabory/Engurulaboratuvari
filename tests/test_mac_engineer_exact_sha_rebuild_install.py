from __future__ import annotations

from pathlib import Path
import plistlib
import tempfile
import unittest

import tools.mac_engineer_exact_sha_rebuild_install as install


class MacEngineerExactShaRebuildInstallTests(unittest.TestCase):
    def test_install_surfaces_are_separate(self):
        self.assertNotEqual(install.PRODUCT, install.RUNTIME_ROOT)
        self.assertNotEqual(install.RUNTIME_APP, install.INSTALLED_APP)
        self.assertTrue(
            install.RUNTIME_APP.is_relative_to(install.RUNTIME_ROOT)
        )

    def test_target_version_is_v06(self):
        self.assertEqual(install.TARGET_VERSION, "0.6")

    def test_status_is_local_only(self):
        self.assertEqual(
            install.STATUS_URL,
            "http://127.0.0.1:8765/api/status",
        )

    def test_plist_info_reads_version_contract(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Info.plist"
            with path.open("wb") as f:
                plistlib.dump(
                    {
                        "CFBundleIdentifier": "com.engurumaya.macengineer",
                        "CFBundleShortVersionString": "0.6",
                        "CFBundleVersion": "0.6",
                        "CFBundleExecutable": "EnguruMacEngineer",
                    },
                    f,
                )
            result = install.plist_info(path)
            self.assertEqual(result["bundle_id"], "com.engurumaya.macengineer")
            self.assertEqual(result["short_version"], "0.6")
            self.assertEqual(result["bundle_version"], "0.6")

    def test_provenance_path_is_runtime_state_not_product_source(self):
        self.assertTrue(
            install.PROVENANCE.is_relative_to(install.RUNTIME_ROOT)
        )
        self.assertFalse(
            install.PROVENANCE.is_relative_to(install.PRODUCT)
        )


if __name__ == "__main__":
    unittest.main()
