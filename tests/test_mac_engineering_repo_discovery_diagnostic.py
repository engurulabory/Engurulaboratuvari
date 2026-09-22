from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import tools.mac_engineering_repo_discovery_diagnostic as diag


class MacEngineeringRepoDiscoveryDiagnosticTests(unittest.TestCase):
    def test_fixture_path_is_canonical(self):
        self.assertEqual(
            diag.FIXTURE,
            Path.home() / "Enguru" / "Projects" / "mac-engineering-v06-field-fixture",
        )

    def test_source_function_extraction_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.py"
            path.write_text(
                "def discover(root):\n"
                "    return root / 'Projects'\n\n"
                "def unrelated():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            result = diag.source_functions(path)
            names = [item["name"] for item in result["functions"]]
            self.assertIn("discover", names)
            self.assertNotIn("unrelated", names)

    def test_git_probe_handles_non_repo(self):
        with tempfile.TemporaryDirectory() as td:
            result = diag.git_probe(Path(td))
            self.assertFalse(result["git_dir"])

    def test_live_scan_function_is_available(self):
        self.assertTrue(callable(diag.live_runtime_scan))

    def test_repo_control_path_is_runtime_scoped(self):
        self.assertEqual(
            diag.REPO_CONTROL,
            diag.RUNTIME / "repo_control.py",
        )

    def test_diagnostic_evidence_is_v06_scoped(self):
        self.assertEqual(
            diag.EVIDENCE.name,
            "package6-real-task-repo-discovery-diagnostic.json",
        )


if __name__ == "__main__":
    unittest.main()
