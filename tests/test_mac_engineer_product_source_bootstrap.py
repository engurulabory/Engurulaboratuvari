from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.mac_engineer_bootstrap_product_source import (
    BootstrapError,
    prepare_tree,
    safe_relative,
    sha256_file,
)


class MacEngineerProductSourceBootstrapTests(unittest.TestCase):
    def test_safe_relative_rejects_escape(self):
        with self.assertRaises(BootstrapError):
            safe_relative("../escape.py")
        with self.assertRaises(BootstrapError):
            safe_relative("/tmp/absolute.py")

    def test_prepare_tree_applies_verified_runtime_overrides(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_root = root / "historical"
            runtime_root = root / "runtime"
            evidence = root / "evidence"
            dest = root / "product"
            source_root.mkdir()
            runtime_root.mkdir()
            evidence.mkdir()

            source_app = source_root / "runtime" / "app.py"
            source_app.parent.mkdir(parents=True)
            source_app.write_text("VALUE = 'historical'\n", encoding="utf-8")

            swift = source_root / "native" / "EnguruMacEngineer.swift"
            swift.parent.mkdir(parents=True)
            swift.write_text("import Foundation\n", encoding="utf-8")

            runtime_app = runtime_root / "app.py"
            runtime_app.write_text("VALUE = 'field'\n", encoding="utf-8")
            runtime_only = runtime_root / "reliability.py"
            runtime_only.write_text("STATE = 'PASS'\n", encoding="utf-8")

            source_app_record = {
                "path": str(source_app),
                "relative_path": "runtime/app.py",
                "sha256": sha256_file(source_app),
                "size": source_app.stat().st_size,
            }
            swift_record = {
                "path": str(swift),
                "relative_path": "native/EnguruMacEngineer.swift",
                "sha256": sha256_file(swift),
                "size": swift.stat().st_size,
            }

            source_review = {
                "source_root": str(source_root),
                "runtime_root": str(runtime_root),
                "source": {
                    "safe_file_count": 2,
                    "safe_files": [source_app_record, swift_record],
                    "secret_findings": [],
                },
            }
            delta_review = {
                "state": "PASS",
                "compile_result": {"pass": True},
                "test_result": {"pass": True},
                "proposed_authority": {
                    "runtime_authority_candidate_files": [
                        "app.py",
                        "reliability.py",
                    ]
                },
                "rows": [
                    {
                        "classification": "DIVERGENT",
                        "authority": "RUNTIME_FIELD_CANDIDATE",
                        "runtime": {
                            "path": str(runtime_app),
                            "relative_path": "app.py",
                            "sha256": sha256_file(runtime_app),
                        },
                        "source_candidates": [
                            {"source": source_app_record, "diff": {}}
                        ],
                    },
                    {
                        "classification": "RUNTIME_ONLY",
                        "authority": "RUNTIME_FIELD_CANDIDATE",
                        "runtime": {
                            "path": str(runtime_only),
                            "relative_path": "reliability.py",
                            "sha256": sha256_file(runtime_only),
                        },
                    },
                ],
            }
            provenance = {"state": "PASS"}

            source_path = evidence / "source.json"
            delta_path = evidence / "delta.json"
            provenance_path = evidence / "provenance.json"
            source_path.write_text(json.dumps(source_review), encoding="utf-8")
            delta_path.write_text(json.dumps(delta_review), encoding="utf-8")
            provenance_path.write_text(json.dumps(provenance), encoding="utf-8")

            result = prepare_tree(
                dest,
                source_review_path=source_path,
                delta_review_path=delta_path,
                provenance_review_path=provenance_path,
            )

            self.assertEqual(result["runtime_overrides"], 2)
            self.assertTrue(result["verification"]["pass"])
            self.assertEqual(
                (dest / "runtime" / "app.py").read_text(encoding="utf-8"),
                "VALUE = 'field'\n",
            )
            self.assertEqual(
                (dest / "reliability.py").read_text(encoding="utf-8"),
                "STATE = 'PASS'\n",
            )
            self.assertTrue((dest / "native" / "EnguruMacEngineer.swift").exists())
            self.assertTrue((dest / "PROVENANCE.json").exists())
            self.assertTrue((dest / ".enguru" / "labory-manifest.json").exists())
            self.assertTrue((dest / ".github" / "workflows" / "product-ci.yml").exists())

    def test_prepare_tree_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "product"
            dest.mkdir()
            with self.assertRaises(BootstrapError):
                prepare_tree(dest)


if __name__ == "__main__":
    unittest.main()
