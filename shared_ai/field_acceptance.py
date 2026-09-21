from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from shared_ai.harvest_controls import ControlResult, HOLD, PASS


FINISHED_ABILITY_STAGES = (
    "UNDERSTAND",
    "DISCOVER",
    "ARCHITECT",
    "EXECUTE",
    "TEST",
    "USER_VERIFY",
    "RECOVER",
    "FINISH",
)


@dataclass(frozen=True)
class FieldStageEvidence:
    stage: str
    state: str
    evidence: tuple[str, ...]
    real_field: bool = True


@dataclass(frozen=True)
class FinishedAbilityResult:
    state: str
    reason: str
    completed_stages: tuple[str, ...]
    evidence: tuple[str, ...]
    critical_failures: tuple[str, ...] = tuple()


class SpecialistSpawnGuard:
    """Bounded specialization without authority or Human Threshold expansion."""

    VALID_REASONS = {"CAPABILITY_GAP", "INDEPENDENT_SECOND_VIEW"}

    def assess(
        self,
        *,
        reason: str,
        need_evidence: tuple[str, ...],
        scope: tuple[str, ...],
        max_steps: int,
        parent_capabilities: tuple[str, ...],
        specialist_capabilities: tuple[str, ...],
        parent_human_thresholds: tuple[str, ...],
        specialist_human_thresholds: tuple[str, ...],
    ) -> ControlResult:
        reason = str(reason).upper()
        if reason not in self.VALID_REASONS:
            return ControlResult(HOLD, "specialist_need_not_verified")
        if not need_evidence:
            return ControlResult(HOLD, "specialist_need_evidence_required")
        if not scope:
            return ControlResult(HOLD, "specialist_scope_required", need_evidence)
        if max_steps < 1 or max_steps > 12:
            return ControlResult(HOLD, "specialist_step_budget_invalid", need_evidence)

        parent = set(parent_capabilities)
        requested = set(specialist_capabilities)
        extra = sorted(requested - parent)
        if extra:
            return ControlResult(
                HOLD,
                "specialist_privilege_escalation",
                (*need_evidence, *(f"extra_capability:{item}" for item in extra)),
            )

        if set(specialist_human_thresholds) != set(parent_human_thresholds):
            return ControlResult(
                HOLD,
                "specialist_human_threshold_drift",
                need_evidence,
            )

        evidence = (
            *need_evidence,
            f"reason:{reason}",
            f"scope:{'|'.join(scope)}",
            f"max_steps:{max_steps}",
            "authority:inherited_without_expansion",
            "human_threshold:inherited_unchanged",
        )
        return ControlResult(PASS, "specialist_spawn_bounded", tuple(evidence))


class GovernedToolGapProposal:
    """A tool gap may produce a reviewed proposal, never autonomous install authority."""

    def assess(
        self,
        *,
        tool_gap_evidence: tuple[str, ...],
        proposal: str,
        authority_review: str,
        security_review: str,
        cost_review: str,
        bounded_test_evidence: tuple[str, ...],
        decision: str,
        autonomous_install_requested: bool = False,
    ) -> ControlResult:
        if not tool_gap_evidence:
            return ControlResult(HOLD, "tool_gap_evidence_required")
        if not proposal.strip():
            return ControlResult(HOLD, "tool_gap_proposal_required", tool_gap_evidence)
        reviews = {
            "authority": str(authority_review).upper(),
            "security": str(security_review).upper(),
            "cost": str(cost_review).upper(),
        }
        invalid = [name for name, state in reviews.items() if state != PASS]
        if invalid:
            return ControlResult(
                HOLD,
                "tool_gap_review_hold:" + ",".join(invalid),
                tool_gap_evidence,
            )
        if not bounded_test_evidence:
            return ControlResult(
                HOLD,
                "tool_gap_bounded_test_required",
                tool_gap_evidence,
            )
        if autonomous_install_requested:
            return ControlResult(
                HOLD,
                "tool_gap_does_not_grant_install_authority",
                (*tool_gap_evidence, *bounded_test_evidence),
            )
        decision = str(decision).upper()
        if decision not in {"ACCEPT", "REJECT"}:
            return ControlResult(
                HOLD,
                "tool_gap_decision_required",
                (*tool_gap_evidence, *bounded_test_evidence),
            )

        return ControlResult(
            PASS,
            f"tool_gap_{decision.lower()}_proposal_only",
            (
                *tool_gap_evidence,
                *bounded_test_evidence,
                "authority_review:PASS",
                "security_review:PASS",
                "cost_review:PASS",
                f"decision:{decision}",
                "installation_authority:NOT_GRANTED",
            ),
        )


