from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_repository_fabric.py"
SPEC = importlib.util.spec_from_file_location("mac_repository_fabric", MODULE_PATH)
assert SPEC and SPEC.loader
fabric = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fabric)


class MacRepositoryFabricTests(unittest.TestCase):
    def test_manifest_has_twelve_unique_repositories(self):
        manifest = fabric.load_manifest()
        repos = manifest["repositories"]
        names = [item["name"] for item in repos]
        self.assertEqual(len(repos), 12)
        self.assertEqual(len(set(names)), 12)
        self.assertEqual(manifest["repositoryCount"], 12)

    def test_donecheck_is_one_product_two_repository_model(self):
        manifest = fabric.load_manifest()
        dc = manifest["doneCheck"]
        self.assertEqual(dc["productCount"], 1)
        self.assertEqual(dc["repositoryCount"], 2)
        self.assertEqual(
            dc["canonicalProductRepository"],
            "engurulabory/donecheck",
        )
        roles = {
            item["name"]: item["role"]
            for item in manifest["repositories"]
        }
        self.assertEqual(roles["donecheck"], "PRODUCT_CORE_CANONICAL_V1_2")
        self.assertEqual(
            roles["donecheck-core-foundation"],
            "HISTORICAL_CONTROLLED_FOUNDATION",
        )

    def test_normalize_remote_equates_https_and_ssh(self):
        self.assertEqual(
            fabric.normalize_remote("git@github.com:engurulabory/donecheck.git"),
            "https://github.com/engurulabory/donecheck",
        )
        self.assertEqual(
            fabric.normalize_remote("https://github.com/engurulabory/donecheck.git"),
            "https://github.com/engurulabory/donecheck",
        )

    def test_offline_queue_proof_keeps_mirror_main_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            subprocess.run(
                ["git", "init", "-b", "main"],
                cwd=source,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Fabric Test"],
                cwd=source,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "fabric@test.invalid"],
                cwd=source,
                check=True,
            )
            (source / "README.md").write_text("truth\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=source, check=True)
            subprocess.run(
                ["git", "commit", "-m", "truth"],
                cwd=source,
                check=True,
                capture_output=True,
            )

            mirror_root = root / "mirrors"
            mirror_root.mkdir()
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--mirror",
                    str(source),
                    str(mirror_root / "donecheck.git"),
                ],
                check=True,
                capture_output=True,
            )

            before = subprocess.run(
                [
                    "git",
                    "--git-dir",
                    str(mirror_root / "donecheck.git"),
                    "rev-parse",
                    "refs/heads/main",
                ],
                text=True,
                check=True,
                capture_output=True,
            ).stdout.strip()

            result = fabric.offline_queue_proof(mirror_root)

            after = subprocess.run(
                [
                    "git",
                    "--git-dir",
                    str(mirror_root / "donecheck.git"),
                    "rev-parse",
                    "refs/heads/main",
                ],
                text=True,
                check=True,
                capture_output=True,
            ).stdout.strip()

        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["ahead"], 1)
        self.assertFalse(result["fixturePushed"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
