from __future__ import annotations

from dataclasses import dataclass


DESTRUCTIVE_OPERATIONS = {
    "DELETE",
    "FORCE_PUSH",
    "RESET_HARD",
    "DROP",
    "TRUNCATE",
    "PRODUCTION_ROLLBACK",
}
DEBUG_ORDER = (
    "REPRODUCE",
    "CAPTURE_EVIDENCE",
    "ROOT_CAUSE",
    "HYPOTHESIS",
    "SMALLEST_EXPERIMENT",
    "FAILING_REGRESSION_TEST",
    "FIX",
    "REVERIFY",
)


@dataclass(frozen=True)
class GuardPolicy:
    allowed_paths: tuple[str, ...]
    frozen_paths: tuple[str, ...] = tuple()


@dataclass(frozen=True)
class DisciplineResult:
    state: str
    reason: str


class RuntimeGuard:
    """Scope and destructive-operation guard. Human authority remains external."""

    @staticmethod
    def _under(path: str, roots: tuple[str, ...]) -> bool:
        clean = path.strip("/")
        return any(clean == root.strip("/") or clean.startswith(root.strip("/") + "/") for root in roots)

    def check(
        self,
        *,
        policy: GuardPolicy,
        path: str,
        operation: str,
        human_approved: bool = False,
    ) -> DisciplineResult:
        if not policy.allowed_paths:
            return DisciplineResult("HOLD", "missing_allowed_scope")
        if not self._under(path, policy.allowed_paths):
            return DisciplineResult("HOLD", "scope_violation")
        if self._under(path, policy.frozen_paths):
            return DisciplineResult("HOLD", "frozen_path")
        if operation.upper() in DESTRUCTIVE_OPERATIONS and not human_approved:
            return DisciplineResult("HOLD", "human_threshold_required")
        return DisciplineResult("PASS", "runtime_guard_pass")


class WorktreeIsolation:
    def assess(
        self,
        *,
        risky_change: bool,
        parallel_work: bool,
        isolated_worktree: bool,
    ) -> DisciplineResult:
        if (risky_change or parallel_work) and not isolated_worktree:
            return DisciplineResult("HOLD", "isolated_worktree_required")
        return DisciplineResult("PASS", "isolation_pass")


class SystematicDebugging:
    def assess(self, steps: tuple[str, ...]) -> DisciplineResult:
        normalized = tuple(step.upper() for step in steps)
        if not normalized:
            return DisciplineResult("HOLD", "reproduction_required")
        unknown = tuple(step for step in normalized if step not in DEBUG_ORDER)
        if unknown:
            return DisciplineResult("HOLD", "unknown_debug_step")

        positions = [DEBUG_ORDER.index(step) for step in normalized]
        if positions != sorted(positions) or len(set(normalized)) != len(normalized):
            return DisciplineResult("HOLD", "debug_order_violation")

        if "FIX" in normalized:
            required_before_fix = {
                "REPRODUCE",
                "CAPTURE_EVIDENCE",
                "ROOT_CAUSE",
                "HYPOTHESIS",
                "SMALLEST_EXPERIMENT",
                "FAILING_REGRESSION_TEST",
            }
            if not required_before_fix.issubset(set(normalized)):
                return DisciplineResult("HOLD", "fix_before_root_cause_or_test")

        if "FIX" in normalized and "REVERIFY" not in normalized:
            return DisciplineResult("HOLD", "reverify_required")

        return DisciplineResult("PASS", "debugging_discipline_pass")


class VerificationBeforeCompletion:
    def assess(
        self,
        *,
        claimed_complete: bool,
        verification_evidence: tuple[str, ...],
    ) -> DisciplineResult:
        if claimed_complete and not verification_evidence:
            return DisciplineResult("HOLD", "completion_without_verification")
        return DisciplineResult("PASS", "completion_claim_bounded")


class SkillTDD:
    def assess(
        self,
        *,
        golden_case: bool,
        negative_case: bool,
        regression_fixture: bool,
    ) -> DisciplineResult:
        if not golden_case:
            return DisciplineResult("HOLD", "golden_case_required")
        if not negative_case:
            return DisciplineResult("HOLD", "negative_case_required")
        if not regression_fixture:
            return DisciplineResult("HOLD", "regression_fixture_required")
        return DisciplineResult("PASS", "skill_tdd_pass")