class HumanInterventionReconciliationGate:
    """Re-read real state after Human Threshold/takeover before resuming."""

    REQUIRED_SURFACES = ("repo", "runtime", "artifact", "state")

    def assess(
        self,
        *,
        human_intervention_occurred: bool,
        checkpoint_revision: int,
        current_revision: int,
        reread_evidence: Mapping[str, str],
        differences: tuple[str, ...],
        reconciled: bool,
        new_verified_state: str,
        reconciliation_evidence: tuple[str, ...],
    ) -> ControlResult:
        if not human_intervention_occurred:
            return ControlResult(PASS, "human_reconciliation_not_required")

        if current_revision <= checkpoint_revision:
            return ControlResult(HOLD, "post_human_revision_not_advanced")

        missing = [
            surface
            for surface in self.REQUIRED_SURFACES
            if not str(reread_evidence.get(surface, "")).strip()
        ]
        if missing:
            return ControlResult(
                HOLD,
                "post_human_reread_incomplete:" + ",".join(missing),
            )

        if differences and not reconciled:
            return ControlResult(
                HOLD,
                "post_human_differences_unreconciled",
                tuple(reread_evidence.values()),
            )
        if not new_verified_state.strip():
            return ControlResult(
                HOLD,
                "new_verified_state_required",
                tuple(reread_evidence.values()),
            )
        if not reconciliation_evidence:
            return ControlResult(
                HOLD,
                "reconciliation_evidence_required",
                tuple(reread_evidence.values()),
            )

        return ControlResult(
            PASS,
            "new_verified_state_established",
            (
                *(f"{key}:{reread_evidence[key]}" for key in self.REQUIRED_SURFACES),
                *(f"difference:{item}" for item in differences),
                *reconciliation_evidence,
                f"NEW_VERIFIED_STATE:{new_verified_state.strip()}",
            ),
        )


class FinishedAbilityGate:
    """Real field acceptance for Understand → ... → Finish."""

    def assess(
        self,
        stages: Sequence[FieldStageEvidence],
        *,
        recovery_exercised: bool,
        donecheck_pass: bool,
        final_evidence: tuple[str, ...],
        critical_failures: tuple[str, ...] = tuple(),
    ) -> FinishedAbilityResult:
        if critical_failures:
            return FinishedAbilityResult(
                HOLD,
                "critical_field_failure",
                tuple(),
                tuple(),
                critical_failures,
            )

        by_stage = {item.stage.upper(): item for item in stages}
        if set(by_stage) != set(FINISHED_ABILITY_STAGES):
            missing = tuple(stage for stage in FINISHED_ABILITY_STAGES if stage not in by_stage)
            return FinishedAbilityResult(
                HOLD,
                "finished_ability_stage_set_incomplete",
                tuple(stage for stage in FINISHED_ABILITY_STAGES if stage in by_stage),
                tuple(f"missing:{stage}" for stage in missing),
            )

        evidence: list[str] = []
        completed: list[str] = []
        for stage in FINISHED_ABILITY_STAGES:
            item = by_stage[stage]
            if item.state != PASS:
                return FinishedAbilityResult(
                    HOLD,
                    f"field_stage_hold:{stage}",
                    tuple(completed),
                    tuple(evidence),
                )
            if not item.real_field:
                return FinishedAbilityResult(
                    HOLD,
                    f"synthetic_field_evidence:{stage}",
                    tuple(completed),
                    tuple(evidence),
                )
            if not item.evidence:
                return FinishedAbilityResult(
                    HOLD,
                    f"field_stage_evidence_required:{stage}",
                    tuple(completed),
                    tuple(evidence),
                )
            completed.append(stage)
            evidence.extend(f"{stage}:{ref}" for ref in item.evidence)

        if not recovery_exercised:
            return FinishedAbilityResult(
                HOLD,
                "recovery_field_proof_required",
                tuple(completed),
                tuple(evidence),
            )
        if not donecheck_pass:
            return FinishedAbilityResult(
                HOLD,
                "mandatory_donecheck_required",
                tuple(completed),
                tuple(evidence),
            )
        if not final_evidence:
            return FinishedAbilityResult(
                HOLD,
                "final_field_evidence_required",
                tuple(completed),
                tuple(evidence),
            )

        evidence.extend(final_evidence)
        return FinishedAbilityResult(
            PASS,
            "finished_ability_real_field_pass",
            tuple(completed),
            tuple(evidence),
        )
