from __future__ import annotations

import unittest

from tools.mac_engineer_merge_v06_alignment import (
    REPOSITORY,
    WORKFLOW,
    select_exact_product_ci,
)


class MacEngineerMergeV06AlignmentTests(unittest.TestCase):
    def test_repository_and_workflow_are_product_scoped(self):
        self.assertEqual(
            REPOSITORY,
            "engurulabory/enguru-mac-engineer",
        )
        self.assertEqual(
            WORKFLOW,
            "ENGURU Mac Engineer Product CI",
        )

    def test_select_exact_ci_ignores_other_sha(self):
        result = select_exact_product_ci(
            [
                {
                    "id": 1,
                    "name": WORKFLOW,
                    "head_sha": "wrong",
                    "run_number": 9,
                },
                {
                    "id": 2,
                    "name": WORKFLOW,
                    "head_sha": "exact",
                    "run_number": 8,
                },
            ],
            "exact",
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 2)

    def test_select_exact_ci_prefers_latest_run(self):
        result = select_exact_product_ci(
            [
                {
                    "id": 1,
                    "name": WORKFLOW,
                    "head_sha": "exact",
                    "run_number": 2,
                },
                {
                    "id": 2,
                    "name": WORKFLOW,
                    "head_sha": "exact",
                    "run_number": 3,
                },
            ],
            "exact",
        )
        self.assertEqual(result["id"], 2)

    def test_unrelated_workflow_is_rejected(self):
        result = select_exact_product_ci(
            [
                {
                    "id": 1,
                    "name": "Other Workflow",
                    "path": ".github/workflows/other.yml",
                    "head_sha": "exact",
                    "run_number": 1,
                }
            ],
            "exact",
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
