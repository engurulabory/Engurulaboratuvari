from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v08_product_reality_reconciliation.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_product_reality_reconciliation",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
gate2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate2)


class V08ProductRealityReconciliationTests(unittest.TestCase):
    def test_donecheck_v12_authority_is_exact(self) -> None:
        self.assertEqual(gate2.DONECHECK_VERSION, "1.2.0")
        self.assertEqual(
            gate2.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )

    def test_gate2_evidence_is_local_v08(self) -> None:
        self.assertIn(
            "MacEngineer/v0.8/product-reality-reconciliation",
            str(gate2.EVIDENCE_ROOT),
        )

    def test_gate2_consumes_gate1_baseline(self) -> None:
        self.assertIn(
            "MacEngineer/v0.8/self-engineering-baseline",
            str(gate2.BASELINE_ROOT),
        )

    def test_gate2_source_declares_zero_product_mutation(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"productMutation": False', source)
        self.assertIn('"remotePush": False', source)
        self.assertIn('"secondCanonicalTruth": False', source)
        self.assertIn('"unnecessaryNewCoreCount": 0', source)


if __name__ == "__main__":
    unittest.main()
