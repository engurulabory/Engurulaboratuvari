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
from tools.mac_engineer_source_intake_review import scan_tree


def record(path: Path, root: Path) -> dict:
    return {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


class MacEngineerProductSourceBootstrapTests(unittest.TestCase):
    def test_source_hygiene_accepts_native_command_script(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            native = root / "execution_prep" / "native_app"
            native.mkdir(parents=True)
            command = native / "prepare_native_app.command"
            command.write_text(
                "#!/bin/zsh\necho READY\n",
                encoding="utf-8",
            )

            result = scan_tree(root)
            safe_relatives = {
                item["relative_path"] for item in result["safe"]
            }
            excluded_paths = {
                item["path"] for item in result["excluded"]
            }

            self.assertIn(
                "execution_prep/native_app/prepare_native_app.command",
                safe_relatives,
            )
            self.assertNotIn(str(command), excluded_paths)

    def test_safe_relative_rejects_escape(self):
        with self.assertRaises(BootstrapError):
            safe_relative("../escape.py")
        with self.assertRaises(BootstrapError):
            safe_relative("/tmp/absolute.py")

    def test_prepare_tree_normalizes_native_and_runtime_surfaces(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_root = root / "historical"
            runtime_root = root / "current-runtime"
            evidence = root / "evidence"
            dest = root / "product"
            source_root.mkdir()
            runtime_root.mkdir()
            evidence.mkdir()

            native = source_root / "execution_prep" / "native_app"
            native.mkdir(parents=True)
            swift = native / "EnguruMacEngineerApp.swift"
            swift.write_text("import Foundation\n", encoding="utf-8")
            info = native / "Info.plist"
            info.write_text("<plist></plist>\n", encoding="utf-8")
            prep = native / "prepare_native_app.command"
            prep.write_text(
                '#!/bin/zsh\n'
                'SRC_DIR="$(cd "$(dirname "$0")" && pwd)"\n'
                'RUNTIME_SRC="$(cd "$SRC_DIR/../../baseline_v0.4/runtime" && pwd)"\n',
                encoding="utf-8",
            )

            baseline_runtime = source_root / "baseline_v0.4" / "runtime"
            baseline_runtime.mkdir(parents=True)
            historical_app = baseline_runtime / "app.py"
            historical_app.write_text("VALUE = 'historical'\n", encoding="utf-8")
            historical_provider = baseline_runtime / "provider.py"
            historical_provider.write_text("PROVIDER = 'local'\n", encoding="utf-8")

            runtime_app = runtime_root / "app.py"
            runtime_app.write_text("VALUE = 'field'\n", encoding="utf-8")
            runtime_provider = runtime_root / "provider.py"
            runtime_provider.write_text("PROVIDER = 'local'\n", encoding="utf-8")
            runtime_reliability = runtime_root / "reliability.py"
            runtime_reliability.write_text("STATE = 'PASS'\n", encoding="utf-8")
            runtime_tests = runtime_root / "tests"
            runtime_tests.mkdir()
            runtime_test = runtime_tests / "test_smoke.py"
            runtime_test.write_text(
                "import unittest\n"
                "import app\n"
                "import reliability\n\n"
                "class Smoke(unittest.TestCase):\n"
                "    def test_current_runtime(self):\n"
                "        self.assertEqual(app.VALUE, 'field')\n"
                "        self.assertEqual(reliability.STATE, 'PASS')\n",
                encoding="utf-8",
            )

            safe_files = [
                record(swift, source_root),
                record(info, source_root),
                record(prep, source_root),
                record(historical_app, source_root),
                record(historical_provider, source_root),
            ]

            source_review = {
                "source_root": str(source_root),
                "runtime_root": str(runtime_root),
                "source": {
                    "safe_file_count": len(safe_files),
                    "safe_files": safe_files,
                    "secret_findings": [],
                },
                "runtime_comparison": {
                    "exact": [
                        {
                            "runtime": record(runtime_provider, runtime_root),
                            "source_matches": [
                                record(historical_provider, source_root)
                            ],
                        }
                    ],
                    "divergent": [
                        {
                            "runtime": record(runtime_app, runtime_root),
                            "source_candidates": [
                                {
                                    "source": record(
                                        historical_app, source_root
                                    )
                                }
                            ],
                        }
                    ],
                    "runtime_only": [
                        {"runtime": record(runtime_reliability, runtime_root)},
                        {"runtime": record(runtime_test, runtime_root)},
                    ],
                    "counts": {
                        "runtime_total": 4,
                        "exact": 1,
                        "divergent": 1,
                        "runtime_only": 2,
                    },
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
                        "tests/test_smoke.py",
                    ]
                },
            }
            provenance = {"state": "PASS"}

            source_path = evidence / "source.json"
            delta_path = evidence / "delta.json"
            provenance_path = evidence / "provenance.json"
            source_path.write_text(
                json.dumps(source_review), encoding="utf-8"
            )
            delta_path.write_text(
                json.dumps(delta_review), encoding="utf-8"
            )
            provenance_path.write_text(
                json.dumps(provenance), encoding="utf-8"
            )

            result = prepare_tree(
                dest,
                source_review_path=source_path,
                delta_review_path=delta_path,
                provenance_review_path=provenance_path,
            )

            self.assertEqual(result["native_source_files"], 3)
            self.assertEqual(result["runtime_source_files"], 4)
            self.assertTrue(result["verification"]["pass"])
            self.assertEqual(
                (dest / "runtime" / "app.py").read_text(encoding="utf-8"),
                "VALUE = 'field'\n",
            )
            self.assertEqual(
                (dest / "runtime" / "provider.py").read_text(
                    encoding="utf-8"
                ),
                "PROVIDER = 'local'\n",
            )
            self.assertTrue(
                (dest / "runtime" / "tests" / "test_smoke.py").exists()
            )
            self.assertTrue(
                (
                    dest
                    / "execution_prep"
                    / "native_app"
                    / "EnguruMacEngineerApp.swift"
                ).exists()
            )
            patched_prep = (
                dest
                / "execution_prep"
                / "native_app"
                / "prepare_native_app.command"
            ).read_text(encoding="utf-8")
            self.assertIn("$SRC_DIR/../../runtime", patched_prep)
            self.assertNotIn("baseline_v0.4/runtime", patched_prep)
            self.assertTrue((dest / "PROVENANCE.json").exists())
            self.assertTrue(
                (dest / ".enguru" / "labory-manifest.json").exists()
            )
            self.assertTrue(
                (dest / ".github" / "workflows" / "product-ci.yml").exists()
            )

    def test_delta_authority_must_cover_all_non_exact_runtime_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.json"
            delta = root / "delta.json"
            provenance = root / "provenance.json"
            historical = root / "historical"
            runtime = root / "runtime"
            historical.mkdir()
            runtime.mkdir()

            source.write_text(
                json.dumps(
                    {
                        "source_root": str(historical),
                        "runtime_root": str(runtime),
                        "source": {
                            "safe_file_count": 1,
                            "safe_files": [],
                            "secret_findings": [],
                        },
                        "runtime_comparison": {
                            "exact": [],
                            "divergent": [],
                            "runtime_only": [],
                            "counts": {"runtime_total": 0},
                        },
                    }
                ),
                encoding="utf-8",
            )
            delta.write_text(
                json.dumps(
                    {
                        "state": "PASS",
                        "compile_result": {"pass": True},
                        "test_result": {"pass": True},
                        "proposed_authority": {
                            "runtime_authority_candidate_files": [
                                "unexpected.py"
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )
            provenance.write_text(
                json.dumps({"state": "PASS"}), encoding="utf-8"
            )

            with self.assertRaises(BootstrapError):
                prepare_tree(
                    root / "product",
                    source_review_path=source,
                    delta_review_path=delta,
                    provenance_review_path=provenance,
                )

    def test_prepare_tree_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "product"
            dest.mkdir()
            with self.assertRaises(BootstrapError):
                prepare_tree(dest)


if __name__ == "__main__":
    unittest.main()
