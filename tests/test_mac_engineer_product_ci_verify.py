from __future__ import annotations

import unittest

from tools.mac_engineer_product_ci_verify import evaluate


class MacEngineerProductCIVerifyTests(unittest.TestCase):
    def test_exact_main_success_passes(self):
        sha = "abc123"
        result = evaluate(
            local_head=sha,
            local_origin_main=sha,
            local_clean=True,
            repo_meta={"private": True, "default_branch": "main"},
            branch_meta={"commit": {"sha": sha}},
            workflow_runs=[
                {
                    "name": "ENGURU Mac Engineer Product CI",
                    "head_sha": sha,
                    "status": "completed",
                    "conclusion": "success",
                    "run_number": 7,
                }
            ],
        )
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["issues"], [])

    def test_different_head_does_not_manufacture_pass(self):
        result = evaluate(
            local_head="aaa",
            local_origin_main="aaa",
            local_clean=True,
            repo_meta={"private": True, "default_branch": "main"},
            branch_meta={"commit": {"sha": "aaa"}},
            workflow_runs=[
                {
                    "name": "ENGURU Mac Engineer Product CI",
                    "head_sha": "bbb",
                    "status": "completed",
                    "conclusion": "success",
                    "run_number": 8,
                }
            ],
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("EXACT_MAIN_PRODUCT_CI_RUN_REQUIRED", result["issues"])

    def test_failed_exact_head_ci_holds(self):
        sha = "abc123"
        result = evaluate(
            local_head=sha,
            local_origin_main=sha,
            local_clean=True,
            repo_meta={"private": True, "default_branch": "main"},
            branch_meta={"commit": {"sha": sha}},
            workflow_runs=[
                {
                    "name": "ENGURU Mac Engineer Product CI",
                    "head_sha": sha,
                    "status": "completed",
                    "conclusion": "failure",
                    "run_number": 9,
                }
            ],
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("EXACT_MAIN_PRODUCT_CI_SUCCESS_REQUIRED", result["issues"])


if __name__ == "__main__":
    unittest.main()
