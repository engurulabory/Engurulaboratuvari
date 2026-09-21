from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tools.mac_engineer_layout_audit as audit


class MacEngineerLayoutAuditTests(unittest.TestCase):
    def test_control_plane_descendant_is_canonical_child(self):
        child = audit.CANONICAL["control_plane"] / "governance" / "mac-engineer"
        with mock.patch.object(Path, "exists", return_value=True):
            state, reason = audit.classify(child)
        self.assertEqual(state, "CANONICAL_CHILD")
        self.assertEqual(reason, "control_plane")

    def test_product_source_descendant_is_canonical_child(self):
        child = (
            audit.CANONICAL["product_source"]
            / "execution_prep"
            / "native_app"
            / "EnguruMacEngineerApp.swift"
        )
        with mock.patch.object(Path, "exists", return_value=True):
            state, reason = audit.classify(child)
        self.assertEqual(state, "CANONICAL_CHILD")
        self.assertEqual(reason, "product_source")

    def test_runtime_build_artifact_remains_known_secondary(self):
        child = (
            audit.CANONICAL["runtime"]
            / "App"
            / "ENGÜRÜ Mac Engineer.app"
        )
        with mock.patch.object(Path, "exists", return_value=True):
            state, reason = audit.classify(child)
        self.assertEqual(state, "KNOWN_SECONDARY")
        self.assertEqual(reason, "RUNTIME_BUILD_ARTIFACT")

    def test_process_path_accepts_unicode_normalization(self):
        canonical = str(audit.CANONICAL["installed_app"])
        decomposed = canonical.replace("Ü", "U\u0308")
        command = f"{decomposed}/Contents/MacOS/EnguruMacEngineer"
        self.assertTrue(audit.canonical_process_command(command))

    def test_unknown_path_remains_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rogue-mac-engineer-copy"
            path.mkdir()
            state, reason = audit.classify(path)
        self.assertEqual(state, "UNKNOWN")
        self.assertEqual(reason, "requires_review")


if __name__ == "__main__":
    unittest.main()
