from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v08_full_product_engineering_chain_binding.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_full_product_engineering_chain_binding",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
gate4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate4)


class V08FullProductEngineeringChainBindingTests(unittest.TestCase):
    def test_full_chain_is_fourteen_stages(self) -> None:
        self.assertEqual(len(gate4.CHAIN), 14)
        self.assertEqual(gate4.CHAIN[0], "INTAKE")
        self.assertEqual(gate4.CHAIN[-1], "HUMAN THRESHOLD")

    def test_product_baseline_and_donecheck_are_exact(self) -> None:
        self.assertEqual(
            gate4.PRODUCT_EXACT_MAIN,
            "5432b9b135499cea18273c0e003877b864af92c6",
        )
        self.assertEqual(
            gate4.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )

    def test_gate4_reuses_existing_product_surfaces(self) -> None:
        required = set(gate4.REQUIRED_PRODUCT_FILES)
        self.assertIn("runtime/local_ci.py", required)
        self.assertIn("runtime/repair.py", required)
        self.assertIn("runtime/reliability.py", required)
        self.assertIn(
            "execution_prep/native_app/prepare_native_app.command",
            required,
        )

    def test_gate4_is_binding_only(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"productMutation":False', source)
        self.assertIn('"remotePush":False', source)
        self.assertIn('"unnecessaryNewCoreCount":0', source)
        self.assertIn('"secondCanonicalTruth":False', source)


if __name__ == "__main__":
    unittest.main()
