from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_ai.field_acceptance import (
    FieldStageEvidence,
    FinishedAbilityGate,
    GovernedToolGapProposal,
    HumanInterventionReconciliationGate,
    SpecialistSpawnGuard,
)


FIXTURE = ROOT / "evidence" / "mac-engineer" / "PACKAGE4_REAL_FIELD_SCENARIO_PACKAGE3.json"


def main() -> int:
    checks: list[dict[str, str]] = []

    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    stages = tuple(
        FieldStageEvidence(
            stage=item["stage"],
            state=item["state"],
            evidence=tuple(item["evidence"]),
            real_field=bool(item["real_field"]),
        )
        for item in payload["stages"]
    )
    finished = FinishedAbilityGate().assess(
        stages,
        recovery_exercised=bool(payload["recoveryExercised"]),
        donecheck_pass=bool(payload["donecheckPass"]),
        final_evidence=tuple(payload["finalEvidence"]),
    )
    if finished.state != "PASS":
        raise AssertionError(f"finished ability hold: {finished.reason}")
    checks.append({"check": "real_field_finished_ability", "state": "PASS"})

    specialist = SpecialistSpawnGuard().assess(
        reason="INDEPENDENT_SECOND_VIEW",
        need_evidence=("review:independence-materially-useful",),
        scope=("package4-review",),
        max_steps=3,
        parent_capabilities=("files", "tests", "review"),
        specialist_capabilities=("review", "files"),
        parent_human_thresholds=("merge", "publish"),
        specialist_human_thresholds=("merge", "publish"),
    )
    if specialist.state != "PASS":
        raise AssertionError(specialist.reason)
    checks.append({"check": "specialist_spawn_guard", "state": "PASS"})

    escalation = SpecialistSpawnGuard().assess(
        reason="CAPABILITY_GAP",
        need_evidence=("capability:missing",),
        scope=("bounded",),
        max_steps=2,
        parent_capabilities=("files",),
        specialist_capabilities=("files", "shell"),
        parent_human_thresholds=("merge",),
        specialist_human_thresholds=("merge",),
    )
    if escalation.state != "HOLD" or escalation.reason != "specialist_privilege_escalation":
        raise AssertionError("specialist escalation must fail closed")
    checks.append({"check": "specialist_privilege_escalation_rejected", "state": "PASS"})

    tool_gap = GovernedToolGapProposal().assess(
        tool_gap_evidence=("tool-gap:verified",),
        proposal="Sandbox one optional adapter.",
        authority_review="PASS",
        security_review="PASS",
        cost_review="PASS",
        bounded_test_evidence=("sandbox:test:pass",),
        decision="ACCEPT",
        autonomous_install_requested=False,
    )
    if tool_gap.state != "PASS" or "installation_authority:NOT_GRANTED" not in tool_gap.evidence:
        raise AssertionError("tool gap proposal boundary failed")
    checks.append({"check": "governed_tool_gap_proposal", "state": "PASS"})

    autonomous_install = GovernedToolGapProposal().assess(
        tool_gap_evidence=("tool-gap:verified",),
        proposal="Sandbox one optional adapter.",
        authority_review="PASS",
        security_review="PASS",
        cost_review="PASS",
        bounded_test_evidence=("sandbox:test:pass",),
        decision="ACCEPT",
        autonomous_install_requested=True,
    )
    if autonomous_install.state != "HOLD":
        raise AssertionError("tool gap granted autonomous install")
    checks.append({"check": "autonomous_install_rejected", "state": "PASS"})

    reconciliation = HumanInterventionReconciliationGate().assess(
        human_intervention_occurred=True,
        checkpoint_revision=7,
        current_revision=8,
        reread_evidence={
            "repo": "main:verified",
            "runtime": "runtime:verified",
            "artifact": "artifact:verified",
            "state": "task:revision-8",
        },
        differences=("human_changed_real_state",),
        reconciled=True,
        new_verified_state="REVISION_8_RECONCILED",
        reconciliation_evidence=("reconciliation:pass",),
    )
    if reconciliation.state != "PASS":
        raise AssertionError(reconciliation.reason)
    checks.append({"check": "human_intervention_reconciliation", "state": "PASS"})

    stale = HumanInterventionReconciliationGate().assess(
        human_intervention_occurred=True,
        checkpoint_revision=7,
        current_revision=7,
        reread_evidence={
            "repo": "main:verified",
            "runtime": "runtime:verified",
            "artifact": "artifact:verified",
            "state": "task:revision-7",
        },
        differences=tuple(),
        reconciled=True,
        new_verified_state="STALE",
        reconciliation_evidence=("reconciliation:attempt",),
    )
    if stale.state != "HOLD":
        raise AssertionError("stale checkpoint resumed after human intervention")
    checks.append({"check": "stale_resume_rejected", "state": "PASS"})

    print(
        json.dumps(
            {
                "state": "PASS",
                "claim": "Package 4 Real Field Acceptance + Finished Ability gates pass.",
                "evidence": checks,
                "field_scenario": payload["scenarioId"],
                "merged_main_sha": payload["mergedMainSha"],
                "next_action": "Run exact-head regression, record Evidence and reconcile canonical WORKLIST.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
