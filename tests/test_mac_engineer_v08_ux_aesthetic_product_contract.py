from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v08_ux_aesthetic_product_contract.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_ux_aesthetic_product_contract",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
gate3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate3)


class V08UXAestheticProductContractTests(unittest.TestCase):
    def test_donecheck_v12_authority_is_exact(self) -> None:
        self.assertEqual(gate3.DONECHECK_VERSION, "1.2.0")
        self.assertEqual(
            gate3.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )

    def test_primary_questions_are_locked(self) -> None:
        self.assertEqual(
            gate3.PRIMARY_QUESTIONS,
            (
                "Her şey yolunda mı?",
                "Nerede dikkat gerekiyor?",
                "Şimdi neye bakmalıyım?",
            ),
        )

    def test_contract_uses_existing_aesthetic_authority(self) -> None:
        text = gate3.CONTRACT.read_text(encoding="utf-8")
        self.assertIn("Aesthetic Motor™", text)
        self.assertIn("Human Artistic Authority™", text)
        self.assertIn("one coherent canonical direction", text)

    def test_gate3_is_read_only_product_contract(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"productMutation": False', source)
        self.assertIn('"remotePush": False', source)
        self.assertIn('"unnecessaryNewCoreCount": 0', source)
        self.assertIn('"secondCanonicalTruth": False', source)


if __name__ == "__main__":
    unittest.main()
