from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v08_native_app_productization.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_native_app_productization",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
gate5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate5)


class V08NativeAppProductizationTests(unittest.TestCase):
    def test_product_identity_and_branch_are_exact(self) -> None:
        self.assertEqual(
            gate5.PRODUCT_BASELINE,
            "5432b9b135499cea18273c0e003877b864af92c6",
        )
        self.assertEqual(
            gate5.PRODUCT_BRANCH,
            "feat/v08-native-productization-provenance",
        )
        self.assertEqual(gate5.PRODUCT_VERSION, "0.8")

    def test_mutation_scope_is_exactly_three_paths(self) -> None:
        self.assertEqual(
            gate5.AUTHORIZED_PATHS,
            (
                "execution_prep/native_app/Info.plist",
                "execution_prep/native_app/prepare_native_app.command",
                "runtime/tests/test_v08_native_productization.py",
            ),
        )

    def test_native_prepare_is_provenance_bound(self) -> None:
        text = gate5.PREPARE_V08
        for expected in (
            "release.json",
            "sourceCommit",
            "runtimeDigest",
            "rsync -a --delete",
            "codesign --verify --deep --strict",
            "runtime_parity=PASS",
        ):
            self.assertIn(expected, text)

    def test_gate5_never_encodes_remote_push(self) -> None:
        self.assertNotIn("git push", gate5.PREPARE_V08)
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"remotePush": False', source)
        self.assertIn('"secondCanonicalTruth": False', source)

    def test_donecheck_v12_authority_is_exact(self) -> None:
        self.assertEqual(
            gate5.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )


if __name__ == "__main__":
    unittest.main()
