from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

MODULE_PATH = (
    ROOT
    / "tools/mac_engineer_v08_existing_product_change.py"
)

SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_existing_product_change",
    MODULE_PATH,
)

assert SPEC and SPEC.loader

gate6 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate6)


class V08ExistingProductChangeControlTests(
    unittest.TestCase
):
    def test_gate5_exact_product_truth_is_preserved(
        self,
    ) -> None:
        self.assertEqual(
            gate6.GATE5_COMMIT,
            "8bd62a2bd8c288b07d51f78ab2164444962bf7c4",
        )

        self.assertEqual(
            gate6.PRODUCT_BASELINE,
            "5432b9b135499cea18273c0e003877b864af92c6",
        )

        self.assertEqual(
            gate6.PRODUCT_BRANCH,
            "feat/v08-native-productization-provenance",
        )

    def test_mutation_scope_is_exactly_two_paths(
        self,
    ) -> None:
        self.assertEqual(
            gate6.AUTHORIZED_PATHS,
            (
                "runtime/static/index.html",
                "runtime/tests/test_v08_existing_product_change.py",
            ),
        )

    def test_primary_surface_contract_is_encoded(
        self,
    ) -> None:
        combined = (
            gate6.PRIMARY_SURFACE_HTML
            + gate6.PRESENTATION_BLOCK
        )

        for expected in (
            "enguruV08PrimaryState",
            "enguruV08OverallState",
            "enguruV08Attention",
            "enguruV08NextAction",
            "enguruV08NewProduction",
            "grid-template-columns:1fr !important;",
            "flex-wrap:wrap;",
            ":focus-visible",
        ):
            self.assertIn(
                expected,
                combined,
            )

    def test_existing_capabilities_remain_bound(
        self,
    ) -> None:
        combined = (
            gate6.PRIMARY_SURFACE_HTML
            + gate6.PRESENTATION_BLOCK
        )

        for expected in (
            "toggleDrawer(true)",
            "newWork()",
            "statusPill",
            "dSystem",
            "dAI",
            "dSteward",
            "dGitHub",
        ):
            self.assertIn(
                expected,
                combined,
            )

    def test_human_artistic_authority_is_explicit(
        self,
    ) -> None:
        source = MODULE_PATH.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            '"humanArtisticAuthority":',
            source,
        )

        self.assertIn(
            '"HUMAN_ARTISTIC_AUTHORITY_REQUIRED"',
            source,
        )

        self.assertIn(
            '"HUMAN_ARTISTIC_AUTHORITY_REVIEW"',
            source,
        )

    def test_remote_product_push_is_absent(
        self,
    ) -> None:
        source = MODULE_PATH.read_text(
            encoding="utf-8"
        )

        self.assertNotIn(
            '["git", "push"',
            source,
        )

        self.assertIn(
            '"remotePush":',
            source,
        )

        self.assertIn(
            "False",
            source,
        )

    def test_donecheck_v12_authority_is_exact(
        self,
    ) -> None:
        self.assertEqual(
            gate6.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )


class GeneratedProductTestPathContract(unittest.TestCase):

    def test_generated_product_test_uses_runtime_static_path(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "tools"
            / "mac_engineer_v08_existing_product_change.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            'RUNTIME = Path(__file__).resolve().parents[1]',
            source,
        )
        self.assertIn(
            'INDEX = RUNTIME / "static" / "index.html"',
            source,
        )
        self.assertNotIn(
            'INDEX = ROOT / "static" / "index.html"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
