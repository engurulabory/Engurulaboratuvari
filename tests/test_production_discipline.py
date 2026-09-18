import unittest

from shared_ai.production_discipline import (
    GuardPolicy,
    RuntimeGuard,
    SkillTDD,
    SystematicDebugging,
    VerificationBeforeCompletion,
    WorktreeIsolation,
)


class ProductionDisciplineTests(unittest.TestCase):
    def test_runtime_guard_rejects_scope_violation(self):
        result = RuntimeGuard().check(
            policy=GuardPolicy(allowed_paths=("shared_ai",)),
            path="billing/live.py",
            operation="EDIT",
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "scope_violation")

    def test_runtime_guard_rejects_frozen_path(self):
        result = RuntimeGuard().check(
            policy=GuardPolicy(
                allowed_paths=("shared_ai",),
                frozen_paths=("shared_ai/authority",),
            ),
            path="shared_ai/authority/policy.py",
            operation="EDIT",
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "frozen_path")

    def test_destructive_operation_requires_human_threshold(self):
        result = RuntimeGuard().check(
            policy=GuardPolicy(allowed_paths=("shared_ai",)),
            path="shared_ai/runtime.py",
            operation="RESET_HARD",
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "human_threshold_required")

    def test_approved_destructive_operation_can_continue_inside_scope(self):
        result = RuntimeGuard().check(
            policy=GuardPolicy(allowed_paths=("shared_ai",)),
            path="shared_ai/runtime.py",
            operation="RESET_HARD",
            human_approved=True,
        )
        self.assertEqual(result.state, "PASS")

    def test_risky_or_parallel_work_requires_isolated_worktree(self):
        for risky, parallel in ((True, False), (False, True), (True, True)):
            with self.subTest(risky=risky, parallel=parallel):
                result = WorktreeIsolation().assess(
                    risky_change=risky,
                    parallel_work=parallel,
                    isolated_worktree=False,
                )
                self.assertEqual(result.state, "HOLD")
                self.assertEqual(result.reason, "isolated_worktree_required")

    def test_debugging_rejects_fix_before_root_cause_and_regression_test(self):
        result = SystematicDebugging().assess(("REPRODUCE", "FIX"))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "fix_before_root_cause_or_test")

    def test_debugging_requires_reverify_after_fix(self):
        result = SystematicDebugging().assess(
            (
                "REPRODUCE",
                "CAPTURE_EVIDENCE",
                "ROOT_CAUSE",
                "HYPOTHESIS",
                "SMALLEST_EXPERIMENT",
                "FAILING_REGRESSION_TEST",
                "FIX",
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "reverify_required")

    def test_complete_debugging_sequence_passes(self):
        result = SystematicDebugging().assess(
            (
                "REPRODUCE",
                "CAPTURE_EVIDENCE",
                "ROOT_CAUSE",
                "HYPOTHESIS",
                "SMALLEST_EXPERIMENT",
                "FAILING_REGRESSION_TEST",
                "FIX",
                "REVERIFY",
            )
        )
        self.assertEqual(result.state, "PASS")

    def test_completion_without_evidence_holds(self):
        result = VerificationBeforeCompletion().assess(
            claimed_complete=True,
            verification_evidence=tuple(),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "completion_without_verification")

    def test_skill_tdd_requires_negative_and_regression_cases(self):
        result = SkillTDD().assess(
            golden_case=True,
            negative_case=False,
            regression_fixture=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "negative_case_required")

    def test_skill_tdd_complete_contract_passes(self):
        result = SkillTDD().assess(
            golden_case=True,
            negative_case=True,
            regression_fixture=True,
        )
        self.assertEqual(result.state, "PASS")


if __name__ == "__main__":
    unittest.main()
