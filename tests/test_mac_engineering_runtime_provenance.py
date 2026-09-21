from __future__ import annotations

from pathlib import Path
import json
import plistlib
import tempfile
import unittest

import tools.mac_engineer_runtime_provenance as provenance


class MacEngineeringRuntimeProvenanceTests(unittest.TestCase):
    def test_canonical_product_source_is_dedicated_repo(self):
        self.assertEqual(
            provenance.PRODUCT,
            Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer",
        )
        self.assertEqual(
            provenance.EXPECTED_REPO,
            "engurulabory/enguru-mac-engineer",
        )

    def test_expected_version_is_v06(self):
        self.assertEqual(provenance.EXPECTED_VERSION, "0.6")

    def test_provenance_receipt_is_runtime_state(self):
        self.assertEqual(
            provenance.PROVENANCE,
            provenance.RUNTIME_ROOT / "state" / "source-provenance.json",
        )

    def test_app_identity_hashes_executable(self):
        with tempfile.TemporaryDirectory() as td:
            app = Path(td) / "Test.app"
            contents = app / "Contents"
            macos = contents / "MacOS"
            macos.mkdir(parents=True)
            with (contents / "Info.plist").open("wb") as fh:
                plistlib.dump(
                    {
                        "CFBundleIdentifier": provenance.EXPECTED_BUNDLE_ID,
                        "CFBundleShortVersionString": "0.6",
                        "CFBundleVersion": "0.6",
                        "CFBundleExecutable": "EnguruMacEngineer",
                    },
                    fh,
                )
            exe = macos / "EnguruMacEngineer"
            exe.write_bytes(b"binary")
            result = provenance.app_identity(app)
            self.assertTrue(result["exists"])
            self.assertEqual(result["short_version"], "0.6")
            self.assertTrue(result["executable"]["sha256"])

    def test_load_json_missing_is_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            result = provenance.load_json(Path(td) / "missing.json")
            self.assertFalse(result["exists"])


if __name__ == "__main__":
    unittest.main()
